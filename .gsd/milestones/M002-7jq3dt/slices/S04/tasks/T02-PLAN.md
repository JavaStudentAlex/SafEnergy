---
estimated_steps: 1
estimated_files: 4
skills_used: []
---

# T02: Connect endpoint to model and baselines

Replace fixed constants in the forecast prediction route with deterministic fixture-backed service execution that runs feature engineering, baseline comparison, optional LightGBM inference, and uncertainty assembly.

## Inputs

- `src/safenergy/forecast/models.py`
- `src/safenergy/forecast/baselines.py`
- `src/safenergy/forecast/evaluate.py`
- `src/safenergy/forecast/service.py`

## Expected Output

- `src/safenergy/forecast/service.py`
- `tests/test_forecast_service.py`
- `tests/test_api.py`

## Verification

uv run pytest tests/test_forecast_service.py tests/test_api.py tests/test_baselines.py tests/test_forecast_models.py -q

## Observability Impact

Reports whether forecast came from trained model, baseline fallback, or unavailable model diagnostic.
