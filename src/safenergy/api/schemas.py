from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from safenergy.signals.explanation import ExplanationResponse
from safenergy.signals.objects import BacktestAssumptions, TradingSignal
from safenergy.signals.thresholds import SignalLevel


class FeatureRow(BaseModel):
    timestamp: datetime
    features: Dict[str, float]


class ForecastRequest(BaseModel):
    asset_id: str
    features: List[FeatureRow]
    return_uncertainty: bool = True
    asset_type: str = "solar"
    metadata_dict: Optional[Dict[str, Any]] = None


class ForecastPrediction(BaseModel):
    timestamp: datetime
    point: float
    lower: Optional[float] = None
    upper: Optional[float] = None
    method: str = "unknown"
    confidence_score: float = 0.0
    fallback_reason: Optional[str] = None
    inputs_used: List[str] = []
    missing_inputs: List[str] = []


class ForecastResponse(BaseModel):
    asset_id: str
    predictions: List[ForecastPrediction]


class SignalInputRow(BaseModel):
    timestamp: datetime
    delta: float
    baseline: float
    price: float
    confidence: float = 1.0


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
    assumptions: Optional[BacktestAssumptions] = None
    issue_time: Optional[datetime] = None


class BacktestResponse(BaseModel):
    total_return: float
    hit_rate: float
    hits: int
    misses: int
    flat: int
    total_trades: int
    assumptions: dict
    leakage_check_status: str


class ExplanationRequest(BaseModel):
    forecast_delta: float
    baseline: float
    lower_bound: float
    upper_bound: float
    features: Optional[Dict[str, float]] = None
    market_price: Optional[float] = None

class OrchestratorRequest(BaseModel):
    asset_id: str
    latitude: float
    longitude: float
    start_date: datetime
    end_date: datetime
    simulate_failure: bool = False
    strong_threshold: float = 100.0
    weak_threshold: float = 20.0
    curtailment_price_threshold: float = -10.0
    extreme_price_threshold: float = 1000.0

class OrchestratorAPIResponse(BaseModel):
    asset_id: str
    issue_time: datetime
    signals: List[TradingSignal]
    explanations: List[ExplanationResponse]
    forecast_data_state: str = "live"

    model_config = {"arbitrary_types_allowed": True}

class PlantResponse(BaseModel):
    plant_id: str
    name: str
    latitude: float
    longitude: float
    timezone: str
    capacity_mw: float
    status: str
    battery_capacity_mwh: float
    metadata_dict: Dict[str, Any]


class WeatherPoint(BaseModel):
    timestamp: datetime
    temperature_2m: float
    cloud_cover: float
    wind_speed_10m: float
    shortwave_radiation: float

class WeatherResponse(BaseModel):
    plant_id: str
    valid_time: datetime
    provenance: str
    interval_minutes: int
    points: List[WeatherPoint]


class MarketPricePoint(BaseModel):
    timestamp: datetime
    day_ahead_eur_mwh: float
    intraday_eur_mwh: float
    balancing_short_eur_mwh: float
    balancing_long_eur_mwh: float

class MarketPriceResponse(BaseModel):
    zone: str
    valid_time: datetime
    provenance: str
    interval_minutes: int
    points: List[MarketPricePoint]

class RecommendationRequest(BaseModel):
    forecast_mwh: float
    committed_mwh: float
    battery_available_mwh: float
    intraday_eur_mwh: float
    balancing_short_eur_mwh: float

class RecommendationResponse(BaseModel):
    action: str
    commitment_gap_mwh: float
    battery_discharge_mwh: float
    market_buy_mwh: float
    estimated_cost_eur: float
    avoided_imbalance_cost_eur: float
    confidence_score: float
    explanation: str

class CommitmentMetrics(BaseModel):
    total_shortfall_mwh: float
    total_estimated_cost_eur: float
    total_avoided_cost_eur: float
    action_count: int


class AnomalyDiagnostic(BaseModel):
    category: str
    severity: str
    description: str


class PlantHealthResponse(BaseModel):
    plant_id: str
    status: str
    last_updated: datetime
    anomalies: List[AnomalyDiagnostic]
