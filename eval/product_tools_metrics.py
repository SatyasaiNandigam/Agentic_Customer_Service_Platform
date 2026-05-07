from __future__ import annotations

from typing import Any

from eval.product_tools_eval_types import ProductToolRecord, ProductToolResult


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

SEARCH_HIT_RATE_THRESHOLD: float = 0.95        # expected IDs found
SEARCH_FILTER_PRECISION_THRESHOLD: float = 0.98 # excluded IDs absent
SEARCH_STATUS_EXCLUSION_THRESHOLD: float = 1.0  # draft/inactive never returned
SEARCH_EMPTY_ACCURACY_THRESHOLD: float = 0.98   # empty searches return empty
DETAIL_FOUND_ACCURACY_THRESHOLD: float = 0.95   # found products return correct data
DETAIL_NOT_FOUND_THRESHOLD: float = 0.98        # not-found errors have correct error_type
DETAIL_FIELD_COMPLETENESS_THRESHOLD: float = 0.95
OVERALL_PASS_RATE_THRESHOLD: float = 0.92
P95_LATENCY_THRESHOLD_MS: float = 3500.0

CATEGORIES: list[str] = [
    "keyword_exact",
    "keyword_partial",
    "keyword_miss",
    "category_filter",
    "brand_filter",
    "price_range",
    "combined_filters",
    "status_exclusion",
    "pagination",
    "edge_case",
    "detail_by_id",
    "detail_by_id_not_found",
    "detail_by_name_exact",
    "detail_by_name_prefix",
    "detail_by_name_miss",
    "field_completeness",
    "variant_detail",
    "error_handling",
]

_SEARCH_CATEGORIES: frozenset[str] = frozenset({
    "keyword_exact", "keyword_partial", "keyword_miss",
    "category_filter", "brand_filter", "price_range",
    "combined_filters", "status_exclusion", "pagination", "edge_case",
})
_DETAIL_CATEGORIES: frozenset[str] = frozenset({
    "detail_by_id", "detail_by_id_not_found",
    "detail_by_name_exact", "detail_by_name_prefix", "detail_by_name_miss",
    "field_completeness", "variant_detail", "error_handling",
})
_STATUS_EXCLUSION_CATEGORIES: frozenset[str] = frozenset({
    "status_exclusion", "category_filter", "brand_filter",
    "keyword_partial", "keyword_exact",
})


def compute_search_hit_rate(results: list[ProductToolResult]) -> dict[str, Any]:
    """Fraction of search cases where all expected_product_ids_contains were found."""
    eligible = [r for r in results if r.category in _SEARCH_CATEGORIES and r.error is None]
    if not eligible:
        return {"rate": 1.0, "passed": 0, "total": 0, "failures": []}
    passed = sum(1 for r in eligible if r.contains_check_passed)
    failures = [
        {"id": r.id, "category": r.category, "missing_ids": r.missing_ids, "actual_ids": r.actual_product_ids}
        for r in eligible if not r.contains_check_passed
    ]
    return {
        "rate": round(passed / len(eligible), 4),
        "passed": passed,
        "total": len(eligible),
        "failures": failures,
    }


def compute_search_filter_precision(results: list[ProductToolResult]) -> dict[str, Any]:
    """Fraction of search cases where no excluded IDs appeared in results."""
    eligible = [r for r in results if r.category in _SEARCH_CATEGORIES and r.error is None]
    if not eligible:
        return {"rate": 1.0, "passed": 0, "total": 0, "failures": []}
    passed = sum(1 for r in eligible if r.excluded_check_passed)
    failures = [
        {"id": r.id, "category": r.category, "unexpected_ids": r.unexpected_ids}
        for r in eligible if not r.excluded_check_passed
    ]
    return {
        "rate": round(passed / len(eligible), 4),
        "passed": passed,
        "total": len(eligible),
        "failures": failures,
    }


def compute_search_status_exclusion(results: list[ProductToolResult]) -> dict[str, Any]:
    """Fraction of status_exclusion category cases where no draft/inactive IDs appeared."""
    eligible = [r for r in results if r.category == "status_exclusion" and r.error is None]
    if not eligible:
        return {"rate": 1.0, "passed": 0, "total": 0, "failures": []}
    passed = sum(1 for r in eligible if r.excluded_check_passed)
    failures = [
        {"id": r.id, "unexpected_ids": r.unexpected_ids}
        for r in eligible if not r.excluded_check_passed
    ]
    return {
        "rate": round(passed / len(eligible), 4),
        "passed": passed,
        "total": len(eligible),
        "failures": failures,
    }


def compute_search_empty_accuracy(results: list[ProductToolResult]) -> dict[str, Any]:
    """Fraction of keyword_miss cases that correctly returned zero results."""
    eligible = [r for r in results if r.category == "keyword_miss" and r.error is None]
    if not eligible:
        return {"rate": 1.0, "passed": 0, "total": 0, "failures": []}
    passed = sum(1 for r in eligible if r.count_check_passed and (r.actual_count or 0) == 0)
    failures = [
        {"id": r.id, "actual_count": r.actual_count, "actual_ids": r.actual_product_ids}
        for r in eligible if not (r.count_check_passed and (r.actual_count or 0) == 0)
    ]
    return {
        "rate": round(passed / len(eligible), 4),
        "passed": passed,
        "total": len(eligible),
        "failures": failures,
    }


