from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DelegatorRecord:
    id: str
    text: str
    expected_domain: str       # one of 5 CustomerDomain literals
    history: list[dict] | None  # [{"role": "human|ai", "content": str}]; None = no context
    boundary_pair: str | None  # e.g. "need_information|need_advice"; None for core records
    source: str                # "seed|paraphrase|edge|adversarial"
    notes: str | None


@dataclass
class DelegatorResult:
    id: str
    text: str
    expected_domain: str
    predicted_domain: str
    confidence: float          # always 0.0 — node strips confidence from its output dict
    correct: bool
    latency_ms: float
    error: str | None          # outer exception string, or None
    had_history: bool          # enables history-vs-no-history accuracy breakdown
    prompt_tokens: int = 0
    completion_tokens: int = 0
