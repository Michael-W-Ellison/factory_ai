"""
Comprehensive test suite for Phase 8.1: Camera System.

Tests:
- SecurityCamera creation and properties
- Vision cone detection
- Camera status changes (active, disabled, broken)
- CameraManager placement
- Robot detection through cameras
"""

import sys
import os
import math

# Add parent directory to path
if os.path.basename(os.getcwd()) == 'src':
    sys.path.insert(0, '..')
else:
    sys.path.insert(0, 'src')

from src.world.grid import Grid
from src.world.tile import TileType
from src.systems.road_network import RoadNetwork
from src.entities.security_camera import SecurityCamera, CameraStatus
from src.systems.camera_manager import CameraManager


class MockRobot:
    """Mock robot for testing detection."""
    def __init__(self, world_x, world_y):
        self.world_x = world_x
        self.world_y = world_y
        self.id = id(self)


def test_camera_creation():
    """Test SecurityCamera creation and properties."""
    print("Test: SecurityCamera Creation")

    camera = SecurityCamera(world_x=100.0, world_y=200.0, facing_angle=90)

    assert camera.world_x == 100.0, "World X should be 100.0"
    assert camera.world_y == 200.0, "World Y should be 200.0"
    assert camera.facing_angle == 90, "Facing angle should be 90"
    assert camera.vision_range == 200.0, "Vision range should be 200"
    assert camera.vision_angle == 90.0, "Vision angle should be 90"
    assert camera.is_active(), "Camera should start active"
    assert not camera.is_disabled(), "Camera should not be disabled"
    assert not camera.is_broken(), "Camera should not be broken"

    print(f"  ✓ Camera created at ({camera.world_x}, {camera.world_y})")
    print(f"  ✓ Facing: {camera.facing_angle}°, Range: {camera.vision_range}px")
    print(f"  ✓ Status: {camera.get_status_string()}")


def test_vision_cone_detection():
    """Test vision cone point detection."""
    print("\nTest: Vision Cone Detection")

    # Camera at origin facing east (0 degrees)
    camera = SecurityCamera(world_x=0.0, world_y=0.0, facing_angle=0)

    # Point directly in front (should be detected)
    assert camera.is_point_in_vision_cone(100, 0), \
        "Point directly in front should be detected"

    # Point at 45 degrees (within 90 degree cone)
    assert camera.is_point_in_vision_cone(100, 100), \
        "Point at 45° should be detected"

    # Point at -45 degrees (within 90 degree cone)
    assert camera.is_point_in_vision_cone(100, -100), \
        "Point at -45° should be detected"

    # Point behind camera (should not be detected)
    assert not camera.is_point_in_vision_cone(-100, 0), \
        "Point behind camera should not be detected"

    # Point too far (outside range)
    assert not camera.is_point_in_vision_cone(300, 0), \
        "Point beyond range should not be detected"

    print(f"  ✓ Points in front detected correctly")
    print(f"  ✓ Points at ±45° detected (within 90° cone)")
    print(f"  ✓ Points behind camera not detected")
    print(f"  ✓ Points beyond range not detected")


def test_camera_status_changes():
    """Test camera status transitions."""
    print("\nTest: Camera Status Changes")

    camera = SecurityCamera(world_x=0.0, world_y=0.0)

    # Start active
    assert camera.is_active(), "Should start active"

    # Disable camera
    camera.disable(duration=10.0)
    assert camera.is_disabled(), "Should be disabled"
    assert camera.disabled_timer == 10.0, "Timer should be set"

    # Update camera (time passes)
    camera.update(5.0)
    assert camera.disabled_timer == 5.0, "Timer should decrease"
    assert camera.is_disabled(), "Should still be disabled"

    # Timer expires
    camera.update(5.0)
    assert camera.is_active(), "Should re-activate after timer expires"

    # Break camera
    camera.break_camera()
    assert camera.is_broken(), "Should be broken"

    # Try to disable broken camera (should not work)
    camera.disable()
    assert camera.is_broken(), "Broken camera should stay broken"

    # Repair camera
    camera.repair()
    assert camera.is_active(), "Should be active after repair"

    print(f"  ✓ Camera can be disabled temporarily")
    print(f"  ✓ Disabled timer counts down correctly")
    print(f"  ✓ Camera re-activates after timer expires")
    print(f"  ✓ Camera can be broken and repaired")


def test_robot_detection():
    """Test robot detection by camera."""
    print("\nTest: Robot Detection")

    camera = SecurityCamera(world_x=0.0, world_y=0.0, facing_angle=0)

    # Robot in front of camera
    robot_in_view = MockRobot(world_x=100.0, world_y=0.0)
    assert camera.detect_robot(robot_in_view), \
        "Robot in front should be detected"

    # Robot behind camera
    robot_behind = MockRobot(world_x=-100.0, world_y=0.0)
    assert not camera.detect_robot(robot_behind), \
        "Robot behind should not be detected"

    # Robot out of range
    robot_far = MockRobot(world_x=300.0, world_y=0.0)
    assert not camera.detect_robot(robot_far), \
        "Robot out of range should not be detected"

    # Disable camera
    camera.disable()

    # Robot should not be detected when camera disabled
    assert not camera.detect_robot(robot_in_view), \
        "Disabled camera should not detect robot"

    print(f"  ✓ Robot in view detected")
    print(f"  ✓ Robot behind camera not detected")
    print(f"  ✓ Robot out of range not detected")
    print(f"  ✓ Disabled camera does not detect")


