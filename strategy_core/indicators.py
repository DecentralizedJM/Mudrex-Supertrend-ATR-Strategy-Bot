"""
Indicator calculations.
Pure functions, no side effects.
"""

import numpy as np
from numpy.typing import NDArray


def wilder_atr(high: NDArray[np.float64], low: NDArray[np.float64], close: NDArray[np.float64], period: int) -> NDArray[np.float64]:
    """
    Wilder ATR (EMA-style smoothing).
    ATR[0] = SMA(TR[:period]); ATR[i] = (ATR[i-1]*(period-1) + TR[i])/period
    """
    n = len(close)
    tr = np.empty(n, dtype=np.float64)
    tr[0] = high[0] - low[0]
    for i in range(1, n):
        tr[i] = max(
            high[i] - low[i],
            abs(high[i] - close[i - 1]),
            abs(low[i] - close[i - 1]),
        )

    atr = np.full(n, np.nan, dtype=np.float64)
    if n < period:
        return atr

    atr[period - 1] = np.mean(tr[:period])
    for i in range(period, n):
        atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period

    return atr


def supertrend(
    high: NDArray[np.float64],
    low: NDArray[np.float64],
    close: NDArray[np.float64],
    atr: NDArray[np.float64],
    factor: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Standard Supertrend.
    Returns (supertrend_values, direction) where direction: +1 bullish, -1 bearish.
    Price-derived, no forced init.
    """
    n = len(close)
    hl_avg = (high + low) / 2.0
    upper_band = hl_avg + factor * atr
    lower_band = hl_avg - factor * atr

    st = np.full(n, np.nan, dtype=np.float64)
    direction = np.zeros(n, dtype=np.float64)

    for i in range(1, n):
        if np.isnan(atr[i]) or atr[i] <= 0:
            st[i] = st[i - 1] if not np.isnan(st[i - 1]) else close[i]
            direction[i] = direction[i - 1]
            continue

        if close[i - 1] <= upper_band[i - 1]:
            upper_band[i] = min(upper_band[i], upper_band[i - 1])
        if close[i - 1] >= lower_band[i - 1]:
            lower_band[i] = max(lower_band[i], lower_band[i - 1])

        if i == 1:
            direction[i] = 1
        elif not np.isnan(st[i - 1]) and st[i - 1] == upper_band[i - 1]:
            direction[i] = -1 if close[i] > upper_band[i] else 1
        else:
            direction[i] = 1 if close[i] < lower_band[i] else -1

        st[i] = lower_band[i] if direction[i] > 0 else upper_band[i]

    return st, direction


def atr_above_median(atr: NDArray[np.float64], idx: int, window: int) -> bool:
    """Volatility filter: ATR at idx above rolling median."""
    if idx < window or np.any(np.isnan(atr[idx - window : idx + 1])):
        return True
    median_val = np.nanmedian(atr[idx - window : idx])
    return atr[idx] > median_val if not np.isnan(median_val) else True
