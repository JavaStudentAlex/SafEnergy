from datetime import datetime, timedelta, timezone

import pandas as pd
from fastapi import APIRouter, HTTPException

from safenergy.api.schemas import (
    BacktestRequest,
    BacktestResponse,
    CommitmentMetrics,
    ExplanationRequest,
    ForecastPrediction,
    ForecastRequest,
    ForecastResponse,
    MarketPricePoint,
    MarketPriceResponse,
    OrchestratorAPIResponse,
    OrchestratorRequest,
    PlantHealthResponse,
    PlantResponse,
    RecommendationRequest,
    RecommendationResponse,
    SignalRequest,
    WeatherPoint,
    WeatherResponse,
)
from safenergy.commitment.engine import recommend_action
from safenergy.commitment.ledger import AcceptedAction, ActionLedger
from safenergy.forecast.service import forecast_serving
from safenergy.health.diagnostics import get_plant_health
from safenergy.ingest.market import fetch_delu_prices
from safenergy.ingest.plants import get_all_plants, get_plant_by_id
from safenergy.ingest.weather import fetch_weather_forecast
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
    confidences = [row.confidence for row in request.data]

    # create timezone-aware index
    index = pd.DatetimeIndex(timestamps)
    s_deltas = pd.Series(deltas, index=index)
    s_baselines = pd.Series(baselines, index=index)
    s_prices = pd.Series(prices, index=index)
    s_confidences = pd.Series(confidences, index=index)

    try:
        signals = generate_trading_signals(
            asset_id=request.asset_id,
            deltas=s_deltas,
            baselines=s_baselines,
            prices=s_prices,
            confidence_scores=s_confidences,
            strong_threshold=request.strong_threshold,
            weak_threshold=request.weak_threshold,
            curtailment_price_threshold=request.curtailment_price_threshold,
            extreme_price_threshold=request.extreme_price_threshold,
        )
        return signals
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred during trading signal generation.")


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
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred during backtest evaluation.")



