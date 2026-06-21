"""End-to-end runner tests (dry-run, no live LLM)."""

from src.config import ROOT
from src.runner import build_user_messages, format_response, run_agent


def test_build_user_messages_flood_zone():
    msgs = build_user_messages(
        age=40,
        location="Austin, TX",
        flood_zone=True,
        coverage_breadth=0.5,
        low_cost=0.25,
        few_exclusions=0.25,
    )
    assert len(msgs) == 2
    assert "flood zone" in msgs[0]
    assert "Austin, TX" in msgs[0]


def test_run_agent_dry_run_quick(policy_paths):
    result = run_agent(
        policy_paths=policy_paths,
        dry_run=True,
        beam_width=2,
        max_depth=2,
    )
    assert result["mode"] == "dry_run"
    assert result.get("final_recommendation")
    assert result.get("winning_branch")
    assert "plan_b" in result["final_recommendation"].lower()
    assert result.get("error") is None
    assert result.get("llm_call_count", 0) >= 1


def test_run_agent_dry_run_indexes_policies(policy_paths):
    result = run_agent(
        policy_paths=policy_paths,
        dry_run=True,
        beam_width=2,
        max_depth=2,
    )
    assert result.get("indexed_chunks", 0) >= 1
    assert len(result.get("normalized_plans", [])) == 2


def test_format_response_shape(policy_paths):
    result = run_agent(
        policy_paths=policy_paths,
        dry_run=True,
        beam_width=2,
        max_depth=2,
    )
    payload = format_response(result)
    assert set(payload.keys()) == {
        "recommendation",
        "winning_branch",
        "normalized_plans",
        "session_profile",
        "llm_call_count",
        "indexed_chunks",
        "mode",
        "error",
    }
    assert payload["mode"] == "dry_run"
    assert payload["recommendation"]
    assert payload["error"] is None


def test_default_policy_files_exist():
    for name in ("plan_a.txt", "plan_b.txt"):
        assert (ROOT / "data" / "synthetic" / name).is_file()
