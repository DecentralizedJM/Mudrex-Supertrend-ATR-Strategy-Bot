"""
Error Handling Example
======================

Demonstrates proper error handling for robust trading applications.
"""

import os
import time
from mudrex import MudrexClient
from mudrex.exceptions import (
    MudrexAPIError,
    MudrexAuthenticationError,
    MudrexRateLimitError,
    MudrexValidationError,
    MudrexNotFoundError,
    MudrexInsufficientBalanceError,
)


def handle_authentication_errors():
    """
    Example: Handling authentication errors.
    
    These occur when:
    - API secret is invalid
    - API key is revoked
    - KYC/2FA not completed
    """
    try:
        # This will fail with an invalid secret
        client = MudrexClient(api_secret="invalid-secret")
        client.wallet.get_spot_balance()
    except MudrexAuthenticationError as e:
        print(f"❌ Authentication failed: {e.message}")
        print(f"   Error code: {e.code}")
        print(f"   Request ID: {e.request_id}")
        print("\n   Solutions:")
        print("   1. Check your API secret is correct")
        print("   2. Ensure KYC and 2FA are completed")
        print("   3. Generate a new API key if needed")


def handle_rate_limiting(client: MudrexClient):
    """
    Example: Handling rate limits with retry logic.
    
    Rate limits:
    - 2 requests/second
    - 50 requests/minute
    - 1000 requests/hour
    - 10000 requests/day
    """
    def make_request_with_retry(max_retries: int = 3):
        for attempt in range(max_retries):
            try:
                return client.wallet.get_spot_balance()
            except MudrexRateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = e.retry_after or (2 ** attempt)
                    print(f"⏳ Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print("❌ Max retries exceeded")
                    raise
    
    # The SDK has built-in rate limiting, but you can add extra protection
    print("Making request with retry logic...")
    balance = make_request_with_retry()
    print(f"✅ Balance: ${balance.available}")


def handle_validation_errors(client: MudrexClient):
    """
    Example: Handling validation errors.
    
    These occur when:
    - Invalid parameter values
    - Out-of-range leverage
    - Invalid quantities
    """
    try:
        # Try to set invalid leverage
        client.leverage.set("BTCUSDT", leverage="1000", margin_type="ISOLATED")
    except MudrexValidationError as e:
        print(f"❌ Validation error: {e.message}")
        print("\n   Solution: Check parameter values against asset limits")
        
        # Show valid range
        asset = client.assets.get("BTCUSDT")
        print(f"   Valid leverage range: {asset.min_leverage}x - {asset.max_leverage}x")


def handle_not_found_errors(client: MudrexClient):
    """
    Example: Handling not-found errors.
    
    These occur when:
    - Invalid asset ID
    - Order/position doesn't exist
    """
    try:
        client.assets.get("INVALID_ASSET_123")
    except MudrexNotFoundError as e:
        print(f"❌ Resource not found: {e.message}")
        print("\n   Solution: Verify the asset ID exists")
        
        # Search for valid assets
        assets = client.assets.search("BTC")
        print(f"   Available BTC assets: {[a.symbol for a in assets]}")


def handle_insufficient_balance(client: MudrexClient):
    """
    Example: Handling insufficient balance errors.
    
    Always check balance before placing orders.
    """
    try:
        # Check balance first (best practice)
        balance = client.wallet.get_futures_balance()
        required_margin = 100  # Example
        
        if float(balance.balance) < required_margin:
            print(f"⚠️ Insufficient balance: ${balance.balance}")
            print(f"   Required: ${required_margin}")
            print("\n   Solutions:")
            print("   1. Transfer more funds from spot wallet")
            print("   2. Reduce position size")
            print("   3. Use higher leverage (increases risk!)")
        else:
            print(f"✅ Sufficient balance: ${balance.balance}")
            
    except MudrexInsufficientBalanceError as e:
        print(f"❌ Insufficient balance: {e.message}")


def robust_order_placement(client: MudrexClient):
    """
    Example: Complete error handling for order placement.
    
    This shows a production-ready approach to placing orders.
    """
    symbol = "BTCUSDT"  # Use symbol directly (recommended!)
    quantity = "0.001"
    leverage = "5"
    
    print(f"\n🔄 Placing order for {symbol}...")
    
    try:
        # Step 1: Verify asset exists and get specs
        asset = client.assets.get(symbol)
        print(f"   ✓ Asset verified: {asset.symbol}")
        print(f"   ✓ Current price: ${asset.price}")
        
        # Step 2: Validate quantity
        if float(quantity) < float(asset.min_quantity):
            print(f"   ❌ Quantity {quantity} below minimum {asset.min_quantity}")
            return
        
        # Step 3: Validate leverage
        if float(leverage) > float(asset.max_leverage):
            print(f"   ❌ Leverage {leverage}x exceeds max {asset.max_leverage}x")
            return
        
        # Step 4: Check balance
        balance = client.wallet.get_futures_balance()
        # Calculate margin estimate using actual price
        price = float(asset.price) if asset.price else 100000
        estimated_margin = float(quantity) * price / float(leverage)
        
        if float(balance.available) < estimated_margin:
            print(f"   ❌ Insufficient margin: need ~${estimated_margin:.2f}")
            print(f"      Available: ${balance.available}")
            return
        
        print(f"   ✓ Balance sufficient: ${balance.available}")
        
        # Step 5: Set leverage
        client.leverage.set(symbol, leverage, "ISOLATED")
        print(f"   ✓ Leverage set to {leverage}x")
        
        # Step 6: Place order (commented out for safety)
        # order = client.orders.create_market_order(
        #     symbol=symbol,  # Use symbol, not asset_id
        #     side="LONG",
        #     quantity=quantity,
        #     leverage=leverage,
        # )
        # print(f"   ✓ Order placed: {order.order_id}")
        
        print(f"   ✓ Order validation passed (not executed in demo)")
        
    except MudrexAuthenticationError:
        print("   ❌ Authentication failed - check API key")
    except MudrexRateLimitError:
        print("   ❌ Rate limited - try again later")
    except MudrexValidationError as e:
        print(f"   ❌ Invalid parameters: {e.message}")
    except MudrexNotFoundError:
        print(f"   ❌ Symbol {symbol} not found")
    except MudrexInsufficientBalanceError:
        print("   ❌ Insufficient balance")
    except MudrexAPIError as e:
        print(f"   ❌ API error: {e.message}")
        print(f"      Request ID: {e.request_id}")


def main():
    """Run all error handling examples."""
    api_secret = os.environ.get("MUDREX_API_SECRET")
    
    print("=" * 60)
    print("MUDREX SDK - Error Handling Examples")
    print("=" * 60)
    
    # Authentication errors (uses invalid key intentionally)
    print("\n1. Authentication Errors")
    print("-" * 40)
    handle_authentication_errors()
    
    if not api_secret:
        print("\n⚠️ Set MUDREX_API_SECRET to run remaining examples")
        return
    
    client = MudrexClient(api_secret=api_secret)
    
    # Rate limiting
    print("\n2. Rate Limiting")
    print("-" * 40)
    handle_rate_limiting(client)
    
    # Validation errors
    print("\n3. Validation Errors")
    print("-" * 40)
    handle_validation_errors(client)
    
    # Not found errors
    print("\n4. Not Found Errors")
    print("-" * 40)
    handle_not_found_errors(client)
    
    # Balance checks
    print("\n5. Balance Checks")
    print("-" * 40)
    handle_insufficient_balance(client)
    
    # Robust order placement
    print("\n6. Robust Order Placement")
    print("-" * 40)
    robust_order_placement(client)
    
    print("\n" + "=" * 60)
    print("Examples complete!")


if __name__ == "__main__":
    main()
