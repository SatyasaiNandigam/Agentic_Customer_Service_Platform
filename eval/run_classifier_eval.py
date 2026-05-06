"""Classifier intent-classification eval runner.

Usage:
    python eval/run_classifier_eval.py
    python eval/run_classifier_eval.py --dataset eval/datasets/intent_classification.jsonl
    python eval/run_classifier_eval.py --concurrency 5

Exit codes:
    0 — all 6 thresholds pass (macro-F1, per-domain F1 x3, false-rejection, requires-tool accuracy)
    1 — any threshold fails or eval aborted due to API errors
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Load .env before any project imports so os.environ is populated for ChatOpenAI
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from langchain_core.messages import AIMessage, HumanMessage

# ensure project root is on sys.path when invoked as `python eval/run_classifier_eval.py`
_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from langchain_openai import ChatOpenAI

from app.agent.nodes.classifier import make_classifier_node
from app.agent.state import create_initial_state
from app.config import get_settings
from eval.callback_handler import attach_token_capture, capture_tokens
from eval.classifier_eval_types import ClassifierRecord, ClassifierResult
from eval.classifier_metrics import (
    DOMAIN_F1_THRESHOLDS,
    FALSE_REJECTION_THRESHOLD,
    MACRO_F1_THRESHOLD,
    REQUIRES_TOOL_ACCURACY_THRESHOLD,
    build_full_report,
    compute_fallback_rate,
    compute_false_rejection_rate,
    compute_macro_f1,
    compute_per_domain_breakdown,
    compute_per_intent_metrics,
    compute_performance_stats,
    compute_requires_tool_accuracy,
)

# Domain fallback intents — what the node silently returns on LLM error
_DOMAIN_FALLBACK_INTENT: dict[str, str] = {
    "need_information": "order_status",
    "need_assistance": "refund_request",
    "need_advice": "unknown",
}

# Abort if more than this fraction of results look like silent API failures
_FALLBACK_ABORT_THRESHOLD = 0.20


def _build_state(record: ClassifierRecord) -> dict:
    state = create_initial_state(
        user_id="eval-classifier",
        session_id=f"eval-{record.id}",
        user_role="customer",
    )
    messages: list = []

    if record.history:
        for turn in record.history:
            cls = HumanMessage if turn["role"] == "human" else AIMessage
            messages.append(cls(content=turn["content"]))

    messages.append(HumanMessage(content=record.text))
    state["messages"] = messages
    state["customer_domain"] = record.customer_domain  # CRITICAL: bounded classifier context
    return state


async def run_single(
    record: ClassifierRecord,
    node,
    semaphore: asyncio.Semaphore,
) -> ClassifierResult:
    state = _build_state(record)
    error: str | None = None

    prompt_tokens = 0
    completion_tokens = 0

    async with semaphore:
        t0 = time.perf_counter()
        try:
            with capture_tokens() as cb:
                output = await node(state)
            prompt_tokens = cb.prompt_tokens
            completion_tokens = cb.completion_tokens
        except Exception as exc:
            output = {
                "intent": _DOMAIN_FALLBACK_INTENT.get(record.customer_domain, "unknown"),
                "confidence": 0.0,
                "requires_tool": False,
                "needs_escalation": False,
            }
            error = str(exc)
        latency_ms = (time.perf_counter() - t0) * 1000
    predicted = output.get("intent", _DOMAIN_FALLBACK_INTENT.get(record.customer_domain, "unknown"))
    confidence = output.get("confidence", 0.0)

    # Detect silent LLM fallback: confidence=0.0 + domain fallback intent = LLM error path
    if error is None and confidence == 0.0:
        expected_fallback = _DOMAIN_FALLBACK_INTENT.get(record.customer_domain, "unknown")
        if predicted == expected_fallback:
            error = "classifier_fallback"

    return ClassifierResult(
        id=record.id,
        text=record.text,
        expected_intent=record.expected_intent,
        predicted_intent=predicted,
        customer_domain=record.customer_domain,
        confidence=confidence,
        requires_tool=output.get("requires_tool", False),
        needs_escalation=output.get("needs_escalation", False),
        correct=(predicted == record.expected_intent and error != "classifier_fallback"),
        latency_ms=round(latency_ms, 1),
        error=error,
        had_history=bool(record.history),
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
    )


async def run_all(
    records: list[ClassifierRecord],
    node,
    concurrency: int = 10,
) -> list[ClassifierResult]:
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [run_single(r, node, semaphore) for r in records]
    return await asyncio.gather(*tasks)


def load_dataset(path: Path) -> list[ClassifierRecord]:
    records: list[ClassifierRecord] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            print(f"[WARN] Skipping malformed line {i} in {path}: {exc}", file=sys.stderr)
            continue
        required = {"id", "text", "expected_intent", "customer_domain"}
        if missing := required - obj.keys():
            print(f"[WARN] Skipping line {i} — missing fields {missing}", file=sys.stderr)
            continue
        record = ClassifierRecord(
            id=obj["id"],
            text=obj["text"],
            expected_intent=obj["expected_intent"],
            customer_domain=obj["customer_domain"],
            history=obj.get("history"),
            boundary_pair=obj.get("boundary_pair"),
            source=obj.get("source", "unknown"),
            notes=obj.get("notes"),
        )
        if "_hist_" in record.id and not record.history:
            print(
                f"[WARN] Record {record.id} looks history-dependent but has no history field.",
                file=sys.stderr,
            )
        records.append(record)
    return records


def write_results(
    results: list[ClassifierResult],
    dataset: list[ClassifierRecord],
    run_metadata: dict,
) -> Path:
    report = build_full_report(results, dataset, run_metadata)
    out_dir = Path("eval/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_intent_classification.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return out_path


def _check_fallback_abort(results: list[ClassifierResult]) -> bool:
    fallback_count = sum(1 for r in results if r.error == "classifier_fallback")
    rate = fallback_count / len(results) if results else 0.0
    if rate > _FALLBACK_ABORT_THRESHOLD:
        print(
            f"\n[ERROR] {fallback_count}/{len(results)} results are classifier fallbacks "
            f"({rate:.0%}). This usually indicates a missing or rate-limited API key. "
            "Check your .env file and retry.",
            file=sys.stderr,
        )
        return True
    return False


def _print_threshold(label: str, value: float, passes: bool, invert: bool = False) -> None:
    status = "PASS" if passes else "FAIL"
    flag = "" if passes else "  <--"
    print(f"    {label:<50} {value:.4f}  {status}{flag}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run classifier intent-classification eval."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("eval/datasets/intent_classification.jsonl"),
        help="Path to labeled JSONL dataset",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Number of concurrent LLM calls (default: 10)",
    )
    args = parser.parse_args()

    if not args.dataset.exists():
        print(f"[ERROR] Dataset not found: {args.dataset}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading dataset from {args.dataset} ...")
    dataset = load_dataset(args.dataset)
    if not dataset:
        print("[ERROR] Dataset is empty.", file=sys.stderr)
        sys.exit(1)
    print(f"  {len(dataset)} records loaded.")

    settings = get_settings()
    llm = ChatOpenAI(
        model=settings.classifier_model,
        temperature=0.0,
        max_tokens=128,
    )
    attach_token_capture(llm)
    classifier_node = make_classifier_node(llm)

    print(
        f"Running classifier eval "
        f"(model={settings.classifier_model}, concurrency={args.concurrency}) ..."
    )

    t_start = time.perf_counter()
    results = asyncio.run(run_all(dataset, classifier_node, concurrency=args.concurrency))
    duration = round(time.perf_counter() - t_start, 1)

    if _check_fallback_abort(results):
        sys.exit(1)

    error_count = sum(1 for r in results if r.error is not None)
    run_metadata = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_path": str(args.dataset),
        "total_cases": len(results),
        "model": settings.classifier_model,
        "confidence_threshold": 0.5,
        "concurrency": args.concurrency,
        "duration_seconds": duration,
        "errors": error_count,
    }

    out_path = write_results(results, dataset, run_metadata)

    # --- Compute metrics for console summary ---
    correct = sum(1 for r in results if r.correct)
    accuracy = correct / len(results) if results else 0.0

    per_intent = compute_per_intent_metrics(results)
    macro_f1 = compute_macro_f1(per_intent)
    domain_breakdown = compute_per_domain_breakdown(results)
    false_rejection = compute_false_rejection_rate(results)
    requires_tool = compute_requires_tool_accuracy(results)
    fallback = compute_fallback_rate(results)

    passes_macro = macro_f1 >= MACRO_F1_THRESHOLD
    passes_ni = domain_breakdown["need_information"]["passes_threshold"]
    passes_na = domain_breakdown["need_assistance"]["passes_threshold"]
    passes_nv = domain_breakdown["need_advice"]["passes_threshold"]
    passes_fr = false_rejection["passes_threshold"]
    passes_rt = requires_tool["passes_threshold"]

    passes_all = all([passes_macro, passes_ni, passes_na, passes_nv, passes_fr, passes_rt])
    overall_status = "PASS" if passes_all else "FAIL"

    print(
        f"\n  accuracy={accuracy:.3f}  macro_f1={macro_f1:.3f}  "
        f"errors={error_count}  duration={duration}s  [{overall_status}]"
    )

    print("\n  Threshold checks:")
    _print_threshold(f"macro_f1 >= {MACRO_F1_THRESHOLD}", macro_f1, passes_macro)
    _print_threshold(
        f"need_information macro_f1 >= {DOMAIN_F1_THRESHOLDS['need_information']}",
        domain_breakdown["need_information"]["macro_f1"],
        passes_ni,
    )
    _print_threshold(
        f"need_assistance macro_f1 >= {DOMAIN_F1_THRESHOLDS['need_assistance']}",
        domain_breakdown["need_assistance"]["macro_f1"],
        passes_na,
    )
    _print_threshold(
        f"need_advice macro_f1 >= {DOMAIN_F1_THRESHOLDS['need_advice']}",
        domain_breakdown["need_advice"]["macro_f1"],
        passes_nv,
    )
    _print_threshold(
        f"false_rejection_rate <= {FALSE_REJECTION_THRESHOLD}",
        false_rejection["false_rejection_rate"],
        passes_fr,
        invert=True,
    )
    _print_threshold(
        f"requires_tool_accuracy >= {REQUIRES_TOOL_ACCURACY_THRESHOLD}",
        requires_tool["accuracy"],
        passes_rt,
    )

    print("\n  Per-domain breakdown:")
    for domain, m in domain_breakdown.items():
        flag = " <--" if not m["passes_threshold"] else ""
        print(
            f"    {domain:<25} macro_f1={m['macro_f1']:.3f}  "
            f"accuracy={m['accuracy']:.3f}  n={m['count']}{flag}"
        )

    print("\n  Per-intent F1:")
    for cls, m in per_intent.items():
        flag = " <--" if m["f1"] < 0.85 and m["support"] > 0 else ""
        print(f"    {cls:<25} f1={m['f1']:.3f}  support={m['support']}{flag}")

    print(f"\n  Fallback rate: {fallback['fallback_rate']:.3f} ({fallback['fallback_count']}/{fallback['total']} records)")

    perf = compute_performance_stats(results)
    print("\n  Performance:")
    lat = perf["latency_ms"]
    print(f"    latency   p50={lat['p50']}ms  p95={lat['p95']}ms  mean={lat['mean']}ms  max={lat['max']}ms")
    tok = perf["tokens"]
    print(f"    tokens    avg_prompt={tok['avg_prompt_per_call']}  avg_completion={tok['avg_completion_per_call']}  total={tok['total_prompt'] + tok['total_completion']}")

    print(f"\n  Results written to: {out_path}")

    sys.exit(0 if passes_all else 1)


if __name__ == "__main__":
    main()
