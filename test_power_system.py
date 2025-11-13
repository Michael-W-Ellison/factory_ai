"""
Test script for Power System.

Tests:
- PowerManager initialization
- Power generation and consumption tracking
- Brownout and blackout handling
- LandfillGasExtraction power source
- Power degradation over time
- Building power states
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.systems.power_manager import PowerManager
from src.systems.building_manager import BuildingManager
from src.entities.buildings.factory import Factory
from src.entities.buildings.landfill_gas_extraction import LandfillGasExtraction
from src.world.grid import Grid


def test_power_manager_initialization():
    """Test power manager initialization."""
    print("\nTesting power manager initialization...")

    grid = Grid(width_tiles=100, height_tiles=75, tile_size=32)
    building_manager = BuildingManager(grid)
    power_manager = PowerManager(building_manager)

    print(f"  {power_manager}")
    print(f"  Current power: {power_manager.current_power:.1f}")
    print(f"  Max storage: {power_manager.max_storage:.1f}")
    print(f"  Total generation: {power_manager.total_generation:.1f}")
    print(f"  Total consumption: {power_manager.total_consumption:.1f}")
    print(f"  Has power: {power_manager.has_power}")

    assert power_manager.current_power == 0.0, "Should start with no stored power"
    assert power_manager.max_storage == 0.0, "Should start with no storage"
    assert power_manager.total_generation == 0.0, "Should start with no generation"
    assert power_manager.has_power, "Should have power flag by default"

    print("  ✓ Power manager initialization correct")


def test_landfill_gas_extraction():
    """Test landfill gas extraction building."""
    print("\nTesting landfill gas extraction...")

    gas_extraction = LandfillGasExtraction(grid_x=10, grid_y=10)

    print(f"  {gas_extraction}")
    print(f"  Name: {gas_extraction.name}")
    print(f"  Size: {gas_extraction.width_tiles}x{gas_extraction.height_tiles}")
    print(f"  Power generation: {gas_extraction.power_generation:.1f} units")
    print(f"  Methane production: {gas_extraction.methane_production_rate:.1f} units/sec")
    print(f"  Pollution: {gas_extraction.pollution:.1f} units/sec")

    assert gas_extraction.width_tiles == 2, "Should be 2x2 tiles"
    assert gas_extraction.height_tiles == 2, "Should be 2x2 tiles"
    assert gas_extraction.power_generation == 10.0, "Should generate 10 power"
    assert gas_extraction.power_consumption == 0.0, "Should not consume power"

    # Test degradation
    initial_power = gas_extraction.power_generation
    gas_extraction.update(1000.0)  # 1000 seconds
    print(f"  After 1000s degradation: {gas_extraction.power_generation:.2f} units")
    assert gas_extraction.power_generation < initial_power, "Should degrade over time"
    assert gas_extraction.power_generation >= gas_extraction.min_power_generation, "Should not go below minimum"

    print("  ✓ Landfill gas extraction works correctly")


def test_power_generation_consumption():
    """Test power generation and consumption tracking."""
    print("\nTesting power generation and consumption...")

    grid = Grid(width_tiles=100, height_tiles=75, tile_size=32)
    building_manager = BuildingManager(grid)
    power_manager = PowerManager(building_manager)

    # Add power generation building
    gas_extraction = LandfillGasExtraction(grid_x=10, grid_y=10)
    building_manager.place_building(gas_extraction)

    # Add power consuming building
    factory = Factory(grid_x=20, grid_y=20)
    building_manager.place_building(factory)

    # Update power manager
    power_manager.update(1.0, building_manager)

    status = power_manager.get_power_status()
    print(f"  Generation: {status['generation']:.1f} units/sec")
    print(f"  Consumption: {status['consumption']:.1f} units/sec")
    print(f"  Net power: {status['net']:.1f} units/sec")
    print(f"  Has power: {status['has_power']}")

    assert status['generation'] == 10.0, "Should have 10 units generation"
    assert status['consumption'] == 5.0, "Factory consumes 5 units"
    assert status['net'] == 5.0, "Net should be 5 units surplus"
    assert status['has_power'], "Should have power"

    print("  ✓ Power tracking works correctly")


def test_brownout():
    """Test brownout (consumption > generation)."""
    print("\nTesting brownout scenario...")

    grid = Grid(width_tiles=100, height_tiles=75, tile_size=32)
    building_manager = BuildingManager(grid)
    power_manager = PowerManager(building_manager)

    # Add small power generation
    gas_extraction = LandfillGasExtraction(grid_x=10, grid_y=10)
    gas_extraction.power_generation = 3.0  # Reduced to 3 units
    building_manager.place_building(gas_extraction)

    # Add factory consuming 5 units
    factory = Factory(grid_x=20, grid_y=20)
    building_manager.place_building(factory)

    # Add battery storage
    power_manager.add_battery_storage(1000.0)
    power_manager.current_power = 500.0  # Start with some stored power

    # Update
    power_manager.update(1.0, building_manager)

    status = power_manager.get_power_status()
    print(f"  Generation: {status['generation']:.1f} units/sec")
    print(f"  Consumption: {status['consumption']:.1f} units/sec")
    print(f"  Net power: {status['net']:.1f} units/sec")
    print(f"  Stored power: {status['stored']:.1f}/{status['storage_capacity']:.1f}")
    print(f"  Brownout: {status['brownout']}")
    print(f"  Has power: {status['has_power']}")

    assert status['generation'] < status['consumption'], "Consumption should exceed generation"
    assert status['brownout'], "Should be in brownout"
    assert status['has_power'], "Should still have power from batteries"
    assert status['stored'] < 500.0, "Should have used some stored power"

    print("  ✓ Brownout handling works correctly")


def test_blackout():
    """Test blackout (no power available)."""
    print("\nTesting blackout scenario...")

    grid = Grid(width_tiles=100, height_tiles=75, tile_size=32)
    building_manager = BuildingManager(grid)
    power_manager = PowerManager(building_manager)

    # Add factory consuming power
    factory = Factory(grid_x=20, grid_y=20)
    building_manager.place_building(factory)

    # No power generation, no batteries

    # Update
    power_manager.update(1.0, building_manager)

    status = power_manager.get_power_status()
    print(f"  Generation: {status['generation']:.1f} units/sec")
    print(f"  Consumption: {status['consumption']:.1f} units/sec")
    print(f"  Blackout: {status['blackout']}")
    print(f"  Has power: {status['has_power']}")
    print(f"  Factory powered: {factory.powered}")

    assert status['generation'] == 0.0, "No power generation"
    assert status['consumption'] > 0.0, "Factory wants power"
    assert status['blackout'], "Should be in blackout"
    assert not status['has_power'], "Should have no power"
    assert not factory.powered, "Factory should be unpowered"

    print("  ✓ Blackout handling works correctly")


def test_battery_storage():
    """Test battery storage system."""
    print("\nTesting battery storage...")

    grid = Grid(width_tiles=100, height_tiles=75, tile_size=32)
    building_manager = BuildingManager(grid)
    power_manager = PowerManager(building_manager)

    # Add power generation
    gas_extraction = LandfillGasExtraction(grid_x=10, grid_y=10)
    gas_extraction.power_generation = 20.0  # Lots of surplus
    building_manager.place_building(gas_extraction)

    # Add small consumption
    factory = Factory(grid_x=20, grid_y=20)
    factory.power_consumption = 2.0  # Reduced
    building_manager.place_building(factory)

    # Add battery storage
    power_manager.add_battery_storage(1000.0)

    print(f"  Initial stored: {power_manager.current_power:.1f}")

    # Update for 10 seconds to charge
    for i in range(10):
        power_manager.update(1.0, building_manager)

    status = power_manager.get_power_status()
    print(f"  After 10s:")
    print(f"    Net power: {status['net']:.1f} units/sec")
    print(f"    Stored: {status['stored']:.1f}/{status['storage_capacity']:.1f}")
    print(f"    Storage percent: {status['storage_percent']:.1f}%")

    assert status['stored'] > 0, "Should have charged batteries"
    assert status['stored'] <= status['storage_capacity'], "Should not exceed capacity"

    # Remove battery storage
    power_manager.remove_battery_storage(500.0)
    print(f"  After removing 500 capacity:")
    print(f"    Storage capacity: {power_manager.max_storage:.1f}")
    print(f"    Stored: {power_manager.current_power:.1f}")

    assert power_manager.max_storage == 500.0, "Should have 500 capacity remaining"

    print("  ✓ Battery storage works correctly")


def test_power_surplus_and_deficit():
    """Test transitions between surplus and deficit."""
    print("\nTesting power surplus and deficit transitions...")

    grid = Grid(width_tiles=100, height_tiles=75, tile_size=32)
    building_manager = BuildingManager(grid)
    power_manager = PowerManager(building_manager)

    # Add adjustable power generation
    gas_extraction = LandfillGasExtraction(grid_x=10, grid_y=10)
    building_manager.place_building(gas_extraction)

    # Add factory
    factory = Factory(grid_x=20, grid_y=20)
    building_manager.place_building(factory)

    # Add battery
    power_manager.add_battery_storage(1000.0)

    # Surplus scenario
    gas_extraction.power_generation = 20.0
    power_manager.update(1.0, building_manager)
    status = power_manager.get_power_status()
    print(f"  Surplus (20 gen, 5 cons):")
    print(f"    Net: {status['net']:.1f} (should be +15)")
    print(f"    Stored: {status['stored']:.1f}")
    assert status['net'] > 0, "Should have surplus"
    assert not status['brownout'], "Should not be in brownout"

    # Balanced scenario
    gas_extraction.power_generation = 5.0
    power_manager.update(1.0, building_manager)
    status = power_manager.get_power_status()
    print(f"\n  Balanced (5 gen, 5 cons):")
    print(f"    Net: {status['net']:.1f} (should be 0)")
    print(f"    Brownout: {status['brownout']}")
    assert abs(status['net']) < 0.1, "Should be balanced"

    # Deficit scenario (with batteries)
    gas_extraction.power_generation = 2.0
    power_manager.update(1.0, building_manager)
    status = power_manager.get_power_status()
    print(f"\n  Deficit (2 gen, 5 cons):")
    print(f"    Net: {status['net']:.1f} (should be -3)")
    print(f"    Stored: {status['stored']:.1f}")
    print(f"    Brownout: {status['brownout']}")
    print(f"    Has power: {status['has_power']}")
    assert status['net'] < 0, "Should have deficit"
    assert status['brownout'], "Should be in brownout"
    assert status['has_power'], "Should still have power from batteries"

    print("\n  ✓ Power transitions work correctly")


def test_building_can_operate_without_power():
    """Test that buildings stop operating without power."""
    print("\nTesting building operation without power...")

    grid = Grid(width_tiles=100, height_tiles=75, tile_size=32)
    building_manager = BuildingManager(grid)
    power_manager = PowerManager(building_manager)

    # Create factory
    factory = Factory(grid_x=20, grid_y=20)
    building_manager.place_building(factory)

    print(f"  Factory powered: {factory.powered}")
    print(f"  Factory can operate: {factory.can_operate()}")
    assert factory.can_operate(), "Should operate with power"

    # Cause blackout
    power_manager.update(1.0, building_manager)

    print(f"  After blackout:")
    print(f"    Factory powered: {factory.powered}")
    print(f"    Factory can operate: {factory.can_operate()}")
    assert not factory.powered, "Should be unpowered"
    assert not factory.can_operate(), "Should not operate without power"

    print("  ✓ Building power state affects operation correctly")


if __name__ == '__main__':
    print("=" * 80)
    print("POWER SYSTEM TESTS")
    print("=" * 80)

    try:
        test_power_manager_initialization()
        test_landfill_gas_extraction()
        test_power_generation_consumption()
        test_brownout()
        test_blackout()
        test_battery_storage()
        test_power_surplus_and_deficit()
        test_building_can_operate_without_power()

        print("\n" + "=" * 80)
        print("ALL POWER SYSTEM TESTS PASSED! ✓")
        print("=" * 80)
        print("\nSummary:")
        print("  - PowerManager initialization: ✓")
        print("  - Landfill gas extraction: ✓")
        print("  - Power generation/consumption tracking: ✓")
        print("  - Brownout handling: ✓")
        print("  - Blackout handling: ✓")
        print("  - Battery storage system: ✓")
        print("  - Power surplus/deficit transitions: ✓")
        print("  - Building operation without power: ✓")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
