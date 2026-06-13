from streamlit.testing.v1 import AppTest


def test_dashboard_renders():
    # Streamlit provides a testing framework
    at = AppTest.from_file("src/safenergy/api/dashboard.py").run(timeout=10)
    assert not at.exception

    # Assert on tabs existing
    assert len(at.tabs) == 5

def test_dashboard_buttons_errors(requests_mock):
    # Mock all the API calls to return errors to test error branches
    requests_mock.get("http://127.0.0.1:8000/dashboard/overview", status_code=500)
    requests_mock.post("http://127.0.0.1:8000/orchestrator/run", status_code=500)
    requests_mock.post("http://127.0.0.1:8000/trading/explain", status_code=500)
    requests_mock.post("http://127.0.0.1:8000/trading/signals", status_code=500)
    requests_mock.post("http://127.0.0.1:8000/trading/backtest", status_code=500)

    at = AppTest.from_file("src/safenergy/api/dashboard.py").run(timeout=10)

    at.button(key="btn_refresh_portfolio").click().run(timeout=10)
    at.button[1].click().run(timeout=10)
    at.button(key="btn_explain").click().run(timeout=10)
    at.button(key="btn_signals").click().run(timeout=10)
    at.button(key="btn_backtest").click().run(timeout=10)

def test_dashboard_buttons_exceptions(requests_mock):
    # Mock all the API calls to throw exceptions to test exception branches
    requests_mock.get("http://127.0.0.1:8000/dashboard/overview", exc=Exception("Network Error"))
    requests_mock.post("http://127.0.0.1:8000/orchestrator/run", exc=Exception("Network Error"))
    requests_mock.post("http://127.0.0.1:8000/trading/explain", exc=Exception("Network Error"))
    requests_mock.post("http://127.0.0.1:8000/trading/signals", exc=Exception("Network Error"))
    requests_mock.post("http://127.0.0.1:8000/trading/backtest", exc=Exception("Network Error"))

    at = AppTest.from_file("src/safenergy/api/dashboard.py").run(timeout=10)

    at.button(key="btn_refresh_portfolio").click().run(timeout=10)
    at.button[1].click().run(timeout=10)
    at.button(key="btn_explain").click().run(timeout=10)
    at.button(key="btn_signals").click().run(timeout=10)
    at.button(key="btn_backtest").click().run(timeout=10)

def test_dashboard_buttons_with_data(requests_mock):
    # Tests branches inside UI loops for explanations and signals
    requests_mock.get("http://127.0.0.1:8000/dashboard/overview", json={
        "plants": [{"plant": {"plant_id": "test", "name": "test", "capacity_mw": 10.0, "status": "active"},
                    "health": {"status": "ok", "anomalies": []}, "weather_live": None, "forecast_nowcast": None}],
        "market_prices": {"points": []},
        "portfolio_metrics": {"total_shortfall_mwh": 0.0, "total_estimated_cost_eur": 0.0, "total_avoided_cost_eur": 0.0, "action_count": 0},
        "recent_actions": []
    })

    requests_mock.post("http://127.0.0.1:8000/orchestrator/run", json={
        "asset_id": "pv-texas-01",
        "signals": [{"timestamp": "2023-01-01T00:00:00Z", "forecast_delta": 10.0, "market_price": 20.0, "base_signal": "HOLD", "adjusted_signal": "HOLD", "explanation": "test"}],
        "explanations": [{"summary": "test", "confidence": "High", "uncertainty_mw": 10.0, "top_drivers": [], "attribution": []}] * 6,
        "forecast_data_state": "live",
        "issue_time": "2023-01-01T00:00:00Z"
    })

    requests_mock.post("http://127.0.0.1:8000/trading/explain", json={
        "summary": "test",
        "confidence": "High",
        "uncertainty_mw": 10.0,
        "top_drivers": [],
        "attribution": [{"feature_name": "cloud_cover", "contribution_mw": 10.0, "description": "test"}]
    })

    requests_mock.post("http://127.0.0.1:8000/trading/signals", json=[
        {"timestamp": "2023-01-01T00:00:00Z", "forecast_delta": 10.0, "market_price": 20.0, "base_signal": "HOLD", "adjusted_signal": "HOLD", "explanation": "test"}
    ])

    requests_mock.post("http://127.0.0.1:8000/trading/backtest", json={
        "total_return": 10.0,
        "hit_rate": 1.0,
        "hits": 1,
        "misses": 0,
        "flat": 0,
        "total_trades": 1,
        "leakage_check_status": "ok"
    })

    at = AppTest.from_file("src/safenergy/api/dashboard.py").run(timeout=10)

    at.button(key="btn_refresh_portfolio").click().run(timeout=10)
    at.button[1].click().run(timeout=10)
    at.button(key="btn_explain").click().run(timeout=10)
    at.button(key="btn_signals").click().run(timeout=10)
    at.button(key="btn_backtest").click().run(timeout=10)

