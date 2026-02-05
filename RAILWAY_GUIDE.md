# Railway Deployment Guide (Hardcoded Version)

This bot is specifically optimized for Railway and executes a fixed Supertrend strategy across all available USDT pairs.

## 📋 Railway Variables

Set these in your Railway service settings:

| Variable | Value | Description |
|----------|-------|-------------|
| `MUDREX_API_SECRET` | `your_secret_here` | **Required**: Your API key |
| `TRADING_DRY_RUN` | `false` | Set to `true` to simulate trades without real money |
| `PYTHONUNBUFFERED` | `1` | Ensures logs are visible in real-time |

## 💾 Persistent Storage (CRITICAL)

To ensure the bot remembers its open positions and trailing stop levels after a restart or deployment, you **must** use a Railway Volume.

1.  In Railway, go to your service dashboard.
2.  Navigate to the **Volumes** tab.
3.  Click **Create Volume**.
4.  Set the **Mount Path** to: `/app/data`

The bot is configured to store its state in `/app/data/bot_state.json`.

## 📈 Monitoring

The bot automatically discovers all active USDT trading pairs on Mudrex. It iterates through them every 5 minutes (standard cycle).

You can monitor the bot's activities via the Railway **Logs** tab. It will log every signal check, entry, and trailing stop update.
