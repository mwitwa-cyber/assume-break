"""AgentState schema, enums, and dataclasses for the ASSUME-BREAK workflow."""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from enum import Enum
from typing import Annotated, Any, TypedDict


class PlanStatus(str, Enum):
    DRAFT = "DRAFT"
    UNDER_REVIEW = "UNDER_REVIEW"
    BROKEN = "BROKEN"
    VALIDATED = "VALIDATED"
    NEEDS_REVISION = "NEEDS_REVISION"


class CritiqueSeverity(str, Enum):
    FATAL = "FATAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    NONE = "NONE"


@dataclass
class RealityFact:
    category: str
    fact: str
    source: str
    effective_date: str
    keywords: list[str] = field(default_factory=list)


@dataclass
class Critique:
    assumption: str
    reality: str
    citation: str
    verdict: CritiqueSeverity
    impact: str


@dataclass
class StressTestResult:
    plan_status: PlanStatus
    critique_severity: CritiqueSeverity
    assumptions: list[str]
    critiques: list[dict[str, Any]]
    defenses: list[dict[str, Any]]
    reality_citations: list[str]
    revision_count: int
    raw_state: dict[str, Any]


class AgentState(TypedDict):
    business_plan: str
    assumption_tree: list[str]
    reality_context: str
    reality_citations: list[str]
    critique_history: Annotated[list[dict[str, Any]], operator.add]
    defense_history: Annotated[list[dict[str, Any]], operator.add]
    plan_status: str
    critique_severity: str
    revision_count: int
    max_revisions: int
    human_override: str
    awaiting_human: bool