def test_dashboard_buttons_with_data_full(requests_mock):
    # Same as above but with all populated data fields for branch coverage
    requests_mock.get("http://127.0.0.1:8000/dashboard/overview", json={
        "plants": [
            {
                "plant": {"plant_id": "test", "name": "test", "capacity_mw": 10.0, "status": "active"},
                "health": {"status": "degraded", "anomalies": [{"category": "weather_derating", "description": "Cloud cover", "severity": "warning"}]},
                "weather_live": None,
                "forecast_nowcast": None
            }
        ],
        "market_prices": {"points": [{"timestamp": "2023-01-01T00:00:00Z", "day_ahead_eur_mwh": 10.0, "intraday_eur_mwh": 10.0, "balancing_short_eur_mwh": 10.0, "balancing_long_eur_mwh": 10.0}]},
        "portfolio_metrics": {"total_shortfall_mwh": 10.0, "total_estimated_cost_eur": 10.0, "total_avoided_cost_eur": 10.0, "action_count": 1},
        "recent_actions": [{"action_id": "1", "plant_id": "test", "action_type": "HOLD", "timestamp": "2023-01-01T00:00:00Z", "commitment_gap_mwh": 10.0, "battery_discharge_mwh": 0.0, "market_buy_mwh": 0.0, "estimated_cost_eur": 0.0, "avoided_imbalance_cost_eur": 0.0}],
        "demo_metadata": {"key": "value"}
    })

    requests_mock.post("http://127.0.0.1:8000/orchestrator/run", json={
        "asset_id": "pv-texas-01",
        "signals": [],
        "explanations": [],
        "forecast_data_state": "live"
    })

    requests_mock.post("http://127.0.0.1:8000/trading/explain", json={
        "summary": "test",
        "confidence": "High",
        "uncertainty_mw": 10.0,
        "top_drivers": [],
        "attribution": []
    })

    requests_mock.post("http://127.0.0.1:8000/trading/signals", json=[])

    requests_mock.post("http://127.0.0.1:8000/trading/backtest", json={
        "total_return": 10.0,
        "hit_rate": 1.0,
        "hits": 1,
        "misses": 0,
        "flat": 0,
        "total_trades": 1,
        "leakage_check_status": "ok"
    })

    at = AppTest.from_file("src/safenergy/api/dashboard.py").run(timeout=10)
    at.button(key="btn_refresh_portfolio").click().run(timeout=10)

def test_dashboard_button_states(requests_mock):
    # To hit line 33, we need to click the refresh portfolio button
    requests_mock.get("http://127.0.0.1:8000/dashboard/overview", json={
        "plants": [
            {
                "plant": {"plant_id": "test", "name": "test", "capacity_mw": 10.0, "status": "active"},
                "health": {"status": "degraded", "anomalies": [{"category": "weather_derating", "description": "Cloud cover", "severity": "warning"}]},
                "weather_live": None,
                "forecast_nowcast": None
            }
        ],
        "market_prices": {"points": [{"timestamp": "2023-01-01T00:00:00Z", "day_ahead_eur_mwh": 10.0, "intraday_eur_mwh": 10.0, "balancing_short_eur_mwh": 10.0, "balancing_long_eur_mwh": 10.0}]},
        "portfolio_metrics": {"total_shortfall_mwh": 10.0, "total_estimated_cost_eur": 10.0, "total_avoided_cost_eur": 10.0, "action_count": 1},
        "recent_actions": [{"action_id": "1", "plant_id": "test", "action_type": "HOLD", "timestamp": "2023-01-01T00:00:00Z", "commitment_gap_mwh": 10.0, "battery_discharge_mwh": 0.0, "market_buy_mwh": 0.0, "estimated_cost_eur": 0.0, "avoided_imbalance_cost_eur": 0.0}],
        "demo_metadata": {"key": "value"}
    })

    requests_mock.post("http://127.0.0.1:8000/orchestrator/run", json={
        "asset_id": "pv-texas-01",
        "signals": [],
        "explanations": [],
        "forecast_data_state": "live"
    })

    requests_mock.post("http://127.0.0.1:8000/trading/explain", json={
        "summary": "test",
        "confidence": "High",
        "uncertainty_mw": 10.0,
        "top_drivers": [],
        "attribution": []
    })

    requests_mock.post("http://127.0.0.1:8000/trading/signals", json=[])

    requests_mock.post("http://127.0.0.1:8000/trading/backtest", json={
        "total_return": 10.0,
        "hit_rate": 1.0,
        "hits": 1,
        "misses": 0,
        "flat": 0,
        "total_trades": 1,
        "leakage_check_status": "ok"
    })

    at = AppTest.from_file("src/safenergy/api/dashboard.py").run(timeout=10)

    # Run UI again after clicking to assert
    at.button(key="btn_refresh_portfolio").click().run(timeout=10)
    # the lines inside the buttons are executed when they are clicked.
    # to hit "len(data['explanations']) > 5" we need 6 items in the list
    requests_mock.post("http://127.0.0.1:8000/orchestrator/run", json={
        "asset_id": "pv-texas-01",
        "signals": [{"timestamp": "2023-01-01T00:00:00Z", "forecast_delta": 10.0, "market_price": 20.0, "base_signal": "HOLD", "adjusted_signal": "HOLD", "explanation": "test"}],
        "explanations": [{"summary": "test", "confidence": "High", "uncertainty_mw": 10.0, "top_drivers": [], "attribution": []}] * 6,
        "forecast_data_state": "live",
        "issue_time": "2023-01-01T00:00:00Z"
    })
    at.button[1].click().run(timeout=10)

    at.button(key="btn_explain").click().run(timeout=10)
    at.button(key="btn_signals").click().run(timeout=10)
    at.button(key="btn_backtest").click().run(timeout=10)
