from __future__ import annotations

from typing import Any

from eval.tool_executor_eval_types import ToolExecutorRecord, ToolExecutorResult


# ---------------------------------------------------------------------------
# Threshold constants (from plan — Node 5 tool_executor eval)
# ---------------------------------------------------------------------------

LIMIT_ENFORCEMENT_THRESHOLD: float = 1.0       # 100%
EXCEPTION_CAPTURE_THRESHOLD: float = 1.0        # 100% (no uncaught exceptions)
TOOL_MESSAGE_RATE_THRESHOLD: float = 1.0        # 100%
NO_TOOL_GUARD_THRESHOLD: float = 1.0            # 100%
TOOL_CALL_ID_LINKAGE_THRESHOLD: float = 1.0     # 100%
COUNTS_INCREMENT_THRESHOLD: float = 1.0         # 100%
SUCCESS_READ_RATE_THRESHOLD: float = 0.90       # >= 90%
P95_LATENCY_THRESHOLD_MS: float = 3000.0        # ms, success_read records only (SSE + DB round-trip; 2000 had only 65ms headroom)

CATEGORIES: list[str] = [
    "success_read",
    "success_write",
    "limit_destructive",
    "limit_write",
    "limit_total",
    "server_error",
    "no_tool",
    "tool_not_found",
]

_LIMIT_CATEGORIES: frozenset[str] = frozenset({"limit_destructive", "limit_write", "limit_total"})


# ---------------------------------------------------------------------------
# Core metrics
# ---------------------------------------------------------------------------

def compute_limit_enforcement_rate(results: list[ToolExecutorResult]) -> dict[str, Any]:
    """Fraction of limit records where tool_error contains the expected limit substring."""
    limit_records = [r for r in results if r.category in _LIMIT_CATEGORIES and not r.skipped]
    if not limit_records:
        return {"rate": 1.0, "count": 0, "failures": []}
    passed = sum(1 for r in limit_records if r.limit_error_correct)
    failures = [
        {"id": r.id, "category": r.category, "tool_error": r.tool_error}
        for r in limit_records if not r.limit_error_correct
    ]
    return {
        "rate": round(passed / len(limit_records), 4),
        "passed": passed,
        "total": len(limit_records),
        "failures": failures,
    }


def compute_exception_capture_rate(results: list[ToolExecutorResult]) -> dict[str, Any]:
    """Fraction of non-skipped records that completed without an uncaught Python exception."""
    eligible = [r for r in results if not r.skipped]
    if not eligible:
        return {"rate": 1.0, "uncaught_count": 0, "failures": []}
    captured = sum(1 for r in eligible if r.error is None)
    failures = [
        {"id": r.id, "category": r.category, "error": r.error}
        for r in eligible if r.error is not None
    ]
    return {
        "rate": round(captured / len(eligible), 4),
        "captured": captured,
        "total": len(eligible),
        "uncaught_count": len(failures),
        "failures": failures,
    }


def compute_tool_message_rate(results: list[ToolExecutorResult]) -> dict[str, Any]:
    """Fraction of non-no_tool, non-skipped records where a ToolMessage was appended."""
    eligible = [r for r in results if r.category != "no_tool" and not r.skipped]
    if not eligible:
        return {"rate": 1.0, "count": 0, "failures": []}
    passed = sum(1 for r in eligible if r.tool_message_appended)
    failures = [
        {"id": r.id, "category": r.category}
        for r in eligible if not r.tool_message_appended
    ]
    return {
        "rate": round(passed / len(eligible), 4),
        "passed": passed,
        "total": len(eligible),
        "failures": failures,
    }


def compute_no_tool_guard_rate(results: list[ToolExecutorResult]) -> dict[str, Any]:
    """Fraction of no_tool records where tool_error is set AND no ToolMessage was appended."""
    no_tool = [r for r in results if r.category == "no_tool" and not r.skipped]
    if not no_tool:
        return {"rate": 1.0, "count": 0, "failures": []}
    passed = sum(
        1 for r in no_tool
        if r.tool_error is not None and not r.tool_message_appended
    )
    failures = [
        {
            "id": r.id,
            "tool_error": r.tool_error,
            "tool_message_appended": r.tool_message_appended,
        }
        for r in no_tool
        if not (r.tool_error is not None and not r.tool_message_appended)
    ]
    return {
        "rate": round(passed / len(no_tool), 4),
        "passed": passed,
        "total": len(no_tool),
        "failures": failures,
    }


