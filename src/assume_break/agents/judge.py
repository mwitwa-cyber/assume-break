"""Judge agent: evaluates adversarial debate and determines plan verdict."""

from __future__ import annotations

import re
import warnings

from assume_break.state import AgentState, CritiqueSeverity, PlanStatus

JUDGE_SYSTEM_PROMPT = """\
You are a neutral, experienced business judge evaluating an adversarial stress test of a Zambian business plan.

You have observed:
1. The original business plan
2. Extracted assumptions
3. Adversarial critiques (with severity ratings)
4. Proponent defenses and proposed revisions
5. Zambian regulatory and economic reality data

Your task: Determine the overall verdict for this business plan.

VERDICT OPTIONS:
- VALIDATED: The plan's core assumptions hold up. Critiques were either minor or successfully defended. The plan can proceed with minor adjustments.
- NEEDS_REVISION: Significant issues were identified but are fixable. The plan needs another round of revision and re-testing.
- BROKEN: Fatal flaws exist that cannot be reasonably mitigated. The plan's fundamental assumptions are wrong.

Output your assessment as:

VERDICT: <VALIDATED | NEEDS_REVISION | BROKEN>
REASONING: <2-3 sentences explaining your decision>
KEY_RISKS: <Remaining risks even if validated>
RECOMMENDATION: <What the business should do next>

Be fair but rigorous. A plan with unresolved FATAL critiques cannot be VALIDATED.
A plan where all MAJOR critiques have been adequately defended or revised CAN be VALIDATED."""


def human_judge(state: AgentState) -> dict:
    """LangGraph node: judge the adversarial debate and route the workflow.

    Uses Claude LLM when available, falls back to rule-based judgment.
    Preserves human-in-the-loop for FATAL critiques.
    """
    critique_severity = state.get("critique_severity", CritiqueSeverity.NONE.value)
    revision_count = state.get("revision_count", 0)
    max_revisions = state.get("max_revisions", 3)

    # Safety brake: if max revisions reached, force a decision
    if revision_count >= max_revisions:
        if critique_severity == CritiqueSeverity.FATAL.value:
            return {
                "plan_status": PlanStatus.BROKEN.value,
                "human_override": f"Max revisions ({max_revisions}) reached with FATAL issues unresolved.",
                "awaiting_human": True,
            }
        return {
            "plan_status": PlanStatus.BROKEN.value,
            "human_override": f"Max revisions ({max_revisions}) reached. Plan needs external review.",
            "awaiting_human": True,
            "revision_count": revision_count,
        }

    # FATAL critiques always trigger human-in-the-loop
    if critique_severity == CritiqueSeverity.FATAL.value:
        return {
            "plan_status": PlanStatus.BROKEN.value,
            "awaiting_human": True,
            "human_override": "FATAL critique detected — human review required before proceeding.",
            "revision_count": revision_count,
        }

    # Try LLM-assisted judgment for non-FATAL cases
    try:
        from assume_break.agents.llm import NoAPIKeyError, call_claude

        critiques = state.get("critique_history", [])
        defenses = state.get("defense_history", [])
        reality = state.get("reality_context", "")

        user_msg_parts = [
            f"BUSINESS PLAN:\n{state.get('business_plan', '')}",
            f"\nCRITIQUE SEVERITY: {critique_severity}",
            f"\nREVISION ROUND: {revision_count + 1} of {max_revisions}",
            "\nCRITIQUE HISTORY:",
        ]
        for entry in critiques:
            for c in entry.get("critiques", []):
                user_msg_parts.append(f"  - [{c.get('verdict')}] {c.get('fracture')}: {c.get('reality')}")

        user_msg_parts.append("\nDEFENSE HISTORY:")
        for entry in defenses:
            for d in entry.get("defenses", []):
                user_msg_parts.append(f"  - RE: {d.get('response_to')}: {d.get('defense', '')}")

        user_msg_parts.append(f"\nREALITY CONTEXT:\n{reality}")
        user_msg_parts.append("\nProvide your verdict.")

        response = call_claude(
            system_prompt=JUDGE_SYSTEM_PROMPT,
            user_message="\n".join(user_msg_parts),
        )

        # Parse verdict
        verdict_match = re.search(r"VERDICT\s*:\s*(VALIDATED|NEEDS_REVISION|BROKEN)", response, re.IGNORECASE)
        if verdict_match:
            verdict = verdict_match.group(1).upper()
            if verdict == "VALIDATED":
                return {
                    "plan_status": PlanStatus.VALIDATED.value,
                    "awaiting_human": False,
                    "revision_count": revision_count,
                }
            elif verdict == "BROKEN":
                return {
                    "plan_status": PlanStatus.BROKEN.value,
                    "awaiting_human": True,
                    "human_override": response,
                    "revision_count": revision_count,
                }
            else:  # NEEDS_REVISION
                return {
                    "plan_status": PlanStatus.NEEDS_REVISION.value,
                    "awaiting_human": False,
                    "revision_count": revision_count + 1,
                }

    except NoAPIKeyError:
        pass  # Expected when no API key — silently use fallback
    except Exception as e:
        warnings.warn(f"LLM judge failed, falling back to rule-based: {e}", stacklevel=2)

    # Fallback rule-based judgment
    if critique_severity == CritiqueSeverity.MINOR.value:
        return {
            "plan_status": PlanStatus.VALIDATED.value,
            "awaiting_human": False,
            "revision_count": revision_count,
        }

    # MAJOR → needs revision
    return {
        "plan_status": PlanStatus.NEEDS_REVISION.value,
        "awaiting_human": False,
        "revision_count": revision_count + 1,
    }
