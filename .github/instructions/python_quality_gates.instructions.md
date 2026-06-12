---
applyTo: "**/*.py"
description: "Python linting, formatting, and test gate policy for SafEnergy."
---

# Python Quality Gates

## Purpose and Scope

This file defines the verification policy for Python changes in this repository.

Applies to:

- Python package modules under `src/`, when present
- scripts under `scripts/`, when present
- application modules under `app/`, when present
- pytest tests under `tests/`, when present
- repository Python tooling

Does not apply to docs-only changes, although docs changes should still be
checked for path and command accuracy.

## Tooling Rules

- Use `uv run ...` from the repository root.
- Use `pyproject.toml` and GitHub Actions workflows as the source of truth.
- Use Ruff for the configured high-signal checks.
- The current scaffold is lintable as a whole. Keep the lint gate aligned with
  `pyproject.toml`.

## Quality Gates

Run from the repository root when Python code changes:

```bash
uv run ruff check .
```

If tests exist, also run:

```bash
uv run pytest tests -q
```

After dependency changes, run:

```bash
uv lock --check
```

For targeted behavior changes, prefer the closest tests or deterministic script
smoke checks. Examples:

```bash
uv run pytest tests/test_features.py -q
uv run pytest tests/test_forecast_targets.py -q
uv run pytest tests/test_backtest.py -q
```

Only run provider-dependent scripts when credentials, rate limits, and cache
paths are available and the user has allowed external access.

## Target Selection Guidance

- Ingestion changes -> provider adapter tests, schema tests, cache/provenance
  tests, and fixture-backed parser tests.
- Satellite/geospatial changes -> raster alignment, CRS, footprint, and
  aggregation tests.
- Weather/PV changes -> irradiance, clear-sky, PV conversion, and time-index
  tests.
- Wind changes -> wind feature, ramp, power-curve, and temporal alignment tests.
- Forecast changes -> target construction, leakage checks, baseline comparisons,
  and metric tests.
- Trading signal changes -> threshold, uncertainty, market feature, and
  backtest tests.
- API changes -> request/response schema, validation, and error-path tests.

## Notes

- Report blocked or failed gates explicitly.
- Do not claim verification you did not run.
- If a full suite is blocked by missing credentials, network access, large data,
  provider limits, or optional native dependencies, run the most relevant
  deterministic subset and state the limitation.
