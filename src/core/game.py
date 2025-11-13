"""
Main game class - handles the core game loop.

This is a starter template. You'll expand this as you progress through
the development phases.
"""

import pygame
import config
from src.world.grid import Grid
from src.rendering.camera import Camera


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

        # Initialize camera
        self.camera = Camera(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

        # Initialize grid (world size from config)
        grid_width = config.WORLD_WIDTH // config.TILE_SIZE
        grid_height = config.WORLD_HEIGHT // config.TILE_SIZE
        self.grid = Grid(grid_width, grid_height, config.TILE_SIZE)

        # Set camera bounds to world size
        self.camera.set_bounds(config.WORLD_WIDTH, config.WORLD_HEIGHT)

        # Create test world
        self.grid.create_test_world()

        # Center camera on factory (middle of world)
        self.camera.center_on(config.WORLD_WIDTH // 2, config.WORLD_HEIGHT // 2)

        # TODO: Initialize other game systems as you build them
        # self.entities = EntityManager()
        # self.resources = ResourceManager()
        # self.ui = UIManager()

        print("Game initialized successfully!")
        print(f"World size: {config.WORLD_WIDTH}x{config.WORLD_HEIGHT} pixels")
        print(f"Grid size: {grid_width}x{grid_height} tiles")

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
                # Toggle grid display with G key
                elif event.key == pygame.K_g:
                    config.SHOW_GRID = not config.SHOW_GRID
                    print(f"Grid display: {'ON' if config.SHOW_GRID else 'OFF'}")

            # Mouse events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Convert screen coordinates to world coordinates
                world_x, world_y = self.camera.screen_to_world(mouse_x, mouse_y)
                grid_x, grid_y = self.grid.world_to_grid(world_x, world_y)
                print(f"Clicked screen({mouse_x}, {mouse_y}) -> world({world_x:.0f}, {world_y:.0f}) -> grid({grid_x}, {grid_y})")

                # Get the clicked tile
                tile = self.grid.get_tile(grid_x, grid_y)
                if tile:
                    print(f"  Tile: {tile}")

    def update(self, dt):
        """Update game logic."""
        # Adjust delta time by game speed
        adjusted_dt = dt * self.game_speed

        # Update camera
        self.camera.update(adjusted_dt)

        # Update grid
        self.grid.update(adjusted_dt)

        # TODO: Update other game systems
        # self.entities.update(adjusted_dt)
        # self.resources.update(adjusted_dt)

    def render(self):
        """Render game to screen."""
        # Clear screen
        self.screen.fill((20, 20, 20))  # Dark gray background

        # Render grid
        self.grid.render(self.screen, self.camera, config.SHOW_GRID)

        # TODO: Render other game elements
        # self.entities.render(self.screen, self.camera)
        # self.ui.render(self.screen)

        # Show FPS and debug info
        if config.DEBUG_MODE and config.SHOW_FPS:
            font = pygame.font.Font(None, 24)
            fps = int(self.clock.get_fps())
            fps_text = font.render(f"FPS: {fps}", True, (255, 255, 0))
            self.screen.blit(fps_text, (10, 10))

            # Show camera position
            cam_text = font.render(f"Camera: ({self.camera.x:.0f}, {self.camera.y:.0f})", True, (255, 255, 0))
            self.screen.blit(cam_text, (10, 35))

            # Show controls
            controls = [
                "WASD/Arrows: Move camera",
                "G: Toggle grid",
                "Space: Pause",
                "ESC: Quit"
            ]
            y_offset = config.SCREEN_HEIGHT - 110
            for control in controls:
                text = font.render(control, True, (200, 200, 200))
                self.screen.blit(text, (10, y_offset))
                y_offset += 25

        # Show paused indicator
        if self.paused:
            font = pygame.font.Font(None, 72)
            text = font.render("PAUSED", True, (255, 255, 0))
            text_rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
            # Draw semi-transparent background
            s = pygame.Surface((text_rect.width + 40, text_rect.height + 20))
            s.set_alpha(200)
            s.fill((0, 0, 0))
            self.screen.blit(s, (text_rect.x - 20, text_rect.y - 10))
            self.screen.blit(text, text_rect)

        # Update display
        pygame.display.flip()
