---
applyTo: "*.py"
description: "Python conventions, renewable forecasting contracts, and forecast-to-trade boundaries for SafEnergy."
---

# Python Renewable Forecasting Conventions

## Scope

This covers Python code under the repository, including future package modules,
tests, scripts, API routes, ingestion jobs, forecasting models, and backtests.

## Tooling Rules

- Use `uv run ...` for Python execution.
- Use `pyproject.toml` as the source of truth for runtime and dev tools.
- Use Ruff for the configured high-signal lint checks. Do not introduce another
  formatter or linter without updating project configuration and CI.

## Architecture Rules

- Keep scripts runnable from the repository root.
- Keep external provider access explicit. API clients should accept credentials
  through configuration or environment variables, never literals in source code.
- Keep generated artifacts under ignored paths such as `data/`, `outputs/`,
  `models/`, or local cache directories unless a task explicitly changes the
  output contract.
- Keep API routes, scheduler jobs, and CLI scripts thin. Domain logic belongs in
  package modules with deterministic functions where practical.
- Keep ingestion adapters separate from feature builders. A feature function
  should not unexpectedly fetch data from a remote API.
- Keep forecast models separate from trading execution. Trading logic should
  consume forecasts, uncertainty, and market context through explicit schemas.
- Keep reusable data structures typed with dataclasses, Pydantic models, or
  clear dictionaries when shape matters.
- Avoid global mutable state and implicit caches unless they are necessary and
  tested or isolated inside one adapter.
- Make failure modes contextual for missing credentials, unavailable providers,
  empty rasters, CRS mismatch, missing time ranges, stale weather, missing
  market prices, and dependency gaps.

## Domain Rules

- Treat forecast horizons as contracts. Name whether code is nowcast, intraday,
  day-ahead, or another explicit horizon.
- Treat the main target as a delta from expected generation when the feature or
  signal is trading-facing.
- Keep timestamp handling timezone-aware. Prefer UTC internally and document
  local market or site timezone conversions.
- Keep issue time, valid time, delivery interval, and data availability time
  separate. Do not use future data in forecast features.
- Preserve spatial metadata for every raster or site feature: CRS, resolution,
  bounds, footprint, and aggregation method.
- Keep solar concepts explicit: irradiance, cloud cover, clear-sky baseline,
  panel/site metadata, temperature effects, and PV conversion assumptions.
- Keep wind concepts explicit: hub-height assumptions, wind speed/direction,
  air density or temperature effects, power curve assumptions, and ramp rates.
- Compare models to simple baselines before claiming improvement.
- Use temporal validation for models and backtests. Random splits are not
  acceptable for forecast or trading performance claims unless clearly limited
  to non-temporal unit behavior.
- Keep uncertainty and confidence separate from point forecasts.
- Trading outputs are research signals by default, not live orders.

## Dataset and Output Rules

- Do not commit secrets, raw satellite tiles, large weather extracts, generated
  model binaries, database files, local caches, or market data that is not
  redistributable.
- Use small deterministic fixtures for tests. Avoid requiring live external APIs
  in the default test suite.
- When adding output files, make paths configurable where practical and safe to
  overwrite only when the caller opted in or the script contract already owns
  the path.
- Preserve data provenance in generated tables: provider, request window, valid
  time, site/region, spatial aggregation, and processing version.

## Verification

- For Python changes, run the gates from
  `.github/instructions/python_quality_gates.instructions.md`.
- For behavior changes, run targeted pytest paths when tests exist.
- For ingestion changes, prefer mocked provider responses or cached sample
  fixtures before relying on live services.
- For forecasting changes, include a baseline comparison, temporal split, and
  metric when practical.
- For trading/backtest changes, include leakage checks, fee/slippage assumptions
  if modeled, and whether market data is real or synthetic.
- State missing external credentials, network access, provider limits, large
  data, or optional dependency blocks explicitly.
