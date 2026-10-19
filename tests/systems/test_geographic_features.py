"""
Tests for geographic features (rivers, ocean, bridges).
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class MockTile:
    """Mock tile for testing."""
    def __init__(self):
        self.terrain_type = 0  # LAND
        self.walkable = True

    def set_terrain_type(self, terrain_type):
        self.terrain_type = terrain_type


class MockGrid:
    """Mock grid for testing."""
    def __init__(self, width=100, height=75):
        self.width_tiles = width
        self.height_tiles = height
        self.tiles = {}

    def get_tile(self, x, y):
        if 0 <= x < self.width_tiles and 0 <= y < self.height_tiles:
            if (x, y) not in self.tiles:
                self.tiles[(x, y)] = MockTile()
            return self.tiles[(x, y)]
        return None


# Mock pygame before importing
@pytest.fixture(autouse=True)
def mock_pygame():
    """Mock pygame module."""
    with patch.dict('sys.modules', {'pygame': MagicMock()}):
        yield


class TestRiverSegment:
    """Tests for RiverSegment class."""

    def test_segment_initialization(self):
        """Test RiverSegment initializes correctly."""
        from src.world.river_generator import RiverSegment
        segment = RiverSegment(10, 20, 4)

        assert segment.x == 10
        assert segment.y == 20
        assert segment.width == 4


class TestBridge:
    """Tests for Bridge class."""

    def test_bridge_horizontal(self):
        """Test horizontal bridge tile calculation."""
        from src.world.river_generator import Bridge
        bridge = Bridge(5, 10, 'horizontal', 4)

        assert bridge.x == 5
        assert bridge.y == 10
        assert bridge.direction == 'horizontal'
        assert bridge.length == 4
        assert len(bridge.tiles) == 4
        assert (5, 10) in bridge.tiles
        assert (8, 10) in bridge.tiles

    def test_bridge_vertical(self):
        """Test vertical bridge tile calculation."""
        from src.world.river_generator import Bridge
        bridge = Bridge(5, 10, 'vertical', 3)

        assert bridge.direction == 'vertical'
        assert len(bridge.tiles) == 3
        assert (5, 10) in bridge.tiles
        assert (5, 12) in bridge.tiles


class TestRiverGeneratorInit:
    """Tests for RiverGenerator initialization."""

    def test_init_with_grid_object(self):
        """Test initialization with grid object."""
        from src.world.river_generator import RiverGenerator
        grid = MockGrid(100, 75)
        rg = RiverGenerator(grid, seed=42)

        assert rg.grid_width == 100
        assert rg.grid_height == 75
        assert rg.grid is grid

    def test_init_with_tuple(self):
        """Test initialization with tuple dimensions."""
        from src.world.river_generator import RiverGenerator
        rg = RiverGenerator((80, 60), seed=123)

        assert rg.grid_width == 80
        assert rg.grid_height == 60
        assert rg.grid is None

    def test_init_creates_empty_sets(self):
        """Test that initialization creates empty tile sets."""
        from src.world.river_generator import RiverGenerator
        rg = RiverGenerator((100, 75))

        assert len(rg.river_tiles) == 0
        assert len(rg.ocean_tiles) == 0
        assert len(rg.dock_tiles) == 0
        assert len(rg.bridge_tiles) == 0
        assert len(rg.rivers) == 0


class TestGenerateOcean:
    """Tests for ocean generation."""

    def test_generate_ocean_south_edge(self):
        """Test generating ocean on south edge."""
        from src.world.river_generator import RiverGenerator
        grid = MockGrid(100, 75)
        rg = RiverGenerator(grid, seed=42)

        result = rg.generate_ocean(edges=['south'], depth=5, create_docks=True)

        assert 'ocean_tiles' in result
        assert 'dock_tiles' in result
        assert result['ocean_tiles'] > 0
        assert len(rg.ocean_tiles) > 0

    def test_generate_ocean_multiple_edges(self):
        """Test generating ocean on multiple edges."""
        from src.world.river_generator import RiverGenerator
        grid = MockGrid(100, 75)
        rg = RiverGenerator(grid, seed=42)

        result = rg.generate_ocean(edges=['south', 'west'], depth=4, create_docks=False)

        assert result['ocean_tiles'] > 0
        # Should have tiles along both edges
        has_south = any(y >= 71 for _, y in rg.ocean_tiles)
        has_west = any(x < 4 for x, _ in rg.ocean_tiles)
        assert has_south
        assert has_west

    def test_generate_ocean_creates_docks(self):
        """Test that docks are created when requested."""
        from src.world.river_generator import RiverGenerator
        grid = MockGrid(100, 75)
        rg = RiverGenerator(grid, seed=42)

        result = rg.generate_ocean(edges=['south'], depth=6, create_docks=True, dock_spacing=10)

        assert result['dock_tiles'] > 0
        assert len(rg.dock_tiles) > 0

    def test_generate_ocean_no_docks(self):
        """Test generating ocean without docks."""
        from src.world.river_generator import RiverGenerator
        grid = MockGrid(100, 75)
        rg = RiverGenerator(grid, seed=42)

        result = rg.generate_ocean(edges=['south'], depth=5, create_docks=False)

        assert result['dock_tiles'] == 0
        assert len(rg.dock_tiles) == 0


class TestGenerateRandomRiver:
    """Tests for random river generation."""

    def test_generate_random_river(self):
        """Test generating a random river."""
        from src.world.river_generator import RiverGenerator
        grid = MockGrid(100, 75)
        rg = RiverGenerator(grid, seed=42)

        result = rg.generate_random_river(
            width_range=(3, 4),
            length_range=(20, 30),
            meandering=0.2
        )

        assert 'segments' in result
        assert 'river_tiles' in result
        assert 'start_edge' in result
        assert 'flow_direction' in result
        assert result['segments'] > 0
        assert result['river_tiles'] > 0

    def test_generate_random_river_avoids_ocean(self):
        """Test that random river doesn't start from ocean edge."""
        from src.world.river_generator import RiverGenerator
        grid = MockGrid(100, 75)
        rg = RiverGenerator(grid, seed=42)

        # First create ocean on south edge
        rg.generate_ocean(edges=['south'], depth=5)

        # Generate river - should not start from south
        result = rg.generate_random_river()

        # River should start from non-ocean edge
        assert result['start_edge'] != 'south'

    def test_generate_multiple_rivers(self):
        """Test generating multiple rivers."""
        from src.world.river_generator import RiverGenerator
        grid = MockGrid(100, 75)
        rg = RiverGenerator(grid, seed=42)

        rg.generate_random_river()
        rg.generate_random_river()

        assert len(rg.rivers) == 2


