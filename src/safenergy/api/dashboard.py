import datetime

import httpx
import pandas as pd
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SafEnergy Dashboard",
    page_icon="☀️",
    layout="wide",
)

st.title("SafEnergy Forecasting and Trading Dashboard")
st.markdown("Visualize renewable forecasts, trading signals, and backtest results.")

tab_portfolio, tab_orchestrator, tab_forecasts, tab_signals, tab_backtest = st.tabs([
    "Portfolio Overview",
    "Orchestrator",
    "Forecasts",
    "Trading Signals",
    "Backtest",
])



with tab_portfolio:
    st.header("Portfolio Overview")
    if st.button("Refresh Portfolio", key="btn_refresh_portfolio"):
        try:
            response = httpx.get(f"{API_URL}/dashboard/overview")
            if response.status_code == 200:
                data = response.json()
                metrics = data.get("portfolio_metrics", {})
                market = data.get("market_prices", {})
                actions = data.get("recent_actions", [])
                plants = data.get("plants", [])

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Shortfall (MWh)", f"{metrics.get('total_shortfall_mwh', 0):.1f}")
                with col2:
                    st.metric("Estimated Cost (EUR)", f"{metrics.get('total_estimated_cost_eur', 0):.1f}")
                with col3:
                    st.metric("Avoided Imbalance Cost (EUR)", f"{metrics.get('total_avoided_cost_eur', 0):.1f}")

                st.subheader("Market Prices")
                if market and market.get("points"):
                    st.dataframe(pd.DataFrame(market["points"]).head(5))
                else:
                    st.info("No market prices available.")

                st.subheader("Recent Actions")
                if actions:
                    st.dataframe(pd.DataFrame(actions))
                else:
                    st.info("No recent actions.")

                st.subheader("Plant Statuses")
                for po in plants:
                    plant_info = po.get("plant", {})
                    health_info = po.get("health", {})
                    st.write(f"**{plant_info.get('name', 'Unknown')}** ({plant_info.get('plant_id', '')}) - Status: {health_info.get('status', 'unknown')}")
                    if health_info.get("anomalies"):
                        for anom in health_info["anomalies"]:
                            st.warning(f"{anom.get('category')}: {anom.get('description')} ({anom.get('severity')})")
            else:
                st.error(f"API Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")

with tab_orchestrator:
    st.header("End-to-End Orchestrator")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Pipeline Configuration")
        asset_id = st.text_input("Asset ID", value="TEST-ASSET")
        lat = st.number_input("Latitude", value=30.2672)
        lon = st.number_input("Longitude", value=-97.7431)
        start_d = st.date_input("Start Date", value=datetime.date(2023,1,1))
        end_d = st.date_input("End Date", value=datetime.date(2023,1,2))
        sim_fail = st.checkbox("Simulate Failure")

        st.subheader("Thresholds")
        strong_threshold_orch = st.number_input("Strong Threshold (MW)", value=100.0, key="orch_strong")
        weak_threshold_orch = st.number_input("Weak Threshold (MW)", value=20.0, key="orch_weak")
        curtailment_price_orch = st.number_input("Curtailment Price Threshold ($)", value=-10.0, key="orch_curtail")
        extreme_price_orch = st.number_input("Extreme Price Threshold ($)", value=1000.0, key="orch_extreme")

        if st.button("Run Pipeline"):
            payload = {
                "asset_id": asset_id,
                "latitude": lat,
                "longitude": lon,
                "start_date": start_d.isoformat() + "T00:00:00Z",
                "end_date": end_d.isoformat() + "T00:00:00Z",
                "simulate_failure": sim_fail,
                "strong_threshold": strong_threshold_orch,
                "weak_threshold": weak_threshold_orch,
                "curtailment_price_threshold": curtailment_price_orch,
                "extreme_price_threshold": extreme_price_orch
            }
            try:
                response = httpx.post(f"{API_URL}/orchestrator/run", json=payload, timeout=60.0)
                if response.status_code == 200:
                    data = response.json()
                    with col2:
                        st.subheader("Pipeline Results")
                        st.write(f"**Asset ID:** {data['asset_id']}")
                        st.write(f"**Issue Time:** {data['issue_time']}")
                        st.info(f"**Forecast Data State:** {data.get('forecast_data_state', 'unknown')}")

                        st.write("**Signals**")
                        if data["signals"]:
                            st.dataframe(pd.DataFrame(data["signals"]))
                        else:
                            st.info("No signals generated.")

                        st.write("**Explanations**")
                        if data["explanations"]:
                            for i, exp in enumerate(data["explanations"][:5]):
                                with st.expander(f"Explanation {i+1}"):
                                    st.json(exp)
                            if len(data["explanations"]) > 5:
                                st.write(f"... and {len(data['explanations']) - 5} more.")
                        else:
                            st.info("No explanations generated.")
                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")