def compute_tool_call_id_linkage_rate(results: list[ToolExecutorResult]) -> dict[str, Any]:
    """Fraction of records with a ToolMessage where tool_call_id matches the synthetic AIMessage id."""
    with_message = [
        r for r in results
        if r.tool_message_appended and not r.skipped
    ]
    if not with_message:
        return {"rate": 1.0, "count": 0, "failures": []}
    passed = sum(1 for r in with_message if r.tool_call_id_linked)
    failures = [
        {"id": r.id, "category": r.category}
        for r in with_message if not r.tool_call_id_linked
    ]
    return {
        "rate": round(passed / len(with_message), 4),
        "passed": passed,
        "total": len(with_message),
        "failures": failures,
    }


def compute_counts_increment_accuracy(results: list[ToolExecutorResult]) -> dict[str, Any]:
    """Fraction of non-skipped records where counts were incremented exactly as expected."""
    eligible = [r for r in results if not r.skipped]
    if not eligible:
        return {"rate": 1.0, "count": 0, "failures": []}
    passed = sum(1 for r in eligible if r.counts_incremented_correctly)
    failures = [
        {
            "id": r.id,
            "category": r.category,
            "selected_tool": r.selected_tool,
            "output_counts": r.output_counts,
        }
        for r in eligible if not r.counts_incremented_correctly
    ]
    return {
        "rate": round(passed / len(eligible), 4),
        "passed": passed,
        "total": len(eligible),
        "failures": failures,
    }


def compute_success_read_rate(results: list[ToolExecutorResult]) -> dict[str, Any]:
    """Fraction of success_read records where tool_result is non-null and expected keys are present."""
    read_records = [r for r in results if r.category == "success_read" and not r.skipped]
    if not read_records:
        return {"rate": 1.0, "count": 0, "failures": []}
    passed = sum(1 for r in read_records if r.success_correct)
    failures = [
        {
            "id": r.id,
            "tool_result_keys": list(r.tool_result.keys()) if r.tool_result else None,
            "tool_error": r.tool_error,
        }
        for r in read_records if not r.success_correct
    ]
    return {
        "rate": round(passed / len(read_records), 4),
        "passed": passed,
        "total": len(read_records),
        "failures": failures,
    }


def compute_performance_stats(results: list[ToolExecutorResult]) -> dict[str, Any]:
    """Latency stats for success_read records (wall-clock time per tool call)."""
    success_read = [
        r for r in results
        if r.category == "success_read" and not r.skipped and r.error is None
    ]
    all_latencies = sorted(r.latency_ms for r in results if not r.skipped and r.error is None)
    read_latencies = sorted(r.latency_ms for r in success_read)

    def _pct(vals: list[float], p: float) -> float:
        if not vals:
            return 0.0
        idx = int(p / 100 * (len(vals) - 1))
        return round(vals[idx], 1)

    n_all = len(all_latencies)
    n_read = len(read_latencies)

    return {
        "success_read_latency_ms": {
            "p50": _pct(read_latencies, 50),
            "p95": _pct(read_latencies, 95),
            "mean": round(sum(read_latencies) / n_read, 1) if n_read else 0.0,
            "max": round(max(read_latencies), 1) if read_latencies else 0.0,
            "count": n_read,
        },
        "all_latency_ms": {
            "p50": _pct(all_latencies, 50),
            "p95": _pct(all_latencies, 95),
            "mean": round(sum(all_latencies) / n_all, 1) if n_all else 0.0,
            "max": round(max(all_latencies), 1) if all_latencies else 0.0,
            "count": n_all,
        },
    }


def compute_per_category_metrics(results: list[ToolExecutorResult]) -> dict[str, dict[str, Any]]:
    """Per-category pass rates and counts."""
    output: dict[str, dict[str, Any]] = {}
    for cat in CATEGORIES:
        subset = [r for r in results if r.category == cat and not r.skipped]
        skipped = sum(1 for r in results if r.category == cat and r.skipped)
        if not subset:
            output[cat] = {"count": 0, "skipped": skipped}
            continue
        uncaught = sum(1 for r in subset if r.error is not None)
        output[cat] = {
            "count": len(subset),
            "skipped": skipped,
            "uncaught_errors": uncaught,
            "tool_message_appended": sum(1 for r in subset if r.tool_message_appended),
            "counts_correct": sum(1 for r in subset if r.counts_incremented_correctly),
            "success_correct": sum(1 for r in subset if r.success_correct),
        }
    return output


