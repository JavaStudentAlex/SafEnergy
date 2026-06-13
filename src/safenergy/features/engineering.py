import logging
from typing import Tuple

import pandas as pd


def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds hour, day_of_week, month, and day_of_year columns based on the timezone-aware UTC index.
    """
    if df.empty:
        return df.copy()

    df_out = df.copy()
    if df_out.index.tz is None:
        df_out.index = df_out.index.tz_localize("UTC")
    else:
        df_out.index = df_out.index.tz_convert("UTC")

    df_out["hour"] = df_out.index.hour
    df_out["day_of_week"] = df_out.index.dayofweek
    df_out["month"] = df_out.index.month
    df_out["day_of_year"] = df_out.index.dayofyear
    return df_out


def create_lagged_features(df: pd.DataFrame, column: str, lags: list[int], horizon_hours: int) -> pd.DataFrame:
    """
    Adds lagged features avoiding data leakage.
    For a given horizon_hours, the lag must be >= horizon_hours.
    """
    if df.empty or column not in df.columns:
        return df.copy()

    df_out = df.copy()
    for lag in lags:
        if lag < horizon_hours:
            logging.warning(f"Lag {lag}h is less than horizon {horizon_hours}h. Skipping to prevent leakage.")
            continue
        df_out[f"{column}_lag_{lag}h"] = df_out[column].shift(lag)

    return df_out


def create_target_deltas(df: pd.DataFrame, columns: list[str], baseline_lag: int = 24) -> pd.DataFrame:
    """
    Calculates the difference between current generation and a baseline (like 24h lag) to predict generation changes.
    """
    if df.empty:
        return df.copy()

    df_out = df.copy()
    for col in columns:
        if col not in df_out.columns:
            continue
        # Ensure we have the baseline lag
        baseline_col = f"{col}_lag_{baseline_lag}h"
        if baseline_col not in df_out.columns:
            df_out[baseline_col] = df_out[col].shift(baseline_lag)

        # Delta = actual - baseline
        df_out[f"{col}_change"] = df_out[col] - df_out[baseline_col]

    return df_out


def split_temporal(df: pd.DataFrame, split_timestamp: pd.Timestamp) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits the dataframe into train and test sets chronologically at the split_timestamp.
    """
    if df.empty:
        return df.copy(), df.copy()

    # Ensure timezone aware
    if split_timestamp.tzinfo is None:
        split_timestamp = split_timestamp.tz_localize("UTC")
    else:
        split_timestamp = split_timestamp.tz_convert("UTC")

    if df.index.tz is None:
        df_out = df.copy()
        df_out.index = df_out.index.tz_localize("UTC")
    else:
        df_out = df.copy()
        df_out.index = df_out.index.tz_convert("UTC")

    train_df = df_out[df_out.index < split_timestamp]
    test_df = df_out[df_out.index >= split_timestamp]

    return train_df, test_df
