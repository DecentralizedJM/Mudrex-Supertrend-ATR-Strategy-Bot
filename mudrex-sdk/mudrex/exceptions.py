"""
Mudrex API Exception Classes
============================

Custom exceptions for handling Mudrex API errors with helpful, human-readable messages.
Each exception includes clear explanations and actionable solutions.
"""

from typing import Optional, Dict, Any, List


class MudrexAPIError(Exception):
    """
    Base exception for all Mudrex API errors.
    
    Every error includes:
    - A clear, human-readable message explaining what went wrong
    - The error code from the API (if available)
    - The HTTP status code
    - Suggestions for how to fix the issue
    """
    
    # Human-readable suggestions for common error scenarios
    SUGGESTIONS: Dict[str, List[str]] = {
        "default": [
            "Check the API documentation at https://docs.trade.mudrex.com",
            "If the issue persists, contact Mudrex support with the request ID",
        ],
    }
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        request_id: Optional[str] = None,
        response: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.request_id = request_id
        self.response = response or {}
        self.suggestions = suggestions or self.SUGGESTIONS.get("default", [])
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format a clear, human-readable error message."""
        lines = [f"❌ {self.message}"]
        
        if self.code and self.code != "UNKNOWN_ERROR":
            lines.append(f"   Error Code: {self.code}")
        if self.status_code:
            lines.append(f"   HTTP Status: {self.status_code}")
        if self.request_id:
            lines.append(f"   Request ID: {self.request_id} (include this when contacting support)")
        
        if self.suggestions:
            lines.append("")
            lines.append("💡 How to fix:")
            for suggestion in self.suggestions:
                lines.append(f"   • {suggestion}")
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        return self._format_message()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r}, code={self.code!r})"


class MudrexAuthenticationError(MudrexAPIError):
    """
    Raised when authentication fails.
    
    This means your API key is invalid, expired, or missing.
    """
    
    SUGGESTIONS = {
        "default": [
            "Verify your API secret is correct (copy it again from Mudrex dashboard)",
            "Check if your API key has expired or been revoked",
            "Ensure KYC verification is complete on your Mudrex account",
            "Enable 2FA (two-factor authentication) if not already done",
            "Generate a new API key if needed: Dashboard → API Keys → Generate",
        ],
    }
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        if "suggestions" not in kwargs:
            kwargs["suggestions"] = self.SUGGESTIONS["default"]
        super().__init__(message, **kwargs)


class MudrexRateLimitError(MudrexAPIError):
    """
    Raised when you've exceeded the API rate limits.
    
    Rate Limits:
    - 2 requests per second
    - 50 requests per minute
    - 1000 requests per hour
    - 10000 requests per day
    """
    
    SUGGESTIONS = {
        "default": [
            "Wait before making more requests (see retry_after)",
            "The SDK has built-in rate limiting - ensure rate_limit=True",
            "Reduce request frequency in your code",
            "Batch multiple operations where possible",
            "Consider using webhooks for real-time updates instead of polling",
        ],
    }
    
    def __init__(
        self,
        message: str = "Rate limit exceeded - too many requests",
        retry_after: Optional[float] = None,
        **kwargs
    ):
        self.retry_after = retry_after
        if "suggestions" not in kwargs:
            suggestions = self.SUGGESTIONS["default"].copy()
            if retry_after:
                suggestions.insert(0, f"Wait {retry_after} seconds before retrying")
            kwargs["suggestions"] = suggestions
        super().__init__(message, **kwargs)


class MudrexValidationError(MudrexAPIError):
    """
    Raised when request parameters are invalid.
    
    Common causes:
    - Quantity not matching the asset's quantity_step
    - Leverage outside allowed range
    - Invalid symbol or asset_id
    - Missing required fields
    """
    
    SUGGESTIONS = {
        "default": [
            "Check that all parameter values are valid",
            "Ensure quantity is a multiple of the asset's quantity_step",
            "Verify leverage is within min_leverage and max_leverage for the asset",
            "Use client.assets.get('SYMBOL') to check asset specifications",
        ],
        "quantity": [
            "Quantity must be a multiple of the asset's quantity_step",
            "Use client.assets.get('SYMBOL') to find the correct quantity_step",
            "The SDK auto-rounds quantities, but extreme values may still fail",
        ],
        "leverage": [
            "Leverage must be between min_leverage and max_leverage for this asset",
            "Use client.assets.get('SYMBOL') to check allowed leverage range",
            "Example: BTC allows 1x-100x, some altcoins may have lower limits",
        ],
        "symbol": [
            "Make sure the symbol exists (e.g., 'BTCUSDT', 'ETHUSDT')",
            "Use client.assets.search('BTC') to find valid symbols",
            "Use client.assets.exists('SYMBOL') to check if tradable",
        ],
    }
    
    def __init__(self, message: str = "Invalid request parameters", **kwargs):
        # Try to detect the type of validation error for better suggestions
        suggestions = self.SUGGESTIONS["default"]
        message_lower = message.lower()
        
        if "quantity" in message_lower or "step" in message_lower:
            suggestions = self.SUGGESTIONS["quantity"]
        elif "leverage" in message_lower:
            suggestions = self.SUGGESTIONS["leverage"]
        elif "symbol" in message_lower or "asset" in message_lower or "not found" in message_lower:
            suggestions = self.SUGGESTIONS["symbol"]
        
        if "suggestions" not in kwargs:
            kwargs["suggestions"] = suggestions
        super().__init__(message, **kwargs)


class MudrexNotFoundError(MudrexAPIError):
    """
    Raised when a resource is not found.
    
    Common causes:
    - Invalid symbol (typo or unsupported trading pair)
    - Order or position ID doesn't exist
    - Resource was already deleted/closed
    """
    
    SUGGESTIONS = {
        "default": [
            "Check that the symbol/ID is correct",
            "Use client.assets.list_all() to see all available trading pairs",
            "Use client.assets.search('keyword') to find similar symbols",
            "The order/position may have already been filled, cancelled, or closed",
        ],
    }
    
    def __init__(self, message: str = "Resource not found", **kwargs):
        if "suggestions" not in kwargs:
            kwargs["suggestions"] = self.SUGGESTIONS["default"]
        super().__init__(message, **kwargs)


class MudrexConflictError(MudrexAPIError):
    """
    Raised when there's a conflicting or duplicate action.
    
    Common causes:
    - Trying to close an already closed position
    - Duplicate order submission
    - Conflicting leverage settings
    """
    
    SUGGESTIONS = {
        "default": [
            "The action may have already been performed",
            "Refresh your position/order list before retrying",
            "Wait a moment and check the current state before retrying",
        ],
    }
    
    def __init__(self, message: str = "Conflicting action", **kwargs):
        if "suggestions" not in kwargs:
            kwargs["suggestions"] = self.SUGGESTIONS["default"]
        super().__init__(message, **kwargs)


class MudrexServerError(MudrexAPIError):
    """
    Raised when the Mudrex server encounters an internal error.
    
    This is usually temporary - retry after a short delay.
    """
    
    SUGGESTIONS = {
        "default": [
            "This is usually a temporary issue - wait and retry",
            "Use exponential backoff: wait 1s, then 2s, then 4s, etc.",
            "Check Mudrex status page for any ongoing issues",
            "If the problem persists, contact Mudrex support",
        ],
    }
    
    def __init__(self, message: str = "Server error occurred", **kwargs):
        if "suggestions" not in kwargs:
            kwargs["suggestions"] = self.SUGGESTIONS["default"]
        super().__init__(message, **kwargs)


class MudrexInsufficientBalanceError(MudrexAPIError):
    """
    Raised when you don't have enough balance for an operation.
    
    Check your futures wallet balance before trading.
    """
    
    SUGGESTIONS = {
        "default": [
            "Check your futures wallet balance: client.wallet.get_futures_balance()",
            "Transfer funds from spot to futures: client.wallet.transfer_to_futures('100')",
            "Reduce your order size or leverage",
            "Close some existing positions to free up margin",
        ],
    }
    
    def __init__(self, message: str = "Insufficient balance for this operation", **kwargs):
        if "suggestions" not in kwargs:
            kwargs["suggestions"] = self.SUGGESTIONS["default"]
        super().__init__(message, **kwargs)


class MudrexOrderError(MudrexAPIError):
    """
    Raised when an order cannot be placed or modified.
    
    Common causes:
    - Market is closed or in maintenance
    - Order size too small or too large
    - Price outside allowed range
    """
    
    SUGGESTIONS = {
        "default": [
            "Check if the market is currently open for trading",
            "Verify order quantity is within min/max limits for this asset",
            "For limit orders, ensure price is within the allowed range",
            "Use client.assets.get('SYMBOL') to check trading limits",
        ],
    }
    
    def __init__(self, message: str = "Order could not be placed", **kwargs):
        if "suggestions" not in kwargs:
            kwargs["suggestions"] = self.SUGGESTIONS["default"]
        super().__init__(message, **kwargs)


class MudrexPositionError(MudrexAPIError):
    """
    Raised when a position operation fails.
    
    Common causes:
    - Position doesn't exist or already closed
    - Invalid stop-loss/take-profit prices
    - Cannot modify position in current state
    """
    
    SUGGESTIONS = {
        "default": [
            "Check if the position still exists: client.positions.list_open()",
            "The position may have been closed by stop-loss/take-profit",
            "Verify stop-loss is below entry (for LONG) or above (for SHORT)",
            "Verify take-profit is above entry (for LONG) or below (for SHORT)",
        ],
    }
    
    def __init__(self, message: str = "Position operation failed", **kwargs):
        if "suggestions" not in kwargs:
            kwargs["suggestions"] = self.SUGGESTIONS["default"]
        super().__init__(message, **kwargs)


# Error code to exception class mapping
ERROR_CODE_MAP = {
    # Authentication errors
    "UNAUTHORIZED": MudrexAuthenticationError,
    "FORBIDDEN": MudrexAuthenticationError,
    "INVALID_API_KEY": MudrexAuthenticationError,
    "API_KEY_EXPIRED": MudrexAuthenticationError,
    
    # Rate limiting
    "RATE_LIMIT_EXCEEDED": MudrexRateLimitError,
    "TOO_MANY_REQUESTS": MudrexRateLimitError,
    
    # Validation errors
    "INVALID_REQUEST": MudrexValidationError,
    "VALIDATION_ERROR": MudrexValidationError,
    "BAD_REQUEST": MudrexValidationError,
    "INVALID_PARAMETER": MudrexValidationError,
    
    # Not found
    "NOT_FOUND": MudrexNotFoundError,
    "ASSET_NOT_FOUND": MudrexNotFoundError,
    "ORDER_NOT_FOUND": MudrexNotFoundError,
    "POSITION_NOT_FOUND": MudrexNotFoundError,
    
    # Conflicts
    "CONFLICT": MudrexConflictError,
    "DUPLICATE": MudrexConflictError,
    
    # Server errors
    "SERVER_ERROR": MudrexServerError,
    "INTERNAL_ERROR": MudrexServerError,
    "SERVICE_UNAVAILABLE": MudrexServerError,
    
    # Balance errors
    "INSUFFICIENT_BALANCE": MudrexInsufficientBalanceError,
    "INSUFFICIENT_MARGIN": MudrexInsufficientBalanceError,
    "INSUFFICIENT_FUNDS": MudrexInsufficientBalanceError,
    
    # Order errors
    "ORDER_REJECTED": MudrexOrderError,
    "ORDER_FAILED": MudrexOrderError,
    
    # Position errors
    "POSITION_ERROR": MudrexPositionError,
    "POSITION_CLOSED": MudrexPositionError,
}

# Human-readable messages for common error scenarios
ERROR_MESSAGE_MAP = {
    "UNAUTHORIZED": "Your API key is invalid or has expired",
    "FORBIDDEN": "You don't have permission to perform this action",
    "RATE_LIMIT_EXCEEDED": "You've exceeded the rate limit - please slow down",
    "INVALID_REQUEST": "The request parameters are invalid",
    "NOT_FOUND": "The requested resource was not found",
    "INSUFFICIENT_BALANCE": "You don't have enough balance for this operation",
    "SERVER_ERROR": "The server encountered an error - please retry",
}


def raise_for_error(response: Dict[str, Any], status_code: int) -> None:
    """
    Parse API response and raise appropriate exception if error detected.
    
    This function creates human-readable error messages with helpful suggestions.
    
    Args:
        response: The JSON response from the API
        status_code: HTTP status code
        
    Raises:
        MudrexAPIError: Or a more specific subclass based on error code
    """
    # Check if success is explicitly False or status indicates error
    if response.get("success", True) and status_code < 400:
        return
    
    # Extract error details
    code = response.get("code", "UNKNOWN_ERROR")
    message = response.get("message", "")
    request_id = response.get("requestId") or response.get("request_id")
    
    # Check for errors array (common Mudrex API format)
    errors = response.get("errors", [])
    if errors:
        # Extract detailed error messages from errors array
        error_texts = []
        for e in errors:
            if isinstance(e, dict):
                text = e.get("text") or e.get("message") or str(e)
                error_texts.append(text)
            else:
                error_texts.append(str(e))
        
        if error_texts:
            message = "; ".join(error_texts)
            # Try to extract error code from first error
            if errors[0] and isinstance(errors[0], dict) and errors[0].get("code"):
                code = errors[0].get("code")
    
    # If no message, use a human-readable default based on code
    if not message or message == "An unknown error occurred":
        message = ERROR_MESSAGE_MAP.get(code, f"An error occurred (code: {code})")
    
    # Make the message more human-readable
    message = _humanize_error_message(message, code, status_code)
    
    # Get the appropriate exception class
    exception_class = ERROR_CODE_MAP.get(code, MudrexAPIError)
    
    # Map status codes to exception classes if code not recognized
    if exception_class == MudrexAPIError:
        if status_code == 401 or status_code == 403:
            exception_class = MudrexAuthenticationError
        elif status_code == 404:
            exception_class = MudrexNotFoundError
        elif status_code == 429:
            exception_class = MudrexRateLimitError
        elif status_code == 409:
            exception_class = MudrexConflictError
        elif status_code >= 500:
            exception_class = MudrexServerError
        elif status_code == 400:
            exception_class = MudrexValidationError
    
    raise exception_class(
        message=message,
        code=code,
        status_code=status_code,
        request_id=request_id,
        response=response,
    )


def _humanize_error_message(message: str, code: str, status_code: int) -> str:
    """Convert technical error messages to human-readable format."""
    # Common technical terms to human-readable
    replacements = {
        "asset_id": "symbol/asset",
        "order_id": "order ID",
        "position_id": "position ID",
        "leverage": "leverage",
        "quantity_step": "quantity increment",
        "min_quantity": "minimum quantity",
        "max_quantity": "maximum quantity",
    }
    
    result = message
    for tech_term, human_term in replacements.items():
        result = result.replace(tech_term, human_term)
    
    # Capitalize first letter if not already
    if result and result[0].islower():
        result = result[0].upper() + result[1:]
    
    return result
