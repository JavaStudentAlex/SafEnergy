# S03: Provenance and Geospatial Metadata Backbone

**Goal:** Make provenance and spatial metadata durable enough for live-data forecast claims and troubleshooting.
**Demo:** Forecast inputs and derived features carry provider, issue time, valid time, CRS, footprint, cache key, and quality metadata through storage.

## Must-Haves

- Shared provenance objects cover satellite, weather, market, generation, and derived features.
- Storage persists and reloads provenance without losing timezone or CRS metadata.
- API schemas can expose provenance summaries.
- Tests verify serialization, UTC handling, and CRS preservation.

## Proof Level

- This slice proves: Unit and storage integration tests.

## Integration Closure

Forecast serving and dashboard slices can surface the same provenance object rather than rebuilding ad hoc metadata.

## Verification

- Adds structured provenance summaries and quality flags to stored artifacts and responses.

## Tasks

- [ ] **T01: Create shared provenance objects** `est:0.75d`
  Introduce reusable provenance and quality objects for provider, query time, valid time, issue time, spatial footprint, CRS, resolution, cache key, source mode, and diagnostic flags. Refactor existing weather, market, and feature code only at stable boundaries.
  - Files: `src/safenergy/core/provenance.py`, `src/safenergy/ingest/weather.py`, `src/safenergy/ingest/market.py`, `tests/core/test_provenance.py`
  - Verify: uv run pytest tests/core/test_provenance.py tests/ingest/test_weather.py tests/ingest/test_market.py -q

- [ ] **T02: Persist provenance in storage layer** `est:0.75d`
  Extend DuckDB or storage serialization so forecast inputs, outputs, and signals can store and reload provenance metadata without losing UTC timestamp or CRS information.
  - Files: `src/safenergy/storage/client.py`, `tests/test_storage.py`, `src/safenergy/api/schemas.py`
  - Verify: uv run pytest tests/test_storage.py tests/core/test_provenance.py -q

- [ ] **T03: Expose provenance summaries in API schemas** `est:0.5d`
  Add compact API schema fields for provenance, quality flags, source mode, and diagnostics. Keep detailed raw provider payloads out of public responses.
  - Files: `src/safenergy/api/schemas.py`, `tests/test_api.py`
  - Verify: uv run pytest tests/test_api.py tests/core/test_provenance.py -q

- [ ] **T04: Verify timezone and CRS contracts** `est:0.5d`
  Add focused tests for UTC normalization, issue-time versus valid-time distinction, CRS serialization, and footprint round trips across provenance, storage, and API schemas.
  - Files: `tests/core/test_provenance.py`, `tests/test_storage.py`, `tests/test_api.py`
  - Verify: uv run pytest tests/core/test_provenance.py tests/test_storage.py tests/test_api.py -q

## Files Likely Touched

- src/safenergy/core/provenance.py
- src/safenergy/ingest/weather.py
- src/safenergy/ingest/market.py
- tests/core/test_provenance.py
- src/safenergy/storage/client.py
- tests/test_storage.py
- src/safenergy/api/schemas.py
- tests/test_api.py
