"""
Supertrend + ATR Risk-Managed Strategy Core
===========================================

Pure strategy logic for Mudrex Futures.
No order placement, no Mudrex calls, no websockets.
Returns structured outputs for execution engine consumption.
"""

from strategy_core.config import StrategyConfig
from strategy_core.state import TradeState
from strategy_core.engine import process_candle, StrategyOutput
from strategy_core.signals import update_trailing

__all__ = [
    "StrategyConfig",
    "TradeState",
    "process_candle",
    "StrategyOutput",
    "update_trailing",
]
