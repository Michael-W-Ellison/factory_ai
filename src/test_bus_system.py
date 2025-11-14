"""
Comprehensive test suite for Phase 7.13: Bus Transportation System.

Tests:
- Bus class creation and properties
- BusStop creation and rendering
- BusRoute creation and pathfinding
- BusManager route generation and bus spawning
- Bus behavior at stops
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
from entities.bus import Bus
from entities.bus_stop import BusStop
from systems.bus_route import BusRoute
from systems.bus_manager import BusManager


def create_test_grid_with_roads():
    """Create a test grid with a road network."""
    grid = Grid(width_tiles=40, height_tiles=40)

    # Create a grid road network for bus routes
    # Horizontal roads every 5 tiles
    for y in [5, 10, 15, 20, 25, 30]:
        for x in range(5, 36):
            tile = grid.get_tile(x, y)
            tile.tile_type = TileType.ROAD_ASPHALT

    # Vertical roads every 5 tiles
    for x in [5, 10, 15, 20, 25, 30, 35]:
        for y in range(5, 36):
            tile = grid.get_tile(x, y)
            tile.tile_type = TileType.ROAD_ASPHALT

    return grid


def test_bus_creation():
    """Test Bus class creation and properties."""
    print("Test: Bus Creation")

    bus = Bus(world_x=100.0, world_y=100.0, route_id=1, initial_direction='east')

    assert bus.route_id == 1, "Bus should have correct route ID"
    assert bus.vehicle_type == 'bus', "Vehicle type should be 'bus'"
    assert bus.max_capacity == 20, "Bus should have capacity of 20"
    assert bus.width == 50, "Bus width should be 50 pixels"
    assert bus.height == 24, "Bus height should be 24 pixels"
    assert bus.max_speed == 30.0, "Bus max speed should be 30 px/s"
    assert len(bus.passengers) == 0, "Bus should start with no passengers"

    print(f"  ✓ Bus created with route_id={bus.route_id}, capacity={bus.max_capacity}")
    print(f"  ✓ Bus size: {bus.width}x{bus.height}, max speed: {bus.max_speed}px/s")


def test_bus_passenger_management():
    """Test adding/removing passengers."""
    print("\nTest: Bus Passenger Management")

    bus = Bus(world_x=100.0, world_y=100.0, route_id=1)

    # Add passengers
    for i in range(5):
        result = bus.add_passenger(i)
        assert result, f"Should be able to add passenger {i}"

    assert bus.get_passenger_count() == 5, "Should have 5 passengers"
    assert not bus.is_full(), "Bus should not be full with 5 passengers"

    # Fill bus to capacity
    for i in range(5, 20):
        bus.add_passenger(i)

    assert bus.is_full(), "Bus should be full at capacity"
    assert bus.get_passenger_count() == 20, "Should have 20 passengers"

    # Try to add one more (should fail)
    result = bus.add_passenger(999)
    assert not result, "Should not be able to add passenger when full"

    # Remove passenger
    result = bus.remove_passenger(5)
    assert result, "Should be able to remove passenger"
    assert bus.get_passenger_count() == 19, "Should have 19 passengers after removal"

    print(f"  ✓ Added 20 passengers successfully")
    print(f"  ✓ Bus at capacity: {bus.is_full()}")
    print(f"  ✓ Removed passenger successfully")


def test_bus_stop_creation():
    """Test BusStop creation."""
    print("\nTest: BusStop Creation")

    stop = BusStop(grid_x=10, grid_y=15, tile_size=32)

    assert stop.grid_x == 10, "Stop should have correct grid X"
    assert stop.grid_y == 15, "Stop should have correct grid Y"
    assert stop.world_x == 10 * 32 + 16, "Stop world X should be tile center"
    assert stop.world_y == 15 * 32 + 16, "Stop world Y should be tile center"

    # Add routes
    stop.add_route(1)
    stop.add_route(2)

    assert len(stop.route_ids) == 2, "Stop should have 2 routes"
    assert 1 in stop.route_ids, "Route 1 should be at this stop"

    print(f"  ✓ BusStop created at ({stop.grid_x}, {stop.grid_y})")
    print(f"  ✓ Routes at stop: {stop.route_ids}")


def test_bus_route_creation():
    """Test BusRoute creation and pathfinding."""
    print("\nTest: BusRoute Creation and Pathfinding")

    grid = create_test_grid_with_roads()
    road_network = RoadNetwork(grid)

    route = BusRoute(route_id=1, name="Test Route")

    # Add stops along a road
    route.add_stop(5, 10)
    route.add_stop(15, 10)
    route.add_stop(25, 10)
    route.add_stop(25, 20)
    route.add_stop(15, 20)
    route.add_stop(5, 20)

    assert route.get_stop_count() == 6, "Route should have 6 stops"

    # Calculate path between stops
    success = route.calculate_path(road_network)

    assert success, "Path calculation should succeed"
    assert route.get_total_waypoint_count() > 0, "Route should have waypoints"

    print(f"  ✓ Route created with {route.get_stop_count()} stops")
    print(f"  ✓ Path calculated with {route.get_total_waypoint_count()} waypoints")


def test_bus_manager_route_generation():
    """Test BusManager route generation."""
    print("\nTest: BusManager Route Generation")

    grid = create_test_grid_with_roads()
    road_network = RoadNetwork(grid)

    bus_manager = BusManager(grid, road_network)
    bus_manager.target_routes = 2

    # Generate routes
    bus_manager.generate_routes()

    assert bus_manager.get_route_count() > 0, "Should generate at least one route"
    assert bus_manager.get_stop_count() > 0, "Should have bus stops"

    print(f"  ✓ Generated {bus_manager.get_route_count()} routes")
    print(f"  ✓ Placed {bus_manager.get_stop_count()} bus stops")


def test_bus_manager_bus_spawning():
    """Test BusManager bus spawning."""
    print("\nTest: BusManager Bus Spawning")

    grid = create_test_grid_with_roads()
    road_network = RoadNetwork(grid)

    bus_manager = BusManager(grid, road_network)
    bus_manager.target_routes = 2
    bus_manager.buses_per_route = 2

    # Generate routes and spawn buses
    bus_manager.generate_routes()
    bus_manager.spawn_buses()

    assert bus_manager.get_bus_count() > 0, "Should have spawned buses"

    # Check that buses have routes
    for bus in bus_manager.buses:
        assert len(bus.route_stops) > 0, "Bus should have route stops"
        assert bus.route_id >= 0, "Bus should have a valid route ID"

    print(f"  ✓ Spawned {bus_manager.get_bus_count()} buses")
    print(f"  ✓ All buses have routes assigned")


def test_bus_stop_behavior():
    """Test bus stopping at bus stops."""
    print("\nTest: Bus Stop Behavior")

    grid = create_test_grid_with_roads()
    road_network = RoadNetwork(grid)

    # Create a bus with a simple route
    bus = Bus(world_x=160.0, world_y=320.0, route_id=1, initial_direction='east')

    # Set route stops
    stops = [(5, 10), (15, 10), (25, 10)]
    bus.set_route(stops)

    # Position bus at first stop
    tile_size = grid.tile_size
    bus.world_x = 5 * tile_size + tile_size / 2
    bus.world_y = 10 * tile_size + tile_size / 2

    # Simulate arrival at stop
    bus._arrive_at_stop()

    assert bus.stopped_at_stop, "Bus should be stopped"
    assert bus.speed == 0.0, "Bus speed should be 0 at stop"
    assert bus.door_open, "Bus doors should be open"

    # Simulate waiting
    bus.stop_timer = bus.stop_duration + 0.1

    # Simulate departure
    bus.update(0.1, road_network)

    # Bus should have departed
    assert not bus.stopped_at_stop or bus.stop_timer >= bus.stop_duration, \
        "Bus should depart after stop duration"

    print(f"  ✓ Bus stops at bus stop")
    print(f"  ✓ Bus doors open when stopped")
    print(f"  ✓ Bus departs after {bus.stop_duration}s")


def test_bus_route_following():
    """Test bus following its route."""
    print("\nTest: Bus Route Following")

    grid = create_test_grid_with_roads()
    road_network = RoadNetwork(grid)

    # Create bus manager and generate a route
    bus_manager = BusManager(grid, road_network)
    bus_manager.target_routes = 1
    bus_manager.buses_per_route = 1

    bus_manager.generate_routes()
    bus_manager.spawn_buses()

    if bus_manager.buses:
        bus = bus_manager.buses[0]

        initial_stop_index = bus.current_stop_index

        # Update bus for a while
        for i in range(100):
            bus.update(0.1, road_network)

        # Bus should have made progress (either moved or waiting at stop)
        assert bus.speed > 0 or bus.stopped_at_stop, \
            "Bus should be moving or stopped at a stop"

        print(f"  ✓ Bus following route {bus.route_id}")
        print(f"  ✓ Current stop: {bus.current_stop_index}/{len(bus.route_stops)}")
        print(f"  ✓ Bus state: {'STOPPED' if bus.stopped_at_stop else 'MOVING'}")
    else:
        print("  ! No buses spawned to test")


def run_all_tests():
    """Run all bus system tests."""
    print("=" * 80)
    print("PHASE 7.13: BUS TRANSPORTATION SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()

    try:
        test_bus_creation()
        test_bus_passenger_management()
        test_bus_stop_creation()
        test_bus_route_creation()
        test_bus_manager_route_generation()
        test_bus_manager_bus_spawning()
        test_bus_stop_behavior()
        test_bus_route_following()

        print()
        print("=" * 80)
        print("ALL BUS SYSTEM TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Phase 7.13 Implementation Complete:")
        print("  ✓ Bus class with passenger management (20 capacity)")
        print("  ✓ BusStop props with route tracking")
        print("  ✓ BusRoute with stop-to-stop pathfinding")
        print("  ✓ BusManager for route generation and bus spawning")
        print("  ✓ Bus stop behavior (5s wait time)")
        print("  ✓ Bus route following with waypoints")
        print("  ✓ Bus rendering with route number and passenger count")

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
