---
estimated_steps: 1
estimated_files: 4
skills_used: []
---

# T03: Add missing model and data diagnostics

Ensure missing model artifacts, missing provider inputs, stale data, and malformed feature rows return safe structured diagnostics rather than raw exceptions or placeholder forecasts. Use the provenance contract from S03 if available.

## Inputs

- `src/safenergy/api/schemas.py`
- `src/safenergy/forecast/service.py`

## Expected Output

- `tests/test_forecast_service.py`
- `tests/test_api.py`

## Verification

uv run pytest tests/test_forecast_service.py tests/test_api.py -q

## Observability Impact

Adds failure class, affected phase, fallback reason, and user-safe messages.
