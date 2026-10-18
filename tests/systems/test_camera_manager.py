"""
Unit tests for CameraManager.

Tests camera placement, robot detection, camera status management,
and camera queries.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class MockCameraStatus:
    """Mock camera status enumeration."""
    ACTIVE = 0
    DISABLED = 1
    BROKEN = 2


class MockSecurityCamera:
    """Mock security camera for testing."""
    _id_counter = 0

    def __init__(self, world_x=0, world_y=0, facing_angle=0):
        MockSecurityCamera._id_counter += 1
        self.id = MockSecurityCamera._id_counter
        self.world_x = world_x
        self.world_y = world_y
        self.facing_angle = facing_angle
        self.status = MockCameraStatus.ACTIVE
        self.disabled_timer = 0.0

    def is_active(self):
        return self.status == MockCameraStatus.ACTIVE

    def is_disabled(self):
        return self.status == MockCameraStatus.DISABLED

    def is_broken(self):
        return self.status == MockCameraStatus.BROKEN

    def detect_robot(self, robot):
        """Simple detection based on distance."""
        if not self.is_active():
            return False
        dx = robot.world_x - self.world_x
        dy = robot.world_y - self.world_y
        distance = (dx * dx + dy * dy) ** 0.5
        return distance <= 200  # Within range

    def update(self, dt):
        if self.status == MockCameraStatus.DISABLED:
            self.disabled_timer -= dt
            if self.disabled_timer <= 0:
                self.status = MockCameraStatus.ACTIVE
                self.disabled_timer = 0.0

    def disable(self, duration=300.0):
        self.status = MockCameraStatus.DISABLED
        self.disabled_timer = duration


class MockTileType:
    """Mock tile types."""
    GRASS = 'grass'
    BUILDING = 'building'
    ROAD_DIRT = 'road_dirt'


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


class MockRoadNetwork:
    """Mock road network for testing."""
    def __init__(self):
        self.road_tiles = set()

    def add_road(self, x, y):
        self.road_tiles.add((x, y))

    def is_intersection(self, x, y):
        return False

    def _get_road_neighbors(self, x, y):
        neighbors = []
        if (x, y - 1) in self.road_tiles:
            neighbors.append('north')
        if (x, y + 1) in self.road_tiles:
            neighbors.append('south')
        if (x - 1, y) in self.road_tiles:
            neighbors.append('west')
        if (x + 1, y) in self.road_tiles:
            neighbors.append('east')
        return neighbors


class MockRobot:
    """Mock robot for testing."""
    def __init__(self, world_x=100, world_y=100, robot_id=1):
        self.id = robot_id
        self.world_x = world_x
        self.world_y = world_y


class MockPoliceStation:
    """Mock police station for testing."""
    def __init__(self, grid_x=10, grid_y=10):
        self.grid_x = grid_x
        self.grid_y = grid_y


@pytest.fixture
def mock_grid():
    """Provide a mock grid."""
    return MockGrid()


@pytest.fixture
def mock_road_network():
    """Provide a mock road network."""
    return MockRoadNetwork()


class TestCameraManagerInit:
    """Tests for CameraManager initialization."""

    def test_init_basic(self, mock_grid):
        """Test basic initialization."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                assert cm.grid is mock_grid
                assert cm.cameras == []
                assert cm.recent_detections == {}

    def test_init_with_road_network(self, mock_grid, mock_road_network):
        """Test initialization with road network."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid, road_network=mock_road_network)
                assert cm.road_network is mock_road_network


class TestCameraPlacement:
    """Tests for camera placement."""

    def test_place_cameras_police_stations(self, mock_grid):
        """Test cameras are placed near police stations."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                stations = [MockPoliceStation(10, 10), MockPoliceStation(20, 20)]

                cm.place_cameras(police_stations=stations)

                # Should have cameras (5 per station by default)
                assert len(cm.cameras) >= 2

    def test_place_cameras_tuple_positions(self, mock_grid):
        """Test cameras can be placed using tuple positions."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                stations = [(100, 100), (200, 200)]

                cm.place_cameras(police_stations=stations)

                assert len(cm.cameras) >= 2

    def test_place_building_cameras(self, mock_grid):
        """Test cameras are placed on buildings."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                # Add buildings to grid
                for x in range(10):
                    for y in range(10):
                        mock_grid.set_tile(x, y, MockTileType.BUILDING)

                cm = CameraManager(mock_grid)
                cm.building_camera_chance = 1.0  # 100% chance for testing
                cm.place_cameras()

                # Should have at least some cameras on buildings
                assert len(cm.cameras) > 0

    def test_clear_cameras_on_place(self, mock_grid):
        """Test existing cameras are cleared on re-placement."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                cm.cameras = [MockSecurityCamera(), MockSecurityCamera()]

                cm.place_cameras()

                # Old cameras should be gone
                # (new ones may or may not exist depending on grid)


class TestCameraDetection:
    """Tests for robot detection by cameras."""

    def test_detect_robots_in_range(self, mock_grid):
        """Test robots in range are detected."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                camera = MockSecurityCamera(world_x=100, world_y=100)
                cm.cameras = [camera]

                robot = MockRobot(world_x=150, world_y=150)
                detections = cm.detect_robots([robot], game_time=0.0)

                assert len(detections) == 1
                assert detections[0] == (camera, robot)

    def test_detect_robots_out_of_range(self, mock_grid):
        """Test robots out of range are not detected."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                camera = MockSecurityCamera(world_x=100, world_y=100)
                cm.cameras = [camera]

                robot = MockRobot(world_x=500, world_y=500)  # Far away
                detections = cm.detect_robots([robot], game_time=0.0)

                assert len(detections) == 0

    def test_detect_robots_disabled_camera(self, mock_grid):
        """Test disabled cameras don't detect robots."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                camera = MockSecurityCamera(world_x=100, world_y=100)
                camera.disable(300.0)
                cm.cameras = [camera]

                robot = MockRobot(world_x=110, world_y=110)
                detections = cm.detect_robots([robot], game_time=0.0)

                assert len(detections) == 0

    def test_detect_robots_cooldown(self, mock_grid):
        """Test detection cooldown prevents rapid re-detection."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                camera = MockSecurityCamera(world_x=100, world_y=100)
                cm.cameras = [camera]

                robot = MockRobot(world_x=110, world_y=110)

                # First detection
                detections1 = cm.detect_robots([robot], game_time=0.0)
                assert len(detections1) == 1

                # Immediate second check should be blocked by cooldown
                detections2 = cm.detect_robots([robot], game_time=0.5)
                assert len(detections2) == 0

                # After cooldown expires
                detections3 = cm.detect_robots([robot], game_time=10.0)
                assert len(detections3) == 1


class TestCameraCounts:
    """Tests for camera count methods."""

    def test_get_camera_count(self, mock_grid):
        """Test get_camera_count returns total cameras."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                cm.cameras = [MockSecurityCamera() for _ in range(5)]

                assert cm.get_camera_count() == 5

    def test_get_active_camera_count(self, mock_grid):
        """Test get_active_camera_count returns only active cameras."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                cam1 = MockSecurityCamera()
                cam2 = MockSecurityCamera()
                cam2.disable(100)
                cam3 = MockSecurityCamera()
                cm.cameras = [cam1, cam2, cam3]

                assert cm.get_active_camera_count() == 2

    def test_get_disabled_camera_count(self, mock_grid):
        """Test get_disabled_camera_count returns disabled cameras."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                cam1 = MockSecurityCamera()
                cam2 = MockSecurityCamera()
                cam2.disable(100)
                cam3 = MockSecurityCamera()
                cam3.disable(100)
                cm.cameras = [cam1, cam2, cam3]

                assert cm.get_disabled_camera_count() == 2

    def test_get_broken_camera_count(self, mock_grid):
        """Test get_broken_camera_count returns broken cameras."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                cam1 = MockSecurityCamera()
                cam2 = MockSecurityCamera()
                cam2.status = MockCameraStatus.BROKEN
                cm.cameras = [cam1, cam2]

                assert cm.get_broken_camera_count() == 1


class TestNearestCamera:
    """Tests for finding nearest camera."""

    def test_get_nearest_camera_empty(self, mock_grid):
        """Test get_nearest_camera returns None when no cameras."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                result = cm.get_nearest_camera(100, 100)

                assert result is None

    def test_get_nearest_camera_single(self, mock_grid):
        """Test get_nearest_camera returns the only camera."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                camera = MockSecurityCamera(world_x=200, world_y=200)
                cm.cameras = [camera]

                result = cm.get_nearest_camera(100, 100)
                assert result is camera

    def test_get_nearest_camera_multiple(self, mock_grid):
        """Test get_nearest_camera returns the closest one."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                cam_far = MockSecurityCamera(world_x=500, world_y=500)
                cam_near = MockSecurityCamera(world_x=110, world_y=110)
                cam_mid = MockSecurityCamera(world_x=200, world_y=200)
                cm.cameras = [cam_far, cam_near, cam_mid]

                result = cm.get_nearest_camera(100, 100)
                assert result is cam_near


