import logging
from datetime import datetime
from typing import Optional

import pandas as pd

from safenergy.ingest.market import GenerationDataResponse, MarketDataResponse


def align_weather_and_generation(
    weather_df: pd.DataFrame,
    generation_df: pd.DataFrame | GenerationDataResponse,
    issue_time: Optional[datetime] = None
) -> pd.DataFrame:
    """
    Aligns weather and generation data into a single feature DataFrame.
    Expects both dataframes to have a timezone-aware DatetimeIndex.
    Uses '1h' frequency.
    """
    if isinstance(generation_df, GenerationDataResponse):
        generation_df = generation_df.data

    if weather_df.empty or generation_df.empty:
        logging.warning("One of the dataframes is empty. Returning empty dataframe.")
        return pd.DataFrame()

    # Ensure timezone aware
    if weather_df.index.tz is None:
        weather_df.index = weather_df.index.tz_localize("UTC")
    else:
        weather_df.index = weather_df.index.tz_convert("UTC")

    if generation_df.index.tz is None:
        generation_df.index = generation_df.index.tz_localize("UTC")
    else:
        generation_df.index = generation_df.index.tz_convert("UTC")

    # Enforce issue time leakage guard
    if issue_time is not None:
        initial_weather_len = len(weather_df)
        initial_gen_len = len(generation_df)
        weather_df = weather_df[weather_df.index <= issue_time]
        generation_df = generation_df[generation_df.index <= issue_time]
        if len(weather_df) < initial_weather_len or len(generation_df) < initial_gen_len:
            logging.warning("Issue-time leakage prevented: some records were dropped because their valid time was > issue_time.")

    # Resample to 1h in case of missing or different frequencies, using interpolation or forward fill as needed
    # We use asfreq to ensure the index is strict 1h
    # In a real app we might want to interpolate or just drop NA, depending on the business logic.
    weather_resampled = weather_df.resample("1h").mean()
    generation_resampled = generation_df.resample("1h").mean()

    # We use an inner join since we need both weather and generation for supervised learning.
    # We can also do an outer join and fillna.
    aligned_df = weather_resampled.join(generation_resampled, how="outer")
    return aligned_df


def align_generation_and_prices(generation_df: pd.DataFrame | GenerationDataResponse, prices_df: pd.DataFrame | MarketDataResponse) -> pd.DataFrame:
    """
    Aligns generation and prices data into a single DataFrame on UTC valid time.
    Resamples prices (typically 15min) to hourly using mean aggregation, matching the generation data.
    """
    if isinstance(generation_df, GenerationDataResponse):
        generation_df = generation_df.data
    if isinstance(prices_df, MarketDataResponse):
        prices_df = prices_df.data

    if generation_df.empty or prices_df.empty:
        logging.warning("One of the dataframes is empty. Returning empty dataframe.")
        return pd.DataFrame()

    if generation_df.index.tz is None:
        generation_df.index = generation_df.index.tz_localize("UTC")
    else:
        generation_df.index = generation_df.index.tz_convert("UTC")

    if prices_df.index.tz is None:
        prices_df.index = prices_df.index.tz_localize("UTC")
    else:
        prices_df.index = prices_df.index.tz_convert("UTC")

    # Resample prices from 15min to 1h
    prices_resampled = prices_df.resample("1h").mean()
    generation_resampled = generation_df.resample("1h").mean()

    aligned_df = generation_resampled.join(prices_resampled, how="outer")
    return aligned_df
