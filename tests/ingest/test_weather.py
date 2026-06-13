import datetime
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from safenergy.ingest.weather import fetch_weather_forecast


@pytest.fixture
def mock_openmeteo():
    with patch("safenergy.ingest.weather.openmeteo") as mock:
        yield mock

def test_fetch_weather_forecast(mock_openmeteo):
    # Setup mock response
    mock_response = MagicMock()
    mock_hourly = MagicMock()

    # Time settings: 2 hours of data
    start_time = int(datetime.datetime(2023, 1, 1, 0, 0, tzinfo=datetime.timezone.utc).timestamp())
    end_time = int(datetime.datetime(2023, 1, 1, 2, 0, tzinfo=datetime.timezone.utc).timestamp())

    mock_hourly.Time.return_value = start_time
    mock_hourly.TimeEnd.return_value = end_time
    mock_hourly.Interval.return_value = 3600

    # Variables setup
    def mock_variable(idx):
        var = MagicMock()
        # Mock 2 hours of data
        if idx == 0:
            var.ValuesAsNumpy.return_value = np.array([10.0, 11.0]) # temp
        elif idx == 1:
            var.ValuesAsNumpy.return_value = np.array([50.0, 55.0]) # humidity
        elif idx == 2:
            var.ValuesAsNumpy.return_value = np.array([5.0, 6.0]) # wind speed
        elif idx == 3:
            var.ValuesAsNumpy.return_value = np.array([180.0, 190.0]) # wind dir
        elif idx == 4:
            var.ValuesAsNumpy.return_value = np.array([100.0, 200.0]) # sw rad
        elif idx == 5:
            var.ValuesAsNumpy.return_value = np.array([80.0, 150.0]) # direct rad
        elif idx == 6:
            var.ValuesAsNumpy.return_value = np.array([20.0, 50.0]) # diffuse rad
        elif idx == 7:
            var.ValuesAsNumpy.return_value = np.array([10.0, 20.0]) # cloud cover
        return var

    mock_hourly.Variables = mock_variable
    mock_response.Hourly.return_value = mock_hourly

    mock_openmeteo.weather_api.return_value = [mock_response]

    # Call function
    df = fetch_weather_forecast(
        latitude=30.2672,
        longitude=-97.7431,
        past_days=1,
        forecast_days=1
    )

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert str(df.index.tz) == "UTC"
    assert "temperature_2m" in df.columns
    assert df["temperature_2m"].iloc[0] == 10.0
    assert df["wind_speed_10m"].iloc[1] == 6.0

    mock_openmeteo.weather_api.assert_called_once()
