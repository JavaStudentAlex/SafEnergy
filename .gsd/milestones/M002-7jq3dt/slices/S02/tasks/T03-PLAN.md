---
estimated_steps: 1
estimated_files: 3
skills_used: []
---

# T03: Align generation and price records for features

Add deterministic alignment helpers that join provider-shaped generation and price records on UTC valid time and region without leaking future values into forecast issue time.

## Inputs

- `src/safenergy/ingest/market.py`
- `src/safenergy/features/alignment.py`

## Expected Output

- `src/safenergy/features/alignment.py`
- `tests/test_features.py`

## Verification

uv run pytest tests/test_features.py tests/ingest/test_market.py -q

## Observability Impact

Adds alignment diagnostics for dropped records, timezone normalization, and stale market data.
