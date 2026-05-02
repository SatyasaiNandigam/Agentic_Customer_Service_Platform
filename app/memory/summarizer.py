
from __future__ import annotations

import structlog
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage

from app.agent.state import AgentState
from app.config import get_settings

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Summarise when this many new messages have accumulated since the last summary.
# The summarizer fires roughly every SUMMARIZE_AFTER_N // 2 turns (each turn adds
# one human + one AI message). Between firings the LLM receives the cumulative
# summary plus the unsummarized messages directly.
SUMMARIZE_AFTER_N: int = 10

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


async def _call_summarizer(
    messages_to_summarize: list[BaseMessage],
    existing_summary: str | None = None,
) -> str:
    """Call GPT-4o-mini to produce a unified summary of prior context + new messages.

    When an existing_summary is provided it is prepended to the transcript so the
    LLM can produce one coherent, de-duplicated summary of the entire history so
    far — not a concatenation of separate summaries.

    Args:
        messages_to_summarize: Ordered list of new messages to condense.
        existing_summary: Previously produced summary to incorporate, if any.

    Returns:
        Summary text string.  On any error returns a safe fallback string
        rather than raising — summarization failure should never block the
        user's request.
    """
    transcript_lines: list[str] = []
    for msg in messages_to_summarize:
        role_label = {"human": "Customer", "ai": "Agent", "tool": "Tool"}.get(
            msg.type, msg.type.capitalize()
        )
        transcript_lines.append(f"{role_label}: {_message_text(msg)}")

    transcript = "\n".join(transcript_lines)

    if existing_summary:
        user_content = (
            f"Previous summary of the conversation so far:\n{existing_summary}"
            f"\n\nNew messages to incorporate into an updated summary:\n{transcript}"
        )
    else:
        user_content = f"Summarise this conversation excerpt:\n\n{transcript}"

    try:
        llm = _get_summarizer_llm()
        response = await llm.ainvoke(
            [
                SystemMessage(content=_SUMMARIZER_SYSTEM),
                HumanMessage(content=user_content),
            ]
        )
        summary_text = str(response.content).strip()
        logger.info(
            "summarizer.summary_produced",
            input_messages=len(messages_to_summarize),
            had_prior_summary=existing_summary is not None,
            summary_tokens=_estimate_tokens(summary_text),
        )
        return summary_text

    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "summarizer.llm_error",
            error=str(exc),
            error_type=type(exc).__name__,
        )
        fallback_base = (
            f"[Summary unavailable — {len(messages_to_summarize)} earlier messages "
            f"were condensed due to context limits.]"
        )
        # Preserve whatever we had rather than losing it entirely
        return f"{existing_summary}\n\n{fallback_base}" if existing_summary else fallback_base


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def maybe_summarize(state: AgentState) -> dict:
    """Batch-summarise older messages once SUMMARIZE_AFTER_N new messages accumulate.

    Runs as a dedicated graph node before response_generator. The summarizer
    fires only when at least SUMMARIZE_AFTER_N messages have built up since the
    last summary — not on every turn. Between firings the LLM receives the
    cumulative summary (in the system prompt) plus the raw unsummarized messages.

    safe_horizon is always len(messages) - 1: the current human message is kept
    outside the summary so that after a fresh summarization the LLM sees exactly
    one raw message alongside the new cumulative summary.

    Messages are never removed from state so the client-side history endpoint
    always returns the full conversation.

    Args:
        state: Full AgentState.

    Returns:
        Partial AgentState dict with updated ``context_summary`` and
        ``summarized_message_count``. Returns ``{}`` when not enough new
        messages have accumulated (no-op).
    """
    messages: list[BaseMessage] = state.get("messages", [])
    session_id: str = state.get("session_id", "")
    existing_summary: str | None = state.get("context_summary")
    summarized_through: int = state.get("summarized_message_count", 0)

    # safe_horizon: everything except the current (latest) message.
    # We never summarize the message we are about to respond to.
    safe_horizon = len(messages) - 1

    # Never split an AIMessage(tool_calls) + ToolMessage pair across the boundary.
    # If safe_horizon lands on a ToolMessage, walk backward until we reach a
    # non-ToolMessage — that keeps the full tool-call group in the recent slice
    # so the LLM always receives a valid (AIMessage → ToolMessage) pair.
    while safe_horizon > summarized_through and isinstance(messages[safe_horizon], ToolMessage):
        safe_horizon -= 1

    # Only fire when SUMMARIZE_AFTER_N or more new messages are waiting.
    if safe_horizon - summarized_through < SUMMARIZE_AFTER_N:
        return {}

    messages_to_summarize = messages[summarized_through:safe_horizon]

    logger.info(
        "summarizer.triggered",
        session_id=session_id,
        total=len(messages),
        cursor_from=summarized_through,
        cursor_to=safe_horizon,
        summarizing=len(messages_to_summarize),
    )

    new_summary = await _call_summarizer(messages_to_summarize, existing_summary=existing_summary)

    logger.info(
        "summarizer.complete",
        session_id=session_id,
        summarized_count=len(messages_to_summarize),
        new_cursor=safe_horizon,
        had_prior_summary=existing_summary is not None,
        summary_tokens=_estimate_tokens(new_summary),
    )

    return {"context_summary": new_summary, "summarized_message_count": safe_horizon}
