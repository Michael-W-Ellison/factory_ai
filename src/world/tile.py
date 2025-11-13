"""
Tile class - represents a single tile in the game world.
"""

import pygame
from src.core.constants import Colors


class TileType:
    """Tile type enumeration."""
    EMPTY = 0
    LANDFILL = 1
    GRASS = 2
    DIRT = 3
    ROAD_DIRT = 4
    ROAD_TAR = 5
    ROAD_ASPHALT = 6
    FACTORY = 7
    BUILDING = 8


class TerrainType:
    """Terrain type enumeration for geographic features."""
    LAND = 0
    WATER = 1
    BRIDGE = 2
    DOCK = 3
    OCEAN = 4


class Tile:
    """
    Represents a single tile in the game world.

    Attributes:
        grid_x (int): X position in grid
        grid_y (int): Y position in grid
        tile_type (int): Type of tile (see TileType)
        walkable (bool): Can entities move through this tile?
        occupied (bool): Is something currently on this tile?
        terrain_data (dict): Additional terrain-specific data
    """

    def __init__(self, grid_x, grid_y, tile_type=TileType.GRASS, terrain_type=None):
        """
        Initialize a tile.

        Args:
            grid_x (int): X position in grid
            grid_y (int): Y position in grid
            tile_type (int): Type of tile
            terrain_type (int): Terrain type (water, land, bridge, etc.)
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.tile_type = tile_type
        self.terrain_type = terrain_type if terrain_type is not None else TerrainType.LAND
        self.walkable = True
        self.occupied = False

        # Additional data for this tile
        self.terrain_data = {}

        # Landfill depletion tracking (0.0 = full, 1.0 = completely depleted)
        self.depletion_level = 0.0

        # Water animation frame for animated water
        self.water_anim_frame = 0

        # Visual properties
        self.color = self._get_color_for_type(tile_type)

        # Update walkability based on terrain
        self._update_walkability()

    def _get_color_for_type(self, tile_type):
        """Get the display color for this tile type."""
        color_map = {
            TileType.EMPTY: (20, 20, 20),           # Dark gray
            TileType.LANDFILL: (100, 80, 60),       # Brown
            TileType.GRASS: (50, 120, 50),          # Green
            TileType.DIRT: (139, 115, 85),          # Light brown
            TileType.ROAD_DIRT: (160, 130, 95),     # Lighter brown
            TileType.ROAD_TAR: (60, 60, 60),        # Dark gray
            TileType.ROAD_ASPHALT: (40, 40, 40),    # Very dark gray
            TileType.FACTORY: (80, 80, 120),        # Blue-gray
            TileType.BUILDING: (120, 100, 80),      # Tan
        }
        return color_map.get(tile_type, Colors.GRAY)

    def _get_landfill_color_for_depletion(self):
        """Get color for landfill tile based on depletion level."""
        # Transition from brown (full) to dirt (empty)
        full_color = (100, 80, 60)    # Brown garbage
        empty_color = (139, 115, 85)  # Dirt

        # Interpolate between colors
        r = int(full_color[0] + (empty_color[0] - full_color[0]) * self.depletion_level)
        g = int(full_color[1] + (empty_color[1] - full_color[1]) * self.depletion_level)
        b = int(full_color[2] + (empty_color[2] - full_color[2]) * self.depletion_level)

        return (r, g, b)

    def _update_walkability(self):
        """Update walkability based on tile type and terrain type."""
        # Water blocks movement (unless bridge)
        if self.terrain_type == TerrainType.WATER or self.terrain_type == TerrainType.OCEAN:
            self.walkable = False
        elif self.terrain_type == TerrainType.BRIDGE:
            self.walkable = True
        # Buildings block movement
        elif self.tile_type in [TileType.FACTORY, TileType.BUILDING]:
            self.walkable = False
        else:
            self.walkable = True

    def set_type(self, tile_type):
        """
        Change the tile type.

        Args:
            tile_type (int): New tile type
        """
        self.tile_type = tile_type
        self.color = self._get_color_for_type(tile_type)
        self._update_walkability()

    def set_terrain_type(self, terrain_type):
        """
        Change the terrain type.

        Args:
            terrain_type (int): New terrain type
        """
        self.terrain_type = terrain_type
        self._update_walkability()

    def add_depletion(self, amount: float, pollution_manager=None):
        """
        Add depletion to this tile (for landfill tiles being collected).

        Args:
            amount (float): Amount to deplete (0.0-1.0)
            pollution_manager: PollutionManager to update pollution (optional)
        """
        self.depletion_level = min(1.0, self.depletion_level + amount)

        # Update color for landfill tiles
        if self.tile_type == TileType.LANDFILL:
            self.color = self._get_landfill_color_for_depletion()

            # Update pollution generation (more trash = more pollution)
            if pollution_manager:
                fullness = 1.0 - self.depletion_level
                # Max pollution rate of 0.5 per tile when full, 0 when empty
                pollution_rate = fullness * 0.5
                pollution_manager.update_source(self.grid_x, self.grid_y, pollution_rate)

    def render(self, screen, x, y, tile_size, show_grid=True):
        """
        Render this tile to the screen.

        Args:
            screen: Pygame surface to draw on
            x (int): Screen X position
            y (int): Screen Y position
            tile_size (int): Size of tile in pixels
            show_grid (bool): Whether to draw grid lines
        """
        rect = pygame.Rect(x, y, tile_size, tile_size)

        # Render based on terrain type
        if self.terrain_type == TerrainType.WATER or self.terrain_type == TerrainType.OCEAN:
            self._render_water(screen, x, y, tile_size)
        elif self.terrain_type == TerrainType.BRIDGE:
            self._render_bridge(screen, x, y, tile_size)
        elif self.terrain_type == TerrainType.DOCK:
            self._render_dock(screen, x, y, tile_size)
        else:
            # Draw normal tile background
            pygame.draw.rect(screen, self.color, rect)

            # Draw landfill trash piles (diminish with depletion)
            if self.tile_type == TileType.LANDFILL and self.depletion_level < 1.0:
                self._render_trash_piles(screen, x, y, tile_size)

        # Draw grid lines
        if show_grid:
            pygame.draw.rect(screen, (30, 30, 30), rect, 1)

        # Draw occupied indicator if needed (for debugging)
        if self.occupied:
            center_x = x + tile_size // 2
            center_y = y + tile_size // 2
            pygame.draw.circle(screen, (255, 0, 0), (center_x, center_y), 3)

    def _render_trash_piles(self, screen, x, y, tile_size):
        """Render trash piles on landfill tiles (fewer as depletion increases)."""
        import random

        # Use tile position as seed for consistent pile placement
        rng = random.Random(self.grid_x * 1000 + self.grid_y)

        # Number of piles decreases with depletion
        remaining = 1.0 - self.depletion_level
        max_piles = 3

        for i in range(max_piles):
            # Skip piles based on depletion
            if rng.random() > remaining:
                continue

            # Random position within tile
            pile_x = x + rng.randint(tile_size // 6, tile_size * 5 // 6)
            pile_y = y + rng.randint(tile_size // 6, tile_size * 5 // 6)

            # Pile size (smaller with depletion)
            base_size = rng.randint(2, 4)
            pile_size = max(1, int(base_size * remaining))

            # Pile color (various trash colors)
            pile_colors = [
                (80, 60, 40),    # Dark brown
                (70, 70, 70),    # Gray
                (90, 70, 50),    # Brown
                (60, 60, 50),    # Dark olive
            ]
            pile_color = pile_colors[rng.randint(0, len(pile_colors) - 1)]

            # Draw pile as small circle
            pygame.draw.circle(screen, pile_color, (pile_x, pile_y), pile_size)

    def _render_water(self, screen, x, y, tile_size):
        """Render water tile with animated effect."""
        # Base water color
        if self.terrain_type == TerrainType.OCEAN:
            base_color = (10, 50, 100)  # Dark blue for ocean
        else:
            base_color = (30, 100, 180)  # Lighter blue for rivers

        # Animate water by varying color slightly
        import math
        time_offset = (self.grid_x + self.grid_y) * 0.1  # Offset based on position
        anim_value = math.sin(self.water_anim_frame * 0.1 + time_offset) * 10

        water_color = (
            min(255, max(0, int(base_color[0] + anim_value))),
            min(255, max(0, int(base_color[1] + anim_value))),
            min(255, max(0, int(base_color[2] + anim_value)))
        )

        rect = pygame.Rect(x, y, tile_size, tile_size)
        pygame.draw.rect(screen, water_color, rect)

        # Draw water ripple effect
        if tile_size >= 16:
            ripple_alpha = int(50 + anim_value * 2)
            ripple_color = (
                min(255, water_color[0] + 20),
                min(255, water_color[1] + 20),
                min(255, water_color[2] + 20)
            )

            # Draw subtle waves
            for i in range(2):
                wave_y = y + tile_size // 3 + i * tile_size // 3 + int(anim_value * 0.3)
                pygame.draw.line(screen, ripple_color, (x, wave_y), (x + tile_size, wave_y), 1)

    def _render_bridge(self, screen, x, y, tile_size):
        """Render bridge tile."""
        # Draw water underneath
        water_color = (30, 100, 180)
        rect = pygame.Rect(x, y, tile_size, tile_size)
        pygame.draw.rect(screen, water_color, rect)

        # Draw bridge planks
        bridge_color = (120, 100, 80)  # Brown
        plank_height = max(tile_size // 5, 2)

        # Horizontal planks
        for i in range(3):
            plank_y = y + i * tile_size // 3 + tile_size // 6
            plank_rect = pygame.Rect(x, plank_y, tile_size, plank_height)
            pygame.draw.rect(screen, bridge_color, plank_rect)
            pygame.draw.rect(screen, (80, 60, 40), plank_rect, 1)  # Dark border

        # Bridge supports (vertical bars)
        support_color = (100, 80, 60)
        support_width = max(tile_size // 8, 2)
        for i in [0, 2]:
            support_x = x + i * tile_size // 3 + tile_size // 6
            support_rect = pygame.Rect(support_x, y, support_width, tile_size)
            pygame.draw.rect(screen, support_color, support_rect)

    def _render_dock(self, screen, x, y, tile_size):
        """Render dock tile."""
        # Draw water on one side, dock platform on other
        water_color = (30, 100, 180)
        dock_color = (100, 90, 70)

        # Half water, half dock
        water_rect = pygame.Rect(x, y, tile_size // 2, tile_size)
        dock_rect = pygame.Rect(x + tile_size // 2, y, tile_size // 2, tile_size)

        pygame.draw.rect(screen, water_color, water_rect)
        pygame.draw.rect(screen, dock_color, dock_rect)

        # Draw dock planks
        plank_color = (120, 100, 80)
        for i in range(4):
            plank_y = y + i * tile_size // 4
            plank_rect = pygame.Rect(x + tile_size // 2, plank_y, tile_size // 2, max(2, tile_size // 8))
            pygame.draw.rect(screen, plank_color, plank_rect)

        # Draw dock posts
        post_color = (80, 70, 50)
        post_width = max(2, tile_size // 10)
        for i in [0, 2]:
            post_x = x + tile_size // 2 + i * tile_size // 4
            post_rect = pygame.Rect(post_x, y, post_width, tile_size)
            pygame.draw.rect(screen, post_color, post_rect)

    def update_animation(self, dt):
        """
        Update tile animation (for water, etc.).

        Args:
            dt (float): Delta time in seconds
        """
        # Update water animation frame
        if self.terrain_type in [TerrainType.WATER, TerrainType.OCEAN]:
            self.water_anim_frame += dt * 10  # Animation speed
            if self.water_anim_frame > 360:
                self.water_anim_frame -= 360

    def __repr__(self):
        """String representation for debugging."""
        return f"Tile({self.grid_x}, {self.grid_y}, type={self.tile_type}, terrain={self.terrain_type})"
