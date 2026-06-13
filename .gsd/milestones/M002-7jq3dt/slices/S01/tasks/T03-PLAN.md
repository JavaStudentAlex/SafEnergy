---
estimated_steps: 1
estimated_files: 4
skills_used: []
---

# T03: Create satellite feature seed extraction

Convert normalized discovered satellite items into minimal deterministic feature seeds such as cloud-cover proxy, scene age, spatial coverage ratio, and quality flags. Do not implement heavy raster processing until the lightweight contract is proven.

## Inputs

- `src/safenergy/ingest/satellite.py`

## Expected Output

- `src/safenergy/features/satellite.py`
- `tests/features/test_satellite_features.py`

## Verification

uv run pytest tests/features/test_satellite_features.py tests/ingest/test_satellite.py -q

## Observability Impact

Adds feature quality flags and source item references for downstream explanation and provenance.
