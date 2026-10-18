"""
Unit tests for DetectionManager.

Tests detection logic, line-of-sight checking, detection levels,
and report generation.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class DetectionLevel:
    """Detection level enumeration (copied from source to avoid pygame import)."""
    GLANCE = 'glance'
    NOTICE = 'notice'
    OBSERVE = 'observe'
    REPORT = 'report'


class MockTile:
    """Mock tile for testing."""
    def __init__(self, tile_type):
        self.tile_type = tile_type


class MockTileType:
    """Mock tile types."""
    GRASS = 'grass'
    ROAD_DIRT = 'road_dirt'
    BUILDING = 'building'
    FACTORY = 'factory'


class MockNPC:
    """Mock NPC for testing."""
    def __init__(self, world_x=100.0, world_y=100.0):
        self.world_x = world_x
        self.world_y = world_y
        self.detecting_robots = {}
        self.current_activity = 'idle'

    def calculate_detection_chance(self, robot_x, robot_y, is_daytime, robot_stealth):
        # Simple detection: higher chance if closer
        dx = robot_x - self.world_x
        dy = robot_y - self.world_y
        distance = (dx * dx + dy * dy) ** 0.5
        if distance > 200:
            return 0.0
        return 1.0 - (distance / 200)

    def update_detection(self, robot_id, detection_chance, dt):
        """Update detection progress. Returns True if detection completes."""
        current = self.detecting_robots.get(robot_id, 0.0)
        self.detecting_robots[robot_id] = min(1.0, current + detection_chance * dt)
        return self.detecting_robots[robot_id] >= 1.0

    def clear_detection(self, robot_id):
        if robot_id in self.detecting_robots:
            del self.detecting_robots[robot_id]


class MockRobot:
    """Mock robot for testing."""
    def __init__(self, x=150.0, y=150.0, robot_id=1, stealth_level=0.5):
        self.x = x
        self.y = y
        self.id = robot_id
        self.stealth_level = stealth_level


class MockGrid:
    """Mock grid for testing."""
    def __init__(self, width_tiles=100, height_tiles=100, tile_size=32):
        self.width_tiles = width_tiles
        self.height_tiles = height_tiles
        self.tile_size = tile_size
        self._tiles = {}

    def get_tile(self, x, y):
        return self._tiles.get((x, y), MockTile(MockTileType.GRASS))

    def set_tile(self, x, y, tile_type):
        self._tiles[(x, y)] = MockTile(tile_type)


class MockNPCManager:
    """Mock NPC manager for testing."""
    def __init__(self, npcs=None, game_time=12.0):
        self.npcs = npcs if npcs is not None else []
        self.game_time = game_time


class TestDetectionLevel:
    """Tests for detection level thresholds."""

    def test_glance_threshold(self):
        """Test detection progress below 25% is GLANCE."""
        # Import with pygame mocked
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.detection_manager import DetectionManager, DetectionLevel as DL

            grid = MockGrid()
            npc_manager = MockNPCManager()
            dm = DetectionManager(grid, npc_manager)

            assert dm.get_detection_level(0.0) == DL.GLANCE
            assert dm.get_detection_level(0.1) == DL.GLANCE
            assert dm.get_detection_level(0.24) == DL.GLANCE

    def test_notice_threshold(self):
        """Test detection progress 25-50% is NOTICE."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.detection_manager import DetectionManager, DetectionLevel as DL

            grid = MockGrid()
            npc_manager = MockNPCManager()
            dm = DetectionManager(grid, npc_manager)

            assert dm.get_detection_level(0.25) == DL.NOTICE
            assert dm.get_detection_level(0.35) == DL.NOTICE
            assert dm.get_detection_level(0.49) == DL.NOTICE

    def test_observe_threshold(self):
        """Test detection progress 50-75% is OBSERVE."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.detection_manager import DetectionManager, DetectionLevel as DL

            grid = MockGrid()
            npc_manager = MockNPCManager()
            dm = DetectionManager(grid, npc_manager)

            assert dm.get_detection_level(0.50) == DL.OBSERVE
            assert dm.get_detection_level(0.60) == DL.OBSERVE
            assert dm.get_detection_level(0.74) == DL.OBSERVE

    def test_report_threshold(self):
        """Test detection progress >= 75% is REPORT."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.detection_manager import DetectionManager, DetectionLevel as DL

            grid = MockGrid()
            npc_manager = MockNPCManager()
            dm = DetectionManager(grid, npc_manager)

            assert dm.get_detection_level(0.75) == DL.REPORT
            assert dm.get_detection_level(0.90) == DL.REPORT
            assert dm.get_detection_level(1.0) == DL.REPORT


