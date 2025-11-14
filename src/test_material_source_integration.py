"""
Test end-to-end material source tracking integration.

Tests that materials collected from collectibles are properly tracked
with their source through the entire collection and deposit flow.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.systems.entity_manager import EntityManager
from src.systems.resource_manager import ResourceManager
from src.systems.material_inventory import MaterialInventory, MaterialSource
from src.world.grid import Grid


def test_collectible_source_tracking():
    """Test that collectibles have source attribute."""
    print("Test: Collectible Source Tracking")

    grid = Grid(50, 50)
    material_inventory = MaterialInventory()
    entity_manager = EntityManager(
        grid=grid,
        resource_manager=ResourceManager(),
        material_inventory=material_inventory
    )

    # Create collectible with default source (LANDFILL)
    collectible1 = entity_manager.create_collectible(100, 100, 'plastic', 50)
    assert collectible1.source == MaterialSource.LANDFILL, "Default source should be LANDFILL"

    # Create collectible with illegal source
    collectible2 = entity_manager.create_collectible(200, 200, 'copper', 30, MaterialSource.FENCE)
    assert collectible2.source == MaterialSource.FENCE, "Source should be FENCE"

    print(f"  ✓ Collectible sources tracked correctly")
    print(f"    - collectible1: {collectible1.material_type} from {collectible1.source.value}")
    print(f"    - collectible2: {collectible2.material_type} from {collectible2.source.value}")


def test_robot_source_tracking():
    """Test that robots track material sources."""
    print("\nTest: Robot Source Tracking")

    grid = Grid(50, 50)
    material_inventory = MaterialInventory()
    resources = ResourceManager()
    entity_manager = EntityManager(
        grid=grid,
        resource_manager=resources,
        material_inventory=material_inventory
    )

    # Create robot
    robot = entity_manager.create_robot(100, 100)

    # Add materials with different sources
    robot.add_material('plastic', 25, MaterialSource.LANDFILL)
    robot.add_material('copper', 15, MaterialSource.FENCE)

    # Check robot inventory
    assert robot.inventory['plastic'] == 25, "Should have 25 plastic"
    assert robot.inventory['copper'] == 15, "Should have 15 copper"

    # Check source tracking
    assert robot.material_sources['plastic'] == MaterialSource.LANDFILL, "Plastic source should be LANDFILL"
    assert robot.material_sources['copper'] == MaterialSource.FENCE, "Copper source should be FENCE"

    print(f"  ✓ Robot tracks sources correctly")
    print(f"    - plastic: {robot.inventory['plastic']}kg from {robot.material_sources['plastic'].value}")
    print(f"    - copper: {robot.inventory['copper']}kg from {robot.material_sources['copper'].value}")


def test_deposit_with_source_tracking():
    """Test that depositing materials tracks sources."""
    print("\nTest: Deposit with Source Tracking")

    material_inventory = MaterialInventory()
    resources = ResourceManager()

    # Create materials dict with sources
    materials = {'plastic': 50, 'copper': 30}
    sources = {'plastic': MaterialSource.LANDFILL, 'copper': MaterialSource.FENCE}

    # Deposit materials
    resources.deposit_materials(materials, sources, material_inventory)

    # Check resource manager storage
    assert resources.stored_materials['plastic'] == 50, "Should have 50 plastic in storage"
    assert resources.stored_materials['copper'] == 30, "Should have 30 copper in storage"

    # Check material inventory source tracking
    illegal_materials = material_inventory.get_illegal_materials()
    assert 'copper' in illegal_materials, "Copper should be tracked as illegal"
    assert illegal_materials['copper'] == 30, "Should have 30 illegal copper"
    assert 'plastic' not in illegal_materials, "Plastic should not be illegal (LANDFILL source)"

    # Check total materials
    assert material_inventory.total_materials['plastic'] == 50, "Should have 50 total plastic"
    assert material_inventory.total_materials['copper'] == 30, "Should have 30 total copper"

    print(f"  ✓ Materials deposited with source tracking")
    print(f"    - plastic: 50kg (legal, from LANDFILL)")
    print(f"    - copper: 30kg (illegal, from FENCE)")
    print(f"  ✓ Illegal materials detected: {illegal_materials}")


def test_end_to_end_collection_flow():
    """Test complete flow: collectible → robot → deposit → material inventory."""
    print("\nTest: End-to-End Collection Flow")

    grid = Grid(50, 50)
    material_inventory = MaterialInventory()
    resources = ResourceManager()
    entity_manager = EntityManager(
        grid=grid,
        resource_manager=resources,
        material_inventory=material_inventory
    )

    # Create collectibles with different sources
    collectible1 = entity_manager.create_collectible(100, 100, 'plastic', 50, MaterialSource.LANDFILL)
    collectible2 = entity_manager.create_collectible(105, 105, 'copper', 30, MaterialSource.FENCE)

    # Create robot
    robot = entity_manager.create_robot(100, 100)

    # Simulate collection from collectibles
    amount1 = collectible1.collect(50)
    robot.add_material(collectible1.material_type, amount1, collectible1.source)

    amount2 = collectible2.collect(30)
    robot.add_material(collectible2.material_type, amount2, collectible2.source)

    # Robot should have both materials
    assert robot.inventory['plastic'] == 50, "Robot should have 50 plastic"
    assert robot.inventory['copper'] == 30, "Robot should have 30 copper"
    assert robot.material_sources['plastic'] == MaterialSource.LANDFILL
    assert robot.material_sources['copper'] == MaterialSource.FENCE

    # Simulate deposit via resource manager
    resources.deposit_materials(robot.inventory, robot.material_sources, material_inventory)

    # Check final state
    assert resources.stored_materials['plastic'] == 50
    assert resources.stored_materials['copper'] == 30

    # Check material inventory
    illegal = material_inventory.get_illegal_materials()
    assert 'copper' in illegal and illegal['copper'] == 30, "Copper should be illegal"
    assert 'plastic' not in illegal, "Plastic should be legal"

    illegal_count = material_inventory.get_illegal_material_count()
    assert illegal_count == 30, f"Should have 30 illegal materials, got {illegal_count}"

    print(f"  ✓ Complete collection flow tested")
    print(f"    - Collectible → Robot → Deposit → MaterialInventory")
    print(f"    - Legal materials (plastic): 50kg from LANDFILL")
    print(f"    - Illegal materials (copper): 30kg from FENCE")
    print(f"    - Total illegal count: {illegal_count}")


def run_all_tests():
    """Run all integration tests."""
    print("=" * 80)
    print("MATERIAL SOURCE TRACKING - END-TO-END INTEGRATION TESTS")
    print("=" * 80)
    print()

    try:
        test_collectible_source_tracking()
        test_robot_source_tracking()
        test_deposit_with_source_tracking()
        test_end_to_end_collection_flow()

        print()
        print("=" * 80)
        print("ALL INTEGRATION TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Material Source Tracking Integration Complete:")
        print("  ✓ Collectibles track material source")
        print("  ✓ Robots track material sources during collection")
        print("  ✓ ResourceManager deposits with source tracking")
        print("  ✓ MaterialInventory receives and tracks sources")
        print("  ✓ Illegal materials detected based on source")
        print("  ✓ Complete flow: Collectible → Robot → Deposit → Inspection")

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
