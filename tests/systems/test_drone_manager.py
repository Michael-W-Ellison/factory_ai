"""
Unit tests for DroneManager.

Tests drone operations, battery management, fog of war, and exploration.
"""

import sys
import os
import pytest
import math
from unittest.mock import Mock, MagicMock

# Mock pygame before any imports that might need it
sys.modules['pygame'] = Mock()

# Import directly to avoid __init__.py cascade
import importlib.util

# Get the path relative to this test file
_test_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_test_dir))
_module_path = os.path.join(_project_root, "src", "systems", "drone_manager.py")

spec = importlib.util.spec_from_file_location(
    "drone_manager",
    _module_path
)
drone_manager_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drone_manager_module)
DroneManager = drone_manager_module.DroneManager
Drone = drone_manager_module.Drone
DroneState = drone_manager_module.DroneState
FogOfWar = drone_manager_module.FogOfWar


class MockResourceManager:
    """Mock resource manager for testing drone purchases."""

    def __init__(self, initial_money=100000):
        self.money = initial_money

    def modify_money(self, amount):
        self.money += amount


class TestDroneDataclass:
    """Tests for Drone dataclass."""

    def test_drone_init_defaults(self):
        """Test drone initialization with default values."""
        drone = Drone(id=1, position=(0, 0), state=DroneState.IDLE)

        assert drone.id == 1
        assert drone.position == (0, 0)
        assert drone.state == DroneState.IDLE
        assert drone.battery == 100.0
        assert drone.max_battery == 100.0
        assert drone.speed == 5.0
        assert drone.vision_radius == 10.0

    def test_drone_get_distance_to(self):
        """Test distance calculation."""
        drone = Drone(id=1, position=(0, 0), state=DroneState.IDLE)

        distance = drone.get_distance_to((3, 4))

        assert distance == 5.0  # 3-4-5 triangle

    def test_drone_move_towards_reaches_target(self):
        """Test drone reaches nearby target within threshold."""
        drone = Drone(id=1, position=(0, 0), state=DroneState.FLYING, speed=10.0)

        # Target within 0.1 threshold - considered reached immediately
        reached = drone.move_towards((0.05, 0), 1.0)

        assert reached is True
        # Position unchanged when within threshold distance
        assert drone.position == (0, 0)

    def test_drone_move_towards_partial_movement(self):
        """Test drone moves partially toward distant target."""
        drone = Drone(id=1, position=(0, 0), state=DroneState.FLYING, speed=5.0)

        reached = drone.move_towards((100, 0), 1.0)

        assert reached is False
        assert drone.position[0] == pytest.approx(5.0, rel=0.01)

    def test_drone_move_towards_diagonal(self):
        """Test drone moves correctly diagonally."""
        drone = Drone(id=1, position=(0, 0), state=DroneState.FLYING, speed=10.0)

        drone.move_towards((10, 10), 1.0)

        # Should move along diagonal
        expected = 10 / math.sqrt(2)
        assert drone.position[0] == pytest.approx(expected, rel=0.01)
        assert drone.position[1] == pytest.approx(expected, rel=0.01)


class TestFogOfWar:
    """Tests for FogOfWar system."""

    def test_fog_init_with_dimensions(self):
        """Test fog of war initialization."""
        fog = FogOfWar(map_width=100, map_height=100)

        assert fog.map_width == 100
        assert fog.map_height == 100

    def test_fog_init_explores_starting_area(self):
        """Test that starting area is explored on init."""
        fog = FogOfWar(100, 100)

        # Origin should be explored
        assert fog.is_explored((0, 0)) is True
        assert fog.is_explored((5, 5)) is True

    def test_fog_reveal_area_permanent(self):
        """Test permanent area reveal."""
        fog = FogOfWar(200, 200)

        revealed = fog.reveal_area((50, 50), 5, is_permanent=True)

        assert len(revealed) > 0
        assert fog.is_explored((50, 50)) is True

    def test_fog_reveal_area_temporary(self):
        """Test temporary (visible) area reveal."""
        fog = FogOfWar(200, 200)

        fog.reveal_area((50, 50), 3, is_permanent=False)

        assert (50, 50) in fog.visible_tiles

    def test_fog_clear_visible_tiles(self):
        """Test clearing visible tiles."""
        fog = FogOfWar(100, 100)
        fog.reveal_area((30, 30), 3, is_permanent=False)

        fog.clear_visible_tiles()

        assert len(fog.visible_tiles) == 0

    def test_fog_is_visible_includes_explored(self):
        """Test is_visible includes explored tiles."""
        fog = FogOfWar(100, 100)

        # Origin is explored by default
        assert fog.is_visible((0, 0)) is True

    def test_fog_get_exploration_percentage(self):
        """Test exploration percentage calculation."""
        fog = FogOfWar(100, 100)  # 10000 total tiles

        # Starting area is ~121 tiles (11x11)
        percentage = fog.get_exploration_percentage()

        assert percentage > 0
        assert percentage < 100


