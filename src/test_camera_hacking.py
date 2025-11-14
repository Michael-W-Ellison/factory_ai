"""
Comprehensive test suite for Phase 8.2: Camera Hacking System.

Tests:
- Research prerequisites for camera hacking
- Camera hacking interaction (click to hack)
- Hacking progress tracking
- Camera disabling with timers
- Suspicion increase on hacks
- Security upgrade trigger (after 10 hacks)
- FBI investigation trigger (after 20 hacks)
- Hack count limits
"""

import sys
import os

# Add parent directory to path
if os.path.basename(os.getcwd()) == 'src':
    sys.path.insert(0, '..')
else:
    sys.path.insert(0, 'src')

from src.world.grid import Grid
from src.systems.camera_manager import CameraManager
from src.systems.camera_hacking_manager import CameraHackingManager
from src.entities.security_camera import SecurityCamera


class MockResearchManager:
    """Mock research manager for testing."""
    def __init__(self):
        self.completed_research = set()
        self.active_effects = {}

    def is_completed(self, tech_id):
        return tech_id in self.completed_research

    def complete(self, tech_id):
        self.completed_research.add(tech_id)

    def set_effect(self, key, value):
        self.active_effects[key] = value


class MockSuspicionManager:
    """Mock suspicion manager for testing."""
    def __init__(self):
        self.suspicion = 0
        self.events = []

    def add_suspicion(self, amount, reason):
        self.suspicion += amount
        self.events.append((amount, reason))


def test_research_prerequisites():
    """Test that hacking is locked without research."""
    print("Test: Research Prerequisites")

    grid = Grid(width_tiles=30, height_tiles=30)
    camera_mgr = CameraManager(grid)
    research = MockResearchManager()
    suspicion = MockSuspicionManager()

    hacking_mgr = CameraHackingManager(camera_mgr, research, suspicion)

    # Should start disabled
    assert not hacking_mgr.hacking_enabled, "Hacking should start disabled"

    # Update from research (still disabled)
    hacking_mgr.update_from_research()
    assert not hacking_mgr.hacking_enabled, "Hacking should be disabled without research"

    # Complete Camera Hacking I research
    research.complete("camera_hacking_1")
    hacking_mgr.update_from_research()
    assert hacking_mgr.hacking_enabled, "Hacking should be enabled after research"
    assert hacking_mgr.hack_count_limit == 1, "Should be able to hack 1 camera"

    print("  ✓ Hacking starts disabled")
    print("  ✓ Hacking enabled after Camera Hacking I")
    print(f"  ✓ Hack limit: {hacking_mgr.hack_count_limit} camera(s)")


def test_research_upgrades():
    """Test research upgrade effects."""
    print("\\nTest: Research Upgrades")

    grid = Grid(width_tiles=30, height_tiles=30)
    camera_mgr = CameraManager(grid)
    research = MockResearchManager()
    suspicion = MockSuspicionManager()

    hacking_mgr = CameraHackingManager(camera_mgr, research, suspicion)

    # Camera Hacking I: 1 camera, 5 minutes (300s)
    research.complete("camera_hacking_1")
    research.set_effect("camera_hack_duration", 300.0)
    hacking_mgr.update_from_research()

    assert hacking_mgr.hack_count_limit == 1, "Level I: 1 camera"
    assert hacking_mgr.hack_duration == 300.0, "Level I: 300s duration"

    # Camera Hacking II: 1 camera, 15 minutes (900s)
    research.complete("camera_hacking_2")
    research.set_effect("camera_hack_duration", 900.0)
    hacking_mgr.update_from_research()

    assert hacking_mgr.hack_count_limit == 1, "Level II: 1 camera"
    assert hacking_mgr.hack_duration == 900.0, "Level II: 900s duration"

    # Camera Hacking III: 3 cameras, 15 minutes (900s)
    research.complete("camera_hacking_3")
    research.set_effect("camera_hack_duration", 900.0)
    hacking_mgr.update_from_research()

    assert hacking_mgr.hack_count_limit == 3, "Level III: 3 cameras"
    assert hacking_mgr.hack_duration == 900.0, "Level III: 900s duration"

    print("  ✓ Level I: 1 camera, 300s")
    print("  ✓ Level II: 1 camera, 900s")
    print("  ✓ Level III: 3 cameras, 900s")


