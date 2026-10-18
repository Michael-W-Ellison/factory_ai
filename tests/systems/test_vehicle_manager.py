"""
Tests for VehicleManager - manages vehicle spawning and tracking.

Tests cover:
- Vehicle spawning in appropriate locations
- Vehicle tracking and removal
- Vehicle queries by position
- Deconstruction updates
- Statistics
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


# Patch pygame before importing modules that use it
with patch.dict('sys.modules', {'pygame': MagicMock()}):
    from src.systems.vehicle_manager import VehicleManager
    from src.world.tile import TileType


class MockVehicle:
    """Mock vehicle for testing without pygame dependencies."""
    _id_counter = 0

    def __init__(self, world_x, world_y, vehicle_type='car', is_scrap=False):
        MockVehicle._id_counter += 1
        self.id = MockVehicle._id_counter
        self.world_x = world_x
        self.world_y = world_y
        self.vehicle_type = vehicle_type
        self.is_scrap = is_scrap
        self.being_deconstructed = False
        self.deconstruction_progress = 0.0

        # Size based on type
        if vehicle_type == 'truck':
            self.width = 48
            self.height = 24
        elif vehicle_type == 'van':
            self.width = 40
            self.height = 22
        else:
            self.width = 32
            self.height = 20

    def update_deconstruction(self, dt):
        """Update deconstruction progress. Returns True when complete."""
        if self.being_deconstructed:
            self.deconstruction_progress += dt / 30.0  # 30 second deconstruction
            return self.deconstruction_progress >= 1.0
        return False

    def render(self, screen, camera):
        pass


class MockTile:
    """Mock tile for testing."""
    def __init__(self, tile_type=TileType.GRASS, occupied=False):
        self.tile_type = tile_type
        self.occupied = occupied


class MockGrid:
    """Mock grid for testing."""
    def __init__(self, width=20, height=20):
        self.width_tiles = width
        self.height_tiles = height
        self.tile_size = 32
        self._tiles = {}

        # Initialize all tiles as grass
        for y in range(height):
            for x in range(width):
                self._tiles[(x, y)] = MockTile(TileType.GRASS)

    def get_tile(self, x, y):
        if 0 <= x < self.width_tiles and 0 <= y < self.height_tiles:
            return self._tiles.get((x, y))
        return None

    def set_tile_type(self, x, y, tile_type):
        """Helper for tests to set tile types."""
        if (x, y) in self._tiles:
            self._tiles[(x, y)].tile_type = tile_type


@pytest.fixture
def mock_grid():
    """Provide a mock grid."""
    return MockGrid()


@pytest.fixture
def vehicle_manager(mock_grid):
    """Provide a VehicleManager instance with mocked grid."""
    return VehicleManager(mock_grid)


class TestVehicleManagerInitialization:
    """Tests for VehicleManager initialization."""

    def test_init_with_grid(self, mock_grid):
        """Test VehicleManager initializes with grid."""
        manager = VehicleManager(mock_grid)

        assert manager.grid is mock_grid
        assert manager.vehicles == []

    def test_init_default_parameters(self, vehicle_manager):
        """Test default spawn parameters."""
        assert vehicle_manager.scrap_ratio == 0.3
        assert vehicle_manager.vehicle_types == ['car', 'truck', 'van']
        assert len(vehicle_manager.vehicle_type_weights) == 3


def add_mock_vehicle(manager, world_x, world_y, vehicle_type='car', is_scrap=False):
    """Helper to add a mock vehicle to the manager."""
    vehicle = MockVehicle(world_x, world_y, vehicle_type, is_scrap)
    manager.vehicles.append(vehicle)
    return vehicle


class TestVehicleSpawning:
    """Tests for vehicle spawning behavior."""

    def test_spawn_locations_found_near_buildings(self, vehicle_manager, mock_grid):
        """Test that spawn locations are found near buildings."""
        # Setup: add some buildings and adjacent grass
        mock_grid.set_tile_type(5, 5, TileType.BUILDING)
        mock_grid.set_tile_type(6, 5, TileType.GRASS)  # Adjacent to building

        locations = vehicle_manager._find_spawn_locations()
        parking_locs = [(x, y) for x, y, t in locations if t == 'parking']

        assert len(parking_locs) > 0

    def test_spawn_locations_found_on_roads(self, mock_grid):
        """Test that spawn locations are found on roads."""
        mock_grid.set_tile_type(10, 10, TileType.ROAD_TAR)
        mock_grid.set_tile_type(11, 10, TileType.ROAD_ASPHALT)

        manager = VehicleManager(mock_grid)
        locations = manager._find_spawn_locations()
        road_locs = [(x, y) for x, y, t in locations if t == 'road']

        assert len(road_locs) >= 2

    def test_spawn_parameters_valid(self, vehicle_manager):
        """Test that default spawn parameters are valid."""
        assert 0.0 <= vehicle_manager.scrap_ratio <= 1.0
        assert len(vehicle_manager.vehicle_types) > 0
        assert sum(vehicle_manager.vehicle_type_weights) > 0


class TestFindSpawnLocations:
    """Tests for finding spawn locations."""

    def test_find_spawn_locations_near_buildings(self, vehicle_manager, mock_grid):
        """Test finding spawn locations near buildings."""
        mock_grid.set_tile_type(5, 5, TileType.BUILDING)
        mock_grid.set_tile_type(6, 5, TileType.GRASS)  # Adjacent

        locations = vehicle_manager._find_spawn_locations()

        parking_locations = [(x, y) for x, y, loc_type in locations if loc_type == 'parking']
        assert len(parking_locations) > 0

    def test_find_spawn_locations_on_roads(self, vehicle_manager, mock_grid):
        """Test finding spawn locations on roads."""
        mock_grid.set_tile_type(10, 10, TileType.ROAD_TAR)
        mock_grid.set_tile_type(11, 10, TileType.ROAD_ASPHALT)

        locations = vehicle_manager._find_spawn_locations()

        road_locations = [(x, y) for x, y, loc_type in locations if loc_type == 'road']
        assert len(road_locations) >= 2

    def test_spawn_locations_exclude_occupied_tiles(self, vehicle_manager, mock_grid):
        """Test that occupied tiles are excluded from spawn locations."""
        mock_grid.set_tile_type(10, 10, TileType.ROAD_TAR)
        mock_grid._tiles[(10, 10)].occupied = True

        locations = vehicle_manager._find_spawn_locations()

        road_locations = [(x, y) for x, y, loc_type in locations
                         if loc_type == 'road' and x == 10 and y == 10]
        assert len(road_locations) == 0


class TestVehicleQueries:
    """Tests for vehicle queries."""

    def test_get_vehicle_at_position(self, vehicle_manager):
        """Test getting vehicle at world position."""
        vehicle = MockVehicle(100.0, 100.0, 'car')
        vehicle_manager.vehicles.append(vehicle)

        result = vehicle_manager.get_vehicle_at(100.0, 100.0)

        assert result == vehicle

    def test_get_vehicle_at_position_with_tolerance(self, vehicle_manager):
        """Test getting vehicle within tolerance distance."""
        vehicle = MockVehicle(100.0, 100.0, 'car')
        vehicle_manager.vehicles.append(vehicle)

        # Within default tolerance of 20.0
        result = vehicle_manager.get_vehicle_at(115.0, 100.0)

        assert result == vehicle

    def test_get_vehicle_at_position_outside_tolerance(self, vehicle_manager):
        """Test getting vehicle outside tolerance returns None."""
        vehicle = MockVehicle(100.0, 100.0, 'car')
        vehicle_manager.vehicles.append(vehicle)

        # Outside default tolerance of 20.0
        result = vehicle_manager.get_vehicle_at(150.0, 100.0)

        assert result is None

    def test_get_vehicle_at_empty_world(self, vehicle_manager):
        """Test getting vehicle in empty world returns None."""
        result = vehicle_manager.get_vehicle_at(100.0, 100.0)

        assert result is None

    def test_get_all_vehicles(self, vehicle_manager):
        """Test getting all vehicles returns a copy."""
        vehicle1 = MockVehicle(100.0, 100.0, 'car')
        vehicle2 = MockVehicle(200.0, 200.0, 'truck')
        vehicle_manager.vehicles.extend([vehicle1, vehicle2])

        result = vehicle_manager.get_all_vehicles()

        assert len(result) == 2
        assert vehicle1 in result
        assert vehicle2 in result
        # Verify it's a copy
        result.append(MockVehicle(300, 300, 'van'))
        assert len(vehicle_manager.vehicles) == 2


class TestVehicleRemoval:
    """Tests for vehicle removal."""

    def test_remove_vehicle(self, vehicle_manager):
        """Test removing a vehicle."""
        vehicle = MockVehicle(100.0, 100.0, 'car')
        vehicle_manager.vehicles.append(vehicle)

        vehicle_manager.remove_vehicle(vehicle)

        assert vehicle not in vehicle_manager.vehicles

    def test_remove_nonexistent_vehicle(self, vehicle_manager):
        """Test removing nonexistent vehicle doesn't raise."""
        vehicle = MockVehicle(100.0, 100.0, 'car')

        # Should not raise
        vehicle_manager.remove_vehicle(vehicle)


