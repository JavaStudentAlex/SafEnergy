# S02: Live Market and Generation Adapter

**Goal:** Replace purely deterministic market mocks with a provider-shaped adapter that can support real or historically correct market and generation data.
**Demo:** A market adapter normalizes live or fixture-backed ERCOT-style price and generation records with issue-time-safe provenance and staleness checks.

## Must-Haves

- Market and generation inputs normalize to explicit schemas.
- Provider, query time, valid time, cache key, and staleness diagnostics are preserved.
- Network and credential failures return typed diagnostics.
- Fixture tests prove deterministic behavior without external access.

## Proof Level

- This slice proves: Adapter contract tests, fixture integration tests, and optional live smoke when public access is available.

## Integration Closure

Feature, backtest, and signal code can consume normalized market and generation data independent of provider implementation.

## Verification

- Adds staleness, provider availability, record-count, and cache-hit diagnostics.

## Tasks

- [x] **T01: Define market provider contracts** `est:0.5d`
  Add provider-shaped request and response objects for price, generation, valid time, issue time, market node or region, cache key, staleness, and unavailable-provider diagnostics. Keep existing deterministic behavior as a fixture mode.
  - Files: `src/safenergy/ingest/market.py`, `tests/ingest/test_market.py`
  - Verify: uv run pytest tests/ingest/test_market.py -q

- [x] **T02: Implement ERCOT style adapter seam** `est:1d`
  Implement an ERCOT-style adapter interface that can call a configured live endpoint when enabled, otherwise loads fixture-backed records. Return typed unavailable-provider diagnostics for HTTP, credential, schema, and empty-result failures.
  - Files: `src/safenergy/ingest/market.py`, `tests/fixtures/market/`, `tests/ingest/test_market.py`
  - Verify: uv run pytest tests/ingest/test_market.py -q

- [x] **T03: Align generation and price records for features** `est:0.5d`
  Add deterministic alignment helpers that join provider-shaped generation and price records on UTC valid time and region without leaking future values into forecast issue time.
  - Files: `src/safenergy/features/alignment.py`, `tests/test_features.py`, `tests/ingest/test_market.py`
  - Verify: uv run pytest tests/test_features.py tests/ingest/test_market.py -q

- [x] **T04: Document market data modes and limits** `est:0.25d`
  Document live, fixture, and unavailable market data behavior, including no-live-trading scope and why provider data is for decision support and backtests only.
  - Files: `docs/CONFIGURATION.md`, `docs/forecast_contract.md`
  - Verify: uv run ruff check src/safenergy/ingest/market.py src/safenergy/features/alignment.py tests/ingest/test_market.py tests/test_features.py && uv run pytest tests/ingest/test_market.py tests/test_features.py -q

## Files Likely Touched

- src/safenergy/ingest/market.py
- tests/ingest/test_market.py
- tests/fixtures/market/
- src/safenergy/features/alignment.py
- tests/test_features.py
- docs/CONFIGURATION.md
- docs/forecast_contract.md
