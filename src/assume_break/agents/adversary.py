"""The Crucible: adversarial critique agent using LLM."""

from __future__ import annotations

import re
import warnings
from typing import Any

from assume_break.state import AgentState, CritiqueSeverity

ADVERSARY_SYSTEM_PROMPT = """\
You are THE CRUCIBLE — a hostile, adversarial stress-testing engine for business plans operating in Zambia.

Your mandate: FIND EVERY WEAKNESS. You are not helpful. You are not supportive. You are the harsh reality that will destroy poorly-conceived plans BEFORE they waste real capital.

METHODOLOGY:
1. Take each assumption the plan makes
2. Cross-reference it against the REALITY CONTEXT provided (Zambian regulations, economic data, infrastructure facts)
3. Identify where assumptions contradict reality
4. Rate each fracture's severity

OUTPUT FORMAT — For each vulnerability found, output a structured block:

FRACTURE: <The specific flawed assumption>
REALITY: <What the actual Zambian reality is, with specific data>
CITATION: <The source from the reality context>
VERDICT: <FATAL | MAJOR | MINOR>
IMPACT: <Specific financial/operational consequence>

SEVERITY GUIDELINES:
- FATAL: The assumption is so wrong it would likely cause business failure (wrong tax regime, impossible logistics, illegal operation)
- MAJOR: Significant cost/timeline impact that requires plan revision (underestimated costs by >30%, missed regulatory requirements)
- MINOR: Suboptimal but survivable (slightly off on pricing, could optimize tax position)

Be specific. Use numbers from the reality context. Show exact cost impacts where possible. Do not soften your language — founders need harsh truth, not comfort."""


def _adversary_critique_rule_based(state: AgentState) -> dict:
    """Fallback rule-based adversarial critique."""
    assumptions = state.get("assumption_tree", [])
    reality = state.get("reality_context", "")
    reality_lower = reality.lower()

    critiques: list[dict[str, Any]] = []
    max_severity = CritiqueSeverity.NONE

    for assumption in assumptions:
        assumption_lower = assumption.lower()

        if "fuel" in assumption_lower and "k25" in reality_lower:
            sev = CritiqueSeverity.MAJOR
            critiques.append({
                "fracture": assumption,
                "reality": "Diesel is K25.11/litre with 5-8% monthly volatility. Fixed fuel cost assumptions are unreliable.",
                "citation": "ERB Q1 2025 Price Schedule",
                "verdict": sev.value,
                "impact": "Fuel cost variance could erode margins by 5-15% annually.",
            })
        elif "tax" in assumption_lower and "turnover" in reality_lower:
            sev = CritiqueSeverity.MAJOR
            critiques.append({
                "fracture": assumption,
                "reality": "Turnover Tax is 5% on gross revenue with NO deductions. If revenue exceeds ZMW 5M, CIT at 30% applies.",
                "citation": "ZRA 2025 Tax Guide",
                "verdict": sev.value,
                "impact": "Tax miscalculation could increase tax burden by 200-500%.",
            })
        elif "transport" in assumption_lower or "logistics" in assumption_lower or "road" in assumption_lower:
            sev = CritiqueSeverity.FATAL
            critiques.append({
                "fracture": assumption,
                "reality": "40-60% of rural roads are impassable during rainy season (Nov-Apr). La Niña flooding confirmed for 2025.",
                "citation": "Road Development Agency 2025",
                "verdict": sev.value,
                "impact": "Complete supply chain disruption for 2-6 weeks per flood event.",
            })
        elif "financ" in assumption_lower or "loan" in assumption_lower or "bank" in assumption_lower:
            sev = CritiqueSeverity.MAJOR
            critiques.append({
                "fracture": assumption,
                "reality": "SME lending rates are 24-32%, not typical plan assumptions of 10-15%. Collateral requirement is 150-200% of loan value.",
                "citation": "Bankers Association Survey 2025",
                "verdict": sev.value,
                "impact": "Debt servicing costs likely 2-3x higher than projected.",
            })
        elif "margin" in assumption_lower or "profit" in assumption_lower:
            sev = CritiqueSeverity.MAJOR
            critiques.append({
                "fracture": assumption,
                "reality": "With inflation at 11%, fuel volatility of 5-8%, and lending rates of 24-32%, single-digit margins are extremely fragile.",
                "citation": "ZamStats CPI Report + BoZ Policy Rate 2025",
                "verdict": sev.value,
                "impact": "Projected margins may turn negative within 6 months under stress conditions.",
            })
        else:
            sev = CritiqueSeverity.MINOR
            critiques.append({
                "fracture": assumption,
                "reality": "This assumption requires further verification against current Zambian regulatory and economic conditions.",
                "citation": "General regulatory framework",
                "verdict": sev.value,
                "impact": "Potential unquantified risk to business operations.",
            })

        if sev.value == CritiqueSeverity.FATAL.value:
            max_severity = CritiqueSeverity.FATAL
        elif sev.value == CritiqueSeverity.MAJOR.value and max_severity != CritiqueSeverity.FATAL:
            max_severity = CritiqueSeverity.MAJOR
        elif sev.value == CritiqueSeverity.MINOR.value and max_severity == CritiqueSeverity.NONE:
            max_severity = CritiqueSeverity.MINOR

    return {
        "critique_history": [{"round": state.get("revision_count", 0) + 1, "critiques": critiques}],
        "critique_severity": max_severity.value,
        "plan_status": "BROKEN" if max_severity == CritiqueSeverity.FATAL else "UNDER_REVIEW",
    }


