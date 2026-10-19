"""
Tests for terrain-aware city generation.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class MockTile:
    """Mock tile for testing."""
    def __init__(self, terrain_type=0):
        self.terrain_type = terrain_type  # 0=LAND, 1=WATER, 4=OCEAN
        self.tile_type = 2  # GRASS
        self.walkable = terrain_type == 0

    def set_type(self, tile_type):
        self.tile_type = tile_type


class MockGrid:
    """Mock grid for testing with configurable water areas."""
    def __init__(self, width=100, height=75, water_areas=None):
        self.width_tiles = width
        self.height_tiles = height
        self.world_width = width * 32
        self.world_height = height * 32
        self.tile_size = 32
        self.tiles = {}
        self.water_areas = water_areas or []

    def get_tile(self, x, y):
        if 0 <= x < self.width_tiles and 0 <= y < self.height_tiles:
            if (x, y) not in self.tiles:
                # Check if this tile is in a water area
                terrain_type = 0  # LAND
                for (wx, wy, ww, wh) in self.water_areas:
                    if wx <= x < wx + ww and wy <= y < wy + wh:
                        terrain_type = 1  # WATER
                        break
                self.tiles[(x, y)] = MockTile(terrain_type)
            return self.tiles[(x, y)]
        return None


@pytest.fixture(autouse=True)
def mock_pygame():
    """Mock pygame module."""
    with patch.dict('sys.modules', {'pygame': MagicMock()}):
        yield


class TestCityGeneratorInit:
    """Tests for CityGenerator initialization."""

    def test_init_with_grid(self):
        """Test initialization with grid reference."""
        from src.world.city_generator import CityGenerator
        grid = MockGrid(100, 75)
        cg = CityGenerator(3200, 2400, 32, grid=grid)

        assert cg.grid is grid
        assert cg.grid_width == 100
        assert cg.grid_height == 75

    def test_init_without_grid(self):
        """Test initialization without grid reference."""
        from src.world.city_generator import CityGenerator
        cg = CityGenerator(3200, 2400, 32, grid=None)

        assert cg.grid is None
        assert len(cg._water_tiles) == 0

    def test_init_caches_water_tiles(self):
        """Test that water tiles are cached on init."""
        from src.world.city_generator import CityGenerator

        # Create grid with water area
        grid = MockGrid(50, 40, water_areas=[(10, 10, 5, 5)])
        cg = CityGenerator(1600, 1280, 32, grid=grid)

        # Should have cached 25 water tiles (5x5)
        assert len(cg._water_tiles) == 25


class TestTerrainChecking:
    """Tests for terrain checking methods."""

    def test_is_water_true(self):
        """Test is_water returns True for water tiles."""
        from src.world.city_generator import CityGenerator
        grid = MockGrid(50, 40, water_areas=[(10, 10, 5, 5)])
        cg = CityGenerator(1600, 1280, 32, grid=grid)

        assert cg._is_water(12, 12) is True

    def test_is_water_false(self):
        """Test is_water returns False for land tiles."""
        from src.world.city_generator import CityGenerator
        grid = MockGrid(50, 40, water_areas=[(10, 10, 5, 5)])
        cg = CityGenerator(1600, 1280, 32, grid=grid)

        assert cg._is_water(0, 0) is False

    def test_is_area_clear_true(self):
        """Test is_area_clear returns True for clear areas."""
        from src.world.city_generator import CityGenerator
        grid = MockGrid(50, 40, water_areas=[(10, 10, 5, 5)])
        cg = CityGenerator(1600, 1280, 32, grid=grid)

        # Area away from water
        assert cg._is_area_clear(0, 0, 5, 5) is True

    def test_is_area_clear_false(self):
        """Test is_area_clear returns False when water present."""
        from src.world.city_generator import CityGenerator
        grid = MockGrid(50, 40, water_areas=[(10, 10, 5, 5)])
        cg = CityGenerator(1600, 1280, 32, grid=grid)

        # Area overlapping water
        assert cg._is_area_clear(8, 8, 5, 5) is False

    def test_is_block_flooded_true(self):
        """Test is_block_flooded returns True for flooded blocks."""
        from src.world.city_generator import CityGenerator

        # Create grid with entire block flooded
        grid = MockGrid(50, 40, water_areas=[(10, 10, 10, 10)])  # Full block
        cg = CityGenerator(1600, 1280, 32, grid=grid)

        # Block 1,1 (starts at tile 10,10) is fully flooded
        assert cg._is_block_flooded(1, 1, threshold=0.5) is True

    def test_is_block_flooded_false(self):
        """Test is_block_flooded returns False for dry blocks."""
        from src.world.city_generator import CityGenerator
        grid = MockGrid(50, 40, water_areas=[(20, 20, 5, 5)])
        cg = CityGenerator(1600, 1280, 32, grid=grid)

        # Block 0,0 has no water
        assert cg._is_block_flooded(0, 0, threshold=0.3) is False


class TestTerrainAwareRoads:
    """Tests for terrain-aware road placement."""

    def test_roads_avoid_water(self):
        """Test that roads are not placed on water tiles."""
        from src.world.city_generator import CityGenerator

        # Water covering part of where roads would go
        grid = MockGrid(50, 40, water_areas=[(0, 0, 10, 5)])
        cg = CityGenerator(1600, 1280, 32, grid=grid)

        cg._initialize_blocks()
        cg._place_roads()

        # Check that no road tiles are in water areas
        for (rx, ry) in cg.road_tiles:
            assert not cg._is_water(rx, ry), f"Road placed on water at ({rx}, {ry})"


class TestTerrainAwareZones:
    """Tests for terrain-aware zone assignment."""

    def test_flooded_blocks_marked_empty(self):
        """Test that flooded blocks are marked as EMPTY zone."""
        from src.world.city_generator import CityGenerator, ZoneType

        # Flood block 2,2 (tiles 20-29, 20-29)
        grid = MockGrid(50, 40, water_areas=[(20, 20, 10, 10)])
        cg = CityGenerator(1600, 1280, 32, grid=grid)

        cg._initialize_blocks()
        cg._place_roads()
        cg._assign_zones()

        # Block 2,2 should be EMPTY due to flooding
        block = cg.blocks[2][2]
        assert block.zone_type == ZoneType.EMPTY


class TestTerrainAwareBuildingPlacement:
    """Tests for terrain-aware building placement."""

    def test_buildings_not_placed_on_water(self):
        """Test that no buildings overlap with water."""
        from src.world.city_generator import CityGenerator

        # Create grid with scattered water
        grid = MockGrid(100, 75, water_areas=[
            (25, 25, 5, 5),
            (50, 30, 8, 8),
            (70, 50, 10, 10)
        ])
        cg = CityGenerator(3200, 2400, 32, grid=grid)

        # Generate city
        cg.generate(seed=42)

        # Check that no building overlaps water
        for building in cg.buildings:
            x, y = building['x'], building['y']
            w, h = building['width'], building['height']

            for dy in range(h):
                for dx in range(w):
                    assert not cg._is_water(x + dx, y + dy), \
                        f"Building {building['type']} at ({x},{y}) overlaps water at ({x+dx},{y+dy})"


class TestCityGeneration:
    """Tests for full city generation."""

    def test_generate_with_no_water(self):
        """Test city generation on fully dry map."""
        from src.world.city_generator import CityGenerator

        grid = MockGrid(100, 75)  # No water
        cg = CityGenerator(3200, 2400, 32, grid=grid)

        result = cg.generate(seed=42)

        assert 'buildings' in result
        assert 'road_tiles' in result
        assert len(cg.buildings) > 0
        assert len(cg.road_tiles) > 0

    def test_generate_with_water(self):
        """Test city generation on map with water."""
        from src.world.city_generator import CityGenerator

        # Water in southwest corner
        grid = MockGrid(100, 75, water_areas=[(0, 65, 30, 10)])
        cg = CityGenerator(3200, 2400, 32, grid=grid)

        result = cg.generate(seed=42)

        # Should still generate city
        assert len(cg.buildings) > 0

        # No buildings should be on water
        for building in cg.buildings:
            x, y = building['x'], building['y']
            w, h = building['width'], building['height']
            for dy in range(h):
                for dx in range(w):
                    assert not cg._is_water(x + dx, y + dy)

    def test_generate_with_river(self):
        """Test city generation with a river through the map."""
        from src.world.city_generator import CityGenerator

        # River running north-south
        grid = MockGrid(100, 75, water_areas=[(48, 0, 4, 75)])
        cg = CityGenerator(3200, 2400, 32, grid=grid)

        result = cg.generate(seed=42)

        # Should generate buildings on both sides
        west_buildings = [b for b in cg.buildings if b['x'] < 48]
        east_buildings = [b for b in cg.buildings if b['x'] >= 52]

        assert len(west_buildings) > 0
        assert len(east_buildings) > 0

        # No buildings in river
        river_buildings = [b for b in cg.buildings if 48 <= b['x'] < 52]
        for b in river_buildings:
            # Verify building doesn't actually overlap river
            for dy in range(b['height']):
                for dx in range(b['width']):
                    assert not cg._is_water(b['x'] + dx, b['y'] + dy)


class TestZoneTypes:
    """Tests for zone type enum."""

    def test_zone_types_exist(self):
        """Test that all zone types exist."""
        from src.world.city_generator import ZoneType

        assert hasattr(ZoneType, 'RESIDENTIAL')
        assert hasattr(ZoneType, 'COMMERCIAL')
        assert hasattr(ZoneType, 'INDUSTRIAL')
        assert hasattr(ZoneType, 'POLICE')
        assert hasattr(ZoneType, 'PARK')
        assert hasattr(ZoneType, 'ROAD')
        assert hasattr(ZoneType, 'EMPTY')


class TestCityBlock:
    """Tests for CityBlock class."""

    def test_block_initialization(self):
        """Test CityBlock initializes correctly."""
        from src.world.city_generator import CityBlock, ZoneType

        block = CityBlock(5, 10, ZoneType.RESIDENTIAL)

        assert block.x == 5
        assert block.y == 10
        assert block.zone_type == ZoneType.RESIDENTIAL
        assert block.density == 0.0
        assert len(block.buildings) == 0
