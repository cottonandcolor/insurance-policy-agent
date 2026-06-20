"""LangGraph routing helpers."""

from __future__ import annotations

from typing import Literal

from src.state import AgentState


def should_continue_tot(state: AgentState) -> Literal["expand", "synthesize"]:
    if state.get("error"):
        return "synthesize"
    # After advance_depth, stop once we have completed max_depth expand cycles
    if state.get("depth", 1) > state.get("max_depth", 4):
        return "synthesize"
    if not state.get("active_branches"):
        return "synthesize"
    return "expand"
