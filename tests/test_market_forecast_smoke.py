from fastapi.testclient import TestClient

from safenergy.api.main import app

client = TestClient(app)

def test_market_forecast_smoke_path():
    """
    Smoke test to verify the plant to weather to forecast to market smoke path
    works deterministically for the frontend demo.
    """
    # 1. Get Plant
    resp_plant = client.get("/plants/pv-texas-01")
    assert resp_plant.status_code == 200
    plant_data = resp_plant.json()
    plant_id = plant_data["plant_id"]
    assert plant_id == "pv-texas-01"

    # 2. Get Weather
    resp_weather = client.get(f"/weather/forecast?plant_id={plant_id}&hours=24")
    assert resp_weather.status_code == 200
    weather_data = resp_weather.json()
    assert len(weather_data.get("points", [])) > 0

    # 3. Get Forecast
    resp_forecast = client.get(f"/forecast/{plant_id}?horizon_minutes=60")
    assert resp_forecast.status_code == 200
    forecast_data = resp_forecast.json()
    assert len(forecast_data.get("predictions", [])) > 0
    assert forecast_data["asset_id"] == plant_id

    # 4. Get Market Prices
    resp_market = client.get("/market/prices?zone=DE-LU&hours=1")
    assert resp_market.status_code == 200
    market_data = resp_market.json()
    assert len(market_data.get("points", [])) > 0
    assert market_data["zone"] == "DE-LU"
