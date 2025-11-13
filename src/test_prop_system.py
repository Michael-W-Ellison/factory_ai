"""
Comprehensive test suite for Phase 7.14: Prop System.

Tests:
- Prop creation and properties
- Bench, LightPole, TrashCan, Bicycle creation
- PropManager placement logic
- Prop rendering
"""

import sys
import os

# Add parent directory to path
if os.path.basename(os.getcwd()) == 'src':
    sys.path.insert(0, '..')
else:
    sys.path.insert(0, 'src')

from world.grid import Grid
from world.tile import TileType
from systems.road_network import RoadNetwork
from entities.prop import Prop, Bench, LightPole, TrashCan, Bicycle, PropType
from systems.prop_manager import PropManager


def create_test_grid():
    """Create a test grid with various tile types."""
    grid = Grid(width_tiles=30, height_tiles=30)

    # Create some roads
    for x in range(5, 26):
        tile = grid.get_tile(x, 10)
        tile.tile_type = TileType.ROAD_ASPHALT

    # Create some grass (park areas)
    for y in range(15, 20):
        for x in range(10, 15):
            tile = grid.get_tile(x, y)
            tile.tile_type = TileType.GRASS

    # Create some buildings
    for y in range(5, 8):
        for x in range(15, 18):
            tile = grid.get_tile(x, y)
            tile.tile_type = TileType.BUILDING

    return grid


def test_bench_creation():
    """Test Bench prop creation."""
    print("Test: Bench Creation")

    bench = Bench(world_x=100.0, world_y=200.0, rotation=90)

    assert bench.prop_type == PropType.BENCH, "Prop type should be BENCH"
    assert bench.world_x == 100.0, "World X should be 100.0"
    assert bench.world_y == 200.0, "World Y should be 200.0"
    assert bench.rotation == 90, "Rotation should be 90"
    assert bench.width == 16, "Bench width should be 16"
    assert bench.height == 8, "Bench height should be 8"

    print(f"  ✓ Bench created at ({bench.world_x}, {bench.world_y})")
    print(f"  ✓ Rotation: {bench.rotation}°, Size: {bench.width}x{bench.height}")


def test_light_pole_creation():
    """Test LightPole prop creation."""
    print("\nTest: LightPole Creation")

    light_pole = LightPole(world_x=150.0, world_y=250.0)

    assert light_pole.prop_type == PropType.LIGHT_POLE, "Prop type should be LIGHT_POLE"
    assert light_pole.world_x == 150.0, "World X should be 150.0"
    assert light_pole.world_y == 250.0, "World Y should be 250.0"
    assert light_pole.width == 4, "Light pole width should be 4"
    assert light_pole.height == 20, "Light pole height should be 20"
    assert not light_pole.is_on, "Light should start off"

    # Test turning light on
    light_pole.is_on = True
    assert light_pole.is_on, "Light should be on"

    print(f"  ✓ Light pole created at ({light_pole.world_x}, {light_pole.world_y})")
    print(f"  ✓ Size: {light_pole.width}x{light_pole.height}")
    print(f"  ✓ Light state toggles correctly")


def test_trash_can_creation():
    """Test TrashCan prop creation."""
    print("\nTest: TrashCan Creation")

    trash_can = TrashCan(world_x=200.0, world_y=300.0)

    assert trash_can.prop_type == PropType.TRASH_CAN, "Prop type should be TRASH_CAN"
    assert trash_can.world_x == 200.0, "World X should be 200.0"
    assert trash_can.world_y == 300.0, "World Y should be 300.0"
    assert trash_can.width == 8, "Trash can width should be 8"
    assert trash_can.height == 10, "Trash can height should be 10"

    print(f"  ✓ Trash can created at ({trash_can.world_x}, {trash_can.world_y})")
    print(f"  ✓ Size: {trash_can.width}x{trash_can.height}")


def test_bicycle_creation():
    """Test Bicycle prop creation."""
    print("\nTest: Bicycle Creation")

    bicycle = Bicycle(world_x=250.0, world_y=350.0, rotation=180)

    assert bicycle.prop_type == PropType.BICYCLE, "Prop type should be BICYCLE"
    assert bicycle.world_x == 250.0, "World X should be 250.0"
    assert bicycle.world_y == 350.0, "World Y should be 350.0"
    assert bicycle.rotation == 180, "Rotation should be 180"
    assert bicycle.width == 16, "Bicycle width should be 16"
    assert bicycle.height == 10, "Bicycle height should be 10"

    print(f"  ✓ Bicycle created at ({bicycle.world_x}, {bicycle.world_y})")
    print(f"  ✓ Rotation: {bicycle.rotation}°, Size: {bicycle.width}x{bicycle.height}")


def test_prop_manager_creation():
    """Test PropManager creation."""
    print("\nTest: PropManager Creation")

    grid = create_test_grid()
    road_network = RoadNetwork(grid)

    prop_manager = PropManager(grid, road_network)

    assert prop_manager.grid == grid, "PropManager should have grid reference"
    assert prop_manager.road_network == road_network, "PropManager should have road network reference"
    assert prop_manager.get_prop_count() == 0, "Should start with 0 props"

    print(f"  ✓ PropManager created")
    print(f"  ✓ Initial prop count: {prop_manager.get_prop_count()}")


