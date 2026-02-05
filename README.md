# Mudrex Supertrend Trading Bot (Railway Optimized)

Automated futures trading bot using the **Supertrend TSL Strategy** and **Mudrex SDK**.

## 🚀 Strategy Configuration (Hardcoded)

This bot follows a strict strategy for maximum consistency:

- **Indicator**: Supertrend (ATR: 10, Factor: 3.0)
- **Timeframe**: 5m
- **Risk management**:
  - **Stop Loss**: 2.0x ATR
  - **Trailing Stop Loss**: 2.0x ATR
  - **Take Profit**: Strictly **1:2 Risk:Reward** ratio
- **Position Sizing**: **2% Margin** per trade (Current Wallet Balance × 0.02)
- **Pairs**: **ALL USDT pairs** active on Mudrex (automatically discovered)

## 📁 Environment Variables

Only the API Key is required. All other parameters are hardcoded.

| Variable | Required | Description |
|----------|----------|-------------|
| `MUDREX_API_SECRET` | **YES** | Your Mudrex API Secret Key |
| `TRADING_DRY_RUN` | No | Set to `true` for testing (default: `false`) |

## 🛠️ Deploy to Railway

1. **Fork/Clone** this repo to your GitHub.
2. **Create New Project** on Railway from GitHub.
3. **Add Variables**: Set your `MUDREX_API_SECRET`.
4. **Persistent State**: Add a Volume and mount it at `/app/data` to persist position state across restarts.

Check [RAILWAY_GUIDE.md](RAILWAY_GUIDE.md) for detailed Railway setup.
