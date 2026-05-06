"""Eval results dashboard — Intent Classifier and Customer Delegator nodes.

Usage:
    streamlit run eval/dashboard.py

Requires:
    pip install streamlit plotly pandas
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

# ── constants ─────────────────────────────────────────────────────────────────

DOMAIN_CLASSES = ["need_information", "need_assistance", "need_advice", "escalate", "block"]

PASS_COLOR = "#2ecc71"
FAIL_COLOR = "#e74c3c"

EVAL_TYPES = {
    "Intent Classifier":  "intent_classification",
    "Customer Delegator": "customer_delegator",
    "Tool Planner":       "tool_planner",
}


# ── helpers ───────────────────────────────────────────────────────────────────

def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _color(passes: bool) -> str:
    return PASS_COLOR if passes else FAIL_COLOR


def _discover_results(eval_suffix: str) -> list[Path]:
    results_dir = Path("eval/results")
    return sorted(results_dir.glob(f"*_{eval_suffix}.json"), reverse=True)


# ── shared charts ─────────────────────────────────────────────────────────────

def chart_history_accuracy(data: dict) -> go.Figure:
    hist = data["history_accuracy"]
    labels = ["With history", "Without history"]
    values = [hist["with_history"]["accuracy"], hist["without_history"]["accuracy"]]
    counts = [hist["with_history"]["count"], hist["without_history"]["count"]]
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=[PASS_COLOR if v >= 0.85 else FAIL_COLOR for v in values],
        text=[f"{v:.1%} (n={c})" for v, c in zip(values, counts)],
        textposition="outside",
    ))
    fig.update_layout(
        title="Accuracy: History vs. No History",
        yaxis=dict(range=[0, 1.15]),
        height=300, margin=dict(t=50, b=20),
    )
    return fig


def chart_performance(data: dict) -> go.Figure:
    lat = data["performance"]["latency_ms"]
    tok = data["performance"]["tokens"]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Latency (ms)",
        x=["p50", "p95", "mean", "max"],
        y=[lat["p50"], lat["p95"], lat["mean"], lat["max"]],
        marker_color="#3498db",
        text=[f"{v:.0f}ms" for v in [lat["p50"], lat["p95"], lat["mean"], lat["max"]]],
        textposition="outside",
        xaxis="x1", yaxis="y1",
    ))
    fig.add_trace(go.Bar(
        name="Tokens / call",
        x=["Avg Prompt", "Avg Completion"],
        y=[tok["avg_prompt_per_call"], tok["avg_completion_per_call"]],
        marker_color="#9b59b6",
        text=[f"{v:.0f}" for v in [tok["avg_prompt_per_call"], tok["avg_completion_per_call"]]],
        textposition="outside",
        xaxis="x2", yaxis="y2",
    ))
    fig.update_layout(
        title="Performance: Latency & Token Usage",
        grid=dict(rows=1, columns=2),
        xaxis=dict(domain=[0.0, 0.45]),
        xaxis2=dict(domain=[0.55, 1.0]),
        yaxis=dict(title="ms"),
        yaxis2=dict(title="tokens", anchor="x2"),
        height=300, margin=dict(t=50, b=20),
        showlegend=False,
    )
    return fig


def chart_boundary_pair_accuracy(data: dict) -> go.Figure:
    bpa = data.get("boundary_pair_accuracy", {})
    if not bpa:
        return go.Figure().update_layout(title="No boundary pair data", height=200)
    pairs = list(bpa.keys())
    accuracies = [bpa[p]["accuracy"] for p in pairs]
    counts = [bpa[p]["count"] for p in pairs]
    errors = [bpa[p]["errors"] for p in pairs]
    fig = go.Figure(go.Bar(
        x=accuracies, y=pairs, orientation="h",
        marker_color=[_color(a >= 0.80) for a in accuracies],
        text=[f"{a:.0%}  ({e} err / {c})" for a, e, c in zip(accuracies, errors, counts)],
        textposition="outside",
    ))
    fig.add_vline(x=0.80, line_dash="dot", line_color="red",
                  annotation_text="80% target", annotation_position="top")
    fig.update_layout(
        title="Boundary Pair Accuracy",
        xaxis=dict(range=[0, 1.25]),
        height=max(260, len(pairs) * 48 + 80),
        margin=dict(l=240, r=80, t=40, b=20),
    )
    return fig


def _status_banner(passes: bool, accuracy: float, macro_f1: float, threshold: float) -> None:
    label = "✅ ALL THRESHOLDS PASS" if passes else "❌ THRESHOLDS FAILING"
    st.markdown(
        f"<div style='padding:12px 20px;background:{_color(passes)};color:white;"
        f"border-radius:6px;font-size:1.1rem;font-weight:600;'>"
        f"{label} &nbsp;|&nbsp; Accuracy: {accuracy:.1%} &nbsp;|&nbsp; "
        f"Macro F1: {macro_f1:.4f} (target ≥ {threshold})"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown("")


# ── delegator charts ──────────────────────────────────────────────────────────

def chart_delegator_thresholds(data: dict) -> go.Figure:
    display = {
        "macro_f1":           "Macro F1",
        "escalate_precision": "Escalate Precision",
        "block_precision":    "Block Precision",
        "escalate_recall":    "Escalate Recall",
        "block_recall":       "Block Recall",
        "false_block_rate":   "False Block Rate",
    }
    labels, values, targets, colors = [], [], [], []
    for key, label in display.items():
        t = data["thresholds"][key]
        labels.append(label)
        values.append(t["value"])
        targets.append(t["threshold"])
        colors.append(_color(t["pass"]))
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=values, y=labels, orientation="h", marker_color=colors, name="Value",
        text=[f"{v:.4f}" for v in values], textposition="outside",
    ))
    fig.add_trace(go.Scatter(
        x=targets, y=labels, mode="markers",
        marker=dict(symbol="line-ns", size=18, color="black", line=dict(width=3)),
        name="Threshold",
    ))
    fig.update_layout(
        title="Threshold Checks", xaxis=dict(range=[0, 1.05]),
        height=320, margin=dict(l=180, r=60, t=40, b=20),
        legend=dict(orientation="h", y=-0.15),
    )
    return fig


def chart_per_domain_metrics(data: dict) -> go.Figure:
    per = data["per_domain"]
    colors_map = {"precision": "#3498db", "recall": "#2ecc71", "f1": "#e67e22"}
    fig = go.Figure()
    for metric, color in colors_map.items():
        fig.add_trace(go.Bar(
            name=metric.capitalize(), x=DOMAIN_CLASSES,
            y=[per[d][metric] for d in DOMAIN_CLASSES], marker_color=color,
            text=[f"{per[d][metric]:.3f}" for d in DOMAIN_CLASSES], textposition="outside",
        ))
    fig.add_hline(y=0.92, line_dash="dot", line_color="red",
                  annotation_text="F1 threshold 0.92", annotation_position="top right")
    fig.update_layout(
        title="Per-Domain Precision / Recall / F1",
        barmode="group", yaxis=dict(range=[0, 1.15]),
        height=380, margin=dict(t=50, b=40),
        legend=dict(orientation="h", y=-0.2),
    )
    return fig


def chart_delegator_confusion(data: dict) -> go.Figure:
    per = data["per_domain"]
    failures = data["failures"]
    matrix: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for d in DOMAIN_CLASSES:
        matrix[d][d] = per[d]["tp"]
    for f in failures:
        if f["expected_domain"] != f["predicted_domain"]:
            matrix[f["expected_domain"]][f["predicted_domain"]] += 1
    z = [[matrix[exp][pred] for pred in DOMAIN_CLASSES] for exp in DOMAIN_CLASSES]
    totals = [sum(row) for row in z]
    z_pct = [
        [round(z[i][j] / totals[i], 3) if totals[i] > 0 else 0 for j in range(len(DOMAIN_CLASSES))]
        for i in range(len(DOMAIN_CLASSES))
    ]
    text = [
        [f"{z[i][j]}<br>({z_pct[i][j]:.0%})" for j in range(len(DOMAIN_CLASSES))]
        for i in range(len(DOMAIN_CLASSES))
    ]
    fig = go.Figure(go.Heatmap(
        z=z_pct, x=DOMAIN_CLASSES, y=DOMAIN_CLASSES,
        text=text, texttemplate="%{text}",
        colorscale="Blues", showscale=True, xgap=2, ygap=2,
    ))
    fig.update_layout(
        title="Confusion Matrix (row = expected, col = predicted)",
        xaxis_title="Predicted", yaxis_title="Expected",
        height=400, margin=dict(t=50, b=60, l=140, r=20),
        yaxis=dict(autorange="reversed"),
    )
    return fig


def delegator_failures_table(data: dict) -> None:
    import pandas as pd
    rows = [
        {
            "ID": f["id"],
            "Text": f["text"],
            "Expected": f["expected_domain"],
            "Predicted": f["predicted_domain"],
            "Boundary Pair": f.get("boundary_pair") or "—",
            "History": "✓" if f["had_history"] else "",
            "Error": f.get("error") or "",
        }
        for f in data["failures"]
    ]
    st.dataframe(
        pd.DataFrame(rows), use_container_width=True,
        column_config={
            "Text": st.column_config.TextColumn(width="large"),
            "Expected": st.column_config.TextColumn(width="medium"),
            "Predicted": st.column_config.TextColumn(width="medium"),
        },
        hide_index=True,
    )


# ── classifier charts ─────────────────────────────────────────────────────────

def chart_classifier_thresholds(data: dict) -> go.Figure:
    display = {
        "macro_f1":               "Macro F1",
        "need_information_f1":    "Need Info F1",
        "need_assistance_f1":     "Need Assistance F1",
        "need_advice_f1":         "Need Advice F1",
        "false_rejection_rate":   "False Rejection Rate",
        "requires_tool_accuracy": "Requires Tool Accuracy",
    }
    labels, values, targets, colors = [], [], [], []
    for key, label in display.items():
        t = data["thresholds"][key]
        labels.append(label)
        values.append(t["value"])
        targets.append(t["threshold"])
        colors.append(_color(t["pass"]))
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=values, y=labels, orientation="h", marker_color=colors, name="Value",
        text=[f"{v:.4f}" for v in values], textposition="outside",
    ))
    fig.add_trace(go.Scatter(
        x=targets, y=labels, mode="markers",
        marker=dict(symbol="line-ns", size=18, color="black", line=dict(width=3)),
        name="Threshold",
    ))
    fig.update_layout(
        title="Threshold Checks", xaxis=dict(range=[0, 1.05]),
        height=360, margin=dict(l=210, r=60, t=40, b=20),
        legend=dict(orientation="h", y=-0.15),
    )
    return fig


def chart_per_intent_metrics(data: dict) -> go.Figure:
    per = data["per_intent"]
    intents = list(per.keys())
    colors_map = {"precision": "#3498db", "recall": "#2ecc71", "f1": "#e67e22"}
    fig = go.Figure()
    for metric, color in colors_map.items():
        fig.add_trace(go.Bar(
            name=metric.capitalize(), x=intents,
            y=[per[i][metric] for i in intents], marker_color=color,
            text=[f"{per[i][metric]:.3f}" for i in intents], textposition="outside",
        ))
    fig.add_hline(y=0.90, line_dash="dot", line_color="red",
                  annotation_text="Macro F1 target 0.90", annotation_position="top right")
    fig.update_layout(
        title="Per-Intent Precision / Recall / F1",
        barmode="group", yaxis=dict(range=[0, 1.2]),
        height=420, margin=dict(t=50, b=90),
        xaxis=dict(tickangle=-35),
        legend=dict(orientation="h", y=-0.35),
    )
    return fig


def chart_domain_breakdown(data: dict) -> go.Figure:
    bd = data["domain_breakdown"]
    domains = list(bd.keys())
    f1_vals = [bd[d]["macro_f1"] for d in domains]
    acc_vals = [bd[d]["accuracy"] for d in domains]
    counts = [bd[d]["count"] for d in domains]
    thresholds = [bd[d]["threshold"] for d in domains]
    passes = [bd[d]["passes_threshold"] for d in domains]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Macro F1", x=domains, y=f1_vals,
        marker_color=[_color(p) for p in passes],
        text=[f"F1:{v:.3f} (n={c})" for v, c in zip(f1_vals, counts)],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="Accuracy", x=domains, y=acc_vals,
        marker_color=["#3498db"] * len(domains),
        text=[f"Acc:{v:.3f}" for v in acc_vals],
        textposition="outside",
        opacity=0.6,
    ))
    fig.add_trace(go.Scatter(
        x=domains, y=thresholds, mode="markers", name="F1 Threshold",
        marker=dict(symbol="line-ew", size=24, color="black", line=dict(width=3)),
    ))
    fig.update_layout(
        title="Domain Breakdown: F1 & Accuracy vs Threshold",
        barmode="group", yaxis=dict(range=[0, 1.15]),
        height=360, margin=dict(t=50, b=40),
        legend=dict(orientation="h", y=-0.2),
    )
    return fig


def chart_classifier_confusion(data: dict) -> go.Figure:
    per = data["per_intent"]
    failures = data["failures"]
    intents = list(per.keys())

    matrix: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for intent in intents:
        matrix[intent][intent] = per[intent]["tp"]
    for f in failures:
        exp, pred = f["expected_intent"], f["predicted_intent"]
        if exp != pred:
            matrix[exp][pred] += 1

    z = [[matrix[exp][pred] for pred in intents] for exp in intents]
    totals = [sum(row) for row in z]
    z_pct = [
        [round(z[i][j] / totals[i], 3) if totals[i] > 0 else 0 for j in range(len(intents))]
        for i in range(len(intents))
    ]
    text = [
        [f"{z[i][j]}<br>({z_pct[i][j]:.0%})" for j in range(len(intents))]
        for i in range(len(intents))
    ]

    fig = go.Figure(go.Heatmap(
        z=z_pct, x=intents, y=intents,
        text=text, texttemplate="%{text}",
        colorscale="Blues", showscale=True, xgap=1, ygap=1,
    ))
    fig.update_layout(
        title="Confusion Matrix (row = expected, col = predicted)",
        xaxis_title="Predicted", yaxis_title="Expected",
        height=540, margin=dict(t=50, b=130, l=170, r=20),
        xaxis=dict(tickangle=-40),
        yaxis=dict(autorange="reversed"),
    )
    return fig


def chart_false_rejection(data: dict) -> go.Figure:
    fr = data["false_rejection"]
    val = fr["false_rejection_rate"]
    threshold = fr["threshold"]
    passes = fr["passes_threshold"]
    count = fr["false_rejection_count"]
    total = fr["total_eligible"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=val * 100,
        title={"text": f"False Rejection Rate<br><sub>{count} rejections / {total} eligible</sub>"},
        delta={
            "reference": threshold * 100,
            "increasing": {"color": FAIL_COLOR},
            "decreasing": {"color": PASS_COLOR},
        },
        gauge={
            "axis": {"range": [0, 20]},
            "bar": {"color": _color(passes)},
            "threshold": {
                "line": {"color": "red", "width": 3},
                "thickness": 0.75,
                "value": threshold * 100,
            },
            "steps": [
                {"range": [0, threshold * 100], "color": "#d5f5e3"},
                {"range": [threshold * 100, 20], "color": "#fadbd8"},
            ],
        },
        number={"suffix": "%", "valueformat": ".2f"},
    ))
    fig.update_layout(height=300, margin=dict(t=80, b=20, l=30, r=30))
    return fig


def chart_confidence_calibration(data: dict) -> go.Figure:
    bins = [b for b in data["confidence_calibration"] if b["count"] > 0]
    if not bins:
        fig = go.Figure()
        fig.update_layout(title="Confidence Calibration (no data)", height=300)
        return fig

    labels = [f"{b['bin_lower']:.1f}–{b['bin_upper']:.1f}\n(n={b['count']})" for b in bins]
    mean_conf = [b["mean_confidence"] for b in bins]
    accuracy = [b["accuracy"] for b in bins]
    gaps = [b["calibration_gap"] for b in bins]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Accuracy", x=labels, y=accuracy,
        marker_color="#3498db",
        text=[f"{v:.1%}" for v in accuracy], textposition="outside",
    ))
    fig.add_trace(go.Scatter(
        name="Mean Confidence", x=labels, y=mean_conf,
        mode="lines+markers", marker=dict(size=9),
        line=dict(color="#e74c3c", dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        name="Calibration Gap", x=labels, y=gaps,
        mode="lines+markers", marker=dict(size=7, symbol="diamond"),
        line=dict(color="#f39c12", dash="dash"),
    ))
    fig.update_layout(
        title="Confidence Calibration (accuracy vs. mean confidence per bin)",
        yaxis=dict(range=[0, 1.15]),
        height=320, margin=dict(t=50, b=60),
        legend=dict(orientation="h", y=-0.25),
    )
    return fig


def classifier_failures_table(data: dict) -> None:
    import pandas as pd
    rows = [
        {
            "ID": f["id"],
            "Text": f["text"],
            "Expected": f["expected_intent"],
            "Predicted": f["predicted_intent"],
            "Confidence": f"{f['confidence']:.2f}",
            "Domain": f.get("customer_domain", ""),
            "Boundary Pair": f.get("boundary_pair") or "—",
            "History": "✓" if f["had_history"] else "",
            "Error": f.get("error") or "",
        }
        for f in data["failures"]
    ]
    st.dataframe(
        pd.DataFrame(rows), use_container_width=True,
        column_config={
            "Text": st.column_config.TextColumn(width="large"),
            "Expected": st.column_config.TextColumn(width="medium"),
            "Predicted": st.column_config.TextColumn(width="medium"),
            "Confidence": st.column_config.TextColumn(width="small"),
        },
        hide_index=True,
    )


# ── tool planner charts ───────────────────────────────────────────────────────

PLANNER_CATEGORIES = ["intent_mapping", "no_tool", "retry", "implicit", "rbac"]
PLANNER_CATEGORY_LABELS = {
    "intent_mapping": "Intent Mapping",
    "no_tool":        "No Tool",
    "retry":          "Retry",
    "implicit":       "Implicit Args",
    "rbac":           "RBAC Boundary",
}


def chart_planner_thresholds(data: dict) -> go.Figure:
    display = {
        "tool_selection_accuracy": ("Tool Selection Accuracy", False),
        "args_coverage_rate":      ("Args Coverage Rate",     False),
        "p95_latency_ms":          ("p95 Latency (ms)",       True),
        "rbac_violations":         ("RBAC Violations",        True),
    }
    labels, values, colors = [], [], []
    for key, (label, _) in display.items():
        t = data["thresholds"][key]
        labels.append(label)
        values.append(t["value"])
        colors.append(_color(t["pass"]))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=values, y=labels, orientation="h", marker_color=colors,
        text=[f"{v:.4f}" if isinstance(v, float) else str(v) for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        title="Threshold Checks",
        xaxis=dict(range=[0, max(max(values) * 1.25, 1.1)]),
        height=280, margin=dict(l=200, r=80, t=40, b=20),
    )
    return fig


def chart_planner_category_accuracy(data: dict) -> go.Figure:
    per = data["per_category"]
    labels = [PLANNER_CATEGORY_LABELS.get(c, c) for c in PLANNER_CATEGORIES]
    accuracies = [per.get(c, {}).get("accuracy", 0.0) for c in PLANNER_CATEGORIES]
    counts = [per.get(c, {}).get("count", 0) for c in PLANNER_CATEGORIES]

    fig = go.Figure(go.Bar(
        x=labels, y=accuracies,
        marker_color=[_color(a >= 0.90) for a in accuracies],
        text=[f"{a:.1%} (n={c})" for a, c in zip(accuracies, counts)],
        textposition="outside",
    ))
    fig.add_hline(y=0.90, line_dash="dot", line_color="red",
                  annotation_text="90% target", annotation_position="top right")
    fig.update_layout(
        title="Accuracy by Category",
        yaxis=dict(range=[0, 1.2]),
        height=300, margin=dict(t=50, b=20),
    )
    return fig


def chart_planner_args_coverage(data: dict) -> go.Figure:
    per = data["per_category"]
    cats = [c for c in PLANNER_CATEGORIES if per.get(c, {}).get("count", 0) > 0]
    labels = [PLANNER_CATEGORY_LABELS.get(c, c) for c in cats]
    tools_correct = [per[c].get("correct", 0) for c in cats]
    counts = [per[c]["count"] for c in cats]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Correct", x=labels, y=tools_correct, marker_color=PASS_COLOR,
        text=[f"{v}" for v in tools_correct], textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="Incorrect", x=labels,
        y=[c - t for c, t in zip(counts, tools_correct)],
        marker_color=FAIL_COLOR,
        text=[f"{c - t}" for c, t in zip(counts, tools_correct)],
        textposition="outside",
    ))
    fig.update_layout(
        title="Correct vs. Incorrect Tool Selection by Category",
        barmode="stack", height=300, margin=dict(t=50, b=20),
        legend=dict(orientation="h", y=-0.2),
    )
    return fig


def planner_failures_table(data: dict) -> None:
    import pandas as pd
    rows = [
        {
            "ID": f["id"],
            "Category": f["category"],
            "Intent": f["intent"],
            "Expected Tool": f["expected_tool"] or "null",
            "Predicted Tool": f["predicted_tool"] or "null",
            "Args Covered": f"{f['args_covered']:.0%}",
            "Tool Input": json.dumps(f["tool_input"]) if f["tool_input"] else "—",
            "Error": f.get("error") or "",
            "Notes": f.get("notes") or "",
        }
        for f in data["failures"]
    ]
    st.dataframe(
        pd.DataFrame(rows), use_container_width=True,
        column_config={
            "Expected Tool": st.column_config.TextColumn(width="medium"),
            "Predicted Tool": st.column_config.TextColumn(width="medium"),
            "Tool Input": st.column_config.TextColumn(width="large"),
        },
        hide_index=True,
    )


def _planner_status_banner(data: dict) -> None:
    summary = data["summary"]
    passes = summary["passes_all_thresholds"]
    label = "✅ ALL THRESHOLDS PASS" if passes else "❌ THRESHOLDS FAILING"
    tool_acc = summary["tool_selection_accuracy"]
    args_cov = summary["args_coverage_rate"]
    p95 = summary["p95_latency_ms"]
    st.markdown(
        f"<div style='padding:12px 20px;background:{_color(passes)};color:white;"
        f"border-radius:6px;font-size:1.1rem;font-weight:600;'>"
        f"{label} &nbsp;|&nbsp; Tool Accuracy: {tool_acc:.1%} &nbsp;|&nbsp; "
        f"Args Coverage: {args_cov:.1%} &nbsp;|&nbsp; p95: {p95:.0f}ms"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown("")


# ── page renderers ────────────────────────────────────────────────────────────

def render_delegator(data: dict) -> None:
    meta = data["run_metadata"]
    summary = data["summary"]

    st.title("Customer Delegator Node — Eval Dashboard")
    cols = st.columns(5)
    cols[0].metric("Date", meta["date"])
    cols[1].metric("Model", meta["model"])
    cols[2].metric("Total Cases", meta["total_cases"])
    cols[3].metric("Duration", f"{meta['duration_seconds']}s")
    cols[4].metric("Errors", meta["errors"])
    _status_banner(summary["passes_all_thresholds"], summary["overall_accuracy"],
                   summary["macro_f1"], summary["macro_f1_threshold"])

    c1, c2 = st.columns([1, 1.4])
    with c1:
        st.plotly_chart(chart_delegator_thresholds(data), use_container_width=True)
    with c2:
        st.plotly_chart(chart_per_domain_metrics(data), use_container_width=True)

    c3, c4 = st.columns([1.2, 1])
    with c3:
        st.plotly_chart(chart_delegator_confusion(data), use_container_width=True)
    with c4:
        st.plotly_chart(chart_boundary_pair_accuracy(data), use_container_width=True)

    c5, c6 = st.columns([1, 1.6])
    with c5:
        st.plotly_chart(chart_history_accuracy(data), use_container_width=True)
    with c6:
        st.plotly_chart(chart_performance(data), use_container_width=True)

    st.subheader(f"Failures ({len(data['failures'])})")
    if data["failures"]:
        delegator_failures_table(data)
    else:
        st.success("No failures — all predictions correct.")


def render_classifier(data: dict) -> None:
    meta = data["run_metadata"]
    summary = data["summary"]

    st.title("Intent Classifier Node — Eval Dashboard")
    cols = st.columns(5)
    cols[0].metric("Date", meta["date"])
    cols[1].metric("Model", meta["model"])
    cols[2].metric("Total Cases", meta["total_cases"])
    cols[3].metric("Duration", f"{meta['duration_seconds']}s")
    cols[4].metric("Errors", meta["errors"])
    _status_banner(summary["passes_all_thresholds"], summary["overall_accuracy"],
                   summary["macro_f1"], summary["macro_f1_threshold"])

    # Row 1: thresholds + per-intent bars
    c1, c2 = st.columns([1, 1.6])
    with c1:
        st.plotly_chart(chart_classifier_thresholds(data), use_container_width=True)
    with c2:
        st.plotly_chart(chart_per_intent_metrics(data), use_container_width=True)

    # Row 2: domain breakdown + confusion matrix
    c3, c4 = st.columns([1, 1.6])
    with c3:
        st.plotly_chart(chart_domain_breakdown(data), use_container_width=True)
    with c4:
        st.plotly_chart(chart_classifier_confusion(data), use_container_width=True)

    # Row 3: false rejection gauge + confidence calibration
    c5, c6 = st.columns([1, 1.6])
    with c5:
        st.plotly_chart(chart_false_rejection(data), use_container_width=True)
    with c6:
        st.plotly_chart(chart_confidence_calibration(data), use_container_width=True)

    # Row 4: history accuracy + performance
    c7, c8 = st.columns([1, 1.6])
    with c7:
        st.plotly_chart(chart_history_accuracy(data), use_container_width=True)
    with c8:
        st.plotly_chart(chart_performance(data), use_container_width=True)

    # Boundary pairs (full width — more pairs than delegator)
    if data.get("boundary_pair_accuracy"):
        st.plotly_chart(chart_boundary_pair_accuracy(data), use_container_width=True)

    st.subheader(f"Failures ({len(data['failures'])})")
    if data["failures"]:
        classifier_failures_table(data)
    else:
        st.success("No failures — all predictions correct.")


def render_tool_planner(data: dict) -> None:
    meta = data["run_metadata"]
    summary = data["summary"]

    st.title("Tool Planner Node — Eval Dashboard")
    cols = st.columns(5)
    cols[0].metric("Date", meta["date"])
    cols[1].metric("Model", meta["model"])
    cols[2].metric("Total Cases", meta["total_cases"])
    cols[3].metric("Duration", f"{meta['duration_seconds']}s")
    cols[4].metric("Errors", meta["errors"])
    _planner_status_banner(data)

    c1, c2 = st.columns([1, 1.4])
    with c1:
        st.plotly_chart(chart_planner_thresholds(data), use_container_width=True)
    with c2:
        st.plotly_chart(chart_planner_category_accuracy(data), use_container_width=True)

    c3, c4 = st.columns([1, 1.4])
    with c3:
        rbac = data.get("rbac", {})
        if rbac.get("count", 0) > 0:
            st.error(f"⚠️ RBAC violation: {rbac['count']} customer-role result(s) selected a non-customer tool.")
            for v in rbac.get("violations", []):
                st.write(f"  • `{v['id']}` → `{v['predicted_tool']}`")
        else:
            st.success("✅ RBAC: no non-customer tools selected by customer role.")
        st.plotly_chart(chart_planner_args_coverage(data), use_container_width=True)
    with c4:
        st.plotly_chart(chart_performance(data), use_container_width=True)

    st.subheader(f"Failures ({len(data['failures'])})")
    if data["failures"]:
        planner_failures_table(data)
    else:
        st.success("No failures — all tool selections correct.")


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    st.set_page_config(
        page_title="Agent Eval Dashboard",
        page_icon="📊",
        layout="wide",
    )

    st.sidebar.title("📊 Agent Eval Dashboard")

    eval_label = st.sidebar.radio(
        "Evaluation Node",
        list(EVAL_TYPES.keys()),
        index=0,
    )
    eval_suffix = EVAL_TYPES[eval_label]

    result_files = _discover_results(eval_suffix)
    if not result_files:
        st.error(
            f"No result files found for **{eval_label}** in `eval/results/`. "
            "Run the eval first."
        )
        return

    st.sidebar.markdown("---")
    file_labels = [f.name for f in result_files]
    selected_label = st.sidebar.selectbox(
        "Select run", file_labels, index=0,
        help="Sorted newest first. Run the eval to add a new entry.",
    )
    selected_path = result_files[file_labels.index(selected_label)]
    data = _load(selected_path)

    if eval_suffix == "customer_delegator":
        render_delegator(data)
    elif eval_suffix == "tool_planner":
        render_tool_planner(data)
    else:
        render_classifier(data)


if __name__ == "__main__":
    main()
