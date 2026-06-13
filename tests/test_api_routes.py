from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from safenergy.api.main import app

client = TestClient(app)

def test_trading_signals_no_data():
    response = client.post("/trading/signals", json={"asset_id": "test", "data": []})
    assert response.status_code == 400
    assert response.json()["detail"] == "No data provided"

@patch("safenergy.api.routes.generate_trading_signals")
def test_trading_signals_exception(mock_gen):
    mock_gen.side_effect = Exception("Test error")
    payload = {
        "asset_id": "test",
        "data": [
            {"timestamp": "2023-01-01T00:00:00Z", "delta": 10, "baseline": 50, "price": 20, "confidence": 0.9}
        ]
    }
    response = client.post("/trading/signals", json=payload)
    assert response.status_code == 500
    assert response.json()["detail"] == "An error occurred during trading signal generation."

def test_backtest_no_data():
    response = client.post("/trading/backtest", json={"data": [], "assumptions": {}})
    assert response.status_code == 400
    assert response.json()["detail"] == "No data provided"

@patch("safenergy.api.routes.evaluate_signals")
def test_backtest_exception(mock_eval):
    mock_eval.side_effect = Exception("Test error")
    payload = {
        "data": [{"timestamp": "2023-01-01T00:00:00Z", "signal": 1, "price_change": 5.0}],
        "assumptions": {}
    }
    response = client.post("/trading/backtest", json=payload)
    assert response.status_code == 500
    assert response.json()["detail"] == "An error occurred during backtest evaluation."

@patch("safenergy.api.routes.generate_explanation")
def test_explain_forecast_exception(mock_exp):
    mock_exp.side_effect = Exception("Test error")
    payload = {
        "forecast_delta": 25.0,
        "baseline": 100.0,
        "lower_bound": 110.0,
        "upper_bound": 140.0,
        "features": {},
        "market_price": -5.0
    }
    response = client.post("/trading/explain", json=payload)
    assert response.status_code == 500
    assert response.json()["detail"] == "An error occurred during forecast explanation."

@patch("safenergy.api.routes.recommend_action")
def test_commitment_recommend_exception(mock_rec):
    mock_rec.side_effect = Exception("Test error")
    payload = {
        "forecast_mwh": 90.0,
        "committed_mwh": 100.0,
        "battery_available_mwh": 5.0,
        "intraday_eur_mwh": 50.0,
        "balancing_short_eur_mwh": 100.0
    }
    response = client.post("/commitment/recommend", json=payload)
    assert response.status_code == 500
    assert response.json()["detail"] == "An error occurred during recommendation generation."

@patch("safenergy.api.routes.get_action_ledger")
def test_accept_action_exception(mock_ledger):
    mock_instance = mock_ledger.return_value
    mock_instance.record_action.side_effect = Exception("Test error")
    payload = {
        "action_id": "act-123",
        "plant_id": "test-plant",
        "action_type": "HOLD",
        "timestamp": "2023-01-01T00:00:00Z",
        "commitment_gap_mwh": 0.0,
        "battery_discharge_mwh": 0.0,
        "market_buy_mwh": 0.0,
        "estimated_cost_eur": 0.0,
        "avoided_imbalance_cost_eur": 0.0
    }
    response = client.post("/commitment/actions/accept", json=payload)
    assert response.status_code == 500
    assert response.json()["detail"] == "An error occurred while accepting the action."

@patch("safenergy.api.routes.get_action_ledger")
def test_get_commitment_actions_exception(mock_ledger):
    mock_instance = mock_ledger.return_value
    mock_instance.get_actions.side_effect = Exception("Test error")
    response = client.get("/commitment/actions")
    assert response.status_code == 500
    assert response.json()["detail"] == "An error occurred while retrieving accepted actions."

def test_get_commitment_metrics_exception_real():
    with patch("safenergy.api.routes.get_action_ledger") as mock_ledger:
        mock_instance = mock_ledger.return_value
        mock_instance.get_actions.side_effect = Exception("Test error")
        response = client.get("/commitment/metrics")
        assert response.status_code == 500
        assert response.json()["detail"] == "An error occurred while calculating commitment metrics."