class TestVehicleUpdate:
    """Tests for vehicle update functionality."""

    def test_update_deconstruction(self, vehicle_manager):
        """Test updating vehicle deconstruction progress."""
        vehicle = MockVehicle(100.0, 100.0, 'car')
        vehicle.being_deconstructed = True
        vehicle_manager.vehicles.append(vehicle)

        vehicle_manager.update(1.0)

        assert vehicle.deconstruction_progress > 0

    def test_update_removes_fully_deconstructed(self, vehicle_manager):
        """Test that fully deconstructed vehicles are removed."""
        vehicle = MockVehicle(100.0, 100.0, 'car')
        vehicle.being_deconstructed = True
        vehicle.deconstruction_progress = 0.95  # Almost done
        vehicle_manager.vehicles.append(vehicle)

        # Update with enough time to complete deconstruction
        vehicle_manager.update(5.0)  # 5 seconds should push it over

        assert vehicle not in vehicle_manager.vehicles

    def test_update_preserves_non_deconstructing(self, vehicle_manager):
        """Test that non-deconstructing vehicles are preserved."""
        vehicle = MockVehicle(100.0, 100.0, 'car')
        vehicle.being_deconstructed = False
        vehicle_manager.vehicles.append(vehicle)

        vehicle_manager.update(10.0)

        assert vehicle in vehicle_manager.vehicles


