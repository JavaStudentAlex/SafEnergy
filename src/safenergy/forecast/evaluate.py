from typing import Dict, Tuple, Union

import numpy as np
import pandas as pd


def calculate_metrics(y_true: pd.Series, y_pred: pd.Series) -> Dict[str, float]:
    """
    Calculate common forecasting metrics.

    Args:
        y_true: Actual values.
        y_pred: Predicted values.

    Returns:
        Dictionary containing RMSE, MAE, and MBE metrics.
    """
    # Align data to ensure we only evaluate where both true and pred exist
    df = pd.DataFrame({"true": y_true, "pred": y_pred}).dropna()

    if df.empty:
        return {"rmse": np.nan, "mae": np.nan, "mbe": np.nan}

    rmse = np.sqrt(((df["true"] - df["pred"]) ** 2).mean())
    mae = (df["true"] - df["pred"]).abs().mean()
    mbe = (df["pred"] - df["true"]).mean()

    return {
        "rmse": float(rmse),
        "mae": float(mae),
        "mbe": float(mbe)
    }

def evaluate_forecast(
    df: pd.DataFrame,
    target_col: str,
    model_pred_col: str,
    baseline_pred_col: str
) -> pd.DataFrame:
    """
    Evaluate a model forecast against a baseline forecast.

    Args:
        df: DataFrame containing the target, model predictions, and baseline predictions.
        target_col: Name of the actual target column.
        model_pred_col: Name of the model prediction column.
        baseline_pred_col: Name of the baseline prediction column.

    Returns:
        DataFrame comparing metrics and computing skill score.
    """
    model_metrics = calculate_metrics(df[target_col], df[model_pred_col])
    baseline_metrics = calculate_metrics(df[target_col], df[baseline_pred_col])

    # Calculate percentage improvement
    rmse_imp = np.nan
    if not np.isnan(model_metrics["rmse"]) and not np.isnan(baseline_metrics["rmse"]) and baseline_metrics["rmse"] > 0:
        rmse_imp = (baseline_metrics["rmse"] - model_metrics["rmse"]) / baseline_metrics["rmse"] * 100

    mae_imp = np.nan
    if not np.isnan(model_metrics["mae"]) and not np.isnan(baseline_metrics["mae"]) and baseline_metrics["mae"] > 0:
        mae_imp = (baseline_metrics["mae"] - model_metrics["mae"]) / baseline_metrics["mae"] * 100

    report = {
        "metric": ["rmse", "mae", "mbe"],
        "model": [model_metrics["rmse"], model_metrics["mae"], model_metrics["mbe"]],
        "baseline": [baseline_metrics["rmse"], baseline_metrics["mae"], baseline_metrics["mbe"]],
        "improvement_pct": [rmse_imp, mae_imp, np.nan] # Percent improvement on bias isn't as straightforward
    }

    return pd.DataFrame(report).set_index("metric")

def temporal_split(df: pd.DataFrame, split_time: Union[str, pd.Timestamp]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split a DataFrame temporally into train and test sets without leakage.
    Features used to predict must strictly reflect data available at or before the forecast issue time.

    Args:
        df: DataFrame with timezone-aware DatetimeIndex.
        split_time: Time to split on. Must be timezone-aware. Data before this time is train, data at or after is test.

    Returns:
        Tuple containing (train_df, test_df).
    """
    if df.empty:
        return df.copy(), df.copy()

    if df.index.tz is None:
        raise ValueError("DataFrame index must be timezone-aware.")

    split_ts = pd.to_datetime(split_time)
    if split_ts.tzinfo is None:
        raise ValueError("split_time must be timezone-aware.")

    train_df = df[df.index < split_ts].copy()
    test_df = df[df.index >= split_ts].copy()

    return train_df, test_df
