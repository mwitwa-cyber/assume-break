"""Unit tests for the reality retrieval engine."""

from __future__ import annotations

from assume_break.reality.database import ZAMBIAN_REALITY_DATABASE
from assume_break.reality.engine import (
    _detect_categories,
    _score_fact,
    _tokenize,
    fetch_reality,
    retrieve_relevant_facts,
)
from assume_break.state import RealityFact


class TestTokenize:
    def test_basic(self):
        tokens = _tokenize("Hello World 123")
        assert "hello" in tokens
        assert "world" in tokens
        assert "123" in tokens

    def test_empty(self):
        assert _tokenize("") == []

    def test_special_chars(self):
        tokens = _tokenize("ZMW 5,000,000 @ 5%")
        assert "zmw" in tokens
        assert "5" in tokens


class TestDetectCategories:
    def test_mining(self):
        cats = _detect_categories("We plan to start a copper mining operation")
        assert "MINING" in cats

    def test_agriculture(self):
        cats = _detect_categories("Our farm will grow maize and export it")
        assert "AGRICULTURE" in cats

    def test_multiple(self):
        cats = _detect_categories("Transport fuel costs for farm logistics")
        assert "ENERGY" in cats
        assert "LOGISTICS" in cats
        assert "AGRICULTURE" in cats

    def test_no_match(self):
        cats = _detect_categories("this is a generic sentence")
        assert len(cats) == 0


class TestScoreFact:
    def test_exact_keyword_match(self):
        fact = RealityFact(
            category="TAX",
            fact="Test fact",
            source="Test",
            effective_date="2025-01-01",
            keywords=["turnover", "tax"],
        )
        tokens = _tokenize("We pay turnover tax on revenue")
        score = _score_fact(fact, tokens, set())
        assert score > 0

    def test_category_boost(self):
        fact = RealityFact(
            category="MINING",
            fact="Test mining fact",
            source="Test",
            effective_date="2025-01-01",
            keywords=["royalty"],
        )
        tokens = _tokenize("royalty calculation")
        score_no_boost = _score_fact(fact, tokens, set())
        score_with_boost = _score_fact(fact, tokens, {"MINING"})
        assert score_with_boost > score_no_boost

    def test_no_match_zero_score(self):
        fact = RealityFact(
            category="TAX",
            fact="Test fact",
            source="Test",
            effective_date="2025-01-01",
            keywords=["completely", "unrelated"],
        )
        tokens = _tokenize("mining copper cobalt")
        score = _score_fact(fact, tokens, set())
        assert score == 0


class TestRetrieveRelevantFacts:
    def test_returns_results(self):
        results = retrieve_relevant_facts("We plan to start a copper mining operation in Zambia")
        assert len(results) > 0
        assert all(isinstance(r[0], RealityFact) for r in results)
        assert all(isinstance(r[1], float) for r in results)

    def test_sorted_by_relevance(self):
        results = retrieve_relevant_facts("diesel fuel costs for transport logistics")
        scores = [r[1] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_empty_plan(self):
        results = retrieve_relevant_facts("")
        assert results == []

    def test_no_matches(self):
        results = retrieve_relevant_facts("xyzzyplugh nothing here")
        assert results == []

    def test_top_k_limit(self):
        results = retrieve_relevant_facts(
            "tax fuel mining logistics agriculture labor import digital registration",
            top_k=5,
        )
        assert len(results) <= 5

    def test_mining_returns_mining_facts(self):
        results = retrieve_relevant_facts("copper mining operation mineral royalty")
        categories = [r[0].category for r in results]
        assert "MINING" in categories


class TestFetchReality:
    def test_returns_dict(self):
        state = {"business_plan": "diesel transport logistics from Lusaka"}
        result = fetch_reality(state)
        assert "reality_context" in result
        assert "reality_citations" in result
        assert isinstance(result["reality_context"], str)
        assert isinstance(result["reality_citations"], list)

    def test_no_match_fallback(self):
        state = {"business_plan": ""}
        result = fetch_reality(state)
        assert "No specific" in result["reality_context"]

    def test_citations_populated(self):
        state = {"business_plan": "We need a loan from the bank to buy mining equipment"}
        result = fetch_reality(state)
        assert len(result["reality_citations"]) > 0


class TestDatabaseCompleteness:
    def test_minimum_facts(self):
        assert len(ZAMBIAN_REALITY_DATABASE) >= 40

    def test_all_categories_present(self):
        categories = {f.category for f in ZAMBIAN_REALITY_DATABASE}
        expected = {"TAX", "ENERGY", "FINANCE", "LOGISTICS", "MINING", "AGRICULTURE", "LABOR", "IMPORT_EXPORT", "DIGITAL", "REGISTRATION"}
        assert expected.issubset(categories)

    def test_all_facts_have_keywords(self):
        for fact in ZAMBIAN_REALITY_DATABASE:
            assert len(fact.keywords) > 0, f"Fact missing keywords: {fact.fact[:50]}"
