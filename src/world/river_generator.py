"""
RiverGenerator - procedural river generation for the game world.

Generates natural-looking rivers using random walk with directional bias.
"""

import random
import math
from src.world.tile import TerrainType


class RiverGenerator:
    """
    Generates procedural rivers on the game grid.

    Uses random walk with directional bias to create meandering rivers
    that flow across the map naturally.
    """

    def __init__(self, grid, seed=None):
        """
        Initialize river generator.

        Args:
            grid: World grid to generate rivers on
            seed (int): Random seed for reproducible generation
        """
        self.grid = grid
        self.rng = random.Random(seed)

    def generate_river(self, start_x, start_y, direction, length, width=3,
                      meandering=0.3, avoid_buildings=True):
        """
        Generate a river from a starting point.

        Args:
            start_x (int): Starting grid X position
            start_y (int): Starting grid Y position
            direction (str): Primary direction ('north', 'south', 'east', 'west')
            length (int): Approximate length in tiles
            width (int): River width in tiles (default 3)
            meandering (float): How much the river meanders (0.0-1.0, default 0.3)
            avoid_buildings (bool): Whether to stop at buildings (default True)

        Returns:
            list: List of (x, y) tuples representing river path centerline
        """
        # Direction vectors
        direction_map = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0)
        }

        if direction not in direction_map:
            print(f"Invalid direction: {direction}. Using 'south'")
            direction = 'south'

        primary_dx, primary_dy = direction_map[direction]

        # Generate centerline path using random walk
        centerline = []
        current_x, current_y = start_x, start_y

        for step in range(length):
            centerline.append((current_x, current_y))

            # Check if we're out of bounds
            if not self._in_bounds(current_x, current_y):
                break

            # Check for obstacles if avoiding buildings
            if avoid_buildings and self._is_obstacle(current_x, current_y):
                break

            # Calculate next position with meandering
            # Most of the time go in primary direction, sometimes deviate
            if self.rng.random() < (1.0 - meandering):
                # Go in primary direction
                next_x = current_x + primary_dx
                next_y = current_y + primary_dy
            else:
                # Meander - go perpendicular or diagonal
                meander_choices = self._get_meander_directions(primary_dx, primary_dy)
                meander_dx, meander_dy = self.rng.choice(meander_choices)
                next_x = current_x + meander_dx
                next_y = current_y + meander_dy

            current_x, current_y = next_x, next_y

        # Widen the river from centerline
        river_tiles = self._widen_river(centerline, width)

        # Apply river tiles to grid
        tiles_placed = 0
        for tile_x, tile_y in river_tiles:
            if self._set_water_tile(tile_x, tile_y, avoid_buildings):
                tiles_placed += 1

        print(f"Generated river: {len(centerline)} centerline tiles, "
              f"{tiles_placed} water tiles placed")

        return centerline

    def generate_random_river(self, width_range=(3, 5), length_range=(30, 60),
                             meandering=0.3, avoid_buildings=True):
        """
        Generate a river at a random location with random parameters.

        Args:
            width_range (tuple): Min/max width in tiles
            length_range (tuple): Min/max length in tiles
            meandering (float): Meandering factor (0.0-1.0)
            avoid_buildings (bool): Whether to avoid buildings

        Returns:
            list: River centerline path
        """
        # Choose random starting edge
        edge = self.rng.choice(['north', 'south', 'east', 'west'])

        # Choose random position on that edge
        if edge == 'north':
            start_x = self.rng.randint(10, self.grid.width_tiles - 10)
            start_y = 0
            direction = 'south'
        elif edge == 'south':
            start_x = self.rng.randint(10, self.grid.width_tiles - 10)
            start_y = self.grid.height_tiles - 1
            direction = 'north'
        elif edge == 'east':
            start_x = self.grid.width_tiles - 1
            start_y = self.rng.randint(10, self.grid.height_tiles - 10)
            direction = 'west'
        else:  # west
            start_x = 0
            start_y = self.rng.randint(10, self.grid.height_tiles - 10)
            direction = 'east'

        # Random width and length
        width = self.rng.randint(*width_range)
        length = self.rng.randint(*length_range)

        return self.generate_river(start_x, start_y, direction, length,
                                   width, meandering, avoid_buildings)

    def generate_multiple_rivers(self, count=3, **kwargs):
        """
        Generate multiple random rivers.

        Args:
            count (int): Number of rivers to generate
            **kwargs: Arguments passed to generate_random_river

        Returns:
            list: List of river centerline paths
        """
        rivers = []
        for i in range(count):
            river = self.generate_random_river(**kwargs)
            rivers.append(river)
        return rivers

    def _get_meander_directions(self, primary_dx, primary_dy):
        """
        Get possible meander directions perpendicular to primary direction.

        Args:
            primary_dx (int): Primary X direction
            primary_dy (int): Primary Y direction

        Returns:
            list: List of (dx, dy) tuples for meandering
        """
        if primary_dx == 0:  # Moving vertically, can meander horizontally
            return [
                (1, primary_dy),   # Diagonal right
                (-1, primary_dy),  # Diagonal left
                (1, 0),            # Right
                (-1, 0),           # Left
                (0, primary_dy)    # Continue straight
            ]
        else:  # Moving horizontally, can meander vertically
            return [
                (primary_dx, 1),   # Diagonal down
                (primary_dx, -1),  # Diagonal up
                (0, 1),            # Down
                (0, -1),           # Up
                (primary_dx, 0)    # Continue straight
            ]

    def _widen_river(self, centerline, width):
        """
        Widen a river centerline to the desired width.

        Args:
            centerline (list): List of (x, y) centerline positions
            width (int): Desired river width

        Returns:
            set: Set of (x, y) tuples representing all river tiles
        """
        river_tiles = set()
        half_width = width // 2

        for cx, cy in centerline:
            # Add tiles around centerline
            for dx in range(-half_width, half_width + 1):
                for dy in range(-half_width, half_width + 1):
                    # Use circular distance for natural shape
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance <= half_width:
                        river_tiles.add((cx + dx, cy + dy))

        return river_tiles

    def _in_bounds(self, x, y):
        """Check if position is within grid bounds."""
        return 0 <= x < self.grid.width_tiles and 0 <= y < self.grid.height_tiles

    def _is_obstacle(self, x, y):
        """
        Check if position has an obstacle (building, landfill, etc.).

        Args:
            x (int): Grid X
            y (int): Grid Y

        Returns:
            bool: True if obstacle present
        """
        tile = self.grid.get_tile(x, y)
        if tile is None:
            return True

        # Check if tile is occupied or has a building/landfill
        if tile.occupied:
            return True

        from src.world.tile import TileType
        if tile.tile_type in [TileType.FACTORY, TileType.BUILDING, TileType.LANDFILL]:
            return True

        return False

    def _set_water_tile(self, x, y, avoid_buildings=True):
        """
        Set a tile to water terrain type.

        Args:
            x (int): Grid X
            y (int): Grid Y
            avoid_buildings (bool): Skip if obstacle present

        Returns:
            bool: True if tile was set to water
        """
        if not self._in_bounds(x, y):
            return False

        if avoid_buildings and self._is_obstacle(x, y):
            return False

        tile = self.grid.get_tile(x, y)
        if tile:
            tile.set_terrain_type(TerrainType.WATER)
            return True

        return False

    def clear_rivers(self):
        """Clear all water tiles from the grid (reset to LAND)."""
        for y in range(self.grid.height_tiles):
            for x in range(self.grid.width_tiles):
                tile = self.grid.get_tile(x, y)
                if tile and tile.terrain_type == TerrainType.WATER:
                    tile.set_terrain_type(TerrainType.LAND)

    def generate_ocean(self, edges=['south'], depth=5, create_docks=False, dock_spacing=10):
        """
        Generate ocean at map edges.

        Args:
            edges (list): List of edges to generate ocean on ('north', 'south', 'east', 'west')
            depth (int): How many tiles deep the ocean should be
            create_docks (bool): Whether to create dock tiles at transition points
            dock_spacing (int): Spacing between docks

        Returns:
            dict: Statistics about ocean generation
        """
        ocean_tiles = 0
        dock_tiles = 0

        for edge in edges:
            if edge == 'north':
                tiles, docks = self._generate_ocean_edge(
                    0, 0, self.grid.width_tiles, depth,
                    horizontal=True, create_docks=create_docks, dock_spacing=dock_spacing
                )
            elif edge == 'south':
                tiles, docks = self._generate_ocean_edge(
                    0, self.grid.height_tiles - depth,
                    self.grid.width_tiles, depth,
                    horizontal=True, create_docks=create_docks, dock_spacing=dock_spacing
                )
            elif edge == 'west':
                tiles, docks = self._generate_ocean_edge(
                    0, 0, depth, self.grid.height_tiles,
                    horizontal=False, create_docks=create_docks, dock_spacing=dock_spacing
                )
            elif edge == 'east':
                tiles, docks = self._generate_ocean_edge(
                    self.grid.width_tiles - depth, 0,
                    depth, self.grid.height_tiles,
                    horizontal=False, create_docks=create_docks, dock_spacing=dock_spacing
                )
            else:
                print(f"Unknown edge: {edge}")
                continue

            ocean_tiles += tiles
            dock_tiles += docks

        print(f"Generated ocean: {ocean_tiles} ocean tiles, {dock_tiles} dock tiles")

        return {
            'ocean_tiles': ocean_tiles,
            'dock_tiles': dock_tiles,
            'edges': edges
        }

    def _generate_ocean_edge(self, start_x, start_y, width, height,
                             horizontal=True, create_docks=False, dock_spacing=10):
        """
        Generate ocean on a specific edge.

        Args:
            start_x (int): Starting X position
            start_y (int): Starting Y position
            width (int): Width of ocean area
            height (int): Height of ocean area
            horizontal (bool): Whether edge is horizontal (north/south) or vertical (east/west)
            create_docks (bool): Whether to create docks
            dock_spacing (int): Spacing between docks

        Returns:
            tuple: (ocean_tiles_placed, dock_tiles_placed)
        """
        ocean_count = 0
        dock_count = 0

        # Generate ocean tiles
        for dy in range(height):
            for dx in range(width):
                x = start_x + dx
                y = start_y + dy

                if not self._in_bounds(x, y):
                    continue

                tile = self.grid.get_tile(x, y)
                if not tile:
                    continue

                # Don't overwrite buildings or landfills
                from src.world.tile import TileType
                if tile.tile_type in [TileType.FACTORY, TileType.BUILDING, TileType.LANDFILL]:
                    continue

                # Check if this should be a dock
                is_dock_position = False
                if create_docks:
                    if horizontal:
                        # Docks at transition (innermost row)
                        if dy == height - 1 and (dx % dock_spacing == 0):
                            is_dock_position = True
                    else:
                        # Docks at transition (innermost column)
                        if dx == width - 1 and (dy % dock_spacing == 0):
                            is_dock_position = True

                if is_dock_position:
                    tile.set_terrain_type(TerrainType.DOCK)
                    dock_count += 1
                else:
                    tile.set_terrain_type(TerrainType.OCEAN)
                    ocean_count += 1

        return ocean_count, dock_count

    def clear_ocean(self):
        """Clear all ocean tiles from the grid (reset to LAND)."""
        for y in range(self.grid.height_tiles):
            for x in range(self.grid.width_tiles):
                tile = self.grid.get_tile(x, y)
                if tile and tile.terrain_type == TerrainType.OCEAN:
                    tile.set_terrain_type(TerrainType.LAND)

    def clear_all_water(self):
        """Clear all water-related terrain (WATER, OCEAN, BRIDGE, DOCK) from grid."""
        for y in range(self.grid.height_tiles):
            for x in range(self.grid.width_tiles):
                tile = self.grid.get_tile(x, y)
                if tile and tile.terrain_type in [TerrainType.WATER, TerrainType.OCEAN,
                                                   TerrainType.BRIDGE, TerrainType.DOCK]:
                    tile.set_terrain_type(TerrainType.LAND)

    def __repr__(self):
        """String representation for debugging."""
        return f"RiverGenerator(grid_size={self.grid.width_tiles}x{self.grid.height_tiles})"
