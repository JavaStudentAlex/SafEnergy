---
applyTo: "**/tests/**/*"
description: "Test conventions, organization, and verification patterns for SafEnergy."
---

# Test Instructions

## Scope

This covers pytest tests under `tests/` and any deterministic script or CLI
verification used to prove repository behavior.

## Tooling Rules

- Use `uv run pytest ...` for tests.
- Use `uv run ruff ...` for configured lint checks.
- Prefer targeted test paths first; run broader tests when touched behavior
  crosses package boundaries.

## Behavioral Overlay

For test changes, also apply:

- `.github/instructions/code_writing_behavior.instructions.md`
- `.github/instructions/python_renewable_forecasting.instructions.md` when
  forecasting, geospatial, weather, generation, signal, or backtest behavior is
  involved

## Test Organization

- Keep shared fixtures in `tests/conftest.py` or explicit subsystem helpers.
- Use deterministic synthetic time series for generation, irradiance, cloud,
  wind, price, and balancing data whenever possible.
- Use small STAC, raster, GeoJSON, CSV, or Parquet fixtures instead of requiring
  live provider calls or large local datasets.
- Use `tmp_path` for filesystem, cache, output, database, and report tests.
- Avoid tests that require external APIs, credentials, Redis, paid data,
  provider network access, or large datasets unless they are clearly marked and
  excluded from the default suite.

## Test Conventions

- Assert on contract boundaries: issue time, valid time, forecast horizon,
  timezone conversion, CRS, raster shape, spatial aggregation, target leakage,
  baseline comparison, signal threshold, and output schema.
- Keep tests small and focused on one behavior.
- Include explicit failure assertions for missing credentials, invalid site
  metadata, unavailable provider data, empty rasters, CRS mismatch, missing
  price intervals, and stale forecasts.
- Prefer numeric tolerances that reflect data resolution, forecast horizon, and
  fixture scale rather than broad arbitrary tolerances.
- For regressions, add the narrowest test that would have failed before the fix.

## Repository-Specific Priorities

- Cover forecast target construction and delta-from-expectation logic.
- Cover temporal splits and data-availability checks to prevent leakage.
- Cover satellite/weather feature alignment by site or region.
- Cover solar clear-sky or persistence baselines before complex model claims.
- Cover wind ramp and power-curve transformations where they are implemented.
- Cover trading signal generation and backtest metric calculations with
  synthetic market data.
- Cover output path behavior for generated forecasts, plots, reports, caches,
  and model artifacts with `tmp_path`.

## Running Tests

Examples from the repository root:

```bash
uv run pytest tests -q
uv run pytest tests/test_features.py -q
uv run pytest tests/test_forecast_targets.py -q
uv run pytest tests/test_backtest.py -q
```
