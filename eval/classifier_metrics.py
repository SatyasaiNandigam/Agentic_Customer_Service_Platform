from __future__ import annotations

from typing import Any

from eval.classifier_eval_types import ClassifierRecord, ClassifierResult


# Active intent classes the bounded classifier can output (complaint is not in any domain set)
INTENT_CLASSES: list[str] = [
    "order_status",
    "shipment_tracking",
    "refund_status",
    "account_info",
    "review_lookup",
    "product_inquiry",
    "product_search",
    "order_cancel",
    "refund_request",
    "faq_policy",
    "chitchat",
    "unknown",
]

DOMAIN_INTENT_MAP: dict[str, list[str]] = {
    "need_information": [
        "order_status", "shipment_tracking", "refund_status",
        "account_info", "review_lookup", "product_inquiry", "product_search",
    ],
    "need_assistance": ["order_cancel", "refund_request"],
    "need_advice": ["faq_policy", "chitchat", "unknown"],
}

# Domain fallback intents — what the classifier returns when confidence is too low
DOMAIN_FALLBACK_INTENT: dict[str, str] = {
    "need_information": "order_status",
    "need_assistance": "refund_request",
    "need_advice": "unknown",
}

MACRO_F1_THRESHOLD: float = 0.90
DOMAIN_F1_THRESHOLDS: dict[str, float] = {
    "need_information": 0.90,
    "need_assistance": 0.95,
    "need_advice": 0.85,
}
FALSE_REJECTION_THRESHOLD: float = 0.05   # valid intents predicted as domain fallback
FALLBACK_RATE_THRESHOLD: float = 0.02     # LLM exception / classifier_fallback error rate
REQUIRES_TOOL_ACCURACY_THRESHOLD: float = 1.0


def compute_per_intent_metrics(results: list[ClassifierResult]) -> dict[str, dict[str, Any]]:
    """TP/FP/FN and derived precision/recall/F1 for each of the 12 active intents."""
    per_intent: dict[str, dict[str, Any]] = {}
    for cls in INTENT_CLASSES:
        tp = sum(1 for r in results if r.expected_intent == cls and r.predicted_intent == cls)
        fp = sum(1 for r in results if r.expected_intent != cls and r.predicted_intent == cls)
        fn = sum(1 for r in results if r.expected_intent == cls and r.predicted_intent != cls)
        support = tp + fn

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        per_intent[cls] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "support": support,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        }
    return per_intent


def compute_macro_f1(per_intent: dict[str, dict[str, Any]]) -> float:
    """Arithmetic mean of per-intent F1. Classes with support=0 contribute 0.0."""
    f1_scores = [per_intent[cls]["f1"] for cls in INTENT_CLASSES]
    return round(sum(f1_scores) / len(f1_scores), 4)


def compute_per_domain_breakdown(results: list[ClassifierResult]) -> dict[str, dict[str, Any]]:
    """Separate macro-F1 and accuracy for each of the 3 active domains."""
    output: dict[str, dict[str, Any]] = {}
    for domain, intents in DOMAIN_INTENT_MAP.items():
        domain_results = [r for r in results if r.customer_domain == domain]
        if not domain_results:
            output[domain] = {"macro_f1": 0.0, "accuracy": 0.0, "count": 0}
            continue

        per_intent: dict[str, dict[str, Any]] = {}
        for cls in intents:
            tp = sum(1 for r in domain_results if r.expected_intent == cls and r.predicted_intent == cls)
            fp = sum(1 for r in domain_results if r.expected_intent != cls and r.predicted_intent == cls)
            fn = sum(1 for r in domain_results if r.expected_intent == cls and r.predicted_intent != cls)
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            per_intent[cls] = {"f1": round(f1, 4), "support": tp + fn}

        macro_f1 = round(sum(v["f1"] for v in per_intent.values()) / len(intents), 4)
        accuracy = round(sum(1 for r in domain_results if r.correct) / len(domain_results), 4)
        threshold = DOMAIN_F1_THRESHOLDS.get(domain, 0.90)

        output[domain] = {
            "macro_f1": macro_f1,
            "accuracy": accuracy,
            "count": len(domain_results),
            "threshold": threshold,
            "passes_threshold": macro_f1 >= threshold,
            "per_intent": per_intent,
        }
    return output


