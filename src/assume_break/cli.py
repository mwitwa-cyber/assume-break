"""Rich CLI interface using Typer."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(
    name="assume-break",
    help="Adversarial business plan stress-testing against Zambian economic realities.",
    add_completion=False,
)
console = Console()


@app.command()
def test(
    plan: Optional[str] = typer.Argument(None, help="Business plan text to stress test"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Path to business plan text file"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive mode with human-in-the-loop"),
    max_revisions: int = typer.Option(3, "--max-revisions", "-r", help="Maximum revision rounds"),
    export: Optional[Path] = typer.Option(None, "--export", "-e", help="Export results to JSON file"),
) -> None:
    """Run an adversarial stress test on a business plan."""
    from assume_break.graph import stress_test_plan
    from assume_break.report import export_json, print_stress_test_report

    # Get plan text
    plan_text = ""
    if file:
        if not file.exists():
            console.print(f"[red]File not found: {file}[/red]")
            raise typer.Exit(1)
        plan_text = file.read_text()
    elif plan:
        plan_text = plan
    elif interactive:
        console.print(
            Panel(
                "Enter your business plan below.\n"
                "Press Enter twice (empty line) when done.",
                title="Interactive Mode",
                border_style="cyan",
            )
        )
        lines: list[str] = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        plan_text = "\n".join(lines).strip()
    else:
        console.print("[red]Provide a plan as argument, --file, or use --interactive[/red]")
        raise typer.Exit(1)

    if not plan_text.strip():
        console.print("[red]Empty business plan provided.[/red]")
        raise typer.Exit(1)

    # Run stress test with spinner
    with console.status("[bold cyan]Running ASSUME-BREAK stress test...", spinner="dots"):
        result = stress_test_plan(plan_text, max_revisions=max_revisions)

    print_stress_test_report(result)

    if export:
        export_json(result, str(export))


@app.command()
def facts(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category (e.g., TAX, ENERGY, MINING)"),
) -> None:
    """List all facts in the Zambian reality database."""
    from assume_break.reality.database import ZAMBIAN_REALITY_DATABASE

    table = Table(title="Zambian Reality Database", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Category", style="cyan", width=14)
    table.add_column("Fact", style="white", max_width=80)
    table.add_column("Source", style="dim", max_width=40)

    filtered = ZAMBIAN_REALITY_DATABASE
    if category:
        cat_upper = category.upper()
        filtered = [f for f in ZAMBIAN_REALITY_DATABASE if f.category == cat_upper]
        if not filtered:
            console.print(f"[yellow]No facts found for category: {category}[/yellow]")
            available = sorted({f.category for f in ZAMBIAN_REALITY_DATABASE})
            console.print(f"Available categories: {', '.join(available)}")
            raise typer.Exit(1)

    for i, fact in enumerate(filtered, 1):
        table.add_row(str(i), fact.category, fact.fact, fact.source)

    console.print(table)
    console.print(f"\n[dim]Total facts: {len(filtered)}[/dim]")


if __name__ == "__main__":
    app()
