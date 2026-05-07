from __future__ import annotations

from typing import Any

from eval.response_generator_eval_types import ResponseGeneratorRecord, ResponseGeneratorResult


# ---------------------------------------------------------------------------
# Threshold constants (EVAL_PLAN.md — Node 7 response_generator eval)
# ---------------------------------------------------------------------------

MUST_CONTAIN_THRESHOLD: float = 0.98       # >= 98%  — hard, blocking
MUST_NOT_CONTAIN_THRESHOLD: float = 1.0    # 100%    — hard, blocking
OFF_TOPIC_REFUSAL_THRESHOLD: float = 0.99  # >= 99%  — hard, blocking
GEVAL_SCORE_THRESHOLD: float = 0.7         # informational only (non-blocking)

CATEGORIES: list[str] = ["tool_result", "tool_error", "direct", "rewrite"]


# ---------------------------------------------------------------------------
# must_contain pass rate
# ---------------------------------------------------------------------------

def compute_must_contain_pass_rate(results: list[ResponseGeneratorResult]) -> dict[str, Any]:
    """Fraction of records where all must_contain strings appear in the response."""
    eligible = [r for r in results if r.must_contain_failures is not None]
    if not eligible:
        return {"pass_rate": 1.0, "passed": 0, "total": 0, "passes": True, "failures": []}

    passed = sum(1 for r in eligible if r.must_contain_passed)
    failures = [
        {
            "id": r.id,
            "category": r.category,
            "intent": r.intent,
            "missing": r.must_contain_failures,
            "response_preview": (r.response or "")[:200],
        }
        for r in eligible if not r.must_contain_passed
    ]
    rate = passed / len(eligible)
    return {
        "pass_rate": round(rate, 4),
        "passed": passed,
        "total": len(eligible),
        "passes": rate >= MUST_CONTAIN_THRESHOLD,
        "failures": failures,
    }


# ---------------------------------------------------------------------------
# must_not_contain pass rate
# ---------------------------------------------------------------------------

def compute_must_not_contain_pass_rate(results: list[ResponseGeneratorResult]) -> dict[str, Any]:
    """Fraction of records where no must_not_contain string appears in the response."""
    if not results:
        return {"pass_rate": 1.0, "passed": 0, "total": 0, "passes": True, "failures": []}

    passed = sum(1 for r in results if r.must_not_contain_passed)
    failures = [
        {
            "id": r.id,
            "category": r.category,
            "intent": r.intent,
            "leaked": r.must_not_contain_failures,
            "response_preview": (r.response or "")[:200],
        }
        for r in results if not r.must_not_contain_passed
    ]
    rate = passed / len(results)
    return {
        "pass_rate": round(rate, 4),
        "passed": passed,
        "total": len(results),
        "passes": rate >= MUST_NOT_CONTAIN_THRESHOLD,
        "failures": failures,
    }


# ---------------------------------------------------------------------------
# Off-topic refusal rate
# ---------------------------------------------------------------------------

def compute_off_topic_refusal_rate(results: list[ResponseGeneratorResult]) -> dict[str, Any]:
    """For records with expected_off_topic_refusal=True, fraction that correctly refused."""
    eligible = [r for r in results if r.expected_off_topic_refusal]
    if not eligible:
        return {"rate": 1.0, "passed": 0, "total": 0, "passes": True, "failures": []}

    passed = sum(1 for r in eligible if r.is_off_topic_refusal)
    failures = [
        {
            "id": r.id,
            "intent": r.intent,
            "response_preview": (r.response or "")[:300],
        }
        for r in eligible if not r.is_off_topic_refusal
    ]
    rate = passed / len(eligible)
    return {
        "rate": round(rate, 4),
        "passed": passed,
        "total": len(eligible),
        "passes": rate >= OFF_TOPIC_REFUSAL_THRESHOLD,
        "failures": failures,
    }


# ---------------------------------------------------------------------------
# GEval summary (non-blocking, informational)
# ---------------------------------------------------------------------------

def compute_geval_summary(results: list[ResponseGeneratorResult]) -> dict[str, Any]:
    """Aggregate GEval scores across all records that were evaluated."""
    scored = [r for r in results if r.geval_score is not None]
    errors = [r for r in results if r.geval_error is not None]

    if not scored:
        return {
            "evaluated": 0,
            "errors": len(errors),
            "avg_score": None,
            "below_threshold": 0,
            "threshold": GEVAL_SCORE_THRESHOLD,
            "passes": True,  # non-blocking — always passes
            "per_path": {},
        }

    avg = sum(r.geval_score for r in scored) / len(scored)
    below = [r for r in scored if r.geval_score < GEVAL_SCORE_THRESHOLD]

    per_path: dict[str, Any] = {}
    for path in ("tool_result", "tool_error", "direct"):
        path_scored = [r for r in scored if r.response_path == path]
        if path_scored:
            per_path[path] = {
                "count": len(path_scored),
                "avg_score": round(sum(r.geval_score for r in path_scored) / len(path_scored), 4),
                "below_threshold": sum(1 for r in path_scored if r.geval_score < GEVAL_SCORE_THRESHOLD),
            }

    return {
        "evaluated": len(scored),
        "errors": len(errors),
        "avg_score": round(avg, 4),
        "below_threshold": len(below),
        "threshold": GEVAL_SCORE_THRESHOLD,
        "passes": True,  # GEval is non-blocking — informational only
        "per_path": per_path,
        "low_scorers": [
            {"id": r.id, "score": r.geval_score, "reason": (r.geval_reason or "")[:200]}
            for r in sorted(below, key=lambda x: x.geval_score or 0)[:10]
        ],
    }


