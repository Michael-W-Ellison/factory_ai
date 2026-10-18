"""
Tests for TrafficManager.

Tests traffic flow mechanics including:
- Vehicle spawning
- Vehicle routing
- Parked vehicles
- Vehicle type selection
- Spawn location finding
- Vehicle lifecycle management
- Statistics tracking
"""

import sys
from unittest.mock import MagicMock, patch
import random

# Mock pygame before any imports that might need it
sys.modules['pygame'] = MagicMock()
sys.modules['pygame.font'] = MagicMock()
sys.modules['pygame.transform'] = MagicMock()
sys.modules['pygame.Surface'] = MagicMock()

import pytest

from src.systems.traffic_manager import TrafficManager, ParkedVehicle


class MockGrid:
    """Mock grid for testing."""

    def __init__(self, width: int = 100, height: int = 100, tile_size: int = 32):
        self.width_tiles = width
        self.height_tiles = height
        self.tile_size = tile_size


class MockRoadNetwork:
    """Mock road network for testing."""

    def __init__(self):
        self.roads = {}  # (x, y) -> True if road
        self.lanes = {}  # (x, y) -> list of available lanes
        self.paths = {}  # (start, end) -> path

    def is_road(self, x: int, y: int) -> bool:
        return self.roads.get((x, y), False)

    def get_available_lanes(self, x: int, y: int) -> list:
        return self.lanes.get((x, y), [])

    def get_lane_center(self, grid_x: int, grid_y: int, direction: str):
        if not self.is_road(grid_x, grid_y):
            return None
        # Return center position in world coordinates
        return (grid_x * 32 + 16, grid_y * 32 + 16)

    def get_random_road_tile(self):
        if self.roads:
            road_tiles = [pos for pos, is_road in self.roads.items() if is_road]
            if road_tiles:
                return random.choice(road_tiles)
        return None

    def find_path(self, start_x: int, start_y: int, end_x: int, end_y: int):
        key = ((start_x, start_y), (end_x, end_y))
        return self.paths.get(key, [(start_x, start_y), (end_x, end_y)])

    def add_road(self, x: int, y: int, lanes: list = None):
        self.roads[(x, y)] = True
        self.lanes[(x, y)] = lanes or ['east', 'west', 'north', 'south']


class MockTrafficVehicle:
    """Mock traffic vehicle for testing."""

    VEHICLE_TYPES = {
        'car': {'width': 20, 'height': 10, 'color_choices': [(200, 0, 0)]},
        'truck': {'width': 30, 'height': 12, 'color_choices': [(0, 200, 0)]},
        'van': {'width': 25, 'height': 11, 'color_choices': [(0, 0, 200)]},
        'bus': {'width': 40, 'height': 14, 'color_choices': [(255, 255, 0)]},
        'police': {'width': 20, 'height': 10, 'color_choices': [(255, 255, 255)]},
    }

    def __init__(self, world_x: float, world_y: float, vehicle_type: str = 'car',
                 initial_direction: str = 'east'):
        self.world_x = world_x
        self.world_y = world_y
        self.vehicle_type = vehicle_type
        self.direction = initial_direction
        self.waypoints = []
        self.current_waypoint_index = 0
        self.destination = None
        self._off_map = False

    def update(self, dt, road_network, other_vehicles=None, npcs=None, time_of_day=None):
        pass

    def is_off_map(self, grid) -> bool:
        return self._off_map

    def set_path(self, path):
        self.waypoints = path

    def set_destination(self, x, y):
        self.destination = (x, y)

    def render(self, screen, camera):
        pass


@pytest.fixture
def mock_grid():
    """Provide a mock grid."""
    return MockGrid()


@pytest.fixture
def mock_road_network():
    """Provide a mock road network."""
    return MockRoadNetwork()


@pytest.fixture
def traffic_manager(mock_grid, mock_road_network):
    """Provide a traffic manager with mocked dependencies."""
    return TrafficManager(mock_grid, mock_road_network)