def compute_false_rejection_rate(results: list[ClassifierResult]) -> dict[str, Any]:
    """Rate at which valid (non-fallback-expected) inputs are predicted as the domain fallback.

    False rejection = the classifier falls back to the domain's safe default when the
    input actually deserved a specific intent. For need_advice this means classifying
    chitchat or faq_policy as 'unknown'. For need_information it means collapsing
    a shipment_tracking request to 'order_status'.
    """
    false_rejections = []
    for r in results:
        fallback = DOMAIN_FALLBACK_INTENT.get(r.customer_domain, "unknown")
        if r.expected_intent != fallback and r.predicted_intent == fallback:
            false_rejections.append(r)

    # Total inputs that could be false-rejected (expected intent is not the fallback)
    eligible = [
        r for r in results
        if r.expected_intent != DOMAIN_FALLBACK_INTENT.get(r.customer_domain, "unknown")
    ]
    total_eligible = len(eligible)
    false_rejection_count = len(false_rejections)
    rate = false_rejection_count / total_eligible if total_eligible > 0 else 0.0

    return {
        "false_rejection_rate": round(rate, 4),
        "false_rejection_count": false_rejection_count,
        "total_eligible": total_eligible,
        "threshold": FALSE_REJECTION_THRESHOLD,
        "passes_threshold": rate <= FALSE_REJECTION_THRESHOLD,
    }


def compute_fallback_rate(results: list[ClassifierResult]) -> dict[str, Any]:
    """Fraction of results that hit the LLM-error silent fallback path."""
    fallback_count = sum(1 for r in results if r.error == "classifier_fallback")
    rate = fallback_count / len(results) if results else 0.0
    return {
        "fallback_rate": round(rate, 4),
        "fallback_count": fallback_count,
        "total": len(results),
        "threshold": FALLBACK_RATE_THRESHOLD,
        "passes_threshold": rate <= FALLBACK_RATE_THRESHOLD,
    }


def compute_requires_tool_accuracy(results: list[ClassifierResult]) -> dict[str, Any]:
    """requires_tool is derived from domain, never from LLM — should always be 100%.

    Tool domains: need_information, need_assistance.
    Direct domains: need_advice.
    """
    tool_domains = frozenset({"need_information", "need_assistance"})
    correct = sum(
        1 for r in results
        if r.requires_tool == (r.customer_domain in tool_domains)
    )
    accuracy = correct / len(results) if results else 0.0
    return {
        "accuracy": round(accuracy, 4),
        "correct": correct,
        "total": len(results),
        "passes_threshold": accuracy >= REQUIRES_TOOL_ACCURACY_THRESHOLD,
    }


def compute_confidence_calibration(
    results: list[ClassifierResult],
    n_bins: int = 5,
) -> list[dict[str, Any]]:
    """Bin results by confidence into equal-width buckets; measure accuracy vs mean confidence."""
    bin_width = 1.0 / n_bins
    bins: list[dict[str, Any]] = []
    for i in range(n_bins):
        lo = round(i * bin_width, 4)
        hi = round((i + 1) * bin_width, 4)
        in_bin = [
            r for r in results
            if lo <= r.confidence < hi or (i == n_bins - 1 and r.confidence == 1.0)
        ]
        count = len(in_bin)
        if count == 0:
            bins.append({"bin_lower": lo, "bin_upper": hi, "count": 0,
                         "mean_confidence": None, "accuracy": None, "calibration_gap": None})
        else:
            mean_conf = sum(r.confidence for r in in_bin) / count
            acc = sum(1 for r in in_bin if r.correct) / count
            bins.append({
                "bin_lower": lo,
                "bin_upper": hi,
                "count": count,
                "mean_confidence": round(mean_conf, 4),
                "accuracy": round(acc, 4),
                "calibration_gap": round(abs(mean_conf - acc), 4),
            })
    return bins


def compute_boundary_pair_accuracy(
    results: list[ClassifierResult],
    dataset: list[ClassifierRecord],
) -> dict[str, dict[str, Any]]:
    """Per boundary_pair accuracy, count, and error count."""
    pair_map: dict[str, list[ClassifierResult]] = {}
    record_by_id = {r.id: r for r in dataset}

    for result in results:
        record = record_by_id.get(result.id)
        if record and record.boundary_pair:
            pair_map.setdefault(record.boundary_pair, []).append(result)

    output: dict[str, dict[str, Any]] = {}
    for pair, pair_results in sorted(pair_map.items()):
        count = len(pair_results)
        errors = sum(1 for r in pair_results if not r.correct)
        output[pair] = {
            "accuracy": round((count - errors) / count, 4) if count > 0 else 0.0,
            "count": count,
            "errors": errors,
        }
    return output


def compute_history_accuracy(results: list[ClassifierResult]) -> dict[str, Any]:
    """Separate accuracy for history-dependent vs. no-history records."""
    with_hist = [r for r in results if r.had_history]
    without_hist = [r for r in results if not r.had_history]

    def _acc(subset: list[ClassifierResult]) -> float:
        return round(sum(1 for r in subset if r.correct) / len(subset), 4) if subset else 0.0

    return {
        "with_history": {"accuracy": _acc(with_hist), "count": len(with_hist)},
        "without_history": {"accuracy": _acc(without_hist), "count": len(without_hist)},
    }


