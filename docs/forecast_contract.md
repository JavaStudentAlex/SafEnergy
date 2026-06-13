# MVP Scope and Forecast Contract

This document defines the core boundaries and contracts for the SafEnergy prototype, ensuring clarity around forecasting targets, horizons, and data boundaries, in accordance with the project requirements.

## 1. Target Region
- **Region:** ERCOT (Texas, USA) - chosen for its public market data, substantial wind/solar capacity, and clear balancing signals.
- **Geospatial Contract:** All data operations (satellite footprints, weather grids, generation sites) must be aligned. Coordinate reference systems (CRS) must be explicitly managed, avoiding silent mixing of lat/lon and projected coordinates.

## 2. Forecast Horizons
- **Nowcast / Intraday:** 1 to 4 hours ahead.
- **Day-Ahead:** 24 to 36 hours ahead.
- **Timezone Contract:** All timestamps internally must be strictly timezone-aware and in UTC. Conversions to local market time (e.g., US/Central) occur only at the external output or evaluation boundaries.

## 3. Target Variable
- **Prediction Target:** Generation Delta (change from expectation).
- **Definition:** The short-term deviation of solar and wind generation from an established baseline (such as persistence, clear-sky expectation, or short-term climatology).
- **Rationale:** Trading signals, congestion, and balancing impacts are driven by unexpected generation changes (the delta), rather than the absolute generation curve alone.

## 4. Data Availability and Assumptions
- **Satellite/Weather Data:** Features rely on inputs like Copernicus/Sentinel and Open-Meteo. Missing data, stale satellite tiles, and cloudy scenes must be explicitly surfaced rather than silently ignored.
- **Market Data:** Historical generation and price data are used. External APIs can be mocked or backed by deterministic fixtures for testing and demo reliability. Note that live market data is meant for **decision support and backtests only**. SafEnergy implements a strict **no-live-trading boundary**.
- **Leakage Prevention:** Features used to predict a given target must strictly reflect data available *at or before the forecast issue time*. Temporal splits must be used for all training and backtesting.

## 5. Success Contract
- **Baseline Outperformance:** Forecast models must demonstrate their performance against simple baselines (e.g., persistence) using valid temporal splits.
- **Signal Boundary:** The system produces explainable operational and trading-impact signals (e.g., risk-filtered signals for backtesting or decision support). **Live trade execution is explicitly out of scope.**
- **Explainability:** Forecasts and signals must be accompanied by human-readable explanations covering key drivers (e.g., "irradiance anomaly", "wind speed change") and model uncertainty.
- **Reproducibility:** The entire pipeline from ingestion to backtest evaluation must be verifiable, with a final reproducible demo using cached or fixture data when external services are unavailable.

## 6. No-Training Forecast Method Stack

When trained AI/ML forecasting model artifacts are unavailable or not trustworthy, SafEnergy falls back to an honest, deterministic **No-Training Forecast Method Stack**.

### Method Fallback Hierarchy
The method selector ranks available no-training methods based on input availability, preferring the best available honest method:
1. **Smart/Normalized Persistence:** Requires recent generation plus irradiance or weather availability.
2. **pvlib Physical Solar:** Requires solar asset metadata (location, capacity, time) plus weather or irradiance.
3. **Wind Power-Curve Approximation:** Requires wind asset metadata plus wind forecast.
4. **Regional Capacity Fallback:** Requires installed capacity and regional weather only (lower confidence).
5. **Diagnostic Fallback:** Occurs when inputs are insufficient. Returns a labeled diagnostic fallback or no reliable forecast; never an unlabeled fixed constant.

### Fallback Contract & Constraints
- **Output Requirements:** Every forecast response without a trained model artifact must identify the selected method, inputs used, missing inputs, fallback reason, confidence score, uncertainty band, issue time, valid time, horizon, and provenance references.
- **Conservative Signaling:** Trading signal generation becomes conservative or returns no-action when confidence is low due to poor input quality or missing data.
- **No False Claims:** The system **must not claim trained AI/ML forecasting performance** when using these deterministic baselines. It must clearly document these outputs as explainable no-training baselines.
