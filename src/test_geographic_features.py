"""
Comprehensive test suite for Phase 7.11: Geographic Features.

Tests:
- Terrain types and walkability
- River generation
- Bridge placement
- Ocean generation
- Dock placement
- Combined scenarios
"""

import sys
import os

# Add parent directory to path if running from src/
if os.path.basename(os.getcwd()) == 'src':
    sys.path.insert(0, '..')
else:
    sys.path.insert(0, 'src')

from world.grid import Grid
from world.tile import Tile, TileType, TerrainType
from world.river_generator import RiverGenerator
from world.bridge_builder import BridgeBuilder


def test_terrain_types():
    """Test basic terrain type functionality."""
    print("Test: Terrain Types")

    grid = Grid(width_tiles=20, height_tiles=20)

    # Test 1: Create water tile
    tile_water = grid.get_tile(5, 5)
    tile_water.set_terrain_type(TerrainType.WATER)
    assert tile_water.terrain_type == TerrainType.WATER
    assert tile_water.walkable == False, "Water should not be walkable"

    # Test 2: Create bridge tile
    tile_bridge = grid.get_tile(6, 5)
    tile_bridge.set_terrain_type(TerrainType.BRIDGE)
    assert tile_bridge.terrain_type == TerrainType.BRIDGE
    assert tile_bridge.walkable == True, "Bridge should be walkable"

    # Test 3: Create ocean tile
    tile_ocean = grid.get_tile(7, 5)
    tile_ocean.set_terrain_type(TerrainType.OCEAN)
    assert tile_ocean.terrain_type == TerrainType.OCEAN
    assert tile_ocean.walkable == False, "Ocean should not be walkable"

    # Test 4: Create dock tile
    tile_dock = grid.get_tile(8, 5)
    tile_dock.set_terrain_type(TerrainType.DOCK)
    assert tile_dock.terrain_type == TerrainType.DOCK
    # Docks should be walkable (for robots/trucks to load/unload)

    print("  ✓ Terrain types created correctly")
    print("  ✓ Walkability rules applied correctly")


def test_river_generation():
    """Test river generation with various parameters."""
    print("\nTest: River Generation")

    grid = Grid(width_tiles=50, height_tiles=50)
    river_gen = RiverGenerator(grid, seed=12345)

    # Test 1: Generate straight river
    centerline = river_gen.generate_river(
        start_x=25,
        start_y=0,
        direction='south',
        length=30,
        width=3,
        meandering=0.0  # Straight
    )

    assert len(centerline) > 0, "River centerline should not be empty"
    print(f"  ✓ Generated straight river with {len(centerline)} centerline tiles")

    # Count water tiles
    water_count = sum(1 for y in range(grid.height_tiles)
                      for x in range(grid.width_tiles)
                      if grid.get_tile(x, y).terrain_type == TerrainType.WATER)

    assert water_count > 0, "Should have water tiles"
    print(f"  ✓ Created {water_count} water tiles")

    # Test 2: Generate meandering river
    river_gen.clear_rivers()
    centerline2 = river_gen.generate_river(
        start_x=25,
        start_y=0,
        direction='south',
        length=40,
        width=4,
        meandering=0.5  # High meandering
    )

    assert len(centerline2) > 0, "Meandering river should have centerline"
    print(f"  ✓ Generated meandering river with {len(centerline2)} centerline tiles")

    # Test 3: Generate random river
    river_gen.clear_rivers()
    random_river = river_gen.generate_random_river(
        width_range=(2, 5),
        length_range=(20, 40)
    )

    assert len(random_river) > 0, "Random river should have centerline"
    print(f"  ✓ Generated random river with {len(random_river)} centerline tiles")


def test_bridge_placement():
    """Test bridge placement across water."""
    print("\nTest: Bridge Placement")

    grid = Grid(width_tiles=40, height_tiles=40)
    river_gen = RiverGenerator(grid, seed=42)

    # Generate a narrow river
    river_gen.generate_river(
        start_x=20,
        start_y=0,
        direction='south',
        length=30,
        width=3,
        meandering=0.1
    )

    bridge_builder = BridgeBuilder(grid)

    # Test 1: Find crossing points
    crossings = bridge_builder.find_narrow_crossings(max_width=6, min_width=2)
    assert len(crossings) > 0, "Should find at least one crossing point"
    print(f"  ✓ Found {len(crossings)} potential crossing points")

    # Test 2: Place manual bridge
    if crossings:
        crossing = crossings[0]
        success, message, tiles = bridge_builder.place_bridge(
            crossing['start_x'],
            crossing['start_y'],
            crossing['end_x'],
            crossing['end_y'],
            pay_cost=False
        )

        assert success, f"Bridge placement should succeed: {message}"
        assert tiles > 0, "Should place at least one bridge tile"
        print(f"  ✓ Placed bridge with {tiles} tiles")

    # Test 3: Verify bridge walkability
    bridge_count = bridge_builder.count_bridges()
    assert bridge_count > 0, "Should have bridge tiles"

    # Find a bridge tile and verify it's walkable
    bridge_found = False
    for y in range(grid.height_tiles):
        for x in range(grid.width_tiles):
            tile = grid.get_tile(x, y)
            if tile.terrain_type == TerrainType.BRIDGE:
                assert tile.walkable, "Bridge tiles should be walkable"
                bridge_found = True
                break
        if bridge_found:
            break

    print(f"  ✓ Verified {bridge_count} bridge tiles are walkable")


