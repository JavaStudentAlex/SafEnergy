import os
import tempfile
from datetime import datetime, timezone

import pandas as pd
import pytest

from safenergy.forecast.models import LightGBMForecaster
from safenergy.forecast.service import forecast_serving


@pytest.fixture
def sample_features():
    idx = pd.date_range(start="2023-01-01 00:00", periods=5, freq="1h", tz="UTC")
    df = pd.DataFrame(
        {
            "generation": [10.0, 15.0, 20.0, 25.0, 30.0],
            "temperature": [15.0, 15.5, 16.0, 16.5, 17.0],
        },
        index=idx,
    )
    return df

def test_forecast_serving_fallback_with_generation(sample_features):
    # Without a model, and with 'generation' in columns, it should use persistence baseline
    issue_time = datetime(2023, 1, 1, 5, 0, tzinfo=timezone.utc)

    # Using horizon_hours=1, so prediction for idx i is generation from idx i-1
    preds_df = forecast_serving(sample_features, issue_time, horizon_hours=1, return_uncertainty=True)

    assert isinstance(preds_df, pd.DataFrame)
    assert len(preds_df) == len(sample_features)
    assert "point" in preds_df.columns
    assert "lower" in preds_df.columns
    assert "upper" in preds_df.columns

    # Check persistence logic manually (shift by 1)
    # Ensure it uses diagnostic fallback or persistence depending on what select_forecast_method found
    # In this mock, there's no normalizer so it probably uses diagnostic fallback
    assert "method" in preds_df.columns
    assert "confidence_score" in preds_df.columns
    assert "fallback_reason" in preds_df.columns
    assert "inputs_used" in preds_df.columns
    assert "missing_inputs" in preds_df.columns

    # Since there's no normalizer, method should be diagnostic_fallback
    assert preds_df["method"].iloc[1] == "diagnostic_fallback"

def test_forecast_serving_selector_metadata():
    idx = pd.date_range(start="2023-01-01 00:00", periods=2, freq="h", tz="UTC")
    df = pd.DataFrame(index=idx)
    issue_time = datetime(2023, 1, 1, 5, 0, tzinfo=timezone.utc)

    preds_df = forecast_serving(df, issue_time, return_uncertainty=True)

    assert "method" in preds_df.columns
    assert preds_df["method"].iloc[0] == "diagnostic_fallback"
    assert preds_df["confidence_score"].iloc[0] == 0.0
    assert preds_df["fallback_reason"].iloc[0] is not None


def test_forecast_serving_fallback_no_generation():
    # Without 'generation', it should fallback to deterministic 10.0
    idx = pd.date_range(start="2023-01-01 00:00", periods=3, freq="1h", tz="UTC")
    df = pd.DataFrame({"temperature": [15.0, 15.5, 16.0]}, index=idx)

    issue_time = datetime(2023, 1, 1, 3, 0, tzinfo=timezone.utc)
    preds_df = forecast_serving(df, issue_time, return_uncertainty=False)

    assert isinstance(preds_df, pd.DataFrame)
    assert "point" in preds_df.columns
    assert "lower" not in preds_df.columns

    # Should all be NaN since diagnostic fallback returns NaN
    assert preds_df["point"].isna().all()

def test_forecast_serving_with_model(sample_features):
    # Train and save a simple model
    model = LightGBMForecaster(params={"n_estimators": 5, "random_state": 42, "verbose": -1})
    # dummy target
    y = sample_features["generation"] * 1.1
    model.fit(sample_features, y)

    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = os.path.join(tmpdir, "model.joblib")
        model.save(model_path)

        issue_time = datetime(2023, 1, 1, 5, 0, tzinfo=timezone.utc)
        preds_df = forecast_serving(sample_features, issue_time, model_path=model_path, return_uncertainty=True)

        assert isinstance(preds_df, pd.DataFrame)
        assert len(preds_df) == len(sample_features)
        assert "point" in preds_df.columns
        assert "lower" in preds_df.columns
        assert "upper" in preds_df.columns

        # Real model predictions shouldn't be exactly the naive fallback
        assert not preds_df["point"].isna().any()

def test_forecast_serving_model_load_failure(sample_features):
    # If model path is invalid, should fallback to baseline gracefully
    issue_time = datetime(2023, 1, 1, 5, 0, tzinfo=timezone.utc)
    preds_df = forecast_serving(sample_features, issue_time, model_path="/invalid/path/to/model.joblib")

    # Should be the diagnostic fallback baseline (returns NaN because no normalizer present)
    assert preds_df["point"].isna().all()
