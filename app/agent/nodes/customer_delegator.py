import structlog
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.agent.prompts.customer_delegator import build_delegator_messages
from app.agent.state import AgentState, CustomerDomain
from app.config import get_settings

logger = structlog.get_logger(__name__)

CONFIDENCE_THRESHOLD: float = 0.5

_FALLBACK_STATE: dict = {
    "customer_domain": "need_advice",  # safest default — no tools, no escalation
}


class DelegatorOutput(BaseModel):
    domain: CustomerDomain
    confidence: float


_llm: ChatOpenAI | None = None


def _get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        settings = get_settings()
        _llm = ChatOpenAI(
            model=settings.classifier_model,
            temperature=0.0,
            max_tokens=64,  # domain output is tiny
        )
    return _llm


def _extract_last_human_message(state: AgentState) -> str | None:
    for message in reversed(state["messages"]):
        if isinstance(message, HumanMessage):
            content = message.content
            if isinstance(content, str):
                return content.strip() or None
            if isinstance(content, list):
                text_parts = [
                    block["text"]
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                combined = " ".join(text_parts).strip()
                return combined or None
    return None


async def customer_delegator_node(state: AgentState) -> dict:
    """Classify what KIND of customer we are dealing with.

    Runs after guardrails_in and before the intent classifier. Determines the
    customer's domain (need_information, need_assistance, need_advice, escalate,
    block) so the next classifier node can load only the relevant bounded intent
    set rather than all 13 intents at once.

    Args:
        state: Current AgentState with at least one HumanMessage.

    Returns:
        Partial state update with key:
            - customer_domain (CustomerDomain)
    """
    log = logger.bind(
        user_id=state.get("user_id"),
        session_id=state.get("session_id"),
    )

    user_message = _extract_last_human_message(state)

    if not user_message:
        log.warning("customer_delegator.no_human_message")
        return _FALLBACK_STATE

    log.info("customer_delegator.started", message_preview=user_message[:80])

    prior_messages = state["messages"][:-1]
    recent_history = prior_messages[-4:] if prior_messages else None

    try:
        messages = build_delegator_messages(user_message, history=recent_history)
        llm = _get_llm()
        result: DelegatorOutput = await llm.with_structured_output(DelegatorOutput).ainvoke(messages)
        domain = result.domain
        confidence = result.confidence
    except Exception as exc:  # noqa: BLE001
        log.error(
            "customer_delegator.llm_error",
            error=str(exc),
            error_type=type(exc).__name__,
        )
        return _FALLBACK_STATE

    if confidence < CONFIDENCE_THRESHOLD:
        log.warning(
            "customer_delegator.low_confidence",
            domain=domain,
            confidence=confidence,
        )
        domain = "need_advice"

    log.info(
        "customer_delegator.completed",
        customer_domain=domain,
        confidence=confidence,
        routing=(
            "handoff" if domain in ("escalate", "block") else "classifier"
        ),
    )

    return {"customer_domain": domain}