class TestParkedVehicle:
    """Tests for ParkedVehicle class."""

    def test_parked_vehicle_initialization(self):
        """Test that ParkedVehicle initializes correctly."""
        with patch.object(MockTrafficVehicle, 'VEHICLE_TYPES', MockTrafficVehicle.VEHICLE_TYPES):
            with patch('src.systems.traffic_manager.TrafficVehicle', MockTrafficVehicle):
                parked = ParkedVehicle(
                    world_x=100.0,
                    world_y=200.0,
                    vehicle_type='car',
                    facing_direction='east'
                )

                assert parked.world_x == 100.0
                assert parked.world_y == 200.0
                assert parked.vehicle_type == 'car'
                assert parked.facing_direction == 'east'
                assert parked.facing_angle == 0

    def test_parked_vehicle_facing_angles(self):
        """Test that ParkedVehicle calculates facing angles correctly."""
        with patch('src.systems.traffic_manager.TrafficVehicle', MockTrafficVehicle):
            directions_and_angles = [
                ('east', 0),
                ('south', 90),
                ('west', 180),
                ('north', 270),
            ]

            for direction, expected_angle in directions_and_angles:
                parked = ParkedVehicle(
                    world_x=100.0,
                    world_y=200.0,
                    vehicle_type='car',
                    facing_direction=direction
                )
                assert parked.facing_angle == expected_angle


class TestTrafficManagerInit:
    """Tests for TrafficManager initialization."""

    def test_manager_initialization(self, traffic_manager):
        """Test that TrafficManager initializes correctly."""
        assert traffic_manager.vehicles == []
        assert traffic_manager.parked_vehicles == []
        assert traffic_manager.spawn_timer == 0.0
        assert traffic_manager.spawn_interval == 2.0

    def test_manager_vehicle_limits(self, traffic_manager):
        """Test that vehicle limits are set correctly."""
        assert traffic_manager.target_vehicle_count == 15
        assert traffic_manager.max_vehicle_count == 25

    def test_manager_vehicle_weights(self, traffic_manager):
        """Test that vehicle type weights are configured."""
        weights = traffic_manager.vehicle_type_weights

        assert 'car' in weights
        assert 'truck' in weights
        assert 'van' in weights
        assert 'bus' in weights
        assert 'police' in weights
        assert sum(weights.values()) == pytest.approx(1.0)


class TestVehicleSpawning:
    """Tests for vehicle spawning logic."""

    def test_spawn_vehicle_at_success(self, traffic_manager, mock_road_network):
        """Test successfully spawning a vehicle at a specific location."""
        mock_road_network.add_road(10, 10, ['east', 'west'])

        with patch('src.systems.traffic_manager.TrafficVehicle', MockTrafficVehicle):
            vehicle = traffic_manager.spawn_vehicle_at(10, 10, 'car', 'east')

            assert vehicle is not None
            assert vehicle.vehicle_type == 'car'
            assert len(traffic_manager.vehicles) == 1

    def test_spawn_vehicle_at_no_road(self, traffic_manager, mock_road_network):
        """Test that spawning on non-road location fails."""
        # No roads added

        with patch('src.systems.traffic_manager.TrafficVehicle', MockTrafficVehicle):
            vehicle = traffic_manager.spawn_vehicle_at(10, 10, 'car')

            assert vehicle is None
            assert len(traffic_manager.vehicles) == 0

    def test_spawn_vehicle_at_auto_direction(self, traffic_manager, mock_road_network):
        """Test that direction is auto-detected when not specified."""
        mock_road_network.add_road(10, 10, ['north'])

        with patch('src.systems.traffic_manager.TrafficVehicle', MockTrafficVehicle):
            vehicle = traffic_manager.spawn_vehicle_at(10, 10, 'truck')

            assert vehicle is not None
            assert vehicle.direction == 'north'


