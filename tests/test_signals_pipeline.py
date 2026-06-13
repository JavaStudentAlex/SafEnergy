import pandas as pd

from safenergy.signals.pipeline import generate_trading_signals
from safenergy.signals.thresholds import SignalLevel


def test_generate_trading_signals():
    """Test generating a list of TradingSignal objects from components."""

    idx = pd.date_range("2024-01-01 00:00:00", periods=4, freq="h", tz="UTC")

    # 1. Strong Long signal -> +150 > 100
    # 2. Strong Long signal curtailed -> +150 > 100, but price is -20 (curtailment)
    # 3. Weak Long signal extreme -> +50 > 20, but price is 1500 (extreme scarcity)
    # 4. Strong Short signal -> -150 < -100
    deltas = pd.Series([150.0, 150.0, 50.0, -150.0], index=idx)
    baselines = pd.Series([1000.0, 1000.0, 1000.0, 1000.0], index=idx)
    prices = pd.Series([30.0, -20.0, 1500.0, 30.0], index=idx)

    signals = generate_trading_signals(
        asset_id="TEST-ASSET",
        deltas=deltas,
        baselines=baselines,
        prices=prices,
        strong_threshold=100.0,
        weak_threshold=20.0,
        curtailment_price_threshold=-10.0,
        extreme_price_threshold=1000.0
    )

    assert len(signals) == 4

    # Test 1: Normal Strong Long
    assert signals[0].base_signal == SignalLevel.STRONG_LONG
    assert signals[0].adjusted_signal == SignalLevel.STRONG_LONG
    assert "strong long" in signals[0].explanation.lower()

    # Test 2: Curtailed Strong Long -> NEUTRAL
    assert signals[1].base_signal == SignalLevel.STRONG_LONG
    assert signals[1].adjusted_signal == SignalLevel.NEUTRAL
    assert "curtailment" in signals[1].explanation.lower()

    # Test 3: Extreme Scarcity Weak Long -> NEUTRAL
    assert signals[2].base_signal == SignalLevel.WEAK_LONG
    assert signals[2].adjusted_signal == SignalLevel.NEUTRAL
    assert "extreme scarcity" in signals[2].explanation.lower()

    # Test 4: Normal Strong Short
    assert signals[3].base_signal == SignalLevel.STRONG_SHORT
    assert signals[3].adjusted_signal == SignalLevel.STRONG_SHORT
    assert "strong short" in signals[3].explanation.lower()


def test_generate_trading_signals_empty():
    """Test behavior with empty inputs."""
    idx = pd.DatetimeIndex([], tz="UTC")

    deltas = pd.Series([], index=idx, dtype=float)
    baselines = pd.Series([], index=idx, dtype=float)
    prices = pd.Series([], index=idx, dtype=float)

    signals = generate_trading_signals(
        asset_id="TEST",
        deltas=deltas,
        baselines=baselines,
        prices=prices
    )

    assert len(signals) == 0


def test_generate_trading_signals_low_confidence():
    """Test behavior when forecast confidence is low."""
    idx = pd.date_range("2024-01-01 00:00:00", periods=1, freq="h", tz="UTC")

    deltas = pd.Series([150.0], index=idx)
    baselines = pd.Series([1000.0], index=idx)
    prices = pd.Series([30.0], index=idx)
    confidences = pd.Series([0.2], index=idx)  # Low confidence

    signals = generate_trading_signals(
        asset_id="TEST",
        deltas=deltas,
        baselines=baselines,
        prices=prices,
        confidence_scores=confidences,
        strong_threshold=100.0,
        weak_threshold=20.0,
        curtailment_price_threshold=-10.0,
        extreme_price_threshold=1000.0
    )

    assert len(signals) == 1
    # Despite strong delta, should be downgraded to neutral due to low confidence
    assert signals[0].adjusted_signal == SignalLevel.NEUTRAL
    assert "low forecast confidence" in signals[0].explanation.lower()
