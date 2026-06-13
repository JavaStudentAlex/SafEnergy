import pandas as pd
import pytest

from safenergy.forecast.baselines import (
    persistence_baseline,
    pvlib_physical_baseline,
    same_hour_yesterday_baseline,
    smart_persistence_baseline,
    weather_only_baseline,
)


@pytest.fixture
def sample_generation_df():
    idx = pd.date_range(start="2023-01-01 00:00", periods=48, freq="1h", tz="UTC")
    # simple linear generation from 0 to 47
    return pd.DataFrame({"generation_mw": range(48)}, index=idx)


def test_persistence_baseline(sample_generation_df):
    horizon = 2
    baseline = persistence_baseline(sample_generation_df, "generation_mw", horizon)

    assert len(baseline) == 48
    assert pd.isna(baseline.iloc[0])
    assert pd.isna(baseline.iloc[1])

    # The prediction at index 2 should be the actual from index 0
    assert baseline.iloc[2] == sample_generation_df["generation_mw"].iloc[0]

    # Value at index 10 should be value at index 8
    assert baseline.iloc[10] == 8


def test_same_hour_yesterday_baseline(sample_generation_df):
    baseline = same_hour_yesterday_baseline(sample_generation_df, "generation_mw")

    assert len(baseline) == 48
    assert pd.isna(baseline.iloc[0])
    assert pd.isna(baseline.iloc[23])

    # The prediction at index 24 should be the actual from index 0
    assert baseline.iloc[24] == sample_generation_df["generation_mw"].iloc[0]

    # Value at index 40 should be value at index 16
    assert baseline.iloc[40] == 16


def test_baselines_with_missing_columns():
    idx = pd.date_range(start="2023-01-01 00:00", periods=5, freq="1h", tz="UTC")
    df = pd.DataFrame({"other_col": range(5)}, index=idx)

    b1 = persistence_baseline(df, "generation_mw", 1)
    b2 = same_hour_yesterday_baseline(df, "generation_mw")

    assert b1.isna().all()
    assert b2.isna().all()


def test_weather_only_baseline():
    # Create train data
    idx_train = pd.date_range(start="2023-01-01 00:00", periods=24, freq="1h", tz="UTC")
    train_df = pd.DataFrame(
        {
            "temperature": [10, 12, 14, 16] * 6,
            "irradiance": [0, 50, 100, 50] * 6,
            "generation_mw": [0, 5, 10, 5] * 6,  # 0.1 * irradiance
        },
        index=idx_train,
    )

    # Create test data
    idx_test = pd.date_range(start="2023-01-02 00:00", periods=4, freq="1h", tz="UTC")
    test_df = pd.DataFrame(
        {
            "temperature": [10, 12, 14, 16],
            "irradiance": [0, 20, 40, 20], # Expected generation: 0, 2, 4, 2
        },
        index=idx_test,
    )

    preds = weather_only_baseline(
        train_df, test_df, weather_cols=["temperature", "irradiance"], target_col="generation_mw"
    )

    assert len(preds) == 4
    assert not preds.isna().any()

    # Check if predictions are close to expected (0.1 * irradiance)
    # The regression should capture the exact relationship since we simulated it
    assert preds.iloc[0] == pytest.approx(0.0, abs=1e-5)
    assert preds.iloc[1] == pytest.approx(2.0, abs=1e-5)
    assert preds.iloc[2] == pytest.approx(4.0, abs=1e-5)
    assert preds.iloc[3] == pytest.approx(2.0, abs=1e-5)

def test_weather_only_baseline_missing_data():
    idx_train = pd.date_range(start="2023-01-01 00:00", periods=4, freq="1h", tz="UTC")
    train_df = pd.DataFrame(
        {
            "temp": [10, 10, 10, 10],
            "gen": [1, 1, 1, 1]
        },
        index=idx_train,
    )

    idx_test = pd.date_range(start="2023-01-01 04:00", periods=2, freq="1h", tz="UTC")
    test_df = pd.DataFrame({"temp": [10, None]}, index=idx_test)

    # Missing columns case
    preds1 = weather_only_baseline(train_df, test_df, ["temp", "missing"], "gen")
    assert preds1.isna().all()

    # Missing data in test case
    preds2 = weather_only_baseline(train_df, test_df, ["temp"], "gen")
    assert len(preds2) == 2
    assert not pd.isna(preds2.iloc[0])
    assert pd.isna(preds2.iloc[1])


def test_smart_persistence_baseline():
    idx = pd.date_range(start="2023-01-01 00:00", periods=4, freq="1h", tz="UTC")
    df = pd.DataFrame(
        {
            "generation": [10, 20, 30, 40],
            "irradiance": [100, 200, 150, 400],
        },
        index=idx,
    )

    horizon = 1
    baseline = smart_persistence_baseline(df, "generation", "irradiance", horizon)

    assert len(baseline) == 4
    assert pd.isna(baseline.iloc[0])

    # t=1: gen_t-1=10, irr_t-1=100, irr_t=200 -> pred = (10/100)*200 = 20
    assert baseline.iloc[1] == pytest.approx(20.0, abs=1e-3)

    # t=2: gen_t-1=20, irr_t-1=200, irr_t=150 -> pred = (20/200)*150 = 15
    assert baseline.iloc[2] == pytest.approx(15.0, abs=1e-3)

    # t=3: gen_t-1=30, irr_t-1=150, irr_t=400 -> pred = (30/150)*400 = 80
    assert baseline.iloc[3] == pytest.approx(80.0, abs=1e-3)


def test_smart_persistence_baseline_missing_cols():
    idx = pd.date_range(start="2023-01-01 00:00", periods=2, freq="1h", tz="UTC")
    df = pd.DataFrame({"gen": [10, 20]}, index=idx)

    # Missing norm_col
    preds1 = smart_persistence_baseline(df, "gen", "irr", 1)
    assert preds1.isna().all()

    # Missing target_col
    preds2 = smart_persistence_baseline(df, "target", "gen", 1)
    assert preds2.isna().all()


def test_pvlib_physical_baseline():
    idx = pd.date_range(start="2023-01-01 12:00", periods=3, freq="1h", tz="UTC")
    df = pd.DataFrame(
        {
            "irradiance": [0, 500, 1000],
            "temperature": [10, 20, 30],
        },
        index=idx,
    )

    # Austin, TX approx
    lat = 30.2672
    lon = -97.7431
    capacity = 100.0  # MW

    baseline = pvlib_physical_baseline(
        df,
        latitude=lat,
        longitude=lon,
        capacity_mw=capacity,
        irradiance_col="irradiance",
        temp_col="temperature",
    )

    assert len(baseline) == 3
    assert not baseline.isna().any()

    # 0 irradiance should give 0 MW
    assert baseline.iloc[0] == pytest.approx(0.0, abs=1e-2)

    # Higher irradiance should give higher generation (up to capacity approx)
    assert baseline.iloc[1] > 0
    assert baseline.iloc[2] > baseline.iloc[1]


def test_pvlib_physical_baseline_missing_cols():
    idx = pd.date_range(start="2023-01-01 12:00", periods=2, freq="1h", tz="UTC")
    df = pd.DataFrame({"irr": [100, 200]}, index=idx)

    baseline = pvlib_physical_baseline(
        df,
        latitude=30.0,
        longitude=-97.0,
        capacity_mw=10.0,
        irradiance_col="irradiance",
        temp_col="temperature",
    )

    assert baseline.isna().all()
