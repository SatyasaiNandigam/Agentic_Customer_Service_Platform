from dataclasses import dataclass


@dataclass
class EvalRecord:
    id: str
    text: str
    expected: str
    source: str
    boundary_pair: str | None
    notes: str | None


@dataclass
class EvalResult:
    id: str
    text: str
    expected: str
    predicted: str
    confidence: float
    requires_tool: bool
    needs_escalation: bool
    correct: bool
    latency_ms: float
    error: str | None  # "classifier_fallback" | exception str | None
