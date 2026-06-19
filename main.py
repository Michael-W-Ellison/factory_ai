"""
Main entry point for Recycling Factory game.

To run the game:
    python main.py
"""

import sys
import pygame
import config
from src.core.logger import setup_logging, get_logger, exception as log_exception
from src.core.game import Game


def main():
    """Initialize and run the game."""
    # Initialize logging first
    setup_logging(
        level=config.LOG_LEVEL,
        log_file=config.LOG_FILE if config.LOG_TO_FILE else None,
        log_dir=config.LOG_DIR,
        console=True,
        debug_format=config.DEBUG_MODE
    )

    logger = get_logger('main')
    logger.info("Starting Recycling Factory...")
    logger.info(f"Log level: {config.LOG_LEVEL}")

    try:
        game = Game()
        game.run()
        logger.info("Game exited normally")
    except KeyboardInterrupt:
        logger.info("Game interrupted by user")
        return 0
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        log_exception("Unhandled exception in main")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
