"""
Tests for NPC system.

Tests NPC entities, daily schedules, movement, vision, and NPCManager functionality.
"""

import sys
import os
import math

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.systems.npc_manager import NPCManager
from src.entities.npc import NPC, Activity
from src.world.grid import Grid


def test_npc_creation():
    """Test creating NPCs with different configurations."""
    print("Testing NPC creation...")

    # Employed NPC
    npc1 = NPC(100, 100, home_x=10, home_y=10, work_x=20, work_y=20)
    assert npc1.world_x == 100
    assert npc1.world_y == 100
    assert npc1.home_x == 10
    assert npc1.home_y == 10
    assert npc1.has_job == True
    print(f"  Employed NPC: home=({npc1.home_x},{npc1.home_y}), work=({npc1.work_x},{npc1.work_y})")

    # Unemployed NPC
    npc2 = NPC(200, 200, home_x=15, home_y=15)
    assert npc2.has_job == False
    assert npc2.work_x is None
    print(f"  Unemployed NPC: home=({npc2.home_x},{npc2.home_y}), work=None")

    # Vision properties
    assert npc1.vision_range == 100.0
    assert npc1.vision_angle == 180.0
    print(f"  Vision: range={npc1.vision_range}px, angle={npc1.vision_angle}°")

    print(f"  ✓ NPCs created with correct properties")
    print()


def test_npc_daily_schedule():
    """Test NPC activity changes based on time."""
    print("Testing NPC daily schedule...")

    npc = NPC(100, 100, home_x=10, home_y=10, work_x=20, work_y=20)

    # Test different times of day
    test_times = [
        (2.0, Activity.SLEEPING, "2am - Sleeping"),
        (7.0, Activity.MORNING_ROUTINE, "7am - Morning routine"),
        (8.5, Activity.COMMUTING_TO_WORK, "8:30am - Commuting to work"),
        (12.0, Activity.WORKING, "12pm - Working"),
        (17.5, Activity.COMMUTING_HOME, "5:30pm - Commuting home"),
        (19.0, Activity.EVENING_ACTIVITIES, "7pm - Evening activities"),
        (21.0, Activity.HOME_ROUTINE, "9pm - Home routine"),
        (23.0, Activity.SLEEPING, "11pm - Sleeping"),
    ]

    for time, expected_activity, description in test_times:
        npc.update_schedule(time)
        assert npc.current_activity == expected_activity, f"Failed at {description}"
        print(f"  {description}: ✓")

    print(f"  ✓ Daily schedule works correctly")
    print()


def test_unemployed_npc_schedule():
    """Test that unemployed NPCs have different schedules."""
    print("Testing unemployed NPC schedule...")

    npc = NPC(100, 100, home_x=10, home_y=10)  # No work location

    # Unemployed NPCs should stay home during work hours
    npc.update_schedule(12.0)  # Noon
    assert npc.current_activity == Activity.HOME_ROUTINE
    print(f"  Unemployed NPC at noon: {npc.current_activity}")

    npc.update_schedule(8.5)  # Commute time
    assert npc.current_activity == Activity.HOME_ROUTINE
    print(f"  Unemployed NPC at 8:30am: {npc.current_activity}")

    print(f"  ✓ Unemployed NPCs stay home during work hours")
    print()


def test_npc_movement():
    """Test NPC movement towards targets."""
    print("Testing NPC movement...")

    npc = NPC(100, 100, home_x=10, home_y=10)

    # Set a target
    npc.target_x = 200
    npc.target_y = 200
    npc.moving = True

    initial_x = npc.world_x
    initial_y = npc.world_y

    # Update movement (1 second at 30px/s)
    npc.update(1.0, 8.0)  # 1 second, 8am

    # Should have moved towards target
    assert npc.world_x != initial_x or npc.world_y != initial_y
    print(f"  Moved from ({initial_x:.0f},{initial_y:.0f}) to ({npc.world_x:.0f},{npc.world_y:.0f})")

    # Check distance traveled (should be ~30 pixels)
    dx = npc.world_x - initial_x
    dy = npc.world_y - initial_y
    distance = math.sqrt(dx * dx + dy * dy)
    assert 28 <= distance <= 32  # Allow small tolerance
    print(f"  Distance traveled: {distance:.1f}px (expected ~30px)")

    print(f"  ✓ NPC movement works correctly")
    print()


def test_npc_vision_cone():
    """Test NPC vision cone detection."""
    print("Testing NPC vision cone...")

    npc = NPC(100, 100, home_x=10, home_y=10)
    npc.facing_angle = 0  # Facing right

    # Target directly ahead (should be visible)
    visible = npc.is_in_vision_cone(150, 100)
    assert visible == True
    print(f"  Target ahead: visible={visible}")

    # Target to the side (should be visible, 180° cone)
    visible = npc.is_in_vision_cone(150, 150)
    assert visible == True
    print(f"  Target to front-side: visible={visible}")

    # Target behind (should NOT be visible)
    visible = npc.is_in_vision_cone(50, 100)
    assert visible == False
    print(f"  Target behind: visible={visible}")

    # Target too far (should NOT be visible)
    visible = npc.is_in_vision_cone(250, 100)  # 150 pixels away
    assert visible == False
    print(f"  Target too far: visible={visible}")

    print(f"  ✓ Vision cone works correctly")
    print()


