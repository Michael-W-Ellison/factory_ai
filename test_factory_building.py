"""
Test script for Factory building.

Tests:
- Factory initialization
- Upgrade levels 1-5
- Material storage
- Processing system
- Level bonuses
"""

import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.entities.buildings.factory import Factory


def test_factory_initialization():
    """Test factory initialization."""
    print("\nTesting factory initialization...")

    factory = Factory(grid_x=50, grid_y=50)

    print(f"  Name: {factory.name}")
    print(f"  Size: {factory.width_tiles}x{factory.height_tiles} tiles")
    print(f"  Position: ({factory.grid_x}, {factory.grid_y})")
    print(f"  Level: {factory.level}/{factory.max_level}")
    print(f"  Power consumption: {factory.power_consumption} units")
    print(f"  Storage capacity: {factory.storage_capacity} kg")
    print(f"  Under construction: {factory.under_construction}")

    assert factory.width_tiles == 5, "Factory should be 5x5 tiles"
    assert factory.height_tiles == 5, "Factory should be 5x5 tiles"
    assert factory.level == 1, "Factory should start at level 1"
    assert factory.max_level == 5, "Factory should have max level 5"
    assert factory.storage_capacity == 10000.0, "Level 1 should have 10,000kg storage"
    assert not factory.under_construction, "Starting factory should be complete"

    print("  ✓ Factory initialization correct")


def test_factory_upgrades():
    """Test factory upgrade levels."""
    print("\nTesting factory upgrade levels...")

    factory = Factory(grid_x=50, grid_y=50)

    print(f"\n  Level 1:")
    print(f"    Storage: {factory.storage_capacity:.0f} kg")
    print(f"    Processing speed: {factory.processing_speed:.1f} s/kg")
    print(f"    Efficiency: {factory.processing_efficiency * 100:.0f}%")
    print(f"    Power: {factory.power_consumption:.1f} units")

    # Upgrade to level 3
    factory.level = 3
    factory._apply_level_bonuses()

    print(f"\n  Level 3:")
    print(f"    Storage: {factory.storage_capacity:.0f} kg")
    print(f"    Processing speed: {factory.processing_speed:.1f} s/kg")
    print(f"    Efficiency: {factory.processing_efficiency * 100:.0f}%")
    print(f"    Power: {factory.power_consumption:.1f} units")

    assert factory.storage_capacity == 30000.0, "Level 3 should have 30,000kg storage"
    assert factory.processing_efficiency > 0.5, "Efficiency should improve with level"

    # Upgrade to level 5
    factory.level = 5
    factory._apply_level_bonuses()

    print(f"\n  Level 5 (Max):")
    print(f"    Storage: {factory.storage_capacity:.0f} kg")
    print(f"    Processing speed: {factory.processing_speed:.1f} s/kg")
    print(f"    Efficiency: {factory.processing_efficiency * 100:.0f}%")
    print(f"    Power: {factory.power_consumption:.1f} units")

    assert factory.storage_capacity == 50000.0, "Level 5 should have 50,000kg storage"
    assert factory.processing_efficiency > 0.8, "Level 5 should have 80%+ efficiency"

    print("\n  ✓ All upgrade levels work correctly")


def test_factory_storage():
    """Test factory storage system."""
    print("\nTesting factory storage...")

    factory = Factory(grid_x=50, grid_y=50)

    # Store materials
    stored = factory.store_material('plastic', 1000.0)
    print(f"  Stored 1000kg plastic: {stored:.0f}kg accepted")
    assert stored == 1000.0, "Should store 1000kg"

    stored = factory.store_material('metal', 2500.0)
    print(f"  Stored 2500kg metal: {stored:.0f}kg accepted")
    assert stored == 2500.0, "Should store 2500kg"

    # Check storage info
    info = factory.get_storage_info()
    print(f"\n  Current storage: {info['current']:.0f}/{info['capacity']:.0f}kg ({info['percent_full']:.1f}%)")
    print(f"  Materials: {info['materials']}")

    assert info['current'] == 3500.0, "Should have 3500kg total"
    assert info['percent_full'] == 35.0, "Should be 35% full"

    # Try to overfill
    stored = factory.store_material('glass', 8000.0)
    print(f"\n  Attempted to store 8000kg glass: {stored:.0f}kg accepted")
    assert stored == 6500.0, "Should only store 6500kg (up to capacity)"

    info = factory.get_storage_info()
    print(f"  Storage after overfill: {info['current']:.0f}/{info['capacity']:.0f}kg ({info['percent_full']:.1f}%)")
    assert info['percent_full'] == 100.0, "Should be 100% full"

    # Retrieve materials
    retrieved = factory.get_material('plastic', 500.0)
    print(f"\n  Retrieved 500kg plastic: {retrieved:.0f}kg")
    assert retrieved == 500.0, "Should retrieve 500kg"

    info = factory.get_storage_info()
    print(f"  Storage after retrieval: {info['current']:.0f}kg")
    assert info['current'] == 9500.0, "Should have 9500kg remaining"

    print("\n  ✓ Storage system works correctly")


