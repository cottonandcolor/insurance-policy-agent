"""Live-mode workflow tests with mocked LLM HTTP calls."""

from unittest.mock import patch

from src.crews import runner as crew_runner
from src.runner import run_agent


def test_crew_runner_intake(mock_llm_responses):
    with patch("src.crews.runner.complete", return_value=mock_llm_responses["intake"]):
        profile = crew_runner.run_intake(["I'm 35 in Cedar Park, TX"])
    assert profile["age"] == 35
    assert profile["flood_zone"] is True


def test_crew_runner_ingest(mock_llm_responses):
    with patch(
        "src.crews.runner.complete", return_value=mock_llm_responses["ingest_plan_b"]
    ):
        plan = crew_runner.run_ingest("policy text", "plan_b")
    assert plan["plan_id"] == "plan_b"
    assert plan["deductible"] == 5_000


def test_run_agent_live_mode_mocked(policy_paths, mock_llm_responses):
    responses = [
        mock_llm_responses["intake"],
        mock_llm_responses["ingest_plan_a"],
        mock_llm_responses["ingest_plan_b"],
        mock_llm_responses["reasoning"],
        mock_llm_responses["critic"],
        mock_llm_responses["synthesis"],
    ]
    call_count = {"i": 0}

    def fake_complete(_system, _user, temperature=0.0):
        idx = call_count["i"]
        call_count["i"] += 1
        return responses[min(idx, len(responses) - 1)]

    with patch("src.crews.runner.complete", side_effect=fake_complete):
        result = run_agent(
            policy_paths=policy_paths,
            dry_run=False,
            beam_width=2,
            max_depth=2,
        )

    assert result["mode"].startswith("ollama/") or result["mode"].startswith("openai/")
    assert result.get("final_recommendation")
    assert result.get("error") is None
    assert call_count["i"] >= 5
