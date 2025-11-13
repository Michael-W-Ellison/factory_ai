"""
Main game class - handles the core game loop.

This is a starter template. You'll expand this as you progress through
the development phases.
"""

import pygame
import random
import config
from src.world.grid import Grid
from src.rendering.camera import Camera
from src.systems.entity_manager import EntityManager
from src.systems.resource_manager import ResourceManager
from src.systems.building_manager import BuildingManager
from src.systems.power_manager import PowerManager
from src.ui.hud import HUD
from src.entities.buildings import Factory, LandfillGasExtraction


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

        # Initialize game systems
        self.resources = ResourceManager()
        self.buildings = BuildingManager(self.grid)
        self.power = PowerManager(self.buildings)
        self.entities = EntityManager(grid=self.grid, resource_manager=self.resources)
        self.ui = HUD(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

        # Place starting buildings
        self._place_starting_buildings()

        # Create initial game entities
        self._create_test_entities()

        print("Game initialized successfully!")
        print(f"World size: {config.WORLD_WIDTH}x{config.WORLD_HEIGHT} pixels")
        print(f"Grid size: {grid_width}x{grid_height} tiles")

    def _place_starting_buildings(self):
        """Place the starting buildings (Factory and Landfill Gas Extraction)."""
        # Calculate center of world in grid coordinates
        center_grid_x = (config.WORLD_WIDTH // config.TILE_SIZE) // 2
        center_grid_y = (config.WORLD_HEIGHT // config.TILE_SIZE) // 2

        # Place Factory at center (5x5)
        factory = Factory(center_grid_x - 2, center_grid_y - 2)
        if self.buildings.place_building(factory):
            # Set factory position for robots
            factory_world_x = factory.x + factory.width // 2
            factory_world_y = factory.y + factory.height // 2
            self.entities.set_factory_position(factory_world_x, factory_world_y)
            print(f"Factory placed at grid ({factory.grid_x}, {factory.grid_y})")

        # Place Landfill Gas Extraction near landfill area (left side)
        # Landfill is roughly at grid coordinates (5-25, 10-30)
        gas_extraction = LandfillGasExtraction(15, 20)
        if self.buildings.place_building(gas_extraction):
            print(f"Landfill Gas Extraction placed at grid ({gas_extraction.grid_x}, {gas_extraction.grid_y})")

    def _create_test_entities(self):
        """Create test robots and collectibles for gameplay demonstration."""
        # Create robots near the factory (center of world)
        center_x = config.WORLD_WIDTH // 2
        center_y = config.WORLD_HEIGHT // 2

        # Create 2 autonomous robots
        self.entities.create_robot(center_x - 50, center_y + 100, autonomous=True)
        self.entities.create_robot(center_x + 50, center_y + 100, autonomous=True)

        # Create 1 manual robot for player control
        manual_robot = self.entities.create_robot(center_x, center_y + 150, autonomous=False)
        self.entities.select_robot(manual_robot)

        # Create collectibles in the landfill area (left side)
        # The landfill is roughly at x: 5-25 tiles, y: 10-30 tiles
        material_types = ['plastic', 'metal', 'glass', 'paper', 'rubber', 'organic', 'wood', 'electronic']

        # Create 30 random collectibles in the landfill area
        for _ in range(30):
            x = random.randint(5 * config.TILE_SIZE, 25 * config.TILE_SIZE)
            y = random.randint(10 * config.TILE_SIZE, 30 * config.TILE_SIZE)
            material = random.choice(material_types)
            quantity = random.uniform(5, 50)  # 5-50 kg
            self.entities.create_collectible(x, y, material, quantity)

        # Create some collectibles near the factory for easy testing
        for i in range(5):
            x = center_x + random.randint(-150, 150)
            y = center_y + random.randint(-100, -20)
            material = random.choice(material_types)
            quantity = random.uniform(10, 30)
            self.entities.create_collectible(x, y, material, quantity)

        print(f"Created {len(self.entities.robots)} robots and {len(self.entities.collectibles)} collectibles")

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

                # Try to select a robot
                selected = self.entities.select_robot_at(world_x, world_y)
                if selected:
                    print(f"Selected {selected}")
                else:
                    # If no robot selected, show tile info
                    grid_x, grid_y = self.grid.world_to_grid(world_x, world_y)
                    tile = self.grid.get_tile(grid_x, grid_y)
                    if tile:
                        print(f"Clicked tile {tile} at world({world_x:.0f}, {world_y:.0f})")

    def update(self, dt):
        """Update game logic."""
        # Adjust delta time by game speed
        adjusted_dt = dt * self.game_speed

        # Handle robot movement input
        self._handle_robot_input()

        # Update camera
        self.camera.update(adjusted_dt)

        # Update grid
        self.grid.update(adjusted_dt)

        # Update buildings
        self.buildings.update(adjusted_dt)

        # Update power system
        self.power.update(adjusted_dt, self.buildings)

        # Update entities (includes collection mechanics)
        self.entities.update(adjusted_dt)

        # Update resources
        self.resources.update(adjusted_dt)

    def _handle_robot_input(self):
        """Handle arrow key input for controlling the selected robot."""
        if not self.entities.selected_robot:
            return

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        # Arrow keys for robot movement
        if keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_DOWN]:
            dy = 1
        if keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_RIGHT]:
            dx = 1

        # Set robot velocity
        if dx != 0 or dy != 0:
            self.entities.selected_robot.move(dx, dy)

    def render(self):
        """Render game to screen."""
        # Clear screen
        self.screen.fill((20, 20, 20))  # Dark gray background

        # Render grid
        self.grid.render(self.screen, self.camera, config.SHOW_GRID)

        # Render buildings (before entities so robots appear on top)
        self.buildings.render(self.screen, self.camera)

        # Render entities
        self.entities.render(self.screen, self.camera)

        # Render HUD (overlays everything)
        self.ui.render(self.screen, self.resources, self.entities, self.clock)

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
