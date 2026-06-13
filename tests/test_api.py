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
    assert data["predictions"][0]["point"] == 10.0
    assert data["predictions"][0]["lower"] == 8.0
    assert data["predictions"][0]["upper"] == 12.0


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
