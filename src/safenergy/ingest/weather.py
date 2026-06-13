import datetime
import logging

import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)



def check_weather_quality(df: pd.DataFrame) -> None:
    """Checks weather DataFrame for missing values and temporal continuity."""
    if df.empty:
        logging.warning("Weather dataframe is empty.")
        return

    # Check for missing values
    if df.isnull().values.any():
        logging.warning("Weather dataframe contains missing values.")

    # Check temporal continuity
    expected_freq = pd.Timedelta(hours=1)
    time_diffs = df.index.to_series().diff().dropna()
    if not (time_diffs == expected_freq).all():
        logging.warning("Weather dataframe has missing hourly intervals.")

def fetch_weather_forecast(
    latitude: float,
    longitude: float,
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    past_days: int | None = None,
    forecast_days: int | None = None,
) -> pd.DataFrame:
    """
    Fetches weather forecast for renewable generation using Open-Meteo.
    Returns timezone-aware (UTC) Pandas DataFrame.
    """
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m", "shortwave_radiation", "direct_radiation", "diffuse_radiation", "cloud_cover"],
        "timezone": "UTC"
    }

    if start_date and end_date:
        params["start_date"] = start_date.strftime("%Y-%m-%d")
        params["end_date"] = end_date.strftime("%Y-%m-%d")
    elif past_days is not None and forecast_days is not None:
        params["past_days"] = past_days
        params["forecast_days"] = forecast_days
    else:
        # Default behavior: next 2 days
        params["forecast_days"] = 2

    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(2).ValuesAsNumpy()
    hourly_wind_direction_10m = hourly.Variables(3).ValuesAsNumpy()
    hourly_shortwave_radiation = hourly.Variables(4).ValuesAsNumpy()
    hourly_direct_radiation = hourly.Variables(5).ValuesAsNumpy()
    hourly_diffuse_radiation = hourly.Variables(6).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(7).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )}

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
    hourly_data["shortwave_radiation"] = hourly_shortwave_radiation
    hourly_data["direct_radiation"] = hourly_direct_radiation
    hourly_data["diffuse_radiation"] = hourly_diffuse_radiation
    hourly_data["cloud_cover"] = hourly_cloud_cover

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    hourly_dataframe.set_index("date", inplace=True)
    check_weather_quality(hourly_dataframe)
    return hourly_dataframe