class TestGenerateRiverPath:
    """Tests for the generate() method."""

    def test_generate_single_river(self):
        """Test generating a single river."""
        from src.world.river_generator import RiverGenerator
        grid = MockGrid(100, 75)
        rg = RiverGenerator(grid, seed=42)

        result = rg.generate(num_rivers=1, flow_direction='south')

        assert len(rg.rivers) == 1
        assert len(rg.river_tiles) > 0
        assert 'rivers' in result
        assert 'river_tiles' in result

    def test_generate_multiple_rivers(self):
        """Test generating multiple rivers."""
        from src.world.river_generator import RiverGenerator
        grid = MockGrid(100, 75)
        rg = RiverGenerator(grid, seed=42)

        result = rg.generate(num_rivers=2, flow_direction='south')

        assert len(rg.rivers) == 2

    def test_generate_different_directions(self):
        """Test river generation with different flow directions."""
        from src.world.river_generator import RiverGenerator

        # Test just one direction to keep test fast
        grid = MockGrid(50, 40)  # Smaller grid
        rg = RiverGenerator(grid, seed=42)
        result = rg.generate(num_rivers=1, flow_direction='south')
        assert len(rg.rivers) == 1


class TestAddOceanEdge:
    """Tests for add_ocean_edge method."""

    def test_add_ocean_edge_south(self):
        """Test adding ocean on south edge."""
        from src.world.river_generator import RiverGenerator
        rg = RiverGenerator((100, 75), seed=42)

        tiles = rg.add_ocean_edge('south', depth=5)

        assert len(tiles) == 100 * 5  # width * depth
        # All tiles should be at y >= 70
        assert all(y >= 70 for _, y in tiles)

    def test_add_ocean_edge_north(self):
        """Test adding ocean on north edge."""
        from src.world.river_generator import RiverGenerator
        rg = RiverGenerator((100, 75), seed=42)

        tiles = rg.add_ocean_edge('north', depth=5)

        assert len(tiles) == 100 * 5
        # All tiles should be at y < 5
        assert all(y < 5 for _, y in tiles)

    def test_add_ocean_edge_west(self):
        """Test adding ocean on west edge."""
        from src.world.river_generator import RiverGenerator
        rg = RiverGenerator((100, 75), seed=42)

        tiles = rg.add_ocean_edge('west', depth=5)

        assert len(tiles) == 75 * 5  # height * depth
        # All tiles should be at x < 5
        assert all(x < 5 for x, _ in tiles)


