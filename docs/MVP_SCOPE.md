# SafEnergy MVP Scope and Forecast Contract

## 1. Target Region
- **Region:** Germany (DE) bidding zone.
- **Why:** High penetration of both solar and wind generation, mature balancing market, and rich public data (ENTSO-E, SMARD).
- **Representative Site:** A bounding box or explicit coordinate set for an aggregate solar/wind footprint or a specific subset region (e.g., northern Germany for wind, southern Germany for solar) if country-wide computation is too heavy for the MVP.

## 2. Forecast Horizons
- **Nowcast:** 1 to 4 hours ahead.
- **Intraday:** Up to 24 hours ahead, updating periodically.
- **Why:** Satellite data (e.g., cloud cover movement) and short-term weather anomalies have the highest value-add over standard numerical weather prediction (NWP) models in the very short term (0-6 hours).

## 3. Prediction Targets
- **Main Variable:** $\Delta P$ (Change in Generation).
  - The model targets the *error* or *delta* relative to a baseline expectation (e.g., persistence or day-ahead forecast).
- **Solar:** Delta between expected clear-sky or standard NWP irradiance-based generation and actual near-term generation (affected by transient cloud cover).
- **Wind:** Delta between expected NWP wind generation and actual near-term generation (affected by ramp events, local pressure/temperature changes not fully resolved in NWP).
- **Output Signals:**
  - Raw MW delta.
  - Categorical operational signals (e.g., "Large Upward Ramp", "Large Downward Ramp", "Normal").

## 4. Data Availability Assumptions
- **Satellite Data:** Earth Engine or Copernicus Data Space will be used to fetch near-real-time (NRT) imagery. Assume data may have processing delays (e.g., 1-2 hours behind realtime).
- **Weather Data:** Open-Meteo provides deterministic and ensemble NWP forecasts, assumed to be available at regular model run intervals (e.g., every 6 hours).
- **Generation & Market Data:** Historical generation and prices (ENTSO-E/SMARD) are used for training and backtesting. During inference (nowcasting), generation data from the previous hour (t-1) is assumed to be available.
- **Missing Data Handling:** The pipeline must explicitly handle missing satellite tiles or delayed weather data using fallback baselines (e.g., persistence).

## 5. Success Contract
- **Predictive Performance:** The nowcasting model must outperform a simple persistence baseline (e.g., "generation at t+1 equals generation at t") and a simple weather-only baseline in terms of RMSE/MAE over a temporal hold-out split.
- **Leakage Safety:** Temporal splits are strictly enforced. Features for forecasting at time $t$ using horizon $h$ must only use information physically available at time $t$. No future data leakage.
- **Signal Transparency:** The model outputs an explainable signal. Any operational or trading decision based on the forecast delta is accompanied by top driver attribution (e.g., "signal triggered by unexpected cloud cover in region X").
- **Reproducibility:** A deterministically seeded evaluation script will produce the same backtest metrics over the defined hold-out period using a cached dataset.
