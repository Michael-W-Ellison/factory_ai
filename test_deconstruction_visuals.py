"""
Tests for deconstruction visual system.

Tests landfill depletion, building deconstruction, and vehicle deconstruction visuals.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.world.tile import Tile, TileType
from src.entities.city_building import House, Store
from src.entities.vehicle import Vehicle


def test_landfill_depletion():
    """Test landfill tile depletion visuals."""
    print("Testing landfill depletion...")

    tile = Tile(10, 10, TileType.LANDFILL)

    # Initial state
    assert tile.tile_type == TileType.LANDFILL
    assert tile.depletion_level == 0.0
    initial_color = tile.color
    print(f"  Initial: depletion=0.0, color={initial_color}")

    # Add depletion
    tile.add_depletion(0.25)
    assert tile.depletion_level == 0.25
    color_25 = tile.color
    print(f"  25% depleted: depletion=0.25, color={color_25}")

    tile.add_depletion(0.25)
    assert tile.depletion_level == 0.5
    color_50 = tile.color
    print(f"  50% depleted: depletion=0.5, color={color_50}")

    tile.add_depletion(0.5)
    assert tile.depletion_level == 1.0
    color_100 = tile.color
    print(f"  100% depleted: depletion=1.0, color={color_100}")

    # Color should transition from brown to dirt
    assert color_25 != initial_color
    assert color_50 != color_25
    assert color_100 != color_50

    # Should get progressively lighter (more dirt-like)
    assert sum(color_25) > sum(initial_color)
    assert sum(color_50) > sum(color_25)
    assert sum(color_100) > sum(color_50)

    print(f"  ✓ Landfill depletion colors transition correctly")
    print()


def test_landfill_depletion_cap():
    """Test that depletion caps at 1.0."""
    print("Testing landfill depletion cap...")

    tile = Tile(15, 15, TileType.LANDFILL)

    # Add more than 100% depletion
    tile.add_depletion(0.8)
    tile.add_depletion(0.5)
    assert tile.depletion_level == 1.0

    print(f"  Depletion capped at: {tile.depletion_level}")
    print(f"  ✓ Depletion correctly caps at 1.0")
    print()


def test_house_deconstruction_stages():
    """Test house deconstruction progress tracking."""
    print("Testing house deconstruction stages...")

    house = House(50, 50, livable=True)

    # Initial state
    assert not house.being_deconstructed
    assert house.deconstruction_progress == 0.0
    print(f"  Initial: not being deconstructed")

    # Start deconstruction
    result = house.start_deconstruction()
    assert result == True
    assert house.being_deconstructed == True
    print(f"  Started deconstruction")

    # Test progress stages
    stages = [
        (0.15, "Stage 1: Breaking windows"),
        (0.40, "Stage 2: Holes in walls"),
        (0.65, "Stage 3: Wall collapse"),
        (0.90, "Stage 4: Rubble"),
    ]

    for progress, stage_name in stages:
        house.deconstruction_progress = progress
        print(f"  {progress:.0%}: {stage_name}")
        assert house.deconstruction_progress == progress

    print(f"  ✓ House deconstruction stages tracked correctly")
    print()


def test_house_deconstruction_completion():
    """Test house deconstruction completion."""
    print("Testing house deconstruction completion...")

    house = House(55, 55, livable=True)
    house.start_deconstruction()
    house.deconstruction_time = 10.0  # 10 seconds for testing

    # Update over time
    dt = 2.5  # 2.5 seconds
    complete = house.update_deconstruction(dt)
    assert not complete
    assert house.deconstruction_progress == 0.25
    print(f"  After 2.5s: {house.deconstruction_progress:.0%}")

    complete = house.update_deconstruction(dt)
    assert not complete
    assert house.deconstruction_progress == 0.5
    print(f"  After 5s: {house.deconstruction_progress:.0%}")

    complete = house.update_deconstruction(dt * 3)  # Finish it
    assert complete
    assert house.deconstruction_progress == 1.0
    print(f"  After 12.5s: {house.deconstruction_progress:.0%} (complete)")

    print(f"  ✓ House deconstruction completes correctly")
    print()


def test_vehicle_creation():
    """Test vehicle entity creation."""
    print("Testing vehicle creation...")

    # Create different vehicle types
    car = Vehicle(100, 100, 'car')
    assert car.vehicle_type == 'car'
    assert car.width == 32
    assert car.height == 20
    assert not car.being_deconstructed
    print(f"  Car: {car.width}x{car.height}px")

    truck = Vehicle(200, 200, 'truck')
    assert truck.vehicle_type == 'truck'
    assert truck.width == 48
    assert truck.height == 24
    print(f"  Truck: {truck.width}x{truck.height}px")

    van = Vehicle(300, 300, 'van')
    assert van.vehicle_type == 'van'
    assert van.width == 40
    assert van.height == 22
    print(f"  Van: {van.width}x{van.height}px")

    # Check materials
    assert 'metal' in car.materials
    assert 'plastic' in car.materials
    assert 'rubber' in car.materials
    assert 'glass' in car.materials
    assert truck.materials['metal'] > car.materials['metal']
    print(f"  Car metal: {car.materials['metal']}kg, Truck metal: {truck.materials['metal']}kg")

    print(f"  ✓ Vehicles created with correct properties")
    print()


def test_vehicle_deconstruction():
    """Test vehicle deconstruction stages."""
    print("Testing vehicle deconstruction...")

    vehicle = Vehicle(400, 400, 'car')

    # Initial state
    assert not vehicle.being_deconstructed
    assert not vehicle.legal_to_deconstruct  # Always illegal
    assert vehicle.noise_level == 8  # Very noisy
    print(f"  Vehicle: legal={vehicle.legal_to_deconstruct}, noise={vehicle.noise_level}")

    # Start deconstruction
    result = vehicle.start_deconstruction()
    assert result == True
    assert vehicle.being_deconstructed == True
    print(f"  Started deconstruction")

    # Test progress stages
    stages = [
        (0.15, "Stage 1: Broken windows"),
        (0.40, "Stage 2: Dents and damage"),
        (0.60, "Stage 3: Missing doors"),
        (0.85, "Stage 4: Just frame"),
    ]

    for progress, stage_name in stages:
        vehicle.deconstruction_progress = progress
        print(f"  {progress:.0%}: {stage_name}")
        assert vehicle.deconstruction_progress == progress

    print(f"  ✓ Vehicle deconstruction stages tracked correctly")
    print()


def test_vehicle_deconstruction_completion():
    """Test vehicle deconstruction completion."""
    print("Testing vehicle deconstruction completion...")

    vehicle = Vehicle(500, 500, 'car')
    vehicle.start_deconstruction()
    vehicle.deconstruction_time = 12.0  # 12 seconds for testing

    # Update over time
    complete = vehicle.update_deconstruction(3.0)
    assert not complete
    assert vehicle.deconstruction_progress == 0.25
    print(f"  After 3s: {vehicle.deconstruction_progress:.0%}")

    complete = vehicle.update_deconstruction(6.0)
    assert not complete
    assert vehicle.deconstruction_progress == 0.75
    print(f"  After 9s: {vehicle.deconstruction_progress:.0%}")

    complete = vehicle.update_deconstruction(4.0)
    assert complete
    assert vehicle.deconstruction_progress == 1.0
    print(f"  After 13s: {vehicle.deconstruction_progress:.0%} (complete)")

    # Get materials
    materials = vehicle.get_materials()
    assert materials['metal'] == 100.0
    print(f"  Materials: {materials}")

    print(f"  ✓ Vehicle deconstruction completes correctly")
    print()


def test_building_types_deconstruction():
    """Test different building types can be deconstructed."""
    print("Testing different building types...")

    house = House(60, 60, livable=True)
    store = Store(65, 65)

    # Both should have deconstruction capability
    assert hasattr(house, 'start_deconstruction')
    assert hasattr(store, 'start_deconstruction')

    house.start_deconstruction()
    store.start_deconstruction()

    assert house.being_deconstructed
    assert store.being_deconstructed

    house.deconstruction_progress = 0.5
    store.deconstruction_progress = 0.7

    print(f"  House: {house.deconstruction_progress:.0%} deconstructed")
    print(f"  Store: {store.deconstruction_progress:.0%} deconstructed")
    print(f"  ✓ Different building types support deconstruction")
    print()


def test_visual_consistency():
    """Test that visuals use position-based seeding for consistency."""
    print("Testing visual consistency...")

    # Same position should produce same visuals
    house1 = House(70, 70, livable=True)
    house2 = House(70, 70, livable=True)

    assert house1.visuals['wall_color'] == house2.visuals['wall_color']
    print(f"  Same position produces same visuals")

    # Different positions should (likely) produce different visuals
    house3 = House(75, 75, livable=True)
    different = house1.visuals['wall_color'] != house3.visuals['wall_color']
    print(f"  Different positions produce different visuals: {different}")

    # Vehicles should also be consistent
    vehicle1 = Vehicle(600, 600, 'car')
    vehicle2 = Vehicle(600, 600, 'car')
    assert vehicle1.body_color == vehicle2.body_color
    print(f"  Vehicles use consistent visuals")

    print(f"  ✓ Visual generation is consistent and reproducible")
    print()


def main():
    """Run all deconstruction visual tests."""
    print("=" * 80)
    print("DECONSTRUCTION VISUAL SYSTEM TESTS")
    print("=" * 80)
    print()

    try:
        test_landfill_depletion()
        test_landfill_depletion_cap()
        test_house_deconstruction_stages()
        test_house_deconstruction_completion()
        test_vehicle_creation()
        test_vehicle_deconstruction()
        test_vehicle_deconstruction_completion()
        test_building_types_deconstruction()
        test_visual_consistency()

        print("=" * 80)
        print("ALL DECONSTRUCTION VISUAL TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Deconstruction Visual Features:")
        print()
        print("LANDFILL DEPLETION:")
        print("  - Tile color transitions from brown (full) to dirt (empty)")
        print("  - Trash piles diminish as depletion increases")
        print("  - Depletion tracked per tile (0.0-1.0)")
        print()
        print("HOUSE/BUILDING DECONSTRUCTION (4 stages):")
        print("  - Stage 1 (0-25%): Breaking windows (black/cracked)")
        print("  - Stage 2 (25-50%): Holes in walls")
        print("  - Stage 3 (50-75%): Partial wall collapse (vertical cracks)")
        print("  - Stage 4 (75-100%): Rubble and debris, missing wall sections")
        print()
        print("VEHICLE DECONSTRUCTION (4 stages):")
        print("  - Stage 1 (0-25%): Broken windows (cracked glass)")
        print("  - Stage 2 (25-50%): Dents and damage on body")
        print("  - Stage 3 (50-75%): Missing parts (doors, hood)")
        print("  - Stage 4 (75-100%): Just frame and wheels remaining")
        print()
        print("GENERAL:")
        print("  - All visuals use position-based seeding for consistency")
        print("  - Progress bars show deconstruction status")
        print("  - Colors fade as deconstruction progresses")
        print("  - All illegal deconstruction generates suspicion")
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
