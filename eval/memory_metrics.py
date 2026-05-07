from __future__ import annotations

from typing import Any

from eval.memory_eval_types import MemoryRecord, MemoryResult


# ---------------------------------------------------------------------------
# Threshold constants (EVAL_PLAN.md — Node 6 memory eval)
# ---------------------------------------------------------------------------

TRIGGER_PRECISION_THRESHOLD: float = 1.0    # 100%
TRIGGER_RECALL_THRESHOLD: float = 1.0       # 100%
ENTITY_RETENTION_THRESHOLD: float = 0.95    # >= 95%
PAIR_PRESERVATION_THRESHOLD: float = 1.0    # 100%
TOKEN_REDUCTION_THRESHOLD: float = 0.40     # >= 40% aggregate reduction
# Prompt instructs LLM to produce "under 300 words"; 300 words ≈ 390 tiktoken tokens
# at typical prose density (~1.3 tok/word). 400 aligns threshold with the prompt target.
SUMMARY_LENGTH_MAX_TOKENS: int = 400
SUMMARY_LENGTH_PASS_THRESHOLD: float = 1.0  # 100% of triggered records stay under max

CATEGORIES: list[str] = [
    "below_threshold",
    "at_threshold",
    "pair_preservation",
    "incremental",
    "key_entity",
]


# ---------------------------------------------------------------------------
# Trigger precision / recall
# ---------------------------------------------------------------------------

def compute_trigger_metrics(results: list[MemoryResult]) -> dict[str, Any]:
    """Precision and recall for the summarization trigger decision."""
    tp = sum(1 for r in results if r.expected_triggers and r.actual_triggers)
    fp = sum(1 for r in results if not r.expected_triggers and r.actual_triggers)
    fn = sum(1 for r in results if r.expected_triggers and not r.actual_triggers)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 1.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "passes_precision": precision >= TRIGGER_PRECISION_THRESHOLD,
        "passes_recall": recall >= TRIGGER_RECALL_THRESHOLD,
    }


# ---------------------------------------------------------------------------
# Entity retention
# ---------------------------------------------------------------------------

def compute_entity_retention(results: list[MemoryResult]) -> dict[str, Any]:
    """Fraction of triggered records where all expected_summary_contains strings appear."""
    eligible = [r for r in results if r.expected_triggers and r.actual_triggers]
    if not eligible:
        return {"rate": 1.0, "numerator": 0, "denominator": 0, "passes": True, "failures": []}

    passed = sum(1 for r in eligible if r.contains_passed)
    failures = [
        {"id": r.id, "category": r.category, "summary_preview": (r.context_summary or "")[:200]}
        for r in eligible if not r.contains_passed
    ]
    rate = passed / len(eligible)
    return {
        "rate": round(rate, 4),
        "numerator": passed,
        "denominator": len(eligible),
        "passes": rate >= ENTITY_RETENTION_THRESHOLD,
        "failures": failures,
    }


# ---------------------------------------------------------------------------
# Pair preservation
# ---------------------------------------------------------------------------

def compute_pair_preservation(results: list[MemoryResult]) -> dict[str, Any]:
    """Fraction of pair_preservation records where the boundary cursor lands on a non-ToolMessage."""
    pp_records = [r for r in results if r.category == "pair_preservation"]
    if not pp_records:
        return {"rate": 1.0, "count": 0, "passes": True, "failures": []}

    passed = sum(1 for r in pp_records if r.pair_preserved)
    failures = [
        {"id": r.id, "output_summarized_count": r.output_summarized_count}
        for r in pp_records if not r.pair_preserved
    ]
    rate = passed / len(pp_records)
    return {
        "rate": round(rate, 4),
        "passed": passed,
        "total": len(pp_records),
        "passes": rate >= PAIR_PRESERVATION_THRESHOLD,
        "failures": failures,
    }


# ---------------------------------------------------------------------------
# Token reduction rate
# ---------------------------------------------------------------------------

def compute_token_reduction(results: list[MemoryResult]) -> dict[str, Any]:
    """Aggregate token reduction rate across all triggered records."""
    triggered = [r for r in results if r.actual_triggers and r.input_token_count > 0]
    if not triggered:
        return {"aggregate_rate": 0.0, "triggered_count": 0, "passes": False}

    total_in  = sum(r.input_token_count for r in triggered)
    total_out = sum(r.output_token_count for r in triggered)
    agg_rate  = (total_in - total_out) / total_in if total_in > 0 else 0.0

    per_record = [
        {
            "id": r.id,
            "category": r.category,
            "input_tokens": r.input_token_count,
            "output_tokens": r.output_token_count,
            "reduction_rate": round(r.token_reduction_rate, 4) if r.token_reduction_rate is not None else None,
        }
        for r in triggered
    ]

    return {
        "aggregate_rate": round(agg_rate, 4),
        "total_input_tokens": total_in,
        "total_output_tokens": total_out,
        "triggered_count": len(triggered),
        "passes": agg_rate >= TOKEN_REDUCTION_THRESHOLD,
        "per_record": per_record,
    }


