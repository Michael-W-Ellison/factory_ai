"""
Unit tests for PoliceManager.

Tests police patrol spawning, route generation, presence adjustments,
detection responses, and robot capture mechanics.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class MockPoliceBehavior:
    """Mock police behavior enumeration."""
    PATROL = 'patrol'
    INVESTIGATE = 'investigate'
    CHASE = 'chase'
    CAPTURE = 'capture'


class MockPoliceOfficer:
    """Mock police officer for testing."""
    _id_counter = 0

    def __init__(self, world_x=0, world_y=0, patrol_route=None):
        MockPoliceOfficer._id_counter += 1
        self.id = MockPoliceOfficer._id_counter
        self.world_x = world_x
        self.world_y = world_y
        self.patrol_route = patrol_route or []
        self.current_waypoint = 0
        self.behavior = MockPoliceBehavior.PATROL
        self.chase_target = None
        self.investigation_location = None

    def update(self, dt, game_time):
        pass

    def start_chase(self, target):
        self.behavior = MockPoliceBehavior.CHASE
        self.chase_target = target

    def start_investigation(self, location):
        self.behavior = MockPoliceBehavior.INVESTIGATE
        self.investigation_location = location


class MockDetectionLevel:
    """Mock detection level enumeration."""
    GLANCE = 'glance'
    NOTICE = 'notice'
    OBSERVE = 'observe'
    REPORT = 'report'


class MockTileType:
    """Mock tile types."""
    GRASS = 'grass'
    ROAD_DIRT = 'road_dirt'
    ROAD_TAR = 'road_tar'
    ROAD_ASPHALT = 'road_asphalt'
    BUILDING = 'building'


class MockTile:
    """Mock tile for testing."""
    def __init__(self, tile_type=MockTileType.GRASS):
        self.tile_type = tile_type


class MockGrid:
    """Mock grid for testing."""
    def __init__(self, width_tiles=50, height_tiles=50, tile_size=32):
        self.width_tiles = width_tiles
        self.height_tiles = height_tiles
        self.tile_size = tile_size
        self._tiles = {}

    def get_tile(self, x, y):
        return self._tiles.get((x, y), MockTile(MockTileType.GRASS))

    def set_tile(self, x, y, tile_type):
        self._tiles[(x, y)] = MockTile(tile_type)


class MockSuspicionManager:
    """Mock suspicion manager for testing."""
    def __init__(self, suspicion_level=0.0):
        self.suspicion_level = suspicion_level


class MockRobot:
    """Mock robot for testing."""
    def __init__(self, robot_id=1):
        self.id = robot_id


@pytest.fixture
def mock_grid():
    """Provide a mock grid with some roads."""
    grid = MockGrid(width_tiles=30, height_tiles=30, tile_size=32)
    # Add a horizontal road
    for x in range(30):
        grid.set_tile(x, 15, MockTileType.ROAD_DIRT)
    # Add a vertical road
    for y in range(30):
        grid.set_tile(15, y, MockTileType.ROAD_TAR)
    return grid


@pytest.fixture
def mock_suspicion_manager():
    """Provide a mock suspicion manager."""
    return MockSuspicionManager()


class TestPoliceManagerInit:
    """Tests for PoliceManager initialization."""

    def test_init_basic(self, mock_grid, mock_suspicion_manager):
        """Test basic initialization."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager

                    pm = PoliceManager(mock_grid, mock_suspicion_manager)

                    assert pm.grid is mock_grid
                    assert pm.suspicion_manager is mock_suspicion_manager
                    assert pm.police_officers == []
                    assert pm.base_patrol_count == 2
                    assert pm.officers_per_patrol == 2


class TestPatrolRouteGeneration:
    """Tests for patrol route generation."""

    def test_generate_patrol_routes_with_roads(self, mock_grid, mock_suspicion_manager):
        """Test patrol routes are generated along roads."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager
                    import random

                    pm = PoliceManager(mock_grid, mock_suspicion_manager)
                    rng = random.Random(42)

                    routes = pm._generate_patrol_routes(rng, count=2)

                    assert len(routes) == 2
                    for route in routes:
                        assert len(route) >= 2  # At least start and one waypoint

    def test_generate_patrol_routes_no_roads(self, mock_suspicion_manager):
        """Test patrol route generation with no roads returns empty."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager
                    import random

                    grid = MockGrid()  # No roads
                    pm = PoliceManager(grid, mock_suspicion_manager)
                    rng = random.Random(42)

                    routes = pm._generate_patrol_routes(rng, count=2)

                    assert routes == []


