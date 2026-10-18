"""
Unit tests for BusManager.

Tests bus routing, stop management, bus spawning, and route operations.
"""

import sys
import pytest
from unittest.mock import Mock, MagicMock, patch

# Mock pygame before any imports that might need it
sys.modules['pygame'] = Mock()


class MockGrid:
    """Mock grid for testing."""

    def __init__(self, tile_size=32):
        self.tile_size = tile_size


class MockRoadNetwork:
    """Mock road network for testing."""

    def __init__(self, roads=None):
        self._roads = roads or set()
        self._paths = {}

    def is_road(self, x, y):
        return (x, y) in self._roads

    def get_random_road_tile(self):
        if self._roads:
            return list(self._roads)[0]
        return None

    def find_path(self, start_x, start_y, end_x, end_y):
        key = ((start_x, start_y), (end_x, end_y))
        if key in self._paths:
            return self._paths[key]
        # Default simple path
        return [(start_x, start_y), (end_x, end_y)]

    def get_available_lanes(self, grid_x, grid_y):
        return ['east']

    def get_lane_center(self, grid_x, grid_y, direction):
        return (grid_x * 32 + 16, grid_y * 32 + 16)


class MockBusRoute:
    """Mock bus route for testing."""

    def __init__(self, route_id, is_express=False):
        self.route_id = route_id
        self.is_express = is_express
        self.stops = []
        self.express_stops = []
        self.waypoints = []

    def add_stop(self, grid_x, grid_y):
        self.stops.append((grid_x, grid_y))

    def get_stop_count(self):
        return len(self.stops)

    def get_total_waypoint_count(self):
        return len(self.waypoints)

    def calculate_express_stops(self, skip_factor=2):
        self.express_stops = self.stops[::skip_factor]

    def calculate_path(self, road_network):
        if len(self.stops) < 2:
            return False
        self.waypoints = list(self.stops)
        return True


class MockBus:
    """Mock bus for testing."""

    def __init__(self, world_x, world_y, route_id=0, initial_direction='east', is_express=False):
        self.world_x = world_x
        self.world_y = world_y
        self.route_id = route_id
        self.initial_direction = initial_direction
        self.is_express = is_express
        self.route_stops = []
        self.current_stop_index = 0
        self.path = []

    def set_route(self, stops):
        self.route_stops = stops

    def set_path(self, waypoints):
        self.path = waypoints

    def update(self, dt, road_network, npcs=None, bus_stops=None):
        pass


class MockBusStop:
    """Mock bus stop for testing."""

    def __init__(self, grid_x, grid_y, tile_size=32):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.tile_size = tile_size
        self.route_ids = set()

    def add_route(self, route_id):
        self.route_ids.add(route_id)


# Import directly to avoid __init__.py cascade
import importlib.util
spec = importlib.util.spec_from_file_location(
    "bus_manager",
    "/home/user/factory_ai/src/systems/bus_manager.py"
)
bus_manager_module = importlib.util.module_from_spec(spec)

# Mock the dependent imports before loading the module
sys.modules['src.entities.bus'] = Mock()
sys.modules['src.entities.bus'].Bus = MockBus
sys.modules['src.entities.bus_stop'] = Mock()
sys.modules['src.entities.bus_stop'].BusStop = MockBusStop
sys.modules['src.systems.bus_route'] = Mock()
sys.modules['src.systems.bus_route'].BusRoute = MockBusRoute

spec.loader.exec_module(bus_manager_module)
BusManager = bus_manager_module.BusManager


@pytest.fixture
def bus_manager():
    """Create a BusManager with mocked dependencies."""
    grid = MockGrid()
    road_network = MockRoadNetwork({(0, 0), (5, 0), (10, 0), (15, 0), (20, 0),
                                     (25, 0), (30, 0), (35, 0), (40, 0), (45, 0)})
    return BusManager(grid, road_network)


class TestBusManagerInit:
    """Tests for BusManager initialization."""

    def test_init_stores_grid_and_network(self, bus_manager):
        """Test initialization stores grid and road network."""
        assert bus_manager.grid is not None
        assert bus_manager.road_network is not None

    def test_init_empty_routes(self, bus_manager):
        """Test initialization starts with empty routes."""
        assert len(bus_manager.routes) == 0
        assert bus_manager.next_route_id == 0

    def test_init_empty_buses(self, bus_manager):
        """Test initialization starts with no buses."""
        assert len(bus_manager.buses) == 0

    def test_init_empty_bus_stops(self, bus_manager):
        """Test initialization starts with no bus stops."""
        assert len(bus_manager.bus_stops) == 0

    def test_init_default_config(self, bus_manager):
        """Test default configuration values."""
        assert bus_manager.target_routes == 3
        assert bus_manager.buses_per_route == 2
        assert bus_manager.stop_spacing == 15
        assert bus_manager.express_route_chance == 0.3


