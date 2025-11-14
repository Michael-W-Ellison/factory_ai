"""
Fence Manager - manages fence spawning and tracking around properties.

Handles:
- Spawning fences around houses and businesses
- Different fence types (chain link, wooden, brick)
- Leaving gaps for entrances
- Fence removal when deconstructed
"""

import random
from typing import List, Tuple, Optional
from src.entities.fence import Fence, FenceType
from src.world.tile import TileType


class FenceManager:
    """
    Manages all fences in the game world.

    Spawns fences around properties (houses, stores) with appropriate
    types and configurations.
    """

    def __init__(self, grid):
        """
        Initialize the fence manager.

        Args:
            grid: The game world grid
        """
        self.grid = grid
        self.fences: List[Fence] = []

        # Fence type distribution
        self.fence_types = [FenceType.CHAIN_LINK, FenceType.WOODEN, FenceType.BRICK]
        self.fence_type_weights = [0.5, 0.35, 0.15]  # 50% chain link, 35% wooden, 15% brick

    def spawn_fences_around_buildings(self, seed: int = 42, fence_coverage: float = 0.6):
        """
        Spawn fences around buildings in the city.

        Args:
            seed (int): Random seed for reproducible spawning
            fence_coverage (float): Probability of a building having a fence (0.0-1.0)
        """
        rng = random.Random(seed)

        # Find all buildings
        buildings = self._find_buildings()

        print(f"Found {len(buildings)} buildings for potential fencing")

        # Spawn fences around selected buildings
        fenced_count = 0
        for grid_x, grid_y in buildings:
            # Random chance to add fence based on coverage
            if rng.random() > fence_coverage:
                continue

            # Choose fence type for this property
            fence_type = rng.choices(self.fence_types, self.fence_type_weights)[0]

            # Generate fence perimeter around building
            self._create_fence_perimeter(grid_x, grid_y, fence_type, rng)
            fenced_count += 1

        print(f"Created fences around {fenced_count} buildings")
        print(f"Total fence segments: {len(self.fences)}")

    def _find_buildings(self) -> List[Tuple[int, int]]:
        """
        Find all buildings in the grid.

        Returns:
            List of (grid_x, grid_y) tuples for building locations
        """
        buildings = []

        for y in range(self.grid.height_tiles):
            for x in range(self.grid.width_tiles):
                tile = self.grid.get_tile(x, y)
                if tile and tile.tile_type == TileType.BUILDING:
                    buildings.append((x, y))

        return buildings

    def _create_fence_perimeter(self, building_x: int, building_y: int, fence_type: str, rng: random.Random):
        """
        Create a fence perimeter around a building.

        Args:
            building_x (int): Building grid X
            building_y (int): Building grid Y
            fence_type (str): Type of fence to use
            rng: Random number generator
        """
        # Fence offset from building (1 tile away)
        fence_offset = 1

        # Check if we should leave a gap for entrance
        # Entrances are typically on the side facing a road
        entrance_side = self._find_entrance_side(building_x, building_y)

        # Create fence segments around the perimeter
        # Top side
        if entrance_side != 'top':
            self._add_horizontal_fence(building_x - fence_offset, building_y - fence_offset,
                                      3, fence_type, rng)

        # Bottom side
        if entrance_side != 'bottom':
            self._add_horizontal_fence(building_x - fence_offset, building_y + fence_offset,
                                      3, fence_type, rng)

        # Left side
        if entrance_side != 'left':
            self._add_vertical_fence(building_x - fence_offset, building_y - fence_offset,
                                    3, fence_type, rng)

        # Right side
        if entrance_side != 'right':
            self._add_vertical_fence(building_x + fence_offset, building_y - fence_offset,
                                    3, fence_type, rng)

    def _find_entrance_side(self, building_x: int, building_y: int) -> str:
        """
        Determine which side of the building should have the entrance gap.

        Looks for nearby roads to determine entrance location.

        Args:
            building_x (int): Building grid X
            building_y (int): Building grid Y

        Returns:
            str: 'top', 'bottom', 'left', 'right', or 'none'
        """
        # Check adjacent tiles for roads
        road_types = [TileType.ROAD_DIRT, TileType.ROAD_TAR, TileType.ROAD_ASPHALT]

        # Check top
        tile_top = self.grid.get_tile(building_x, building_y - 1)
        if tile_top and tile_top.tile_type in road_types:
            return 'top'

        # Check bottom
        tile_bottom = self.grid.get_tile(building_x, building_y + 1)
        if tile_bottom and tile_bottom.tile_type in road_types:
            return 'bottom'

        # Check left
        tile_left = self.grid.get_tile(building_x - 1, building_y)
        if tile_left and tile_left.tile_type in road_types:
            return 'left'

        # Check right
        tile_right = self.grid.get_tile(building_x + 1, building_y)
        if tile_right and tile_right.tile_type in road_types:
            return 'right'

        # No road found, default to bottom entrance
        return 'bottom'

    def _add_horizontal_fence(self, grid_x: int, grid_y: int, length_tiles: int,
                             fence_type: str, rng: random.Random):
        """
        Add a horizontal fence segment.

        Args:
            grid_x (int): Starting grid X
            grid_y (int): Grid Y
            length_tiles (int): Length in tiles
            fence_type (str): Type of fence
            rng: Random number generator
        """
        for i in range(length_tiles):
            x = grid_x + i
            y = grid_y

            # Check if position is valid
            if not (0 <= x < self.grid.width_tiles and 0 <= y < self.grid.height_tiles):
                continue

            tile = self.grid.get_tile(x, y)
            if not tile:
                continue

            # Don't place fence on roads or buildings
            if tile.tile_type in [TileType.ROAD_DIRT, TileType.ROAD_TAR,
                                 TileType.ROAD_ASPHALT, TileType.BUILDING, TileType.FACTORY]:
                continue

            # Convert to world coordinates
            world_x = x * self.grid.tile_size
            world_y = y * self.grid.tile_size + self.grid.tile_size // 2 - 4  # Center vertically

            # Create fence
            fence = Fence(world_x, world_y, fence_type, 'horizontal', self.grid.tile_size)
            self.fences.append(fence)

    def _add_vertical_fence(self, grid_x: int, grid_y: int, length_tiles: int,
                           fence_type: str, rng: random.Random):
        """
        Add a vertical fence segment.

        Args:
            grid_x (int): Grid X
            grid_y (int): Starting grid Y
            length_tiles (int): Length in tiles
            fence_type (str): Type of fence
            rng: Random number generator
        """
        for i in range(length_tiles):
            x = grid_x
            y = grid_y + i

            # Check if position is valid
            if not (0 <= x < self.grid.width_tiles and 0 <= y < self.grid.height_tiles):
                continue

            tile = self.grid.get_tile(x, y)
            if not tile:
                continue

            # Don't place fence on roads or buildings
            if tile.tile_type in [TileType.ROAD_DIRT, TileType.ROAD_TAR,
                                 TileType.ROAD_ASPHALT, TileType.BUILDING, TileType.FACTORY]:
                continue

            # Convert to world coordinates
            world_x = x * self.grid.tile_size + self.grid.tile_size // 2 - 4  # Center horizontally
            world_y = y * self.grid.tile_size

            # Create fence
            fence = Fence(world_x, world_y, fence_type, 'vertical', self.grid.tile_size)
            self.fences.append(fence)

    def get_fence_at(self, world_x: float, world_y: float, tolerance: float = 10.0) -> Optional[Fence]:
        """
        Get fence at a specific world position.

        Args:
            world_x (float): World X coordinate
            world_y (float): World Y coordinate
            tolerance (float): Distance tolerance in pixels

        Returns:
            Fence if found, None otherwise
        """
        for fence in self.fences:
            # Check if point is within fence bounds (with tolerance)
            if (fence.world_x - tolerance <= world_x <= fence.world_x + fence.width + tolerance and
                fence.world_y - tolerance <= world_y <= fence.world_y + fence.height + tolerance):
                return fence

        return None

    def remove_fence(self, fence: Fence):
        """
        Remove a fence from the world.

        Args:
            fence: The fence to remove
        """
        if fence in self.fences:
            self.fences.remove(fence)

    def get_all_fences(self) -> List[Fence]:
        """
        Get all fences in the world.

        Returns:
            List of all fences
        """
        return self.fences.copy()

    def update(self, dt: float):
        """
        Update all fences.

        Args:
            dt (float): Delta time in seconds
        """
        # Update fence deconstruction
        for fence in self.fences[:]:  # Copy list to allow removal during iteration
            if fence.being_deconstructed:
                complete = fence.update_deconstruction(dt)
                if complete:
                    # Fence fully deconstructed - remove it
                    self.remove_fence(fence)

    def render(self, screen, camera):
        """
        Render all fences.

        Args:
            screen: Pygame surface
            camera: Camera for world-to-screen transformation
        """
        for fence in self.fences:
            fence.render(screen, camera)

    def get_stats(self) -> dict:
        """
        Get statistics about fences in the world.

        Returns:
            Dictionary with fence statistics
        """
        total = len(self.fences)
        by_type = {}
        being_deconstructed = 0

        for fence in self.fences:
            # Count by type
            fence_type = fence.fence_type
            by_type[fence_type] = by_type.get(fence_type, 0) + 1

            # Count being deconstructed
            if fence.being_deconstructed:
                being_deconstructed += 1

        return {
            'total': total,
            'by_type': by_type,
            'being_deconstructed': being_deconstructed,
        }