def test_detection_chance():
    """Test detection chance calculation."""
    print("Testing detection chance calculation...")

    npc = NPC(100, 100, home_x=10, home_y=10)
    npc.facing_angle = 0  # Facing right
    npc.alertness = 0.5

    # Close robot, daytime, low stealth (should have high detection chance)
    chance = npc.calculate_detection_chance(120, 100, is_daytime=True, robot_stealth=0.2)
    assert chance > 0
    print(f"  Close, daytime, low stealth: {chance:.3f}")

    # Far robot (should have lower detection chance)
    chance_far = npc.calculate_detection_chance(180, 100, is_daytime=True, robot_stealth=0.2)
    assert chance_far < chance
    print(f"  Far, daytime, low stealth: {chance_far:.3f}")

    # Night time (should reduce detection)
    chance_night = npc.calculate_detection_chance(120, 100, is_daytime=False, robot_stealth=0.2)
    assert chance_night < chance
    print(f"  Close, nighttime, low stealth: {chance_night:.3f}")

    # High stealth (should reduce detection)
    chance_stealth = npc.calculate_detection_chance(120, 100, is_daytime=True, robot_stealth=0.8)
    assert chance_stealth < chance
    print(f"  Close, daytime, high stealth: {chance_stealth:.3f}")

    # Out of vision cone (should be zero)
    chance_behind = npc.calculate_detection_chance(50, 100, is_daytime=True, robot_stealth=0.2)
    assert chance_behind == 0.0
    print(f"  Behind NPC: {chance_behind:.3f}")

    print(f"  ✓ Detection chance calculation works correctly")
    print()


def test_detection_accumulation():
    """Test detection progress accumulation."""
    print("Testing detection accumulation...")

    npc = NPC(100, 100, home_x=10, home_y=10)

    robot_id = 123

    # Accumulate detection
    detected = npc.update_detection(robot_id, detection_chance=0.3, dt=1.0)
    assert not detected
    assert robot_id in npc.detecting_robots
    assert npc.detecting_robots[robot_id] == 0.3
    print(f"  After 1s at 0.3/s: {npc.detecting_robots[robot_id]:.1%}")

    # Continue accumulating
    detected = npc.update_detection(robot_id, detection_chance=0.3, dt=1.0)
    assert not detected
    assert npc.detecting_robots[robot_id] == 0.6
    print(f"  After 2s at 0.3/s: {npc.detecting_robots[robot_id]:.1%}")

    # Reach full detection
    detected = npc.update_detection(robot_id, detection_chance=0.5, dt=1.0)
    assert detected  # Should trigger at >= 1.0
    assert npc.detecting_robots[robot_id] == 1.0
    print(f"  After 3s (detected): {npc.detecting_robots[robot_id]:.1%}")

    print(f"  ✓ Detection accumulation works correctly")
    print()


def test_npc_manager_initialization():
    """Test NPCManager initialization."""
    print("Testing NPCManager initialization...")

    grid = Grid(30, 30, 32)
    manager = NPCManager(grid)

    assert manager.grid == grid
    assert len(manager.npcs) == 0
    assert manager.game_time == 8.0  # Starts at 8am
    print(f"  Initial time: {manager.get_time_string()}")
    print(f"  Time scale: {manager.time_scale}x")
    print(f"  Employment rate: {manager.employment_rate:.0%}")
    print(f"  ✓ NPCManager initialized correctly")
    print()


def test_npc_spawning():
    """Test spawning NPCs in the city."""
    print("Testing NPC spawning...")

    # Create a grid with buildings
    grid = Grid(30, 30, 32)
    grid.create_test_world()

    manager = NPCManager(grid)
    manager.spawn_npcs_in_city(seed=123)

    # Should have spawned NPCs
    npc_count = len(manager.npcs)
    assert npc_count > 0
    print(f"  Spawned {npc_count} NPCs")

    # Check employment
    employed = sum(1 for npc in manager.npcs if npc.has_job)
    unemployed = npc_count - employed
    employment_rate = employed / npc_count if npc_count > 0 else 0

    print(f"  Employed: {employed} ({employment_rate:.1%})")
    print(f"  Unemployed: {unemployed}")

    # Employment rate should be close to target (with some randomness)
    assert 0.5 <= employment_rate <= 0.9

    print(f"  ✓ NPCs spawned correctly")
    print()


