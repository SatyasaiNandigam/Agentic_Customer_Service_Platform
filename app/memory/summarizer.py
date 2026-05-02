
from __future__ import annotations

import structlog
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from app.agent.state import AgentState
from app.config import get_settings

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Keep only this many recent messages verbatim; summarise everything older.
KEEP_LAST_N_MESSAGES: int = 10

# System prompt for the summarizer call
_SUMMARIZER_SYSTEM = (
    "You are a conversation summarizer for an ecommerce customer service system. "
    "Your task is to create a concise, factual summary of the conversation excerpt "
    "provided.\n\n"
    "The summary must:\n"
    "- Capture all ORDER IDs, TRACKING NUMBERS, REFUND IDs, and PRODUCT names mentioned.\n"
    "- Record any commitments made by the agent (e.g. 'initiated refund for order #1234').\n"
    "- Note the customer's unresolved issues or pending actions.\n"
    "- Be written in third-person past tense ('The customer asked...', 'The agent confirmed...').\n"
    "- Be under 300 words.\n\n"
    "Do NOT include opinions, greetings, or filler. Output only the summary text."
)


# ---------------------------------------------------------------------------
# Lazy LLM client
# ---------------------------------------------------------------------------

_summarizer_llm: ChatOpenAI | None = None


def _get_summarizer_llm() -> ChatOpenAI:
    """Return a cached LLM client for summarization (temperature 0)."""
    global _summarizer_llm
    if _summarizer_llm is None:
        settings = get_settings()
        _summarizer_llm = ChatOpenAI(
            model=settings.classifier_model,
            temperature=0,
            max_tokens=512,
        )
    return _summarizer_llm


# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------


def _estimate_tokens(text: str) -> int:
    """Fast heuristic: characters / 4 ≈ tokens.  Accurate enough for budgeting."""
    return max(1, len(text) // 4)


def _message_text(msg: BaseMessage) -> str:
    """Extract the plain-text content of a message for token estimation."""
    content = msg.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        return " ".join(parts)
    return str(content)


def _total_token_estimate(messages: list[BaseMessage]) -> int:
    """Sum estimated tokens for a list of messages."""
    return sum(_estimate_tokens(_message_text(m)) for m in messages)


# ---------------------------------------------------------------------------
# Core summarization
# ---------------------------------------------------------------------------


async def _call_summarizer(messages_to_summarize: list[BaseMessage]) -> str:
    """Call GPT-4o-mini to produce a summary of *messages_to_summarize*.

    Args:
        messages_to_summarize: Ordered list of messages to condense.

    Returns:
        Summary text string.  On any error returns a safe fallback string
        rather than raising — summarization failure should never block the
        user's request.
    """
    # Build the user turn: a readable transcript of the messages to summarise
    transcript_lines: list[str] = []
    for msg in messages_to_summarize:
        role_label = {"human": "Customer", "ai": "Agent", "tool": "Tool"}.get(
            msg.type, msg.type.capitalize()
        )
        transcript_lines.append(f"{role_label}: {_message_text(msg)}")

    transcript = "\n".join(transcript_lines)

    try:
        llm = _get_summarizer_llm()
        response = await llm.ainvoke(
            [
                SystemMessage(content=_SUMMARIZER_SYSTEM),
                HumanMessage(content=f"Summarise this conversation excerpt:\n\n{transcript}"),
            ]
        )
        summary_text = str(response.content).strip()
        logger.info(
            "summarizer.summary_produced",
            input_messages=len(messages_to_summarize),
            summary_tokens=_estimate_tokens(summary_text),
        )
        return summary_text

    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "summarizer.llm_error",
            error=str(exc),
            error_type=type(exc).__name__,
        )
        # Safe fallback — preserve key facts by listing message count
        return (
            f"[Summary unavailable — {len(messages_to_summarize)} earlier messages "
            f"were condensed due to context limits.]"
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def maybe_summarize(state: AgentState) -> dict:
    """Trim the active message list to the last N messages, summarising the rest.

    Runs as a dedicated graph node before response_generator. When the
    conversation exceeds KEEP_LAST_N_MESSAGES, the oldest messages are
    condensed into ``context_summary`` which is injected into the system
    prompt. Messages are NOT removed from state so the client-side history
    remains complete; the response_generator independently limits the slice
    it passes to the LLM.

    Args:
        state: Full AgentState.

    Returns:
        Partial AgentState dict with updated ``context_summary``.
        Returns ``{}`` when the message count is within the budget (no-op).
    """
    messages: list[BaseMessage] = state.get("messages", [])
    session_id: str = state.get("session_id", "")
    existing_summary: str | None = state.get("context_summary")

    if len(messages) <= KEEP_LAST_N_MESSAGES:
        return {}

    messages_to_summarize = messages[:-KEEP_LAST_N_MESSAGES]

    logger.info(
        "summarizer.triggered",
        session_id=session_id,
        total=len(messages),
        summarizing=len(messages_to_summarize),
        keeping=KEEP_LAST_N_MESSAGES,
    )

    new_summary = await _call_summarizer(messages_to_summarize)

    combined_summary = (
        f"{existing_summary}\n\n---\n\n{new_summary}" if existing_summary else new_summary
    )

    logger.info(
        "summarizer.complete",
        session_id=session_id,
        summarized_count=len(messages_to_summarize),
        summary_tokens=_estimate_tokens(combined_summary),
    )

    # Only update the summary — messages are left intact in state so the
    # client-side history remains complete. The response_generator limits
    # how many messages it passes to the LLM separately.
    return {"context_summary": combined_summary}
