---
estimated_steps: 1
estimated_files: 4
skills_used: []
---

# T01: Design forecast serving service boundary

Extract a forecast-serving service that accepts region, horizon, issue time, and normalized provider inputs, then returns forecast delta, interval, baseline comparison, provenance, model version, feature schema, and diagnostics.

## Inputs

- `src/safenergy/forecast/models.py`
- `src/safenergy/forecast/baselines.py`
- `src/safenergy/features/engineering.py`

## Expected Output

- `src/safenergy/forecast/service.py`
- `tests/test_forecast_service.py`

## Verification

uv run pytest tests/test_forecast_service.py tests/test_api.py -q

## Observability Impact

Adds canonical inference status and diagnostic payloads.
