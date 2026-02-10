"""Integration tests for the ASSUME-BREAK workflow graph."""

from __future__ import annotations

from unittest.mock import patch

from assume_break.graph import (
    MockAssumeBreakGraph,
    route_after_judge,
    should_continue,
    stress_test_plan,
)
from assume_break.state import CritiqueSeverity, PlanStatus, StressTestResult


class TestRouting:
    def test_fatal_ends(self):
        state = {"critique_severity": CritiqueSeverity.FATAL.value}
        assert should_continue(state) == "end"

    def test_major_goes_to_proponent(self):
        state = {"critique_severity": CritiqueSeverity.MAJOR.value}
        assert should_continue(state) == "proponent_revise"

    def test_minor_goes_to_judge(self):
        state = {"critique_severity": CritiqueSeverity.MINOR.value}
        assert should_continue(state) == "human_judge"

    def test_none_goes_to_judge(self):
        state = {"critique_severity": CritiqueSeverity.NONE.value}
        assert should_continue(state) == "human_judge"

    def test_validated_ends(self):
        state = {"plan_status": PlanStatus.VALIDATED.value}
        assert route_after_judge(state) == "end"

    def test_broken_ends(self):
        state = {"plan_status": PlanStatus.BROKEN.value}
        assert route_after_judge(state) == "end"

    def test_needs_revision_loops(self):
        state = {"plan_status": PlanStatus.NEEDS_REVISION.value}
        assert route_after_judge(state) == "adversary_critique"


class TestMockGraph:
    def test_mock_graph_runs(self):
        """Mock graph should execute the full flow without errors."""
        graph = MockAssumeBreakGraph()
        state = graph.invoke({
            "business_plan": "We plan to start a diesel transport business in Lusaka.",
            "critique_history": [],
            "defense_history": [],
            "revision_count": 0,
            "max_revisions": 2,
        })
        assert state["plan_status"] in [s.value for s in PlanStatus]
        assert len(state.get("assumption_tree", [])) > 0
        assert len(state.get("critique_history", [])) > 0

    def test_mock_graph_respects_max_revisions(self):
        """Mock graph should not exceed max_revisions."""
        graph = MockAssumeBreakGraph()
        state = graph.invoke({
            "business_plan": "We plan to import goods from China and sell in Zambia.",
            "critique_history": [],
            "defense_history": [],
            "revision_count": 0,
            "max_revisions": 1,
        })
        assert state["revision_count"] <= 2  # At most max_revisions + 1 check


class TestStressTestPlan:
    def test_returns_result(self):
        """stress_test_plan should return a StressTestResult."""
        # Force mock graph by making langgraph import fail
        with patch("assume_break.graph.build_assume_break_graph", return_value=MockAssumeBreakGraph()):
            result = stress_test_plan(
                "We plan to start a copper mining operation in North-Western Province.",
                max_revisions=1,
            )
        assert isinstance(result, StressTestResult)
        assert isinstance(result.plan_status, PlanStatus)
        assert isinstance(result.critique_severity, CritiqueSeverity)
        assert len(result.assumptions) > 0

    def test_empty_plan_still_runs(self):
        """Even a minimal plan should produce a result."""
        with patch("assume_break.graph.build_assume_break_graph", return_value=MockAssumeBreakGraph()):
            result = stress_test_plan("A small shop.", max_revisions=1)
        assert isinstance(result, StressTestResult)
