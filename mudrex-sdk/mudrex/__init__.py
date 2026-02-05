"""
Mudrex Trading SDK
==================

A Python SDK for the Mudrex Futures Trading API.

This library provides a simple, intuitive interface for:
- Wallet management (spot & futures)
- Asset discovery and leverage management
- Order placement and management
- Position tracking and risk management
- Fee history retrieval

Quick Start:
    >>> from mudrex import MudrexClient
    >>> 
    >>> # Initialize client
    >>> client = MudrexClient(api_secret="your-api-secret")
    >>> 
    >>> # Check balance
    >>> balance = client.wallet.get_spot_balance()
    >>> print(f"Available: ${balance.available}")
    >>> 
    >>> # List ALL tradable assets (500+)
    >>> assets = client.assets.list_all()
    >>> print(f"Found {len(assets)} tradable assets")
    >>> 
    >>> # Get current price
    >>> price = client.assets.get_price("BTCUSDT")
    >>> print(f"BTC: ${price}")
    >>> 
    >>> # Place an order (use symbol directly!)
    >>> order = client.orders.create_market_order(
    ...     symbol="BTCUSDT",
    ...     side="LONG",
    ...     quantity="0.001",
    ...     leverage="10"
    ... )

For more information, visit: https://docs.trade.mudrex.com
"""

from mudrex.client import MudrexClient
from mudrex.exceptions import (
    MudrexAPIError,
    MudrexAuthenticationError,
    MudrexRateLimitError,
    MudrexValidationError,
    MudrexNotFoundError,
    MudrexInsufficientBalanceError,
    MudrexOrderError,
    MudrexPositionError,
    MudrexServerError,
)
from mudrex.models import (
    Order,
    OrderType,
    OrderStatus,
    Position,
    PositionStatus,
    TriggerType,
    MarginType,
    WalletBalance,
    FuturesBalance,
    Asset,
    Leverage,
    Ticker,
    FeeRecord,
)

__version__ = "1.2.0"
__author__ = "Mudrex SDK Contributors"
__all__ = [
    # Client
    "MudrexClient",
    # Exceptions (human-readable errors)
    "MudrexAPIError",
    "MudrexAuthenticationError",
    "MudrexRateLimitError",
    "MudrexValidationError",
    "MudrexNotFoundError",
    "MudrexInsufficientBalanceError",
    "MudrexOrderError",
    "MudrexPositionError",
    "MudrexServerError",
    # Models
    "Order",
    "OrderType",
    "OrderStatus",
    "Position",
    "PositionStatus",
    "TriggerType",
    "MarginType",
    "WalletBalance",
    "FuturesBalance",
    "Asset",
    "Leverage",
    "Ticker",
    "FeeRecord",
]