def test_dashboard_overview_exception_plants():
    # If get_all_plants throws an unhandled exception, FastAPI returns a 500 automatically.
    # To test this gracefully we would need a try except in the route, but since there isn't one
    # it throws a 500 Internal Server Error.
    # Because of how TestClient works it bubbles up the 500 Exception, so we can catch it with pytest.raises
    with patch("safenergy.api.routes.get_all_plants") as mock_plants:
        mock_plants.side_effect = Exception("Test error")
        with pytest.raises(Exception, match="Test error"):
            client.get("/dashboard/overview")

def test_dashboard_overview_exception_subcomponents():
    # Test that when subcomponents throw exceptions, they are caught and fallback values are used.
    # We patch the inner functions called by get_dashboard_overview to raise exceptions
    with patch("safenergy.api.routes.get_all_plants") as mock_plants, \
         patch("safenergy.api.routes.get_market_prices") as mock_market, \
         patch("safenergy.api.routes.get_commitment_metrics") as mock_metrics, \
         patch("safenergy.api.routes.get_commitment_actions") as mock_actions, \
         patch("safenergy.api.routes.get_plant_health") as mock_health, \
         patch("safenergy.api.routes.get_weather_live") as mock_weather, \
         patch("safenergy.api.routes.get_forecast") as mock_forecast:

         mock_plants.return_value = [{
            "plant_id": "test-plant-001",
            "name": "Test Plant",
            "latitude": 52.52,
            "longitude": 13.40,
            "timezone": "Europe/Berlin",
            "capacity_mw": 10.0,
            "status": "active",
            "battery_capacity_mwh": 0.0,
            "metadata_dict": {}
         }]

         mock_market.side_effect = Exception("Market error")
         mock_metrics.side_effect = Exception("Metrics error")
         mock_actions.side_effect = Exception("Actions error")
         mock_health.side_effect = Exception("Health error")
         mock_weather.side_effect = Exception("Weather error")
         mock_forecast.side_effect = Exception("Forecast error")

         response = client.get("/dashboard/overview")
         assert response.status_code == 200
         data = response.json()

         assert data["market_prices"]["provenance"] == "none"
         assert data["market_prices"]["points"] == []

         assert data["portfolio_metrics"]["total_shortfall_mwh"] == 0.0
         assert data["recent_actions"] == []

         plant_overview = data["plants"][0]
         assert plant_overview["health"]["status"] == "unknown"
         assert plant_overview["weather_live"] is None
         assert plant_overview["forecast_nowcast"] is None

@patch("safenergy.api.routes.forecast_serving")
def test_predict_forecast_exception(mock_serving):
    mock_serving.side_effect = Exception("Test error")
    payload = {
        "asset_id": "test",
        "features": [{"timestamp": "2023-01-01T00:00:00Z", "features": {"temperature": 15.0}}]
    }
    response = client.post("/forecast/predict", json=payload)
    assert response.status_code == 500
    assert response.json()["detail"] == "An error occurred during forecast prediction."

