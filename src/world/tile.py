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

    def __init__(self, grid_x, grid_y, tile_type=TileType.GRASS):
        """
        Initialize a tile.

        Args:
            grid_x (int): X position in grid
            grid_y (int): Y position in grid
            tile_type (int): Type of tile
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.tile_type = tile_type
        self.walkable = True
        self.occupied = False

        # Additional data for this tile
        self.terrain_data = {}

        # Landfill depletion tracking (0.0 = full, 1.0 = completely depleted)
        self.depletion_level = 0.0

        # Visual properties
        self.color = self._get_color_for_type(tile_type)

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

    def set_type(self, tile_type):
        """
        Change the tile type.

        Args:
            tile_type (int): New tile type
        """
        self.tile_type = tile_type
        self.color = self._get_color_for_type(tile_type)

        # Update walkability based on type
        if tile_type in [TileType.FACTORY, TileType.BUILDING]:
            self.walkable = False
        else:
            self.walkable = True

    def add_depletion(self, amount: float):
        """
        Add depletion to this tile (for landfill tiles being collected).

        Args:
            amount (float): Amount to deplete (0.0-1.0)
        """
        self.depletion_level = min(1.0, self.depletion_level + amount)

        # Update color for landfill tiles
        if self.tile_type == TileType.LANDFILL:
            self.color = self._get_landfill_color_for_depletion()

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
        # Draw tile background
        rect = pygame.Rect(x, y, tile_size, tile_size)
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

    def __repr__(self):
        """String representation for debugging."""
        return f"Tile({self.grid_x}, {self.grid_y}, type={self.tile_type})"
