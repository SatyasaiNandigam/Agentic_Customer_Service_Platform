import structlog
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.agent.prompts.classifier_v4 import build_domain_classifier_messages
from app.agent.state import (
    ADVICE_INTENTS,
    ASSISTANCE_INTENTS,
    ESCALATION_INTENTS,
    INFORMATION_INTENTS,
    AgentState,
    IntentType,
)

logger = structlog.get_logger(__name__)

CONFIDENCE_THRESHOLD: float = 0.5

# Domain-to-fallback-intent: if confidence is too low, use the safest intent
# for the domain rather than a one-size-fits-all "unknown".
_DOMAIN_FALLBACK_INTENT: dict[str, IntentType] = {
    "need_information": "order_status",
    "need_assistance": "refund_request",
    "need_advice": "unknown",
}

# Domains whose intents always require a tool call.
_TOOL_DOMAINS: frozenset[str] = frozenset({"need_information", "need_assistance"})


class ClassifierOutput(BaseModel):
    intent: IntentType
    confidence: float


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


def _derive_flags(intent: IntentType, domain: str) -> dict:
    """Derive requires_tool and needs_escalation from domain and intent.

    Domain is the authoritative source for requires_tool — avoids any
    mismatch between what the LLM labels and what the domain implies.
    needs_escalation is checked against ESCALATION_INTENTS as a secondary
    safety net for complaint signals that slipped through the delegator.
    """
    return {
        "requires_tool": domain in _TOOL_DOMAINS,
        "needs_escalation": intent in ESCALATION_INTENTS,
    }


def _validate_intent_for_domain(intent: IntentType, domain: str) -> IntentType:
    """Ensure the classified intent belongs to the expected domain's set.

    If the LLM somehow returns an intent from a different domain (shouldn't
    happen with the bounded prompt, but defensive check), fall back to the
    domain's safe default so routing flags remain consistent.
    """
    domain_sets: dict[str, frozenset] = {
        "need_information": INFORMATION_INTENTS,
        "need_assistance": ASSISTANCE_INTENTS,
        "need_advice": ADVICE_INTENTS,
    }
    allowed = domain_sets.get(domain)
    if allowed and intent not in allowed:
        logger.warning(
            "classifier.intent_domain_mismatch",
            intent=intent,
            domain=domain,
            fallback=_DOMAIN_FALLBACK_INTENT[domain],
        )
        return _DOMAIN_FALLBACK_INTENT[domain]
    return intent


def make_classifier_node(llm: ChatOpenAI):
    """Return a classifier node coroutine that uses the provided LLM."""

    async def classifier_node(state: AgentState) -> dict:
        """Classify the customer's specific intent within their domain.

        Runs after customer_delegator_node. Reads the customer_domain from state
        and builds a focused prompt containing only the intents valid for that
        domain — the bounded-context guarantee. Returns the fine-grained intent
        and routing flags.

        Args:
            state: Current AgentState. Must have customer_domain set by the
                   delegator and at least one HumanMessage in messages.

        Returns:
            Partial state update with keys:
                - intent           (IntentType)
                - confidence       (float)
                - requires_tool    (bool)
                - needs_escalation (bool)
        """
        log = logger.bind(
            user_id=state.get("user_id"),
            session_id=state.get("session_id"),
        )

        domain = state.get("customer_domain", "need_advice")

        fallback: dict = {
            "intent": _DOMAIN_FALLBACK_INTENT.get(domain, "unknown"),
            "confidence": 0.0,
            "requires_tool": domain in _TOOL_DOMAINS,
            "needs_escalation": False,
        }

        user_message = _extract_last_human_message(state)
        if not user_message:
            log.warning("classifier.no_human_message")
            return fallback

        log.info("classifier.started", message_preview=user_message[:80], domain=domain)

        prior_messages = state["messages"][:-1]
        recent_history = prior_messages[-4:] if prior_messages else None

        try:
            messages = build_domain_classifier_messages(
                user_message, domain=domain, history=recent_history
            )
            result: ClassifierOutput = await llm.with_structured_output(ClassifierOutput).ainvoke(messages)
            intent = result.intent
            confidence = result.confidence
        except Exception as exc:  # noqa: BLE001
            log.error(
                "classifier.llm_error",
                error=str(exc),
                error_type=type(exc).__name__,
            )
            return fallback

        log.debug("classifier.raw", intent=intent, confidence=confidence, domain=domain)

        if confidence <= CONFIDENCE_THRESHOLD:
            intent = _DOMAIN_FALLBACK_INTENT.get(domain, "unknown")

        intent = _validate_intent_for_domain(intent, domain)
        flags = _derive_flags(intent, domain)

        output = {
            "intent": intent,
            "confidence": confidence,
            "requires_tool": flags["requires_tool"],
            "needs_escalation": flags["needs_escalation"],
        }

        log.info(
            "classifier.completed",
            intent=output["intent"],
            confidence=output["confidence"],
            domain=domain,
            requires_tool=output["requires_tool"],
            needs_escalation=output["needs_escalation"],
            routing=(
                "escalate" if output["needs_escalation"]
                else ("tool" if output["requires_tool"] else "direct")
            ),
        )

        return output

    return classifier_node
