@/home/jovyan/.codex/RTK.md

# AGENTS.md

## Purpose: Repository Contract and LLM Guidance for SafEnergy

This file is the repository-local instruction surface for agent-based work in
this project. It complements the workspace/runtime contract and focuses on the
parts that are specific to SafEnergy: satellite-enhanced renewable generation
forecasting and forecast-to-trade decision support.

## Project Overview

SafEnergy is a Python project for the Invertix open track around renewable
generation forecasting and energy trading agents. The project goal is a useful,
explainable prototype that predicts short-term changes in renewable generation,
especially solar and wind, and translates those changes into trading-relevant
signals.

The system should answer operational questions such as:

- Will solar production be higher or lower than expected in the next hour?
- Is wind generation likely to ramp up or ramp down?
- Is the predicted generation change large enough to matter for intraday,
  balancing, congestion, curtailment, or day-ahead decisions?
- Which weather, satellite, or market features explain the signal?

The project sits between two domains:

- Forecasting: satellite data, weather data, historical generation data, and
  machine learning estimate near-term renewable generation changes.
- Trading: the forecast delta is converted into a transparent signal that can be
  backtested against prices or balancing outcomes.

The demo should remain practical and explainable. Favor a narrow, working
forecast-to-trade slice over a large unfinished system.

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Package manager | uv |
| API / services | FastAPI, Uvicorn, Pydantic, Pydantic Settings |
| HTTP / retries | httpx, aiohttp, tenacity, requests-cache, retry-requests |
| Data frames / analytics | Pandas, NumPy, SciPy, PyArrow, DuckDB, Polars |
| Satellite / STAC | sentinelhub, pystac-client, stackstac, odc-stac |
| Geospatial / rasters | rasterio, rioxarray, xarray, GeoPandas, Shapely, PyProj |
| Weather / solar | pvlib, openmeteo-requests |
| ML | scikit-learn, LightGBM, joblib |
| Scheduling / state | APScheduler, Redis |
| Database | SQLAlchemy, Alembic, SQLModel |
| Testing | pytest |
| Linting | Ruff high-signal checks |
| CI | GitHub Actions for lint, optional tests, PR structure, and task automation |

## CLI Guidance

- Use `uv sync --group dev` to install runtime and development dependencies.
- Use `uv run python <script>.py` for scripts when scripts exist.
- Use `uv run ruff check .` for the configured lint gate.
- Use `uv run pytest tests -q` when a `tests/` directory exists.
- Use `uv lock --check` after dependency changes.
- Do not use `pip`, `poetry`, or `conda` for normal project dependency
  management unless the repository explicitly changes package managers.
- Do not commit secrets, downloaded raw satellite scenes, local caches,
  generated model binaries, database files, large Parquet extracts, or
  credentials.

## Project Structure and Boundaries

The repository is currently a dependency scaffold. When code is introduced,
prefer a clear package layout such as:

- `src/safenergy/ingest/` for STAC, Sentinel/Copernicus, Open-Meteo, NASA POWER,
  and market data ingestion adapters.
- `src/safenergy/features/` for cloud, irradiance, wind, temperature, temporal,
  geospatial, and baseline-expectation features.
- `src/safenergy/forecast/` for solar/wind nowcast and forecast models.
- `src/safenergy/signals/` for forecast-delta-to-trading-signal logic.
- `src/safenergy/backtest/` for leakage-safe historical evaluation and trading
  metrics.
- `src/safenergy/api/` for FastAPI endpoints, if the demo needs an API.
- `src/safenergy/storage/` for SQLModel/SQLAlchemy schemas and cache metadata.
- `tests/` for deterministic unit, integration, and fixture-backed tests.
- `scripts/` for narrow data pulls, training runs, demos, and smoke checks.
- `data/` for ignored local raw and cached inputs.
- `outputs/` for ignored generated forecasts, reports, plots, and model
  artifacts.

Subsystem boundaries:

- Ingestion code should normalize external data into explicit schemas and keep
  API credentials outside source code.
- Feature code should be deterministic and independent of network calls.
- Forecast code should not know about live trading or order execution.
- Signal code should consume forecast deltas and market context, not raw
  satellite files directly.
- Backtests must be leakage-safe and reproducible.
- Demo/API code should orchestrate existing package functions rather than
  embedding domain logic in route handlers.

## Renewable Forecasting and Trading Domain Contracts

- Treat the main prediction target as a change from expectation, not just an
  absolute generation curve.
- Keep forecast horizons explicit: nowcast, intraday, day-ahead, or another
  named horizon.
- Keep timestamps timezone-aware. Prefer UTC internally and document any local
  market or site timezone conversions.
