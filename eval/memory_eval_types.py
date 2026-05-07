from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MemoryRecord:
    id: str
    category: str                        # below_threshold|at_threshold|pair_preservation|incremental|key_entity
    messages: list[dict]                 # [{"role":"human|ai|tool","content":str,"tool_call_id"?:str,"has_tool_calls"?:bool,"tool_name"?:str}]
    summarized_message_count: int        # starting cursor (0 for fresh; >0 for incremental)
    existing_summary: str | None         # None except incremental records
    expected_triggers: bool
    expected_summary_contains: list[str] # entity strings checked case-insensitively
    expected_summary_excludes: list[str] # strings that must NOT appear in summary
    expected_output_token_count_max: int # 300 for all records
    notes: str | None = None


@dataclass
class MemoryResult:
    id: str
    category: str

    # Trigger correctness
    expected_triggers: bool
    actual_triggers: bool
    trigger_correct: bool

    # Summary output
    context_summary: str | None
    output_summarized_count: int         # output["summarized_message_count"]

    # Hard assertions
    contains_passed: bool                # all expected_summary_contains found (case-insensitive)
    excludes_passed: bool                # all expected_summary_excludes absent (case-insensitive)
    pair_preserved: bool                 # boundary does not land on a ToolMessage index

    # Token counts (tiktoken cl100k_base)
    input_token_count: int               # tokens in the messages_to_summarize slice
    output_token_count: int              # tokens in context_summary
    token_reduction_rate: float | None   # None for non-triggered records

    latency_ms: float
    error: str | None                    # uncaught Python exception (should always be None)

    # API token counts via callback_handler
    prompt_tokens: int = 0
    completion_tokens: int = 0
