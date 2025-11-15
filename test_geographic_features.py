"""
Test Geographic Features

Tests the river generation, ocean placement, and bridge system.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))


def test_river_generator_creation():
    """Test RiverGenerator initialization."""
    print("=" * 80)
    print("TEST 1: RiverGenerator Creation")
    print("=" * 80)
    print()

    from src.world.river_generator import RiverGenerator

    # Create generator
    gen = RiverGenerator(100, 75, seed=42)
    print(f"✓ RiverGenerator created: {gen}")
    assert gen.grid_width == 100
    assert gen.grid_height == 75
    print(f"✓ Grid dimensions: {gen.grid_width}x{gen.grid_height}")

    # Check initial state
    assert len(gen.rivers) == 0
    assert len(gen.river_tiles) == 0
    assert len(gen.bridges) == 0
    print(f"✓ Initial state: no rivers, no bridges")

    print("\n✓ RiverGenerator creation test PASSED\n")


def test_single_river_generation():
    """Test generating a single river."""
    print("=" * 80)
    print("TEST 2: Single River Generation")
    print("=" * 80)
    print()

    from src.world.river_generator import RiverGenerator

    gen = RiverGenerator(100, 75, seed=42)

    # Generate one river
    river_data = gen.generate(num_rivers=1, flow_direction='south')

    assert len(gen.rivers) == 1, f"Expected 1 river, got {len(gen.rivers)}"
    print(f"✓ Generated 1 river")

    assert len(gen.river_tiles) > 0, "River should have tiles"
    print(f"✓ River has {len(gen.river_tiles)} water tiles")

    # Check river flows from north to south
    river_path = gen.rivers[0]
    first_segment = river_path[0]
    last_segment = river_path[-1]
    assert last_segment.y > first_segment.y, "River should flow south (increasing Y)"
    print(f"✓ River flows south: Y {first_segment.y} -> {last_segment.y}")

    # Check river width (3-5 tiles)
    for segment in river_path:
        assert 3 <= segment.width <= 5, f"River width should be 3-5, got {segment.width}"
    print(f"✓ River width in range 3-5 tiles")

    # Check statistics
    stats = gen.get_statistics()
    assert stats['num_rivers'] == 1
    assert stats['river_tiles'] > 0
    print(f"✓ Statistics: {stats}")

    print("\n✓ Single river generation test PASSED\n")


def test_multiple_rivers():
    """Test generating multiple rivers."""
    print("=" * 80)
    print("TEST 3: Multiple Rivers")
    print("=" * 80)
    print()

    from src.world.river_generator import RiverGenerator

    gen = RiverGenerator(100, 75, seed=123)

    # Generate two rivers
    river_data = gen.generate(num_rivers=2, flow_direction='south')

    assert len(gen.rivers) == 2, f"Expected 2 rivers, got {len(gen.rivers)}"
    print(f"✓ Generated 2 rivers")

    # Each river should have tiles
    for i, river in enumerate(gen.rivers):
        assert len(river) > 0, f"River {i} should have segments"
        print(f"✓ River {i}: {len(river)} segments")

    # Total tiles
    print(f"✓ Total water tiles: {len(gen.river_tiles)}")

    print("\n✓ Multiple rivers test PASSED\n")


def test_ocean_generation():
    """Test ocean edge generation."""
    print("=" * 80)
    print("TEST 4: Ocean Generation")
    print("=" * 80)
    print()

    from src.world.river_generator import RiverGenerator

    gen = RiverGenerator(100, 75, seed=42)

    # Add ocean on south edge
    ocean_tiles = gen.add_ocean_edge('south', depth=8)

    assert len(ocean_tiles) > 0, "Ocean should have tiles"
    print(f"✓ Ocean added: {len(ocean_tiles)} tiles")

    # Check ocean is at south edge
    for x, y in list(ocean_tiles)[:10]:  # Check first 10 tiles
        assert y >= 75 - 8, f"Ocean tile should be at south edge, got Y={y}"
    print(f"✓ Ocean tiles at south edge (Y >= {75 - 8})")

    # Add ocean on east edge
    east_ocean = gen.add_ocean_edge('east', depth=5)
    assert len(east_ocean) > 0, "East ocean should have tiles"
    print(f"✓ East ocean added: {len(east_ocean)} tiles")

    for x, y in list(east_ocean)[:10]:
        assert x >= 100 - 5, f"East ocean tile should be at east edge, got X={x}"
    print(f"✓ East ocean tiles at east edge (X >= {100 - 5})")

    print("\n✓ Ocean generation test PASSED\n")


def test_bridge_placement():
    """Test bridge placement on river crossings."""
    print("=" * 80)
    print("TEST 5: Bridge Placement")
    print("=" * 80)
    print()

    from src.world.river_generator import RiverGenerator

    gen = RiverGenerator(100, 75, seed=42)

    # Generate a river
    gen.generate(num_rivers=1, flow_direction='south')
    print(f"✓ River generated with {len(gen.river_tiles)} water tiles")

    # Create fake road tiles crossing the river
    road_tiles = set()

    # Find a river tile and create a horizontal road through it
    sample_river_tiles = list(gen.river_tiles)[:50]
    if sample_river_tiles:
        river_x, river_y = sample_river_tiles[25]  # Pick middle tile

        # Create horizontal road crossing river
        for x in range(max(0, river_x - 10), min(100, river_x + 10)):
            road_tiles.add((x, river_y))

        print(f"✓ Created test road crossing river at Y={river_y}")

    # Place bridges
    gen.place_bridges(road_tiles, min_spacing=5)

    # Should have at least one bridge if road crosses river
    if road_tiles & gen.river_tiles:  # If road and river intersect
        assert len(gen.bridges) > 0, "Should have bridges where road crosses river"
        print(f"✓ Placed {len(gen.bridges)} bridge(s)")

        # Check bridge tiles
        assert len(gen.bridge_tiles) > 0, "Bridges should have tiles"
        print(f"✓ Bridge tiles: {len(gen.bridge_tiles)}")

        # Check bridge structure
        for bridge in gen.bridges:
            assert bridge.length >= 2, "Bridge should be at least 2 tiles long"
            assert bridge.direction in ['horizontal', 'vertical']
            print(f"✓ Bridge: {bridge.direction}, length {bridge.length}")
    else:
        print("✓ No road-river intersection, no bridges needed")

    print("\n✓ Bridge placement test PASSED\n")


def test_grid_integration():
    """Test Grid integration with geographic features."""
    print("=" * 80)
    print("TEST 6: Grid Integration")
    print("=" * 80)
    print()

    from src.world.grid import Grid
    from src.world.tile import TerrainType

    # Create grid
    grid = Grid(100, 75, tile_size=32)
    print(f"✓ Grid created: {grid.width_tiles}x{grid.height_tiles}")

    # Generate geographic features
    grid.generate_geographic_features(seed=42, num_rivers=1, ocean_edges=['south'])

    assert grid.has_geographic_features, "Grid should have geographic features"
    assert grid.river_generator is not None, "Grid should have river generator"
    print(f"✓ Geographic features generated")

    # Check river tiles have water terrain type
    water_tile_count = 0
    ocean_tile_count = 0

    for y in range(grid.height_tiles):
        for x in range(grid.width_tiles):
            tile = grid.get_tile(x, y)
            if tile.terrain_type == TerrainType.WATER:
                water_tile_count += 1
            elif tile.terrain_type == TerrainType.OCEAN:
                ocean_tile_count += 1

    assert water_tile_count > 0, "Should have water tiles from river"
    assert ocean_tile_count > 0, "Should have ocean tiles from south edge"
    print(f"✓ Water tiles: {water_tile_count}")
    print(f"✓ Ocean tiles: {ocean_tile_count}")

    # Check water tiles are not walkable
    for x, y in list(grid.river_generator.river_tiles)[:10]:
        tile = grid.get_tile(x, y)
        assert not tile.walkable, f"Water tile at ({x}, {y}) should not be walkable"
    print(f"✓ Water tiles are not walkable")

    print("\n✓ Grid integration test PASSED\n")


def test_bridge_walkability():
    """Test that bridges are walkable."""
    print("=" * 80)
    print("TEST 7: Bridge Walkability")
    print("=" * 80)
    print()

    from src.world.grid import Grid
    from src.world.tile import TerrainType

    # Create grid and generate features
    grid = Grid(100, 75, tile_size=32)
    grid.generate_geographic_features(seed=42, num_rivers=1)

    # Generate city (which has roads)
    grid.generate_city(seed=42)

    # Place bridges on roads
    grid.place_bridges_on_roads()

    # Check bridge tiles
    if grid.river_generator and len(grid.river_generator.bridge_tiles) > 0:
        bridge_count = 0
        for x, y in grid.river_generator.bridge_tiles:
            tile = grid.get_tile(x, y)
            assert tile.terrain_type == TerrainType.BRIDGE, f"Tile ({x}, {y}) should be bridge"
            assert tile.walkable, f"Bridge tile ({x}, {y}) should be walkable"
            bridge_count += 1

        print(f"✓ All {bridge_count} bridge tiles are walkable")
        print(f"✓ Bridges placed: {len(grid.river_generator.bridges)}")
    else:
        print("✓ No bridges needed (no road-river crossings)")

    print("\n✓ Bridge walkability test PASSED\n")


def test_pathfinding_around_water():
    """Test that pathfinding routes around water."""
    print("=" * 80)
    print("TEST 8: Pathfinding Around Water")
    print("=" * 80)
    print()

    from src.world.grid import Grid
    from src.systems.pathfinding import Pathfinding
    from src.world.tile import TerrainType

    # Create small grid for easier testing
    grid = Grid(50, 50, tile_size=32)

    # Manually create a vertical river in the middle
    for y in range(10, 40):
        tile = grid.get_tile(25, y)
        if tile:
            tile.set_terrain_type(TerrainType.WATER)

    print(f"✓ Created test river at X=25, Y=10-40")

    # Create pathfinder
    pathfinder = Pathfinding(grid)

    # Try to find path across river (should fail or go around)
    start = (20, 25)
    goal = (30, 25)

    path = pathfinder.find_path(start, goal)

    if path:
        # Path found - verify it doesn't cross water
        for x, y in path:
            tile = grid.get_tile(x, y)
            assert tile.terrain_type != TerrainType.WATER, f"Path should not cross water at ({x}, {y})"
        print(f"✓ Path found going around water: {len(path)} tiles")
    else:
        print(f"✓ No path found (water blocks the way)")

    # Now add a bridge
    bridge_y = 25
    tile = grid.get_tile(25, bridge_y)
    tile.set_terrain_type(TerrainType.BRIDGE)
    print(f"✓ Added bridge at (25, {bridge_y})")

    # Try again - should find path using bridge
    path2 = pathfinder.find_path(start, goal)

    assert path2 is not None, "Should find path with bridge"
    print(f"✓ Path found using bridge: {len(path2)} tiles")

    # Verify path uses the bridge
    uses_bridge = any(x == 25 and y == bridge_y for x, y in path2)
    assert uses_bridge, "Path should use the bridge"
    print(f"✓ Path uses bridge at (25, {bridge_y})")

    print("\n✓ Pathfinding around water test PASSED\n")


def test_reproducibility():
    """Test that same seed produces same rivers."""
    print("=" * 80)
    print("TEST 9: Reproducibility")
    print("=" * 80)
    print()

    from src.world.river_generator import RiverGenerator

    # Generate with seed 999
    gen1 = RiverGenerator(100, 75, seed=999)
    data1 = gen1.generate(num_rivers=1, flow_direction='south')

    # Generate again with same seed
    gen2 = RiverGenerator(100, 75, seed=999)
    data2 = gen2.generate(num_rivers=1, flow_direction='south')

    # Should be identical
    assert len(gen1.river_tiles) == len(gen2.river_tiles), "Same seed should produce same number of tiles"
    assert gen1.river_tiles == gen2.river_tiles, "Same seed should produce identical river tiles"

    print(f"✓ Both generators created {len(gen1.river_tiles)} tiles")
    print(f"✓ River tiles are identical")

    # Check river paths
    assert len(gen1.rivers) == len(gen2.rivers)
    assert len(gen1.rivers[0]) == len(gen2.rivers[0])
    print(f"✓ River paths are identical ({len(gen1.rivers[0])} segments)")

    print("\n✓ Reproducibility test PASSED\n")


def run_all_tests():
    """Run all geographic features tests."""
    print("\n")
    print("=" * 80)
    print("GEOGRAPHIC FEATURES TEST SUITE")
    print("=" * 80)
    print("\n")

    try:
        test_river_generator_creation()
        test_single_river_generation()
        test_multiple_rivers()
        test_ocean_generation()
        test_bridge_placement()
        test_grid_integration()
        test_bridge_walkability()
        test_pathfinding_around_water()
        test_reproducibility()

        print("=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
        print()
        print("Summary:")
        print("  ✓ RiverGenerator creation and initialization")
        print("  ✓ Single and multiple river generation")
        print("  ✓ Ocean edge placement")
        print("  ✓ Bridge placement at road crossings")
        print("  ✓ Grid integration with terrain types")
        print("  ✓ Bridge walkability")
        print("  ✓ Pathfinding respects water and bridges")
        print("  ✓ Reproducible generation with seeds")
        print()

        return True

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ TEST ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
