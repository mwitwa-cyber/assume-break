"""Rich-formatted report output for stress test results."""

from __future__ import annotations

import json
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from assume_break.state import CritiqueSeverity, PlanStatus, StressTestResult

console = Console()

STATUS_STYLES: dict[str, tuple[str, str]] = {
    PlanStatus.VALIDATED.value: ("bold green", "green"),
    PlanStatus.BROKEN.value: ("bold red", "red"),
    PlanStatus.NEEDS_REVISION.value: ("bold yellow", "yellow"),
    PlanStatus.UNDER_REVIEW.value: ("bold cyan", "cyan"),
    PlanStatus.DRAFT.value: ("bold white", "white"),
}

SEVERITY_STYLES: dict[str, str] = {
    CritiqueSeverity.FATAL.value: "bold red",
    CritiqueSeverity.MAJOR.value: "bold yellow",
    CritiqueSeverity.MINOR.value: "bold green",
    CritiqueSeverity.NONE.value: "dim",
}


def print_stress_test_report(result: StressTestResult) -> None:
    """Print a rich-formatted stress test report to the console."""
    console.print()

    # ── Status Banner ──
    status_style, border_style = STATUS_STYLES.get(
        result.plan_status.value, ("bold white", "white")
    )
    console.print(
        Panel(
            f"[{status_style}]PLAN STATUS: {result.plan_status.value}[/{status_style}]\n"
            f"Critique Severity: [{SEVERITY_STYLES.get(result.critique_severity.value, 'dim')}]"
            f"{result.critique_severity.value}[/]\n"
            f"Revision Rounds: {result.revision_count}",
            title="ASSUME-BREAK Stress Test Result",
            border_style=border_style,
            expand=False,
        )
    )

    # ── Assumptions Table ──
    if result.assumptions:
        assumption_table = Table(title="Extracted Assumptions", show_lines=True)
        assumption_table.add_column("#", style="dim", width=4)
        assumption_table.add_column("Assumption", style="white")
        for i, assumption in enumerate(result.assumptions, 1):
            assumption_table.add_row(str(i), assumption)
        console.print(assumption_table)

    # ── Critique/Defense Debate Timeline ──
    if result.critiques:
        debate_tree = Tree("[bold]Adversarial Debate Timeline[/bold]")
        for round_data in result.critiques:
            round_num = round_data.get("round", "?")
            round_branch = debate_tree.add(f"[bold cyan]Round {round_num}[/bold cyan]")
            for critique in round_data.get("critiques", []):
                verdict = critique.get("verdict", "MINOR")
                style = SEVERITY_STYLES.get(verdict, "dim")
                node = round_branch.add(
                    f"[{style}][{verdict}][/{style}] {critique.get('fracture', 'N/A')}"
                )
                node.add(f"[dim]Reality:[/dim] {critique.get('reality', 'N/A')}")
                node.add(f"[dim]Impact:[/dim] {critique.get('impact', 'N/A')}")
                node.add(f"[dim]Citation:[/dim] {critique.get('citation', 'N/A')}")

        # Attach defenses to the tree
        for defense_round in result.defenses:
            round_num = defense_round.get("round", "?")
            defense_branch = debate_tree.add(
                f"[bold green]Defense Round {round_num}[/bold green]"
            )
            for defense in defense_round.get("defenses", []):
                node = defense_branch.add(
                    f"[green]RE:[/green] {defense.get('response_to', 'N/A')}"
                )
                if defense.get("defense"):
                    node.add(f"[dim]Defense:[/dim] {defense['defense']}")
                if defense.get("revision"):
                    node.add(f"[dim]Revision:[/dim] {defense['revision']}")
                if defense.get("mitigation"):
                    node.add(f"[dim]Mitigation:[/dim] {defense['mitigation']}")

        console.print(debate_tree)

    # ── Citations Table ──
    if result.reality_citations:
        citation_table = Table(title="Reality Citations", show_lines=True)
        citation_table.add_column("#", style="dim", width=4)
        citation_table.add_column("Source", style="cyan")
        for i, citation in enumerate(result.reality_citations, 1):
            citation_table.add_row(str(i), citation)
        console.print(citation_table)

    console.print()


def result_to_dict(result: StressTestResult) -> dict[str, Any]:
    """Convert a StressTestResult to a JSON-serializable dict."""
    return {
        "plan_status": result.plan_status.value,
        "critique_severity": result.critique_severity.value,
        "assumptions": result.assumptions,
        "critiques": result.critiques,
        "defenses": result.defenses,
        "reality_citations": result.reality_citations,
        "revision_count": result.revision_count,
    }


def export_json(result: StressTestResult, path: str) -> None:
    """Export stress test result to a JSON file."""
    data = result_to_dict(result)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    console.print(f"[green]Report exported to {path}[/green]")
