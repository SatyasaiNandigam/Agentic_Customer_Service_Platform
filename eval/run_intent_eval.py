"""Intent classification accuracy eval runner.

Usage:
    python eval/run_intent_eval.py
    python eval/run_intent_eval.py --dataset eval/datasets/intent_classification.jsonl
    python eval/run_intent_eval.py --dataset eval/datasets/intent_classification.jsonl --concurrency 5

Exit codes:
    0 — macro-F1 >= 0.90 (passes threshold)
    1 — macro-F1 < 0.90 or eval aborted due to API errors
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from datetime import date
from pathlib import Path

# Load .env before any project imports so os.environ is populated for ChatOpenAI
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from langchain_core.messages import HumanMessage

# ensure project root is on sys.path when invoked as `python eval/run_intent_eval.py`
_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from app.agent.nodes.classifier import classifier_node
from app.agent.state import create_initial_state
from app.config import get_settings
from eval.metrics import MACRO_F1_THRESHOLD, build_full_report
from eval.eval_types import EvalRecord, EvalResult

_FALLBACK_CONFIDENCE = 0.0
_FALLBACK_INTENT = "unknown"
_FALLBACK_ERROR_RATE_ABORT = 0.20  # abort if >20% of results are classifier fallbacks


def _build_state(text: str):
    state = create_initial_state(user_id=1, session_id="eval-run", user_role="customer")
    state["messages"] = [HumanMessage(content=text)]
    return state


async def run_single(record: EvalRecord, semaphore: asyncio.Semaphore) -> EvalResult:
    state = _build_state(record.text)
    t0 = time.perf_counter()
    error: str | None = None

    async with semaphore:
        try:
            output = await classifier_node(state)
        except Exception as exc:
            output = {"intent": _FALLBACK_INTENT, "confidence": _FALLBACK_CONFIDENCE,
                      "requires_tool": False, "needs_escalation": False}
            error = str(exc)

    latency_ms = (time.perf_counter() - t0) * 1000

    predicted = output["intent"]
    confidence = output["confidence"]

    # Distinguish classifier's own fallback from a genuine unknown prediction
    if error is None and predicted == _FALLBACK_INTENT and confidence == _FALLBACK_CONFIDENCE:
        error = "classifier_fallback"

    return EvalResult(
        id=record.id,
        text=record.text,
        expected=record.expected,
        predicted=predicted,
        confidence=confidence,
        requires_tool=output.get("requires_tool", False),
        needs_escalation=output.get("needs_escalation", False),
        correct=(predicted == record.expected and error != "classifier_fallback"),
        latency_ms=round(latency_ms, 1),
        error=error,
    )


async def run_all(records: list[EvalRecord], concurrency: int = 10) -> list[EvalResult]:
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [run_single(r, semaphore) for r in records]
    return await asyncio.gather(*tasks)


def load_dataset(path: Path) -> list[EvalRecord]:
    records: list[EvalRecord] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            print(f"[WARN] Skipping malformed line {i} in {path}: {exc}", file=sys.stderr)
            continue
        required = {"id", "text", "expected"}
        if missing := required - obj.keys():
            print(f"[WARN] Skipping line {i} — missing fields {missing}", file=sys.stderr)
            continue
        records.append(EvalRecord(
            id=obj["id"],
            text=obj["text"],
            expected=obj["expected"],
            source=obj.get("source", "unknown"),
            boundary_pair=obj.get("boundary_pair"),
            notes=obj.get("notes"),
        ))
    return records


def write_results(results: list[EvalResult], dataset: list[EvalRecord], run_metadata: dict) -> Path:
    report = build_full_report(results, dataset, run_metadata)
    out_dir = Path("eval/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{date.today()}_intent_classification.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return out_path


def _check_api_key_abort(results: list[EvalResult]) -> bool:
    """Return True (and print error) if >20% of results look like API key failures."""
    fallback_count = sum(1 for r in results if r.error == "classifier_fallback")
    if len(results) > 0 and fallback_count / len(results) > _FALLBACK_ERROR_RATE_ABORT:
        print(
            f"\n[ERROR] {fallback_count}/{len(results)} results are classifier fallbacks "
            f"({fallback_count/len(results):.0%}). "
            "This usually means OPENAI_API_KEY is missing or rate-limited. "
            "Check your .env file and retry.",
            file=sys.stderr,
        )
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Run intent classification accuracy eval.")
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
    print(f"Running classifier eval (model={settings.classifier_model}, concurrency={args.concurrency}) ...")

    t_start = time.perf_counter()
    results = asyncio.run(run_all(dataset, concurrency=args.concurrency))
    duration = round(time.perf_counter() - t_start, 1)

    if _check_api_key_abort(results):
        sys.exit(1)

    error_count = sum(1 for r in results if r.error is not None)
    run_metadata = {
        "date": str(date.today()),
        "dataset_path": str(args.dataset),
        "total_cases": len(results),
        "model": settings.classifier_model,
        "confidence_threshold": 0.5,
        "concurrency": args.concurrency,
        "duration_seconds": duration,
        "errors": error_count,
    }

    out_path = write_results(results, dataset, run_metadata)

    # --- Console summary ---
    correct = sum(1 for r in results if r.correct)
    accuracy = correct / len(results) if results else 0.0

    from eval.metrics import compute_per_intent_metrics, compute_macro_f1
    per_intent = compute_per_intent_metrics(results)
    macro_f1 = compute_macro_f1(per_intent)

    status = "PASS" if macro_f1 >= MACRO_F1_THRESHOLD else "FAIL"
    print(
        f"\n  accuracy={accuracy:.3f}  macro_f1={macro_f1:.3f}  "
        f"errors={error_count}  duration={duration}s  [{status}]"
    )

    print(f"\n  Per-intent F1:")
    for cls, m in per_intent.items():
        flag = " <--" if m["f1"] < 0.85 and m["support"] > 0 else ""
        print(f"    {cls:<25} f1={m['f1']:.3f}  support={m['support']}{flag}")

    print(f"\n  Results written to: {out_path}")

    sys.exit(0 if macro_f1 >= MACRO_F1_THRESHOLD else 1)


if __name__ == "__main__":
    main()
