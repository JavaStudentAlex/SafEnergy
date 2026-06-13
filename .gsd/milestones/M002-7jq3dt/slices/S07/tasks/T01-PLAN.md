---
estimated_steps: 1
estimated_files: 3
skills_used: []
---

# T01: Add backtest assumption model

Extend backtest inputs and outputs with transaction cost, fee, slippage, liquidity, position sizing, delivery interval, market holiday, and no-live-trading assumption fields. Defaults must be explicit, not hidden.

## Inputs

- `src/safenergy/signals/backtest.py`
- `src/safenergy/signals/objects.py`

## Expected Output

- `src/safenergy/signals/backtest.py`
- `tests/test_backtest.py`

## Verification

uv run pytest tests/test_backtest.py tests/test_signals.py -q

## Observability Impact

Adds assumption metadata to backtest results and diagnostics.
