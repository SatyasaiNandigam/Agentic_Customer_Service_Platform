"""Tool executor node isolation eval runner.

Uses the REAL MCP server (no mocks). Exercises actual DB queries, Redis cache,
SSE transport, and tool-level auth checks.

Usage:
    python eval/run_tool_executor_eval.py
    python eval/run_tool_executor_eval.py --include-writes
    python eval/run_tool_executor_eval.py --dataset eval/datasets/tool_executor.jsonl
    python eval/run_tool_executor_eval.py --concurrency 3

Exit codes:
    0 — all thresholds pass
    1 — any threshold fails or eval aborted due to errors

Requires MCP server running at MCP_TOOLS_URL (default http://localhost:8001/sse).
Start with: docker compose up  OR  python -m tools_mcp.server

Write tests (category=success_write) are SKIPPED by default because they mutate DB state.
Pass --include-writes to run them. Reset DB afterwards:
    docker compose down -v && docker compose up --build
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
from eval.tool_executor_eval_types import ToolExecutorRecord, ToolExecutorResult
from eval.tool_executor_metrics import (
    LIMIT_ENFORCEMENT_THRESHOLD,
    EXCEPTION_CAPTURE_THRESHOLD,
    TOOL_MESSAGE_RATE_THRESHOLD,
    NO_TOOL_GUARD_THRESHOLD,
    TOOL_CALL_ID_LINKAGE_THRESHOLD,
    COUNTS_INCREMENT_THRESHOLD,
    SUCCESS_READ_RATE_THRESHOLD,
    P95_LATENCY_THRESHOLD_MS,
    build_full_report,
    compute_limit_enforcement_rate,
    compute_exception_capture_rate,
    compute_tool_message_rate,
    compute_no_tool_guard_rate,
    compute_tool_call_id_linkage_rate,
    compute_counts_increment_accuracy,
    compute_success_read_rate,
    compute_performance_stats,
    compute_per_category_metrics,
)

_LIMIT_CATEGORIES: frozenset[str] = frozenset({"limit_destructive", "limit_write", "limit_total"})


def _build_state(record: ToolExecutorRecord) -> tuple[AgentState, str]:
    """Build AgentState for a record and return (state, synthetic_tool_call_id).

    Injects a synthetic AIMessage carrying a tool_call so that
    _extract_tool_call_id can find a matching id. Without this the executor
    falls back to "unknown_tool_call_id", which is still valid but hides the
    real linkage check.
    """
    state = create_initial_state(
        user_id=record.user_id,
        session_id=f"eval-{record.id}",
        user_role=record.user_role,
    )

    synthetic_id = f"eval_call_{record.id}"
    messages: list = [HumanMessage(content="eval test message")]

    if record.selected_tool:
        messages.append(
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "id": synthetic_id,
                        "name": record.selected_tool,
                        "args": record.tool_input or {},
                        "type": "tool_call",
                    }
                ],
            )
        )

    state["messages"] = messages
    state["selected_tool"] = record.selected_tool
    state["tool_input"] = record.tool_input or {}
    state["tool_call_counts"] = dict(record.tool_call_counts)

    return state, synthetic_id


def _result_content_has_error(tool_result: dict | None) -> bool:
    """Check whether the serialised MCP content inside tool_result carries an error payload.

    LangChain's MCP adapter returns content as a list of content objects, which
    _serialise_result wraps as {"results": [...]}. The actual MCP error dict
    (e.g. {"error": "not_found", "error_type": "not_found"}) is embedded inside
    the content text, not at the top level of tool_result. This helper reaches
    inside and parses that content.
    """
    if not tool_result:
        return False
    results = tool_result.get("results")
    if not isinstance(results, list) or not results:
        return False
    for item in results:
        text = getattr(item, "text", None) or str(item)
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict) and "error" in parsed:
                return True
        except (json.JSONDecodeError, TypeError):
            if '"error"' in text:
                return True
    return False


def _is_error_result(tool_result: dict | None, tool_error: str | None) -> bool:
    """Return True if the execution produced any kind of error.

    Checks three layers:
    1. tool_error set (Python exception captured by executor)
    2. top-level "error" key in tool_result (shouldn't occur given MCP adapter wrapping,
       but kept as a safety net)
    3. "error" key inside the serialised MCP content within tool_result["results"]
    """
    if tool_error is not None:
        return True
    if tool_result is not None and "error" in tool_result:
        return True
    if _result_content_has_error(tool_result):
        return True
    return False


def _assess(
    record: ToolExecutorRecord,
    output: dict,
    synthetic_id: str,
    initial_counts: dict,
) -> dict:
    """Evaluate the executor output against the record's expectations.

    Returns a dict of boolean assertion results used to build ToolExecutorResult.
    """
    tool_result: dict | None = output.get("tool_result")
    tool_error: str | None  = output.get("tool_error")
    new_counts: dict        = output.get("tool_call_counts") or {}
    out_messages: list      = output.get("messages") or []

    # ToolMessage presence
    tool_messages = [m for m in out_messages if isinstance(m, ToolMessage)]
    tool_message_appended = len(tool_messages) > 0

    # tool_call_id linkage
    tool_call_id_linked = all(
        m.tool_call_id == synthetic_id for m in tool_messages
    ) if tool_messages else True  # vacuously true when no messages expected

    # Counts increment check
    tool_name = record.selected_tool
    if tool_name:
        was_incremented = new_counts.get(tool_name, 0) > initial_counts.get(tool_name, 0)
    else:
        was_incremented = False
    counts_incremented_correctly = (was_incremented == record.expected_counts_incremented)

    # Limit error check (only relevant for limit categories)
    if record.category in _LIMIT_CATEGORIES:
        if record.expected_success:
            # Negative boundary test: limit must NOT fire — call should be allowed through
            limit_error_correct = (tool_error is None)
        else:
            # Positive limit test: limit must fire with the expected message
            limit_error_correct = (
                tool_error is not None
                and record.expected_error_contains is not None
                and record.expected_error_contains in tool_error
            )
    else:
        limit_error_correct = True  # not a limit record — always passes this check

    # Success check
    if record.expected_success:
        # Must have tool_result with no error key, and all expected keys present
        if tool_result is None or "error" in tool_result or tool_error is not None:
            success_correct = False
        else:
            success_correct = all(k in tool_result for k in record.expected_result_keys)
    else:
        # Expected failure — tool_result should contain "error" key OR tool_error is set
        success_correct = _is_error_result(tool_result, tool_error)

    return {
        "tool_result": tool_result,
        "tool_error": tool_error,
        "output_counts": new_counts,
        "tool_message_appended": tool_message_appended,
        "tool_call_id_linked": tool_call_id_linked,
        "counts_incremented_correctly": counts_incremented_correctly,
        "limit_error_correct": limit_error_correct,
        "success_correct": success_correct,
    }


async def run_single(
    record: ToolExecutorRecord,
    semaphore: asyncio.Semaphore,
    include_writes: bool,
) -> ToolExecutorResult:
    # Skip write records unless --include-writes is set
    if record.requires_flag == "include_writes" and not include_writes:
        return ToolExecutorResult(
            id=record.id,
            category=record.category,
            selected_tool=record.selected_tool,
            user_id=record.user_id,
            user_role=record.user_role,
            tool_result=None,
            tool_error=None,
            output_counts={},
            tool_message_appended=False,
            tool_call_id_linked=True,
            counts_incremented_correctly=True,
            limit_error_correct=True,
            success_correct=True,
            latency_ms=0.0,
            error=None,
            skipped=True,
        )

    state, synthetic_id = _build_state(record)
    initial_counts = dict(record.tool_call_counts)
    error: str | None = None

    async with semaphore:
        t0 = time.perf_counter()
        try:
            output = await tool_executor_node(state)
        except Exception as exc:
            output = {
                "tool_result": None,
                "tool_error": f"UNCAUGHT: {type(exc).__name__}: {exc}",
                "tool_call_counts": initial_counts,
                "messages": [],
            }
            error = str(exc)
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)

    assessed = _assess(record, output, synthetic_id, initial_counts)

    return ToolExecutorResult(
        id=record.id,
        category=record.category,
        selected_tool=record.selected_tool,
        user_id=record.user_id,
        user_role=record.user_role,
        tool_result=assessed["tool_result"],
        tool_error=assessed["tool_error"],
        output_counts=assessed["output_counts"],
        tool_message_appended=assessed["tool_message_appended"],
        tool_call_id_linked=assessed["tool_call_id_linked"],
        counts_incremented_correctly=assessed["counts_incremented_correctly"],
        limit_error_correct=assessed["limit_error_correct"],
        success_correct=assessed["success_correct"],
        latency_ms=latency_ms,
        error=error,
        skipped=False,
    )


async def run_all(
    records: list[ToolExecutorRecord],
    concurrency: int,
    include_writes: bool,
) -> list[ToolExecutorResult]:
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [run_single(r, semaphore, include_writes) for r in records]
    return await asyncio.gather(*tasks)


def load_dataset(path: Path) -> list[ToolExecutorRecord]:
    records: list[ToolExecutorRecord] = []
    required = {
        "id", "category", "user_id", "user_role", "selected_tool", "tool_input",
        "tool_call_counts", "expected_success", "expected_error_contains",
        "expected_tool_message_appended", "expected_counts_incremented",
        "expected_result_keys",
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
            ToolExecutorRecord(
                id=obj["id"],
                category=obj["category"],
                user_id=obj["user_id"],
                user_role=obj["user_role"],
                selected_tool=obj["selected_tool"],
                tool_input=obj["tool_input"] or {},
                tool_call_counts=obj["tool_call_counts"] or {},
                expected_success=obj["expected_success"],
                expected_error_contains=obj.get("expected_error_contains"),
                expected_tool_message_appended=obj["expected_tool_message_appended"],
                expected_counts_incremented=obj["expected_counts_incremented"],
                expected_result_keys=obj.get("expected_result_keys") or [],
                requires_flag=obj.get("requires_flag"),
                notes=obj.get("notes"),
            )
        )
    return records


def write_results(
    results: list[ToolExecutorResult],
    dataset: list[ToolExecutorRecord],
    run_metadata: dict,
) -> Path:
    report = build_full_report(results, dataset, run_metadata)
    out_dir = Path("eval/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_tool_executor.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return out_path


def _print_threshold(label: str, value: float, passes: bool, fmt: str = ".4f") -> None:
    status = "PASS" if passes else "FAIL"
    flag   = "" if passes else "  <--"
    print(f"    {label:<60} {value:{fmt}}  {status}{flag}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run tool_executor node isolation eval against the real MCP server."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("eval/datasets/tool_executor.jsonl"),
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=3,
        help="Concurrent tool calls (default: 3; no LLM rate limit, but MCP/DB connection bound)",
    )
    parser.add_argument(
        "--include-writes",
        action="store_true",
        default=False,
        help=(
            "Run write test records (success_write category). "
            "WARNING: permanently modifies seeded DB state. Reset with: "
            "docker compose down -v && docker compose up --build"
        ),
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

    write_count = sum(1 for r in dataset if r.requires_flag == "include_writes")
    active_count = len(dataset) - (write_count if not args.include_writes else 0)
    print(f"  {len(dataset)} records loaded  ({active_count} will run, {write_count} write records {'INCLUDED' if args.include_writes else 'SKIPPED'}).")

    if args.include_writes:
        print(
            "\n  [WARNING] --include-writes is set. Write tests will mutate DB state.\n"
            "  Reset DB after run: docker compose down -v && docker compose up --build\n"
        )

    # Warm tool registry for each role present in the dataset to confirm MCP is up
    # and to isolate connection overhead from per-record latency measurements.
    roles_in_dataset = {r.user_role for r in dataset}
    print(f"Warming tool registry for roles: {sorted(roles_in_dataset)} ...")
    try:
        async def _warmup() -> None:
            for role in sorted(roles_in_dataset):
                await get_registry_tools(user_id="eval-warmup", user_role=role)

        asyncio.run(_warmup())
        print("  Registry warm.")
    except Exception as exc:
        print(
            f"\n[ERROR] Could not reach MCP server during warmup: {exc}\n"
            "  Ensure the MCP server is running: docker compose up  or  python -m tools_mcp.server",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"\nRunning tool_executor eval (concurrency={args.concurrency}) ...")
    t_start = time.perf_counter()
    results = asyncio.run(
        run_all(dataset, concurrency=args.concurrency, include_writes=args.include_writes)
    )
    duration = round(time.perf_counter() - t_start, 1)

    run_metadata = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_path": str(args.dataset),
        "total_cases": len(results),
        "concurrency": args.concurrency,
        "include_writes": args.include_writes,
        "duration_seconds": duration,
        "note": "Runs against real MCP server — ensure MCP_TOOLS_URL is reachable and DB is seeded.",
    }

    out_path = write_results(results, dataset, run_metadata)

    # --- Compute and display metrics ---
    limit_enf = compute_limit_enforcement_rate(results)
    exc_cap   = compute_exception_capture_rate(results)
    msg_rate  = compute_tool_message_rate(results)
    no_tool   = compute_no_tool_guard_rate(results)
    id_link   = compute_tool_call_id_linkage_rate(results)
    counts    = compute_counts_increment_accuracy(results)
    read_rate = compute_success_read_rate(results)
    perf      = compute_performance_stats(results)
    per_cat   = compute_per_category_metrics(results)

    p95_read = perf["success_read_latency_ms"]["p95"]

    passes_limit   = limit_enf["rate"] >= LIMIT_ENFORCEMENT_THRESHOLD
    passes_exc     = exc_cap["rate"] >= EXCEPTION_CAPTURE_THRESHOLD
    passes_msg     = msg_rate["rate"] >= TOOL_MESSAGE_RATE_THRESHOLD
    passes_no_tool = no_tool["rate"] >= NO_TOOL_GUARD_THRESHOLD
    passes_link    = id_link["rate"] >= TOOL_CALL_ID_LINKAGE_THRESHOLD
    passes_counts  = counts["rate"] >= COUNTS_INCREMENT_THRESHOLD
    passes_read    = read_rate["rate"] >= SUCCESS_READ_RATE_THRESHOLD
    passes_latency = p95_read <= P95_LATENCY_THRESHOLD_MS
    passes_all = all([
        passes_limit, passes_exc, passes_msg, passes_no_tool,
        passes_link, passes_counts, passes_read, passes_latency,
    ])

    skipped_count = sum(1 for r in results if r.skipped)
    uncaught      = exc_cap["uncaught_count"]

    overall_status = "PASS" if passes_all else "FAIL"
    print(
        f"\n  skipped={skipped_count}  uncaught={uncaught}  "
        f"p95_read={p95_read}ms  duration={duration}s  [{overall_status}]"
    )

    print("\n  Threshold checks:")
    _print_threshold(
        f"limit_enforcement_rate >= {LIMIT_ENFORCEMENT_THRESHOLD:.0%}",
        limit_enf["rate"], passes_limit,
    )
    _print_threshold(
        f"exception_capture_rate >= {EXCEPTION_CAPTURE_THRESHOLD:.0%}",
        exc_cap["rate"], passes_exc,
    )
    _print_threshold(
        f"tool_message_rate >= {TOOL_MESSAGE_RATE_THRESHOLD:.0%}",
        msg_rate["rate"], passes_msg,
    )
    _print_threshold(
        f"no_tool_guard_rate >= {NO_TOOL_GUARD_THRESHOLD:.0%}",
        no_tool["rate"], passes_no_tool,
    )
    _print_threshold(
        f"tool_call_id_linkage_rate >= {TOOL_CALL_ID_LINKAGE_THRESHOLD:.0%}",
        id_link["rate"], passes_link,
    )
    _print_threshold(
        f"counts_increment_accuracy >= {COUNTS_INCREMENT_THRESHOLD:.0%}",
        counts["rate"], passes_counts,
    )
    _print_threshold(
        f"success_read_rate >= {SUCCESS_READ_RATE_THRESHOLD:.0%}",
        read_rate["rate"], passes_read,
    )
    _print_threshold(
        f"p95_latency_ms (success_read) <= {P95_LATENCY_THRESHOLD_MS:.0f}ms",
        p95_read, passes_latency, fmt=".1f",
    )

    print("\n  Per-category results:")
    for cat, m in per_cat.items():
        if m["count"] == 0 and m["skipped"] == 0:
            continue
        skp = f"  (skipped={m['skipped']})" if m["skipped"] > 0 else ""
        uncaught_cat = m.get("uncaught_errors", 0)
        err_flag = "  <-- UNCAUGHT ERRORS" if uncaught_cat > 0 else ""
        print(
            f"    {cat:<22} n={m['count']}  "
            f"success_correct={m.get('success_correct', 0)}  "
            f"counts_correct={m.get('counts_correct', 0)}  "
            f"msg_appended={m.get('tool_message_appended', 0)}"
            f"{skp}{err_flag}"
        )

    lat = perf["success_read_latency_ms"]
    print(
        f"\n  Performance (success_read):  "
        f"p50={lat['p50']}ms  p95={lat['p95']}ms  mean={lat['mean']}ms  max={lat['max']}ms"
    )

    # Surface any failures concisely
    failures_to_show = [
        r for r in results
        if not r.skipped and not r.error is None
        or (not r.skipped and not r.success_correct)
        or (not r.skipped and not r.counts_incremented_correctly)
        or (not r.skipped and not r.limit_error_correct)
    ]
    if failures_to_show:
        print(f"\n  Failures ({len(failures_to_show)}):")
        for r in failures_to_show[:20]:
            print(
                f"    [{r.category}] {r.id}  "
                f"tool={r.selected_tool}  "
                f"tool_error={r.tool_error!r:.80}  "
                f"result_keys={list(r.tool_result.keys()) if r.tool_result else None}"
            )
        if len(failures_to_show) > 20:
            print(f"    ... and {len(failures_to_show) - 20} more (see results file)")

    print(f"\n  Results written to: {out_path}")

    sys.exit(0 if passes_all else 1)


if __name__ == "__main__":
    main()
