"""
Tests for ConstructionManager.

Tests construction workflows including:
- Queuing construction orders
- Location validation
- Starting and completing construction
- Canceling construction
- Robot assignment
- Statistics tracking
"""

import sys
from unittest.mock import MagicMock, patch
from typing import Dict, Optional

# Mock pygame before any imports that might need it
sys.modules['pygame'] = MagicMock()
sys.modules['pygame.font'] = MagicMock()
sys.modules['pygame.transform'] = MagicMock()
sys.modules['pygame.Surface'] = MagicMock()

import pytest

from src.systems.construction_manager import ConstructionManager, ConstructionOrder


class MockTile:
    """Mock tile for grid testing."""

    def __init__(self, occupied: bool = False):
        self.occupied = occupied


class MockGrid:
    """Mock grid for testing."""

    def __init__(self, width: int = 100, height: int = 100, tile_size: int = 32):
        self.width_tiles = width
        self.height_tiles = height
        self.tile_size = tile_size
        self._tiles: Dict[tuple, MockTile] = {}
        self._default_tile = MockTile(occupied=False)

    def get_tile(self, x: int, y: int) -> Optional[MockTile]:
        if 0 <= x < self.width_tiles and 0 <= y < self.height_tiles:
            if (x, y) not in self._tiles:
                self._tiles[(x, y)] = MockTile(occupied=False)
            return self._tiles[(x, y)]
        return None

    def set_tile_occupied(self, x: int, y: int, occupied: bool):
        if (x, y) not in self._tiles:
            self._tiles[(x, y)] = MockTile(occupied=occupied)
        else:
            self._tiles[(x, y)].occupied = occupied


class MockBuildingManager:
    """Mock building manager for testing."""

    def __init__(self):
        self.buildings = {}
        self.placed_buildings = []

    def get_building_at(self, x: int, y: int):
        return self.buildings.get((x, y), None)

    def place_building(self, building):
        self.placed_buildings.append(building)


class MockResourceManager:
    """Mock resource manager for testing."""

    def __init__(self, initial_money: float = 100000.0):
        self.money = initial_money
        self.materials = {}

    def add_material(self, material_type: str, quantity: float):
        if material_type not in self.materials:
            self.materials[material_type] = 0.0
        self.materials[material_type] += quantity


class MockConstructionSite:
    """Mock construction site for testing."""

    def __init__(self, grid_x: int, grid_y: int, width_tiles: int, height_tiles: int,
                 building_type: str, construction_time: float, required_materials: dict = None):
        self.id = id(self)
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.width_tiles = width_tiles
        self.height_tiles = height_tiles
        self.building_type = building_type
        self.construction_time = construction_time
        self.required_materials = required_materials or {}
        self.x = grid_x * 32
        self.y = grid_y * 32
        self.width = width_tiles * 32
        self.height = height_tiles * 32
        self.robots_working = []
        self.max_workers = 5
        self._complete = False
        self.materials_delivered = {}

    def add_robot(self, robot_id) -> bool:
        if robot_id not in self.robots_working and len(self.robots_working) < self.max_workers:
            self.robots_working.append(robot_id)
            return True
        return False

    def remove_robot(self, robot_id):
        if robot_id in self.robots_working:
            self.robots_working.remove(robot_id)

    def update(self, dt: float):
        pass

    def is_complete(self) -> bool:
        return self._complete

    def cancel(self) -> dict:
        return self.materials_delivered.copy()


@pytest.fixture
def mock_grid():
    """Provide a mock grid."""
    return MockGrid()


@pytest.fixture
def mock_building_manager():
    """Provide a mock building manager."""
    return MockBuildingManager()


@pytest.fixture
def mock_resource_manager():
    """Provide a mock resource manager."""
    return MockResourceManager()


@pytest.fixture
def construction_manager(mock_building_manager, mock_resource_manager, mock_grid):
    """Provide a construction manager with mocked dependencies."""
    return ConstructionManager(mock_building_manager, mock_resource_manager, mock_grid)


class TestConstructionOrder:
    """Tests for ConstructionOrder dataclass."""

    def test_construction_order_initialization(self):
        """Test that ConstructionOrder initializes with correct values."""
        order = ConstructionOrder(
            building_type="factory",
            grid_x=10,
            grid_y=20,
            width_tiles=3,
            height_tiles=3,
            construction_time=60.0,
            cost=5000.0,
            required_materials={"steel": 100.0, "concrete": 200.0}
        )

        assert order.building_type == "factory"
        assert order.grid_x == 10
        assert order.grid_y == 20
        assert order.width_tiles == 3
        assert order.height_tiles == 3
        assert order.construction_time == 60.0
        assert order.cost == 5000.0
        assert order.required_materials == {"steel": 100.0, "concrete": 200.0}
        assert order.started is False
        assert order.construction_site is None

    def test_construction_order_default_materials(self):
        """Test that ConstructionOrder defaults to empty materials dict."""
        order = ConstructionOrder(
            building_type="warehouse",
            grid_x=5,
            grid_y=5,
            width_tiles=2,
            height_tiles=2,
            construction_time=30.0,
            cost=2000.0
        )

        assert order.required_materials == {}

    def test_construction_order_has_unique_id(self):
        """Test that each ConstructionOrder has a unique ID."""
        order1 = ConstructionOrder("factory", 0, 0, 1, 1, 10.0, 100.0)
        order2 = ConstructionOrder("factory", 0, 0, 1, 1, 10.0, 100.0)

        assert order1.id != order2.id


