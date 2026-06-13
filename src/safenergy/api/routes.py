import pandas as pd
from fastapi import APIRouter, HTTPException

from safenergy.api.schemas import (
    BacktestRequest,
    BacktestResponse,
    ForecastPrediction,
    ForecastRequest,
    ForecastResponse,
    SignalRequest,
)
from safenergy.signals.backtest import evaluate_signals
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
        results = evaluate_signals(s_signals, s_price_changes)
        return BacktestResponse(**results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast/predict", response_model=ForecastResponse, tags=["Forecast"])
def predict_forecast(request: ForecastRequest):
    """
    Predict target values using a mocked response to fulfill the forecast API contract.
    """
    if not request.features:
        raise HTTPException(status_code=400, detail="No features provided")

    predictions = []
    for row in request.features:
        # Mock prediction logic
        point_prediction = 10.0
        prediction = ForecastPrediction(
            timestamp=row.timestamp,
            point=point_prediction
        )
        if request.return_uncertainty:
            prediction.lower = point_prediction - 2.0
            prediction.upper = point_prediction + 2.0

        predictions.append(prediction)

    return ForecastResponse(
        asset_id=request.asset_id,
        predictions=predictions
    )
