import datetime
from pathlib import Path

import pandas as pd

from safenergy.ingest.market import (
    GenerationDataResponse,
    MarketDataDiagnostic,
    MarketDataResponse,
    fetch_ercot_generation,
    fetch_ercot_prices,
)


def test_market_data_response_schema():
    diag = MarketDataDiagnostic(status="ok", records_returned=10)
    df = pd.DataFrame({"rtm_price_usd_mwh": [20.0]})
    resp = MarketDataResponse(
        provider="test",
        region="ERCOT",
        issue_time=datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc),
        valid_time_start=datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc),
        valid_time_end=datetime.datetime(2023, 1, 2, tzinfo=datetime.timezone.utc),
        diagnostic=diag,
        data=df
    )
    assert resp.provider == "test"
    assert resp.region == "ERCOT"
    assert resp.diagnostic.status == "ok"
    assert not resp.data.empty

def test_generation_data_response_schema():
    diag = MarketDataDiagnostic(status="ok", records_returned=10)
    df = pd.DataFrame({"solar_generation_mw": [100.0]})
    resp = GenerationDataResponse(
        provider="test",
        region="ERCOT",
        issue_time=datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc),
        valid_time_start=datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc),
        valid_time_end=datetime.datetime(2023, 1, 2, tzinfo=datetime.timezone.utc),
        diagnostic=diag,
        data=df
    )
    assert resp.provider == "test"
    assert resp.region == "ERCOT"
    assert resp.diagnostic.status == "ok"
    assert not resp.data.empty

def test_fetch_ercot_generation():
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2023, 1, 2)

    resp = fetch_ercot_generation(start_date, end_date)
    df = resp.data

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

    resp = fetch_ercot_prices(start_date, end_date)
    df = resp.data

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



def test_fetch_ercot_generation_fixture():
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2023, 1, 1)
    fixture_path = Path("tests/fixtures/market/generation.csv")

    resp = fetch_ercot_generation(start_date, end_date, fixture_path=fixture_path)

    assert resp.diagnostic.status == "ok"
    assert resp.diagnostic.cache_hit is True
    assert len(resp.data) == 3
    assert "solar_generation_mw" in resp.data.columns

def test_fetch_ercot_prices_fixture():
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2023, 1, 1)
    fixture_path = Path("tests/fixtures/market/prices.csv")

    resp = fetch_ercot_prices(start_date, end_date, fixture_path=fixture_path)

    assert resp.diagnostic.status == "ok"
    assert resp.diagnostic.cache_hit is True
    assert len(resp.data) == 3
    assert "rtm_price_usd_mwh" in resp.data.columns

def test_fetch_ercot_generation_failure():
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2023, 1, 1)

    resp = fetch_ercot_generation(start_date, end_date, simulate_failure=True)

    assert resp.diagnostic.status == "network_error"
    assert resp.data.empty

def test_fetch_ercot_prices_failure():
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2023, 1, 1)

    resp = fetch_ercot_prices(start_date, end_date, simulate_failure=True)

    assert resp.diagnostic.status == "network_error"
    assert resp.data.empty
