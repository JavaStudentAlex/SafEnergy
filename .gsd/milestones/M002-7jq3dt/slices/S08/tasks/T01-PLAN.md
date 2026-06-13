---
estimated_steps: 1
estimated_files: 4
skills_used: []
---

# T01: Replace raw API exception leakage

Audit FastAPI route error handling and replace raw exception-string responses with safe structured errors that include error code, phase or endpoint, diagnostic ID where practical, and user-safe message.

## Inputs

- `src/safenergy/api/main.py`
- `src/safenergy/api/routes.py`
- `src/safenergy/api/schemas.py`

## Expected Output

- `src/safenergy/api/main.py`
- `src/safenergy/api/routes.py`
- `tests/test_api.py`

## Verification

uv run pytest tests/test_api.py -q

## Observability Impact

Prevents raw exception leakage while preserving actionable diagnostics.
