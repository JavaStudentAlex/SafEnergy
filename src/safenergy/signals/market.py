import pandas as pd

from safenergy.signals.thresholds import SignalLevel


def apply_market_context(
    signals: pd.Series,
    prices: pd.Series,
    curtailment_price_threshold: float = -10.0,
    extreme_price_threshold: float = 1000.0,
) -> pd.Series:
    """
    Adjust signals based on market context (prices).

    Args:
        signals: Series of SignalLevel values.
        prices: Series of market prices aligned with the signals.
        curtailment_price_threshold: Price below which generation might be curtailed
                                     (e.g., highly negative prices). Long signals are neutralized.
        extreme_price_threshold: Price above which we may want to strengthen short signals,
                                 or limit risk. (Currently just an example of context logic:
                                 we downgrade weak longs if prices are extreme, prioritizing
                                 reliability over marginal opportunistic gains).

    Returns:
        Adjusted Series of SignalLevel values.
    """
    if not signals.index.equals(prices.index):
        # We assume an inner join or exact alignment before this step
        # If not, align them
        df = pd.DataFrame({'signal': signals, 'price': prices}).dropna()
        signals = df['signal']
        prices = df['price']

    adjusted = signals.copy()

    # Rule 1: Curtailment Risk
    # If price is highly negative, excess generation might be curtailed.
    # Therefore, "LONG" signals (expecting more generation than normal) might not materialize
    # as extra market value. Downgrade them to NEUTRAL.
    curtailment_mask = (prices <= curtailment_price_threshold)
    long_mask = (adjusted > SignalLevel.NEUTRAL)
    adjusted[curtailment_mask & long_mask] = SignalLevel.NEUTRAL

    # Rule 2: Extreme Scarcity
    # If prices are extremely high, short signals (we have less generation than expected)
    # represent high risk. We might want to ensure they are at least WEAK_SHORT
    # to highlight the exposure, or downgrade WEAK_LONGs to NEUTRAL to avoid false confidence.
    extreme_mask = (prices >= extreme_price_threshold)
    weak_long_mask = (adjusted == SignalLevel.WEAK_LONG)
    adjusted[extreme_mask & weak_long_mask] = SignalLevel.NEUTRAL

    return adjusted
