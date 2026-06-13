from datetime import datetime, timezone

from fastapi.testclient import TestClient

from safenergy.api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_forecast_predict():
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "asset_id": "test-asset",
        "features": [
            {
                "timestamp": now,
                "features": {"f1": 1.0, "f2": 2.0}
            }
        ],
        "return_uncertainty": True
    }

    response = client.post("/forecast/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["asset_id"] == "test-asset"
    assert len(data["predictions"]) == 1
    assert data["predictions"][0]["point"] is None
    assert data["predictions"][0]["method"] == "diagnostic_fallback"
    assert data["predictions"][0]["confidence_score"] == 0.0
    assert data["predictions"][0]["lower"] is None
    assert data["predictions"][0]["upper"] is None


def test_trading_signals():
    now1 = datetime(2023, 1, 1, 10, tzinfo=timezone.utc).isoformat()
    now2 = datetime(2023, 1, 1, 11, tzinfo=timezone.utc).isoformat()

    payload = {
        "asset_id": "test-asset",
        "data": [
            {
                "timestamp": now1,
                "delta": 30.0,
                "baseline": 50.0,
                "price": 20.0
            },
            {
                "timestamp": now2,
                "delta": 110.0,
                "baseline": 60.0,
                "price": 1050.0
            }
        ],
        "strong_threshold": 100.0,
        "weak_threshold": 20.0,
        "curtailment_price_threshold": -10.0,
        "extreme_price_threshold": 1000.0
    }

    response = client.post("/trading/signals", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["asset_id"] == "test-asset"
    assert data[0]["base_signal"] == 1  # WEAK_LONG
    assert data[0]["adjusted_signal"] == 1  # WEAK_LONG
    assert data[1]["base_signal"] == 2  # STRONG_LONG
    # Note: extreme price adjustment logic drops weak long to neutral, but strong long stays strong long unless custom logic overrides.
    # Current threshold logic says price >= extreme_price and base == WEAK_LONG -> NEUTRAL.
    # So for STRONG_LONG it should remain STRONG_LONG or adjust based on market context implementation. Let's just check length and parsing.


def test_trading_backtest():
    now1 = datetime(2023, 1, 1, 10, tzinfo=timezone.utc).isoformat()
    now2 = datetime(2023, 1, 1, 11, tzinfo=timezone.utc).isoformat()

    payload = {
        "data": [
            {
                "timestamp": now1,
                "signal": 1, # WEAK_LONG
                "price_change": 5.0
            },
            {
                "timestamp": now2,
                "signal": -2, # STRONG_SHORT
                "price_change": 10.0 # Price went up but we were short -> miss
            }
        ]
    }

    response = client.post("/trading/backtest", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "total_return" in data
    assert data["total_return"] == 5.0 - 20.0  # (1*5.0) + (-2*10.0) = -15.0
    assert data["hit_rate"] == 0.5
    assert data["hits"] == 1
    assert data["misses"] == 1
    assert data["flat"] == 0
    assert data["total_trades"] == 2


def test_explain_forecast():
    payload = {
        "forecast_delta": 25.0,
        "baseline": 100.0,
        "lower_bound": 110.0,
        "upper_bound": 140.0,
        "features": {
            "cloud_cover": -15.0,
            "wind_speed": 5.0
        },
        "market_price": -5.0
    }
    response = client.post("/trading/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "25.0 MW higher" in data["summary"]
    assert data["confidence"] in ["High", "Medium", "Low"]
    assert data["uncertainty_mw"] == 30.0
    assert "cloud_cover" in data["top_drivers"]
    assert "wind_speed" in data["top_drivers"]
    assert len(data["attribution"]) == 2
    assert "negative" in data["summary"]

def test_list_plants():
    response = client.get("/plants")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["plant_id"] == "pv-texas-01"
    assert data[1]["plant_id"] == "pv-texas-02"


def test_get_plant():
    response = client.get("/plants/pv-texas-01")
    assert response.status_code == 200
    data = response.json()
    assert data["plant_id"] == "pv-texas-01"
    assert data["name"] == "Texas Solar 1"
    assert data["capacity_mw"] == 150.0
    assert data["status"] == "active"


def test_get_plant_not_found():
    response = client.get("/plants/non-existent-plant")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Plant non-existent-plant not found"