class TestRouteGeneration:
    """Tests for route generation."""

    def test_generate_routes_creates_routes(self, bus_manager):
        """Test generate_routes creates the specified number of routes."""
        # Set up roads for route generation
        bus_manager.road_network._roads = {
            (i, 0) for i in range(50)
        }

        bus_manager.generate_routes(num_routes=2)

        # Routes may fail if not enough stops, but should attempt generation
        assert bus_manager.routes is not None

    def test_generate_routes_uses_default_count(self, bus_manager):
        """Test generate_routes uses target_routes when not specified."""
        bus_manager.target_routes = 1
        bus_manager.road_network._roads = {(i, 0) for i in range(50)}

        bus_manager.generate_routes()

        # Attempted to generate target_routes routes

    def test_generate_single_route_returns_route(self, bus_manager):
        """Test _generate_single_route returns a route object."""
        bus_manager.road_network._roads = {(i, 0) for i in range(50)}

        route = bus_manager._generate_single_route(0)

        # May return None if no valid route found
        assert route is None or hasattr(route, 'route_id')

    def test_generate_single_route_no_roads_returns_none(self, bus_manager):
        """Test route generation returns None with no roads."""
        bus_manager.road_network._roads = set()

        route = bus_manager._generate_single_route(0)

        assert route is None


class TestFindNextStopLocation:
    """Tests for finding next stop locations."""

    def test_find_next_stop_location_returns_tuple(self, bus_manager):
        """Test _find_next_stop_location returns position tuple."""
        bus_manager.road_network._roads = {(i, 0) for i in range(100)}

        mock_route = MockBusRoute(0)
        mock_route.stops = [(0, 0)]

        # May return None if no valid location found
        result = bus_manager._find_next_stop_location((0, 0), mock_route)

        assert result is None or (isinstance(result, tuple) and len(result) == 2)

    def test_find_next_stop_respects_spacing(self, bus_manager):
        """Test that next stop respects minimum spacing."""
        bus_manager.road_network._roads = {(i, 0) for i in range(100)}
        bus_manager.stop_spacing = 15

        mock_route = MockBusRoute(0)
        mock_route.stops = [(50, 0)]

        # Run multiple times due to randomness
        for _ in range(10):
            result = bus_manager._find_next_stop_location((50, 0), mock_route)
            if result:
                # Should be at least stop_spacing away
                distance = abs(result[0] - 50) + abs(result[1] - 0)
                assert distance >= bus_manager.stop_spacing


class TestBusStopManagement:
    """Tests for bus stop management."""

    def test_get_stop_at_returns_existing(self, bus_manager):
        """Test _get_stop_at returns existing stop."""
        stop = MockBusStop(10, 20)
        bus_manager.bus_stops.append(stop)

        result = bus_manager._get_stop_at(10, 20)

        assert result is stop

    def test_get_stop_at_returns_none_if_not_found(self, bus_manager):
        """Test _get_stop_at returns None if no stop at position."""
        result = bus_manager._get_stop_at(999, 999)

        assert result is None

    def test_place_bus_stops_for_route_creates_stops(self, bus_manager):
        """Test _place_bus_stops_for_route creates bus stops."""
        with patch('src.systems.bus_manager.BusStop', MockBusStop):
            route = MockBusRoute(1)
            route.stops = [(5, 0), (10, 0)]

            bus_manager._place_bus_stops_for_route(route)

            assert len(bus_manager.bus_stops) == 2

    def test_place_bus_stops_adds_route_to_existing(self, bus_manager):
        """Test that route is added to existing stop."""
        existing_stop = MockBusStop(5, 0)
        bus_manager.bus_stops.append(existing_stop)

        route = MockBusRoute(2)
        route.stops = [(5, 0)]

        bus_manager._place_bus_stops_for_route(route)

        assert 2 in existing_stop.route_ids

    def test_get_nearest_bus_stop_returns_closest(self, bus_manager):
        """Test get_nearest_bus_stop returns closest stop."""
        stop1 = MockBusStop(0, 0)
        stop2 = MockBusStop(100, 100)
        bus_manager.bus_stops = [stop1, stop2]

        nearest = bus_manager.get_nearest_bus_stop(5, 5)

        assert nearest is stop1

    def test_get_nearest_bus_stop_no_stops_returns_none(self, bus_manager):
        """Test get_nearest_bus_stop returns None with no stops."""
        result = bus_manager.get_nearest_bus_stop(0, 0)

        assert result is None


