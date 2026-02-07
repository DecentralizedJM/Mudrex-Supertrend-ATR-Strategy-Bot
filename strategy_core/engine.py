"""
Main engine: process_candle.
Deterministic, no side effects. Called on every closed candle.
"""

from typing import Sequence, Any, TypedDict
import numpy as np
from numpy.typing import NDArray

from strategy_core.config import StrategyConfig
from strategy_core.state import TradeState
from strategy_core.indicators import wilder_atr, supertrend, atr_above_median
from strategy_core.signals import detect_flip, check_exit, update_trailing
from strategy_core.risk import position_size, compute_leverage


class ProposedPosition(TypedDict):
    side: str
    quantity: float
    leverage: int
    entry_price: float
    stop_loss: float
    take_profit: float


class StrategyOutput(TypedDict):
    signal: str
    reason: str
    proposed_position: ProposedPosition | None


def _to_arrays(ohlcv: Sequence[Any]) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Convert OHLCV to numpy arrays. Accepts list of dicts or list of (o,h,l,c,v)."""
    if len(ohlcv) == 0:
        return np.array([]), np.array([]), np.array([]), np.array([])

    first = ohlcv[0]
    if isinstance(first, dict):
        o = np.array([float(r["open"]) for r in ohlcv])
        h = np.array([float(r["high"]) for r in ohlcv])
        l = np.array([float(r["low"]) for r in ohlcv])
        c = np.array([float(r["close"]) for r in ohlcv])
    else:
        o = np.array([float(r[0]) for r in ohlcv])
        h = np.array([float(r[1]) for r in ohlcv])
        l = np.array([float(r[2]) for r in ohlcv])
        c = np.array([float(r[3]) for r in ohlcv])

    return o, h, l, c


def process_candle(
    ohlcv: Sequence[Any],
    account_equity: float,
    contract_specs: dict,
    prev_state: TradeState,
    config: StrategyConfig,
) -> StrategyOutput:
    """
    Process a closed candle. Returns structured output for execution engine.
    OHLCV: list of dicts {open,high,low,close,volume} or list of (o,h,l,c,v).
    contract_specs: {min_quantity, quantity_step}.
    """
    o, h, l_arr, c = _to_arrays(ohlcv)
    n = len(c)

    min_qty = float(contract_specs.get("min_quantity", 0.001))
    quantity_step = float(contract_specs.get("quantity_step", 0.001))
    if quantity_step <= 0:
        quantity_step = 0.001

    if n < config.atr_period + 1:
        return {
            "signal": "HOLD",
            "reason": "insufficient_data",
            "proposed_position": None,
        }

    idx = n - 1

    atr = wilder_atr(h, l_arr, c, config.atr_period)
    st, direction = supertrend(h, l_arr, c, atr, config.supertrend_factor)

    atr_val = atr[idx]
    if np.isnan(atr_val) or atr_val <= 0:
        return {"signal": "HOLD", "reason": "invalid_atr", "proposed_position": None}

    close_val = c[idx]
    high_val = h[idx]
    low_val = l_arr[idx]

    if prev_state.position_side != "FLAT":
        new_extreme = (
            max(prev_state.extreme_price, high_val)
            if prev_state.position_side == "LONG"
            else min(prev_state.extreme_price, low_val)
        )
        if prev_state.extreme_price == 0:
            new_extreme = high_val if prev_state.position_side == "LONG" else low_val

        state_with_extreme = TradeState(
            position_side=prev_state.position_side,
            entry_price=prev_state.entry_price,
            stop_loss=prev_state.stop_loss,
            take_profit=prev_state.take_profit,
            trailing_stop=prev_state.trailing_stop,
            bars_in_trade=prev_state.bars_in_trade + 1,
            extreme_price=new_extreme,
        )

        exit_reason = check_exit(
            state_with_extreme,
            high_val,
            low_val,
            close_val,
            atr_val,
            config.tp_rr,
            config.tsl_atr_mult,
            config.max_bars_in_trade,
        )
        if exit_reason:
            return {
                "signal": "EXIT",
                "reason": exit_reason,
                "proposed_position": None,
            }

        _ = update_trailing(state_with_extreme, high_val, low_val, atr_val, config.tsl_atr_mult)

        return {
            "signal": "HOLD",
            "reason": "position_open",
            "proposed_position": None,
        }

    flip = detect_flip(direction, idx)
    if flip is None:
        return {"signal": "HOLD", "reason": "no_flip", "proposed_position": None}

    if config.volatility_filter_enabled and not atr_above_median(atr, idx, config.volatility_median_window):
        return {"signal": "HOLD", "reason": "volatility_filter", "proposed_position": None}

    entry_price = close_val
    stop_distance = config.risk_atr_mult * atr_val

    if flip == "LONG":
        stop_loss = entry_price - stop_distance
        take_profit = entry_price + stop_distance * config.tp_rr
    else:
        stop_loss = entry_price + stop_distance
        take_profit = entry_price - stop_distance * config.tp_rr

    leverage = compute_leverage(config.leverage, config.leverage_min, config.leverage_max)
    qty, lev = position_size(
        account_equity,
        config.margin_pct,
        entry_price,
        leverage,
        min_qty,
        quantity_step,
    )

    if qty <= 0:
        return {"signal": "HOLD", "reason": "below_min_qty", "proposed_position": None}

    return {
        "signal": flip,
        "reason": "supertrend_flip",
        "proposed_position": {
            "side": flip,
            "quantity": float(qty),
            "leverage": int(lev),
            "entry_price": float(entry_price),
            "stop_loss": float(stop_loss),
            "take_profit": float(take_profit),
        },
    }
