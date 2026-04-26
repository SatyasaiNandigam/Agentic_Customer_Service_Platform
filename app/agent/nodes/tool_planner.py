from __future__ import annotations

import structlog
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langchain_core.tools import BaseTool
from pydantic import ValidationError

from app.agent.prompts import build_system_prompt
from app.agent.state import AgentState
from app.config import get_settings
from app.mcp_client.tool_registry import get_registry_tools

logger = structlog.get_logger(__name__)


_llm : ChatOpenAI | None = None

def _get_llm() -> ChatOpenAI:
    """Return the shared ChatOpenAI client, creating it on first call."""
    global _llm
    if _llm is None:
        settings = get_settings()
        _llm = ChatOpenAI(
            model=settings.classifier_model,
            temperature=0,            # deterministic tool selection
            max_tokens=settings.openai_max_tokens,
        )
    return _llm 

def _build_messages(state: AgentState) -> list[BaseMessage]:
    """Prepend the system prompt to the current conversation history.

    The system prompt is rebuilt on every invocation so that context_summary
    and customer_history (loaded from Redis/Postgres) are always fresh.

    Args:
        state: Current AgentState.

    Returns:
        List starting with SystemMessage followed by all conversation messages.
    """
    system_msg: SystemMessage = build_system_prompt(
        user_id=state["user_id"],
        user_role=state["user_role"],
        context_summary=state.get("context_summary"),
        customer_history=state.get("customer_history"),
    )
    return [system_msg, *state["messages"]]


def _validate_tool_args(
    tool_name: str,
    args: dict,
    available_tools: list[BaseTool],
) -> tuple[dict, str | None]:
    """Validate LLM-generated tool args against the tool's Pydantic schema.

    Each LangChain ``BaseTool`` that comes from the MCP server carries an
    ``args_schema`` Pydantic model derived from the tool's JSON schema.
    Validating against it here catches:
      - Missing required fields the LLM forgot to populate.
      - Wrong types (e.g. str where int is expected).
      - Extra fields the LLM hallucinated.

    Args:
        tool_name:       Name of the tool the LLM selected.
        args:            Raw args dict from ``ai_msg.tool_calls[0]["args"]``.
        available_tools: Full list of available tools (to find the schema).

    Returns:
        Tuple of ``(validated_args, error_message)``.
        On success: ``(validated_args, None)`` — args coerced by Pydantic.
        On failure: ``(args, error_str)`` — original args + human-readable error.
    """
    matched: BaseTool | None = next(
        (t for t in available_tools if t.name == tool_name), None
    )
    if matched is None or matched.args_schema is None:
        # No schema to validate against — pass args through unchanged.
        return args, None

    # MCP tools may surface args_schema as a raw dict (JSON Schema) instead of
    # a Pydantic model class. Skip Pydantic validation in that case.
    if not hasattr(matched.args_schema, "model_validate"):
        return args, None

    try:
        validated = matched.args_schema.model_validate(args)
        # model_dump() coerces types (e.g. int "5" → 5) and strips extra fields.
        return validated.model_dump(exclude_none=True), None
    except ValidationError as exc:
        # Collect all field errors into one readable string for the retry context.
        error_lines = [
            f"  • {' → '.join(str(loc) for loc in e['loc'])}: {e['msg']}"
            for e in exc.errors()
        ]
        error_str = f"Tool args validation failed for '{tool_name}':\n" + "\n".join(error_lines)
        return args, error_str



