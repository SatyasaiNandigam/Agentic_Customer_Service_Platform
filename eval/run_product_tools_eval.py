"""Product tools eval runner — tests search_products and get_product_detail MCP tools.

Runs the real tool_executor node against the live MCP server to evaluate:
  - search_products: keyword accuracy, filter precision, status exclusion, pagination
  - get_product_detail: by-ID lookup, by-name lookup, field completeness, error handling

Usage:
    python eval/run_product_tools_eval.py
    python eval/run_product_tools_eval.py --dataset eval/datasets/product_tools.jsonl
    python eval/run_product_tools_eval.py --concurrency 5

Exit codes:
    0 — all thresholds pass
    1 — any threshold fails or eval aborted

Requires MCP server running at MCP_TOOLS_URL.
Start with: docker compose up  OR  python -m tools_mcp.server
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

from app.agent.nodes.tool_executor import tool_executor_node
from app.agent.state import AgentState, create_initial_state
from app.mcp_client.tool_registry import get_registry_tools
from eval.product_tools_eval_types import ProductToolRecord, ProductToolResult
from eval.product_tools_metrics import (
    SEARCH_HIT_RATE_THRESHOLD,
    SEARCH_FILTER_PRECISION_THRESHOLD,
    SEARCH_STATUS_EXCLUSION_THRESHOLD,
    SEARCH_EMPTY_ACCURACY_THRESHOLD,
    DETAIL_FOUND_ACCURACY_THRESHOLD,
    DETAIL_NOT_FOUND_THRESHOLD,
    DETAIL_FIELD_COMPLETENESS_THRESHOLD,
    OVERALL_PASS_RATE_THRESHOLD,
    P95_LATENCY_THRESHOLD_MS,
    build_full_report,
    compute_search_hit_rate,
    compute_search_filter_precision,
    compute_search_status_exclusion,
    compute_search_empty_accuracy,
    compute_detail_found_accuracy,
    compute_detail_not_found_handling,
    compute_detail_field_completeness,
    compute_overall_pass_rate,
    compute_performance_stats,
    compute_per_category_metrics,
)


def _build_state(record: ProductToolRecord) -> tuple[AgentState, str]:
    state = create_initial_state(
        user_id=record.user_id,
        session_id=f"eval-{record.id}",
        user_role=record.user_role,
    )
    synthetic_id = f"eval_call_{record.id}"
    state["messages"] = [
        HumanMessage(content="eval test message"),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": synthetic_id,
                    "name": record.tool,
                    "args": record.tool_input,
                    "type": "tool_call",
                }
            ],
        ),
    ]
    state["selected_tool"] = record.tool
    state["tool_input"] = record.tool_input
    state["tool_call_counts"] = {}
    return state, synthetic_id


def _extract_content_json(tool_result: dict | None) -> dict | None:
    """Parse the JSON payload from inside the MCP-adapter-wrapped tool_result.

    Handles three forms that appear depending on how the adapter version wraps results:
      1. tool_result IS the product dict directly (bypassed adapter path)
      2. {"results": [{"type": "text", "text": JSON_STRING}]} — langchain-mcp-adapters dict items
      3. {"results": [TextContent(text=JSON_STRING)]} — mcp.types.TextContent objects
    """
    if not tool_result:
        return None

    # Case 1: tool_result is the product/error data directly
    if "products" in tool_result or "product_id" in tool_result or "error_type" in tool_result:
        return tool_result

    # Case 2 & 3: wrapped in {"results": [...]}
    results = tool_result.get("results")
    if not isinstance(results, list) or not results:
        return None

    first = results[0]
    text: str | None = None
    if isinstance(first, str):
        text = first
    elif isinstance(first, dict):
        text = first.get("text")           # langchain-mcp-adapters content block dict
    else:
        text = getattr(first, "text", None)  # mcp.types.TextContent object

    if not text:
        return None

    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except (json.JSONDecodeError, TypeError):
        return None


def _assess(record: ProductToolRecord, output: dict) -> dict:
    tool_result: dict | None = output.get("tool_result")
    tool_error: str | None = output.get("tool_error")

    content = _extract_content_json(tool_result)

    # Determine if this is an error response
    is_error_response = (
        tool_error is not None
        or (content is not None and "error" in content)
        or (tool_result is not None and "error" in tool_result)
    )

    success_correct = (record.expected_success != is_error_response)

    # --- Parse product IDs and count from content ---
    actual_product_ids: list[int] = []
    actual_count: int | None = None
    actual_error_type: str | None = None

    if content is not None:
        if "error_type" in content:
            actual_error_type = content["error_type"]
        elif "error" in content:
            # error without error_type field
            actual_error_type = "unknown"

        if record.tool == "search_products" and "products" in content:
            products = content["products"]
            if isinstance(products, list):
                actual_product_ids = [
                    p["product_id"] for p in products
                    if isinstance(p, dict) and "product_id" in p
                ]
                actual_count = len(products)

        elif record.tool == "get_product_detail" and "product_id" in content:
            actual_product_ids = [content["product_id"]]
            actual_count = 1

    # --- Assertions ---
    # contains: all expected IDs must appear
    missing_ids = [pid for pid in record.expected_product_ids_contains if pid not in actual_product_ids]
    contains_check_passed = len(missing_ids) == 0

    # excluded: none of the excluded IDs must appear
    unexpected_ids = [pid for pid in record.expected_product_ids_excluded if pid in actual_product_ids]
    excluded_check_passed = len(unexpected_ids) == 0

    # count bounds
    count_check_passed = True
    if record.expected_count_min is not None and actual_count is not None:
        if actual_count < record.expected_count_min:
            count_check_passed = False
    if record.expected_count_max is not None and actual_count is not None:
        if actual_count > record.expected_count_max:
            count_check_passed = False
    # For keyword_miss cases: count must be 0
    if record.expected_count_max == 0 and (actual_count or 0) != 0:
        count_check_passed = False

    # error type
    error_type_correct = (actual_error_type == record.expected_error_type)

    # field completeness — check top-level keys in content
    missing_fields: list[str] = []
    if record.expected_fields_present and content:
        missing_fields = [f for f in record.expected_fields_present if f not in content]
    fields_complete = len(missing_fields) == 0

    return {
        "actual_product_ids": actual_product_ids,
        "actual_count": actual_count,
        "actual_error_type": actual_error_type,
        "success_correct": success_correct,
        "contains_check_passed": contains_check_passed,
        "excluded_check_passed": excluded_check_passed,
        "count_check_passed": count_check_passed,
        "error_type_correct": error_type_correct,
        "fields_complete": fields_complete,
        "missing_ids": missing_ids,
        "unexpected_ids": unexpected_ids,
        "missing_fields": missing_fields,
    }


async def run_single(
    record: ProductToolRecord,
    semaphore: asyncio.Semaphore,
) -> ProductToolResult:
    state, _ = _build_state(record)
    error: str | None = None

    async with semaphore:
        t0 = time.perf_counter()
        try:
            output = await tool_executor_node(state)
        except Exception as exc:
            output = {"tool_result": None, "tool_error": f"UNCAUGHT: {exc}", "messages": []}
            error = str(exc)
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)

    assessed = _assess(record, output)

    return ProductToolResult(
        id=record.id,
        tool=record.tool,
        category=record.category,
        actual_product_ids=assessed["actual_product_ids"],
        actual_count=assessed["actual_count"],
        actual_error_type=assessed["actual_error_type"],
        success_correct=assessed["success_correct"],
        contains_check_passed=assessed["contains_check_passed"],
        excluded_check_passed=assessed["excluded_check_passed"],
        count_check_passed=assessed["count_check_passed"],
        error_type_correct=assessed["error_type_correct"],
        fields_complete=assessed["fields_complete"],
        missing_ids=assessed["missing_ids"],
        unexpected_ids=assessed["unexpected_ids"],
        missing_fields=assessed["missing_fields"],
        latency_ms=latency_ms,
        error=error,
    )


async def run_all(
    records: list[ProductToolRecord],
    concurrency: int,
) -> list[ProductToolResult]:
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [run_single(r, semaphore) for r in records]
    return await asyncio.gather(*tasks)


def load_dataset(path: Path) -> list[ProductToolRecord]:
    records: list[ProductToolRecord] = []
    required = {
        "id", "tool", "category", "user_id", "user_role", "tool_input",
        "expected_success", "expected_product_ids_contains", "expected_product_ids_excluded",
        "expected_count_min", "expected_count_max", "expected_error_type",
        "expected_fields_present",
    }
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
            ProductToolRecord(
                id=obj["id"],
                tool=obj["tool"],
                category=obj["category"],
                user_id=obj["user_id"],
                user_role=obj["user_role"],
                tool_input=obj["tool_input"] or {},
                expected_success=obj["expected_success"],
                expected_product_ids_contains=obj["expected_product_ids_contains"] or [],
                expected_product_ids_excluded=obj["expected_product_ids_excluded"] or [],
                expected_count_min=obj["expected_count_min"],
                expected_count_max=obj["expected_count_max"],
                expected_error_type=obj["expected_error_type"],
                expected_fields_present=obj.get("expected_fields_present") or [],
                notes=obj.get("notes", ""),
            )
        )
    return records


def _print_threshold(label: str, value: float, passes: bool, fmt: str = ".4f") -> None:
    status = "PASS" if passes else "FAIL"
    flag = "" if passes else "  <--"
    print(f"    {label:<60} {value:{fmt}}  {status}{flag}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run product tools eval against the live MCP server."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("eval/datasets/product_tools.jsonl"),
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=5,
        help="Concurrent tool calls (default: 5)",
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

    search_count = sum(1 for r in dataset if r.tool == "search_products")
    detail_count = sum(1 for r in dataset if r.tool == "get_product_detail")
    print(f"  {len(dataset)} records loaded  ({search_count} search_products, {detail_count} get_product_detail)")

    print("Warming tool registry (confirms MCP server is reachable) ...")
    try:
        asyncio.run(get_registry_tools(user_id="eval-warmup", user_role="customer"))
        print("  Registry warm.")
    except Exception as exc:
        print(
            f"\n[ERROR] Could not reach MCP server: {exc}\n"
            "  Ensure MCP server is running: docker compose up  or  python -m tools_mcp.server",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"\nRunning product tools eval (concurrency={args.concurrency}) ...")
    t_start = time.perf_counter()
    results = asyncio.run(run_all(dataset, concurrency=args.concurrency))
    duration = round(time.perf_counter() - t_start, 1)

    run_metadata = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_path": str(args.dataset),
        "total_cases": len(results),
        "concurrency": args.concurrency,
        "duration_seconds": duration,
        "search_cases": search_count,
        "detail_cases": detail_count,
        "note": "Runs against real MCP server — ensure MCP_TOOLS_URL is reachable and DB is seeded.",
    }

    report = build_full_report(results, dataset, run_metadata)
    out_dir = Path("eval/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_product_tools.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Compute metrics for console display
    search_hit   = compute_search_hit_rate(results)
    search_prec  = compute_search_filter_precision(results)
    status_excl  = compute_search_status_exclusion(results)
    empty_acc    = compute_search_empty_accuracy(results)
    detail_found = compute_detail_found_accuracy(results)
    not_found    = compute_detail_not_found_handling(results)
    field_comp   = compute_detail_field_completeness(results)
    overall      = compute_overall_pass_rate(results)
    perf         = compute_performance_stats(results)
    per_cat      = compute_per_category_metrics(results)

    p95 = perf["all_latency_ms"]["p95"]
    errors = sum(1 for r in results if r.error is not None)
    passes_all = report["summary"]["passes_all_thresholds"]

    print(
        f"\n  total={len(results)}  errors={errors}  "
        f"p95={p95}ms  duration={duration}s  "
        f"[{'PASS' if passes_all else 'FAIL'}]"
    )

    print("\n  Threshold checks:")
    _print_threshold(f"search_hit_rate >= {SEARCH_HIT_RATE_THRESHOLD:.0%}", search_hit["rate"], search_hit["rate"] >= SEARCH_HIT_RATE_THRESHOLD)
    _print_threshold(f"search_filter_precision >= {SEARCH_FILTER_PRECISION_THRESHOLD:.0%}", search_prec["rate"], search_prec["rate"] >= SEARCH_FILTER_PRECISION_THRESHOLD)
    _print_threshold(f"search_status_exclusion_rate == {SEARCH_STATUS_EXCLUSION_THRESHOLD:.0%}", status_excl["rate"], status_excl["rate"] >= SEARCH_STATUS_EXCLUSION_THRESHOLD)
    _print_threshold(f"search_empty_accuracy >= {SEARCH_EMPTY_ACCURACY_THRESHOLD:.0%}", empty_acc["rate"], empty_acc["rate"] >= SEARCH_EMPTY_ACCURACY_THRESHOLD)
    _print_threshold(f"detail_found_accuracy >= {DETAIL_FOUND_ACCURACY_THRESHOLD:.0%}", detail_found["rate"], detail_found["rate"] >= DETAIL_FOUND_ACCURACY_THRESHOLD)
    _print_threshold(f"detail_not_found_handling >= {DETAIL_NOT_FOUND_THRESHOLD:.0%}", not_found["rate"], not_found["rate"] >= DETAIL_NOT_FOUND_THRESHOLD)
    _print_threshold(f"detail_field_completeness >= {DETAIL_FIELD_COMPLETENESS_THRESHOLD:.0%}", field_comp["rate"], field_comp["rate"] >= DETAIL_FIELD_COMPLETENESS_THRESHOLD)
    _print_threshold(f"overall_pass_rate >= {OVERALL_PASS_RATE_THRESHOLD:.0%}", overall["rate"], overall["rate"] >= OVERALL_PASS_RATE_THRESHOLD)
    _print_threshold(f"p95_latency_ms <= {P95_LATENCY_THRESHOLD_MS:.0f}ms", p95, p95 <= P95_LATENCY_THRESHOLD_MS, fmt=".1f")

    print("\n  Per-category results:")
    for cat, m in per_cat.items():
        if m.get("count", 0) == 0:
            continue
        n = m["count"]
        overall_n = m.get("success_correct", 0) + m.get("contains_passed", 0)
        print(
            f"    {cat:<28} n={n}  "
            f"success={m.get('success_correct', 0)}/{n}  "
            f"contains={m.get('contains_passed', 0)}/{n}  "
            f"excluded={m.get('excluded_passed', 0)}/{n}  "
            f"err_type={m.get('error_type_correct', 0)}/{n}  "
            f"avg={m.get('avg_latency_ms', 0)}ms"
        )

    lat = perf["all_latency_ms"]
    slat = perf["search_latency_ms"]
    dlat = perf["detail_latency_ms"]
    print(
        f"\n  Performance:  all p95={lat['p95']}ms  "
        f"search p95={slat['p95']}ms  detail p95={dlat['p95']}ms"
    )

    failures = overall.get("failures", [])
    if failures:
        print(f"\n  Failures ({len(failures)}):")
        for f in failures[:20]:
            flags = []
            if not f["success_correct"]:
                flags.append(f"wrong_success(err_type={f['actual_error_type']})")
            if not f["contains_check_passed"]:
                flags.append(f"missing_ids={f['missing_ids']}")
            if not f["excluded_check_passed"]:
                flags.append(f"unexpected_ids={f['unexpected_ids']}")
            if not f["count_check_passed"]:
                flags.append("count_out_of_range")
            if not f["fields_complete"]:
                flags.append(f"missing_fields={f['missing_fields']}")
            print(f"    [{f['category']}] {f['id']}  {' | '.join(flags)}")
        if len(failures) > 20:
            print(f"    ... and {len(failures) - 20} more (see results file)")

    print(f"\n  Results written to: {out_path}")
    sys.exit(0 if passes_all else 1)


if __name__ == "__main__":
    main()
