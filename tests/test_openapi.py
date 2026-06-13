from fastapi.testclient import TestClient

from safenergy.api.main import app

client = TestClient(app)

def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema

    # Verify plants contract
    assert "/plants" in schema["paths"]
    assert "get" in schema["paths"]["/plants"]

    assert "/plants/{plant_id}" in schema["paths"]
    assert "get" in schema["paths"]["/plants/{plant_id}"]

    # Verify weather contract
    assert "/weather/live" in schema["paths"]
    assert "get" in schema["paths"]["/weather/live"]

    assert "/weather/forecast" in schema["paths"]
    assert "get" in schema["paths"]["/weather/forecast"]

    # Verify components/schemas exist for frontend contracts
    components = schema.get("components", {}).get("schemas", {})
    assert "PlantResponse" in components
    assert "WeatherResponse" in components
    assert "WeatherPoint" in components