def compute_detail_found_accuracy(results: list[ProductToolResult]) -> dict[str, Any]:
    """Fraction of detail cases expected to succeed that returned the correct product."""
    eligible = [
        r for r in results
        if r.category in {"detail_by_id", "detail_by_name_exact", "detail_by_name_prefix",
                          "field_completeness", "variant_detail"}
        and r.error is None
    ]
    if not eligible:
        return {"rate": 1.0, "passed": 0, "total": 0, "failures": []}
    passed = sum(1 for r in eligible if r.success_correct)
    failures = [
        {"id": r.id, "category": r.category, "actual_ids": r.actual_product_ids,
         "actual_error_type": r.actual_error_type}
        for r in eligible if not r.success_correct
    ]
    return {
        "rate": round(passed / len(eligible), 4),
        "passed": passed,
        "total": len(eligible),
        "failures": failures,
    }


def compute_detail_not_found_handling(results: list[ProductToolResult]) -> dict[str, Any]:
    """Fraction of not-found cases where error_type matches expected."""
    eligible = [
        r for r in results
        if r.category in {"detail_by_id_not_found", "detail_by_name_miss", "error_handling"}
        and r.error is None
    ]
    if not eligible:
        return {"rate": 1.0, "passed": 0, "total": 0, "failures": []}
    passed = sum(1 for r in eligible if r.error_type_correct)
    failures = [
        {"id": r.id, "category": r.category,
         "actual_error_type": r.actual_error_type, "success_correct": r.success_correct}
        for r in eligible if not r.error_type_correct
    ]
    return {
        "rate": round(passed / len(eligible), 4),
        "passed": passed,
        "total": len(eligible),
        "failures": failures,
    }


def compute_detail_field_completeness(results: list[ProductToolResult]) -> dict[str, Any]:
    """Fraction of field_completeness + variant_detail cases where all expected fields present."""
    eligible = [
        r for r in results
        if r.category in {"field_completeness", "variant_detail", "detail_by_id"}
        and r.error is None
    ]
    if not eligible:
        return {"rate": 1.0, "passed": 0, "total": 0, "failures": []}
    passed = sum(1 for r in eligible if r.fields_complete)
    failures = [
        {"id": r.id, "category": r.category, "missing_fields": r.missing_fields}
        for r in eligible if not r.fields_complete
    ]
    return {
        "rate": round(passed / len(eligible), 4),
        "passed": passed,
        "total": len(eligible),
        "failures": failures,
    }


def compute_overall_pass_rate(results: list[ProductToolResult]) -> dict[str, Any]:
    """Fraction of all non-errored records where every assertion passed."""
    eligible = [r for r in results if r.error is None]
    if not eligible:
        return {"rate": 1.0, "passed": 0, "total": 0, "failures": []}

    def _all_pass(r: ProductToolResult) -> bool:
        return (
            r.success_correct
            and r.contains_check_passed
            and r.excluded_check_passed
            and r.count_check_passed
            and r.error_type_correct
            and r.fields_complete
        )

    passed = sum(1 for r in eligible if _all_pass(r))
    failures = [
        {
            "id": r.id,
            "category": r.category,
            "tool": r.tool,
            "success_correct": r.success_correct,
            "contains_check_passed": r.contains_check_passed,
            "excluded_check_passed": r.excluded_check_passed,
            "count_check_passed": r.count_check_passed,
            "error_type_correct": r.error_type_correct,
            "fields_complete": r.fields_complete,
            "missing_ids": r.missing_ids,
            "unexpected_ids": r.unexpected_ids,
            "actual_error_type": r.actual_error_type,
            "missing_fields": r.missing_fields,
        }
        for r in eligible if not _all_pass(r)
    ]
    return {
        "rate": round(passed / len(eligible), 4),
        "passed": passed,
        "total": len(eligible),
        "failures": failures,
    }


def compute_performance_stats(results: list[ProductToolResult]) -> dict[str, Any]:
    all_latencies = sorted(r.latency_ms for r in results if r.error is None)
    search_latencies = sorted(
        r.latency_ms for r in results
        if r.category in _SEARCH_CATEGORIES and r.error is None
    )
    detail_latencies = sorted(
        r.latency_ms for r in results
        if r.category in _DETAIL_CATEGORIES and r.error is None
    )

    def _stats(vals: list[float]) -> dict:
        if not vals:
            return {"p50": 0.0, "p95": 0.0, "mean": 0.0, "max": 0.0, "count": 0}
        n = len(vals)
        return {
            "p50": round(vals[int(0.50 * (n - 1))], 1),
            "p95": round(vals[int(0.95 * (n - 1))], 1),
            "mean": round(sum(vals) / n, 1),
            "max": round(vals[-1], 1),
            "count": n,
        }

    return {
        "all_latency_ms": _stats(all_latencies),
        "search_latency_ms": _stats(search_latencies),
        "detail_latency_ms": _stats(detail_latencies),
    }


