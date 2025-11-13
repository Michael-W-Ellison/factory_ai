"""
Tests for building visual variety system.

Tests that buildings have unique visual variations that are reproducible.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.entities.city_building import House, Store, Office, CityFactory, BuildingVisuals
from src.world.grid import Grid


def test_house_visual_variety():
    """Test that houses have visual variety."""
    print("Testing house visual variety...")

    # Create multiple houses at different positions
    houses = [
        House(10, 10, livable=True),
        House(20, 20, livable=True),
        House(30, 30, livable=True),
        House(40, 40, livable=True),
        House(50, 50, livable=True),
    ]

    # Check that they have visual data
    for house in houses:
        assert house.visuals, "House should have visual data"
        assert 'wall_color' in house.visuals
        assert 'roof_color' in house.visuals
        assert 'window_color' in house.visuals
        assert 'door_color' in house.visuals
        assert 'window_pattern' in house.visuals
        assert 'door_position' in house.visuals

    # Check that colors vary
    wall_colors = [h.visuals['wall_color'] for h in houses]
    unique_wall_colors = len(set(wall_colors))
    print(f"  {unique_wall_colors} unique wall colors out of {len(houses)} houses")
    assert unique_wall_colors > 1, "Should have variety in wall colors"

    roof_colors = [h.visuals['roof_color'] for h in houses]
    unique_roof_colors = len(set(roof_colors))
    print(f"  {unique_roof_colors} unique roof colors out of {len(houses)} houses")
    assert unique_roof_colors > 1, "Should have variety in roof colors"

    # Check that window patterns vary
    window_patterns = [str(h.visuals['window_pattern']) for h in houses]
    unique_patterns = len(set(window_patterns))
    print(f"  {unique_patterns} unique window patterns out of {len(houses)} houses")

    # Check that door positions vary
    door_positions = [h.visuals['door_position'] for h in houses]
    unique_doors = len(set(door_positions))
    print(f"  {unique_doors} unique door positions out of {len(houses)} houses")

    print(f"  ✓ Houses have visual variety")
    print()


def test_decrepit_house_visuals():
    """Test that decrepit houses have different visuals from livable."""
    print("Testing decrepit house visuals...")

    livable = House(10, 10, livable=True)
    decrepit = House(10, 10, livable=False)

    # Same position but different livable status
    assert livable.visuals['wall_color'] != decrepit.visuals['wall_color'], \
        "Decrepit houses should have different colors"

    # Decrepit houses should have darker, faded colors
    livable_brightness = sum(livable.visuals['wall_color'])
    decrepit_brightness = sum(decrepit.visuals['wall_color'])
    print(f"  Livable brightness: {livable_brightness}")
    print(f"  Decrepit brightness: {decrepit_brightness}")
    assert decrepit_brightness < livable_brightness, \
        "Decrepit houses should be darker"

    print(f"  ✓ Decrepit houses have distinct visual style")
    print()


def test_store_visual_variety():
    """Test that stores have visual variety."""
    print("Testing store visual variety...")

    stores = [
        Store(15, 15),
        Store(25, 25),
        Store(35, 35),
        Store(45, 45),
        Store(55, 55),
    ]

    # Check wall colors vary
    wall_colors = [s.visuals['wall_color'] for s in stores]
    unique_colors = len(set(wall_colors))
    print(f"  {unique_colors} unique wall colors out of {len(stores)} stores")
    assert unique_colors > 1, "Stores should have variety"

    # Check that stores have awning data
    has_awning_count = sum(1 for s in stores if s.visuals.get('has_awning'))
    print(f"  {has_awning_count} stores have awnings")

    print(f"  ✓ Stores have visual variety")
    print()


def test_office_visual_variety():
    """Test that offices have visual variety."""
    print("Testing office visual variety...")

    offices = [
        Office(12, 12),
        Office(22, 22),
        Office(32, 32),
        Office(42, 42),
    ]

    # Check wall colors vary
    wall_colors = [o.visuals['wall_color'] for o in offices]
    unique_colors = len(set(wall_colors))
    print(f"  {unique_colors} unique wall colors out of {len(offices)} offices")
    assert unique_colors > 1, "Offices should have variety"

    # Check window patterns vary
    window_patterns = [str(o.visuals['window_pattern']) for o in offices]
    unique_patterns = len(set(window_patterns))
    print(f"  {unique_patterns} unique window patterns out of {len(offices)} offices")

    print(f"  ✓ Offices have visual variety")
    print()


def test_factory_visual_variety():
    """Test that factories have visual variety."""
    print("Testing factory visual variety...")

    factories = [
        CityFactory(18, 18),
        CityFactory(28, 28),
        CityFactory(38, 38),
    ]

    # Check wall colors vary
    wall_colors = [f.visuals['wall_color'] for f in factories]
    unique_colors = len(set(wall_colors))
    print(f"  {unique_colors} unique wall colors out of {len(factories)} factories")
    assert unique_colors > 1, "Factories should have variety"

    # Check smokestack presence
    has_smokestack_count = sum(1 for f in factories if f.visuals.get('has_smokestack'))
    print(f"  {has_smokestack_count} factories have smokestacks")

    print(f"  ✓ Factories have visual variety")
    print()


def test_reproducibility():
    """Test that same position produces same visuals."""
    print("Testing visual reproducibility...")

    # Create two houses at same position
    house1 = House(25, 35, livable=True)
    house2 = House(25, 35, livable=True)

    # Should have identical visuals
    assert house1.visuals['wall_color'] == house2.visuals['wall_color'], \
        "Same position should produce same wall color"
    assert house1.visuals['roof_color'] == house2.visuals['roof_color'], \
        "Same position should produce same roof color"
    assert house1.visuals['door_position'] == house2.visuals['door_position'], \
        "Same position should produce same door position"

    print(f"  ✓ Same position produces same visuals")

    # Different positions should produce different visuals
    house3 = House(26, 35, livable=True)
    different = (house1.visuals['wall_color'] != house3.visuals['wall_color'] or
                 house1.visuals['roof_color'] != house3.visuals['roof_color'] or
                 house1.visuals['door_position'] != house3.visuals['door_position'])

    assert different, "Different positions should produce different visuals"
    print(f"  ✓ Different positions produce different visuals")
    print()


def test_city_visual_variety():
    """Test that generated city has visual variety."""
    print("Testing city-wide visual variety...")

    grid = Grid(100, 75, 32)
    grid.generate_city(seed=99999)

    # Get all houses
    houses = [b for b in grid.city_buildings if isinstance(b, House)]
    stores = [b for b in grid.city_buildings if isinstance(b, Store)]

    # Check house variety
    if len(houses) > 5:
        house_colors = [h.visuals['wall_color'] for h in houses]
        unique_house_colors = len(set(house_colors))
        variety_pct = unique_house_colors / len(houses) * 100

        print(f"  Houses: {len(houses)} total, {unique_house_colors} unique colors ({variety_pct:.1f}% variety)")
        # With 6 color options, expect at least 5 unique colors in a large city
        assert unique_house_colors >= 5, \
            f"Should have variety in house colors (got {unique_house_colors}, expected at least 5)"

    # Check store variety
    if len(stores) > 3:
        store_colors = [s.visuals['wall_color'] for s in stores]
        unique_store_colors = len(set(store_colors))
        variety_pct = unique_store_colors / len(stores) * 100

        print(f"  Stores: {len(stores)} total, {unique_store_colors} unique colors ({variety_pct:.1f}% variety)")
        assert unique_store_colors > 1, "Should have variety in store colors"

    print(f"  ✓ City has good visual variety")
    print()


def main():
    """Run all visual variety tests."""
    print("=" * 80)
    print("BUILDING VISUAL VARIETY TESTS")
    print("=" * 80)
    print()

    try:
        test_house_visual_variety()
        test_decrepit_house_visuals()
        test_store_visual_variety()
        test_office_visual_variety()
        test_factory_visual_variety()
        test_reproducibility()
        test_city_visual_variety()

        print("=" * 80)
        print("ALL VISUAL VARIETY TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Visual Variety Features:")
        print("  - Color palettes for each building type")
        print("  - 6 house wall colors, 5 roof colors")
        print("  - 5 store colors, 4 office colors, 4 factory colors")
        print("  - 4 window glass tints, 5 door colors")
        print("  - Random window patterns (2x2, 2x3, 3x2, etc.)")
        print("  - Random door positions (left, center, right)")
        print("  - Optional components: chimneys, awnings, smokestacks")
        print("  - Position-based seeding for reproducibility")
        print("  - Distinct visual styles for livable vs decrepit")
        print("  - Significant variety across entire city")
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
