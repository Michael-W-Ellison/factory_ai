"""
RiverGenerator - Procedurally generates rivers across the map.

Handles:
- River path generation using random walk
- River width variation (3-5 tiles)
- Flow direction (north to south or configurable)
- Bridge placement across rivers
- Integration with city roads
"""

import random
import math
from typing import List, Tuple, Set, Optional
from src.world.tile import TerrainType


class RiverSegment:
    """Represents a segment of a river."""

    def __init__(self, x: int, y: int, width: int):
        """
        Initialize a river segment.

        Args:
            x (int): Center X position
            y (int): Center Y position
            width (int): Width of river at this point (3-5 tiles)
        """
        self.x = x
        self.y = y
        self.width = width


class Bridge:
    """Represents a bridge crossing a river."""

    def __init__(self, x: int, y: int, direction: str, length: int):
        """
        Initialize a bridge.

        Args:
            x (int): Starting X position
            y (int): Starting Y position
            direction (str): 'horizontal' or 'vertical'
            length (int): Length of bridge in tiles
        """
        self.x = x
        self.y = y
        self.direction = direction
        self.length = length
        self.tiles = self._calculate_tiles()

    def _calculate_tiles(self) -> List[Tuple[int, int]]:
        """Calculate all tiles that are part of this bridge."""
        tiles = []
        if self.direction == 'horizontal':
            for i in range(self.length):
                tiles.append((self.x + i, self.y))
        else:  # vertical
            for i in range(self.length):
                tiles.append((self.x, self.y + i))
        return tiles