def compute_performance_stats(results: list[ClassifierResult]) -> dict[str, Any]:
    """Latency (p50, p95, mean, max) and token aggregates."""
    latencies = sorted(r.latency_ms for r in results)
    n = len(latencies)

    def _percentile(sorted_vals: list[float], p: float) -> float:
        if not sorted_vals:
            return 0.0
        idx = int(p / 100 * (len(sorted_vals) - 1))
        return round(sorted_vals[idx], 1)

    total_prompt = sum(r.prompt_tokens for r in results)
    total_completion = sum(r.completion_tokens for r in results)

    return {
        "latency_ms": {
            "p50": _percentile(latencies, 50),
            "p95": _percentile(latencies, 95),
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


def build_full_report(
    results: list[ClassifierResult],
    dataset: list[ClassifierRecord],
    run_metadata: dict[str, Any],
) -> dict[str, Any]:
    """Assemble the complete report dict ready for json.dumps()."""
    per_intent = compute_per_intent_metrics(results)
    macro_f1 = compute_macro_f1(per_intent)
    domain_breakdown = compute_per_domain_breakdown(results)
    false_rejection = compute_false_rejection_rate(results)
    fallback = compute_fallback_rate(results)
    requires_tool = compute_requires_tool_accuracy(results)

    total = len(results)
    overall_accuracy = round(sum(1 for r in results if r.correct) / total, 4) if total > 0 else 0.0

    passes_all_thresholds = (
        macro_f1 >= MACRO_F1_THRESHOLD
        and all(v["passes_threshold"] for v in domain_breakdown.values())
        and false_rejection["passes_threshold"]
        and requires_tool["passes_threshold"]
    )

    failures = sorted(
        [
            {
                "id": r.id,
                "text": r.text,
                "customer_domain": r.customer_domain,
                "expected_intent": r.expected_intent,
                "predicted_intent": r.predicted_intent,
                "confidence": r.confidence,
                "had_history": r.had_history,
                "boundary_pair": next(
                    (d.boundary_pair for d in dataset if d.id == r.id), None
                ),
                "error": r.error,
            }
            for r in results
            if not r.correct
        ],
        key=lambda x: x["expected_intent"],
    )

    return {
        "run_metadata": run_metadata,
        "summary": {
            "overall_accuracy": overall_accuracy,
            "macro_f1": macro_f1,
            "macro_f1_threshold": MACRO_F1_THRESHOLD,
            "passes_all_thresholds": passes_all_thresholds,
        },
        "thresholds": {
            "macro_f1": {"value": macro_f1, "threshold": MACRO_F1_THRESHOLD, "pass": macro_f1 >= MACRO_F1_THRESHOLD},
            "need_information_f1": {
                "value": domain_breakdown["need_information"]["macro_f1"],
                "threshold": DOMAIN_F1_THRESHOLDS["need_information"],
                "pass": domain_breakdown["need_information"]["passes_threshold"],
            },
            "need_assistance_f1": {
                "value": domain_breakdown["need_assistance"]["macro_f1"],
                "threshold": DOMAIN_F1_THRESHOLDS["need_assistance"],
                "pass": domain_breakdown["need_assistance"]["passes_threshold"],
            },
            "need_advice_f1": {
                "value": domain_breakdown["need_advice"]["macro_f1"],
                "threshold": DOMAIN_F1_THRESHOLDS["need_advice"],
                "pass": domain_breakdown["need_advice"]["passes_threshold"],
            },
            "false_rejection_rate": {
                "value": false_rejection["false_rejection_rate"],
                "threshold": FALSE_REJECTION_THRESHOLD,
                "pass": false_rejection["passes_threshold"],
            },
            "requires_tool_accuracy": {
                "value": requires_tool["accuracy"],
                "threshold": REQUIRES_TOOL_ACCURACY_THRESHOLD,
                "pass": requires_tool["passes_threshold"],
            },
        },
        "per_intent": per_intent,
        "domain_breakdown": domain_breakdown,
        "false_rejection": false_rejection,
        "fallback_rate": fallback,
        "requires_tool": requires_tool,
        "confidence_calibration": compute_confidence_calibration(results),
        "history_accuracy": compute_history_accuracy(results),
        "boundary_pair_accuracy": compute_boundary_pair_accuracy(results, dataset),
        "performance": compute_performance_stats(results),
        "failures": failures,
    }
