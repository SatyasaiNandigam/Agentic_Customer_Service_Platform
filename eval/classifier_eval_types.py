from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ClassifierRecord:
    id: str
    text: str
    expected_intent: str        # one of 12 active IntentType literals (no complaint)
    customer_domain: str        # one of 3: need_information|need_assistance|need_advice
    history: list[dict] | None  # [{"role": "human|ai", "content": str}]; None = no context
    boundary_pair: str | None   # e.g. "order_status|shipment_tracking"; None for core records
    source: str                 # "seed|paraphrase|edge"
    notes: str | None


@dataclass
class ClassifierResult:
    id: str
    text: str
    expected_intent: str
    predicted_intent: str
    customer_domain: str
    confidence: float           # classifier returns confidence; 0.0 on LLM error
    requires_tool: bool
    needs_escalation: bool
    correct: bool
    latency_ms: float
    error: str | None           # "classifier_fallback" | exception str | None
    had_history: bool
    prompt_tokens: int = 0
    completion_tokens: int = 0
