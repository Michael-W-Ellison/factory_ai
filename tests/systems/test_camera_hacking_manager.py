"""
Unit tests for CameraHackingManager.

Tests camera hacking mechanics, progress tracking, consequences,
and research integration.
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

    def disable(self, duration=300.0):
        self.status = MockCameraStatus.DISABLED
        self.disabled_timer = duration


class MockCameraManager:
    """Mock camera manager for testing."""
    def __init__(self):
        self.cameras = []
        self.grid = MockGrid()

    def get_disabled_camera_count(self):
        return sum(1 for c in self.cameras if c.is_disabled())

    def disable_camera(self, camera, duration):
        camera.disable(duration)


class MockGrid:
    """Mock grid for testing."""
    def __init__(self, width_tiles=50, height_tiles=50, tile_size=32):
        self.width_tiles = width_tiles
        self.height_tiles = height_tiles
        self.tile_size = tile_size


class MockResearchManager:
    """Mock research manager for testing."""
    def __init__(self):
        self.completed_research = set()
        self.active_effects = {}

    def is_completed(self, research_id):
        return research_id in self.completed_research

    def complete_research(self, research_id):
        self.completed_research.add(research_id)


class MockSuspicionManager:
    """Mock suspicion manager for testing."""
    def __init__(self):
        self.suspicion_level = 0.0
        self.history = []

    def add_suspicion(self, amount, reason=""):
        self.suspicion_level = max(0, min(100, self.suspicion_level + amount))
        self.history.append((amount, reason))


class MockFBIManager:
    """Mock FBI manager for testing."""
    def __init__(self):
        self.reports = []

    def report_camera_hacks(self, hack_count, game_time):
        self.reports.append({'hack_count': hack_count, 'game_time': game_time})


@pytest.fixture
def mock_camera_manager():
    """Provide a mock camera manager with cameras."""
    cm = MockCameraManager()
    cm.cameras = [
        MockSecurityCamera(world_x=100, world_y=100),
        MockSecurityCamera(world_x=200, world_y=200),
        MockSecurityCamera(world_x=300, world_y=300),
    ]
    return cm


@pytest.fixture
def mock_research_manager():
    """Provide a mock research manager."""
    return MockResearchManager()


@pytest.fixture
def mock_suspicion_manager():
    """Provide a mock suspicion manager."""
    return MockSuspicionManager()


@pytest.fixture
def mock_fbi_manager():
    """Provide a mock FBI manager."""
    return MockFBIManager()


class TestCameraHackingManagerInit:
    """Tests for CameraHackingManager initialization."""

    def test_init_basic(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test basic initialization."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)

            assert chm.camera_manager is mock_camera_manager
            assert chm.research is mock_research_manager
            assert chm.suspicion is mock_suspicion_manager
            assert chm.hacking_enabled is False
            assert chm.total_hacks == 0
            assert chm.currently_hacking is False

    def test_init_with_fbi_manager(self, mock_camera_manager, mock_research_manager,
                                    mock_suspicion_manager, mock_fbi_manager):
        """Test initialization with FBI manager."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            chm = CameraHackingManager(
                mock_camera_manager, mock_research_manager,
                mock_suspicion_manager, fbi_manager=mock_fbi_manager
            )

            assert chm.fbi is mock_fbi_manager