with tab_forecasts:

    st.header("Forecasts & Explanations")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Forecast Inputs")
        delta = st.number_input("Forecast Delta (MW)", value=25.0, key="fc_delta")
        baseline = st.number_input("Baseline Generation (MW)", value=100.0, key="fc_base")
        lower = st.number_input("Lower Bound (MW)", value=110.0, key="fc_low")
        upper = st.number_input("Upper Bound (MW)", value=140.0, key="fc_up")
        price = st.number_input("Market Price ($)", value=-5.0, key="fc_price")
        cloud_cover = st.number_input("Cloud Cover Driver", value=-15.0, key="fc_cloud")
        wind_speed = st.number_input("Wind Speed Driver", value=5.0, key="fc_wind")

        if st.button("Generate Explanation", key="btn_explain"):
            payload = {
                "forecast_delta": delta,
                "baseline": baseline,
                "lower_bound": lower,
                "upper_bound": upper,
                "features": {"cloud_cover": cloud_cover, "wind_speed": wind_speed},
                "market_price": price
            }
            try:
                response = httpx.post(f"{API_URL}/trading/explain", json=payload)
                if response.status_code == 200:
                    explanation = response.json()
                    with col2:
                        st.subheader("Explanation Output")
                        st.info(explanation["summary"])
                        st.metric("Confidence", explanation["confidence"])
                        st.metric("Uncertainty (MW)", f"{explanation['uncertainty_mw']:.1f}")
                        st.write("**Top Drivers:**", ", ".join(explanation["top_drivers"]))

                        st.write(f"**Limitations:** {explanation.get('attribution_limitations', '')}")
                        st.write("**Attribution:**")
                        for attr in explanation["attribution"]:
                            source = attr.get('source_label', 'heuristic')
                            st.write(f"- {attr['feature_name']} [{source}]: {attr['contribution_mw']:.1f} MW ({attr['description']})")
                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")

