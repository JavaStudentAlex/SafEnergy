from fastapi.testclient import TestClient

from safenergy.api.main import app

client = TestClient(app)

def test_commitment_smoke():
    # 1. Fetch plants
    resp = client.get("/plants")
    assert resp.status_code == 200
    plants = resp.json()
    assert len(plants) > 0
    plant_id = plants[0]["plant_id"]

    # 2. Fetch weather forecast for plant
    resp = client.get(f"/weather/forecast?plant_id={plant_id}&hours=24")
    assert resp.status_code == 200
    weather = resp.json()
    assert len(weather["points"]) > 0

    # 3. Fetch market prices
    resp = client.get("/market/prices?zone=DE-LU&hours=24")
    assert resp.status_code == 200
    market = resp.json()
    assert len(market["points"]) > 0
    intraday_price = market["points"][0]["intraday_eur_mwh"]
    balancing_short_price = market["points"][0]["balancing_short_eur_mwh"]

    # 4. Request recommendation
    rec_req = {
        "forecast_mwh": 90.0,
        "committed_mwh": 100.0,
        "battery_available_mwh": 5.0,
        "intraday_eur_mwh": intraday_price,
        "balancing_short_eur_mwh": balancing_short_price
    }
    resp = client.post("/commitment/recommend", json=rec_req)
    assert resp.status_code == 200
    rec = resp.json()
    assert "action" in rec
    assert rec["commitment_gap_mwh"] == 10.0

    # 5. Accept recommendation action
    acc_req = {
        "action_id": "test-action-123",
        "plant_id": plant_id,
        "action_type": rec["action"],
        "timestamp": "2023-10-01T12:00:00Z",
        "commitment_gap_mwh": rec["commitment_gap_mwh"],
        "battery_discharge_mwh": rec["battery_discharge_mwh"],
        "market_buy_mwh": rec["market_buy_mwh"],
        "estimated_cost_eur": rec["estimated_cost_eur"],
        "avoided_imbalance_cost_eur": rec["avoided_imbalance_cost_eur"]
    }
    resp = client.post("/commitment/actions/accept", json=acc_req)
    assert resp.status_code == 200

    # 6. Fetch metrics
    resp = client.get(f"/commitment/metrics?plant_id={plant_id}")
    assert resp.status_code == 200
    metrics = resp.json()

    # Assert metrics contain our accepted action's values
    assert metrics["action_count"] >= 1
    assert metrics["total_shortfall_mwh"] >= 10.0
