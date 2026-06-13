# M001-7qeil2: Renewable Forecasting Trading Prototype

**Vision:** Build a satellite-driven renewable production forecasting and trading-impact prototype that takes a region and horizon, fetches or prepares satellite, weather, generation, and price data, predicts solar and wind generation change against persistence baselines, and translates forecast deltas into explainable operational or trading signals.

## Success Criteria

- MVP scope is explicit: target region, forecast horizons, prediction target, and data availability assumptions are documented.
- Repository structure supports ingestion, features, forecast models, signals, backtesting, API, storage, and demo code with clear subsystem boundaries.
- Data ingestion and quality checks produce provenance-aware, cacheable inputs for satellite, weather, generation, and price data.
- Feature engineering aligns timestamps in UTC, avoids leakage, and builds deterministic solar, weather, generation, and target features.
- Forecast models are evaluated against persistence and other simple baselines using temporal splits.
- Trading signal and backtest components convert forecast deltas into transparent, risk-filtered operational signals.
- API and dashboard demonstrate the forecast-to-trade loop with human-readable explanations and visible failure modes.
- Final demo can be run reproducibly with documented commands and deterministic fixture or cached data where external services are unavailable.

## Slices

- [x] **S01: MVP Scope and Forecast Contract** `[sketch]` `risk:high` `depends:[]`
  > After this: The project has a documented region, horizons, target variable, data assumptions, and success contract.

- [x] **S02: Repository Structure and Configuration** `[sketch]` `risk:medium` `depends:[S01]`
  > After this: A clean package layout and typed configuration surface exists for the prototype.

- [x] **S03: Data Ingestion and Quality Checks** `[sketch]` `risk:high` `depends:[S01,S02]`
  > After this: Satellite, weather, generation, and price ingestion adapters expose normalized, provenance-aware data or fixture-backed fallbacks.

- [x] **S04: Time Alignment and Feature Engineering** `[sketch]` `risk:high` `depends:[S03]`
  > After this: Aligned feature tables exist with solar, weather, generation history, target variables, and leakage-safe splits.

- [ ] **S05: Forecast Baselines** `[sketch]` `risk:medium` `depends:[S04]`
  > After this: Persistence, same-hour-yesterday, and weather-only baseline outputs are available for comparison.

- [ ] **S06: Forecasting Model Service** `[sketch]` `risk:high` `depends:[S04,S05]`
  > After this: First ML models produce solar and wind generation-change forecasts with uncertainty and serialized artifacts if needed.

- [ ] **S07: Forecast Evaluation** `[sketch]` `risk:high` `depends:[S05,S06]`
  > After this: Evaluation reports show model performance versus persistence using temporal splits and forecasting metrics.

- [ ] **S08: Signal Thresholds and Market Context** `[sketch]` `risk:medium` `depends:[S06,S07]`
  > After this: Forecast deltas are categorized into operationally meaningful signal levels with market context.

- [ ] **S09: Trading Signal and Backtest Engine** `[sketch]` `risk:high` `depends:[S08]`
  > After this: Trading signal objects, price sensitivity, risk filters, and backtest metrics can be generated from forecast deltas.

- [ ] **S10: Storage Layer** `[sketch]` `risk:medium` `depends:[S03,S04]`
  > After this: Forecast, signal, and cache metadata can be stored and reloaded from DuckDB or Parquet.

- [ ] **S11: FastAPI Backend** `[sketch]` `risk:medium` `depends:[S06,S09,S10]`
  > After this: FastAPI endpoints expose forecast, trading signal, and backtest functionality with explicit error handling.

- [ ] **S12: Explanation Service** `[sketch]` `risk:medium` `depends:[S06,S09]`
  > After this: Forecast and trading explanations describe drivers, confidence, uncertainty, and attribution.

- [ ] **S13: Dashboard and Backtest Views** `[sketch]` `risk:medium` `depends:[S07,S09,S11,S12]`
  > After this: A Streamlit dashboard visualizes forecasts, satellite features, trading impact, and backtest results.

- [ ] **S14: Testing and Final Demo Polish** `[sketch]` `risk:medium` `depends:[S01,S02,S03,S04,S05,S06,S07,S08,S09,S10,S11,S12,S13]`
  > After this: The prototype has deterministic tests, smoke checks, documentation, and final demo polish.

## Boundary Map

| Area | Owns | Does Not Own |
|---|---|---|
| Ingestion | Provider adapters, normalized schemas, provenance, cache keys, data quality | Forecast modeling or signal thresholds |
| Features | Time alignment, deterministic feature creation, target variables, temporal splits | Network calls or live trading |
| Forecast | Baselines, solar and wind models, uncertainty, evaluation | Order execution or raw provider APIs |
| Signals | Forecast-delta thresholds, risk filters, trading-impact objects, backtest inputs | Raw satellite processing or live broker integration |
| API and UI | Demo orchestration, error surfaces, visualization, explanation display | Hidden domain logic outside package modules |
