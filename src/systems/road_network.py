"""
RoadNetwork - builds and manages a graph of road tiles for vehicle navigation.

Provides:
- Road segment graph with connections
- Intersection detection
- Lane direction mapping
- Pathfinding support for vehicles
"""

from typing import Dict, List, Tuple, Set, Optional
from src.world.tile import TileType


class RoadSegment:
    """
    Represents a connected segment of road tiles.

    A segment is a contiguous run of road tiles in one direction
    (e.g., a horizontal or vertical street).
    """

    def __init__(self, segment_id: int):
        """
        Initialize a road segment.

        Args:
            segment_id (int): Unique ID for this segment
        """
        self.id = segment_id
        self.tiles: List[Tuple[int, int]] = []  # List of (grid_x, grid_y) positions
        self.direction: Optional[str] = None  # 'horizontal' or 'vertical'
        self.two_way = True  # Most roads are two-way
        self.connected_segments: Set[int] = set()  # IDs of connected segments
        self.intersections: List[Tuple[int, int]] = []  # Tiles that are intersections

    def add_tile(self, grid_x: int, grid_y: int):
        """Add a tile to this segment."""
        self.tiles.append((grid_x, grid_y))

    def is_horizontal(self) -> bool:
        """Check if this segment runs horizontally."""
        return self.direction == 'horizontal'

    def is_vertical(self) -> bool:
        """Check if this segment runs vertically."""
        return self.direction == 'vertical'

    def __repr__(self):
        return f"RoadSegment(id={self.id}, tiles={len(self.tiles)}, dir={self.direction})"


