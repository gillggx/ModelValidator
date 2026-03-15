"""
Reporter: generates test_report.json
Structure:
{
  "metadata": { timestamp, models_tested, baseline, pass_line },
  "results": {
    "<model>": {
      "overall_score": float,
      "passed": bool,
      "dimension_scores": { fidelity, stability, speed, consistency },  # V14
      OR
      "dimension_scores": { precision, planning, context, robustness, safety },  # V15
      "performance": { ttft_avg, tps_avg },
      "scenarios": [
        {
          "id", "name", "category", "score", "passed",
          "details", "raw_prompt", "raw_response", "error"
        }
      ]
    }
  },
  "ranking": [{ "model", "score", "passed" }]
}
"""
import json
import os
from datetime import datetime, timezone
from scorer import (
    compute_dimension_scores, BASELINE_MODEL, BASELINE_SCORE, PASS_LINE,
    compute_dimension_scores_v15, PASS_LINE_V15,
    compute_dimension_scores_v16, PASS_LINE_V16,
)


def build_report(all_results: dict[str, list[dict]], suite: str = "v14") -> dict:
    """
    all_results: {model: [{"scenario", "run", "validation", "prompt", "ground_truth"}]}
    suite: "v14" or "v15"
    """
    timestamp = datetime.now(tz=timezone.utc).isoformat()

    is_v15 = suite == "v15"
    is_v16 = suite == "v16"

    spec_version = "v16.0" if is_v16 else ("v15.0" if is_v15 else "v14.0")
    pass_line = PASS_LINE_V16 if is_v16 else (PASS_LINE_V15 if is_v15 else PASS_LINE)

    report = {
        "metadata": {
            "timestamp": timestamp,
            "spec_version": spec_version,
            "suite": suite,
            "models_tested": list(all_results.keys()),
            "baseline_model": BASELINE_MODEL,
            "baseline_score": BASELINE_SCORE,
            "pass_line": pass_line,
        },
        "results": {},
        "ranking": [],
    }

    for model, items in all_results.items():
        # Collect performance metrics
        run_results = [item["run"] for item in items]
        valid_runs = [r for r in run_results if not r.timed_out and not r.error]

        ttft_avg = sum(r.ttft for r in valid_runs) / len(valid_runs) if valid_runs else 0.0
        tps_avg = sum(r.tps for r in valid_runs) / len(valid_runs) if valid_runs else 0.0

        if is_v16:
            dim_scores = compute_dimension_scores_v16(items)
        elif is_v15:
            dim_scores = compute_dimension_scores_v15(items)
        else:
            dim_scores = compute_dimension_scores(items, ttft_avg, tps_avg)

        scenario_records = []
        for item in items:
            sc = item["scenario"]
            run = item["run"]
            val = item["validation"]

            scenario_records.append({
                "id": sc.id,
                "name": sc.name,
                "category": sc.category,
                "score": round(val.score, 2),
                "passed": val.passed,
                "details": val.details,
                "raw_prompt": item.get("prompt", ""),
                "raw_response": run.response,
                "ttft": round(run.ttft, 4),
                "total_time": round(run.total_time, 4),
                "tps": round(run.tps, 2),
                "error": run.error,
                "timed_out": run.timed_out,
            })

        if is_v16:
            dimension_scores_dict = {
                "code_gen":         dim_scores.code_gen,
                "function_calling": dim_scores.function_calling,
                "context_mapping":  dim_scores.context_mapping,
                "planning":         dim_scores.planning,
                "robustness":       dim_scores.robustness,
                "safety":           dim_scores.safety,
            }
        elif is_v15:
            dimension_scores_dict = {
                "precision": dim_scores.precision,
                "planning": dim_scores.planning,
                "context": dim_scores.context,
                "robustness": dim_scores.robustness,
                "safety": dim_scores.safety,
            }
        else:
            dimension_scores_dict = {
                "fidelity": dim_scores.fidelity,
                "stability": dim_scores.stability,
                "speed": dim_scores.speed,
                "consistency": dim_scores.consistency,
            }

        report["results"][model] = {
            "overall_score": dim_scores.overall,
            "passed": dim_scores.passes(),
            "verdict": "PASS ✓" if dim_scores.passes() else "FAIL ✗",
            "dimension_scores": dimension_scores_dict,
            "performance": {
                "ttft_avg": round(ttft_avg, 4),
                "tps_avg": round(tps_avg, 2),
            },
            "scenarios": scenario_records,
        }

        ranking_entry = {
            "model": model,
            "score": dim_scores.overall,
            "passed": dim_scores.passes(),
        }
        ranking_entry.update(dimension_scores_dict)
        report["ranking"].append(ranking_entry)

    # Sort ranking by overall score descending
    report["ranking"].sort(key=lambda x: x["score"], reverse=True)

    return report


