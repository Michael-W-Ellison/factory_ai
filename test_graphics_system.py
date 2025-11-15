"""
Graphics System Test - Demonstrates sprite generation and animation.

Run this to see all sprite types and animations in action.
"""

import pygame
import sys
import math

# Add src to path
sys.path.insert(0, 'src')

from graphics import (
    get_sprite_generator, SpriteType, Direction,
    NPCAnimationController, VehicleAnimationController,
    RobotAnimationController, DroneAnimationController,
    get_render_effects
)


def test_graphics_system():
    """Test and demonstrate the graphics system."""
    pygame.init()

    # Create display
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Factory AI - Graphics System Demo")
    clock = pygame.time.Clock()

    # Get graphics instances
    sprite_gen = get_sprite_generator()
    effects = get_render_effects()

    # Animation controllers
    npc_anim = NPCAnimationController()
    vehicle_anim = VehicleAnimationController()
    robot_anim = RobotAnimationController()
    drone_anim = DroneAnimationController()

    # Test state
    running = True
    time_elapsed = 0.0
    battery_level = 100.0

    print("=" * 80)
    print("GRAPHICS SYSTEM DEMO")
    print("=" * 80)
    print("\nDemonstrating:")
    print("  - NPC sprites with 8-way direction and walking animation")
    print("  - Vehicle sprites (car, truck, van, bus, police)")
    print("  - Robot sprites with idle/move animation")
    print("  - Drone sprites with rotor animation")
    print("  - Visual effects (shadows, glow, highlights, health bars)")
    print("\nPress ESC to exit")
    print("=" * 80)

    while running:
        dt = clock.tick(60) / 1000.0  # 60 FPS, dt in seconds
        time_elapsed += dt

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Clear screen
        screen.fill((40, 40, 50))

        # Update animations
        npc_frame = npc_anim.update_for_activity('walking', dt)
        vehicle_frame = vehicle_anim.update_for_state(True, dt)
        robot_frame = robot_anim.update_for_state(True, dt)
        drone_frame = drone_anim.update_for_state(True, battery_level, dt)

        # Cycle battery for demo
        battery_level = 50 + 50 * math.sin(time_elapsed)

        # Render title
        font_large = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)

        title = font_large.render("Graphics System Demo", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 20))

        y_offset = 100

        # Section 1: NPCs
        section_text = font_medium.render("NPCs (8 Directions + Walk Animation)", True, (200, 200, 200))
        screen.blit(section_text, (50, y_offset))
        y_offset += 40

        directions = [Direction.EAST, Direction.SOUTHEAST, Direction.SOUTH,
                     Direction.SOUTHWEST, Direction.WEST, Direction.NORTHWEST,
                     Direction.NORTH, Direction.NORTHEAST]

        x_start = 100
        for i, direction in enumerate(directions):
            x = x_start + (i % 4) * 150
            y = y_offset + (i // 4) * 100

            # Get sprite
            sprite = sprite_gen.get_sprite(SpriteType.NPC, direction, npc_frame, variant=i)

            # Draw shadow
            effects.draw_shadow(screen, (x - 8, y + 10), 20, 8, opacity=60)

            # Draw sprite
            screen.blit(sprite, (x - sprite.get_width()//2, y - sprite.get_height()//2))

            # Label
            dir_name = font_small.render(direction.name, True, (150, 150, 150))
            screen.blit(dir_name, (x - dir_name.get_width()//2, y + 25))

        y_offset += 220

        # Section 2: Vehicles
        section_text = font_medium.render("Vehicles (Multiple Types)", True, (200, 200, 200))
        screen.blit(section_text, (50, y_offset))
        y_offset += 40

        vehicle_types = [
            (SpriteType.CAR, "Car"),
            (SpriteType.TRUCK, "Truck"),
            (SpriteType.VAN, "Van"),
            (SpriteType.BUS, "Bus"),
            (SpriteType.POLICE_CAR, "Police"),
        ]

        x_start = 150
        for i, (vtype, name) in enumerate(vehicle_types):
            x = x_start + i * 200
            y = y_offset + 40

            # Get sprite
            sprite = sprite_gen.get_sprite(vtype, Direction.EAST, vehicle_frame,
                                          variant=i, lights_on=(i == 4))  # Police lights on

            # Draw shadow
            effects.draw_shadow(screen, (x - 20, y + 15), 50, 15, opacity=80)

            # Draw sprite
            screen.blit(sprite, (x - sprite.get_width()//2, y - sprite.get_height()//2))

            # Label
            label = font_small.render(name, True, (150, 150, 150))
            screen.blit(label, (x - label.get_width()//2, y + 40))

        y_offset += 140

        # Section 3: Robots
        section_text = font_medium.render("Robots (Animated)", True, (200, 200, 200))
        screen.blit(section_text, (50, y_offset))
        y_offset += 40

        for i in range(4):
            x = 150 + i * 200
            y = y_offset + 40

            # Get sprite with different variants
            sprite = sprite_gen.get_sprite(SpriteType.ROBOT, Direction.SOUTH,
                                          robot_frame, variant=i)

            # Draw glow effect
            effects.draw_glow(screen, (x, y), 15, (0, 200, 255), intensity=0.5)

            # Draw sprite
            screen.blit(sprite, (x - sprite.get_width()//2, y - sprite.get_height()//2))

            # Health bar
            health = 100 - (i * 20)
            effects.draw_health_bar(screen, (x - 15, y - 30), 30, 4, health)

        y_offset += 120

        # Section 4: Drones
        section_text = font_medium.render("Drones (Rotor Animation + Battery)", True, (200, 200, 200))
        screen.blit(section_text, (50, y_offset))
        y_offset += 40

        for i in range(3):
            x = 200 + i * 250
            y = y_offset + 40

            # Get sprite with varying battery
            batt = 100 - (i * 40)
            sprite = sprite_gen.get_sprite(SpriteType.DRONE, Direction.SOUTH,
                                          drone_frame, variant=0,
                                          battery_level=batt)

            # Draw selection indicator
            pulse_phase = time_elapsed * 3 + i
            effects.draw_selection_indicator(screen, (x, y), 20,
                                            color=(100, 255, 100),
                                            pulse_phase=pulse_phase)

            # Draw sprite
            screen.blit(sprite, (x - sprite.get_width()//2, y - sprite.get_height()//2))

            # Battery text
            batt_text = font_small.render(f"Battery: {batt}%", True, (200, 200, 200))
            screen.blit(batt_text, (x - batt_text.get_width()//2, y + 30))

        # FPS counter
        fps_text = font_small.render(f"FPS: {int(clock.get_fps())}", True, (100, 255, 100))
        screen.blit(fps_text, (screen.get_width() - 100, 10))

        # Cache info
        cache_info = sprite_gen.get_cache_info()
        cache_text = font_small.render(
            f"Cached Sprites: {cache_info['cached_sprites']}",
            True, (150, 150, 150)
        )
        screen.blit(cache_text, (screen.get_width() - 200, 40))

        # Update display
        pygame.display.flip()

    pygame.quit()
    print("\nGraphics system demo completed!")
    print(f"Final sprite cache: {sprite_gen.get_cache_info()}")


if __name__ == "__main__":
    try:
        test_graphics_system()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        pygame.quit()
        sys.exit(0)
