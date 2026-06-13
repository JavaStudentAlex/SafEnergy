import logging
from typing import Any, Dict, Tuple

import pandas as pd

from safenergy.forecast.baselines import (
    pvlib_physical_baseline,
    regional_capacity_fallback,
    smart_persistence_baseline,
    wind_power_curve_baseline,
)

logger = logging.getLogger(__name__)


def select_forecast_method(
    df: pd.DataFrame,
    asset_type: str,
    metadata: Dict[str, Any],
    horizon_hours: int = 1,
) -> Tuple[pd.Series, Dict[str, Any]]:
    """
    Select the best deterministic forecast method based on available inputs.

    Args:
        df: Input DataFrame with features.
        asset_type: 'solar' or 'wind'.
        metadata: Dictionary containing asset metadata like capacity_mw, latitude, longitude.
        horizon_hours: Forecast horizon in hours.

    Returns:
        A tuple of (point_predictions, meta_info_dict).
    """
    available_cols = set(df.columns)
    meta = {
        "method": "diagnostic_fallback",
        "inputs_used": [],
        "missing_inputs": [],
        "fallback_reason": "Insufficient inputs for any reliable forecast method",
        "confidence_score": 0.0,
        "lower_bound": None,
        "upper_bound": None,
    }

    if len(df) == 0:
        return pd.Series(dtype=float), meta

    # Helper for extracting columns safely
    gen_col = "generation" if "generation" in available_cols else "generation_mw"

    # 1. Try Smart Persistence
    # Needs generation and a normalizing column.
    norm_col = "irradiance" if asset_type == "solar" else "wind_speed"
    if gen_col in available_cols and norm_col in available_cols:
        logger.info("Selecting Smart Persistence baseline.")
        preds = smart_persistence_baseline(
            df=df, target_col=gen_col, norm_col=norm_col, horizon_hours=horizon_hours
        )
        if not preds.isna().all():
            meta.update({
                "method": "smart_persistence",
                "inputs_used": [gen_col, norm_col],
                "fallback_reason": None,
                "confidence_score": 0.8,
            })
            return preds, meta
        else:
            meta["missing_inputs"].append(f"{gen_col} or {norm_col} for persistence")

    # 2. Try Physical/Domain methods
    capacity = metadata.get("capacity_mw")

    if asset_type == "solar":
        lat = metadata.get("latitude")
        lon = metadata.get("longitude")

        if all(x is not None for x in (lat, lon, capacity)) and "irradiance" in available_cols and "temperature" in available_cols:
            logger.info("Selecting pvlib Physical baseline.")
            preds = pvlib_physical_baseline(
                df=df,
                latitude=lat,
                longitude=lon,
                capacity_mw=capacity,
                irradiance_col="irradiance",
                temp_col="temperature"
            )
            if not preds.isna().all():
                meta.update({
                    "method": "pvlib_physical",
                    "inputs_used": ["irradiance", "temperature", "latitude", "longitude", "capacity_mw"],
                    "fallback_reason": "Missing recent generation for persistence",
                    "confidence_score": 0.6,
                })
                return preds, meta
            else:
                meta["missing_inputs"].append("Valid irradiance/temp data for pvlib")
        else:
            if "irradiance" not in available_cols:
                meta["missing_inputs"].append("irradiance")
            if "temperature" not in available_cols:
                meta["missing_inputs"].append("temperature")
            if lat is None:
                meta["missing_inputs"].append("latitude")
            if lon is None:
                meta["missing_inputs"].append("longitude")
            if capacity is None:
                meta["missing_inputs"].append("capacity_mw")

    elif asset_type == "wind":
        if capacity is not None and "wind_speed" in available_cols:
            logger.info("Selecting Wind Power-Curve baseline.")
            preds = wind_power_curve_baseline(
                df=df,
                wind_speed_col="wind_speed",
                capacity_mw=capacity
            )
            if not preds.isna().all():
                meta.update({
                    "method": "wind_power_curve",
                    "inputs_used": ["wind_speed", "capacity_mw"],
                    "fallback_reason": "Missing recent generation for persistence",
                    "confidence_score": 0.6,
                })
                return preds, meta
            else:
                meta["missing_inputs"].append("Valid wind_speed data for power curve")
        else:
            if "wind_speed" not in available_cols:
                meta["missing_inputs"].append("wind_speed")
            if capacity is None:
                meta["missing_inputs"].append("capacity_mw")

    # 3. Regional Capacity Fallback
    if capacity is not None:
        logger.info("Selecting Regional Capacity fallback.")
        # We can guess base capacity factor from type, e.g., 0.2 for solar, 0.3 for wind
        cf = 0.2 if asset_type == "solar" else 0.3
        preds = regional_capacity_fallback(df=df, capacity_mw=capacity, base_capacity_factor=cf)
        if not preds.isna().all():
             meta.update({
                 "method": "regional_capacity",
                 "inputs_used": ["capacity_mw"],
                 "fallback_reason": "Missing detailed features or metadata for physical models",
                 "confidence_score": 0.2,
             })
             return preds, meta
    else:
        if "capacity_mw" not in meta["missing_inputs"]:
            meta["missing_inputs"].append("capacity_mw")

    # 4. Diagnostic Fallback (return NaN series with 0 confidence)
    logger.warning("No reliable forecast method available.")
    preds = pd.Series(index=df.index, dtype=float)
    return preds, meta
