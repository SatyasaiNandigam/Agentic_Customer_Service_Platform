import structlog

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from pydantic import BaseModel

from app.agent.prompts import build_classifier_messages
from app.agent.state import (
    AgentState,
    DIRECT_RESPONSE_INTENTS,
    ESCALATION_INTENTS,
    TOOL_INTENTS,
    IntentType
)


from app.config import get_settings




logger = structlog.get_logger(__name__)

CONFIDENCE_THRESHOLD: float = 0.5

_FALLBACK_STATE: dict = {
    "intent": "unknown",
    "confidence": 0.0,
    "requires_tool": False,
    "needs_escalation": False,
}


class ClassifierOutput(BaseModel):
    intent: IntentType
    confidence: float
    requires_tool: bool
    needs_escalation: bool


_llm: ChatOpenAI | None = None

def _get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        settings = get_settings()
        _llm = ChatOpenAI(
            model=settings.classifier_model,
            temperature=0.0,
            max_tokens=256, # classification output is tiny — cap tokens for cost
        )
    return _llm

def _extract_last_human_message(state: AgentState) -> str | None:
    """Return the text of the most recent HumanMessage in the conversation.

    Iterates the messages list in reverse so we find the latest user turn
    without assuming a fixed position.

    Args:
        state: Current AgentState with populated ``messages`` list.

    Returns:
        The string content of the last HumanMessage, or None if no human
        message exists (e.g., the graph was invoked in an unexpected state).
    """
    for message in reversed(state["messages"]):
        if isinstance(message, HumanMessage):
            content = message.content
            # content can be str or list[dict] (multimodal) — handle both
            if isinstance(content, str):
                return content.strip() or None
            if isinstance(content, list):
                # Extract text parts from multimodal content blocks
                text_parts = [
                    block["text"]
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                combined = " ".join(text_parts).strip()
                return combined or None
    return None

def _apply_confidence_threshold(parsed: dict) -> dict:
    """Downgrade low-confidence results to 'unknown'.

    When the model returns confidence below CONFIDENCE_THRESHOLD, acting on
    the intent would be unreliable. Returning 'unknown' ensures the routing
    edge falls back to a safe direct-response path.

    Args:
        parsed: Output of ``parse_classifier_output()`` — already validated.

    Returns:
        The same dict, potentially with intent overridden to 'unknown' and
        requires_tool/needs_escalation cleared.
    """
    if parsed["confidence"] < CONFIDENCE_THRESHOLD:
        return {
            "intent": "unknown",
            "confidence": parsed["confidence"],
            "requires_tool": False,
            "needs_escalation": False,
        }
    return parsed

def _derive_flags(intent: IntentType, parsed: dict) -> dict:
    """Re-derive requires_tool and needs_escalation from the intent value.

    The LLM returns these flags, but we recompute them from the authoritative
    TOOL_INTENTS / ESCALATION_INTENTS sets to guarantee consistency regardless
    of what the model output said. The model's values are used as a cross-check
    and logged if they disagree.

    Args:
        intent: The validated, post-threshold intent string.
        parsed: Raw parsed output from the classifier (for cross-check logging).

    Returns:
        Dict with corrected ``requires_tool`` and ``needs_escalation`` values.
    """
    authoritative_requires_tool = intent in TOOL_INTENTS
    authoritative_needs_escalation = (
        intent in ESCALATION_INTENTS or parsed.get("needs_escalation", False)
    )

    # Log discrepancy if the model disagreed — useful for prompt tuning
    if parsed.get("requires_tool") != authoritative_requires_tool:
        logger.warning(
            "classifier.flag_mismatch",
            field="requires_tool",
            intent=intent,
            model_said=parsed.get("requires_tool"),
            authoritative=authoritative_requires_tool,
        )

    return {
        "requires_tool": authoritative_requires_tool,
        "needs_escalation": authoritative_needs_escalation,
    }



async def classifier_node(state: AgentState) -> dict:
    """Classify the customer's intent and return a partial state update.

    Called as the second node in the graph (after guardrails_in passes).
    Makes a single LLM call using the few-shot classifier prompt,
    parses the JSON response, and returns the classification fields so
    LangGraph can route to the next node via conditional edges.

    The node never raises — all exceptions are caught, logged, and converted
    to a safe "unknown" fallback so the graph can always continue.

    Args:
        state: The current AgentState.  Must have at least one HumanMessage
               in ``state["messages"]``.

    Returns:
        Partial AgentState dict with keys:
            - intent          (IntentType)
            - confidence      (float)
            - requires_tool   (bool)
            - needs_escalation (bool)
    """
    log = logger.bind(
        user_id=state.get("user_id"),
        session_id=state.get("session_id"),
    )

    # ------------------------------------------------------------------
    # 1. Extract the user's message
    # ------------------------------------------------------------------
    user_message = _extract_last_human_message(state)

    if not user_message:
        log.warning("classifier.no_human_message")
        return _FALLBACK_STATE

    log.info("classifier.started", message_preview=user_message[:80])

    # ------------------------------------------------------------------
    # 2. Build messages and call LLM
    # ------------------------------------------------------------------
    # Pass up to 2 prior turns (4 messages) so the classifier can resolve
    # follow-up references like "cancel it" or "what about the price?".
    # We exclude the last message (current user turn) since it is passed
    # separately as user_message.
    prior_messages = state["messages"][:-1]
    recent_history = prior_messages[-4:] if prior_messages else None

    try:
        messages = build_classifier_messages(user_message, history=recent_history)
        llm = _get_llm()
        result: ClassifierOutput = await llm.with_structured_output(ClassifierOutput).ainvoke(messages)
        parsed = result.model_dump()

    except Exception as exc:  # noqa: BLE001
        log.error(
            "classifier.llm_error",
            error=str(exc),
            error_type=type(exc).__name__,
        )
        return _FALLBACK_STATE

    log.debug(
        "classifier.raw_parsed",
        intent=parsed["intent"],
        confidence=parsed["confidence"],
        requires_tool=parsed["requires_tool"],
        needs_escalation=parsed["needs_escalation"],
    )

    # ------------------------------------------------------------------
    # 4. Apply confidence threshold
    # ------------------------------------------------------------------
    parsed = _apply_confidence_threshold(parsed)

    intent: IntentType = parsed["intent"]  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # 5. Re-derive flags from authoritative intent sets
    # ------------------------------------------------------------------
    flags = _derive_flags(intent, parsed)

    # ------------------------------------------------------------------
    # 6. Build and return the state update
    # ------------------------------------------------------------------
    result = {
        "intent": intent,
        "confidence": parsed["confidence"],
        "requires_tool": flags["requires_tool"],
        "needs_escalation": flags["needs_escalation"],
    }

    log.info(
        "classifier.completed",
        intent=result["intent"],
        confidence=result["confidence"],
        requires_tool=result["requires_tool"],
        needs_escalation=result["needs_escalation"],
        routing=(
            "escalate"
            if result["needs_escalation"]
            else ("tool" if result["requires_tool"] else "direct")
        ),
    )

    return result
