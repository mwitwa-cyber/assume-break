"""Assumption extraction agent using LLM."""

from __future__ import annotations

import re
import warnings

from assume_break.state import AgentState

EXTRACTOR_SYSTEM_PROMPT = """\
You are a strategic business analyst specializing in decomposing business plans into testable assumptions.

Your task: Given a business plan, extract 5-10 specific, testable assumptions that the plan relies on. Each assumption should be a concrete claim that can be verified or challenged against real-world data.

Categorize each assumption into one of these categories:
- Financial: Revenue projections, cost assumptions, margins, pricing, funding
- Operational: Logistics, supply chain, staffing, infrastructure, technology
- Market: Customer demand, competition, market size, growth rates
- Regulatory: Licensing, tax obligations, compliance, permits, legal requirements
- Environmental: Weather, climate, geographic, seasonal factors

Format each assumption as:
[CATEGORY] ASSUMPTION: <specific testable statement>

Example:
[Financial] ASSUMPTION: The business can achieve 8% net profit margins within the first year of operation.
[Operational] ASSUMPTION: Diesel fuel costs will remain below K22 per litre throughout the planning period.
[Regulatory] ASSUMPTION: The business qualifies for Turnover Tax at 5% rather than Corporate Income Tax.

Be specific and quantitative where the plan provides numbers. If the plan makes implicit assumptions, make them explicit."""


def _extract_assumptions_rule_based(plan: str) -> list[str]:
    """Fallback rule-based assumption extraction."""
    assumptions: list[str] = []
    plan_lower = plan.lower()

    if any(w in plan_lower for w in ["revenue", "income", "turnover", "sales", "zmw"]):
        assumptions.append("[Financial] ASSUMPTION: Revenue projections are achievable given current market conditions and tax obligations.")
    if any(w in plan_lower for w in ["loan", "bank", "financing", "credit", "borrow"]):
        assumptions.append("[Financial] ASSUMPTION: Bank financing is available at the assumed interest rate and terms.")
    if any(w in plan_lower for w in ["diesel", "fuel", "petrol", "energy"]):
        assumptions.append("[Operational] ASSUMPTION: Fuel costs will remain stable at the assumed price level.")
    if any(w in plan_lower for w in ["transport", "delivery", "logistics", "fleet", "road"]):
        assumptions.append("[Operational] ASSUMPTION: Transport routes will remain passable year-round without significant disruption.")
    if any(w in plan_lower for w in ["tax", "vat", "turnover tax"]):
        assumptions.append("[Regulatory] ASSUMPTION: The business qualifies for the assumed tax regime and rates.")
    if any(w in plan_lower for w in ["farm", "agriculture", "crop", "harvest", "maize"]):
        assumptions.append("[Market] ASSUMPTION: Agricultural commodity prices will meet the projected levels.")
    if any(w in plan_lower for w in ["mine", "mining", "copper", "mineral"]):
        assumptions.append("[Regulatory] ASSUMPTION: Mining licenses and permits can be obtained within the projected timeline.")
    if any(w in plan_lower for w in ["employee", "staff", "worker", "hire", "salary"]):
        assumptions.append("[Operational] ASSUMPTION: Labor costs align with the assumed wage levels and statutory contributions are accounted for.")
    if any(w in plan_lower for w in ["import", "export", "customs"]):
        assumptions.append("[Regulatory] ASSUMPTION: Import/export duties and fees are correctly estimated in the financial model.")
    if any(w in plan_lower for w in ["app", "digital", "online", "mobile", "software"]):
        assumptions.append("[Regulatory] ASSUMPTION: All digital/telecom licensing and data protection requirements are met.")
    if any(w in plan_lower for w in ["property", "land", "building", "premises"]):
        assumptions.append("[Financial] ASSUMPTION: Property costs (rent/purchase/transfer) match the assumed levels.")
    if any(w in plan_lower for w in ["western", "northern", "rural", "province"]):
        assumptions.append("[Environmental] ASSUMPTION: Geographic and seasonal conditions will not materially impact operations.")
    if any(w in plan_lower for w in ["margin", "profit", "net"]):
        assumptions.append("[Financial] ASSUMPTION: Projected profit margins are achievable after accounting for all costs and regulatory burdens.")

    if not assumptions:
        assumptions.append("[Financial] ASSUMPTION: The business plan's financial projections are realistic given Zambian market conditions.")
        assumptions.append("[Regulatory] ASSUMPTION: All necessary licenses, permits, and regulatory requirements have been identified.")

    return assumptions


def extract_assumptions(state: AgentState) -> dict:
    """LangGraph node: extract testable assumptions from the business plan.

    Uses Claude LLM when available, falls back to rule-based extraction.
    """
    plan = state.get("business_plan", "")

    try:
        from assume_break.agents.llm import NoAPIKeyError, call_claude

        response = call_claude(
            system_prompt=EXTRACTOR_SYSTEM_PROMPT,
            user_message=f"Extract the key testable assumptions from this Zambian business plan:\n\n{plan}",
        )

        # Parse assumptions from response
        assumptions: list[str] = []
        for line in response.strip().split("\n"):
            line = line.strip()
            if re.match(r"\[(?:Financial|Operational|Market|Regulatory|Environmental)\]\s*ASSUMPTION:", line, re.IGNORECASE):
                assumptions.append(line)

        if assumptions:
            return {
                "assumption_tree": assumptions,
                "plan_status": "UNDER_REVIEW",
            }

    except NoAPIKeyError:
        pass  # Expected when no API key — silently use fallback
    except Exception as e:
        warnings.warn(f"LLM extraction failed, falling back to rule-based: {e}", stacklevel=2)

    # Fallback
    return {
        "assumption_tree": _extract_assumptions_rule_based(plan),
        "plan_status": "UNDER_REVIEW",
    }
