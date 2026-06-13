from datetime import datetime, timezone

import pandas as pd
from fastapi import APIRouter, HTTPException

from safenergy.api.schemas import (
    BacktestRequest,
    BacktestResponse,
    ExplanationRequest,
    ForecastPrediction,
    ForecastRequest,
    ForecastResponse,
    OrchestratorAPIResponse,
    OrchestratorRequest,
    SignalRequest,
)
from safenergy.forecast.service import forecast_serving
from safenergy.orchestrator.pipeline import run_end_to_end_pipeline
from safenergy.signals.backtest import evaluate_signals
from safenergy.signals.explanation import ExplanationResponse, generate_explanation
from safenergy.signals.objects import TradingSignal
from safenergy.signals.pipeline import generate_trading_signals

router = APIRouter()

@router.get("/health", tags=["System"])
def health_check():
    """Basic health check endpoint."""
    return {"status": "ok"}


@router.post("/trading/signals", response_model=list[TradingSignal], tags=["Trading"])
def compute_trading_signals(request: SignalRequest):
    """
    Generate a list of TradingSignal objects from forecast deltas, baselines, and prices.
    """
    if not request.data:
        raise HTTPException(status_code=400, detail="No data provided")

    timestamps = [row.timestamp for row in request.data]
    deltas = [row.delta for row in request.data]
    baselines = [row.baseline for row in request.data]
    prices = [row.price for row in request.data]

    # create timezone-aware index
    index = pd.DatetimeIndex(timestamps)
    s_deltas = pd.Series(deltas, index=index)
    s_baselines = pd.Series(baselines, index=index)
    s_prices = pd.Series(prices, index=index)

    try:
        signals = generate_trading_signals(
            asset_id=request.asset_id,
            deltas=s_deltas,
            baselines=s_baselines,
            prices=s_prices,
            strong_threshold=request.strong_threshold,
            weak_threshold=request.weak_threshold,
            curtailment_price_threshold=request.curtailment_price_threshold,
            extreme_price_threshold=request.extreme_price_threshold,
        )
        return signals
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trading/backtest", response_model=BacktestResponse, tags=["Trading"])
def compute_backtest(request: BacktestRequest):
    """
    Evaluate trading signals against subsequent price changes.
    """
    if not request.data:
        raise HTTPException(status_code=400, detail="No data provided")

    timestamps = [row.timestamp for row in request.data]
    signals = [row.signal.value for row in request.data]
    price_changes = [row.price_change for row in request.data]

    index = pd.DatetimeIndex(timestamps)
    s_signals = pd.Series(signals, index=index)
    s_price_changes = pd.Series(price_changes, index=index)

    try:
        results = evaluate_signals(
            s_signals,
            s_price_changes,
            assumptions=request.assumptions,
            issue_time=request.issue_time
        )
        return BacktestResponse(**results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/predict", response_model=ForecastResponse, tags=["Forecast"])
def predict_forecast(request: ForecastRequest):
    """
    Predict target values using the forecast serving service.
    """
    if not request.features:
        raise HTTPException(status_code=400, detail="No features provided")

    try:
        # Reconstruct DataFrame from features
        timestamps = [row.timestamp for row in request.features]
        feature_dicts = [row.features for row in request.features]
        df_features = pd.DataFrame(feature_dicts, index=pd.DatetimeIndex(timestamps))

        issue_time = datetime.now(timezone.utc)

        # Use forecast service
        preds_df = forecast_serving(
            features=df_features,
            issue_time=issue_time,
            model_path=None,  # Fallback to baseline in demo
            return_uncertainty=request.return_uncertainty
        )

        predictions = []
        for timestamp, row in preds_df.iterrows():
            prediction = ForecastPrediction(
                timestamp=timestamp,
                point=row["point"]
            )
            if request.return_uncertainty and "lower" in row and "upper" in row:
                prediction.lower = row["lower"]
                prediction.upper = row["upper"]

            predictions.append(prediction)

        return ForecastResponse(
            asset_id=request.asset_id,
            predictions=predictions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trading/explain", response_model=ExplanationResponse, tags=["Trading"])
def explain_forecast(request: ExplanationRequest):
    """
    Generate an explainable summary and attribution for a given forecast.
    """
    try:
        return generate_explanation(
            forecast_delta=request.forecast_delta,
            baseline=request.baseline,
            lower_bound=request.lower_bound,
            upper_bound=request.upper_bound,
            features=request.features,
            market_price=request.market_price,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orchestrator/run", response_model=OrchestratorAPIResponse, tags=["Orchestrator"])
def run_orchestrator(request: OrchestratorRequest):
    """
    Run the full end-to-end forecasting and trading signal pipeline.
    """
    try:
        response = run_end_to_end_pipeline(
            asset_id=request.asset_id,
            latitude=request.latitude,
            longitude=request.longitude,
            start_date=request.start_date,
            end_date=request.end_date,
            simulate_failure=request.simulate_failure,
            strong_threshold=request.strong_threshold,
            weak_threshold=request.weak_threshold,
            curtailment_price_threshold=request.curtailment_price_threshold,
            extreme_price_threshold=request.extreme_price_threshold,
        )
        # Simple heuristic for demo purposes:
        # If simulated_failure it's unavailable. If we returned empty predictions it might be unavailable.
        # Ideally, we'd pull this directly from the orchestrator response metadata.
        state = "unavailable" if request.simulate_failure else "live"
        if not response.signals and not response.explanations:
            state = "unavailable"

        return OrchestratorAPIResponse(
            asset_id=response.asset_id,
            issue_time=response.issue_time,
            signals=response.signals,
            explanations=response.explanations,
            forecast_data_state=state
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
