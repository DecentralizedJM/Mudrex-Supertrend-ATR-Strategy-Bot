"""
Configuration Module
====================

Central configuration for the Supertrend TSL Strategy + Mudrex integration.
Supports environment variables, .env files, and AWS Secrets Manager.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional
import json


@dataclass
class StrategyConfig:
    """Supertrend TSL Strategy parameters."""
    
    # Supertrend parameters
    atr_period: int = 10
    factor: float = 3.0
    
    # Risk ATR parameters
    risk_atr_len: int = 14
    risk_atr_mult: float = 2.0
    
    # Trailing Stop Loss parameters
    tsl_atr_len: int = 14
    tsl_mult: float = 2.0
    
    # Take Profit (Risk:Reward ratio)
    tp_rr: float = 2.0
    
    # Position sizing (as percentage of available balance)
    position_size_pct: float = 0.15
    
    @classmethod
    def from_env(cls) -> "StrategyConfig":
        """Load strategy config from environment variables."""
        return cls(
            atr_period=int(os.getenv("STRATEGY_ATR_PERIOD", "10")),
            factor=float(os.getenv("STRATEGY_FACTOR", "3.0")),
            risk_atr_len=int(os.getenv("STRATEGY_RISK_ATR_LEN", "14")),
            risk_atr_mult=float(os.getenv("STRATEGY_RISK_ATR_MULT", "2.0")),
            tsl_atr_len=int(os.getenv("STRATEGY_TSL_ATR_LEN", "14")),
            tsl_mult=float(os.getenv("STRATEGY_TSL_MULT", "2.0")),
            tp_rr=float(os.getenv("STRATEGY_TP_RR", "2.0")),
            position_size_pct=float(os.getenv("STRATEGY_POSITION_SIZE_PCT", "0.15")),
        )


@dataclass
class TradingConfig:
    """Trading-specific configuration."""
    
    # Symbols to trade
    symbols: List[str] = field(default_factory=lambda: ["BTCUSDT", "ETHUSDT"])
    
    # Default leverage
    leverage: str = "5"
    
    # Margin type (ISOLATED recommended)
    margin_type: str = "ISOLATED"
    
    # Timeframe for OHLCV data
    timeframe: str = "5m"
    
    # Number of candles to fetch for strategy calculation
    lookback_periods: int = 100
    
    # Minimum balance required to trade (USDT)
    min_balance: float = 10.0
    
    # Maximum positions allowed at once
    max_positions: int = 3
    
    # Dry run mode (no real trades)
    dry_run: bool = False
    
    @classmethod
    def from_env(cls) -> "TradingConfig":
        """Load trading config from environment variables."""
        symbols_str = os.getenv("TRADING_SYMBOLS", "BTCUSDT,ETHUSDT")
        symbols = [s.strip() for s in symbols_str.split(",") if s.strip()]
        
        return cls(
            symbols=symbols,
            leverage=os.getenv("TRADING_LEVERAGE", "5"),
            margin_type=os.getenv("TRADING_MARGIN_TYPE", "ISOLATED"),
            timeframe=os.getenv("TRADING_TIMEFRAME", "5m"),
            lookback_periods=int(os.getenv("TRADING_LOOKBACK_PERIODS", "100")),
            min_balance=float(os.getenv("TRADING_MIN_BALANCE", "10.0")),
            max_positions=int(os.getenv("TRADING_MAX_POSITIONS", "3")),
            dry_run=os.getenv("TRADING_DRY_RUN", "false").lower() == "true",
        )


@dataclass
class Config:
    """Main configuration container."""
    
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    trading: TradingConfig = field(default_factory=TradingConfig)
    mudrex: MudrexConfig = field(default_factory=MudrexConfig)
    ccxt: CCXTConfig = field(default_factory=CCXTConfig)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load all configuration from environment variables."""
        # Try to load .env file if python-dotenv is available
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        return cls(
            strategy=StrategyConfig.from_env(),
            trading=TradingConfig.from_env(),
            mudrex=MudrexConfig.from_env(),
            ccxt=CCXTConfig.from_env(),
        )
    
    def validate(self) -> bool:
        """Validate all configuration."""
        self.mudrex.validate()
        
        if not self.trading.symbols:
            raise ValueError("At least one trading symbol is required")
        
        if self.strategy.position_size_pct <= 0 or self.strategy.position_size_pct > 1:
            raise ValueError("position_size_pct must be between 0 and 1")
        
        return True
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "strategy": {
                "atr_period": self.strategy.atr_period,
                "factor": self.strategy.factor,
                "risk_atr_len": self.strategy.risk_atr_len,
                "risk_atr_mult": self.strategy.risk_atr_mult,
                "tsl_atr_len": self.strategy.tsl_atr_len,
                "tsl_mult": self.strategy.tsl_mult,
                "tp_rr": self.strategy.tp_rr,
                "position_size_pct": self.strategy.position_size_pct,
            },
            "trading": {
                "symbols": self.trading.symbols,
                "leverage": self.trading.leverage,
                "margin_type": self.trading.margin_type,
                "timeframe": self.trading.timeframe,
                "lookback_periods": self.trading.lookback_periods,
                "min_balance": self.trading.min_balance,
                "max_positions": self.trading.max_positions,
                "dry_run": self.trading.dry_run,
            },
        }


# Global config instance (lazy-loaded)
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def reload_config() -> Config:
    """Reload configuration from environment."""
    global _config
    _config = Config.from_env()
    return _config