def test_hacking_interaction():
    """Test camera hacking interaction."""
    print("\\nTest: Hacking Interaction")

    grid = Grid(width_tiles=30, height_tiles=30)
    camera_mgr = CameraManager(grid)
    research = MockResearchManager()
    suspicion = MockSuspicionManager()

    # Enable hacking
    research.complete("camera_hacking_1")
    research.set_effect("camera_hack_duration", 300.0)

    hacking_mgr = CameraHackingManager(camera_mgr, research, suspicion)
    hacking_mgr.update_from_research()

    # Place a camera
    camera = SecurityCamera(world_x=500.0, world_y=500.0)
    camera_mgr.cameras.append(camera)

    # Click on camera to start hacking
    handled = hacking_mgr.handle_click(500.0, 500.0, game_time=0.0)

    assert handled, "Click should be handled"
    assert hacking_mgr.currently_hacking, "Should be hacking"
    assert hacking_mgr.hack_target == camera, "Should target the camera"
    assert hacking_mgr.hack_progress == 0.0, "Progress should start at 0"

    print("  ✓ Camera hacking started on click")
    print(f"  ✓ Hacking target: camera at ({camera.world_x}, {camera.world_y})")


def test_hacking_progress():
    """Test hacking progress and completion."""
    print("\\nTest: Hacking Progress")

    grid = Grid(width_tiles=30, height_tiles=30)
    camera_mgr = CameraManager(grid)
    research = MockResearchManager()
    suspicion = MockSuspicionManager()

    # Enable hacking
    research.complete("camera_hacking_1")
    research.set_effect("camera_hack_duration", 300.0)

    hacking_mgr = CameraHackingManager(camera_mgr, research, suspicion)
    hacking_mgr.update_from_research()

    # Place a camera
    camera = SecurityCamera(world_x=500.0, world_y=500.0)
    camera_mgr.cameras.append(camera)

    # Start hacking
    hacking_mgr.handle_click(500.0, 500.0, game_time=0.0)

    # Update progress (1 second)
    hacking_mgr.update(1.0, game_time=1.0)
    assert hacking_mgr.currently_hacking, "Should still be hacking"
    assert hacking_mgr.hack_progress == 1.0, "Progress should be 1.0"
    assert camera.is_active(), "Camera should still be active"

    # Update progress (2 more seconds - total 3 seconds, hack complete)
    hacking_mgr.update(2.0, game_time=3.0)
    assert not hacking_mgr.currently_hacking, "Hacking should be complete"
    assert camera.is_disabled(), "Camera should be disabled"
    assert camera.disabled_timer == 300.0, "Camera should be disabled for 300s"

    print("  ✓ Hacking progress tracked correctly")
    print("  ✓ Camera disabled after 3 seconds")
    print(f"  ✓ Disabled duration: {camera.disabled_timer}s")


def test_suspicion_increase():
    """Test suspicion increase on hack."""
    print("\\nTest: Suspicion Increase")

    grid = Grid(width_tiles=30, height_tiles=30)
    camera_mgr = CameraManager(grid)
    research = MockResearchManager()
    suspicion = MockSuspicionManager()

    # Enable hacking
    research.complete("camera_hacking_1")
    research.set_effect("camera_hack_duration", 300.0)

    hacking_mgr = CameraHackingManager(camera_mgr, research, suspicion)
    hacking_mgr.update_from_research()

    # Place a camera
    camera = SecurityCamera(world_x=500.0, world_y=500.0)
    camera_mgr.cameras.append(camera)

    # Hack the camera
    hacking_mgr.handle_click(500.0, 500.0, game_time=0.0)
    hacking_mgr.update(3.0, game_time=3.0)

    # Check suspicion
    assert suspicion.suspicion == 2, "Suspicion should increase by 2"
    assert len(suspicion.events) == 1, "Should have 1 suspicion event"

    print(f"  ✓ Suspicion increased by {suspicion.suspicion}")
    print(f"  ✓ Total hacks: {hacking_mgr.total_hacks}")


