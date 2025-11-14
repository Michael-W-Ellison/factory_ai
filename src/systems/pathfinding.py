"""
A* pathfinding system for robot navigation.
"""

import heapq
from typing import List, Tuple, Optional


class Node:
    """A node in the pathfinding graph."""

    def __init__(self, position: Tuple[int, int], parent=None):
        self.position = position  # (grid_x, grid_y)
        self.parent = parent
        self.g = 0  # Cost from start to this node
        self.h = 0  # Heuristic cost from this node to goal
        self.f = 0  # Total cost (g + h)

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f < other.f

    def __hash__(self):
        return hash(self.position)


class Pathfinder:
    """
    A* pathfinding implementation.

    Finds optimal paths through a grid, avoiding obstacles.
    """

    def __init__(self, grid):
        """
        Initialize pathfinder.

        Args:
            grid: Grid object containing tile information
        """
        self.grid = grid

    def heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        Calculate heuristic (Manhattan distance).

        Args:
            pos1: Starting position (grid_x, grid_y)
            pos2: Goal position (grid_x, grid_y)

        Returns:
            float: Estimated distance
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_neighbors(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Get walkable neighboring tiles.

        Args:
            position: Current position (grid_x, grid_y)

        Returns:
            List of neighboring positions
        """
        x, y = position
        neighbors = []

        # 8-directional movement (including diagonals)
        directions = [
            (0, -1),  # North
            (1, 0),   # East
            (0, 1),   # South
            (-1, 0),  # West
            (1, -1),  # Northeast
            (1, 1),   # Southeast
            (-1, 1),  # Southwest
            (-1, -1), # Northwest
        ]

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy

            # Check if position is valid and walkable
            if self.is_walkable(new_x, new_y):
                # For diagonal movement, check that adjacent tiles are also walkable
                # (prevents cutting corners)
                if dx != 0 and dy != 0:
                    if not self.is_walkable(x + dx, y) or not self.is_walkable(x, y + dy):
                        continue

                neighbors.append((new_x, new_y))

        return neighbors

    def is_walkable(self, grid_x: int, grid_y: int) -> bool:
        """
        Check if a tile is walkable.

        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate

        Returns:
            bool: True if walkable, False otherwise
        """
        tile = self.grid.get_tile(grid_x, grid_y)
        if tile is None:
            return False
        return tile.walkable and not tile.occupied

    def find_path(self, start_pos: Tuple[int, int], goal_pos: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Find a path from start to goal using A*.

        Args:
            start_pos: Starting position (grid_x, grid_y)
            goal_pos: Goal position (grid_x, grid_y)

        Returns:
            List of positions forming a path, or None if no path exists
        """
        # Quick check: are start and goal valid?
        if not self.is_walkable(start_pos[0], start_pos[1]):
            return None
        if not self.is_walkable(goal_pos[0], goal_pos[1]):
            return None

        # Special case: already at goal
        if start_pos == goal_pos:
            return [start_pos]

        # Initialize
        start_node = Node(start_pos)
        goal_node = Node(goal_pos)

        open_list = []
        heapq.heappush(open_list, start_node)
        closed_set = set()
        open_dict = {start_pos: start_node}  # For quick lookup

        # A* search
        max_iterations = 1000  # Prevent infinite loops
        iterations = 0

        while open_list and iterations < max_iterations:
            iterations += 1

            # Get node with lowest f score
            current_node = heapq.heappop(open_list)
            if current_node.position in open_dict:
                del open_dict[current_node.position]
            closed_set.add(current_node.position)

            # Found the goal?
            if current_node.position == goal_pos:
                return self._reconstruct_path(current_node)

            # Check neighbors
            for neighbor_pos in self.get_neighbors(current_node.position):
                if neighbor_pos in closed_set:
                    continue

                # Calculate costs
                # Diagonal movement costs more (1.414) than straight (1.0)
                dx = abs(neighbor_pos[0] - current_node.position[0])
                dy = abs(neighbor_pos[1] - current_node.position[1])
                movement_cost = 1.414 if (dx + dy) == 2 else 1.0

                tentative_g = current_node.g + movement_cost

                # Check if this is a better path
                if neighbor_pos in open_dict:
                    neighbor_node = open_dict[neighbor_pos]
                    if tentative_g < neighbor_node.g:
                        neighbor_node.g = tentative_g
                        neighbor_node.h = self.heuristic(neighbor_pos, goal_pos)
                        neighbor_node.f = neighbor_node.g + neighbor_node.h
                        neighbor_node.parent = current_node
                        heapq.heapify(open_list)  # Re-sort
                else:
                    neighbor_node = Node(neighbor_pos, current_node)
                    neighbor_node.g = tentative_g
                    neighbor_node.h = self.heuristic(neighbor_pos, goal_pos)
                    neighbor_node.f = neighbor_node.g + neighbor_node.h
                    heapq.heappush(open_list, neighbor_node)
                    open_dict[neighbor_pos] = neighbor_node

        # No path found
        return None

    def _reconstruct_path(self, node: Node) -> List[Tuple[int, int]]:
        """
        Reconstruct path from goal node back to start.

        Args:
            node: Goal node

        Returns:
            List of positions from start to goal
        """
        path = []
        current = node
        while current is not None:
            path.append(current.position)
            current = current.parent
        path.reverse()
        return path

    def smooth_path(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Smooth path by removing unnecessary waypoints.

        Uses line-of-sight to skip intermediate points.

        Args:
            path: Original path

        Returns:
            Smoothed path
        """
        if len(path) <= 2:
            return path

        smoothed = [path[0]]
        current_index = 0

        while current_index < len(path) - 1:
            # Look ahead as far as possible
            farthest_visible = current_index + 1

            for i in range(current_index + 2, len(path)):
                if self._has_line_of_sight(path[current_index], path[i]):
                    farthest_visible = i
                else:
                    break

            smoothed.append(path[farthest_visible])
            current_index = farthest_visible

        return smoothed

    def _has_line_of_sight(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """
        Check if there's a clear line of sight between two positions.

        Uses Bresenham's line algorithm.

        Args:
            pos1: Starting position
            pos2: Ending position

        Returns:
            bool: True if clear line of sight
        """
        x0, y0 = pos1
        x1, y1 = pos2

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        x, y = x0, y0

        while True:
            # Check if current position is walkable
            if not self.is_walkable(x, y):
                return False

            if x == x1 and y == y1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

        return True
