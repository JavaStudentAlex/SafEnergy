import numpy as np
import pandas as pd
import pytest

from safenergy.forecast.evaluate import (
    calculate_metrics,
    evaluate_forecast,
    temporal_split,
)


def test_calculate_metrics() -> None:
    y_true = pd.Series([10.0, 20.0, 30.0, 40.0])
    y_pred = pd.Series([12.0, 18.0, 33.0, 40.0])

    # errors: -2, 2, -3, 0
    # squared: 4, 4, 9, 0 -> sum=17, mean=4.25, rmse=2.0615528
    # abs: 2, 2, 3, 0 -> mean = 1.75
    # bias (pred - true): 2, -2, 3, 0 -> mean = 0.75

    metrics = calculate_metrics(y_true, y_pred)

    assert "rmse" in metrics
    assert "mae" in metrics
    assert "mbe" in metrics

    np.testing.assert_almost_equal(metrics["rmse"], np.sqrt(4.25))
    np.testing.assert_almost_equal(metrics["mae"], 1.75)
    np.testing.assert_almost_equal(metrics["mbe"], 0.75)

def test_calculate_metrics_with_nans() -> None:
    y_true = pd.Series([10.0, 20.0, np.nan, 40.0])
    y_pred = pd.Series([12.0, np.nan, 33.0, 40.0])

    # Valid pairs: (10, 12), (40, 40)
    # errors: -2, 0
    # squared: 4, 0 -> mean=2.0, rmse=sqrt(2)
    # abs: 2, 0 -> mean=1.0
    # bias: 2, 0 -> mean=1.0

    metrics = calculate_metrics(y_true, y_pred)

    np.testing.assert_almost_equal(metrics["rmse"], np.sqrt(2.0))
    np.testing.assert_almost_equal(metrics["mae"], 1.0)
    np.testing.assert_almost_equal(metrics["mbe"], 1.0)

def test_calculate_metrics_empty() -> None:
    y_true = pd.Series([], dtype=float)
    y_pred = pd.Series([], dtype=float)

    metrics = calculate_metrics(y_true, y_pred)

    assert np.isnan(metrics["rmse"])
    assert np.isnan(metrics["mae"])
    assert np.isnan(metrics["mbe"])

def test_evaluate_forecast() -> None:
    df = pd.DataFrame({
        "target": [10.0, 20.0, 30.0, 40.0],
        "model": [12.0, 18.0, 33.0, 40.0],  # rmse ~ 2.06
        "baseline": [15.0, 15.0, 25.0, 45.0] # errors: -5, 5, 5, -5. rmse: 5
    })

    report = evaluate_forecast(df, "target", "model", "baseline")

    assert list(report.index) == ["rmse", "mae", "mbe"]
    assert "model" in report.columns
    assert "baseline" in report.columns
    assert "improvement_pct" in report.columns

    # model rmse < baseline rmse, so improvement should be positive
    assert report.loc["rmse", "improvement_pct"] > 0

def test_temporal_split() -> None:
    dates = pd.date_range("2023-01-01", periods=10, freq="D", tz="UTC")
    df = pd.DataFrame({"value": range(10)}, index=dates)

    split_time = pd.Timestamp("2023-01-05", tz="UTC")
    train_df, test_df = temporal_split(df, split_time)

    assert len(train_df) == 4
    assert len(test_df) == 6
    assert train_df.index.max() < split_time
    assert test_df.index.min() == split_time

def test_temporal_split_tz_naive_fails() -> None:
    dates = pd.date_range("2023-01-01", periods=10, freq="D")
    df = pd.DataFrame({"value": range(10)}, index=dates)

    with pytest.raises(ValueError, match="timezone-aware"):
        temporal_split(df, pd.Timestamp("2023-01-05", tz="UTC"))

def test_temporal_split_split_time_tz_naive_fails() -> None:
    dates = pd.date_range("2023-01-01", periods=10, freq="D", tz="UTC")
    df = pd.DataFrame({"value": range(10)}, index=dates)

    with pytest.raises(ValueError, match="split_time must be timezone-aware"):
        temporal_split(df, "2023-01-05")

def test_temporal_split_empty() -> None:
    df = pd.DataFrame(index=pd.DatetimeIndex([], tz="UTC"))
    train_df, test_df = temporal_split(df, pd.Timestamp("2023-01-05", tz="UTC"))

    assert train_df.empty
    assert test_df.empty