# ---------------------------------------------------------------------------
# Performance stats
# ---------------------------------------------------------------------------

def compute_performance_stats(results: list[ResponseGeneratorResult]) -> dict[str, Any]:
    latencies = sorted(r.latency_ms for r in results if r.error is None)
    n = len(latencies)

    def _pct(vals: list[float], p: float) -> float:
        if not vals:
            return 0.0
        return round(vals[int(p / 100 * (len(vals) - 1))], 1)

    total_prompt = sum(r.prompt_tokens for r in results)
    total_completion = sum(r.completion_tokens for r in results)

    return {
        "latency_ms": {
            "p50": _pct(latencies, 50),
            "p95": _pct(latencies, 95),
            "mean": round(sum(latencies) / n, 1) if n else 0.0,
            "max": round(max(latencies), 1) if latencies else 0.0,
        },
        "api_tokens": {
            "total_prompt": total_prompt,
            "total_completion": total_completion,
            "avg_prompt": round(total_prompt / n, 1) if n else 0.0,
            "avg_completion": round(total_completion / n, 1) if n else 0.0,
        },
    }


# ---------------------------------------------------------------------------
# Per-category breakdown
# ---------------------------------------------------------------------------

def compute_per_category_metrics(results: list[ResponseGeneratorResult]) -> dict[str, Any]:
    breakdown: dict[str, Any] = {}
    for cat in CATEGORIES:
        recs = [r for r in results if r.category == cat]
        if not recs:
            breakdown[cat] = {"count": 0}
            continue
        scored = [r for r in recs if r.geval_score is not None]
        breakdown[cat] = {
            "count": len(recs),
            "must_contain_passed": sum(1 for r in recs if r.must_contain_passed),
            "must_not_contain_passed": sum(1 for r in recs if r.must_not_contain_passed),
            "refusal_correct": sum(
                1 for r in recs
                if not r.expected_off_topic_refusal or r.is_off_topic_refusal
            ),
            "errors": sum(1 for r in recs if r.error is not None),
            "avg_latency_ms": round(
                sum(r.latency_ms for r in recs) / len(recs), 1
            ),
            "avg_geval_score": (
                round(sum(r.geval_score for r in scored) / len(scored), 4)
                if scored else None
            ),
        }
    return breakdown


# ---------------------------------------------------------------------------
# Full report
# ---------------------------------------------------------------------------

def build_full_report(
    results: list[ResponseGeneratorResult],
    dataset: list[ResponseGeneratorRecord],
    run_metadata: dict[str, Any],
) -> dict[str, Any]:
    mc = compute_must_contain_pass_rate(results)
    mnc = compute_must_not_contain_pass_rate(results)
    refusal = compute_off_topic_refusal_rate(results)
    geval = compute_geval_summary(results)
    perf = compute_performance_stats(results)
    per_cat = compute_per_category_metrics(results)

    passes_all = mc["passes"] and mnc["passes"] and refusal["passes"]

    all_failures = [
        {
            "id": r.id,
            "category": r.category,
            "intent": r.intent,
            "response_path": r.response_path,
            "must_contain_passed": r.must_contain_passed,
            "must_contain_failures": r.must_contain_failures,
            "must_not_contain_passed": r.must_not_contain_passed,
            "must_not_contain_failures": r.must_not_contain_failures,
            "expected_off_topic_refusal": r.expected_off_topic_refusal,
            "is_off_topic_refusal": r.is_off_topic_refusal,
            "error": r.error,
            "response_preview": (r.response or "")[:300],
        }
        for r in results
        if not r.must_contain_passed
        or not r.must_not_contain_passed
        or (r.expected_off_topic_refusal and not r.is_off_topic_refusal)
        or r.error is not None
    ]

    return {
        "run_metadata": run_metadata,
        "summary": {
            "total_records": len(results),
            "error_count": sum(1 for r in results if r.error is not None),
            "passes_all_thresholds": passes_all,
        },
        "thresholds": {
            "must_contain_pass_rate": {
                "value": mc["pass_rate"],
                "threshold": MUST_CONTAIN_THRESHOLD,
                "pass": mc["passes"],
            },
            "must_not_contain_pass_rate": {
                "value": mnc["pass_rate"],
                "threshold": MUST_NOT_CONTAIN_THRESHOLD,
                "pass": mnc["passes"],
            },
            "off_topic_refusal_rate": {
                "value": refusal["rate"],
                "threshold": OFF_TOPIC_REFUSAL_THRESHOLD,
                "total_eligible": refusal["total"],
                "pass": refusal["passes"],
            },
        },
        "geval_summary": geval,
        "performance": perf,
        "per_category": per_cat,
        "failures": all_failures,
    }