def test_hack_count_limit():
    """Test hack count limit."""
    print("\\nTest: Hack Count Limit")

    grid = Grid(width_tiles=30, height_tiles=30)
    camera_mgr = CameraManager(grid)
    research = MockResearchManager()
    suspicion = MockSuspicionManager()

    # Enable hacking (Level I: 1 camera only)
    research.complete("camera_hacking_1")
    research.set_effect("camera_hack_duration", 300.0)

    hacking_mgr = CameraHackingManager(camera_mgr, research, suspicion)
    hacking_mgr.update_from_research()

    # Place 2 cameras
    camera1 = SecurityCamera(world_x=400.0, world_y=500.0)
    camera2 = SecurityCamera(world_x=600.0, world_y=500.0)
    camera_mgr.cameras.extend([camera1, camera2])

    # Hack first camera
    hacking_mgr.handle_click(400.0, 500.0, game_time=0.0)
    hacking_mgr.update(3.0, game_time=3.0)

    assert camera1.is_disabled(), "Camera 1 should be disabled"
    assert hacking_mgr.total_hacks == 1, "Should have 1 hack"

    # Try to hack second camera (should fail - limit reached)
    handled = hacking_mgr.handle_click(600.0, 500.0, game_time=3.0)

    assert not handled, "Second hack should be rejected"
    assert camera2.is_active(), "Camera 2 should still be active"
    assert hacking_mgr.total_hacks == 1, "Should still have 1 hack"

    print("  ✓ First camera hacked successfully")
    print("  ✓ Second hack rejected (limit reached)")
    print(f"  ✓ Hack limit: {hacking_mgr.hack_count_limit}")


def test_security_upgrade_trigger():
    """Test security upgrade after 10 hacks."""
    print("\\nTest: Security Upgrade Trigger")

    grid = Grid(width_tiles=50, height_tiles=50)

    # Create some roads for camera placement
    from src.world.tile import TileType
    for x in range(10, 40):
        tile = grid.get_tile(x, 25)
        tile.tile_type = TileType.ROAD_ASPHALT

    from src.systems.road_network import RoadNetwork
    road_network = RoadNetwork(grid)

    camera_mgr = CameraManager(grid, road_network)
    camera_mgr.target_camera_count = 50  # Place many cameras
    camera_mgr.place_cameras()

    research = MockResearchManager()
    suspicion = MockSuspicionManager()

    # Enable hacking
    research.complete("camera_hacking_1")
    research.set_effect("camera_hack_duration", 10.0)  # Short duration for testing

    hacking_mgr = CameraHackingManager(camera_mgr, research, suspicion)
    hacking_mgr.update_from_research()

    initial_camera_count = camera_mgr.get_camera_count()

    # Hack 10 cameras
    hacked_count = 0
    game_time = 0.0
    for i in range(15):  # Try to hack up to 15 times
        if hacked_count >= 10:
            break

        # Find an active camera
        active_camera = None
        for cam in camera_mgr.cameras:
            if cam.is_active():
                active_camera = cam
                break

        if active_camera is None:
            # Wait for cameras to re-enable
            game_time += 15.0
            # Update all cameras
            for cam in camera_mgr.cameras:
                cam.update(15.0)
            continue

        # Hack the camera
        success = hacking_mgr.handle_click(active_camera.world_x, active_camera.world_y, game_time)
        if success:
            # Complete the hack
            hacking_mgr.update(3.0, game_time + 3.0)
            hacked_count += 1
            game_time += 3.0

        # Wait for camera to re-enable before next hack
        game_time += 15.0
        for cam in camera_mgr.cameras:
            cam.update(15.0)

    # Security upgrade should be triggered
    assert hacking_mgr.security_upgrade_triggered, "Security upgrade should be triggered"
    assert camera_mgr.get_camera_count() > initial_camera_count, "Should have more cameras"

    print(f"  ✓ Performed {hacked_count} hacks")
    print(f"  ✓ Security upgrade triggered")
    print(f"  ✓ Cameras: {initial_camera_count} → {camera_mgr.get_camera_count()}")


