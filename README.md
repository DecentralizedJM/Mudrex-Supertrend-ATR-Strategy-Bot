# Supertrend + Mudrex Trading Bot

Automated trading bot that combines the **Supertrend TSL Strategy** with the **Mudrex Futures Trading SDK**, ready for AWS Lambda deployment.

## 🎯 Features

- **Supertrend Strategy**: Uses Supertrend indicator for trend detection and entry signals
- **Smart Risk Management**: ATR-based stop loss and take profit levels
- **Trailing Stop Loss**: Dynamic TSL that follows price movement
- **Mudrex Integration**: Direct order execution via Mudrex Futures API
- **AWS Ready**: Lambda + EventBridge for scheduled execution
- **State Persistence**: S3 storage for position tracking across invocations

## 📁 Project Structure

```
mudrex-supertrend-integration/
├── config.py              # Configuration management
├── strategy.py            # Supertrend TSL Strategy implementation
├── mudrex_adapter.py      # Bridge between strategy and Mudrex SDK
├── supertrend_mudrex_bot.py  # Main trading bot
├── lambda_handler.py      # AWS Lambda entry point
├── run_local.py           # Local development runner
├── requirements.txt       # Python dependencies
├── serverless.yml         # AWS deployment configuration
├── Dockerfile             # Container image for Lambda
├── .env.example           # Environment variables template
└── mudrex-sdk/            # Mudrex Trading SDK
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd mudrex-supertrend-integration

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Mudrex SDK locally
pip install -e ./mudrex-sdk
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your settings
nano .env
```

**Required settings:**
- `MUDREX_API_SECRET`: Your Mudrex API secret key
- `TRADING_SYMBOLS`: Comma-separated symbols (e.g., `BTCUSDT,ETHUSDT`)

### 3. Run Locally

```bash
# Dry run mode (no real trades)
python run_local.py --dry-run

# Run with specific symbols
python run_local.py --dry-run --symbols BTCUSDT ETHUSDT

# Continuous mode (runs every 5 minutes)
python run_local.py --dry-run --continuous --interval 300
```

### 4. Run with Real Trades

```bash
# Set dry run to false in .env
# TRADING_DRY_RUN=false

# Single execution
python run_local.py

# Continuous execution
python run_local.py --continuous
```

## ☁️ AWS Deployment

### Prerequisites

- AWS CLI configured with appropriate permissions
- Node.js and npm installed
- Serverless Framework installed

```bash
npm install -g serverless
npm install --save-dev serverless-python-requirements
```

### Deploy

```bash
# Set environment variables
export MUDREX_API_SECRET="your-api-secret"
export TRADING_SYMBOLS="BTCUSDT,ETHUSDT"
export TRADING_DRY_RUN="false"

# Deploy to AWS
serverless deploy

# Deploy to specific stage
serverless deploy --stage prod
```

### Monitor

```bash
# View logs
serverless logs -f tradingBot --tail

# Invoke manually
serverless invoke -f tradingBot
```

### Alternative: Docker Deployment

```bash
# Build image
docker build -t supertrend-mudrex-bot .

# Run locally
docker run -e MUDREX_API_SECRET="..." supertrend-mudrex-bot

# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker tag supertrend-mudrex-bot:latest <account>.dkr.ecr.<region>.amazonaws.com/supertrend-mudrex-bot:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/supertrend-mudrex-bot:latest
```

## ⚙️ Configuration

### Strategy Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `STRATEGY_ATR_PERIOD` | 10 | Supertrend ATR period |
| `STRATEGY_FACTOR` | 3.0 | Supertrend multiplier |
| `STRATEGY_RISK_ATR_LEN` | 14 | ATR period for stop loss |
| `STRATEGY_RISK_ATR_MULT` | 2.0 | ATR multiplier for SL |
| `STRATEGY_TSL_ATR_LEN` | 14 | ATR period for trailing stop |
| `STRATEGY_TSL_MULT` | 2.0 | TSL ATR multiplier |
| `STRATEGY_TP_RR` | 2.0 | Take profit R:R ratio |
| `STRATEGY_POSITION_SIZE_PCT` | 0.15 | Position size (% of balance) |

### Trading Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `TRADING_SYMBOLS` | BTCUSDT,ETHUSDT | Symbols to trade |
| `TRADING_LEVERAGE` | 5 | Leverage to use |
| `TRADING_TIMEFRAME` | 5m | OHLCV timeframe |
| `TRADING_MAX_POSITIONS` | 3 | Maximum concurrent positions |
| `TRADING_DRY_RUN` | true | Dry run mode |

## 📊 How It Works

1. **Fetch Data**: OHLCV candles are fetched from Binance via CCXT
2. **Generate Signal**: Supertrend indicator detects trend changes
3. **Calculate Levels**: ATR-based SL/TP levels are computed
4. **Execute Trade**: Order is placed via Mudrex SDK with risk parameters
5. **Manage Position**: Trailing stop is updated as price moves favorably
6. **Close Position**: Position closes on opposite signal or SL/TP hit

```
Supertrend Bullish Crossover → LONG Signal
├── Entry: Current close price
├── Stop Loss: Entry - (ATR × risk_mult)
├── Take Profit: Entry + (Risk × tp_rr)
└── TSL: Trails behind highest price by (ATR × tsl_mult)
```

## ⚠️ Disclaimer

This software is for educational purposes only. Cryptocurrency trading involves substantial risk of loss. Never trade with money you cannot afford to lose. Past performance is not indicative of future results.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
