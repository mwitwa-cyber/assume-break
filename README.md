# ASSUME-BREAK

Adversarial business plan stress-testing against Zambian 2025-2026 economic realities.

ASSUME-BREAK uses an adversarial multi-agent workflow to decompose business plans into testable assumptions, cross-reference them against a comprehensive Zambian regulatory and economic database, and surface fatal flaws before real capital is deployed.

## Quick Start

```bash
pip install -e ".[dev]"
```

Create a `.env` file from the template (optional — works without API key using rule-based fallback):

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## CLI Usage

```bash
# Stress test a business plan
assume-break test "We plan to start a copper mining operation..."

# From file
assume-break test --file business_plan.txt

# Interactive mode
assume-break test --interactive

# List reality database facts
assume-break facts
assume-break facts --category MINING

# Export results to JSON
assume-break test "My plan..." --export results.json
```

## Web UI

```bash
streamlit run streamlit_app.py
```

## Architecture

The system uses a LangGraph state machine with four agent nodes:

1. **Extractor** — Decomposes business plans into testable assumptions
2. **Adversary (The Crucible)** — Attacks each assumption against Zambian reality data
3. **Proponent** — Defends or revises the plan against critiques
4. **Judge** — Evaluates the debate and determines the verdict

Each agent uses Claude LLM when an API key is configured, with rule-based fallbacks for offline use.

## Reality Database

40+ ground-truth facts across 10 categories: TAX, ENERGY, FINANCE, LOGISTICS, MINING, AGRICULTURE, LABOR, IMPORT/EXPORT, DIGITAL, REGISTRATION.

## Tests

```bash
pytest tests/ -v
```
