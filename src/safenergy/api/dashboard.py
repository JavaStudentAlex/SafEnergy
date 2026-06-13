import pandas as pd
import streamlit as st

from safenergy.signals.backtest import evaluate_signals
from safenergy.signals.explanation import generate_explanation
from safenergy.signals.pipeline import generate_trading_signals

st.set_page_config(
    page_title="SafEnergy Dashboard",
    page_icon="☀️",
    layout="wide",
)

st.title("SafEnergy Forecasting and Trading Dashboard")
st.markdown("Visualize renewable forecasts, trading signals, and backtest results.")

tab_forecasts, tab_signals, tab_backtest = st.tabs([
    "Forecasts",
    "Trading Signals",
    "Backtest",
])

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
            explanation = generate_explanation(
                forecast_delta=delta,
                baseline=baseline,
                lower_bound=lower,
                upper_bound=upper,
                features={"cloud_cover": cloud_cover, "wind_speed": wind_speed},
                market_price=price,
            )

            with col2:
                st.subheader("Explanation Output")
                st.info(explanation.summary)
                st.metric("Confidence", explanation.confidence)
                st.metric("Uncertainty (MW)", f"{explanation.uncertainty_mw:.1f}")
                st.write("**Top Drivers:**", ", ".join(explanation.top_drivers))

                st.write("**Attribution:**")
                for attr in explanation.attribution:
                    st.write(f"- {attr.feature_name}: {attr.contribution_mw:.1f} MW ({attr.description})")

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

                signals = generate_trading_signals(
                    asset_id="mock-asset",
                    deltas=deltas,
                    baselines=baselines,
                    prices=prices,
                    strong_threshold=strong_threshold,
                    weak_threshold=weak_threshold,
                    curtailment_price_threshold=curtailment_price,
                    extreme_price_threshold=extreme_price,
                )

                with col2:
                    st.subheader("Generated Signals")
                    if not signals:
                        st.warning("No signals generated.")
                    else:
                        signal_data = []
                        for sig in signals:
                            signal_data.append({
                                "Timestamp": sig.timestamp,
                                "Delta": sig.forecast_delta,
                                "Price": sig.market_price,
                                "Base Signal": sig.base_signal.name,
                                "Adjusted Signal": sig.adjusted_signal.name,
                                "Explanation": sig.explanation
                            })
                        st.dataframe(pd.DataFrame(signal_data))
            except Exception as e:
                st.error(f"Error generating signals: {e}")

with tab_backtest:
    st.header("Backtest Evaluation")
    col1, col2 = st.columns(2)

    with col1:
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

                results = evaluate_signals(signals=sig_vals, price_changes=price_changes)

                with col2:
                    st.subheader("Backtest Metrics")
                    st.metric("Total Return ($)", f"{results['total_return']:.2f}")
                    st.metric("Hit Rate", f"{results['hit_rate'] * 100:.1f}%")

                    st.write("**Details:**")
                    st.write(f"- Hits: {results['hits']}")
                    st.write(f"- Misses: {results['misses']}")
                    st.write(f"- Flat Trades: {results['flat']}")
                    st.write(f"- Total Active Trades: {results['total_trades']}")

            except Exception as e:
                st.error(f"Error evaluating backtest: {e}")
