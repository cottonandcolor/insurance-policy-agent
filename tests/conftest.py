"""Shared pytest fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.config import ROOT

DEFAULT_POLICY_PATHS = [
    str(ROOT / "data" / "synthetic" / "plan_a.txt"),
    str(ROOT / "data" / "synthetic" / "plan_b.txt"),
]


@pytest.fixture
def policy_paths():
    return DEFAULT_POLICY_PATHS.copy()


@pytest.fixture
def sample_profile():
    return {
        "age": 35,
        "location": "Cedar Park, TX",
        "jurisdiction": "TX",
        "assets": {"home_value": 350_000},
        "existing_coverage": [],
        "risk_factors": ["flood_zone"],
        "flood_zone": True,
        "priority_weights": {
            "coverage_breadth": 0.4,
            "low_cost": 0.3,
            "few_exclusions": 0.3,
        },
    }


@pytest.fixture
def sample_normalized_plan_b():
    return {
        "plan_id": "plan_b",
        "carrier": "Synthetic Shield",
        "dwelling_limit": 350_000,
        "deductible": 5_000,
        "perils": {
            "flood": {"value": "covered up to $100,000 sublimit", "section": "Section IV"},
        },
        "exclusions": [],
        "riders": [],
    }


@pytest.fixture
def mock_llm_responses(sample_profile, sample_normalized_plan_b):
    """Deterministic LLM JSON payloads for live-mode workflow tests."""
    reasoning_branch = {
        "interpretation": "Plan A excludes flood; Plan B covers flood with sublimit",
        "thoughts": [
            {
                "plan_id": "plan_a",
                "scenario_id": "flood",
                "claim": "Plan A pays $0 without HO-FLD",
                "evidence_ids": ["plan_a:2"],
                "payout": 0.0,
                "deductible_applied": 0.0,
            },
            {
                "plan_id": "plan_b",
                "scenario_id": "flood",
                "claim": "Plan B pays sublimit after deductible",
                "evidence_ids": ["plan_b:1"],
                "payout": 95_000.0,
                "deductible_applied": 5_000.0,
            },
        ],
    }
    return {
        "intake": json.dumps(sample_profile),
        "ingest_plan_a": json.dumps(
            {
                "plan_id": "plan_a",
                "carrier": "Synthetic Mutual",
                "dwelling_limit": 350_000,
                "deductible": 2_000,
                "perils": {
                    "flood": {
                        "value": "excluded unless HO-FLD attached",
                        "section": "Section IV-A",
                    },
                },
                "exclusions": [{"value": "flood excluded", "section": "Section VI"}],
                "riders": [],
            }
        ),
        "ingest_plan_b": json.dumps(sample_normalized_plan_b),
        "reasoning": json.dumps([reasoning_branch]),
        "critic": json.dumps(
            [
                {
                    "branch_id": "root-d1-0",
                    "scores": {
                        "grounding": 0.9,
                        "consistency": 0.85,
                        "scenario_completeness": 0.8,
                        "arithmetic_validity": 0.88,
                        "priority_alignment": 0.75,
                    },
                    "composite_score": 0.8,
                    "prune": False,
                    "rationale": "Grounded comparison",
                }
            ]
        ),
        "synthesis": "# Recommendation\n\n**Preferred plan:** plan_b",
    }
