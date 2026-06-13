import sys

from fastapi.testclient import TestClient

from safenergy.api.main import app

client = TestClient(app)

def run_market_forecast_smoke():
    print("Starting Market & Forecast End-to-End Smoke Check...")

    # 1. Get Plant
    print("Fetching plant data for pv-texas-01...")
    resp_plant = client.get("/plants/pv-texas-01")
    if resp_plant.status_code != 200:
        print(f"  ✗ Failed to fetch plant: {resp_plant.status_code} {resp_plant.text}")
        return False
    plant_data = resp_plant.json()
    plant_id = plant_data["plant_id"]
    print(f"  ✓ Fetched plant {plant_id}")

    # 2. Get Weather
    print(f"Fetching weather for plant {plant_id}...")
    resp_weather = client.get(f"/weather/forecast?plant_id={plant_id}&hours=24")
    if resp_weather.status_code != 200:
        print(f"  ✗ Failed to fetch weather: {resp_weather.status_code} {resp_weather.text}")
        return False
    weather_data = resp_weather.json()
    print(f"  ✓ Fetched {len(weather_data.get('points', []))} weather points")

    # 3. Get Forecast
    print(f"Fetching forecast for plant {plant_id}...")
    resp_forecast = client.get(f"/forecast/{plant_id}?horizon_minutes=60")
    if resp_forecast.status_code != 200:
        print(f"  ✗ Failed to fetch forecast: {resp_forecast.status_code} {resp_forecast.text}")
        return False
    forecast_data = resp_forecast.json()
    print(f"  ✓ Fetched {len(forecast_data.get('predictions', []))} forecast predictions")

    # 4. Get Market Prices
    print("Fetching DE-LU market prices...")
    resp_market = client.get("/market/prices?zone=DE-LU&hours=1")
    if resp_market.status_code != 200:
        print(f"  ✗ Failed to fetch market prices: {resp_market.status_code} {resp_market.text}")
        return False
    market_data = resp_market.json()
    print(f"  ✓ Fetched {len(market_data.get('points', []))} market price points")

    print("Market & Forecast Smoke Check completed successfully!")
    return True

if __name__ == "__main__":
    success = run_market_forecast_smoke()
    sys.exit(0 if success else 1)
