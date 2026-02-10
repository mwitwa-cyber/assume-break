"""Tests for agent nodes with mocked LLM calls."""

from __future__ import annotations

from unittest.mock import patch

from assume_break.agents.adversary import adversary_critique
from assume_break.agents.extractor import extract_assumptions
from assume_break.agents.judge import human_judge
from assume_break.agents.llm import parse_structured_response
from assume_break.agents.proponent import proponent_revise
from assume_break.state import CritiqueSeverity, PlanStatus

LLM_CALL = "assume_break.agents.llm.call_claude"
LLM_PARSE = "assume_break.agents.llm.parse_structured_response"


def _make_state(**overrides):
    """Create a minimal AgentState dict for testing."""
    state = {
        "business_plan": "We plan to start a fresh produce delivery service from Mongu to Lusaka.",
        "assumption_tree": [],
        "reality_context": "[1] [LOGISTICS] Rural roads impassable during rainy season.",
        "reality_citations": ["[1] Road Development Agency 2025"],
        "critique_history": [],
        "defense_history": [],
        "plan_status": PlanStatus.DRAFT.value,
        "critique_severity": CritiqueSeverity.NONE.value,
        "revision_count": 0,
        "max_revisions": 3,
        "human_override": "",
        "awaiting_human": False,
    }
    state.update(overrides)
    return state


class TestParseStructuredResponse:
    def test_parse_single_block(self):
        response = """
FRACTURE: The plan assumes diesel costs K20/litre
REALITY: Diesel is K25.11/litre
CITATION: ERB Q1 2025
VERDICT: MAJOR
IMPACT: 25% cost increase
"""
        blocks = parse_structured_response(
            response, ["FRACTURE", "REALITY", "CITATION", "VERDICT", "IMPACT"]
        )
        assert len(blocks) == 1
        assert "diesel" in blocks[0]["fracture"].lower()
        assert "MAJOR" in blocks[0]["verdict"]

    def test_parse_multiple_blocks(self):
        response = """
FRACTURE: Assumption 1
REALITY: Reality 1
CITATION: Source 1
VERDICT: FATAL
IMPACT: Impact 1

FRACTURE: Assumption 2
REALITY: Reality 2
CITATION: Source 2
VERDICT: MINOR
IMPACT: Impact 2
"""
        blocks = parse_structured_response(
            response, ["FRACTURE", "REALITY", "CITATION", "VERDICT", "IMPACT"]
        )
        assert len(blocks) == 2

    def test_parse_empty_response(self):
        blocks = parse_structured_response("No structured data here", ["FRACTURE", "REALITY"])
        assert blocks == []


class TestExtractor:
    def test_fallback_extraction(self):
        """Test rule-based fallback when LLM is unavailable."""
        state = _make_state(
            business_plan="We need a bank loan to buy diesel trucks for transport logistics"
        )
        with patch(LLM_CALL, side_effect=Exception("No API key")):
            result = extract_assumptions(state)

        assert "assumption_tree" in result
        assert len(result["assumption_tree"]) > 0
        assert result["plan_status"] == "UNDER_REVIEW"

    def test_llm_extraction(self):
        """Test LLM-based extraction with mocked Claude response."""
        mock_response = (
            "[Financial] ASSUMPTION: Revenue will reach ZMW 4.5M in year one.\n"
            "[Operational] ASSUMPTION: Diesel fuel costs will remain below K22/litre.\n"
            "[Regulatory] ASSUMPTION: The business qualifies for Turnover Tax at 5%.\n"
        )
        state = _make_state()
        with patch(LLM_CALL, return_value=mock_response):
            result = extract_assumptions(state)

        assert len(result["assumption_tree"]) == 3
        assert any("Revenue" in a for a in result["assumption_tree"])