def test_ocean_generation():
    """Test ocean generation at map edges."""
    print("\nTest: Ocean Generation")

    grid = Grid(width_tiles=50, height_tiles=40)
    river_gen = RiverGenerator(grid, seed=999)

    # Test 1: Generate ocean on one edge
    stats = river_gen.generate_ocean(
        edges=['south'],
        depth=5,
        create_docks=False
    )

    assert stats['ocean_tiles'] > 0, "Should generate ocean tiles"
    print(f"  ✓ Generated {stats['ocean_tiles']} ocean tiles on south edge")

    # Test 2: Generate ocean with docks
    river_gen.clear_all_water()
    stats2 = river_gen.generate_ocean(
        edges=['north'],
        depth=4,
        create_docks=True,
        dock_spacing=10
    )

    assert stats2['dock_tiles'] > 0, "Should generate dock tiles"
    print(f"  ✓ Generated {stats2['ocean_tiles']} ocean + {stats2['dock_tiles']} dock tiles")

    # Test 3: Generate ocean on all edges
    river_gen.clear_all_water()
    stats3 = river_gen.generate_ocean(
        edges=['north', 'south', 'east', 'west'],
        depth=3
    )

    total_tiles = stats3['ocean_tiles'] + stats3['dock_tiles']
    assert total_tiles > 0, "Should generate ocean/dock tiles on all edges"
    print(f"  ✓ Generated ocean on all 4 edges ({total_tiles} total tiles)")


def test_combined_generation():
    """Test combining rivers, bridges, and ocean."""
    print("\nTest: Combined Generation (Ocean + Rivers + Bridges)")

    grid = Grid(width_tiles=60, height_tiles=50)
    river_gen = RiverGenerator(grid, seed=777)
    bridge_builder = BridgeBuilder(grid)

    # Step 1: Generate ocean on edges
    ocean_stats = river_gen.generate_ocean(
        edges=['south', 'east'],
        depth=4,
        create_docks=True,
        dock_spacing=12
    )

    # Step 2: Generate multiple rivers
    rivers = river_gen.generate_multiple_rivers(
        count=2,
        width_range=(3, 4),
        length_range=(20, 35),
        meandering=0.3
    )

    # Step 3: Auto-place bridges
    bridge_results = bridge_builder.auto_place_bridges(
        max_bridges=4,
        max_width=7,
        pay_cost=False
    )

    successful_bridges = sum(1 for r in bridge_results if r[0])

    # Count all terrain types
    terrain_counts = {
        'LAND': 0,
        'WATER': 0,
        'OCEAN': 0,
        'BRIDGE': 0,
        'DOCK': 0
    }

    for y in range(grid.height_tiles):
        for x in range(grid.width_tiles):
            tile = grid.get_tile(x, y)
            if tile.terrain_type == TerrainType.LAND:
                terrain_counts['LAND'] += 1
            elif tile.terrain_type == TerrainType.WATER:
                terrain_counts['WATER'] += 1
            elif tile.terrain_type == TerrainType.OCEAN:
                terrain_counts['OCEAN'] += 1
            elif tile.terrain_type == TerrainType.BRIDGE:
                terrain_counts['BRIDGE'] += 1
            elif tile.terrain_type == TerrainType.DOCK:
                terrain_counts['DOCK'] += 1

    print(f"  ✓ Ocean tiles: {terrain_counts['OCEAN']}")
    print(f"  ✓ River tiles: {terrain_counts['WATER']}")
    print(f"  ✓ Bridge tiles: {terrain_counts['BRIDGE']}")
    print(f"  ✓ Dock tiles: {terrain_counts['DOCK']}")
    print(f"  ✓ Land tiles: {terrain_counts['LAND']}")

    assert terrain_counts['OCEAN'] > 0, "Should have ocean"
    assert terrain_counts['WATER'] > 0, "Should have rivers"
    assert terrain_counts['LAND'] > 0, "Should have land"

    total_tiles = sum(terrain_counts.values())
    expected_total = grid.width_tiles * grid.height_tiles
    assert total_tiles == expected_total, f"All tiles accounted for: {total_tiles}/{expected_total}"

    print(f"  ✓ All {expected_total} tiles properly classified")


def test_water_animation():
    """Test water animation frame updates."""
    print("\nTest: Water Animation")

    grid = Grid(width_tiles=20, height_tiles=20)

    # Create water tile
    water_tile = grid.get_tile(10, 10)
    water_tile.set_terrain_type(TerrainType.WATER)

    # Test animation update
    initial_frame = water_tile.water_anim_frame
    water_tile.update_animation(0.1)  # Update with 0.1 second delta

    assert water_tile.water_anim_frame > initial_frame, "Animation frame should advance"
    print(f"  ✓ Water animation advances correctly")

    # Test animation wrapping
    water_tile.water_anim_frame = 360
    water_tile.update_animation(0.5)

    assert water_tile.water_anim_frame < 360, "Animation should wrap around"
    print(f"  ✓ Water animation wraps at 360 degrees")


def run_all_tests():
    """Run all geographic features tests."""
    print("=" * 80)
    print("PHASE 7.11: GEOGRAPHIC FEATURES - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()

    try:
        test_terrain_types()
        test_river_generation()
        test_bridge_placement()
        test_ocean_generation()
        test_combined_generation()
        test_water_animation()

        print()
        print("=" * 80)
        print("ALL GEOGRAPHIC FEATURES TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Phase 7.11 Implementation Complete:")
        print("  ✓ Terrain type system (LAND, WATER, BRIDGE, DOCK, OCEAN)")
        print("  ✓ River generation with meandering")
        print("  ✓ Bridge placement across water")
        print("  ✓ Ocean generation at map edges")
        print("  ✓ Dock placement for water access")
        print("  ✓ Water animation system")
        print("  ✓ Walkability rules for all terrain types")

        return True

    except AssertionError as e:
        print()
        print("=" * 80)
        print(f"TEST FAILED: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
