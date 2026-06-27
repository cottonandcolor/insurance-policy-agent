"""Prompt templates for live LLM agent steps."""

from __future__ import annotations

import json

from src.tools.policy_text import excerpt_for_ingest


def intake_prompt(user_messages: list[str]) -> tuple[str, str]:
    system = (
        "You are a Profile Intake Specialist. Collect user age, location, assets, "
        "existing coverage, flood-zone risk, and priority weights. Output ONLY valid JSON."
    )
    user = (
        "Parse user messages into JSON with keys: age, location, jurisdiction, assets, "
        "existing_coverage, risk_factors, flood_zone, priority_weights "
        "(coverage_breadth, low_cost, few_exclusions summing to 1.0).\n\n"
        f"Messages:\n{json.dumps(user_messages, indent=2)}\n\n"
        "Return a single JSON object only, no markdown."
    )
    return system, user


def ingest_prompt(policy_text: str, plan_id: str) -> tuple[str, str]:
    system = (
        "You are a Document and Retrieval Analyst. Extract coverage limits, deductibles, "
        "exclusions, and riders from policy text. Output ONLY valid JSON."
    )
    user = (
        f"Normalize plan_id={plan_id}. Return JSON with: plan_id, carrier, "
        "dwelling_limit, deductible, perils (map of peril -> {value, section}), "
        "exclusions (list of {value, section}), riders (list of {value, section}).\n\n"
        f"Policy:\n{excerpt_for_ingest(policy_text)}\n\n"
        "Include perils.flood (or note exclusion). Return a single JSON object only."
    )
    return system, user


def reasoning_prompt(context: dict, depth: int) -> tuple[str, str]:
    plans = context.get("plans") or []
    plan_ids = [p.get("plan_id") for p in plans if p.get("plan_id")]
    system = (
        "You are a Scenario Reasoning Analyst. Generate alternative interpretation branches "
        "with flood scenario thoughts using evidence only. Output ONLY valid JSON."
    )
    user = (
        f"Depth {depth}. Return JSON array (max 3 items). Each item: "
        "{interpretation, thoughts:[{plan_id, scenario_id, claim, evidence_ids, payout, deductible_applied}]}.\n\n"
        f"IMPORTANT: use these exact plan_id values in every thought: {plan_ids}. "
        "Do NOT use plan_a or plan_b unless those are the actual plan_id values.\n"
        "Set scenario_id to 'flood'. Leave evidence_ids as [] — retrieval will fill them.\n"
        "Set payout and deductible_applied from normalized plan peril data.\n\n"
        f"Context:\n{json.dumps(context, default=str)[:8000]}\n\n"
        "Return a JSON array of branch proposals only."
    )
    return system, user


def critic_prompt(branches: list[dict], profile: dict) -> tuple[str, str]:
    branch_summaries = [
        {
            "branch_id": b.get("branch_id"),
            "interpretation": b.get("interpretation"),
            "thoughts": b.get("thoughts", []),
            "hard_gate_failed": b.get("hard_gate_failed", False),
        }
        for b in branches
    ]
    system = (
        "You are a Policy Critic. Score branches adversarially and reject uncited claims. "
        "Output ONLY valid JSON."
    )
    user = (
        "Evaluate each branch. Return JSON array with one object per branch_id: "
        "{branch_id, scores:{grounding, consistency, scenario_completeness, "
        "arithmetic_validity, priority_alignment}, composite_score, prune, rationale}.\n\n"
        f"Profile:\n{json.dumps(profile)}\n\n"
        f"Branches:\n{json.dumps(branch_summaries, default=str)[:8000]}\n\n"
        "Evaluate EVERY branch listed. Use the exact branch_id values provided. "
        "composite_score should be 0.55–0.95 for grounded branches. "
        "Return a JSON array of evaluations only."
    )
    return system, user


def synthesize_prompt(winning_branch: dict, plans: list[dict]) -> tuple[str, str]:
    system = (
        "You are a Recommendation Synthesizer. Produce a consumer-facing markdown comparison "
        "and recommendation from the validated branch only. Do not invent new coverage claims."
    )
    user = (
        "Write markdown with: comparison table, recommended plan, tradeoffs, citations.\n\n"
        f"Winning branch:\n{json.dumps(winning_branch, default=str)}\n\n"
        f"Plans:\n{json.dumps(plans, default=str)[:6000]}"
    )
    return system, user
