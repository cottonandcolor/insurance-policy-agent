"""Pydantic schemas for structured agent I/O."""

from __future__ import annotations

from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, model_validator


class PriorityWeights(BaseModel):
    coverage_breadth: float = Field(ge=0, le=1)
    low_cost: float = Field(ge=0, le=1)
    few_exclusions: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def check_sum(self) -> "PriorityWeights":
        total = self.coverage_breadth + self.low_cost + self.few_exclusions
        if abs(total - 1.0) > 0.05:
            raise ValueError("priority weights must sum to ~1.0")
        return self


class UserProfile(BaseModel):
    age: int
    location: str
    jurisdiction: str = "TX"
    assets: Dict[str, Union[float, int, str]] = Field(default_factory=dict)
    existing_coverage: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)
    priority_weights: PriorityWeights
    flood_zone: bool = False


class CitationField(BaseModel):
    value: Union[str, float, int, bool, List[str]]
    section: str


class NormalizedPlan(BaseModel):
    plan_id: str
    carrier: str = "Synthetic Carrier"
    dwelling_limit: Optional[float] = None
    deductible: Optional[float] = None
    perils: Dict[str, CitationField] = Field(default_factory=dict)
    exclusions: List[CitationField] = Field(default_factory=list)
    riders: List[CitationField] = Field(default_factory=list)


class Thought(BaseModel):
    plan_id: str
    scenario_id: str
    claim: str
    evidence_ids: List[str] = Field(default_factory=list)
    payout: Optional[float] = None
    deductible_applied: Optional[float] = None


class ReasoningBranch(BaseModel):
    branch_id: Optional[str] = None
    interpretation: str
    thoughts: List[Thought] = Field(default_factory=list)


class BranchScores(BaseModel):
    grounding: float = Field(ge=0, le=1)
    consistency: float = Field(ge=0, le=1)
    scenario_completeness: float = Field(ge=0, le=1)
    arithmetic_validity: float = Field(ge=0, le=1)
    priority_alignment: float = Field(ge=0, le=1)


class CriticEvaluation(BaseModel):
    branch_id: str
    scores: BranchScores
    composite_score: float = Field(ge=0, le=1)
    prune: bool
    rationale: str = ""


class RetrievedChunk(BaseModel):
    chunk_id: str
    plan_id: str
    section: str
    jurisdiction: str
    text: str
    peril_tags: List[str] = Field(default_factory=list)
