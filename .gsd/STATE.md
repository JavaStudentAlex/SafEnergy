# GSD State

**Active Milestone:** M003-4jb56n: No Training Forecast Method Stack
**Active Slice:**
**Phase:** completed
**Requirements Status:** 12 active · 0 validated · 1 deferred · 0 out of scope

## Milestone Registry
- 🔄 **M001-7qeil2:** Renewable Forecasting Trading Prototype
- 🔄 **M002-7jq3dt:** Live Data Forecast Serving Integration
- ⬜ **M003-4jb56n:** No Training Forecast Method Stack
- ⬜ **M004-njfgw0:** Frontend Alignment Foundation
- ⬜ **M005-9qprou:** Forecast and Market Credibility Layer
- ⬜ **M006-cgt3hd:** Commitment Action Loop
- ⬜ **M007-19pj5r:** Portfolio Health Dashboard Closure

## Recent Decisions
- Completed S06 of M003-4jb56n: Documented rationale for deterministic baselines and added end-to-end integration tests to test_no_training_stack.py.
- Completed S05 of M003-4jb56n: API and Signal Integration for no-training forecast stack.
- Completed S04 of M003-4jb56n: Implemented deterministic method selector with confidence scoring, fallback diagnostics, and uncertainty metadata.
- Completed S03 of M003-4jb56n: Implemented Wind Power-Curve Approximation and Regional Capacity Fallback methods for no-training forecast stack.
- Completed S02 of M003-4jb56n: Implemented Solar and Persistence Methods including smart persistence baseline and pvlib physical baseline.
- Completed S01 of M003-4jb56n: Defined the Forecast Method Contract in docs/forecast_contract.md.
- Completed S08 of M002-7jq3dt: Handled raw exception leakages across API routes and the global exception handler, added the root documentation (README.md).
- Completed S07 of M002-7jq3dt: Added backtest assumptions including transaction costs and slippage, enforced issue-time leakage guard, and added source attribution limitations to explanation payload.
- D001 (M003-4jb56n planning): How to represent the no-training forecast strategy -> Create a separate queued milestone M003-4jb56n focused only on the unique no-training forecast method stack
- Completed S06 of M002-7jq3dt: Refactored the Streamlit dashboard to hit FastAPI endpoints instead of calling python functions directly, added Orchestrator tab.
- Completed S05 of M002-7jq3dt: Created End to End Orchestrator which seamlessly runs data retrieval, feature building, inference, signals generation and explanations.
- Completed S04 of M002-7jq3dt: Created forecast serving boundary supporting model inference and persistence fallback, connected it to API.
- Completed S03 of M002-7jq3dt: Added provenance and geospatial metadata tracking in the duckdb storage client.
- Completed S02 of M002-7jq3dt: Replaced deterministic market mocks with a provider-shaped adapter, added fixture fallback and network failure simulation.
- Completed S01 of M002-7jq3dt: Implemented satellite discovery via fixture fallback and minimal deterministic satellite feature extraction.
- Verified all tasks in M001-7qeil2 are complete and tests are passing.
- Completed S14: Testing and Final Demo Polish, including documentation and smoke tests.
- Implemented Dashboard and Backtest Views using Streamlit for S13.
- Implemented Explanation Service including human-readable summaries, confidence, and attribution for S12.
- Implemented FastAPI Backend including REST endpoints for signals, backtesting, and forecasts for S11.
- Implemented Storage Layer using DuckDB and Parquet for S10.
- Implemented backtest evaluation engine converting signals and price changes into trading metrics for S09.
- Implemented Signal Thresholds and Market Context logic, creating categorical signals and risk adjustments for S08.
- Implemented Forecast Evaluation metrics, model vs baseline reporting, and timezone-aware temporal splitting for S07.
- Implemented Forecasting Model Service using LightGBM with quantile uncertainty and joblib serialization for S06.
- Implemented Forecast Baselines, including persistence, same-hour-yesterday, and weather-only models for S05.
- Implemented Data Ingestion and Quality Checks with mock markets and Open-Meteo adapters for S03.
- Defined MVP scope, forecasting horizons, and success contracts in `docs/forecast_contract.md` for S01.
- Implemented repository structure, configuration via `pydantic-settings`, and base directories for S02.

## Blockers
- None
