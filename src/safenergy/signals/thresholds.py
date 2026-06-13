from enum import IntEnum

import pandas as pd


class SignalLevel(IntEnum):
    """Categorical trading signal levels."""
    STRONG_SHORT = -2
    WEAK_SHORT = -1
    NEUTRAL = 0
    WEAK_LONG = 1
    STRONG_LONG = 2


def categorize_delta(
    deltas: pd.Series,
    strong_threshold: float,
    weak_threshold: float,
) -> pd.Series:
    """
    Categorize forecast deltas into operational signal levels.

    Args:
        deltas: Series of forecast generation deltas (predicted - expected).
        strong_threshold: Absolute value above which a delta is considered a STRONG signal.
        weak_threshold: Absolute value above which a delta is considered a WEAK signal.

    Returns:
        Series of SignalLevel values.
    """
    if strong_threshold <= weak_threshold:
        raise ValueError("strong_threshold must be strictly greater than weak_threshold")
    if weak_threshold < 0:
        raise ValueError("thresholds must be non-negative")

    signals = pd.Series(SignalLevel.NEUTRAL, index=deltas.index, name="signal")

    # Positive deltas
    signals[deltas > weak_threshold] = SignalLevel.WEAK_LONG
    signals[deltas > strong_threshold] = SignalLevel.STRONG_LONG

    # Negative deltas
    signals[deltas < -weak_threshold] = SignalLevel.WEAK_SHORT
    signals[deltas < -strong_threshold] = SignalLevel.STRONG_SHORT

    return signals
