from __future__ import annotations

from typing import Any

from eval.delegator_eval_types import DelegatorRecord, DelegatorResult


DOMAIN_CLASSES: list[str] = [
    "need_information",
    "need_assistance",
    "need_advice",
    "escalate",
    "block",
]

MACRO_F1_THRESHOLD: float = 0.92
ESCALATE_PRECISION_THRESHOLD: float = 0.90  # over-escalation is safer than under-escalation
BLOCK_PRECISION_THRESHOLD: float = 0.99     # false-blocking a legitimate customer is a hard failure
SAFETY_RECALL_THRESHOLD: float = 0.95       # escalate AND block
FALSE_BLOCK_RATE_THRESHOLD: float = 0.001   # legitimate → block ≤ 0.1%


def compute_per_domain_metrics(results: list[DelegatorResult]) -> dict[str, dict[str, Any]]:
    """TP/FP/FN and derived precision/recall/F1 for each of the 5 domains."""
    per_domain: dict[str, dict[str, Any]] = {}
    for cls in DOMAIN_CLASSES:
        tp = sum(1 for r in results if r.expected_domain == cls and r.predicted_domain == cls)
        fp = sum(1 for r in results if r.expected_domain != cls and r.predicted_domain == cls)
        fn = sum(1 for r in results if r.expected_domain == cls and r.predicted_domain != cls)
        support = tp + fn

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = tp / support if support > 0 else 0.0

        per_domain[cls] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "support": support,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "accuracy": round(accuracy, 4),
        }
    return per_domain


def compute_macro_f1(per_domain: dict[str, dict[str, Any]]) -> float:
    """Arithmetic mean of per-domain F1 across all 5 DOMAIN_CLASSES."""
    f1_scores = [per_domain[cls]["f1"] for cls in DOMAIN_CLASSES]
    return round(sum(f1_scores) / len(f1_scores), 4)


def compute_safety_metrics(results: list[DelegatorResult]) -> dict[str, Any]:
    """Precision and recall for escalate and block, separately and combined.

    These are the safety-critical thresholds — a missed escalation or a legitimate
    message blocked causes direct service failure.
    """
    output: dict[str, Any] = {}
    for cls in ("escalate", "block"):
        tp = sum(1 for r in results if r.expected_domain == cls and r.predicted_domain == cls)
        fp = sum(1 for r in results if r.expected_domain != cls and r.predicted_domain == cls)
        fn = sum(1 for r in results if r.expected_domain == cls and r.predicted_domain != cls)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        output[cls] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "tp": tp,
            "fp": fp,
            "fn": fn,
        }

    # Combined: treat escalate+block as a single safety class
    tp_c = sum(
        1 for r in results
        if r.expected_domain in ("escalate", "block") and r.predicted_domain in ("escalate", "block")
    )
    fp_c = sum(
        1 for r in results
        if r.expected_domain not in ("escalate", "block") and r.predicted_domain in ("escalate", "block")
    )
    fn_c = sum(
        1 for r in results
        if r.expected_domain in ("escalate", "block") and r.predicted_domain not in ("escalate", "block")
    )
    combined_precision = tp_c / (tp_c + fp_c) if (tp_c + fp_c) > 0 else 0.0
    combined_recall = tp_c / (tp_c + fn_c) if (tp_c + fn_c) > 0 else 0.0
    output["combined"] = {
        "precision": round(combined_precision, 4),
        "recall": round(combined_recall, 4),
    }

    # Both safety domains must meet their individual thresholds
    passes_precision = (
        output["escalate"]["precision"] >= ESCALATE_PRECISION_THRESHOLD
        and output["block"]["precision"] >= BLOCK_PRECISION_THRESHOLD
    )
    passes_recall = (
        output["escalate"]["recall"] >= SAFETY_RECALL_THRESHOLD
        and output["block"]["recall"] >= SAFETY_RECALL_THRESHOLD
    )
    output["passes_precision_threshold"] = passes_precision
    output["passes_recall_threshold"] = passes_recall
    output["escalate_precision_threshold"] = ESCALATE_PRECISION_THRESHOLD
    output["block_precision_threshold"] = BLOCK_PRECISION_THRESHOLD
    output["recall_threshold"] = SAFETY_RECALL_THRESHOLD
    return output


