"""
Example: Running the Mudrex MCP Server
=======================================

This example shows how to run the built-in MCP server for Mudrex trading.

The MCP server allows you to interact with Mudrex trading API through
Claude Desktop or other MCP clients using natural language.

Setup:
------
1. Install with MCP support:
   pip install -e ".[mcp]"

2. Set your API credentials:
   export MUDREX_API_SECRET="your-api-secret"

3. Run this script:
   python examples/mcp_example.py

   Or run the server directly:
   python -m mudrex.mcp

Usage with Claude Desktop:
---------------------------
Add this to your Claude Desktop config:

{
  "mcpServers": {
    "mudrex": {
      "command": "python",
      "args": ["-m", "mudrex.mcp"],
      "env": {
        "MUDREX_API_SECRET": "your-secret-here"
      }
    }
  }
}

Then you can interact with Claude:
- "Check my futures balance"
- "List all markets"
- "Buy 100 XRPUSDT with 5x leverage"
- "Show my open positions"
"""

import os
from mudrex.mcp import run_server

if __name__ == "__main__":
    # Check if API secret is set
    if not os.getenv("MUDREX_API_SECRET"):
        print("Error: MUDREX_API_SECRET environment variable not set")
        print("\nUsage:")
        print("  export MUDREX_API_SECRET='your-api-secret'")
        print("  python3 examples/mcp_example.py")
        exit(1)
    
    print("Starting Mudrex MCP Server...")
    print("The server runs over STDIO and follows the MCP protocol.")
    print("Connect from Claude Desktop or other MCP clients.")
    print("\nPress Ctrl+C to stop the server.\n")
    
    # Run the server (this blocks until Ctrl+C)
    run_server()
