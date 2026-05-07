"""Memory node (maybe_summarize) isolation eval runner.

Hard-assertion harness — no LLM judge. Tests five behavioral categories:
  - below_threshold: trigger must NOT fire (< 10 new messages)
  - at_threshold:    trigger must fire at exactly 10 new messages
  - pair_preservation: AIMessage+ToolMessage pair at boundary must not be split
  - incremental:     existing context_summary is merged into new summary
  - key_entity:      order IDs / tracking numbers / refund IDs appear verbatim in summary

Token reduction rate (tiktoken cl100k_base) is the primary cost metric:
reports aggregate (input_tokens → summary_tokens) across all triggered records.

Usage:
    python eval/run_memory_eval.py
    python eval/run_memory_eval.py --dataset eval/datasets/memory.jsonl
    python eval/run_memory_eval.py --concurrency 5

Exit codes:
    0 — all thresholds pass
    1 — any threshold fails or eval aborted due to errors

Requires OPENAI_API_KEY set (reads from .env).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import tiktoken
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.agent.state import create_initial_state
from app.memory.summarizer import maybe_summarize, _get_summarizer_llm
from eval.callback_handler import attach_token_capture, capture_tokens
from eval.memory_eval_types import MemoryRecord, MemoryResult
from eval.memory_metrics import (
    TRIGGER_PRECISION_THRESHOLD,
    TRIGGER_RECALL_THRESHOLD,
    ENTITY_RETENTION_THRESHOLD,
    PAIR_PRESERVATION_THRESHOLD,
    TOKEN_REDUCTION_THRESHOLD,
    SUMMARY_LENGTH_MAX_TOKENS,
    SUMMARY_LENGTH_PASS_THRESHOLD,
    build_full_report,
    compute_trigger_metrics,
    compute_entity_retention,
    compute_pair_preservation,
    compute_token_reduction,
    compute_summary_length,
    compute_excludes_pass_rate,
    compute_performance_stats,
    compute_per_category_metrics,
)

# ---------------------------------------------------------------------------
# tiktoken helpers
# ---------------------------------------------------------------------------

_ENC = tiktoken.get_encoding("cl100k_base")


def _count_text_tokens(text: str) -> int:
    return len(_ENC.encode(text))


def _message_text(msg: object) -> str:
    content = getattr(msg, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        return " ".join(parts)
    return str(content)


def _count_message_tokens(messages: list) -> int:
    return sum(_count_text_tokens(_message_text(m)) for m in messages)


# ---------------------------------------------------------------------------
# State builder
# ---------------------------------------------------------------------------

def _build_state(record: MemoryRecord) -> dict:
    state = create_initial_state(
        user_id="eval-memory",
        session_id=f"eval-{record.id}",
        user_role="customer",
    )

    messages: list = []
    for msg in record.messages:
        role = msg["role"]
        content = msg.get("content", "")
        if role == "human":
            messages.append(HumanMessage(content=content))
        elif role == "ai":
            if msg.get("has_tool_calls"):
                tc_id = msg.get("tool_call_id", f"tc-{record.id}")
                messages.append(
                    AIMessage(
                        content="",
                        tool_calls=[
                            {
                                "id": tc_id,
                                "name": msg.get("tool_name", "eval_tool"),
                                "args": {},
                                "type": "tool_call",
                            }
                        ],
                    )
                )
            else:
                messages.append(AIMessage(content=content))
        elif role == "tool":
            tc_id = msg.get("tool_call_id", f"tc-{record.id}")
            messages.append(ToolMessage(content=content, tool_call_id=tc_id))

    state["messages"] = messages
    state["summarized_message_count"] = record.summarized_message_count
    state["context_summary"] = record.existing_summary
    return state


# ---------------------------------------------------------------------------
# Single-record runner
# ---------------------------------------------------------------------------

async def run_single(
    record: MemoryRecord,
    semaphore: asyncio.Semaphore,
) -> MemoryResult:
    state = _build_state(record)
    messages = state["messages"]

    error: str | None = None
    prompt_tokens = 0
    completion_tokens = 0

    async with semaphore:
        t0 = time.perf_counter()
        try:
            with capture_tokens() as cb:
                output = await maybe_summarize(state)
            prompt_tokens = cb.prompt_tokens
            completion_tokens = cb.completion_tokens
        except Exception as exc:
            output = {}
            error = f"{type(exc).__name__}: {exc}"
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)

    # --- Trigger detection ---
    actual_triggers: bool = bool(output)
    trigger_correct: bool = actual_triggers == record.expected_triggers

    context_summary: str | None = output.get("context_summary") if actual_triggers else None
    output_summarized_count: int = (
        output.get("summarized_message_count", record.summarized_message_count)
        if actual_triggers
        else record.summarized_message_count
    )

    # --- tiktoken counts (only meaningful when triggered) ---
    if actual_triggers:
        slice_end   = output_summarized_count
        input_toks  = _count_message_tokens(messages[record.summarized_message_count:slice_end])
        # For incremental records the LLM receives both the existing_summary and the new
        # messages slice — the output merges both, so both must be counted as input.
        if record.existing_summary:
            input_toks += _count_text_tokens(record.existing_summary)
        output_toks = _count_text_tokens(context_summary or "")
        reduction   = (input_toks - output_toks) / input_toks if input_toks > 0 else None
    else:
        input_toks  = 0
        output_toks = 0
        reduction   = None

    # --- Pair preservation: boundary must not land on a ToolMessage index ---
    if actual_triggers and output_summarized_count < len(messages):
        pair_preserved = not isinstance(messages[output_summarized_count], ToolMessage)
    else:
        pair_preserved = True  # not applicable or cursor is past the end

    # --- Entity contains/excludes (case-insensitive) ---
    summary_lower = (context_summary or "").lower()
    contains_passed = all(p.lower() in summary_lower for p in record.expected_summary_contains)
    excludes_passed = all(p.lower() not in summary_lower for p in record.expected_summary_excludes)

    return MemoryResult(
        id=record.id,
        category=record.category,
        expected_triggers=record.expected_triggers,
        actual_triggers=actual_triggers,
        trigger_correct=trigger_correct,
        context_summary=context_summary,
        output_summarized_count=output_summarized_count,
        contains_passed=contains_passed,
        excludes_passed=excludes_passed,
        pair_preserved=pair_preserved,
        input_token_count=input_toks,
        output_token_count=output_toks,
        token_reduction_rate=reduction,
        latency_ms=latency_ms,
        error=error,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
    )


async def run_all(
    records: list[MemoryRecord],
    concurrency: int = 5,
) -> list[MemoryResult]:
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [run_single(r, semaphore) for r in records]
    return await asyncio.gather(*tasks)


# ---------------------------------------------------------------------------
# Dataset loader
# ---------------------------------------------------------------------------

def load_dataset(path: Path) -> list[MemoryRecord]:
    records: list[MemoryRecord] = []
    required = {
        "id", "category", "messages", "summarized_message_count",
        "expected_triggers", "expected_summary_contains",
        "expected_summary_excludes", "expected_output_token_count_max",
    }
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            print(f"[WARN] Skipping malformed line {i} in {path}: {exc}", file=sys.stderr)
            continue
        if missing := required - obj.keys():
            print(f"[WARN] Skipping line {i} — missing fields {missing}", file=sys.stderr)
            continue
        records.append(
            MemoryRecord(
                id=obj["id"],
                category=obj["category"],
                messages=obj["messages"],
                summarized_message_count=obj["summarized_message_count"],
                existing_summary=obj.get("existing_summary"),
                expected_triggers=obj["expected_triggers"],
                expected_summary_contains=obj["expected_summary_contains"],
                expected_summary_excludes=obj["expected_summary_excludes"],
                expected_output_token_count_max=obj["expected_output_token_count_max"],
                notes=obj.get("notes"),
            )
        )
    return records


# ---------------------------------------------------------------------------
# Result writer
# ---------------------------------------------------------------------------

def write_results(
    results: list[MemoryResult],
    dataset: list[MemoryRecord],
    run_metadata: dict,
) -> Path:
    report = build_full_report(results, dataset, run_metadata)
    out_dir = Path("eval/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_memory.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# Console helpers
# ---------------------------------------------------------------------------

def _print_threshold(label: str, value: float, passes: bool, fmt: str = ".4f") -> None:
    status = "PASS" if passes else "FAIL"
    flag   = "" if passes else "  <--"
    print(f"    {label:<60} {value:{fmt}}  {status}{flag}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run memory node (maybe_summarize) isolation eval."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("eval/datasets/memory.jsonl"),
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=5,
        help="Concurrent LLM calls (default: 5; non-triggered records complete instantly)",
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

    trigger_count = sum(1 for r in dataset if r.expected_triggers)
    print(
        f"  {len(dataset)} records loaded  "
        f"({trigger_count} expected to trigger, "
        f"{len(dataset) - trigger_count} expected no-ops)."
    )

    # Force summarizer LLM initialization and attach token capture
    print("Initializing summarizer LLM and attaching token capture ...")
    _llm = _get_summarizer_llm()
    attach_token_capture(_llm)
    print("  Ready.")

    print(f"\nRunning memory eval (concurrency={args.concurrency}) ...")
    t_start = time.perf_counter()
    results = asyncio.run(run_all(dataset, concurrency=args.concurrency))
    duration = round(time.perf_counter() - t_start, 1)

    error_count = sum(1 for r in results if r.error is not None)
    run_metadata = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_path": str(args.dataset),
        "total_cases": len(results),
        "concurrency": args.concurrency,
        "duration_seconds": duration,
        "errors": error_count,
        "note": "Hard-assertion harness for maybe_summarize node. No LLM judge.",
    }

    out_path = write_results(results, dataset, run_metadata)

    # --- Compute metrics ---
    trigger   = compute_trigger_metrics(results)
    entity    = compute_entity_retention(results)
    pair      = compute_pair_preservation(results)
    reduction = compute_token_reduction(results)
    length    = compute_summary_length(results)
    excludes  = compute_excludes_pass_rate(results)
    perf      = compute_performance_stats(results)
    per_cat   = compute_per_category_metrics(results)

    passes_all = all([
        trigger["passes_precision"],
        trigger["passes_recall"],
        entity["passes"],
        pair["passes"],
        reduction["passes"],
        length["passes"],
        excludes["passes"],
    ])
    overall_status = "PASS" if passes_all else "FAIL"

    triggered_count = sum(1 for r in results if r.actual_triggers)
    print(
        f"\n  triggered={triggered_count}/{len(results)}  errors={error_count}  "
        f"duration={duration}s  [{overall_status}]"
    )

    print("\n  Threshold checks:")
    _print_threshold(
        f"trigger_precision >= {TRIGGER_PRECISION_THRESHOLD:.0%}",
        trigger["precision"], trigger["passes_precision"],
    )
    _print_threshold(
        f"trigger_recall >= {TRIGGER_RECALL_THRESHOLD:.0%}",
        trigger["recall"], trigger["passes_recall"],
    )
    _print_threshold(
        f"entity_retention >= {ENTITY_RETENTION_THRESHOLD:.0%}",
        entity["rate"], entity["passes"],
    )
    _print_threshold(
        f"pair_preservation >= {PAIR_PRESERVATION_THRESHOLD:.0%}",
        pair["rate"], pair["passes"],
    )
    _print_threshold(
        f"token_reduction_rate (aggregate) >= {TOKEN_REDUCTION_THRESHOLD:.0%}",
        reduction["aggregate_rate"], reduction["passes"],
    )
    _print_threshold(
        f"summary_length_pass_rate (all <= {SUMMARY_LENGTH_MAX_TOKENS} tokens) >= {SUMMARY_LENGTH_PASS_THRESHOLD:.0%}",
        length["pass_rate"], length["passes"],
    )
    _print_threshold(
        "excludes_pass_rate >= 100%",
        excludes["pass_rate"], excludes["passes"],
    )

    print("\n  Per-category results:")
    for cat, m in per_cat.items():
        if m["count"] == 0:
            continue
        print(
            f"    {cat:<20} n={m['count']}  "
            f"triggered={m.get('triggered', 0)}  "
            f"trigger_correct={m.get('trigger_correct', 0)}  "
            f"contains_ok={m.get('contains_passed', 0)}  "
            f"pair_ok={m.get('pair_preserved', 0)}"
            + (f"  avg_in={m['avg_input_tokens']}tok  avg_out={m['avg_output_tokens']}tok"
               if m.get("avg_input_tokens") is not None else "")
        )

    trig_lat = perf["triggered_latency_ms"]
    api_tok  = perf["api_tokens"]
    print(
        f"\n  Triggered record latency:  "
        f"p50={trig_lat['p50']}ms  p95={trig_lat['p95']}ms  "
        f"mean={trig_lat['mean']}ms  max={trig_lat['max']}ms"
    )
    print(
        f"  Token reduction (tiktoken): "
        f"in={reduction['total_input_tokens']}  "
        f"out={reduction['total_output_tokens']}  "
        f"rate={reduction['aggregate_rate']:.1%}  "
        f"max_summary_length={length['max_seen']} tokens"
    )
    print(
        f"  API tokens (callback):  "
        f"prompt={api_tok['total_prompt']}  "
        f"completion={api_tok['total_completion']}"
    )

    # Surface failures
    all_failures = [
        r for r in results
        if not r.trigger_correct
        or not r.contains_passed
        or not r.excludes_passed
        or not r.pair_preserved
        or (r.actual_triggers and r.output_token_count > SUMMARY_LENGTH_MAX_TOKENS)
        or r.error is not None
    ]
    if all_failures:
        print(f"\n  Failures ({len(all_failures)}):")
        for r in all_failures[:20]:
            reasons = []
            if not r.trigger_correct:
                reasons.append(f"trigger_wrong(expected={r.expected_triggers},got={r.actual_triggers})")
            if not r.contains_passed:
                reasons.append("contains_failed")
            if not r.excludes_passed:
                reasons.append("excludes_failed")
            if not r.pair_preserved:
                reasons.append(f"pair_split_at={r.output_summarized_count}")
            if r.actual_triggers and r.output_token_count > SUMMARY_LENGTH_MAX_TOKENS:
                reasons.append(f"too_long={r.output_token_count}tok")
            if r.error:
                reasons.append(f"error={r.error!r:.60}")
            print(f"    [{r.category}] {r.id}  {', '.join(reasons)}")
        if len(all_failures) > 20:
            print(f"    ... and {len(all_failures) - 20} more (see results file)")

    print(f"\n  Results written to: {out_path}")
    sys.exit(0 if passes_all else 1)


if __name__ == "__main__":
    main()
