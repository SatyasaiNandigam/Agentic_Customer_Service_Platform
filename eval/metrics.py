from __future__ import annotations

from typing import Any

from eval.eval_types import EvalRecord, EvalResult


INTENT_CLASSES: list[str] = [
    "order_status",
    "order_cancel",
    "shipment_tracking",
    "refund_request",
    "refund_status",
    "product_inquiry",
    "product_search",
    "account_info",
    "review_lookup",
    "faq_policy",
    "chitchat",
    "complaint",
    "unknown",
]

MACRO_F1_THRESHOLD = 0.90
FALSE_REJECTION_THRESHOLD = 0.05


def compute_per_intent_metrics(results: list[EvalResult]) -> dict[str, dict[str, Any]]:
    """Compute TP/FP/FN and derived precision/recall/F1 for each intent class."""
    per_intent: dict[str, dict[str, Any]] = {}
    for cls in INTENT_CLASSES:
        tp = sum(1 for r in results if r.expected == cls and r.predicted == cls)
        fp = sum(1 for r in results if r.expected != cls and r.predicted == cls)
        fn = sum(1 for r in results if r.expected == cls and r.predicted != cls)
        support = tp + fn

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = tp / support if support > 0 else 0.0

        per_intent[cls] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "support": support,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "accuracy": round(accuracy, 4),
        }
    return per_intent


def compute_macro_f1(per_intent: dict[str, dict[str, Any]]) -> float:
    """Arithmetic mean of per-class F1. Classes with support=0 contribute 0.0."""
    f1_scores = [per_intent[cls]["f1"] for cls in INTENT_CLASSES]
    return round(sum(f1_scores) / len(f1_scores), 4)


def compute_confidence_calibration(
    results: list[EvalResult],
    n_bins: int = 5,
) -> list[dict[str, Any]]:
    """Bin results by confidence into equal-width buckets; measure accuracy vs mean confidence."""
    bin_width = 1.0 / n_bins
    bins: list[dict[str, Any]] = []

    for i in range(n_bins):
        lo = round(i * bin_width, 4)
        hi = round((i + 1) * bin_width, 4)
        # include upper bound on last bin to capture confidence == 1.0
        in_bin = [
            r for r in results
            if lo <= r.confidence < hi or (i == n_bins - 1 and r.confidence == 1.0)
        ]
        count = len(in_bin)
        if count == 0:
            bins.append({
                "bin_lower": lo,
                "bin_upper": hi,
                "count": 0,
                "mean_confidence": None,
                "accuracy": None,
                "calibration_gap": None,
            })
        else:
            mean_conf = sum(r.confidence for r in in_bin) / count
            acc = sum(1 for r in in_bin if r.correct) / count
            gap = abs(mean_conf - acc)
            bins.append({
                "bin_lower": lo,
                "bin_upper": hi,
                "count": count,
                "mean_confidence": round(mean_conf, 4),
                "accuracy": round(acc, 4),
                "calibration_gap": round(gap, 4),
            })
    return bins


def compute_unknown_rejection_precision(results: list[EvalResult]) -> dict[str, Any]:
    """
    Measure how often valid-intent inputs are incorrectly predicted as 'unknown' (false rejections).
    Also compute precision/recall for the 'unknown' class itself.
    """
    valid_cases = [r for r in results if r.expected != "unknown"]
    false_rejections = [r for r in valid_cases if r.predicted == "unknown"]

    total_valid = len(valid_cases)
    false_rejection_count = len(false_rejections)
    false_rejection_rate = false_rejection_count / total_valid if total_valid > 0 else 0.0

    tp_unknown = sum(1 for r in results if r.expected == "unknown" and r.predicted == "unknown")
    fp_unknown = sum(1 for r in results if r.expected != "unknown" and r.predicted == "unknown")
    fn_unknown = sum(1 for r in results if r.expected == "unknown" and r.predicted != "unknown")

    unknown_precision = tp_unknown / (tp_unknown + fp_unknown) if (tp_unknown + fp_unknown) > 0 else 0.0
    unknown_recall = tp_unknown / (tp_unknown + fn_unknown) if (tp_unknown + fn_unknown) > 0 else 0.0

    return {
        "false_rejection_rate": round(false_rejection_rate, 4),
        "false_rejection_count": false_rejection_count,
        "total_valid_cases": total_valid,
        "unknown_precision": round(unknown_precision, 4),
        "unknown_recall": round(unknown_recall, 4),
        "passes_threshold": false_rejection_rate <= FALSE_REJECTION_THRESHOLD,
    }


def compute_boundary_pair_accuracy(
    results: list[EvalResult],
    dataset: list[EvalRecord],
) -> dict[str, dict[str, Any]]:
    """Per boundary_pair: accuracy, count, error count."""
    pair_map: dict[str, list[EvalResult]] = {}
    record_by_id = {r.id: r for r in dataset}

    for result in results:
        record = record_by_id.get(result.id)
        if record and record.boundary_pair:
            pair_map.setdefault(record.boundary_pair, []).append(result)

    output: dict[str, dict[str, Any]] = {}
    for pair, pair_results in sorted(pair_map.items()):
        count = len(pair_results)
        errors = sum(1 for r in pair_results if not r.correct)
        accuracy = (count - errors) / count if count > 0 else 0.0
        output[pair] = {
            "accuracy": round(accuracy, 4),
            "count": count,
            "errors": errors,
        }
    return output


def build_full_report(
    results: list[EvalResult],
    dataset: list[EvalRecord],
    run_metadata: dict[str, Any],
) -> dict[str, Any]:
    """Assemble the complete report dict ready for json.dumps()."""
    per_intent = compute_per_intent_metrics(results)
    macro_f1 = compute_macro_f1(per_intent)
    total = len(results)
    overall_accuracy = round(sum(1 for r in results if r.correct) / total, 4) if total > 0 else 0.0

    failures = sorted(
        [
            {
                "id": r.id,
                "text": r.text,
                "expected": r.expected,
                "predicted": r.predicted,
                "confidence": r.confidence,
                "boundary_pair": next(
                    (d.boundary_pair for d in dataset if d.id == r.id), None
                ),
                "error": r.error,
            }
            for r in results
            if not r.correct
        ],
        key=lambda x: x["confidence"],
        reverse=True,
    )

    return {
        "run_metadata": run_metadata,
        "summary": {
            "overall_accuracy": overall_accuracy,
            "macro_f1": macro_f1,
            "threshold": MACRO_F1_THRESHOLD,
            "passes_threshold": macro_f1 >= MACRO_F1_THRESHOLD,
        },
        "per_intent": per_intent,
        "confidence_calibration": compute_confidence_calibration(results),
        "unknown_rejection": compute_unknown_rejection_precision(results),
        "boundary_pair_accuracy": compute_boundary_pair_accuracy(results, dataset),
        "failures": failures,
    }
