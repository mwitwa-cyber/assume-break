"""LangGraph workflow definition for the ASSUME-BREAK stress-test pipeline."""

from __future__ import annotations

import warnings
from typing import Any

from assume_break.agents.adversary import adversary_critique
from assume_break.agents.extractor import extract_assumptions
from assume_break.agents.judge import human_judge
from assume_break.agents.proponent import proponent_revise
from assume_break.config import get_settings
from assume_break.reality.engine import fetch_reality
from assume_break.state import (
    AgentState,
    CritiqueSeverity,
    PlanStatus,
    StressTestResult,
)


def should_continue(state: AgentState) -> str:
    """Route after adversary critique based on severity."""
    severity = state.get("critique_severity", CritiqueSeverity.NONE.value)
    if severity == CritiqueSeverity.FATAL.value:
        return "end"
    if severity == CritiqueSeverity.MAJOR.value:
        return "proponent_revise"
    return "human_judge"


def route_after_judge(state: AgentState) -> str:
    """Route after judge decision."""
    status = state.get("plan_status", "")
    if status in (PlanStatus.VALIDATED.value, PlanStatus.BROKEN.value):
        return "end"
    return "adversary_critique"


def build_assume_break_graph():
    """Build the LangGraph StateGraph for the ASSUME-BREAK workflow.

    Falls back to MockAssumeBreakGraph if langgraph is unavailable.
    """
    try:
        from langgraph.graph import END, StateGraph

        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("extract_assumptions", extract_assumptions)
        graph.add_node("retrieve_reality", fetch_reality)
        graph.add_node("adversary_critique", adversary_critique)
        graph.add_node("proponent_revise", proponent_revise)
        graph.add_node("human_judge", human_judge)

        # Set entry point
        graph.set_entry_point("extract_assumptions")

        # Linear edges
        graph.add_edge("extract_assumptions", "retrieve_reality")
        graph.add_edge("retrieve_reality", "adversary_critique")

        # Conditional edges after adversary
        graph.add_conditional_edges(
            "adversary_critique",
            should_continue,
            {
                "end": END,
                "proponent_revise": "proponent_revise",
                "human_judge": "human_judge",
            },
        )

        # After proponent revise, go to judge
        graph.add_edge("proponent_revise", "human_judge")

        # Conditional edges after judge
        graph.add_conditional_edges(
            "human_judge",
            route_after_judge,
            {
                "end": END,
                "adversary_critique": "adversary_critique",
            },
        )

        return graph.compile()

    except ImportError:
        warnings.warn("langgraph not installed — using MockAssumeBreakGraph fallback", stacklevel=2)
        return MockAssumeBreakGraph()


class MockAssumeBreakGraph:
    """Offline mock that simulates the exact graph execution flow without langgraph."""

    def invoke(self, state: dict[str, Any]) -> dict[str, Any]:
        # Initialize
        state.setdefault("critique_history", [])
        state.setdefault("defense_history", [])
        state.setdefault("revision_count", 0)
        state.setdefault("max_revisions", 3)
        state.setdefault("human_override", "")
        state.setdefault("awaiting_human", False)

        # Step 1: Extract assumptions
        state.update(extract_assumptions(state))

        # Step 2: Retrieve reality
        state.update(fetch_reality(state))

        # Debate loop
        for _ in range(state["max_revisions"] + 1):
            # Adversary critique
            critique_result = adversary_critique(state)
            state["critique_history"] = state.get("critique_history", []) + critique_result.get("critique_history", [])
            state["critique_severity"] = critique_result.get("critique_severity", state.get("critique_severity"))
            state["plan_status"] = critique_result.get("plan_status", state.get("plan_status"))

            # Route after adversary
            route = should_continue(state)
            if route == "end":
                break
            elif route == "proponent_revise":
                revise_result = proponent_revise(state)
                state["defense_history"] = state.get("defense_history", []) + revise_result.get("defense_history", [])

            # Judge
            judge_result = human_judge(state)
            state.update(judge_result)

            # Route after judge
            route = route_after_judge(state)
            if route == "end":
                break

        return state


def stress_test_plan(business_plan: str, max_revisions: int | None = None) -> StressTestResult:
    """Main entry point: run a full stress test on a business plan.

    Returns a structured StressTestResult.
    """
    settings = get_settings()
    if max_revisions is None:
        max_revisions = settings.max_revisions

    graph = build_assume_break_graph()

    initial_state: dict[str, Any] = {
        "business_plan": business_plan,
        "assumption_tree": [],
        "reality_context": "",
        "reality_citations": [],
        "critique_history": [],
        "defense_history": [],
        "plan_status": PlanStatus.DRAFT.value,
        "critique_severity": CritiqueSeverity.NONE.value,
        "revision_count": 0,
        "max_revisions": max_revisions,
        "human_override": "",
        "awaiting_human": False,
    }

    config = {"recursion_limit": max_revisions * 5 + 20}
    try:
        final_state = graph.invoke(initial_state, config=config)
    except Exception:
        # If the graph hits recursion limit or other error, fall back to mock
        warnings.warn("LangGraph execution failed, falling back to mock graph", stacklevel=2)
        mock = MockAssumeBreakGraph()
        final_state = mock.invoke(initial_state)

    return StressTestResult(
        plan_status=PlanStatus(final_state.get("plan_status", PlanStatus.DRAFT.value)),
        critique_severity=CritiqueSeverity(final_state.get("critique_severity", CritiqueSeverity.NONE.value)),
        assumptions=final_state.get("assumption_tree", []),
        critiques=final_state.get("critique_history", []),
        defenses=final_state.get("defense_history", []),
        reality_citations=final_state.get("reality_citations", []),
        revision_count=final_state.get("revision_count", 0),
        raw_state=final_state,
    )
