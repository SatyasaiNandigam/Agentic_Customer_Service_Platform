"""Customer delegator domain-classification eval runner.

Usage:
    python eval/run_customer_delegator_eval.py
    python eval/run_customer_delegator_eval.py --dataset eval/datasets/customer_delegator.jsonl
    python eval/run_customer_delegator_eval.py --concurrency 5

Exit codes:
    0 — all four thresholds pass (macro-F1, safety precision, safety recall, false-block rate)
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

# ensure project root is on sys.path when invoked as `python eval/run_customer_delegator_eval.py`
_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from langchain_openai import ChatOpenAI

from app.agent.nodes.customer_delegator import make_customer_delegator_node
from app.agent.state import create_initial_state
from app.config import get_settings
from eval.callback_handler import attach_token_capture, capture_tokens
from eval.delegator_eval_types import DelegatorRecord, DelegatorResult
from eval.delegator_metrics import (
    BLOCK_PRECISION_THRESHOLD,
    ESCALATE_PRECISION_THRESHOLD,
    FALSE_BLOCK_RATE_THRESHOLD,
    MACRO_F1_THRESHOLD,
    SAFETY_RECALL_THRESHOLD,
    build_full_report,
    compute_false_block_rate,
    compute_macro_f1,
    compute_per_domain_metrics,
    compute_performance_stats,
    compute_safety_metrics,
)

# If more than this fraction of results fall back to need_advice AND the expected
# rate is much lower, it is almost certainly an API key / rate-limit failure.
_FALLBACK_ABORT_THRESHOLD = 0.30
_EXPECTED_NEED_ADVICE_RATE = 0.125  # ~25 out of 200 in the dataset


def _build_state(record: DelegatorRecord):
    state = create_initial_state(
        user_id="eval-delegator",
        session_id=f"eval-{record.id}",
        user_role="customer",
    )
    messages: list = []

    # History messages first — they form the prior-turns context the node uses
    if record.history:
        for turn in record.history:
            cls = HumanMessage if turn["role"] == "human" else AIMessage
            messages.append(cls(content=turn["content"]))

    # Current message last — this is what _extract_last_human_message returns
    messages.append(HumanMessage(content=record.text))
    state["messages"] = messages
    return state


async def run_single(
    record: DelegatorRecord,
    node,
    semaphore: asyncio.Semaphore,
) -> DelegatorResult:
    state = _build_state(record)
    t0 = time.perf_counter()
    error: str | None = None

    prompt_tokens = 0
    completion_tokens = 0

    async with semaphore:
        try:
            with capture_tokens() as cb:
                output = await node(state)
            prompt_tokens = cb.prompt_tokens
            completion_tokens = cb.completion_tokens
        except Exception as exc:
            output = {"customer_domain": "need_advice"}
            error = str(exc)

    latency_ms = (time.perf_counter() - t0) * 1000
    predicted = output.get("customer_domain", "need_advice")

    return DelegatorResult(
        id=record.id,
        text=record.text,
        expected_domain=record.expected_domain,
        predicted_domain=predicted,
        confidence=0.0,  # node strips confidence from its return dict
        correct=(predicted == record.expected_domain and error is None),
        latency_ms=round(latency_ms, 1),
        error=error,
        had_history=bool(record.history),
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
    )


async def run_all(
    records: list[DelegatorRecord],
    node,
    concurrency: int = 10,
) -> list[DelegatorResult]:
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [run_single(r, node, semaphore) for r in records]
    return await asyncio.gather(*tasks)


def load_dataset(path: Path) -> list[DelegatorRecord]:
    records: list[DelegatorRecord] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            print(f"[WARN] Skipping malformed line {i} in {path}: {exc}", file=sys.stderr)
            continue
        required = {"id", "text", "expected_domain"}
        if missing := required - obj.keys():
            print(f"[WARN] Skipping line {i} — missing fields {missing}", file=sys.stderr)
            continue
        record = DelegatorRecord(
            id=obj["id"],
            text=obj["text"],
            expected_domain=obj["expected_domain"],
            history=obj.get("history"),
            boundary_pair=obj.get("boundary_pair"),
            source=obj.get("source", "unknown"),
            notes=obj.get("notes"),
        )
        # Warn if a history-dependent record (id contains _hist_) has no history
        if "_hist_" in record.id and not record.history:
            print(
                f"[WARN] Record {record.id} looks history-dependent but has no history field.",
                file=sys.stderr,
            )
        records.append(record)
    return records


def write_results(
    results: list[DelegatorResult],
    dataset: list[DelegatorRecord],
    run_metadata: dict,
) -> Path:
    report = build_full_report(results, dataset, run_metadata)
    out_dir = Path("eval/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_customer_delegator.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return out_path


def _check_fallback_abort(results: list[DelegatorResult]) -> bool:
    """Warn and return True if need_advice proportion is suspiciously high.

    The node silently returns need_advice on LLM errors, so a large need_advice
    rate when not expected usually signals a missing or rate-limited API key.
    """
    need_advice_count = sum(1 for r in results if r.predicted_domain == "need_advice")
    rate = need_advice_count / len(results) if results else 0.0
    if rate > _FALLBACK_ABORT_THRESHOLD and rate > _EXPECTED_NEED_ADVICE_RATE * 2:
        print(
            f"\n[ERROR] {need_advice_count}/{len(results)} results predicted 'need_advice' "
            f"({rate:.0%}). This is unusually high and likely indicates the LLM is failing "
            "silently (missing API key, rate limit, or model error). Check your .env file.",
            file=sys.stderr,
        )
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run customer_delegator domain-classification eval."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("eval/datasets/customer_delegator.jsonl"),
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
        max_tokens=64,
    )
    attach_token_capture(llm)   # adds ContextVar proxy once; works for any provider
    delegator_node = make_customer_delegator_node(llm)

    print(
        f"Running delegator eval "
        f"(model={settings.classifier_model}, concurrency={args.concurrency}) ..."
    )

    t_start = time.perf_counter()
    results = asyncio.run(run_all(dataset, delegator_node, concurrency=args.concurrency))
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
        "note": "confidence omitted from report — node strips it from output dict",
    }

    out_path = write_results(results, dataset, run_metadata)

    # --- Compute metrics for console summary ---
    correct = sum(1 for r in results if r.correct)
    accuracy = correct / len(results) if results else 0.0

    per_domain = compute_per_domain_metrics(results)
    macro_f1 = compute_macro_f1(per_domain)
    safety = compute_safety_metrics(results)
    false_block = compute_false_block_rate(results)

    passes_macro_f1 = macro_f1 >= MACRO_F1_THRESHOLD
    passes_escalate_prec = safety["escalate"]["precision"] >= ESCALATE_PRECISION_THRESHOLD
    passes_block_prec = safety["block"]["precision"] >= BLOCK_PRECISION_THRESHOLD
    passes_escalate_rec = safety["escalate"]["recall"] >= SAFETY_RECALL_THRESHOLD
    passes_block_rec = safety["block"]["recall"] >= SAFETY_RECALL_THRESHOLD
    passes_false_block = false_block["passes_threshold"]

    passes_all = all([
        passes_macro_f1,
        passes_escalate_prec,
        passes_block_prec,
        passes_escalate_rec,
        passes_block_rec,
        passes_false_block,
    ])

    overall_status = "PASS" if passes_all else "FAIL"
    print(
        f"\n  accuracy={accuracy:.3f}  macro_f1={macro_f1:.3f}  "
        f"errors={error_count}  duration={duration}s  [{overall_status}]"
    )

    print("\n  Threshold checks:")
    _print_threshold(
        f"macro_f1 >= {MACRO_F1_THRESHOLD}",
        macro_f1,
        passes_macro_f1,
    )
    _print_threshold(
        f"escalate_precision >= {ESCALATE_PRECISION_THRESHOLD}",
        safety["escalate"]["precision"],
        passes_escalate_prec,
    )
    _print_threshold(
        f"block_precision >= {BLOCK_PRECISION_THRESHOLD}",
        safety["block"]["precision"],
        passes_block_prec,
    )
    _print_threshold(
        f"escalate_recall >= {SAFETY_RECALL_THRESHOLD}",
        safety["escalate"]["recall"],
        passes_escalate_rec,
    )
    _print_threshold(
        f"block_recall >= {SAFETY_RECALL_THRESHOLD}",
        safety["block"]["recall"],
        passes_block_rec,
    )
    _print_threshold(
        f"false_block_rate <= {FALSE_BLOCK_RATE_THRESHOLD}",
        false_block["false_block_rate"],
        passes_false_block,
        invert=True,
    )

    print("\n  Per-domain F1:")
    for cls, m in per_domain.items():
        flag = " <--" if m["f1"] < 0.90 and m["support"] > 0 else ""
        print(f"    {cls:<20} f1={m['f1']:.3f}  support={m['support']}{flag}")

    perf = compute_performance_stats(results)
    print("\n  Performance:")
    lat = perf["latency_ms"]
    print(f"    latency   p50={lat['p50']}ms  p95={lat['p95']}ms  mean={lat['mean']}ms  max={lat['max']}ms")
    tok = perf["tokens"]
    print(f"    tokens    avg_prompt={tok['avg_prompt_per_call']}  avg_completion={tok['avg_completion_per_call']}  total={tok['total_prompt'] + tok['total_completion']}")

    print(f"\n  Results written to: {out_path}")

    sys.exit(0 if passes_all else 1)


def _print_threshold(label: str, value: float, passes: bool, invert: bool = False) -> None:
    status = "PASS" if passes else "FAIL"
    flag = "" if passes else "  <--"
    print(f"    {label:<45} {value:.4f}  {status}{flag}")


if __name__ == "__main__":
    main()
