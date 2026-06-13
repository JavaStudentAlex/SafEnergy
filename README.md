# SafEnergy

SafEnergy is a Python-based project for renewable generation forecasting and energy trading agents. It predicts short-term changes in renewable generation and translates those forecasts into trading-relevant signals.

The target region for the prototype is ERCOT (Texas, USA).

## Prerequisites

- **Python 3.12+**
- **uv** (dependency manager)

Install dependencies using:

```bash
uv sync --group dev
```

## Running the SafEnergy Backend

The backend is built with FastAPI. It handles forecasting, trading signal generation, backtesting, and explanation paths.

To start the API locally:

```bash
uv run uvicorn safenergy.api.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. You can access the automatic documentation and test the endpoints directly at `http://localhost:8000/docs`.

## Running the Dashboard

A Streamlit dashboard is provided to interact with the API endpoints and visualize the forecasts, explanations, trading signals, and backtest results.

You can launch the dashboard using the provided script:

```bash
uv run python run_dashboard.py
```

Alternatively, you can run Streamlit directly:

```bash
uv run streamlit run src/safenergy/api/dashboard.py
```

The dashboard will open in your default browser, typically at `http://localhost:8501`.

## Documentation

For more detailed information, please refer to the documents in the `docs/` directory:

- [Demo Guide](docs/demo.md): Instructions on how to use the dashboard and smoke tests.
- [Configuration Guide](docs/CONFIGURATION.md): How to configure API keys, credentials, and data modes for external providers (e.g., Earth Engine, Open-Meteo).
- [Forecast Contract](docs/forecast_contract.md): Details on forecasting targets, horizons, and data boundaries.

## Testing and Verification

To ensure the basic data paths and functionality are intact without running the full services, you can execute the smoke check script:

```bash
uv run python scripts/smoke_check.py
```

Run unit tests via:

```bash
uv run pytest tests -q
```

Run linting checks via:

```bash
uv run ruff check .
```

## Optional API Credentials

By default, the project can run using deterministic fixtures when live services are unavailable.

For live capabilities, you can copy `.env.example` to `.env` and set optional credentials (see `docs/CONFIGURATION.md` for full details). Keep provider access split into mandatory, recommended, and optional groups so deterministic tests, fixtures, and local development still work when live services are unavailable.

- Recommended Google Earth Engine authentication:
  ```env
  EE_PROJECT=your-google-cloud-project
  ```
