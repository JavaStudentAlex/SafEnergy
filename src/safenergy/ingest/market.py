import datetime
import logging
from pathlib import Path

import pandas as pd


def check_market_quality(df: pd.DataFrame, expected_freq: str) -> None:
    """Checks market DataFrame for missing values and temporal continuity."""
    if df.empty:
        logging.warning("Market dataframe is empty.")
        return

    if df.isnull().values.any():
        logging.warning("Market dataframe contains missing values.")

    freq = pd.Timedelta(expected_freq)
    time_diffs = df.index.to_series().diff().dropna()
    if not (time_diffs == freq).all():
        logging.warning(f"Market dataframe has missing {expected_freq} intervals.")

def fetch_ercot_generation(
    start_date: datetime.date,
    end_date: datetime.date,
    fixture_path: Path | None = None,
) -> pd.DataFrame:
    """
    Fetches mock ERCOT generation data.
    Since external ERCOT APIs might not be available, this uses a fixture or generates deterministic mock data.
    Returns a DataFrame indexed by a timezone-aware (UTC) datetime.
    """
    if fixture_path and fixture_path.exists():
        df = pd.read_csv(fixture_path, parse_dates=["timestamp"])
        df.set_index("timestamp", inplace=True)
        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC")
        else:
            df.index = df.index.tz_convert("UTC")
        # Filter dates
        start_ts = pd.Timestamp(start_date, tz="UTC")
        end_ts = pd.Timestamp(end_date, tz="UTC") + pd.Timedelta(days=1)
        return df[(df.index >= start_ts) & (df.index < end_ts)]

    # Generate deterministic mock data
    dr = pd.date_range(start=start_date, end=end_date + datetime.timedelta(days=1), freq="1h", tz="UTC", inclusive="left")
    df = pd.DataFrame(index=dr)

    # Simple deterministic curves
    hour = df.index.hour

    # Solar peaks mid-day
    df["solar_generation_mw"] = 0.0
    mask_day = (hour >= 7) & (hour <= 19)
    df.loc[mask_day, "solar_generation_mw"] = 5000.0 * (1 - abs(hour[mask_day] - 13) / 6.0)
    df["solar_generation_mw"] = df["solar_generation_mw"].clip(lower=0.0)

    # Wind peaks at night
    df["wind_generation_mw"] = 10000.0 * (1 - abs(hour - 12) / 12.0)

    check_market_quality(df, '1h')
    return df


def fetch_ercot_prices(
    start_date: datetime.date,
    end_date: datetime.date,
    fixture_path: Path | None = None,
) -> pd.DataFrame:
    """
    Fetches mock ERCOT pricing data (e.g. Day-Ahead Market vs Real-Time Market).
    Returns a DataFrame indexed by a timezone-aware (UTC) datetime.
    """
    if fixture_path and fixture_path.exists():
        df = pd.read_csv(fixture_path, parse_dates=["timestamp"])
        df.set_index("timestamp", inplace=True)
        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC")
        else:
            df.index = df.index.tz_convert("UTC")
        start_ts = pd.Timestamp(start_date, tz="UTC")
        end_ts = pd.Timestamp(end_date, tz="UTC") + pd.Timedelta(days=1)
        return df[(df.index >= start_ts) & (df.index < end_ts)]

    # Generate deterministic mock data
    dr = pd.date_range(start=start_date, end=end_date + datetime.timedelta(days=1), freq="15min", tz="UTC", inclusive="left")
    df = pd.DataFrame(index=dr)

    # Prices spike during evening peak
    hour = df.index.hour
    df["rtm_price_usd_mwh"] = 20.0
    mask_peak = (hour >= 17) & (hour <= 20)
    df.loc[mask_peak, "rtm_price_usd_mwh"] = 80.0

    # DAM is smoother
    df["dam_price_usd_mwh"] = 25.0
    df.loc[mask_peak, "dam_price_usd_mwh"] = 60.0

    check_market_quality(df, '15min')
    return df
