"""
Tests for BuildingManager - manages all buildings in the factory.

Tests cover:
- Building placement and removal
- Grid occupancy tracking
- Building queries by position and type
- Power calculations
- Research effect application
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


# Patch pygame before importing modules that use it
with patch.dict('sys.modules', {'pygame': MagicMock()}):
    from src.systems.building_manager import BuildingManager


class MockBuilding:
    """Mock building for testing without pygame dependencies."""
    _id_counter = 0

    def __init__(self, grid_x, grid_y, width_tiles=2, height_tiles=2, building_type='factory'):
        MockBuilding._id_counter += 1
        self.id = f"building_{MockBuilding._id_counter}"
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.width_tiles = width_tiles
        self.height_tiles = height_tiles
        self.building_type = building_type
        self.name = building_type
        self.x = grid_x * 32
        self.y = grid_y * 32
        self.operational = True
        self.powered = True
        self.power_generation = 0.0
        self.power_consumption = 0.0
        self.active = True

    def can_operate(self):
        return self.operational and self.powered

    def update(self, dt):
        pass

    def render(self, screen, camera):
        pass


class MockTile:
    """Mock tile for testing."""
    def __init__(self, occupied=False, walkable=True):
        self.occupied = occupied
        self.walkable = walkable


class MockGrid:
    """Mock grid for testing."""
    def __init__(self, width=100, height=100):
        self.width_tiles = width
        self.height_tiles = height
        self.tile_size = 32
        self._tiles = {}

        # Initialize all tiles as unoccupied
        for y in range(height):
            for x in range(width):
                self._tiles[(x, y)] = MockTile()

    def get_tile(self, x, y):
        if 0 <= x < self.width_tiles and 0 <= y < self.height_tiles:
            return self._tiles.get((x, y), MockTile())
        return None


@pytest.fixture
def mock_grid():
    """Provide a mock grid."""
    return MockGrid()


@pytest.fixture
def building_manager(mock_grid):
    """Provide a BuildingManager instance with mocked grid."""
    return BuildingManager(mock_grid)


class TestBuildingManagerInitialization:
    """Tests for BuildingManager initialization."""

    def test_init_with_grid(self, mock_grid):
        """Test BuildingManager initializes with grid."""
        manager = BuildingManager(mock_grid)

        assert manager.grid is mock_grid
        assert manager.buildings == {}
        assert manager.buildings_by_type == {}
        assert manager.grid_occupancy == {}


class TestBuildingPlacement:
    """Tests for building placement."""

    def test_place_building_success(self, building_manager):
        """Test successfully placing a building."""
        building = MockBuilding(5, 5, 2, 2, 'solar_panel')

        result = building_manager.place_building(building)

        assert result is True
        assert building.id in building_manager.buildings
        assert building in building_manager.buildings_by_type.get('solar_panel', [])

    def test_place_building_marks_occupancy(self, building_manager):
        """Test that placing building marks grid tiles as occupied."""
        building = MockBuilding(5, 5, 2, 2, 'factory')

        building_manager.place_building(building)

        # All tiles under the building should be marked
        assert (5, 5) in building_manager.grid_occupancy
        assert (6, 5) in building_manager.grid_occupancy
        assert (5, 6) in building_manager.grid_occupancy
        assert (6, 6) in building_manager.grid_occupancy
        assert building_manager.grid_occupancy[(5, 5)] == building.id

    def test_place_building_on_occupied_tile_fails(self, building_manager):
        """Test that placing building on occupied tile fails."""
        building1 = MockBuilding(5, 5, 2, 2, 'factory')
        building2 = MockBuilding(6, 5, 2, 2, 'solar_panel')  # Overlaps with building1

        building_manager.place_building(building1)
        result = building_manager.place_building(building2)

        assert result is False
        assert building2.id not in building_manager.buildings

    def test_place_building_outside_grid_fails(self, building_manager):
        """Test that placing building outside grid boundaries fails."""
        building = MockBuilding(99, 99, 2, 2, 'factory')  # Extends beyond 100x100 grid

        result = building_manager.place_building(building)

        assert result is False

    def test_place_multiple_buildings_same_type(self, building_manager):
        """Test placing multiple buildings of the same type."""
        building1 = MockBuilding(5, 5, 1, 1, 'solar_panel')
        building2 = MockBuilding(10, 10, 1, 1, 'solar_panel')

        building_manager.place_building(building1)
        building_manager.place_building(building2)

        assert len(building_manager.buildings_by_type['solar_panel']) == 2


class TestBuildingRemoval:
    """Tests for building removal."""

    def test_remove_building_success(self, building_manager):
        """Test successfully removing a building."""
        building = MockBuilding(5, 5, 2, 2, 'factory')
        building_manager.place_building(building)

        result = building_manager.remove_building(building.id)

        assert result is True
        assert building.id not in building_manager.buildings

    def test_remove_building_frees_occupancy(self, building_manager):
        """Test that removing building frees grid tiles."""
        building = MockBuilding(5, 5, 2, 2, 'factory')
        building_manager.place_building(building)

        building_manager.remove_building(building.id)

        assert (5, 5) not in building_manager.grid_occupancy
        assert (6, 5) not in building_manager.grid_occupancy
        assert (5, 6) not in building_manager.grid_occupancy
        assert (6, 6) not in building_manager.grid_occupancy

    def test_remove_building_updates_type_list(self, building_manager):
        """Test that removing building updates type list."""
        building1 = MockBuilding(5, 5, 1, 1, 'solar_panel')
        building2 = MockBuilding(10, 10, 1, 1, 'solar_panel')
        building_manager.place_building(building1)
        building_manager.place_building(building2)

        building_manager.remove_building(building1.id)

        assert building1 not in building_manager.buildings_by_type['solar_panel']
        assert building2 in building_manager.buildings_by_type['solar_panel']

    def test_remove_nonexistent_building_fails(self, building_manager):
        """Test removing nonexistent building returns False."""
        result = building_manager.remove_building("nonexistent_id")

        assert result is False


class TestBuildingQueries:
    """Tests for building queries."""

    def test_get_building_at_position(self, building_manager):
        """Test getting building at grid position."""
        building = MockBuilding(5, 5, 2, 2, 'factory')
        building_manager.place_building(building)

        result = building_manager.get_building_at(5, 5)

        assert result == building

    def test_get_building_at_edge_of_building(self, building_manager):
        """Test getting building at edge tile of multi-tile building."""
        building = MockBuilding(5, 5, 2, 2, 'factory')
        building_manager.place_building(building)

        result = building_manager.get_building_at(6, 6)  # Bottom-right corner

        assert result == building

    def test_get_building_at_empty_position(self, building_manager):
        """Test getting building at empty position returns None."""
        result = building_manager.get_building_at(50, 50)

        assert result is None

    def test_get_buildings_by_type(self, building_manager):
        """Test getting buildings by type."""
        building1 = MockBuilding(5, 5, 1, 1, 'solar_panel')
        building2 = MockBuilding(10, 10, 1, 1, 'solar_panel')
        building3 = MockBuilding(15, 15, 1, 1, 'factory')

        building_manager.place_building(building1)
        building_manager.place_building(building2)
        building_manager.place_building(building3)

        solar_panels = building_manager.get_buildings_by_type('solar_panel')

        assert len(solar_panels) == 2
        assert building1 in solar_panels
        assert building2 in solar_panels

    def test_get_buildings_by_type_empty(self, building_manager):
        """Test getting buildings by type returns empty list when none exist."""
        result = building_manager.get_buildings_by_type('nonexistent_type')

        assert result == []


class TestPowerCalculations:
    """Tests for power generation and consumption calculations."""

    def test_calculate_total_power_generation(self, building_manager):
        """Test calculating total power generation."""
        building1 = MockBuilding(5, 5, 1, 1, 'solar_panel')
        building1.power_generation = 100.0
        building2 = MockBuilding(10, 10, 1, 1, 'solar_panel')
        building2.power_generation = 150.0

        building_manager.place_building(building1)
        building_manager.place_building(building2)

        total = building_manager.calculate_total_power_generation()

        assert total == 250.0

    def test_power_generation_excludes_non_operational(self, building_manager):
        """Test that non-operational buildings don't generate power."""
        building1 = MockBuilding(5, 5, 1, 1, 'solar_panel')
        building1.power_generation = 100.0
        building2 = MockBuilding(10, 10, 1, 1, 'solar_panel')
        building2.power_generation = 150.0
        building2.operational = False  # Not operational

        building_manager.place_building(building1)
        building_manager.place_building(building2)

        total = building_manager.calculate_total_power_generation()

        assert total == 100.0

    def test_calculate_total_power_consumption(self, building_manager):
        """Test calculating total power consumption."""
        building1 = MockBuilding(5, 5, 1, 1, 'assembler')
        building1.power_consumption = 50.0
        building2 = MockBuilding(10, 10, 1, 1, 'recycler')
        building2.power_consumption = 75.0

        building_manager.place_building(building1)
        building_manager.place_building(building2)

        total = building_manager.calculate_total_power_consumption()

        assert total == 125.0


