"""Shared LangGraph state."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class Thought(TypedDict, total=False):
    plan_id: str
    scenario_id: str
    claim: str
    evidence_ids: List[str]
    payout: Optional[float]
    deductible_applied: Optional[float]


class Branch(TypedDict, total=False):
    branch_id: str
    depth: int
    parent_id: Optional[str]
    interpretation: str
    thoughts: List[Thought]
    scores: Dict[str, float]
    composite_score: float
    pruned: bool
    hard_gate_failed: bool
    hard_gate_failures: List[str]
    rationale: str


class ConversationTurn(TypedDict, total=False):
    role: str
    content: str


class AgentState(TypedDict, total=False):
    dry_run: bool
    thread_id: str
    follow_up_mode: bool
    user_messages: List[str]
    conversation_history: List[ConversationTurn]
    session_summary: str
    session_profile: Dict[str, Any]
    external_enrichment: Dict[str, Any]
    policy_paths: List[str]
    normalized_plans: List[Dict[str, Any]]
    retrieval_cache: Dict[str, List[Dict[str, Any]]]
    indexed_chunks: int
    depth: int
    start_depth: int
    beam_width: int
    max_depth: int
    active_branches: List[Branch]
    llm_call_count: int
    max_llm_calls: int
    winning_branch: Optional[Branch]
    final_recommendation: str
    follow_up: Optional[str]
    error: Optional[str]
