"""
Test script for storage and power buildings.

Tests Warehouse, Silo, Solar Array, Methane Generator, and Battery Bank.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.entities.buildings import (
    Warehouse,
    Silo,
    SolarArray,
    MethaneGenerator,
    BatteryBank
)


def test_warehouse():
    """Test Warehouse building."""
    print("Testing Warehouse...")

    warehouse = Warehouse(10, 10)

    # Test basic properties
    assert warehouse.name == "Warehouse"
    assert warehouse.storage_capacity == 50000.0
    assert warehouse.get_total_stored() == 0.0
    assert warehouse.get_fill_percentage() == 0.0

    # Store different materials
    stored = warehouse.store_material('plastic', 1000.0)
    assert stored == 1000.0
    assert warehouse.get_stored_amount('plastic') == 1000.0

    stored = warehouse.store_material('metal', 2000.0)
    assert stored == 2000.0
    assert warehouse.get_stored_amount('metal') == 2000.0

    assert warehouse.get_total_stored() == 3000.0
    assert len(warehouse.stored_materials) == 2

    # Retrieve materials
    retrieved = warehouse.get_material('plastic', 500.0)
    assert retrieved == 500.0
    assert warehouse.get_stored_amount('plastic') == 500.0

    # Fill to capacity
    available = warehouse.get_available_space()
    stored = warehouse.store_material('paper', available)
    assert stored == available
    assert warehouse.get_fill_percentage() == 1.0

    # Try to overfill
    stored = warehouse.store_material('glass', 100.0)
    assert stored == 0.0

    print(f"  ✓ {warehouse}")
    print(f"  ✓ Stores multiple material types")
    print(f"  ✓ Capacity management works")
    print(f"  ✓ Materials: {list(warehouse.stored_materials.keys())}\n")


def test_warehouse_levels():
    """Test Warehouse upgrade levels."""
    print("Testing Warehouse levels...")

    # Level 1
    w1 = Warehouse(0, 0)
    assert w1.storage_capacity == 50000.0

    # Level 2
    w2 = Warehouse(0, 0)
    w2.level = 2
    w2._apply_level_bonuses()
    assert w2.storage_capacity == 75000.0

    # Level 3
    w3 = Warehouse(0, 0)
    w3.level = 3
    w3._apply_level_bonuses()
    assert w3.storage_capacity == 100000.0

    print(f"  ✓ Level 1: {w1.storage_capacity:.0f}kg")
    print(f"  ✓ Level 2: {w2.storage_capacity:.0f}kg")
    print(f"  ✓ Level 3: {w3.storage_capacity:.0f}kg\n")


def test_silo():
    """Test Silo building."""
    print("Testing Silo...")

    silo = Silo(20, 10)

    # Test basic properties
    assert silo.name == "Silo"
    assert silo.storage_capacity == 100000.0
    assert silo.stored_material_type is None
    assert silo.stored_quantity == 0.0

    # Store first material
    stored = silo.store_material('glass', 5000.0)
    assert stored == 5000.0
    assert silo.stored_material_type == 'glass'
    assert silo.stored_quantity == 5000.0

    # Try to store different material - should reject
    stored = silo.store_material('plastic', 1000.0)
    assert stored == 0.0
    assert silo.stored_material_type == 'glass'  # Still glass

    # Store more of same material
    stored = silo.store_material('glass', 10000.0)
    assert stored == 10000.0
    assert silo.stored_quantity == 15000.0

    # Retrieve material
    retrieved = silo.get_material('plastic', 100.0)  # Wrong type
    assert retrieved == 0.0

    retrieved = silo.get_material('glass', 5000.0)  # Correct type
    assert retrieved == 5000.0
    assert silo.stored_quantity == 10000.0

    # Empty the silo
    retrieved = silo.get_material('glass', 20000.0)
    assert retrieved == 10000.0  # Only had 10000
    assert silo.stored_quantity == 0.0
    assert silo.stored_material_type is None  # Reset when empty

    # Now can store different material
    stored = silo.store_material('metal', 1000.0)
    assert stored == 1000.0
    assert silo.stored_material_type == 'metal'

    print(f"  ✓ {silo}")
    print(f"  ✓ Single material type enforcement")
    print(f"  ✓ 2x capacity of warehouse (100,000kg)")
    print(f"  ✓ Resets material type when empty\n")


def test_solar_array():
    """Test Solar Array building."""
    print("Testing Solar Array...")

    solar = SolarArray(30, 10)

    # Test basic properties
    assert solar.name == "Solar Array"
    assert solar.max_power_generation == 15.0
    assert solar.pollution == 0.0  # Clean energy

    # Test time-based generation
    # Night - no power
    solar.set_time_of_day(0.0)  # Midnight
    assert solar.power_generation == 0.0

    solar.set_time_of_day(3.0)  # 3 AM
    assert solar.power_generation == 0.0

    # Dawn - starting to generate
    solar.set_time_of_day(6.0)  # Sunrise
    assert solar.power_generation < 0.1  # Very close to zero at sunrise

    # Morning - ramping up
    solar.set_time_of_day(9.0)
    morning_power = solar.power_generation
    assert morning_power > 0

    # Noon - peak power
    solar.set_time_of_day(12.0)
    noon_power = solar.power_generation
    assert noon_power > morning_power
    assert noon_power > 10.0  # Should be near max (15 * 0.85 efficiency)

    # Afternoon - declining
    solar.set_time_of_day(15.0)
    afternoon_power = solar.power_generation
    assert 0 < afternoon_power < noon_power

    # Evening - sunset
    solar.set_time_of_day(18.0)
    assert solar.power_generation < 0.1  # Very close to zero at sunset

    # Night - no power
    solar.set_time_of_day(21.0)
    assert solar.power_generation == 0.0

    print(f"  ✓ {solar}")
    print(f"  ✓ Time-based power generation")
    print(f"  ✓ Peak at noon: {noon_power:.1f}W")
    print(f"  ✓ Zero at night")
    print(f"  ✓ Zero pollution (clean energy)\n")


def test_solar_array_levels():
    """Test Solar Array upgrade levels."""
    print("Testing Solar Array levels...")

    # Level 1
    s1 = SolarArray(0, 0)
    s1.set_time_of_day(12.0)  # Noon
    power1 = s1.power_generation

    # Level 2
    s2 = SolarArray(0, 0)
    s2.level = 2
    s2._apply_level_bonuses()
    s2.set_time_of_day(12.0)
    power2 = s2.power_generation

    # Level 3
    s3 = SolarArray(0, 0)
    s3.level = 3
    s3._apply_level_bonuses()
    s3.set_time_of_day(12.0)
    power3 = s3.power_generation

    assert power2 > power1
    assert power3 > power2

    print(f"  ✓ Level 1: {power1:.1f}W (max {s1.max_power_generation:.1f}W)")
    print(f"  ✓ Level 2: {power2:.1f}W (max {s2.max_power_generation:.1f}W)")
    print(f"  ✓ Level 3: {power3:.1f}W (max {s3.max_power_generation:.1f}W)\n")


def test_methane_generator():
    """Test Methane Generator building."""
    print("Testing Methane Generator...")

    generator = MethaneGenerator(40, 10)

    # Test basic properties
    assert generator.name == "Methane Generator"
    assert generator.base_power_generation == 25.0
    assert generator.fuel_type == "pure_methane"
    assert generator.fuel_stored == 0.0

    # No fuel - no power
    generator.powered = True
    generator.operational = True
    generator.update(1.0)
    assert generator.power_generation == 0.0

    # Add fuel
    added = generator.add_fuel(50.0)
    assert added == 50.0
    assert generator.fuel_stored == 50.0

    # Update - should generate power
    generator.update(1.0)
    assert generator.power_generation > 0

    # Fuel should be consumed
    assert generator.fuel_stored < 50.0

    # Run until out of fuel
    initial_fuel = generator.fuel_stored
    for _ in range(30):  # Run for 30 seconds
        generator.update(1.0)

    # Should be out of fuel or very low
    assert generator.fuel_stored < initial_fuel

    # If completely out, no power
    if generator.fuel_stored == 0.0:
        assert generator.power_generation == 0.0

    # Refuel to capacity
    added = generator.add_fuel(200.0)
    assert added == 100.0  # Can only hold max_fuel_storage
    assert generator.fuel_stored == 100.0

    # Try to overfill
    added = generator.add_fuel(50.0)
    assert added == 0.0

    print(f"  ✓ {generator}")
    print(f"  ✓ Fuel consumption and power generation")
    print(f"  ✓ Fuel buffer capacity: {generator.max_fuel_storage}kg")
    print(f"  ✓ Power when fueled: {generator.base_power_generation}W\n")


def test_battery_bank():
    """Test Battery Bank building."""
    print("Testing Battery Bank...")

    battery = BatteryBank(50, 10)

    # Test basic properties
    assert battery.name == "Battery Bank"
    assert battery.max_storage == 1000.0
    assert battery.stored_power == 0.0
    assert battery.pollution == 0.0

    battery.powered = True
    battery.operational = True

    # Charge the battery
    power_consumed = battery.charge(100.0, 1.0)
    assert power_consumed > 0
    assert battery.stored_power > 0
    assert battery.charging == True
    assert battery.discharging == False

    # Continue charging
    for _ in range(20):
        battery.charge(50.0, 1.0)

    # Should have significant charge
    assert battery.stored_power > 500.0
    charge_level = battery.stored_power

    # Discharge the battery
    power_provided = battery.discharge(100.0, 1.0)
    assert power_provided > 0
    assert battery.stored_power < charge_level
    assert battery.charging == False
    assert battery.discharging == True

    # Fully charge
    for _ in range(30):
        battery.charge(100.0, 1.0)

    # Should be at or near capacity
    assert battery.stored_power >= battery.max_storage * 0.95
    assert battery.get_charge_percentage() >= 0.95

    # Can't charge more when full
    power_consumed = battery.charge(100.0, 1.0)
    assert power_consumed == 0.0  # Full

    # Fully discharge
    for _ in range(30):
        battery.discharge(100.0, 1.0)

    # Should be empty or very low
    assert battery.stored_power < battery.max_storage * 0.1

    # Can't discharge when empty
    power_provided = battery.discharge(100.0, 1.0)
    assert power_provided == 0.0  # Empty

    print(f"  ✓ {battery}")
    print(f"  ✓ Charging and discharging")
    print(f"  ✓ Capacity: {battery.max_storage}units")
    print(f"  ✓ Charge rate: {battery.max_charge_rate}units/sec")
    print(f"  ✓ Discharge rate: {battery.max_discharge_rate}units/sec\n")


def test_battery_bank_levels():
    """Test Battery Bank upgrade levels."""
    print("Testing Battery Bank levels...")

    # Level 1
    b1 = BatteryBank(0, 0)
    assert b1.max_storage == 1000.0

    # Level 2
    b2 = BatteryBank(0, 0)
    b2.level = 2
    b2._apply_level_bonuses()
    assert b2.max_storage == 2000.0

    # Level 3
    b3 = BatteryBank(0, 0)
    b3.level = 3
    b3._apply_level_bonuses()
    assert b3.max_storage == 4000.0

    print(f"  ✓ Level 1: {b1.max_storage:.0f} units")
    print(f"  ✓ Level 2: {b2.max_storage:.0f} units (2x)")
    print(f"  ✓ Level 3: {b3.max_storage:.0f} units (4x)\n")


def test_all_buildings_stats():
    """Display stats for all storage and power buildings."""
    print("Storage & Power Buildings Statistics:")
    print("-" * 80)

    buildings = [
        Warehouse(0, 0),
        Silo(0, 0),
        SolarArray(0, 0),
        MethaneGenerator(0, 0),
        BatteryBank(0, 0)
    ]

    for building in buildings:
        print(f"\n{building.name}:")
        print(f"  Size: {building.width_tiles}x{building.height_tiles} tiles")
        print(f"  Cost: ${building.base_cost:,}")
        print(f"  Max level: {building.max_level}")

        if hasattr(building, 'storage_capacity'):
            print(f"  Storage: {building.storage_capacity:,.0f}kg")
        if hasattr(building, 'max_storage'):
            print(f"  Power storage: {building.max_storage:,.0f} units")
        if hasattr(building, 'max_power_generation'):
            print(f"  Max power generation: {building.max_power_generation:.1f}W")
        if hasattr(building, 'base_power_generation'):
            print(f"  Power generation: {building.base_power_generation:.1f}W")
        if building.power_consumption > 0:
            print(f"  Power consumption: {building.power_consumption:.1f}W")
        if hasattr(building, 'pollution') and building.pollution > 0:
            print(f"  Pollution: {building.pollution:.1f}")

    print("\n" + "-" * 80 + "\n")


def main():
    """Run all tests."""
    print("=" * 80)
    print("STORAGE & POWER BUILDINGS TEST SUITE")
    print("=" * 80)
    print()

    try:
        # Storage tests
        test_warehouse()
        test_warehouse_levels()
        test_silo()

        # Power tests
        test_solar_array()
        test_solar_array_levels()
        test_methane_generator()
        test_battery_bank()
        test_battery_bank_levels()

        # Summary
        test_all_buildings_stats()

        print("=" * 80)
        print("ALL TESTS PASSED! ✓")
        print("=" * 80)
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
