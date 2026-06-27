#!/usr/bin/env python3
"""Verify agent_workflow.ipynb logic runs top-to-bottom (dry-run, twice)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from src.config import get_llm_mode_label
from src.notebook_helpers import inspect_workflow
from src.runner import build_user_messages, run_agent_streaming


def run_notebook_flow(*, label: str) -> dict:
    print(f"\n{'=' * 60}\n{label}\n{'=' * 60}")
    print("Model label:", get_llm_mode_label())

    policies = [
        str(ROOT / "data/synthetic/plan_a.txt"),
        str(ROOT / "data/synthetic/plan_b.txt"),
    ]
    messages = build_user_messages(
        age=35,
        location="Cedar Park, TX",
        flood_zone=True,
        coverage_breadth=0.4,
        low_cost=0.3,
        few_exclusions=0.3,
    )

    result = run_agent_streaming(
        policy_paths=policies,
        user_messages=messages,
        dry_run=True,
        beam_width=2,
        max_depth=2,
    )
    assert result.get("final_recommendation"), "missing final_recommendation"
    assert result.get("winning_branch"), "missing winning_branch"
    assert result.get("session_profile"), "missing session_profile"
    assert result.get("normalized_plans"), "missing normalized_plans"
    inspect_workflow(result)

    public_policies = [
        str(ROOT / "data/public/travelers_ho3_nv.txt"),
        str(ROOT / "data/public/statefarm_hw2136_ok.txt"),
    ]
    result_public = run_agent_streaming(
        policy_paths=public_policies,
        user_messages=messages,
        dry_run=True,
        beam_width=2,
        max_depth=2,
    )
    assert result_public.get("final_recommendation"), "public run missing recommendation"
    inspect_workflow(result_public)

    return result


def main() -> int:
    print("Verifying notebook flow (dry-run x2)...")
    run_notebook_flow(label="Pass 1 — synthetic policies")
    run_notebook_flow(label="Pass 2 — repeat synthetic + public policies")
    print("\nOK — notebook flow verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
