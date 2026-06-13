import pandas as pd
import pytest

from safenergy.signals.market import apply_market_context
from safenergy.signals.thresholds import SignalLevel, categorize_delta


def test_categorize_delta():
    """Test categorizing deltas into SignalLevels."""
    deltas = pd.Series([-50, -20, -5, 0, 5, 20, 50])

    signals = categorize_delta(deltas, strong_threshold=30, weak_threshold=10)

    assert signals.iloc[0] == SignalLevel.STRONG_SHORT
    assert signals.iloc[1] == SignalLevel.WEAK_SHORT
    assert signals.iloc[2] == SignalLevel.NEUTRAL
    assert signals.iloc[3] == SignalLevel.NEUTRAL
    assert signals.iloc[4] == SignalLevel.NEUTRAL
    assert signals.iloc[5] == SignalLevel.WEAK_LONG
    assert signals.iloc[6] == SignalLevel.STRONG_LONG


def test_categorize_delta_invalid_thresholds():
    """Test validation of threshold values."""
    deltas = pd.Series([10])

    with pytest.raises(ValueError, match="strong_threshold must be strictly greater than weak_threshold"):
        categorize_delta(deltas, strong_threshold=10, weak_threshold=20)

    with pytest.raises(ValueError, match="thresholds must be non-negative"):
        categorize_delta(deltas, strong_threshold=20, weak_threshold=-5)


def test_apply_market_context():
    """Test applying market context rules to signals."""
    signals = pd.Series([
        SignalLevel.STRONG_LONG,
        SignalLevel.WEAK_LONG,
        SignalLevel.NEUTRAL,
        SignalLevel.WEAK_SHORT,
        SignalLevel.STRONG_SHORT,
        SignalLevel.WEAK_LONG,  # For extreme price
    ])
    prices = pd.Series([
        -20.0,  # Curtailment: STRONG_LONG -> NEUTRAL
        -15.0,  # Curtailment: WEAK_LONG -> NEUTRAL
        -20.0,  # Curtailment: NEUTRAL -> NEUTRAL
        -20.0,  # Curtailment: WEAK_SHORT -> WEAK_SHORT
        -20.0,  # Curtailment: STRONG_SHORT -> STRONG_SHORT
        1500.0, # Extreme: WEAK_LONG -> NEUTRAL
    ])

    adjusted = apply_market_context(
        signals,
        prices,
        curtailment_price_threshold=-10.0,
        extreme_price_threshold=1000.0
    )

    assert adjusted.iloc[0] == SignalLevel.NEUTRAL
    assert adjusted.iloc[1] == SignalLevel.NEUTRAL
    assert adjusted.iloc[2] == SignalLevel.NEUTRAL
    assert adjusted.iloc[3] == SignalLevel.WEAK_SHORT
    assert adjusted.iloc[4] == SignalLevel.STRONG_SHORT
    assert adjusted.iloc[5] == SignalLevel.NEUTRAL

def test_apply_market_context_alignment():
    """Test market context when indices do not initially match."""
    signals = pd.Series(
        [SignalLevel.STRONG_LONG, SignalLevel.STRONG_SHORT],
        index=[1, 2]
    )
    prices = pd.Series(
        [-50.0, -50.0],
        index=[2, 3] # Only index 2 overlaps
    )

    adjusted = apply_market_context(signals, prices)

    # Only index 2 should remain
    assert len(adjusted) == 1
    assert adjusted.index[0] == 2
    assert adjusted.iloc[0] == SignalLevel.STRONG_SHORT
