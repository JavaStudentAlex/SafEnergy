# M003-4jb56n: No Training Forecast Method Stack

**Vision:** Replace generic or mock-like forecast fallbacks with an honest deterministic no-training forecast stack that selects the best available method from recent generation, weather, irradiance, asset metadata, and regional capacity signals, then exposes confidence, uncertainty, fallback reasons, and conservative trading-signal behavior without claiming trained ML performance.

## Success Criteria

- Forecast responses can be produced without trained model artifacts using named deterministic methods rather than fixed constants or silent mock predictions.
- Solar forecasts support smart persistence, irradiance or weather normalized persistence, and a pvlib physical baseline when required metadata is available.
- Wind forecasts support a simple documented power-curve approximation and regional capacity fallback when detailed asset data is missing.
- Every forecast response identifies the selected method, inputs used, missing inputs, fallback reason, confidence score, uncertainty band, issue time, valid time, horizon, and provenance references.
- Trading signal generation consumes forecast deltas from the no-training stack and becomes conservative or no-action when confidence is low.
- Tests cover method selection, missing-input fallback behavior, uncertainty/confidence calculation, API response shape, and low-confidence trading behavior.
- Documentation clearly states that this milestone implements explainable no-training baselines, not a trained AI forecasting model.

## Slices

- [x] **S01: Forecast Method Contract** `risk:high` `depends:[]`
  > After this: A reader can open the milestone context and forecast contract notes to see exactly which methods exist, what inputs they need, how selection works, and what the system must not claim.

- [x] **S02: Solar and Persistence Methods** `risk:high` `depends:[S01]`
  > After this: Fixture inputs can produce smart persistence, weather or irradiance normalized persistence, pvlib physical solar, or regional fallback outputs with named method metadata.

- [x] **S03: Wind and Regional Fallback Methods** `risk:medium` `depends:[S01]`
  > After this: Fixture wind inputs can produce a documented wind generation-change estimate or an honest regional fallback when detailed wind asset metadata is missing.

- [x] **S04: Method Selector Confidence and Uncertainty** `risk:high` `depends:[S02,S03]`
  > After this: Changing fixture availability from rich inputs to missing inputs changes selected method, confidence, uncertainty, and fallback reason predictably.

- [x] **S05: API and Signal Integration** `risk:medium` `depends:[S04]`
  > After this: A forecast request without a trained model artifact returns a named no-training method, confidence and uncertainty metadata, and a trading signal that is conservative when confidence is low.

- [x] **S06: Tests and Clear Documentation** `risk:medium` `depends:[S05]`
  > After this: A new contributor can read the docs, run targeted tests, and understand why the system uses deterministic baselines instead of new trainable models.

## Boundary Map

## Boundary Map

- **In scope**: deterministic forecast methods, method selection, confidence and uncertainty, fallback diagnostics, forecast API response fields, conservative signal behavior, tests, and clear documentation.
- **Out of scope**: new live data providers, dashboard redesign, broad backtest UI, live trading, trained CatBoost or XGBoost or neural forecasting models, model-tuning claims, and paid external service calls.
- **Related to M002**: this milestone consumes the forecast serving boundary, provenance conventions, market and generation adapter shapes, and existing signal pipeline interfaces once they are available; it does not duplicate M002 live-data, dashboard, or backtest slices.
- **Provides downstream**: an honest forecast-method layer that orchestration, dashboard, and backtest views can display without relying on mock constants or unsupported trained-model claims.
