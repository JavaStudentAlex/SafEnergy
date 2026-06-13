from fastapi.testclient import TestClient

from safenergy.api.main import app

client = TestClient(app)

def test_run_orchestrator():
    response = client.post(
        "/orchestrator/run",
        json={
            "asset_id": "TEST_API_1",
            "latitude": 30.2672,
            "longitude": -97.7431,
            "start_date": "2023-01-01",
            "end_date": "2023-01-02",
            "simulate_failure": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["asset_id"] == "TEST_API_1"
    assert "issue_time" in data
    assert "signals" in data
    assert "explanations" in data

def test_run_orchestrator_failure():
    response = client.post(
        "/orchestrator/run",
        json={
            "asset_id": "TEST_API_FAIL",
            "latitude": 30.2672,
            "longitude": -97.7431,
            "start_date": "2023-01-01",
            "end_date": "2023-01-02",
            "simulate_failure": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["asset_id"] == "TEST_API_FAIL"
    assert data["signals"] == []
    assert data["explanations"] == []
