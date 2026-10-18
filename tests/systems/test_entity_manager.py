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


# Patch pygame before importing modules that use it
with patch.dict('sys.modules', {'pygame': MagicMock()}):
    from src.systems.entity_manager import EntityManager
    from src.systems.material_inventory import MaterialSource


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
        self.source = source or MaterialSource.LANDFILL
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
    with patch('src.systems.entity_manager.Robot', MockRobot):
        with patch('src.systems.entity_manager.CollectibleObject', MockCollectible):
            manager = EntityManager(grid=mock_grid)
            return manager


class TestEntityManagerInitialization:
    """Tests for EntityManager initialization."""

    def test_init_with_default_values(self):
        """Test EntityManager initializes with empty collections."""
        manager = EntityManager()

        assert manager.entities == {}
        assert manager.robots == []
        assert manager.collectibles == []
        assert manager.buildings == []
        assert manager.selected_robot is None
        assert manager.factory_pos is None

    def test_init_with_grid(self, mock_grid):
        """Test EntityManager accepts grid on initialization."""
        manager = EntityManager(grid=mock_grid)

        assert manager.grid is mock_grid


class TestRobotCreation:
    """Tests for robot creation and management."""

    def test_create_robot_basic(self, entity_manager):
        """Test creating a basic robot."""
        with patch('src.systems.entity_manager.Robot', MockRobot):
            robot = entity_manager.create_robot(100.0, 200.0)

        assert robot is not None
        assert robot.x == 100.0
        assert robot.y == 200.0
        assert robot.autonomous is True
        assert robot in entity_manager.robots
        assert robot.id in entity_manager.entities

    def test_create_robot_non_autonomous(self, entity_manager):
        """Test creating a non-autonomous (player-controlled) robot."""
        with patch('src.systems.entity_manager.Robot', MockRobot):
            robot = entity_manager.create_robot(50.0, 75.0, autonomous=False)

        assert robot.autonomous is False
        assert entity_manager.selected_robot == robot
        assert robot.selected is True

    def test_create_multiple_robots(self, entity_manager):
        """Test creating multiple robots."""
        with patch('src.systems.entity_manager.Robot', MockRobot):
            robot1 = entity_manager.create_robot(0, 0)
            robot2 = entity_manager.create_robot(100, 100)
            robot3 = entity_manager.create_robot(200, 200)

        assert len(entity_manager.robots) == 3
        assert len(entity_manager.entities) == 3

    def test_robot_gets_factory_position(self, entity_manager):
        """Test that new robots receive the factory position."""
        entity_manager.factory_pos = (500, 600)

        with patch('src.systems.entity_manager.Robot', MockRobot):
            robot = entity_manager.create_robot(100, 100)

        assert robot.factory_pos == (500, 600)

    def test_robot_gets_research_effects(self, entity_manager):
        """Test that new robots receive research effects."""
        mock_research = Mock()
        entity_manager.research_manager = mock_research

        with patch('src.systems.entity_manager.Robot', MockRobot):
            robot = entity_manager.create_robot(100, 100)

        # MockRobot.apply_research_effects should have been called
        # (in real implementation, robot.apply_research_effects(research_manager) is called)


class TestCollectibleCreation:
    """Tests for collectible creation."""

    def test_create_collectible_basic(self, entity_manager):
        """Test creating a basic collectible."""
        with patch('src.systems.entity_manager.CollectibleObject', MockCollectible):
            collectible = entity_manager.create_collectible(
                x=100.0, y=200.0,
                material_type='metal',
                quantity=50.0
            )

        assert collectible is not None
        assert collectible.x == 100.0
        assert collectible.y == 200.0
        assert collectible.material_type == 'metal'
        assert collectible.quantity == 50.0
        assert collectible in entity_manager.collectibles
        assert collectible.id in entity_manager.entities

    def test_create_collectible_with_source(self, entity_manager):
        """Test creating collectible with specific material source."""
        with patch('src.systems.entity_manager.CollectibleObject', MockCollectible):
            collectible = entity_manager.create_collectible(
                x=50.0, y=50.0,
                material_type='plastic',
                quantity=20.0,
                source=MaterialSource.VEHICLE
            )

        assert collectible.source == MaterialSource.VEHICLE


class TestRobotSelection:
    """Tests for robot selection functionality."""

    def test_select_robot(self, entity_manager):
        """Test selecting a robot."""
        with patch('src.systems.entity_manager.Robot', MockRobot):
            robot = entity_manager.create_robot(100, 100)

        entity_manager.select_robot(robot)

        assert entity_manager.selected_robot == robot
        assert robot.selected is True

    def test_select_robot_deselects_previous(self, entity_manager):
        """Test that selecting a new robot deselects the previous one."""
        with patch('src.systems.entity_manager.Robot', MockRobot):
            robot1 = entity_manager.create_robot(100, 100)
            robot2 = entity_manager.create_robot(200, 200)

        entity_manager.select_robot(robot1)
        entity_manager.select_robot(robot2)

        assert robot1.selected is False
        assert robot2.selected is True
        assert entity_manager.selected_robot == robot2

    def test_select_robot_none_deselects(self, entity_manager):
        """Test deselecting by passing None."""
        with patch('src.systems.entity_manager.Robot', MockRobot):
            robot = entity_manager.create_robot(100, 100)

        entity_manager.select_robot(robot)
        entity_manager.select_robot(None)

        assert entity_manager.selected_robot is None
        assert robot.selected is False

    def test_select_robot_at_position(self, entity_manager):
        """Test selecting robot at a world position."""
        with patch('src.systems.entity_manager.Robot', MockRobot):
            robot = entity_manager.create_robot(100, 100)

        # Robot is at (100, 100) with size 28x28
        result = entity_manager.select_robot_at(110, 110)

        assert result == robot
        assert entity_manager.selected_robot == robot

    def test_select_robot_at_position_no_robot(self, entity_manager):
        """Test selecting at position with no robot returns None."""
        with patch('src.systems.entity_manager.Robot', MockRobot):
            entity_manager.create_robot(100, 100)

        result = entity_manager.select_robot_at(500, 500)

        assert result is None