class TestChooseVehicleType:
    """Tests for vehicle type selection."""

    def test_choose_vehicle_type_returns_valid_type(self, traffic_manager):
        """Test that chosen vehicle type is valid."""
        for _ in range(20):
            vehicle_type = traffic_manager._choose_vehicle_type()

            assert vehicle_type in traffic_manager.vehicle_type_weights.keys()

    def test_choose_vehicle_type_respects_weights(self, traffic_manager):
        """Test that vehicle types are chosen according to weights."""
        # Run many iterations to check distribution
        type_counts = {t: 0 for t in traffic_manager.vehicle_type_weights.keys()}

        for _ in range(1000):
            vehicle_type = traffic_manager._choose_vehicle_type()
            type_counts[vehicle_type] += 1

        # Cars should be most common (60% weight)
        assert type_counts['car'] > type_counts['truck']
        assert type_counts['car'] > type_counts['van']
        assert type_counts['car'] > type_counts['bus']
        assert type_counts['car'] > type_counts['police']


class TestFindSpawnLocation:
    """Tests for spawn location finding."""

    def test_find_spawn_on_edge_north(self, traffic_manager, mock_road_network):
        """Test finding spawn location on north edge."""
        mock_road_network.add_road(5, 0, ['south'])

        result = traffic_manager._find_spawn_on_edge('north')

        assert result is not None
        grid_x, grid_y, direction = result
        assert grid_y == 0
        assert direction == 'south'

    def test_find_spawn_on_edge_south(self, traffic_manager, mock_road_network, mock_grid):
        """Test finding spawn location on south edge."""
        south_edge = mock_grid.height_tiles - 1
        mock_road_network.add_road(5, south_edge, ['north'])

        result = traffic_manager._find_spawn_on_edge('south')

        assert result is not None
        grid_x, grid_y, direction = result
        assert grid_y == south_edge
        assert direction == 'north'

    def test_find_spawn_on_edge_west(self, traffic_manager, mock_road_network):
        """Test finding spawn location on west edge."""
        mock_road_network.add_road(0, 5, ['east'])

        result = traffic_manager._find_spawn_on_edge('west')

        assert result is not None
        grid_x, grid_y, direction = result
        assert grid_x == 0
        assert direction == 'east'

    def test_find_spawn_on_edge_east(self, traffic_manager, mock_road_network, mock_grid):
        """Test finding spawn location on east edge."""
        east_edge = mock_grid.width_tiles - 1
        mock_road_network.add_road(east_edge, 5, ['west'])

        result = traffic_manager._find_spawn_on_edge('east')

        assert result is not None
        grid_x, grid_y, direction = result
        assert grid_x == east_edge
        assert direction == 'west'

    def test_find_spawn_on_edge_no_roads(self, traffic_manager):
        """Test finding spawn returns None when no roads on edge."""
        result = traffic_manager._find_spawn_on_edge('north')

        assert result is None

    def test_find_random_road_spawn(self, traffic_manager, mock_road_network):
        """Test finding random road spawn."""
        mock_road_network.add_road(25, 25, ['east', 'west'])

        result = traffic_manager._find_random_road_spawn()

        assert result is not None
        grid_x, grid_y, direction = result
        assert grid_x == 25
        assert grid_y == 25

    def test_find_random_road_spawn_no_roads(self, traffic_manager):
        """Test finding random road spawn returns None when no roads."""
        result = traffic_manager._find_random_road_spawn()

        assert result is None


class TestVehicleUpdate:
    """Tests for vehicle update logic."""

    def test_update_increments_spawn_timer(self, traffic_manager):
        """Test that update increments the spawn timer."""
        initial_timer = traffic_manager.spawn_timer

        traffic_manager.update(dt=1.0)

        assert traffic_manager.spawn_timer == initial_timer + 1.0

    def test_update_removes_off_map_vehicles(self, traffic_manager):
        """Test that update removes vehicles that are off map."""
        mock_vehicle = MockTrafficVehicle(100.0, 100.0)
        mock_vehicle._off_map = True
        traffic_manager.vehicles.append(mock_vehicle)

        traffic_manager.update(dt=0.1)

        assert mock_vehicle not in traffic_manager.vehicles

    def test_update_handles_idle_vehicles(self, traffic_manager, mock_road_network):
        """Test that update handles vehicles with no waypoints."""
        mock_road_network.add_road(10, 10, ['east'])

        mock_vehicle = MockTrafficVehicle(320.0, 320.0)
        mock_vehicle.waypoints = []
        mock_vehicle.current_waypoint_index = 0
        traffic_manager.vehicles.append(mock_vehicle)

        # Set seed for reproducibility
        random.seed(0)

        traffic_manager.update(dt=0.1)

        # Vehicle may be despawned or given new route (30% chance to despawn)
        # We just verify no error occurs


