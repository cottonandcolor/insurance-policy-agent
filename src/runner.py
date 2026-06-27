"""Reusable agent runner for CLI, API, and notebooks."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from src.config import get_llm_mode_label
from src.graph.workflow import build_graph
from src.memory.session_store import load_session, save_session
from src.progress import progress

MAX_CONVERSATION_TURNS = 8


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


def trim_conversation_history(
    history: list[dict[str, str]] | None,
    max_turns: int = MAX_CONVERSATION_TURNS,
) -> list[dict[str, str]]:
    if not history:
        return []
    return history[-max_turns:]


def _graph_config(thread_id: str) -> dict:
    return {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 50,
    }


def _initial_state(
    policy_paths: list[str],
    user_messages: list[str] | None,
    *,
    dry_run: bool,
    beam_width: int,
    max_depth: int,
    max_llm_calls: int,
    start_depth: int,
    thread_id: str | None = None,
    follow_up_mode: bool = False,
    follow_up: str | None = None,
    conversation_history: list[dict[str, str]] | None = None,
    normalized_plans: list[dict] | None = None,
    retrieval_cache: dict | None = None,
    session_profile: dict | None = None,
) -> dict:
    return {
        "dry_run": dry_run,
        "thread_id": thread_id,
        "follow_up_mode": follow_up_mode,
        "follow_up": follow_up,
        "user_messages": user_messages
        or build_user_messages(
            age=35,
            location="Cedar Park, TX",
            flood_zone=True,
            coverage_breadth=0.4,
            low_cost=0.3,
            few_exclusions=0.3,
        ),
        "conversation_history": trim_conversation_history(conversation_history or []),
        "policy_paths": policy_paths,
        "normalized_plans": normalized_plans or [],
        "session_profile": session_profile or {},
        "llm_call_count": 0,
        "max_llm_calls": max_llm_calls,
        "beam_width": beam_width,
        "max_depth": max_depth,
        "start_depth": start_depth,
        "retrieval_cache": retrieval_cache or {},
    }


def _persist_session(thread_id: str, result: dict, meta: dict[str, Any]) -> None:
    save_session(
        thread_id,
        {
            **meta,
            "conversation_history": result.get("conversation_history", []),
            "normalized_plans": result.get("normalized_plans", []),
            "retrieval_cache": result.get("retrieval_cache", {}),
            "session_profile": result.get("session_profile", {}),
            "external_enrichment": result.get("external_enrichment", {}),
            "winning_branch": result.get("winning_branch"),
            "final_recommendation": result.get("final_recommendation"),
        },
    )


def run_agent(
    policy_paths: list[str],
    user_messages: list[str] | None = None,
    dry_run: bool = False,
    beam_width: int = 3,
    max_depth: int = 4,
    max_llm_calls: int = 25,
    start_depth: int = 1,
    thread_id: str | None = None,
) -> dict:
    """Run the LangGraph workflow and return final state."""
    app = build_graph()
    thread_id = thread_id or uuid.uuid4().hex[:12]
    state = _initial_state(
        policy_paths,
        user_messages,
        dry_run=dry_run,
        beam_width=beam_width,
        max_depth=max_depth,
        max_llm_calls=max_llm_calls,
        start_depth=start_depth,
        thread_id=thread_id,
    )
    result = app.invoke(state, config=_graph_config(thread_id))
    result["mode"] = "dry_run" if dry_run else get_llm_mode_label()
    result["thread_id"] = thread_id

    _persist_session(
        thread_id,
        result,
        {
            "policy_paths": policy_paths,
            "user_messages": state["user_messages"],
            "dry_run": dry_run,
            "beam_width": beam_width,
            "max_depth": max_depth,
            "max_llm_calls": max_llm_calls,
        },
    )
    return result


def run_follow_up(
    thread_id: str,
    message: str,
    *,
    dry_run: bool | None = None,
    quick: bool | None = None,
) -> dict:
    """Re-score with session memory — skips re-ingest when plans are cached."""
    session = load_session(thread_id)
    if session is None:
        raise ValueError(f"Unknown session thread_id={thread_id}")

    use_dry_run = dry_run if dry_run is not None else bool(session.get("dry_run"))
    beam_width = 2 if quick else session.get("beam_width", 3)
    max_depth = 2 if quick else session.get("max_depth", 4)
    if quick is False:
        beam_width = session.get("beam_width", 3)
        max_depth = session.get("max_depth", 4)

    user_messages = list(session.get("user_messages", []))
    user_messages.append(message)
    history = trim_conversation_history(session.get("conversation_history", []))
    history.append({"role": "user", "content": message})

    app = build_graph()
    state = _initial_state(
        session["policy_paths"],
        user_messages,
        dry_run=use_dry_run,
        beam_width=beam_width,
        max_depth=max_depth,
        max_llm_calls=session.get("max_llm_calls", 25),
        start_depth=2,
        thread_id=thread_id,
        follow_up_mode=True,
        follow_up=message,
        conversation_history=history,
        normalized_plans=session.get("normalized_plans"),
        retrieval_cache=session.get("retrieval_cache"),
        session_profile=session.get("session_profile"),
    )

    result = app.invoke(state, config=_graph_config(thread_id))
    result["mode"] = "dry_run" if use_dry_run else get_llm_mode_label()
    result["thread_id"] = thread_id

    _persist_session(
        thread_id,
        result,
        {
            "policy_paths": session["policy_paths"],
            "user_messages": user_messages,
            "dry_run": use_dry_run,
            "beam_width": beam_width,
            "max_depth": max_depth,
            "max_llm_calls": session.get("max_llm_calls", 25),
        },
    )
    return result


def run_agent_streaming(
    policy_paths: list[str],
    user_messages: list[str] | None = None,
    *,
    dry_run: bool = False,
    beam_width: int = 2,
    max_depth: int = 2,
    max_llm_calls: int = 25,
    start_depth: int = 1,
    verbose: bool = True,
    thread_id: str | None = None,
) -> dict:
    """Run LangGraph and optionally print one line per completed node."""
    app = build_graph()
    thread_id = thread_id or uuid.uuid4().hex[:12]
    state = _initial_state(
        policy_paths,
        user_messages,
        dry_run=dry_run,
        beam_width=beam_width,
        max_depth=max_depth,
        max_llm_calls=max_llm_calls,
        start_depth=start_depth,
        thread_id=thread_id,
    )

    result = dict(state)
    if verbose:
        progress(f"Mode: {'dry-run' if dry_run else get_llm_mode_label()}")
        progress(f"Policies: {[Path(p).name for p in policy_paths]}")
        progress(f"beam_width={beam_width} max_depth={max_depth}")
        progress(f"thread_id={thread_id}")
        progress("Building graph and starting workflow...")

    for step in app.stream(state, config=_graph_config(thread_id), stream_mode="updates"):
        for node_name, update in step.items():
            if "llm_call_count" in update:
                result["llm_call_count"] = update["llm_call_count"]
            result.update(update)
            if not verbose:
                continue
            calls = result.get("llm_call_count", 0)
            depth = result.get("depth")
            extra = (
                f"depth={depth}"
                if depth is not None
                and node_name in ("tot_expand", "evaluate", "prune_beam", "advance_depth")
                else ""
            )
            branches = update.get("active_branches")
            if branches is not None and node_name in ("tot_expand", "evaluate", "prune_beam"):
                extra += f" branches={len(branches)}"
            if "indexed_chunks" in update:
                extra += f" chunks={update['indexed_chunks']}"
            if "normalized_plans" in update:
                extra += f" plans={len(update['normalized_plans'])}"
            if update.get("error"):
                extra += f" ERROR={update['error']}"
            suffix = f" ({extra.strip()})" if extra.strip() else ""
            progress(f"  ✓ {node_name}{suffix}  [LLM calls: {calls}]")

    result["mode"] = "dry_run" if dry_run else get_llm_mode_label()
    result["thread_id"] = thread_id
    _persist_session(
        thread_id,
        result,
        {
            "policy_paths": policy_paths,
            "user_messages": state["user_messages"],
            "dry_run": dry_run,
            "beam_width": beam_width,
            "max_depth": max_depth,
            "max_llm_calls": max_llm_calls,
        },
    )
    if verbose:
        progress("\n--- DONE ---")
        progress(f"Mode: {result.get('mode')}")
        progress(f"LLM calls: {result.get('llm_call_count')}")
        if result.get("error"):
            progress(f"Error: {result['error']}")
    return result


def format_response(result: dict) -> dict:
    """Shape agent state for API / frontend consumption."""
    return {
        "thread_id": result.get("thread_id"),
        "recommendation": result.get("final_recommendation"),
        "winning_branch": result.get("winning_branch"),
        "normalized_plans": result.get("normalized_plans", []),
        "session_profile": result.get("session_profile", {}),
        "external_enrichment": result.get("external_enrichment", {}),
        "conversation_history": result.get("conversation_history", []),
        "llm_call_count": result.get("llm_call_count", 0),
        "indexed_chunks": result.get("indexed_chunks"),
        "mode": result.get("mode"),
        "error": result.get("error"),
    }
