# M003-4jb56n: No Training Forecast Method Stack

**Gathered:** 2026-06-13
**Status:** Ready for planning

## Project Description

SafEnergy needs renewable generation-change forecasts that are credible before there is enough historical target data to train and validate a reliable ML model. The current project has live-data, provenance, serving, API, and signal scaffolding, but the forecast method layer still needs an honest deterministic strategy for cases where trained model artifacts are unavailable or not trustworthy.

This milestone turns the long `Milestone_2_No_Training_Forecast_Strategy.md` proposal into a clean execution plan. It keeps only the unique work: no-training forecast methods, method selection, confidence and uncertainty, explicit fallback reasons, API metadata, conservative signal behavior, and focused tests.

## Why This Milestone

The project should not add more trainable models such as CatBoost, XGBoost, PVNet, NeuralForecast, or transformer forecasters until it has enough clean historical target data, leakage-safe validation, and a stable serving path. Adding those models now would make the demo look more advanced without making it more trustworthy.

Instead, this milestone makes the forecast output more realistic and explainable by implementing deterministic baselines that can operate with operationally available data:

- recent generation
- weather forecasts or observations
- irradiance or shortwave radiation signals
- asset location and installed capacity
- generic wind metadata when detailed turbine metadata is missing
- regional fallback assumptions when site-level data is incomplete

## User-Visible Outcome

### When this milestone is complete, the user can:

- Request a forecast without providing a trained model artifact and receive a named no-training forecast method instead of a silent mock value.
- See which method was selected, which inputs were used, which inputs were missing, and why any fallback was chosen.
- See confidence and uncertainty change when data quality or availability changes.
- Receive a trading or balancing signal that becomes conservative when forecast confidence is low.
- Read documentation that clearly states the system uses explainable no-training baselines and does not claim trained AI forecast performance.

### Entry point / environment

- Entry point: existing forecast serving and API boundary from M002.
- Environment: local Python development with deterministic fixtures and pytest.
- Live dependencies involved: none required for proof; live provider data remains optional and credential-gated through existing M002 boundaries.

## Completion Class

- Contract complete means: the forecast method contract defines method names, required inputs, outputs, fallback reasons, confidence, uncertainty, issue time, valid time, horizon, baseline comparison, and provenance references.
- Integration complete means: the existing forecast serving path can call the no-training selector and pass forecast deltas plus confidence metadata to the signal pipeline.
- Operational complete means: missing data, stale data, regional fallback, generic metadata, and low confidence are visible in response diagnostics.
- UAT complete means: a deterministic forecast request without a model artifact returns a named no-training method, uncertainty band, confidence score, fallback reason when applicable, and conservative signal metadata.

## What Is Unique Here

This milestone adds the parts not already covered by M002:

1. Smart persistence and weather or irradiance normalized persistence.
2. pvlib physical solar baseline when location, capacity, time, and irradiance or weather metadata are available.
3. Simple wind power-curve approximation with honest generic-metadata labels.
4. Regional capacity or capacity-factor fallback for incomplete asset metadata.
5. Method selector that ranks available no-training methods from input availability.
6. Confidence scoring and uncertainty bands tied to data quality, metadata specificity, and horizon.
7. Explicit fallback reasons and missing-input diagnostics.
8. API response metadata for selected method, inputs used, missing inputs, confidence, uncertainty, and provenance.
9. Conservative trading signal behavior when confidence is low.
10. Focused tests for the above behaviors.

## What This Milestone Must Not Duplicate

The following work belongs to existing or prior milestones and should not be rebuilt here:

- Live satellite discovery and feature seeding.
- Live market and generation adapters.
- Provenance and geospatial metadata backbone.
- Dashboard redesign or broad dashboard backend work.
- Full trading backtest UI hardening.
- General API hardening unrelated to the no-training response contract.
- Live trading or order submission.
- New trained ML models or model-tuning claims.
- Paid external service calls.

## Forecast Method Stack

The selector should prefer the best available honest method:

1. **Recent generation plus irradiance or weather available**: use smart persistence or normalized persistence.
2. **Solar asset metadata plus weather or irradiance available**: use pvlib physical solar baseline.
3. **Wind asset plus wind forecast available**: use simple wind power-curve approximation.
4. **Only installed capacity and regional weather available**: use regional capacity fallback with lower confidence.
5. **Inputs insufficient**: return a labeled diagnostic fallback or no reliable forecast; never return an unlabeled fixed constant.

## Forecast Contract Notes

Every forecast result should preserve:

- target type: generation change against an expectation baseline
- issue time
- valid time
- horizon
- timezone-aware timestamps
- selected method
- baseline or expectation used
- forecast delta
- uncertainty band
- confidence score
- inputs used
- missing inputs
- fallback reason
- assumptions
- provenance references where available

## Trading Signal Boundary

Trading output remains research/backtest signal metadata only. The signal pipeline may consume forecast deltas and confidence, but it must not submit live orders. Low confidence should weaken or suppress action and explain why.

## Future Criteria for Trained Models

A later milestone may add additional trained models only after the project has:

- enough clean historical target data
- temporal splits based on forecast issue time
- leakage-safe feature availability checks
- baseline comparison against persistence and no-training methods
- model artifact versioning and serving diagnostics
- evidence that the trained model improves reliability rather than just complexity

## Reader Test

A new contributor should be able to read this document and answer:

- Why are we not adding new trainable models now?
- Which forecast methods are in scope?
- How does the fallback hierarchy work?
- What must be visible in API responses?
- What work should not be duplicated from M002?
- How will tests prove the behavior?