class TestParkedVehicleGeneration:
    """Tests for parked vehicle generation."""

    def test_generate_parked_vehicles(self, traffic_manager, mock_road_network):
        """Test generating parked vehicles."""
        mock_road_network.add_road(10, 10, ['east', 'west'])
        mock_road_network.add_road(20, 20, ['north', 'south'])

        with patch('src.systems.traffic_manager.TrafficVehicle', MockTrafficVehicle):
            traffic_manager.generate_parked_vehicles(count=5)

            # Should have generated some parked vehicles (may be less if no valid spots)
            assert isinstance(traffic_manager.parked_vehicles, list)

    def test_generate_parked_vehicles_clears_existing(self, traffic_manager, mock_road_network):
        """Test that generating parked vehicles clears existing ones."""
        mock_road_network.add_road(10, 10, ['east'])

        # Add a pre-existing parked vehicle
        with patch('src.systems.traffic_manager.TrafficVehicle', MockTrafficVehicle):
            existing = ParkedVehicle(100.0, 100.0, 'car', 'east')
            traffic_manager.parked_vehicles.append(existing)

            traffic_manager.generate_parked_vehicles(count=0)

            assert existing not in traffic_manager.parked_vehicles


class TestVehicleManagement:
    """Tests for vehicle management functions."""

    def test_get_vehicle_count(self, traffic_manager):
        """Test getting current vehicle count."""
        mock_vehicle1 = MockTrafficVehicle(100.0, 100.0)
        mock_vehicle2 = MockTrafficVehicle(200.0, 200.0)

        traffic_manager.vehicles.append(mock_vehicle1)
        traffic_manager.vehicles.append(mock_vehicle2)

        assert traffic_manager.get_vehicle_count() == 2

    def test_set_target_vehicle_count(self, traffic_manager):
        """Test setting target vehicle count."""
        traffic_manager.set_target_vehicle_count(20)

        assert traffic_manager.target_vehicle_count == 20

    def test_set_target_vehicle_count_clamped_max(self, traffic_manager):
        """Test that target count is clamped to max."""
        traffic_manager.set_target_vehicle_count(50)  # Above max of 25

        assert traffic_manager.target_vehicle_count == 25

    def test_set_target_vehicle_count_clamped_min(self, traffic_manager):
        """Test that target count is clamped to min (0)."""
        traffic_manager.set_target_vehicle_count(-5)

        assert traffic_manager.target_vehicle_count == 0

    def test_clear_all_vehicles(self, traffic_manager):
        """Test clearing all vehicles."""
        mock_vehicle1 = MockTrafficVehicle(100.0, 100.0)
        mock_vehicle2 = MockTrafficVehicle(200.0, 200.0)
        traffic_manager.vehicles.extend([mock_vehicle1, mock_vehicle2])

        traffic_manager.clear_all_vehicles()

        assert len(traffic_manager.vehicles) == 0


class TestAssignRandomRoute:
    """Tests for route assignment."""

    def test_assign_random_route(self, traffic_manager, mock_road_network):
        """Test assigning a random route to a vehicle."""
        mock_road_network.add_road(10, 10, ['east'])
        mock_road_network.add_road(20, 20, ['west'])

        mock_vehicle = MockTrafficVehicle(320.0, 320.0)  # Grid position (10, 10)

        traffic_manager._assign_random_route(mock_vehicle)

        # Vehicle should have waypoints set
        assert mock_vehicle.waypoints is not None


class TestRepr:
    """Tests for string representation."""

    def test_repr(self, traffic_manager):
        """Test string representation."""
        mock_vehicle = MockTrafficVehicle(100.0, 100.0)
        traffic_manager.vehicles.append(mock_vehicle)

        repr_str = repr(traffic_manager)

        assert "TrafficManager" in repr_str
        assert "vehicles=" in repr_str
        assert "1/15" in repr_str  # 1 vehicle / 15 target