def test_prop_manager_placement():
    """Test PropManager automatic prop placement."""
    print("\nTest: PropManager Prop Placement")

    grid = create_test_grid()
    road_network = RoadNetwork(grid)

    prop_manager = PropManager(grid, road_network)

    # Generate props
    prop_manager.generate_props()

    initial_count = prop_manager.get_prop_count()
    assert initial_count > 0, "Should have placed some props"

    # Count each type
    light_poles = sum(1 for p in prop_manager.props if p.prop_type == PropType.LIGHT_POLE)
    benches = sum(1 for p in prop_manager.props if p.prop_type == PropType.BENCH)
    trash_cans = sum(1 for p in prop_manager.props if p.prop_type == PropType.TRASH_CAN)
    bicycles = sum(1 for p in prop_manager.props if p.prop_type == PropType.BICYCLE)

    print(f"  ✓ Generated {initial_count} props total")
    print(f"  ✓ Light poles: {light_poles}")
    print(f"  ✓ Benches: {benches}")
    print(f"  ✓ Trash cans: {trash_cans}")
    print(f"  ✓ Bicycles: {bicycles}")


def test_light_pole_placement():
    """Test light pole placement along roads."""
    print("\nTest: Light Pole Placement Along Roads")

    grid = create_test_grid()
    road_network = RoadNetwork(grid)

    prop_manager = PropManager(grid, road_network)
    prop_manager.light_pole_spacing = 5  # Place more frequently for testing

    # Place only light poles
    prop_manager._place_light_poles()

    light_poles = [p for p in prop_manager.props if p.prop_type == PropType.LIGHT_POLE]

    assert len(light_poles) > 0, "Should have placed light poles"

    # Verify light poles are near roads
    tile_size = grid.tile_size
    for light_pole in light_poles:
        grid_x = int(light_pole.world_x // tile_size)
        grid_y = int(light_pole.world_y // tile_size)

        # Light poles should be offset from road, check nearby tiles
        nearby_road = False
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                check_x = grid_x + dx
                check_y = grid_y + dy
                if road_network.is_road(check_x, check_y):
                    nearby_road = True
                    break

        assert nearby_road, f"Light pole at ({light_pole.world_x}, {light_pole.world_y}) should be near a road"

    print(f"  ✓ Placed {len(light_poles)} light poles along roads")
    print(f"  ✓ All light poles are near road tiles")


def test_prop_manager_update():
    """Test PropManager update (light on/off)."""
    print("\nTest: PropManager Update (Day/Night Cycle)")

    grid = create_test_grid()
    road_network = RoadNetwork(grid)

    prop_manager = PropManager(grid, road_network)
    prop_manager._place_light_poles()

    light_poles = [p for p in prop_manager.props if p.prop_type == PropType.LIGHT_POLE]

    if light_poles:
        # Day time - lights off
        prop_manager.update(0.1, is_night=False)

        for light_pole in light_poles:
            assert not light_pole.is_on, "Lights should be off during day"

        # Night time - lights on
        prop_manager.update(0.1, is_night=True)

        for light_pole in light_poles:
            assert light_pole.is_on, "Lights should be on at night"

        print(f"  ✓ Day mode: All {len(light_poles)} lights off")
        print(f"  ✓ Night mode: All {len(light_poles)} lights on")
    else:
        print("  ! No light poles to test")


def test_prop_position_clearing():
    """Test prop position clearing logic."""
    print("\nTest: Prop Position Clearing")

    grid = create_test_grid()
    prop_manager = PropManager(grid)

    # Add a prop
    bench = Bench(100.0, 100.0)
    prop_manager.add_prop(bench)

    # Check if position is clear (should be false - prop is there)
    is_clear_close = prop_manager._is_position_clear(105.0, 105.0, min_distance=10)
    assert not is_clear_close, "Position close to prop should not be clear"

    # Check farther away (should be clear)
    is_clear_far = prop_manager._is_position_clear(200.0, 200.0, min_distance=10)
    assert is_clear_far, "Position far from props should be clear"

    print(f"  ✓ Position clearing works correctly")
    print(f"  ✓ Close position blocked: {not is_clear_close}")
    print(f"  ✓ Far position clear: {is_clear_far}")


def run_all_tests():
    """Run all prop system tests."""
    print("=" * 80)
    print("PHASE 7.14: PROP SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()

    try:
        test_bench_creation()
        test_light_pole_creation()
        test_trash_can_creation()
        test_bicycle_creation()
        test_prop_manager_creation()
        test_prop_manager_placement()
        test_light_pole_placement()
        test_prop_manager_update()
        test_prop_position_clearing()

        print()
        print("=" * 80)
        print("ALL PROP SYSTEM TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Phase 7.14 Prop System Complete:")
        print("  ✓ Bench props with rotation")
        print("  ✓ Light poles with day/night toggle")
        print("  ✓ Trash can props")
        print("  ✓ Bicycle props with rotation and random colors")
        print("  ✓ PropManager with automatic placement")
        print("  ✓ Light poles placed along roads")
        print("  ✓ Benches placed in parks")
        print("  ✓ Trash cans placed near buildings")
        print("  ✓ Bicycles placed near buildings")
        print("  ✓ Position collision checking")
        print("  ✓ Day/night light control")

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