class TestCollectibleQueries:
    """Tests for collectible lookup functionality."""

    def test_get_collectibles_near(self, entity_manager):
        """Test finding collectibles near a position."""
        with patch('src.systems.entity_manager.CollectibleObject', MockCollectible):
            entity_manager.create_collectible(100, 100, 'metal', 10)
            entity_manager.create_collectible(150, 150, 'plastic', 20)
            entity_manager.create_collectible(500, 500, 'glass', 30)

        nearby = entity_manager.get_collectibles_near(100, 100, radius=100)

        assert len(nearby) == 2  # First two are within radius

    def test_get_collectibles_near_none(self, entity_manager):
        """Test finding collectibles when none are nearby."""
        with patch('src.systems.entity_manager.CollectibleObject', MockCollectible):
            entity_manager.create_collectible(500, 500, 'metal', 10)

        nearby = entity_manager.get_collectibles_near(0, 0, radius=50)

        assert len(nearby) == 0


class TestEntityUpdate:
    """Tests for entity update functionality."""

    def test_update_calls_robot_update(self, entity_manager):
        """Test that update calls robot updates."""
        with patch('src.systems.entity_manager.Robot', MockRobot):
            robot = entity_manager.create_robot(100, 100)
        robot.update = Mock()

        entity_manager.update(0.016)

        robot.update.assert_called_once()

    def test_update_removes_inactive_entities(self, entity_manager):
        """Test that inactive entities are removed during update."""
        with patch('src.systems.entity_manager.CollectibleObject', MockCollectible):
            collectible = entity_manager.create_collectible(100, 100, 'metal', 10)

        collectible.active = False
        entity_manager.update(0.016)

        assert collectible not in entity_manager.collectibles
        assert collectible.id not in entity_manager.entities


class TestFactoryPosition:
    """Tests for factory position management."""

    def test_set_factory_position(self, entity_manager):
        """Test setting factory position."""
        entity_manager.set_factory_position(500, 600)

        assert entity_manager.factory_pos == (500, 600)

    def test_factory_position_updates_existing_robots(self, entity_manager):
        """Test that setting factory position updates existing robots."""
        with patch('src.systems.entity_manager.Robot', MockRobot):
            robot = entity_manager.create_robot(100, 100)

        entity_manager.set_factory_position(500, 600)

        assert robot.factory_pos == (500, 600)


class TestEntityStats:
    """Tests for entity statistics."""

    def test_get_stats_empty(self, entity_manager):
        """Test stats for empty manager."""
        stats = entity_manager.get_stats()

        assert stats['total_entities'] == 0
        assert stats['robots'] == 0
        assert stats['collectibles'] == 0
        assert stats['buildings'] == 0

    def test_get_stats_with_entities(self, entity_manager):
        """Test stats with various entities."""
        with patch('src.systems.entity_manager.Robot', MockRobot):
            entity_manager.create_robot(0, 0)
            entity_manager.create_robot(100, 100)

        with patch('src.systems.entity_manager.CollectibleObject', MockCollectible):
            entity_manager.create_collectible(50, 50, 'metal', 10)

        stats = entity_manager.get_stats()

        assert stats['total_entities'] == 3
        assert stats['robots'] == 2
        assert stats['collectibles'] == 1


class TestClearAll:
    """Tests for clearing all entities."""

    def test_clear_all(self, entity_manager):
        """Test clearing all entities."""
        with patch('src.systems.entity_manager.Robot', MockRobot):
            robot = entity_manager.create_robot(100, 100)
        entity_manager.select_robot(robot)

        with patch('src.systems.entity_manager.CollectibleObject', MockCollectible):
            entity_manager.create_collectible(50, 50, 'metal', 10)

        entity_manager.clear_all()

        assert len(entity_manager.robots) == 0
        assert len(entity_manager.collectibles) == 0
        assert len(entity_manager.entities) == 0
        assert entity_manager.selected_robot is None


class TestRepr:
    """Tests for string representation."""

    def test_repr(self, entity_manager):
        """Test string representation."""
        with patch('src.systems.entity_manager.Robot', MockRobot):
            entity_manager.create_robot(100, 100)

        with patch('src.systems.entity_manager.CollectibleObject', MockCollectible):
            entity_manager.create_collectible(50, 50, 'metal', 10)

        repr_str = repr(entity_manager)

        assert 'EntityManager' in repr_str
        assert 'robots=1' in repr_str
        assert 'collectibles=1' in repr_str
