---
estimated_steps: 1
estimated_files: 3
skills_used: []
---

# T01: Define satellite ingestion contracts

Add explicit satellite provider settings and normalized data objects for discovery requests, discovered items, footprints, CRS, cloud quality, cache keys, and unavailable-provider diagnostics. Keep credentials in settings only and never in source or logs.

## Inputs

- `SafEnergy_Implementation_Verdict.md`
- `.gsd/REQUIREMENTS.md`

## Expected Output

- `src/safenergy/ingest/satellite.py`
- `tests/ingest/test_satellite.py`

## Verification

uv run pytest tests/ingest/test_satellite.py -q

## Observability Impact

Creates typed diagnostic fields for provider, query window, CRS, footprint, cache key, and unavailable reason.