def test_camera_manager_creation():
    """Test CameraManager creation."""
    print("\nTest: CameraManager Creation")

    grid = Grid(width_tiles=50, height_tiles=50)
    road_network = RoadNetwork(grid)

    camera_mgr = CameraManager(grid, road_network)

    assert camera_mgr.grid == grid, "Should have grid reference"
    assert camera_mgr.road_network == road_network, "Should have road network reference"
    assert camera_mgr.get_camera_count() == 0, "Should start with 0 cameras"

    print(f"  ✓ CameraManager created")
    print(f"  ✓ Initial camera count: {camera_mgr.get_camera_count()}")


def test_camera_placement():
    """Test camera placement in city."""
    print("\nTest: Camera Placement")

    grid = Grid(width_tiles=50, height_tiles=50)

    # Create some roads
    for x in range(10, 40):
        tile = grid.get_tile(x, 25)
        tile.tile_type = TileType.ROAD_ASPHALT

    # Create some buildings
    for y in range(10, 15):
        for x in range(15, 20):
            tile = grid.get_tile(x, y)
            tile.tile_type = TileType.BUILDING

    road_network = RoadNetwork(grid)
    camera_mgr = CameraManager(grid, road_network)
    camera_mgr.target_camera_count = 20

    # Place cameras
    camera_mgr.place_cameras()

    assert camera_mgr.get_camera_count() > 0, "Should have placed cameras"
    assert camera_mgr.get_active_camera_count() > 0, "Should have active cameras"

    print(f"  ✓ Placed {camera_mgr.get_camera_count()} cameras")
    print(f"  ✓ Active cameras: {camera_mgr.get_active_camera_count()}")


def test_police_station_camera_placement():
    """Test camera placement near police stations."""
    print("\nTest: Police Station Camera Placement")

    grid = Grid(width_tiles=50, height_tiles=50)
    camera_mgr = CameraManager(grid)

    # Mock police station positions
    police_stations = [(800, 800), (1200, 1200)]

    camera_mgr.place_cameras(police_stations)

    # Should have cameras (5 per police station)
    expected_min = len(police_stations) * camera_mgr.police_station_camera_density
    assert camera_mgr.get_camera_count() >= expected_min, \
        f"Should have at least {expected_min} cameras near police stations"

    print(f"  ✓ Placed {camera_mgr.get_camera_count()} cameras near {len(police_stations)} police stations")


def test_camera_manager_detection():
    """Test robot detection through CameraManager."""
    print("\nTest: Camera Manager Detection")

    grid = Grid(width_tiles=30, height_tiles=30)
    camera_mgr = CameraManager(grid)

    # Place a camera
    camera = SecurityCamera(world_x=500.0, world_y=500.0, facing_angle=0)
    camera_mgr.cameras.append(camera)

    # Create robots
    robot_in_view = MockRobot(world_x=600.0, world_y=500.0)
    robot_out_of_view = MockRobot(world_x=400.0, world_y=500.0)

    robots = [robot_in_view, robot_out_of_view]

    # Detect robots
    detections = camera_mgr.detect_robots(robots, game_time=0.0)

    assert len(detections) == 1, "Should detect 1 robot"
    assert detections[0][1] == robot_in_view, "Should detect robot in view"

    # Test detection cooldown
    detections2 = camera_mgr.detect_robots(robots, game_time=1.0)
    assert len(detections2) == 0, "Should not detect again within cooldown"

    # After cooldown
    detections3 = camera_mgr.detect_robots(robots, game_time=10.0)
    assert len(detections3) == 1, "Should detect again after cooldown"

    print(f"  ✓ Detected robot in camera view")
    print(f"  ✓ Did not detect robot out of view")
    print(f"  ✓ Detection cooldown works correctly")


def test_nearest_camera():
    """Test finding nearest camera."""
    print("\nTest: Find Nearest Camera")

    grid = Grid(width_tiles=30, height_tiles=30)
    camera_mgr = CameraManager(grid)

    # Place cameras at known positions
    cam1 = SecurityCamera(world_x=100.0, world_y=100.0)
    cam2 = SecurityCamera(world_x=500.0, world_y=500.0)
    cam3 = SecurityCamera(world_x=900.0, world_y=900.0)

    camera_mgr.cameras.extend([cam1, cam2, cam3])

    # Find nearest to point near cam2
    nearest = camera_mgr.get_nearest_camera(520.0, 520.0)
    assert nearest == cam2, "Should find cam2 as nearest"

    # Find nearest to point near cam1
    nearest = camera_mgr.get_nearest_camera(110.0, 110.0)
    assert nearest == cam1, "Should find cam1 as nearest"

    print(f"  ✓ Correctly finds nearest camera to given position")


def run_all_tests():
    """Run all camera system tests."""
    print("=" * 80)
    print("PHASE 8.1: CAMERA SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()

    try:
        test_camera_creation()
        test_vision_cone_detection()
        test_camera_status_changes()
        test_robot_detection()
        test_camera_manager_creation()
        test_camera_placement()
        test_police_station_camera_placement()
        test_camera_manager_detection()
        test_nearest_camera()

        print()
        print("=" * 80)
        print("ALL CAMERA SYSTEM TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Phase 8.1 Camera System Complete:")
        print("  ✓ SecurityCamera with 90° vision cone")
        print("  ✓ 200 pixel detection range")
        print("  ✓ Vision cone point detection")
        print("  ✓ Camera status management (active, disabled, broken)")
        print("  ✓ Disable timer with auto re-activation")
        print("  ✓ Robot detection through cameras")
        print("  ✓ CameraManager with intelligent placement")
        print("  ✓ Police station camera clusters")
        print("  ✓ Road and building camera placement")
        print("  ✓ Detection cooldown system")
        print("  ✓ Nearest camera finding")

        return True

    except AssertionError as e:
        print()
        print("=" * 80)
        print(f"TEST FAILED: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