- Keep geospatial coordinate reference systems explicit. Do not mix lat/lon,
  projected CRS, raster grid coordinates, or site polygons silently.
- Preserve provenance for satellite, weather, generation, and market inputs:
  provider, query time, valid time, spatial footprint, resolution, and cache key.
- Use baselines before complex models. At minimum, compare against persistence,
  clear-sky or climatology-style solar baselines, and simple lag/weather
  baselines where applicable.
- Avoid train/test leakage. Splits for forecasting and trading evaluation must
  be temporal, with features available only as of the forecast issue time.
- Keep trading claims as research/backtest signals unless the user explicitly
  asks for live execution. Do not implement live order submission by default.
- Explain every signal with top drivers such as cloud cover, irradiance anomaly,
  wind speed change, ramp rate, forecast uncertainty, market price spread, or
  balancing price exposure.
- Report uncertainty and failure modes. Missing satellite tiles, stale weather,
  bad site metadata, incomplete generation data, and market holidays should be
  visible, not silently ignored.
- Do not tune models or thresholds only to improve a single chart. Tie changes
  to leakage-safe validation, backtest evidence, or challenge-demo clarity.

## Verification and Quality Gates

- Prefer the lightest verification that proves the change.
- For Python code changes, run the quality gates from
  `.github/instructions/python_quality_gates.instructions.md`.
- For behavior changes, run targeted tests when a `tests/` tree exists and use a
  deterministic smoke check when possible.
- For ingestion changes, state whether external APIs, credentials, cache data,
  and network access were available.
- For forecasting or trading changes, state the temporal split, baseline, metric,
  and whether any price/generation data was synthetic.
- Do not claim verification that did not run in the current session.
- If full verification is blocked by missing credentials, paid APIs, large data,
  optional native dependencies, or external service limits, report the block
  explicitly and run the closest deterministic checks available.

## GSD and Jules Task Selection

- Treat `.gsd/QUEUE.md`, `.gsd/STATE.md`, and
  `.gsd/milestones/<milestone>/<milestone>-ROADMAP.md` as the task-running
  source of truth.
- When a Jules or agent task runner starts without an explicit task override,
  select exactly one work item: the active slice in `.gsd/STATE.md`; if that is
  missing or already complete, use the first unchecked `[ ]` slice in the active
  milestone roadmap.
- Do not run the whole milestone, all requirements, or
  `.gsd/normalized_task_outline.txt` as a single task. The normalized outline is
  an ignored import artifact, not the execution queue.
- After completing a slice, update the relevant GSD state or roadmap checkbox
  before selecting the next unfinished slice.

## Instruction Map

- Behavioral overlay:
  `.github/instructions/code_writing_behavior.instructions.md`
- Python renewable forecasting conventions:
  `.github/instructions/python_renewable_forecasting.instructions.md`
- Test conventions: `.github/instructions/tests.instructions.md`
- Python quality gates:
  `.github/instructions/python_quality_gates.instructions.md`
- Delegation policy: `.github/instructions/delegation_policy.instructions.md`
- Agent maintenance workflow:
  `.github/instructions/agent_maintenance_workflow.instructions.md`
- Read-only QA overlay: `.github/instructions/qa_readonly.instructions.md`

## Custom Agents

- Renewable forecasting engineering:
  `.github/agents/renewable-forecasting-engineer.agent.md`
- Satellite, weather, and geospatial data:
  `.github/agents/satellite-weather-data-engineer.agent.md`
- Trading signal and backtest evaluation:
  `.github/agents/trading-backtest-engineer.agent.md`
- Testing and verification: `.github/agents/test-engineer.agent.md`
- Code review: `.github/agents/code-reviewer.agent.md`
- Documentation maintenance: `.github/agents/docs-maintainer.agent.md`

## Skills

- Project-scoped GitHub skills live under `.github/skills/`.
- Use `.github/skills/forecast-contract-check/SKILL.md` before completing
  domain changes that affect forecasting targets, satellite/weather features,
  trading signals, or backtest methodology.

## Mandatory Guardrails

1. Treat `AGENTS.md` as the base repository contract for this project.
2. Load the relevant `.github/instructions/*.instructions.md` files for the
   task scope before making changes.
3. Keep forecasting target, timestamp, geospatial, data provenance, baseline,
   leakage, signal, and backtest contracts covered by tests or explicit
   verification notes.
4. Never commit, push, publish, trigger paid external services, submit trades, or
   take external service actions from an agent session unless the user
   explicitly asks and confirms.
5. Double-check that the final report matches the actual edits, verification,
   and remaining risks.
