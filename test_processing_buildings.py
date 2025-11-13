"""
Test script for processing buildings.

Tests the ProcessingBuilding base class and all derived classes.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.entities.buildings import (
    PaperRecycler,
    PlasticRecycler,
    MetalRefinery,
    Glassworks,
    RubberRecycler
)


def test_building_instantiation():
    """Test that all processing buildings can be instantiated."""
    print("Testing building instantiation...")

    buildings = [
        ("Paper Recycler", PaperRecycler(10, 10)),
        ("Plastic Recycler", PlasticRecycler(20, 10)),
        ("Metal Refinery", MetalRefinery(30, 10)),
        ("Glassworks", Glassworks(40, 10)),
        ("Rubber Recycler", RubberRecycler(50, 10))
    ]

    for name, building in buildings:
        print(f"  ✓ {name}: {building}")
        assert building.name == name
        assert building.grid_x >= 0
        assert building.grid_y >= 0
        assert building.width_tiles > 0
        assert building.height_tiles > 0
        assert building.power_consumption > 0
        assert building.processing_speed > 0
        assert 0 < building.efficiency <= 1.0
        assert len(building.input_material_types) > 0

    print("  All buildings instantiated successfully!\n")
    return buildings


def test_material_acceptance():
    """Test material acceptance logic."""
    print("Testing material acceptance...")

    paper = PaperRecycler(10, 10)

    # Test accepted materials
    assert paper.can_accept_material('paper') == True
    assert paper.can_accept_material('cardboard') == True

    # Test rejected materials
    assert paper.can_accept_material('plastic') == False
    assert paper.can_accept_material('metal') == False

    print("  ✓ Paper Recycler correctly accepts paper and cardboard")
    print("  ✓ Paper Recycler correctly rejects other materials\n")


def test_input_queue():
    """Test input queue management."""
    print("Testing input queue...")

    plastic = PlasticRecycler(10, 10)

    # Add materials to queue
    added = plastic.add_to_input_queue('plastic', 100.0)
    assert added == 100.0
    assert plastic.get_current_input_weight() == 100.0

    # Add more
    added = plastic.add_to_input_queue('pet', 200.0)
    assert added == 200.0
    assert plastic.get_current_input_weight() == 300.0

    # Try to add rejected material
    added = plastic.add_to_input_queue('paper', 50.0)
    assert added == 0.0
    assert plastic.get_current_input_weight() == 300.0

    # Fill queue to capacity
    max_queue = plastic.max_input_queue
    added = plastic.add_to_input_queue('plastic', max_queue)
    assert added == (max_queue - 300.0)
    assert plastic.get_current_input_weight() == max_queue

    # Try to overfill
    added = plastic.add_to_input_queue('plastic', 100.0)
    assert added == 0.0

    print(f"  ✓ Input queue accepts valid materials")
    print(f"  ✓ Input queue rejects invalid materials")
    print(f"  ✓ Input queue respects capacity limit ({max_queue}kg)\n")


def test_processing_cycle():
    """Test processing materials through the building."""
    print("Testing processing cycle...")

    metal = MetalRefinery(10, 10)
    metal.powered = True
    metal.operational = True

    # Add material to input queue
    metal.add_to_input_queue('aluminum', 100.0)

    # Start processing
    metal._start_processing()
    assert metal.processing_current is not None
    assert metal.processing_current['material_type'] == 'aluminum'
    assert metal.processing_current['quantity'] == 100.0
    assert metal.processing_time_remaining > 0

    expected_time = 100.0 * metal.processing_speed
    assert metal.processing_time_remaining == expected_time

    print(f"  ✓ Processing started for 100kg aluminum")
    print(f"  ✓ Processing time: {expected_time:.1f} seconds")

    # Finish processing
    initial_output_count = len(metal.output_queue)
    metal._finish_processing()

    # Check output was created
    assert len(metal.output_queue) > initial_output_count
    assert metal.processing_current is None
    assert metal.processing_time_remaining == 0.0

    # Check output materials have quality tiers
    output_materials = [item['material_type'] for item in metal.output_queue]
    print(f"  ✓ Processing completed")
    print(f"  ✓ Output materials: {output_materials}\n")


def test_quality_distribution():
    """Test quality tier distribution."""
    print("Testing quality distribution...")

    glass = Glassworks(10, 10)

    # Process material and check distribution
    glass.add_to_input_queue('glass', 1000.0)
    glass._start_processing()
    glass._finish_processing()

    # Collect output by quality
    quality_output = {'waste': 0, 'low': 0, 'medium': 0, 'high': 0}

    for item in glass.output_queue:
        material = item['material_type']
        quantity = item['quantity']

        if 'waste_' in material:
            quality_output['waste'] += quantity
        elif 'low_' in material:
            quality_output['low'] += quantity
        elif 'medium_' in material:
            quality_output['medium'] += quantity
        elif 'high_' in material:
            quality_output['high'] += quantity

    total_output = sum(quality_output.values())

    print(f"  Input: 1000kg glass")
    print(f"  Efficiency: {glass.efficiency*100:.0f}%")
    print(f"  Output distribution:")
    for quality, amount in quality_output.items():
        if total_output > 0:
            percent = (amount / total_output) * 100
            print(f"    {quality:8s}: {amount:6.1f}kg ({percent:5.1f}%)")
    print(f"  Total output: {total_output:.1f}kg")
    print(f"  Waste/loss: {1000.0 - total_output:.1f}kg\n")


def test_level_bonuses():
    """Test that leveling up improves building stats."""
    print("Testing level bonuses...")

    rubber = RubberRecycler(10, 10)

    # Record initial stats
    level_1_speed = rubber.processing_speed
    level_1_efficiency = rubber.efficiency
    level_1_waste = rubber.quality_distribution['waste']
    level_1_high = rubber.quality_distribution['high']

    print(f"  Level 1:")
    print(f"    Processing speed: {level_1_speed:.2f} sec/kg")
    print(f"    Efficiency: {level_1_efficiency*100:.1f}%")
    print(f"    Waste chance: {level_1_waste*100:.0f}%")
    print(f"    High quality chance: {level_1_high*100:.0f}%")

    # Upgrade to level 2
    rubber.level = 2
    rubber._apply_level_bonuses()

    print(f"  Level 2:")
    print(f"    Processing speed: {rubber.processing_speed:.2f} sec/kg")
    print(f"    Efficiency: {rubber.efficiency*100:.1f}%")
    print(f"    Waste chance: {rubber.quality_distribution['waste']*100:.0f}%")
    print(f"    High quality chance: {rubber.quality_distribution['high']*100:.0f}%")

    # Verify improvements
    assert rubber.processing_speed < level_1_speed, "Speed should improve (lower is better)"
    assert rubber.efficiency > level_1_efficiency, "Efficiency should improve"
    assert rubber.quality_distribution['waste'] < level_1_waste, "Waste should decrease"
    assert rubber.quality_distribution['high'] > level_1_high, "High quality should increase"

    print(f"  ✓ All stats improved at level 2\n")


def test_all_buildings_stats():
    """Display stats for all buildings."""
    print("Building Statistics Summary:")
    print("-" * 80)

    buildings = [
        PaperRecycler(0, 0),
        PlasticRecycler(0, 0),
        MetalRefinery(0, 0),
        Glassworks(0, 0),
        RubberRecycler(0, 0)
    ]

    for building in buildings:
        print(f"\n{building.name}:")
        print(f"  Size: {building.width_tiles}x{building.height_tiles} tiles")
        print(f"  Cost: ${building.base_cost:,}")
        print(f"  Power: {building.power_consumption:.1f} units")
        print(f"  Speed: {building.processing_speed:.1f} sec/kg")
        print(f"  Efficiency: {building.efficiency*100:.0f}%")
        print(f"  Input types: {', '.join(building.input_material_types)}")
        print(f"  Queue capacity: {building.max_input_queue}kg in, {building.max_output_queue}kg out")
        print(f"  Max level: {building.max_level}")

    print("\n" + "-" * 80 + "\n")


def main():
    """Run all tests."""
    print("=" * 80)
    print("PROCESSING BUILDINGS TEST SUITE")
    print("=" * 80)
    print()

    try:
        # Run all tests
        buildings = test_building_instantiation()
        test_material_acceptance()
        test_input_queue()
        test_processing_cycle()
        test_quality_distribution()
        test_level_bonuses()
        test_all_buildings_stats()

        print("=" * 80)
        print("ALL TESTS PASSED! ✓")
        print("=" * 80)
        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