class TestBuildingUpdate:
    """Tests for building update functionality."""

    def test_update_calls_building_update(self, building_manager):
        """Test that update calls each building's update method."""
        building = MockBuilding(5, 5, 1, 1, 'factory')
        building.update = Mock()
        building_manager.place_building(building)

        building_manager.update(0.016)

        building.update.assert_called_once_with(0.016)


class TestBuildingCounts:
    """Tests for building count statistics."""

    def test_get_building_counts(self, building_manager):
        """Test getting building counts by type."""
        building_manager.place_building(MockBuilding(5, 5, 1, 1, 'solar_panel'))
        building_manager.place_building(MockBuilding(10, 10, 1, 1, 'solar_panel'))
        building_manager.place_building(MockBuilding(15, 15, 1, 1, 'factory'))

        counts = building_manager.get_building_counts()

        assert counts['solar_panel'] == 2
        assert counts['factory'] == 1

    def test_get_stats(self, building_manager):
        """Test getting building statistics."""
        building1 = MockBuilding(5, 5, 1, 1, 'solar_panel')
        building1.power_generation = 100.0
        building2 = MockBuilding(10, 10, 1, 1, 'assembler')
        building2.power_consumption = 50.0

        building_manager.place_building(building1)
        building_manager.place_building(building2)

        stats = building_manager.get_stats()

        assert stats['total_buildings'] == 2
        assert 'by_type' in stats
        assert stats['total_power_generation'] == 100.0
        assert stats['total_power_consumption'] == 50.0


