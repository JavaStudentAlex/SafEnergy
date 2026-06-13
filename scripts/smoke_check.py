#!/usr/bin/env python
"""
Smoke test to verify the core functionality of the SafEnergy prototype.
This runs a deterministic check through the signal and backtest components
to ensure the basic plumbing works without external dependencies.
"""

import sys

import pandas as pd

from safenergy.signals.backtest import evaluate_signals
from safenergy.signals.explanation import generate_explanation
from safenergy.signals.pipeline import generate_trading_signals


def run_smoke_check():
    print("Starting SafEnergy Smoke Check...")

    # 1. Test Explanation Generation
    print("Testing Explanation Generation...")
    try:
        explanation = generate_explanation(
            forecast_delta=30.0,
            baseline=100.0,
            lower_bound=110.0,
            upper_bound=150.0,
            features={"cloud_cover": -20.0, "wind_speed": 5.0},
            market_price=10.0,
        )
        assert explanation is not None
        assert explanation.confidence in ["High", "Medium", "Low"]
        print("  ✓ Explanation generation successful.")
    except Exception as e:
        print(f"  ✗ Explanation generation failed: {e}")
        return False

    # 2. Test Trading Signals
    print("Testing Trading Signals Pipeline...")
    try:
        index = pd.date_range(start="2024-01-01", periods=3, freq="h", tz="UTC")
        deltas = pd.Series([50.0, -120.0, 10.0], index=index)
        baselines = pd.Series([100.0, 150.0, 100.0], index=index)
        prices = pd.Series([20.0, 1050.0, -15.0], index=index)

        signals = generate_trading_signals(
            asset_id="smoke-asset",
            deltas=deltas,
            baselines=baselines,
            prices=prices,
            strong_threshold=100.0,
            weak_threshold=20.0,
            curtailment_price_threshold=-10.0,
            extreme_price_threshold=1000.0,
        )
        assert len(signals) == 3
        print("  ✓ Trading signals generation successful.")
    except Exception as e:
        print(f"  ✗ Trading signals generation failed: {e}")
        return False

    # 3. Test Backtest
    print("Testing Backtest Evaluation...")
    try:
        index = pd.date_range(start="2024-01-01", periods=3, freq="h", tz="UTC")
        # Base signals from above might be adjusted, using explicit enum values to test
        # Signal integers: STRONG_LONG = 2, WEAK_LONG = 1, NEUTRAL = 0, WEAK_SHORT = -1, STRONG_SHORT = -2
        test_signals = pd.Series([1, -2, 0], index=index)
        price_changes = pd.Series([5.0, 10.0, -5.0], index=index)

        results = evaluate_signals(signals=test_signals, price_changes=price_changes)
        assert "total_return" in results
        assert "hit_rate" in results
        print("  ✓ Backtest evaluation successful.")
    except Exception as e:
        print(f"  ✗ Backtest evaluation failed: {e}")
        return False

    print("Smoke Check completed successfully!")
    return True


if __name__ == "__main__":
    success = run_smoke_check()
    sys.exit(0 if success else 1)
