"""
Fees API Module
===============

Endpoints for retrieving trading fee history.
"""

from typing import TYPE_CHECKING, List, Optional

from mudrex.api.base import BaseAPI
from mudrex.models import FeeRecord

if TYPE_CHECKING:
    from mudrex.client import MudrexClient


class FeesAPI(BaseAPI):
    """
    Fee history endpoints.
    
    Use these methods to:
    - Retrieve your trading fee history
    - Analyze trading costs
    - Track fees by symbol
    
    Example:
        >>> client = MudrexClient(api_secret="...")
        >>> 
        >>> # Get ALL fee history
        >>> fees = client.fees.get_history()
        >>> total_fees = sum(float(f.fee_amount) for f in fees)
        >>> print(f"Total fees paid: ${total_fees:.2f}")
    """
    
    def get_history(
        self,
        limit: Optional[int] = None,
        symbol: Optional[str] = None,
    ) -> List[FeeRecord]:
        """
        Get trading fee history.
        
        Automatically fetches all pages if no limit specified.
        
        Args:
            limit: Maximum number of records to return (None = fetch ALL)
            symbol: Filter by trading symbol (optional)
            
        Returns:
            List[FeeRecord]: List of fee transactions
            
        Example:
            >>> # Get ALL fees
            >>> fees = client.fees.get_history()
            >>> print(f"Total fee records: {len(fees)}")
            >>> 
            >>> # Calculate total fees paid
            >>> total = sum(float(f.fee_amount) for f in fees)
            >>> print(f"Total fees: ${total:.2f}")
            >>> 
            >>> # Get last 50 fee records
            >>> recent = client.fees.get_history(limit=50)
            >>> 
            >>> # Get fees for specific symbol
            >>> btc_fees = client.fees.get_history(symbol="BTCUSDT")
        """
        all_fees = []
        page = 1
        per_page = 100  # Fetch 100 at a time for efficiency
        
        while True:
            response = self._get("/futures/fee/history", {
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
            
            fees = [FeeRecord.from_dict(item) for item in items]
            
            # Filter by symbol if specified
            if symbol:
                fees = [f for f in fees if f.symbol == symbol or f.asset_id == symbol]
            
            all_fees.extend(fees)
            
            # Stop if we've hit the limit
            if limit and len(all_fees) >= limit:
                return all_fees[:limit]
            
            # Stop if this was the last page
            if len(items) < per_page:
                break
            
            page += 1
        
        return all_fees
    
    def get_total_fees(self, symbol: Optional[str] = None) -> dict:
        """
        Calculate total fees paid.
        
        Args:
            symbol: Filter by trading symbol (optional)
            
        Returns:
            dict: Summary with total_fees, fee_count, and average_fee
            
        Example:
            >>> summary = client.fees.get_total_fees()
            >>> print(f"Total fees paid: ${summary['total_fees']:.2f}")
            >>> print(f"Average fee: ${summary['average_fee']:.4f}")
            >>> 
            >>> # Get fees for specific symbol
            >>> btc_summary = client.fees.get_total_fees(symbol="BTCUSDT")
        """
        fees = self.get_history(symbol=symbol)
        
        total = 0.0
        for fee in fees:
            try:
                total += float(fee.fee_amount)
            except (ValueError, TypeError):
                pass
        
        return {
            "total_fees": total,
            "fee_count": len(fees),
            "average_fee": total / len(fees) if fees else 0.0,
        }
    
    def get_fees_by_symbol(self) -> dict:
        """
        Get fee breakdown by trading symbol.
        
        Returns:
            dict: Mapping of symbol to total fees paid
            
        Example:
            >>> breakdown = client.fees.get_fees_by_symbol()
            >>> for symbol, total in sorted(breakdown.items(), key=lambda x: -x[1]):
            ...     print(f"{symbol}: ${total:.2f}")
        """
        fees = self.get_history()
        
        by_symbol = {}
        for fee in fees:
            symbol = fee.symbol or fee.asset_id
            if symbol:
                try:
                    amount = float(fee.fee_amount)
                    by_symbol[symbol] = by_symbol.get(symbol, 0.0) + amount
                except (ValueError, TypeError):
                    pass
        
        return by_symbol
