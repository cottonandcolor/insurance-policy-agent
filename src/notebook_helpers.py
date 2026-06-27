"""Helpers for Jupyter notebook workflow inspection."""

from __future__ import annotations

import json
from pprint import pprint


def inspect_workflow(state: dict) -> None:
    """Print session profile, plans, branches, and winning branch summary."""
    print("=" * 60)
    print("SESSION PROFILE (intake agent)")
    print("=" * 60)
    pprint(state.get("session_profile", {}))

    print("\n" + "=" * 60)
    print("INDEX & PLANS")
    print("=" * 60)
    print("Indexed chunks:", state.get("indexed_chunks"))
    for plan in state.get("normalized_plans", []):
        pid = plan.get("plan_id", "?")
        carrier = plan.get("carrier", "unknown")
        premium = plan.get("annual_premium")
        print(f"  · {pid}: carrier={carrier}, premium={premium}")

    branches = state.get("active_branches") or []
    if state.get("winning_branch"):
        winner_id = state["winning_branch"].get("branch_id")
        branches = [state["winning_branch"]] + [
            b for b in branches if b.get("branch_id") != winner_id
        ]

    print("\n" + "=" * 60)
    print("BRANCHES (Tree-of-Thought)")
    print("=" * 60)
    if not branches:
        print("  (no branches in final state)")
    for b in branches:
        winner = state.get("winning_branch", {}).get("branch_id") == b.get("branch_id")
        tag = " ★ WINNER" if winner else ""
        pruned = " [PRUNED]" if b.get("pruned") else ""
        hard = " [HARD GATE FAIL]" if b.get("hard_gate_failed") else ""
        print(
            f"\n  {b.get('branch_id')}{tag}{pruned}{hard}"
            f"  depth={b.get('depth')}  score={b.get('composite_score', 0):.3f}"
        )
        if b.get("interpretation"):
            print(f"    interpretation: {b['interpretation'][:120]}")
        if b.get("rationale"):
            print(f"    rationale: {b['rationale'][:160]}")
        scores = b.get("scores") or {}
        if scores:
            print("    scores:", json.dumps(scores, indent=6))
        for i, thought in enumerate(b.get("thoughts") or [], 1):
            claim = (thought.get("claim") or "")[:80]
            payout = thought.get("payout")
            print(
                f"    thought {i}: plan={thought.get('plan_id')} "
                f"scenario={thought.get('scenario_id')} payout={payout} — {claim}"
            )

    wb = state.get("winning_branch")
    if wb:
        print("\n" + "=" * 60)
        print("WINNING BRANCH SUMMARY")
        print("=" * 60)
        print(f"  id: {wb.get('branch_id')}")
        print(f"  composite_score: {wb.get('composite_score')}")
        print(f"  rationale: {wb.get('rationale', '')[:200]}")
