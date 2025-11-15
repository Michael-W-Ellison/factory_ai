"""
BusRoute - Defines a bus route with stops and waypoints.

A bus route consists of:
- List of bus stops
- Calculated path between stops using road network
- Schedule information
"""

from typing import List, Tuple, Optional


class BusRoute:
    """
    Represents a single bus route with stops and paths.

    Attributes:
        route_id (int): Unique route identifier
        stops (list): List of (grid_x, grid_y) stop positions
        waypoints (list): Full path including all waypoints between stops
        color (tuple): Route color for visual identification
        name (str): Route name
    """

    def __init__(self, route_id: int, name: str = None, is_express: bool = False):
        """
        Initialize a bus route.

        Args:
            route_id (int): Unique route ID
            name (str): Optional route name
            is_express (bool): Whether this is an express route (skips some stops)
        """
        self.route_id = route_id
        self.name = name or f"Route {route_id}"
        self.is_express = is_express

        # Route definition
        self.stops: List[Tuple[int, int]] = []  # List of (grid_x, grid_y) positions
        self.express_stops: List[Tuple[int, int]] = []  # Subset of stops for express buses
        self.waypoints: List[Tuple[int, int]] = []  # Full path with all waypoints

        # Visual properties
        self.color = self._generate_route_color(route_id)

        # Schedule
        self.frequency_minutes = 10 if not is_express else 15  # Express buses less frequent
        self.active_hours = (6, 22)  # Buses run 6am-10pm

    def add_stop(self, grid_x: int, grid_y: int):
        """
        Add a stop to the route.

        Args:
            grid_x (int): Grid X position of stop
            grid_y (int): Grid Y position of stop
        """
        self.stops.append((grid_x, grid_y))

    def calculate_path(self, road_network) -> bool:
        """
        Calculate the full path between all stops using road network.

        Args:
            road_network: RoadNetwork for pathfinding

        Returns:
            bool: True if path was successfully calculated
        """
        if len(self.stops) < 2:
            return False

        self.waypoints = []

        # Calculate path between each consecutive pair of stops
        for i in range(len(self.stops)):
            start_x, start_y = self.stops[i]

            # Next stop (loop back to first stop)
            next_index = (i + 1) % len(self.stops)
            end_x, end_y = self.stops[next_index]

            # Find path from current stop to next stop
            path_segment = road_network.find_path(start_x, start_y, end_x, end_y)

            if path_segment is None:
                print(f"Warning: Could not find path from stop {i} to stop {next_index} on route {self.route_id}")
                return False

            # Add path segment to waypoints (avoid duplicating the stop position)
            if not self.waypoints or path_segment[0] != self.waypoints[-1]:
                self.waypoints.extend(path_segment)
            else:
                # Skip first waypoint if it's the same as last waypoint
                self.waypoints.extend(path_segment[1:])

        return True

    def get_stop_count(self) -> int:
        """Get number of stops on this route."""
        return len(self.stops)

    def get_total_waypoint_count(self) -> int:
        """Get total number of waypoints in the route."""
        return len(self.waypoints)

    def is_stop(self, grid_x: int, grid_y: int) -> bool:
        """
        Check if a position is a stop on this route.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position

        Returns:
            bool: True if position is a stop
        """
        return (grid_x, grid_y) in self.stops

    def get_stop_index(self, grid_x: int, grid_y: int) -> Optional[int]:
        """
        Get the index of a stop position.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position

        Returns:
            int: Stop index, or None if not a stop
        """
        try:
            return self.stops.index((grid_x, grid_y))
        except ValueError:
            return None

    def calculate_express_stops(self, skip_factor: int = 2):
        """
        Calculate express stops (every nth stop).

        Args:
            skip_factor (int): Express buses stop every nth stop (2 = every other stop)
        """
        if not self.is_express or len(self.stops) < 3:
            self.express_stops = self.stops.copy()
            return

        self.express_stops = []
        # Always include first and last stops
        self.express_stops.append(self.stops[0])

        # Add every nth stop in between
        for i in range(skip_factor, len(self.stops) - 1, skip_factor):
            self.express_stops.append(self.stops[i])

        # Always include last stop
        if self.stops[-1] not in self.express_stops:
            self.express_stops.append(self.stops[-1])

    def _generate_route_color(self, route_id: int) -> Tuple[int, int, int]:
        """
        Generate a color for the route based on ID.

        Args:
            route_id (int): Route ID

        Returns:
            tuple: RGB color
        """
        colors = [
            (200, 50, 50),    # Red
            (50, 50, 200),    # Blue
            (50, 200, 50),    # Green
            (200, 200, 50),   # Yellow
            (200, 50, 200),   # Magenta
            (50, 200, 200),   # Cyan
            (200, 100, 50),   # Orange
            (150, 50, 200),   # Purple
        ]

        return colors[route_id % len(colors)]

    def __repr__(self):
        """String representation for debugging."""
        return f"BusRoute(id={self.route_id}, name='{self.name}', stops={len(self.stops)})"
