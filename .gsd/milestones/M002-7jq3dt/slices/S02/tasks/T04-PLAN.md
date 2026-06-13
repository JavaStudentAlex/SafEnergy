---
estimated_steps: 1
estimated_files: 2
skills_used: []
---

# T04: Document market data modes and limits

Document live, fixture, and unavailable market data behavior, including no-live-trading scope and why provider data is for decision support and backtests only.

## Inputs

- `src/safenergy/ingest/market.py`
- `.gsd/REQUIREMENTS.md`

## Expected Output

- `docs/CONFIGURATION.md`
- `docs/forecast_contract.md`

## Verification

uv run ruff check src/safenergy/ingest/market.py src/safenergy/features/alignment.py tests/ingest/test_market.py tests/test_features.py && uv run pytest tests/ingest/test_market.py tests/test_features.py -q

## Observability Impact

Makes live versus fixture market state explicit in run documentation.
