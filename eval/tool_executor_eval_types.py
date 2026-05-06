from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ToolExecutorRecord:
    id: str
    category: str                        # success_read|success_write|limit_destructive|limit_write|limit_total|server_error|no_tool|tool_not_found
    user_id: str                         # numeric string matching seeded DB user_id (e.g. "91")
    user_role: str                       # "customer" | "support_agent" | "admin"
    selected_tool: str | None            # None triggers the no-tool guard path
    tool_input: dict                     # args passed to tool; {} if none
    tool_call_counts: dict               # pre-populated counts; {} for normal runs; non-empty to trigger limits
    expected_success: bool               # True = tool_result non-null AND no "error" key in tool_result
    expected_error_contains: str | None  # substring expected in tool_error (error/limit categories)
    expected_tool_message_appended: bool # False ONLY for no_tool category; True everywhere else
    expected_counts_incremented: bool    # False for no_tool + limit categories; True for success + server_error
    expected_result_keys: list[str]      # keys that must appear in tool_result (success cases only)
    requires_flag: str | None = None     # "include_writes" → skip unless --include-writes passed
    notes: str | None = None


@dataclass
class ToolExecutorResult:
    id: str
    category: str
    selected_tool: str | None
    user_id: str
    user_role: str

    # Raw output from tool_executor_node
    tool_result: dict | None
    tool_error: str | None
    output_counts: dict                  # tool_call_counts from node output

    # Behavioural assertions (True = assertion passed)
    tool_message_appended: bool
    tool_call_id_linked: bool            # ToolMessage.tool_call_id matches synthetic AIMessage id
    counts_incremented_correctly: bool   # matches expected_counts_incremented
    limit_error_correct: bool            # True when not a limit record, or limit msg contains expected substring
    success_correct: bool                # tool_result present + expected_result_keys found (or correctly errored)

    latency_ms: float
    error: str | None                    # uncaught Python exception during eval run (should always be None)
    skipped: bool = False                # True if record was skipped due to missing flag