def save_report(report: dict, output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────
# Markdown report — V14
# ──────────────────────────────────────────────

def _model_md(report: dict, model: str) -> str:
    res = report["results"][model]
    ds = res["dimension_scores"]
    perf = res["performance"]
    meta = report["metadata"]
    scenarios = sorted(res["scenarios"], key=lambda s: s["id"])

    def icon(val, threshold=80):
        return "✅" if val >= threshold else "❌"

    def result_icon(s):
        if s.get("timed_out"):
            return "⏱ TIMEOUT"
        if s.get("error") and not s["passed"]:
            return "💥 ERROR"
        return "✅ PASS" if s["passed"] else "❌ FAIL"

    lines = [
        f"# {model} — LLM 核心誠信驗證報告",
        f"",
        f"> 測試時間：{meta['timestamp'][:10]}  |  Spec：{meta['spec_version']}  |  及格線：{meta['pass_line']}",
        f"",
        f"## 總分：{res['overall_score']} / 100 　{'✅ PASS' if res['passed'] else '❌ FAIL'}",
        f"",
        f"---",
        f"",
        f"## 維度分數",
        f"",
        f"| 維度 | 分數 | 目標 | 狀態 |",
        f"|---|---|---|---|",
        f"| 資料保真度 (Fidelity)    | {ds['fidelity']}  | ≥80 | {icon(ds['fidelity'])} |",
        f"| 結構穩定度 (Stability)   | {ds['stability']} | ≥80 | {icon(ds['stability'])} |",
        f"| 速度評分   (Speed)       | {ds['speed']}     | ≥80 | {icon(ds['speed'])} |",
        f"| 邏輯一致性 (Consistency) | {ds['consistency']} | ≥80 | {icon(ds['consistency'])} |",
        f"",
        f"## 效能指標",
        f"",
        f"| 指標 | 數值 | 目標 |",
        f"|---|---|---|",
        f"| TTFT 平均 | {perf['ttft_avg']:.2f}s | < 1.0s |",
        f"| TPS 平均  | {perf['tps_avg']:.1f} tok/s | > 30 |",
        f"",
        f"---",
        f"",
        f"## 20 個場景明細",
        f"",
        f"| ID | 場景名稱 | 類別 | 分數 | TTFT | 結果 |",
        f"|---|---|---|---|---|---|",
    ]

    for s in scenarios:
        lines.append(
            f"| {s['id']} | {s['name']} | {s['category']} "
            f"| {s['score']:.0f} | {s['ttft']:.2f}s | {result_icon(s)} |"
        )

    fails = [s for s in scenarios if not s["passed"]]
    if fails:
        lines += ["", "---", "", "## 失敗分析", ""]
        for s in fails:
            lines.append(f"### Scenario {s['id']} — {s['name']}")
            lines.append(f"- **分數**：{s['score']:.0f} / 100")
            if s.get("timed_out"):
                lines.append(f"- **原因**：超過 timeout（本機推理速度不足）")
            elif s.get("error"):
                lines.append(f"- **原因**：`{s['error']}`")
            else:
                lines.append(f"- **詳情**：{json.dumps(s.get('details', {}), ensure_ascii=False)}")
            lines.append("")

    lines += ["---", "", "*Generated by LLM Core Integrity Validator v14.0*"]
    return "\n".join(lines)


# ──────────────────────────────────────────────
# Markdown report — V15
# ──────────────────────────────────────────────

def _model_md_v15(report: dict, model: str) -> str:
    res = report["results"][model]
    ds = res["dimension_scores"]
    perf = res["performance"]
    meta = report["metadata"]
    scenarios = sorted(res["scenarios"], key=lambda s: s["id"])

    pass_line = meta.get("pass_line", 70)

    def icon(val, threshold=70):
        return "✅" if val >= threshold else "❌"

    def result_icon(s):
        if s.get("timed_out"):
            return "⏱ TIMEOUT"
        if s.get("error") and not s["passed"]:
            return "💥 ERROR"
        return "✅ PASS" if s["passed"] else "❌ FAIL"

    lines = [
        f"# {model} — Agentic AI 能力驗證報告 (V15)",
        f"",
        f"> 測試時間：{meta['timestamp'][:10]}  |  Spec：{meta['spec_version']}  |  及格線：{pass_line}",
        f"",
        f"## 總分：{res['overall_score']} / 100 　{'✅ PASS' if res['passed'] else '❌ FAIL'}",
        f"",
        f"---",
        f"",
        f"## V15 維度分數",
        f"",
        f"| 維度 | 分數 | 權重 | 目標 | 狀態 |",
        f"|---|---|---|---|---|",
        f"| 精準度 (Precision)         | {ds['precision']}  | 25% | ≥70 | {icon(ds['precision'])} |",
        f"| 規劃力 (Planning)          | {ds['planning']}   | 20% | ≥70 | {icon(ds['planning'])} |",
        f"| 上下文保真度 (Context)     | {ds['context']}    | 20% | ≥70 | {icon(ds['context'])} |",
        f"| 健壯性 (Robustness)        | {ds['robustness']} | 20% | ≥70 | {icon(ds['robustness'])} |",
        f"| 安全範圍 (Safety)          | {ds['safety']}     | 15% | ≥70 | {icon(ds['safety'])} |",
        f"",
        f"## 效能指標",
        f"",
        f"| 指標 | 數值 | 目標 |",
        f"|---|---|---|",
        f"| TTFT 平均 | {perf['ttft_avg']:.2f}s | < 1.0s |",
        f"| TPS 平均  | {perf['tps_avg']:.1f} tok/s | > 30 |",
        f"",
        f"---",
        f"",
        f"## 20 個 Agentic 場景明細",
        f"",
        f"| ID | 場景名稱 | 類別 | 分數 | TTFT | 結果 |",
        f"|---|---|---|---|---|---|",
    ]

    for s in scenarios:
        lines.append(
            f"| {s['id']} | {s['name']} | {s['category']} "
            f"| {s['score']:.0f} | {s['ttft']:.2f}s | {result_icon(s)} |"
        )

    fails = [s for s in scenarios if not s["passed"]]
    if fails:
        lines += ["", "---", "", "## 失敗分析", ""]
        for s in fails:
            lines.append(f"### Scenario {s['id']} — {s['name']}")
            lines.append(f"- **分數**：{s['score']:.0f} / 100")
            lines.append(f"- **類別**：{s['category']}")
            if s.get("timed_out"):
                lines.append(f"- **原因**：超過 timeout")
            elif s.get("error"):
                lines.append(f"- **原因**：`{s['error']}`")
            else:
                lines.append(f"- **詳情**：{json.dumps(s.get('details', {}), ensure_ascii=False)}")
            lines.append("")

    lines += ["---", "", "*Generated by LLM Core Integrity Validator v15.0 — Agentic AI Test Suite*"]
    return "\n".join(lines)


def save_markdown_reports(report: dict, json_path: str, suite: str = "v14") -> list[str]:
    """
    Generate one .md file per model, named after the model.
    E.g. output=test_report.json → claude-sonnet-4-6.md, gpt-4o.md, ...
    Returns list of written file paths.
    """
    base_dir = os.path.dirname(os.path.abspath(json_path))
    written = []
    for model in report["results"]:
        safe_name = model.replace(":", "-").replace("/", "-")
        md_path = os.path.join(base_dir, f"{safe_name}.md")
        if suite == "v16":
            content = _model_md_v16(report, model)
        elif suite == "v15":
            content = _model_md_v15(report, model)
        else:
            content = _model_md(report, model)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(content)
        written.append(md_path)
    return written


# ──────────────────────────────────────────────
# AgenticAI Summary — V15
# ──────────────────────────────────────────────

def save_agenticai_summary(report: dict, output_path: str = "agenticAI_summary.md") -> str:
    """
    Generates a summary markdown file for V15 agentic results.
    Includes ranking table, key findings, and pass/fail analysis.
    Returns the path of the written file.
    """
    meta = report["metadata"]
    ranking = report["ranking"]
    results = report["results"]
    pass_line = meta.get("pass_line", 70)

    lines = [
        "# AgenticAI Benchmark Summary — V15.0",
        "",
        f"> Generated: {meta['timestamp'][:10]}  |  Suite: Agentic AI Stress-Test (20 scenarios)  |  Pass Line: {pass_line}",
        "",
        "---",
        "",
        "## Overall Ranking",
        "",
        "| Rank | Model | Overall | Precision | Planning | Context | Robustness | Safety | Verdict |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    for rank, entry in enumerate(ranking, 1):
        model = entry["model"]
        verdict = "PASS" if entry["passed"] else "FAIL"
        verdict_marker = "✅" if entry["passed"] else "❌"
        lines.append(
            f"| {rank} | {model} | **{entry['score']}** "
            f"| {entry.get('precision', 'N/A')} "
            f"| {entry.get('planning', 'N/A')} "
            f"| {entry.get('context', 'N/A')} "
            f"| {entry.get('robustness', 'N/A')} "
            f"| {entry.get('safety', 'N/A')} "
            f"| {verdict_marker} {verdict} |"
        )

    # Models that passed
    passing_models = [e["model"] for e in ranking if e["passed"]]
    failing_models = [e["model"] for e in ranking if not e["passed"]]

    lines += [
        "",
        "---",
        "",
        "## Production Qualification",
        "",
    ]

    if passing_models:
        lines.append(f"### Models Qualified for Production Agentic Use (score >= {pass_line})")
        lines.append("")
        for m in passing_models:
            lines.append(f"- **{m}** — Score: {results[m]['overall_score']}")
        lines.append("")
    else:
        lines.append(f"### No models achieved the pass line of {pass_line} in this run.")
        lines.append("")

    if failing_models:
        lines.append("### Models Below Pass Line")
        lines.append("")
        for m in failing_models:
            lines.append(f"- {m} — Score: {results[m]['overall_score']}")
        lines.append("")

    # Per-category analysis
    lines += [
        "---",
        "",
        "## Category Performance Analysis",
        "",
    ]

    categories = ["precision", "planning", "context", "robustness", "safety"]
    cat_labels = {
        "precision":  "Tool Use Precision (精準度)",
        "planning":   "Planning & Decomposition (規劃力)",
        "context":    "Context Fidelity (上下文保真度)",
        "robustness": "Error Robustness (健壯性)",
        "safety":     "Safety & Scope (安全範圍)",
    }

    for cat in categories:
        lines.append(f"### {cat_labels[cat]}")
        lines.append("")
        cat_scores = [(m, results[m]["dimension_scores"].get(cat, 0)) for m in results]
        cat_scores.sort(key=lambda x: x[1], reverse=True)
        for model, score in cat_scores:
            bar_len = int(score / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            status = "✅" if score >= 70 else "❌"
            lines.append(f"- {model}: {score:.1f} {status}  `{bar}`")
        lines.append("")

    # Common failure patterns
    lines += [
        "---",
        "",
        "## Common Failure Patterns",
        "",
    ]

    cat_failures: dict[str, list[str]] = {cat: [] for cat in categories}

    for model, res in results.items():
        for sc in res["scenarios"]:
            if not sc["passed"]:
                # Map category to dimension
                cat_map = {
                    "tool_use": "precision",
                    "planning": "planning",
                    "context": "context",
                    "robustness": "robustness",
                    "safety": "safety",
                }
                dim = cat_map.get(sc["category"], sc["category"])
                if dim in cat_failures:
                    cat_failures[dim].append(f"{model} / Scenario {sc['id']} ({sc['name']}): score={sc['score']:.0f}")

    for cat in categories:
        failures = cat_failures[cat]
        if failures:
            lines.append(f"### {cat_labels[cat]}")
            for f in failures[:10]:  # limit to 10 per category
                lines.append(f"- {f}")
            if len(failures) > 10:
                lines.append(f"- ... and {len(failures) - 10} more")
            lines.append("")

    # Dimension weights reminder
    lines += [
        "---",
        "",
        "## V15 Scoring Formula",
        "",
        "```",
        "Overall = 0.25 * Precision  (Tool Use)",
        "        + 0.20 * Planning    (Goal Decomposition)",
        "        + 0.20 * Context     (Multi-turn Fidelity)",
        "        + 0.20 * Robustness  (Error Handling)",
        "        + 0.15 * Safety      (Scope & Safety)",
        "",
        f"Pass Line: {pass_line} / 100",
        "```",
        "",
        "---",
        "",
        "*Generated by LLM Core Integrity Validator v15.0 — Agentic AI Test Suite*",
    ]

    # Determine output directory
    if not os.path.isabs(output_path):
        output_path = os.path.abspath(output_path)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output_path


# ──────────────────────────────────────────────
# Markdown report — V16
# ──────────────────────────────────────────────

def _model_md_v16(report: dict, model: str) -> str:
    res = report["results"][model]
    ds = res["dimension_scores"]
    perf = res["performance"]
    meta = report["metadata"]
    scenarios = sorted(res["scenarios"], key=lambda s: s["id"])
    pass_line = meta.get("pass_line", 65)

    def icon(val, threshold=65):
        return "✅" if val >= threshold else "❌"

    def result_icon(s):
        if s.get("timed_out"):
            return "⏱ TIMEOUT"
        if s.get("error") and not s["passed"]:
            return "💥 ERROR"
        return "✅ PASS" if s["passed"] else "❌ FAIL"

    lines = [
        f"# {model} — Agentic AI + Code Gen 驗證報告 (V16)",
        "",
        f"> 測試時間：{meta['timestamp'][:10]}  |  Spec：{meta['spec_version']}  |  及格線：{pass_line}",
        "",
        f"## 總分：{res['overall_score']} / 100 　{'✅ PASS' if res['passed'] else '❌ FAIL'}",
        "",
        "---",
        "",
        "## V16 維度分數 (Difficulty-Weighted)",
        "",
        "| 維度 | 分數 | 權重 | 目標 | 狀態 |",
        "|---|---|---|---|---|",
        f"| 程式生成 (Code Gen)          | {ds['code_gen']}         | 30% | ≥65 | {icon(ds['code_gen'])} |",
        f"| 工具呼叫 (Function Calling)  | {ds['function_calling']} | 25% | ≥65 | {icon(ds['function_calling'])} |",
        f"| 上下文映射 (Context Mapping) | {ds['context_mapping']}  | 20% | ≥65 | {icon(ds['context_mapping'])} |",
        f"| 規劃能力 (Planning)          | {ds['planning']}         | 15% | ≥65 | {icon(ds['planning'])} |",
        f"| 健壯性 (Robustness)          | {ds['robustness']}       |  7% | ≥65 | {icon(ds['robustness'])} |",
        f"| 安全範圍 (Safety)            | {ds['safety']}           |  3% | ≥65 | {icon(ds['safety'])} |",
        "",
        "## 效能指標",
        "",
        "| 指標 | 數值 |",
        "|---|---|",
        f"| TTFT 平均 | {perf['ttft_avg']:.2f}s |",
        f"| TPS 平均  | {perf['tps_avg']:.1f} tok/s |",
        "",
        "---",
        "",
        "## 50 個場景明細",
        "",
        "| ID | 場景名稱 | 類別 | 難度 | 分數 | TTFT | 結果 |",
        "|---|---|---|---|---|---|---|",
    ]

    for s in scenarios:
        difficulty = getattr(s.get("scenario_obj"), "difficulty", "—") if "scenario_obj" in s else "—"
        lines.append(
            f"| {s['id']} | {s['name']} | {s['category']} | — "
            f"| {s['score']:.0f} | {s['ttft']:.2f}s | {result_icon(s)} |"
        )

    fails = [s for s in scenarios if not s["passed"]]
    if fails:
        lines += ["", "---", "", "## 失敗分析", ""]
        for s in fails:
            lines.append(f"### {s['id']} — {s['name']}")
            lines.append(f"- **分數**：{s['score']:.0f} / 100  |  **類別**：{s['category']}")
            if s.get("timed_out"):
                lines.append("- **原因**：Timeout")
            elif s.get("error"):
                lines.append(f"- **原因**：`{s['error']}`")
            else:
                lines.append(f"- **詳情**：{json.dumps(s.get('details', {}), ensure_ascii=False)}")
            lines.append("")

    lines += ["---", "", "*Generated by LLM Core Integrity Validator v16.0 — Agentic + Code Gen Suite*"]
    return "\n".join(lines)


def save_v16_summary(report: dict, output_path: str = "v16_summary.md") -> str:
    """
    Generate agenticCodeGen_summary.md for V16 results.
    """
    meta = report["metadata"]
    ranking = report["ranking"]
    results = report["results"]
    pass_line = meta.get("pass_line", 65)

    lines = [
        "# Agentic + Code Gen Benchmark Summary — V16.0",
        "",
        f"> Generated: {meta['timestamp'][:10]}  |  Suite: V16 (50 scenarios)  |  Pass Line: {pass_line}",
        "",
        "---",
        "",
        "## Overall Ranking",
        "",
        "| Rank | Model | Overall | Code Gen | Func Call | Context | Planning | Robust | Safety | Verdict |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]

    for rank, entry in enumerate(ranking, 1):
        vm = "✅ PASS" if entry["passed"] else "❌ FAIL"
        lines.append(
            f"| {rank} | {entry['model']} | **{entry['score']}** "
            f"| {entry.get('code_gen', 'N/A')} "
            f"| {entry.get('function_calling', 'N/A')} "
            f"| {entry.get('context_mapping', 'N/A')} "
            f"| {entry.get('planning', 'N/A')} "
            f"| {entry.get('robustness', 'N/A')} "
            f"| {entry.get('safety', 'N/A')} "
            f"| {vm} |"
        )

    passing = [e["model"] for e in ranking if e["passed"]]
    failing = [e["model"] for e in ranking if not e["passed"]]

    lines += ["", "---", "", "## Production Qualification", ""]
    if passing:
        lines.append(f"### Qualified for Agentic + Code Agent Use (≥{pass_line})")
        lines.append("")
        for m in passing:
            lines.append(f"- **{m}** — {results[m]['overall_score']}")
        lines.append("")
    if failing:
        lines.append("### Below Pass Line")
        lines.append("")
        for m in failing:
            lines.append(f"- {m} — {results[m]['overall_score']}")
        lines.append("")

    # Per-category bar charts
    categories = [
        ("code_gen",         "Code Generation (程式生成)",    30),
        ("function_calling", "Function Calling (工具呼叫)",   25),
        ("context_mapping",  "Context Mapping (上下文映射)",  20),
        ("planning",         "Planning (規劃能力)",           15),
        ("robustness",       "Robustness (健壯性)",            7),
        ("safety",           "Safety (安全範圍)",              3),
    ]

    lines += ["---", "", "## Category Performance", ""]
    for cat, label, weight in categories:
        lines.append(f"### {label} — Weight: {weight}%")
        lines.append("")
        scores = [(m, results[m]["dimension_scores"].get(cat, 0)) for m in results]
        scores.sort(key=lambda x: x[1], reverse=True)
        for model, score in scores:
            bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
            status = "✅" if score >= 65 else "❌"
            lines.append(f"- {model}: {score:.1f} {status}  `{bar}`")
        lines.append("")

    # Failure patterns
    lines += ["---", "", "## Common Failure Patterns", ""]
    for cat, label, _ in categories:
        fails = []
        for model, res in results.items():
            for sc in res["scenarios"]:
                if not sc["passed"] and sc["category"] == cat:
                    fails.append(f"{model} / {sc['id']} ({sc['name']}): {sc['score']:.0f}pts")
        if fails:
            lines.append(f"### {label}")
            for f in fails[:8]:
                lines.append(f"- {f}")
            if len(fails) > 8:
                lines.append(f"- ... and {len(fails)-8} more")
            lines.append("")

    lines += [
        "---",
        "",
        "## V16 Scoring Formula",
        "",
        "```",
        "category_score = Σ(scenario_score × difficulty_weight) / Σ(difficulty_weight)",
        "  where difficulty: 1x=1.0 | 1.5x=1.5 | 2x=2.0",
        "",
        "Overall = code_gen×0.30 + function_calling×0.25 + context_mapping×0.20",
        "        + planning×0.15 + robustness×0.07 + safety×0.03",
        "",
        f"Pass Line: {pass_line} / 100",
        "```",
        "",
        "---",
        "",
        "*Generated by LLM Core Integrity Validator v16.0*",
    ]

    if not os.path.isabs(output_path):
        output_path = os.path.abspath(output_path)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output_path