# ---------------------------------------------------------------------------
# Full report
# ---------------------------------------------------------------------------

def build_full_report(
    results: list[ToolExecutorResult],
    dataset: list[ToolExecutorRecord],
    run_metadata: dict[str, Any],
) -> dict[str, Any]:
    limit_enf = compute_limit_enforcement_rate(results)
    exc_cap   = compute_exception_capture_rate(results)
    msg_rate  = compute_tool_message_rate(results)
    no_tool   = compute_no_tool_guard_rate(results)
    id_link   = compute_tool_call_id_linkage_rate(results)
    counts    = compute_counts_increment_accuracy(results)
    read_rate = compute_success_read_rate(results)
    perf      = compute_performance_stats(results)
    per_cat   = compute_per_category_metrics(results)

    passes_limit   = limit_enf["rate"] >= LIMIT_ENFORCEMENT_THRESHOLD
    passes_exc     = exc_cap["rate"] >= EXCEPTION_CAPTURE_THRESHOLD
    passes_msg     = msg_rate["rate"] >= TOOL_MESSAGE_RATE_THRESHOLD
    passes_no_tool = no_tool["rate"] >= NO_TOOL_GUARD_THRESHOLD
    passes_link    = id_link["rate"] >= TOOL_CALL_ID_LINKAGE_THRESHOLD
    passes_counts  = counts["rate"] >= COUNTS_INCREMENT_THRESHOLD
    passes_read    = read_rate["rate"] >= SUCCESS_READ_RATE_THRESHOLD
    passes_latency = perf["success_read_latency_ms"]["p95"] <= P95_LATENCY_THRESHOLD_MS
    passes_all = all([
        passes_limit, passes_exc, passes_msg, passes_no_tool,
        passes_link, passes_counts, passes_read, passes_latency,
    ])

    total = len(results)
    skipped = sum(1 for r in results if r.skipped)

    return {
        "run_metadata": run_metadata,
        "summary": {
            "total_cases": total,
            "skipped": skipped,
            "evaluated": total - skipped,
            "uncaught_errors": exc_cap["uncaught_count"],
            "passes_all_thresholds": passes_all,
        },
        "thresholds": {
            "limit_enforcement_rate": {
                "value": limit_enf["rate"],
                "threshold": LIMIT_ENFORCEMENT_THRESHOLD,
                "pass": passes_limit,
            },
            "exception_capture_rate": {
                "value": exc_cap["rate"],
                "threshold": EXCEPTION_CAPTURE_THRESHOLD,
                "pass": passes_exc,
            },
            "tool_message_rate": {
                "value": msg_rate["rate"],
                "threshold": TOOL_MESSAGE_RATE_THRESHOLD,
                "pass": passes_msg,
            },
            "no_tool_guard_rate": {
                "value": no_tool["rate"],
                "threshold": NO_TOOL_GUARD_THRESHOLD,
                "pass": passes_no_tool,
            },
            "tool_call_id_linkage_rate": {
                "value": id_link["rate"],
                "threshold": TOOL_CALL_ID_LINKAGE_THRESHOLD,
                "pass": passes_link,
            },
            "counts_increment_accuracy": {
                "value": counts["rate"],
                "threshold": COUNTS_INCREMENT_THRESHOLD,
                "pass": passes_counts,
            },
            "success_read_rate": {
                "value": read_rate["rate"],
                "threshold": SUCCESS_READ_RATE_THRESHOLD,
                "pass": passes_read,
            },
            "p95_latency_ms_success_read": {
                "value": perf["success_read_latency_ms"]["p95"],
                "threshold": P95_LATENCY_THRESHOLD_MS,
                "pass": passes_latency,
            },
        },
        "per_category": per_cat,
        "performance": perf,
        "detail": {
            "limit_enforcement": limit_enf,
            "exception_capture": exc_cap,
            "tool_message": msg_rate,
            "no_tool_guard": no_tool,
            "tool_call_id_linkage": id_link,
            "counts_accuracy": counts,
            "success_read": read_rate,
        },
    }
