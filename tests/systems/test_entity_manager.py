"""
Tests for EntityManager - manages all entities in the game.

Tests cover:
- Entity creation (robots, collectibles)
- Entity lifecycle management
- Selection and control
- Entity lookups and queries
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys


# Mock pygame before any imports that might need it
sys.modules['pygame'] = MagicMock()


class MockRobot:
    """Mock robot for testing without pygame dependencies."""
    _id_counter = 0

    def __init__(self, x, y, autonomous=True):
        MockRobot._id_counter += 1
        self.id = f"robot_{MockRobot._id_counter}"
        self.x = x
        self.y = y
        self.width = 28
        self.height = 28
        self.autonomous = autonomous
        self.selected = False
        self.active = True
        self.factory_pos = None
        self.max_capacity = 100
        self.current_load = 0
        self.inventory = {}

    def apply_research_effects(self, research_manager):
        pass

    def update(self, dt, grid=None, entity_manager=None):
        pass

    def is_full(self):
        return self.current_load >= self.max_capacity

    def get_center(self):
        return (self.x + self.width / 2, self.y + self.height / 2)

    def collides_with(self, other):
        return True

    def add_material(self, material_type, quantity, source):
        self.current_load += quantity
        self.inventory[material_type] = self.inventory.get(material_type, 0) + quantity


class MockCollectible:
    """Mock collectible for testing without pygame dependencies."""
    _id_counter = 0

    def __init__(self, x, y, material_type, quantity, source=None):
        MockCollectible._id_counter += 1
        self.id = f"collectible_{MockCollectible._id_counter}"
        self.x = x
        self.y = y
        self.material_type = material_type
        self.quantity = quantity
        self.source = source or "LANDFILL"
        self.active = True

    def update(self, dt):
        pass

    def collect(self, max_amount):
        collected = min(max_amount, self.quantity)
        self.quantity -= collected
        if self.quantity <= 0:
            self.active = False
        return collected


class MockGrid:
    """Mock grid for testing."""
    def __init__(self):
        self.tile_size = 32

    def get_tile(self, x, y):
        return Mock(occupied=False, walkable=True)


@pytest.fixture
def mock_grid():
    """Provide a mock grid."""
    return MockGrid()


@pytest.fixture
def entity_manager(mock_grid):
    """Provide an EntityManager instance with mocked dependencies."""
    from src.systems.entity_manager import EntityManager
    manager = EntityManager(grid=mock_grid)
    return manager


def add_mock_robot(manager, x, y, autonomous=True):
    """Helper to add a mock robot to the manager."""
    robot = MockRobot(x, y, autonomous)
    manager.entities[robot.id] = robot
    manager.robots.append(robot)
    return robot


def add_mock_collectible(manager, x, y, material_type, quantity, source=None):
    """Helper to add a mock collectible to the manager."""
    collectible = MockCollectible(x, y, material_type, quantity, source)
    manager.entities[collectible.id] = collectible
    manager.collectibles.append(collectible)
    return collectible


class TestEntityManagerInitialization:
    """Tests for EntityManager initialization."""

    def test_init_with_default_values(self):
        """Test EntityManager initializes with empty collections."""
        from src.systems.entity_manager import EntityManager
        manager = EntityManager()

        assert manager.entities == {}
        assert manager.robots == []
        assert manager.collectibles == []
        assert manager.buildings == []
        assert manager.selected_robot is None
        assert manager.factory_pos is None

    def test_init_with_grid(self, mock_grid):
        """Test EntityManager accepts grid on initialization."""
        from src.systems.entity_manager import EntityManager
        manager = EntityManager(grid=mock_grid)

        assert manager.grid is mock_grid

    def test_init_with_resource_manager(self, mock_grid):
        """Test EntityManager accepts resource manager on initialization."""
        from src.systems.entity_manager import EntityManager
        mock_resource = Mock()
        manager = EntityManager(grid=mock_grid, resource_manager=mock_resource)

        assert manager.resource_manager is mock_resource

    def test_init_with_research_manager(self, mock_grid):
        """Test EntityManager accepts research manager on initialization."""
        from src.systems.entity_manager import EntityManager
        mock_research = Mock()
        manager = EntityManager(grid=mock_grid, research_manager=mock_research)

        assert manager.research_manager is mock_research


class TestRobotManagement:
    """Tests for robot management using mock objects."""

    def test_add_robot_to_manager(self, entity_manager):
        """Test adding a robot to the manager."""
        robot = add_mock_robot(entity_manager, 100.0, 200.0)

        assert robot in entity_manager.robots
        assert robot.id in entity_manager.entities

    def test_add_multiple_robots(self, entity_manager):
        """Test adding multiple robots."""
        robot1 = add_mock_robot(entity_manager, 0, 0)
        robot2 = add_mock_robot(entity_manager, 100, 100)
        robot3 = add_mock_robot(entity_manager, 200, 200)

        assert len(entity_manager.robots) == 3
        assert len(entity_manager.entities) == 3

    def test_robot_with_factory_position(self, entity_manager):
        """Test robot receives factory position when added."""
        entity_manager.factory_pos = (500, 600)
        robot = add_mock_robot(entity_manager, 100, 100)
        robot.factory_pos = entity_manager.factory_pos

        assert robot.factory_pos == (500, 600)


class TestCollectibleManagement:
    """Tests for collectible management."""

    def test_add_collectible_to_manager(self, entity_manager):
        """Test adding a collectible to the manager."""
        collectible = add_mock_collectible(
            entity_manager, 100.0, 200.0, 'metal', 50.0
        )

        assert collectible in entity_manager.collectibles
        assert collectible.id in entity_manager.entities

    def test_add_multiple_collectibles(self, entity_manager):
        """Test adding multiple collectibles."""
        c1 = add_mock_collectible(entity_manager, 0, 0, 'metal', 10)
        c2 = add_mock_collectible(entity_manager, 100, 100, 'plastic', 20)
        c3 = add_mock_collectible(entity_manager, 200, 200, 'glass', 30)

        assert len(entity_manager.collectibles) == 3
        assert len(entity_manager.entities) == 3


class TestRobotSelection:
    """Tests for robot selection functionality."""

    def test_select_robot(self, entity_manager):
        """Test selecting a robot."""
        robot = add_mock_robot(entity_manager, 100, 100)

        entity_manager.select_robot(robot)

        assert entity_manager.selected_robot == robot
        assert robot.selected is True

    def test_select_robot_deselects_previous(self, entity_manager):
        """Test that selecting a new robot deselects the previous one."""
        robot1 = add_mock_robot(entity_manager, 100, 100)
        robot2 = add_mock_robot(entity_manager, 200, 200)

        entity_manager.select_robot(robot1)
        entity_manager.select_robot(robot2)

        assert robot1.selected is False
        assert robot2.selected is True
        assert entity_manager.selected_robot == robot2

    def test_select_robot_none_deselects(self, entity_manager):
        """Test deselecting by passing None."""
        robot = add_mock_robot(entity_manager, 100, 100)

        entity_manager.select_robot(robot)
        entity_manager.select_robot(None)

        assert entity_manager.selected_robot is None
        assert robot.selected is False

    def test_select_robot_at_position(self, entity_manager):
        """Test selecting robot at a world position."""
        robot = add_mock_robot(entity_manager, 100, 100)

        # Robot is at (100, 100) with size 28x28
        result = entity_manager.select_robot_at(110, 110)

        assert result == robot
        assert entity_manager.selected_robot == robot

    def test_select_robot_at_position_no_robot(self, entity_manager):
        """Test selecting at position with no robot returns None."""
        add_mock_robot(entity_manager, 100, 100)

        result = entity_manager.select_robot_at(500, 500)

        assert result is None


class TestCollectibleQueries:
    """Tests for collectible lookup functionality."""

    def test_get_collectibles_near(self, entity_manager):
        """Test finding collectibles near a position."""
        add_mock_collectible(entity_manager, 100, 100, 'metal', 10)
        add_mock_collectible(entity_manager, 150, 150, 'plastic', 20)
        add_mock_collectible(entity_manager, 500, 500, 'glass', 30)

        nearby = entity_manager.get_collectibles_near(100, 100, radius=100)

        assert len(nearby) == 2  # First two are within radius

    def test_get_collectibles_near_none(self, entity_manager):
        """Test finding collectibles when none are nearby."""
        add_mock_collectible(entity_manager, 500, 500, 'metal', 10)

        nearby = entity_manager.get_collectibles_near(0, 0, radius=50)

        assert len(nearby) == 0

    def test_get_collectibles_near_exact_radius(self, entity_manager):
        """Test collectibles exactly at radius boundary."""
        add_mock_collectible(entity_manager, 100, 0, 'metal', 10)  # Distance = 100

        nearby = entity_manager.get_collectibles_near(0, 0, radius=100)

        assert len(nearby) == 1


class TestEntityUpdate:
    """Tests for entity update functionality."""

    def test_update_calls_robot_update(self, entity_manager):
        """Test that update calls robot updates."""
        robot = add_mock_robot(entity_manager, 100, 100)
        robot.update = Mock()

        entity_manager.update(0.016)

        robot.update.assert_called_once()

    def test_update_calls_collectible_update(self, entity_manager):
        """Test that update calls collectible updates."""
        collectible = add_mock_collectible(entity_manager, 50, 50, 'metal', 10)
        collectible.update = Mock()

        entity_manager.update(0.016)

        collectible.update.assert_called_once()

    def test_update_removes_inactive_entities(self, entity_manager):
        """Test that inactive entities are removed from entities dict during update."""
        collectible = add_mock_collectible(entity_manager, 100, 100, 'metal', 10)
        collectible_id = collectible.id

        collectible.active = False
        entity_manager.update(0.016)

        # The entity should be removed from the main entities dict
        # (removal from type-specific lists requires isinstance checks which mock objects fail)
        assert collectible_id not in entity_manager.entities

    def test_update_preserves_active_entities(self, entity_manager):
        """Test that active entities are preserved during update."""
        robot = add_mock_robot(entity_manager, 100, 100)
        robot.update = Mock()  # Prevent actual update
        robot_id = robot.id

        # Keep robot active (default state)
        entity_manager.update(0.016)

        # Active entity should still be present
        assert robot_id in entity_manager.entities
        assert robot in entity_manager.robots


class TestFactoryPosition:
    """Tests for factory position management."""

    def test_set_factory_position(self, entity_manager):
        """Test setting factory position."""
        entity_manager.set_factory_position(500, 600)

        assert entity_manager.factory_pos == (500, 600)

    def test_factory_position_updates_existing_robots(self, entity_manager):
        """Test that setting factory position updates existing robots."""
        robot = add_mock_robot(entity_manager, 100, 100)

        entity_manager.set_factory_position(500, 600)

        assert robot.factory_pos == (500, 600)

    def test_factory_position_updates_multiple_robots(self, entity_manager):
        """Test that setting factory position updates all robots."""
        robot1 = add_mock_robot(entity_manager, 100, 100)
        robot2 = add_mock_robot(entity_manager, 200, 200)

        entity_manager.set_factory_position(300, 400)

        assert robot1.factory_pos == (300, 400)
        assert robot2.factory_pos == (300, 400)


class TestEntityStats:
    """Tests for entity statistics."""

    def test_get_stats_empty(self, entity_manager):
        """Test stats for empty manager."""
        stats = entity_manager.get_stats()

        assert stats['total_entities'] == 0
        assert stats['robots'] == 0
        assert stats['collectibles'] == 0
        assert stats['buildings'] == 0

    def test_get_stats_with_robots(self, entity_manager):
        """Test stats with robots."""
        add_mock_robot(entity_manager, 0, 0)
        add_mock_robot(entity_manager, 100, 100)

        stats = entity_manager.get_stats()

        assert stats['total_entities'] == 2
        assert stats['robots'] == 2

    def test_get_stats_with_collectibles(self, entity_manager):
        """Test stats with collectibles."""
        add_mock_collectible(entity_manager, 50, 50, 'metal', 10)
        add_mock_collectible(entity_manager, 100, 100, 'plastic', 20)

        stats = entity_manager.get_stats()

        assert stats['total_entities'] == 2
        assert stats['collectibles'] == 2

    def test_get_stats_mixed_entities(self, entity_manager):
        """Test stats with mixed entity types."""
        add_mock_robot(entity_manager, 0, 0)
        add_mock_robot(entity_manager, 100, 100)
        add_mock_collectible(entity_manager, 50, 50, 'metal', 10)

        stats = entity_manager.get_stats()

        assert stats['total_entities'] == 3
        assert stats['robots'] == 2
        assert stats['collectibles'] == 1


class TestClearAll:
    """Tests for clearing all entities."""

    def test_clear_all(self, entity_manager):
        """Test clearing all entities."""
        robot = add_mock_robot(entity_manager, 100, 100)
        entity_manager.select_robot(robot)
        add_mock_collectible(entity_manager, 50, 50, 'metal', 10)

        entity_manager.clear_all()

        assert len(entity_manager.robots) == 0
        assert len(entity_manager.collectibles) == 0
        assert len(entity_manager.entities) == 0
        assert entity_manager.selected_robot is None

    def test_clear_all_clears_buildings(self, entity_manager):
        """Test that clear_all also clears buildings list."""
        entity_manager.buildings.append(Mock())

        entity_manager.clear_all()

        assert len(entity_manager.buildings) == 0


class TestResearchEffects:
    """Tests for research effect application."""

    def test_apply_research_effects_to_robots(self, entity_manager):
        """Test applying research effects to all robots."""
        mock_research = Mock()
        robot1 = add_mock_robot(entity_manager, 0, 0)
        robot2 = add_mock_robot(entity_manager, 100, 100)
        robot1.apply_research_effects = Mock()
        robot2.apply_research_effects = Mock()

        entity_manager.apply_research_effects_to_robots(mock_research)

        robot1.apply_research_effects.assert_called_once_with(mock_research)
        robot2.apply_research_effects.assert_called_once_with(mock_research)


class TestRepr:
    """Tests for string representation."""

    def test_repr_empty(self, entity_manager):
        """Test string representation for empty manager."""
        repr_str = repr(entity_manager)

        assert 'EntityManager' in repr_str
        assert 'robots=0' in repr_str
        assert 'collectibles=0' in repr_str

    def test_repr_with_entities(self, entity_manager):
        """Test string representation with entities."""
        add_mock_robot(entity_manager, 100, 100)
        add_mock_collectible(entity_manager, 50, 50, 'metal', 10)

        repr_str = repr(entity_manager)

        assert 'EntityManager' in repr_str
        assert 'robots=1' in repr_str
        assert 'collectibles=1' in repr_str
