from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ExplanationAttribution(BaseModel):
    """Represents the attribution of a feature to the overall forecast."""
    feature_name: str
    contribution_mw: float
    description: str


class ExplanationResponse(BaseModel):
    """
    Response model for an explanation of a forecast and signal.
    """
    summary: str = Field(..., description="Human-readable summary of the situation.")
    confidence: str = Field(..., description="High, Medium, or Low confidence.")
    uncertainty_mw: float = Field(..., description="Total uncertainty spread in MW.")
    top_drivers: List[str] = Field(..., description="Names of the most impactful features.")
    attribution: List[ExplanationAttribution] = Field(
        default_factory=list, description="Detailed feature contributions."
    )

    model_config = ConfigDict()


def generate_explanation(
    forecast_delta: float,
    baseline: float,
    lower_bound: float,
    upper_bound: float,
    features: Optional[Dict[str, float]] = None,
    market_price: Optional[float] = None,
) -> ExplanationResponse:
    """
    Generate an explainable summary and attribution for a given forecast.

    Args:
        forecast_delta: Expected deviation from baseline in MW.
        baseline: Expected baseline generation in MW.
        lower_bound: Lower bound of the forecast (MW).
        upper_bound: Upper bound of the forecast (MW).
        features: Optional dictionary of feature names to their values or importance scores.
        market_price: Optional prevailing market price.

    Returns:
        An ExplanationResponse containing summary, confidence, drivers, and attribution.
    """
    uncertainty_mw = max(0.0, upper_bound - lower_bound)

    # Simple confidence heuristic based on uncertainty relative to baseline/delta
    base_scale = max(abs(baseline), abs(forecast_delta), 1.0)
    relative_uncertainty = uncertainty_mw / base_scale

    if relative_uncertainty < 0.2:
        confidence = "High"
    elif relative_uncertainty < 0.5:
        confidence = "Medium"
    else:
        confidence = "Low"

    top_drivers = []
    attribution = []

    # Process features if provided
    if features:
        # Sort features by absolute magnitude of their value/score
        sorted_features = sorted(features.items(), key=lambda x: abs(x[1]), reverse=True)
        top_features = sorted_features[:3]  # Take top 3

        for name, value in top_features:
            top_drivers.append(name)
            # In a real model, value might be SHAP or similar; here we mock attribution
            desc = "Increases generation" if value > 0 else "Decreases generation"
            attribution.append(
                ExplanationAttribution(
                    feature_name=name,
                    contribution_mw=value,
                    description=desc
                )
            )

    # Build summary text
    direction = "higher" if forecast_delta > 0 else "lower"
    abs_delta = abs(forecast_delta)

    summary = (
        f"Forecast expects generation to be {abs_delta:.1f} MW {direction} than baseline. "
        f"Uncertainty spread is {uncertainty_mw:.1f} MW ({confidence} confidence)."
    )

    if top_drivers:
        drivers_str = ", ".join(top_drivers)
        summary += f" Key drivers include: {drivers_str}."

    if market_price is not None:
        if market_price < 0:
            summary += f" Market price is negative ({market_price:.2f}), indicating potential curtailment."
        elif market_price > 200:
            summary += f" Market price is high ({market_price:.2f}), increasing opportunity value."

    return ExplanationResponse(
        summary=summary,
        confidence=confidence,
        uncertainty_mw=uncertainty_mw,
        top_drivers=top_drivers,
        attribution=attribution
    )
