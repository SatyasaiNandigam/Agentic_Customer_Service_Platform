"""Response-generator node isolation eval runner.

Hard-assertion harness (must_contain / must_not_contain) with optional
DeepEval GEval LLM-as-judge (gpt-4o-mini) for grounding and tone quality.

Response paths under test:
  - tool_result: structured JSON injected → response must reference specific IDs/amounts
  - tool_error:  graceful fallback → raw error details must NOT appear in response
  - direct:      chitchat / faq_policy / unknown → on-topic or polite off-topic refusal
  - rewrite:     output_retry_count > 0 / guardrail_violation set → re-generation still valid

GEval runs after all responses are collected and is non-blocking (failures do not
affect the exit code). Enabled with --geval flag.

Usage:
    python eval/run_response_generator_eval.py
    python eval/run_response_generator_eval.py --dataset eval/datasets/response_generator.jsonl
    python eval/run_response_generator_eval.py --concurrency 4 --geval
    python eval/run_response_generator_eval.py --concurrency 4 --geval --geval-concurrency 2

Exit codes:
    0 — all hard thresholds pass (must_contain >= 98%, must_not_contain 100%, refusal >= 99%)
    1 — any hard threshold fails or eval aborted
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

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from app.agent.state import create_initial_state
from app.config import get_settings
from app.agent.nodes.response_generator import make_response_generator_node
from eval.callback_handler import attach_token_capture, capture_tokens
from eval.response_generator_eval_types import ResponseGeneratorRecord, ResponseGeneratorResult
from eval.response_generator_metrics import (
    MUST_CONTAIN_THRESHOLD,
    MUST_NOT_CONTAIN_THRESHOLD,
    OFF_TOPIC_REFUSAL_THRESHOLD,
    GEVAL_SCORE_THRESHOLD,
    build_full_report,
    compute_must_contain_pass_rate,
    compute_must_not_contain_pass_rate,
    compute_off_topic_refusal_rate,
    compute_geval_summary,
    compute_performance_stats,
    compute_per_category_metrics,
)

# deepeval 3.9.9 default model is "gpt-5.4" — pin explicitly so no implicit upgrade occurs
_GEVAL_MODEL = "gpt-4o-mini"


# ---------------------------------------------------------------------------
# Off-topic refusal heuristic
# ---------------------------------------------------------------------------

# Phrases from the system prompt refusal instruction — the LLM is told to
# "politely explain you can only assist with their ShopEasy shopping experience"
_REFUSAL_KEYWORDS: list[str] = [
    "only assist",
    "only help",
    "can only",
    "shopeasy",
    "shopping experience",
    "ecommerce",
    "can't help with that",
    "cannot help with that",
    "not able to help with",
    "outside of what i",
    "not able to assist with",
    "orders, products",
    "orders and",
]


def _detect_off_topic_refusal(response: str) -> bool:
    """Heuristic: detect whether the response politely refuses an off-topic request."""
    lowered = response.lower()
    return any(kw in lowered for kw in _REFUSAL_KEYWORDS)


# ---------------------------------------------------------------------------
# GEval criteria per response path
# ---------------------------------------------------------------------------

_GEVAL_CRITERIA: dict[str, str] = {
    "tool_result": (
        "The response accurately references specific data from the provided context "
        "(order IDs, tracking numbers, refund IDs, prices, product names, statuses). "
        "It does not fabricate any facts absent from the context JSON. "
        "Every specific claim in the response is traceable to the context payload."
    ),
    "tool_error": (
        "The response gracefully acknowledges a service issue in professional, "
        "empathetic language without revealing any technical details. "
        "It must not mention error class names, database names, API names, "
        "internal system identifiers, error codes, or raw error message text. "
        "The response should suggest trying again or contacting support."
    ),
    "direct": (
        "For chitchat or FAQ queries: the response is warm, helpful, and relevant "
        "to ecommerce customer service without fabricating order data. "
        "For off-topic queries (not related to ecommerce or shopping): the response "
        "politely declines and redirects the customer to shopping assistance — "
        "it must NOT provide the actual answer to the off-topic question."
    ),
}


def _get_geval_criteria(record: ResponseGeneratorRecord) -> str:
    if record.geval_criteria:
        return record.geval_criteria
    return _GEVAL_CRITERIA.get(record.response_path, _GEVAL_CRITERIA["direct"])


# ---------------------------------------------------------------------------
# State builder
# ---------------------------------------------------------------------------

def _build_state(record: ResponseGeneratorRecord) -> dict:
    state = create_initial_state(
        user_id="eval-rg",
        session_id=f"eval-{record.id}",
        user_role="customer",
    )

    messages: list = []
    for msg in record.messages:
        role = msg.get("role", "human")
        content = msg.get("content", "")
        if role == "human":
            messages.append(HumanMessage(content=content))
        elif role == "ai":
            messages.append(AIMessage(content=content))

    state["messages"] = messages
    state["intent"] = record.intent
    state["tool_result"] = record.tool_result
    state["tool_error"] = record.tool_error
    state["context_summary"] = record.context_summary
    state["guardrail_violation"] = record.guardrail_violation
    state["output_retry_count"] = record.output_retry_count
    return state


# ---------------------------------------------------------------------------
# GEval runner (async, non-blocking — failures do not affect exit code)
# ---------------------------------------------------------------------------

async def _run_geval_single(
    record: ResponseGeneratorRecord,
    result: ResponseGeneratorResult,
    geval_semaphore: asyncio.Semaphore,
) -> tuple[float | None, str | None, str | None]:
    """Run DeepEval GEval for one record. Returns (score, reason, error)."""
    if result.response is None or result.error is not None:
        return None, None, "skipped: no response or node error"

    try:
        from deepeval.metrics import GEval
        from deepeval.test_case import LLMTestCase, SingleTurnParams
    except ImportError:
        return None, None, "deepeval not installed"

    criteria = _get_geval_criteria(record)

    # Build context list for tool_result and tool_error paths
    context: list[str] | None = None
    if record.response_path == "tool_result" and record.tool_result is not None:
        context = [json.dumps(record.tool_result, indent=2, default=str)]
    elif record.response_path == "tool_error" and record.tool_error is not None:
        context = [f"[Internal error — must NOT be shown to customer]: {record.tool_error}"]

    eval_params = [SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT]
    if context is not None:
        eval_params.append(SingleTurnParams.CONTEXT)

    user_input = record.messages[-1]["content"] if record.messages else ""

    test_case = LLMTestCase(
        input=user_input,
        actual_output=result.response,
        context=context,
    )

    metric = GEval(
        name=f"ResponseQuality_{record.response_path}",
        criteria=criteria,
        evaluation_params=eval_params,
        model=_GEVAL_MODEL,
        threshold=GEVAL_SCORE_THRESHOLD,
        async_mode=False,
    )

    async with geval_semaphore:
        try:
            await metric.a_measure(test_case)
            return metric.score, metric.reason, None
        except Exception as exc:
            return None, None, f"{type(exc).__name__}: {exc}"


async def run_geval_all(
    records: list[ResponseGeneratorRecord],
    results: list[ResponseGeneratorResult],
    geval_concurrency: int,
) -> list[ResponseGeneratorResult]:
    """Annotate results with GEval scores in-place. Non-blocking."""
    geval_semaphore = asyncio.Semaphore(geval_concurrency)
    record_map = {r.id: r for r in records}

    tasks = [
        _run_geval_single(record_map[res.id], res, geval_semaphore)
        for res in results
        if res.id in record_map
    ]
    geval_outputs = await asyncio.gather(*tasks)

    for res, (score, reason, err) in zip(results, geval_outputs):
        res.geval_score = score
        res.geval_reason = reason
        res.geval_error = err

    return results


# ---------------------------------------------------------------------------
# Single-record runner
# ---------------------------------------------------------------------------

async def run_single(
    record: ResponseGeneratorRecord,
    semaphore: asyncio.Semaphore,
    response_generator_node,
) -> ResponseGeneratorResult:
    state = _build_state(record)

    error: str | None = None
    response: str | None = None
    prompt_tokens = 0
    completion_tokens = 0

    async with semaphore:
        t0 = time.perf_counter()
        try:
            with capture_tokens() as cb:
                output = await response_generator_node(state)
            prompt_tokens = cb.prompt_tokens
            completion_tokens = cb.completion_tokens

            # response_generator appends AIMessage to messages — take the last one
            new_msgs = output.get("messages", [])
            if new_msgs:
                response = str(new_msgs[-1].content).strip()
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)

    # --- Hard assertions ---
    response_lower = (response or "").lower()

    mc_failures = [s for s in record.must_contain if s.lower() not in response_lower]
    mnc_failures = [s for s in record.must_not_contain if s.lower() in response_lower]

    # --- Off-topic refusal detection ---
    is_refusal = _detect_off_topic_refusal(response or "")

    return ResponseGeneratorResult(
        id=record.id,
        category=record.category,
        intent=record.intent,
        response_path=record.response_path,
        response=response,
        must_contain_passed=len(mc_failures) == 0,
        must_contain_failures=mc_failures,
        must_not_contain_passed=len(mnc_failures) == 0,
        must_not_contain_failures=mnc_failures,
        expected_off_topic_refusal=record.expected_off_topic_refusal,
        is_off_topic_refusal=is_refusal,
        latency_ms=latency_ms,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        error=error,
    )


async def run_all(
    records: list[ResponseGeneratorRecord],
    concurrency: int,
    response_generator_node,
    use_geval: bool = False,
    geval_concurrency: int = 2,
) -> list[ResponseGeneratorResult]:
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [run_single(r, semaphore, response_generator_node) for r in records]
    results = await asyncio.gather(*tasks)

    if use_geval:
        print("\n  Running DeepEval GEval (gpt-4o-mini) — non-blocking ...")
        results = await run_geval_all(records, list(results), geval_concurrency)

    return list(results)


# ---------------------------------------------------------------------------
# Dataset loader
# ---------------------------------------------------------------------------

def load_dataset(path: Path) -> list[ResponseGeneratorRecord]:
    records: list[ResponseGeneratorRecord] = []
    required = {"id", "category", "intent", "response_path", "messages", "must_contain", "must_not_contain"}
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            print(f"[WARN] Skipping malformed line {i}: {exc}", file=sys.stderr)
            continue
        if missing := required - obj.keys():
            print(f"[WARN] Skipping line {i} — missing fields {missing}", file=sys.stderr)
            continue
        records.append(
            ResponseGeneratorRecord(
                id=obj["id"],
                category=obj["category"],
                intent=obj["intent"],
                response_path=obj["response_path"],
                messages=obj["messages"],
                must_contain=obj["must_contain"],
                must_not_contain=obj["must_not_contain"],
                tool_result=obj.get("tool_result"),
                tool_error=obj.get("tool_error"),
                context_summary=obj.get("context_summary"),
                guardrail_violation=obj.get("guardrail_violation"),
                output_retry_count=obj.get("output_retry_count", 0),
                expected_off_topic_refusal=obj.get("expected_off_topic_refusal", False),
                geval_criteria=obj.get("geval_criteria"),
                notes=obj.get("notes"),
            )
        )
    return records


# ---------------------------------------------------------------------------
# Result writer
# ---------------------------------------------------------------------------

def write_results(
    results: list[ResponseGeneratorResult],
    dataset: list[ResponseGeneratorRecord],
    run_metadata: dict,
) -> Path:
    report = build_full_report(results, dataset, run_metadata)
    out_dir = Path("eval/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_response_generator.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# Console helpers
# ---------------------------------------------------------------------------

def _print_threshold(label: str, value: float, passes: bool, fmt: str = ".4f") -> None:
    status = "PASS" if passes else "FAIL"
    flag = "" if passes else "  <--"
    print(f"    {label:<60} {value:{fmt}}  {status}{flag}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run response_generator node isolation eval."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("eval/datasets/response_generator.jsonl"),
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=4,
        help="Concurrent response_generator calls (default: 4)",
    )
    parser.add_argument(
        "--geval",
        action="store_true",
        default=False,
        help="Enable DeepEval GEval LLM judge (gpt-4o-mini). Non-blocking. Off by default.",
    )
    parser.add_argument(
        "--geval-concurrency",
        type=int,
        default=2,
        dest="geval_concurrency",
        help="Concurrent GEval calls (default: 2; avoids OpenAI rate limits)",
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

    by_cat = {}
    for r in dataset:
        by_cat.setdefault(r.category, 0)
        by_cat[r.category] += 1
    cat_summary = "  ".join(f"{k}={v}" for k, v in sorted(by_cat.items()))
    print(f"  {len(dataset)} records loaded  ({cat_summary})")

    off_topic_count = sum(1 for r in dataset if r.expected_off_topic_refusal)
    print(f"  {off_topic_count} off-topic refusal records")

    # Initialise the LLM + node
    print("Initialising response_generator LLM and node ...")
    settings = get_settings()
    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=0.0,
        max_tokens=settings.openai_max_tokens,
    )
    attach_token_capture(llm)
    response_generator_node = make_response_generator_node(llm)
    print(f"  model={settings.openai_model}  max_tokens={settings.openai_max_tokens}")

    if args.geval:
        print(f"  GEval: ENABLED ({_GEVAL_MODEL}, concurrency={args.geval_concurrency})")
    else:
        print("  GEval: DISABLED (pass --geval to enable)")

    print(f"\nRunning response_generator eval (concurrency={args.concurrency}) ...")
    t_start = time.perf_counter()
    results = asyncio.run(
        run_all(
            dataset,
            concurrency=args.concurrency,
            response_generator_node=response_generator_node,
            use_geval=args.geval,
            geval_concurrency=args.geval_concurrency,
        )
    )
    duration = round(time.perf_counter() - t_start, 1)

    error_count = sum(1 for r in results if r.error is not None)
    run_metadata = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_path": str(args.dataset),
        "total_cases": len(results),
        "concurrency": args.concurrency,
        "duration_seconds": duration,
        "errors": error_count,
        "geval_enabled": args.geval,
        "geval_model": _GEVAL_MODEL if args.geval else None,
        "llm_model": settings.openai_model,
        "note": "Response-generator isolation eval: hard assertions + optional GEval",
    }

    out_path = write_results(results, dataset, run_metadata)

    # --- Compute metrics ---
    mc = compute_must_contain_pass_rate(results)
    mnc = compute_must_not_contain_pass_rate(results)
    refusal = compute_off_topic_refusal_rate(results)
    geval_summary = compute_geval_summary(results)
    perf = compute_performance_stats(results)
    per_cat = compute_per_category_metrics(results)

    passes_all = mc["passes"] and mnc["passes"] and refusal["passes"]
    overall_status = "PASS" if passes_all else "FAIL"

    print(
        f"\n  total={len(results)}  errors={error_count}  "
        f"duration={duration}s  [{overall_status}]"
    )

    print("\n  Threshold checks (hard assertions):")
    _print_threshold(
        f"must_contain_pass_rate >= {MUST_CONTAIN_THRESHOLD:.0%}",
        mc["pass_rate"],
        mc["passes"],
    )
    _print_threshold(
        f"must_not_contain_pass_rate >= {MUST_NOT_CONTAIN_THRESHOLD:.0%}",
        mnc["pass_rate"],
        mnc["passes"],
    )
    _print_threshold(
        f"off_topic_refusal_rate >= {OFF_TOPIC_REFUSAL_THRESHOLD:.0%}  (n={refusal['total']})",
        refusal["rate"],
        refusal["passes"],
    )

    if args.geval and geval_summary["evaluated"] > 0:
        avg = geval_summary["avg_score"] or 0.0
        print(f"\n  GEval summary (informational — non-blocking):")
        print(
            f"    evaluated={geval_summary['evaluated']}  "
            f"errors={geval_summary['errors']}  "
            f"avg_score={avg:.4f}  "
            f"below_{GEVAL_SCORE_THRESHOLD}={geval_summary['below_threshold']}"
        )
        for path, pm in geval_summary["per_path"].items():
            print(
                f"    {path:<12} n={pm['count']}  "
                f"avg={pm['avg_score']:.4f}  "
                f"below_threshold={pm['below_threshold']}"
            )

    print("\n  Per-category:")
    for cat, m in per_cat.items():
        if m.get("count", 0) == 0:
            continue
        geval_str = (
            f"  avg_geval={m['avg_geval_score']:.4f}"
            if m.get("avg_geval_score") is not None
            else ""
        )
        print(
            f"    {cat:<12}  n={m['count']}  "
            f"mc_ok={m['must_contain_passed']}  "
            f"mnc_ok={m['must_not_contain_passed']}  "
            f"refusal_ok={m['refusal_correct']}  "
            f"err={m['errors']}  "
            f"avg_lat={m['avg_latency_ms']}ms"
            f"{geval_str}"
        )

    lat = perf["latency_ms"]
    api = perf["api_tokens"]
    print(
        f"\n  Latency:  p50={lat['p50']}ms  p95={lat['p95']}ms  "
        f"mean={lat['mean']}ms  max={lat['max']}ms"
    )
    print(
        f"  Tokens:   prompt_total={api['total_prompt']}  "
        f"completion_total={api['total_completion']}  "
        f"avg_prompt={api['avg_prompt']}  avg_completion={api['avg_completion']}"
    )

    # Surface failures
    all_failures = [
        r for r in results
        if not r.must_contain_passed
        or not r.must_not_contain_passed
        or (r.expected_off_topic_refusal and not r.is_off_topic_refusal)
        or r.error is not None
    ]
    if all_failures:
        print(f"\n  Failures ({len(all_failures)}):")
        for r in all_failures[:20]:
            reasons = []
            if not r.must_contain_passed:
                reasons.append(f"must_contain_missing={r.must_contain_failures}")
            if not r.must_not_contain_passed:
                reasons.append(f"must_not_contain_leaked={r.must_not_contain_failures}")
            if r.expected_off_topic_refusal and not r.is_off_topic_refusal:
                reasons.append("off_topic_not_refused")
            if r.error:
                reasons.append(f"error={r.error!r:.80}")
            preview = (r.response or "")[:120].replace("\n", " ")
            print(f"    [{r.category}] {r.id}  {', '.join(reasons)}")
            print(f"       response: {preview!r}")
        if len(all_failures) > 20:
            print(f"    ... and {len(all_failures) - 20} more (see results file)")

    # Show GEval low-scorers when enabled
    if args.geval and geval_summary.get("low_scorers"):
        print(f"\n  GEval low-scorers (score < {GEVAL_SCORE_THRESHOLD}):")
        for item in geval_summary["low_scorers"][:10]:
            print(f"    {item['id']}  score={item['score']:.4f}  reason: {item['reason'][:100]}")

    print(f"\n  Results written to: {out_path}")
    sys.exit(0 if passes_all else 1)


if __name__ == "__main__":
    main()
