"""
Main entry point for Recycling Factory game.

To run the game:
    python main.py
"""

import sys
import pygame
from src.core.game import Game


def main():
    """Initialize and run the game."""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
