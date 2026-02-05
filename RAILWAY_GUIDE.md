# Railway Deployment Guide

This bot is optimized for deployment on [Railway](https://railway.app/).

## 🚀 Quick Deploy

1. **New Project**: In Railway, create a new project from this GitHub repo.
2. **Variables**: Add the required environment variables.
3. **Volume**: Add a persistent volume for state storage (Optional but recommended).

## 🛠️ Environment Variables

Copy these into your Railway service settings:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MUDREX_API_SECRET` | **YES** | - | Your Mudrex API Secret Key |
| `TRADING_SYMBOLS` | **YES** | - | Comma-separated symbols (e.g., `BTCUSDT,ETHUSDT`) |
| `TRADING_DRY_RUN` | No | `true` | Set to `false` to execute real trades |
| `TRADING_LEVERAGE` | No | `5` | Leverage (1-125) |
| `TRADING_TIMEFRAME` | No | `5m` | OHLCV Timeframe |
| `PYTHONUNBUFFERED` | No | `1` | Ensures logs show up immediately |

## 💾 Persistent Storage (State)

To prevent the bot from forgetting open positions if it restarts, you should add a **Volume** in Railway.

1. Go to your Railway Service.
2. Click **Volumes** tab.
3. Create a new volume.
4. Mount path: `/app/data`

The bot will automatically check `/app/data/bot_state.json` for existing state.

## 📋 Docker Configuration

The included `Dockerfile` is set up for:
- **Base Image**: `python:3.10-slim`
- **Entrypoint**: `python main.py`
- **Dependencies**: Installs from `requirements.txt` + `mudrex-sdk`

No additional Railway build inputs are needed.
