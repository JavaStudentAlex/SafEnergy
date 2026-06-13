---
estimated_steps: 1
estimated_files: 3
skills_used: []
---

# T04: Route API through orchestrator

Update API routes that produce forecast-to-signal outputs to call the orchestrator instead of duplicating data preparation, forecast, signal, explanation, or storage logic.

## Inputs

- `src/safenergy/api/routes.py`
- `src/safenergy/pipeline.py`

## Expected Output

- `src/safenergy/api/routes.py`
- `tests/test_api.py`

## Verification

uv run pytest tests/test_api.py tests/test_pipeline.py -q

## Observability Impact

Aligns API diagnostics with orchestrator phase diagnostics.
