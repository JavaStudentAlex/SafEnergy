from safenergy.api.schemas import RecommendationRequest, RecommendationResponse


def recommend_action(request: RecommendationRequest) -> RecommendationResponse:
    gap = request.committed_mwh - request.forecast_mwh

    if gap <= 0:
        return RecommendationResponse(
            action="HOLD",
            commitment_gap_mwh=gap,
            battery_discharge_mwh=0.0,
            market_buy_mwh=0.0,
            estimated_cost_eur=0.0,
            avoided_imbalance_cost_eur=0.0,
            confidence_score=1.0,
            explanation="Forecast exceeds or meets commitment. No action needed."
        )

    battery_use = min(gap, request.battery_available_mwh)
    remaining_gap = gap - battery_use

    market_buy = 0.0
    if remaining_gap > 0 and request.intraday_eur_mwh < request.balancing_short_eur_mwh:
        market_buy = remaining_gap

    action = "HOLD"
    if battery_use > 0 and market_buy > 0:
        action = "DISCHARGE_AND_BUY"
    elif battery_use > 0:
        action = "DISCHARGE_BATTERY"
    elif market_buy > 0:
        action = "BUY_MARKET"

    estimated_cost = market_buy * request.intraday_eur_mwh
    avoided_cost = (battery_use + market_buy) * request.balancing_short_eur_mwh

    explanation = f"Gap of {gap:.2f} MWh detected. "
    if battery_use > 0:
        explanation += f"Discharging {battery_use:.2f} MWh from battery. "
    if market_buy > 0:
        explanation += f"Buying {market_buy:.2f} MWh from intraday market to avoid higher balancing costs. "
    if action == "HOLD":
        explanation += "Holding position as market buy is not cheaper than balancing or battery is unavailable."

    return RecommendationResponse(
        action=action,
        commitment_gap_mwh=gap,
        battery_discharge_mwh=battery_use,
        market_buy_mwh=market_buy,
        estimated_cost_eur=estimated_cost,
        avoided_imbalance_cost_eur=avoided_cost,
        confidence_score=0.9,
        explanation=explanation.strip()
    )