class TestResearchIntegration:
    """Tests for research-based capability updates."""

    def test_hacking_disabled_without_research(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test hacking is disabled without research."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
            chm.update_from_research()

            assert chm.hacking_enabled is False

    def test_hacking_enabled_with_research(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test hacking is enabled with camera_hacking_1 research."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            mock_research_manager.complete_research("camera_hacking_1")

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
            chm.update_from_research()

            assert chm.hacking_enabled is True

    def test_hack_count_increases_with_research(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test hack count limit increases with higher research tiers."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            mock_research_manager.complete_research("camera_hacking_1")
            mock_research_manager.complete_research("camera_hacking_2")
            mock_research_manager.complete_research("camera_hacking_3")

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
            chm.update_from_research()

            assert chm.hack_count_limit == 3

    def test_hack_duration_from_research(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test hack duration is read from research effects."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            mock_research_manager.complete_research("camera_hacking_1")
            mock_research_manager.active_effects = {"camera_hack_duration": 600.0}

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
            chm.update_from_research()

            assert chm.hack_duration == 600.0


class TestHackClick:
    """Tests for handling hack clicks."""

    def test_handle_click_hacking_disabled(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test click is ignored when hacking is disabled."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)

            result = chm.handle_click(100, 100, game_time=0.0)

            assert result is False

    def test_handle_click_starts_hacking(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test clicking on camera starts hacking."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            mock_research_manager.complete_research("camera_hacking_1")

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
            chm.update_from_research()

            result = chm.handle_click(100, 100, game_time=0.0)

            assert result is True
            assert chm.currently_hacking is True
            assert chm.hack_target is not None

    def test_handle_click_no_camera_at_position(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test click on empty area does nothing."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            mock_research_manager.complete_research("camera_hacking_1")

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
            chm.update_from_research()

            result = chm.handle_click(500, 500, game_time=0.0)  # Far from cameras

            assert result is False
            assert chm.currently_hacking is False

    def test_handle_click_already_hacking(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test click is ignored when already hacking."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            mock_research_manager.complete_research("camera_hacking_1")

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
            chm.update_from_research()
            chm.currently_hacking = True
            chm.hack_target = mock_camera_manager.cameras[0]

            result = chm.handle_click(200, 200, game_time=0.0)

            assert result is False

    def test_handle_click_camera_already_disabled(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test clicking on disabled camera does nothing."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            mock_research_manager.complete_research("camera_hacking_1")
            mock_camera_manager.cameras[0].disable(100)

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
            chm.update_from_research()

            result = chm.handle_click(100, 100, game_time=0.0)

            assert result is False

    def test_handle_click_hack_limit_reached(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test click is blocked when hack limit reached."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            mock_research_manager.complete_research("camera_hacking_1")
            mock_camera_manager.cameras[0].disable(100)  # Already at limit (1)

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
            chm.update_from_research()

            result = chm.handle_click(200, 200, game_time=0.0)

            assert result is False


class TestHackingProgress:
    """Tests for hacking progress mechanics."""

    def test_hack_progress_increases(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test hacking progress increases over time."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            mock_research_manager.complete_research("camera_hacking_1")

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
            chm.update_from_research()
            chm.handle_click(100, 100, game_time=0.0)

            initial_progress = chm.hack_progress
            chm.update(dt=1.0, game_time=1.0)

            assert chm.hack_progress > initial_progress

    def test_hack_completes_after_required_time(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test hacking completes after required time."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            mock_research_manager.complete_research("camera_hacking_1")

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
            chm.update_from_research()
            chm.handle_click(100, 100, game_time=0.0)

            target = chm.hack_target

            # Update past the required time
            chm.update(dt=5.0, game_time=5.0)

            assert chm.currently_hacking is False
            assert target.is_disabled()
            assert chm.total_hacks == 1

    def test_get_hack_progress_percent(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test get_hack_progress_percent returns correct value."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            mock_research_manager.complete_research("camera_hacking_1")

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
            chm.update_from_research()
            chm.handle_click(100, 100, game_time=0.0)

            # Set progress to half
            chm.hack_progress = chm.hack_time_required / 2

            assert chm.get_hack_progress_percent() == 50.0

    def test_get_hack_progress_percent_not_hacking(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test get_hack_progress_percent returns 0 when not hacking."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)

            assert chm.get_hack_progress_percent() == 0.0


class TestCancelHack:
    """Tests for cancelling hacks."""

    def test_cancel_hack(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test cancel_hack stops hacking."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            mock_research_manager.complete_research("camera_hacking_1")

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
            chm.update_from_research()
            chm.handle_click(100, 100, game_time=0.0)

            chm.cancel_hack()

            assert chm.currently_hacking is False
            assert chm.hack_target is None
            assert chm.hack_progress == 0.0


class TestSuspicionIncrease:
    """Tests for suspicion increase on hacking."""

    def test_hacking_adds_suspicion(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test completing a hack adds suspicion."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            mock_research_manager.complete_research("camera_hacking_1")

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
            chm.update_from_research()
            chm.handle_click(100, 100, game_time=0.0)

            initial_suspicion = mock_suspicion_manager.suspicion_level
            chm.update(dt=5.0, game_time=5.0)  # Complete hack

            assert mock_suspicion_manager.suspicion_level > initial_suspicion
            assert len(mock_suspicion_manager.history) > 0


class TestSecurityUpgrade:
    """Tests for security upgrade consequence."""

    def test_security_upgrade_trigger(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test security upgrade triggers after threshold hacks."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            mock_research_manager.complete_research("camera_hacking_1")

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
            chm.update_from_research()
            chm.hack_count_limit = 100  # Allow many hacks

            # Perform enough hacks to trigger upgrade
            for i in range(11):
                camera = MockSecurityCamera(world_x=50 + i * 25, world_y=100)
                mock_camera_manager.cameras.append(camera)
                # Set hack_target before calling _complete_hack
                chm.hack_target = camera
                chm._complete_hack(game_time=float(i))

            assert chm.security_upgrade_triggered is True

    def test_security_upgrade_adds_cameras(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test security upgrade adds new cameras."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            with patch('src.systems.camera_hacking_manager.SecurityCamera', MockSecurityCamera):
                from src.systems.camera_hacking_manager import CameraHackingManager

                mock_research_manager.complete_research("camera_hacking_1")

                chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
                chm.update_from_research()
                chm.total_hacks = 10  # Just below threshold

                initial_camera_count = len(mock_camera_manager.cameras)

                chm._trigger_security_upgrade()

                assert len(mock_camera_manager.cameras) > initial_camera_count


class TestFBIInvestigation:
    """Tests for FBI investigation consequence."""

    def test_fbi_investigation_trigger(self, mock_camera_manager, mock_research_manager,
                                        mock_suspicion_manager, mock_fbi_manager):
        """Test FBI investigation triggers after threshold hacks."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            mock_research_manager.complete_research("camera_hacking_1")

            chm = CameraHackingManager(
                mock_camera_manager, mock_research_manager,
                mock_suspicion_manager, fbi_manager=mock_fbi_manager
            )
            chm.update_from_research()
            chm.total_hacks = 20

            chm._check_consequences(game_time=10.0)

            assert chm.fbi_investigation_triggered is True
            assert len(mock_fbi_manager.reports) > 0

    def test_fbi_investigation_adds_suspicion(self, mock_camera_manager, mock_research_manager,
                                              mock_suspicion_manager, mock_fbi_manager):
        """Test FBI investigation adds significant suspicion."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            chm = CameraHackingManager(
                mock_camera_manager, mock_research_manager,
                mock_suspicion_manager, fbi_manager=mock_fbi_manager
            )
            chm.total_hacks = 20

            initial_suspicion = mock_suspicion_manager.suspicion_level

            chm._trigger_fbi_investigation(game_time=10.0)

            assert mock_suspicion_manager.suspicion_level >= initial_suspicion + 30


class TestCanHackCameras:
    """Tests for can_hack_cameras check."""

    def test_can_hack_cameras_enabled_and_available(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test can_hack_cameras returns True when enabled and slots available."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            mock_research_manager.complete_research("camera_hacking_1")

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
            chm.update_from_research()

            assert chm.can_hack_cameras() is True

    def test_can_hack_cameras_disabled(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test can_hack_cameras returns False when disabled."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)

            assert chm.can_hack_cameras() is False

    def test_can_hack_cameras_limit_reached(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test can_hack_cameras returns False when limit reached."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            mock_research_manager.complete_research("camera_hacking_1")
            mock_camera_manager.cameras[0].disable(100)

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
            chm.update_from_research()

            assert chm.can_hack_cameras() is False


class TestRepr:
    """Tests for string representation."""

    def test_repr(self, mock_camera_manager, mock_research_manager, mock_suspicion_manager):
        """Test __repr__ returns useful information."""
        with patch.dict('sys.modules', {'pygame': MagicMock()}):
            from src.systems.camera_hacking_manager import CameraHackingManager

            chm = CameraHackingManager(mock_camera_manager, mock_research_manager, mock_suspicion_manager)
            chm.hacking_enabled = True
            chm.total_hacks = 5
            chm.hack_count_limit = 2

            repr_str = repr(chm)

            assert 'CameraHackingManager' in repr_str
            assert 'enabled=True' in repr_str
            assert 'total_hacks=5' in repr_str
            assert 'limit=2' in repr_str
