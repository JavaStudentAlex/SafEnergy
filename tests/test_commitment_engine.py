from safenergy.api.schemas import RecommendationRequest
from safenergy.commitment.engine import recommend_action


def test_recommendation_hold_no_gap():
    req = RecommendationRequest(
        forecast_mwh=100.0,
        committed_mwh=100.0,
        battery_available_mwh=0.0,
        intraday_eur_mwh=50.0,
        balancing_short_eur_mwh=100.0
    )
    resp = recommend_action(req)
    assert resp.action == "HOLD"
    assert resp.commitment_gap_mwh == 0.0
    assert resp.battery_discharge_mwh == 0.0
    assert resp.market_buy_mwh == 0.0

def test_recommendation_discharge_battery():
    req = RecommendationRequest(
        forecast_mwh=90.0,
        committed_mwh=100.0,
        battery_available_mwh=20.0,
        intraday_eur_mwh=50.0,
        balancing_short_eur_mwh=100.0
    )
    resp = recommend_action(req)
    assert resp.action == "DISCHARGE_BATTERY"
    assert resp.commitment_gap_mwh == 10.0
    assert resp.battery_discharge_mwh == 10.0
    assert resp.market_buy_mwh == 0.0

def test_recommendation_buy_market():
    req = RecommendationRequest(
        forecast_mwh=90.0,
        committed_mwh=100.0,
        battery_available_mwh=0.0,
        intraday_eur_mwh=50.0,
        balancing_short_eur_mwh=100.0
    )
    resp = recommend_action(req)
    assert resp.action == "BUY_MARKET"
    assert resp.commitment_gap_mwh == 10.0
    assert resp.battery_discharge_mwh == 0.0
    assert resp.market_buy_mwh == 10.0

def test_recommendation_discharge_and_buy():
    req = RecommendationRequest(
        forecast_mwh=90.0,
        committed_mwh=100.0,
        battery_available_mwh=5.0,
        intraday_eur_mwh=50.0,
        balancing_short_eur_mwh=100.0
    )
    resp = recommend_action(req)
    assert resp.action == "DISCHARGE_AND_BUY"
    assert resp.commitment_gap_mwh == 10.0
    assert resp.battery_discharge_mwh == 5.0
    assert resp.market_buy_mwh == 5.0

def test_recommendation_hold_unfavorable_market():
    req = RecommendationRequest(
        forecast_mwh=90.0,
        committed_mwh=100.0,
        battery_available_mwh=0.0,
        intraday_eur_mwh=150.0,
        balancing_short_eur_mwh=100.0
    )
    resp = recommend_action(req)
    assert resp.action == "HOLD"
    assert resp.commitment_gap_mwh == 10.0
    assert resp.battery_discharge_mwh == 0.0
    assert resp.market_buy_mwh == 0.0
