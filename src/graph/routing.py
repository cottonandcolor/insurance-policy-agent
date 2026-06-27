"""LangGraph routing helpers."""

from __future__ import annotations

from typing import Literal

from src.state import AgentState


def route_after_enrich(state: AgentState) -> Literal["index", "tot_init"]:
    """Skip re-indexing when follow-up reuses normalized plans from session memory."""
    if state.get("follow_up_mode") and state.get("normalized_plans"):
        return "tot_init"
    return "index"


def should_continue_tot(state: AgentState) -> Literal["expand", "synthesize"]:
    if state.get("error"):
        return "synthesize"
    # After advance_depth, stop once we have completed max_depth expand cycles
    if state.get("depth", 1) > state.get("max_depth", 4):
        return "synthesize"
    if not state.get("active_branches"):
        return "synthesize"
    return "expand"
