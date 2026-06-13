---
estimated_steps: 1
estimated_files: 5
skills_used: []
---

# T04: Propagate honest trading metadata to API and dashboard

Expose backtest assumptions, leakage-check status, and explanation attribution labels in API and dashboard outputs so users understand the decision-support boundary.

## Inputs

- `src/safenergy/api/schemas.py`
- `src/safenergy/api/routes.py`
- `src/safenergy/api/dashboard.py`

## Expected Output

- `src/safenergy/api/schemas.py`
- `src/safenergy/api/routes.py`
- `src/safenergy/api/dashboard.py`
- `tests/test_api.py`
- `tests/test_dashboard.py`

## Verification

uv run pytest tests/test_api.py tests/test_dashboard.py tests/test_backtest.py tests/test_explanation.py -q

## Observability Impact

Surfaces assumption and attribution metadata at user-facing boundaries.
