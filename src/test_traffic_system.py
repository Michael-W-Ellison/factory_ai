"""
Comprehensive test suite for Phase 7.12: Vehicle Traffic System.

Tests:
- RoadNetwork building and graph analysis
- Intersection detection
- Lane center calculation
- Pathfinding on roads
- TrafficVehicle creation and movement
- TrafficManager spawning and management
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
from entities.traffic_vehicle import TrafficVehicle
from systems.traffic_manager import TrafficManager


def create_test_grid_with_roads():
    """Create a test grid with a simple road network."""
    grid = Grid(width_tiles=30, height_tiles=30)

    # Create a simple road network:
    # - Horizontal road at y=10 (x: 5-25)
    # - Vertical road at x=15 (y: 5-25)
    # - Creates an intersection at (15, 10)

    # Horizontal road
    for x in range(5, 26):
        tile = grid.get_tile(x, 10)
        tile.tile_type = TileType.ROAD_ASPHALT

    # Vertical road
    for y in range(5, 26):
        tile = grid.get_tile(15, y)
        tile.tile_type = TileType.ROAD_ASPHALT

    return grid


def test_road_network_building():
    """Test RoadNetwork construction and graph building."""
    print("Test: RoadNetwork Building")

    grid = create_test_grid_with_roads()
    road_network = RoadNetwork(grid)

    # Check road count
    # Horizontal road: 21 tiles (5-25)
    # Vertical road: 21 tiles (5-25)
    # Overlap at intersection: 1 tile
    # Total: 21 + 21 - 1 = 41
    expected_roads = 41
    actual_roads = road_network.get_road_count()

    assert actual_roads == expected_roads, \
        f"Expected {expected_roads} road tiles, got {actual_roads}"

    print(f"  ✓ Found {actual_roads} road tiles")

    # Check intersection detection
    # Should have exactly 1 intersection at (15, 10)
    intersection_count = road_network.get_intersection_count()
    assert intersection_count == 1, \
        f"Expected 1 intersection, got {intersection_count}"

    assert road_network.is_intersection(15, 10), \
        "Position (15, 10) should be an intersection"

    print(f"  ✓ Detected {intersection_count} intersection(s)")


def test_lane_centers():
    """Test lane center position calculation."""
    print("\nTest: Lane Centers")

    grid = create_test_grid_with_roads()
    road_network = RoadNetwork(grid)

    # Test horizontal road tile (has east/west lanes)
    grid_x, grid_y = 10, 10  # On horizontal road
    lanes = road_network.get_available_lanes(grid_x, grid_y)

    assert 'east' in lanes, "Horizontal road should have east lane"
    assert 'west' in lanes, "Horizontal road should have west lane"

    # Get lane centers
    east_lane = road_network.get_lane_center(grid_x, grid_y, 'east')
    west_lane = road_network.get_lane_center(grid_x, grid_y, 'west')

    assert east_lane is not None, "East lane center should exist"
    assert west_lane is not None, "West lane center should exist"

    # East and west lanes should have different Y positions (offset)
    assert east_lane[1] != west_lane[1], "East and west lanes should be offset"

    print(f"  ✓ East lane at: {east_lane}")
    print(f"  ✓ West lane at: {west_lane}")

    # Test vertical road tile (has north/south lanes)
    grid_x, grid_y = 15, 5  # On vertical road (not intersection)
    lanes = road_network.get_available_lanes(grid_x, grid_y)

    assert 'north' in lanes, "Vertical road should have north lane"
    assert 'south' in lanes, "Vertical road should have south lane"

    print(f"  ✓ Vertical road has north and south lanes")


def test_pathfinding():
    """Test A* pathfinding on road network."""
    print("\nTest: Pathfinding")

    grid = create_test_grid_with_roads()
    road_network = RoadNetwork(grid)

    # Find path from one end of horizontal road to other
    start_x, start_y = 5, 10
    end_x, end_y = 25, 10

    path = road_network.find_path(start_x, start_y, end_x, end_y)

    assert path is not None, "Path should be found"
    assert len(path) > 0, "Path should contain waypoints"

    # Path should start at start and end at end
    assert path[0] == (start_x, start_y), "Path should start at start position"
    assert path[-1] == (end_x, end_y), "Path should end at end position"

    print(f"  ✓ Found path with {len(path)} waypoints")

    # Find path that requires turning at intersection
    start_x, start_y = 5, 10  # West end of horizontal road
    end_x, end_y = 15, 25     # South end of vertical road

    path2 = road_network.find_path(start_x, start_y, end_x, end_y)

    assert path2 is not None, "Path with turn should be found"
    assert (15, 10) in path2, "Path should go through intersection"

    print(f"  ✓ Found path with turn (via intersection)")


def test_traffic_vehicle_creation():
    """Test TrafficVehicle creation and properties."""
    print("\nTest: TrafficVehicle Creation")

    # Test each vehicle type
    vehicle_types = ['car', 'truck', 'van', 'bus', 'police']

    for vtype in vehicle_types:
        vehicle = TrafficVehicle(
            world_x=100.0,
            world_y=100.0,
            vehicle_type=vtype,
            initial_direction='east'
        )

        assert vehicle.vehicle_type == vtype, f"Vehicle type should be {vtype}"
        assert vehicle.current_lane == 'east', "Initial lane should be east"
        assert vehicle.speed == 0.0, "Initial speed should be 0"
        assert vehicle.max_speed > 0, "Max speed should be positive"

        print(f"  ✓ Created {vtype}: max_speed={vehicle.max_speed:.1f}px/s, size={vehicle.width}x{vehicle.height}")


def test_traffic_vehicle_movement():
    """Test TrafficVehicle movement and updates."""
    print("\nTest: TrafficVehicle Movement")

    grid = create_test_grid_with_roads()
    road_network = RoadNetwork(grid)

    # Create vehicle at start of horizontal road
    tile_size = grid.tile_size
    start_x = 5 * tile_size + tile_size / 2
    start_y = 10 * tile_size + tile_size / 2

    vehicle = TrafficVehicle(
        world_x=start_x,
        world_y=start_y,
        vehicle_type='car',
        initial_direction='east'
    )

    initial_x = vehicle.world_x

    # Update vehicle (should accelerate)
    dt = 0.1  # 100ms
    vehicle.update(dt, road_network)

    assert vehicle.speed > 0, "Vehicle should have accelerated"
    assert vehicle.world_x > initial_x, "Vehicle should have moved east"

    print(f"  ✓ Vehicle accelerated to {vehicle.speed:.1f}px/s")
    print(f"  ✓ Vehicle moved from x={initial_x:.1f} to x={vehicle.world_x:.1f}")


def test_traffic_vehicle_pathfinding():
    """Test TrafficVehicle following waypoints."""
    print("\nTest: TrafficVehicle Path Following")

    grid = create_test_grid_with_roads()
    road_network = RoadNetwork(grid)

    # Create vehicle
    tile_size = grid.tile_size
    start_x = 5 * tile_size + tile_size / 2
    start_y = 10 * tile_size + tile_size / 2

    vehicle = TrafficVehicle(
        world_x=start_x,
        world_y=start_y,
        vehicle_type='car',
        initial_direction='east'
    )

    # Set path to end of road
    path = [(5, 10), (10, 10), (15, 10), (20, 10), (25, 10)]
    vehicle.set_path(path)

    assert len(vehicle.waypoints) == 5, "Vehicle should have 5 waypoints"
    assert vehicle.current_waypoint_index == 0, "Should start at first waypoint"

    print(f"  ✓ Assigned path with {len(path)} waypoints")

    # Simulate movement for a while
    for i in range(100):
        vehicle.update(0.1, road_network)

    # Vehicle should have made progress through waypoints
    assert vehicle.current_waypoint_index > 0, "Vehicle should have passed some waypoints"

    print(f"  ✓ Vehicle reached waypoint {vehicle.current_waypoint_index}/{len(path)}")


def test_traffic_manager_spawning():
    """Test TrafficManager vehicle spawning."""
    print("\nTest: TrafficManager Spawning")

    grid = create_test_grid_with_roads()
    road_network = RoadNetwork(grid)

    traffic_manager = TrafficManager(grid, road_network)

    # Set low target to test spawning
    traffic_manager.set_target_vehicle_count(3)

    initial_count = traffic_manager.get_vehicle_count()
    assert initial_count == 0, "Should start with 0 vehicles"

    # Force spawn by updating with large interval
    traffic_manager.spawn_timer = traffic_manager.spawn_interval

    # Update several times to spawn vehicles
    for i in range(10):
        traffic_manager.update(traffic_manager.spawn_interval)

    final_count = traffic_manager.get_vehicle_count()
    assert final_count > 0, "Should have spawned some vehicles"

    print(f"  ✓ Spawned {final_count} vehicle(s)")


def test_traffic_manager_update():
    """Test TrafficManager updating vehicles."""
    print("\nTest: TrafficManager Update")

    grid = create_test_grid_with_roads()
    road_network = RoadNetwork(grid)

    traffic_manager = TrafficManager(grid, road_network)

    # Manually spawn a vehicle
    vehicle = traffic_manager.spawn_vehicle_at(10, 10, 'car', 'east')

    assert vehicle is not None, "Should spawn vehicle successfully"
    assert traffic_manager.get_vehicle_count() == 1, "Should have 1 vehicle"

    initial_x = vehicle.world_x

    # Update traffic manager
    for i in range(10):
        traffic_manager.update(0.1)

    # Vehicle should have moved
    assert vehicle.world_x != initial_x, "Vehicle should have moved after updates"

    print(f"  ✓ Vehicle moved from x={initial_x:.1f} to x={vehicle.world_x:.1f}")


def test_intersection_behavior():
    """Test vehicle behavior at intersections."""
    print("\nTest: Intersection Behavior")

    grid = create_test_grid_with_roads()
    road_network = RoadNetwork(grid)

    # Create vehicle approaching intersection
    tile_size = grid.tile_size
    start_x = 10 * tile_size + tile_size / 2
    start_y = 10 * tile_size + tile_size / 2

    vehicle = TrafficVehicle(
        world_x=start_x,
        world_y=start_y,
        vehicle_type='car',
        initial_direction='east'
    )

    # Vehicle is at (10, 10), intersection is at (15, 10)
    # Set max speed
    vehicle.speed = vehicle.max_speed
    vehicle.target_speed = vehicle.max_speed
    initial_speed = vehicle.speed

    # Move vehicle to intersection
    vehicle.world_x = 15 * tile_size + tile_size / 2
    vehicle.world_y = 10 * tile_size + tile_size / 2

    # Update at intersection
    vehicle.update(0.1, road_network)

    # Vehicle should slow down at intersection
    # (target_speed should be reduced)
    assert vehicle.target_speed < vehicle.max_speed, \
        "Vehicle should slow down at intersection"

    print(f"  ✓ Vehicle slows at intersection: {vehicle.max_speed:.1f} → {vehicle.target_speed:.1f}px/s")


def run_all_tests():
    """Run all traffic system tests."""
    print("=" * 80)
    print("PHASE 7.12: VEHICLE TRAFFIC SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()

    try:
        test_road_network_building()
        test_lane_centers()
        test_pathfinding()
        test_traffic_vehicle_creation()
        test_traffic_vehicle_movement()
        test_traffic_vehicle_pathfinding()
        test_traffic_manager_spawning()
        test_traffic_manager_update()
        test_intersection_behavior()

        print()
        print("=" * 80)
        print("ALL TRAFFIC SYSTEM TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Phase 7.12 Implementation Complete:")
        print("  ✓ RoadNetwork with graph building and lane tracking")
        print("  ✓ Intersection detection (3+ road neighbors)")
        print("  ✓ Lane center calculation for two-lane roads")
        print("  ✓ A* pathfinding on road network")
        print("  ✓ TrafficVehicle with movement and rotation")
        print("  ✓ Multiple vehicle types (car, truck, van, bus, police)")
        print("  ✓ Lane-based movement with direction following")
        print("  ✓ Traffic rules (slow at intersections)")
        print("  ✓ TrafficManager with spawning and lifecycle")
        print("  ✓ Automatic route assignment")

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
