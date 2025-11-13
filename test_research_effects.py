"""
Tests for Phase 6.3: Research Effect Application.

Tests that research bonuses are actually applied to robots and buildings.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.systems.research_manager import ResearchManager
from src.systems.entity_manager import EntityManager
from src.entities.robot import Robot


def test_robot_base_stats():
    """Test that robots start with correct base stats."""
    print("Testing robot base stats...")

    robot = Robot(100, 100)

    # Check base values
    assert robot.base_speed == 100.0, "Base speed should be 100"
    assert robot.base_capacity == 100, "Base capacity should be 100"
    assert robot.base_power_capacity == 1000, "Base power capacity should be 1000"
    assert robot.base_health == 100, "Base health should be 100"

    # Initially, current values should match base values
    assert robot.speed == 100.0
    assert robot.max_capacity == 100
    assert robot.power_capacity == 1000
    assert robot.max_health == 100

    print(f"  ✓ Robot base stats: speed={robot.speed}, capacity={robot.max_capacity}")
    print(f"    power={robot.power_capacity}, health={robot.max_health}")
    print()


def test_research_effects_on_robot():
    """Test applying research effects to a single robot."""
    print("Testing research effects on robot...")

    research_manager = ResearchManager()
    robot = Robot(100, 100)

    # Initially no bonuses
    robot.apply_research_effects(research_manager)
    assert robot.speed == 100.0, "Speed should be 100 with no research"
    assert robot.max_capacity == 100, "Capacity should be 100 with no research"

    print("  Initial stats (no research):")
    print(f"    Speed: {robot.speed:.1f}")
    print(f"    Capacity: {robot.max_capacity:.1f}kg")
    print(f"    Power: {robot.power_capacity:.1f}")

    # Complete legs_1 research (+20% speed)
    research_manager.completed_research.add('legs_1')
    research_manager._complete_research('legs_1')

    robot.apply_research_effects(research_manager)
    assert robot.speed == 120.0, f"Speed should be 120 after legs_1, got {robot.speed}"
    assert robot.max_capacity == 100, "Capacity shouldn't change"

    print("  After legs_1 (+20% speed):")
    print(f"    Speed: {robot.speed:.1f} (expected 120.0)")

    # Complete motor_1 research (+25% capacity)
    research_manager.completed_research.add('motor_1')
    research_manager._complete_research('motor_1')

    robot.apply_research_effects(research_manager)
    assert robot.speed == 120.0, "Speed should still be 120"
    assert robot.max_capacity == 125.0, f"Capacity should be 125 after motor_1, got {robot.max_capacity}"

    print("  After motor_1 (+25% capacity):")
    print(f"    Speed: {robot.speed:.1f}")
    print(f"    Capacity: {robot.max_capacity:.1f}kg (expected 125.0)")

    # Complete legs_2 research (+40% speed, replaces legs_1)
    research_manager.completed_research.add('legs_2')
    research_manager._complete_research('legs_2')

    robot.apply_research_effects(research_manager)
    assert robot.speed == 140.0, f"Speed should be 140 after legs_2, got {robot.speed}"
    assert robot.max_capacity == 125.0, "Capacity should still be 125"

    print("  After legs_2 (+40% speed, replaces legs_1):")
    print(f"    Speed: {robot.speed:.1f} (expected 140.0)")

    print("  ✓ Research effects correctly applied and stacked")
    print()


def test_power_capacity_increase():
    """Test that power capacity increases grant free energy."""
    print("Testing power capacity increase...")

    research_manager = ResearchManager()
    robot = Robot(100, 100)

    # Start with some energy used
    robot.current_power = 500  # Half power

    print(f"  Initial power: {robot.current_power}/{robot.power_capacity}")

    # Complete battery_1 research (+30% power capacity)
    research_manager.completed_research.add('battery_1')
    research_manager._complete_research('battery_1')

    robot.apply_research_effects(research_manager)

    # Power capacity should be 1300, and current power should increase
    assert robot.power_capacity == 1300, f"Power capacity should be 1300, got {robot.power_capacity}"
    # Current power should have increased by the difference
    # Old capacity: 1000, new capacity: 1300, difference: 300
    # Old current: 500, new current: min(1300, 500 + 300) = 800
    assert robot.current_power == 800, f"Current power should be 800, got {robot.current_power}"

    print(f"  After battery_1 (+30% capacity):")
    print(f"    Power: {robot.current_power}/{robot.power_capacity}")
    print(f"  ✓ Power capacity increase grants bonus energy")
    print()


def test_health_increase():
    """Test that health increases grant bonus health."""
    print("Testing health increase...")

    research_manager = ResearchManager()
    robot = Robot(100, 100)

    # Damage the robot
    robot.current_health = 50

    print(f"  Initial health: {robot.current_health}/{robot.max_health}")

    # Complete frames_1 research (+25% health)
    research_manager.completed_research.add('frames_1')
    research_manager._complete_research('frames_1')

    robot.apply_research_effects(research_manager)

    # Max health should be 125, and current health should increase
    assert robot.max_health == 125, f"Max health should be 125, got {robot.max_health}"
    # Current health should have increased by the difference: 50 + 25 = 75
    assert robot.current_health == 75, f"Current health should be 75, got {robot.current_health}"

    print(f"  After frames_1 (+25% health):")
    print(f"    Health: {robot.current_health}/{robot.max_health}")
    print(f"  ✓ Health increase grants bonus health")
    print()


def test_entity_manager_integration():
    """Test that EntityManager applies research to new robots."""
    print("Testing EntityManager integration...")

    research_manager = ResearchManager()
    entity_manager = EntityManager(research_manager=research_manager)

    # Complete some research
    research_manager.completed_research.add('legs_1')
    research_manager._complete_research('legs_1')
    research_manager.completed_research.add('motor_1')
    research_manager._complete_research('motor_1')

    # Create a new robot
    robot = entity_manager.create_robot(100, 100)

    # Robot should have bonuses applied immediately
    assert robot.speed == 120.0, f"New robot should have speed 120, got {robot.speed}"
    assert robot.max_capacity == 125.0, f"New robot should have capacity 125, got {robot.max_capacity}"

    print(f"  New robot created with research bonuses:")
    print(f"    Speed: {robot.speed:.1f} (expected 120.0)")
    print(f"    Capacity: {robot.max_capacity:.1f}kg (expected 125.0)")
    print(f"  ✓ New robots start with active research bonuses")
    print()


def test_apply_to_all_robots():
    """Test applying research effects to multiple robots."""
    print("Testing bulk application to all robots...")

    research_manager = ResearchManager()
    entity_manager = EntityManager(research_manager=research_manager)

    # Create multiple robots
    robot1 = entity_manager.create_robot(100, 100)
    robot2 = entity_manager.create_robot(200, 200)
    robot3 = entity_manager.create_robot(300, 300)

    print(f"  Created 3 robots")

    # Complete research
    research_manager.completed_research.add('legs_2')
    research_manager._complete_research('legs_2')

    # Apply to all robots
    entity_manager.apply_research_effects_to_robots(research_manager)

    # All robots should have the bonus
    for i, robot in enumerate([robot1, robot2, robot3], 1):
        assert robot.speed == 140.0, f"Robot {i} should have speed 140, got {robot.speed}"
        print(f"    Robot {i}: speed={robot.speed:.1f}")

    print(f"  ✓ All robots received research effects")
    print()


def test_cumulative_effects():
    """Test that multiple research bonuses stack correctly."""
    print("Testing cumulative research effects...")

    research_manager = ResearchManager()
    robot = Robot(100, 100)

    # Complete multiple research in sequence
    research_list = [
        ('legs_1', 'robot_speed', 1.2, 120.0),
        ('motor_1', 'robot_capacity', 1.25, 125.0),
        ('battery_1', 'robot_power_capacity', 1.3, 1300.0),
        ('frames_1', 'robot_health', 1.25, 125.0),
    ]

    for tech_id, effect_name, multiplier, expected_value in research_list:
        research_manager.completed_research.add(tech_id)
        research_manager._complete_research(tech_id)
        robot.apply_research_effects(research_manager)

        actual_value = getattr(robot, {
            'robot_speed': 'speed',
            'robot_capacity': 'max_capacity',
            'robot_power_capacity': 'power_capacity',
            'robot_health': 'max_health'
        }[effect_name])

        assert actual_value == expected_value, \
            f"After {tech_id}, {effect_name} should be {expected_value}, got {actual_value}"

        print(f"  After {tech_id}: {effect_name} = {actual_value}")

    print("  ✓ Cumulative effects applied correctly")
    print()


def main():
    """Run all research effect tests."""
    print("=" * 80)
    print("RESEARCH EFFECT APPLICATION TESTS (Phase 6.3)")
    print("=" * 80)
    print()

    try:
        test_robot_base_stats()
        test_research_effects_on_robot()
        test_power_capacity_increase()
        test_health_increase()
        test_entity_manager_integration()
        test_apply_to_all_robots()
        test_cumulative_effects()

        print("=" * 80)
        print("ALL RESEARCH EFFECT TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Phase 6.3 Features:")
        print("  - Robot base stats tracking (speed, capacity, power, health)")
        print("  - Research effects applied to robot stats")
        print("  - Power capacity increases grant bonus energy")
        print("  - Health increases grant bonus health")
        print("  - New robots automatically receive active bonuses")
        print("  - Bulk application to all existing robots")
        print("  - Cumulative effects from multiple research")
        print("  - Effects persist and stack correctly")
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
