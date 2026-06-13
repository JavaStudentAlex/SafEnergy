from fastapi.testclient import TestClient

from safenergy.api.main import app

client = TestClient(app)

def test_get_plant_health_all():
    response = client.get("/plant-health")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    # Verify expected schema structure
    for plant_health in data:
        assert "plant_id" in plant_health
        assert "status" in plant_health
        assert "last_updated" in plant_health
        assert "anomalies" in plant_health

def test_get_plant_health_by_id_maintenance():
    response = client.get("/plant-health/pv-texas-02")
    assert response.status_code == 200
    data = response.json()
    assert data["plant_id"] == "pv-texas-02"
    assert data["status"] == "maintenance"
    assert len(data["anomalies"]) == 1
    anomaly = data["anomalies"][0]
    assert anomaly["category"] == "inverter_outage"
    assert anomaly["severity"] == "critical"

def test_get_plant_health_by_id_degraded():
    response = client.get("/plant-health/pv-texas-01")
    assert response.status_code == 200
    data = response.json()
    assert data["plant_id"] == "pv-texas-01"
    assert data["status"] == "degraded"
    assert len(data["anomalies"]) == 1
    anomaly = data["anomalies"][0]
    assert anomaly["category"] == "weather_derating"
    assert anomaly["severity"] == "warning"

def test_get_plant_health_not_found():
    response = client.get("/plant-health/non-existent")
    assert response.status_code == 404
