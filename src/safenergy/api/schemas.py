from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from safenergy.signals.thresholds import SignalLevel


class FeatureRow(BaseModel):
    timestamp: datetime
    features: Dict[str, float]


class ForecastRequest(BaseModel):
    asset_id: str
    features: List[FeatureRow]
    return_uncertainty: bool = True


class ForecastPrediction(BaseModel):
    timestamp: datetime
    point: float
    lower: Optional[float] = None
    upper: Optional[float] = None


class ForecastResponse(BaseModel):
    asset_id: str
    predictions: List[ForecastPrediction]


class SignalInputRow(BaseModel):
    timestamp: datetime
    delta: float
    baseline: float
    price: float


class SignalRequest(BaseModel):
    asset_id: str
    data: List[SignalInputRow]
    strong_threshold: float = 100.0
    weak_threshold: float = 20.0
    curtailment_price_threshold: float = -10.0
    extreme_price_threshold: float = 1000.0


class BacktestInputRow(BaseModel):
    timestamp: datetime
    signal: SignalLevel
    price_change: float


class BacktestRequest(BaseModel):
    data: List[BacktestInputRow]


class BacktestResponse(BaseModel):
    total_return: float
    hit_rate: float
    hits: int
    misses: int
    flat: int
    total_trades: int
