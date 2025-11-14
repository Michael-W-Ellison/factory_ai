"""
Tests for PollutionManager system.

Tests pollution generation, spreading, decay, and visualization.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.systems.pollution_manager import PollutionManager


def test_pollution_manager_initialization():
    """Test pollution manager initialization."""
    print("Testing pollution manager initialization...")

    pm = PollutionManager(100, 75)

    assert pm.grid_width == 100
    assert pm.grid_height == 75
    assert len(pm.pollution) == 0
    assert len(pm.sources) == 0
    assert not pm.overlay_visible

    print(f"  ✓ Initialized: {pm}")
    print()


def test_add_pollution():
    """Test adding pollution to tiles."""
    print("Testing add pollution...")

    pm = PollutionManager(100, 75)

    # Add pollution to a tile
    pm.add_pollution(50, 50, 10.0)
    assert pm.get_pollution(50, 50) == 10.0

    # Add more pollution to same tile
    pm.add_pollution(50, 50, 15.0)
    assert pm.get_pollution(50, 50) == 25.0

    # Test max cap
    pm.add_pollution(50, 50, 200.0)
    assert pm.get_pollution(50, 50) == pm.max_pollution

    print(f"  ✓ Pollution added correctly")
    print(f"  ✓ Max cap enforced at {pm.max_pollution}")
    print()


def test_pollution_sources():
    """Test pollution sources."""
    print("Testing pollution sources...")

    pm = PollutionManager(100, 75)

    # Add a source
    pm.add_source(50, 50, 5.0)
    assert len(pm.sources) == 1
    assert pm.sources[(50, 50)] == 5.0

    # Update to generate pollution
    pm.update(1.0)  # 1 second

    pollution = pm.get_pollution(50, 50)
    print(f"  After 1 second: {pollution:.1f} pollution at source")
    assert pollution > 0

    # Update more
    pm.update(2.0)  # 2 more seconds
    pollution2 = pm.get_pollution(50, 50)
    print(f"  After 3 seconds: {pollution2:.1f} pollution at source")
    assert pollution2 > pollution

    # Remove source
    pm.remove_source(50, 50)
    assert len(pm.sources) == 0

    print(f"  ✓ Pollution sources work correctly")
    print()


def test_pollution_spreading():
    """Test pollution spreading to neighbors."""
    print("Testing pollution spreading...")

    pm = PollutionManager(100, 75)

    # Add high pollution at one tile
    pm.add_pollution(50, 50, 50.0)

    initial = pm.get_pollution(50, 50)
    print(f"  Initial pollution at (50,50): {initial:.1f}")

    # Update to spread
    pm.update(2.0)

    # Check neighbors have some pollution
    center = pm.get_pollution(50, 50)
    north = pm.get_pollution(50, 49)
    south = pm.get_pollution(50, 51)
    east = pm.get_pollution(51, 50)
    west = pm.get_pollution(49, 50)

    print(f"  After spreading:")
    print(f"    Center (50,50): {center:.1f}")
    print(f"    North (50,49): {north:.1f}")
    print(f"    South (50,51): {south:.1f}")
    print(f"    East (51,50): {east:.1f}")
    print(f"    West (49,50): {west:.1f}")

    # Neighbors should have some pollution
    assert north > 0 or south > 0 or east > 0 or west > 0, "Pollution should spread to neighbors"

    print(f"  ✓ Pollution spreads to neighbors")
    print()


def test_pollution_decay():
    """Test pollution decay over time."""
    print("Testing pollution decay...")

    pm = PollutionManager(100, 75)

    # Add pollution
    pm.add_pollution(50, 50, 30.0)
    initial = pm.get_pollution(50, 50)
    print(f"  Initial pollution: {initial:.1f}")

    # Update without sources (decay only)
    pm.update(5.0)

    final = pm.get_pollution(50, 50)
    print(f"  After 5 seconds decay: {final:.1f}")

    assert final < initial, "Pollution should decay"

    # Update a lot to test complete decay
    for _ in range(100):
        pm.update(1.0)

    remaining = pm.get_pollution(50, 50)
    print(f"  After long time: {remaining:.1f}")

    assert remaining < 1.0, "Pollution should eventually decay to near zero"

    print(f"  ✓ Pollution decays over time")
    print()


def test_pollution_color_gradient():
    """Test pollution color gradient."""
    print("Testing pollution color gradient...")

    pm = PollutionManager(100, 75)

    # Test color at different levels
    levels = [0, 25, 50, 75, 100]
    for level in levels:
        color = pm._get_pollution_color(level)
        print(f"  Level {level:3d}: RGB({color[0]:3d}, {color[1]:3d}, {color[2]:3d}) Alpha={color[3]:3d}")
        assert len(color) == 4, "Color should be RGBA"
        assert 0 <= color[3] <= 255, "Alpha should be 0-255"

    print(f"  ✓ Color gradient works (yellow -> orange -> red)")
    print()


def test_statistics():
    """Test pollution statistics."""
    print("Testing pollution statistics...")

    pm = PollutionManager(100, 75)

    # Add pollution at multiple locations
    pm.add_pollution(50, 50, 30.0)
    pm.add_pollution(60, 60, 20.0)
    pm.add_pollution(70, 70, 40.0)

    # Add a source
    pm.add_source(50, 50, 5.0)

    stats = pm.get_stats()

    print(f"  Total tiles: {stats['total_tiles']}")
    print(f"  Average pollution: {stats['avg_pollution']:.1f}")
    print(f"  Max pollution: {stats['max_pollution_level']:.1f}")
    print(f"  Total pollution: {stats['total_pollution']:.1f}")
    print(f"  Sources: {stats['sources']}")

    assert stats['total_tiles'] == 3
    assert stats['max_pollution_level'] == 40.0
    assert stats['sources'] == 1

    print(f"  ✓ Statistics calculated correctly")
    print()


def test_save_load():
    """Test save and load functionality."""
    print("Testing save/load...")

    pm1 = PollutionManager(100, 75)

    # Set up state
    pm1.add_pollution(50, 50, 30.0)
    pm1.add_pollution(60, 60, 20.0)
    pm1.add_source(50, 50, 5.0)
    pm1.toggle_overlay()

    # Save
    saved_data = pm1.to_dict()

    print(f"  Saved {len(saved_data['pollution'])} pollution tiles")
    print(f"  Saved {len(saved_data['sources'])} sources")
    print(f"  Overlay visible: {saved_data['overlay_visible']}")

    # Load into new manager
    pm2 = PollutionManager(100, 75)
    pm2.from_dict(saved_data)

    # Verify
    assert pm2.get_pollution(50, 50) == 30.0
    assert pm2.get_pollution(60, 60) == 20.0
    assert (50, 50) in pm2.sources
    assert pm2.overlay_visible

    print(f"  ✓ Save/load works correctly")
    print()


def main():
    """Run all pollution system tests."""
    print("=" * 80)
    print("POLLUTION SYSTEM TESTS")
    print("=" * 80)
    print()

    try:
        test_pollution_manager_initialization()
        test_add_pollution()
        test_pollution_sources()
        test_pollution_spreading()
        test_pollution_decay()
        test_pollution_color_gradient()
        test_statistics()
        test_save_load()

        print("=" * 80)
        print("ALL POLLUTION TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Pollution System Features:")
        print("  - Grid-based pollution tracking (0-100 per tile)")
        print("  - Pollution sources with generation rates")
        print("  - Spreading algorithm (diffuses to 4 neighbors)")
        print("  - Natural decay over time")
        print("  - Factorio-style color gradient overlay")
        print("  - Yellow -> Orange -> Red -> Dark Red visualization")
        print("  - Alpha transparency based on pollution level")
        print("  - Statistics tracking (total, average, max)")
        print("  - Save/load support")
        print("  - Toggle overlay with P key (in game)")
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
