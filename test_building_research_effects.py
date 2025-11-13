"""
Tests for building research effects.

Tests that research bonuses are applied to processing buildings.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.systems.research_manager import ResearchManager
from src.systems.building_manager import BuildingManager
from src.world.grid import Grid
from src.entities.buildings import PaperRecycler, PlasticRecycler, MetalRefinery


def test_processing_building_base_stats():
    """Test that processing buildings start with correct base stats."""
    print("Testing processing building base stats...")

    recycler = PaperRecycler(10, 10)

    # Check base values exist
    assert hasattr(recycler, 'base_processing_speed'), "Should have base_processing_speed"
    assert hasattr(recycler, 'base_efficiency'), "Should have base_efficiency"
    assert hasattr(recycler, 'base_power_consumption'), "Should have base_power_consumption"

    # Initially, current values should match base values
    assert recycler.processing_speed == recycler.base_processing_speed
    assert recycler.efficiency == recycler.base_efficiency
    assert recycler.power_consumption == recycler.base_power_consumption

    print(f"  ✓ Paper Recycler base stats:")
    print(f"    Processing speed: {recycler.processing_speed}s/kg")
    print(f"    Efficiency: {recycler.efficiency:.1%}")
    print(f"    Power: {recycler.power_consumption}W")
    print()


def test_processing_speed_research():
    """Test applying processing speed research to buildings."""
    print("Testing processing speed research...")

    research_manager = ResearchManager()
    recycler = PaperRecycler(10, 10)

    initial_speed = recycler.processing_speed
    print(f"  Initial processing speed: {initial_speed}s/kg")

    # Simulate processing speed research (2x speed = half the time)
    research_manager.active_effects['processing_speed'] = 2.0

    recycler.apply_research_effects(research_manager)

    # Processing speed should be halved (faster)
    expected_speed = initial_speed / 2.0
    assert abs(recycler.processing_speed - expected_speed) < 0.01, \
        f"Processing speed should be {expected_speed}, got {recycler.processing_speed}"

    print(f"  After 2x speed research: {recycler.processing_speed}s/kg (expected {expected_speed})")
    print(f"  ✓ Processing speed correctly doubled (time halved)")
    print()


def test_efficiency_research():
    """Test applying efficiency research to buildings."""
    print("Testing efficiency research...")

    research_manager = ResearchManager()
    recycler = PaperRecycler(10, 10)

    initial_efficiency = recycler.base_efficiency
    print(f"  Initial efficiency: {initial_efficiency:.1%}")

    # Simulate efficiency research (1.1x = +10% efficiency)
    research_manager.active_effects['processing_efficiency'] = 1.1

    recycler.apply_research_effects(research_manager)

    # Efficiency should increase but be capped at 98%
    expected_efficiency = min(0.98, initial_efficiency * 1.1)
    assert abs(recycler.efficiency - expected_efficiency) < 0.001, \
        f"Efficiency should be {expected_efficiency:.1%}, got {recycler.efficiency:.1%}"

    print(f"  After 1.1x efficiency research: {recycler.efficiency:.1%} (expected {expected_efficiency:.1%})")
    print(f"  ✓ Efficiency correctly improved")
    print()


def test_power_efficiency_research():
    """Test applying power efficiency research to buildings."""
    print("Testing power efficiency research...")

    research_manager = ResearchManager()
    recycler = PaperRecycler(10, 10)

    initial_power = recycler.base_power_consumption
    print(f"  Initial power consumption: {initial_power}W")

    # Simulate power efficiency research (1.2x = 20% more efficient, consumes less)
    research_manager.active_effects['building_power_efficiency'] = 1.2

    recycler.apply_research_effects(research_manager)

    # Power consumption should decrease
    expected_power = initial_power / 1.2
    assert abs(recycler.power_consumption - expected_power) < 0.01, \
        f"Power should be {expected_power:.1f}W, got {recycler.power_consumption:.1f}W"

    print(f"  After 1.2x power efficiency: {recycler.power_consumption:.1f}W (expected {expected_power:.1f})")
    print(f"  ✓ Power consumption correctly reduced")
    print()


def test_cumulative_building_effects():
    """Test that multiple research bonuses stack on buildings."""
    print("Testing cumulative building research effects...")

    research_manager = ResearchManager()
    recycler = PlasticRecycler(10, 10)

    initial_speed = recycler.base_processing_speed
    initial_efficiency = recycler.base_efficiency
    initial_power = recycler.base_power_consumption

    print(f"  Initial stats:")
    print(f"    Speed: {initial_speed}s/kg")
    print(f"    Efficiency: {initial_efficiency:.1%}")
    print(f"    Power: {initial_power}W")

    # Apply multiple research effects
    research_manager.active_effects['processing_speed'] = 1.5  # 50% faster
    research_manager.active_effects['processing_efficiency'] = 1.05  # 5% more efficient
    research_manager.active_effects['building_power_efficiency'] = 1.3  # 30% less power

    recycler.apply_research_effects(research_manager)

    # Check all effects applied
    expected_speed = initial_speed / 1.5
    expected_efficiency = min(0.98, initial_efficiency * 1.05)
    expected_power = initial_power / 1.3

    assert abs(recycler.processing_speed - expected_speed) < 0.01
    assert abs(recycler.efficiency - expected_efficiency) < 0.001
    assert abs(recycler.power_consumption - expected_power) < 0.01

    print(f"  After all research:")
    print(f"    Speed: {recycler.processing_speed:.2f}s/kg (expected {expected_speed:.2f})")
    print(f"    Efficiency: {recycler.efficiency:.1%} (expected {expected_efficiency:.1%})")
    print(f"    Power: {recycler.power_consumption:.1f}W (expected {expected_power:.1f})")
    print(f"  ✓ All research effects stacked correctly")
    print()


def test_level_bonuses_with_research():
    """Test that level bonuses work together with research bonuses."""
    print("Testing level bonuses with research...")

    research_manager = ResearchManager()
    recycler = MetalRefinery(10, 10)

    # Apply research first
    research_manager.active_effects['processing_speed'] = 2.0  # 2x speed
    recycler.apply_research_effects(research_manager)

    speed_with_research_l1 = recycler.processing_speed
    print(f"  Level 1 with 2x speed research: {speed_with_research_l1:.2f}s/kg")

    # Upgrade to level 2
    recycler.level = 2
    recycler.apply_research_effects(research_manager)

    # Level bonuses should be applied on top of research bonuses
    speed_with_research_l2 = recycler.processing_speed
    assert speed_with_research_l2 < speed_with_research_l1, \
        "Level 2 should be faster than level 1"

    print(f"  Level 2 with 2x speed research: {speed_with_research_l2:.2f}s/kg")
    print(f"  ✓ Level bonuses and research bonuses work together")
    print()


def test_building_manager_integration():
    """Test that BuildingManager applies research to all buildings."""
    print("Testing BuildingManager integration...")

    grid = Grid(100, 75, 32)
    building_manager = BuildingManager(grid)
    research_manager = ResearchManager()

    # Place multiple buildings
    recycler1 = PaperRecycler(10, 10)
    recycler2 = PlasticRecycler(20, 20)
    refinery = MetalRefinery(30, 30)

    building_manager.place_building(recycler1)
    building_manager.place_building(recycler2)
    building_manager.place_building(refinery)

    print(f"  Placed 3 buildings")

    # Apply research
    research_manager.active_effects['processing_speed'] = 1.5
    research_manager.active_effects['processing_efficiency'] = 1.1

    # Apply to all buildings
    building_manager.apply_research_effects_to_buildings(research_manager)

    # Check all buildings received effects
    for i, building in enumerate([recycler1, recycler2, refinery], 1):
        # Processing speed should be reduced (faster)
        assert building.processing_speed < building.base_processing_speed
        print(f"    Building {i}: speed={building.processing_speed:.2f}s/kg, efficiency={building.efficiency:.1%}")

    print(f"  ✓ All buildings received research effects")
    print()


def test_efficiency_cap():
    """Test that efficiency is capped at 98%."""
    print("Testing efficiency cap...")

    research_manager = ResearchManager()
    recycler = PaperRecycler(10, 10)

    # Try to apply huge efficiency bonus
    research_manager.active_effects['processing_efficiency'] = 10.0  # 10x efficiency!

    recycler.apply_research_effects(research_manager)

    # Should be capped at 98%
    assert recycler.efficiency <= 0.98, \
        f"Efficiency should be capped at 98%, got {recycler.efficiency:.1%}"

    print(f"  With 10x efficiency research: {recycler.efficiency:.1%}")
    print(f"  ✓ Efficiency correctly capped at 98%")
    print()


def main():
    """Run all building research effect tests."""
    print("=" * 80)
    print("BUILDING RESEARCH EFFECT TESTS")
    print("=" * 80)
    print()

    try:
        test_processing_building_base_stats()
        test_processing_speed_research()
        test_efficiency_research()
        test_power_efficiency_research()
        test_cumulative_building_effects()
        test_level_bonuses_with_research()
        test_building_manager_integration()
        test_efficiency_cap()

        print("=" * 80)
        print("ALL BUILDING RESEARCH TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Building Research Features:")
        print("  - Processing buildings track base stats (speed, efficiency, power)")
        print("  - Research effects applied to building stats")
        print("  - Processing speed research makes buildings faster")
        print("  - Efficiency research improves material conversion")
        print("  - Power efficiency research reduces power consumption")
        print("  - Efficiency capped at 98% (realistic limit)")
        print("  - Level bonuses stack with research bonuses")
        print("  - BuildingManager applies effects to all buildings")
        print("  - Multiple research effects stack correctly")
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
