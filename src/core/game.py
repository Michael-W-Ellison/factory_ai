"""
Main game class - handles the core game loop.

This is a starter template. You'll expand this as you progress through
the development phases.
"""

import pygame
import config


class Game:
    """Main game controller."""

    def __init__(self):
        """Initialize the game."""
        # Initialize Pygame
        pygame.init()

        # Create game window
        self.screen = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(config.WINDOW_TITLE)

        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()

        # Game state
        self.running = True
        self.paused = False
        self.game_speed = 1.0

        # TODO: Initialize game systems as you build them
        # self.world = WorldManager()
        # self.entities = EntityManager()
        # self.resources = ResourceManager()
        # self.ui = UIManager()

        print("Game initialized successfully!")

    def run(self):
        """Main game loop."""
        print("Starting game loop...")

        while self.running:
            # Calculate delta time (time since last frame)
            dt = self.clock.tick(config.FPS) / 1000.0  # Convert to seconds

            # Process events
            self.handle_events()

            # Update game state (unless paused)
            if not self.paused:
                self.update(dt)

            # Render to screen
            self.render()

        # Clean up
        pygame.quit()
        print("Game ended.")

    def handle_events(self):
        """Process user input and system events."""
        for event in pygame.event.get():
            # Window close button
            if event.type == pygame.QUIT:
                self.running = False

            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                # ESC to quit
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # Space to pause
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    print(f"Game {'paused' if self.paused else 'resumed'}")

            # Mouse events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                print(f"Mouse clicked at ({mouse_x}, {mouse_y})")

    def update(self, dt):
        """Update game logic."""
        # Adjust delta time by game speed
        adjusted_dt = dt * self.game_speed

        # TODO: Update game systems
        # self.world.update(adjusted_dt)
        # self.entities.update(adjusted_dt)
        # self.resources.update(adjusted_dt)

        pass

    def render(self):
        """Render game to screen."""
        # Clear screen
        self.screen.fill((0, 0, 0))  # Black background

        # TODO: Render game elements
        # self.world.render(self.screen)
        # self.entities.render(self.screen)
        # self.ui.render(self.screen)

        # Temporary: Show "Hello World" message
        font = pygame.font.Font(None, 74)
        text = font.render("Recycling Factory", True, (0, 255, 0))
        text_rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)

        # Show instructions
        small_font = pygame.font.Font(None, 36)
        instructions = [
            "Press SPACE to pause",
            "Press ESC to quit",
            "Click anywhere with mouse"
        ]
        y_offset = config.SCREEN_HEIGHT // 2 + 100
        for instruction in instructions:
            text_surface = small_font.render(instruction, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(config.SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text_surface, text_rect)
            y_offset += 40

        # Show FPS if debug mode
        if config.DEBUG_MODE and config.SHOW_FPS:
            fps = int(self.clock.get_fps())
            fps_text = small_font.render(f"FPS: {fps}", True, (255, 255, 0))
            self.screen.blit(fps_text, (10, 10))

        # Update display
        pygame.display.flip()
