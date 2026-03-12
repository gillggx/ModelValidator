"""
Reporter: generates test_report.json
Structure:
{
  "metadata": { timestamp, models_tested, baseline, pass_line },
  "results": {
    "<model>": {
      "overall_score": float,
      "passed": bool,
      "dimension_scores": { fidelity, stability, speed, consistency },
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
from datetime import datetime, timezone
from scorer import compute_dimension_scores, BASELINE_MODEL, BASELINE_SCORE, PASS_LINE


def build_report(all_results: dict[str, list[dict]]) -> dict:
    """
    all_results: {model: [{"scenario", "run", "validation", "prompt", "ground_truth"}]}
    """
    timestamp = datetime.now(tz=timezone.utc).isoformat()

    report = {
        "metadata": {
            "timestamp": timestamp,
            "spec_version": "v14.0",
            "models_tested": list(all_results.keys()),
            "baseline_model": BASELINE_MODEL,
            "baseline_score": BASELINE_SCORE,
            "pass_line": PASS_LINE,
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

        report["results"][model] = {
            "overall_score": dim_scores.overall,
            "passed": dim_scores.passes(),
            "verdict": "PASS ✓" if dim_scores.passes() else "FAIL ✗",
            "dimension_scores": {
                "fidelity": dim_scores.fidelity,
                "stability": dim_scores.stability,
                "speed": dim_scores.speed,
                "consistency": dim_scores.consistency,
            },
            "performance": {
                "ttft_avg": round(ttft_avg, 4),
                "tps_avg": round(tps_avg, 2),
            },
            "scenarios": scenario_records,
        }

        report["ranking"].append({
            "model": model,
            "score": dim_scores.overall,
            "passed": dim_scores.passes(),
            "fidelity": dim_scores.fidelity,
            "stability": dim_scores.stability,
            "speed": dim_scores.speed,
            "consistency": dim_scores.consistency,
        })

    # Sort ranking by overall score descending
    report["ranking"].sort(key=lambda x: x["score"], reverse=True)

    return report


def save_report(report: dict, output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────
# Markdown report
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


def save_markdown_reports(report: dict, json_path: str) -> list[str]:
    """
    Generate one .md file per model, named after the model.
    E.g. output=test_report.json → claude-sonnet-4-6.md, gpt-4o.md, ...
    Returns list of written file paths.
    """
    import os
    base_dir = os.path.dirname(os.path.abspath(json_path))
    written = []
    for model in report["results"]:
        safe_name = model.replace(":", "-").replace("/", "-")
        md_path = os.path.join(base_dir, f"{safe_name}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(_model_md(report, model))
        written.append(md_path)
    return written
