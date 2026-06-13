import logging

import pandas as pd


def align_weather_and_generation(weather_df: pd.DataFrame, generation_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aligns weather and generation data into a single feature DataFrame.
    Expects both dataframes to have a timezone-aware DatetimeIndex.
    Uses '1h' frequency.
    """
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

    # Resample to 1h in case of missing or different frequencies, using interpolation or forward fill as needed
    # We use asfreq to ensure the index is strict 1h
    # In a real app we might want to interpolate or just drop NA, depending on the business logic.
    weather_resampled = weather_df.resample("1h").mean()
    generation_resampled = generation_df.resample("1h").mean()

    # We use an inner join since we need both weather and generation for supervised learning.
    # We can also do an outer join and fillna.
    aligned_df = weather_resampled.join(generation_resampled, how="outer")
    return aligned_df
