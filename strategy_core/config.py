"""Strategy configuration."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StrategyConfig:
    """Strategy parameters. Immutable for deterministic behavior."""

    # Supertrend
    atr_period: int = 10
    supertrend_factor: float = 3.0

    # Risk
    risk_atr_mult: float = 2.0
    tsl_atr_mult: float = 2.0
    tp_rr: float = 2.0  # Risk:Reward 1:2
    margin_pct: float = 0.02
    leverage_min: int = 5
    leverage_max: int = 20
    leverage: int = 5  # Base leverage (clamped to min/max)

    # Exits
    max_bars_in_trade: int = 24  # Time stop (e.g., 24 candles on 1H = 24h)

    # Volatility filter (optional)
    volatility_filter_enabled: bool = False
    volatility_median_window: int = 20
