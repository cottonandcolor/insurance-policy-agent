"""Deterministic responses when --dry-run is set (no API key needed)."""

from __future__ import annotations

import json
from pathlib import Path

from src.schemas import NormalizedPlan, CitationField, UserProfile, PriorityWeights


def mock_profile(user_messages: list[str]) -> dict:
    profile = UserProfile(
        age=35,
        location="Cedar Park, TX",
        jurisdiction="TX",
        assets={"home_value": 350_000},
        existing_coverage=[],
        risk_factors=["flood_zone"],
        flood_zone=True,
        priority_weights=PriorityWeights(
            coverage_breadth=0.4,
            low_cost=0.3,
            few_exclusions=0.3,
        ),
    )
    return profile.model_dump()


def mock_normalized_plan(path: Path) -> dict:
    plan_id = path.stem
    text = path.read_text(encoding="utf-8").lower()

    if plan_id == "plan_a":
        plan = NormalizedPlan(
            plan_id=plan_id,
            carrier="Synthetic Mutual",
            dwelling_limit=350_000,
            deductible=2_000,
            perils={
                "flood": CitationField(value="excluded unless HO-FLD attached", section="Section IV-A"),
                "water_backup": CitationField(value="covered up to $10,000", section="Section IV"),
            },
            exclusions=[
                CitationField(value="flood and surface water excluded", section="Section VI"),
            ],
            riders=[
                CitationField(value="HO-FLD optional flood endorsement", section="Section VIII"),
            ],
        )
    else:
        plan = NormalizedPlan(
            plan_id=plan_id,
            carrier="Synthetic Shield",
            dwelling_limit=350_000,
            deductible=5_000,
            perils={
                "flood": CitationField(value="covered up to $100,000 sublimit", section="Section IV"),
                "water_backup": CitationField(value="plumbing water damage covered", section="Section IV"),
            },
            exclusions=[
                CitationField(value="named storm surge in coastal zones", section="Section VI"),
            ],
        )
    return plan.model_dump()


def mock_reasoning_branches(depth: int, profile: dict, plans: list[dict]) -> list[dict]:
    loss = 150_000
    branches = [
        {
            "interpretation": "Plan A excludes flood without HO-FLD; Plan B covers flood with sublimit",
            "thoughts": [
                {
                    "plan_id": "plan_a",
                    "scenario_id": "flood",
                    "claim": "Plan A pays $0 for flood without HO-FLD endorsement",
                    "evidence_ids": ["plan_a:2"],
                    "payout": 0.0,
                    "deductible_applied": 0.0,
                },
                {
                    "plan_id": "plan_b",
                    "scenario_id": "flood",
                    "claim": f"Plan B pays ${min(100_000, loss) - 5000} after $5K deductible on $100K sublimit",
                    "evidence_ids": ["plan_b:1"],
                    "payout": 95_000.0,
                    "deductible_applied": 5_000.0,
                },
            ],
        },
        {
            "interpretation": "Plan A flood covered if HO-FLD purchased; Plan B base flood applies",
            "thoughts": [
                {
                    "plan_id": "plan_a",
                    "scenario_id": "flood",
                    "claim": "With HO-FLD, Plan A pays $148K after $2K deductible",
                    "evidence_ids": ["plan_a:4"],
                    "payout": 148_000.0,
                    "deductible_applied": 2_000.0,
                },
                {
                    "plan_id": "plan_b",
                    "scenario_id": "flood",
                    "claim": "Plan B pays $95K on flood sublimit scenario",
                    "evidence_ids": ["plan_b:1"],
                    "payout": 95_000.0,
                    "deductible_applied": 5_000.0,
                },
            ],
        },
        {
            "interpretation": "Conservative reading — both plans partial flood coverage",
            "thoughts": [
                {
                    "plan_id": "plan_a",
                    "scenario_id": "flood",
                    "claim": "Plan A base form excludes flood",
                    "evidence_ids": ["plan_a:3"],
                    "payout": 0.0,
                    "deductible_applied": 0.0,
                },
                {
                    "plan_id": "plan_b",
                    "scenario_id": "flood",
                    "claim": "Plan B limited to sublimit",
                    "evidence_ids": ["plan_b:1"],
                    "payout": 95_000.0,
                    "deductible_applied": 5_000.0,
                },
            ],
        },
    ]
    return branches[:3]


def mock_critic_evaluations(branches: list[dict], depth: int) -> list[dict]:
    results = []
    for branch in branches:
        hard_failed = branch.get("hard_gate_failed", False)
        composite = 0.45 if hard_failed else 0.72 + (0.05 if "HO-FLD" in branch.get("interpretation", "") else 0)
        composite = min(composite, 0.95)
        results.append(
            {
                "branch_id": branch["branch_id"],
                "scores": {
                    "grounding": 0.0 if hard_failed else 0.9,
                    "consistency": 0.85,
                    "scenario_completeness": 0.8,
                    "arithmetic_validity": 0.0 if hard_failed else 0.88,
                    "priority_alignment": 0.75,
                },
                "composite_score": composite,
                "prune": hard_failed or composite < 0.55,
                "rationale": "Hard gate failure" if hard_failed else "Grounded flood scenario comparison",
            }
        )
    return results


def mock_synthesis(winning_branch: dict, plans: list[dict]) -> str:
    return f"""# Insurance Recommendation (Synthetic Dry Run)

## Comparison — $150K Flood Loss Scenario

| Plan | Flood Payout | Key Tradeoff |
|------|-------------|--------------|
| plan_a | See winning branch | Lower premium; flood requires HO-FLD |
| plan_b | See winning branch | Higher sublimit coverage in base form |

## Recommendation
**Preferred plan:** plan_b for flood-zone profile without optional endorsements.

## Winning interpretation
{winning_branch.get('interpretation', 'N/A')}

## Citations
Evidence IDs: {json.dumps([t.get('evidence_ids') for t in winning_branch.get('thoughts', [])])}
"""
