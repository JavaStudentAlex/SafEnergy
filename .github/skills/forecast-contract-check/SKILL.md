---
name: forecast-contract-check
description: Review SafEnergy changes for forecast horizon, timestamp, leakage, satellite/weather, geospatial, baseline, signal, backtest, output, and provider-contract risks. Use before completing domain changes or reviewing diffs.
---

# Forecast Contract Check Skill

Use this skill when a change touches renewable generation targets,
satellite/weather ingestion, geospatial features, forecast models, trading
signals, backtests, generated outputs, or provider integrations.

## Checkpoints

Ask whether the change affects any of these contracts:

- Forecast horizon, issue time, valid time, delivery interval, or timezone.
- Data availability time and train/test leakage risk.
- Target definition: absolute generation, generation delta, ramp, anomaly, or
  trading-facing surprise.
- Baseline comparison: persistence, clear-sky, climatology, or lag/weather
  baseline.
- Satellite provider, STAC query, raster resolution, CRS, footprint, and cloud
  or irradiance aggregation.
- Weather provider, request window, forecast issue time, and feature alignment.
- Solar PV assumptions: site metadata, clear-sky model, irradiance conversion,
  temperature correction, and capacity normalization.
- Wind assumptions: hub height, power curve, wind speed/direction alignment,
  ramp rate, and capacity normalization.
- Model validation split, metrics, random seed, uncertainty, and calibration.
- Trading signal threshold, market price source, fees/slippage assumptions, and
  backtest methodology.
- Generated forecast, feature, model, plot, report, cache, and database paths.
- External credentials, provider limits, network availability, and ignored raw
  artifacts.

## Verification Pattern

1. Find the closest existing tests or deterministic script checks for the
   affected contract.
2. Add or update the narrowest deterministic regression test if needed.
3. Run targeted tests when a `tests/` tree exists.
4. Run Ruff checks for touched Python paths.
5. State any unverified external provider, credential, market-data, network, or
   optional dependency assumptions explicitly.

## Guardrails

- Do not use future data in features, baselines, model training, or backtests.
- Do not hide missing provider data, CRS mismatches, empty rasters, stale
  forecasts, or missing prices behind broad exception handling.
- Do not rely on live external services for the only proof of correctness.
- Do not present backtest signals as live trading advice or execution.
