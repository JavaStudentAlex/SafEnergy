# M002-7jq3dt: Live Data Forecast Serving Integration

**Vision:** Turn the completed SafEnergy prototype scaffold described in SafEnergy_Implementation_Verdict.md into a credible live-data forecast-to-signal service by replacing the highest-impact mocks with observable satellite, market, model-serving, orchestration, dashboard, backtest, and documentation paths while preserving the no-live-trading boundary.

## Success Criteria

- A target region and horizon can flow through real or credential-gated satellite discovery, market and generation retrieval, feature construction, model inference, baseline comparison, signal generation, explanation, storage, and API response.
- Forecast-serving responses no longer return fixed constants and include model, baseline, data provenance, uncertainty, and diagnostic metadata.
- Satellite, weather, market, generation, and derived feature artifacts preserve provider, valid time, issue time, spatial footprint, CRS, cache key, and quality or staleness diagnostics.
- The dashboard can call the backend forecast-to-signal path and clearly distinguish live, cached, fixture, and unavailable data states.
- Backtest and explanation outputs are honest enough for decision support by documenting costs, leakage controls, feature attribution limits, and no-live-trading constraints.
- Root README and demo documentation explain what is live, what is fixture-backed, how to run the service, and what external credentials are optional or required.

## Slices

- [x] **S01: Satellite Discovery and Feature Seed** `risk:high` `depends:[]`
  > After this: A small region and time range either discovers satellite provider items with CRS and footprint metadata or returns a typed unavailable-provider diagnostic.

- [ ] **S02: Live Market and Generation Adapter** `risk:high` `depends:[]`
  > After this: A market adapter normalizes live or fixture-backed ERCOT-style price and generation records with issue-time-safe provenance and staleness checks.

- [ ] **S03: Provenance and Geospatial Metadata Backbone** `risk:medium` `depends:[S01,S02]`
  > After this: Forecast inputs and derived features carry provider, issue time, valid time, CRS, footprint, cache key, and quality metadata through storage.

- [ ] **S04: Real Forecast Serving Path** `risk:high` `depends:[S01,S02,S03]`
  > After this: The forecast predict endpoint uses normalized inputs, feature engineering, baselines, model inference, and storage instead of fixed point and interval constants.

- [ ] **S05: End to End Orchestrator** `risk:high` `depends:[S04]`
  > After this: A single orchestration function or service path runs data retrieval, feature building, model inference, baseline comparison, signal generation, explanation, storage, and API response assembly.

- [ ] **S06: Dashboard Backend Integration** `risk:medium` `depends:[S05]`
  > After this: The Streamlit dashboard requests forecasts from the FastAPI backend or a shared service client and displays live, cached, fixture, and unavailable states clearly.

- [ ] **S07: Trading Backtest and Explanation Hardening** `risk:medium` `depends:[S05]`
  > After this: Backtest and explanation outputs document transaction-cost assumptions, leakage controls, issue-time constraints, and attribution limits tied to real forecast features.

- [ ] **S08: API Hardening and Root Documentation** `risk:medium` `depends:[S04,S06,S07]`
  > After this: A fresh user can read the root README, configure optional providers, run tests, start API and dashboard demos, and see safe API errors without raw exception leakage.

## Boundary Map

## Boundary Map

- **In scope**: satellite discovery or fixture fallback, ERCOT-style market and generation adapters, provenance metadata, forecast-serving integration, orchestration, dashboard-backend integration, safer backtest assumptions, explanation limits, API hardening, README updates.
- **Out of scope**: live broker integration, order submission, paid data acquisition without explicit user approval, production SRE deployment, and claims of financially validated trading performance.
- **External dependencies**: Copernicus or Sentinel STAC access, optional Earth Engine or NASA POWER paths, ERCOT-style public data access, local model artifacts, DuckDB storage, FastAPI, Streamlit.
