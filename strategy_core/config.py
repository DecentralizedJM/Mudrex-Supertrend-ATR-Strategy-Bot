"""Strategy configuration."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StrategyConfig:
    """Strategy parameters. Immutable for deterministic behavior."""

    # Supertrend (higher factor = fewer false flips, higher-quality signals)
    atr_period: int = 10
    supertrend_factor: float = 4.0  # 4.0 reduces whipsaw vs 3.5

    # Risk — wider SL avoids noise stops; realistic TP improves win rate
    risk_atr_mult: float = 2.5   # 2.5x ATR gives breathing room in crypto volatility
    tsl_atr_mult: float = 2.5    # Looser trail = fewer premature exits
    tp_rr: float = 2.0           # 1:2 R:R is achievable; 2.5R was often missed
    margin_pct: float = 0.02
    leverage_min: int = 5
    leverage_max: int = 20
    leverage: int = 5  # Base leverage (clamped to min/max)

    # Exits — longer hold lets trends develop
    max_bars_in_trade: int = 96  # 96 candles (e.g. 24h on 15m) for trend-following

    # Smart time exit: only time-exit trades that are "flat" (not in meaningful profit).
    # Trades with unrealised PnL > time_exit_flat_r (in R-multiples) keep running.
    # E.g. 0.5 means: if trade is > +0.5R in profit, don't time-exit; let TSL handle it.
    time_exit_flat_r: float = 0.5

    # Volatility filter: only trade when ATR > median (avoids chop)
    volatility_filter_enabled: bool = True
    volatility_median_window: int = 20

    # Flip confirmation: require close beyond supertrend by min ATR% (reduces marginal crosses)
    flip_confirm_atr_pct: float = 0.15  # 15% of ATR buffer beyond supertrend to confirm