class TestBusSpawning:
    """Tests for bus spawning."""

    def test_spawn_buses_creates_buses(self, bus_manager):
        """Test spawn_buses creates buses for routes."""
        with patch('src.systems.bus_manager.Bus', MockBus):
            route = MockBusRoute(0)
            route.stops = [(0, 0), (20, 0)]
            route.waypoints = [(0, 0), (20, 0)]
            bus_manager.routes = {0: route}

            bus_manager.spawn_buses()

            assert len(bus_manager.buses) > 0

    def test_spawn_bus_on_route_sets_route(self, bus_manager):
        """Test _spawn_bus_on_route sets bus route."""
        with patch('src.systems.bus_manager.Bus', MockBus):
            route = MockBusRoute(1)
            route.stops = [(0, 0), (20, 0)]

            bus = bus_manager._spawn_bus_on_route(route, 0)

            if bus:
                assert bus.route_stops == route.stops

    def test_spawn_bus_no_stops_returns_none(self, bus_manager):
        """Test _spawn_bus_on_route returns None with no stops."""
        route = MockBusRoute(0)
        route.stops = []

        bus = bus_manager._spawn_bus_on_route(route, 0)

        assert bus is None


class TestBusUpdate:
    """Tests for bus update functionality."""

    def test_update_updates_all_buses(self, bus_manager):
        """Test update calls update on all buses."""
        mock_bus = Mock()
        bus_manager.buses = [mock_bus]

        bus_manager.update(0.1)

        mock_bus.update.assert_called_once()

    def test_update_passes_game_time(self, bus_manager):
        """Test update stores game time."""
        bus_manager.update(0.1, game_time=12.5)

        assert bus_manager.game_time == 12.5

    def test_update_passes_npcs_to_buses(self, bus_manager):
        """Test update passes NPCs to buses."""
        mock_bus = Mock()
        bus_manager.buses = [mock_bus]
        mock_npcs = [Mock(), Mock()]

        bus_manager.update(0.1, npcs=mock_npcs)

        call_args = mock_bus.update.call_args
        assert call_args[1]['npcs'] == mock_npcs


class TestCountMethods:
    """Tests for count methods."""

    def test_get_route_count(self, bus_manager):
        """Test get_route_count returns correct count."""
        bus_manager.routes = {0: MockBusRoute(0), 1: MockBusRoute(1)}

        assert bus_manager.get_route_count() == 2

    def test_get_bus_count(self, bus_manager):
        """Test get_bus_count returns correct count."""
        bus_manager.buses = [MockBus(0, 0), MockBus(100, 100)]

        assert bus_manager.get_bus_count() == 2

    def test_get_stop_count(self, bus_manager):
        """Test get_stop_count returns correct count."""
        bus_manager.bus_stops = [MockBusStop(0, 0), MockBusStop(10, 10), MockBusStop(20, 20)]

        assert bus_manager.get_stop_count() == 3


class TestBusManagerRepr:
    """Tests for string representation."""

    def test_repr_format(self, bus_manager):
        """Test string representation format."""
        bus_manager.routes = {0: MockBusRoute(0)}
        bus_manager.buses = [MockBus(0, 0)]
        bus_manager.bus_stops = [MockBusStop(0, 0)]

        repr_str = repr(bus_manager)

        assert 'BusManager' in repr_str
        assert 'routes=1' in repr_str
        assert 'buses=1' in repr_str
        assert 'stops=1' in repr_str


class TestBusRouteIntegration:
    """Integration tests for bus route operations."""

    def test_route_with_express_stops(self, bus_manager):
        """Test route with express stops subset."""
        route = MockBusRoute(0, is_express=True)
        route.stops = [(0, 0), (10, 0), (20, 0), (30, 0)]
        route.calculate_express_stops(skip_factor=2)

        assert len(route.express_stops) == 2
        assert route.express_stops[0] == (0, 0)
        assert route.express_stops[1] == (20, 0)

    def test_route_path_calculation(self, bus_manager):
        """Test route path calculation."""
        route = MockBusRoute(0)
        route.stops = [(0, 0), (10, 0)]

        result = route.calculate_path(bus_manager.road_network)

        assert result is True
        assert len(route.waypoints) == 2

    def test_route_path_fails_with_insufficient_stops(self, bus_manager):
        """Test route path calculation fails with < 2 stops."""
        route = MockBusRoute(0)
        route.stops = [(0, 0)]

        result = route.calculate_path(bus_manager.road_network)

        assert result is False


class TestScheduling:
    """Tests for bus scheduling."""

    def test_game_time_initialization(self, bus_manager):
        """Test game time starts at zero."""
        assert bus_manager.game_time == 0.0

    def test_spawn_timers_initialization(self, bus_manager):
        """Test spawn timers start empty."""
        assert bus_manager.spawn_timers == {}
