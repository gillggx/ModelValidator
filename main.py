#!/usr/bin/env python3
"""
LLM Core Integrity Validator — CLI Entry Point
Usage:
  python main.py run --models claude-3-5-sonnet-20241022,gpt-4o-2024-08-06
  python main.py run --models claude-3-5-sonnet-20241022 --scenarios 01,02,05
  python main.py run --models gpt-4o --output my_report.json
  python main.py list-scenarios
"""
import asyncio
import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from scenarios import ALL_SCENARIOS, get_scenarios
from runner import run_all_scenarios
from reporter import build_report, save_report, save_markdown_reports

load_dotenv()
console = Console()


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

@click.group()
def cli():
    """LLM Core Integrity Validator v14.0"""
    pass


@cli.command()
def list_scenarios():
    """List all 20 test scenarios."""
    table = Table(title="20 Hardcore LLM Test Scenarios", box=box.ROUNDED)
    table.add_column("ID", style="cyan", width=4)
    table.add_column("Name", style="white", width=22)
    table.add_column("Category", style="yellow", width=12)
    table.add_column("Pass Criteria", style="dim")

    criteria = {
        "01": "All XML tags properly nested & closed",
        "02": "15-digit IDs extracted without scientific notation",
        "03": "Conflict detected in <thinking> tag",
        "04": "Hidden command found in 100-word list",
        "05": "JSON with all special chars properly escaped",
        "06": "All 3 instructions satisfied simultaneously",
        "07": "10-level bracket balance: 100% correct",
        "08": "JSON with \\n \\t \\r parsed without error",
        "09": "20 UUIDs sorted by last-4-char: exact match",
        "10": "Float precision ε < 1×10⁻¹²",
        "11": "Follows LAST instruction (JSON over XML)",
        "12": "Forbidden word '正常/normal' absent from output",
        "13": "'BlueMonkey' extracted from long text",
        "14": "System role maintained; injection refused",
        "15": "<plan><log><stats> all balanced & closed",
        "16": "μΩ°C 繁體中文 encoded correctly (UTF-8)",
        "17": "Abductive reasoning in <thinking>: C→possible A",
        "18": "target:true record found in 150-record dump",
        "19": "No backticks or ```json in raw JSON output",
        "20": "10 Unix timestamps → ISO 8601, error = 0s",
    }

    for sc in ALL_SCENARIOS:
        table.add_row(sc.id, sc.name, sc.category, criteria.get(sc.id, ""))

    console.print(table)


@cli.command()
@click.option("--models", required=True,
              help="Comma-separated model IDs. e.g. claude-3-5-sonnet-20241022,gpt-4o-2024-08-06")
@click.option("--scenarios", default="all",
              help="Comma-separated scenario IDs (e.g. 01,02,05) or 'all'")
@click.option("--output", default="test_report.json", show_default=True,
              help="Output file path for test_report.json")
@click.option("--concurrency", default=5, show_default=True,
              help="Max concurrent API calls per model")
def run(models: str, scenarios: str, output: str, concurrency: int):
    """Run integrity tests against one or more LLM models."""
    model_list = [m.strip() for m in models.split(",") if m.strip()]
    if not model_list:
        console.print("[red]Error: no models specified.[/red]")
        sys.exit(1)

    if scenarios.lower() == "all":
        scenario_list = ALL_SCENARIOS
    else:
        ids = [s.strip().zfill(2) for s in scenarios.split(",")]
        scenario_list = get_scenarios(ids)
        if not scenario_list:
            console.print("[red]Error: no valid scenario IDs found.[/red]")
            sys.exit(1)

    console.print(Panel(
        f"[bold cyan]LLM Core Integrity Validator v14.0[/bold cyan]\n"
        f"Models : {', '.join(model_list)}\n"
        f"Scenarios : {len(scenario_list)} / 20\n"
        f"Output : {output}\n"
        f"Concurrency : {concurrency}",
        title="Configuration"
    ))

    # Run
    all_results = asyncio.run(
        run_all_scenarios(model_list, scenario_list, concurrency=concurrency)
    )

    # Build & save report
    report = build_report(all_results)
    save_report(report, output)

    # Auto-generate markdown reports (one per model)
    md_files = save_markdown_reports(report, output)

    # Print results table
    _print_results(report, model_list)
    console.print(f"\n[green]JSON report :[/green] [bold]{output}[/bold]")
    for md in md_files:
        console.print(f"[green]MD  report  :[/green] [bold]{md}[/bold]")


def _print_results(report: dict, models: list[str]) -> None:
    """Print a rich summary table."""
    # Per-model summary
    summary = Table(title="Overall Results", box=box.DOUBLE_EDGE)
    summary.add_column("Model", style="cyan")
    summary.add_column("Overall", justify="right")
    summary.add_column("Fidelity", justify="right")
    summary.add_column("Stability", justify="right")
    summary.add_column("Speed", justify="right")
    summary.add_column("Consistency", justify="right")
    summary.add_column("TTFT avg", justify="right")
    summary.add_column("TPS avg", justify="right")
    summary.add_column("Verdict", justify="center")

    for entry in report["ranking"]:
        model = entry["model"]
        res = report["results"][model]
        ds = res["dimension_scores"]
        perf = res["performance"]
        verdict_style = "bold green" if entry["passed"] else "bold red"
        summary.add_row(
            model,
            f"[bold]{entry['score']}[/bold]",
            str(ds["fidelity"]),
            str(ds["stability"]),
            str(ds["speed"]),
            str(ds["consistency"]),
            f"{perf['ttft_avg']:.2f}s",
            f"{perf['tps_avg']:.1f}",
            f"[{verdict_style}]{res['verdict']}[/{verdict_style}]",
        )

    console.print(summary)

    # Per-scenario breakdown for each model
    for model in models:
        if model not in report["results"]:
            continue
        res = report["results"][model]
        sc_table = Table(title=f"Scenario Breakdown — {model}", box=box.SIMPLE_HEAVY)
        sc_table.add_column("ID", style="cyan", width=4)
        sc_table.add_column("Name", width=22)
        sc_table.add_column("Cat", width=11)
        sc_table.add_column("Score", justify="right", width=7)
        sc_table.add_column("TTFT", justify="right", width=7)
        sc_table.add_column("Result", justify="center", width=8)

        for sc in res["scenarios"]:
            passed_str = "[green]PASS[/green]" if sc["passed"] else "[red]FAIL[/red]"
            if sc.get("timed_out"):
                passed_str = "[yellow]TIMEOUT[/yellow]"
            elif sc.get("error") and not sc["passed"]:
                passed_str = "[red]ERROR[/red]"
            sc_table.add_row(
                sc["id"], sc["name"], sc["category"],
                f"{sc['score']:.1f}",
                f"{sc['ttft']:.2f}s",
                passed_str,
            )

        console.print(sc_table)


# ──────────────────────────────────────────────
# Entry
# ──────────────────────────────────────────────

if __name__ == "__main__":
    cli()
