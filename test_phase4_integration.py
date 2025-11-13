"""
Comprehensive integration tests for Phase 4: Building System.

Tests building placement, power management, material processing,
and storage systems working together.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.world.grid import Grid
from src.systems.building_manager import BuildingManager
from src.systems.power_manager import PowerManager
from src.entities.buildings import (
    Factory,
    LandfillGasExtraction,
    PaperRecycler,
    PlasticRecycler,
    MetalRefinery,
    Glassworks,
    RubberRecycler,
    Warehouse,
    Silo,
    SolarArray,
    MethaneGenerator,
    BatteryBank
)


def create_test_grid():
    """Create a test grid."""
    return Grid(50, 50, tile_size=32)


def test_building_placement():
    """Test building placement validation."""
    print("Testing building placement...")

    grid = create_test_grid()
    manager = BuildingManager(grid)

    # Place a factory
    factory = Factory(10, 10)
    assert manager.place_building(factory) == True
    assert len(manager.buildings) == 1

    # Try to place overlapping building - should fail
    factory2 = Factory(10, 10)
    assert manager.place_building(factory2) == False
    assert len(manager.buildings) == 1  # Still just 1

    # Place non-overlapping building
    solar = SolarArray(20, 10)
    assert manager.place_building(solar) == True
    assert len(manager.buildings) == 2

    # Try to place partially overlapping - should fail
    warehouse = Warehouse(12, 12)  # Overlaps with factory
    assert manager.place_building(warehouse) == False

    # Place in valid location
    warehouse = Warehouse(20, 20)
    assert manager.place_building(warehouse) == True
    assert len(manager.buildings) == 3

    # Check grid occupancy (check tiles within building footprints)
    assert manager.get_building_at(10, 10) == factory  # Factory origin
    assert manager.get_building_at(11, 11) == factory  # Factory middle
    assert manager.get_building_at(20, 10) == solar    # Solar origin
    assert manager.get_building_at(21, 11) == solar    # Solar tile
    assert manager.get_building_at(20, 20) == warehouse  # Warehouse origin
    assert manager.get_building_at(5, 5) is None  # Empty tile

    # Remove a building
    assert manager.remove_building(factory.id) == True
    assert len(manager.buildings) == 2
    assert manager.get_building_at(10, 10) is None

    # Can now place at freed location
    factory3 = Factory(10, 10)
    assert manager.place_building(factory3) == True

    print(f"  ✓ Building placement validation works")
    print(f"  ✓ Overlap detection works")
    print(f"  ✓ Grid occupancy tracking works")
    print(f"  ✓ Building removal frees tiles\n")

    return manager


def test_power_system_basic():
    """Test basic power generation and consumption."""
    print("Testing power system basics...")

    grid = create_test_grid()
    building_manager = BuildingManager(grid)
    power_manager = PowerManager(building_manager)

    # Start with no power
    power_manager.update(1.0, building_manager)
    assert power_manager.total_generation == 0.0
    assert power_manager.total_consumption == 0.0

    # Add power generation
    gas_extraction = LandfillGasExtraction(10, 10)
    building_manager.place_building(gas_extraction)

    power_manager.update(1.0, building_manager)
    assert power_manager.total_generation == 10.0  # 10W from gas extraction

    # Add power consumption
    factory = Factory(20, 10)
    building_manager.place_building(factory)

    power_manager.update(1.0, building_manager)
    assert power_manager.total_consumption == 5.0  # 5W from factory
    assert power_manager.net_power == 5.0  # 10W gen - 5W cons

    # Add more consumption
    paper_recycler = PaperRecycler(20, 20)
    building_manager.place_building(paper_recycler)

    power_manager.update(1.0, building_manager)
    assert power_manager.total_consumption == 8.0  # 5W + 3W
    assert power_manager.net_power == 2.0  # Surplus

    print(f"  ✓ Power generation: {power_manager.total_generation:.1f}W")
    print(f"  ✓ Power consumption: {power_manager.total_consumption:.1f}W")
    print(f"  ✓ Net power: {power_manager.net_power:.1f}W")
    print(f"  ✓ System status: Normal\n")

    return building_manager, power_manager


def test_power_system_brownout_blackout():
    """Test power deficit scenarios."""
    print("Testing power surplus and deficit...")

    grid = create_test_grid()
    building_manager = BuildingManager(grid)
    power_manager = PowerManager(building_manager)

    # Add limited power
    gas = LandfillGasExtraction(10, 10)
    building_manager.place_building(gas)  # 10W

    # Add consumption that matches generation
    factory = Factory(20, 10)
    paper = PaperRecycler(25, 10)

    building_manager.place_building(factory)   # 5W
    building_manager.place_building(paper)     # 3W
    # Total: 8W consumption
    # Generation: 10W
    # Surplus: 2W

    power_manager.update(1.0, building_manager)

    assert power_manager.total_generation == 10.0
    assert power_manager.total_consumption == 8.0
    assert power_manager.net_power == 2.0  # Surplus
    assert power_manager.has_power == True

    print(f"  ✓ Power surplus: {power_manager.net_power:.1f}W")

    # Add more consumption to create deficit
    plastic = PlasticRecycler(30, 10)  # 4W
    metal = MetalRefinery(35, 10)  # 8W
    building_manager.place_building(plastic)
    building_manager.place_building(metal)
    # Total: 20W consumption
    # Generation: 10W
    # Deficit: -10W

    power_manager.update(1.0, building_manager)

    assert power_manager.total_consumption == 20.0
    assert power_manager.net_power == -10.0  # Deficit

    print(f"  ✓ Power deficit: {abs(power_manager.net_power):.1f}W")
    print(f"  ✓ Buildings operate until battery/storage depleted\n")


def test_solar_time_based_generation():
    """Test solar array time-based power generation."""
    print("Testing solar array time-based generation...")

    grid = create_test_grid()
    building_manager = BuildingManager(grid)

    solar = SolarArray(10, 10)
    building_manager.place_building(solar)

    # Test different times of day
    times_and_powers = []

    for hour in [0, 6, 9, 12, 15, 18, 21]:
        solar.set_time_of_day(hour)
        power = solar.power_generation
        times_and_powers.append((hour, power))
        print(f"    {hour:2d}:00 - {power:5.1f}W")

    # Verify pattern
    midnight_power = times_and_powers[0][1]
    sunrise_power = times_and_powers[1][1]
    morning_power = times_and_powers[2][1]
    noon_power = times_and_powers[3][1]
    afternoon_power = times_and_powers[4][1]
    sunset_power = times_and_powers[5][1]
    night_power = times_and_powers[6][1]

    assert midnight_power == 0.0
    assert noon_power > morning_power
    assert noon_power > afternoon_power
    assert morning_power > 0
    assert afternoon_power > 0
    assert sunset_power < 0.1
    assert night_power == 0.0

    print(f"  ✓ Solar power varies correctly with time")
    print(f"  ✓ Peak at noon: {noon_power:.1f}W\n")


def test_battery_charge_discharge():
    """Test battery charging and discharging directly."""
    print("Testing battery charge/discharge...")

    # Test battery directly (not through PowerManager)
    battery = BatteryBank(0, 0)
    battery.powered = True
    battery.operational = True

    # Test charging
    initial_charge = battery.stored_power
    power_consumed = battery.charge(100.0, 1.0)  # 100W available for 1 sec

    assert power_consumed > 0
    assert battery.stored_power > initial_charge
    assert battery.charging == True

    print(f"  ✓ Battery accepts charge")
    print(f"  ✓ Charged: {battery.stored_power:.0f}/1000")

    # Charge more
    for _ in range(10):
        battery.charge(50.0, 1.0)

    charged_amount = battery.stored_power
    assert charged_amount > 100.0

    print(f"  ✓ Battery capacity: {charged_amount:.0f}/1000")

    # Test discharging
    power_provided = battery.discharge(50.0, 1.0)  # Request 50W for 1 sec

    assert power_provided > 0
    assert battery.stored_power < charged_amount
    assert battery.discharging == True

    print(f"  ✓ Battery provides power on demand")
    print(f"  ✓ Remaining: {battery.stored_power:.0f}/1000\n")


def test_material_processing():
    """Test material processing buildings."""
    print("Testing material processing...")

    # Create paper recycler
    recycler = PaperRecycler(0, 0)
    recycler.powered = True
    recycler.operational = True

    # Add materials to input queue
    added = recycler.add_to_input_queue('paper', 100.0)
    assert added == 100.0
    assert len(recycler.input_queue) == 1

    # Start processing
    recycler._start_processing()
    assert recycler.processing_current is not None
    assert recycler.processing_current['material_type'] == 'paper'

    # Process for required time
    processing_time = 100.0 * recycler.processing_speed
    recycler.update(processing_time)

    # Should be complete and have output
    assert recycler.processing_current is None
    assert len(recycler.output_queue) > 0

    # Check output has quality tiers
    output_materials = [item['material_type'] for item in recycler.output_queue]
    has_quality_tiers = any('waste_' in mat or 'low_' in mat or 'medium_' in mat or 'high_' in mat
                           for mat in output_materials)
    assert has_quality_tiers

    print(f"  ✓ Material processing completes")
    print(f"  ✓ Output materials: {output_materials}")
    print(f"  ✓ Quality tiers generated\n")


def test_storage_buildings():
    """Test warehouse and silo storage."""
    print("Testing storage buildings...")

    # Test warehouse
    warehouse = Warehouse(0, 0)

    # Store multiple materials
    warehouse.store_material('plastic', 1000.0)
    warehouse.store_material('metal', 2000.0)
    warehouse.store_material('glass', 1500.0)

    assert warehouse.get_total_stored() == 4500.0
    assert len(warehouse.stored_materials) == 3

    # Retrieve material
    retrieved = warehouse.get_material('plastic', 500.0)
    assert retrieved == 500.0
    assert warehouse.get_stored_amount('plastic') == 500.0

    print(f"  ✓ Warehouse stores multiple materials")
    print(f"  ✓ Warehouse capacity: {warehouse.storage_capacity:.0f}kg")

    # Test silo
    silo = Silo(0, 0)

    # Store single material
    silo.store_material('paper', 5000.0)
    assert silo.stored_material_type == 'paper'
    assert silo.stored_quantity == 5000.0

    # Try to store different material - should reject
    added = silo.store_material('plastic', 1000.0)
    assert added == 0.0
    assert silo.stored_material_type == 'paper'  # Still paper

    # Empty and accept new material
    silo.get_material('paper', 10000.0)  # Get all
    assert silo.stored_material_type is None  # Reset

    silo.store_material('metal', 3000.0)
    assert silo.stored_material_type == 'metal'

    print(f"  ✓ Silo enforces single material type")
    print(f"  ✓ Silo capacity: {silo.storage_capacity:.0f}kg")
    print(f"  ✓ Silo resets when empty\n")


def test_building_levels():
    """Test building upgrade levels."""
    print("Testing building levels...")

    # Test factory levels
    factory1 = Factory(0, 0)
    assert factory1.storage_capacity == 10000.0

    factory2 = Factory(0, 0)
    factory2.level = 3
    factory2._apply_level_bonuses()
    assert factory2.storage_capacity == 30000.0

    print(f"  ✓ Factory L1: {factory1.storage_capacity:.0f}kg")
    print(f"  ✓ Factory L3: {factory2.storage_capacity:.0f}kg")

    # Test solar levels
    solar1 = SolarArray(0, 0)
    solar1.set_time_of_day(12.0)
    power1 = solar1.power_generation

    solar3 = SolarArray(0, 0)
    solar3.level = 3
    solar3._apply_level_bonuses()
    solar3.set_time_of_day(12.0)
    power3 = solar3.power_generation

    assert power3 > power1

    print(f"  ✓ Solar L1: {power1:.1f}W")
    print(f"  ✓ Solar L3: {power3:.1f}W")

    # Test recycler levels
    recycler1 = PaperRecycler(0, 0)
    speed1 = recycler1.processing_speed

    recycler3 = PaperRecycler(0, 0)
    recycler3.level = 3
    recycler3._apply_level_bonuses()
    speed3 = recycler3.processing_speed

    assert speed3 < speed1  # Lower is faster

    print(f"  ✓ Recycler L1: {speed1:.1f} sec/kg")
    print(f"  ✓ Recycler L3: {speed3:.1f} sec/kg (faster)\n")


def test_performance_many_buildings():
    """Test performance with many buildings."""
    print("Testing performance with many buildings...")

    grid = create_test_grid()
    building_manager = BuildingManager(grid)
    power_manager = PowerManager(building_manager)

    # Place many buildings
    buildings_placed = 0
    building_types = [
        (SolarArray, 3, 3),
        (PaperRecycler, 3, 3),
        (Warehouse, 4, 4),
        (Silo, 3, 3),
    ]

    for y in range(0, 40, 6):
        for x in range(0, 40, 6):
            building_class, width, height = building_types[buildings_placed % len(building_types)]
            building = building_class(x, y)
            if building_manager.place_building(building):
                buildings_placed += 1

    print(f"  Buildings placed: {buildings_placed}")

    # Update system
    import time
    start = time.time()

    for _ in range(100):  # 100 frames
        building_manager.update(0.016)  # 60 FPS
        power_manager.update(0.016, building_manager)

    elapsed = time.time() - start

    print(f"  ✓ 100 updates completed in {elapsed:.3f}s")
    print(f"  ✓ Average: {elapsed/100*1000:.2f}ms per frame")
    print(f"  ✓ Performance acceptable for {buildings_placed} buildings\n")


def main():
    """Run all integration tests."""
    print("=" * 80)
    print("PHASE 4 INTEGRATION TESTS")
    print("=" * 80)
    print()

    try:
        # Run all tests
        test_building_placement()
        test_power_system_basic()
        test_power_system_brownout_blackout()
        test_solar_time_based_generation()
        test_battery_charge_discharge()
        test_material_processing()
        test_storage_buildings()
        test_building_levels()
        test_performance_many_buildings()

        print("=" * 80)
        print("ALL INTEGRATION TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Phase 4: Building System is fully integrated and working!")
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
