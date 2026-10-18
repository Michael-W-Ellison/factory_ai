"""
Unit tests for FenceManager.

Tests fence spawning, management, and updates.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from enum import Enum

# Import the actual TileType so comparisons work
from src.world.tile import TileType


class MockTile:
    """Mock tile for testing."""
    def __init__(self, tile_type):
        self.tile_type = tile_type


class MockGrid:
    """Mock grid for testing."""
    def __init__(self, width_tiles=20, height_tiles=20, tile_size=32):
        self.width_tiles = width_tiles
        self.height_tiles = height_tiles
        self.tile_size = tile_size
        self._tiles = {}

    def get_tile(self, x, y):
        return self._tiles.get((x, y))

    def set_tile(self, x, y, tile):
        self._tiles[(x, y)] = tile


class MockFence:
    """Mock fence for testing."""
    def __init__(self, world_x, world_y, fence_type, orientation, length):
        self.world_x = world_x
        self.world_y = world_y
        self.fence_type = fence_type
        self.orientation = orientation
        self.width = length if orientation == 'horizontal' else 8
        self.height = 8 if orientation == 'horizontal' else length
        self.being_deconstructed = False
        self.deconstruction_progress = 0.0

    def update_deconstruction(self, dt):
        self.deconstruction_progress += dt
        return self.deconstruction_progress >= 1.0


@pytest.fixture
def mock_grid():
    """Create a mock grid."""
    return MockGrid()


@pytest.fixture
def fence_manager(mock_grid):
    """Create FenceManager instance with mock grid."""
    with patch('src.systems.fence_manager.Fence', MockFence):
        from src.systems.fence_manager import FenceManager
        return FenceManager(mock_grid)


class TestFenceManagerInit:
    """Tests for FenceManager initialization."""

    def test_init_with_grid(self, mock_grid):
        """Test initialization with grid."""
        with patch('src.systems.fence_manager.Fence', MockFence):
            from src.systems.fence_manager import FenceManager
            fm = FenceManager(mock_grid)

            assert fm.grid == mock_grid
            assert fm.fences == []

    def test_init_fence_types(self, fence_manager):
        """Test fence type configuration."""
        assert len(fence_manager.fence_types) == 3
        assert len(fence_manager.fence_type_weights) == 3
        assert sum(fence_manager.fence_type_weights) == pytest.approx(1.0)


class TestFindBuildings:
    """Tests for building detection."""

    def test_find_buildings_empty_grid(self, fence_manager):
        """Test finding buildings on empty grid."""
        buildings = fence_manager._find_buildings()
        assert buildings == []

    def test_find_buildings_with_buildings(self, fence_manager, mock_grid):
        """Test finding buildings when buildings exist."""
        mock_grid.set_tile(5, 5, MockTile(MockTileType.BUILDING))
        mock_grid.set_tile(10, 10, MockTile(MockTileType.BUILDING))

        buildings = fence_manager._find_buildings()

        assert len(buildings) == 2
        assert (5, 5) in buildings
        assert (10, 10) in buildings

    def test_find_buildings_ignores_other_tiles(self, fence_manager, mock_grid):
        """Test that only buildings are found."""
        mock_grid.set_tile(5, 5, MockTile(MockTileType.BUILDING))
        mock_grid.set_tile(6, 6, MockTile(MockTileType.GRASS))
        mock_grid.set_tile(7, 7, MockTile(MockTileType.ROAD_TAR))

        buildings = fence_manager._find_buildings()

        assert len(buildings) == 1
        assert (5, 5) in buildings


class TestFindEntranceSide:
    """Tests for entrance side detection."""

    def test_find_entrance_top_road(self, fence_manager, mock_grid):
        """Test entrance on top when road is above."""
        mock_grid.set_tile(5, 5, MockTile(MockTileType.BUILDING))
        mock_grid.set_tile(5, 4, MockTile(MockTileType.ROAD_TAR))

        side = fence_manager._find_entrance_side(5, 5)
        assert side == 'top'

    def test_find_entrance_bottom_road(self, fence_manager, mock_grid):
        """Test entrance on bottom when road is below."""
        mock_grid.set_tile(5, 5, MockTile(MockTileType.BUILDING))
        mock_grid.set_tile(5, 6, MockTile(MockTileType.ROAD_ASPHALT))

        side = fence_manager._find_entrance_side(5, 5)
        assert side == 'bottom'

    def test_find_entrance_left_road(self, fence_manager, mock_grid):
        """Test entrance on left when road is to the left."""
        mock_grid.set_tile(5, 5, MockTile(MockTileType.BUILDING))
        mock_grid.set_tile(4, 5, MockTile(MockTileType.ROAD_DIRT))

        side = fence_manager._find_entrance_side(5, 5)
        assert side == 'left'

    def test_find_entrance_right_road(self, fence_manager, mock_grid):
        """Test entrance on right when road is to the right."""
        mock_grid.set_tile(5, 5, MockTile(MockTileType.BUILDING))
        mock_grid.set_tile(6, 5, MockTile(MockTileType.ROAD_TAR))

        side = fence_manager._find_entrance_side(5, 5)
        assert side == 'right'

    def test_find_entrance_default_bottom(self, fence_manager, mock_grid):
        """Test default entrance is bottom when no road found."""
        mock_grid.set_tile(5, 5, MockTile(MockTileType.BUILDING))

        side = fence_manager._find_entrance_side(5, 5)
        assert side == 'bottom'


class TestFenceManagement:
    """Tests for fence add/remove operations."""

    def test_get_all_fences_empty(self, fence_manager):
        """Test getting all fences when none exist."""
        result = fence_manager.get_all_fences()
        assert result == []

    def test_get_all_fences_returns_copy(self, fence_manager):
        """Test that get_all_fences returns a copy."""
        fence = MockFence(100, 100, 'wooden', 'horizontal', 32)
        fence_manager.fences.append(fence)

        result = fence_manager.get_all_fences()

        assert result == [fence]
        assert result is not fence_manager.fences

    def test_remove_fence(self, fence_manager):
        """Test removing a fence."""
        fence = MockFence(100, 100, 'wooden', 'horizontal', 32)
        fence_manager.fences.append(fence)

        fence_manager.remove_fence(fence)

        assert fence not in fence_manager.fences

    def test_remove_nonexistent_fence(self, fence_manager):
        """Test removing a fence that doesn't exist."""
        fence = MockFence(100, 100, 'wooden', 'horizontal', 32)

        # Should not raise exception
        fence_manager.remove_fence(fence)

    def test_get_fence_at_position(self, fence_manager):
        """Test getting fence at specific position."""
        fence = MockFence(100, 100, 'wooden', 'horizontal', 32)
        fence_manager.fences.append(fence)

        result = fence_manager.get_fence_at(105, 105)
        assert result == fence

    def test_get_fence_at_position_not_found(self, fence_manager):
        """Test getting fence at position with no fence."""
        fence = MockFence(100, 100, 'wooden', 'horizontal', 32)
        fence_manager.fences.append(fence)

        result = fence_manager.get_fence_at(500, 500)
        assert result is None


