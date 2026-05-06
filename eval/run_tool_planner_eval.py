"""Tool planner node isolation eval runner.

Usage:
    python eval/run_tool_planner_eval.py
    python eval/run_tool_planner_eval.py --dataset eval/datasets/tool_planner.jsonl
    python eval/run_tool_planner_eval.py --concurrency 5

Exit codes:
    0 — all thresholds pass (tool selection accuracy, args coverage, p95 latency, RBAC)
    1 — any threshold fails or eval aborted due to errors

Requires the MCP server to be running at MCP_TOOLS_URL (default http://localhost:8001/sse).
Start it with: python -m tools_mcp.server
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

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI

from app.agent.nodes.tool_planner import make_tool_planner_node
from app.agent.state import AgentState, create_initial_state
from app.config import get_settings
from app.mcp_client.tool_registry import get_registry_tools
from eval.callback_handler import attach_token_capture, capture_tokens
from eval.tool_planner_eval_types import ToolPlannerRecord, ToolPlannerResult
from eval.tool_planner_metrics import (
    ARGS_COVERAGE_THRESHOLD,
    P95_LATENCY_THRESHOLD_MS,
    TOOL_SELECTION_ACCURACY_THRESHOLD,
    build_full_report,
    compute_args_coverage_rate,
    compute_per_category_metrics,
    compute_performance_stats,
    compute_rbac_violation_rate,
    compute_tool_selection_accuracy,
)

# Domain lookup so _build_state can set customer_domain correctly
_INTENT_TO_DOMAIN: dict[str, str] = {
    "order_status": "need_information",
    "shipment_tracking": "need_information",
    "refund_status": "need_information",
    "account_info": "need_information",
    "review_lookup": "need_information",
    "product_inquiry": "need_information",
    "product_search": "need_information",
    "order_cancel": "need_assistance",
    "refund_request": "need_assistance",
    "faq_policy": "need_advice",
    "chitchat": "need_advice",
    "unknown": "need_advice",
    "complaint": "need_advice",
}


def _build_state(record: ToolPlannerRecord) -> AgentState:
    state = create_initial_state(
        user_id="eval-tool-planner",
        session_id=f"eval-{record.id}",
        user_role=record.user_role,
    )
    state["intent"] = record.intent
    state["requires_tool"] = not record.expected_no_tool
    state["customer_domain"] = _INTENT_TO_DOMAIN.get(record.intent, "need_advice")

    messages = []
    for msg in record.messages:
        role = msg["role"]
        if role == "human":
            messages.append(HumanMessage(content=msg["content"]))
        elif role == "ai":
            messages.append(AIMessage(content=msg.get("content", "")))
        elif role == "ai_tool_call":
            # AIMessage carrying a prior (failed) tool call — used in retry scenarios
            messages.append(
                AIMessage(
                    content=msg.get("content", ""),
                    tool_calls=[
                        {
                            "id": msg["tool_call_id"],
                            "name": msg["tool_name"],
                            "args": msg["tool_args"],
                            "type": "tool_call",
                        }
                    ],
                )
            )
        elif role == "tool":
            messages.append(
                ToolMessage(
                    content=msg["content"],
                    tool_call_id=msg["tool_call_id"],
                )
            )

    state["messages"] = messages

    if record.tool_error:
        state["tool_error"] = record.tool_error
        state["tool_retry_count"] = record.tool_retry_count

    return state


def _compute_args_covered(tool_input: dict | None, expected_args_schema: dict) -> float:
    """Fraction of expected required arg keys present (with non-None value) in tool_input."""
    if not expected_args_schema:
        return 1.0
    if tool_input is None:
        return 0.0
    present = sum(
        1 for key in expected_args_schema
        if tool_input.get(key) is not None
    )
    return round(present / len(expected_args_schema), 4)


async def run_single(
    record: ToolPlannerRecord,
    node,
    semaphore: asyncio.Semaphore,
) -> ToolPlannerResult:
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
            output = {"selected_tool": None, "tool_input": None}
            error = str(exc)
        latency_ms = (time.perf_counter() - t0) * 1000
    predicted_tool: str | None = output.get("selected_tool")
    tool_input: dict | None = output.get("tool_input")

    # Correct if predicted matches expected (both can be None for no-tool cases)
    tool_correct = (predicted_tool == record.expected_tool) and (error is None)

    args_covered = _compute_args_covered(tool_input, record.expected_args_schema)

    return ToolPlannerResult(
        id=record.id,
        category=record.category,
        intent=record.intent,
        user_role=record.user_role,
        expected_tool=record.expected_tool,
        predicted_tool=predicted_tool,
        tool_correct=tool_correct,
        tool_input=tool_input,
        args_covered=args_covered,
        latency_ms=round(latency_ms, 1),
        error=error,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
    )


async def run_all(
    records: list[ToolPlannerRecord],
    node,
    concurrency: int = 5,
) -> list[ToolPlannerResult]:
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [run_single(r, node, semaphore) for r in records]
    return await asyncio.gather(*tasks)


def load_dataset(path: Path) -> list[ToolPlannerRecord]:
    records: list[ToolPlannerRecord] = []
    required = {"id", "messages", "intent", "user_role", "expected_tool", "expected_args_schema", "expected_no_tool", "category"}
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
            ToolPlannerRecord(
                id=obj["id"],
                messages=obj["messages"],
                intent=obj["intent"],
                user_role=obj["user_role"],
                expected_tool=obj["expected_tool"],
                expected_args_schema=obj["expected_args_schema"],
                expected_no_tool=obj["expected_no_tool"],
                category=obj["category"],
                tool_error=obj.get("tool_error"),
                tool_retry_count=obj.get("tool_retry_count", 0),
                notes=obj.get("notes"),
            )
        )
    return records


def write_results(
    results: list[ToolPlannerResult],
    dataset: list[ToolPlannerRecord],
    run_metadata: dict,
) -> Path:
    report = build_full_report(results, dataset, run_metadata)
    out_dir = Path("eval/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_tool_planner.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return out_path


def _print_threshold(label: str, value: float, passes: bool, invert: bool = False) -> None:
    status = "PASS" if passes else "FAIL"
    flag = "" if passes else "  <--"
    fmt_value = f"{value:.4f}" if not invert else f"{value:.1f}"
    print(f"    {label:<50} {fmt_value}  {status}{flag}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run tool_planner node isolation eval.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("eval/datasets/tool_planner.jsonl"),
        help="Path to labeled JSONL dataset",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=5,
        help="Number of concurrent LLM calls (default: 5)",
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
    # tool_planner uses the planner model; fall back to classifier_model if not set
    model = getattr(settings, "planner_model", None) or settings.classifier_model
    llm = ChatOpenAI(model=model, temperature=0.0)
    attach_token_capture(llm)
    node = make_tool_planner_node(llm)

    # Warm the tool registry cache for every role present in the dataset so the
    # SSE connection cost does not appear inside the timed eval window.
    roles_in_dataset = {r.user_role for r in dataset}
    print(f"Warming tool registry for roles: {sorted(roles_in_dataset)} ...")

    async def _warmup() -> None:
        for role in roles_in_dataset:
            await get_registry_tools(user_id="eval-warmup", user_role=role)

    asyncio.run(_warmup())
    print("  Registry warm.")

    print(f"Running tool_planner eval (model={model}, concurrency={args.concurrency}) ...")
    t_start = time.perf_counter()
    results = asyncio.run(run_all(dataset, node, concurrency=args.concurrency))
    duration = round(time.perf_counter() - t_start, 1)

    error_count = sum(1 for r in results if r.error is not None)

    run_metadata = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_path": str(args.dataset),
        "total_cases": len(results),
        "model": model,
        "concurrency": args.concurrency,
        "duration_seconds": duration,
        "errors": error_count,
        "note": "Runs against real MCP server — ensure MCP_TOOLS_URL is reachable before executing",
    }

    out_path = write_results(results, dataset, run_metadata)

    # --- Compute metrics ---
    tool_accuracy = compute_tool_selection_accuracy(results)
    args_coverage = compute_args_coverage_rate(results)
    per_category = compute_per_category_metrics(results)
    perf = compute_performance_stats(results)
    rbac = compute_rbac_violation_rate(results)

    p95 = perf["latency_ms"]["p95"]

    passes_tool = tool_accuracy >= TOOL_SELECTION_ACCURACY_THRESHOLD
    passes_args = args_coverage >= ARGS_COVERAGE_THRESHOLD
    passes_latency = p95 <= P95_LATENCY_THRESHOLD_MS
    passes_rbac = rbac["count"] == 0
    passes_all = passes_tool and passes_args and passes_latency and passes_rbac

    overall_status = "PASS" if passes_all else "FAIL"
    print(
        f"\n  tool_accuracy={tool_accuracy:.3f}  args_coverage={args_coverage:.3f}  "
        f"p95={p95}ms  rbac_violations={rbac['count']}  errors={error_count}  "
        f"duration={duration}s  [{overall_status}]"
    )

    print("\n  Threshold checks:")
    _print_threshold(
        f"tool_selection_accuracy >= {TOOL_SELECTION_ACCURACY_THRESHOLD}",
        tool_accuracy,
        passes_tool,
    )
    _print_threshold(
        f"args_coverage_rate >= {ARGS_COVERAGE_THRESHOLD}",
        args_coverage,
        passes_args,
    )
    _print_threshold(
        f"p95_latency_ms <= {P95_LATENCY_THRESHOLD_MS}",
        p95,
        passes_latency,
        invert=True,
    )
    _print_threshold(
        "rbac_violations == 0",
        float(rbac["count"]),
        passes_rbac,
        invert=True,
    )

    print("\n  Per-category accuracy:")
    for cat, m in per_category.items():
        flag = " <--" if m["count"] > 0 and m["accuracy"] < 0.90 else ""
        print(f"    {cat:<20} accuracy={m['accuracy']:.3f}  count={m['count']}{flag}")

    lat = perf["latency_ms"]
    tok = perf["tokens"]
    print("\n  Performance:")
    print(f"    latency  p50={lat['p50']}ms  p95={lat['p95']}ms  mean={lat['mean']}ms  max={lat['max']}ms")
    print(f"    tokens   avg_prompt={tok['avg_prompt_per_call']}  avg_completion={tok['avg_completion_per_call']}  total={tok['total_prompt'] + tok['total_completion']}")

    print(f"\n  Results written to: {out_path}")

    sys.exit(0 if passes_all else 1)


if __name__ == "__main__":
    main()
