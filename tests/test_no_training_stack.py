from datetime import datetime, timezone

import pandas as pd
from fastapi.testclient import TestClient

from safenergy.api.main import app
from safenergy.forecast.selector import select_forecast_method

client = TestClient(app)

def test_no_training_stack_method_selection():
    """Test the deterministic method selection based on data availability."""
    idx = pd.date_range(start="2023-01-01 12:00", periods=5, freq="1h", tz="UTC")
    df_solar = pd.DataFrame(
        {
            "generation": [10.0, 20.0, 30.0, 40.0, 50.0],
            "irradiance": [100.0, 200.0, 300.0, 400.0, 500.0],
            "temperature": [25.0, 26.0, 27.0, 28.0, 29.0],
        },
        index=idx,
    )
    metadata_solar = {"capacity_mw": 100.0, "latitude": 30.0, "longitude": -97.0}

    # 1. Smart Persistence selection
    preds, meta = select_forecast_method(df_solar, "solar", metadata_solar)
    assert meta["method"] == "smart_persistence"
    assert meta["confidence_score"] == 0.8

    # 2. PVLib selection (drop generation)
    preds, meta = select_forecast_method(df_solar.drop(columns=["generation"]), "solar", metadata_solar)
    assert meta["method"] == "pvlib_physical"
    assert meta["confidence_score"] == 0.6

    # 3. Regional Capacity Fallback selection (drop irradiance/temp and generation)
    preds, meta = select_forecast_method(pd.DataFrame(index=idx), "solar", metadata_solar)
    assert meta["method"] == "regional_capacity"
    assert meta["confidence_score"] == 0.2

def test_no_training_stack_api_response_metadata():
    """Test that the API provides the metadata for no-training fallback methods."""
    now = datetime.now(timezone.utc).isoformat()
    # Provide data that will trigger pvlib_physical method (irradiance and temperature, no generation)
    payload = {
        "asset_id": "test-solar-asset",
        "asset_type": "solar",
        "metadata_dict": {"capacity_mw": 100.0, "latitude": 30.0, "longitude": -97.0},
        "features": [
            {
                "timestamp": now,
                "features": {"irradiance": 500.0, "temperature": 25.0}
            }
        ],
        "return_uncertainty": True
    }

    response = client.post("/forecast/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["predictions"]) == 1

    pred = data["predictions"][0]
    # Check that method, confidence, and inputs are returned appropriately
    assert pred["method"] == "pvlib_physical"
    assert pred["confidence_score"] == 0.6
    assert "irradiance" in pred["inputs_used"]
    assert pred["fallback_reason"] is not None
    # Uncertainty metadata should be valid since return_uncertainty was requested
    assert pred["point"] is not None
    assert pred["lower"] is not None
    assert pred["upper"] is not None
    assert pred["lower"] <= pred["point"] <= pred["upper"]

def test_no_training_stack_conservative_trading():
    """Test that low confidence yields conservative trading signals."""
    # When the method confidence is low, trading signals should be suppressed or conservative.
    now = datetime(2023, 1, 1, 10, tzinfo=timezone.utc).isoformat()

    payload = {
        "asset_id": "test-asset",
        "data": [
            {
                "timestamp": now,
                "delta": 30.0,
                "baseline": 50.0,
                "price": 20.0,
                "confidence": 0.2 # Extremely low confidence
            }
        ],
        "strong_threshold": 10.0,
        "weak_threshold": 5.0,
        "curtailment_price_threshold": -10.0,
        "extreme_price_threshold": 1000.0
    }

    response = client.post("/trading/signals", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    # Low confidence reduces any signal (which would otherwise be STRONG_LONG due to delta 30 > 10) to NEUTRAL.
    assert data[0]["adjusted_signal"] == 0 # NEUTRAL

    # Verify that high confidence gives the expected strong signal
    payload["data"][0]["confidence"] = 0.8
    response = client.post("/trading/signals", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["adjusted_signal"] == 2 # STRONG_LONG