class TestDroneManagerInit:
    """Tests for DroneManager initialization."""

    def test_init_creates_fog_of_war(self):
        """Test initialization creates fog of war."""
        resources = MockResourceManager()
        manager = DroneManager(resources, map_width=200, map_height=200)

        assert manager.fog_of_war is not None
        assert manager.fog_of_war.map_width == 200

    def test_init_empty_drones(self):
        """Test initialization starts with no drones."""
        resources = MockResourceManager()
        manager = DroneManager(resources)

        assert len(manager.drones) == 0
        assert manager.next_drone_id == 1

    def test_init_default_values(self):
        """Test initialization default values."""
        resources = MockResourceManager()
        manager = DroneManager(resources)

        assert manager.max_drones == 5
        assert manager.drone_purchase_cost == 5000
        assert manager.auto_return_battery == 20.0


class TestDronePurchase:
    """Tests for drone purchase functionality."""

    def test_purchase_drone_success(self):
        """Test successful drone purchase."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)

        result = manager.purchase_drone()

        assert result is True
        assert len(manager.drones) == 1
        assert resources.money == 95000  # 100000 - 5000

    def test_purchase_drone_insufficient_funds(self):
        """Test purchase fails with insufficient funds."""
        resources = MockResourceManager(1000)  # Less than 5000
        manager = DroneManager(resources)

        result = manager.purchase_drone()

        assert result is False
        assert len(manager.drones) == 0
        assert resources.money == 1000

    def test_purchase_drone_max_limit(self):
        """Test purchase fails when at max drones."""
        resources = MockResourceManager(1000000)
        manager = DroneManager(resources)
        manager.max_drones = 2

        manager.purchase_drone()
        manager.purchase_drone()
        result = manager.purchase_drone()  # Third purchase

        assert result is False
        assert len(manager.drones) == 2

    def test_purchase_drone_creates_at_base(self):
        """Test purchased drone is created at base position."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)
        manager.base_position = (10.0, 20.0)

        manager.purchase_drone()

        drone = manager.drones[1]
        assert drone.position == (10.0, 20.0)
        assert drone.state == DroneState.IDLE


class TestDroneDeployment:
    """Tests for drone deployment."""

    def test_deploy_drone_success(self):
        """Test successful drone deployment."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)
        manager.purchase_drone()

        result = manager.deploy_drone(1, (50.0, 50.0))

        assert result is True
        assert manager.drones[1].state == DroneState.FLYING
        assert manager.drones[1].target_position == (50.0, 50.0)

    def test_deploy_drone_invalid_id(self):
        """Test deployment fails for invalid drone ID."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)

        result = manager.deploy_drone(999, (50.0, 50.0))

        assert result is False

    def test_deploy_drone_already_flying(self):
        """Test deployment fails if drone already flying."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)
        manager.purchase_drone()
        manager.deploy_drone(1, (50.0, 50.0))

        result = manager.deploy_drone(1, (100.0, 100.0))

        assert result is False

    def test_deploy_drone_low_battery(self):
        """Test deployment fails with low battery."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)
        manager.purchase_drone()
        manager.drones[1].battery = 5.0  # Below 10% threshold

        result = manager.deploy_drone(1, (50.0, 50.0))

        assert result is False

    def test_deploy_drone_increments_deployed_stat(self):
        """Test deployment increments statistics."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)
        manager.purchase_drone()

        manager.deploy_drone(1, (50.0, 50.0))

        assert manager.drones_deployed == 1


class TestDroneRecall:
    """Tests for drone recall functionality."""

    def test_recall_drone_success(self):
        """Test successful drone recall."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)
        manager.purchase_drone()
        manager.deploy_drone(1, (50.0, 50.0))

        result = manager.recall_drone(1)

        assert result is True
        assert manager.drones[1].state == DroneState.RETURNING

    def test_recall_drone_invalid_id(self):
        """Test recall fails for invalid ID."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)

        result = manager.recall_drone(999)

        assert result is False

    def test_recall_drone_not_flying(self):
        """Test recall fails if drone not flying."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)
        manager.purchase_drone()

        result = manager.recall_drone(1)  # Drone is IDLE

        assert result is False


