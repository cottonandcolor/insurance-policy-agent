"""Hard gates from capstone design — run before critic soft scoring."""

from __future__ import annotations

from src.config import PRUNE_THRESHOLD_EARLY, PRUNE_THRESHOLD_LATE
from src.schemas import CriticEvaluation, Thought
from src.tools.payout import compute_payout
from src.schemas import NormalizedPlan


def has_citations(thought: Thought) -> bool:
    return len(thought.evidence_ids) >= 1


def hard_gate_thought(thought: Thought) -> list[str]:
    failures: list[str] = []
    if not thought.claim.strip():
        failures.append("empty claim")
    if not has_citations(thought):
        failures.append("missing citation")
    if thought.payout is not None and thought.payout < 0:
        failures.append("negative payout")
    return failures


def apply_hard_gates(
    branch: dict,
    plans_by_id: dict[str, NormalizedPlan],
    loss_amount: float = 150_000.0,
) -> dict:
    """Augment branch with hard_gate_failures and auto-prune flag."""
    failures: list[str] = []
    for raw in branch.get("thoughts", []):
        try:
            thought = Thought.model_validate(raw)
        except Exception:
            failures.append("invalid thought schema")
            continue
        failures.extend(hard_gate_thought(thought))

        plan = plans_by_id.get(thought.plan_id)
        if plan and thought.payout is not None:
            expected, ded, _ = compute_payout(plan, thought.scenario_id, loss_amount)
            if abs(expected - thought.payout) > 500:
                failures.append(
                    f"arithmetic mismatch on {thought.plan_id}: "
                    f"expected ~{expected:.0f}, got {thought.payout:.0f}"
                )

    branch["hard_gate_failures"] = failures
    branch["hard_gate_failed"] = len(failures) > 0
    return branch


def prune_threshold_for_depth(depth: int) -> float:
    return PRUNE_THRESHOLD_LATE if depth >= 3 else PRUNE_THRESHOLD_EARLY


def should_prune(composite: float, depth: int, hard_gate_failed: bool) -> bool:
    if hard_gate_failed:
        return True
    return composite < prune_threshold_for_depth(depth)
