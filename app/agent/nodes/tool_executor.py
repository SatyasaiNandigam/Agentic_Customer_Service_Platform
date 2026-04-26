from __future__ import annotations

import json
import structlog
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage

from app.agent.state import AgentState
from app.config import get_settings
from app.mcp_client.client import mcp_client_for_user

logger = structlog.get_logger(__name__)


_WRITE_TOOLS: frozenset[str] = frozenset({"initiate_refund", "cancel_order"})
_DESTRUCTIVE_TOOLS: frozenset[str] = frozenset({"cancel_order"})


def _classify_tool(tool_name: str) -> str:
    """Return 'destructive', 'write', or 'read' for a given tool name."""
    if tool_name in _DESTRUCTIVE_TOOLS:
        return "destructive"
    if tool_name in _WRITE_TOOLS:
        return "write"
    return "read"



def _check_tool_limits(
    tool_name: str,
    current_counts: dict[str, int],
) -> str | None:
    """Return an error string if a per-turn call limit would be exceeded, else None.

    Checks are applied in order: destructive → write → read (total).
    The read limit acts as an absolute cap on all tool calls per turn.

    Args:
        tool_name:      Name of the tool about to be called.
        current_counts: ``state["tool_call_counts"]`` before this execution.

    Returns:
        Human-readable limit-exceeded message, or None if execution is allowed.
    """
    settings = get_settings()
    tool_type = _classify_tool(tool_name)

    if tool_type == "destructive":
        destructive_total = sum(
            current_counts.get(t, 0) for t in _DESTRUCTIVE_TOOLS
        )
        if destructive_total >= settings.agent_tool_destructive_limit:
            return (
                f"Destructive tool limit reached "
                f"({settings.agent_tool_destructive_limit} per turn). "
                f"Cannot call '{tool_name}' again this turn."
            )

    if tool_type in ("write", "destructive"):
        write_total = sum(current_counts.get(t, 0) for t in _WRITE_TOOLS)
        if write_total >= settings.agent_tool_write_limit:
            return (
                f"Write tool limit reached "
                f"({settings.agent_tool_write_limit} per turn). "
                f"Cannot call '{tool_name}' again this turn."
            )

    # Total call cap covers all tool types
    total_calls = sum(current_counts.values())
    if total_calls >= settings.agent_tool_read_limit:
        return (
            f"Tool call limit reached "
            f"({settings.agent_tool_read_limit} per turn). "
            f"Cannot call '{tool_name}' again this turn."
        )

    return None


def _extract_tool_call_id(messages: list[BaseMessage], tool_name: str | None) -> str:
    """Find the tool_call_id from the most recent AIMessage with a matching tool_call.

    LangChain requires ``ToolMessage.tool_call_id`` to match the ``id`` in the
    preceding ``AIMessage.tool_calls`` entry.  We search backwards so we always
    find the most recent planning step (handles multi-retry flows correctly).

    Args:
        messages:  ``state["messages"]`` after tool_planner has appended its AIMessage.
        tool_name: Name of the selected tool.  Used to find the exact ToolCall entry.

    Returns:
        The ``id`` string, or a fallback sentinel if none is found (shouldn't
        happen in normal graph flow but avoids a hard crash).
    """
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                if tool_name is None or tc["name"] == tool_name:
                    return tc["id"]
    # Fallback — graph invariant violation; log a warning upstream
    return "unknown_tool_call_id"


def _serialise_result(result: Any) -> tuple[dict, str]:
    """Convert a tool result into (structured_dict, content_string) for state + ToolMessage.

    Args:
        result: Raw return value from ``tool.ainvoke()``.

    Returns:
        Tuple of:
          - ``tool_result`` dict (stored in state for response_generator grounding)
          - ``content`` string (stored in ToolMessage for LLM context)
    """
    if isinstance(result, dict):
        return result, json.dumps(result, default=str, ensure_ascii=False)
    if isinstance(result, list):
        wrapper = {"results": result}
        return wrapper, json.dumps(wrapper, default=str, ensure_ascii=False)
    # Scalar / string — wrap so tool_result is always a dict
    str_result = str(result)
    return {"output": str_result}, str_result


