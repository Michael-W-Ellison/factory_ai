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

        # Draw grid lines
        if show_grid:
            pygame.draw.rect(screen, (30, 30, 30), rect, 1)

        # Draw occupied indicator if needed (for debugging)
        if self.occupied:
            center_x = x + tile_size // 2
            center_y = y + tile_size // 2
            pygame.draw.circle(screen, (255, 0, 0), (center_x, center_y), 3)

    def __repr__(self):
        """String representation for debugging."""
        return f"Tile({self.grid_x}, {self.grid_y}, type={self.tile_type})"
