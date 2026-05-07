from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ResponseGeneratorRecord:
    id: str
    category: str               # tool_result|tool_error|direct|rewrite
    intent: str
    response_path: str          # tool_result|tool_error|direct (drives state construction)
    messages: list[dict]        # [{"role":"human|ai","content":str}]
    must_contain: list[str]     # case-insensitive substrings that MUST appear in response
    must_not_contain: list[str] # case-insensitive substrings that must NOT appear
    tool_result: dict | None = None
    tool_error: str | None = None
    context_summary: str | None = None
    guardrail_violation: str | None = None
    output_retry_count: int = 0
    expected_off_topic_refusal: bool = False  # for direct/unknown path records
    geval_criteria: str | None = None         # custom GEval criteria; path default used when None
    notes: str | None = None


@dataclass
class ResponseGeneratorResult:
    id: str
    category: str
    intent: str
    response_path: str

    # Generated response
    response: str | None

    # Hard assertion results
    must_contain_passed: bool
    must_contain_failures: list[str]   # which must_contain strings were missing
    must_not_contain_passed: bool
    must_not_contain_failures: list[str]  # which must_not_contain strings were found

    # Off-topic refusal (for expected_off_topic_refusal=True records)
    expected_off_topic_refusal: bool
    is_off_topic_refusal: bool  # heuristic keyword detection

    # GEval scores — non-blocking, informational only
    geval_score: float | None = None
    geval_reason: str | None = None
    geval_error: str | None = None

    # Performance
    latency_ms: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    error: str | None = None  # uncaught Python exception (should always be None)
