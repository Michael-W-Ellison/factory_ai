"""
Animal System Test - Demonstrates animal spawning, behaviors, and interactions.

Run this to see all animal types and their AI behaviors in action.
"""

import pygame
import sys
import random

# Add src to path
sys.path.insert(0, 'src')

from graphics import (
    get_sprite_generator, SpriteType, Direction,
    AnimalAnimationController, BirdAnimationController, FishAnimationController,
    get_render_effects
)
from systems.animal_manager import get_animal_manager, AnimalManager
from entities.animal import (
    Animal, Bird, BirdOfPrey, Dog, Cat, Deer, Rat, Raccoon, Fish
)


class MockNPC:
    """Mock NPC for testing animal interactions."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0


def test_animal_system():
    """Test and demonstrate the animal system."""
    pygame.init()

    # Create display
    screen = pygame.display.set_mode((1400, 900))
    pygame.display.set_caption("Factory AI - Animal System Demo")
    clock = pygame.time.Clock()

    # Get graphics instances
    sprite_gen = get_sprite_generator()
    effects = get_render_effects()

    # Create animal manager
    animal_mgr = get_animal_manager(1400, 900)

    # Add spawn zones
    animal_mgr.add_spawn_zone('water', 200, 700, 150)  # River/lake
    animal_mgr.add_spawn_zone('forest', 1200, 200, 100)  # Forest
    animal_mgr.add_spawn_zone('park', 700, 450, 200)  # Central park
    animal_mgr.add_spawn_zone('urban', 300, 300, 150)  # Urban area

    # Spawn initial animals
    animal_mgr.spawn_initial_animals()

    # Create some mock NPCs for interaction testing
    npcs = [
        MockNPC(400, 400),
        MockNPC(600, 300),
        MockNPC(900, 500),
    ]

    # Test state
    running = True
    time_elapsed = 0.0
    camera_x = 0
    camera_y = 0

    # Fonts
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 20)

    print("=" * 80)
    print("ANIMAL SYSTEM DEMO")
    print("=" * 80)
    print("\nDemonstrating:")
    print("  - 8 animal types with unique behaviors")
    print("  - Animal-animal interactions (chase/flee)")
    print("  - NPC interaction (animals flee from NPCs)")
    print("  - Fish schooling behavior")
    print("  - Pet dogs following NPCs")
    print("  - Grazing deer, hunting cats, soaring birds")
    print("\nControls:")
    print("  Arrow keys: Move camera")
    print("  SPACE: Spawn random animal at center")
    print("  ESC: Exit")
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
                elif event.key == pygame.K_SPACE:
                    # Spawn random animal
                    animal_types = ['bird', 'dog', 'cat', 'deer', 'rat', 'raccoon', 'bird_of_prey']
                    animal_type = random.choice(animal_types)
                    animal_mgr.spawn_animal(animal_type)

        # Handle camera movement
        keys = pygame.key.get_pressed()
        camera_speed = 200 * dt
        if keys[pygame.K_LEFT]:
            camera_x -= camera_speed
        if keys[pygame.K_RIGHT]:
            camera_x += camera_speed
        if keys[pygame.K_UP]:
            camera_y -= camera_speed
        if keys[pygame.K_DOWN]:
            camera_y += camera_speed

        # Update NPCs (simple movement)
        for npc in npcs:
            if random.random() < 0.02:  # Occasionally change direction
                npc.velocity_x = random.uniform(-2, 2)
                npc.velocity_y = random.uniform(-2, 2)
            npc.x += npc.velocity_x
            npc.y += npc.velocity_y

        # Update animals
        animal_mgr.update(dt, npcs=npcs)

        # Clear screen
        screen.fill((40, 80, 40))  # Green grass background

        # Draw spawn zones
        # Water
        pygame.draw.circle(screen, (50, 100, 200, 128),
                         (int(200 - camera_x), int(700 - camera_y)), 150)
        # Forest
        pygame.draw.circle(screen, (20, 60, 20, 128),
                         (int(1200 - camera_x), int(200 - camera_y)), 100)
        # Park
        pygame.draw.circle(screen, (60, 120, 60, 128),
                         (int(700 - camera_x), int(450 - camera_y)), 200)
        # Urban
        pygame.draw.rect(screen, (100, 100, 100, 128),
                        (int(150 - camera_x), int(150 - camera_y), 300, 300))

        # Draw NPCs
        for npc in npcs:
            screen_x = int(npc.x - camera_x)
            screen_y = int(npc.y - camera_y)
            if 0 <= screen_x < 1400 and 0 <= screen_y < 900:
                # Simple NPC representation
                pygame.draw.circle(screen, (200, 200, 200), (screen_x, screen_y), 8)
                effects.draw_shadow(screen, (screen_x - 8, screen_y + 8), 16, 6, opacity=60)

        # Draw animals
        for animal in animal_mgr.animals:
            screen_x = int(animal.x - camera_x)
            screen_y = int(animal.y - camera_y)

            # Only draw if on screen
            if -50 <= screen_x < 1450 and -50 <= screen_y < 950:
                # Get sprite
                params = animal.get_sprite_params()
                sprite = sprite_gen.get_sprite(**params)

                # Draw shadow
                shadow_size = 8
                if isinstance(animal, Deer):
                    shadow_size = 12
                elif isinstance(animal, (Bird, BirdOfPrey)):
                    shadow_size = 6  # Flying animals have small shadows

                effects.draw_shadow(screen,
                                  (screen_x - shadow_size, screen_y + shadow_size),
                                  shadow_size * 2, shadow_size // 2, opacity=40)

                # Draw sprite
                sprite_rect = sprite.get_rect(center=(screen_x, screen_y))
                screen.blit(sprite, sprite_rect)

                # Draw behavior indicator
                if animal.behavior.value in ['chase', 'flee']:
                    color = (255, 100, 100) if animal.behavior.value == 'flee' else (255, 255, 100)
                    pygame.draw.circle(screen, color, (screen_x, screen_y - 15), 3)

        # Draw UI
        title = font_large.render("Animal System Demo", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 10))

        # Statistics
        stats = animal_mgr.get_statistics()
        y_offset = 70

        stats_text = [
            f"Total Animals: {stats['total_animals']}",
            f"Fish Schools: {stats['fish_schools']}",
            "",
            "Animal Counts:",
            f"  Birds: {stats['type_counts']['birds']}",
            f"  Birds of Prey: {stats['type_counts']['birds_of_prey']}",
            f"  Dogs: {stats['type_counts']['dogs']}",
            f"  Cats: {stats['type_counts']['cats']}",
            f"  Deer: {stats['type_counts']['deer']}",
            f"  Rats: {stats['type_counts']['rats']}",
            f"  Raccoons: {stats['type_counts']['raccoons']}",
            f"  Fish: {stats['type_counts']['fish']}",
            "",
            f"Total Spawned: {stats['total_spawned']}",
            f"Interactions: {stats['interactions']}",
        ]

        for text in stats_text:
            label = font_small.render(text, True, (255, 255, 255))
            screen.blit(label, (10, y_offset))
            y_offset += 22

        # Instructions
        instructions = [
            "Arrow Keys: Move Camera",
            "SPACE: Spawn Random Animal",
            "ESC: Exit",
        ]

        y_offset = screen.get_height() - 70
        for text in instructions:
            label = font_small.render(text, True, (200, 200, 200))
            screen.blit(label, (10, y_offset))
            y_offset += 22

        # FPS counter
        fps_text = font_small.render(f"FPS: {int(clock.get_fps())}", True, (100, 255, 100))
        screen.blit(fps_text, (screen.get_width() - 100, 10))

        # Cache info
        cache_info = sprite_gen.get_cache_info()
        cache_text = font_small.render(
            f"Sprite Cache: {cache_info['cached_sprites']}",
            True, (150, 150, 150)
        )
        screen.blit(cache_text, (screen.get_width() - 200, 40))

        # Update display
        pygame.display.flip()

    pygame.quit()
    print("\nAnimal system demo completed!")
    print(f"Final statistics: {animal_mgr.get_statistics()}")


if __name__ == "__main__":
    try:
        test_animal_system()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        pygame.quit()
        sys.exit(0)
