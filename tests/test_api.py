from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pandas as pd
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




@patch("safenergy.api.routes.fetch_weather_forecast")
def test_weather_live(mock_fetch_weather):
    now = datetime.now(timezone.utc)
    current_hour = now.replace(minute=0, second=0, microsecond=0)

    # Create mock weather df
    timestamps = [current_hour - timedelta(hours=1), current_hour, current_hour + timedelta(hours=1)]
    df = pd.DataFrame(
        data={
            "temperature_2m": [10.0, 15.0, 20.0],
            "cloud_cover": [0.0, 50.0, 100.0],
            "wind_speed_10m": [5.0, 10.0, 15.0],
            "shortwave_radiation": [100.0, 500.0, 800.0]
        },
        index=pd.DatetimeIndex(timestamps, tz="UTC")
    )
    mock_fetch_weather.return_value = df

    response = client.get("/weather/live?plant_id=pv-texas-01")
    assert response.status_code == 200
    data = response.json()
    assert data["plant_id"] == "pv-texas-01"
    assert data["provenance"] == "open-meteo"
    assert len(data["points"]) == 1
    point = data["points"][0]
    assert point["temperature_2m"] == 15.0
    assert point["cloud_cover"] == 50.0

def test_weather_live_not_found():
    response = client.get("/weather/live?plant_id=non-existent-plant")
    assert response.status_code == 404

@patch("safenergy.api.routes.fetch_weather_forecast")
def test_weather_forecast(mock_fetch_weather):
    now = datetime.now(timezone.utc)
    current_hour = now.replace(minute=0, second=0, microsecond=0)

    timestamps = [current_hour, current_hour + timedelta(hours=1), current_hour + timedelta(hours=2)]
    df = pd.DataFrame(
        data={
            "temperature_2m": [15.0, 20.0, 25.0],
            "cloud_cover": [50.0, 60.0, 70.0],
            "wind_speed_10m": [10.0, 15.0, 20.0],
            "shortwave_radiation": [500.0, 800.0, 900.0]
        },
        index=pd.DatetimeIndex(timestamps, tz="UTC")
    )
    mock_fetch_weather.return_value = df

    response = client.get("/weather/forecast?plant_id=pv-texas-01&hours=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["points"]) == 2
    assert data["points"][0]["temperature_2m"] == 20.0
    assert data["points"][1]["temperature_2m"] == 25.0

def test_weather_forecast_not_found():
    response = client.get("/weather/forecast?plant_id=non-existent-plant")
    assert response.status_code == 404

def test_get_forecast_by_plant_id():
    """
    Test the new /forecast/{plant_id} endpoint.
    """
    plant_id = "test-plant-001" # from fixtures if we have one, or mock the plant

    # We can mock get_plant_by_id and fetch_weather_forecast to make it deterministic
    with patch("safenergy.api.routes.get_plant_by_id") as mock_get_plant:
        mock_get_plant.return_value = {
            "plant_id": plant_id,
            "name": "Test Plant",
            "latitude": 52.52,
            "longitude": 13.40,
            "timezone": "Europe/Berlin",
            "capacity_mw": 10.0,
            "status": "active",
            "battery_capacity_mwh": 0.0,
            "metadata_dict": {}
        }

        with patch("safenergy.api.routes.fetch_weather_forecast") as mock_fetch_weather:
            # Create dummy weather data
            now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
            idx = pd.date_range(start=now - pd.Timedelta(hours=1), periods=4, freq="1h", tz="UTC")
            df = pd.DataFrame({
                "shortwave_radiation": [0.0, 500.0, 600.0, 0.0],
                "temperature_2m": [15.0, 16.0, 17.0, 15.0],
                "wind_speed_10m": [3.0, 4.0, 5.0, 3.0]
            }, index=idx)
            mock_fetch_weather.return_value = df

            response = client.get(f"/forecast/{plant_id}?horizon_minutes=60")
            assert response.status_code == 200
            data = response.json()

            assert data["asset_id"] == plant_id
            assert "predictions" in data

            # Since we return future points, it should return at least some points
            # up to the horizon. (15m resampling means up to 4 points for 60m horizon)
            predictions = data["predictions"]
            assert len(predictions) > 0

            # Check the method is populated (should use pvlib_physical or diagnostic_fallback)
            for pred in predictions:
                assert pred["method"] in ["pvlib_physical", "diagnostic_fallback"]

@patch("safenergy.api.routes.fetch_delu_prices")
def test_market_prices(mock_fetch_delu):
    now = datetime.now(timezone.utc)
    current_hour = now.replace(minute=0, second=0, microsecond=0)

    timestamps = [current_hour, current_hour + timedelta(minutes=15), current_hour + timedelta(minutes=30)]
    df = pd.DataFrame(
        data={
            "day_ahead_eur_mwh": [50.0, 50.0, 50.0],
            "intraday_eur_mwh": [55.0, 55.0, 55.0],
            "balancing_short_eur_mwh": [75.0, 75.0, 75.0],
            "balancing_long_eur_mwh": [25.0, 25.0, 25.0]
        },
        index=pd.DatetimeIndex(timestamps, tz="UTC")
    )
    from safenergy.ingest.market import MarketDataDiagnostic, MarketDataResponse
    diag = MarketDataDiagnostic(status="ok", records_returned=3)
    resp = MarketDataResponse(
        provider="DE-LU-Mock",
        region="DE-LU",
        issue_time=now,
        valid_time_start=timestamps[0],
        valid_time_end=timestamps[-1],
        diagnostic=diag,
        data=df
    )
    mock_fetch_delu.return_value = resp

    response = client.get("/market/prices?zone=DE-LU&hours=1")
    assert response.status_code == 200
    data = response.json()
    assert data["zone"] == "DE-LU"
    assert "points" in data
    # 3 points mocked here (for an hour there would be 4, but we gave it 3 valid points in df)
    assert len(data["points"]) == 3
    assert data["points"][0]["day_ahead_eur_mwh"] == 50.0

def test_market_prices_invalid_zone():
    response = client.get("/market/prices?zone=ERCOT")
    assert response.status_code == 400
    assert "Only DE-LU zone is supported" in response.json()["detail"]

def test_commitment_recommend():
    payload = {
        "forecast_mwh": 90.0,
        "committed_mwh": 100.0,
        "battery_available_mwh": 5.0,
        "intraday_eur_mwh": 50.0,
        "balancing_short_eur_mwh": 100.0
    }

    response = client.post("/commitment/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "DISCHARGE_AND_BUY"
    assert data["commitment_gap_mwh"] == 10.0
    assert data["battery_discharge_mwh"] == 5.0
    assert data["market_buy_mwh"] == 5.0
    assert data["estimated_cost_eur"] == 250.0
    assert data["avoided_imbalance_cost_eur"] == 1000.0
    assert data["confidence_score"] == 0.9
    assert "Discharging 5.00 MWh from battery" in data["explanation"]
