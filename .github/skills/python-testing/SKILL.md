---
name: python-testing
description: Run pytest for SafEnergy using uv with forecast-aware target selection. Use when changing forecasting code, tests, provider adapters, signals, backtests, or debugging failures.
---

# Python Testing Skill

Use this skill to run and inspect Python tests for this repository.

## Scope

- Test directory: `tests/`, when present
- Shared fixtures: `tests/conftest.py`, when present
- Preferred execution wrapper: `uv run ...`
- CI target-selection reference: `.github/workflows/ci-tests.yml`

## Running Tests

```bash
uv run pytest tests -q
```

Suggested targeted commands when tests exist:

```bash
uv run pytest tests/test_features.py -q
uv run pytest tests/test_forecast_targets.py -q
uv run pytest tests/test_backtest.py -q
```

## Target Selection

- Ingestion changes -> provider adapter, cache, provenance, and schema tests.
- Satellite/geospatial changes -> CRS, raster alignment, footprint, and
  aggregation tests.
- Weather/PV/wind changes -> feature transformation and temporal-alignment
  tests.
- Forecast changes -> target construction, leakage checks, baseline, and metric
  tests.
- Trading signal or backtest changes -> signal threshold, market data, and
  backtest metric tests.
- API or service changes -> request/response, validation, and error-path tests.

## Pass Criteria

- The selected test command exits with code `0`.
- All collected tests pass.
- Any skipped or blocked provider, credential, network, large-data, Redis, or
  optional dependency checks are named explicitly.

## Troubleshooting

If dev dependencies are missing:

```bash
uv sync --group dev
```
