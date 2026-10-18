"""
Unit tests for PropManager.

Tests prop spawning, lifecycle, rendering, and management.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class MockTile:
    """Mock tile for testing."""
    def __init__(self, tile_type):
        self.tile_type = tile_type


class MockGrid:
    """Mock grid for testing."""
    def __init__(self, width_tiles=10, height_tiles=10, tile_size=32):
        self.width_tiles = width_tiles
        self.height_tiles = height_tiles
        self.tile_size = tile_size
        self._tiles = {}

    def get_tile(self, x, y):
        return self._tiles.get((x, y))

    def set_tile(self, x, y, tile):
        self._tiles[(x, y)] = tile


class MockRoadNetwork:
    """Mock road network for testing."""
    def __init__(self):
        self.road_tiles = set()
        self._intersections = set()

    def add_road(self, x, y, is_intersection=False):
        self.road_tiles.add((x, y))
        if is_intersection:
            self._intersections.add((x, y))

    def is_intersection(self, x, y):
        return (x, y) in self._intersections

    def _get_road_neighbors(self, x, y):
        neighbors = []
        if (x, y - 1) in self.road_tiles:
            neighbors.append('north')
        if (x, y + 1) in self.road_tiles:
            neighbors.append('south')
        if (x - 1, y) in self.road_tiles:
            neighbors.append('west')
        if (x + 1, y) in self.road_tiles:
            neighbors.append('east')
        return neighbors


@pytest.fixture
def mock_grid():
    """Create a mock grid."""
    return MockGrid()


@pytest.fixture
def mock_road_network():
    """Create a mock road network."""
    return MockRoadNetwork()


@pytest.fixture
def prop_manager(mock_grid, mock_road_network):
    """Create PropManager instance with mocks."""
    with patch.dict('sys.modules', {'pygame': MagicMock()}):
        from src.systems.prop_manager import PropManager
        return PropManager(mock_grid, mock_road_network)


class TestPropManagerInit:
    """Tests for PropManager initialization."""

    def test_init_with_grid_only(self, mock_grid):
        """Test initialization with just grid."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.prop_manager import PropManager
            pm = PropManager(mock_grid)

            assert pm.grid == mock_grid
            assert pm.road_network is None
            assert pm.props == []

    def test_init_with_road_network(self, mock_grid, mock_road_network):
        """Test initialization with grid and road network."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.prop_manager import PropManager
            pm = PropManager(mock_grid, mock_road_network)

            assert pm.grid == mock_grid
            assert pm.road_network == mock_road_network

    def test_init_default_config(self, prop_manager):
        """Test default configuration values."""
        assert prop_manager.target_prop_count == 80
        assert prop_manager.light_pole_spacing == 8
        assert prop_manager.bench_density == 0.3
        assert prop_manager.trash_can_density == 0.2
        assert prop_manager.bicycle_density == 0.15


class TestPropManagerCounting:
    """Tests for prop counting and management."""

    def test_get_prop_count_empty(self, prop_manager):
        """Test prop count when no props exist."""
        assert prop_manager.get_prop_count() == 0

    def test_add_prop(self, prop_manager):
        """Test adding a prop manually."""
        mock_prop = Mock()
        mock_prop.world_x = 100
        mock_prop.world_y = 100
        mock_prop.prop_type = 1

        prop_manager.add_prop(mock_prop)

        assert prop_manager.get_prop_count() == 1
        assert mock_prop in prop_manager.props

    def test_remove_prop(self, prop_manager):
        """Test removing a prop."""
        mock_prop = Mock()
        mock_prop.world_x = 100
        mock_prop.world_y = 100

        prop_manager.add_prop(mock_prop)
        assert prop_manager.get_prop_count() == 1

        prop_manager.remove_prop(mock_prop)
        assert prop_manager.get_prop_count() == 0

    def test_remove_nonexistent_prop(self, prop_manager):
        """Test removing a prop that doesn't exist does nothing."""
        mock_prop = Mock()
        prop_manager.remove_prop(mock_prop)
        assert prop_manager.get_prop_count() == 0

    def test_clear_all_props(self, prop_manager):
        """Test clearing all props."""
        for i in range(5):
            mock_prop = Mock()
            mock_prop.world_x = i * 50
            mock_prop.world_y = i * 50
            prop_manager.add_prop(mock_prop)

        assert prop_manager.get_prop_count() == 5

        prop_manager.clear_all_props()
        assert prop_manager.get_prop_count() == 0


class TestPropManagerPositionCheck:
    """Tests for position checking functionality."""

    def test_is_position_clear_empty(self, prop_manager):
        """Test position is clear when no props exist."""
        assert prop_manager._is_position_clear(100, 100) is True

    def test_is_position_clear_with_nearby_prop(self, prop_manager):
        """Test position is not clear when prop is nearby."""
        mock_prop = Mock()
        mock_prop.world_x = 100
        mock_prop.world_y = 100

        prop_manager.add_prop(mock_prop)

        # Position very close should not be clear
        assert prop_manager._is_position_clear(105, 100, min_distance=10) is False

    def test_is_position_clear_with_distant_prop(self, prop_manager):
        """Test position is clear when prop is far away."""
        mock_prop = Mock()
        mock_prop.world_x = 100
        mock_prop.world_y = 100

        prop_manager.add_prop(mock_prop)

        # Position far away should be clear
        assert prop_manager._is_position_clear(200, 200, min_distance=10) is True


class TestPropManagerUpdate:
    """Tests for prop update functionality."""

    def test_update_light_poles_night(self, prop_manager):
        """Test light poles turn on at night."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.entities.prop import PropType

            mock_light_pole = Mock()
            mock_light_pole.prop_type = PropType.LIGHT_POLE
            mock_light_pole.is_on = False

            prop_manager.add_prop(mock_light_pole)
            prop_manager.update(0.1, is_night=True)

            assert mock_light_pole.is_on is True

    def test_update_light_poles_day(self, prop_manager):
        """Test light poles turn off during day."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.entities.prop import PropType

            mock_light_pole = Mock()
            mock_light_pole.prop_type = PropType.LIGHT_POLE
            mock_light_pole.is_on = True

            prop_manager.add_prop(mock_light_pole)
            prop_manager.update(0.1, is_night=False)

            assert mock_light_pole.is_on is False

    def test_update_tree_seasons(self, prop_manager):
        """Test trees update with season changes."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.entities.prop import PropType

            mock_tree = Mock()
            mock_tree.prop_type = PropType.TREE
            mock_tree.season = 'summer'

            prop_manager.add_prop(mock_tree)
            prop_manager.update(0.1, is_night=False, season='autumn')

            assert mock_tree.season == 'autumn'


class TestPropManagerRepr:
    """Tests for string representation."""

    def test_repr_empty(self, prop_manager):
        """Test repr with no props."""
        result = repr(prop_manager)
        assert 'PropManager' in result
        assert 'props=0' in result

    def test_repr_with_props(self, prop_manager):
        """Test repr with props."""
        for i in range(5):
            mock_prop = Mock()
            mock_prop.world_x = i * 50
            mock_prop.world_y = i * 50
            prop_manager.add_prop(mock_prop)

        result = repr(prop_manager)
        assert 'props=5' in result
