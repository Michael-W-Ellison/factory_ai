"""
Tests for NPCManager - manages NPC spawning, scheduling, and detection.

Tests cover:
- NPC spawning in houses
- NPC queries by position
- Game time management
- Detection of robot activities
- Statistics
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


# Patch pygame before importing modules that use it
with patch.dict('sys.modules', {'pygame': MagicMock()}):
    from src.systems.npc_manager import NPCManager
    from src.entities.npc import Activity
    from src.world.tile import TileType


class MockNPC:
    """Mock NPC for testing without pygame dependencies."""
    _id_counter = 0

    def __init__(self, world_x, world_y, home_x, home_y, work_x=None, work_y=None):
        MockNPC._id_counter += 1
        self.id = MockNPC._id_counter
        self.world_x = world_x
        self.world_y = world_y
        self.home_x = home_x
        self.home_y = home_y
        self.work_x = work_x
        self.work_y = work_y
        self.has_job = work_x is not None and work_y is not None
        self.current_activity = Activity.HOME_ROUTINE
        self.target_x = world_x
        self.target_y = world_y
        self.using_bus = False
        self.target_bus_stop = None
        self.bus_preference = 0.5
        self.detecting_robots = {}

    def update(self, dt, game_time):
        pass

    def calculate_detection_chance(self, robot_x, robot_y, is_daytime, robot_stealth):
        """Calculate chance of detecting a robot."""
        dx = robot_x - self.world_x
        dy = robot_y - self.world_y
        distance = (dx * dx + dy * dy) ** 0.5

        if distance > 100:  # vision range
            return 0.0

        return (1.0 - distance / 100.0) * (1.0 - robot_stealth) * (1.5 if is_daytime else 0.5)

    def update_detection(self, robot_id, detection_chance, dt):
        """Update detection progress for a robot."""
        if robot_id not in self.detecting_robots:
            self.detecting_robots[robot_id] = 0.0

        self.detecting_robots[robot_id] += detection_chance * dt
        return self.detecting_robots[robot_id] >= 1.0

    def clear_detection(self, robot_id):
        """Clear detection progress for a robot."""
        if robot_id in self.detecting_robots:
            del self.detecting_robots[robot_id]

    def render(self, screen, camera):
        pass

    def start_bus_journey(self, bus_stop_pos, destination_stop, final_dest):
        """Start a bus journey."""
        self.using_bus = True
        self.target_bus_stop = bus_stop_pos


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


class MockRobot:
    """Mock robot for testing."""
    def __init__(self, x, y, robot_id=None):
        self.id = robot_id or id(self)
        self.x = x
        self.y = y
        self.stealth_level = 0.5


@pytest.fixture
def mock_grid():
    """Provide a mock grid."""
    return MockGrid()


@pytest.fixture
def npc_manager(mock_grid):
    """Provide an NPCManager instance with mocked grid."""
    return NPCManager(mock_grid)


class TestNPCManagerInitialization:
    """Tests for NPCManager initialization."""

    def test_init_with_grid(self, mock_grid):
        """Test NPCManager initializes with grid."""
        manager = NPCManager(mock_grid)

        assert manager.grid is mock_grid
        assert manager.npcs == []

    def test_init_default_time(self, npc_manager):
        """Test default game time is 8am."""
        assert npc_manager.game_time == 8.0

    def test_init_default_parameters(self, npc_manager):
        """Test default NPC parameters."""
        assert npc_manager.npcs_per_house == 2
        assert npc_manager.employment_rate == 0.7
        assert npc_manager.time_scale == 60.0
        assert npc_manager.bus_usage_rate == 0.4


class TestNPCSpawning:
    """Tests for NPC spawning."""

    def test_spawn_npcs_in_city(self, npc_manager, mock_grid):
        """Test spawning NPCs in city buildings."""
        # Setup: add some buildings
        mock_grid.set_tile_type(5, 5, TileType.BUILDING)
        mock_grid.set_tile_type(10, 10, TileType.BUILDING)

        with patch('src.systems.npc_manager.NPC', MockNPC):
            npc_manager.spawn_npcs_in_city(seed=42)

        assert len(npc_manager.npcs) > 0

    def test_spawn_with_seed_is_reproducible(self, mock_grid):
        """Test that same seed produces same NPC placement."""
        mock_grid.set_tile_type(5, 5, TileType.BUILDING)
        mock_grid.set_tile_type(10, 10, TileType.BUILDING)

        manager1 = NPCManager(mock_grid)
        manager2 = NPCManager(mock_grid)

        with patch('src.systems.npc_manager.NPC', MockNPC):
            manager1.spawn_npcs_in_city(seed=123)

        # Reset mock NPC counter
        MockNPC._id_counter = 0

        with patch('src.systems.npc_manager.NPC', MockNPC):
            manager2.spawn_npcs_in_city(seed=123)

        assert len(manager1.npcs) == len(manager2.npcs)

    def test_spawn_creates_employed_npcs(self, npc_manager, mock_grid):
        """Test that some spawned NPCs are employed."""
        mock_grid.set_tile_type(5, 5, TileType.BUILDING)
        mock_grid.set_tile_type(10, 10, TileType.BUILDING)
        mock_grid.set_tile_type(15, 15, TileType.BUILDING)

        with patch('src.systems.npc_manager.NPC', MockNPC):
            npc_manager.spawn_npcs_in_city(seed=42)

        employed = sum(1 for npc in npc_manager.npcs if npc.has_job)
        assert employed > 0


class TestFindBuildings:
    """Tests for finding buildings."""

    def test_find_buildings_of_type(self, npc_manager, mock_grid):
        """Test finding buildings of a specific type."""
        mock_grid.set_tile_type(5, 5, TileType.BUILDING)
        mock_grid.set_tile_type(10, 10, TileType.BUILDING)
        mock_grid.set_tile_type(15, 15, TileType.GRASS)  # Not a building

        buildings = npc_manager._find_buildings(TileType.BUILDING)

        assert len(buildings) == 2
        assert (5, 5) in buildings
        assert (10, 10) in buildings

    def test_find_buildings_empty(self, npc_manager, mock_grid):
        """Test finding buildings when none exist."""
        buildings = npc_manager._find_buildings(TileType.BUILDING)

        assert len(buildings) == 0


class TestNPCQueries:
    """Tests for NPC queries."""

    def test_get_npc_at_position(self, npc_manager):
        """Test getting NPC at world position."""
        npc = MockNPC(100.0, 100.0, 5, 5)
        npc_manager.npcs.append(npc)

        result = npc_manager.get_npc_at(100.0, 100.0)

        assert result == npc

    def test_get_npc_at_position_with_tolerance(self, npc_manager):
        """Test getting NPC within tolerance distance."""
        npc = MockNPC(100.0, 100.0, 5, 5)
        npc_manager.npcs.append(npc)

        # Within default tolerance of 16.0
        result = npc_manager.get_npc_at(110.0, 100.0)

        assert result == npc

    def test_get_npc_at_position_outside_tolerance(self, npc_manager):
        """Test getting NPC outside tolerance returns None."""
        npc = MockNPC(100.0, 100.0, 5, 5)
        npc_manager.npcs.append(npc)

        # Outside default tolerance of 16.0
        result = npc_manager.get_npc_at(150.0, 100.0)

        assert result is None

    def test_get_npc_at_empty_world(self, npc_manager):
        """Test getting NPC in empty world returns None."""
        result = npc_manager.get_npc_at(100.0, 100.0)

        assert result is None


class TestGameTime:
    """Tests for game time management."""

    def test_update_advances_time(self, npc_manager):
        """Test that update advances game time."""
        initial_time = npc_manager.game_time

        npc_manager.update(1.0)  # 1 second

        # With time_scale of 60.0, 1 second = 1/60 hour = 0.0167 hours
        expected_time = initial_time + (1.0 * 60.0) / 3600.0
        assert abs(npc_manager.game_time - expected_time) < 0.001

    def test_time_wraps_at_24_hours(self, npc_manager):
        """Test that game time wraps at 24 hours."""
        npc_manager.game_time = 23.9

        # Advance time by enough to pass midnight
        npc_manager.update(10.0)  # Should push past 24

        assert npc_manager.game_time >= 0.0
        assert npc_manager.game_time < 24.0

    def test_get_time_string_am(self, npc_manager):
        """Test time string formatting for AM times."""
        npc_manager.game_time = 9.5  # 9:30 AM

        time_str = npc_manager.get_time_string()

        assert 'AM' in time_str
        assert '09' in time_str or '9' in time_str
        assert '30' in time_str

    def test_get_time_string_pm(self, npc_manager):
        """Test time string formatting for PM times."""
        npc_manager.game_time = 14.25  # 2:15 PM

        time_str = npc_manager.get_time_string()

        assert 'PM' in time_str
        assert '02' in time_str or '2' in time_str
        assert '15' in time_str

    def test_get_time_string_noon(self, npc_manager):
        """Test time string formatting for noon."""
        npc_manager.game_time = 12.0

        time_str = npc_manager.get_time_string()

        assert 'PM' in time_str
        assert '12' in time_str

    def test_get_time_string_midnight(self, npc_manager):
        """Test time string formatting for midnight."""
        npc_manager.game_time = 0.0

        time_str = npc_manager.get_time_string()

        assert 'AM' in time_str
        assert '12' in time_str


class TestNPCUpdate:
    """Tests for NPC update functionality."""

    def test_update_calls_npc_update(self, npc_manager):
        """Test that update calls each NPC's update method."""
        npc = MockNPC(100.0, 100.0, 5, 5)
        npc.update = Mock()
        npc_manager.npcs.append(npc)

        npc_manager.update(0.016)

        npc.update.assert_called_once()


