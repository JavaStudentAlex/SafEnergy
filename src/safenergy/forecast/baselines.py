import pandas as pd
from sklearn.linear_model import LinearRegression


def persistence_baseline(df: pd.DataFrame, target_col: str, horizon_hours: int) -> pd.Series:
    """
    Creates a persistence baseline forecast.
    Predicts that the generation for the forecast horizon will be the exact same
    as the most recent known observation (which is lagged by `horizon_hours`).

    Args:
        df: Input DataFrame containing the target column with a timezone-aware DatetimeIndex.
        target_col: The name of the target column to forecast.
        horizon_hours: The forecast horizon in hours.

    Returns:
        A pandas Series containing the persistence baseline forecast.
    """
    if df.empty or target_col not in df.columns:
        return pd.Series(index=df.index, dtype=float)

    # Shift the target by the horizon to represent the most recent known observation
    return df[target_col].shift(horizon_hours)


def weather_only_baseline(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    weather_cols: list[str],
    target_col: str
) -> pd.Series:
    """
    Creates a weather-only baseline forecast using a simple linear regression.
    It fits the model on train_df and predicts on test_df.

    Args:
        train_df: DataFrame containing training data.
        test_df: DataFrame containing data to predict on.
        weather_cols: List of column names representing weather features.
        target_col: The name of the target column to forecast.

    Returns:
        A pandas Series containing the weather-only baseline forecast, indexed to test_df.
    """
    # Check if we have all necessary columns
    required_cols = weather_cols + [target_col]
    missing_cols = [col for col in required_cols if col not in train_df.columns]

    if missing_cols or not weather_cols:
        return pd.Series(index=test_df.index, dtype=float)

    # Filter out missing data
    train_clean = train_df.dropna(subset=required_cols)

    if train_clean.empty:
        # Cannot fit model, return NaNs
        return pd.Series(index=test_df.index, dtype=float)

    X_train = train_clean[weather_cols]
    y_train = train_clean[target_col]

    model = LinearRegression()
    model.fit(X_train, y_train)

    # Check if test_df has the necessary columns
    missing_test_cols = [col for col in weather_cols if col not in test_df.columns]
    if missing_test_cols:
        return pd.Series(index=test_df.index, dtype=float)

    # For testing, we also need weather features.
    # If missing in test, prediction will be NaN for those rows.
    # We'll fill NA temporally or just predict and re-align
    X_test = test_df[weather_cols].copy()

    # Keep track of valid rows for prediction
    valid_test_idx = X_test.dropna().index
    if valid_test_idx.empty:
        return pd.Series(index=test_df.index, dtype=float)

    predictions = model.predict(X_test.loc[valid_test_idx])

    result = pd.Series(index=test_df.index, dtype=float)
    result.loc[valid_test_idx] = predictions

    return result


def same_hour_yesterday_baseline(df: pd.DataFrame, target_col: str) -> pd.Series:
    """
    Creates a same-hour-yesterday baseline forecast.
    Predicts that the generation will be the same as it was exactly 24 hours ago.

    Args:
        df: Input DataFrame containing the target column with a timezone-aware DatetimeIndex.
        target_col: The name of the target column to forecast.

    Returns:
        A pandas Series containing the same-hour-yesterday baseline forecast.
    """
    if df.empty or target_col not in df.columns:
        return pd.Series(index=df.index, dtype=float)

    # Shift the target by 24 hours
    return df[target_col].shift(24)