# ---------------------------------------------------------------------------
# Summary length
# ---------------------------------------------------------------------------

def compute_summary_length(results: list[MemoryResult]) -> dict[str, Any]:
    """Fraction of triggered records whose summary is under SUMMARY_LENGTH_MAX_TOKENS."""
    triggered = [r for r in results if r.actual_triggers]
    if not triggered:
        return {"pass_rate": 1.0, "max_seen": 0, "passes": True, "violations": []}

    under_limit = [r for r in triggered if r.output_token_count <= SUMMARY_LENGTH_MAX_TOKENS]
    pass_rate   = len(under_limit) / len(triggered)
    max_seen    = max(r.output_token_count for r in triggered)
    violations  = [
        {"id": r.id, "output_token_count": r.output_token_count}
        for r in triggered if r.output_token_count > SUMMARY_LENGTH_MAX_TOKENS
    ]

    return {
        "pass_rate": round(pass_rate, 4),
        "max_seen": max_seen,
        "max_allowed": SUMMARY_LENGTH_MAX_TOKENS,
        "passes": pass_rate >= SUMMARY_LENGTH_PASS_THRESHOLD,
        "violations": violations,
    }


# ---------------------------------------------------------------------------
# Excludes (PII / internal field protection)
# ---------------------------------------------------------------------------

def compute_excludes_pass_rate(results: list[MemoryResult]) -> dict[str, Any]:
    """Fraction of triggered records where no excluded string appears in the summary."""
    triggered_with_excludes = [
        r for r in results if r.actual_triggers
    ]
    if not triggered_with_excludes:
        return {"pass_rate": 1.0, "passes": True, "failures": []}

    passed   = sum(1 for r in triggered_with_excludes if r.excludes_passed)
    failures = [
        {"id": r.id, "category": r.category, "summary_preview": (r.context_summary or "")[:200]}
        for r in triggered_with_excludes if not r.excludes_passed
    ]
    pass_rate = passed / len(triggered_with_excludes)
    return {
        "pass_rate": round(pass_rate, 4),
        "passes": pass_rate == 1.0,
        "failures": failures,
    }


# ---------------------------------------------------------------------------
# Performance stats
# ---------------------------------------------------------------------------

def compute_performance_stats(results: list[MemoryResult]) -> dict[str, Any]:
    latencies = sorted(r.latency_ms for r in results)
    n = len(latencies)

    def _pct(vals: list[float], p: float) -> float:
        if not vals:
            return 0.0
        return round(vals[int(p / 100 * (len(vals) - 1))], 1)

    triggered = [r for r in results if r.actual_triggers]
    triggered_latencies = sorted(r.latency_ms for r in triggered)

    total_prompt     = sum(r.prompt_tokens for r in results)
    total_completion = sum(r.completion_tokens for r in results)

    return {
        "all_records_latency_ms": {
            "p50": _pct(latencies, 50),
            "p95": _pct(latencies, 95),
            "mean": round(sum(latencies) / n, 1) if n else 0.0,
            "max": round(max(latencies), 1) if latencies else 0.0,
        },
        "triggered_latency_ms": {
            "p50": _pct(triggered_latencies, 50),
            "p95": _pct(triggered_latencies, 95),
            "mean": round(sum(triggered_latencies) / len(triggered_latencies), 1) if triggered_latencies else 0.0,
            "max": round(max(triggered_latencies), 1) if triggered_latencies else 0.0,
        },
        "api_tokens": {
            "total_prompt": total_prompt,
            "total_completion": total_completion,
            "avg_prompt_per_triggered": round(total_prompt / len(triggered), 1) if triggered else 0.0,
            "avg_completion_per_triggered": round(total_completion / len(triggered), 1) if triggered else 0.0,
        },
    }


# ---------------------------------------------------------------------------
# Per-category breakdown
# ---------------------------------------------------------------------------

