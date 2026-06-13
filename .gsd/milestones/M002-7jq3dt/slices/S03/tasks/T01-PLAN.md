---
estimated_steps: 1
estimated_files: 4
skills_used: []
---

# T01: Create shared provenance objects

Introduce reusable provenance and quality objects for provider, query time, valid time, issue time, spatial footprint, CRS, resolution, cache key, source mode, and diagnostic flags. Refactor existing weather, market, and feature code only at stable boundaries.

## Inputs

- `src/safenergy/ingest/weather.py`
- `src/safenergy/ingest/market.py`
- `src/safenergy/features/engineering.py`

## Expected Output

- `src/safenergy/core/provenance.py`
- `tests/core/test_provenance.py`

## Verification

uv run pytest tests/core/test_provenance.py tests/ingest/test_weather.py tests/ingest/test_market.py -q

## Observability Impact

Standardizes provider status, data mode, quality flags, and cache references across inputs.
