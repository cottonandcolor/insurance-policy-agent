"""CrewAI tasks with explicit JSON output instructions."""

from __future__ import annotations

import json

from crewai import Task

from src.crews.agents import (
    document_retrieval_agent,
    policy_critic_agent,
    profile_intake_agent,
    recommendation_synthesizer_agent,
    scenario_reasoning_agent,
)


def intake_task(user_messages: list[str]) -> Task:
    return Task(
        description=(
            "Parse user messages into JSON with keys: age, location, jurisdiction, assets, "
            "existing_coverage, risk_factors, flood_zone, priority_weights "
            "(coverage_breadth, low_cost, few_exclusions summing to 1.0).\n\n"
            f"Messages:\n{json.dumps(user_messages, indent=2)}"
        ),
        expected_output="Single JSON object only, no markdown.",
        agent=profile_intake_agent(),
    )


def ingest_task(policy_text: str, plan_id: str) -> Task:
    return Task(
        description=(
            f"Normalize plan_id={plan_id}. Return JSON with: plan_id, carrier, "
            "dwelling_limit, deductible, perils (map of peril -> {{value, section}}), "
            "exclusions (list of {{value, section}}), riders (list of {{value, section}}).\n\n"
            f"Policy:\n{policy_text[:10000]}"
        ),
        expected_output="Single JSON object only.",
        agent=document_retrieval_agent(),
    )


def reasoning_task(context: dict, depth: int) -> Task:
    return Task(
        description=(
            f"Depth {depth}. Return JSON array (max 3 items). Each item: "
            "{{interpretation, thoughts:[{{plan_id, scenario_id, claim, evidence_ids, payout, deductible_applied}}]}}.\n\n"
            f"Context:\n{json.dumps(context, default=str)[:8000]}"
        ),
        expected_output="JSON array of branch proposals.",
        agent=scenario_reasoning_agent(),
    )


def critic_task(branches: list[dict], profile: dict) -> Task:
    return Task(
        description=(
            "Evaluate each branch. Return JSON array: "
            "{{branch_id, scores:{{grounding, consistency, scenario_completeness, "
            "arithmetic_validity, priority_alignment}}, composite_score, prune, rationale}}.\n\n"
            f"Profile:\n{json.dumps(profile)}\n\nBranches:\n{json.dumps(branches, default=str)[:8000]}"
        ),
        expected_output="JSON array of evaluations.",
        agent=policy_critic_agent(),
    )


def synthesize_task(winning_branch: dict, plans: list[dict]) -> Task:
    return Task(
        description=(
            "Write markdown with: comparison table, recommended plan, tradeoffs, citations.\n\n"
            f"Winning branch:\n{json.dumps(winning_branch, default=str)}\n\n"
            f"Plans:\n{json.dumps(plans, default=str)[:6000]}"
        ),
        expected_output="Markdown report.",
        agent=recommendation_synthesizer_agent(),
    )
