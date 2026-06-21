"""API tests for React demo backend."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "llm_provider" in data


def test_models():
    resp = client.get("/api/models")
    assert resp.status_code == 200
    assert "provider" in resp.json()


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
    assert data["error"] is None