class TestFenceUpdate:
    """Tests for fence update functionality."""

    def test_update_no_deconstruction(self, fence_manager):
        """Test update when no fences are being deconstructed."""
        fence = MockFence(100, 100, 'wooden', 'horizontal', 32)
        fence.being_deconstructed = False
        fence_manager.fences.append(fence)

        fence_manager.update(0.1)

        assert fence in fence_manager.fences

    def test_update_deconstruction_in_progress(self, fence_manager):
        """Test update during deconstruction."""
        fence = MockFence(100, 100, 'wooden', 'horizontal', 32)
        fence.being_deconstructed = True
        fence.deconstruction_progress = 0.0
        fence_manager.fences.append(fence)

        fence_manager.update(0.5)

        # Fence should still exist (not complete)
        assert fence in fence_manager.fences

    def test_update_deconstruction_complete(self, fence_manager):
        """Test update when deconstruction completes."""
        fence = MockFence(100, 100, 'wooden', 'horizontal', 32)
        fence.being_deconstructed = True
        fence.deconstruction_progress = 0.9
        fence_manager.fences.append(fence)

        fence_manager.update(0.5)  # This should complete deconstruction

        assert fence not in fence_manager.fences


class TestFenceStats:
    """Tests for fence statistics."""

    def test_get_stats_empty(self, fence_manager):
        """Test stats with no fences."""
        stats = fence_manager.get_stats()

        assert stats['total'] == 0
        assert stats['by_type'] == {}
        assert stats['being_deconstructed'] == 0

    def test_get_stats_with_fences(self, fence_manager):
        """Test stats with various fences."""
        fence1 = MockFence(100, 100, 'wooden', 'horizontal', 32)
        fence2 = MockFence(200, 200, 'wooden', 'vertical', 32)
        fence3 = MockFence(300, 300, 'chain_link', 'horizontal', 32)

        fence_manager.fences = [fence1, fence2, fence3]

        stats = fence_manager.get_stats()

        assert stats['total'] == 3
        assert stats['by_type']['wooden'] == 2
        assert stats['by_type']['chain_link'] == 1
        assert stats['being_deconstructed'] == 0

    def test_get_stats_with_deconstructing(self, fence_manager):
        """Test stats with fences being deconstructed."""
        fence1 = MockFence(100, 100, 'wooden', 'horizontal', 32)
        fence2 = MockFence(200, 200, 'wooden', 'vertical', 32)
        fence2.being_deconstructed = True

        fence_manager.fences = [fence1, fence2]

        stats = fence_manager.get_stats()

        assert stats['being_deconstructed'] == 1
