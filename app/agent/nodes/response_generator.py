import json

import structlog

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, SystemMessage

from app.agent.prompts import build_system_prompt
from app.agent.state import AgentState

logger = structlog.get_logger(__name__)

_FALLBACK_GENERIC = (
    "I'm sorry, I encountered an issue while preparing your response. "
    "Please try again, or contact our support team if the problem persists."
)

_FALLBACK_TOOL_ERROR = (
    "I wasn't able to retrieve the information needed to answer your question right now. "
    "Please try again in a moment, or let me know if I can help with something else."
)


def _build_grounding_section(
    tool_result: dict | None,
    tool_error: str | None,
) -> str:
    """Build the data-grounding section appended to the system prompt.

    Three distinct cases:
    1. ``tool_error`` is set → instruct graceful error acknowledgement only.
    2. ``tool_result`` is present → inject the structured data payload and
       enforce strict grounding (every factual claim must trace to this data).
    3. Neither is set (chitchat / faq_policy / unknown) → return "" so the
       system prompt remains lean and uncluttered.

    Args:
        tool_result: Structured dict returned by the tool_executor node.
                     May be an empty dict ``{}`` when the query returned no
                     rows — the LLM is instructed to say "not found" in that
                     case rather than fabricate results.
        tool_error:  Human-readable error string if tool execution failed.
                     The content of this string is intentionally withheld from
                     the LLM — only the fact that retrieval failed is shared.

    Returns:
        Multi-line string ready to be appended to the system prompt content,
        or an empty string when no tool was involved in this turn.
    """
    if tool_error:
        # Intentionally do not forward the raw error string — it may contain
        # SQL state, table names, or other internals that must stay hidden.
        return (
            "\n\n## Data retrieval result\n"
            "The database query for this request encountered an error. "
            "Acknowledge the issue professionally: tell the customer you are having "
            "trouble accessing their information right now and suggest they try again "
            "shortly, or contact support if the problem continues. "
            "Do NOT mention the error, any error message text, or any system details."
        )

    if tool_result is not None:
        # ``default=str`` serialises Decimal, datetime, UUID, etc. that
        # SQLAlchemy returns but json.dumps cannot handle natively.
        data_json = json.dumps(tool_result, indent=2, default=str)
        return (
            "\n\n## Data retrieved from database\n"
            "The JSON below is the ONLY data source you may use for factual claims. "
            "Every order ID, tracking number, price, date, status, product name, "
            "or account detail in your response MUST appear verbatim in this payload. "
            "Do not infer, estimate, round, or recall any figures not present here.\n"
            "If the payload contains empty lists or null fields, tell the customer "
            "honestly that no matching information was found — do not guess.\n\n"
            f"```json\n{data_json}\n```"
        )

    # No tool involved — chitchat, faq_policy, or unknown intent.
    return ""


def _build_messages(state: AgentState) -> list:
    """Compose the full message list for the response-generation LLM call."""
    system_message = build_system_prompt(
        user_id=state["user_id"],
        user_role=state["user_role"],
        context_summary=state.get("context_summary"),
        customer_history=state.get("customer_history"),
    )

    grounding = _build_grounding_section(
        tool_result=state.get("tool_result"),
        tool_error=state.get("tool_error"),
    )
    if grounding:
        system_message = SystemMessage(content=system_message.content + grounding)

    all_messages = list(state["messages"])
    recent_messages = all_messages[-10:] if len(all_messages) > 10 else all_messages
    return [system_message] + recent_messages


def _resolve_response_path(state: AgentState) -> str:
    """Return a label describing which response path is active (for logging)."""
    if state.get("tool_error"):
        return "tool_error"
    if state.get("tool_result") is not None:
        return "tool_result"
    return "direct"


def make_response_generator_node(llm: ChatOpenAI):
    """Return a response_generator node coroutine that uses the provided LLM."""

    async def response_generator_node(state: AgentState) -> dict:
        """Generate the final customer-facing response and return a state update.

        Called as the last reasoning step before ``guardrails_out``.  Builds a
        system-prompt-augmented message list, invokes LLM, and returns
        the resulting AIMessage as a partial state update.

        The node never raises — any exception produces a safe, customer-friendly
        fallback message so the graph always terminates cleanly.

        Args:
            state: The current AgentState.

        Returns:
            Partial AgentState dict with:

                ``messages``
                    ``[AIMessage(response_text)]`` — the add_messages reducer
                    appends this to the existing history without overwriting it.
                ``output_safe``
                    ``True`` as the initial value.  The ``guardrails_out`` node
                    reads this and may flip it to ``False`` if a violation is
                    detected, triggering a rewrite loop (max 2 retries).
        """
        response_path = _resolve_response_path(state)
        log = logger.bind(
            user_id=state.get("user_id"),
            session_id=state.get("session_id"),
            intent=state.get("intent"),
            response_path=response_path,
        )

        log.info("response_generator.started")

        fallback = _FALLBACK_TOOL_ERROR if state.get("tool_error") else _FALLBACK_GENERIC

        try:
            messages = _build_messages(state)
            llm_response = await llm.ainvoke(messages)
            content: str = str(llm_response.content).strip()

            if not content:
                log.warning("response_generator.empty_llm_response")
                content = fallback

        except Exception as exc:  # noqa: BLE001
            log.error(
                "response_generator.llm_error",
                error=str(exc),
                error_type=type(exc).__name__,
            )
            content = fallback

        log.info(
            "response_generator.completed",
            response_length=len(content),
            response_path=response_path,
        )

        return {
            "messages": [AIMessage(content=content)],
            "output_safe": True,
        }

    return response_generator_node
