import os
import tempfile

import pandas as pd
import pytest

from safenergy.forecast.models import LightGBMForecaster


@pytest.fixture
def sample_training_data():
    idx = pd.date_range(start="2023-01-01 00:00", periods=100, freq="1h", tz="UTC")

    # Create simple predictable data
    # y = 2 * x1 + 0.5 * x2 + noise
    df = pd.DataFrame(
        {
            "temperature": [10 + i * 0.1 for i in range(100)],
            "irradiance": [0 if i % 24 < 6 or i % 24 > 18 else 500 for i in range(100)],
        },
        index=idx,
    )

    y = 2 * df["temperature"] + 0.05 * df["irradiance"]

    return df, y


@pytest.fixture
def sample_test_data():
    idx = pd.date_range(start="2023-01-05 04:00", periods=20, freq="1h", tz="UTC")

    df = pd.DataFrame(
        {
            "temperature": [15 + i * 0.1 for i in range(20)],
            "irradiance": [0 if i % 24 < 6 or i % 24 > 18 else 500 for i in range(20)],
        },
        index=idx,
    )
    return df


def test_lightgbm_point_forecast(sample_training_data, sample_test_data):
    X_train, y_train = sample_training_data
    X_test = sample_test_data

    model = LightGBMForecaster(params={"n_estimators": 10, "random_state": 42, "verbose": -1})
    model.fit(X_train, y_train)

    preds = model.predict(X_test, return_uncertainty=False)

    assert isinstance(preds, pd.Series)
    assert len(preds) == len(X_test)
    assert preds.index.equals(X_test.index)
    assert preds.name == "point"
    assert not preds.isna().any()


def test_lightgbm_uncertainty_forecast(sample_training_data, sample_test_data):
    X_train, y_train = sample_training_data
    X_test = sample_test_data

    model = LightGBMForecaster(quantiles=(0.1, 0.5, 0.9), params={"n_estimators": 10, "random_state": 42, "verbose": -1})
    model.fit(X_train, y_train)

    preds_df = model.predict(X_test, return_uncertainty=True)

    assert isinstance(preds_df, pd.DataFrame)
    assert len(preds_df) == len(X_test)
    assert preds_df.index.equals(X_test.index)
    assert list(preds_df.columns) == ["lower", "point", "upper"]
    assert not preds_df.isna().any().any()

    # Ensure valid bounds
    assert (preds_df["lower"] <= preds_df["point"]).all()
    assert (preds_df["point"] <= preds_df["upper"]).all()


def test_lightgbm_unfitted_model_raises_error(sample_test_data):
    X_test = sample_test_data
    model = LightGBMForecaster()

    with pytest.raises(ValueError, match="Model is not fitted yet"):
        model.predict(X_test)


def test_lightgbm_serialization(sample_training_data, sample_test_data):
    X_train, y_train = sample_training_data
    X_test = sample_test_data

    model = LightGBMForecaster(params={"n_estimators": 5, "random_state": 42, "verbose": -1})
    model.fit(X_train, y_train)

    original_preds = model.predict(X_test, return_uncertainty=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "model.joblib")

        # Save model
        model.save(filepath)
        assert os.path.exists(filepath)

        # Load model
        loaded_model = LightGBMForecaster.load(filepath)

        # Verify predictions match
        loaded_preds = loaded_model.predict(X_test, return_uncertainty=True)
        pd.testing.assert_frame_equal(original_preds, loaded_preds)