with tab_signals:
    st.header("Trading Signals")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Signal Configuration")
        strong_threshold = st.number_input("Strong Threshold (MW)", value=100.0, key="sig_strong")
        weak_threshold = st.number_input("Weak Threshold (MW)", value=20.0, key="sig_weak")
        curtailment_price = st.number_input("Curtailment Price Threshold ($)", value=-10.0, key="sig_curtail")
        extreme_price = st.number_input("Extreme Price Threshold ($)", value=1000.0, key="sig_extreme")

        st.subheader("Mock Data Series (comma-separated)")
        deltas_input = st.text_input("Forecast Deltas (MW)", value="30.0, 110.0, -50.0, -120.0, 0.0", key="sig_deltas")
        baselines_input = st.text_input("Baselines (MW)", value="50.0, 60.0, 70.0, 80.0, 50.0", key="sig_baselines")
        prices_input = st.text_input("Market Prices ($)", value="20.0, 1050.0, 30.0, -20.0, 50.0", key="sig_prices")

        if st.button("Generate Trading Signals", key="btn_signals"):
            try:
                deltas = pd.Series([float(x.strip()) for x in deltas_input.split(",")])
                baselines = pd.Series([float(x.strip()) for x in baselines_input.split(",")])
                prices = pd.Series([float(x.strip()) for x in prices_input.split(",")])

                # Make simple timezone aware index
                index = pd.date_range(start="2023-01-01", periods=len(deltas), freq="h", tz="UTC")
                deltas.index = index
                baselines.index = index
                prices.index = index

                data_list = [
                    {"timestamp": ts.isoformat() + "Z" if str(ts.tzinfo) == "UTC" else ts.isoformat(),
                     "delta": float(d),
                     "baseline": float(b),
                     "price": float(p)}
                    for ts, d, b, p in zip(index, deltas, baselines, prices)
                ]
                payload = {
                    "asset_id": "mock-asset",
                    "data": data_list,
                    "strong_threshold": strong_threshold,
                    "weak_threshold": weak_threshold,
                    "curtailment_price_threshold": curtailment_price,
                    "extreme_price_threshold": extreme_price
                }

                response = httpx.post(f"{API_URL}/trading/signals", json=payload)
                if response.status_code == 200:
                    signals = response.json()
                    with col2:
                        st.subheader("Generated Signals")
                        if not signals:
                            st.warning("No signals generated.")
                        else:
                            signal_data = []
                            for sig in signals:
                                signal_data.append({
                                    "Timestamp": sig["timestamp"],
                                    "Delta": sig["forecast_delta"],
                                    "Price": sig["market_price"],
                                    "Base Signal": str(sig["base_signal"]),
                                    "Adjusted Signal": str(sig["adjusted_signal"]),
                                    "Explanation": sig["explanation"]
                                })
                            st.dataframe(pd.DataFrame(signal_data))
                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Error generating signals: {e}")

with tab_backtest:
    st.header("Backtest Evaluation")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Backtest Assumptions")
        st.checkbox("No Live Trading Constraint", value=True, disabled=True)
        tx_cost = st.number_input("Transaction Cost ($)", value=0.0, step=0.1, key="bt_tx_cost")
        fee = st.number_input("Fee ($)", value=0.0, step=0.1, key="bt_fee")
        slippage = st.number_input("Slippage ($)", value=0.0, step=0.1, key="bt_slip")

        st.subheader("Backtest Data (comma-separated)")
        bt_signals_input = st.text_input("Signals (-2, -1, 0, 1, 2)", value="1, 2, -1, -2, 0", key="bt_signals")
        bt_prices_input = st.text_input("Price Changes ($)", value="5.0, 10.0, -5.0, 20.0, 10.0", key="bt_prices")

        if st.button("Run Backtest Evaluation", key="btn_backtest"):
            try:
                sig_vals = pd.Series([int(x.strip()) for x in bt_signals_input.split(",")])
                price_changes = pd.Series([float(x.strip()) for x in bt_prices_input.split(",")])

                index = pd.date_range(start="2023-01-01", periods=len(sig_vals), freq="h", tz="UTC")
                sig_vals.index = index
                price_changes.index = index

                data_list = [
                    {"timestamp": ts.isoformat() + "Z" if str(ts.tzinfo) == "UTC" else ts.isoformat(),
                     "signal": int(s),
                     "price_change": float(p)}
                    for ts, s, p in zip(index, sig_vals, price_changes)
                ]
                payload = {
                    "data": data_list,
                    "assumptions": {
                        "transaction_cost": tx_cost,
                        "fee": fee,
                        "slippage": slippage,
                        "no_live_trading": True
                    }
                }

                response = httpx.post(f"{API_URL}/trading/backtest", json=payload)
                if response.status_code == 200:
                    results = response.json()
                    with col2:
                        st.subheader("Backtest Metrics")
                        st.metric("Total Return ($)", f"{results['total_return']:.2f}")
                        st.metric("Hit Rate", f"{results['hit_rate'] * 100:.1f}%")

                        st.write("**Details:**")
                        st.write(f"- Hits: {results['hits']}")
                        st.write(f"- Misses: {results['misses']}")
                        st.write(f"- Flat Trades: {results['flat']}")
                        st.write(f"- Total Active Trades: {results['total_trades']}")
                        st.write(f"- Leakage Check: {results.get('leakage_check_status')}")
                else:
                    st.error(f"API Error {response.status_code}: {response.text}")

            except Exception as e:
                st.error(f"Error evaluating backtest: {e}")
