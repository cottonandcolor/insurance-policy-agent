"""Deterministic payout calculator for scenario validation."""

from __future__ import annotations

from src.schemas import NormalizedPlan, Thought


def compute_payout(
    plan: NormalizedPlan,
    scenario_id: str,
    loss_amount: float,
) -> tuple[float, float, str]:
    """
    Returns (payout, deductible_applied, note).
    Uses normalized plan fields only — no LLM.
    """
    deductible = float(plan.deductible or 0)
    limit = float(plan.dwelling_limit or loss_amount)

    peril_info = plan.perils.get(scenario_id)
    if peril_info is None:
        return 0.0, 0.0, f"No peril mapping for {scenario_id}"

    value = str(peril_info.value).lower()
    if "exclude" in value or "not covered" in value:
        return 0.0, 0.0, "Peril excluded"

    capped_loss = min(loss_amount, limit)

    # Handle sublimit phrasing e.g. "covered up to $100,000 sublimit"
    value_raw = str(peril_info.value)
    sublimit = None
    for token in value_raw.replace(",", "").split():
        if token.startswith("$"):
            try:
                sublimit = float(token.replace("$", ""))
            except ValueError:
                pass

    if sublimit is not None:
        capped_loss = min(capped_loss, sublimit)

    payout = max(0.0, capped_loss - deductible)
    return payout, deductible, "Standard deductible applied"
