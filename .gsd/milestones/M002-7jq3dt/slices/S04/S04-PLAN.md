# S04: Real Forecast Serving Path

**Goal:** Remove the most visible backend mock by connecting the forecast endpoint to the existing forecasting components and explicit fallback diagnostics.
**Demo:** The forecast predict endpoint uses normalized inputs, feature engineering, baselines, model inference, and storage instead of fixed point and interval constants.

## Must-Haves

- Forecast endpoint no longer returns fixed placeholder values for real prediction requests.
- Response includes forecast delta, baseline comparison, uncertainty, model version, feature schema, and provenance.
- Missing model artifact or missing data produces structured diagnostics.
- Tests cover success, missing model, and malformed request behavior.

## Proof Level

- This slice proves: API contract tests and targeted integration tests using deterministic fixtures.

## Integration Closure

Orchestration and dashboard can call one canonical forecast-serving path. This slice consumes the provenance contract from S03 when present.

## Verification

- Adds model version, feature schema, inference status, baseline status, and diagnostic fields.

## Tasks

- [ ] **T01: Design forecast serving service boundary** `est:0.75d`
  Extract a forecast-serving service that accepts region, horizon, issue time, and normalized provider inputs, then returns forecast delta, interval, baseline comparison, provenance, model version, feature schema, and diagnostics.
  - Files: `src/safenergy/forecast/service.py`, `src/safenergy/api/routes.py`, `src/safenergy/api/schemas.py`, `tests/test_api.py`
  - Verify: uv run pytest tests/test_forecast_service.py tests/test_api.py -q

- [ ] **T02: Connect endpoint to model and baselines** `est:1d`
  Replace fixed constants in the forecast prediction route with deterministic fixture-backed service execution that runs feature engineering, baseline comparison, optional LightGBM inference, and uncertainty assembly.
  - Files: `src/safenergy/api/routes.py`, `src/safenergy/forecast/service.py`, `tests/test_api.py`, `tests/test_forecast_service.py`
  - Verify: uv run pytest tests/test_forecast_service.py tests/test_api.py tests/test_baselines.py tests/test_forecast_models.py -q

- [ ] **T03: Add missing model and data diagnostics** `est:0.5d`
  Ensure missing model artifacts, missing provider inputs, stale data, and malformed feature rows return safe structured diagnostics rather than raw exceptions or placeholder forecasts. Use the provenance contract from S03 if available.
  - Files: `src/safenergy/forecast/service.py`, `src/safenergy/api/routes.py`, `tests/test_forecast_service.py`, `tests/test_api.py`
  - Verify: uv run pytest tests/test_forecast_service.py tests/test_api.py -q

- [ ] **T04: Lock response contract with tests** `est:0.5d`
  Add API contract tests proving the forecast endpoint does not return fixed placeholder constants for real fixture-backed prediction requests and includes provenance, baseline, uncertainty, and model metadata.
  - Files: `tests/test_api.py`, `tests/test_forecast_service.py`
  - Verify: uv run pytest tests/test_api.py tests/test_forecast_service.py -q

## Files Likely Touched

- src/safenergy/forecast/service.py
- src/safenergy/api/routes.py
- src/safenergy/api/schemas.py
- tests/test_api.py
- tests/test_forecast_service.py
