from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from safenergy.signals.thresholds import SignalLevel


class TradingSignal(BaseModel):
    """
    Represents a discrete trading signal generated from a forecast delta
    and adjusted for market context.
    """
    timestamp: datetime = Field(
        ..., description="The time for which the signal is valid (timezone-aware UTC)."
    )
    asset_id: str = Field(
        ..., description="Identifier for the region, market, or site (e.g., 'ERCOT-NORTH')."
    )
    forecast_delta: float = Field(
        ..., description="The predicted generation minus the baseline expectation (MW)."
    )
    baseline_expectation: float = Field(
        ..., description="The baseline expected generation (MW)."
    )
    base_signal: SignalLevel = Field(
        ..., description="The raw signal level before market context adjustments."
    )
    adjusted_signal: SignalLevel = Field(
        ..., description="The final risk-adjusted operational signal level."
    )
    market_price: Optional[float] = Field(
        None, description="The prevailing or expected market price at the time of the signal."
    )
    explanation: str = Field(
        ..., description="A human-readable explanation of the signal drivers."
    )

    model_config = ConfigDict(use_enum_values=True)