@patch("safenergy.api.routes.forecast_serving")
def test_predict_forecast_no_data(mock_serving):
    payload = {
        "asset_id": "test",
        "features": []
    }
    response = client.post("/forecast/predict", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "No features provided"

def test_get_forecast_exception():
    with patch("safenergy.api.routes.get_plant_by_id") as mock_get_plant:
        mock_get_plant.return_value = {
            "plant_id": "test",
            "name": "test",
            "latitude": 50.0,
            "longitude": 10.0,
            "timezone": "UTC",
            "capacity_mw": 10.0,
            "status": "active",
            "battery_capacity_mwh": 0.0,
            "metadata_dict": {}
        }
        with patch("safenergy.api.routes.fetch_weather_forecast") as mock_weather:
            mock_weather.side_effect = Exception("Test error")
            response = client.get("/forecast/test?horizon_minutes=60")
            assert response.status_code == 500
            assert "Error fetching weather: Test error" in response.json()["detail"]

def test_weather_live_empty_data():
    with patch("safenergy.api.routes.get_plant_by_id") as mock_get_plant:
        mock_get_plant.return_value = {
            "plant_id": "test",
            "name": "test",
            "latitude": 50.0,
            "longitude": 10.0,
            "timezone": "UTC",
            "capacity_mw": 10.0,
            "status": "active",
            "battery_capacity_mwh": 0.0,
            "metadata_dict": {}
        }
        with patch("safenergy.api.routes.fetch_weather_forecast") as mock_weather:
            import pandas as pd
            mock_weather.return_value = pd.DataFrame()
            response = client.get("/weather/live?plant_id=test")
            assert response.status_code == 500
            assert response.json()["detail"] == "Weather data is empty"

def test_weather_live_no_current_hour():
    with patch("safenergy.api.routes.get_plant_by_id") as mock_get_plant:
        mock_get_plant.return_value = {
            "plant_id": "test",
            "name": "test",
            "latitude": 50.0,
            "longitude": 10.0,
            "timezone": "UTC",
            "capacity_mw": 10.0,
            "status": "active",
            "battery_capacity_mwh": 0.0,
            "metadata_dict": {}
        }
        with patch("safenergy.api.routes.fetch_weather_forecast") as mock_weather:
            from datetime import datetime, timedelta, timezone

            import pandas as pd
            # return future data only
            future = datetime.now(timezone.utc) + timedelta(hours=2)
            mock_weather.return_value = pd.DataFrame({"temperature_2m": [10.0]}, index=pd.DatetimeIndex([future]))
            response = client.get("/weather/live?plant_id=test")
            assert response.status_code == 500
            assert response.json()["detail"] == "Could not find current hour weather data"

def test_weather_forecast_empty_data():
    with patch("safenergy.api.routes.get_plant_by_id") as mock_get_plant:
        mock_get_plant.return_value = {
            "plant_id": "test",
            "name": "test",
            "latitude": 50.0,
            "longitude": 10.0,
            "timezone": "UTC",
            "capacity_mw": 10.0,
            "status": "active",
            "battery_capacity_mwh": 0.0,
            "metadata_dict": {}
        }
        with patch("safenergy.api.routes.fetch_weather_forecast") as mock_weather:
            import pandas as pd
            mock_weather.return_value = pd.DataFrame()
            response = client.get("/weather/forecast?plant_id=test&hours=2")
            assert response.status_code == 500
            assert response.json()["detail"] == "Weather data is empty"

def test_market_prices_exception():
    with patch("safenergy.api.routes.fetch_delu_prices") as mock_fetch:
        mock_fetch.side_effect = Exception("Test error")
        response = client.get("/market/prices?zone=DE-LU&hours=1")
        assert response.status_code == 500
        assert "Error fetching market prices: Test error" in response.json()["detail"]

def test_market_prices_empty():
    with patch("safenergy.api.routes.fetch_delu_prices") as mock_fetch:
        from datetime import datetime, timezone

        import pandas as pd

        from safenergy.ingest.market import MarketDataDiagnostic, MarketDataResponse
        diag = MarketDataDiagnostic(status="empty_result", records_returned=0)
        resp = MarketDataResponse(
            provider="DE-LU-Mock",
            region="DE-LU",
            issue_time=datetime.now(timezone.utc),
            valid_time_start=datetime.now(timezone.utc),
            valid_time_end=datetime.now(timezone.utc),
            diagnostic=diag,
            data=pd.DataFrame()
        )
        mock_fetch.return_value = resp
        response = client.get("/market/prices?zone=DE-LU&hours=1")
        assert response.status_code == 500
        assert response.json()["detail"] == "Market prices data is empty or unavailable."

@patch("safenergy.api.routes.get_plant_by_id")
def test_get_forecast_plant_not_found(mock_get_plant):
    mock_get_plant.return_value = None
    response = client.get("/forecast/non-existent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Plant non-existent not found"

@patch("safenergy.api.routes.get_plant_by_id")
def test_weather_forecast_plant_not_found(mock_get_plant):
    mock_get_plant.return_value = None
    response = client.get("/weather/forecast?plant_id=non-existent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Plant non-existent not found"

def test_orchestrator_exception():
    with patch("safenergy.api.routes.run_end_to_end_pipeline") as mock_pipeline:
        mock_pipeline.side_effect = Exception("Test error")
        payload = {
            "asset_id": "test",
            "latitude": 50.0,
            "longitude": 10.0,
            "start_date": "2023-01-01T00:00:00Z",
            "end_date": "2023-01-01T01:00:00Z"
        }
        response = client.post("/orchestrator/run", json=payload)
        assert response.status_code == 500
        assert response.json()["detail"] == "An error occurred during orchestrator pipeline execution."

@patch("safenergy.api.routes.get_plant_by_id")
@patch("safenergy.api.routes.fetch_weather_forecast")
def test_weather_live_no_tz(mock_weather, mock_get_plant):
    # Coverage for df.index.tz is None branch
    mock_get_plant.return_value = {
        "plant_id": "test",
        "name": "test",
        "latitude": 50.0,
        "longitude": 10.0,
        "timezone": "UTC",
        "capacity_mw": 10.0,
        "status": "active",
        "battery_capacity_mwh": 0.0,
        "metadata_dict": {}
    }
    from datetime import datetime

    import pandas as pd
    # Naive datetime
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    df = pd.DataFrame({"temperature_2m": [10.0], "cloud_cover": [0.0], "wind_speed_10m": [0.0], "shortwave_radiation": [0.0]}, index=pd.DatetimeIndex([now]))
    mock_weather.return_value = df
    response = client.get("/weather/live?plant_id=test")
    assert response.status_code == 200

@patch("safenergy.api.routes.get_plant_by_id")
@patch("safenergy.api.routes.fetch_weather_forecast")
def test_weather_forecast_no_tz(mock_weather, mock_get_plant):
    mock_get_plant.return_value = {
        "plant_id": "test",
        "name": "test",
        "latitude": 50.0,
        "longitude": 10.0,
        "timezone": "UTC",
        "capacity_mw": 10.0,
        "status": "active",
        "battery_capacity_mwh": 0.0,
        "metadata_dict": {}
    }
    from datetime import datetime

    import pandas as pd
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    df = pd.DataFrame({"temperature_2m": [10.0], "cloud_cover": [0.0], "wind_speed_10m": [0.0], "shortwave_radiation": [0.0]}, index=pd.DatetimeIndex([now]))
    mock_weather.return_value = df
    response = client.get("/weather/forecast?plant_id=test&hours=2")
    assert response.status_code == 200

@patch("safenergy.api.routes.get_plant_by_id")
@patch("safenergy.api.routes.fetch_weather_forecast")
@patch("safenergy.api.routes.forecast_serving")
def test_get_forecast_no_tz(mock_serving, mock_weather, mock_get_plant):
    mock_get_plant.return_value = {
        "plant_id": "test",
        "name": "test",
        "latitude": 50.0,
        "longitude": 10.0,
        "timezone": "UTC",
        "capacity_mw": 10.0,
        "status": "active",
        "battery_capacity_mwh": 0.0,
        "metadata_dict": {}
    }
    from datetime import datetime

    import pandas as pd
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    df = pd.DataFrame({"temperature_2m": [10.0], "cloud_cover": [0.0], "wind_speed_10m": [0.0], "shortwave_radiation": [0.0]}, index=pd.DatetimeIndex([now]))
    mock_weather.return_value = df

    mock_serving.return_value = pd.DataFrame({"point": [10.0], "method": ["pvlib_physical"]}, index=pd.DatetimeIndex([now + pd.Timedelta(hours=1)]).tz_localize("UTC"))

    response = client.get("/forecast/test?horizon_minutes=60")
    assert response.status_code == 200

@patch("safenergy.api.routes.fetch_delu_prices")
def test_market_prices_no_tz(mock_fetch):
    from datetime import datetime, timezone

    import pandas as pd

    from safenergy.ingest.market import MarketDataDiagnostic, MarketDataResponse
    now = datetime.now(timezone.utc)
    # Naive index
    idx = pd.DatetimeIndex([datetime.utcnow().replace(minute=0, second=0, microsecond=0)])
    df = pd.DataFrame({
        "day_ahead_eur_mwh": [10.0],
        "intraday_eur_mwh": [10.0],
        "balancing_short_eur_mwh": [10.0],
        "balancing_long_eur_mwh": [10.0]
    }, index=idx)
    diag = MarketDataDiagnostic(status="ok", records_returned=1)
    resp = MarketDataResponse(
        provider="DE-LU-Mock",
        region="DE-LU",
        issue_time=now,
        valid_time_start=now,
        valid_time_end=now,
        diagnostic=diag,
        data=df
    )
    mock_fetch.return_value = resp
    response = client.get("/market/prices?zone=DE-LU&hours=1")
    assert response.status_code == 200

def test_get_dashboard_overview_plants_unhandled_exception():
    with patch("safenergy.api.routes.get_all_plants") as mock_plants:
        mock_plants.side_effect = Exception("Unhandled plants error")
        with pytest.raises(Exception, match="Unhandled plants error"):
            client.get("/dashboard/overview")
