import pandas as pd
import pytest

from safenergy.features.alignment import align_weather_and_generation
from safenergy.features.engineering import (
    create_lagged_features,
    create_target_deltas,
    create_time_features,
    split_temporal,
)


@pytest.fixture
def sample_weather_df():
    idx = pd.date_range(start="2023-01-01 00:00", periods=5, freq="1h", tz="UTC")
    return pd.DataFrame({"temperature_2m": [10, 11, 12, 11, 10]}, index=idx)


@pytest.fixture
def sample_generation_df():
    idx = pd.date_range(start="2023-01-01 00:00", periods=5, freq="1h", tz="UTC")
    return pd.DataFrame({"solar_generation_mw": [0, 50, 100, 50, 0]}, index=idx)


def test_align_weather_and_generation(sample_weather_df, sample_generation_df):
    aligned = align_weather_and_generation(sample_weather_df, sample_generation_df)
    assert not aligned.empty
    assert "temperature_2m" in aligned.columns
    assert "solar_generation_mw" in aligned.columns
    assert str(aligned.index.tz) == "UTC"
    assert len(aligned) == 5


def test_create_time_features(sample_weather_df):
    df_feat = create_time_features(sample_weather_df)
    assert "hour" in df_feat.columns
    assert "day_of_week" in df_feat.columns
    assert "month" in df_feat.columns
    assert "day_of_year" in df_feat.columns
    assert df_feat["hour"].iloc[0] == 0
    assert df_feat["hour"].iloc[2] == 2


def test_create_lagged_features():
    idx = pd.date_range(start="2023-01-01 00:00", periods=48, freq="1h", tz="UTC")
    df = pd.DataFrame({"solar_generation_mw": range(48)}, index=idx)

    # Lag 24, horizon 24 -> allowed
    # Lag 12, horizon 24 -> blocked (leakage)
    df_lagged = create_lagged_features(df, "solar_generation_mw", lags=[12, 24], horizon_hours=24)

    assert "solar_generation_mw_lag_24h" in df_lagged.columns
    assert "solar_generation_mw_lag_12h" not in df_lagged.columns
    assert pd.isna(df_lagged["solar_generation_mw_lag_24h"].iloc[0])
    assert df_lagged["solar_generation_mw_lag_24h"].iloc[24] == 0


def test_create_target_deltas():
    idx = pd.date_range(start="2023-01-01 00:00", periods=48, freq="1h", tz="UTC")
    df = pd.DataFrame({"solar_generation_mw": range(48)}, index=idx)

    df_deltas = create_target_deltas(df, ["solar_generation_mw"], baseline_lag=24)
    assert "solar_generation_mw_change" in df_deltas.columns
    assert "solar_generation_mw_lag_24h" in df_deltas.columns

    # Delta at index 24 (value 24) compared to index 0 (value 0) should be 24
    assert df_deltas["solar_generation_mw_change"].iloc[24] == 24


def test_split_temporal():
    idx = pd.date_range(start="2023-01-01 00:00", periods=10, freq="1h", tz="UTC")
    df = pd.DataFrame({"value": range(10)}, index=idx)

    split_time = pd.Timestamp("2023-01-01 05:00", tz="UTC")
    train, test = split_temporal(df, split_time)

    assert len(train) == 5
    assert len(test) == 5
    assert train.index.max() < split_time
    assert test.index.min() == split_time
