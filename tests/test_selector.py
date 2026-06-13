import pandas as pd
import pytest

from safenergy.forecast.selector import select_forecast_method


@pytest.fixture
def rich_solar_df():
    idx = pd.date_range(start="2023-01-01 12:00", periods=5, freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "generation": [10.0, 20.0, 30.0, 40.0, 50.0],
            "irradiance": [100.0, 200.0, 300.0, 400.0, 500.0],
            "temperature": [25.0, 26.0, 27.0, 28.0, 29.0],
        },
        index=idx,
    )


@pytest.fixture
def rich_wind_df():
    idx = pd.date_range(start="2023-01-01 12:00", periods=5, freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "generation": [10.0, 20.0, 30.0, 40.0, 50.0],
            "wind_speed": [5.0, 6.0, 7.0, 8.0, 9.0],
        },
        index=idx,
    )


def test_select_smart_persistence_solar(rich_solar_df):
    metadata = {"capacity_mw": 100.0, "latitude": 30.0, "longitude": -97.0}
    preds, meta = select_forecast_method(rich_solar_df, "solar", metadata)

    assert meta["method"] == "smart_persistence"
    assert meta["confidence_score"] == 0.8
    assert "generation" in meta["inputs_used"]
    assert "irradiance" in meta["inputs_used"]
    assert len(preds) == 5
    # First row is NaN due to shift
    assert pd.isna(preds.iloc[0])
    assert not pd.isna(preds.iloc[1])


def test_select_pvlib_physical_solar(rich_solar_df):
    # Drop generation to force fallback
    df = rich_solar_df.drop(columns=["generation"])
    metadata = {"capacity_mw": 100.0, "latitude": 30.0, "longitude": -97.0}

    preds, meta = select_forecast_method(df, "solar", metadata)

    assert meta["method"] == "pvlib_physical"
    assert meta["confidence_score"] == 0.6
    assert "irradiance" in meta["inputs_used"]
    assert "temperature" in meta["inputs_used"]
    assert "capacity_mw" in meta["inputs_used"]
    assert len(preds) == 5
    assert not preds.isna().any()


def test_select_wind_power_curve(rich_wind_df):
    # Drop generation to force fallback to power curve
    df = rich_wind_df.drop(columns=["generation"])
    metadata = {"capacity_mw": 100.0}

    preds, meta = select_forecast_method(df, "wind", metadata)

    assert meta["method"] == "wind_power_curve"
    assert meta["confidence_score"] == 0.6
    assert "wind_speed" in meta["inputs_used"]
    assert "capacity_mw" in meta["inputs_used"]
    assert len(preds) == 5
    assert not preds.isna().any()


def test_select_regional_capacity_fallback(rich_solar_df):
    # Drop irradiance and temperature to force fallback past physical
    df = rich_solar_df.drop(columns=["irradiance", "temperature"])
    # And generation to force fallback past persistence
    df = df.drop(columns=["generation"])

    metadata = {"capacity_mw": 100.0, "latitude": 30.0, "longitude": -97.0}

    preds, meta = select_forecast_method(df, "solar", metadata)

    assert meta["method"] == "regional_capacity"
    assert meta["confidence_score"] == 0.2
    assert "capacity_mw" in meta["inputs_used"]
    assert len(preds) == 5
    assert not preds.isna().any()
    # It uses 0.2 capacity factor for solar
    assert (preds == 20.0).all()


def test_select_diagnostic_fallback_empty_df():
    metadata = {"capacity_mw": 100.0}
    preds, meta = select_forecast_method(pd.DataFrame(), "solar", metadata)

    assert meta["method"] == "diagnostic_fallback"
    assert meta["confidence_score"] == 0.0
    assert len(preds) == 0


def test_select_diagnostic_fallback_missing_inputs(rich_solar_df):
    # Empty df, no metadata
    df = rich_solar_df.drop(columns=["generation", "irradiance", "temperature"])
    metadata = {} # no capacity

    preds, meta = select_forecast_method(df, "solar", metadata)

    assert meta["method"] == "diagnostic_fallback"
    assert meta["confidence_score"] == 0.0
    assert "capacity_mw" in meta["missing_inputs"]
    assert len(preds) == 5
    assert preds.isna().all()
