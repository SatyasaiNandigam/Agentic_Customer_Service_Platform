from __future__ import annotations

from typing import Any

from eval.tool_planner_eval_types import ToolPlannerRecord, ToolPlannerResult

# Tool names that must never appear in a customer-role prediction.
# RBAC is enforced at MCP execution time (JWT headers), not at schema-fetch time —
# so the planner sees the full tool list for all roles and must self-restrict via
# system-prompt role guidance. A non-zero violation count is a genuine planner failure.
ADMIN_TOOL_NAMES: frozenset[str] = frozenset({
    "force_cancel_order",
    "force_initiate_refund",
    "get_all_reviews",
})
SUPPORT_TOOL_NAMES: frozenset[str] = frozenset({
    "get_orders_any_user",
    "get_refund_status_any_user",
    "track_shipment_any_user",
})
NON_CUSTOMER_TOOL_NAMES: frozenset[str] = ADMIN_TOOL_NAMES | SUPPORT_TOOL_NAMES


# ---------------------------------------------------------------------------
# Threshold constants (from EVAL_PLAN.md Phase 2 — Node 4)
# ---------------------------------------------------------------------------

TOOL_SELECTION_ACCURACY_THRESHOLD: float = 0.95
ARGS_COVERAGE_THRESHOLD: float = 0.90
P95_LATENCY_THRESHOLD_MS: float = 1500.0

CATEGORIES: list[str] = ["intent_mapping", "no_tool", "retry", "implicit", "rbac"]


# ---------------------------------------------------------------------------
# Core metrics
# ---------------------------------------------------------------------------

def compute_tool_selection_accuracy(results: list[ToolPlannerResult]) -> float:
    """Fraction of results where predicted_tool == expected_tool."""
    if not results:
        return 0.0
    return round(sum(1 for r in results if r.tool_correct) / len(results), 4)


def compute_args_coverage_rate(results: list[ToolPlannerResult]) -> float:
    """Mean args_covered fraction across records where a tool was both expected and correctly selected.

    Skips no-tool records and records where the wrong tool was selected, since
    args_covered is only meaningful when the tool choice itself was correct.
    """
    eligible = [
        r for r in results
        if r.expected_tool is not None and r.tool_correct and r.tool_input is not None
    ]
    if not eligible:
        return 1.0  # no tool records to check — trivially passes
    return round(sum(r.args_covered for r in eligible) / len(eligible), 4)


def compute_rbac_violation_rate(results: list[ToolPlannerResult]) -> dict[str, Any]:
    """Fraction of customer-role results that selected a non-customer tool.

    A non-zero rate here means the planner hallucinated a tool not in its list,
    which should be structurally impossible but is checked as a sanity gate.
    """
    customer_results = [r for r in results if r.user_role == "customer"]
    if not customer_results:
        return {"rate": 0.0, "count": 0, "total": 0, "violations": []}

    violations = [
        r for r in customer_results
        if r.predicted_tool is not None and r.predicted_tool in NON_CUSTOMER_TOOL_NAMES
    ]
    return {
        "rate": round(len(violations) / len(customer_results), 6),
        "count": len(violations),
        "total": len(customer_results),
        "violations": [{"id": r.id, "predicted_tool": r.predicted_tool} for r in violations],
    }


def compute_per_category_metrics(results: list[ToolPlannerResult]) -> dict[str, dict[str, Any]]:
    """Per-category accuracy and count breakdown."""
    output: dict[str, dict[str, Any]] = {}
    for cat in CATEGORIES:
        subset = [r for r in results if r.category == cat]
        if not subset:
            output[cat] = {"accuracy": 0.0, "count": 0, "errors": 0}
            continue
        correct = sum(1 for r in subset if r.tool_correct)
        errors = sum(1 for r in subset if r.error is not None)
        output[cat] = {
            "accuracy": round(correct / len(subset), 4),
            "count": len(subset),
            "correct": correct,
            "errors": errors,
        }
    return output


