"""Tests for session memory, routing, and location enrichment."""

from unittest.mock import patch

import pytest

from src.graph.routing import route_after_enrich
from src.runner import run_agent, run_follow_up, trim_conversation_history
from src.tools.location_enrichment import enrich_location


def test_route_after_enrich_skips_index_on_follow_up():
    state = {"follow_up_mode": True, "normalized_plans": [{"plan_id": "plan_a"}]}
    assert route_after_enrich(state) == "tot_init"


def test_route_after_enrich_runs_index_on_first_pass():
    state = {"follow_up_mode": False, "normalized_plans": []}
    assert route_after_enrich(state) == "index"


def test_trim_conversation_history():
    history = [{"role": "user", "content": str(i)} for i in range(12)]
    trimmed = trim_conversation_history(history, max_turns=8)
    assert len(trimmed) == 8
    assert trimmed[0]["content"] == "4"


def test_enrich_location_with_mocked_apis():
    geocode = {"latitude": 30.5, "longitude": -97.8}
    zone = {"flood_zone_code": "AE", "flood_zone_subtype": "FLOODWAY"}

    with patch("src.tools.location_enrichment.geocode_us_address", return_value=geocode), patch(
        "src.tools.location_enrichment.lookup_flood_zone", return_value=zone
    ):
        result = enrich_location("Cedar Park, TX")

    assert result["latitude"] == 30.5
    assert result["flood_zone_code"] == "AE"
    assert result["flood_zone_inferred"] is True


def test_follow_up_dry_run_reuses_session(policy_paths):
    first = run_agent(
        policy_paths,
        dry_run=True,
        beam_width=2,
        max_depth=2,
    )
    assert first.get("thread_id")
    assert first.get("normalized_plans")

    second = run_follow_up(
        first["thread_id"],
        "I care more about lowest cost than broad coverage.",
        dry_run=True,
        quick=True,
    )
    assert second.get("final_recommendation")
    assert second["thread_id"] == first["thread_id"]
    assert second.get("error") is None


def test_follow_up_unknown_thread_raises():
    with pytest.raises(ValueError, match="Unknown session"):
        run_follow_up("missing-thread-id", "hello", dry_run=True)
