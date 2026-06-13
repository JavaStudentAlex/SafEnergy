---
estimated_steps: 1
estimated_files: 2
skills_used: []
---

# T04: Lock response contract with tests

Add API contract tests proving the forecast endpoint does not return fixed placeholder constants for real fixture-backed prediction requests and includes provenance, baseline, uncertainty, and model metadata.

## Inputs

- `src/safenergy/api/routes.py`
- `src/safenergy/api/schemas.py`
- `tests/test_forecast_service.py`

## Expected Output

- `tests/test_api.py`

## Verification

uv run pytest tests/test_api.py tests/test_forecast_service.py -q

## Observability Impact

Prevents future regressions to constant mock predictions.
