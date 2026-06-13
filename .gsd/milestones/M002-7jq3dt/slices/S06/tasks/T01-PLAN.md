---
estimated_steps: 1
estimated_files: 3
skills_used: []
---

# T01: Create dashboard service client boundary

Introduce a dashboard-facing client or service function that can request forecast-to-signal results from FastAPI when configured or call the shared orchestrator locally for deterministic tests.

## Inputs

- `src/safenergy/api/dashboard.py`
- `src/safenergy/api/routes.py`

## Expected Output

- `src/safenergy/api/dashboard.py`
- `tests/test_dashboard.py`

## Verification

uv run pytest tests/test_dashboard.py tests/test_api.py -q

## Observability Impact

Adds dashboard-visible backend mode, request status, and fallback reason.