async def tool_executor_node(state: AgentState) -> dict:
    """Execute the MCP tool selected by tool_planner and record the outcome.

    Node contract:
        Input:  AgentState — reads selected_tool, tool_input, user_id, user_role,
                tool_call_counts, messages.
        Output: Partial state dict — updates tool_result OR tool_error,
                tool_call_counts, and messages (appends ToolMessage).

    The node never raises — all exceptions (tool errors, MCP connection failures,
    limit violations) are captured as ``tool_error`` so ``route_after_tool_executor``
    can decide between retry and graceful fallback.

    Args:
        state: Current AgentState.

    Returns:
        Partial state dict with execution results.
    """
    selected_tool: str | None = state.get("selected_tool")
    tool_input: dict = state.get("tool_input") or {}
    user_id: int = state["user_id"]
    user_role: str = state["user_role"]
    tool_call_counts: dict[str, int] = dict(state.get("tool_call_counts") or {})

    log = logger.bind(
        user_id=user_id,
        session_id=state.get("session_id"),
        selected_tool=selected_tool,
        intent=state.get("intent"),
    )

   
    if not selected_tool:
        log.error("tool_executor.no_tool_selected")
        return {
            "tool_result": None,
            "tool_error": "tool_executor called with no selected_tool in state",
            "tool_call_counts": tool_call_counts,
        }

  
    limit_error = _check_tool_limits(selected_tool, tool_call_counts)
    if limit_error:
        log.warning(
            "tool_executor.limit_exceeded",
            tool_name=selected_tool,
            tool_type=_classify_tool(selected_tool),
            counts=tool_call_counts,
            error=limit_error,
        )
        tool_call_id = _extract_tool_call_id(state["messages"], selected_tool)
        return {
            "tool_result": None,
            "tool_error": limit_error,
            "tool_call_counts": tool_call_counts,
            "messages": [
                ToolMessage(content=f"Limit error: {limit_error}", tool_call_id=tool_call_id)
            ],
        }


    tool_call_id = _extract_tool_call_id(state["messages"], selected_tool)

    log.info(
        "tool_executor.started",
        tool_name=selected_tool,
        tool_type=_classify_tool(selected_tool),
        tool_call_id=tool_call_id,
        args_keys=list(tool_input.keys()),
    )

    # ------------------------------------------------------------------
    # Execute via MCP
    # ------------------------------------------------------------------
    # A fresh SSE connection is opened per graph invocation, scoped to the
    # authenticated user's headers.  The connection is torn down on exit
    # regardless of success or failure (context manager guarantee).
    try:
        async with mcp_client_for_user(user_id=user_id, user_role=user_role) as client:
            tools = await client.get_tools()

            matched = next((t for t in tools if t.name == selected_tool), None)
            if matched is None:
                raise ValueError(
                    f"Tool '{selected_tool}' not found in MCP server registry. "
                    f"Available: {[t.name for t in tools]}"
                )

            log.debug("tool_executor.invoking", tool_name=selected_tool, args=tool_input)
            raw_result = await matched.ainvoke(tool_input)

        # ------------------------------------------------------------------
        # Success path
        # ------------------------------------------------------------------
        tool_result, content_str = _serialise_result(raw_result)
        tool_call_counts[selected_tool] = tool_call_counts.get(selected_tool, 0) + 1

        log.info(
            "tool_executor.success",
            tool_name=selected_tool,
            result_keys=list(tool_result.keys()) if isinstance(tool_result, dict) else None,
            call_count=tool_call_counts[selected_tool],
        )

        return {
            "tool_result": tool_result,
            "tool_error": None,
            "tool_call_counts": tool_call_counts,
            "messages": [
                ToolMessage(content=content_str, tool_call_id=tool_call_id)
            ],
        }

    except Exception as exc:
        # ------------------------------------------------------------------
        # Error path — record error but do NOT raise so the graph continues
        # ------------------------------------------------------------------
        error_str = f"{type(exc).__name__}: {exc}"
        tool_call_counts[selected_tool] = tool_call_counts.get(selected_tool, 0) + 1

        log.error(
            "tool_executor.error",
            tool_name=selected_tool,
            error=error_str,
            call_count=tool_call_counts[selected_tool],
        )

        # Append a ToolMessage even on error — required by LangChain's message
        # schema and gives the LLM full context for the retry decision.
        return {
            "tool_result": None,
            "tool_error": error_str,
            "tool_call_counts": tool_call_counts,
            "messages": [
                ToolMessage(
                    content=f"Tool execution failed: {error_str}",
                    tool_call_id=tool_call_id,
                )
            ],
        }
