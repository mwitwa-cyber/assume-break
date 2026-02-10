"""Improved reality retrieval engine with fuzzy matching and category boosting."""

from __future__ import annotations

import re
from difflib import SequenceMatcher

from assume_break.reality.database import ZAMBIAN_REALITY_DATABASE
from assume_break.state import AgentState, RealityFact

# Category keywords for sector detection in business plans
CATEGORY_INDICATORS: dict[str, list[str]] = {
    "TAX": ["tax", "revenue", "turnover", "vat", "income tax", "withholding"],
    "ENERGY": ["fuel", "diesel", "petrol", "electricity", "power", "solar", "energy", "generator"],
    "FINANCE": ["loan", "bank", "interest", "financing", "credit", "lending", "inflation", "exchange rate", "forex", "kwacha"],
    "LOGISTICS": ["transport", "road", "delivery", "logistics", "fleet", "shipping", "cold chain", "warehouse"],
    "MINING": ["mining", "mine", "copper", "cobalt", "mineral", "smelting", "ore", "drill"],
    "AGRICULTURE": ["farm", "agriculture", "maize", "crop", "harvest", "fertilizer", "seed", "livestock", "land"],
    "LABOR": ["employee", "worker", "salary", "wage", "staff", "hire", "payroll", "labour", "labor", "napsa"],
    "IMPORT_EXPORT": ["import", "export", "customs", "tariff", "comesa", "trade", "shipping"],
    "DIGITAL": ["digital", "mobile", "app", "software", "internet", "telecom", "fintech", "data", "online", "e-commerce"],
    "REGISTRATION": ["register", "license", "permit", "pacra", "zema", "certification", "compliance"],
}

# Weights for scoring
EXACT_KEYWORD_WEIGHT = 3.0
FUZZY_KEYWORD_WEIGHT = 1.5
CATEGORY_BOOST_WEIGHT = 2.0
FUZZY_THRESHOLD = 0.65
TOP_K = 10


def _tokenize(text: str) -> list[str]:
    """Extract lowercase tokens from text."""
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text.lower())


def _detect_categories(plan_text: str) -> set[str]:
    """Detect which business categories are relevant to the plan."""
    plan_lower = plan_text.lower()
    detected: set[str] = set()
    for category, indicators in CATEGORY_INDICATORS.items():
        for indicator in indicators:
            if indicator in plan_lower:
                detected.add(category)
                break
    return detected


def _score_fact(fact: RealityFact, plan_tokens: list[str], detected_categories: set[str]) -> float:
    """Score a fact's relevance to the business plan."""
    score = 0.0

    # Exact keyword matches
    for keyword in fact.keywords:
        keyword_lower = keyword.lower()
        for token in plan_tokens:
            if token == keyword_lower:
                score += EXACT_KEYWORD_WEIGHT
                break

    # Fuzzy keyword matches (for partial matches like "logistic" matching "logistics")
    plan_text_joined = " ".join(plan_tokens)
    for keyword in fact.keywords:
        keyword_lower = keyword.lower()
        # Skip if already exact-matched
        if keyword_lower in plan_tokens:
            continue
        # Check fuzzy similarity against plan text substrings
        ratio = SequenceMatcher(None, keyword_lower, plan_text_joined).ratio()
        if ratio >= FUZZY_THRESHOLD:
            score += FUZZY_KEYWORD_WEIGHT
        else:
            # Try matching against individual tokens
            for token in plan_tokens:
                if len(token) >= 4 and len(keyword_lower) >= 4:
                    token_ratio = SequenceMatcher(None, keyword_lower, token).ratio()
                    if token_ratio >= 0.75:
                        score += FUZZY_KEYWORD_WEIGHT * 0.5
                        break

    # Category boost
    if fact.category in detected_categories:
        score += CATEGORY_BOOST_WEIGHT

    return score


def retrieve_relevant_facts(plan_text: str, top_k: int = TOP_K) -> list[tuple[RealityFact, float]]:
    """Retrieve the top-K most relevant facts for a business plan.

    Returns list of (fact, score) tuples sorted by relevance.
    """
    plan_tokens = _tokenize(plan_text)
    detected_categories = _detect_categories(plan_text)

    scored: list[tuple[RealityFact, float]] = []
    for fact in ZAMBIAN_REALITY_DATABASE:
        score = _score_fact(fact, plan_tokens, detected_categories)
        if score > 0:
            scored.append((fact, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def fetch_reality(state: AgentState) -> dict:
    """LangGraph node: retrieve reality context for the business plan.

    Returns dict updates for AgentState with reality_context and reality_citations.
    """
    plan = state.get("business_plan", "")
    results = retrieve_relevant_facts(plan)

    if not results:
        return {
            "reality_context": "No specific Zambian regulatory or economic data matched this business plan. General business regulations still apply.",
            "reality_citations": ["No specific matches found"],
        }

    context_parts: list[str] = []
    citations: list[str] = []

    for i, (fact, score) in enumerate(results, 1):
        context_parts.append(
            f"[{i}] [{fact.category}] {fact.fact} "
            f"(Source: {fact.source}, Effective: {fact.effective_date}, Relevance: {score:.1f})"
        )
        citations.append(f"[{i}] {fact.source} ({fact.effective_date})")

    return {
        "reality_context": "\n\n".join(context_parts),
        "reality_citations": citations,
    }
