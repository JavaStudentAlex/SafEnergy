# S01: Satellite Discovery and Feature Seed

**Goal:** Introduce the first real satellite ingestion seam and minimal satellite-derived feature contract without requiring paid credentials for deterministic tests.
**Demo:** A small region and time range either discovers satellite provider items with CRS and footprint metadata or returns a typed unavailable-provider diagnostic.

## Must-Haves

- Satellite provider configuration is explicit and secret-free.
- A bounded discovery call can return normalized item metadata or a typed unavailable-provider result.
- CRS, footprint, valid time, provider, cache key, and quality fields are represented in the normalized schema.
- Tests cover fixture-backed success and unavailable-provider behavior.

## Proof Level

- This slice proves: Contract and integration tests with mocked or fixture-backed provider responses; optional live smoke only when credentials and network are available.

## Integration Closure

Downstream slices can consume normalized satellite metadata and feature seeds without knowing provider-specific response shapes.

## Verification

- Adds provider, query window, cache key, item count, and unavailable-provider diagnostics.

## Tasks

- [ ] **T01: Define satellite ingestion contracts** `est:0.5d`
  Add explicit satellite provider settings and normalized data objects for discovery requests, discovered items, footprints, CRS, cloud quality, cache keys, and unavailable-provider diagnostics. Keep credentials in settings only and never in source or logs.
  - Files: `src/safenergy/core/config.py`, `src/safenergy/ingest/satellite.py`, `tests/ingest/test_satellite.py`
  - Verify: uv run pytest tests/ingest/test_satellite.py -q

- [ ] **T02: Implement provider discovery with fixture fallback** `est:1d`
  Implement a bounded Copernicus or STAC-style discovery adapter that can use live HTTP when configured and deterministic fixtures when not. The adapter must return normalized item metadata or a typed unavailable-provider result instead of raising raw network errors.
  - Files: `src/safenergy/ingest/satellite.py`, `tests/fixtures/satellite/`, `tests/ingest/test_satellite.py`
  - Verify: uv run pytest tests/ingest/test_satellite.py -q

- [ ] **T03: Create satellite feature seed extraction** `est:0.5d`
  Convert normalized discovered satellite items into minimal deterministic feature seeds such as cloud-cover proxy, scene age, spatial coverage ratio, and quality flags. Do not implement heavy raster processing until the lightweight contract is proven.
  - Files: `src/safenergy/features/satellite.py`, `src/safenergy/features/__init__.py`, `tests/test_features.py`, `tests/features/test_satellite_features.py`
  - Verify: uv run pytest tests/features/test_satellite_features.py tests/ingest/test_satellite.py -q

- [ ] **T04: Document satellite availability modes** `est:0.25d`
  Document live, cached, fixture, and unavailable satellite modes, including which environment variables enable live discovery and what deterministic tests prove without credentials.
  - Files: `docs/CONFIGURATION.md`, `docs/forecast_contract.md`
  - Verify: uv run ruff check src/safenergy/ingest/satellite.py src/safenergy/features/satellite.py tests/ingest/test_satellite.py tests/features/test_satellite_features.py && uv run pytest tests/ingest/test_satellite.py tests/features/test_satellite_features.py -q

## Files Likely Touched

- src/safenergy/core/config.py
- src/safenergy/ingest/satellite.py
- tests/ingest/test_satellite.py
- tests/fixtures/satellite/
- src/safenergy/features/satellite.py
- src/safenergy/features/__init__.py
- tests/test_features.py
- tests/features/test_satellite_features.py
- docs/CONFIGURATION.md
- docs/forecast_contract.md
