# Mudrex MCP Quick Reference

Quick reference for trading with Claude Desktop using the Mudrex MCP server.

## Setup (One-Time)

1. Install: `pip install "mudrex-trading-sdk[mcp]"`
2. Add to Claude Desktop config:
```json
{
  "mcpServers": {
    "mudrex": {
      "command": "python3",
      "args": ["-m", "mudrex.mcp"],
      "env": {"MUDREX_API_SECRET": "your-secret"}
    }
  }
}
```
3. Restart Claude Desktop

## Common Commands

### Check Account Balance
```
What's my futures balance?
Show my spot wallet balance
How much margin do I have available?
```

### Discover Markets
```
List all tradable markets
Search for BTC trading pairs
Get specifications for XRPUSDT
What's the minimum order size for ETHUSDT?
```

### View Open Positions
```
Show my open positions
What's my current PnL?
List all my active trades
```

### Place Market Orders
```
Buy 100 XRPUSDT with 5x leverage
Open a long position on BTCUSDT with 0.001 quantity and 10x leverage
Short 1000 DOGEUSDT with 3x leverage
```

### Place Limit Orders
```
Place a limit buy for 50 XRPUSDT at $2.00 with 5x leverage
Create a limit sell order for BTCUSDT at $105,000
```

### Orders with Risk Management
```
Buy 100 XRPUSDT with 5x leverage, set stop-loss at $2.00 and take-profit at $3.50
Place a long order on ETHUSDT with stop-loss at $3,000
```

### View Orders
```
Show my open orders
List all unfilled orders
Get details for order abc123
```

### Cancel Orders
```
Cancel order xyz789
Cancel all my open orders for BTCUSDT
```

### Manage Positions
```
Close my XRPUSDT position
Set stop-loss at $95,000 for my BTC position
Set take-profit at $110,000 for position abc123
Update my ETHUSDT position with SL at $3,000 and TP at $4,500
```

### Set Leverage
```
Set 10x leverage for BTCUSDT
Change leverage to 5x for XRPUSDT with isolated margin
What's my current leverage for ETHUSDT?
```

### Transfer Funds
```
Transfer $100 from spot to futures wallet
Move $50 from futures to spot wallet
```

## Tips

- **Always specify quantity** when placing orders
- **Include leverage** if you want more than 1x
- **Set stop-losses** to manage risk
- **Start small** when testing
- **Check balance first** before trading
- **Monitor open positions** regularly

## Symbol Format

Use standard trading symbols:
- Bitcoin: `BTCUSDT`
- Ethereum: `ETHUSDT`
- XRP: `XRPUSDT`
- Solana: `SOLUSDT`
- Dogecoin: `DOGEUSDT`

Search if unsure: "Search for Cardano trading pairs"

## Risk Management

Always include risk parameters:
- `stoploss_price` - Exit if price drops here (for longs)
- `takeprofit_price` - Exit if price reaches here

Example:
> "Buy 100 XRPUSDT with 5x leverage, stop-loss at $2.00, take-profit at $3.50"

## Troubleshooting

**"Tool not found"**
- Restart Claude Desktop
- Verify MCP server config

**"Authentication failed"**
- Check MUDREX_API_SECRET is correct
- Generate new API key if needed

**"Insufficient balance"**
- Check balance first: "What's my futures balance?"
- Transfer funds if needed: "Transfer $100 to futures"

**Rate limited**
- Wait 30-60 seconds
- Avoid rapid consecutive requests

## Safety Checklist

Before trading:
- ✅ Check current balance
- ✅ Verify symbol is correct
- ✅ Start with small amounts
- ✅ Set stop-loss levels
- ✅ Understand leverage risks
- ✅ Monitor positions actively

## Support

- Full docs: See `MCP_SETUP.md`
- Test setup: Run `python3 test_mcp_setup.py`
- Issues: [GitHub Issues](https://github.com/DecentralizedJM/mudrex-trading-sdk/issues)

---

**⚠️ Trading Risk Warning**: Cryptocurrency trading involves substantial risk. Only trade with funds you can afford to lose. Always use proper risk management.