class TestConstructionManagerInit:
    """Tests for ConstructionManager initialization."""

    def test_construction_manager_initialization(self, construction_manager):
        """Test that ConstructionManager initializes correctly."""
        assert construction_manager.queue == []
        assert construction_manager.active_sites == []
        assert construction_manager.max_concurrent == 3

    def test_construction_manager_has_dependencies(self, construction_manager, mock_building_manager,
                                                    mock_resource_manager, mock_grid):
        """Test that ConstructionManager stores its dependencies."""
        assert construction_manager.building_manager == mock_building_manager
        assert construction_manager.resource_manager == mock_resource_manager
        assert construction_manager.grid == mock_grid


class TestQueueConstruction:
    """Tests for queuing construction orders."""

    def test_queue_construction_success(self, construction_manager):
        """Test successfully queuing a construction order."""
        success, message = construction_manager.queue_construction(
            building_type="factory",
            grid_x=10,
            grid_y=10,
            width_tiles=3,
            height_tiles=3,
            construction_time=60.0,
            cost=5000.0
        )

        assert success is True
        assert "Queued" in message
        assert len(construction_manager.queue) == 1
        assert construction_manager.queue[0].building_type == "factory"

    def test_queue_construction_deducts_cost(self, construction_manager, mock_resource_manager):
        """Test that queuing construction deducts the cost."""
        initial_money = mock_resource_manager.money

        construction_manager.queue_construction(
            building_type="factory",
            grid_x=10,
            grid_y=10,
            width_tiles=3,
            height_tiles=3,
            construction_time=60.0,
            cost=5000.0
        )

        assert mock_resource_manager.money == initial_money - 5000.0

    def test_queue_construction_insufficient_funds(self, construction_manager, mock_resource_manager):
        """Test that queuing fails with insufficient funds."""
        mock_resource_manager.money = 1000.0

        success, message = construction_manager.queue_construction(
            building_type="factory",
            grid_x=10,
            grid_y=10,
            width_tiles=3,
            height_tiles=3,
            construction_time=60.0,
            cost=5000.0
        )

        assert success is False
        assert "Insufficient" in message
        assert len(construction_manager.queue) == 0

    def test_queue_construction_invalid_location_occupied(self, construction_manager, mock_grid):
        """Test that queuing fails on occupied tile."""
        mock_grid.set_tile_occupied(10, 10, True)

        success, message = construction_manager.queue_construction(
            building_type="factory",
            grid_x=10,
            grid_y=10,
            width_tiles=1,
            height_tiles=1,
            construction_time=60.0,
            cost=5000.0
        )

        assert success is False
        assert "Invalid location" in message

    def test_queue_construction_invalid_location_out_of_bounds(self, construction_manager):
        """Test that queuing fails for out of bounds location."""
        success, message = construction_manager.queue_construction(
            building_type="factory",
            grid_x=200,
            grid_y=200,
            width_tiles=1,
            height_tiles=1,
            construction_time=60.0,
            cost=5000.0
        )

        assert success is False
        assert "Invalid location" in message

    def test_queue_construction_overlapping_queued(self, construction_manager):
        """Test that queuing fails when overlapping existing queued construction."""
        # Queue first building
        construction_manager.queue_construction(
            building_type="factory",
            grid_x=10,
            grid_y=10,
            width_tiles=3,
            height_tiles=3,
            construction_time=60.0,
            cost=5000.0
        )

        # Try to queue overlapping building
        success, message = construction_manager.queue_construction(
            building_type="warehouse",
            grid_x=11,
            grid_y=11,
            width_tiles=2,
            height_tiles=2,
            construction_time=30.0,
            cost=2000.0
        )

        assert success is False
        assert "Invalid location" in message


