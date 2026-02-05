"""
Async Trading Example
=====================

Demonstrates how to use the SDK with asyncio for concurrent operations.
Useful for high-frequency trading or monitoring multiple assets.

Note: The base SDK is synchronous, but this example shows how to
wrap it for async usage.
"""

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List

from mudrex import MudrexClient


# Thread pool for running sync operations
executor = ThreadPoolExecutor(max_workers=5)


async def run_sync(func, *args, **kwargs):
    """Run a synchronous function in a thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, lambda: func(*args, **kwargs))


class AsyncMudrexClient:
    """
    Async wrapper for MudrexClient.
    
    Example:
        >>> async with AsyncMudrexClient(api_secret="...") as client:
        ...     balance = await client.get_balance()
        ...     positions = await client.get_positions()
    """
    
    def __init__(self, api_secret: str):
        self._client = MudrexClient(api_secret=api_secret)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._client.close()
    
    async def get_spot_balance(self):
        """Get spot wallet balance asynchronously."""
        return await run_sync(self._client.wallet.get_spot_balance)
    
    async def get_futures_balance(self):
        """Get futures wallet balance asynchronously."""
        return await run_sync(self._client.wallet.get_futures_balance)
    
    async def list_assets(self):
        """List all assets asynchronously."""
        return await run_sync(self._client.assets.list_all)
    
    async def get_asset(self, asset_id: str):
        """Get asset details asynchronously."""
        return await run_sync(self._client.assets.get, asset_id)
    
    async def get_positions(self):
        """Get open positions asynchronously."""
        return await run_sync(self._client.positions.list_open)
    
    async def get_orders(self):
        """Get open orders asynchronously."""
        return await run_sync(self._client.orders.list_open)


async def monitor_multiple_assets(client: AsyncMudrexClient, assets: List[str]):
    """
    Monitor multiple assets concurrently.
    
    This demonstrates the power of async - we can fetch data for
    multiple assets at the same time instead of sequentially.
    """
    print(f"\n📊 Monitoring {len(assets)} assets concurrently...\n")
    
    # Fetch all asset details concurrently
    tasks = [client.get_asset(asset) for asset in assets]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for asset_id, result in zip(assets, results):
        if isinstance(result, Exception):
            print(f"❌ {asset_id}: Error - {result}")
        else:
            print(f"✅ {result.symbol}:")
            print(f"   Max Leverage: {result.max_leverage}x")
            print(f"   Min Qty: {result.min_quantity}")


async def dashboard(client: AsyncMudrexClient):
    """
    Display a real-time dashboard.
    
    Fetches balances, positions, and orders concurrently.
    """
    print("\n" + "=" * 50)
    print("📈 MUDREX TRADING DASHBOARD")
    print("=" * 50)
    
    # Fetch everything concurrently
    spot_balance, futures_balance, positions, orders = await asyncio.gather(
        client.get_spot_balance(),
        client.get_futures_balance(),
        client.get_positions(),
        client.get_orders(),
    )
    
    # Display balances
    print(f"\n💰 Balances:")
    print(f"   Spot:    ${spot_balance.available} available")
    print(f"   Futures: ${futures_balance.balance} (${futures_balance.available_transfer} transferable)")
    
    # Display positions
    print(f"\n📊 Open Positions: {len(positions)}")
    for pos in positions:
        pnl_emoji = "🟢" if float(pos.unrealized_pnl) >= 0 else "🔴"
        print(f"   {pnl_emoji} {pos.symbol}: {pos.side.value} {pos.quantity}")
        print(f"      Entry: ${pos.entry_price} → ${pos.mark_price}")
        print(f"      PnL: ${pos.unrealized_pnl} ({pos.pnl_percentage:.2f}%)")
    
    # Display orders
    print(f"\n📋 Open Orders: {len(orders)}")
    for order in orders:
        print(f"   • {order.symbol}: {order.order_type.value} {order.quantity} @ ${order.price}")
    
    print("\n" + "=" * 50)


async def main():
    """Main async function."""
    api_secret = os.environ.get("MUDREX_API_SECRET")
    
    if not api_secret:
        print("Please set MUDREX_API_SECRET environment variable")
        return
    
    async with AsyncMudrexClient(api_secret=api_secret) as client:
        # Monitor multiple assets
        await monitor_multiple_assets(client, ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
        
        # Show dashboard
        await dashboard(client)
        
        # Continuous monitoring example (uncomment to run)
        # while True:
        #     await dashboard(client)
        #     await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