class RiverGenerator:
    """
    Generates procedural rivers across the map.

    Creates natural-looking rivers using random walk algorithm,
    with bridges placed at road crossings.
    """

    def __init__(self, grid_width: int, grid_height: int, seed: Optional[int] = None):
        """
        Initialize the river generator.

        Args:
            grid_width (int): Width of grid in tiles
            grid_height (int): Height of grid in tiles
            seed (int, optional): Random seed for reproducible generation
        """
        self.grid_width = grid_width
        self.grid_height = grid_height

        if seed is not None:
            random.seed(seed)

        # Generated data
        self.rivers = []  # List of river paths (each path is a list of RiverSegments)
        self.river_tiles = set()  # Set of (x, y) tiles that are river
        self.bridges = []  # List of Bridge objects
        self.bridge_tiles = set()  # Set of (x, y) tiles that are bridges

    def generate(self, num_rivers: int = 1, flow_direction: str = 'south') -> dict:
        """
        Generate rivers across the map.

        Args:
            num_rivers (int): Number of rivers to generate
            flow_direction (str): General flow direction ('north', 'south', 'east', 'west')

        Returns:
            dict: River data with tiles, bridges, etc.
        """
        print(f"Generating {num_rivers} river(s) flowing {flow_direction}...")

        self.rivers = []
        self.river_tiles = set()

        for i in range(num_rivers):
            river_path = self._generate_river_path(flow_direction, river_index=i)
            if river_path:
                self.rivers.append(river_path)

        print(f"  Generated {len(self.rivers)} rivers with {len(self.river_tiles)} water tiles")

        return {
            'rivers': self.rivers,
            'river_tiles': self.river_tiles,
            'bridges': self.bridges,
            'bridge_tiles': self.bridge_tiles,
        }

    def _generate_river_path(self, flow_direction: str, river_index: int = 0) -> List[RiverSegment]:
        """
        Generate a single river path using random walk.

        Args:
            flow_direction (str): General flow direction
            river_index (int): Index of this river (for spacing)

        Returns:
            list: List of RiverSegment objects
        """
        path = []

        # Determine starting position based on flow direction
        if flow_direction == 'south':
            # Start at north edge
            start_x = self.grid_width // (river_index + 2) + random.randint(-10, 10)
            start_y = 0
            primary_dir = (0, 1)  # Move down
        elif flow_direction == 'north':
            # Start at south edge
            start_x = self.grid_width // (river_index + 2) + random.randint(-10, 10)
            start_y = self.grid_height - 1
            primary_dir = (0, -1)  # Move up
        elif flow_direction == 'east':
            # Start at west edge
            start_x = 0
            start_y = self.grid_height // (river_index + 2) + random.randint(-5, 5)
            primary_dir = (1, 0)  # Move right
        elif flow_direction == 'west':
            # Start at east edge
            start_x = self.grid_width - 1
            start_y = self.grid_height // (river_index + 2) + random.randint(-5, 5)
            primary_dir = (-1, 0)  # Move left
        else:
            print(f"Unknown flow direction: {flow_direction}, using south")
            start_x = self.grid_width // 2
            start_y = 0
            primary_dir = (0, 1)

        # Ensure starting position is within bounds
        start_x = max(5, min(self.grid_width - 6, start_x))
        start_y = max(0, min(self.grid_height - 1, start_y))

        # Current position
        current_x = start_x
        current_y = start_y

        # Random walk parameters
        step_size = 1
        max_steps = max(self.grid_width, self.grid_height) * 2
        steps = 0

        # Width variation (3-5 tiles)
        current_width = random.randint(3, 5)

        while steps < max_steps:
            # Check if we've reached the opposite edge
            if flow_direction == 'south' and current_y >= self.grid_height - 1:
                break
            elif flow_direction == 'north' and current_y <= 0:
                break
            elif flow_direction == 'east' and current_x >= self.grid_width - 1:
                break
            elif flow_direction == 'west' and current_x <= 0:
                break

            # Add current segment to path
            segment = RiverSegment(current_x, current_y, current_width)
            path.append(segment)

            # Add tiles to river_tiles set
            self._add_river_tiles(current_x, current_y, current_width)

            # Decide next move (mostly in primary direction, occasional deviation)
            if random.random() < 0.7:  # 70% chance to move in primary direction
                dx, dy = primary_dir
            else:
                # Occasionally deviate perpendicular to flow
                if primary_dir[0] == 0:  # Vertical flow
                    dx = random.choice([-1, 0, 1])
                    dy = primary_dir[1]
                else:  # Horizontal flow
                    dx = primary_dir[0]
                    dy = random.choice([-1, 0, 1])

            # Move to next position
            next_x = current_x + dx * step_size
            next_y = current_y + dy * step_size

            # Bounds checking
            if next_x < 5 or next_x >= self.grid_width - 5:
                # Hit edge, try to steer back
                if primary_dir[0] == 0:  # Vertical river hitting horizontal edge
                    dx = 1 if next_x < 5 else -1
                    next_x = current_x + dx
                else:
                    continue  # Skip this step
            if next_y < 0 or next_y >= self.grid_height:
                continue  # Skip this step

            current_x = next_x
            current_y = next_y

            # Occasionally vary width
            if random.random() < 0.1:
                current_width = random.randint(3, 5)

            steps += 1

        print(f"  River {river_index}: {len(path)} segments")
        return path

    def _add_river_tiles(self, center_x: int, center_y: int, width: int):
        """
        Add tiles around center point to river_tiles set.

        Args:
            center_x (int): Center X position
            center_y (int): Center Y position
            width (int): Width of river at this point
        """
        half_width = width // 2

        for dx in range(-half_width, half_width + 1):
            for dy in range(-half_width, half_width + 1):
                # Use circular shape for river
                distance = math.sqrt(dx * dx + dy * dy)
                if distance <= half_width:
                    tile_x = center_x + dx
                    tile_y = center_y + dy

                    # Bounds check
                    if 0 <= tile_x < self.grid_width and 0 <= tile_y < self.grid_height:
                        self.river_tiles.add((tile_x, tile_y))

    def place_bridges(self, road_tiles: Set[Tuple[int, int]], min_spacing: int = 10):
        """
        Place bridges where roads cross rivers.

        Args:
            road_tiles (set): Set of (x, y) tiles that are roads
            min_spacing (int): Minimum spacing between bridges
        """
        print("Placing bridges at river crossings...")

        self.bridges = []
        self.bridge_tiles = set()

        # Find road-river intersections
        intersections = []
        for road_tile in road_tiles:
            if road_tile in self.river_tiles:
                intersections.append(road_tile)

        if not intersections:
            print("  No river-road intersections found")
            return

        # Group nearby intersections into bridge locations
        bridge_locations = []
        used_intersections = set()

        for intersection in intersections:
            if intersection in used_intersections:
                continue

            # Find contiguous road tiles crossing the river
            bridge_tiles_list = self._find_bridge_crossing(intersection, road_tiles)

            if bridge_tiles_list:
                # Determine bridge direction
                if len(bridge_tiles_list) > 1:
                    first = bridge_tiles_list[0]
                    last = bridge_tiles_list[-1]

                    # Horizontal or vertical?
                    if first[1] == last[1]:  # Same Y = horizontal
                        direction = 'horizontal'
                        start_x = min(t[0] for t in bridge_tiles_list)
                        start_y = first[1]
                    else:  # Vertical
                        direction = 'vertical'
                        start_x = first[0]
                        start_y = min(t[1] for t in bridge_tiles_list)

                    length = len(bridge_tiles_list)

                    # Check spacing from existing bridges
                    too_close = False
                    for existing_bridge in self.bridges:
                        dist = abs(existing_bridge.x - start_x) + abs(existing_bridge.y - start_y)
                        if dist < min_spacing:
                            too_close = True
                            break

                    if not too_close:
                        bridge = Bridge(start_x, start_y, direction, length)
                        self.bridges.append(bridge)
                        self.bridge_tiles.update(bridge.tiles)

                        # Mark intersections as used
                        for tile in bridge_tiles_list:
                            used_intersections.add(tile)

        print(f"  Placed {len(self.bridges)} bridges")

    def _find_bridge_crossing(self, start_tile: Tuple[int, int], road_tiles: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Find contiguous road tiles crossing river from a starting intersection.

        Args:
            start_tile (tuple): Starting (x, y) tile
            road_tiles (set): Set of road tiles

        Returns:
            list: List of (x, y) tiles forming the bridge
        """
        x, y = start_tile
        bridge_tiles = []

        # Try horizontal crossing
        horizontal = []
        # Extend left
        test_x = x
        while test_x >= 0 and (test_x, y) in self.river_tiles and (test_x, y) in road_tiles:
            horizontal.append((test_x, y))
            test_x -= 1
        horizontal.reverse()

        # Extend right
        test_x = x + 1
        while test_x < self.grid_width and (test_x, y) in self.river_tiles and (test_x, y) in road_tiles:
            horizontal.append((test_x, y))
            test_x += 1

        # Try vertical crossing
        vertical = []
        # Extend up
        test_y = y
        while test_y >= 0 and (x, test_y) in self.river_tiles and (x, test_y) in road_tiles:
            vertical.append((x, test_y))
            test_y -= 1
        vertical.reverse()

        # Extend down
        test_y = y + 1
        while test_y < self.grid_height and (x, test_y) in self.river_tiles and (x, test_y) in road_tiles:
            vertical.append((x, test_y))
            test_y += 1

        # Use the longer crossing
        if len(horizontal) >= len(vertical):
            bridge_tiles = horizontal
        else:
            bridge_tiles = vertical

        # Minimum bridge length of 2
        if len(bridge_tiles) < 2:
            return []

        return bridge_tiles

    def add_ocean_edge(self, edge: str, depth: int = 10):
        """
        Add ocean along map edge.

        Args:
            edge (str): Which edge ('north', 'south', 'east', 'west')
            depth (int): How many tiles deep the ocean extends
        """
        print(f"Adding ocean on {edge} edge (depth {depth})...")

        ocean_tiles = set()

        if edge == 'north':
            for y in range(min(depth, self.grid_height)):
                for x in range(self.grid_width):
                    ocean_tiles.add((x, y))
        elif edge == 'south':
            for y in range(max(0, self.grid_height - depth), self.grid_height):
                for x in range(self.grid_width):
                    ocean_tiles.add((x, y))
        elif edge == 'west':
            for x in range(min(depth, self.grid_width)):
                for y in range(self.grid_height):
                    ocean_tiles.add((x, y))
        elif edge == 'east':
            for x in range(max(0, self.grid_width - depth), self.grid_width):
                for y in range(self.grid_height):
                    ocean_tiles.add((x, y))

        print(f"  Added {len(ocean_tiles)} ocean tiles")
        return ocean_tiles

    def get_statistics(self) -> dict:
        """Get statistics about generated rivers."""
        return {
            'num_rivers': len(self.rivers),
            'river_tiles': len(self.river_tiles),
            'num_bridges': len(self.bridges),
            'bridge_tiles': len(self.bridge_tiles),
        }

    def is_river(self, x: int, y: int) -> bool:
        """Check if tile is a river."""
        return (x, y) in self.river_tiles

    def is_bridge(self, x: int, y: int) -> bool:
        """Check if tile is a bridge."""
        return (x, y) in self.bridge_tiles

    def __repr__(self):
        """String representation for debugging."""
        return (f"RiverGenerator({len(self.rivers)} rivers, "
                f"{len(self.river_tiles)} water tiles, {len(self.bridges)} bridges)")