class TestVehicleStats:
    """Tests for vehicle statistics."""

    def test_get_stats_empty(self, vehicle_manager):
        """Test stats for empty vehicle manager."""
        stats = vehicle_manager.get_stats()

        assert stats['total'] == 0
        assert stats['scrap'] == 0
        assert stats['working'] == 0
        assert stats['being_deconstructed'] == 0

    def test_get_stats_with_vehicles(self, vehicle_manager):
        """Test stats with various vehicles."""
        vehicle1 = MockVehicle(100.0, 100.0, 'car', is_scrap=True)
        vehicle2 = MockVehicle(200.0, 200.0, 'truck', is_scrap=False)
        vehicle3 = MockVehicle(300.0, 300.0, 'van', is_scrap=True)
        vehicle3.being_deconstructed = True

        vehicle_manager.vehicles.extend([vehicle1, vehicle2, vehicle3])

        stats = vehicle_manager.get_stats()

        assert stats['total'] == 3
        assert stats['scrap'] == 2
        assert stats['working'] == 1
        assert stats['being_deconstructed'] == 1

    def test_get_stats_all_scrap(self, vehicle_manager):
        """Test stats when all vehicles are scrap."""
        for i in range(5):
            vehicle = MockVehicle(i * 50.0, i * 50.0, 'car', is_scrap=True)
            vehicle_manager.vehicles.append(vehicle)

        stats = vehicle_manager.get_stats()

        assert stats['total'] == 5
        assert stats['scrap'] == 5
        assert stats['working'] == 0

    def test_get_stats_all_working(self, vehicle_manager):
        """Test stats when all vehicles are working."""
        for i in range(3):
            vehicle = MockVehicle(i * 50.0, i * 50.0, 'truck', is_scrap=False)
            vehicle_manager.vehicles.append(vehicle)

        stats = vehicle_manager.get_stats()

        assert stats['total'] == 3
        assert stats['scrap'] == 0
        assert stats['working'] == 3


class TestVehicleTypes:
    """Tests for vehicle type distribution."""

    def test_vehicle_type_weights_sum(self, vehicle_manager):
        """Test that vehicle type weights are defined for each type."""
        assert len(vehicle_manager.vehicle_types) == len(vehicle_manager.vehicle_type_weights)

    def test_scrap_ratio_valid(self, vehicle_manager):
        """Test that scrap ratio is between 0 and 1."""
        assert 0.0 <= vehicle_manager.scrap_ratio <= 1.0
