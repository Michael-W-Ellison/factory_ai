"""
Test script for visual animations and directional rendering.

Tests:
- NPC directional rendering and walking animation
- Police directional rendering and walking animation
- Vehicle directional rendering (rotation)
"""

import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.entities.npc import NPC, Activity
from src.entities.police_officer import PoliceOfficer
from src.entities.vehicle import Vehicle


class SimpleCamera:
    """Simple camera for testing."""
    def __init__(self):
        self.x = 0
        self.y = 0
        self.zoom = 1.0

    def world_to_screen(self, world_x, world_y):
        return int(world_x - self.x), int(world_y - self.y)


def test_npc_rendering():
    """Test NPC rendering with animation."""
    print("\nTesting NPC rendering...")

    # Create NPC
    npc = NPC(world_x=100, world_y=100, home_x=5, home_y=5, work_x=10, work_y=10)

    # Check animation properties exist
    assert hasattr(npc, 'animation_frame'), "NPC should have animation_frame"
    assert hasattr(npc, 'animation_timer'), "NPC should have animation_timer"
    assert hasattr(npc, 'animation_speed'), "NPC should have animation_speed"
    assert hasattr(npc, 'facing_angle'), "NPC should have facing_angle"

    print(f"  Animation frame: {npc.animation_frame}")
    print(f"  Animation timer: {npc.animation_timer}")
    print(f"  Animation speed: {npc.animation_speed}")
    print(f"  Facing angle: {npc.facing_angle}")

    # Test animation update
    npc.moving = True
    npc.target_x = 200
    npc.target_y = 200

    initial_frame = npc.animation_frame
    npc.update(0.4, 12.0)  # Update with 0.4 seconds (should trigger frame change)

    print(f"  After update - Animation frame: {npc.animation_frame}")
    print(f"  Facing angle: {npc.facing_angle}")

    print("  ✓ NPC animation properties work")


def test_police_rendering():
    """Test Police rendering with animation."""
    print("\nTesting Police rendering...")

    # Create police officer
    police = PoliceOfficer(world_x=200, world_y=200, patrol_route=[(5, 5), (10, 10)])

    # Check animation properties (inherited from NPC)
    assert hasattr(police, 'animation_frame'), "Police should have animation_frame"
    assert hasattr(police, 'animation_timer'), "Police should have animation_timer"
    assert hasattr(police, 'facing_angle'), "Police should have facing_angle"

    print(f"  Animation frame: {police.animation_frame}")
    print(f"  Facing angle: {police.facing_angle}")
    print(f"  Behavior: {police.behavior}")

    # Test animation update
    police.moving = True
    police.target_x = 300
    police.target_y = 300

    police.update(0.4, 12.0)

    print(f"  After update - Animation frame: {police.animation_frame}")
    print(f"  Facing angle: {police.facing_angle}")

    print("  ✓ Police animation properties work")


def test_vehicle_rendering():
    """Test Vehicle rendering with rotation."""
    print("\nTesting Vehicle rendering...")

    # Create vehicles with different types
    car = Vehicle(world_x=300, world_y=300, vehicle_type='car', is_scrap=False)
    truck = Vehicle(world_x=400, world_y=400, vehicle_type='truck', is_scrap=True)

    # Check facing angle exists
    assert hasattr(car, 'facing_angle'), "Vehicle should have facing_angle"
    assert hasattr(truck, 'facing_angle'), "Vehicle should have facing_angle"

    print(f"  Car facing angle: {car.facing_angle}")
    print(f"  Truck facing angle: {truck.facing_angle}")

    # Verify facing angle is one of the valid directions
    assert car.facing_angle in [0, 90, 180, 270], "Car should face cardinal direction"
    assert truck.facing_angle in [0, 90, 180, 270], "Truck should face cardinal direction"

    print("  ✓ Vehicle rotation properties work")


def test_rendering_visual():
    """Test actual rendering (visual test - requires pygame)."""
    print("\nTesting actual rendering (visual)...")

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Visual Animation Test")
    camera = SimpleCamera()
    clock = pygame.time.Clock()

    # Create test entities
    npc = NPC(world_x=200, world_y=200, home_x=5, home_y=5, work_x=10, work_y=10)
    npc.moving = True
    npc.target_x = 600
    npc.target_y=400

    police = PoliceOfficer(world_x=400, world_y=200, patrol_route=[(10, 10), (20, 20)])
    police.moving = True
    police.target_x = 600
    police.target_y = 400

    car = Vehicle(world_x=200, world_y=400, vehicle_type='car', is_scrap=False)
    truck = Vehicle(world_x=400, world_y=400, vehicle_type='truck', is_scrap=True)

    print("  Visual test window opened (will run for 5 seconds)...")
    print("  You should see:")
    print("    - NPCs with walking animation and facing indicators")
    print("    - Police with walking animation and gold facing indicators")
    print("    - Vehicles rotated at different angles")

    # Run for 5 seconds
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < 5000:
        dt = clock.tick(60) / 1000.0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # Update entities
        npc.update(dt, 12.0)
        police.update(dt, 12.0)

        # Render
        screen.fill((50, 80, 50))  # Green background

        # Render entities
        npc.render(screen, camera)
        police.render(screen, camera)
        car.render(screen, camera)
        truck.render(screen, camera)

        # Add labels
        font = pygame.font.Font(None, 20)
        npc_label = font.render("NPC (walking)", True, (255, 255, 255))
        police_label = font.render("Police (walking)", True, (255, 255, 255))
        car_label = font.render(f"Car (angle: {car.facing_angle}°)", True, (255, 255, 255))
        truck_label = font.render(f"Truck (angle: {truck.facing_angle}°)", True, (255, 255, 255))

        screen.blit(npc_label, (10, 10))
        screen.blit(police_label, (10, 30))
        screen.blit(car_label, (10, 50))
        screen.blit(truck_label, (10, 70))

        pygame.display.flip()

    pygame.quit()
    print("  ✓ Visual test completed")


if __name__ == '__main__':
    print("="*80)
    print("VISUAL ANIMATION TESTS")
    print("="*80)

    try:
        test_npc_rendering()
        test_police_rendering()
        test_vehicle_rendering()
        test_rendering_visual()

        print("\n" + "="*80)
        print("ALL VISUAL ANIMATION TESTS PASSED! ✓")
        print("="*80)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
