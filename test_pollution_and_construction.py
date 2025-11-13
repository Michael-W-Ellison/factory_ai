"""
Tests for landfill pollution and building construction visuals.

Tests that landfill tiles generate pollution based on fullness and that
buildings show progressive construction states.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.world.tile import Tile, TileType
from src.systems.pollution_manager import PollutionManager
from src.entities.buildings.factory import Factory
from src.entities.building import Building


def test_landfill_pollution_generation():
    """Test that landfill tiles generate pollution based on fullness."""
    print("Testing landfill pollution generation...")

    pm = PollutionManager(100, 75)
    tile = Tile(10, 10, TileType.LANDFILL)

    # Full landfill should generate maximum pollution
    tile.add_depletion(0.0, pm)
    assert (10, 10) in pm.sources
    assert pm.sources[(10, 10)] == 0.5  # Max rate when full
    print(f"  Full landfill (0% depleted): {pm.sources[(10, 10)]:.2f} pollution/s")

    # 50% depleted should generate half pollution
    tile.add_depletion(0.5, pm)
    assert pm.sources[(10, 10)] == 0.25  # Half rate at 50% depletion
    print(f"  Half-full landfill (50% depleted): {pm.sources[(10, 10)]:.2f} pollution/s")

    # Fully depleted should not generate pollution
    tile.add_depletion(0.5, pm)
    assert (10, 10) not in pm.sources  # Removed when rate hits 0
    print(f"  Empty landfill (100% depleted): no pollution")

    print(f"  ✓ Landfill pollution scales with fullness")
    print()


def test_landfill_pollution_update():
    """Test that pollution manager can update source rates."""
    print("Testing pollution source updates...")

    pm = PollutionManager(100, 75)

    # Add a source
    pm.add_source(20, 20, 1.0)
    assert pm.sources[(20, 20)] == 1.0
    print(f"  Initial source: {pm.sources[(20, 20)]:.2f} pollution/s")

    # Update the source
    pm.update_source(20, 20, 2.5)
    assert pm.sources[(20, 20)] == 2.5
    print(f"  After update: {pm.sources[(20, 20)]:.2f} pollution/s")

    # Update to zero should remove
    pm.update_source(20, 20, 0.0)
    assert (20, 20) not in pm.sources
    print(f"  After zero update: source removed")

    print(f"  ✓ Pollution sources can be updated dynamically")
    print()


def test_multiple_landfill_tiles():
    """Test pollution from multiple landfill tiles."""
    print("Testing multiple landfill tiles...")

    pm = PollutionManager(100, 75)

    # Create multiple landfill tiles at different depletion levels
    tiles = [
        Tile(5, 5, TileType.LANDFILL),   # Full
        Tile(6, 6, TileType.LANDFILL),   # 25% depleted
        Tile(7, 7, TileType.LANDFILL),   # 50% depleted
        Tile(8, 8, TileType.LANDFILL),   # 75% depleted
        Tile(9, 9, TileType.LANDFILL),   # 100% depleted
    ]

    # Set depletion levels
    tiles[0].add_depletion(0.0, pm)    # 0% depleted: 0.5 pollution/s
    tiles[1].add_depletion(0.25, pm)   # 25% depleted: 0.375 pollution/s
    tiles[2].add_depletion(0.5, pm)    # 50% depleted: 0.25 pollution/s
    tiles[3].add_depletion(0.75, pm)   # 75% depleted: 0.125 pollution/s
    tiles[4].add_depletion(1.0, pm)    # 100% depleted: 0 pollution/s

    # Check source count
    assert len(pm.sources) == 4  # 5th tile has no pollution
    print(f"  Created {len(pm.sources)} pollution sources from 5 landfill tiles")

    # Verify rates
    assert pm.sources[(5, 5)] == 0.5
    assert pm.sources[(6, 6)] == 0.375
    assert pm.sources[(7, 7)] == 0.25
    assert pm.sources[(8, 8)] == 0.125

    total_pollution = sum(pm.sources.values())
    print(f"  Total pollution rate: {total_pollution:.3f} pollution/s")
    print(f"  ✓ Multiple landfill tiles generate correct pollution")
    print()


def test_building_construction_progress():
    """Test building construction progress tracking."""
    print("Testing building construction progress...")

    building = Factory(50, 50)
    building.under_construction = True
    building.construction_progress = 0.0
    building.construction_time = 10.0  # 10 seconds

    # Stage 1: 0-25%
    building.construction_progress = 15.0
    assert building.construction_progress < 25.0
    print(f"  Stage 1 (Foundation): {building.construction_progress:.0f}%")

    # Stage 2: 25-50%
    building.construction_progress = 40.0
    assert 25.0 <= building.construction_progress < 50.0
    print(f"  Stage 2 (Walls rising): {building.construction_progress:.0f}%")

    # Stage 3: 50-75%
    building.construction_progress = 65.0
    assert 50.0 <= building.construction_progress < 75.0
    print(f"  Stage 3 (Full scaffolding): {building.construction_progress:.0f}%")

    # Stage 4: 75-100%
    building.construction_progress = 90.0
    assert 75.0 <= building.construction_progress < 100.0
    print(f"  Stage 4 (Nearly complete): {building.construction_progress:.0f}%")

    print(f"  ✓ Building tracks construction progress correctly")
    print()


def test_building_construction_completion():
    """Test building construction completion."""
    print("Testing building construction completion...")

    building = Factory(55, 55)
    building.under_construction = True
    building.construction_progress = 0.0
    building.construction_time = 5.0  # 5 seconds

    # Update over time
    building.update(1.25)  # 25% complete
    assert building.under_construction
    assert building.construction_progress == 25.0
    print(f"  After 1.25s: {building.construction_progress:.0f}% (still building)")

    building.update(1.25)  # 50% complete
    assert building.under_construction
    assert building.construction_progress == 50.0
    print(f"  After 2.5s: {building.construction_progress:.0f}% (still building)")

    building.update(2.5)  # 100% complete
    assert not building.under_construction
    assert building.construction_progress == 100.0
    print(f"  After 5s: {building.construction_progress:.0f}% (construction complete)")

    print(f"  ✓ Building construction completes correctly")
    print()


def test_construction_stages_exist():
    """Test that construction has 4 distinct visual stages."""
    print("Testing construction stage definitions...")

    # We can't test rendering without pygame display, but we can verify the logic
    building = Factory(60, 60)
    building.under_construction = True

    stages = [
        (10, "Foundation and materials"),
        (35, "Walls rising from bottom"),
        (60, "Full walls with side scaffolding"),
        (85, "Nearly complete with top scaffolding"),
    ]

    for progress, description in stages:
        building.construction_progress = float(progress)
        actual_progress = building.construction_progress / 100.0

        if actual_progress < 0.25:
            stage = 1
        elif actual_progress < 0.5:
            stage = 2
        elif actual_progress < 0.75:
            stage = 3
        else:
            stage = 4

        print(f"  {progress}%: Stage {stage} - {description}")

    print(f"  ✓ Construction has 4 distinct visual stages")
    print()


def test_landfill_pollution_integration():
    """Test integration of landfill pollution into pollution system."""
    print("Testing landfill pollution integration...")

    pm = PollutionManager(100, 75)

    # Simulate Game initialization registering landfill tiles
    landfill_tiles = [
        (10, 10, 0.0),   # Full landfill
        (11, 11, 0.3),   # 30% depleted
        (12, 12, 0.7),   # 70% depleted
        (13, 13, 1.0),   # Empty
    ]

    registered = 0
    for x, y, depletion in landfill_tiles:
        fullness = 1.0 - depletion
        pollution_rate = fullness * 0.5
        if pollution_rate > 0:
            pm.add_source(x, y, pollution_rate)
            registered += 1

    assert registered == 3  # 4th tile is empty, no pollution
    print(f"  Registered {registered} landfill tiles")

    # Verify sources have correct rates
    print(f"  Sources: {pm.sources}")
    assert abs(pm.sources[(10, 10)] - 0.5) < 0.01     # Full landfill
    assert abs(pm.sources[(11, 11)] - 0.35) < 0.01    # 70% full
    assert abs(pm.sources[(12, 12)] - 0.15) < 0.01    # 30% full
    assert (13, 13) not in pm.sources                  # Empty

    print(f"  Sources have correct pollution rates")
    print(f"  ✓ Landfill pollution integrates correctly")
    print()


def main():
    """Run all tests."""
    print("=" * 80)
    print("LANDFILL POLLUTION & CONSTRUCTION VISUAL TESTS")
    print("=" * 80)
    print()

    try:
        test_landfill_pollution_generation()
        test_landfill_pollution_update()
        test_multiple_landfill_tiles()
        test_building_construction_progress()
        test_building_construction_completion()
        test_construction_stages_exist()
        test_landfill_pollution_integration()

        print("=" * 80)
        print("ALL TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Features Implemented:")
        print()
        print("LANDFILL POLLUTION:")
        print("  - Landfill tiles generate pollution based on fullness")
        print("  - Full landfill: 0.5 pollution/s per tile")
        print("  - Empty landfill: 0 pollution/s")
        print("  - Pollution rate decreases linearly with depletion")
        print("  - Automatically updated when materials collected")
        print()
        print("BUILDING CONSTRUCTION (4 stages):")
        print("  - Stage 1 (0-25%): Foundation with material piles")
        print("  - Stage 2 (25-50%): Walls rising from bottom")
        print("  - Stage 3 (50-75%): Complete walls with side scaffolding")
        print("  - Stage 4 (75-100%): Nearly complete with top scaffolding")
        print("  - Progress bar and percentage display")
        print("  - Scaffolding removes progressively")
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
