"""Signal generation. Entry on Supertrend flip, exit on SL/TP/TSL/time."""

import numpy as np
from numpy.typing import NDArray

from strategy_core.state import TradeState
from strategy_core.indicators import atr_above_median


def detect_flip(direction: NDArray[np.float64], idx: int) -> str | None:
    """
    Detect Supertrend direction flip on closed candle.
    Returns "LONG" if -1 -> +1, "SHORT" if +1 -> -1, else None.
    """
    if idx < 1:
        return None
    prev = int(direction[idx - 1])
    curr = int(direction[idx])
    if prev == -1 and curr == 1:
        return "LONG"
    if prev == 1 and curr == -1:
        return "SHORT"
    return None


def check_exit(
    state: TradeState,
    high: float,
    low: float,
    close: float,
    atr: float,
    config_tp_rr: float,
    config_tsl_mult: float,
    config_max_bars: int,
) -> str | None:
    """
    Check if position should exit.
    Returns reason: "stop_hit", "tp_hit", "trailing_stop", "time_exit", or None.
    """
    if state.position_side == "FLAT":
        return None

    initial_stop = state.initial_stop_loss if state.initial_stop_loss else state.stop_loss
    stop_distance = abs(state.entry_price - initial_stop)

    if state.position_side == "LONG":
        if low <= state.stop_loss:
            return "stop_hit"
        if high >= state.take_profit:
            return "tp_hit"
        if state.trailing_stop is not None and low <= state.trailing_stop:
            return "trailing_stop"
    else:  # SHORT
        if high >= state.stop_loss:
            return "stop_hit"
        if low <= state.take_profit:
            return "tp_hit"
        if state.trailing_stop is not None and high >= state.trailing_stop:
            return "trailing_stop"

    if state.bars_in_trade >= config_max_bars:
        return "time_exit"

    return None


def update_trailing(
    state: TradeState,
    high: float,
    low: float,
    atr: float,
    tsl_mult: float,
) -> float | None:
    """
    Update trailing stop. Activates after 1R. Never loosens.
    Returns new trailing_stop level or None if not yet activated/updated.
    """
    if state.position_side == "FLAT":
        return None

    initial_stop = state.initial_stop_loss if state.initial_stop_loss else state.stop_loss
    stop_distance = abs(state.entry_price - initial_stop)

    if state.position_side == "LONG":
        extreme = max(state.extreme_price, high)
        if state.trailing_stop is None:
            if extreme >= state.entry_price + stop_distance:
                new_tsl = extreme - tsl_mult * atr
                return max(state.stop_loss, new_tsl)
            return None
        else:
            if extreme >= state.entry_price + stop_distance:
                new_tsl = extreme - tsl_mult * atr
                return max(state.trailing_stop, new_tsl)
            return state.trailing_stop
    else:
        extreme = min(state.extreme_price, low)
        if state.trailing_stop is None:
            if extreme <= state.entry_price - stop_distance:
                new_tsl = extreme + tsl_mult * atr
                return min(state.stop_loss, new_tsl)
            return None
        else:
            if extreme <= state.entry_price - stop_distance:
                new_tsl = extreme + tsl_mult * atr
                return min(state.trailing_stop, new_tsl)
            return state.trailing_stop
