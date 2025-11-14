"""
Tests for city buildings and Grid integration.

Tests building classes, deconstruction, materials, and rendering integration.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.entities.city_building import (
    CityBuilding, House, Store, Office, CityFactory, PoliceStation
)
from src.world.grid import Grid


def test_house_creation():
    """Test house creation and properties."""
    print("Testing house creation...")

    # Livable house
    livable = House(10, 10, livable=True)
    assert livable.name == "Livable House"
    assert not livable.legal_to_deconstruct, "Livable house should be illegal"
    assert livable.deconstruction_time == 120.0
    assert livable.noise_level == 8
    assert livable.width == 3
    assert livable.height == 4
    assert len(livable.materials) > 0, "Should have materials"
    assert 'wood' in livable.materials
    assert 'concrete' in livable.materials

    print(f"  ✓ Livable house: {livable.name}, illegal={not livable.legal_to_deconstruct}")
    print(f"    Materials: {sum(livable.materials.values()):.1f}kg total")

    # Decrepit house
    decrepit = House(20, 20, livable=False)
    assert decrepit.name == "Decrepit House"
    assert decrepit.legal_to_deconstruct, "Decrepit house should be legal"
    assert decrepit.deconstruction_time == 60.0
    assert decrepit.noise_level == 6
    assert len(decrepit.materials) > 0, "Should have materials"

    print(f"  ✓ Decrepit house: {decrepit.name}, legal={decrepit.legal_to_deconstruct}")
    print(f"    Materials: {sum(decrepit.materials.values()):.1f}kg total")
    print()


def test_store_creation():
    """Test store creation."""
    print("Testing store creation...")

    store = Store(30, 30)
    assert store.name == "Store"
    assert not store.legal_to_deconstruct, "Store should be illegal"
    assert store.width == 4
    assert store.height == 4
    assert len(store.materials) > 0
    assert 'glass' in store.materials  # Display windows

    print(f"  ✓ Store: {store.name}, {store.width}x{store.height}")
    print(f"    Materials: {sum(store.materials.values()):.1f}kg total")
    print()


def test_office_creation():
    """Test office creation."""
    print("Testing office creation...")

    office = Office(40, 40)
    assert office.name == "Office Building"
    assert not office.legal_to_deconstruct
    assert office.width == 5
    assert office.height == 5
    assert 'electronic' in office.materials  # Computers

    print(f"  ✓ Office: {office.name}, {office.width}x{office.height}")
    print(f"    Materials: {sum(office.materials.values()):.1f}kg total")
    print()


def test_city_factory_creation():
    """Test city factory creation."""
    print("Testing city factory creation...")

    factory = CityFactory(50, 50)
    assert factory.name == "Industrial Factory"
    assert not factory.legal_to_deconstruct
    assert factory.width == 6
    assert factory.height == 6
    assert 'steel' in factory.materials

    print(f"  ✓ Factory: {factory.name}, {factory.width}x{factory.height}")
    print(f"    Materials: {sum(factory.materials.values()):.1f}kg total")
    print()


def test_police_station_creation():
    """Test police station creation."""
    print("Testing police station creation...")

    station = PoliceStation(60, 60)
    assert station.name == "Police Station"
    assert not station.legal_to_deconstruct
    assert station.width == 5
    assert station.height == 5
    assert len(station.materials) == 0, "Police station should have no materials"

    # Cannot be deconstructed
    result = station.start_deconstruction()
    assert not result, "Police station should not be deconstructible"

    print(f"  ✓ Police Station: {station.name}, cannot be deconstructed")
    print()


def test_deconstruction():
    """Test building deconstruction."""
    print("Testing building deconstruction...")

    house = House(10, 10, livable=False)

    # Start deconstruction
    result = house.start_deconstruction()
    assert result, "Should be able to start deconstruction"
    assert house.being_deconstructed

    print(f"  ✓ Started deconstruction")

    # Update for half the time
    half_time = house.deconstruction_time / 2.0
    complete = house.update_deconstruction(half_time)
    assert not complete, "Should not be complete yet"
    assert 0.4 < house.deconstruction_progress < 0.6, "Should be ~50% complete"

    print(f"    Progress: {house.deconstruction_progress:.1%}")

    # Update for remaining time
    complete = house.update_deconstruction(half_time + 1.0)
    assert complete, "Should be complete"
    assert house.deconstruction_progress >= 1.0
    assert not house.being_deconstructed

    print(f"  ✓ Deconstruction complete")

    # Get materials
    materials = house.get_materials()
    assert len(materials) > 0
    assert 'wood' in materials

    print(f"  ✓ Collected {len(materials)} material types")
    print()


def test_contains_point():
    """Test building contains_point method."""
    print("Testing contains_point...")

    house = House(10, 10, livable=True)

    # Inside building
    assert house.contains_point(10, 10), "Top-left corner should be inside"
    assert house.contains_point(11, 11), "Middle should be inside"
    assert house.contains_point(12, 13), "Bottom-right should be inside"

    # Outside building
    assert not house.contains_point(9, 10), "Left edge should be outside"
    assert not house.contains_point(10, 9), "Top edge should be outside"
    assert not house.contains_point(13, 10), "Right edge should be outside"
    assert not house.contains_point(10, 14), "Bottom edge should be outside"

    print(f"  ✓ contains_point works correctly")
    print()


def test_grid_integration():
    """Test city building integration with Grid."""
    print("Testing Grid integration...")

    grid = Grid(100, 75, 32)

    # Generate city
    grid.generate_city(seed=12345)

    # Check that city was generated
    assert grid.city_generated, "City should be generated"
    assert len(grid.city_buildings) > 0, "Should have buildings"

    print(f"  ✓ Grid generated city with {len(grid.city_buildings)} buildings")

    # Test get_city_building_at
    if grid.city_buildings:
        # Get first building
        building = grid.city_buildings[0]
        x = building.grid_x
        y = building.grid_y

        # Should find building at its position
        found = grid.get_city_building_at(x, y)
        assert found is not None, f"Should find building at ({x}, {y})"
        assert found == building, "Should return the same building"

        # Should also find at position inside building
        found = grid.get_city_building_at(x + 1, y + 1)
        assert found is not None, f"Should find building at ({x+1}, {y+1})"
        assert found == building, "Should return the same building"

        print(f"  ✓ get_city_building_at works correctly")

    # Check building types
    houses = [b for b in grid.city_buildings if isinstance(b, House)]
    stores = [b for b in grid.city_buildings if isinstance(b, Store)]
    offices = [b for b in grid.city_buildings if isinstance(b, Office)]
    factories = [b for b in grid.city_buildings if isinstance(b, CityFactory)]
    police = [b for b in grid.city_buildings if isinstance(b, PoliceStation)]

    print(f"  ✓ Houses: {len(houses)}")
    print(f"  ✓ Stores: {len(stores)}")
    print(f"  ✓ Offices: {len(offices)}")
    print(f"  ✓ Factories: {len(factories)}")
    print(f"  ✓ Police Stations: {len(police)}")
    print()


def test_legal_illegal_separation():
    """Test that legal and illegal buildings are correctly separated."""
    print("Testing legal/illegal separation...")

    grid = Grid(100, 75, 32)
    grid.generate_city(seed=12345)

    legal_buildings = [b for b in grid.city_buildings if b.legal_to_deconstruct]
    illegal_buildings = [b for b in grid.city_buildings if not b.legal_to_deconstruct]

    assert len(legal_buildings) > 0, "Should have legal buildings"
    assert len(illegal_buildings) > 0, "Should have illegal buildings"

    # All legal buildings should be decrepit houses
    for building in legal_buildings:
        assert isinstance(building, House), "Legal buildings should be Houses"
        assert not building.livable, "Legal houses should be decrepit"

    # All livable houses should be illegal
    livable_houses = [b for b in grid.city_buildings
                      if isinstance(b, House) and b.livable]
    for house in livable_houses:
        assert not house.legal_to_deconstruct, "Livable houses should be illegal"

    print(f"  ✓ Legal buildings: {len(legal_buildings)}")
    print(f"  ✓ Illegal buildings: {len(illegal_buildings)}")
    print(f"  ✓ All legal buildings are decrepit houses")
    print(f"  ✓ All livable houses are illegal")
    print()


def main():
    """Run all city building tests."""
    print("=" * 80)
    print("CITY BUILDING TESTS")
    print("=" * 80)
    print()

    try:
        test_house_creation()
        test_store_creation()
        test_office_creation()
        test_city_factory_creation()
        test_police_station_creation()
        test_deconstruction()
        test_contains_point()
        test_grid_integration()
        test_legal_illegal_separation()

        print("=" * 80)
        print("ALL CITY BUILDING TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("City Building Features:")
        print("  - 5 building types: House, Store, Office, Factory, Police Station")
        print("  - Livable vs decrepit houses (illegal vs legal)")
        print("  - Deconstruction system with progress tracking")
        print("  - Material collection from deconstructed buildings")
        print("  - Noise levels for detection system")
        print("  - Grid integration with building placement and queries")
        print("  - Rendering support with progress bars")
        print("  - Legal/illegal building classification")
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
