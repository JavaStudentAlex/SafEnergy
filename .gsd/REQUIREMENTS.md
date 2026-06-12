# Requirements

This file is the explicit capability and coverage contract for the project.

## Active

### R001 — Given a target region and forecast horizon, produce solar and wind renewable generation-change forecasts against an expectation baseline.
- Class: core-capability
- Status: active
- Description: Given a target region and forecast horizon, produce solar and wind renewable generation-change forecasts against an expectation baseline.
- Why it matters: This is the central product capability described by the task brief and the Invertix open-track framing.
- Source: renewable_forecasting_trading_tasks.md
- Primary owning slice: S06
- Supporting slices: S01, S03, S04, S05, S07
- Validation: Temporal evaluation shows model forecasts compared with persistence and other simple baselines.

### R002 — Ingest or fixture-load satellite, weather, realised generation, and price data with provenance, cache keys, and data quality diagnostics.
- Class: integration
- Status: active
- Description: Ingest or fixture-load satellite, weather, realised generation, and price data with provenance, cache keys, and data quality diagnostics.
- Why it matters: The service depends on external and cached data, and failures must be explicit rather than silently ignored.
- Source: renewable_forecasting_trading_tasks.md
- Primary owning slice: S03
- Supporting slices: S10, S14
- Validation: Adapters or deterministic fixtures produce normalized inputs and visible quality/staleness checks.

### R003 — Feature engineering and evaluation must be leakage-safe, timezone-aware, and deterministic.
- Class: quality-attribute
- Status: active
- Description: Feature engineering and evaluation must be leakage-safe, timezone-aware, and deterministic.
- Why it matters: Forecasting and trading claims are only credible if features are available as of issue time and timestamps are consistent.
- Source: renewable_forecasting_trading_tasks.md
- Primary owning slice: S04
- Supporting slices: S05, S07, S14
- Validation: Tests or documented checks cover UTC timestamp normalization, temporal splits, and deterministic feature generation.

### R004 — Translate forecast deltas into transparent operational or trading-impact signals with risk filters.
- Class: core-capability
- Status: active
- Description: Translate forecast deltas into transparent operational or trading-impact signals with risk filters.
- Why it matters: The project goal is forecast-to-trade decision support, not only generation prediction.
- Source: renewable_forecasting_trading_tasks.md
- Primary owning slice: S09
- Supporting slices: S08, S12, S13
- Validation: Signal outputs include thresholds, confidence, risk filters, and backtest or impact metrics.

### R005 — Surface missing data, stale satellite inputs, unavailable providers, high uncertainty, and low model confidence in API and demo outputs.
- Class: failure-visibility
- Status: active
- Description: Surface missing data, stale satellite inputs, unavailable providers, high uncertainty, and low model confidence in API and demo outputs.
- Why it matters: Operational users need to know when a signal should not be trusted.
- Source: renewable_forecasting_trading_tasks.md
- Primary owning slice: S11
- Supporting slices: S03, S09, S12, S13
- Validation: API or dashboard smoke checks demonstrate structured errors and diagnostic fields without logging secrets.

### R006 — Generate human-readable forecast and trading explanations with key drivers such as cloud change, weather change, historical trend, confidence, and uncertainty.
- Class: differentiator
- Status: active
- Description: Generate human-readable forecast and trading explanations with key drivers such as cloud change, weather change, historical trend, confidence, and uncertainty.
- Why it matters: Explainability is required for a practical demo and helps distinguish useful signals from black-box forecasts.
- Source: renewable_forecasting_trading_tasks.md
- Primary owning slice: S12
- Supporting slices: S06, S09, S13
- Validation: Example outputs include forecast explanations, trading rationale, and feature attribution or driver summaries.

### R007 — Provide a reproducible final demo with API or dashboard flow, tests, smoke checks, and documented commands.
- Class: launchability
- Status: active
- Description: Provide a reproducible final demo with API or dashboard flow, tests, smoke checks, and documented commands.
- Why it matters: The task list culminates in a working challenge demo that future agents can run and verify.
- Source: renewable_forecasting_trading_tasks.md
- Primary owning slice: S14
- Supporting slices: S11, S13
- Validation: Final demo instructions run locally with fixture or cached data, and verification commands are documented.

### R008 — Do not implement live trade execution or submit orders by default; keep trading outputs as research, backtest, or decision-support signals.
- Class: anti-feature
- Status: active
- Description: Do not implement live trade execution or submit orders by default; keep trading outputs as research, backtest, or decision-support signals.
- Why it matters: The repository contract requires avoiding outward-facing trading actions unless explicitly requested and confirmed.
- Source: AGENTS.md and renewable_forecasting_trading_tasks.md
- Primary owning slice: S09
- Supporting slices: S11, S13, S14
- Validation: No live broker/order-submission code is added unless a future explicit requirement changes scope.

## Validated

## Deferred

### R009 — Trading outputs must remain research, backtest, or decision-support signals unless a future user explicitly requests and confirms live trade execution.
- Class: constraint
- Status: deferred
- Description: Trading outputs must remain research, backtest, or decision-support signals unless a future user explicitly requests and confirms live trade execution.
- Why it matters: This keeps the prototype aligned with repository guardrails and prevents accidental outward-facing trading actions.
- Source: AGENTS.md and renewable_forecasting_trading_tasks.md
- Primary owning slice: S09
- Supporting slices: S11, S13, S14
- Validation: No live broker/order-submission code is added by default; API and dashboard copy label signals as decision support or backtest outputs.
- Notes: Superseded by active anti-feature R008, which captures the same live-trading scope guard in the clearer requirement class.

## Out of Scope

## Traceability

| ID | Class | Status | Primary owner | Supporting | Proof |
|---|---|---|---|---|---|
| R001 | core-capability | active | S06 | S01, S03, S04, S05, S07 | Temporal evaluation shows model forecasts compared with persistence and other simple baselines. |
| R002 | integration | active | S03 | S10, S14 | Adapters or deterministic fixtures produce normalized inputs and visible quality/staleness checks. |
| R003 | quality-attribute | active | S04 | S05, S07, S14 | Tests or documented checks cover UTC timestamp normalization, temporal splits, and deterministic feature generation. |
| R004 | core-capability | active | S09 | S08, S12, S13 | Signal outputs include thresholds, confidence, risk filters, and backtest or impact metrics. |
| R005 | failure-visibility | active | S11 | S03, S09, S12, S13 | API or dashboard smoke checks demonstrate structured errors and diagnostic fields without logging secrets. |
| R006 | differentiator | active | S12 | S06, S09, S13 | Example outputs include forecast explanations, trading rationale, and feature attribution or driver summaries. |
| R007 | launchability | active | S14 | S11, S13 | Final demo instructions run locally with fixture or cached data, and verification commands are documented. |
| R008 | anti-feature | active | S09 | S11, S13, S14 | No live broker/order-submission code is added unless a future explicit requirement changes scope. |
| R009 | constraint | deferred | S09 | S11, S13, S14 | No live broker/order-submission code is added by default; API and dashboard copy label signals as decision support or backtest outputs. |

## Coverage Summary

- Active requirements: 8
- Mapped to slices: 0
- Validated: 0
- Unmapped active requirements: 8