class TestDetection:
    """Tests for robot detection."""

    def test_check_detections_returns_reports(self, npc_manager):
        """Test that check_detections returns reports when NPCs detect robots."""
        npc = MockNPC(100.0, 100.0, 5, 5)
        npc.current_activity = Activity.WORKING
        npc_manager.npcs.append(npc)

        robot = MockRobot(105.0, 100.0)
        robot.stealth_level = 0.0  # Very visible

        # Run detection multiple times to build up progress
        for _ in range(100):
            reports = npc_manager.check_detections([robot], 0.1)
            if reports:
                break

        # Eventually should get a report
        assert npc.detecting_robots.get(robot.id, 0) > 0 or len(reports) > 0

    def test_sleeping_npcs_dont_detect(self, npc_manager):
        """Test that sleeping NPCs don't detect robots."""
        npc = MockNPC(100.0, 100.0, 5, 5)
        npc.current_activity = Activity.SLEEPING
        npc_manager.npcs.append(npc)

        robot = MockRobot(105.0, 100.0)

        reports = npc_manager.check_detections([robot], 0.1)

        assert len(reports) == 0
        assert robot.id not in npc.detecting_robots

    def test_distant_robots_not_detected(self, npc_manager):
        """Test that distant robots are not detected."""
        npc = MockNPC(100.0, 100.0, 5, 5)
        npc.current_activity = Activity.WORKING
        npc_manager.npcs.append(npc)

        robot = MockRobot(500.0, 500.0)  # Far away

        reports = npc_manager.check_detections([robot], 0.1)

        assert len(reports) == 0


