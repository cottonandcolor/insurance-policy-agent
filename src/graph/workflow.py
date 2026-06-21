"""
LangGraph orchestrator with CrewAI workers and ToT beam search.

Run dry-run (no API key):
  python main.py --dry-run

Run with OpenAI:
  export OPENAI_API_KEY=...
  python main.py
"""

from __future__ import annotations

from pathlib import Path

from langgraph.graph import END, StateGraph

from src.config import BEAM_WIDTH, MAX_DEPTH, MAX_LLM_CALLS
from src.graph.routing import should_continue_tot
from src.mocks import dry_run
from src.schemas import NormalizedPlan
from src.state import AgentState, Branch
from src.tools.retrieval import build_index, index_policy_paths, retrieve_evidence
from src.tools.validators import apply_hard_gates, should_prune


def _plans_by_id(plans: list[dict]) -> dict[str, NormalizedPlan]:
    out: dict[str, NormalizedPlan] = {}
    for p in plans:
        try:
            out[p["plan_id"]] = NormalizedPlan.model_validate(p)
        except Exception:
            continue
    return out


def _increment_calls(state: AgentState, n: int = 1) -> int:
    return state.get("llm_call_count", 0) + n


# ── Step 1: Intake ───────────────────────────────────────────────────────

def intake_node(state: AgentState) -> AgentState:
    if state.get("dry_run"):
        profile = dry_run.mock_profile(state.get("user_messages", []))
    else:
        from src.crews import runner as crew_runner
        profile = crew_runner.run_intake(state.get("user_messages", []))

    return {"session_profile": profile, "llm_call_count": _increment_calls(state)}


# ── Step 2: Index policies ───────────────────────────────────────────────

def index_node(state: AgentState) -> AgentState:
    paths = state.get("policy_paths", [])
    if paths:
        count = index_policy_paths(paths)
    else:
        count = build_index()
    return {"indexed_chunks": count}


# ── Step 3: Ingest + normalize ───────────────────────────────────────────

def ingest_node(state: AgentState) -> AgentState:
    plans: list[dict] = []
    calls = state.get("llm_call_count", 0)

    for path_str in state.get("policy_paths", []):
        path = Path(path_str)
        plan_id = path.stem
        text = path.read_text(encoding="utf-8")

        if state.get("dry_run"):
            parsed = dry_run.mock_normalized_plan(path)
        else:
            from src.crews import runner as crew_runner
            parsed = crew_runner.run_ingest(text, plan_id)
            calls += 1

        plans.append(parsed)

    return {"normalized_plans": plans, "llm_call_count": calls}


# ── Step 4: ToT init ─────────────────────────────────────────────────────

def tot_init_node(state: AgentState) -> AgentState:
    start_depth = state.get("start_depth", 1)
    root: Branch = {
        "branch_id": "root",
        "depth": 0,
        "parent_id": None,
        "interpretation": "root",
        "thoughts": [],
        "scores": {},
        "composite_score": 0.0,
        "pruned": False,
    }
    return {
        "depth": start_depth,
        "beam_width": state.get("beam_width", BEAM_WIDTH),
        "max_depth": state.get("max_depth", MAX_DEPTH),
        "max_llm_calls": state.get("max_llm_calls", MAX_LLM_CALLS),
        "active_branches": [root],
        "retrieval_cache": state.get("retrieval_cache", {}),
    }


# ── Step 5: ToT expand ───────────────────────────────────────────────────

def tot_expand_node(state: AgentState) -> AgentState:
    if state.get("llm_call_count", 0) >= state.get("max_llm_calls", MAX_LLM_CALLS):
        return {"error": "LLM budget exceeded"}

    new_branches: list[Branch] = []
    calls = state.get("llm_call_count", 0)
    depth = state.get("depth", 1)

    for parent in state.get("active_branches", []):
        if parent.get("pruned"):
            continue

        ctx = {
            "parent_branch_id": parent.get("branch_id"),
            "profile": state.get("session_profile", {}),
            "plans": state.get("normalized_plans", []),
            "depth": depth,
        }

        if state.get("dry_run"):
            children = dry_run.mock_reasoning_branches(
                depth, ctx["profile"], ctx["plans"]
            )
        else:
            from src.crews import runner as crew_runner
            children = crew_runner.run_reasoning(ctx, depth)
            calls += 1

        for i, child in enumerate(children[: state.get("beam_width", BEAM_WIDTH)]):
            new_branches.append(
                {
                    "branch_id": f"{parent['branch_id']}-d{depth}-{i}",
                    "depth": depth,
                    "parent_id": parent["branch_id"],
                    "interpretation": child.get("interpretation", f"branch-{i}"),
                    "thoughts": child.get("thoughts", []),
                    "scores": {},
                    "composite_score": 0.0,
                    "pruned": False,
                }
            )

    if not new_branches:
        return {"error": "No branches generated at expand step"}

    return {"active_branches": new_branches, "llm_call_count": calls}


