"""
Tests for vehicle spawning system.

Tests vehicle spawning, placement, and VehicleManager functionality.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.systems.vehicle_manager import VehicleManager
from src.entities.vehicle import Vehicle
from src.world.grid import Grid


def test_vehicle_creation():
    """Test creating vehicles with different configurations."""
    print("Testing vehicle creation...")

    # Working car
    car = Vehicle(100, 100, 'car', is_scrap=False)
    assert car.vehicle_type == 'car'
    assert not car.is_scrap
    assert not car.legal_to_deconstruct
    assert car.deconstruction_time == 45.0
    print(f"  Working car: legal={car.legal_to_deconstruct}, time={car.deconstruction_time}s")

    # Scrap truck
    truck = Vehicle(200, 200, 'truck', is_scrap=True)
    assert truck.vehicle_type == 'truck'
    assert truck.is_scrap
    assert truck.legal_to_deconstruct
    assert truck.deconstruction_time == 30.0
    print(f"  Scrap truck: legal={truck.legal_to_deconstruct}, time={truck.deconstruction_time}s")

    # Verify material differences
    assert truck.materials['metal'] == 150.0
    assert car.materials['metal'] == 100.0
    print(f"  Car metal: {car.materials['metal']}kg, Truck metal: {truck.materials['metal']}kg")

    print(f"  ✓ Vehicles created with correct properties")
    print()


def test_vehicle_colors():
    """Test that working and scrap vehicles have different color palettes."""
    print("Testing vehicle color schemes...")

    working = Vehicle(300, 300, 'car', is_scrap=False)
    scrap = Vehicle(400, 400, 'car', is_scrap=True)

    # Both should have colors
    assert working.body_color is not None
    assert scrap.body_color is not None

    # Window colors should be different
    assert working.window_color == (100, 150, 200)  # Bright windows
    assert scrap.window_color == (60, 70, 80)  # Faded windows

    print(f"  Working vehicle window: {working.window_color}")
    print(f"  Scrap vehicle window: {scrap.window_color}")
    print(f"  ✓ Working and scrap vehicles have distinct visuals")
    print()


def test_vehicle_manager_initialization():
    """Test VehicleManager initialization."""
    print("Testing VehicleManager initialization...")

    grid = Grid(50, 50, 32)
    manager = VehicleManager(grid)

    assert manager.grid == grid
    assert len(manager.vehicles) == 0
    assert manager.scrap_ratio == 0.3
    print(f"  Scrap ratio: {manager.scrap_ratio}")
    print(f"  Vehicle types: {manager.vehicle_types}")
    print(f"  ✓ VehicleManager initialized correctly")
    print()


def test_vehicle_spawning():
    """Test spawning vehicles in a grid."""
    print("Testing vehicle spawning...")

    # Create a small grid with some buildings
    grid = Grid(30, 30, 32)
    grid.create_test_world()  # Creates buildings and roads

    manager = VehicleManager(grid)
    manager.spawn_vehicles_in_city(seed=123, vehicle_density=0.5)

    # Should have spawned some vehicles
    vehicle_count = len(manager.vehicles)
    assert vehicle_count > 0
    print(f"  Spawned {vehicle_count} vehicles")

    # Check scrap vs working ratio
    scrap_count = sum(1 for v in manager.vehicles if v.is_scrap)
    working_count = vehicle_count - scrap_count

    scrap_ratio = scrap_count / vehicle_count if vehicle_count > 0 else 0
    print(f"  Scrap vehicles: {scrap_count} ({scrap_ratio:.1%})")
    print(f"  Working vehicles: {working_count}")

    # Verify scrap ratio is roughly 30% (with some tolerance for randomness)
    assert 0.1 <= scrap_ratio <= 0.5  # Allow 10-50% range for small sample sizes

    print(f"  ✓ Vehicles spawned with correct distribution")
    print()


def test_vehicle_types_distribution():
    """Test that different vehicle types are spawned."""
    print("Testing vehicle type distribution...")

    grid = Grid(40, 40, 32)
    grid.create_test_world()

    manager = VehicleManager(grid)
    manager.spawn_vehicles_in_city(seed=456, vehicle_density=0.6)

    # Count each type
    type_counts = {}
    for vehicle in manager.vehicles:
        vehicle_type = vehicle.vehicle_type
        type_counts[vehicle_type] = type_counts.get(vehicle_type, 0) + 1

    print(f"  Total vehicles: {len(manager.vehicles)}")
    for vtype, count in type_counts.items():
        percentage = (count / len(manager.vehicles)) * 100 if len(manager.vehicles) > 0 else 0
        print(f"  {vtype}: {count} ({percentage:.1f}%)")

    # Should have at least cars (most common)
    assert 'car' in type_counts
    assert type_counts['car'] > 0

    print(f"  ✓ Vehicle types distributed correctly")
    print()


def test_vehicle_manager_get_vehicle_at():
    """Test getting vehicle at a specific location."""
    print("Testing get_vehicle_at...")

    grid = Grid(20, 20, 32)
    manager = VehicleManager(grid)

    # Add a vehicle manually
    vehicle1 = Vehicle(500, 500, 'car')
    vehicle2 = Vehicle(600, 600, 'truck')
    manager.vehicles.append(vehicle1)
    manager.vehicles.append(vehicle2)

    # Find vehicle at exact location
    found = manager.get_vehicle_at(500, 500, tolerance=5)
    assert found == vehicle1
    print(f"  Found vehicle at (500, 500)")

    # Find vehicle with tolerance
    found = manager.get_vehicle_at(510, 510, tolerance=20)
    assert found == vehicle1
    print(f"  Found vehicle with tolerance")

    # No vehicle at empty location
    found = manager.get_vehicle_at(1000, 1000, tolerance=20)
    assert found is None
    print(f"  No vehicle at (1000, 1000)")

    print(f"  ✓ get_vehicle_at works correctly")
    print()


def test_vehicle_removal():
    """Test removing vehicles."""
    print("Testing vehicle removal...")

    grid = Grid(20, 20, 32)
    manager = VehicleManager(grid)

    # Add vehicles
    vehicle1 = Vehicle(700, 700, 'car')
    vehicle2 = Vehicle(800, 800, 'van')
    manager.vehicles.append(vehicle1)
    manager.vehicles.append(vehicle2)

    assert len(manager.vehicles) == 2

    # Remove one vehicle
    manager.remove_vehicle(vehicle1)
    assert len(manager.vehicles) == 1
    assert vehicle2 in manager.vehicles
    assert vehicle1 not in manager.vehicles
    print(f"  Removed vehicle 1, count: {len(manager.vehicles)}")

    # Remove second vehicle
    manager.remove_vehicle(vehicle2)
    assert len(manager.vehicles) == 0
    print(f"  Removed vehicle 2, count: {len(manager.vehicles)}")

    print(f"  ✓ Vehicle removal works correctly")
    print()


def test_vehicle_deconstruction_completion():
    """Test that vehicles are auto-removed when deconstruction completes."""
    print("Testing vehicle auto-removal on deconstruction...")

    grid = Grid(20, 20, 32)
    manager = VehicleManager(grid)

    # Add a scrap vehicle (fast deconstruction)
    vehicle = Vehicle(900, 900, 'car', is_scrap=True)
    manager.vehicles.append(vehicle)

    # Start deconstruction
    vehicle.start_deconstruction()
    assert len(manager.vehicles) == 1

    # Update with enough time to complete
    manager.update(40.0)  # 30s deconstruction time for scrap + buffer

    # Vehicle should be removed
    assert len(manager.vehicles) == 0
    print(f"  Vehicle auto-removed after deconstruction")

    print(f"  ✓ Vehicle auto-removal on completion works")
    print()


def test_vehicle_stats():
    """Test vehicle statistics."""
    print("Testing vehicle statistics...")

    grid = Grid(20, 20, 32)
    manager = VehicleManager(grid)

    # Add mixed vehicles
    manager.vehicles.append(Vehicle(100, 100, 'car', is_scrap=True))
    manager.vehicles.append(Vehicle(200, 200, 'car', is_scrap=False))
    manager.vehicles.append(Vehicle(300, 300, 'truck', is_scrap=True))
    manager.vehicles.append(Vehicle(400, 400, 'van', is_scrap=False))

    # Start deconstructing one
    manager.vehicles[0].start_deconstruction()

    stats = manager.get_stats()

    assert stats['total'] == 4
    assert stats['scrap'] == 2
    assert stats['working'] == 2
    assert stats['being_deconstructed'] == 1

    print(f"  Total: {stats['total']}")
    print(f"  Scrap: {stats['scrap']}")
    print(f"  Working: {stats['working']}")
    print(f"  Being deconstructed: {stats['being_deconstructed']}")

    print(f"  ✓ Vehicle statistics correct")
    print()


def test_reproducible_spawning():
    """Test that spawning with same seed produces consistent results on same grid."""
    print("Testing reproducible spawning...")

    # Create a single grid
    grid = Grid(25, 25, 32)
    grid.create_test_world()

    # Spawn twice with same seed on same grid
    manager1 = VehicleManager(grid)
    manager1.spawn_vehicles_in_city(seed=789, vehicle_density=0.5)

    # Record first spawn
    first_spawn = []
    for v in manager1.vehicles:
        first_spawn.append((v.world_x, v.world_y, v.vehicle_type, v.is_scrap))

    # Clear and respawn
    manager2 = VehicleManager(grid)
    manager2.spawn_vehicles_in_city(seed=789, vehicle_density=0.5)

    # Should have same number of vehicles
    assert len(manager1.vehicles) == len(manager2.vehicles)
    print(f"  Both spawns created {len(manager1.vehicles)} vehicles")

    # Should have same vehicle types at same positions
    for i, (v1, (x, y, vtype, is_scrap)) in enumerate(zip(manager2.vehicles, first_spawn)):
        assert v1.vehicle_type == vtype
        assert v1.is_scrap == is_scrap
        assert abs(v1.world_x - x) < 1  # Allow tiny floating point differences
        assert abs(v1.world_y - y) < 1

    print(f"  ✓ Spawning is reproducible with same seed")
    print()


def main():
    """Run all tests."""
    print("=" * 80)
    print("VEHICLE SPAWNING SYSTEM TESTS")
    print("=" * 80)
    print()

    try:
        test_vehicle_creation()
        test_vehicle_colors()
        test_vehicle_manager_initialization()
        test_vehicle_spawning()
        test_vehicle_types_distribution()
        test_vehicle_manager_get_vehicle_at()
        test_vehicle_removal()
        test_vehicle_deconstruction_completion()
        test_vehicle_stats()
        test_reproducible_spawning()

        print("=" * 80)
        print("ALL VEHICLE SPAWNING TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Phase 7.3 Features Implemented:")
        print()
        print("VEHICLE SYSTEM:")
        print("  - Working vehicles (illegal to deconstruct, 45s)")
        print("  - Scrap vehicles (legal to deconstruct, 30s)")
        print("  - Different vehicle types: car, truck, van")
        print("  - Distinct visual styles (bright vs rusty/faded)")
        print("  - Random material composition")
        print()
        print("VEHICLE MANAGER:")
        print("  - Spawns vehicles throughout city")
        print("  - Places cars on roads and near buildings")
        print("  - 30% scrap, 70% working distribution")
        print("  - Reproducible spawning with seeds")
        print("  - Auto-removal when deconstruction completes")
        print("  - Vehicle tracking and statistics")
        print()
        print("INTEGRATION:")
        print("  - Integrated into game update/render loop")
        print("  - Vehicles rendered between buildings and entities")
        print("  - Vehicle spawning on game initialization")
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
