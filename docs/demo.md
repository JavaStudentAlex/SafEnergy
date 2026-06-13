# SafEnergy Prototype Demo

This guide explains how to run the SafEnergy forecasting and trading prototype demo end-to-end.
The prototype demonstrates the prediction of short-term changes in renewable generation and the translation of those forecasts into trading-relevant signals.

## Prerequisites

Make sure you have `uv` installed, as it is the dependency manager for this project.
Install dependencies using:

```bash
uv sync --group dev
```

## Running the API Backend

The backend is built with FastAPI and exposes endpoints for forecasting, trading signals, and backtest evaluation.

To start the backend server, run:

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

## Using the Demo

The dashboard contains three main tabs:

1.  **Forecasts**: Simulates a forecast input and uses the API to generate a human-readable explanation with confidence, uncertainty, and feature attribution.
2.  **Trading Signals**: Allows you to input mock time series data for forecast deltas, baselines, and market prices to generate categorical trading signals adjusted by market context.
3.  **Backtest**: Evaluates a mock trading strategy by passing historical signals and price changes to calculate total return and hit rate.

## Smoke Testing

To ensure the basic data paths and functionality are intact without running the full services, you can execute the smoke check script:

```bash
uv run python scripts/smoke_check.py
```

This will run a lightweight, deterministic check on the core pipeline using mock data.
