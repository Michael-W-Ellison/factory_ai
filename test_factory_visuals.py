"""
Tests for Factory visual upgrade system.

Tests that factory visual components appear based on research completion.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.entities.buildings.factory import Factory
from src.systems.research_manager import ResearchManager


def test_factory_initialization():
    """Test factory visual upgrades initialization."""
    print("Testing factory initialization...")

    factory = Factory(50, 50)

    assert 'server_farm' in factory.visual_upgrades
    assert 'battery_bank' in factory.visual_upgrades
    assert 'robot_factory' in factory.visual_upgrades
    assert 'hacking_algorithms' in factory.visual_upgrades
    assert 'processing_improvements' in factory.visual_upgrades
    assert 'research_active' in factory.visual_upgrades

    # Initial state should be no upgrades
    assert factory.visual_upgrades['server_farm'] == 0
    assert factory.visual_upgrades['battery_bank'] == 0
    assert factory.visual_upgrades['robot_factory'] == False
    assert factory.visual_upgrades['hacking_algorithms'] == 0
    assert factory.visual_upgrades['processing_improvements'] == False
    assert factory.visual_upgrades['research_active'] == False

    print(f"  ✓ Factory initialized with visual upgrades: {factory.visual_upgrades}")
    print()


def test_server_farm_upgrades():
    """Test server farm visual upgrades."""
    print("Testing server farm upgrades...")

    factory = Factory(50, 50)
    research = ResearchManager()

    # No research
    factory.update_visual_upgrades(research)
    assert factory.visual_upgrades['server_farm'] == 0

    # Complete tier 1
    research.completed_research.add('server_farm_1')
    factory.update_visual_upgrades(research)
    assert factory.visual_upgrades['server_farm'] == 1
    print(f"  After server_farm_1: tier = {factory.visual_upgrades['server_farm']}")

    # Complete tier 2
    research.completed_research.add('server_farm_2')
    factory.update_visual_upgrades(research)
    assert factory.visual_upgrades['server_farm'] == 2
    print(f"  After server_farm_2: tier = {factory.visual_upgrades['server_farm']}")

    # Complete tier 3
    research.completed_research.add('server_farm_3')
    factory.update_visual_upgrades(research)
    assert factory.visual_upgrades['server_farm'] == 3
    print(f"  After server_farm_3: tier = {factory.visual_upgrades['server_farm']}")

    print(f"  ✓ Server farm visual tiers work correctly")
    print()


def test_battery_bank_upgrades():
    """Test battery bank visual upgrades."""
    print("Testing battery bank upgrades...")

    factory = Factory(50, 50)
    research = ResearchManager()

    # Complete tiers
    research.completed_research.add('battery_bank_1')
    factory.update_visual_upgrades(research)
    assert factory.visual_upgrades['battery_bank'] == 1

    research.completed_research.add('battery_bank_2')
    factory.update_visual_upgrades(research)
    assert factory.visual_upgrades['battery_bank'] == 2

    research.completed_research.add('battery_bank_3')
    factory.update_visual_upgrades(research)
    assert factory.visual_upgrades['battery_bank'] == 3

    print(f"  Battery bank tier: {factory.visual_upgrades['battery_bank']}")
    print(f"  ✓ Battery bank visual tiers work correctly")
    print()


def test_robot_factory_upgrade():
    """Test robot factory visual upgrade."""
    print("Testing robot factory upgrade...")

    factory = Factory(50, 50)
    research = ResearchManager()

    # No research
    factory.update_visual_upgrades(research)
    assert factory.visual_upgrades['robot_factory'] == False

    # Complete robot factory
    research.completed_research.add('robot_factory')
    factory.update_visual_upgrades(research)
    assert factory.visual_upgrades['robot_factory'] == True

    print(f"  Robot factory enabled: {factory.visual_upgrades['robot_factory']}")
    print(f"  ✓ Robot factory visual upgrade works")
    print()


def test_hacking_algorithms_upgrades():
    """Test hacking algorithms visual upgrades."""
    print("Testing hacking algorithms upgrades...")

    factory = Factory(50, 50)
    research = ResearchManager()

    # Complete tiers 1-5
    for i in range(1, 6):
        research.completed_research.add(f'hacking_algorithms_{i}')
        factory.update_visual_upgrades(research)
        assert factory.visual_upgrades['hacking_algorithms'] == i
        print(f"  After hacking_algorithms_{i}: level = {factory.visual_upgrades['hacking_algorithms']}")

    print(f"  ✓ Hacking algorithms visual tiers work correctly")
    print()


def test_processing_improvements():
    """Test processing improvements visual upgrade."""
    print("Testing processing improvements...")

    factory = Factory(50, 50)
    research = ResearchManager()

    # No research
    factory.update_visual_upgrades(research)
    assert factory.visual_upgrades['processing_improvements'] == False

    # Complete processing improvements
    research.completed_research.add('recycling_improvements')
    factory.update_visual_upgrades(research)
    assert factory.visual_upgrades['processing_improvements'] == True

    print(f"  Processing improvements enabled: {factory.visual_upgrades['processing_improvements']}")
    print(f"  ✓ Processing improvements visual upgrade works")
    print()


def test_research_active_indicator():
    """Test research active indicator."""
    print("Testing research active indicator...")

    factory = Factory(50, 50)
    research = ResearchManager()

    # No research active
    factory.update_visual_upgrades(research)
    assert factory.visual_upgrades['research_active'] == False

    # Start research
    research.current_research = 'legs_1'
    factory.update_visual_upgrades(research)
    assert factory.visual_upgrades['research_active'] == True

    # Complete research
    research.current_research = None
    factory.update_visual_upgrades(research)
    assert factory.visual_upgrades['research_active'] == False

    print(f"  Research active indicator works correctly")
    print(f"  ✓ Research active visual indicator works")
    print()


def test_combined_upgrades():
    """Test multiple upgrades together."""
    print("Testing combined upgrades...")

    factory = Factory(50, 50)
    research = ResearchManager()

    # Complete multiple researches
    research.completed_research.add('server_farm_2')
    research.completed_research.add('battery_bank_1')
    research.completed_research.add('robot_factory')
    research.completed_research.add('hacking_algorithms_3')
    research.completed_research.add('recycling_improvements')
    research.current_research = 'legs_1'

    factory.update_visual_upgrades(research)

    assert factory.visual_upgrades['server_farm'] == 2
    assert factory.visual_upgrades['battery_bank'] == 1
    assert factory.visual_upgrades['robot_factory'] == True
    assert factory.visual_upgrades['hacking_algorithms'] == 3
    assert factory.visual_upgrades['processing_improvements'] == True
    assert factory.visual_upgrades['research_active'] == True

    print(f"  Combined upgrades:")
    print(f"    Server farm: {factory.visual_upgrades['server_farm']}")
    print(f"    Battery bank: {factory.visual_upgrades['battery_bank']}")
    print(f"    Robot factory: {factory.visual_upgrades['robot_factory']}")
    print(f"    Hacking algorithms: {factory.visual_upgrades['hacking_algorithms']}")
    print(f"    Processing improvements: {factory.visual_upgrades['processing_improvements']}")
    print(f"    Research active: {factory.visual_upgrades['research_active']}")
    print(f"  ✓ Multiple upgrades work together correctly")
    print()


def main():
    """Run all factory visual upgrade tests."""
    print("=" * 80)
    print("FACTORY VISUAL UPGRADE TESTS")
    print("=" * 80)
    print()

    try:
        test_factory_initialization()
        test_server_farm_upgrades()
        test_battery_bank_upgrades()
        test_robot_factory_upgrade()
        test_hacking_algorithms_upgrades()
        test_processing_improvements()
        test_research_active_indicator()
        test_combined_upgrades()

        print("=" * 80)
        print("ALL FACTORY VISUAL UPGRADE TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Factory Visual Upgrade Features:")
        print("  - Server Farm: Satellite dish + antennas (3 tiers)")
        print("  - Battery Bank: Battery units on side (3 tiers)")
        print("  - Robot Factory: Animated assembly arm")
        print("  - Hacking Algorithms: Server racks with blinking lights (5 tiers)")
        print("  - Processing Improvements: Smokestack with animated smoke")
        print("  - Research Active: Pulsing blue glow indicator")
        print("  - All upgrades visible and animated in real-time")
        print("  - Updates automatically when research completes")
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
