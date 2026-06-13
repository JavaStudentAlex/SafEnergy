# S05: End to End Orchestrator

**Goal:** Connect existing components into one operational forecast-to-trade decision-support path.
**Demo:** A single orchestration function or service path runs data retrieval, feature building, model inference, baseline comparison, signal generation, explanation, storage, and API response assembly.

## Must-Haves

- Orchestrator has clear phases and typed phase results.
- Happy path produces forecast, signal, explanation, backtest-ready record, and stored artifact.
- Failure path records last successful phase, error class, timestamp, and retry or fallback hint.
- Tests prove phase ordering and failure visibility.

## Proof Level

- This slice proves: End-to-end fixture smoke test and focused unit tests for phase failure handling.

## Integration Closure

API and dashboard use the orchestrator rather than duplicating domain logic.

## Verification

- Adds phase-level status, last error, retry count or fallback reason, and artifact identifiers.

## Tasks

- [ ] **T01: Design orchestration phase model** `est:0.75d`
  Define typed phase inputs and outputs for provider retrieval, feature construction, forecast serving, baseline comparison, signal generation, explanation, storage, and response assembly. Keep orchestration separate from route handlers.
  - Files: `src/safenergy/pipeline.py`, `src/safenergy/api/routes.py`, `tests/test_pipeline.py`
  - Verify: uv run pytest tests/test_pipeline.py -q

- [ ] **T02: Implement fixture backed happy path** `est:1d`
  Wire existing deterministic weather, market, generation, feature, forecast, signal, explanation, and storage components through the orchestrator so one call returns a complete decision-support result.
  - Files: `src/safenergy/pipeline.py`, `src/safenergy/signals/pipeline.py`, `tests/test_pipeline.py`, `scripts/smoke_check.py`
  - Verify: uv run pytest tests/test_pipeline.py tests/test_signals_pipeline.py tests/test_storage.py -q

- [ ] **T03: Implement phase failure diagnostics** `est:0.75d`
  Make each orchestrator phase return or raise typed safe diagnostics that preserve last successful phase, error class, timestamp, retry or fallback hint, and source mode without exposing secrets.
  - Files: `src/safenergy/pipeline.py`, `tests/test_pipeline.py`, `src/safenergy/api/routes.py`
  - Verify: uv run pytest tests/test_pipeline.py tests/test_api.py -q

- [ ] **T04: Route API through orchestrator** `est:0.5d`
  Update API routes that produce forecast-to-signal outputs to call the orchestrator instead of duplicating data preparation, forecast, signal, explanation, or storage logic.
  - Files: `src/safenergy/api/routes.py`, `tests/test_api.py`, `tests/test_pipeline.py`
  - Verify: uv run pytest tests/test_api.py tests/test_pipeline.py -q

- [ ] **T05: Add end to end smoke check** `est:0.5d`
  Extend or add a deterministic smoke check that runs the orchestrator end to end using fixtures and confirms forecast, signal, explanation, storage artifact, and diagnostic fields are present.
  - Files: `scripts/smoke_check.py`, `tests/test_pipeline.py`
  - Verify: uv run python scripts/smoke_check.py && uv run pytest tests/test_pipeline.py -q

## Files Likely Touched

- src/safenergy/pipeline.py
- src/safenergy/api/routes.py
- tests/test_pipeline.py
- src/safenergy/signals/pipeline.py
- scripts/smoke_check.py
- tests/test_api.py