def adversary_critique(state: AgentState) -> dict:
    """LangGraph node: adversarial critique of the business plan assumptions.

    Uses Claude LLM when available, falls back to rule-based critique.
    """
    plan = state.get("business_plan", "")
    assumptions = state.get("assumption_tree", [])
    reality = state.get("reality_context", "")
    defense_history = state.get("defense_history", [])

    try:
        from assume_break.agents.llm import NoAPIKeyError, call_claude, parse_structured_response

        user_msg_parts = [
            "BUSINESS PLAN:",
            plan,
            "\nEXTRACTED ASSUMPTIONS:",
        ]
        for i, a in enumerate(assumptions, 1):
            user_msg_parts.append(f"{i}. {a}")

        user_msg_parts.append("\nZAMBIAN REALITY CONTEXT:")
        user_msg_parts.append(reality)

        if defense_history:
            user_msg_parts.append("\nPRIOR DEFENSE HISTORY:")
            for defense in defense_history:
                user_msg_parts.append(str(defense))
            user_msg_parts.append("\nCritique the plan again, accounting for any defenses offered. Find NEW weaknesses or show why defenses are insufficient.")

        response = call_claude(
            system_prompt=ADVERSARY_SYSTEM_PROMPT,
            user_message="\n".join(user_msg_parts),
        )

        # Parse structured blocks
        blocks = parse_structured_response(
            response,
            ["FRACTURE", "REALITY", "CITATION", "VERDICT", "IMPACT"],
        )

        critiques: list[dict[str, Any]] = []
        max_severity = CritiqueSeverity.NONE

        for block in blocks:
            verdict_str = block.get("verdict", "MINOR").upper().strip()
            if "FATAL" in verdict_str:
                sev = CritiqueSeverity.FATAL
            elif "MAJOR" in verdict_str:
                sev = CritiqueSeverity.MAJOR
            else:
                sev = CritiqueSeverity.MINOR

            critiques.append({
                "fracture": block.get("fracture", "Unknown assumption"),
                "reality": block.get("reality", ""),
                "citation": block.get("citation", ""),
                "verdict": sev.value,
                "impact": block.get("impact", ""),
            })

            if sev == CritiqueSeverity.FATAL:
                max_severity = CritiqueSeverity.FATAL
            elif sev == CritiqueSeverity.MAJOR and max_severity != CritiqueSeverity.FATAL:
                max_severity = CritiqueSeverity.MAJOR
            elif sev == CritiqueSeverity.MINOR and max_severity == CritiqueSeverity.NONE:
                max_severity = CritiqueSeverity.MINOR

        if critiques:
            return {
                "critique_history": [{"round": state.get("revision_count", 0) + 1, "critiques": critiques}],
                "critique_severity": max_severity.value,
                "plan_status": "BROKEN" if max_severity == CritiqueSeverity.FATAL else "UNDER_REVIEW",
            }

    except NoAPIKeyError:
        pass  # Expected when no API key — silently use fallback
    except Exception as e:
        warnings.warn(f"LLM adversary failed, falling back to rule-based: {e}", stacklevel=2)

    return _adversary_critique_rule_based(state)
