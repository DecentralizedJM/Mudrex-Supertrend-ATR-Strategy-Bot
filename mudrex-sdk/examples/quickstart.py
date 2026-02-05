"""
Mudrex SDK Quickstart
=====================

This example shows you how to get started with the Mudrex Trading SDK.
It covers all the basics a first-time user needs to know.

Installation:
    pip install git+https://github.com/DecentralizedJM/mudrex-trading-sdk.git

Prerequisites:
    1. Create a Mudrex account
    2. Complete KYC verification
    3. Enable 2FA
    4. Generate an API key from Dashboard -> API Keys
"""

import os
from mudrex import (
    MudrexClient,
    MudrexAPIError,
    MudrexAuthenticationError,
    MudrexInsufficientBalanceError,
)


def main():
    # =========================================================================
    # Step 1: Get your API key
    # =========================================================================
    # Option A: Set as environment variable (recommended for security)
    #   export MUDREX_API_SECRET="your-api-secret"
    #
    # Option B: Replace the string below (for testing only)
    
    API_SECRET = os.environ.get("MUDREX_API_SECRET", "your-api-secret-here")
    
    if API_SECRET == "your-api-secret-here":
        print("=" * 60)
        print("⚠️  Please set your API secret!")
        print("")
        print("Option 1 (Recommended): Set environment variable")
        print("   export MUDREX_API_SECRET='your-secret'")
        print("")
        print("Option 2: Edit this file and replace 'your-api-secret-here'")
        print("")
        print("Get your API key from: https://trade.mudrex.com")
        print("   Dashboard -> API Keys -> Generate")
        print("=" * 60)
        return
    
    # =========================================================================
    # Step 2: Initialize the client
    # =========================================================================
    print("🚀 Connecting to Mudrex API...")
    
    try:
        client = MudrexClient(api_secret=API_SECRET)
        print("✅ Connected successfully!")
    except MudrexAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("\n💡 Check that your API key is correct and not expired.")
        return
    
    # =========================================================================
    # Step 3: Check your wallet balances
    # =========================================================================
    print("\n" + "=" * 60)
    print("💰 WALLET BALANCES")
    print("=" * 60)
    
    # Spot wallet (for deposits)
    spot = client.wallet.get_spot_balance()
    print(f"\n📍 Spot Wallet:")
    print(f"   Total:       ${spot.total}")
    print(f"   Available:   ${spot.available}")
    print(f"   Withdrawable: ${spot.withdrawable}")
    
    # Futures wallet (for trading)
    futures = client.wallet.get_futures_balance()
    print(f"\n📍 Futures Wallet:")
    print(f"   Balance:     ${futures.balance}")
    print(f"   Available:   ${futures.available}")
    print(f"   Locked:      ${futures.locked_amount}")
    
    # =========================================================================
    # Step 4: Discover tradable assets
    # =========================================================================
    print("\n" + "=" * 60)
    print("📊 AVAILABLE ASSETS")
    print("=" * 60)
    
    # Get ALL assets (500+ pairs!) - automatically handles pagination
    print("\n🔍 Fetching all tradable assets...")
    assets = client.assets.list_all()
    print(f"✅ Found {len(assets)} tradable assets!")
    
    # Show some examples
    print("\n📋 Sample assets:")
    for asset in assets[:5]:
        print(f"   • {asset.symbol}: {asset.min_leverage}x - {asset.max_leverage}x leverage")
    print(f"   ... and {len(assets) - 5} more!")
    
    # =========================================================================
    # Step 5: Get details for a specific asset
    # =========================================================================
    print("\n" + "=" * 60)
    print("🔎 ASSET DETAILS")
    print("=" * 60)
    
    # Get Bitcoin details - just use the symbol!
    btc = client.assets.get("BTCUSDT")
    print(f"\n📈 {btc.symbol}:")
    print(f"   Current Price:  ${btc.price}")
    print(f"   Min Quantity:   {btc.min_quantity}")
    print(f"   Max Quantity:   {btc.max_quantity}")
    print(f"   Quantity Step:  {btc.quantity_step}")
    print(f"   Max Leverage:   {btc.max_leverage}x")
    print(f"   Taker Fee:      {btc.taker_fee}%")
    
    # Get current price (convenience method)
    eth_price = client.assets.get_price("ETHUSDT")
    print(f"\n   ETH Price:      ${eth_price}")
    
    # Search for assets
    print("\n🔍 Search example - finding 'DOGE' pairs:")
    doge_assets = client.assets.search("DOGE")
    for asset in doge_assets[:3]:
        print(f"   • {asset.symbol}")
    
    # =========================================================================
    # Step 6: Check leverage settings
    # =========================================================================
    print("\n" + "=" * 60)
    print("⚡ LEVERAGE SETTINGS")
    print("=" * 60)
    
    # Get current leverage for a symbol
    leverage = client.leverage.get("BTCUSDT")
    print(f"\n📊 Current BTC leverage: {leverage.leverage}x ({leverage.margin_type.value})")
    
    # Set leverage (uncomment to test)
    # client.leverage.set("BTCUSDT", leverage="10", margin_type="ISOLATED")
    # print("✅ Leverage set to 10x")
    
    # =========================================================================
    # Step 7: View open positions
    # =========================================================================
    print("\n" + "=" * 60)
    print("📊 OPEN POSITIONS")
    print("=" * 60)
    
    positions = client.positions.list_open()
    
    if positions:
        print(f"\n📍 You have {len(positions)} open position(s):")
        for pos in positions:
            emoji = "🟢" if pos.is_profitable else "🔴"
            direction = "LONG ↑" if pos.is_long else "SHORT ↓"
            print(f"\n   {emoji} {pos.symbol} ({direction})")
            print(f"      Quantity:    {pos.quantity}")
            print(f"      Entry:       ${pos.entry_price}")
            print(f"      Current:     ${pos.mark_price}")
            print(f"      PnL:         ${pos.unrealized_pnl} ({pos.pnl_percentage:.2f}%)")
            print(f"      Leverage:    {pos.leverage}x")
            if pos.stoploss_price:
                print(f"      Stop-Loss:   ${pos.stoploss_price}")
            if pos.takeprofit_price:
                print(f"      Take-Profit: ${pos.takeprofit_price}")
        
        # Get total PnL summary
        summary = client.positions.get_total_pnl()
        print(f"\n   📊 Total Unrealized PnL: ${summary['total_unrealized_pnl']:.2f}")
        print(f"   📊 Total Margin Used:    ${summary['total_margin']:.2f}")
    else:
        print("\n   No open positions.")
    
    # =========================================================================
    # Step 8: View open orders
    # =========================================================================
    print("\n" + "=" * 60)
    print("📝 OPEN ORDERS")
    print("=" * 60)
    
    orders = client.orders.list_open()
    
    if orders:
        print(f"\n📍 You have {len(orders)} open order(s):")
        for order in orders:
            print(f"   • {order.symbol}: {order.order_type.value} {order.quantity} @ ${order.price}")
    else:
        print("\n   No open orders.")
    
    # =========================================================================
    # Step 9: Example of placing an order (COMMENTED OUT FOR SAFETY)
    # =========================================================================
    print("\n" + "=" * 60)
    print("🎯 PLACING ORDERS")
    print("=" * 60)
    print("""
    # Uncomment the code below to place real orders:
    
    # Market order (executes immediately)
    order = client.orders.create_market_order(
        symbol="BTCUSDT",
        side="LONG",
        quantity="0.001",
        leverage="5"
    )
    print(f"Order placed: {order.order_id}")
    
    # Limit order (executes when price reaches target)
    order = client.orders.create_limit_order(
        symbol="BTCUSDT",
        side="LONG",
        quantity="0.001",
        price="90000",
        leverage="5"
    )
    
    # Order with stop-loss and take-profit
    order = client.orders.create_market_order(
        symbol="ETHUSDT",
        side="LONG",
        quantity="0.01",
        leverage="10",
        stoploss_price="3000",
        takeprofit_price="4500"
    )
    
    # Order by USD amount (SDK calculates quantity)
    order = client.orders.create_market_order_with_amount(
        symbol="BTCUSDT",
        side="LONG",
        amount="100",  # $100 worth of BTC
        leverage="5"
    )
    """)
    
    # =========================================================================
    # Step 10: Error handling example
    # =========================================================================
    print("\n" + "=" * 60)
    print("🛡️ ERROR HANDLING")
    print("=" * 60)
    print("""
    from mudrex import (
        MudrexClient,
        MudrexAPIError,
        MudrexAuthenticationError,
        MudrexRateLimitError,
        MudrexValidationError,
        MudrexInsufficientBalanceError,
        MudrexNotFoundError,
    )
    
    try:
        # Your trading code here
        order = client.orders.create_market_order(...)
        
    except MudrexAuthenticationError as e:
        # Invalid or expired API key
        print(f"Auth error: {e}")
        
    except MudrexInsufficientBalanceError as e:
        # Not enough funds
        print(f"Need more funds: {e}")
        
    except MudrexValidationError as e:
        # Invalid parameters
        print(f"Invalid request: {e}")
        
    except MudrexRateLimitError as e:
        # Too many requests - wait and retry
        print(f"Rate limited: {e}")
        print(f"Retry after: {e.retry_after} seconds")
        
    except MudrexNotFoundError as e:
        # Asset/order/position not found
        print(f"Not found: {e}")
        
    except MudrexAPIError as e:
        # Any other API error
        print(f"API error: {e}")
    """)
    
    # =========================================================================
    # Done!
    # =========================================================================
    print("\n" + "=" * 60)
    print("✅ QUICKSTART COMPLETE!")
    print("=" * 60)
    print("""
    📚 Next steps:
    
    1. Transfer funds to futures wallet:
       client.wallet.transfer_to_futures("100")
    
    2. Set leverage before trading:
       client.leverage.set("BTCUSDT", "10")
    
    3. Place your first order:
       order = client.orders.create_market_order(
           symbol="BTCUSDT",
           side="LONG",
           quantity="0.001",
           leverage="10"
       )
    
    4. Monitor your position:
       positions = client.positions.list_open()
    
    5. Close when ready:
       client.positions.close(position_id)
    
    📖 Full docs: https://docs.trade.mudrex.com
    💻 GitHub: https://github.com/DecentralizedJM/mudrex-trading-sdk
    """)


if __name__ == "__main__":
    main()