class TestCancelConstruction:
    """Tests for canceling construction."""

    def test_cancel_queued_construction(self, construction_manager, mock_resource_manager):
        """Test canceling a queued construction refunds cost."""
        initial_money = mock_resource_manager.money

        construction_manager.queue_construction(
            building_type="factory",
            grid_x=10,
            grid_y=10,
            width_tiles=3,
            height_tiles=3,
            construction_time=60.0,
            cost=5000.0
        )

        order_id = construction_manager.queue[0].id

        success, message = construction_manager.cancel_construction(order_id)

        assert success is True
        assert "refunded" in message.lower()
        assert mock_resource_manager.money == initial_money
        assert len(construction_manager.queue) == 0

    def test_cancel_nonexistent_construction(self, construction_manager):
        """Test canceling a non-existent construction returns failure."""
        success, message = construction_manager.cancel_construction(99999)

        assert success is False
        assert "not found" in message.lower()


class TestLocationValidation:
    """Tests for location validation logic."""

    def test_rectangles_overlap_true(self, construction_manager):
        """Test rectangle overlap detection when overlapping."""
        result = construction_manager._rectangles_overlap(
            0, 0, 5, 5,   # First rectangle
            3, 3, 5, 5    # Second rectangle - overlaps
        )
        assert result is True

    def test_rectangles_overlap_false_separate(self, construction_manager):
        """Test rectangle overlap detection when separate."""
        result = construction_manager._rectangles_overlap(
            0, 0, 5, 5,    # First rectangle
            10, 10, 5, 5   # Second rectangle - no overlap
        )
        assert result is False

    def test_rectangles_overlap_false_adjacent(self, construction_manager):
        """Test rectangle overlap detection when adjacent (touching but not overlapping)."""
        result = construction_manager._rectangles_overlap(
            0, 0, 5, 5,   # First rectangle
            5, 0, 5, 5    # Second rectangle - adjacent, not overlapping
        )
        assert result is False

    def test_is_valid_location_existing_building(self, construction_manager, mock_building_manager):
        """Test that location with existing building is invalid."""
        mock_building_manager.buildings[(10, 10)] = MagicMock()

        result = construction_manager._is_valid_location(10, 10, 1, 1)

        assert result is False


class TestRobotAssignment:
    """Tests for robot assignment to construction sites."""

    def test_assign_robot_to_site(self, construction_manager):
        """Test assigning a robot to a construction site."""
        site = MockConstructionSite(10, 10, 2, 2, "factory", 60.0)

        result = construction_manager.assign_robot_to_site("robot_1", site)

        assert result is True
        assert "robot_1" in site.robots_working

    def test_unassign_robot_from_site(self, construction_manager):
        """Test removing a robot from a construction site."""
        site = MockConstructionSite(10, 10, 2, 2, "factory", 60.0)
        site.robots_working.append("robot_1")

        construction_manager.unassign_robot_from_site("robot_1", site)

        assert "robot_1" not in site.robots_working


class TestGetNearestConstructionSite:
    """Tests for finding nearest construction site."""

    def test_get_nearest_construction_site_returns_closest(self, construction_manager):
        """Test that get_nearest_construction_site returns the closest site."""
        site1 = MockConstructionSite(10, 10, 2, 2, "factory", 60.0)
        site2 = MockConstructionSite(50, 50, 2, 2, "warehouse", 30.0)

        construction_manager.active_sites = [site1, site2]

        # Position closer to site1
        nearest = construction_manager.get_nearest_construction_site(320, 320)  # World coords near grid 10,10

        assert nearest == site1

    def test_get_nearest_construction_site_no_sites(self, construction_manager):
        """Test that get_nearest_construction_site returns None when no sites."""
        result = construction_manager.get_nearest_construction_site(0, 0)

        assert result is None

    def test_get_nearest_construction_site_skips_full_sites(self, construction_manager):
        """Test that get_nearest_construction_site skips sites at max workers."""
        site1 = MockConstructionSite(10, 10, 2, 2, "factory", 60.0)
        site1.robots_working = ["r1", "r2", "r3", "r4", "r5"]  # Full

        site2 = MockConstructionSite(50, 50, 2, 2, "warehouse", 30.0)

        construction_manager.active_sites = [site1, site2]

        # Position closer to site1, but site1 is full
        nearest = construction_manager.get_nearest_construction_site(320, 320)

        assert nearest == site2


class TestStatistics:
    """Tests for construction statistics."""

    def test_get_statistics(self, construction_manager):
        """Test getting construction statistics."""
        # Queue some construction
        construction_manager.queue_construction(
            building_type="factory",
            grid_x=10,
            grid_y=10,
            width_tiles=2,
            height_tiles=2,
            construction_time=60.0,
            cost=5000.0
        )

        stats = construction_manager.get_statistics()

        assert stats['queued'] == 1
        assert stats['active'] == 0
        assert stats['max_concurrent'] == 3

    def test_repr(self, construction_manager):
        """Test string representation."""
        repr_str = repr(construction_manager)

        assert "ConstructionManager" in repr_str
        assert "queued=" in repr_str
        assert "active=" in repr_str
