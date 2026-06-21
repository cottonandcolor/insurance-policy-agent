"""API tests for React demo backend."""

from io import BytesIO
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "llm_provider" in data
    assert "ollama_reachable" in data
    assert "configured_model" in data


def test_models():
    resp = client.get("/api/models")
    assert resp.status_code == 200
    data = resp.json()
    assert "provider" in data
    assert "label" in data


def test_analyze_dry_run_defaults():
    resp = client.post(
        "/api/analyze?dry_run=true&quick=true",
        data={
            "age": 35,
            "location": "Cedar Park, TX",
            "flood_zone": "true",
            "home_value": 350000,
            "coverage_breadth": 0.4,
            "low_cost": 0.3,
            "few_exclusions": 0.3,
            "use_defaults": "true",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "dry_run"
    assert data["recommendation"]
    assert "plan_b" in data["recommendation"].lower()
    assert data["winning_branch"]
    assert data["error"] is None
    assert data["llm_call_count"] >= 1


def test_analyze_dry_run_full_depth():
    resp = client.post(
        "/api/analyze?dry_run=true&quick=false",
        data={"use_defaults": "true"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "dry_run"
    assert data["recommendation"]
    assert data["error"] is None


def test_analyze_live_without_ollama_returns_503():
    with patch("api.main._ollama_reachable", new=AsyncMock(return_value=False)), patch(
        "api.main.LLM_PROVIDER", "ollama"
    ):
        resp = client.post("/api/analyze?dry_run=false&quick=true", data={})
    assert resp.status_code == 503
    assert "Ollama" in resp.json()["detail"]


def test_analyze_rejects_non_txt_upload():
    resp = client.post(
        "/api/analyze?dry_run=true&quick=true",
        data={"use_defaults": "false"},
        files={"policies": ("policy.pdf", BytesIO(b"%PDF"), "application/pdf")},
    )
    assert resp.status_code == 400
    assert ".txt" in resp.json()["detail"]


def test_analyze_accepts_txt_upload():
    policy = b"FLOOD: excluded unless endorsement attached.\n"
    resp = client.post(
        "/api/analyze?dry_run=true&quick=true",
        data={"use_defaults": "false"},
        files={"policies": ("custom_plan.txt", BytesIO(policy), "text/plain")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["recommendation"]
    assert data["error"] is None


def test_analyze_live_mocked(policy_paths, mock_llm_responses):
    responses = [
        mock_llm_responses["intake"],
        mock_llm_responses["ingest_plan_a"],
        mock_llm_responses["ingest_plan_b"],
        mock_llm_responses["reasoning"],
        mock_llm_responses["critic"],
        mock_llm_responses["synthesis"],
    ]
    idx = {"n": 0}

    def fake_complete(_system, _user, temperature=0.0):
        i = idx["n"]
        idx["n"] += 1
        return responses[min(i, len(responses) - 1)]

    with patch("api.main._ollama_reachable", new=AsyncMock(return_value=True)), patch(
        "src.crews.runner.complete", side_effect=fake_complete
    ):
        resp = client.post(
            "/api/analyze?dry_run=false&quick=true",
            data={"use_defaults": "true"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["recommendation"]
    assert data["error"] is None
    assert data["mode"] != "dry_run"