class TestNPCStats:
    """Tests for NPC statistics."""

    def test_get_stats_empty(self, npc_manager):
        """Test stats for empty NPC manager."""
        stats = npc_manager.get_stats()

        assert stats['total'] == 0
        assert stats['employed'] == 0
        assert stats['unemployed'] == 0
        assert 'current_time' in stats

    def test_get_stats_with_npcs(self, npc_manager):
        """Test stats with various NPCs."""
        npc1 = MockNPC(100.0, 100.0, 5, 5, work_x=10, work_y=10)  # Employed
        npc2 = MockNPC(200.0, 200.0, 6, 6)  # Unemployed
        npc3 = MockNPC(300.0, 300.0, 7, 7, work_x=15, work_y=15)  # Employed

        npc_manager.npcs.extend([npc1, npc2, npc3])

        stats = npc_manager.get_stats()

        assert stats['total'] == 3
        assert stats['employed'] == 2
        assert stats['unemployed'] == 1

    def test_get_stats_includes_activities(self, npc_manager):
        """Test that stats include activity breakdown."""
        npc1 = MockNPC(100.0, 100.0, 5, 5)
        npc1.current_activity = Activity.WORKING
        npc2 = MockNPC(200.0, 200.0, 6, 6)
        npc2.current_activity = Activity.SLEEPING

        npc_manager.npcs.extend([npc1, npc2])

        stats = npc_manager.get_stats()

        assert 'activities' in stats
        assert Activity.WORKING in stats['activities']
        assert Activity.SLEEPING in stats['activities']


class TestBusIntegration:
    """Tests for bus system integration."""

    def test_bus_manager_initially_none(self, npc_manager):
        """Test that bus manager is initially None."""
        assert npc_manager.bus_manager is None

    def test_bus_manager_can_be_set(self, npc_manager):
        """Test that bus manager can be set externally."""
        mock_bus_manager = Mock()
        npc_manager.bus_manager = mock_bus_manager

        assert npc_manager.bus_manager is mock_bus_manager

    def test_update_without_bus_manager(self, npc_manager):
        """Test that update works without bus manager."""
        npc = MockNPC(100.0, 100.0, 5, 5)
        npc_manager.npcs.append(npc)

        # Should not raise
        npc_manager.update(0.016)