def test_factory_processing():
    """Test factory processing system."""
    print("\nTesting factory processing...")

    factory = Factory(grid_x=50, grid_y=50)

    # Add material to input queue
    factory.add_to_input_queue('plastic', 10.0)
    print(f"  Added 10kg plastic to input queue")
    print(f"  Input queue size: {len(factory.input_queue)}")

    # Start processing
    factory._start_processing()
    print(f"  Started processing")
    print(f"  Processing time: {factory.processing_time_remaining:.1f}s")

    assert factory.processing_current is not None, "Should be processing"
    assert factory.processing_time_remaining > 0, "Should have processing time"

    # Simulate processing completion
    factory.processing_time_remaining = 0.0
    factory._finish_processing()

    print(f"  Finished processing")
    print(f"  Output queue size: {len(factory.output_queue)}")

    assert len(factory.output_queue) > 0, "Should have output"
    output = factory.output_queue[0]
    print(f"  Output: {output['quantity']:.1f}kg of {output['material_type']}")

    # At level 1, efficiency is 50%
    expected_output = 10.0 * 0.5
    assert abs(output['quantity'] - expected_output) < 0.1, f"Should output ~{expected_output}kg (50% efficiency)"

    print("\n  ✓ Processing system works correctly")


def test_factory_can_operate():
    """Test factory operational checks."""
    print("\nTesting factory operational checks...")

    factory = Factory(grid_x=50, grid_y=50)

    print(f"  Normal operation: {factory.can_operate()}")
    assert factory.can_operate(), "Factory should operate normally"

    # Test power check
    factory.powered = False
    print(f"  Without power: {factory.can_operate()}")
    assert not factory.can_operate(), "Factory should not operate without power"
    factory.powered = True

    # Test operational check
    factory.operational = False
    print(f"  Not operational: {factory.can_operate()}")
    assert not factory.can_operate(), "Factory should not operate if not operational"
    factory.operational = True

    # Test health check
    factory.health = 0.0
    print(f"  Zero health: {factory.can_operate()}")
    assert not factory.can_operate(), "Factory should not operate with zero health"
    factory.health = 100.0

    # Test construction check
    factory.under_construction = True
    print(f"  Under construction: {factory.can_operate()}")
    assert not factory.can_operate(), "Factory should not operate while under construction"
    factory.under_construction = False

    print(f"  After restoring all: {factory.can_operate()}")
    assert factory.can_operate(), "Factory should operate after restoring"

    print("\n  ✓ Operational checks work correctly")


def test_factory_visual():
    """Test factory visual rendering (visual test)."""
    print("\nTesting factory visual rendering...")

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Factory Visual Test")

    # Create simple camera
    class SimpleCamera:
        def __init__(self):
            self.x = 0
            self.y = 0
            self.zoom = 1.0
        def world_to_screen(self, wx, wy):
            return int(wx - self.x), int(wy - self.y)
        def is_visible(self, x, y, w, h):
            return True

    camera = SimpleCamera()
    clock = pygame.time.Clock()

    # Create factory at different levels
    factories = []
    for level in range(1, 6):
        factory = Factory(grid_x=50 + level * 10, grid_y=50)
        factory.level = level
        factory._apply_level_bonuses()
        # Position for display
        factory.x = 50 + (level - 1) * 150
        factory.y = 250
        # Add some storage
        factory.store_material('plastic', level * 2000.0)
        factories.append(factory)

    print("  Visual test window opened (will run for 5 seconds)...")
    print("  You should see:")
    print("    - 5 factories in a row (Level 1-5)")
    print("    - Power indicators (green dots)")
    print("    - Storage bars showing fill levels")
    print("    - Level indicators (L1-L5)")

    # Run for 5 seconds
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < 5000:
        dt = clock.tick(60) / 1000.0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # Render
        screen.fill((30, 30, 30))

        # Draw title
        font = pygame.font.Font(None, 32)
        title = font.render("Factory Upgrade Levels (1-5)", True, (255, 255, 255))
        screen.blit(title, (20, 20))

        # Draw labels
        font_small = pygame.font.Font(None, 20)
        for i, factory in enumerate(factories):
            x = 50 + i * 150
            y = 500
            text = font_small.render(f"Level {factory.level}", True, (200, 200, 200))
            screen.blit(text, (x, y))

            storage_info = factory.get_storage_info()
            storage_text = font_small.render(f"{storage_info['percent_full']:.0f}% full", True, (150, 150, 150))
            screen.blit(storage_text, (x, y + 20))

        # Render factories
        for factory in factories:
            factory.render(screen, camera)

        pygame.display.flip()

    pygame.quit()
    print("  ✓ Visual test completed")


if __name__ == '__main__':
    print("=" * 80)
    print("FACTORY BUILDING TESTS")
    print("=" * 80)

    try:
        test_factory_initialization()
        test_factory_upgrades()
        test_factory_storage()
        test_factory_processing()
        test_factory_can_operate()
        test_factory_visual()

        print("\n" + "=" * 80)
        print("ALL FACTORY BUILDING TESTS PASSED! ✓")
        print("=" * 80)
        print("\nSummary:")
        print("  - Factory initialization: ✓")
        print("  - Upgrade levels 1-5: ✓")
        print("  - Material storage system: ✓")
        print("  - Processing system: ✓")
        print("  - Operational checks: ✓")
        print("  - Visual rendering: ✓")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