@router.get("/forecast/{plant_id}", response_model=ForecastResponse, tags=["Forecast"])
def get_forecast(plant_id: str, horizon_minutes: int = 60):
    """
    Generate short-term PV generation forecast using physics-informed baselines.
    Supports horizon_minutes (e.g., 15, 30, 45, 60). Returns future points.
    """
    plant = get_plant_by_id(plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail=f"Plant {plant_id} not found")

    lat = plant["latitude"]
    lon = plant["longitude"]
    metadata_dict = plant.get("metadata_dict", {})
    # Provide capacity, lat, lon explicitly in metadata_dict as expected by select_forecast_method
    metadata_dict.setdefault("capacity_mw", plant.get("capacity_mw"))
    metadata_dict.setdefault("latitude", lat)
    metadata_dict.setdefault("longitude", lon)

    # We need recent and future weather data to predict.
    try:
        # Fetching a bit of history to allow persistence-like baselines if needed,
        # and enough future to cover the horizon.
        horizon_hours = max(1, horizon_minutes // 60 + 1)
        df_weather = fetch_weather_forecast(latitude=lat, longitude=lon, past_days=1, forecast_days=horizon_hours)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather: {str(e)}")

    if df_weather.empty:
        raise HTTPException(status_code=500, detail="Weather data is empty")

    if df_weather.index.tz is None:
        df_weather.index = df_weather.index.tz_localize("UTC")

    # Rename weather columns to match what the baseline logic expects
    if "shortwave_radiation" in df_weather.columns:
        df_weather["irradiance"] = df_weather["shortwave_radiation"]
    if "temperature_2m" in df_weather.columns:
        df_weather["temperature"] = df_weather["temperature_2m"]
    if "wind_speed_10m" in df_weather.columns:
        df_weather["wind_speed"] = df_weather["wind_speed_10m"]

    now = datetime.now(timezone.utc)
    current_hour = now.replace(minute=0, second=0, microsecond=0)

    asset_type = "solar"
    # Basic asset type inference from plant type or capacity, if present
    # Assume solar for these demo PV plants.

    try:
        preds_df = forecast_serving(
            features=df_weather,
            issue_time=now,
            model_path=None,
            horizon_hours=horizon_hours,
            return_uncertainty=True,
            asset_type=asset_type,
            metadata_dict=metadata_dict
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast serving failed: {str(e)}")

    # Filter for future points only (up to horizon_minutes)
    horizon_delta = pd.Timedelta(minutes=horizon_minutes)
    future_mask = (preds_df.index > current_hour) & (preds_df.index <= current_hour + horizon_delta)
    # If horizon is small but we only have hourly data, we might not get exact 15m intervals unless we resample.
    # The requirement says 15/30/45/60. Let's return what we have (hourly points) or optionally resample if needed.
    # We will resample to 15min to provide those specific horizons if the user requested them.

    # Resample to 15min for high-res output
    # Only interpolate numeric columns
    numeric_cols = preds_df.select_dtypes(include="number").columns
    resampled_df = preds_df.resample("15min").asfreq()
    resampled_df[numeric_cols] = resampled_df[numeric_cols].interpolate(method="linear")
    preds_df = resampled_df
    future_mask = (preds_df.index > current_hour) & (preds_df.index <= current_hour + horizon_delta)

    df_future = preds_df[future_mask]

    predictions = []
    for ts, row in df_future.iterrows():
        # Ensure 'point' is not NaN, fallback to 0 if it is (for robustness)
        point_val = row["point"] if pd.notna(row.get("point")) else 0.0

        prediction = ForecastPrediction(
            timestamp=ts.to_pydatetime(),
            point=float(point_val)
        )
        if "lower" in row and pd.notna(row["lower"]):
            prediction.lower = float(row["lower"])
        if "upper" in row and pd.notna(row["upper"]):
            prediction.upper = float(row["upper"])

        if "method" in row:
            prediction.method = str(row["method"])
        if "confidence_score" in row and pd.notna(row["confidence_score"]):
            prediction.confidence_score = float(row["confidence_score"])
        if "fallback_reason" in row:
            prediction.fallback_reason = str(row["fallback_reason"])

        # Safe handling of lists in resampled columns
        # Since interpolation turns object columns (like lists) into NaNs or strings, we need safe extraction
        # Let's take the static values directly from the first un-resampled row if they got corrupted.
        first_orig_row = preds_df.dropna(subset=['method']).iloc[0] if not preds_df.dropna(subset=['method']).empty else {}

        prediction.method = str(row.get("method") if pd.notna(row.get("method")) else first_orig_row.get("method", "unknown"))
        prediction.fallback_reason = str(row.get("fallback_reason") if pd.notna(row.get("fallback_reason")) else first_orig_row.get("fallback_reason", ""))

        # Get inputs_used/missing from the original data (since resampled rows won't have the list object properly)
        prediction.inputs_used = first_orig_row.get("inputs_used", [])
        prediction.missing_inputs = first_orig_row.get("missing_inputs", [])

        predictions.append(prediction)

    return ForecastResponse(
        asset_id=plant_id,
        predictions=predictions
    )


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
            return_uncertainty=request.return_uncertainty,
            asset_type=request.asset_type,
            metadata_dict=request.metadata_dict
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

            if "method" in row:
                prediction.method = row["method"]
            if "confidence_score" in row:
                prediction.confidence_score = row["confidence_score"]
            if "fallback_reason" in row:
                prediction.fallback_reason = row["fallback_reason"]
            if "inputs_used" in row:
                prediction.inputs_used = row["inputs_used"]
            if "missing_inputs" in row:
                prediction.missing_inputs = row["missing_inputs"]

            predictions.append(prediction)

        return ForecastResponse(
            asset_id=request.asset_id,
            predictions=predictions
        )
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred during forecast prediction.")


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
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred during forecast explanation.")

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
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred during orchestrator pipeline execution.")

@router.get("/plants", response_model=list[PlantResponse], tags=["Plants"])
def list_plants():
    """
    Returns a list of all stable demo PV plants.
    """
    return get_all_plants()

@router.get("/plants/{plant_id}", response_model=PlantResponse, tags=["Plants"])
def get_plant(plant_id: str):
    """
    Returns metadata for a specific plant by its identifier.
    """
    plant = get_plant_by_id(plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail=f"Plant {plant_id} not found")
    return plant


@router.get("/weather/live", response_model=WeatherResponse, tags=["Weather"])
def get_weather_live(plant_id: str):
    """
    Returns the current hour's weather for a given plant.
    """
    plant = get_plant_by_id(plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail=f"Plant {plant_id} not found")

    lat = plant["latitude"]
    lon = plant["longitude"]

    try:
        # Fetch weather data for today and tomorrow to cover UTC overlap
        df = fetch_weather_forecast(latitude=lat, longitude=lon, past_days=0, forecast_days=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather: {str(e)}")

    if df.empty:
        raise HTTPException(status_code=500, detail="Weather data is empty")

    now = datetime.now(timezone.utc)
    current_hour = now.replace(minute=0, second=0, microsecond=0)

    # Filter for the current hour's row
    # Ensure timezone comparison works properly
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")

    df_current = df[df.index == current_hour]

    if len(df_current) == 0:
        # Fallback to the closest available past row if current hour is somehow missing
        df_past = df[df.index <= current_hour]
        if len(df_past) > 0:
            df_current = df_past.iloc[[-1]]
        else:
            raise HTTPException(status_code=500, detail="Could not find current hour weather data")

    row = df_current.iloc[0]
    point = WeatherPoint(
        timestamp=df_current.index[0].to_pydatetime(),
        temperature_2m=float(row.get("temperature_2m", 0.0)),
        cloud_cover=float(row.get("cloud_cover", 0.0)),
        wind_speed_10m=float(row.get("wind_speed_10m", 0.0)),
        shortwave_radiation=float(row.get("shortwave_radiation", 0.0))
    )

    return WeatherResponse(
        plant_id=plant_id,
        valid_time=now,
        provenance="open-meteo",
        interval_minutes=60,
        points=[point]
    )

@router.get("/weather/forecast", response_model=WeatherResponse, tags=["Weather"])
def get_weather_forecast(plant_id: str, hours: int = 24):
    """
    Returns the future weather forecast points for a given plant.
    """
    plant = get_plant_by_id(plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail=f"Plant {plant_id} not found")

    lat = plant["latitude"]
    lon = plant["longitude"]

    # Estimate how many days we need. hours / 24 + 1
    forecast_days = max(1, (hours // 24) + 2)

    try:
        df = fetch_weather_forecast(latitude=lat, longitude=lon, past_days=0, forecast_days=forecast_days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather: {str(e)}")

    if df.empty:
        raise HTTPException(status_code=500, detail="Weather data is empty")

    now = datetime.now(timezone.utc)
    current_hour = now.replace(minute=0, second=0, microsecond=0)

    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")

    # Filter to include rows strictly greater than current hour
    df_future = df[df.index > current_hour]

    # Limit to requested hours
    df_future = df_future.head(hours)

    points = []
    for ts, row in df_future.iterrows():
        point = WeatherPoint(
            timestamp=ts.to_pydatetime(),
            temperature_2m=float(row.get("temperature_2m", 0.0)),
            cloud_cover=float(row.get("cloud_cover", 0.0)),
            wind_speed_10m=float(row.get("wind_speed_10m", 0.0)),
            shortwave_radiation=float(row.get("shortwave_radiation", 0.0))
        )
        points.append(point)

    return WeatherResponse(
        plant_id=plant_id,
        valid_time=now,
        provenance="open-meteo",
        interval_minutes=60,
        points=points
    )

@router.get("/market/prices", response_model=MarketPriceResponse, tags=["Market"])
def get_market_prices(zone: str = "DE-LU", hours: int = 24):
    """
    Returns future market prices for a given zone.
    Currently only DE-LU is supported via fixture or simulated spreads.
    """
    if zone != "DE-LU":
        raise HTTPException(status_code=400, detail="Only DE-LU zone is supported for market prices.")

    now = datetime.now(timezone.utc)
    current_hour = now.replace(minute=0, second=0, microsecond=0)
    start_date = current_hour.date()
    # Estimate how many days we need: hours / 24 + 1 to cross day boundaries safely
    end_date = start_date + timedelta(days=max(1, (hours // 24) + 1))

    try:
        # In a real environment, we'd pull from a real database or service.
        # For this prototype, we use the deterministic mock/fetch function directly.
        resp = fetch_delu_prices(start_date=start_date, end_date=end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market prices: {str(e)}")

    if resp.diagnostic.status != "ok" or resp.data.empty:
        raise HTTPException(status_code=500, detail="Market prices data is empty or unavailable.")

    df = resp.data
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")

    # Filter to include rows strictly >= current_hour
    df_future = df[df.index >= current_hour]

    # In '15min' frequency, each hour has 4 intervals
    # 'hours' represents how many hours of data we want, so points = hours * 4
    df_future = df_future.head(hours * 4)

    points = []
    for ts, row in df_future.iterrows():
        points.append(
            MarketPricePoint(
                timestamp=ts.to_pydatetime(),
                day_ahead_eur_mwh=float(row.get("day_ahead_eur_mwh", 0.0)),
                intraday_eur_mwh=float(row.get("intraday_eur_mwh", 0.0)),
                balancing_short_eur_mwh=float(row.get("balancing_short_eur_mwh", 0.0)),
                balancing_long_eur_mwh=float(row.get("balancing_long_eur_mwh", 0.0)),
            )
        )

    return MarketPriceResponse(
        zone=zone,
        valid_time=now,
        provenance=resp.provider,
        interval_minutes=15, # 15-minute intervals for DE-LU mock
        points=points
    )

@router.post("/commitment/recommend", response_model=RecommendationResponse, tags=["Commitment"])
def get_commitment_recommendation(request: RecommendationRequest):
    """
    Generate an action recommendation based on commitment gap, battery availability, and market prices.
    """
    try:
        return recommend_action(request)
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred during recommendation generation.")

def get_action_ledger() -> ActionLedger:
    return ActionLedger()

@router.post("/commitment/actions/accept", response_model=AcceptedAction, tags=["Commitment"])
def accept_commitment_action(action: AcceptedAction):
    """
    Accepts and persists a commitment recommendation action to the local ledger.
    """
    try:
        ledger = get_action_ledger()
        ledger.record_action(action)
        return action
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred while accepting the action.")

@router.get("/commitment/actions", response_model=list[AcceptedAction], tags=["Commitment"])
def get_commitment_actions(plant_id: str | None = None):
    """
    Retrieves the list of accepted commitment actions from the local ledger.
    """
    try:
        ledger = get_action_ledger()
        return ledger.get_actions(plant_id)
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred while retrieving accepted actions.")

@router.get("/commitment/metrics", response_model=CommitmentMetrics, tags=["Commitment"])
def get_commitment_metrics(plant_id: str | None = None):
    """
    Calculates aggregated metrics from the accepted commitment actions.
    """
    try:
        ledger = get_action_ledger()
        actions = ledger.get_actions(plant_id)

        total_shortfall_mwh = sum(a.commitment_gap_mwh for a in actions)
        total_estimated_cost_eur = sum(a.estimated_cost_eur for a in actions)
        total_avoided_cost_eur = sum(a.avoided_imbalance_cost_eur for a in actions)

        return CommitmentMetrics(
            total_shortfall_mwh=total_shortfall_mwh,
            total_estimated_cost_eur=total_estimated_cost_eur,
            total_avoided_cost_eur=total_avoided_cost_eur,
            action_count=len(actions)
        )
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred while calculating commitment metrics.")

@router.get("/plant-health", response_model=list[PlantHealthResponse], tags=["Health"])
def list_plant_health():
    """
    Returns rule-based health diagnostics for all stable demo plants.
    """
    plants = get_all_plants()
    results = []
    for p in plants:
        health = get_plant_health(p["plant_id"])
        if health:
            results.append(health)
    return results

@router.get("/plant-health/{plant_id}", response_model=PlantHealthResponse, tags=["Health"])
def get_single_plant_health(plant_id: str):
    """
    Returns health diagnostics for a specific plant by its identifier.
    """
    health = get_plant_health(plant_id)
    if not health:
        raise HTTPException(status_code=404, detail=f"Plant {plant_id} not found")
    return health
