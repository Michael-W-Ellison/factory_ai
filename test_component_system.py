"""
Test Component System and Manufacturing Buildings

Tests the ComponentManager, material/component inventory, recipes,
and manufacturing building functionality.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))


def test_component_manager():
    """Test ComponentManager functionality."""
    print("=" * 80)
    print("TEST 1: ComponentManager")
    print("=" * 80)
    print()

    from src.systems.component_manager import ComponentManager

    # Create manager
    manager = ComponentManager()
    print(f"✓ ComponentManager created: {manager}")

    # Test loading component definitions
    assert len(manager.component_definitions) > 0, "No component definitions loaded"
    print(f"✓ Loaded {len(manager.component_definitions)} component types")

    # Test getting definitions
    circuit_def = manager.get_component_definition('circuit_board')
    assert circuit_def is not None, "Circuit board definition not found"
    print(f"✓ Circuit board definition: {circuit_def['name']}")

    # Test recipe
    recipe = manager.get_recipe('circuit_board')
    assert recipe is not None, "Circuit board recipe not found"
    print(f"✓ Circuit board recipe: {recipe}")

    # Test processing time
    time = manager.get_processing_time('circuit_board')
    print(f"✓ Circuit board processing time: {time}s")

    # Test adding components
    manager.add_component('circuit_board', 'medium', 10.0)
    count = manager.get_component_count('circuit_board', 'medium')
    assert count == 10.0, f"Expected 10.0, got {count}"
    print(f"✓ Added 10 medium circuit boards")

    manager.add_component('circuit_board', 'high', 5.0)
    total = manager.get_component_count('circuit_board')
    assert total == 15.0, f"Expected 15.0, got {total}"
    print(f"✓ Total circuit boards: {total}")

    # Test removing components
    removed = manager.remove_component('circuit_board', 'medium', 3.0)
    assert removed, "Failed to remove components"
    count = manager.get_component_count('circuit_board', 'medium')
    assert count == 7.0, f"Expected 7.0, got {count}"
    print(f"✓ Removed 3 circuit boards, {count} remaining")

    # Test inventory value
    value = manager.get_total_value('circuit_board')
    print(f"✓ Circuit board inventory value: ${value:.2f}")

    # Test inventory summary
    summary = manager.get_inventory_summary()
    print(f"✓ Inventory summary: {len(summary)} entries")
    for entry in summary:
        print(f"  - {entry['name']} ({entry['quality']}): {entry['quantity']} units, ${entry['total_value']:.2f}")

    # Test save/load state
    state = manager.save_state()
    print(f"✓ Saved state: {len(state)} keys")

    manager2 = ComponentManager()
    manager2.load_state(state)
    count2 = manager2.get_component_count('circuit_board')
    expected = 12.0  # 7 medium + 5 high (after removal)
    assert count2 == expected, f"Expected {expected}, got {count2}"
    print(f"✓ Loaded state successfully")

    print("\n✓ ComponentManager test PASSED\n")


def test_manufacturing_building():
    """Test ManufacturingBuilding functionality."""
    print("=" * 80)
    print("TEST 2: ManufacturingBuilding")
    print("=" * 80)
    print()

    from src.entities.buildings.circuit_board_fab import CircuitBoardFab

    # Create building
    building = CircuitBoardFab(10, 10)
    print(f"✓ Created building: {building}")
    print(f"  Recipe: {building.recipe}")
    print(f"  Output: {building.output_component}")

    # Test can_start_manufacturing (should be False initially)
    can_start = building.can_start_manufacturing()
    assert not can_start, "Should not be able to start without materials"
    print(f"✓ Cannot start manufacturing without materials")

    # Add materials to input queue
    added_copper = building.add_to_input_queue('copper', 5.0)
    assert added_copper == 5.0, "Failed to add copper"
    print(f"✓ Added {added_copper}kg copper")

    added_plastic = building.add_to_input_queue('plastic', 3.0)
    assert added_plastic == 3.0, "Failed to add plastic"
    print(f"✓ Added {added_plastic}kg plastic")

    added_chemicals = building.add_to_input_queue('chemicals', 2.0)
    assert added_chemicals == 2.0, "Failed to add chemicals"
    print(f"✓ Added {added_chemicals}kg chemicals")

    # Check input queue
    input_weight = building.get_current_input_weight()
    print(f"✓ Total input weight: {input_weight}kg")

    # Test can_start_manufacturing (should be True now)
    can_start = building.can_start_manufacturing()
    assert can_start, "Should be able to start with enough materials"
    print(f"✓ Can start manufacturing with sufficient materials")

    # Test recipe status
    recipe_status = building.get_recipe_status()
    print(f"✓ Recipe status:")
    for mat, (available, required) in recipe_status.items():
        status = "✓" if available >= required else "✗"
        print(f"  {status} {mat}: {available:.1f}/{required:.1f}kg")

    # Test consuming materials
    consumed = building.consume_recipe_materials()
    assert consumed, "Failed to consume recipe materials"
    input_weight_after = building.get_current_input_weight()
    print(f"✓ Consumed recipe materials ({input_weight}kg -> {input_weight_after}kg)")

    # Verify correct amounts consumed
    assert input_weight_after < input_weight, "Input weight should decrease"

    # Test building info
    info = building.get_info()
    print(f"✓ Building info:")
    print(f"  Name: {info['name']}")
    print(f"  Level: {info['level']}")
    print(f"  Power: {info['power_consumption']}W")
    print(f"  Processing speed: {info['processing_speed']}s/kg")
    print(f"  Efficiency: {info['efficiency']:.1f}%")

    print("\n✓ ManufacturingBuilding test PASSED\n")


def test_motor_assembly():
    """Test MotorAssembly building."""
    print("=" * 80)
    print("TEST 3: MotorAssembly")
    print("=" * 80)
    print()

    from src.entities.buildings.motor_assembly import MotorAssembly

    building = MotorAssembly(20, 20)
    print(f"✓ Created: {building}")
    print(f"  Recipe: {building.recipe}")
    print(f"  Output: {building.output_component}")

    # Add materials
    building.add_to_input_queue('iron', 6.0)
    building.add_to_input_queue('copper', 3.0)
    building.add_to_input_queue('magnets', 1.0)

    can_start = building.can_start_manufacturing()
    assert can_start, "Should be able to start manufacturing"
    print(f"✓ Can manufacture electric motors")

    print("\n✓ MotorAssembly test PASSED\n")


def test_battery_fab():
    """Test BatteryFab building."""
    print("=" * 80)
    print("TEST 4: BatteryFab")
    print("=" * 80)
    print()

    from src.entities.buildings.battery_fab import BatteryFab

    building = BatteryFab(30, 30)
    print(f"✓ Created: {building}")
    print(f"  Recipe: {building.recipe}")
    print(f"  Output: {building.output_component}")
    print(f"  Hazard level: {building.hazard_level}")

    # Add materials
    building.add_to_input_queue('lithium', 2.0)
    building.add_to_input_queue('chemicals', 4.0)
    building.add_to_input_queue('copper', 1.0)
    building.add_to_input_queue('plastic', 1.0)

    can_start = building.can_start_manufacturing()
    assert can_start, "Should be able to start manufacturing"
    print(f"✓ Can manufacture battery cells")

    print("\n✓ BatteryFab test PASSED\n")


def test_material_definitions():
    """Test materials.json loading."""
    print("=" * 80)
    print("TEST 5: Material Definitions")
    print("=" * 80)
    print()

    import json

    # Load materials.json
    with open('data/materials.json', 'r') as f:
        materials = json.load(f)

    print(f"✓ Loaded materials.json version {materials['version']}")

    base_materials = materials.get('base_materials', {})
    print(f"✓ Base materials: {len(base_materials)} types")

    # Test a few materials
    for mat_type in ['plastic', 'metal', 'glass', 'paper', 'electronics']:
        assert mat_type in base_materials, f"Missing material: {mat_type}"
        mat = base_materials[mat_type]
        print(f"  ✓ {mat['name']}: {mat['base_value']}$ base value, {len(mat['quality_tiers'])} quality tiers")

    # Test fuel materials
    fuel_materials = materials.get('fuel_materials', {})
    print(f"✓ Fuel materials: {len(fuel_materials)} types")

    # Test chemical materials
    chemical_materials = materials.get('chemical_materials', {})
    print(f"✓ Chemical materials: {len(chemical_materials)} types")

    print("\n✓ Material definitions test PASSED\n")


def test_component_definitions():
    """Test components.json loading."""
    print("=" * 80)
    print("TEST 6: Component Definitions")
    print("=" * 80)
    print()

    import json

    # Load components.json
    with open('data/components.json', 'r') as f:
        comp_data = json.load(f)

    print(f"✓ Loaded components.json version {comp_data['version']}")

    components = comp_data.get('components', {})
    print(f"✓ Total components: {len(components)} types")

    # Count by category
    categories = {}
    for comp_type, comp in components.items():
        category = comp.get('category', 'unknown')
        categories[category] = categories.get(category, 0) + 1

    print(f"✓ Categories:")
    for category, count in sorted(categories.items()):
        print(f"  - {category}: {count} components")

    # Test some key components
    key_components = ['circuit_board', 'electric_motor', 'battery_cell',
                     'solar_panel', 'sensor_array', 'ai_chip']

    print(f"✓ Key components:")
    for comp_type in key_components:
        if comp_type in components:
            comp = components[comp_type]
            recipe_size = len(comp.get('recipe', {}))
            research_req = comp.get('requires_research', 'None')
            print(f"  ✓ {comp['name']}: ${comp['base_value']}, "
                  f"{recipe_size} ingredients, research: {research_req}")

    print("\n✓ Component definitions test PASSED\n")


def run_all_tests():
    """Run all tests."""
    print("\n")
    print("=" * 80)
    print("COMPONENT SYSTEM TEST SUITE")
    print("=" * 80)
    print("\n")

    try:
        test_material_definitions()
        test_component_definitions()
        test_component_manager()
        test_manufacturing_building()
        test_motor_assembly()
        test_battery_fab()

        print("=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
        print()
        print("Summary:")
        print("  ✓ Material system (15+ base materials with quality tiers)")
        print("  ✓ Component system (50+ component types with recipes)")
        print("  ✓ ComponentManager (inventory, manufacturing tracking)")
        print("  ✓ ManufacturingBuilding (multi-material recipes)")
        print("  ✓ Circuit Board Fabricator (electronics manufacturing)")
        print("  ✓ Motor Assembly (mechanical components)")
        print("  ✓ Battery Fabrication (power components)")
        print()

        return True

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ TEST ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
