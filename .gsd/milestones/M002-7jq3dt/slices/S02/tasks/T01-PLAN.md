---
estimated_steps: 1
estimated_files: 2
skills_used: []
---

# T01: Define market provider contracts

Add provider-shaped request and response objects for price, generation, valid time, issue time, market node or region, cache key, staleness, and unavailable-provider diagnostics. Keep existing deterministic behavior as a fixture mode.

## Inputs

- `SafEnergy_Implementation_Verdict.md`
- `src/safenergy/signals/market.py`

## Expected Output

- `src/safenergy/ingest/market.py`
- `tests/ingest/test_market.py`

## Verification

uv run pytest tests/ingest/test_market.py -q

## Observability Impact

Adds normalized provider status and staleness metadata to market and generation inputs.