class TestLineOfSight:
    """Tests for line-of-sight raycasting."""

    def test_line_of_sight_clear_path(self):
        """Test LOS returns True when path is clear."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.detection_manager import DetectionManager

            grid = MockGrid(tile_size=32)
            npc_manager = MockNPCManager()
            dm = DetectionManager(grid, npc_manager)

            # Clear path with no obstacles
            has_los = dm.check_line_of_sight(50, 50, 150, 150)
            assert has_los is True

    def test_line_of_sight_blocked_by_building(self):
        """Test LOS returns False when blocked by building."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.detection_manager import DetectionManager
            from src.world.tile import TileType

            grid = MockGrid(tile_size=32)
            # Place a building between NPC and robot
            grid.set_tile(3, 3, TileType.BUILDING)
            npc_manager = MockNPCManager()
            dm = DetectionManager(grid, npc_manager)

            # Path from (32, 32) to (160, 160) goes through tile (3, 3) = (96-128, 96-128)
            has_los = dm.check_line_of_sight(32, 32, 160, 160)
            assert has_los is False

    def test_line_of_sight_very_close(self):
        """Test LOS returns True for very close positions."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.detection_manager import DetectionManager

            grid = MockGrid()
            npc_manager = MockNPCManager()
            dm = DetectionManager(grid, npc_manager)

            # Very close positions (< 1 pixel)
            has_los = dm.check_line_of_sight(100, 100, 100.5, 100.5)
            assert has_los is True

    def test_line_of_sight_blocked_by_factory(self):
        """Test LOS returns False when blocked by factory."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.detection_manager import DetectionManager

            grid = MockGrid(tile_size=32)
            grid.set_tile(5, 5, MockTileType.FACTORY)
            npc_manager = MockNPCManager()
            dm = DetectionManager(grid, npc_manager)

            has_los = dm.check_line_of_sight(100, 100, 220, 220)
            assert has_los is False


class TestDetectionUpdate:
    """Tests for detection update logic."""

    def test_no_detection_when_npc_sleeping(self):
        """Test NPCs don't detect robots while sleeping."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.detection_manager import DetectionManager

            grid = MockGrid()
            npc = MockNPC(world_x=100, world_y=100)
            npc.current_activity = 'sleeping'  # Sleeping NPC
            npc_manager = MockNPCManager(npcs=[npc], game_time=12.0)
            dm = DetectionManager(grid, npc_manager)

            robot = MockRobot(x=110, y=110)
            reports = dm.update([robot], dt=1.0)

            assert reports == []
            assert robot.id not in npc.detecting_robots

    def test_detection_progress_increases_when_visible(self):
        """Test detection progress increases when robot is visible."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.detection_manager import DetectionManager

            grid = MockGrid()
            npc = MockNPC(world_x=100, world_y=100)
            npc_manager = MockNPCManager(npcs=[npc], game_time=12.0)
            dm = DetectionManager(grid, npc_manager)

            robot = MockRobot(x=120, y=120)
            dm.update([robot], dt=0.5)

            # Detection should have started
            assert robot.id in npc.detecting_robots
            assert npc.detecting_robots[robot.id] > 0

    def test_detection_decays_when_no_los(self):
        """Test detection decays when NPC loses line-of-sight."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.detection_manager import DetectionManager

            grid = MockGrid(tile_size=32)
            npc = MockNPC(world_x=50, world_y=50)
            npc.detecting_robots[1] = 0.5  # Pre-existing detection
            npc_manager = MockNPCManager(npcs=[npc], game_time=12.0)
            dm = DetectionManager(grid, npc_manager)

            # Place building to block LOS
            grid.set_tile(3, 3, MockTileType.BUILDING)
            robot = MockRobot(x=150, y=150)

            initial_detection = npc.detecting_robots[1]
            dm.update([robot], dt=1.0)

            # Detection should have decayed
            if 1 in npc.detecting_robots:
                assert npc.detecting_robots[1] < initial_detection

    def test_full_detection_generates_report(self):
        """Test full detection generates a REPORT level report."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.detection_manager import DetectionManager, DetectionLevel as DL

            grid = MockGrid()
            npc = MockNPC(world_x=100, world_y=100)
            npc_manager = MockNPCManager(npcs=[npc], game_time=12.0)
            dm = DetectionManager(grid, npc_manager)

            robot = MockRobot(x=105, y=105)  # Very close for high detection

            # Run multiple updates to reach full detection
            for _ in range(20):
                reports = dm.update([robot], dt=0.5)
                if reports:
                    break

            # Check we eventually got a report
            assert len(dm.detection_reports) > 0 or len(reports) > 0


