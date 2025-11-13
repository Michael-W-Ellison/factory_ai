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
from src.systems.research_manager import ResearchManager
from src.systems.pollution_manager import PollutionManager
from src.systems.vehicle_manager import VehicleManager
from src.systems.fence_manager import FenceManager
from src.systems.npc_manager import NPCManager
from src.systems.detection_manager import DetectionManager
from src.systems.suspicion_manager import SuspicionManager
from src.systems.police_manager import PoliceManager
from src.ui.hud import HUD
from src.ui.research_ui import ResearchUI
from src.entities.buildings import Factory, LandfillGasExtraction
from src.world.river_generator import RiverGenerator
from src.world.bridge_builder import BridgeBuilder
from src.systems.road_network import RoadNetwork
from src.systems.traffic_manager import TrafficManager
from src.systems.bus_manager import BusManager
from src.systems.prop_manager import PropManager
from src.systems.camera_manager import CameraManager


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

        # Generate procedural city
        self.grid.generate_city(seed=42)  # Use seed for consistent testing

        # Initialize geographic features (rivers, bridges, ocean)
        self.river_generator = RiverGenerator(self.grid, seed=42)
        self.bridge_builder = BridgeBuilder(self.grid, resource_manager=None)

        # Generate geographic features
        self._generate_geographic_features()

        # Initialize traffic system (road network and traffic manager)
        self.road_network = RoadNetwork(self.grid)
        self.traffic_manager = TrafficManager(self.grid, self.road_network)
        self.traffic_manager.set_target_vehicle_count(10)  # Moderate traffic

        # Initialize bus system (public transportation)
        self.bus_manager = BusManager(self.grid, self.road_network)
        self.bus_manager.target_routes = 3  # Generate 3 bus routes
        self.bus_manager.buses_per_route = 2  # 2 buses per route
        self.bus_manager.generate_routes()
        self.bus_manager.spawn_buses()

        # Initialize prop system (benches, light poles, trash cans, bicycles)
        self.prop_manager = PropManager(self.grid, self.road_network)
        self.prop_manager.target_prop_count = 100  # Target number of props
        self.prop_manager.generate_props()

        # Initialize camera system (security cameras for surveillance)
        self.camera_manager = CameraManager(self.grid, self.road_network)
        self.camera_manager.target_camera_count = 25  # Target number of cameras
        # Note: Police stations will be added in future phase, for now place on roads/buildings
        self.camera_manager.place_cameras()

        # Center camera on factory (middle of world)
        self.camera.center_on(config.WORLD_WIDTH // 2, config.WORLD_HEIGHT // 2)

        # Initialize game systems
        self.resources = ResourceManager()
        self.buildings = BuildingManager(self.grid)
        self.power = PowerManager(self.buildings)
        self.research = ResearchManager()
        self.pollution = PollutionManager(grid_width, grid_height)
        self.vehicles = VehicleManager(self.grid)
        self.fences = FenceManager(self.grid)
        self.npcs = NPCManager(self.grid)
        self.detection = DetectionManager(self.grid, self.npcs)
        self.suspicion = SuspicionManager()
        self.police = PoliceManager(self.grid, self.suspicion)
        self.entities = EntityManager(grid=self.grid, resource_manager=self.resources, research_manager=self.research)
        self.ui = HUD(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self.research_ui = ResearchUI(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

        # Factory reference (for visual upgrades)
        self.factory = None

        # Place starting buildings
        self._place_starting_buildings()

        # Create initial game entities
        self._create_test_entities()

        # Add test pollution sources (factory generates pollution)
        center_grid_x = (config.WORLD_WIDTH // config.TILE_SIZE) // 2
        center_grid_y = (config.WORLD_HEIGHT // config.TILE_SIZE) // 2
        self.pollution.add_source(center_grid_x, center_grid_y, 2.0)  # Factory pollution
        self.pollution.add_source(15, 20, 1.0)  # Landfill gas extraction pollution

        # Register landfill tiles as pollution sources
        self._register_landfill_pollution()

        # Spawn vehicles throughout the city
        self.vehicles.spawn_vehicles_in_city(seed=42, vehicle_density=0.4)

        # Spawn fences around buildings
        self.fences.spawn_fences_around_buildings(seed=42, fence_coverage=0.6)

        # Spawn NPCs in the city
        self.npcs.spawn_npcs_in_city(seed=42)

        # Spawn initial police patrols
        self.police.spawn_initial_patrols(seed=42)

        print("Game initialized successfully!")
        print(f"World size: {config.WORLD_WIDTH}x{config.WORLD_HEIGHT} pixels")
        print(f"Grid size: {grid_width}x{grid_height} tiles")

    def _place_starting_buildings(self):
        """Place the starting buildings (Factory and Landfill Gas Extraction)."""
        # Calculate center of world in grid coordinates
        center_grid_x = (config.WORLD_WIDTH // config.TILE_SIZE) // 2
        center_grid_y = (config.WORLD_HEIGHT // config.TILE_SIZE) // 2

        # Place Factory at center (5x5)
        self.factory = Factory(center_grid_x - 2, center_grid_y - 2)
        if self.buildings.place_building(self.factory):
            # Set factory position for robots
            factory_world_x = self.factory.x + self.factory.width // 2
            factory_world_y = self.factory.y + self.factory.height // 2
            self.entities.set_factory_position(factory_world_x, factory_world_y)
            print(f"Factory placed at grid ({self.factory.grid_x}, {self.factory.grid_y})")

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

    def _generate_geographic_features(self):
        """Generate rivers, ocean, and bridges for the game world."""
        print("Generating geographic features...")

        # Generate ocean at south edge (for aesthetic/gameplay boundary)
        ocean_stats = self.river_generator.generate_ocean(
            edges=['south'],
            depth=4,
            create_docks=True,
            dock_spacing=12
        )

        # Generate 1-2 rivers across the map
        river_count = random.randint(1, 2)
        for i in range(river_count):
            self.river_generator.generate_random_river(
                width_range=(3, 4),
                length_range=(25, 40),
                meandering=0.25,
                avoid_buildings=True
            )

        # Auto-place bridges at narrow crossing points
        bridge_results = self.bridge_builder.auto_place_bridges(
            max_bridges=3,
            max_width=6,
            min_width=2,
            pay_cost=False  # Free bridges during world generation
        )

        successful_bridges = sum(1 for success, _, _ in bridge_results if success)
        print(f"Geographic features generated: {ocean_stats['ocean_tiles']} ocean tiles, "
              f"{ocean_stats['dock_tiles']} docks, {river_count} rivers, {successful_bridges} bridges")

    def _register_landfill_pollution(self):
        """Register all landfill tiles as pollution sources based on their fullness."""
        from src.world.tile import TileType

        landfill_count = 0
        for y in range(self.grid.height_tiles):
            for x in range(self.grid.width_tiles):
                tile = self.grid.get_tile(x, y)
                if tile and tile.tile_type == TileType.LANDFILL:
                    # Calculate pollution based on fullness (inverse of depletion)
                    fullness = 1.0 - tile.depletion_level
                    pollution_rate = fullness * 0.5  # Max 0.5 per tile when full
                    if pollution_rate > 0:
                        self.pollution.add_source(x, y, pollution_rate)
                        landfill_count += 1

        print(f"Registered {landfill_count} landfill tiles as pollution sources")

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
            # Let research UI handle events first if visible
            if self.research_ui.handle_event(event, self.research, self.resources.money):
                continue  # Event was handled by research UI

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
                # R key to open research menu
                elif event.key == pygame.K_r:
                    self.research_ui.toggle()
                    print(f"Research menu: {'opened' if self.research_ui.visible else 'closed'}")
                # P key to toggle pollution overlay
                elif event.key == pygame.K_p:
                    self.pollution.toggle_overlay()

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

        # Update research
        self.research.update(adjusted_dt)

        # Update factory visual upgrades (for research_active indicator)
        if self.factory:
            self.factory.update_visual_upgrades(self.research)

        # Apply research effects to robots and buildings when research completes
        if self.research.effects_changed:
            self.entities.apply_research_effects_to_robots(self.research)
            self.buildings.apply_research_effects_to_buildings(self.research)
            self.research.effects_changed = False
            print("Applied research effects to all robots and buildings")

        # Update entities (includes collection mechanics)
        self.entities.update(adjusted_dt)

        # Update resources
        self.resources.update(adjusted_dt)

        # Update pollution
        self.pollution.update(adjusted_dt)

        # Update vehicles
        self.vehicles.update(adjusted_dt)

        # Update traffic system (moving vehicles on roads)
        self.traffic_manager.update(adjusted_dt)

        # Update bus system (public transportation)
        self.bus_manager.update(adjusted_dt)

        # Update prop system (turn lights on/off based on time - placeholder for now)
        # TODO: Integrate with day/night cycle when implemented
        is_night = False  # Placeholder - will be replaced with actual day/night check
        self.prop_manager.update(adjusted_dt, is_night)

        # Update camera system (camera timers)
        self.camera_manager.update(adjusted_dt)

        # Update fences
        self.fences.update(adjusted_dt)

        # Update NPCs
        self.npcs.update(adjusted_dt)

        # Update detection system
        detection_reports = self.detection.update(self.entities.robots, adjusted_dt)

        # Process detection reports (increase suspicion)
        tier_changed = False
        for report in detection_reports:
            changed = self.suspicion.process_detection_report(report)
            if changed:
                tier_changed = True
            # Notify police of high-level detections
            self.police.handle_detection_report(report)

        # Update suspicion (decay over time)
        self.suspicion.update(adjusted_dt, self.npcs.game_time)

        # Update police presence based on suspicion (check every tier change)
        if tier_changed:
            self.police.update_police_presence()

        # Update police
        self.police.update(adjusted_dt, self.npcs.game_time)

        # Check if police captured any robots (game over condition)
        captured = self.police.check_captures(self.entities.robots)
        if captured:
            # TODO: Implement game over
            print("⚠️ GAME OVER: Police captured robot!")

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

        # Render props (after grid, before buildings)
        self.prop_manager.render(self.screen, self.camera)

        # Render buildings (before entities so robots appear on top)
        self.buildings.render(self.screen, self.camera)

        # Render vehicles (after buildings, before entities)
        self.vehicles.render(self.screen, self.camera)

        # Render traffic vehicles (after static vehicles)
        self.traffic_manager.render(self.screen, self.camera)

        # Render bus system (buses and bus stops)
        self.bus_manager.render(self.screen, self.camera)

        # Render fences (after vehicles, before entities)
        self.fences.render(self.screen, self.camera)

        # Render NPCs (after fences, before entities)
        self.npcs.render(self.screen, self.camera)

        # Render police (after NPCs, before entities)
        self.police.render(self.screen, self.camera)

        # Render cameras (security infrastructure)
        self.camera_manager.render(self.screen, self.camera)

        # Render entities
        self.entities.render(self.screen, self.camera)

        # Render detection UI (after entities)
        self.detection.render_detection_ui(self.screen, self.camera, self.entities.robots)

        # Render pollution overlay (if enabled)
        self.pollution.render_overlay(self.screen, self.camera, config.TILE_SIZE)

        # Render HUD (overlays everything)
        self.ui.render(self.screen, self.resources, self.entities, self.clock,
                      self.power, self.buildings, self.research, self.suspicion)

        # Render research UI (if visible)
        self.research_ui.render(self.screen, self.research, self.resources.money)

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
