# S06: Dashboard Backend Integration

**Goal:** Turn the manual dashboard into a truthful frontend for the backend forecast-to-signal path.
**Demo:** The Streamlit dashboard requests forecasts from the FastAPI backend or a shared service client and displays live, cached, fixture, and unavailable states clearly.

## Must-Haves

- Dashboard can call the backend or shared service layer for forecast-to-signal results.
- UI labels distinguish live, cached, fixture, and unavailable-provider outputs.
- User-visible diagnostics include provenance, uncertainty, and failure mode.
- Tests or smoke checks verify dashboard rendering for success and unavailable states.

## Proof Level

- This slice proves: Dashboard tests plus a manual or scripted smoke run where practical.

## Integration Closure

The demo surface reflects the same behavior as the API and no longer relies only on isolated local calculations.

## Verification

- Adds visible status panels and diagnostic copy for data mode, provider state, and model status.

## Tasks

- [ ] **T01: Create dashboard service client boundary** `est:0.75d`
  Introduce a dashboard-facing client or service function that can request forecast-to-signal results from FastAPI when configured or call the shared orchestrator locally for deterministic tests.
  - Files: `src/safenergy/api/dashboard.py`, `src/safenergy/api/routes.py`, `tests/test_dashboard.py`
  - Verify: uv run pytest tests/test_dashboard.py tests/test_api.py -q

- [ ] **T02: Display provenance and data mode clearly** `est:0.5d`
  Update dashboard panels to show whether a result used live, cached, fixture, or unavailable provider data, plus provenance summaries, uncertainty, and model or baseline mode.
  - Files: `src/safenergy/api/dashboard.py`, `tests/test_dashboard.py`
  - Verify: uv run pytest tests/test_dashboard.py -q

- [ ] **T03: Add unavailable state UI path** `est:0.5d`
  Add dashboard behavior for missing credentials, provider outage, missing model artifact, and stale data so the UI explains the issue instead of implying live results are available.
  - Files: `src/safenergy/api/dashboard.py`, `tests/test_dashboard.py`
  - Verify: uv run pytest tests/test_dashboard.py -q

- [ ] **T04: Document dashboard backend run modes** `est:0.25d`
  Update demo documentation with commands for running FastAPI and Streamlit, how dashboard backend mode is selected, and what live, cached, fixture, and unavailable labels mean.
  - Files: `docs/demo.md`, `docs/CONFIGURATION.md`
  - Verify: uv run pytest tests/test_dashboard.py -q && uv run ruff check src/safenergy/api/dashboard.py tests/test_dashboard.py

## Files Likely Touched

- src/safenergy/api/dashboard.py
- src/safenergy/api/routes.py
- tests/test_dashboard.py
- docs/demo.md
- docs/CONFIGURATION.md