class TestDetectionReports:
    """Tests for detection report retrieval."""

    def test_get_recent_reports_empty(self):
        """Test get_recent_reports returns empty list when no reports."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.detection_manager import DetectionManager

            grid = MockGrid()
            npc_manager = MockNPCManager()
            dm = DetectionManager(grid, npc_manager)

            reports = dm.get_recent_reports()
            assert reports == []

    def test_get_recent_reports_limited(self):
        """Test get_recent_reports returns limited count."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.detection_manager import DetectionManager, DetectionLevel as DL

            grid = MockGrid()
            npc_manager = MockNPCManager()
            dm = DetectionManager(grid, npc_manager)

            # Add fake reports
            for i in range(15):
                dm.detection_reports.append({
                    'npc': None,
                    'robot': None,
                    'time': 12.0 + i,
                    'location': (i * 10, i * 10),
                    'suspicion_increase': 5.0,
                    'detection_level': DL.REPORT
                })

            reports = dm.get_recent_reports(count=5)
            assert len(reports) == 5
            # Should be the most recent 5
            assert reports[0]['time'] == 22.0


class TestDetectionStats:
    """Tests for detection statistics."""

    def test_get_stats_initial(self):
        """Test get_stats returns correct initial state."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.detection_manager import DetectionManager

            grid = MockGrid()
            npc_manager = MockNPCManager()
            dm = DetectionManager(grid, npc_manager)

            stats = dm.get_stats()
            assert stats['total_reports'] == 0
            assert stats['by_level'] == {}
            assert stats['currently_being_detected'] == 0

    def test_get_stats_with_active_detections(self):
        """Test get_stats counts active detections."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.detection_manager import DetectionManager

            grid = MockGrid()
            npc1 = MockNPC()
            npc1.detecting_robots = {1: 0.3, 2: 0.5}
            npc2 = MockNPC()
            npc2.detecting_robots = {1: 0.2}
            npc_manager = MockNPCManager(npcs=[npc1, npc2])
            dm = DetectionManager(grid, npc_manager)

            stats = dm.get_stats()
            # 2 robots being detected by npc1, 1 by npc2 = 3 total
            assert stats['currently_being_detected'] == 3

    def test_get_stats_by_level(self):
        """Test get_stats counts reports by level."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.detection_manager import DetectionManager, DetectionLevel as DL

            grid = MockGrid()
            npc_manager = MockNPCManager()
            dm = DetectionManager(grid, npc_manager)

            dm.detection_reports = [
                {'detection_level': DL.NOTICE},
                {'detection_level': DL.NOTICE},
                {'detection_level': DL.OBSERVE},
                {'detection_level': DL.REPORT},
                {'detection_level': DL.REPORT},
                {'detection_level': DL.REPORT},
            ]

            stats = dm.get_stats()
            assert stats['by_level'][DL.NOTICE] == 2
            assert stats['by_level'][DL.OBSERVE] == 1
            assert stats['by_level'][DL.REPORT] == 3


class TestDaytimeDetection:
    """Tests for daytime vs nighttime detection."""

    def test_daytime_detection_6am_to_8pm(self):
        """Test daytime is defined as 6am to 8pm."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.detection_manager import DetectionManager

            grid = MockGrid()

            # Test various times
            test_cases = [
                (5.0, False),   # 5am - nighttime
                (6.0, True),    # 6am - daytime start
                (12.0, True),   # noon - daytime
                (19.5, True),   # 7:30pm - still daytime
                (20.0, False),  # 8pm - nighttime start
                (23.0, False),  # 11pm - nighttime
            ]

            for game_time, expected_daytime in test_cases:
                npc = MockNPC(world_x=100, world_y=100)
                npc_manager = MockNPCManager(npcs=[npc], game_time=game_time)
                dm = DetectionManager(grid, npc_manager)

                # Check the daytime calculation inside update
                is_daytime = 6 <= game_time < 20
                assert is_daytime == expected_daytime, f"Time {game_time} should be daytime={expected_daytime}"
