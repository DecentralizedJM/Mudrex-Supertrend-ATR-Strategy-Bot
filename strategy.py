"""
Supertrend TSL Strategy
=======================

Supertrend + Single TP + Smart Trailing Stop Loss Strategy.
Based on the original implementation with enhancements for Mudrex integration.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any
from enum import Enum


class Signal(Enum):
    """Trading signal types."""
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"


@dataclass
class StrategyResult:
    """Result from strategy signal generation."""
    signal: Signal
    entry_price: float
    stop_loss: float
    take_profit: float
    atr: float
    supertrend: float
    direction: int  # 1 for bullish, -1 for bearish
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal": self.signal.value,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "atr": self.atr,
            "supertrend": self.supertrend,
            "direction": self.direction,
        }


class SupertrendTSLStrategy:
    """
    Supertrend + Single TP + Smart TSL Strategy.
    
    This strategy combines:
    - Supertrend indicator for trend direction and entry signals
    - ATR-based stop loss for risk management
    - Single take profit target based on Risk:Reward ratio
    - Smart trailing stop loss that follows price
    
    Parameters:
    -----------
    atr_period : int
        Period for Supertrend ATR calculation (default: 10)
    factor : float
        Supertrend multiplier factor (default: 3.0)
    risk_atr_len : int
        ATR period for risk calculation (default: 14)
    risk_atr_mult : float
        ATR multiplier for stop loss (default: 2.0)
    tsl_atr_len : int
        ATR period for trailing stop (default: 14)
    tsl_mult : float
        ATR multiplier for trailing stop (default: 2.0)
    tp_rr : float
        Take profit Risk:Reward ratio (default: 2.0)
    position_size_pct : float
        Position size as percentage of balance (default: 0.15)
    """
    
    def __init__(
        self,
        atr_period: int = 10,
        factor: float = 3.0,
        risk_atr_len: int = 14,
        risk_atr_mult: float = 2.0,
        tsl_atr_len: int = 14,
        tsl_mult: float = 2.0,
        tp_rr: float = 2.0,
        position_size_pct: float = 0.15,
    ):
        self.atr_period = atr_period
        self.factor = factor
        self.risk_atr_len = risk_atr_len
        self.risk_atr_mult = risk_atr_mult
        self.tsl_atr_len = tsl_atr_len
        self.tsl_mult = tsl_mult
        self.tp_rr = tp_rr
        self.position_size_pct = position_size_pct
    
    def calculate_atr(self, df: pd.DataFrame, period: int) -> pd.Series:
        """
        Calculate Average True Range.
        
        Parameters:
        -----------
        df : pd.DataFrame
            OHLCV dataframe with 'high', 'low', 'close' columns
        period : int
            ATR period
            
        Returns:
        --------
        pd.Series
            ATR values
        """
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def calculate_supertrend(
        self, 
        df: pd.DataFrame, 
        atr_period: int, 
        factor: float
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Supertrend indicator.
        
        Parameters:
        -----------
        df : pd.DataFrame
            OHLCV dataframe
        atr_period : int
            ATR period
        factor : float
            Supertrend multiplier
            
        Returns:
        --------
        Tuple[pd.Series, pd.Series]
            (supertrend values, direction: 1 for bullish, -1 for bearish)
        """
        atr = self.calculate_atr(df, atr_period)
        hl_avg = (df['high'] + df['low']) / 2
        
        # Upper and lower bands
        upper_band = hl_avg + (factor * atr)
        lower_band = hl_avg - (factor * atr)
        
        # Make copies to avoid SettingWithCopyWarning
        upper_band = upper_band.copy()
        lower_band = lower_band.copy()
        
        # Initialize
        supertrend = pd.Series(index=df.index, dtype=float)
        direction = pd.Series(index=df.index, dtype=float)
        
        for i in range(1, len(df)):
            # Adjust bands
            if df['close'].iloc[i-1] <= upper_band.iloc[i-1]:
                upper_band.iloc[i] = min(upper_band.iloc[i], upper_band.iloc[i-1])
            
            if df['close'].iloc[i-1] >= lower_band.iloc[i-1]:
                lower_band.iloc[i] = max(lower_band.iloc[i], lower_band.iloc[i-1])
            
            # Determine direction
            if i == 1:
                direction.iloc[i] = 1
            elif supertrend.iloc[i-1] == upper_band.iloc[i-1]:
                direction.iloc[i] = -1 if df['close'].iloc[i] > upper_band.iloc[i] else 1
            else:
                direction.iloc[i] = 1 if df['close'].iloc[i] < lower_band.iloc[i] else -1
            
            # Set supertrend value
            supertrend.iloc[i] = lower_band.iloc[i] if direction.iloc[i] > 0 else upper_band.iloc[i]
        
        return supertrend, direction
    
    def get_current_signal(self, df: pd.DataFrame) -> Signal:
        """
        Get the current trading signal based on Supertrend direction change.
        
        Parameters:
        -----------
        df : pd.DataFrame
            OHLCV dataframe
            
        Returns:
        --------
        Signal
            LONG, SHORT, or NEUTRAL
        """
        _, direction = self.calculate_supertrend(df, self.atr_period, self.factor)
        
        if len(direction) < 2:
            return Signal.NEUTRAL
        
        # Check if there was a direction change in the last bar
        direction_change = direction.iloc[-1] - direction.iloc[-2]
        
        if direction_change < 0:
            return Signal.LONG
        elif direction_change > 0:
            return Signal.SHORT
        else:
            return Signal.NEUTRAL
    
    def calculate_risk_levels(
        self, 
        df: pd.DataFrame, 
        signal: Signal
    ) -> Tuple[float, float, float]:
        """
        Calculate stop loss and take profit levels.
        
        Parameters:
        -----------
        df : pd.DataFrame
            OHLCV dataframe
        signal : Signal
            Trading signal (LONG or SHORT)
            
        Returns:
        --------
        Tuple[float, float, float]
            (entry_price, stop_loss, take_profit)
        """
        entry_price = df['close'].iloc[-1]
        risk_atr = self.calculate_atr(df, self.risk_atr_len).iloc[-1]
        
        if signal == Signal.LONG:
            stop_loss = entry_price - (risk_atr * self.risk_atr_mult)
            risk = entry_price - stop_loss
            take_profit = entry_price + (risk * self.tp_rr)
        elif signal == Signal.SHORT:
            stop_loss = entry_price + (risk_atr * self.risk_atr_mult)
            risk = stop_loss - entry_price
            take_profit = entry_price - (risk * self.tp_rr)
        else:
            stop_loss = entry_price
            take_profit = entry_price
        
        return entry_price, stop_loss, take_profit
    
    def calculate_trailing_stop(
        self, 
        df: pd.DataFrame, 
        position_side: Signal,
        current_stop: float,
        highest_price: float,
        lowest_price: float,
    ) -> float:
        """
        Calculate updated trailing stop loss level.
        
        Parameters:
        -----------
        df : pd.DataFrame
            OHLCV dataframe
        position_side : Signal
            LONG or SHORT
        current_stop : float
            Current stop loss level
        highest_price : float
            Highest price since entry (for LONG)
        lowest_price : float
            Lowest price since entry (for SHORT)
            
        Returns:
        --------
        float
            New trailing stop loss level
        """
        tsl_atr = self.calculate_atr(df, self.tsl_atr_len).iloc[-1]
        
        if position_side == Signal.LONG:
            new_stop = highest_price - (tsl_atr * self.tsl_mult)
            return max(current_stop, new_stop)  # Only move up
        elif position_side == Signal.SHORT:
            new_stop = lowest_price + (tsl_atr * self.tsl_mult)
            return min(current_stop, new_stop)  # Only move down
        else:
            return current_stop
    
    def generate_signal(self, df: pd.DataFrame) -> StrategyResult:
        """
        Generate a complete trading signal with all parameters.
        
        Parameters:
        -----------
        df : pd.DataFrame
            OHLCV dataframe with 'open', 'high', 'low', 'close', 'volume' columns
            
        Returns:
        --------
        StrategyResult
            Complete signal with entry, SL, TP, and indicator values
        """
        signal = self.get_current_signal(df)
        entry_price, stop_loss, take_profit = self.calculate_risk_levels(df, signal)
        
        supertrend, direction = self.calculate_supertrend(df, self.atr_period, self.factor)
        atr = self.calculate_atr(df, self.risk_atr_len).iloc[-1]
        
        return StrategyResult(
            signal=signal,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            atr=atr,
            supertrend=supertrend.iloc[-1],
            direction=int(direction.iloc[-1]) if not pd.isna(direction.iloc[-1]) else 0,
        )
    
    def calculate_position_size(
        self, 
        balance: float, 
        entry_price: float, 
        stop_loss: float,
        leverage: int = 1,
    ) -> float:
        """
        Calculate position size based on risk parameters.
        
        Parameters:
        -----------
        balance : float
            Available balance
        entry_price : float
            Entry price
        stop_loss : float
            Stop loss price
        leverage : int
            Leverage to use
            
        Returns:
        --------
        float
            Position size in base currency
        """
        risk_amount = balance * self.position_size_pct
        risk_per_unit = abs(entry_price - stop_loss)
        
        if risk_per_unit == 0:
            return 0
        
        # Position size = Risk Amount / Risk per unit
        position_size = risk_amount / risk_per_unit
        
        # Adjust for leverage (we can trade larger with leverage)
        position_size = position_size * leverage
        
        return position_size
    
    def backtest(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Run backtest on OHLC data.
        
        Parameters:
        -----------
        df : pd.DataFrame
            OHLCV dataframe
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with signals and position tracking
        """
        df = df.copy()
        
        # Calculate Supertrend
        supertrend, direction = self.calculate_supertrend(df, self.atr_period, self.factor)
        
        # Calculate ATR values
        risk_atr = self.calculate_atr(df, self.risk_atr_len)
        tsl_atr = self.calculate_atr(df, self.tsl_atr_len)
        
        # Add to dataframe
        df['supertrend'] = supertrend
        df['direction'] = direction
        df['risk_atr'] = risk_atr
        df['tsl_atr'] = tsl_atr
        
        # Generate signals
        df['direction_change'] = direction.diff()
        df['signal'] = 'NEUTRAL'
        df.loc[df['direction_change'] < 0, 'signal'] = 'LONG'
        df.loc[df['direction_change'] > 0, 'signal'] = 'SHORT'
        
        return df