class TestSpawnPatrols:
    """Tests for spawning police patrols."""

    def test_spawn_initial_patrols(self, mock_grid, mock_suspicion_manager):
        """Test initial patrol spawning."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager

                    pm = PoliceManager(mock_grid, mock_suspicion_manager)
                    pm.spawn_initial_patrols(seed=42)

                    # Should have base_patrol_count * officers_per_patrol officers
                    expected = pm.base_patrol_count * pm.officers_per_patrol
                    assert len(pm.police_officers) == expected

    def test_spawn_patrol_empty_route(self, mock_grid, mock_suspicion_manager):
        """Test spawn_patrol with empty route does nothing."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager
                    import random

                    pm = PoliceManager(mock_grid, mock_suspicion_manager)
                    rng = random.Random(42)

                    pm._spawn_patrol([], rng)

                    assert pm.police_officers == []


class TestPolicePresenceUpdate:
    """Tests for police presence adjustment based on suspicion."""

    def test_normal_suspicion_base_patrols(self, mock_grid, mock_suspicion_manager):
        """Test normal suspicion level has base patrols."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager

                    mock_suspicion_manager.suspicion_level = 10  # Normal
                    pm = PoliceManager(mock_grid, mock_suspicion_manager)
                    pm.spawn_initial_patrols(seed=42)

                    initial_count = len(pm.police_officers)
                    pm.update_police_presence()

                    assert len(pm.police_officers) == initial_count

    def test_rumors_suspicion_adds_patrol(self, mock_grid, mock_suspicion_manager):
        """Test rumors tier adds a patrol."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager

                    mock_suspicion_manager.suspicion_level = 30  # Rumors
                    pm = PoliceManager(mock_grid, mock_suspicion_manager)
                    pm.spawn_initial_patrols(seed=42)

                    initial_count = len(pm.police_officers)
                    pm.update_police_presence()

                    # Should have added officers
                    assert len(pm.police_officers) > initial_count

    def test_investigation_suspicion_adds_patrols(self, mock_grid, mock_suspicion_manager):
        """Test investigation tier adds more patrols."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager

                    mock_suspicion_manager.suspicion_level = 50  # Investigation
                    pm = PoliceManager(mock_grid, mock_suspicion_manager)
                    pm.spawn_initial_patrols(seed=42)

                    initial_count = len(pm.police_officers)
                    pm.update_police_presence()

                    # Should have added 2 patrols worth
                    assert len(pm.police_officers) >= initial_count + 2

    def test_high_suspicion_max_patrols(self, mock_grid, mock_suspicion_manager):
        """Test maximum suspicion has maximum patrols."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager

                    mock_suspicion_manager.suspicion_level = 90  # Restrictions
                    pm = PoliceManager(mock_grid, mock_suspicion_manager)
                    pm.spawn_initial_patrols(seed=42)

                    pm.update_police_presence()

                    # Should have base + 4 patrols
                    expected_patrols = pm.base_patrol_count + 4
                    expected_officers = expected_patrols * pm.officers_per_patrol
                    assert len(pm.police_officers) == expected_officers

    def test_suspicion_decrease_removes_patrols(self, mock_grid, mock_suspicion_manager):
        """Test low suspicion removes extra patrols."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager

                    # Start with high suspicion
                    mock_suspicion_manager.suspicion_level = 50
                    pm = PoliceManager(mock_grid, mock_suspicion_manager)
                    pm.spawn_initial_patrols(seed=42)
                    pm.update_police_presence()

                    high_count = len(pm.police_officers)

                    # Lower suspicion
                    mock_suspicion_manager.suspicion_level = 10
                    pm.update_police_presence()

                    # Should have fewer officers
                    assert len(pm.police_officers) < high_count


class TestPoliceUpdate:
    """Tests for police officer updates."""

    def test_update_calls_officer_update(self, mock_grid, mock_suspicion_manager):
        """Test update calls update on all officers."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager

                    pm = PoliceManager(mock_grid, mock_suspicion_manager)
                    officer1 = MockPoliceOfficer()
                    officer2 = MockPoliceOfficer()
                    pm.police_officers = [officer1, officer2]

                    # This should not raise
                    pm.update(dt=0.5, game_time=12.0)


