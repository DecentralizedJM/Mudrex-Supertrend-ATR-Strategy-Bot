"""
Main Entrypoint
===============
Production entrypoint for Railway deployment.
Runs the bot continuously with persistent state storage.
"""

import os
import sys
import time
import logging
import signal
from pathlib import Path
from datetime import datetime

# Add mudrex-sdk to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mudrex-sdk'))

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from config import get_config
from supertrend_mudrex_bot import SupertrendMudrexBot
from mudrex_adapter import PositionState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("main")

class StateManager:
    """Manages bot state in a persistent JSON file."""
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        # Ensure directory exists
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> dict:
        """Load state from file."""
        if self.filepath.exists():
            try:
                import json
                with open(self.filepath, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
        return {}
    
    def save(self, state: dict) -> None:
        """Save state to file."""
        try:
            import json
            # Atomic write to prevent corruption
            tmp_path = self.filepath.with_suffix(".tmp")
            with open(tmp_path, "w") as f:
                json.dump(state, f, indent=2)
            tmp_path.replace(self.filepath)
            logger.debug(f"State saved to {self.filepath}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

def handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, stopping bot...")
    sys.exit(0)

def main():
    """Main execution loop."""
    # Register signal handlers
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)
    
    logger.info("Starting Mudrex Supertrend Bot (Railway Edition)")
    
    # Load configuration
    try:
        config = get_config()
        config.validate()
    except ValueError as e:
        logger.critical(f"Configuration error: {e}")
        sys.exit(1)
        
    # Log startup config
    logger.info(f"Symbols: {config.trading.symbols}")
    logger.info(f"Mode: {'DRY RUN' if config.trading.dry_run else 'LIVE TRADING'}")
    
    # Initialize state manager (Railway persistent volume)
    # Use /app/data for persistent storage if available, else local
    data_dir = os.environ.get("RAILWAY_VOLUME_MOUNT_PATH", "/app/data")
    state_file = os.path.join(data_dir, "bot_state.json")
    state_manager = StateManager(state_file)
    logger.info(f"State file: {state_file}")
    
    # Initialize bot
    bot = SupertrendMudrexBot(config)
    
    # Load initial state
    state = state_manager.load()
    if state:
        bot.load_state(state)
        logger.info("Restored previous state")
    
    # Main loop
    interval = 300  # 5 minutes default
    
    try:
        while True:
            start_time = time.time()
            
            try:
                # Run one cycle
                result = bot.run_once()
                
                # Save state immediately after run
                new_state = bot.save_state()
                state_manager.save(new_state)
                
            except Exception as e:
                logger.exception(f"Error in execution cycle: {e}")
            
            # Sleep logic
            elapsed = time.time() - start_time
            sleep_time = max(10, interval - elapsed)
            logger.info(f"Sleeping for {sleep_time:.1f} seconds...")
            time.sleep(sleep_time)
            
    finally:
        bot.close()
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    main()
