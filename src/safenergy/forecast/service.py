import logging
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd

from safenergy.forecast.models import LightGBMForecaster
from safenergy.forecast.selector import select_forecast_method


def forecast_serving(
    features: pd.DataFrame,
    issue_time: datetime,
    model_path: Optional[str] = None,
    horizon_hours: int = 1,
    return_uncertainty: bool = True,
    asset_type: str = "solar",
    metadata_dict: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Generate forecast predictions from features, falling back to a baseline if a model isn't available.

    Args:
        features: DataFrame containing features, indexed by timezone-aware timestamps.
        issue_time: The time the forecast is issued.
        model_path: Optional path to a trained LightGBM model.
        horizon_hours: Horizon for persistence fallback if needed.
        return_uncertainty: Whether to include uncertainty bounds in the output.

    Returns:
        DataFrame containing 'point' predictions and optionally 'lower' and 'upper' bounds.
    """
    model = None
    if model_path:
        try:
            model = LightGBMForecaster.load(model_path)
            logging.info(f"Successfully loaded model from {model_path}")
        except Exception as e:
            logging.warning(f"Failed to load model from {model_path}, falling back to baseline: {e}")

    if model:
        try:
            return model.predict(features, return_uncertainty=return_uncertainty)
        except Exception as e:
            logging.warning(f"Model prediction failed, falling back to baseline: {e}")

    # Fallback: Persistence baseline using 'generation' column if present
    # If we don't have generation, just return 0s or handle gracefully.
    # In this scaffold, we expect some feature representing previous state to exist.
    # Often, features has the exact target column or something similar.
    # We will look for 'generation' or default to 10.0 for deterministic mock behaviour if missing

    preds, meta = select_forecast_method(
        df=features,
        asset_type=asset_type,
        metadata=metadata_dict or {},
        horizon_hours=horizon_hours
    )

    df_out = pd.DataFrame({"point": preds}, index=features.index)

    if return_uncertainty:
        # Scale uncertainty bounds inversely with confidence
        conf = meta.get("confidence_score", 0.0)
        df_out["lower"] = df_out["point"] - (1.0 - conf) * 10.0
        df_out["upper"] = df_out["point"] + (1.0 - conf) * 10.0

    # Attach metadata columns
    df_out["method"] = meta.get("method", "unknown")
    df_out["confidence_score"] = meta.get("confidence_score", 0.0)
    df_out["fallback_reason"] = meta.get("fallback_reason")
    df_out["inputs_used"] = [meta.get("inputs_used", [])] * len(df_out)
    df_out["missing_inputs"] = [meta.get("missing_inputs", [])] * len(df_out)

    return df_out
