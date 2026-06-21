"""Reusable agent runner for CLI and API."""

from __future__ import annotations

from src.config import get_llm_mode_label
from src.graph.workflow import build_graph


def build_user_messages(
    age: int,
    location: str,
    flood_zone: bool,
    coverage_breadth: float,
    low_cost: float,
    few_exclusions: float,
    home_value: int = 350_000,
) -> list[str]:
    flood = "in a flood zone" if flood_zone else "not in a flood zone"
    return [
        f"I'm {age}, live {flood} in {location}, own a ${home_value:,} home.",
        (
            "Priorities: broad coverage "
            f"{coverage_breadth}, low cost {low_cost}, few exclusions {few_exclusions}."
        ),
    ]


def run_agent(
    policy_paths: list[str],
    user_messages: list[str] | None = None,
    dry_run: bool = False,
    beam_width: int = 3,
    max_depth: int = 4,
    max_llm_calls: int = 25,
    start_depth: int = 1,
) -> dict:
    """Run the LangGraph workflow and return final state."""
    app = build_graph()
    state = {
        "dry_run": dry_run,
        "user_messages": user_messages
        or build_user_messages(
            age=35,
            location="Cedar Park, TX",
            flood_zone=True,
            coverage_breadth=0.4,
            low_cost=0.3,
            few_exclusions=0.3,
        ),
        "policy_paths": policy_paths,
        "llm_call_count": 0,
        "max_llm_calls": max_llm_calls,
        "beam_width": beam_width,
        "max_depth": max_depth,
        "start_depth": start_depth,
        "retrieval_cache": {},
    }
    result = app.invoke(state, config={"recursion_limit": 50})
    result["mode"] = "dry_run" if dry_run else get_llm_mode_label()
    return result


def format_response(result: dict) -> dict:
    """Shape agent state for API / frontend consumption."""
    return {
        "recommendation": result.get("final_recommendation"),
        "winning_branch": result.get("winning_branch"),
        "normalized_plans": result.get("normalized_plans", []),
        "session_profile": result.get("session_profile", {}),
        "llm_call_count": result.get("llm_call_count", 0),
        "indexed_chunks": result.get("indexed_chunks"),
        "mode": result.get("mode"),
        "error": result.get("error"),
    }