async def tool_planner_node(state: AgentState) -> dict:
    """Select a tool and populate its arguments based on the conversation context.

    Node contract:
        Input:  AgentState (full) — reads messages, user_id, user_role,
                intent, tool_error (when retrying), retry_count.
        Output: Partial AgentState dict — updates selected_tool, tool_input,
                retry_count, tool_error, requires_tool, and messages.

    The node never raises — all exceptions are caught and converted to a
    ``tool_error`` state update so ``route_after_tool_executor`` can handle
    the retry/fallback logic without crashing the graph.

    Args:
        state: Current AgentState.

    Returns:
        Partial state dict with tool planning results.
    """
    user_id: int = state["user_id"]
    user_role: str = state["user_role"]
    intent: str = state.get("intent", "unknown")
    is_retry: bool = state.get("tool_error") is not None
    retry_count: int = state.get("retry_count", 0)

    log = logger.bind(
        user_id=user_id,
        session_id=state.get("session_id"),
        intent=intent,
        is_retry=is_retry,
        retry_count=retry_count,
    )

    log.info("tool_planner.started")

    # ------------------------------------------------------------------
    # 1. Fetch tool schemas from the in-process registry
    # ------------------------------------------------------------------
    # get_registry_tools() serves from memory on cache-hit (normal path)
    # and connects to MCP server on cache-miss (first request for this role).
    try:
        tools: list[BaseTool] = await get_registry_tools(
            user_id=user_id,
            user_role=user_role,
        )
    except Exception as exc:
        log.error("tool_planner.registry_error", error=str(exc))
        return {
            "tool_error": f"Tool registry unavailable: {exc}",
            "selected_tool": None,
            "tool_input": None,
            "retry_count": retry_count + (1 if is_retry else 0),
        }

    log.debug("tool_planner.tools_loaded", tool_count=len(tools))

    # ------------------------------------------------------------------
    # 2. Build the LLM with bound tools
    # ------------------------------------------------------------------
    # bind_tools() registers the tool schemas so Claude knows the exact
    # shape of each tool's arguments. tool_choice="auto" lets it decide
    # whether to call a tool at all (handles edge cases where the needed
    # data is already in the conversation).
    llm = _get_llm()
    llm_with_tools = llm.bind_tools(tools, tool_choice="auto")

    # ------------------------------------------------------------------
    # 3. Build message list (system prompt + conversation history)
    # ------------------------------------------------------------------
    # On retry, the previous AIMessage (bad tool_use) + ToolMessage (error)
    # are already in state["messages"] — tool_executor appended them.
    # The LLM sees the full failure context without any extra injection.
    messages = _build_messages(state)

    # ------------------------------------------------------------------
    # 4. Invoke the LLM
    # ------------------------------------------------------------------
    try:
        ai_msg: AIMessage = await llm_with_tools.ainvoke(messages)
    except Exception as exc:
        log.error(
            "tool_planner.llm_error",
            error=str(exc),
            error_type=type(exc).__name__,
        )
        return {
            "tool_error": f"LLM call failed during tool planning: {exc}",
            "selected_tool": None,
            "tool_input": None,
            "retry_count": retry_count + (1 if is_retry else 0),
        }

    # ------------------------------------------------------------------
    # 5. Parse the response
    # ------------------------------------------------------------------
    # LangChain already converts Anthropic's raw tool_use JSON into a list
    # of ToolCall dicts: [{"name": str, "args": dict, "id": str}]
    # No manual parsing or regex needed.

    if not ai_msg.tool_calls:
        # The LLM decided no tool call is needed (information already in
        # conversation, or it wants to ask a clarifying question).
        # Let response_generator use the AI message directly.
        log.info(
            "tool_planner.no_tool_selected",
            content_preview=str(ai_msg.content)[:120],
        )
        return {
            "requires_tool": False,
            "selected_tool": None,
            "tool_input": None,
            "tool_error": None,
            "retry_count": retry_count,
            "messages": [ai_msg],
        }

    # Take the first tool call — Claude rarely returns more than one for
    # customer-service queries, and our tool_executor handles one call per turn.
    tool_call = ai_msg.tool_calls[0]
    selected_tool: str = tool_call["name"]
    raw_args: dict = tool_call["args"]

    log.info(
        "tool_planner.tool_selected",
        tool_name=selected_tool,
        raw_args=raw_args,
    )

    # ------------------------------------------------------------------
    # 6. Validate args against the tool's Pydantic schema
    # ------------------------------------------------------------------
    # This is the structured-output validation step: each BaseTool carries
    # an args_schema (Pydantic model) generated from its JSON schema.
    # Validating here — before hitting the MCP server — converts a runtime
    # 422 from the tool server into a clean retry with a useful error message.
    tool_input, validation_error = _validate_tool_args(
        tool_name=selected_tool,
        args=raw_args,
        available_tools=tools,
    )

    if validation_error:
        log.warning(
            "tool_planner.args_validation_failed",
            tool_name=selected_tool,
            validation_error=validation_error,
        )
        # Treat invalid args as a planning error → retry edge will re-invoke
        # this node with the error surfaced in state so the LLM can correct.
        return {
            "tool_error": validation_error,
            "selected_tool": None,
            "tool_input": None,
            "retry_count": retry_count + 1,
            "messages": [ai_msg],  # keep the planning message for LLM context
        }

    log.info(
        "tool_planner.plan_ready",
        tool_name=selected_tool,
        validated_args=tool_input,
        retry_count=retry_count,
    )

    # ------------------------------------------------------------------
    # 7. Return the plan
    # ------------------------------------------------------------------
    return {
        "selected_tool": selected_tool,
        "tool_input": tool_input,
        "tool_error": None,                          # clear any previous error
        "retry_count": retry_count + (1 if is_retry else 0),
        "messages": [ai_msg],                        # append planning message to history
    }
