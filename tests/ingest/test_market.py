import datetime

import pandas as pd

from safenergy.ingest.market import fetch_ercot_generation, fetch_ercot_prices


def test_fetch_ercot_generation():
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2023, 1, 2)

    df = fetch_ercot_generation(start_date, end_date)

    assert isinstance(df, pd.DataFrame)
    # 2 days (48 hours)
    assert len(df) == 48
    assert str(df.index.tz) == "UTC"
    assert "solar_generation_mw" in df.columns
    assert "wind_generation_mw" in df.columns

    # Check that solar generation is greater than zero at mid-day (UTC noon is daytime)
    assert df.loc["2023-01-01 13:00:00+00:00", "solar_generation_mw"] > 0
    # Check that solar generation is zero at night
    assert df.loc["2023-01-01 02:00:00+00:00", "solar_generation_mw"] == 0

def test_fetch_ercot_prices():
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2023, 1, 1)

    df = fetch_ercot_prices(start_date, end_date)

    assert isinstance(df, pd.DataFrame)
    # 1 day of 15 min intervals (96 intervals)
    assert len(df) == 96
    assert str(df.index.tz) == "UTC"
    assert "rtm_price_usd_mwh" in df.columns
    assert "dam_price_usd_mwh" in df.columns

    # Check peak vs off-peak prices
    off_peak_price = df.loc["2023-01-01 00:00:00+00:00", "rtm_price_usd_mwh"]
    peak_price = df.loc["2023-01-01 18:00:00+00:00", "rtm_price_usd_mwh"]

    assert peak_price > off_peak_price
