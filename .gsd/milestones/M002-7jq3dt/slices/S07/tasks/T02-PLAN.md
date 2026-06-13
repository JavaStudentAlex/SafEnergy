---
estimated_steps: 1
estimated_files: 4
skills_used: []
---

# T02: Enforce issue time leakage guards

Add validation that backtest records and feature rows do not use inputs with valid times unavailable at the forecast issue time. Fail with clear diagnostics when leakage is detected.

## Inputs

- `src/safenergy/signals/backtest.py`
- `src/safenergy/features/alignment.py`

## Expected Output

- `src/safenergy/signals/backtest.py`
- `tests/test_backtest.py`

## Verification

uv run pytest tests/test_backtest.py tests/test_features.py -q

## Observability Impact

Records leakage-check status and offending timestamp fields.