class TestResearchEffects:
    """Tests for research effect application."""

    def test_apply_research_effects_to_buildings(self, building_manager):
        """Test applying research effects to all buildings."""
        mock_research = Mock()

        building1 = MockBuilding(5, 5, 1, 1, 'factory')
        building1.apply_research_effects = Mock()
        building2 = MockBuilding(10, 10, 1, 1, 'assembler')
        building2.apply_research_effects = Mock()

        building_manager.place_building(building1)
        building_manager.place_building(building2)

        building_manager.apply_research_effects_to_buildings(mock_research)

        building1.apply_research_effects.assert_called_once_with(mock_research)
        building2.apply_research_effects.assert_called_once_with(mock_research)

    def test_apply_research_skips_buildings_without_method(self, building_manager):
        """Test that research application skips buildings without the method."""
        mock_research = Mock()

        building = MockBuilding(5, 5, 1, 1, 'simple')
        # Ensure building doesn't have apply_research_effects
        if hasattr(building, 'apply_research_effects'):
            delattr(building, 'apply_research_effects')

        building_manager.place_building(building)

        # Should not raise
        building_manager.apply_research_effects_to_buildings(mock_research)


class TestRepr:
    """Tests for string representation."""

    def test_repr(self, building_manager):
        """Test string representation."""
        building_manager.place_building(MockBuilding(5, 5, 1, 1, 'factory'))
        building_manager.place_building(MockBuilding(10, 10, 1, 1, 'solar_panel'))

        repr_str = repr(building_manager)

        assert 'BuildingManager' in repr_str
        assert 'buildings=2' in repr_str
