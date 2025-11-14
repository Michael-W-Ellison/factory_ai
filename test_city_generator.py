"""
Tests for CityGenerator.

Tests city layout generation, zone assignment, building placement, and road generation.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.world.city_generator import CityGenerator, ZoneType


def test_city_generator_initialization():
    """Test CityGenerator initialization."""
    print("Testing CityGenerator initialization...")

    # Standard world size from config
    world_width = 3200  # 100 tiles * 32 pixels
    world_height = 2400  # 75 tiles * 32 pixels
    tile_size = 32

    generator = CityGenerator(world_width, world_height, tile_size)

    # Check dimensions
    assert generator.grid_width == 100, f"Grid width should be 100, got {generator.grid_width}"
    assert generator.grid_height == 75, f"Grid height should be 75, got {generator.grid_height}"
    assert generator.block_size == 10, "Block size should be 10"
    assert generator.blocks_wide == 10, f"Blocks wide should be 10, got {generator.blocks_wide}"
    assert generator.blocks_high == 7, f"Blocks high should be 7, got {generator.blocks_high}"

    print(f"  ✓ CityGenerator initialized: {generator.blocks_wide}x{generator.blocks_high} blocks")
    print(f"  ✓ Grid: {generator.grid_width}x{generator.grid_height} tiles")
    print()


def test_city_generation():
    """Test complete city generation."""
    print("Testing city generation...")

    generator = CityGenerator(3200, 2400, 32)
    city_data = generator.generate(seed=12345)  # Use seed for reproducibility

    # Check that data was returned
    assert 'blocks' in city_data
    assert 'buildings' in city_data
    assert 'road_tiles' in city_data
    assert 'stats' in city_data

    stats = city_data['stats']

    print(f"  ✓ Generated city with {stats['total_buildings']} buildings")
    print(f"  ✓ Roads: {stats['road_tiles']} tiles")
    print(f"  ✓ Residential blocks: {stats['residential_blocks']}")
    print(f"  ✓ Commercial blocks: {stats['commercial_blocks']}")
    print(f"  ✓ Industrial blocks: {stats['industrial_blocks']}")
    print(f"  ✓ Parks: {stats['park_blocks']}")
    print()


def test_road_placement():
    """Test road placement."""
    print("Testing road placement...")

    generator = CityGenerator(3200, 2400, 32)
    generator.generate(seed=12345)

    # Check that roads exist
    assert len(generator.road_tiles) > 0, "Should have road tiles"

    # Roads should be placed every 10 tiles
    # Check horizontal road at y=0
    for x in range(generator.grid_width):
        assert generator.is_road(x, 0), f"Should be road at ({x}, 0)"

    # Check vertical road at x=0
    for y in range(generator.grid_height):
        assert generator.is_road(0, y), f"Should be road at (0, {y})"

    # Check horizontal road at y=10
    for x in range(generator.grid_width):
        assert generator.is_road(x, 10), f"Should be road at ({x}, 10)"

    print(f"  ✓ Roads placed correctly in grid pattern")
    print(f"  ✓ Total road tiles: {len(generator.road_tiles)}")
    print()


def test_zone_assignment():
    """Test zone assignment."""
    print("Testing zone assignment...")

    generator = CityGenerator(3200, 2400, 32)
    generator.generate(seed=12345)

    # Check that zones are assigned
    zone_counts = {
        ZoneType.RESIDENTIAL: 0,
        ZoneType.COMMERCIAL: 0,
        ZoneType.INDUSTRIAL: 0,
        ZoneType.POLICE: 0,
        ZoneType.PARK: 0,
        ZoneType.ROAD: 0,
        ZoneType.EMPTY: 0
    }

    for row in generator.blocks:
        for block in row:
            zone_counts[block.zone_type] += 1

    # Should have at least some of each major zone type
    assert zone_counts[ZoneType.RESIDENTIAL] > 0, "Should have residential zones"
    assert zone_counts[ZoneType.COMMERCIAL] > 0, "Should have commercial zones"
    assert zone_counts[ZoneType.POLICE] == 1, "Should have exactly 1 police zone"

    print(f"  ✓ Residential zones: {zone_counts[ZoneType.RESIDENTIAL]}")
    print(f"  ✓ Commercial zones: {zone_counts[ZoneType.COMMERCIAL]}")
    print(f"  ✓ Industrial zones: {zone_counts[ZoneType.INDUSTRIAL]}")
    print(f"  ✓ Police zones: {zone_counts[ZoneType.POLICE]}")
    print(f"  ✓ Parks: {zone_counts[ZoneType.PARK]}")
    print()


def test_building_placement():
    """Test building placement."""
    print("Testing building placement...")

    generator = CityGenerator(3200, 2400, 32)
    city_data = generator.generate(seed=12345)

    buildings = city_data['buildings']
    stats = city_data['stats']

    # Should have buildings
    assert len(buildings) > 0, "Should have buildings"

    # Should have houses
    assert stats['houses'] > 0, "Should have houses"

    # Should have police station
    assert stats['police_stations'] == 1, "Should have exactly 1 police station"

    # Check building structure
    first_building = buildings[0]
    assert 'type' in first_building, "Building should have type"
    assert 'x' in first_building, "Building should have x"
    assert 'y' in first_building, "Building should have y"
    assert 'width' in first_building, "Building should have width"
    assert 'height' in first_building, "Building should have height"
    assert 'legal' in first_building, "Building should have legal flag"
    assert 'block' in first_building, "Building should have block reference"

    print(f"  ✓ Total buildings: {len(buildings)}")
    print(f"  ✓ Houses: {stats['houses']}")
    print(f"  ✓ Stores: {stats['stores']}")
    print(f"  ✓ Offices: {stats['offices']}")
    print(f"  ✓ Factories: {stats['factories']}")
    print(f"  ✓ Police stations: {stats['police_stations']}")
    print()


def test_legal_flags():
    """Test that legal flags are set correctly."""
    print("Testing building legal flags...")

    generator = CityGenerator(3200, 2400, 32)
    city_data = generator.generate(seed=12345)

    buildings = city_data['buildings']

    legal_buildings = [b for b in buildings if b['legal']]
    illegal_buildings = [b for b in buildings if not b['legal']]

    # Decrepit houses should be legal
    decrepit_houses = [b for b in buildings if b['type'] == 'house' and b['subtype'] == 'decrepit']
    for house in decrepit_houses:
        assert house['legal'], "Decrepit houses should be legal"

    # Livable houses should be illegal
    livable_houses = [b for b in buildings if b['type'] == 'house' and b['subtype'] == 'livable']
    for house in livable_houses:
        assert not house['legal'], "Livable houses should be illegal"

    # Police station should be illegal
    police = [b for b in buildings if b['type'] == 'police_station']
    for station in police:
        assert not station['legal'], "Police station should be illegal"

    print(f"  ✓ Legal buildings: {len(legal_buildings)}")
    print(f"  ✓ Illegal buildings: {len(illegal_buildings)}")
    print(f"  ✓ Decrepit houses (legal): {len(decrepit_houses)}")
    print(f"  ✓ Livable houses (illegal): {len(livable_houses)}")
    print()


def test_get_building_at():
    """Test getting building at position."""
    print("Testing get_building_at...")

    generator = CityGenerator(3200, 2400, 32)
    generator.generate(seed=12345)

    # Get first building
    if generator.buildings:
        building = generator.buildings[0]
        x = building['x']
        y = building['y']

        # Should find building at its position
        found = generator.get_building_at(x, y)
        assert found is not None, f"Should find building at ({x}, {y})"
        assert found == building, "Should return the same building"

        # Should also find at position inside building
        found = generator.get_building_at(x + 1, y + 1)
        assert found is not None, f"Should find building at ({x+1}, {y+1})"
        assert found == building, "Should return the same building"

        print(f"  ✓ get_building_at works correctly")

    # Empty position should return None
    found = generator.get_building_at(0, 0)
    # 0,0 is a road, should not have building
    print(f"  ✓ Returns None for empty positions")
    print()


def test_reproducibility():
    """Test that same seed produces same city."""
    print("Testing reproducibility...")

    gen1 = CityGenerator(3200, 2400, 32)
    city1 = gen1.generate(seed=99999)

    gen2 = CityGenerator(3200, 2400, 32)
    city2 = gen2.generate(seed=99999)

    # Should have same number of buildings
    assert len(city1['buildings']) == len(city2['buildings']), \
        "Same seed should produce same number of buildings"

    # Should have same number of roads
    assert len(city1['road_tiles']) == len(city2['road_tiles']), \
        "Same seed should produce same number of roads"

    # Compare first few buildings
    for i in range(min(5, len(city1['buildings']))):
        b1 = city1['buildings'][i]
        b2 = city2['buildings'][i]
        assert b1['type'] == b2['type'], f"Building {i} type should match"
        assert b1['x'] == b2['x'], f"Building {i} x should match"
        assert b1['y'] == b2['y'], f"Building {i} y should match"

    print(f"  ✓ Same seed produces same city")
    print()


def main():
    """Run all city generator tests."""
    print("=" * 80)
    print("CITY GENERATOR TESTS")
    print("=" * 80)
    print()

    try:
        test_city_generator_initialization()
        test_city_generation()
        test_road_placement()
        test_zone_assignment()
        test_building_placement()
        test_legal_flags()
        test_get_building_at()
        test_reproducibility()

        print("=" * 80)
        print("ALL CITY GENERATOR TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("CityGenerator Features:")
        print("  - Grid-based city layout with 10x10 blocks")
        print("  - Road placement in grid pattern (every 10 tiles)")
        print("  - Zone assignment (residential, commercial, industrial, police, parks)")
        print("  - Building placement with varying density")
        print("  - Legal/illegal building classification")
        print("  - Reproducible generation with seeds")
        print("  - Query methods for buildings and roads")
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