# ── Step 6: Ground with retrieval ────────────────────────────────────────

def ground_node(state: AgentState) -> AgentState:
    cache = dict(state.get("retrieval_cache", {}))
    profile = state.get("session_profile", {})
    jurisdiction = profile.get("jurisdiction", "TX")
    updated: list[Branch] = []

    for branch in state.get("active_branches", []):
        for thought in branch.get("thoughts", []):
            if thought.get("evidence_ids"):
                continue
            plan_id = thought.get("plan_id", "plan_a")
            peril = thought.get("scenario_id", "flood")
            chunks = retrieve_evidence(plan_id, peril, jurisdiction, cache)
            if chunks:
                thought["evidence_ids"] = [c["chunk_id"] for c in chunks]
        updated.append(branch)

    return {"active_branches": updated, "retrieval_cache": cache}


# ── Step 7: Hard gates ───────────────────────────────────────────────────

def hard_gate_node(state: AgentState) -> AgentState:
    plans = _plans_by_id(state.get("normalized_plans", []))
    gated = [
        apply_hard_gates(branch, plans)
        for branch in state.get("active_branches", [])
    ]
    return {"active_branches": gated}


# ── Step 8: Critic evaluate ──────────────────────────────────────────────

def evaluate_node(state: AgentState) -> AgentState:
    branches = state.get("active_branches", [])
    profile = state.get("session_profile", {})
    depth = state.get("depth", 1)

    if state.get("dry_run"):
        evaluations = dry_run.mock_critic_evaluations(branches, depth)
        calls = state.get("llm_call_count", 0)
    else:
        from src.crews import runner as crew_runner
        evaluations = crew_runner.run_critic(branches, profile)
        calls = _increment_calls(state)

    eval_map = {e["branch_id"]: e for e in evaluations if "branch_id" in e}
    updated: list[Branch] = []

    for branch in branches:
        meta = eval_map.get(branch["branch_id"], {})
        composite = float(meta.get("composite_score", 0.0))
        hard_failed = branch.get("hard_gate_failed", False)
        branch["scores"] = meta.get("scores", {})
        branch["composite_score"] = composite
        branch["pruned"] = should_prune(composite, depth, hard_failed)
        branch["rationale"] = meta.get("rationale", "")
        updated.append(branch)

    return {"active_branches": updated, "llm_call_count": calls}


# ── Step 9: Beam prune ───────────────────────────────────────────────────

def prune_and_beam_node(state: AgentState) -> AgentState:
    survivors = [b for b in state.get("active_branches", []) if not b.get("pruned")]
    survivors.sort(key=lambda b: b.get("composite_score", 0.0), reverse=True)
    beam = survivors[: state.get("beam_width", BEAM_WIDTH)]
    if not beam:
        return {"error": "All branches pruned", "active_branches": []}
    return {"active_branches": beam}


def advance_depth_node(state: AgentState) -> AgentState:
    return {"depth": state.get("depth", 1) + 1}


# ── Step 10: Synthesize ──────────────────────────────────────────────────

def synthesize_node(state: AgentState) -> AgentState:
    branches = state.get("active_branches", [])
    if not branches:
        return {"error": state.get("error", "No surviving branch for recommendation.")}

    winning = max(branches, key=lambda b: b.get("composite_score", 0.0))

    if state.get("dry_run"):
        report = dry_run.mock_synthesis(winning, state.get("normalized_plans", []))
        calls = state.get("llm_call_count", 0)
    else:
        from src.crews import runner as crew_runner
        report = crew_runner.run_synthesize(winning, state.get("normalized_plans", []))
        calls = _increment_calls(state)

    return {
        "winning_branch": winning,
        "final_recommendation": report,
        "llm_call_count": calls,
    }


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("intake", intake_node)
    graph.add_node("index", index_node)
    graph.add_node("ingest", ingest_node)
    graph.add_node("tot_init", tot_init_node)
    graph.add_node("tot_expand", tot_expand_node)
    graph.add_node("ground", ground_node)
    graph.add_node("hard_gate", hard_gate_node)
    graph.add_node("evaluate", evaluate_node)
    graph.add_node("prune_beam", prune_and_beam_node)
    graph.add_node("advance_depth", advance_depth_node)
    graph.add_node("synthesize", synthesize_node)

    graph.set_entry_point("intake")
    graph.add_edge("intake", "index")
    graph.add_edge("index", "ingest")
    graph.add_edge("ingest", "tot_init")
    graph.add_edge("tot_init", "tot_expand")
    graph.add_edge("tot_expand", "ground")
    graph.add_edge("ground", "hard_gate")
    graph.add_edge("hard_gate", "evaluate")
    graph.add_edge("evaluate", "prune_beam")
    graph.add_edge("prune_beam", "advance_depth")
    graph.add_conditional_edges(
        "advance_depth",
        should_continue_tot,
        {"expand": "tot_expand", "synthesize": "synthesize"},
    )
    graph.add_edge("synthesize", END)

    return graph.compile()
