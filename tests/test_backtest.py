
import pandas as pd
import pytest

from safenergy.signals.backtest import evaluate_signals
from safenergy.signals.objects import BacktestAssumptions
from safenergy.signals.thresholds import SignalLevel


def test_evaluate_signals():
    """Test the core backtest evaluation metrics logic."""

    # Define an index
    idx = pd.date_range("2024-01-01 00:00:00", periods=6, freq="h", tz="UTC")

    # Define signals
    signals = pd.Series([
        SignalLevel.STRONG_LONG, # 2
        SignalLevel.WEAK_LONG,   # 1
        SignalLevel.NEUTRAL,     # 0
        SignalLevel.WEAK_SHORT,  # -1
        SignalLevel.STRONG_SHORT,# -2
        SignalLevel.STRONG_LONG, # 2 (will result in miss)
    ], index=idx)

    # Define price changes
    price_changes = pd.Series([
        10.0,  # 2 * 10 = +20 (hit)
        5.0,   # 1 * 5 = +5 (hit)
        100.0, # 0 * 100 = 0 (ignored/neutral)
        -10.0, # -1 * -10 = +10 (hit)
        0.0,   # -2 * 0 = 0 (flat trade)
        -5.0,  # 2 * -5 = -10 (miss)
    ], index=idx)

    metrics = evaluate_signals(signals, price_changes)

    assert metrics["total_return"] == 25.0
    assert metrics["hits"] == 3
    assert metrics["misses"] == 1
    assert metrics["flat"] == 1
    assert metrics["total_trades"] == 5
    assert metrics["hit_rate"] == 3 / 5

def test_evaluate_signals_unaligned():
    """Test the behavior when inputs are not aligned on the index."""
    idx1 = pd.date_range("2024-01-01 00:00:00", periods=2, freq="h", tz="UTC")
    idx2 = pd.date_range("2024-01-01 01:00:00", periods=2, freq="h", tz="UTC")

    signals = pd.Series([SignalLevel.WEAK_LONG, SignalLevel.STRONG_SHORT], index=idx1)
    # price_changes overlaps with signals only on idx1[1] (which is idx2[0])
    price_changes = pd.Series([-10.0, 5.0], index=idx2)

    # At the overlap (idx1[1] / idx2[0]), signal is STRONG_SHORT (-2) and price change is -10.0
    # Expected return is -2 * -10.0 = 20.0
    metrics = evaluate_signals(signals, price_changes)

    assert metrics["total_return"] == 20.0
    assert metrics["hits"] == 1
    assert metrics["total_trades"] == 1
    assert metrics["hit_rate"] == 1.0

def test_evaluate_signals_all_neutral():
    """Test the behavior when all signals are neutral."""
    idx = pd.date_range("2024-01-01 00:00:00", periods=3, freq="h", tz="UTC")
    signals = pd.Series([SignalLevel.NEUTRAL] * 3, index=idx)
    price_changes = pd.Series([10.0, -5.0, 0.0], index=idx)

    metrics = evaluate_signals(signals, price_changes)

    assert metrics["total_return"] == 0.0
    assert metrics["total_trades"] == 0
    assert metrics["hit_rate"] == 0.0

def test_evaluate_signals_with_assumptions():
    idx = pd.date_range("2024-01-01 00:00:00", periods=2, freq="h", tz="UTC")
    signals = pd.Series([SignalLevel.WEAK_LONG, SignalLevel.STRONG_SHORT], index=idx) # 1, -2
    price_changes = pd.Series([10.0, -5.0], index=idx) # +10, +10 gross returns = +20

    # Total positions abs = 3. Transaction cost = 1.0, slippage = 0.5. Total cost = 3 * 1.5 = 4.5
    # Net return = 20.0 - 4.5 = 15.5
    assumptions = BacktestAssumptions(transaction_cost=1.0, slippage=0.5)

    metrics = evaluate_signals(signals, price_changes, assumptions=assumptions)
    assert metrics["total_return"] == 15.5

def test_evaluate_signals_leakage_failure():
    idx = pd.date_range("2024-01-01 00:00:00", periods=2, freq="h", tz="UTC")
    signals = pd.Series([SignalLevel.WEAK_LONG, SignalLevel.WEAK_LONG], index=idx)
    price_changes = pd.Series([10.0, 10.0], index=idx)

    issue_time = pd.Timestamp("2023-12-31 00:00:00", tz="UTC")

    with pytest.raises(ValueError, match="Issue-time leakage detected"):
        evaluate_signals(signals, price_changes, issue_time=issue_time)
