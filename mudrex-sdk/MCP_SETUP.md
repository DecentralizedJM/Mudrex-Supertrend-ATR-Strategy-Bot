# Mudrex MCP Server Setup Guide

## What is MCP?

The **Model Context Protocol (MCP)** allows AI assistants like Claude Desktop to interact with external tools and services. This SDK includes a built-in MCP server that exposes Mudrex trading functionality to Claude, enabling you to trade with natural language.

## Features

- **20 Trading Tools**: Execute trades, manage positions, check balances, and more
- **Zero External Dependencies**: Runs locally using the Python SDK you already have
- **Natural Language Trading**: Interact with Claude using plain English
- **Real-time Market Data**: Access 500+ trading pairs with live prices
- **Risk Management**: Set stop-loss and take-profit levels through conversation

## Quick Start

### 1. Install with MCP Support

```bash
# From GitHub
pip install "git+https://github.com/DecentralizedJM/mudrex-trading-sdk.git#egg=mudrex-trading-sdk[mcp]"

# Or from local clone
cd mudrex-trading-sdk
pip install -e ".[mcp]"
```

### 2. Get Your API Secret

1. Visit [Mudrex API Settings](https://trade.mudrex.com/settings/api-keys)
2. Complete KYC verification (PAN & Aadhaar)
3. Enable 2FA (TOTP)
4. Generate a new API key
5. **Save the secret immediately** (shown only once!)

### 3. Configure Claude Desktop

Edit your Claude Desktop configuration file:

**macOS:**
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```cmd
notepad %APPDATA%\Claude\claude_desktop_config.json
```

Add the Mudrex MCP server:

```json
{
  "mcpServers": {
    "mudrex": {
      "command": "python3",
      "args": ["-m", "mudrex.mcp"],
      "env": {
        "MUDREX_API_SECRET": "your-api-secret-here"
      }
    }
  }
}
```

**Alternative with UV:**

If you use `uv` for Python package management:

```json
{
  "mcpServers": {
    "mudrex": {
      "command": "uv",
      "args": ["run", "--with", "mudrex-trading-sdk[mcp]", "python", "-m", "mudrex.mcp"],
      "env": {
        "MUDREX_API_SECRET": "your-api-secret-here"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

Close and reopen Claude Desktop to load the new MCP server.

### 5. Verify Connection

In Claude Desktop, you should see a 🔌 icon or indication that the MCP server is connected. Try asking:

> "Check my futures balance"

## Available Tools

The MCP server provides these categories of tools:

### Wallet Management (4 tools)
- `get_spot_balance` - Check spot wallet balance
- `get_futures_balance` - Check futures wallet balance and unrealized PnL
- `transfer_to_futures` - Transfer funds from spot to futures
- `transfer_to_spot` - Transfer funds from futures to spot

### Market Discovery (3 tools)
- `list_markets` - List all 500+ tradable futures pairs
- `get_market` - Get detailed specs for a specific symbol
- `search_markets` - Search markets by name (e.g., "BTC", "DOGE")

### Leverage Management (2 tools)
- `get_leverage` - Check current leverage settings
- `set_leverage` - Set leverage and margin type for a symbol

### Order Management (5 tools)
- `create_market_order` - Place market order (executes immediately)
- `create_limit_order` - Place limit order (executes at target price)
- `list_open_orders` - View all unfilled orders
- `get_order` - Get details of a specific order
- `cancel_order` - Cancel an open order

### Position Management (6 tools)
- `list_open_positions` - View all open positions with live PnL
- `get_position` - Get details of a specific position
- `close_position` - Fully close a position
- `set_position_stoploss` - Set stop-loss price
- `set_position_takeprofit` - Set take-profit price
- `set_position_risk_levels` - Set both SL and TP together

## Example Conversations

Here are some things you can ask Claude with the MCP server running:

### Check Account Status
```
You: What's my futures balance?
Claude: [Calls get_futures_balance tool] You have $1,234.56 in your futures wallet...
```

### Find Trading Opportunities
```
You: Search for all BTC trading pairs
Claude: [Calls search_markets tool] I found 3 BTC pairs: BTCUSDT, BTCUSD, BTC1000USDT...
```

### Place a Trade
```
You: Buy 100 XRPUSDT with 5x leverage and set a stop-loss at $2.00
Claude: [Calls create_market_order tool with appropriate parameters]
Order placed successfully! Order ID: abc123, Entry price: $2.45...
```

### Manage Positions
```
You: Show my open positions
Claude: [Calls list_open_positions tool] You have 2 open positions:
1. BTCUSDT: +$234.50 unrealized PnL (2.3%)
2. XRPUSDT: -$45.00 unrealized PnL (-0.9%)
```

### Risk Management
```
You: Set take-profit at $110,000 for my BTC position
Claude: [Calls set_position_takeprofit tool] Done! Your BTC position now has...
```

## Testing Standalone

You can test the MCP server without Claude Desktop:

```bash
# Set your API secret
export MUDREX_API_SECRET="your-secret"

# Run the server
python3 -m mudrex.mcp
```

The server will start and wait for MCP protocol messages over STDIO. Press Ctrl+C to stop.

## Verify Installation

Run the test script to check everything is properly set up:

```bash
python3 test_mcp_setup.py
```

Expected output:
```
Testing MCP Server Setup
==================================================
✓ FastMCP dependency is installed
✓ MCP module imports successfully
✓ MCP tools module imports successfully
✓ MCP server module imports successfully

==================================================
✓ All tests passed!
```

## Troubleshooting

### MCP Server Not Appearing in Claude

1. **Check the config file path** - Make sure you edited the correct file
2. **Verify JSON syntax** - Use a JSON validator to check for errors
3. **Check API secret** - Make sure it's the actual secret, not the API key name
4. **Restart Claude** - Fully quit and reopen Claude Desktop
5. **Check logs** - Look for errors in Claude Desktop logs

### Import Errors

If you see import errors when running `python3 -m mudrex.mcp`:

```bash
# Reinstall with MCP dependencies
pip install -e ".[mcp]" --force-reinstall
```

### "Command not found: python3"

Update your config to use the full path to python:

```bash
# Find your python path
which python3

# Use the full path in config
{
  "command": "/usr/local/bin/python3",  # or whatever path you found
  ...
}
```

### Rate Limiting

The Mudrex API has rate limits:
- 2 requests/second
- 50 requests/minute
- 1000 requests/hour
- 10000 requests/day

The SDK includes automatic rate limiting, but if you make many rapid requests through Claude, you may hit limits. Wait a moment and try again.

## Security Best Practices

1. **Never commit API secrets** to version control
2. **Use environment variables** for API credentials
3. **Rotate API keys regularly** on the Mudrex dashboard
4. **Monitor API activity** in your Mudrex account
5. **Start with small amounts** when testing
6. **Use stop-losses** for risk management

## Advanced Configuration

### Custom Base URL

If you need to use a different API endpoint:

```json
{
  "mcpServers": {
    "mudrex": {
      "command": "python3",
      "args": ["-m", "mudrex.mcp"],
      "env": {
        "MUDREX_API_SECRET": "your-secret",
        "MUDREX_BASE_URL": "https://custom-api.example.com"
      }
    }
  }
}
```

### Enable Debug Logging

```json
{
  "mcpServers": {
    "mudrex": {
      "command": "python3",
      "args": ["-m", "mudrex.mcp"],
      "env": {
        "MUDREX_API_SECRET": "your-secret",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## Programmatic Usage

You can also use the MCP server programmatically in your own code:

```python
from mudrex.mcp import create_server

# Create the server instance
mcp = create_server(api_secret="your-secret")

# The server is now ready to handle MCP requests
# You can inspect registered tools:
for tool_name in mcp._tools:
    print(f"Tool: {tool_name}")
```

## Resources

- [Model Context Protocol Docs](https://modelcontextprotocol.io)
- [Mudrex API Documentation](https://docs.trade.mudrex.com)
- [SDK GitHub Repository](https://github.com/DecentralizedJM/mudrex-trading-sdk)
- [Report Issues](https://github.com/DecentralizedJM/mudrex-trading-sdk/issues)

## Support

If you encounter issues:

1. Check this documentation first
2. Run the test script: `python3 test_mcp_setup.py`
3. Look at example usage: `examples/mcp_example.py`
4. File an issue on GitHub with error details

## Disclaimer

**Trading involves risk.** This tool executes real trades on your behalf when instructed through Claude. Always:
- Start with small amounts
- Use proper risk management (stop-losses)
- Understand what commands you're giving
- Never trade more than you can afford to lose
- Test thoroughly in small amounts first

The MCP server is provided as-is for educational purposes. The developers are not responsible for trading losses.
