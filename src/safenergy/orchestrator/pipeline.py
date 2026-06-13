import datetime
import logging
from typing import List, Optional

import pandas as pd
from pydantic import BaseModel

from safenergy.features.alignment import align_generation_and_prices, align_weather_and_generation
from safenergy.features.engineering import create_target_deltas, create_time_features
from safenergy.forecast.service import forecast_serving
from safenergy.ingest.market import fetch_ercot_generation, fetch_ercot_prices
from safenergy.ingest.weather import fetch_weather_forecast
from safenergy.signals.explanation import ExplanationResponse, generate_explanation
from safenergy.signals.objects import TradingSignal
from safenergy.signals.pipeline import generate_trading_signals
from safenergy.storage.client import StorageClient


class OrchestratorResponse(BaseModel):
    asset_id: str
    issue_time: datetime.datetime
    forecast_df: pd.DataFrame
    signals: List[TradingSignal]
    explanations: List[ExplanationResponse]

    model_config = {"arbitrary_types_allowed": True}

def run_end_to_end_pipeline(
    asset_id: str,
    latitude: float,
    longitude: float,
    start_date: datetime.date,
    end_date: datetime.date,
    model_path: Optional[str] = None,
    simulate_failure: bool = False,
    strong_threshold: float = 100.0,
    weak_threshold: float = 20.0,
    curtailment_price_threshold: float = -10.0,
    extreme_price_threshold: float = 1000.0,
) -> OrchestratorResponse:
    """
    Runs the full end-to-end forecasting and trading signal pipeline.
    """
    issue_time = datetime.datetime.now(datetime.timezone.utc)

    # 1. Data Retrieval
    logging.info(f"Fetching generation data for {asset_id}")
    gen_data = fetch_ercot_generation(start_date, end_date, simulate_failure=simulate_failure)

    logging.info(f"Fetching market price data for {asset_id}")
    price_data = fetch_ercot_prices(start_date, end_date, simulate_failure=simulate_failure)

    logging.info(f"Fetching weather forecast for {latitude}, {longitude}")
    try:
        weather_df = fetch_weather_forecast(latitude, longitude, start_date=start_date, end_date=end_date)
    except Exception as e:
        logging.warning(f"Failed to fetch weather: {e}")
        weather_df = pd.DataFrame()

    if weather_df.empty or gen_data.data.empty or price_data.data.empty:
        logging.warning("Incomplete data retrieved, returning empty results.")
        return OrchestratorResponse(
            asset_id=asset_id,
            issue_time=issue_time,
            forecast_df=pd.DataFrame(),
            signals=[],
            explanations=[]
        )

    # 2. Feature Building
    logging.info("Aligning and building features")
    aligned_gen_weather = align_weather_and_generation(weather_df, gen_data)

    # We create time features
    features_df = create_time_features(aligned_gen_weather)

    # For baseline comparison we create target deltas if 'solar_generation_mw' exists
    if "solar_generation_mw" in features_df.columns:
        features_df["generation"] = features_df["solar_generation_mw"]
    elif "wind_generation_mw" in features_df.columns:
        features_df["generation"] = features_df["wind_generation_mw"]
    else:
        # Fallback for baseline calculation to succeed
        features_df["generation"] = 0.0

    # Let's also prepare baselines
    # We'll use 24h lag for expected baseline
    features_df = create_target_deltas(features_df, columns=["generation"], baseline_lag=24)
    baseline_col = "generation_lag_24h"
    if baseline_col not in features_df.columns:
        features_df[baseline_col] = features_df["generation"].shift(24)

    # 3. Model Inference & Baseline Comparison
    logging.info("Running forecast inference")
    preds_df = forecast_serving(
        features=features_df,
        issue_time=issue_time,
        model_path=model_path,
        return_uncertainty=True
    )

    # Join predictions with features to calculate deltas
    preds_df = preds_df.join(features_df[[baseline_col, "generation"]], how="inner")

    # The actual delta = forecast point - baseline expectation
    preds_df["delta"] = preds_df["point"] - preds_df[baseline_col]

    # Align predictions and prices
    # preds_df is hourly, prices might need alignment
    preds_with_prices = align_generation_and_prices(preds_df, price_data)

    # Fill prices if missing with some reasonable default to allow pipeline to proceed
    if "rtm_price_usd_mwh" not in preds_with_prices.columns:
         preds_with_prices["rtm_price_usd_mwh"] = 20.0

    preds_with_prices["rtm_price_usd_mwh"] = preds_with_prices["rtm_price_usd_mwh"].fillna(20.0)

    # Drop NA to avoid issues in signal generation
    if "delta" in preds_with_prices.columns and baseline_col in preds_with_prices.columns:
        final_df = preds_with_prices.dropna(subset=["delta", baseline_col, "rtm_price_usd_mwh"])
    else:
        final_df = pd.DataFrame()

    if final_df.empty:
        logging.warning("Aligned features are empty, returning empty results.")
        return OrchestratorResponse(
            asset_id=asset_id,
            issue_time=issue_time,
            forecast_df=pd.DataFrame(),
            signals=[],
            explanations=[]
        )

    # 4. Signal Generation
    logging.info("Generating trading signals")
    signals = generate_trading_signals(
        asset_id=asset_id,
        deltas=final_df["delta"],
        baselines=final_df[baseline_col],
        prices=final_df["rtm_price_usd_mwh"],
        strong_threshold=strong_threshold,
        weak_threshold=weak_threshold,
        curtailment_price_threshold=curtailment_price_threshold,
        extreme_price_threshold=extreme_price_threshold,
    )

    # 5. Explanation
    logging.info("Generating explanations")
    explanations = []
    for ts, row in final_df.iterrows():
        # Get features for attribution, simplified here
        ts_features = {}
        for col in ["temperature_2m", "cloud_cover", "wind_speed_10m"]:
            if col in features_df.columns and ts in features_df.index:
                ts_features[col] = features_df.loc[ts, col]

        explanation = generate_explanation(
            forecast_delta=row["delta"],
            baseline=row[baseline_col],
            lower_bound=row.get("lower", row["point"]),
            upper_bound=row.get("upper", row["point"]),
            features=ts_features,
            market_price=row["rtm_price_usd_mwh"],
        )
        explanations.append(explanation)

    # 6. Storage
    logging.info("Saving outputs to storage")
    storage = StorageClient()
    try:
        cache_key = f"pipeline_{asset_id}_{issue_time.strftime('%Y%m%d%H%M%S')}"
        storage.save_dataframe(
            df=preds_with_prices,
            cache_key=cache_key,
            dataset_type="pipeline_results",
            issue_time=issue_time,
        )
    finally:
        storage.close()

    # 7. Response Assembly
    logging.info("Pipeline complete")
    return OrchestratorResponse(
        asset_id=asset_id,
        issue_time=issue_time,
        forecast_df=preds_with_prices,
        signals=signals,
        explanations=explanations,
    )
