---
estimated_steps: 1
estimated_files: 3
skills_used: []
---

# T02: Implement ERCOT style adapter seam

Implement an ERCOT-style adapter interface that can call a configured live endpoint when enabled, otherwise loads fixture-backed records. Return typed unavailable-provider diagnostics for HTTP, credential, schema, and empty-result failures.

## Inputs

- `src/safenergy/core/config.py`

## Expected Output

- `tests/fixtures/market/`
- `tests/ingest/test_market.py`

## Verification

uv run pytest tests/ingest/test_market.py -q

## Observability Impact

Records provider mode, endpoint family, row count, cache key, staleness, and failure class.
