"""
MCP Tools for Mudrex Trading SDK
=================================

Defines all MCP tools that wrap the Mudrex SDK methods.
Each tool maps directly to SDK functionality.
"""

from typing import Any, Dict, TypedDict, Optional, List
from mcp.server.fastmcp import FastMCP
import logging

logger = logging.getLogger(__name__)


# Type definitions for tool return values
class ErrorResponse(TypedDict):
    """Standard error response format."""
    error: str
    error_type: str
    details: Optional[str]


class BalanceResponse(TypedDict):
    """Spot wallet balance response."""
    total: str
    available: str
    rewards: str
    withdrawable: str


class FuturesBalanceResponse(TypedDict):
    """Futures wallet balance response."""
    balance: str
    available_to_transfer: str
    unrealized_pnl: str
    margin_used: str


class TransferResponse(TypedDict):
    """Fund transfer response."""
    success: bool
    amount: str
    from_wallet: str
    to_wallet: str


class MarketResponse(TypedDict):
    """Market specification response."""
    symbol: str
    asset_id: str
    min_quantity: str
    max_quantity: str
    quantity_step: str
    min_leverage: str
    max_leverage: str
    maker_fee: str
    taker_fee: str
    price: str
    price_step: str


class LeverageResponse(TypedDict):
    """Leverage settings response."""
    symbol: str
    leverage: str
    margin_type: str


class OrderResponse(TypedDict):
    """Order response."""
    order_id: str
    symbol: str
    side: str
    quantity: str
    leverage: str
    status: str
    fill_price: Optional[str]


class PositionResponse(TypedDict):
    """Position response."""
    position_id: str
    symbol: str
    side: Optional[str]
    quantity: str
    entry_price: str
    mark_price: str
    leverage: str
    unrealized_pnl: str
    pnl_percentage: str
    margin_used: Optional[str]


class SuccessResponse(TypedDict):
    """Generic success response."""
    success: bool
    message: Optional[str]


