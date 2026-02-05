"""
Orders API Module
=================

Endpoints for creating, managing, and tracking futures orders.

Supports both symbol-based trading (recommended) and asset_id for backward compatibility.
Use symbols like "BTCUSDT", "XRPUSDT", "ETHUSDT" directly.
"""

from typing import TYPE_CHECKING, Optional, List, Union

from mudrex.api.base import BaseAPI
from mudrex.models import Order, OrderRequest, OrderType, TriggerType, PaginatedResponse

if TYPE_CHECKING:
    from mudrex.client import MudrexClient


class OrdersAPI(BaseAPI):
    """
    Order management endpoints.
    
    Use these methods to:
    - Place market and limit orders using trading symbols
    - View open orders
    - Get order details and history
    - Cancel or amend existing orders
    
    All methods accept trading symbols like "BTCUSDT", "XRPUSDT", "ETHUSDT".
    For backward compatibility, asset_id is also supported.
    
    Example:
        >>> client = MudrexClient(api_secret="...")
        >>> 
        >>> # Place a market order (uses symbol directly!)
        >>> order = client.orders.create_market_order(
        ...     symbol="XRPUSDT",  # Trading symbol (recommended)
        ...     side="LONG",
        ...     quantity="100",
        ...     leverage="5"
        ... )
        >>> print(f"Order placed: {order.order_id}")
        >>> 
        >>> # Also works with asset_id for backward compatibility
        >>> order = client.orders.create_market_order(
        ...     asset_id="01903a7b-...",  # Legacy asset ID
        ...     side="LONG",
        ...     quantity="0.001",
        ...     leverage="10"
        ... )
    """
    
    def create_market_order(
        self,
        symbol: Optional[str] = None,
        side: Union[str, OrderType] = None,
        quantity: str = None,
        leverage: str = "1",
        stoploss_price: Optional[str] = None,
        takeprofit_price: Optional[str] = None,
        reduce_only: bool = False,
        # Backward compatibility - asset_id still works
        asset_id: Optional[str] = None,
    ) -> Order:
        """
        Place a market order (executes immediately at current price).
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT", "XRPUSDT") - RECOMMENDED
            side: Order direction - "LONG" or "SHORT"
            quantity: Order quantity (as string for precision)
            leverage: Leverage to use (default: "1")
            stoploss_price: Optional stop-loss price
            takeprofit_price: Optional take-profit price
            reduce_only: If True, only reduces existing position
            asset_id: Legacy asset ID (use symbol instead) - for backward compatibility
            
        Returns:
            Order: Created order details
            
        Example:
            >>> # Recommended: Use symbol
            >>> order = client.orders.create_market_order(
            ...     symbol="BTCUSDT",
            ...     side="LONG",
            ...     quantity="0.001",
            ...     leverage="10"
            ... )
            >>> 
            >>> # With stop-loss and take-profit
            >>> order = client.orders.create_market_order(
            ...     symbol="XRPUSDT",
            ...     side="LONG",
            ...     quantity="100",
            ...     leverage="5",
            ...     stoploss_price="2.00",
            ...     takeprofit_price="3.00"
            ... )
        """
        # Resolve symbol vs asset_id (symbol takes priority)
        identifier, use_symbol = self._resolve_identifier(symbol, asset_id)
        
        return self._create_order(
            identifier=identifier,
            use_symbol=use_symbol,
            side=side,
            quantity=quantity,
            trigger_type=TriggerType.MARKET,
            leverage=leverage,
            stoploss_price=stoploss_price,
            takeprofit_price=takeprofit_price,
            reduce_only=reduce_only,
        )
    
    def create_market_order_with_amount(
        self,
        symbol: Optional[str] = None,
        side: Union[str, OrderType] = None,
        amount: str = None,
        leverage: str = "1",
        stoploss_price: Optional[str] = None,
        takeprofit_price: Optional[str] = None,
        reduce_only: bool = False,
        asset_id: Optional[str] = None,
    ) -> Order:
        """
        Place a market order specified by quote currency amount (USDT).
        
        This helper retrieves the current market price and calculates the 
        correct base asset quantity to match the desired USD amount.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT") - RECOMMENDED
            side: Order direction - "LONG" or "SHORT"
            amount: Amount in Quote Currency (USDT) to trade
            leverage: Leverage to use (default: "1")
            stoploss_price: Optional stop-loss price
            takeprofit_price: Optional take-profit price
            reduce_only: If True, only reduces existing position
            asset_id: Legacy asset ID (use symbol instead)
            
        Returns:
            Order: Created order details
            
        Example:
            >>> # Buy $100 worth of BTC
            >>> order = client.orders.create_market_order_with_amount(
            ...     symbol="BTCUSDT",
            ...     side="LONG",
            ...     amount="100",  # $100 USD
            ...     leverage="5"
            ... )
        """
        # Resolve symbol vs asset_id
        identifier, use_symbol = self._resolve_identifier(symbol, asset_id)
        
        # Fetch asset info to get current price and precision
        if use_symbol:
            asset = self._client.assets.get(identifier)
        else:
            asset = self._client.assets.get_by_id(identifier)
        
        if not asset.price:
            raise ValueError(
                f"Could not fetch current price for {identifier} to calculate quantity. "
                "Try using create_market_order() with an explicit quantity instead."
            )
             
        try:
            price = float(asset.price)
            quantity_step = float(asset.quantity_step) if asset.quantity_step else 0.0
            target_amount = float(amount)
        except (ValueError, TypeError):
            raise ValueError(
                f"Invalid price ({asset.price}) or quantity step for {identifier}. "
                "The asset may not be available for trading."
            )

        # Calculate quantity using shared utility
        from mudrex.utils import calculate_order_from_usd
        qty, actual_value = calculate_order_from_usd(target_amount, price, quantity_step)
        
        if qty <= 0:
            raise ValueError(
                f"Calculated quantity is 0 for amount ${amount} at price ${price}. "
                f"Minimum order value for {identifier} is approximately ${float(asset.min_quantity) * price:.2f}"
            )
            
        return self.create_market_order(
            symbol=identifier if use_symbol else None,
            asset_id=identifier if not use_symbol else None,
            side=side,
            quantity=str(qty),
            leverage=leverage,
            stoploss_price=stoploss_price,
            takeprofit_price=takeprofit_price,
            reduce_only=reduce_only,
        )

    def create_limit_order(
        self,
        symbol: Optional[str] = None,
        side: Union[str, OrderType] = None,
        quantity: str = None,
        price: str = None,
        leverage: str = "1",
        stoploss_price: Optional[str] = None,
        takeprofit_price: Optional[str] = None,
        reduce_only: bool = False,
        asset_id: Optional[str] = None,
    ) -> Order:
        """
        Place a limit order (executes when price reaches target).
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT", "XRPUSDT") - RECOMMENDED
            side: Order direction - "LONG" or "SHORT"
            quantity: Order quantity (as string for precision)
            price: Limit price (order triggers at this price)
            leverage: Leverage to use (default: "1")
            stoploss_price: Optional stop-loss price
            takeprofit_price: Optional take-profit price
            reduce_only: If True, only reduces existing position
            asset_id: Legacy asset ID (use symbol instead)
            
        Returns:
            Order: Created order details
            
        Example:
            >>> # Limit buy XRP when it dips
            >>> order = client.orders.create_limit_order(
            ...     symbol="XRPUSDT",
            ...     side="LONG",
            ...     quantity="100",
            ...     price="2.00",  # Buy when XRP drops to $2
            ...     leverage="5"
            ... )
        """
        # Resolve symbol vs asset_id
        identifier, use_symbol = self._resolve_identifier(symbol, asset_id)
        
        return self._create_order(
            identifier=identifier,
            use_symbol=use_symbol,
            side=side,
            quantity=quantity,
            trigger_type=TriggerType.LIMIT,
            price=price,
            leverage=leverage,
            stoploss_price=stoploss_price,
            takeprofit_price=takeprofit_price,
            reduce_only=reduce_only,
        )
    
    def _resolve_identifier(
        self, 
        symbol: Optional[str], 
        asset_id: Optional[str]
    ) -> tuple:
        """
        Resolve symbol vs asset_id with symbol taking priority.
        
        Returns:
            Tuple of (identifier, use_symbol)
        """
        if symbol:
            return symbol, True
        elif asset_id:
            return asset_id, False
        else:
            raise ValueError(
                "Either 'symbol' or 'asset_id' is required. "
                "Example: create_market_order(symbol='BTCUSDT', ...)"
            )
    
    def _create_order(
        self,
        identifier: str,
        use_symbol: bool,
        side: Union[str, OrderType],
        quantity: str,
        trigger_type: TriggerType,
        leverage: str = "1",
        price: Optional[str] = None,
        stoploss_price: Optional[str] = None,
        takeprofit_price: Optional[str] = None,
        reduce_only: bool = False,
    ) -> Order:
        """Internal method to create orders with smart quantity handling."""
        # Validate required fields
        if not side:
            raise ValueError("'side' is required. Use 'LONG' to buy or 'SHORT' to sell.")
        if not quantity:
            raise ValueError(
                "'quantity' is required. Use create_market_order_with_amount() "
                "if you want to specify a USD amount instead."
            )
        
        # Convert side to OrderType if string
        if isinstance(side, str):
            side_upper = side.upper()
            if side_upper not in ("LONG", "SHORT"):
                raise ValueError(
                    f"Invalid side '{side}'. Must be 'LONG' (buy) or 'SHORT' (sell)."
                )
            side = OrderType(side_upper)
        
        # Fetch asset info for smart quantity/price rounding
        try:
            if use_symbol:
                asset = self._client.assets.get(identifier)
            else:
                asset = self._client.assets.get_by_id(identifier)
            
            quantity_step = float(asset.quantity_step) if asset.quantity_step else None
            
            # Auto-round quantity to match asset's quantity_step
            if quantity_step and quantity_step > 0:
                raw_qty = float(quantity)
                
                # Check minimum quantity
                min_qty = float(asset.min_quantity) if asset.min_quantity else 0
                if raw_qty < min_qty:
                    raise ValueError(
                        f"Quantity {quantity} is below minimum {asset.min_quantity} for {identifier}. "
                        f"Increase your quantity or use a larger order amount."
                    )
                
                # Round to nearest multiple of quantity_step
                rounded_qty = round(raw_qty / quantity_step) * quantity_step
                precision = len(str(quantity_step).split('.')[-1]) if '.' in str(quantity_step) else 0
                quantity = str(round(rounded_qty, precision))
            
            # Auto-round price to match asset's price_step (tick size)
            if price and asset.price_step:
                price_step = float(asset.price_step)
                if price_step > 0:
                    raw_price = float(price)
                    rounded_price = round(raw_price / price_step) * price_step
                    price_precision = len(str(asset.price_step).split('.')[-1]) if '.' in str(asset.price_step) else 0
                    price = str(round(rounded_price, price_precision))
                    
        except Exception as e:
            # If asset fetch fails, use values as-is but warn
            if "not found" in str(e).lower():
                raise ValueError(
                    f"Symbol '{identifier}' not found. "
                    f"Use client.assets.search('{identifier[:3]}') to find valid symbols, "
                    f"or client.assets.list_all() to see all available pairs."
                )
            # For other errors, continue with original values
        
        # Mudrex API requires order_price even for MARKET orders
        if price is None and trigger_type == TriggerType.MARKET:
            price = "999999999"  # High placeholder price for market buy
        
        # Build order request
        request = OrderRequest(
            quantity=quantity,
            order_type=side,
            trigger_type=trigger_type,
            leverage=leverage,
            order_price=price,
            is_stoploss=stoploss_price is not None,
            stoploss_price=stoploss_price,
            is_takeprofit=takeprofit_price is not None,
            takeprofit_price=takeprofit_price,
            reduce_only=reduce_only,
        )
        
        # Make API request
        response = self._post(
            f"/futures/{identifier}/order", 
            request.to_dict(),
            use_symbol=use_symbol
        )
        
        data = response.get("data", response)
        data["asset_id"] = identifier
        data["symbol"] = identifier if use_symbol else data.get("symbol", identifier)
        
        return Order.from_dict(data)
    
    def create(
        self, 
        symbol: Optional[str] = None, 
        request: OrderRequest = None,
        asset_id: Optional[str] = None,
    ) -> Order:
        """
        Create an order using an OrderRequest object.
        
        This is useful when you need full control over order parameters.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT") - RECOMMENDED
            request: OrderRequest with all order parameters
            asset_id: Legacy asset ID (use symbol instead)
            
        Returns:
            Order: Created order details
        """
        identifier, use_symbol = self._resolve_identifier(symbol, asset_id)
        
        response = self._post(
            f"/futures/{identifier}/order", 
            request.to_dict(),
            use_symbol=use_symbol
        )
        data = response.get("data", response)
        data["asset_id"] = identifier
        data["symbol"] = identifier if use_symbol else data.get("symbol", identifier)
        return Order.from_dict(data)
    
    def list_open(self) -> List[Order]:
        """
        Get all open orders.
        
        Returns:
            List[Order]: List of open orders
            
        Example:
            >>> orders = client.orders.list_open()
            >>> print(f"You have {len(orders)} open orders")
            >>> for order in orders:
            ...     print(f"  {order.symbol}: {order.order_type.value} {order.quantity}")
        """
        response = self._get("/futures/orders")
        data = response.get("data", response)
        
        if isinstance(data, list):
            return [Order.from_dict(item) for item in data]
        
        items = data.get("items", data.get("data", []))
        return [Order.from_dict(item) for item in items]
    
    def get(self, order_id: str) -> Order:
        """
        Get details of a specific order.
        
        Args:
            order_id: The order ID to retrieve
            
        Returns:
            Order: Order details
        """
        response = self._get(f"/futures/orders/{order_id}")
        return Order.from_dict(response.get("data", response))
    
    def get_history(self, limit: Optional[int] = None) -> List[Order]:
        """
        Get order history.
        
        Automatically fetches all pages if no limit specified.
        
        Args:
            limit: Maximum number of orders to return (None = fetch ALL)
            
        Returns:
            List[Order]: Historical orders
            
        Example:
            >>> # Get ALL order history
            >>> history = client.orders.get_history()
            >>> print(f"Total orders: {len(history)}")
            >>> 
            >>> # Get last 50 orders only
            >>> recent = client.orders.get_history(limit=50)
        """
        all_orders = []
        page = 1
        per_page = 100  # Fetch 100 at a time for efficiency
        
        while True:
            response = self._get("/futures/orders/history", {
                "page": page,
                "per_page": per_page,
            })
            data = response.get("data", response)
            
            if isinstance(data, list):
                items = data
            else:
                items = data.get("items", data.get("data", []))
            
            if not items:
                break
            
            all_orders.extend([Order.from_dict(item) for item in items])
            
            # Stop if we've hit the limit
            if limit and len(all_orders) >= limit:
                return all_orders[:limit]
            
            # Stop if this was the last page
            if len(items) < per_page:
                break
            
            page += 1
        
        return all_orders
    
    def cancel(self, order_id: str) -> bool:
        """
        Cancel an open order.
        
        Args:
            order_id: The order ID to cancel
            
        Returns:
            bool: True if cancelled successfully
            
        Example:
            >>> orders = client.orders.list_open()
            >>> if orders:
            ...     success = client.orders.cancel(orders[0].order_id)
            ...     print(f"Order cancelled: {success}")
        """
        response = self._delete(f"/futures/orders/{order_id}")
        return response.get("success", False)
    
    def cancel_all(self, symbol: Optional[str] = None) -> int:
        """
        Cancel all open orders, optionally filtered by symbol.
        
        Args:
            symbol: If provided, only cancel orders for this symbol
            
        Returns:
            int: Number of orders cancelled
            
        Example:
            >>> # Cancel all open orders
            >>> count = client.orders.cancel_all()
            >>> print(f"Cancelled {count} orders")
            >>> 
            >>> # Cancel only BTC orders
            >>> count = client.orders.cancel_all(symbol="BTCUSDT")
        """
        orders = self.list_open()
        
        if symbol:
            orders = [o for o in orders if o.symbol == symbol or o.asset_id == symbol]
        
        cancelled = 0
        for order in orders:
            try:
                if self.cancel(order.order_id):
                    cancelled += 1
            except Exception:
                pass  # Continue cancelling others even if one fails
        
        return cancelled
    
    def amend(
        self,
        order_id: str,
        price: Optional[str] = None,
        quantity: Optional[str] = None,
    ) -> Order:
        """
        Amend an existing order.
        
        Args:
            order_id: The order ID to amend
            price: New price (optional)
            quantity: New quantity (optional)
            
        Returns:
            Order: Updated order details
        """
        data = {}
        if price is not None:
            data["order_price"] = price
        if quantity is not None:
            data["quantity"] = quantity
        
        response = self._patch(f"/futures/orders/{order_id}", data)
        return Order.from_dict(response.get("data", response))