def test_time_progression():
    """Test game time progression."""
    print("Testing time progression...")

    grid = Grid(20, 20, 32)
    manager = NPCManager(grid)

    initial_time = manager.game_time
    print(f"  Initial time: {manager.get_time_string()}")

    # Update for 60 seconds (should advance 1 hour at 60x time scale)
    manager.update(60.0)

    expected_time = (initial_time + 1.0) % 24
    assert abs(manager.game_time - expected_time) < 0.1
    print(f"  After 60s real time: {manager.get_time_string()} (expected ~{expected_time:.1f})")

    # Time should wrap at 24 hours
    manager.game_time = 23.5
    manager.update(60.0)  # +1 hour = 24.5 -> 0.5
    assert manager.game_time < 24.0
    print(f"  After wrapping midnight: {manager.get_time_string()}")

    print(f"  ✓ Time progression works correctly")
    print()


def test_npc_schedule_changes_over_time():
    """Test that NPCs change activities as time progresses."""
    print("Testing NPC activity changes over time...")

    grid = Grid(20, 20, 32)
    manager = NPCManager(grid)

    # Create an employed NPC manually
    npc = NPC(100, 100, home_x=10, home_y=10, work_x=20, work_y=20)
    manager.npcs.append(npc)

    # Set time to morning
    manager.game_time = 7.0
    manager.update(0.1)
    assert npc.current_activity == Activity.MORNING_ROUTINE
    print(f"  7am: {npc.current_activity}")

    # Advance to work time
    manager.game_time = 10.0
    manager.update(0.1)
    assert npc.current_activity == Activity.WORKING
    print(f"  10am: {npc.current_activity}")

    # Advance to evening
    manager.game_time = 19.0
    manager.update(0.1)
    assert npc.current_activity == Activity.EVENING_ACTIVITIES
    print(f"  7pm: {npc.current_activity}")

    # Advance to night
    manager.game_time = 23.0
    manager.update(0.1)
    assert npc.current_activity == Activity.SLEEPING
    print(f"  11pm: {npc.current_activity}")

    print(f"  ✓ NPCs change activities correctly over time")
    print()


def test_npc_stats():
    """Test NPC statistics."""
    print("Testing NPC statistics...")

    grid = Grid(25, 25, 32)
    grid.create_test_world()

    manager = NPCManager(grid)
    manager.spawn_npcs_in_city(seed=456)

    stats = manager.get_stats()

    assert stats['total'] > 0
    assert stats['employed'] + stats['unemployed'] == stats['total']
    assert 'activities' in stats
    assert stats['current_time'] == manager.game_time

    print(f"  Total NPCs: {stats['total']}")
    print(f"  Employed: {stats['employed']}")
    print(f"  Unemployed: {stats['unemployed']}")
    print(f"  Current time: {manager.get_time_string()}")
    print(f"  Activities: {stats['activities']}")

    print(f"  ✓ NPC statistics correct")
    print()


def main():
    """Run all tests."""
    print("=" * 80)
    print("NPC SYSTEM TESTS")
    print("=" * 80)
    print()

    try:
        test_npc_creation()
        test_npc_daily_schedule()
        test_unemployed_npc_schedule()
        test_npc_movement()
        test_npc_vision_cone()
        test_detection_chance()
        test_detection_accumulation()
        test_npc_manager_initialization()
        test_npc_spawning()
        test_time_progression()
        test_npc_schedule_changes_over_time()
        test_npc_stats()

        print("=" * 80)
        print("ALL NPC SYSTEM TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Phase 7.5 Features Implemented:")
        print()
        print("NPC ENTITY:")
        print("  - Position, movement (30px/s walking speed)")
        print("  - Home and work locations")
        print("  - Vision: 100px range, 180° front-facing cone")
        print("  - Alertness levels (0.0-1.0)")
        print("  - Detection tracking per robot")
        print()
        print("DAILY SCHEDULE:")
        print("  - Sleep: 10pm-6am (alertness 0.1)")
        print("  - Morning routine: 6am-8am (alertness 0.4)")
        print("  - Commute to work: 8am-9am (alertness 0.6)")
        print("  - Work: 9am-5pm (alertness 0.5)")
        print("  - Commute home: 5pm-6pm (alertness 0.6)")
        print("  - Evening activities: 6pm-8pm (alertness 0.7)")
        print("  - Home routine: 8pm-10pm (alertness 0.5)")
        print()
        print("DETECTION SYSTEM:")
        print("  - Vision cone checks (range + angle)")
        print("  - Detection chance based on:")
        print("    * Distance (closer = higher)")
        print("    * Time of day (daytime = higher)")
        print("    * Robot stealth level")
        print("    * NPC alertness")
        print("  - Detection accumulates over time")
        print("  - Full detection (100%) triggers report")
        print()
        print("NPC MANAGER:")
        print("  - Spawns 1-3 NPCs per house")
        print("  - 70% employment rate")
        print("  - Game time: 60x real-time (1 min = 1 hour)")
        print("  - Starts at 8am")
        print("  - Time wraps at midnight")
        print()
        print("INTEGRATION:")
        print("  - Integrated into game update/render loop")
        print("  - NPCs rendered between fences and entities")
        print("  - NPC spawning on game initialization")
        print("  - Activity indicators (when zoomed in)")
        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
