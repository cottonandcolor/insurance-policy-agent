"""Shared LangGraph checkpointer for thread-scoped memory."""

from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver

_CHECKPOINTER = MemorySaver()


def get_checkpointer() -> MemorySaver:
    return _CHECKPOINTER
