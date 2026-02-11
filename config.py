"""
Configuration Module
====================

Central configuration for the Supertrend TSL Strategy + Mudrex integration.
Optimized for Railway: Only MUDREX_API_SECRET is required from environment.
All strategy parameters are hardcoded as per requirements.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class StrategyConfig:
    """Hardcoded Strategy Parameters. Tuned for better win rate / quality / ROI."""

    # Supertrend (higher factor = fewer false flips, higher-quality signals)
    atr_period: int = 10
    factor: float = 4.0  # 4.0 reduces whipsaw vs 3.5

    # Risk (same ATR period for Supertrend and risk)
    risk_atr_len: int = 10  # Same as atr_period
    tsl_atr_len: int = 10   # Same as atr_period
    risk_atr_mult: float = 2.5   # Wider SL = fewer noise stops
    tsl_mult: float = 2.5        # Looser trail = fewer premature exits
    tp_rr: float = 2.0           # 1:2 R:R more achievable than 2.5

    # Position sizing: 2% margin, leverage 5x-20x (asset max may be lower)
    margin_pct: float = 0.02
    leverage_min: int = 5
    leverage_max: int = 20
    leverage: int = 5

    # Exits — longer hold for trend-following
    max_bars_in_trade: int = 48

    # Volatility filter: only take flips when ATR > median (avoids low-vol chop)
    volatility_filter_enabled: bool = True
    volatility_median_window: int = 20

    # Flip confirmation buffer (% of ATR beyond supertrend)
    flip_confirm_atr_pct: float = 0.15


@dataclass
class TradingConfig:
    """Trading-specific configuration."""
    
    # Set to empty list to automatically fetch ALL tradable assets from Mudrex
    symbols: List[str] = field(default_factory=list)
    
    # Default leverage (clamped to leverage_min/max at execution)
    leverage: str = "5"
    leverage_min: int = 5
    leverage_max: int = 20

    # Margin per entry as percent of balance (1-100). Default 2%
    # Set via env MARGIN_PERCENT (e.g. 2 for 2%, 5 for 5%)
    margin_percent: int = 2

    # Margin type
    margin_type: str = "ISOLATED"
    
    # Timeframe - Bybit interval: '1', '5', '15', '60', 'D'. Set via env TIMEFRAME. Default 15m.
    timeframe: str = "15"
    
    # Number of candles to fetch/maintain
    lookback_periods: int = 200
    
    # Minimum balance required to trade (USDT)
    min_balance: float = 10.0

    # Min order value (notional = quantity x price) in USDT. Mudrex ~$7-8. Set via MIN_ORDER_VALUE.
    min_order_value: float = 7.0

    # Delay (seconds) between order API calls. Hardcoded 4s for safe rate limits; env ORDER_DELAY_SECONDS overrides.
    order_delay_seconds: float = 4.0
    
    # Maximum concurrent positions (no cap = 999)
    max_positions: int = 999

    # Dry run mode
    dry_run: bool = False


@dataclass
class TelegramConfig:
    """Telegram notifications configuration. Supports multiple chat IDs (comma-separated)."""

    bot_token: str = ""
    chat_ids: List[str] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> "TelegramConfig":
        raw = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        chat_ids = [c.strip() for c in raw.split(",") if c.strip()]
        return cls(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
            chat_ids=chat_ids,
        )


@dataclass
class MudrexConfig:
    """Mudrex API configuration."""
    
    # API Secret (Loaded from environment)
    api_secret: str = ""
    
    # Default settings
    base_url: Optional[str] = None
    timeout: int = 30
    rate_limit: bool = True
    # No retry on 429 — avoid hammering; we retry after cooldown
    max_retries: int = 0
    # When we get 429, wait this long then try one request again. Env: MUDREX_RATE_LIMIT_COOLDOWN_HOURS (default 1 = try every hour)
    rate_limit_cooldown_seconds: float = 3600.0  # 1 hour

    @classmethod
    def from_env(cls) -> "MudrexConfig":
        """Load API secret and rate-limit cooldown from environment."""
        cooldown_hours = 1.0  # try every hour by default
        try:
            raw = os.getenv("MUDREX_RATE_LIMIT_COOLDOWN_HOURS", "").strip()
            if raw:
                cooldown_hours = max(0.5, min(168.0, float(raw)))
        except ValueError:
            pass
        return cls(
            api_secret=os.getenv("MUDREX_API_SECRET", ""),
            rate_limit_cooldown_seconds=cooldown_hours * 3600.0,
        )
    
    def validate(self) -> bool:
        if not self.api_secret:
            raise ValueError("MUDREX_API_SECRET environment variable is missing")
        return True


@dataclass
class Config:
    """Main configuration container."""

    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    trading: TradingConfig = field(default_factory=TradingConfig)
    mudrex: MudrexConfig = field(default_factory=MudrexConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig.from_env)

    @classmethod
    def from_env(cls) -> "Config":
        """Load minimal config from environment."""
        dry_run = os.getenv("TRADING_DRY_RUN", "false").lower() == "true"
        raw = os.getenv("MARGIN_PERCENT", "2").strip()
        try:
            margin_percent = max(1, min(100, int(raw)))
        except ValueError:
            margin_percent = 2

        config = cls(
            mudrex=MudrexConfig.from_env(),
            telegram=TelegramConfig.from_env(),
        )
        config.trading.dry_run = dry_run
        config.trading.margin_percent = margin_percent
        config.trading.leverage_min = config.strategy.leverage_min
        config.trading.leverage_max = config.strategy.leverage_max
        try:
            config.trading.min_order_value = max(1.0, float(os.getenv("MIN_ORDER_VALUE", "7").strip()))
        except ValueError:
            config.trading.min_order_value = 7.0
        try:
            config.trading.order_delay_seconds = max(0.5, float(os.getenv("ORDER_DELAY_SECONDS", "4").strip()))
        except ValueError:
            config.trading.order_delay_seconds = 0.5
        tf = os.getenv("TIMEFRAME", "").strip()
        if tf:
            config.trading.timeframe = tf
        try:
            config.trading.max_positions = max(1, int(os.getenv("MAX_POSITIONS", "999").strip()))
        except ValueError:
            config.trading.max_positions = 999
        config.strategy.margin_pct = margin_percent / 100.0
        return config
    
    def validate(self) -> bool:
        self.mudrex.validate()
        return True
    
    def to_dict(self) -> dict:
        return {
            "strategy": {
                "atr_period": self.strategy.atr_period,
                "factor": self.strategy.factor,
                "tp_rr": self.strategy.tp_rr,
                "margin_pct": self.strategy.margin_pct,
                "leverage_min": self.strategy.leverage_min,
                "leverage_max": self.strategy.leverage_max,
            },
            "trading": {
                "leverage": self.trading.leverage,
                "margin_percent": self.trading.margin_percent,
                "dry_run": self.trading.dry_run,
                "all_symbols": True if not self.trading.symbols else False
            }
        }


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config
