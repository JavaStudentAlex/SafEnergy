import pandas as pd
import pvlib
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


def smart_persistence_baseline(
    df: pd.DataFrame, target_col: str, norm_col: str, horizon_hours: int, eps: float = 1e-4
) -> pd.Series:
    """
    Creates a smart persistence baseline forecast.
    Predicts that generation is proportional to a normalizing variable (like irradiance).
    generation_t = (generation_{t-h} / (norm_col_{t-h} + eps)) * norm_col_t

    Args:
        df: Input DataFrame containing target_col and norm_col with a timezone-aware DatetimeIndex.
        target_col: Name of the target column.
        norm_col: Name of the normalizing column (e.g., irradiance).
        horizon_hours: Forecast horizon in hours.
        eps: Small value to prevent division by zero.

    Returns:
        A pandas Series containing the smart persistence baseline forecast.
    """
    if df.empty or target_col not in df.columns or norm_col not in df.columns:
        return pd.Series(index=df.index, dtype=float)

    recent_gen = df[target_col].shift(horizon_hours)
    recent_norm = df[norm_col].shift(horizon_hours)
    current_norm = df[norm_col]

    prediction = (recent_gen / (recent_norm + eps)) * current_norm
    return prediction


def pvlib_physical_baseline(
    df: pd.DataFrame,
    latitude: float,
    longitude: float,
    capacity_mw: float,
    irradiance_col: str = "irradiance",
    temp_col: str = "temperature"
) -> pd.Series:
    """
    Creates a physical baseline forecast for solar using pvlib.

    Args:
        df: Input DataFrame containing irradiance and temperature columns.
        latitude: Latitude of the solar asset.
        longitude: Longitude of the solar asset.
        capacity_mw: Installed capacity in MW.
        irradiance_col: Column name for irradiance (GHI) in W/m^2.
        temp_col: Column name for temperature in Celsius.

    Returns:
        A pandas Series containing the physical baseline forecast in MW.
    """
    if df.empty or irradiance_col not in df.columns or temp_col not in df.columns:
        return pd.Series(index=df.index, dtype=float)

    location = pvlib.location.Location(latitude, longitude)

    system = pvlib.pvsystem.PVSystem(
        arrays=[
            pvlib.pvsystem.Array(
                mount=pvlib.pvsystem.FixedMount(surface_tilt=latitude, surface_azimuth=180),
                module_parameters={"pdc0": capacity_mw, "gamma_pdc": -0.004},
            )
        ],
        inverter_parameters={"pdc0": capacity_mw, "eta_inv_nom": 0.96},
    )

    times = df.index
    solar_position = location.get_solarposition(times)

    ghi = df[irradiance_col]
    zenith = solar_position["zenith"]

    dni_dhi = pvlib.irradiance.erbs(ghi, zenith, times)
    dni = dni_dhi["dni"]
    dhi = dni_dhi["dhi"]

    poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt=system.arrays[0].mount.surface_tilt,
        surface_azimuth=system.arrays[0].mount.surface_azimuth,
        dni=dni,
        ghi=ghi,
        dhi=dhi,
        solar_zenith=zenith,
        solar_azimuth=solar_position["azimuth"],
    )

    temp_air = df[temp_col]
    cell_temp = pvlib.temperature.pvsyst_cell(poa["poa_global"], temp_air)

    dc = pvlib.pvsystem.pvwatts_dc(
        poa["poa_global"],
        cell_temp,
        system.arrays[0].module_parameters["pdc0"],
        system.arrays[0].module_parameters["gamma_pdc"],
    )

    ac = pvlib.inverter.pvwatts(
        dc,
        system.inverter_parameters["pdc0"],
        system.inverter_parameters["eta_inv_nom"],
    )

    ac = ac.fillna(0.0)
    ac = ac.clip(lower=0.0)

    return ac
