"""
Grid class - manages the tile-based game world.
"""

import pygame
import random
from src.world.tile import Tile, TileType


class Grid:
    """
    Manages the tile-based game world.

    The grid is the foundation of the game - everything exists on tiles.
    """

    def __init__(self, width_tiles, height_tiles, tile_size=32):
        """
        Initialize the grid.

        Args:
            width_tiles (int): Width of grid in tiles
            height_tiles (int): Height of grid in tiles
            tile_size (int): Size of each tile in pixels
        """
        self.width_tiles = width_tiles
        self.height_tiles = height_tiles
        self.tile_size = tile_size

        # World dimensions in pixels
        self.world_width = width_tiles * tile_size
        self.world_height = height_tiles * tile_size

        # Create 2D array of tiles
        self.tiles = []
        for y in range(height_tiles):
            row = []
            for x in range(width_tiles):
                tile = Tile(x, y, TileType.GRASS)
                row.append(tile)
            self.tiles.append(row)

        print(f"Grid created: {width_tiles}x{height_tiles} tiles ({self.world_width}x{self.world_height} pixels)")

    def get_tile(self, grid_x, grid_y):
        """
        Get tile at grid coordinates.

        Args:
            grid_x (int): X position in grid
            grid_y (int): Y position in grid

        Returns:
            Tile or None if out of bounds
        """
        if 0 <= grid_x < self.width_tiles and 0 <= grid_y < self.height_tiles:
            return self.tiles[grid_y][grid_x]
        return None

    def get_tile_at_world_pos(self, world_x, world_y):
        """
        Get tile at world pixel coordinates.

        Args:
            world_x (int): X position in world pixels
            world_y (int): Y position in world pixels

        Returns:
            Tile or None if out of bounds
        """
        grid_x = int(world_x // self.tile_size)
        grid_y = int(world_y // self.tile_size)
        return self.get_tile(grid_x, grid_y)

    def world_to_grid(self, world_x, world_y):
        """
        Convert world pixel coordinates to grid coordinates.

        Args:
            world_x (int): X position in world pixels
            world_y (int): Y position in world pixels

        Returns:
            tuple: (grid_x, grid_y)
        """
        grid_x = int(world_x // self.tile_size)
        grid_y = int(world_y // self.tile_size)
        return (grid_x, grid_y)

    def grid_to_world(self, grid_x, grid_y):
        """
        Convert grid coordinates to world pixel coordinates (top-left of tile).

        Args:
            grid_x (int): X position in grid
            grid_y (int): Y position in grid

        Returns:
            tuple: (world_x, world_y)
        """
        world_x = grid_x * self.tile_size
        world_y = grid_y * self.tile_size
        return (world_x, world_y)

    def set_tile_type(self, grid_x, grid_y, tile_type):
        """
        Change the type of a tile.

        Args:
            grid_x (int): X position in grid
            grid_y (int): Y position in grid
            tile_type (int): New tile type
        """
        tile = self.get_tile(grid_x, grid_y)
        if tile:
            tile.set_type(tile_type)

    def create_test_world(self):
        """
        Create a simple test world for demonstration.
        This will be replaced with proper world generation later.
        """
        # Center area - factory zone (grass)
        center_x = self.width_tiles // 2
        center_y = self.height_tiles // 2

        # Create a 10x10 factory area in the center
        for y in range(center_y - 5, center_y + 5):
            for x in range(center_x - 5, center_x + 5):
                if 0 <= x < self.width_tiles and 0 <= y < self.height_tiles:
                    self.tiles[y][x].set_type(TileType.GRASS)

        # Add a simple factory building (5x5)
        for y in range(center_y - 2, center_y + 3):
            for x in range(center_x - 2, center_x + 3):
                if 0 <= x < self.width_tiles and 0 <= y < self.height_tiles:
                    self.tiles[y][x].set_type(TileType.FACTORY)

        # Create a road leading from factory to the left (dirt road)
        road_y = center_y
        for x in range(center_x - 10, center_x - 2):
            if 0 <= x < self.width_tiles:
                self.tiles[road_y][x].set_type(TileType.ROAD_DIRT)

        # Create landfill area to the left
        for y in range(10, 30):
            for x in range(5, 25):
                if 0 <= x < self.width_tiles and 0 <= y < self.height_tiles:
                    # Randomize landfill appearance slightly
                    if random.random() < 0.8:
                        self.tiles[y][x].set_type(TileType.LANDFILL)
                    else:
                        self.tiles[y][x].set_type(TileType.DIRT)

        # Create a city area to the right
        for y in range(10, 40):
            for x in range(self.width_tiles - 30, self.width_tiles - 10):
                if 0 <= x < self.width_tiles and 0 <= y < self.height_tiles:
                    # Create a grid pattern for city
                    if x % 8 in [0, 7] or y % 8 in [0, 7]:
                        # Roads
                        self.tiles[y][x].set_type(TileType.ROAD_TAR)
                    elif random.random() < 0.6:
                        # Buildings
                        self.tiles[y][x].set_type(TileType.BUILDING)
                    else:
                        # Grass
                        self.tiles[y][x].set_type(TileType.GRASS)

        print("Test world created with factory, landfill, and city areas")

    def render(self, screen, camera, show_grid=True):
        """
        Render the visible portion of the grid.

        Args:
            screen: Pygame surface to draw on
            camera: Camera object for view transformation
            show_grid (bool): Whether to show grid lines
        """
        # Calculate which tiles are visible
        start_x = max(0, int(camera.x // self.tile_size))
        start_y = max(0, int(camera.y // self.tile_size))

        # Add extra tiles to ensure screen is fully covered
        end_x = min(self.width_tiles, int((camera.x + camera.width) // self.tile_size) + 2)
        end_y = min(self.height_tiles, int((camera.y + camera.height) // self.tile_size) + 2)

        # Render visible tiles
        for grid_y in range(start_y, end_y):
            for grid_x in range(start_x, end_x):
                tile = self.tiles[grid_y][grid_x]

                # Calculate screen position
                world_x = grid_x * self.tile_size
                world_y = grid_y * self.tile_size
                screen_x = world_x - camera.x
                screen_y = world_y - camera.y

                # Render the tile
                tile.render(screen, screen_x, screen_y, self.tile_size, show_grid)

    def update(self, dt):
        """
        Update grid state (placeholder for future use).

        Args:
            dt (float): Delta time in seconds
        """
        # For now, the grid doesn't need updating
        # Later, this could handle things like:
        # - Landfill regeneration
        # - Terrain changes
        # - Environmental effects
        pass

    def __repr__(self):
        """String representation for debugging."""
        return f"Grid({self.width_tiles}x{self.height_tiles}, tile_size={self.tile_size})"