def compute_per_category_metrics(results: list[MemoryResult]) -> dict[str, Any]:
    breakdown: dict[str, Any] = {}
    for cat in CATEGORIES:
        recs = [r for r in results if r.category == cat]
        if not recs:
            breakdown[cat] = {"count": 0}
            continue
        triggered_count = sum(1 for r in recs if r.actual_triggers)
        breakdown[cat] = {
            "count": len(recs),
            "triggered": triggered_count,
            "trigger_correct": sum(1 for r in recs if r.trigger_correct),
            "contains_passed": sum(1 for r in recs if r.contains_passed),
            "excludes_passed": sum(1 for r in recs if r.excludes_passed),
            "pair_preserved": sum(1 for r in recs if r.pair_preserved),
            "errors": sum(1 for r in recs if r.error is not None),
            "avg_input_tokens": (
                round(sum(r.input_token_count for r in recs if r.actual_triggers)
                      / triggered_count, 1)
                if triggered_count > 0 else None
            ),
            "avg_output_tokens": (
                round(sum(r.output_token_count for r in recs if r.actual_triggers)
                      / triggered_count, 1)
                if triggered_count > 0 else None
            ),
        }
    return breakdown


# ---------------------------------------------------------------------------
# Full report
# ---------------------------------------------------------------------------

def build_full_report(
    results: list[MemoryResult],
    dataset: list[MemoryRecord],
    run_metadata: dict[str, Any],
) -> dict[str, Any]:
    trigger     = compute_trigger_metrics(results)
    entity      = compute_entity_retention(results)
    pair        = compute_pair_preservation(results)
    reduction   = compute_token_reduction(results)
    length      = compute_summary_length(results)
    excludes    = compute_excludes_pass_rate(results)
    perf        = compute_performance_stats(results)
    per_cat     = compute_per_category_metrics(results)

    total            = len(results)
    triggered_count  = sum(1 for r in results if r.actual_triggers)
    error_count      = sum(1 for r in results if r.error is not None)
    passes_all       = all([
        trigger["passes_precision"],
        trigger["passes_recall"],
        entity["passes"],
        pair["passes"],
        reduction["passes"],
        length["passes"],
        excludes["passes"],
    ])

    failures = sorted(
        [
            {
                "id": r.id,
                "category": r.category,
                "expected_triggers": r.expected_triggers,
                "actual_triggers": r.actual_triggers,
                "trigger_correct": r.trigger_correct,
                "contains_passed": r.contains_passed,
                "excludes_passed": r.excludes_passed,
                "pair_preserved": r.pair_preserved,
                "output_token_count": r.output_token_count,
                "token_reduction_rate": r.token_reduction_rate,
                "error": r.error,
            }
            for r in results
            if not r.trigger_correct
            or not r.contains_passed
            or not r.excludes_passed
            or not r.pair_preserved
            or (r.actual_triggers and r.output_token_count > SUMMARY_LENGTH_MAX_TOKENS)
            or r.error is not None
        ],
        key=lambda x: x["category"],
    )

    return {
        "run_metadata": run_metadata,
        "summary": {
            "total_records": total,
            "triggered_count": triggered_count,
            "error_count": error_count,
            "passes_all_thresholds": passes_all,
        },
        "thresholds": {
            "trigger_precision": {
                "value": trigger["precision"],
                "threshold": TRIGGER_PRECISION_THRESHOLD,
                "pass": trigger["passes_precision"],
            },
            "trigger_recall": {
                "value": trigger["recall"],
                "threshold": TRIGGER_RECALL_THRESHOLD,
                "pass": trigger["passes_recall"],
            },
            "entity_retention": {
                "value": entity["rate"],
                "threshold": ENTITY_RETENTION_THRESHOLD,
                "pass": entity["passes"],
            },
            "pair_preservation": {
                "value": pair["rate"],
                "threshold": PAIR_PRESERVATION_THRESHOLD,
                "pass": pair["passes"],
            },
            "token_reduction_rate": {
                "value": reduction["aggregate_rate"],
                "threshold": TOKEN_REDUCTION_THRESHOLD,
                "pass": reduction["passes"],
            },
            "summary_length_pass_rate": {
                "value": length["pass_rate"],
                "threshold": SUMMARY_LENGTH_PASS_THRESHOLD,
                "max_tokens_allowed": SUMMARY_LENGTH_MAX_TOKENS,
                "max_tokens_seen": length["max_seen"],
                "pass": length["passes"],
            },
            "excludes_pass_rate": {
                "value": excludes["pass_rate"],
                "threshold": 1.0,
                "pass": excludes["passes"],
            },
        },
        "trigger_detail": trigger,
        "token_reduction": reduction,
        "performance": perf,
        "per_category": per_cat,
        "failures": failures,
    }
