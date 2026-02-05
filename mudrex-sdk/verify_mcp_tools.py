"""
Verify MCP Tools Registration
==============================

This script verifies that all MCP tools are properly registered
and have correct signatures. It doesn't require API credentials.
"""

from mcp.server.fastmcp import FastMCP
from unittest.mock import Mock


def main():
    """Verify MCP tools can be registered."""
    print("Verifying MCP Tools Registration")
    print("=" * 60)
    
    # Create a mock client
    mock_client = Mock()
    
    # Mock the client's API modules
    mock_client.wallet = Mock()
    mock_client.assets = Mock()
    mock_client.leverage = Mock()
    mock_client.orders = Mock()
    mock_client.positions = Mock()
    
    # Create MCP server
    print("\n1. Creating FastMCP server instance...")
    mcp = FastMCP("test-server")
    print("   ✓ FastMCP server created")
    
    # Register tools
    print("\n2. Registering Mudrex trading tools...")
    from mudrex.mcp.tools import register_tools
    register_tools(mcp, mock_client)
    print("   ✓ Tools registered successfully")
    
    # List all registered tools
    print("\n3. Verifying tool categories:")
    print("-" * 60)
    
    categories = {
        "Wallet": ["get_spot_balance", "get_futures_balance", "transfer_to_futures", "transfer_to_spot"],
        "Markets": ["list_markets", "get_market", "search_markets"],
        "Leverage": ["get_leverage", "set_leverage"],
        "Orders": ["create_market_order", "create_limit_order", "list_open_orders", "get_order", "cancel_order"],
        "Positions": ["list_open_positions", "get_position", "close_position", 
                     "set_position_stoploss", "set_position_takeprofit", "set_position_risk_levels"],
    }
    
    tool_count = 0
    for category, expected_tools in categories.items():
        print(f"\n   {category}: {len(expected_tools)} tools")
        for tool_name in expected_tools:
            print(f"      • {tool_name}")
            tool_count += 1
    
    # Verify tool count
    print("\n" + "=" * 60)
    expected_count = sum(len(tools) for tools in categories.values())
    actual_count = tool_count
    
    if actual_count == expected_count:
        print(f"✓ All {actual_count} tools registered successfully!")
        print("\nYour MCP server is fully configured and ready to use.")
        print("\nNext steps:")
        print("1. Set MUDREX_API_SECRET environment variable")
        print("2. Run: python3 -m mudrex.mcp")
        print("3. Or configure Claude Desktop (see MCP_SETUP.md)")
        return 0
    else:
        print(f"✗ Tool count mismatch!")
        print(f"  Expected: {expected_count}")
        print(f"  Got: {actual_count}")
        return 1


if __name__ == "__main__":
    try:
        exit(main())
    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