class TestDetectionReportHandling:
    """Tests for handling detection reports."""

    def test_handle_report_level_dispatches_officer(self, mock_grid, mock_suspicion_manager):
        """Test REPORT level detection dispatches nearest officer."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager

                    pm = PoliceManager(mock_grid, mock_suspicion_manager)
                    officer = MockPoliceOfficer(world_x=100, world_y=100)
                    pm.police_officers = [officer]

                    robot = MockRobot()
                    report = {
                        'detection_level': MockDetectionLevel.REPORT,
                        'location': (120, 120),
                        'robot': robot,
                    }

                    pm.handle_detection_report(report)

                    assert officer.behavior == MockPoliceBehavior.CHASE
                    assert officer.chase_target is robot

    def test_handle_report_no_robot_investigates_location(self, mock_grid, mock_suspicion_manager):
        """Test REPORT without robot reference investigates location."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager

                    pm = PoliceManager(mock_grid, mock_suspicion_manager)
                    officer = MockPoliceOfficer(world_x=100, world_y=100)
                    pm.police_officers = [officer]

                    report = {
                        'detection_level': MockDetectionLevel.REPORT,
                        'location': (120, 120),
                    }

                    pm.handle_detection_report(report)

                    assert officer.behavior == MockPoliceBehavior.INVESTIGATE
                    assert officer.investigation_location == (120, 120)

    def test_handle_report_officer_too_far(self, mock_grid, mock_suspicion_manager):
        """Test report is ignored if officer is too far."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager

                    pm = PoliceManager(mock_grid, mock_suspicion_manager)
                    officer = MockPoliceOfficer(world_x=1000, world_y=1000)  # Far away
                    pm.police_officers = [officer]

                    report = {
                        'detection_level': MockDetectionLevel.REPORT,
                        'location': (100, 100),
                        'robot': MockRobot(),
                    }

                    pm.handle_detection_report(report)

                    # Officer should not respond (>500 pixels away)
                    assert officer.behavior == MockPoliceBehavior.PATROL

    def test_handle_report_low_level_ignored(self, mock_grid, mock_suspicion_manager):
        """Test non-REPORT level detections are ignored."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager

                    pm = PoliceManager(mock_grid, mock_suspicion_manager)
                    officer = MockPoliceOfficer(world_x=100, world_y=100)
                    pm.police_officers = [officer]

                    report = {
                        'detection_level': MockDetectionLevel.NOTICE,
                        'location': (120, 120),
                        'robot': MockRobot(),
                    }

                    pm.handle_detection_report(report)

                    assert officer.behavior == MockPoliceBehavior.PATROL


class TestCaptureChecks:
    """Tests for robot capture checks."""

    def test_check_captures_finds_captured(self, mock_grid, mock_suspicion_manager):
        """Test check_captures finds captured robots."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager

                    pm = PoliceManager(mock_grid, mock_suspicion_manager)
                    robot = MockRobot()
                    officer = MockPoliceOfficer()
                    officer.behavior = MockPoliceBehavior.CAPTURE
                    officer.chase_target = robot
                    pm.police_officers = [officer]

                    captured = pm.check_captures([robot])

                    assert robot in captured

    def test_check_captures_no_captures(self, mock_grid, mock_suspicion_manager):
        """Test check_captures returns empty when no captures."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager

                    pm = PoliceManager(mock_grid, mock_suspicion_manager)
                    robot = MockRobot()
                    officer = MockPoliceOfficer()
                    officer.behavior = MockPoliceBehavior.PATROL
                    pm.police_officers = [officer]

                    captured = pm.check_captures([robot])

                    assert captured == []


class TestPoliceStats:
    """Tests for police statistics."""

    def test_get_stats_empty(self, mock_grid, mock_suspicion_manager):
        """Test get_stats with no officers."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager

                    pm = PoliceManager(mock_grid, mock_suspicion_manager)

                    stats = pm.get_stats()

                    assert stats['total_officers'] == 0
                    assert stats['patrol_count'] == 0
                    assert stats['by_behavior'] == {}

    def test_get_stats_with_officers(self, mock_grid, mock_suspicion_manager):
        """Test get_stats counts officers by behavior."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.police_manager.PoliceOfficer', MockPoliceOfficer):
                with patch('src.systems.police_manager.PoliceBehavior', MockPoliceBehavior):
                    from src.systems.police_manager import PoliceManager

                    pm = PoliceManager(mock_grid, mock_suspicion_manager)
                    off1 = MockPoliceOfficer()
                    off1.behavior = MockPoliceBehavior.PATROL
                    off2 = MockPoliceOfficer()
                    off2.behavior = MockPoliceBehavior.PATROL
                    off3 = MockPoliceOfficer()
                    off3.behavior = MockPoliceBehavior.CHASE
                    off4 = MockPoliceOfficer()
                    off4.behavior = MockPoliceBehavior.INVESTIGATE
                    pm.police_officers = [off1, off2, off3, off4]

                    stats = pm.get_stats()

                    assert stats['total_officers'] == 4
                    assert stats['patrol_count'] == 2  # 4 // 2
                    assert stats['by_behavior'][MockPoliceBehavior.PATROL] == 2
                    assert stats['by_behavior'][MockPoliceBehavior.CHASE] == 1
                    assert stats['by_behavior'][MockPoliceBehavior.INVESTIGATE] == 1