class TestDroneUpdate:
    """Tests for drone update functionality."""

    def test_update_clears_visible_tiles(self):
        """Test update clears visible tiles each frame."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)
        manager.fog_of_war.visible_tiles.add((100, 100))

        manager.update(0.1, 0)

        assert len(manager.fog_of_war.visible_tiles) == 0

    def test_update_flying_drone_drains_battery(self):
        """Test flying drone loses battery."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)
        manager.purchase_drone()
        manager.deploy_drone(1, (50.0, 50.0))

        initial_battery = manager.drones[1].battery
        manager.update(1.0, 0)

        assert manager.drones[1].battery < initial_battery

    def test_update_flying_drone_reveals_area(self):
        """Test flying drone reveals fog of war."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)
        manager.purchase_drone()
        manager.drones[1].position = (50.0, 50.0)
        manager.drones[1].state = DroneState.FLYING

        manager.update(0.1, 0)

        assert manager.fog_of_war.is_explored((50, 50))

    def test_update_drone_crashes_at_zero_battery(self):
        """Test drone crashes when battery depleted."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)
        manager.purchase_drone()
        manager.deploy_drone(1, (50.0, 50.0))
        manager.drones[1].battery = 0.5  # Very low

        manager.update(1.0, 0)

        assert manager.drones[1].state == DroneState.CRASHED
        assert manager.drones_crashed == 1

    def test_update_drone_auto_returns_low_battery(self):
        """Test drone auto-returns at low battery."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)
        manager.auto_return_battery = 20.0
        manager.purchase_drone()
        manager.deploy_drone(1, (50.0, 50.0))
        manager.drones[1].battery = 18.0  # Below threshold

        manager.update(0.1, 0)

        assert manager.drones[1].state == DroneState.RETURNING

    def test_update_charging_drone_gains_battery(self):
        """Test charging drone regains battery."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)
        manager.purchase_drone()
        manager.drones[1].state = DroneState.CHARGING
        manager.drones[1].battery = 50.0

        manager.update(1.0, 0)

        assert manager.drones[1].battery > 50.0

    def test_update_fully_charged_becomes_idle(self):
        """Test fully charged drone becomes idle."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)
        manager.purchase_drone()
        manager.drones[1].state = DroneState.CHARGING
        manager.drones[1].battery = 99.9
        manager.drones[1].max_battery = 100.0

        manager.update(1.0, 0)

        assert manager.drones[1].state == DroneState.IDLE

    def test_update_returning_drone_reaches_base(self):
        """Test returning drone reaches base and starts charging."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)
        manager.purchase_drone()
        manager.drones[1].state = DroneState.RETURNING
        manager.drones[1].position = (0.01, 0)  # Very close to base

        manager.update(1.0, 0)

        assert manager.drones[1].state == DroneState.CHARGING


class TestDroneQueries:
    """Tests for drone query methods."""

    def test_get_drone_count_by_state(self):
        """Test drone count by state."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)
        manager.purchase_drone()
        manager.purchase_drone()
        manager.deploy_drone(1, (50.0, 50.0))

        counts = manager.get_drone_count()

        assert counts['total'] == 2
        assert counts['flying'] == 1
        assert counts['idle'] == 1

    def test_get_exploration_percentage(self):
        """Test exploration percentage retrieval."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources, map_width=100, map_height=100)

        percentage = manager.get_exploration_percentage()

        assert isinstance(percentage, float)
        assert 0 <= percentage <= 100

    def test_is_position_explored(self):
        """Test position exploration check."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)

        # Origin should be explored by default
        assert manager.is_position_explored((0, 0)) is True
        assert manager.is_position_explored((1000, 1000)) is False

    def test_is_position_visible(self):
        """Test position visibility check."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)

        assert manager.is_position_visible((0, 0)) is True

    def test_get_summary(self):
        """Test summary retrieval."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources)
        manager.purchase_drone()

        summary = manager.get_summary()

        assert 'drones' in summary
        assert 'max_drones' in summary
        assert 'exploration_percent' in summary
        assert 'tiles_explored' in summary
        assert 'drones_deployed' in summary
        assert 'drones_crashed' in summary
        assert 'purchase_cost' in summary


class TestDroneStateEnum:
    """Tests for DroneState enum."""

    def test_drone_states_exist(self):
        """Test all expected drone states exist."""
        assert DroneState.IDLE.value == 0
        assert DroneState.FLYING.value == 1
        assert DroneState.RETURNING.value == 2
        assert DroneState.CRASHED.value == 3
        assert DroneState.CHARGING.value == 4


class TestDroneManagerRepr:
    """Tests for string representation."""

    def test_repr_format(self):
        """Test string representation format."""
        resources = MockResourceManager(100000)
        manager = DroneManager(resources, map_width=100, map_height=100)
        manager.purchase_drone()
        manager.deploy_drone(1, (50.0, 50.0))

        repr_str = repr(manager)

        assert 'DroneManager' in repr_str
        assert 'drones=' in repr_str
        assert 'flying=' in repr_str
        assert 'exploration=' in repr_str
