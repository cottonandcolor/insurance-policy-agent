import pytest

from src.tools.chunking import chunk_policy_file
from src.tools.payout import compute_payout
from src.schemas import NormalizedPlan, CitationField, Thought
from src.tools.validators import apply_hard_gates, should_prune
from src.graph.routing import should_continue_tot
from src.config import ROOT


def test_chunk_policy_plan_a():
    chunks = chunk_policy_file(ROOT / "data" / "synthetic" / "plan_a.txt")
    assert len(chunks) >= 3
    assert any("flood" in c.peril_tags for c in chunks)


def test_payout_plan_b_flood_sublimit():
    plan = NormalizedPlan(
        plan_id="plan_b",
        dwelling_limit=350_000,
        deductible=5_000,
        perils={"flood": CitationField(value="covered up to $100,000 sublimit", section="IV")},
    )
    payout, ded, _ = compute_payout(plan, "flood", 150_000)
    assert ded == 5_000
    assert payout == 95_000


def test_hard_gate_missing_citation():
    branch = {
        "branch_id": "b1",
        "thoughts": [
            {
                "plan_id": "plan_a",
                "scenario_id": "flood",
                "claim": "no cite",
                "evidence_ids": [],
                "payout": 0,
            }
        ],
    }
    plans = {
        "plan_a": NormalizedPlan(plan_id="plan_a", deductible=2000, dwelling_limit=350000),
    }
    gated = apply_hard_gates(branch, plans)
    assert gated["hard_gate_failed"] is True


def test_should_prune_respects_hard_gate():
    assert should_prune(0.9, 1, hard_gate_failed=True) is True
    assert should_prune(0.9, 1, hard_gate_failed=False) is False
    assert should_prune(0.4, 1, hard_gate_failed=False) is True


def test_routing_to_synthesize_on_error():
    assert should_continue_tot({"error": "fail", "active_branches": [{}]}) == "synthesize"


def test_routing_continue_when_branches_exist():
    assert should_continue_tot({"depth": 2, "max_depth": 4, "active_branches": [{"branch_id": "x"}]}) == "expand"
