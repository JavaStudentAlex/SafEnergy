from typing import List, Optional

import pandas as pd

from safenergy.signals.market import apply_market_context
from safenergy.signals.objects import TradingSignal
from safenergy.signals.thresholds import SignalLevel, categorize_delta


def generate_trading_signals(
    asset_id: str,
    deltas: pd.Series,
    baselines: pd.Series,
    prices: pd.Series,
    confidence_scores: Optional[pd.Series] = None,
    strong_threshold: float = 100.0,
    weak_threshold: float = 20.0,
    curtailment_price_threshold: float = -10.0,
    extreme_price_threshold: float = 1000.0,
) -> List[TradingSignal]:
    """
    Generate a list of TradingSignal objects from forecast deltas, baselines, and prices.

    Args:
        asset_id: Identifier for the region, market, or site.
        deltas: Series of forecast generation deltas (predicted - expected) in MW.
        baselines: Series of baseline expected generation in MW.
        prices: Series of market prices.
        strong_threshold: MW threshold for a STRONG signal.
        weak_threshold: MW threshold for a WEAK signal.
        curtailment_price_threshold: Price below which generation might be curtailed.
        extreme_price_threshold: Price above which we may want to limit risk.

    Returns:
        List of TradingSignal objects.
    """
    # Ensure all series have the same timezone-aware datetime index
    df_dict = {
        "delta": deltas,
        "baseline": baselines,
        "price": prices
    }
    if confidence_scores is not None:
        df_dict["confidence"] = confidence_scores

    df = pd.DataFrame(df_dict).dropna()

    if df.empty:
        return []

    base_signals = categorize_delta(
        df["delta"],
        strong_threshold=strong_threshold,
        weak_threshold=weak_threshold
    )

    adjusted_signals = apply_market_context(
        base_signals,
        df["price"],
        curtailment_price_threshold=curtailment_price_threshold,
        extreme_price_threshold=extreme_price_threshold
    )

    signals = []
    for timestamp, row in df.iterrows():
        base_sig = SignalLevel(base_signals.loc[timestamp])
        adj_sig = SignalLevel(adjusted_signals.loc[timestamp])

        delta = row["delta"]
        price = row["price"]

        # Generate a human readable explanation
        if base_sig == adj_sig:
            if base_sig == SignalLevel.NEUTRAL:
                explanation = f"Forecast delta of {delta:.1f} MW is within neutral thresholds."
            else:
                dir_str = "long" if base_sig > 0 else "short"
                strength = "strong" if abs(int(base_sig)) == 2 else "weak"
                explanation = f"Generated {strength} {dir_str} signal due to delta of {delta:.1f} MW."
        else:
            if price <= curtailment_price_threshold and base_sig > SignalLevel.NEUTRAL:
                explanation = (
                    f"Downgraded long signal to NEUTRAL due to curtailment risk "
                    f"(price {price:.1f} <= {curtailment_price_threshold})."
                )
            elif price >= extreme_price_threshold and base_sig == SignalLevel.WEAK_LONG:
                explanation = (
                    f"Downgraded weak long signal to NEUTRAL due to extreme scarcity "
                    f"(price {price:.1f} >= {extreme_price_threshold})."
                )
            else:
                explanation = f"Market context adjusted signal from {base_sig.name} to {adj_sig.name}."

        # Apply confidence downgrade
        if "confidence" in row and row["confidence"] < 0.5:
            adj_sig = SignalLevel.NEUTRAL
            explanation = f"Downgraded signal to NEUTRAL due to low forecast confidence ({row['confidence']:.2f})."

        signal = TradingSignal(
            timestamp=timestamp,  # type: ignore
            asset_id=asset_id,
            forecast_delta=delta,
            baseline_expectation=row["baseline"],
            base_signal=base_sig,
            adjusted_signal=adj_sig,
            market_price=price,
            explanation=explanation
        )
        signals.append(signal)

    return signals
