from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ToolPlannerRecord:
    id: str
    messages: list[dict]           # [{"role": "human|ai|ai_tool_call|tool", ...}]
    intent: str
    user_role: str                 # "customer" | "support_agent" | "admin"
    expected_tool: str | None      # None = no-tool expected
    expected_args_schema: dict     # {"field": "type_hint"} — required arg keys to check
    expected_no_tool: bool
    category: str                  # "intent_mapping|no_tool|retry|implicit|rbac"
    tool_error: str | None = None  # pre-set tool_error for retry scenarios
    tool_retry_count: int = 0      # pre-set retry count for retry scenarios
    notes: str | None = None


@dataclass
class ToolPlannerResult:
    id: str
    category: str
    intent: str
    user_role: str
    expected_tool: str | None
    predicted_tool: str | None
    tool_correct: bool
    tool_input: dict | None
    args_covered: float            # fraction of expected_args_schema keys present in tool_input
    latency_ms: float
    error: str | None
    prompt_tokens: int = 0
    completion_tokens: int = 0
