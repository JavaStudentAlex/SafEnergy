1. **Design Forecast Serving Service Boundary (`src/safenergy/forecast/service.py`)**
   - Create a `forecast_serving` function or class that accepts regions, horizons, issue time, and normalized features.
   - Implement logic to load or fallback to baselines if no trained LightGBM model is available or valid.
   - Generate points, uncertainties, baselines, and provenance metadata.

2. **Connect API Endpoint to Forecast Serving Service (`src/safenergy/api/routes.py`)**
   - Replace the static/mocked predictions in `predict_forecast` with a call to the new service logic.
   - Map `ForecastRequest` to a proper `pd.DataFrame` indexed by `timestamp` to feed the service.
   - Build `ForecastPrediction` output objects based on the service response.

3. **Add Tests (`tests/test_forecast_service.py`)**
   - Verify that the service operates deterministically.
   - Verify fallback mechanism.

4. **Verify changes**
   - `uv run ruff check .`
   - `uv run pytest tests -q`

5. **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.**
