"""
Minimap UI - Small overview map of the game world.

Displays a scaled-down view of the entire world showing:
- Terrain/tiles
- Buildings
- Robots
- NPCs
- Camera viewport
- Click-to-move camera functionality
"""

import pygame
from typing import Optional


class Minimap:
    """
    Minimap overlay showing the game world overview.

    Provides navigation and situational awareness with:
    - Scaled world view
    - Entity markers
    - Camera viewport indicator
    - Click-to-move camera
    """

    def __init__(self, screen_width: int, screen_height: int, world_width: int, world_height: int):
        """
        Initialize the minimap.

        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
            world_width: Width of the game world in pixels
            world_height: Height of the game world in pixels
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = world_width
        self.world_height = world_height

        # Visibility
        self.visible = True  # Minimap starts visible

        # Minimap dimensions (bottom-right corner)
        self.minimap_width = 250
        self.minimap_height = 180
        self.minimap_x = screen_width - self.minimap_width - 10
        self.minimap_y = screen_height - self.minimap_height - 10

        # Scaling factors
        self.scale_x = self.minimap_width / world_width
        self.scale_y = self.minimap_height / world_height

        # Colors
        self.color_bg = (20, 20, 30)
        self.color_border = (100, 150, 255)
        self.color_landfill = (100, 80, 60)
        self.color_city = (80, 80, 100)
        self.color_road = (60, 60, 70)
        self.color_water = (40, 80, 120)
        self.color_building = (200, 150, 50)
        self.color_robot = (100, 255, 100)
        self.color_npc = (255, 100, 100)
        self.color_camera = (255, 255, 100)
        self.color_factory = (255, 200, 50)

        # Fonts
        self.font_small = pygame.font.Font(None, 18)

        # Interaction
        self.hovering = False

    def toggle(self):
        """Toggle minimap visibility."""
        self.visible = not self.visible

    def show(self):
        """Show the minimap."""
        self.visible = True

    def hide(self):
        """Hide the minimap."""
        self.visible = False

    def world_to_minimap(self, world_x: float, world_y: float) -> tuple:
        """
        Convert world coordinates to minimap coordinates.

        Args:
            world_x: World X coordinate
            world_y: World Y coordinate

        Returns:
            Tuple of (minimap_x, minimap_y)
        """
        minimap_x = int(world_x * self.scale_x) + self.minimap_x
        minimap_y = int(world_y * self.scale_y) + self.minimap_y
        return (minimap_x, minimap_y)

    def minimap_to_world(self, minimap_x: int, minimap_y: int) -> tuple:
        """
        Convert minimap coordinates to world coordinates.

        Args:
            minimap_x: Minimap X coordinate
            minimap_y: Minimap Y coordinate

        Returns:
            Tuple of (world_x, world_y)
        """
        # Adjust for minimap position
        local_x = minimap_x - self.minimap_x
        local_y = minimap_y - self.minimap_y

        # Scale to world coordinates
        world_x = local_x / self.scale_x
        world_y = local_y / self.scale_y

        return (world_x, world_y)

    def is_point_on_minimap(self, screen_x: int, screen_y: int) -> bool:
        """
        Check if a screen point is on the minimap.

        Args:
            screen_x: Screen X coordinate
            screen_y: Screen Y coordinate

        Returns:
            True if point is on minimap, False otherwise
        """
        return (self.minimap_x <= screen_x <= self.minimap_x + self.minimap_width and
                self.minimap_y <= screen_y <= self.minimap_y + self.minimap_height)

    def handle_click(self, screen_x: int, screen_y: int, camera) -> bool:
        """
        Handle click on minimap to move camera.

        Args:
            screen_x: Click X coordinate
            screen_y: Click Y coordinate
            camera: Camera object to move

        Returns:
            True if click was on minimap, False otherwise
        """
        if not self.visible:
            return False

        if self.is_point_on_minimap(screen_x, screen_y):
            # Convert to world coordinates
            world_x, world_y = self.minimap_to_world(screen_x, screen_y)

            # Center camera on this position
            camera.center_on(world_x, world_y)
            return True

        return False

    def render(self, screen: pygame.Surface, grid, entity_manager, camera, building_manager=None):
        """
        Render the minimap.

        Args:
            screen: Pygame surface to render to
            grid: Grid object with tile data
            entity_manager: EntityManager with robots
            camera: Camera object for viewport indicator
            building_manager: BuildingManager with buildings (optional)
        """
        if not self.visible:
            return

        # Create minimap surface
        minimap_surface = pygame.Surface((self.minimap_width, self.minimap_height))
        minimap_surface.fill(self.color_bg)

        # Render terrain/tiles (simplified)
        self._render_terrain(minimap_surface, grid)

        # Render buildings
        if building_manager:
            self._render_buildings(minimap_surface, building_manager)

        # Render entities (robots, NPCs)
        self._render_entities(minimap_surface, entity_manager)

        # Render camera viewport
        self._render_viewport(minimap_surface, camera)

        # Border
        pygame.draw.rect(minimap_surface, self.color_border, (0, 0, self.minimap_width, self.minimap_height), 2)

        # Title
        title_text = self.font_small.render("Map (M)", True, (200, 200, 200))
        minimap_surface.blit(title_text, (5, 3))

        # Blit minimap to screen
        screen.blit(minimap_surface, (self.minimap_x, self.minimap_y))

        # Hover indicator
        if self.hovering:
            # Draw subtle highlight
            hover_surface = pygame.Surface((self.minimap_width, self.minimap_height))
            hover_surface.set_alpha(30)
            hover_surface.fill((255, 255, 255))
            screen.blit(hover_surface, (self.minimap_x, self.minimap_y))

    def _render_terrain(self, surface: pygame.Surface, grid):
        """Render simplified terrain on minimap."""
        # Sample tiles for performance (don't render every single tile)
        sample_rate = 4  # Sample every 4th tile

        for y in range(0, grid.height, sample_rate):
            for x in range(0, grid.width, sample_rate):
                tile = grid.get_tile(x, y)
                if tile:
                    # Determine color based on tile type
                    color = self.color_bg

                    tile_type = tile.tile_type.name if hasattr(tile.tile_type, 'name') else str(tile.tile_type)

                    if 'LANDFILL' in tile_type:
                        color = self.color_landfill
                    elif 'CITY' in tile_type or 'BUILDING' in tile_type:
                        color = self.color_city
                    elif 'ROAD' in tile_type:
                        color = self.color_road
                    elif 'WATER' in tile_type or 'RIVER' in tile_type or 'OCEAN' in tile_type:
                        color = self.color_water

                    # Draw tile as small rectangle
                    world_x = x * grid.tile_size
                    world_y = y * grid.tile_size
                    minimap_x = int(world_x * self.scale_x)
                    minimap_y = int(world_y * self.scale_y)

                    # Draw a small rect (scaled tile size)
                    tile_width = max(1, int(grid.tile_size * self.scale_x * sample_rate))
                    tile_height = max(1, int(grid.tile_size * self.scale_y * sample_rate))

                    pygame.draw.rect(surface, color, (minimap_x, minimap_y, tile_width, tile_height))

    def _render_buildings(self, surface: pygame.Surface, building_manager):
        """Render buildings on minimap."""
        for building in building_manager.buildings.values():
            # Get building world position (in pixels)
            world_x = building.x * building_manager.grid.tile_size
            world_y = building.y * building_manager.grid.tile_size

            # Convert to minimap coordinates
            minimap_x = int(world_x * self.scale_x)
            minimap_y = int(world_y * self.scale_y)

            # Determine color (highlight factory)
            if hasattr(building, 'building_type'):
                building_type_name = building.building_type.name if hasattr(building.building_type, 'name') else str(building.building_type)
                color = self.color_factory if 'FACTORY' in building_type_name else self.color_building
            else:
                color = self.color_building

            # Draw building as a small square (2-4 pixels)
            size = 3 if hasattr(building, 'building_type') and 'FACTORY' in str(building.building_type) else 2
            pygame.draw.rect(surface, color, (minimap_x, minimap_y, size, size))

    def _render_entities(self, surface: pygame.Surface, entity_manager):
        """Render entities (robots, NPCs) on minimap."""
        # Render robots
        if hasattr(entity_manager, 'robots'):
            for robot in entity_manager.robots:
                minimap_x, minimap_y = self.world_to_minimap(robot.x, robot.y)

                # Adjust to local coordinates
                local_x = minimap_x - self.minimap_x
                local_y = minimap_y - self.minimap_y

                # Draw robot as small dot
                pygame.draw.circle(surface, self.color_robot, (local_x, local_y), 2)

        # Render NPCs if available
        # (Assuming entity_manager might have npcs or we get them from elsewhere)
        # For now, we'll skip NPCs as they might be in a separate manager

    def _render_viewport(self, surface: pygame.Surface, camera):
        """Render camera viewport rectangle on minimap."""
        # Get camera viewport in world coordinates
        viewport_world_x = camera.x
        viewport_world_y = camera.y
        viewport_world_width = camera.width
        viewport_world_height = camera.height

        # Convert to minimap coordinates
        minimap_vp_x = int(viewport_world_x * self.scale_x)
        minimap_vp_y = int(viewport_world_y * self.scale_y)
        minimap_vp_width = int(viewport_world_width * self.scale_x)
        minimap_vp_height = int(viewport_world_height * self.scale_y)

        # Draw viewport rectangle
        pygame.draw.rect(surface, self.color_camera,
                        (minimap_vp_x, minimap_vp_y, minimap_vp_width, minimap_vp_height), 2)

    def update(self, mouse_pos: tuple):
        """
        Update minimap state (hover detection, etc.).

        Args:
            mouse_pos: Current mouse position (x, y)
        """
        if self.visible:
            self.hovering = self.is_point_on_minimap(mouse_pos[0], mouse_pos[1])