class RoadNetwork:
    """
    Manages the road network graph for vehicle navigation.

    Analyzes all road tiles from the grid and builds a graph structure
    with segments, intersections, and lane information.
    """

    def __init__(self, grid):
        """
        Initialize road network.

        Args:
            grid: World grid containing road tiles
        """
        self.grid = grid

        # Road graph data
        self.road_tiles: Set[Tuple[int, int]] = set()  # All road tile positions
        self.intersections: Set[Tuple[int, int]] = set()  # Intersection positions
        self.segments: Dict[int, RoadSegment] = {}  # segment_id -> RoadSegment
        self.tile_to_segment: Dict[Tuple[int, int], int] = {}  # (x,y) -> segment_id

        # Lane information (for two-lane roads)
        # Maps (x, y) -> {'north': (lane_x, lane_y), 'south': (lane_x, lane_y), ...}
        self.lane_centers: Dict[Tuple[int, int], Dict[str, Tuple[float, float]]] = {}

        # Build the network
        self._build_network()

    def _build_network(self):
        """Build the road network graph from grid tiles."""
        print("Building road network...")

        # Step 1: Find all road tiles
        self._find_road_tiles()

        # Step 2: Identify intersections
        self._identify_intersections()

        # Step 3: Build road segments (not implemented in this version,
        #         but could segment roads between intersections)

        # Step 4: Calculate lane centers for each road tile
        self._calculate_lane_centers()

        print(f"Road network built: {len(self.road_tiles)} road tiles, "
              f"{len(self.intersections)} intersections")

    def _find_road_tiles(self):
        """Scan grid and find all road tiles."""
        for y in range(self.grid.height_tiles):
            for x in range(self.grid.width_tiles):
                tile = self.grid.get_tile(x, y)
                if tile and self._is_road_tile(tile):
                    self.road_tiles.add((x, y))

    def _is_road_tile(self, tile) -> bool:
        """Check if a tile is a road."""
        return tile.tile_type in [TileType.ROAD_DIRT, TileType.ROAD_TAR, TileType.ROAD_ASPHALT]

    def _identify_intersections(self):
        """
        Identify intersection tiles (roads with 3+ road neighbors).

        An intersection is defined as a road tile with 3 or 4 neighboring roads.
        """
        for road_pos in self.road_tiles:
            x, y = road_pos

            # Count road neighbors in cardinal directions
            neighbors = self._get_road_neighbors(x, y)

            # 3+ road neighbors = intersection
            # Also detect T-junctions and 4-way intersections
            if len(neighbors) >= 3:
                self.intersections.add(road_pos)

    def _get_road_neighbors(self, grid_x: int, grid_y: int) -> List[str]:
        """
        Get list of directions with road neighbors.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position

        Returns:
            list: List of directions ('north', 'south', 'east', 'west')
        """
        neighbors = []

        # Check cardinal directions
        directions = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0)
        }

        for direction, (dx, dy) in directions.items():
            neighbor_x = grid_x + dx
            neighbor_y = grid_y + dy

            if (neighbor_x, neighbor_y) in self.road_tiles:
                neighbors.append(direction)

        return neighbors

    def _calculate_lane_centers(self):
        """
        Calculate lane center positions for each road tile.

        For two-lane roads (one lane each direction), we calculate
        the center position of each lane within the tile.

        Uses right-side driving:
        - Horizontal roads: north lane goes east, south lane goes west
        - Vertical roads: west lane goes south, east lane goes north
        """
        # Get tile size from grid
        tile_size = self.grid.tile_size

        # Lane offset from center (1/4 of tile size)
        lane_offset = tile_size / 4.0

        for road_pos in self.road_tiles:
            grid_x, grid_y = road_pos

            # World position of tile center
            world_x = grid_x * tile_size + tile_size / 2
            world_y = grid_y * tile_size + tile_size / 2

            # Determine road orientation
            neighbors = self._get_road_neighbors(grid_x, grid_y)

            # Check if horizontal road (has east/west neighbors)
            has_horizontal = 'east' in neighbors or 'west' in neighbors
            # Check if vertical road (has north/south neighbors)
            has_vertical = 'north' in neighbors or 'south' in neighbors

            lanes = {}

            # Horizontal road lanes
            if has_horizontal:
                # North lane (goes east, right-side driving)
                lanes['east'] = (world_x, world_y - lane_offset)
                # South lane (goes west)
                lanes['west'] = (world_x, world_y + lane_offset)

            # Vertical road lanes
            if has_vertical:
                # West lane (goes south)
                lanes['south'] = (world_x - lane_offset, world_y)
                # East lane (goes north)
                lanes['north'] = (world_x + lane_offset, world_y)

            self.lane_centers[road_pos] = lanes

    def is_road(self, grid_x: int, grid_y: int) -> bool:
        """
        Check if a position is a road.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position

        Returns:
            bool: True if position is a road
        """
        return (grid_x, grid_y) in self.road_tiles

    def is_intersection(self, grid_x: int, grid_y: int) -> bool:
        """
        Check if a position is an intersection.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position

        Returns:
            bool: True if position is an intersection
        """
        return (grid_x, grid_y) in self.intersections

    def get_lane_center(self, grid_x: int, grid_y: int, direction: str) -> Optional[Tuple[float, float]]:
        """
        Get the center position of a lane at a road tile.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
            direction (str): Direction of travel ('north', 'south', 'east', 'west')

        Returns:
            tuple: (world_x, world_y) of lane center, or None if not available
        """
        road_pos = (grid_x, grid_y)

        if road_pos not in self.lane_centers:
            return None

        lanes = self.lane_centers[road_pos]
        return lanes.get(direction)

    def get_available_lanes(self, grid_x: int, grid_y: int) -> List[str]:
        """
        Get list of available lane directions at a road tile.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position

        Returns:
            list: List of available directions ('north', 'south', 'east', 'west')
        """
        road_pos = (grid_x, grid_y)

        if road_pos not in self.lane_centers:
            return []

        return list(self.lane_centers[road_pos].keys())

    def get_next_road_tile(self, grid_x: int, grid_y: int, direction: str) -> Optional[Tuple[int, int]]:
        """
        Get the next road tile in a given direction.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
            direction (str): Direction to check ('north', 'south', 'east', 'west')

        Returns:
            tuple: (next_x, next_y) or None if no road in that direction
        """
        direction_offsets = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0)
        }

        if direction not in direction_offsets:
            return None

        dx, dy = direction_offsets[direction]
        next_x = grid_x + dx
        next_y = grid_y + dy

        if self.is_road(next_x, next_y):
            return (next_x, next_y)

        return None

    def get_valid_turns(self, grid_x: int, grid_y: int, current_direction: str) -> List[str]:
        """
        Get valid turn directions at an intersection.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
            current_direction (str): Current direction of travel

        Returns:
            list: List of valid directions to turn to (including straight)
        """
        if not self.is_intersection(grid_x, grid_y):
            # Not an intersection, can only go straight
            next_tile = self.get_next_road_tile(grid_x, grid_y, current_direction)
            return [current_direction] if next_tile else []

        # At intersection, can turn to any connected road
        neighbors = self._get_road_neighbors(grid_x, grid_y)

        # Can't immediately reverse direction (no U-turns at intersections)
        opposite_direction = {
            'north': 'south',
            'south': 'north',
            'east': 'west',
            'west': 'east'
        }.get(current_direction)

        valid_turns = [d for d in neighbors if d != opposite_direction]

        return valid_turns

    def find_path(self, start_x: int, start_y: int, end_x: int, end_y: int) -> Optional[List[Tuple[int, int]]]:
        """
        Find a path from start to end using roads.

        Uses A* pathfinding on the road network.

        Args:
            start_x (int): Start grid X
            start_y (int): Start grid Y
            end_x (int): End grid X
            end_y (int): End grid Y

        Returns:
            list: List of (grid_x, grid_y) waypoints, or None if no path
        """
        import heapq

        # Validate start and end are roads
        if not self.is_road(start_x, start_y) or not self.is_road(end_x, end_y):
            return None

        # A* pathfinding
        start = (start_x, start_y)
        goal = (end_x, end_y)

        # Priority queue: (f_score, g_score, position, path)
        open_set = [(0, 0, start, [start])]
        closed_set = set()

        while open_set:
            f_score, g_score, current, path = heapq.heappop(open_set)

            if current in closed_set:
                continue

            if current == goal:
                return path

            closed_set.add(current)

            # Check all neighboring road tiles
            cx, cy = current
            for direction in ['north', 'south', 'east', 'west']:
                neighbor = self.get_next_road_tile(cx, cy, direction)

                if neighbor is None or neighbor in closed_set:
                    continue

                # Calculate scores
                new_g_score = g_score + 1
                nx, ny = neighbor
                h_score = abs(nx - end_x) + abs(ny - end_y)  # Manhattan distance
                new_f_score = new_g_score + h_score

                new_path = path + [neighbor]
                heapq.heappush(open_set, (new_f_score, new_g_score, neighbor, new_path))

        # No path found
        return None

    def get_random_road_tile(self) -> Optional[Tuple[int, int]]:
        """
        Get a random road tile position.

        Returns:
            tuple: (grid_x, grid_y) of a random road tile, or None if no roads
        """
        import random

        if not self.road_tiles:
            return None

        return random.choice(list(self.road_tiles))

    def get_road_count(self) -> int:
        """Get total number of road tiles."""
        return len(self.road_tiles)

    def get_intersection_count(self) -> int:
        """Get total number of intersections."""
        return len(self.intersections)

    def __repr__(self):
        """String representation for debugging."""
        return (f"RoadNetwork(roads={len(self.road_tiles)}, "
                f"intersections={len(self.intersections)})")