class TestAdversary:
    def test_fallback_critique(self):
        """Test rule-based fallback critique."""
        state = _make_state(
            assumption_tree=[
                "[Operational] ASSUMPTION: Fuel costs will remain stable at K20/litre.",
                "[Operational] ASSUMPTION: Transport routes will remain passable year-round.",
            ],
            reality_context="[1] Diesel K25.11/litre with 5-8% monthly volatility.",
        )
        with patch(LLM_CALL, side_effect=Exception("No API key")):
            result = adversary_critique(state)

        assert "critique_history" in result
        assert len(result["critique_history"]) > 0
        critiques = result["critique_history"][0]["critiques"]
        assert len(critiques) > 0

    def test_llm_critique(self):
        """Test LLM-based critique with mocked response."""
        mock_response = """
FRACTURE: The plan assumes diesel at K20/litre
REALITY: Diesel is K25.11/litre as of Q1 2025
CITATION: ERB Q1 2025 Price Schedule
VERDICT: MAJOR
IMPACT: 25% increase in fuel costs erodes margins

FRACTURE: The plan assumes year-round road access to Mongu
REALITY: 40-60% of rural roads impassable Nov-Apr
CITATION: Road Development Agency 2025
VERDICT: FATAL
IMPACT: Complete supply chain disruption for 2-6 weeks
"""
        state = _make_state(
            assumption_tree=["fuel cost assumption", "road access assumption"]
        )
        with patch(LLM_CALL, return_value=mock_response):
            with patch(LLM_PARSE) as mock_parse:
                mock_parse.return_value = [
                    {"fracture": "diesel at K20", "reality": "K25.11", "citation": "ERB", "verdict": "MAJOR", "impact": "25%"},
                    {"fracture": "year-round road", "reality": "impassable", "citation": "RDA", "verdict": "FATAL", "impact": "disruption"},
                ]
                result = adversary_critique(state)

        assert result["critique_severity"] == CritiqueSeverity.FATAL.value


class TestProponent:
    def test_fallback_revision(self):
        """Test rule-based fallback revision."""
        state = _make_state(
            critique_history=[{
                "round": 1,
                "critiques": [
                    {"fracture": "fuel cost", "reality": "K25", "citation": "ERB", "verdict": "MAJOR", "impact": "25%"},
                ],
            }],
        )
        with patch(LLM_CALL, side_effect=Exception("No API key")):
            result = proponent_revise(state)

        assert "defense_history" in result
        defenses = result["defense_history"][0]["defenses"]
        assert len(defenses) > 0


class TestJudge:
    def test_fatal_triggers_human(self):
        """FATAL critiques should always trigger human-in-the-loop."""
        state = _make_state(critique_severity=CritiqueSeverity.FATAL.value)
        result = human_judge(state)
        assert result["plan_status"] == PlanStatus.BROKEN.value
        assert result["awaiting_human"] is True

    def test_minor_validates(self):
        """MINOR critiques should validate the plan (fallback)."""
        state = _make_state(critique_severity=CritiqueSeverity.MINOR.value)
        with patch(LLM_CALL, side_effect=Exception("No API")):
            result = human_judge(state)
        assert result["plan_status"] == PlanStatus.VALIDATED.value

    def test_max_revisions_brake(self):
        """Max revisions should force a terminal decision."""
        state = _make_state(
            revision_count=3,
            max_revisions=3,
            critique_severity=CritiqueSeverity.MAJOR.value,
        )
        result = human_judge(state)
        assert result["plan_status"] == PlanStatus.BROKEN.value

    def test_llm_judge_validated(self):
        """Test LLM judge returning VALIDATED."""
        state = _make_state(critique_severity=CritiqueSeverity.MAJOR.value)
        mock_response = "VERDICT: VALIDATED\nREASONING: Defenses hold up.\nKEY_RISKS: None major.\nRECOMMENDATION: Proceed."
        with patch(LLM_CALL, return_value=mock_response):
            result = human_judge(state)
        assert result["plan_status"] == PlanStatus.VALIDATED.value