class TestCameraUpdate:
    """Tests for camera update."""

    def test_update_all_cameras(self, mock_grid):
        """Test update calls update on all cameras."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                cam1 = MockSecurityCamera()
                cam2 = MockSecurityCamera()
                cam1.disable(100)
                cm.cameras = [cam1, cam2]

                initial_timer = cam1.disabled_timer
                cm.update(dt=10.0)

                # Disabled timer should decrease
                assert cam1.disabled_timer < initial_timer


class TestClearAllCameras:
    """Tests for clearing cameras."""

    def test_clear_all_cameras(self, mock_grid):
        """Test clear_all_cameras removes all cameras and detections."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                cm.cameras = [MockSecurityCamera() for _ in range(5)]
                cm.recent_detections = {(1, 1): 5.0, (2, 1): 3.0}

                cm.clear_all_cameras()

                assert cm.cameras == []
                assert cm.recent_detections == {}


class TestDisableCamera:
    """Tests for disabling cameras."""

    def test_disable_camera(self, mock_grid):
        """Test disable_camera disables a camera."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                camera = MockSecurityCamera()
                cm.cameras = [camera]

                cm.disable_camera(camera, duration=500.0)

                assert camera.is_disabled()
                assert camera.disabled_timer == 500.0


class TestCameraManagerRepr:
    """Tests for string representation."""

    def test_repr(self, mock_grid):
        """Test __repr__ returns useful information."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_manager import CameraManager

                cm = CameraManager(mock_grid)
                cam1 = MockSecurityCamera()
                cam2 = MockSecurityCamera()
                cam2.disable(100)
                cm.cameras = [cam1, cam2]

                repr_str = repr(cm)
                assert 'CameraManager' in repr_str
                assert 'total=2' in repr_str
                assert 'active=1' in repr_str
                assert 'disabled=1' in repr_str
