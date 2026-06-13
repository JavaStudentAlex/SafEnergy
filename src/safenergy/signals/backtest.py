import pandas as pd


def evaluate_signals(
    signals: pd.Series,
    price_changes: pd.Series,
) -> dict:
    """
    Evaluate trading signals against subsequent price changes.

    A LONG signal generates positive return if the price goes up.
    A SHORT signal generates positive return if the price goes down.
    The size of the position is determined by the signal strength
    (e.g. STRONG_LONG = 2, WEAK_LONG = 1).

    Args:
        signals: Series of SignalLevel values.
        price_changes: Series of realized price changes aligned with the signals.
            A positive value means the price increased.

    Returns:
        A dictionary with backtest metrics including total return, hit rate, and counts.
    """
    if not signals.index.equals(price_changes.index):
        # We assume an inner join or exact alignment before this step
        df = pd.DataFrame({'signal': signals, 'price_change': price_changes}).dropna()
        signals = df['signal']
        price_changes = df['price_change']

    # Convert enum to integer values representing position size
    positions = signals.astype(int)

    # Calculate returns per period
    returns = positions * price_changes

    total_return = returns.sum()

    # Only consider periods where we actually took a position (not NEUTRAL)
    active_periods = (positions != 0)
    num_active = active_periods.sum()

    # Hits are periods where we made a strictly positive return
    hits = (returns > 0).sum()

    # Misses are periods where we made a strictly negative return
    misses = (returns < 0).sum()

    # Neutral/Zero return periods where we took a position
    flat = (returns == 0) & active_periods
    num_flat = flat.sum()

    hit_rate = hits / num_active if num_active > 0 else 0.0

    return {
        "total_return": total_return,
        "hit_rate": hit_rate,
        "hits": int(hits),
        "misses": int(misses),
        "flat": int(num_flat),
        "total_trades": int(num_active)
    }