def compute_performance_stats(results: list[ToolPlannerResult]) -> dict[str, Any]:
    """Latency (p50, p95, mean, max) and token aggregates."""
    latencies = sorted(r.latency_ms for r in results)
    n = len(latencies)

    def _pct(vals: list[float], p: float) -> float:
        if not vals:
            return 0.0
        idx = int(p / 100 * (len(vals) - 1))
        return round(vals[idx], 1)

    total_prompt = sum(r.prompt_tokens for r in results)
    total_completion = sum(r.completion_tokens for r in results)

    return {
        "latency_ms": {
            "p50": _pct(latencies, 50),
            "p95": _pct(latencies, 95),
            "mean": round(sum(latencies) / n, 1) if n else 0.0,
            "max": round(max(latencies), 1) if latencies else 0.0,
        },
        "tokens": {
            "total_prompt": total_prompt,
            "total_completion": total_completion,
            "avg_prompt_per_call": round(total_prompt / n, 1) if n else 0.0,
            "avg_completion_per_call": round(total_completion / n, 1) if n else 0.0,
        },
    }


# ---------------------------------------------------------------------------
# Full report
# ---------------------------------------------------------------------------

def build_full_report(
    results: list[ToolPlannerResult],
    dataset: list[ToolPlannerRecord],
    run_metadata: dict[str, Any],
) -> dict[str, Any]:
    tool_accuracy = compute_tool_selection_accuracy(results)
    args_coverage = compute_args_coverage_rate(results)
    per_category = compute_per_category_metrics(results)
    perf = compute_performance_stats(results)
    rbac = compute_rbac_violation_rate(results)

    total = len(results)
    errors = sum(1 for r in results if r.error is not None)

    passes_tool = tool_accuracy >= TOOL_SELECTION_ACCURACY_THRESHOLD
    passes_args = args_coverage >= ARGS_COVERAGE_THRESHOLD
    passes_latency = perf["latency_ms"]["p95"] <= P95_LATENCY_THRESHOLD_MS
    passes_rbac = rbac["count"] == 0
    passes_all = passes_tool and passes_args and passes_latency and passes_rbac

    failures = sorted(
        [
            {
                "id": r.id,
                "category": r.category,
                "intent": r.intent,
                "user_role": r.user_role,
                "expected_tool": r.expected_tool,
                "predicted_tool": r.predicted_tool,
                "tool_input": r.tool_input,
                "args_covered": r.args_covered,
                "error": r.error,
                "notes": next((d.notes for d in dataset if d.id == r.id), None),
            }
            for r in results
            if not r.tool_correct
        ],
        key=lambda x: x["category"],
    )

    return {
        "run_metadata": run_metadata,
        "summary": {
            "total_cases": total,
            "errors": errors,
            "tool_selection_accuracy": tool_accuracy,
            "args_coverage_rate": args_coverage,
            "p95_latency_ms": perf["latency_ms"]["p95"],
            "rbac_violations": rbac["count"],
            "passes_all_thresholds": passes_all,
        },
        "thresholds": {
            "tool_selection_accuracy": {
                "value": tool_accuracy,
                "threshold": TOOL_SELECTION_ACCURACY_THRESHOLD,
                "pass": passes_tool,
            },
            "args_coverage_rate": {
                "value": args_coverage,
                "threshold": ARGS_COVERAGE_THRESHOLD,
                "pass": passes_args,
            },
            "p95_latency_ms": {
                "value": perf["latency_ms"]["p95"],
                "threshold": P95_LATENCY_THRESHOLD_MS,
                "pass": passes_latency,
            },
            "rbac_violations": {
                "value": rbac["count"],
                "threshold": 0,
                "pass": passes_rbac,
            },
        },
        "per_category": per_category,
        "rbac": rbac,
        "performance": perf,
        "failures": failures,
    }