def test_fbi_investigation_trigger():
    """Test FBI investigation after 20 hacks."""
    print("\\nTest: FBI Investigation Trigger")

    grid = Grid(width_tiles=50, height_tiles=50)

    # Create roads for camera placement
    from src.world.tile import TileType
    for x in range(5, 45):
        tile = grid.get_tile(x, 25)
        tile.tile_type = TileType.ROAD_ASPHALT

    from src.systems.road_network import RoadNetwork
    road_network = RoadNetwork(grid)

    camera_mgr = CameraManager(grid, road_network)
    camera_mgr.target_camera_count = 100  # Place many cameras
    camera_mgr.place_cameras()

    research = MockResearchManager()
    suspicion = MockSuspicionManager()

    # Enable hacking with Level III (3 cameras at once)
    research.complete("camera_hacking_1")
    research.complete("camera_hacking_2")
    research.complete("camera_hacking_3")
    research.set_effect("camera_hack_duration", 5.0)  # Very short for testing

    hacking_mgr = CameraHackingManager(camera_mgr, research, suspicion)
    hacking_mgr.update_from_research()

    # Hack 20 cameras
    hacked_count = 0
    game_time = 0.0
    max_attempts = 30

    for attempt in range(max_attempts):
        if hacked_count >= 20:
            break

        # Find active cameras (up to 3 since Level III allows 3 at once)
        active_cameras = [cam for cam in camera_mgr.cameras if cam.is_active()]

        if len(active_cameras) == 0:
            # Wait for cameras to re-enable
            game_time += 10.0
            for cam in camera_mgr.cameras:
                cam.update(10.0)
            continue

        # Hack an active camera
        camera = active_cameras[0]
        success = hacking_mgr.handle_click(camera.world_x, camera.world_y, game_time)
        if success:
            # Complete the hack
            hacking_mgr.update(3.0, game_time + 3.0)
            hacked_count += 1
            game_time += 3.0

        # Check if we need to wait for cameras to re-enable
        currently_disabled = sum(1 for cam in camera_mgr.cameras if cam.is_disabled())
        if currently_disabled >= 3:
            # Wait for some cameras to re-enable
            game_time += 10.0
            for cam in camera_mgr.cameras:
                cam.update(10.0)

    # FBI investigation should be triggered
    assert hacking_mgr.fbi_investigation_triggered, "FBI investigation should be triggered"
    assert hacking_mgr.total_hacks >= 20, "Should have at least 20 hacks"

    print(f"  ✓ Performed {hacked_count} hacks")
    print(f"  ✓ FBI investigation triggered")
    print(f"  ✓ Total suspicion: {suspicion.suspicion}")


def test_cancel_hack():
    """Test canceling a hack in progress."""
    print("\\nTest: Cancel Hack")

    grid = Grid(width_tiles=30, height_tiles=30)
    camera_mgr = CameraManager(grid)
    research = MockResearchManager()
    suspicion = MockSuspicionManager()

    # Enable hacking
    research.complete("camera_hacking_1")
    research.set_effect("camera_hack_duration", 300.0)

    hacking_mgr = CameraHackingManager(camera_mgr, research, suspicion)
    hacking_mgr.update_from_research()

    # Place a camera
    camera = SecurityCamera(world_x=500.0, world_y=500.0)
    camera_mgr.cameras.append(camera)

    # Start hacking
    hacking_mgr.handle_click(500.0, 500.0, game_time=0.0)
    assert hacking_mgr.currently_hacking, "Should be hacking"

    # Cancel hack
    hacking_mgr.cancel_hack()
    assert not hacking_mgr.currently_hacking, "Should not be hacking"
    assert hacking_mgr.hack_target is None, "Target should be cleared"
    assert camera.is_active(), "Camera should still be active"

    print("  ✓ Hack cancelled successfully")
    print("  ✓ Camera remains active")


def run_all_tests():
    """Run all camera hacking tests."""
    print("=" * 80)
    print("PHASE 8.2: CAMERA HACKING - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()

    try:
        test_research_prerequisites()
        test_research_upgrades()
        test_hacking_interaction()
        test_hacking_progress()
        test_suspicion_increase()
        test_hack_count_limit()
        test_security_upgrade_trigger()
        test_fbi_investigation_trigger()
        test_cancel_hack()

        print()
        print("=" * 80)
        print("ALL CAMERA HACKING TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Phase 8.2 Camera Hacking Complete:")
        print("  ✓ Research prerequisites (Camera Hacking I/II/III)")
        print("  ✓ Click-to-hack interaction")
        print("  ✓ Hacking progress tracking (3 seconds)")
        print("  ✓ Camera disabling with timers")
        print("  ✓ Suspicion increase (+2 per hack)")
        print("  ✓ Hack count limits (1/1/3 cameras)")
        print("  ✓ Security upgrade trigger (after 10 hacks)")
        print("  ✓ FBI investigation trigger (after 20 hacks)")
        print("  ✓ Hack cancellation")

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
