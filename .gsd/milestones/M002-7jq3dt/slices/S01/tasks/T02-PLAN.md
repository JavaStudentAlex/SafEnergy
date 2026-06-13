---
estimated_steps: 1
estimated_files: 3
skills_used: []
---

# T02: Implement provider discovery with fixture fallback

Implement a bounded Copernicus or STAC-style discovery adapter that can use live HTTP when configured and deterministic fixtures when not. The adapter must return normalized item metadata or a typed unavailable-provider result instead of raising raw network errors.

## Inputs

- `src/safenergy/ingest/weather.py`
- `src/safenergy/ingest/market.py`

## Expected Output

- `src/safenergy/ingest/satellite.py`
- `tests/fixtures/satellite/`
- `tests/ingest/test_satellite.py`

## Verification

uv run pytest tests/ingest/test_satellite.py -q

## Observability Impact

Records discovery mode, item count, provider status, cache key, and failure class.