def _handle_tool_error(func):
    """
    Decorator to handle exceptions in tool functions gracefully.
    
    Returns clean JSON error messages instead of raising exceptions,
    making it easier for AI to understand and communicate errors.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Import here to avoid circular dependency
            from mudrex.exceptions import (
                MudrexAPIError,
                MudrexAuthenticationError,
                MudrexRateLimitError,
                MudrexValidationError,
            )
            
            # Determine error type and create user-friendly message
            error_type = type(e).__name__
            error_message = str(e)
            
            # Extract helpful details from known error types
            if isinstance(e, MudrexAuthenticationError):
                error_type = "AuthenticationError"
                error_message = "Invalid API credentials. Please check your MUDREX_API_SECRET."
            elif isinstance(e, MudrexRateLimitError):
                error_type = "RateLimitError"
                error_message = f"Rate limit exceeded. {error_message}"
            elif isinstance(e, MudrexValidationError):
                error_type = "ValidationError"
                # Validation errors usually have good messages already
                pass
            elif "insufficient" in error_message.lower():
                error_type = "InsufficientFundsError"
                error_message = "Insufficient funds. Please transfer funds to your futures wallet or reduce order size."
            elif "not found" in error_message.lower():
                error_type = "NotFoundError"
                error_message = f"{error_message}. Use search_markets or list_markets to find valid symbols."
            
            logger.error(f"Tool error in {func.__name__}: {error_type} - {error_message}")
            
            return ErrorResponse(
                error=error_message,
                error_type=error_type,
                details=str(e) if str(e) != error_message else None
            )
    
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def register_tools(mcp: FastMCP, client: Any) -> None:
    """
    Register all Mudrex trading tools with the MCP server.
    
    Args:
        mcp: FastMCP server instance
        client: MudrexClient instance
    """
    
    # ==================
    # Wallet Tools
    # ==================
    
    @mcp.tool()
    @_handle_tool_error
    def get_spot_balance() -> BalanceResponse | ErrorResponse:
        """
        Get spot wallet balance including available funds and rewards.
        
        Returns:
            Dictionary with total, available, rewards, and withdrawable amounts
        """
        balance = client.wallet.get_spot_balance()
        return BalanceResponse(
            total=balance.total,
            available=balance.available,
            rewards=balance.rewards,
            withdrawable=balance.withdrawable,
        )
    
    @mcp.tool()
    @_handle_tool_error
    def get_futures_balance() -> FuturesBalanceResponse | ErrorResponse:
        """
        Get futures wallet balance including unrealized PnL and margin used.
        
        Returns:
            Dictionary with balance, available transfer, unrealized PnL, and margin used
        """
        balance = client.wallet.get_futures_balance()
        return FuturesBalanceResponse(
            balance=balance.balance,
            available_to_transfer=balance.available_to_transfer,
            unrealized_pnl=balance.unrealized_pnl,
            margin_used=balance.margin_used,
        )
    
    @mcp.tool()
    @_handle_tool_error
    def transfer_to_futures(amount: str) -> TransferResponse | ErrorResponse:
        """
        Transfer funds from spot wallet to futures wallet.
        
        Args:
            amount: Amount to transfer (e.g., "100.00")
            
        Returns:
            Transfer confirmation with success status and amount
        """
        result = client.wallet.transfer_to_futures(amount)
        return TransferResponse(
            success=result.success,
            amount=result.amount,
            from_wallet=result.from_wallet_type,
            to_wallet=result.to_wallet_type,
        )
    
    @mcp.tool()
    @_handle_tool_error
    def transfer_to_spot(amount: str) -> TransferResponse | ErrorResponse:
        """
        Transfer funds from futures wallet to spot wallet.
        
        Args:
            amount: Amount to transfer (e.g., "50.00")
            
        Returns:
            Transfer confirmation with success status and amount
        """
        result = client.wallet.transfer_to_spot(amount)
        return TransferResponse(
            success=result.success,
            amount=result.amount,
            from_wallet=result.from_wallet_type,
            to_wallet=result.to_wallet_type,
        )
    
    # ==================
    # Asset Tools
    # ==================
    
    @mcp.tool()
    @_handle_tool_error
    def list_markets() -> List[Dict[str, Any]] | ErrorResponse:
        """
        List ALL tradable futures markets (500+ trading pairs).
        
        Returns:
            List of all available trading pairs with specifications
        """
        assets = client.assets.list_all()
        return [
            {
                "symbol": asset.symbol,
                "asset_id": asset.asset_id,
                "min_quantity": asset.min_quantity,
                "max_quantity": asset.max_quantity,
                "min_leverage": asset.min_leverage,
                "max_leverage": asset.max_leverage,
                "maker_fee": asset.maker_fee,
                "taker_fee": asset.taker_fee,
                "price": asset.price,
            }
            for asset in assets
        ]
    
    @mcp.tool()
    @_handle_tool_error
    def get_market(symbol: str) -> MarketResponse | ErrorResponse:
        """
        Get detailed specifications for a specific trading symbol.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT", "XRPUSDT", "ETHUSDT")
            
        Returns:
            Detailed market specifications including fees, limits, and current price
        """
        asset = client.assets.get(symbol)
        return MarketResponse(
            symbol=asset.symbol,
            asset_id=asset.asset_id,
            min_quantity=asset.min_quantity,
            max_quantity=asset.max_quantity,
            quantity_step=asset.quantity_step,
            min_leverage=asset.min_leverage,
            max_leverage=asset.max_leverage,
            maker_fee=asset.maker_fee,
            taker_fee=asset.taker_fee,
            price=asset.price,
            price_step=asset.price_step,
        )
    
    @mcp.tool()
    @_handle_tool_error
    def search_markets(query: str) -> List[Dict[str, Any]] | ErrorResponse:
        """
        Search for trading symbols by name pattern.
        
        Args:
            query: Search term (e.g., "BTC", "DOGE", "ETH")
            
        Returns:
            List of matching trading symbols
        """
        assets = client.assets.search(query)
        return [
            {
                "symbol": asset.symbol,
                "asset_id": asset.asset_id,
                "price": asset.price,
                "max_leverage": asset.max_leverage,
            }
            for asset in assets
        ]
    
    # ==================
    # Leverage Tools
    # ==================
    
    @mcp.tool()
    @_handle_tool_error
    def get_leverage(symbol: str) -> LeverageResponse | ErrorResponse:
        """
        Get current leverage settings for a trading symbol.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            
        Returns:
            Current leverage and margin type settings
        """
        leverage = client.leverage.get(symbol)
        return LeverageResponse(
            symbol=symbol,
            leverage=leverage.leverage,
            margin_type=leverage.margin_type.value,
        )
    
    @mcp.tool()
    @_handle_tool_error
    def set_leverage(symbol: str, leverage: str, margin_type: str = "ISOLATED") -> LeverageResponse | ErrorResponse:
        """
        Set leverage and margin type for a trading symbol.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            leverage: Desired leverage (e.g., "5", "10", "20")
            margin_type: Margin type - currently only "ISOLATED" supported
            
        Returns:
            Updated leverage settings
        """
        result = client.leverage.set(symbol, leverage, margin_type)
        return LeverageResponse(
            symbol=symbol,
            leverage=result.leverage,
            margin_type=result.margin_type.value,
        )
    
    # ==================
    # Order Tools
    # ==================
    
    @mcp.tool()
    @_handle_tool_error
    def create_market_order(
        symbol: str,
        side: str,
        quantity: str,
        leverage: str = "1",
        stoploss_price: str | None = None,
        takeprofit_price: str | None = None,
    ) -> OrderResponse | ErrorResponse:
        """
        Place a market order that executes immediately at current price.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT", "XRPUSDT")
            side: Order direction - "LONG" or "SHORT"
            quantity: Order quantity (e.g., "0.001" for BTC, "100" for XRP)
            leverage: Leverage to use (default: "1")
            stoploss_price: Optional stop-loss price
            takeprofit_price: Optional take-profit price
            
        Returns:
            Order details including order_id, status, and fill price
        """
        order = client.orders.create_market_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            leverage=leverage,
            stoploss_price=stoploss_price,
            takeprofit_price=takeprofit_price,
        )
        return OrderResponse(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.order_type.value,
            quantity=order.quantity,
            leverage=order.leverage,
            status=order.status,
            fill_price=order.fill_price,
        )
    
    @mcp.tool()
    @_handle_tool_error
    def create_limit_order(
        symbol: str,
        side: str,
        quantity: str,
        price: str,
        leverage: str = "1",
        stoploss_price: str | None = None,
        takeprofit_price: str | None = None,
    ) -> OrderResponse | ErrorResponse:
        """
        Place a limit order that executes when price reaches the specified level.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            side: Order direction - "LONG" or "SHORT"
            quantity: Order quantity
            price: Limit price (order triggers at this price)
            leverage: Leverage to use (default: "1")
            stoploss_price: Optional stop-loss price
            takeprofit_price: Optional take-profit price
            
        Returns:
            Order details including order_id and status
        """
        order = client.orders.create_limit_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            leverage=leverage,
            stoploss_price=stoploss_price,
            takeprofit_price=takeprofit_price,
        )
        return OrderResponse(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.order_type.value,
            quantity=order.quantity,
            leverage=order.leverage,
            status=order.status,
            fill_price=order.fill_price,
        )
    
    @mcp.tool()
    @_handle_tool_error
    def list_open_orders() -> List[Dict[str, Any]] | ErrorResponse:
        """
        Get all open (unfilled) orders.
        
        Returns:
            List of open orders with details
        """
        orders = client.orders.list_open()
        return [
            {
                "order_id": order.order_id,
                "symbol": order.symbol,
                "side": order.order_type.value,
                "quantity": order.quantity,
                "price": order.order_price,
                "status": order.status,
                "trigger_type": order.trigger_type.value if order.trigger_type else None,
            }
            for order in orders
        ]
    
    @mcp.tool()
    @_handle_tool_error
    def get_order(order_id: str) -> OrderResponse | ErrorResponse:
        """
        Get details of a specific order.
        
        Args:
            order_id: The order ID to retrieve
            
        Returns:
            Order details
        """
        order = client.orders.get(order_id)
        return OrderResponse(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.order_type.value,
            quantity=order.quantity,
            leverage=order.leverage,
            status=order.status,
            fill_price=order.fill_price,
        )
    
    @mcp.tool()
    @_handle_tool_error
    def cancel_order(order_id: str) -> Dict[str, Any] | ErrorResponse:
        """
        Cancel an open order.
        
        Args:
            order_id: The order ID to cancel
            
        Returns:
            Cancellation confirmation
        """
        success = client.orders.cancel(order_id)
        return {
            "success": success,
            "order_id": order_id,
        }
    
    # ==================
    # Position Tools
    # ==================
    
    @mcp.tool()
    @_handle_tool_error
    def list_open_positions() -> List[PositionResponse] | ErrorResponse:
        """
        Get all open positions with live PnL data from the exchange.
        
        Returns:
            List of open positions with current prices and unrealized PnL
        """
        positions = client.positions.list_open()
        return [
            PositionResponse(
                position_id=pos.position_id,
                symbol=pos.symbol,
                side=pos.side.value if pos.side else None,
                quantity=pos.quantity,
                entry_price=pos.entry_price,
                mark_price=pos.mark_price,
                leverage=pos.leverage,
                unrealized_pnl=pos.unrealized_pnl,
                pnl_percentage=pos.pnl_percentage,
                margin_used=pos.margin_used,
            )
            for pos in positions
        ]
    
    @mcp.tool()
    @_handle_tool_error
    def get_position(position_id: str) -> PositionResponse | ErrorResponse:
        """
        Get details of a specific position.
        
        Args:
            position_id: The position ID to retrieve
            
        Returns:
            Position details with current PnL
        """
        pos = client.positions.get(position_id)
        return PositionResponse(
            position_id=pos.position_id,
            symbol=pos.symbol,
            side=pos.side.value if pos.side else None,
            quantity=pos.quantity,
            entry_price=pos.entry_price,
            mark_price=pos.mark_price,
            leverage=pos.leverage,
            unrealized_pnl=pos.unrealized_pnl,
            pnl_percentage=pos.pnl_percentage,
            margin_used=pos.margin_used,
        )
    
    @mcp.tool()
    @_handle_tool_error
    def close_position(position_id: str) -> Dict[str, Any] | ErrorResponse:
        """
        Fully close a position.
        
        Args:
            position_id: The position ID to close
            
        Returns:
            Closure confirmation
        """
        success = client.positions.close(position_id)
        return {
            "success": success,
            "position_id": position_id,
        }
    
    @mcp.tool()
    @_handle_tool_error
    def set_position_stoploss(position_id: str, price: str) -> Dict[str, Any] | ErrorResponse:
        """
        Set stop-loss for a position.
        
        Args:
            position_id: The position ID
            price: Stop-loss price
            
        Returns:
            Confirmation of stop-loss update
        """
        success = client.positions.set_stoploss(position_id, price)
        return {
            "success": success,
            "position_id": position_id,
            "stoploss_price": price,
        }
    
    @mcp.tool()
    @_handle_tool_error
    def set_position_takeprofit(position_id: str, price: str) -> Dict[str, Any] | ErrorResponse:
        """
        Set take-profit for a position.
        
        Args:
            position_id: The position ID
            price: Take-profit price
            
        Returns:
            Confirmation of take-profit update
        """
        success = client.positions.set_takeprofit(position_id, price)
        return {
            "success": success,
            "position_id": position_id,
            "takeprofit_price": price,
        }
    
    @mcp.tool()
    @_handle_tool_error
    def set_position_risk_levels(
        position_id: str,
        stoploss_price: str | None = None,
        takeprofit_price: str | None = None,
    ) -> Dict[str, Any] | ErrorResponse:
        """
        Set both stop-loss and take-profit for a position.
        
        Args:
            position_id: The position ID
            stoploss_price: Stop-loss price (optional)
            takeprofit_price: Take-profit price (optional)
            
        Returns:
            Confirmation of risk level updates
        """
        success = client.positions.set_risk_order(
            position_id,
            stoploss_price=stoploss_price,
            takeprofit_price=takeprofit_price,
        )
        return {
            "success": success,
            "position_id": position_id,
            "stoploss_price": stoploss_price,
            "takeprofit_price": takeprofit_price,
        }
