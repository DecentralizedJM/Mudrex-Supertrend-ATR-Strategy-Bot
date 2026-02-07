"""Trade state and transitions."""

from dataclasses import dataclass
from typing import Literal

PositionSide = Literal["FLAT", "LONG", "SHORT"]


@dataclass
class TradeState:
    """Trade state. Updated deterministically per candle."""

    position_side: PositionSide
    entry_price: float
    stop_loss: float  # Current effective stop (initial or trailing)
    take_profit: float
    trailing_stop: float | None  # Active TSL level; None if not yet activated
    bars_in_trade: int
    extreme_price: float  # Highest (LONG) or lowest (SHORT) since entry
    initial_stop_loss: float = 0.0  # For 1R activation (stop_distance = abs(entry - initial))

    @staticmethod
    def flat() -> "TradeState":
        return TradeState(
            position_side="FLAT",
            entry_price=0.0,
            stop_loss=0.0,
            take_profit=0.0,
            trailing_stop=None,
            bars_in_trade=0,
            extreme_price=0.0,
        )