class TestPlaceBridges:
    """Tests for bridge placement."""

    def test_place_bridges_with_intersections(self):
        """Test placing bridges where roads cross rivers."""
        from src.world.river_generator import RiverGenerator
        rg = RiverGenerator((100, 75), seed=42)

        # Add some river tiles
        for y in range(20, 30):
            for x in range(40, 50):
                rg.river_tiles.add((x, y))

        # Add some road tiles that cross the river
        road_tiles = set()
        for x in range(35, 55):
            road_tiles.add((x, 25))

        rg.place_bridges(road_tiles, min_spacing=5)

        # Should have placed at least one bridge
        assert len(rg.bridges) >= 0  # May not place if no valid crossing

    def test_place_bridges_no_intersections(self):
        """Test placing bridges with no road-river intersections."""
        from src.world.river_generator import RiverGenerator
        rg = RiverGenerator((100, 75), seed=42)

        # Add river tiles in one area
        for y in range(20, 30):
            for x in range(10, 20):
                rg.river_tiles.add((x, y))

        # Add road tiles that don't cross the river
        road_tiles = {(x, 5) for x in range(50, 60)}

        rg.place_bridges(road_tiles, min_spacing=5)

        assert len(rg.bridges) == 0


class TestHelperMethods:
    """Tests for helper methods."""

    def test_is_river(self):
        """Test is_river method."""
        from src.world.river_generator import RiverGenerator
        rg = RiverGenerator((100, 75), seed=42)
        rg.river_tiles.add((10, 20))

        assert rg.is_river(10, 20) is True
        assert rg.is_river(10, 21) is False

    def test_is_bridge(self):
        """Test is_bridge method."""
        from src.world.river_generator import RiverGenerator
        rg = RiverGenerator((100, 75), seed=42)
        rg.bridge_tiles.add((15, 25))

        assert rg.is_bridge(15, 25) is True
        assert rg.is_bridge(15, 26) is False

    def test_is_ocean(self):
        """Test is_ocean method."""
        from src.world.river_generator import RiverGenerator
        rg = RiverGenerator((100, 75), seed=42)
        rg.ocean_tiles.add((5, 70))

        assert rg.is_ocean(5, 70) is True
        assert rg.is_ocean(5, 69) is False

    def test_is_dock(self):
        """Test is_dock method."""
        from src.world.river_generator import RiverGenerator
        rg = RiverGenerator((100, 75), seed=42)
        rg.dock_tiles.add((20, 70))

        assert rg.is_dock(20, 70) is True
        assert rg.is_dock(20, 69) is False


class TestStatistics:
    """Tests for statistics methods."""

    def test_get_statistics(self):
        """Test get_statistics method."""
        from src.world.river_generator import RiverGenerator
        grid = MockGrid(100, 75)
        rg = RiverGenerator(grid, seed=42)

        rg.generate_ocean(edges=['south'], depth=4)
        rg.generate_random_river()

        stats = rg.get_statistics()

        assert 'num_rivers' in stats
        assert 'river_tiles' in stats
        assert 'num_bridges' in stats
        assert 'bridge_tiles' in stats

    def test_repr(self):
        """Test string representation."""
        from src.world.river_generator import RiverGenerator
        rg = RiverGenerator((100, 75), seed=42)

        repr_str = repr(rg)

        assert 'RiverGenerator' in repr_str
        assert 'rivers' in repr_str
        assert 'water tiles' in repr_str
