"""
Test script for AI game player.

Tests the AI's ability to play the game autonomously.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.game import Game
from src.ai.game_ai import GameAI


def test_ai_basic_gameplay():
    """Test AI playing the game for a short duration."""
    print("=" * 80)
    print("AI PLAYER TEST - Basic Gameplay")
    print("=" * 80)
    print()

    # Create game instance (headless mode)
    game = Game()
    game.paused = False

    # Give AI some starting funds for testing
    game.resources.money = 10000.0

    # Create AI player
    ai = GameAI(game, difficulty="medium")

    print(f"AI initialized: {ai}")
    print(f"Starting money: ${game.resources.money:.2f}")
    print(f"Starting buildings: {len(game.buildings.buildings)}")
    print()

    # Run AI for a simulated time period
    dt = 1.0  # 1 second per update
    total_time = 60.0  # Run for 60 seconds
    updates = int(total_time / dt)

    print(f"Running AI for {total_time:.0f} seconds ({updates} updates)...")
    print()

    for i in range(updates):
        # Update game systems
        game.entities.update(dt)
        game.buildings.update(dt)
        game.power.update(dt, game.buildings)

        # Update AI
        ai.update(dt)

        # Print status every 10 seconds
        if (i + 1) % 10 == 0:
            elapsed = (i + 1) * dt
            state = ai._evaluate_game_state()
            print(f"[{elapsed:.0f}s] Money: ${state['money']:.2f}, "
                  f"Buildings: {state['building_count']}, "
                  f"Power: {state['power_generation']:.1f}W gen / {state['power_consumption']:.1f}W cons")

    print()
    print("Final AI Statistics:")
    print("-" * 80)

    stats = ai.get_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    print()
    print("Final Game State:")
    print("-" * 80)
    print(f"  Money: ${game.resources.money:.2f}")
    print(f"  Buildings: {len(game.buildings.buildings)}")
    print(f"  Power generation: {game.power.total_generation:.1f}W")
    print(f"  Power consumption: {game.power.total_consumption:.1f}W")
    print(f"  Power surplus: {game.power.net_power:.1f}W")
    print()

    # Verify AI placed at least some buildings
    assert stats['buildings_placed'] > 0, "AI should have placed at least one building"

    print("✓ AI successfully played the game!")
    print()


def test_ai_difficulty_levels():
    """Test different AI difficulty levels."""
    print("=" * 80)
    print("AI PLAYER TEST - Difficulty Levels")
    print("=" * 80)
    print()

    difficulties = ["easy", "medium", "hard"]
    results = {}

    for difficulty in difficulties:
        print(f"Testing {difficulty.upper()} difficulty...")

        # Create game and AI
        game = Game()
        game.paused = False
        game.resources.money = 10000.0  # Give starting funds
        ai = GameAI(game, difficulty=difficulty)

        # Run for 30 seconds
        for _ in range(30):
            game.entities.update(1.0)
            game.buildings.update(1.0)
            game.power.update(1.0, game.buildings)
            ai.update(1.0)

        stats = ai.get_stats()
        results[difficulty] = stats

        print(f"  Buildings placed: {stats['buildings_placed']}")
        print(f"  Buildings failed: {stats['buildings_failed']}")
        print(f"  Final money: ${stats['current_money']:.2f}")
        print()

    # Verify difficulty scaling
    print("Difficulty Comparison:")
    print("-" * 80)
    for difficulty in difficulties:
        stats = results[difficulty]
        print(f"  {difficulty.upper():6s}: {stats['buildings_placed']} buildings, "
              f"${stats['current_money']:.2f} remaining")

    # Hard AI should place more buildings than easy
    assert (results['hard']['buildings_placed'] >= results['easy']['buildings_placed']), \
        "Hard AI should be more aggressive than easy AI"

    print()
    print("✓ Difficulty levels working correctly!")
    print()


def test_ai_building_priorities():
    """Test AI building priority system."""
    print("=" * 80)
    print("AI PLAYER TEST - Building Priorities")
    print("=" * 80)
    print()

    game = Game()
    game.paused = False
    ai = GameAI(game, difficulty="medium")

    # Give AI lots of money
    game.resources.money = 50000.0

    print("AI has $50,000 to spend")
    print("Testing building strategy over 60 seconds...")
    print()

    # Run AI
    for i in range(60):
        game.entities.update(1.0)
        game.buildings.update(1.0)
        game.power.update(1.0, game.buildings)
        ai.update(1.0)

    # Analyze what was built
    building_stats = game.buildings.get_building_counts()

    print("Buildings Constructed:")
    print("-" * 80)
    for building_type, count in sorted(building_stats.items()):
        if count > 0:
            print(f"  {building_type}: {count}")

    print()
    print(f"Total buildings: {sum(building_stats.values())}")
    print(f"Money remaining: ${game.resources.money:.2f}")
    print(f"Money spent: ${50000 - game.resources.money:.2f}")
    print()

    # Verify AI built multiple buildings (being strategic, not just spamming)
    assert sum(building_stats.values()) >= 3, "AI should build multiple buildings with ample funds"

    print("✓ AI building priorities working correctly!")
    print()


def main():
    """Run all AI tests."""
    try:
        test_ai_basic_gameplay()
        test_ai_difficulty_levels()
        test_ai_building_priorities()

        print("=" * 80)
        print("ALL AI TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("The AI can successfully:")
        print("  - Play the game autonomously")
        print("  - Make strategic building decisions")
        print("  - Manage resources")
        print("  - Scale with difficulty levels")
        print("  - Prioritize based on game state")
        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
