"""
Local Development Runner
========================

Run the Supertrend Mudrex Trading Bot locally for testing and development.
Supports dry-run mode, continuous execution, and local file-based state.
"""

import sys
import os
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add local path for imports
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mudrex-sdk'))

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from config import Config, get_config
from supertrend_mudrex_bot import SupertrendMudrexBot


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for local development."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("bot.log"),
        ]
    )


class LocalStateManager:
    """Manages bot state in local JSON file."""
    
    def __init__(self, filepath: str = "bot_state.json"):
        self.filepath = Path(filepath)
    
    def load(self) -> dict:
        """Load state from file."""
        if self.filepath.exists():
            with open(self.filepath, "r") as f:
                return json.load(f)
        return {}
    
    def save(self, state: dict) -> None:
        """Save state to file."""
        with open(self.filepath, "w") as f:
            json.dump(state, f, indent=2)
        print(f"State saved to {self.filepath}")


def print_banner():
    """Print ASCII banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║   ███████╗██╗   ██╗██████╗ ███████╗██████╗ ████████╗██████╗   ║
║   ██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██╔══██╗  ║
║   ███████╗██║   ██║██████╔╝█████╗  ██████╔╝   ██║   ██████╔╝  ║
║   ╚════██║██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗   ██║   ██╔══██╗  ║
║   ███████║╚██████╔╝██║     ███████╗██║  ██║   ██║   ██║  ██║  ║
║   ╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝  ║
║           + Mudrex Futures Trading Bot                        ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_config(config: Config) -> None:
    """Print current configuration."""
    print("\n📊 Configuration:")
    print(f"  ├── Symbols: {', '.join(config.trading.symbols)}")
    print(f"  ├── Timeframe: {config.trading.timeframe}")
    print(f"  ├── Leverage: {config.trading.leverage}x")
    print(f"  ├── Margin: {config.strategy.margin_pct * 100:.1f}%")
    print(f"  ├── Dry Run: {'Yes ✅' if config.trading.dry_run else 'No ❌'}")
    print(f"  └── Max Positions: {config.trading.max_positions}")
    
    print("\n📈 Strategy Parameters:")
    print(f"  ├── ATR Period: {config.strategy.atr_period}")
    print(f"  ├── Supertrend Factor: {config.strategy.factor}")
    print(f"  ├── Risk ATR: {config.strategy.risk_atr_len} × {config.strategy.risk_atr_mult}")
    print(f"  ├── TSL ATR: {config.strategy.tsl_atr_len} × {config.strategy.tsl_mult}")
    print(f"  └── TP Risk:Reward: 1:{config.strategy.tp_rr}")
    print()


def run_once(bot: SupertrendMudrexBot, state_manager: LocalStateManager) -> bool:
    """Run one execution cycle."""
    # Load state
    state = state_manager.load()
    bot.load_state(state)
    
    # Execute
    result = bot.run_once()
    
    # Save state
    new_state = bot.save_state()
    state_manager.save(new_state)
    
    # Print summary
    print("\n📋 Execution Summary:")
    print(f"  ├── Success: {'✅' if result.success else '❌'}")
    print(f"  ├── Symbols Processed: {result.symbols_processed}")
    print(f"  ├── Signals Generated: {result.signals_generated}")
    print(f"  ├── Trades Executed: {result.trades_executed}")
    print(f"  ├── TSL Updates: {result.tsl_updates}")
    
    if result.errors:
        print(f"  └── Errors:")
        for error in result.errors:
            print(f"      ├── {error}")
    else:
        print(f"  └── Errors: None")
    
    print()
    return result.success


def run_continuous(
    bot: SupertrendMudrexBot,
    state_manager: LocalStateManager,
    interval: int,
) -> None:
    """Run continuously at specified interval."""
    import time
    
    print(f"🔄 Running continuously every {interval} seconds")
    print("   Press Ctrl+C to stop\n")
    
    iteration = 0
    while True:
        iteration += 1
        print(f"\n{'='*60}")
        print(f"Iteration #{iteration} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        try:
            run_once(bot, state_manager)
        except KeyboardInterrupt:
            print("\n⏹️  Stopping bot...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            logging.exception("Bot error")
        
        print(f"💤 Sleeping for {interval} seconds...")
        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n⏹️  Stopping bot...")
            break


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Supertrend + Mudrex Trading Bot - Local Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run once in dry-run mode
  python run_local.py --dry-run
  
  # Run continuously every 5 minutes
  python run_local.py --continuous --interval 300
  
  # Run with specific symbols
  python run_local.py --symbols BTCUSDT ETHUSDT SOLUSDT
  
  # Run with custom timeframe
  python run_local.py --timeframe 15m
        """
    )
    
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Run in dry-run mode (no real trades)"
    )
    parser.add_argument(
        "--continuous", "-c",
        action="store_true",
        help="Run continuously at specified interval"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=300,
        help="Interval in seconds for continuous mode (default: 300)"
    )
    parser.add_argument(
        "--symbols", "-s",
        nargs="+",
        help="Trading symbols to process (e.g., BTCUSDT ETHUSDT)"
    )
    parser.add_argument(
        "--timeframe", "-t",
        type=str,
        help="OHLCV timeframe (e.g., 1m, 5m, 15m, 1h)"
    )
    parser.add_argument(
        "--leverage", "-l",
        type=str,
        help="Leverage to use (e.g., 5, 10, 20)"
    )
    parser.add_argument(
        "--state-file",
        type=str,
        default="bot_state.json",
        help="Path to state file (default: bot_state.json)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Print banner
    print_banner()
    
    # Load config
    config = get_config()
    
    # Apply overrides
    if args.dry_run:
        config.trading.dry_run = True
    if args.symbols:
        config.trading.symbols = args.symbols
    if args.timeframe:
        config.trading.timeframe = args.timeframe
    if args.leverage:
        config.trading.leverage = args.leverage
    
    # Validate config
    try:
        config.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nMake sure to set MUDREX_API_SECRET environment variable:")
        print("  export MUDREX_API_SECRET='your-api-secret'")
        print("\nOr create a .env file with your configuration.")
        sys.exit(1)
    
    # Print config
    print_config(config)
    
    # Create state manager
    state_manager = LocalStateManager(args.state_file)
    
    # Create bot
    bot = SupertrendMudrexBot(config)
    
    try:
        if args.continuous:
            run_continuous(bot, state_manager, args.interval)
        else:
            run_once(bot, state_manager)
    finally:
        bot.close()
        print("👋 Bot closed")


if __name__ == "__main__":
    main()