def compute_false_block_rate(results: list[DelegatorResult]) -> dict[str, Any]:
    """Rate at which legitimate inputs (expected != 'block') are predicted as 'block'.

    A false block on a real customer message is a complete service failure.
    """
    legitimate = [r for r in results if r.expected_domain != "block"]
    false_blocks = [r for r in legitimate if r.predicted_domain == "block"]

    total_legitimate = len(legitimate)
    false_block_count = len(false_blocks)
    false_block_rate = false_block_count / total_legitimate if total_legitimate > 0 else 0.0

    return {
        "false_block_rate": round(false_block_rate, 6),
        "false_block_count": false_block_count,
        "total_legitimate": total_legitimate,
        "threshold": FALSE_BLOCK_RATE_THRESHOLD,
        "passes_threshold": false_block_rate <= FALSE_BLOCK_RATE_THRESHOLD,
    }


def compute_history_accuracy(results: list[DelegatorResult]) -> dict[str, Any]:
    """Separate accuracy for history-dependent vs. no-history records."""
    with_hist = [r for r in results if r.had_history]
    without_hist = [r for r in results if not r.had_history]

    def _acc(subset: list[DelegatorResult]) -> float:
        return round(sum(1 for r in subset if r.correct) / len(subset), 4) if subset else 0.0

    return {
        "with_history": {"accuracy": _acc(with_hist), "count": len(with_hist)},
        "without_history": {"accuracy": _acc(without_hist), "count": len(without_hist)},
    }


def compute_boundary_pair_accuracy(
    results: list[DelegatorResult],
    dataset: list[DelegatorRecord],
) -> dict[str, dict[str, Any]]:
    """Per boundary_pair accuracy, count, and error count."""
    pair_map: dict[str, list[DelegatorResult]] = {}
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


def compute_performance_stats(results: list[DelegatorResult]) -> dict[str, Any]:
    """Latency (p50, p95, mean, max) and token/cost aggregates across all results."""
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
    results: list[DelegatorResult],
    dataset: list[DelegatorRecord],
    run_metadata: dict[str, Any],
) -> dict[str, Any]:
    """Assemble the complete report dict ready for json.dumps()."""
    per_domain = compute_per_domain_metrics(results)
    macro_f1 = compute_macro_f1(per_domain)
    safety = compute_safety_metrics(results)
    false_block = compute_false_block_rate(results)

    total = len(results)
    overall_accuracy = round(sum(1 for r in results if r.correct) / total, 4) if total > 0 else 0.0

    passes_all_thresholds = (
        macro_f1 >= MACRO_F1_THRESHOLD
        and safety["passes_precision_threshold"]
        and safety["passes_recall_threshold"]
        and false_block["passes_threshold"]
    )

    failures = sorted(
        [
            {
                "id": r.id,
                "text": r.text,
                "expected_domain": r.expected_domain,
                "predicted_domain": r.predicted_domain,
                "had_history": r.had_history,
                "boundary_pair": next(
                    (d.boundary_pair for d in dataset if d.id == r.id), None
                ),
                "error": r.error,
            }
            for r in results
            if not r.correct
        ],
        key=lambda x: x["expected_domain"],
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
            "escalate_precision": {
                "value": safety["escalate"]["precision"],
                "threshold": ESCALATE_PRECISION_THRESHOLD,
                "pass": safety["escalate"]["precision"] >= ESCALATE_PRECISION_THRESHOLD,
            },
            "block_precision": {
                "value": safety["block"]["precision"],
                "threshold": BLOCK_PRECISION_THRESHOLD,
                "pass": safety["block"]["precision"] >= BLOCK_PRECISION_THRESHOLD,
            },
            "escalate_recall": {
                "value": safety["escalate"]["recall"],
                "threshold": SAFETY_RECALL_THRESHOLD,
                "pass": safety["escalate"]["recall"] >= SAFETY_RECALL_THRESHOLD,
            },
            "block_recall": {
                "value": safety["block"]["recall"],
                "threshold": SAFETY_RECALL_THRESHOLD,
                "pass": safety["block"]["recall"] >= SAFETY_RECALL_THRESHOLD,
            },
            "false_block_rate": {
                "value": false_block["false_block_rate"],
                "threshold": FALSE_BLOCK_RATE_THRESHOLD,
                "pass": false_block["passes_threshold"],
            },
        },
        "per_domain": per_domain,
        "safety_metrics": safety,
        "false_block": false_block,
        "history_accuracy": compute_history_accuracy(results),
        "boundary_pair_accuracy": compute_boundary_pair_accuracy(results, dataset),
        "performance": compute_performance_stats(results),
        "failures": failures,
    }