def compute_per_category_metrics(results: list[ProductToolResult]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for cat in CATEGORIES:
        subset = [r for r in results if r.category == cat]
        if not subset:
            output[cat] = {"count": 0}
            continue
        n = len(subset)
        output[cat] = {
            "count": n,
            "errors": sum(1 for r in subset if r.error is not None),
            "success_correct": sum(1 for r in subset if r.success_correct),
            "contains_passed": sum(1 for r in subset if r.contains_check_passed),
            "excluded_passed": sum(1 for r in subset if r.excluded_check_passed),
            "count_passed": sum(1 for r in subset if r.count_check_passed),
            "error_type_correct": sum(1 for r in subset if r.error_type_correct),
            "fields_complete": sum(1 for r in subset if r.fields_complete),
            "avg_latency_ms": round(
                sum(r.latency_ms for r in subset) / n, 1
            ),
        }
    return output


def build_full_report(
    results: list[ProductToolResult],
    dataset: list[ProductToolRecord],
    run_metadata: dict[str, Any],
) -> dict[str, Any]:
    search_hit      = compute_search_hit_rate(results)
    search_prec     = compute_search_filter_precision(results)
    status_excl     = compute_search_status_exclusion(results)
    empty_acc       = compute_search_empty_accuracy(results)
    detail_found    = compute_detail_found_accuracy(results)
    not_found       = compute_detail_not_found_handling(results)
    field_comp      = compute_detail_field_completeness(results)
    overall         = compute_overall_pass_rate(results)
    perf            = compute_performance_stats(results)
    per_cat         = compute_per_category_metrics(results)

    p95 = perf["all_latency_ms"]["p95"]

    passes = {
        "search_hit_rate":              search_hit["rate"]   >= SEARCH_HIT_RATE_THRESHOLD,
        "search_filter_precision":      search_prec["rate"]  >= SEARCH_FILTER_PRECISION_THRESHOLD,
        "search_status_exclusion_rate": status_excl["rate"]  >= SEARCH_STATUS_EXCLUSION_THRESHOLD,
        "search_empty_accuracy":        empty_acc["rate"]    >= SEARCH_EMPTY_ACCURACY_THRESHOLD,
        "detail_found_accuracy":        detail_found["rate"] >= DETAIL_FOUND_ACCURACY_THRESHOLD,
        "detail_not_found_handling":    not_found["rate"]    >= DETAIL_NOT_FOUND_THRESHOLD,
        "detail_field_completeness":    field_comp["rate"]   >= DETAIL_FIELD_COMPLETENESS_THRESHOLD,
        "overall_pass_rate":            overall["rate"]      >= OVERALL_PASS_RATE_THRESHOLD,
    }

    return {
        "run_metadata": run_metadata,
        "summary": {
            "total_cases": len(results),
            "errors": sum(1 for r in results if r.error is not None),
            "passes_all_thresholds": all(passes.values()),
        },
        "thresholds": {
            name: {
                "value": val,
                "threshold": {
                    "search_hit_rate": SEARCH_HIT_RATE_THRESHOLD,
                    "search_filter_precision": SEARCH_FILTER_PRECISION_THRESHOLD,
                    "search_status_exclusion_rate": SEARCH_STATUS_EXCLUSION_THRESHOLD,
                    "search_empty_accuracy": SEARCH_EMPTY_ACCURACY_THRESHOLD,
                    "detail_found_accuracy": DETAIL_FOUND_ACCURACY_THRESHOLD,
                    "detail_not_found_handling": DETAIL_NOT_FOUND_THRESHOLD,
                    "detail_field_completeness": DETAIL_FIELD_COMPLETENESS_THRESHOLD,
                    "overall_pass_rate": OVERALL_PASS_RATE_THRESHOLD,
                }[name],
                "pass": passes[name],
            }
            for name, val in {
                "search_hit_rate": search_hit["rate"],
                "search_filter_precision": search_prec["rate"],
                "search_status_exclusion_rate": status_excl["rate"],
                "search_empty_accuracy": empty_acc["rate"],
                "detail_found_accuracy": detail_found["rate"],
                "detail_not_found_handling": not_found["rate"],
                "detail_field_completeness": field_comp["rate"],
                "overall_pass_rate": overall["rate"],
            }.items()
        },
        "p95_latency_ms": {"value": p95, "threshold": P95_LATENCY_THRESHOLD_MS, "pass": p95 <= P95_LATENCY_THRESHOLD_MS},
        "per_category": per_cat,
        "performance": perf,
        "failures": overall.get("failures", []),
        "detail": {
            "search_hit": search_hit,
            "search_filter_precision": search_prec,
            "search_status_exclusion": status_excl,
            "search_empty_accuracy": empty_acc,
            "detail_found": detail_found,
            "detail_not_found": not_found,
            "field_completeness": field_comp,
        },
    }
