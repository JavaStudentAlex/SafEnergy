---
estimated_steps: 1
estimated_files: 3
skills_used: []
---

# T03: Implement phase failure diagnostics

Make each orchestrator phase return or raise typed safe diagnostics that preserve last successful phase, error class, timestamp, retry or fallback hint, and source mode without exposing secrets.

## Inputs

- `src/safenergy/pipeline.py`
- `src/safenergy/api/routes.py`

## Expected Output

- `src/safenergy/pipeline.py`
- `tests/test_pipeline.py`

## Verification

uv run pytest tests/test_pipeline.py tests/test_api.py -q

## Observability Impact

Makes unattended failures debuggable through structured phase state.
