"""
Assets API Module
=================

Endpoints for discovering tradable futures instruments.
Supports 500+ trading pairs available on Mudrex.
"""

from typing import TYPE_CHECKING, Optional, List

from mudrex.api.base import BaseAPI
from mudrex.models import Asset, Ticker, PaginatedResponse

if TYPE_CHECKING:
    from mudrex.client import MudrexClient


class AssetsAPI(BaseAPI):
    """
    Asset discovery endpoints.
    
    Use these methods to:
    - List ALL tradable futures contracts (500+ pairs)
    - Get detailed specifications for a specific asset by symbol
    - Search assets by name
    - Get current price/ticker data
    
    Example:
        >>> client = MudrexClient(api_secret="...")
        >>> 
        >>> # List ALL assets (no limit!)
        >>> assets = client.assets.list_all()
        >>> print(f"Found {len(assets)} tradable assets")  # 500+
        >>> 
        >>> # Get specific asset by symbol (recommended)
        >>> btc = client.assets.get("BTCUSDT")
        >>> xrp = client.assets.get("XRPUSDT")
        >>> print(f"Min qty: {btc.min_quantity}, Max qty: {btc.max_quantity}")
        >>> 
        >>> # Get current price
        >>> ticker = client.assets.get_ticker("BTCUSDT")
        >>> print(f"BTC Price: ${ticker.price}")
    """
    
    # Cache for all assets to avoid repeated API calls
    _assets_cache: Optional[List[Asset]] = None
    _cache_symbols: Optional[dict] = None
    
    def list_all(
        self,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        refresh: bool = False,
    ) -> List[Asset]:
        """
        List ALL tradable futures contracts.
        
        This fetches all available assets (500+) without pagination limits.
        The SDK automatically fetches all pages for you.
        
        Results are cached for efficiency. Use refresh=True to force a fresh fetch.
        
        Args:
            sort_by: Field to sort by (optional)
            sort_order: Sort direction - "asc" or "desc" (default: "asc")
            refresh: Force refresh the cache (default: False)
            
        Returns:
            List[Asset]: Complete list of ALL tradable assets
            
        Example:
            >>> assets = client.assets.list_all()
            >>> print(f"Total tradable assets: {len(assets)}")  # 500+
            >>> 
            >>> # Find all USDT pairs
            >>> usdt_pairs = [a for a in assets if a.symbol.endswith("USDT")]
            >>> print(f"USDT pairs: {len(usdt_pairs)}")
            >>> 
            >>> # Force refresh to get latest data
            >>> assets = client.assets.list_all(refresh=True)
        """
        # Return cached results if available and not forcing refresh
        if not refresh and self._assets_cache is not None:
            assets = self._assets_cache
            # Apply sorting if requested
            if sort_by:
                reverse = sort_order.lower() == "desc"
                assets = sorted(assets, key=lambda a: getattr(a, sort_by, ""), reverse=reverse)
            return assets
        
        all_assets = []
        offset = 0
        limit = 100  # Fetch 100 assets per request for efficiency
        
        while True:
            params = {
                "offset": offset,
                "limit": limit,
            }
            if sort_by:
                params["sort_by"] = sort_by
                params["sort_order"] = sort_order
            
            response = self._get("/futures", params)
            
            # Handle both list and paginated responses
            data = response.get("data", response)
            if isinstance(data, list):
                items = data
            else:
                items = data.get("items", data.get("data", []))
            
            if not items:
                break
                
            all_assets.extend([Asset.from_dict(item) for item in items])
            
            # Check if we've gotten all items
            if len(items) < limit:
                break
            
            offset += limit
        
        # Cache the results
        self._assets_cache = all_assets
        self._cache_symbols = {a.symbol: a for a in all_assets}
        
        return all_assets
    
    def get(self, symbol: str) -> Asset:
        """
        Get detailed specifications for a specific asset by symbol.
        
        Use trading symbols like "BTCUSDT", "ETHUSDT", "XRPUSDT", etc.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT", "XRPUSDT", "SOLUSDT")
            
        Returns:
            Asset: Detailed asset specifications
            
        Raises:
            MudrexNotFoundError: If the symbol doesn't exist
            
        Example:
            >>> btc = client.assets.get("BTCUSDT")
            >>> print(f"Symbol: {btc.symbol}")
            >>> print(f"Min quantity: {btc.min_quantity}")
            >>> print(f"Max leverage: {btc.max_leverage}x")
            >>> print(f"Maker fee: {btc.maker_fee}%")
            >>> print(f"Taker fee: {btc.taker_fee}%")
            >>> print(f"Current price: ${btc.price}")
            >>> 
            >>> # Works with any supported symbol
            >>> xrp = client.assets.get("XRPUSDT")
            >>> sol = client.assets.get("SOLUSDT")
        """
        response = self._get(f"/futures/{symbol}", use_symbol=True)
        return Asset.from_dict(response.get("data", response))
    
    def get_by_id(self, asset_id: str) -> Asset:
        """
        Get asset by internal asset ID (advanced usage).
        
        Most users should use get(symbol) instead.
        
        Args:
            asset_id: Internal Mudrex asset ID
            
        Returns:
            Asset: Detailed asset specifications
        """
        response = self._get(f"/futures/{asset_id}")
        return Asset.from_dict(response.get("data", response))
    
    def get_ticker(self, symbol: str) -> Ticker:
        """
        Get current ticker/price data for a symbol.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            
        Returns:
            Ticker: Current price and market data
            
        Example:
            >>> ticker = client.assets.get_ticker("BTCUSDT")
            >>> print(f"BTC Price: ${ticker.price}")
            >>> print(f"24h Change: {ticker.change_24h}%")
        """
        asset = self.get(symbol)
        return Ticker(
            symbol=asset.symbol,
            price=asset.price or "0",
        )
    
    def get_price(self, symbol: str) -> str:
        """
        Get current price for a symbol.
        
        This is a convenience method that returns just the price.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            
        Returns:
            str: Current price as string
            
        Example:
            >>> price = client.assets.get_price("BTCUSDT")
            >>> print(f"BTC: ${price}")
        """
        asset = self.get(symbol)
        return asset.price or "0"
    
    def search(self, query: str) -> List[Asset]:
        """
        Search for assets by symbol pattern.
        
        Args:
            query: Search term (case-insensitive)
            
        Returns:
            List[Asset]: Matching assets
            
        Example:
            >>> # Find all BTC pairs
            >>> btc_assets = client.assets.search("BTC")
            >>> for asset in btc_assets:
            ...     print(asset.symbol)  # BTCUSDT, BTCUSD, etc.
            >>> 
            >>> # Find meme coins
            >>> meme = client.assets.search("DOGE")
        """
        all_assets = self.list_all()
        query_upper = query.upper()
        return [
            asset for asset in all_assets
            if query_upper in asset.symbol.upper() or 
               (asset.name and query_upper in asset.name.upper())
        ]
    
    def exists(self, symbol: str) -> bool:
        """
        Check if a trading symbol exists.
        
        Args:
            symbol: Trading symbol to check
            
        Returns:
            bool: True if the symbol exists and is tradable
            
        Example:
            >>> if client.assets.exists("XRPUSDT"):
            ...     print("XRP is tradable!")
        """
        try:
            self.get(symbol)
            return True
        except Exception:
            return False
    
    def get_by_leverage(self, min_leverage: int = 1, max_leverage: Optional[int] = None) -> List[Asset]:
        """
        Get assets that support specific leverage requirements.
        
        Args:
            min_leverage: Minimum required leverage (default: 1)
            max_leverage: Maximum leverage to filter by (optional)
            
        Returns:
            List[Asset]: Assets meeting the leverage requirements
            
        Example:
            >>> # Find assets with high leverage (50x+)
            >>> high_lev = client.assets.get_by_leverage(min_leverage=50)
            >>> print(f"{len(high_lev)} assets support 50x+ leverage")
        """
        all_assets = self.list_all()
        
        results = []
        for asset in all_assets:
            try:
                asset_max_lev = int(float(asset.max_leverage))
                if asset_max_lev >= min_leverage:
                    if max_leverage is None or asset_max_lev <= max_leverage:
                        results.append(asset)
            except (ValueError, TypeError):
                pass
        
        return results
    
    def get_active(self) -> List[Asset]:
        """
        Get all currently active/tradable assets.
        
        Returns:
            List[Asset]: Active assets only
            
        Example:
            >>> active = client.assets.get_active()
            >>> print(f"{len(active)} assets are currently tradable")
        """
        return [a for a in self.list_all() if a.is_active]
    
    def clear_cache(self) -> None:
        """
        Clear the assets cache.
        
        Call this if you need to force a refresh on the next list_all() call.
        
        Example:
            >>> client.assets.clear_cache()
            >>> fresh_assets = client.assets.list_all()
        """
        self._assets_cache = None
        self._cache_symbols = None