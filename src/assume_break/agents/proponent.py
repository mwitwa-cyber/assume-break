"""Proponent revision agent using LLM."""

from __future__ import annotations

import warnings
from typing import Any

from assume_break.state import AgentState

PROPONENT_SYSTEM_PROMPT = """\
You are the business plan's proponent and defender. Your role is to respond to adversarial critiques by either:

1. DEFENDING the assumption with evidence, data, or reasoning that the adversary missed
2. ACCEPTING the critique and proposing SPECIFIC, actionable revisions to the plan

For each critique, respond with:

RESPONSE TO: <the fracture/assumption being addressed>
DEFENSE: <your defense argument OR "ACCEPTED — revision needed">
REVISION: <specific change to the business plan, if applicable>
MITIGATION: <risk mitigation strategy>

Be realistic — do not deny valid critiques. The goal is to strengthen the plan, not blindly defend it.
Use data from the Zambian reality context to support your arguments where possible.
Be specific: if you propose changing a number, state the new number. If you propose a new strategy, describe it concretely."""


def _proponent_revise_rule_based(state: AgentState) -> dict:
    """Fallback rule-based proponent revision."""
    critiques = state.get("critique_history", [])
    latest = critiques[-1] if critiques else {"critiques": []}
    items = latest.get("critiques", [])

    defenses: list[dict[str, Any]] = []
    for critique in items:
        verdict = critique.get("verdict", "MINOR")
        fracture = critique.get("fracture", "Unknown")

        if verdict == "FATAL":
            defenses.append({
                "response_to": fracture,
                "defense": "ACCEPTED — this is a critical flaw requiring fundamental plan restructuring.",
                "revision": "Conduct detailed feasibility study addressing this specific risk before proceeding.",
                "mitigation": "Engage local consultants with sector-specific expertise to redesign this component.",
            })
        elif verdict == "MAJOR":
            defenses.append({
                "response_to": fracture,
                "defense": "Partially accepted — the critique identifies a real risk but the impact may be mitigable.",
                "revision": "Revise financial model to incorporate realistic cost assumptions from the cited sources.",
                "mitigation": "Build contingency buffer of 20-30% on affected cost lines and develop alternative supply chains.",
            })
        else:
            defenses.append({
                "response_to": fracture,
                "defense": "Noted — this is a minor optimization opportunity rather than a fundamental flaw.",
                "revision": "No major revision needed; will incorporate into detailed planning phase.",
                "mitigation": "Monitor this factor and adjust operations as needed.",
            })

    return {
        "defense_history": [{"round": state.get("revision_count", 0) + 1, "defenses": defenses}],
    }


def proponent_revise(state: AgentState) -> dict:
    """LangGraph node: defend or revise the business plan against critiques.

    Uses Claude LLM when available, falls back to rule-based revision.
    """
    plan = state.get("business_plan", "")
    critiques = state.get("critique_history", [])
    reality = state.get("reality_context", "")

    latest = critiques[-1] if critiques else {"critiques": []}

    try:
        from assume_break.agents.llm import NoAPIKeyError, call_claude

        user_msg_parts = [
            "ORIGINAL BUSINESS PLAN:",
            plan,
            "\nLATEST ADVERSARIAL CRITIQUES:",
        ]
        for critique in latest.get("critiques", []):
            user_msg_parts.append(f"\nFRACTURE: {critique.get('fracture', '')}")
            user_msg_parts.append(f"REALITY: {critique.get('reality', '')}")
            user_msg_parts.append(f"CITATION: {critique.get('citation', '')}")
            user_msg_parts.append(f"VERDICT: {critique.get('verdict', '')}")
            user_msg_parts.append(f"IMPACT: {critique.get('impact', '')}")

        user_msg_parts.append("\nZAMBIAN REALITY CONTEXT:")
        user_msg_parts.append(reality)

        user_msg_parts.append("\nRespond to each critique. Defend where you can, accept and revise where you must.")

        response = call_claude(
            system_prompt=PROPONENT_SYSTEM_PROMPT,
            user_message="\n".join(user_msg_parts),
        )

        # Parse defense blocks
        import re
        blocks = re.split(r"(?:^|\n)\s*RESPONSE TO\s*:", response, flags=re.IGNORECASE)
        defenses: list[dict[str, Any]] = []

        for block in blocks[1:]:
            defense: dict[str, Any] = {"response_to": ""}
            lines = block.strip().split("\n")
            if lines:
                defense["response_to"] = lines[0].strip()

            block_text = "\n".join(lines)
            for field in ["DEFENSE", "REVISION", "MITIGATION"]:
                pattern = rf"{field}\s*:\s*(.+?)(?=\n\s*(?:DEFENSE|REVISION|MITIGATION|RESPONSE TO)\s*:|\Z)"
                match = re.search(pattern, block_text, re.IGNORECASE | re.DOTALL)
                if match:
                    defense[field.lower()] = match.group(1).strip()

            defenses.append(defense)

        if defenses:
            return {
                "defense_history": [{"round": state.get("revision_count", 0) + 1, "defenses": defenses}],
            }

    except NoAPIKeyError:
        pass  # Expected when no API key — silently use fallback
    except Exception as e:
        warnings.warn(f"LLM proponent failed, falling back to rule-based: {e}", stacklevel=2)

    return _proponent_revise_rule_based(state)
