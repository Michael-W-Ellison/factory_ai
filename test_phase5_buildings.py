"""
Comprehensive tests for Phase 5: Advanced Processing & Manufacturing Buildings.

Tests Phase 5.2 advanced processing buildings and Phase 5.3 manufacturing buildings.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.entities.buildings import (
    BioWasteTreatment,
    ToxicIncinerator,
    CoalOven,
    CrudeOilRefinery,
    LandfillGasPlant,
    CircuitBoardFab,
    MotorAssembly,
    BatteryFab
)


def test_bio_waste_treatment():
    """Test bio-waste treatment plant."""
    print("Testing Bio-Waste Treatment Plant...")

    # Test initialization
    plant = BioWasteTreatment(10, 10)
    assert plant.name == 'Bio-Waste Treatment Plant'
    assert plant.base_cost == 8000
    assert plant.width_tiles == 4
    assert plant.height_tiles == 4
    assert plant.power_consumption == 4.0

    # Test special attributes
    assert plant.methane_production_rate == 0.5
    assert plant.pollution_reduction == -2.0

    # Test material acceptance
    assert 'organic' in plant.input_material_types
    assert 'wood' in plant.input_material_types
    assert 'textiles' in plant.input_material_types
    assert 'bio_waste' in plant.input_material_types

    # Test level bonuses
    plant.level = 3
    plant._apply_level_bonuses()
    assert plant.methane_production_rate > 0.5  # Improved with level
    assert plant.pollution_reduction < -2.0  # More reduction

    print(f"  ✓ Bio-Waste Treatment: {plant}")
    print(f"    Methane rate: {plant.methane_production_rate:.2f}kg/kg")
    print(f"    Pollution: {plant.pollution_reduction:.1f}\n")


def test_toxic_incinerator():
    """Test toxic incinerator."""
    print("Testing Toxic Incinerator...")

    # Test initialization
    incinerator = ToxicIncinerator(10, 10)
    assert incinerator.name == 'Toxic Incinerator'
    assert incinerator.base_cost == 10000
    assert incinerator.width_tiles == 3
    assert incinerator.height_tiles == 3
    assert incinerator.power_consumption == 6.0

    # Test special attributes
    assert incinerator.processing_cost == 5.0
    assert incinerator.pollution_output == 3.0
    assert incinerator.ash_production_rate == 0.15

    # Test material acceptance
    assert 'hazardous' in incinerator.input_material_types
    assert 'toxic' in incinerator.input_material_types
    assert 'chemicals' in incinerator.input_material_types

    # Test processing cost calculation
    cost = incinerator.get_processing_cost(100.0)
    assert cost == 500.0  # 100 kg * $5/kg

    # Test level bonuses
    incinerator.level = 3
    incinerator._apply_level_bonuses()
    assert incinerator.processing_cost < 5.0  # Reduced cost
    assert incinerator.pollution_output < 3.0  # Reduced pollution

    print(f"  ✓ Toxic Incinerator: {incinerator}")
    print(f"    Processing cost: ${incinerator.processing_cost:.1f}/kg")
    print(f"    Pollution: {incinerator.pollution_output:.1f}\n")


def test_coal_oven():
    """Test coal oven."""
    print("Testing Coal Oven...")

    # Test initialization
    oven = CoalOven(10, 10)
    assert oven.name == 'Coal Oven'
    assert oven.base_cost == 6000
    assert oven.width_tiles == 3
    assert oven.height_tiles == 3
    assert oven.power_consumption == 3.0

    # Test special attributes
    assert oven.charcoal_yield == 0.40
    assert oven.pollution_output == 2.0
    assert oven.heat_output == 5.0

    # Test material acceptance
    assert 'wood' in oven.input_material_types
    assert 'organic' in oven.input_material_types
    assert 'textiles' in oven.input_material_types

    # Test level bonuses
    oven.level = 3
    oven._apply_level_bonuses()
    assert oven.charcoal_yield > 0.40  # Improved yield
    assert oven.pollution_output < 2.0  # Reduced pollution

    print(f"  ✓ Coal Oven: {oven}")
    print(f"    Charcoal yield: {oven.charcoal_yield:.1%}")
    print(f"    Heat output: {oven.heat_output:.1f}\n")


def test_crude_oil_refinery():
    """Test crude oil refinery."""
    print("Testing Crude Oil Refinery...")

    # Test initialization
    refinery = CrudeOilRefinery(10, 10)
    assert refinery.name == 'Crude Oil Refinery'
    assert refinery.base_cost == 15000
    assert refinery.width_tiles == 5
    assert refinery.height_tiles == 5
    assert refinery.power_consumption == 8.0

    # Test special attributes
    assert refinery.refining_efficiency == 0.85
    assert refinery.pollution_output == 4.0
    assert len(refinery.valuable_byproducts) == 3

    # Test material acceptance
    assert 'petroleum' in refinery.input_material_types
    assert 'oil' in refinery.input_material_types
    assert 'plastic' in refinery.input_material_types
    assert 'rubber' in refinery.input_material_types

    # Test level bonuses
    refinery.level = 3
    refinery._apply_level_bonuses()
    assert refinery.refining_efficiency > 0.85  # Improved efficiency
    # Quality distribution should be better
    assert refinery.quality_distribution['high'] > 0.25

    print(f"  ✓ Crude Oil Refinery: {refinery}")
    print(f"    Refining efficiency: {refinery.refining_efficiency:.1%}")
    print(f"    Pollution: {refinery.pollution_output:.1f}\n")


def test_landfill_gas_plant():
    """Test landfill gas plant."""
    print("Testing Landfill Gas Plant...")

    # Test initialization
    plant = LandfillGasPlant(10, 10)
    assert plant.name == 'Landfill Gas Plant'
    assert plant.base_cost == 9000
    assert plant.width_tiles == 4
    assert plant.height_tiles == 4
    assert plant.power_consumption == 2.0

    # Test special attributes
    assert plant.methane_production_rate == 0.60
    assert plant.pollution_reduction == -1.5
    assert plant.digestate_production == 0.25

    # Test material acceptance
    assert 'bio_waste' in plant.input_material_types
    assert 'organic' in plant.input_material_types

    # Test methane calculation
    methane_output = plant.get_methane_output(100.0)
    assert methane_output > 0
    assert methane_output == 100.0 * 0.60 * 0.88  # input * rate * efficiency

    # Test level bonuses
    plant.level = 3
    plant._apply_level_bonuses()
    assert plant.methane_production_rate > 0.60  # Improved rate
    assert plant.pollution_reduction < -1.5  # More reduction

    print(f"  ✓ Landfill Gas Plant: {plant}")
    print(f"    Methane rate: {plant.methane_production_rate:.1%}")
    print(f"    Pollution: {plant.pollution_reduction:.1f}\n")


def test_circuit_board_fab():
    """Test circuit board fabricator."""
    print("Testing Circuit Board Fabricator...")

    # Test initialization
    fab = CircuitBoardFab(10, 10)
    assert fab.name == 'Circuit Board Fabricator'
    assert fab.base_cost == 18000
    assert fab.width_tiles == 4
    assert fab.height_tiles == 4
    assert fab.power_consumption == 10.0

    # Test recipe
    assert 'copper' in fab.recipe
    assert 'plastic' in fab.recipe
    assert 'chemicals' in fab.recipe
    assert fab.recipe['copper'] == 2.0
    assert fab.recipe['plastic'] == 1.0

    # Test special attributes
    assert fab.output_per_batch == 1.0
    assert fab.batch_value_multiplier == 3.0

    # Test material acceptance
    assert 'copper' in fab.input_material_types
    assert 'plastic' in fab.input_material_types

    # Test level bonuses
    fab.level = 3
    fab._apply_level_bonuses()
    assert fab.output_per_batch > 1.0  # Better yield
    assert fab.quality_distribution['high'] > 0.27  # Better quality

    print(f"  ✓ Circuit Board Fab: {fab}")
    print(f"    Output per batch: {fab.output_per_batch:.1f}kg")
    print(f"    Value multiplier: {fab.batch_value_multiplier:.1f}x\n")


def test_motor_assembly():
    """Test motor assembly plant."""
    print("Testing Motor Assembly...")

    # Test initialization
    assembly = MotorAssembly(10, 10)
    assert assembly.name == 'Motor Assembly'
    assert assembly.base_cost == 16000
    assert assembly.width_tiles == 4
    assert assembly.height_tiles == 4
    assert assembly.power_consumption == 7.0

    # Test recipe
    assert 'iron' in assembly.recipe
    assert 'copper' in assembly.recipe
    assert 'magnets' in assembly.recipe
    assert assembly.recipe['iron'] == 3.0
    assert assembly.recipe['copper'] == 1.5
    assert assembly.recipe['magnets'] == 0.5

    # Test special attributes
    assert assembly.output_per_batch == 1.0
    assert assembly.batch_value_multiplier == 4.0

    # Test material acceptance
    assert 'iron' in assembly.input_material_types
    assert 'steel' in assembly.input_material_types
    assert 'copper' in assembly.input_material_types
    assert 'magnets' in assembly.input_material_types

    # Test level bonuses
    assembly.level = 3
    assembly._apply_level_bonuses()
    assert assembly.output_per_batch > 1.0  # Better yield
    assert assembly.quality_distribution['high'] > 0.25  # Better quality

    print(f"  ✓ Motor Assembly: {assembly}")
    print(f"    Output per batch: {assembly.output_per_batch:.1f} motors")
    print(f"    Value multiplier: {assembly.batch_value_multiplier:.1f}x\n")


def test_battery_fab():
    """Test battery fabrication plant."""
    print("Testing Battery Fabrication...")

    # Test initialization
    fab = BatteryFab(10, 10)
    assert fab.name == 'Battery Fabrication'
    assert fab.base_cost == 20000
    assert fab.width_tiles == 4
    assert fab.height_tiles == 4
    assert fab.power_consumption == 9.0

    # Test recipe
    assert 'lithium' in fab.recipe
    assert 'chemicals' in fab.recipe
    assert 'copper' in fab.recipe
    assert 'plastic' in fab.recipe
    assert fab.recipe['lithium'] == 1.0
    assert fab.recipe['chemicals'] == 2.0

    # Test special attributes
    assert fab.output_per_batch == 1.0
    assert fab.batch_value_multiplier == 5.0
    assert fab.hazard_level == 2

    # Test material acceptance
    assert 'lithium' in fab.input_material_types
    assert 'chemicals' in fab.input_material_types
    assert 'copper' in fab.input_material_types
    assert 'plastic' in fab.input_material_types

    # Test level bonuses
    fab.level = 3
    fab._apply_level_bonuses()
    assert fab.output_per_batch > 1.0  # Better yield
    assert fab.quality_distribution['high'] > 0.22  # Better quality
    assert fab.hazard_level < 2  # Safer with upgrades

    print(f"  ✓ Battery Fabrication: {fab}")
    print(f"    Output per batch: {fab.output_per_batch:.1f}kg")
    print(f"    Value multiplier: {fab.batch_value_multiplier:.1f}x")
    print(f"    Hazard level: {fab.hazard_level}\n")


def test_building_sizes():
    """Test that building sizes are appropriate."""
    print("Testing building sizes and costs...")

    buildings = [
        (BioWasteTreatment(0, 0), 4, 4, 8000),
        (ToxicIncinerator(0, 0), 3, 3, 10000),
        (CoalOven(0, 0), 3, 3, 6000),
        (CrudeOilRefinery(0, 0), 5, 5, 15000),
        (LandfillGasPlant(0, 0), 4, 4, 9000),
        (CircuitBoardFab(0, 0), 4, 4, 18000),
        (MotorAssembly(0, 0), 4, 4, 16000),
        (BatteryFab(0, 0), 4, 4, 20000),
    ]

    for building, expected_w, expected_h, expected_cost in buildings:
        assert building.width_tiles == expected_w
        assert building.height_tiles == expected_h
        assert building.base_cost == expected_cost
        print(f"  ✓ {building.name}: {expected_w}x{expected_h} tiles, ${expected_cost}")

    print()


def test_power_consumption_levels():
    """Test power consumption across all buildings."""
    print("Testing power consumption...")

    buildings = [
        BioWasteTreatment(0, 0),
        ToxicIncinerator(0, 0),
        CoalOven(0, 0),
        CrudeOilRefinery(0, 0),
        LandfillGasPlant(0, 0),
        CircuitBoardFab(0, 0),
        MotorAssembly(0, 0),
        BatteryFab(0, 0),
    ]

    for building in buildings:
        assert building.power_consumption > 0
        print(f"  {building.name:30s}: {building.power_consumption:5.1f}W")

    print()


def main():
    """Run all Phase 5 building tests."""
    print("=" * 80)
    print("PHASE 5 BUILDING TESTS")
    print("=" * 80)
    print()

    try:
        # Phase 5.2 tests
        print("PHASE 5.2: ADVANCED PROCESSING BUILDINGS")
        print("-" * 80)
        test_bio_waste_treatment()
        test_toxic_incinerator()
        test_coal_oven()
        test_crude_oil_refinery()
        test_landfill_gas_plant()

        # Phase 5.3 tests
        print("\nPHASE 5.3: MANUFACTURING BUILDINGS")
        print("-" * 80)
        test_circuit_board_fab()
        test_motor_assembly()
        test_battery_fab()

        # Additional tests
        print("\nADDITIONAL TESTS")
        print("-" * 80)
        test_building_sizes()
        test_power_consumption_levels()

        print("=" * 80)
        print("ALL PHASE 5 TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Phase 5.2: 5 Advanced Processing Buildings implemented")
        print("Phase 5.3: 3 Manufacturing Buildings implemented")
        print()
        print("Features tested:")
        print("  - Bio-waste treatment with methane production")
        print("  - Toxic waste incineration (costs money to process)")
        print("  - Coal/charcoal production from wood")
        print("  - Petroleum refining into fuels")
        print("  - Landfill gas to methane conversion")
        print("  - Circuit board manufacturing (multi-input)")
        print("  - Electric motor assembly (multi-input)")
        print("  - Battery fabrication (multi-input, hazardous)")
        print("  - Level bonuses and upgrades")
        print("  - Pollution reduction/generation")
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
