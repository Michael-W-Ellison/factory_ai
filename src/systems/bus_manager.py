"""
BusManager - manages bus routes, buses, and bus stops.

Handles:
- Route generation and management
- Bus spawning and lifecycle
- Bus stop placement
- NPC boarding/disembarking (future integration)
"""

import random
from typing import List, Dict, Optional
from src.entities.bus import Bus
from src.entities.bus_stop import BusStop
from src.systems.bus_route import BusRoute


class BusManager:
    """
    Manages the bus transportation system.

    Handles route generation, bus spawning, and stop placement.
    """

    def __init__(self, grid, road_network):
        """
        Initialize bus manager.

        Args:
            grid: World grid
            road_network: RoadNetwork for route pathfinding
        """
        self.grid = grid
        self.road_network = road_network

        # Routes
        self.routes: Dict[int, BusRoute] = {}  # route_id -> BusRoute
        self.next_route_id = 0

        # Buses
        self.buses: List[Bus] = []

        # Bus stops
        self.bus_stops: List[BusStop] = []  # All bus stops in the city

        # Configuration
        self.target_routes = 3  # Number of routes to generate
        self.buses_per_route = 2  # Number of buses per route
        self.stop_spacing = 15  # Tiles between stops
        self.express_route_chance = 0.3  # 30% chance a route is express

        # Scheduling
        self.game_time = 0.0  # Current game time (0-24 hours)
        self.spawn_timers: Dict[int, float] = {}  # route_id -> time until next spawn

    def generate_routes(self, num_routes: Optional[int] = None):
        """
        Generate bus routes in the city.

        Args:
            num_routes (int): Number of routes to generate (or use default)
        """
        if num_routes is None:
            num_routes = self.target_routes

        print(f"Generating {num_routes} bus routes...")

        for i in range(num_routes):
            route = self._generate_single_route(i)

            if route and route.get_stop_count() >= 3:
                self.routes[route.route_id] = route
                print(f"  Route {route.route_id}: {route.get_stop_count()} stops, "
                      f"{route.get_total_waypoint_count()} waypoints")
            else:
                print(f"  Route {i}: Failed to generate (not enough stops)")

        print(f"Generated {len(self.routes)} routes total")

    def _generate_single_route(self, route_id: int) -> Optional[BusRoute]:
        """
        Generate a single bus route.

        Args:
            route_id (int): Route ID

        Returns:
            BusRoute: Generated route, or None if failed
        """
        # Randomly decide if this is an express route
        is_express = random.random() < self.express_route_chance

        route = BusRoute(route_id, is_express=is_express)

        # Find suitable stops along roads
        # Try to create a route with 5-10 stops
        target_stops = random.randint(5, 10)

        # Start from a random road tile
        start_pos = self.road_network.get_random_road_tile()

        if start_pos is None:
            return None

        route.add_stop(*start_pos)

        # Generate subsequent stops
        current_pos = start_pos

        for _ in range(target_stops - 1):
            # Find next stop location (some distance away)
            next_stop = self._find_next_stop_location(current_pos, route)

            if next_stop is None:
                break

            route.add_stop(*next_stop)
            current_pos = next_stop

        # Calculate express stops if this is an express route
        if is_express:
            route.calculate_express_stops(skip_factor=2)

        # Calculate path between all stops
        if not route.calculate_path(self.road_network):
            return None

        # Place bus stops at each stop location (all stops, not just express)
        self._place_bus_stops_for_route(route)

        return route

    def _find_next_stop_location(self, current_pos: tuple, route: BusRoute) -> Optional[tuple]:
        """
        Find a location for the next bus stop.

        Args:
            current_pos (tuple): Current (grid_x, grid_y) position
            route (BusRoute): Route being generated

        Returns:
            tuple: (grid_x, grid_y) for next stop, or None
        """
        current_x, current_y = current_pos

        # Try to find a road tile that's 10-20 tiles away
        attempts = 50

        for _ in range(attempts):
            # Random direction and distance
            dx = random.randint(-20, 20)
            dy = random.randint(-20, 20)

            target_x = current_x + dx
            target_y = current_y + dy

            # Check if it's a road and not too close to existing stops
            if not self.road_network.is_road(target_x, target_y):
                continue

            # Check distance from all existing stops
            too_close = False
            for stop_x, stop_y in route.stops:
                distance = abs(target_x - stop_x) + abs(target_y - stop_y)
                if distance < self.stop_spacing:
                    too_close = True
                    break

            if not too_close:
                return (target_x, target_y)

        return None

    def _place_bus_stops_for_route(self, route: BusRoute):
        """
        Place bus stop props for a route.

        Args:
            route (BusRoute): Route to place stops for
        """
        for stop_x, stop_y in route.stops:
            # Check if there's already a stop at this location
            existing_stop = self._get_stop_at(stop_x, stop_y)

            if existing_stop:
                # Add this route to the existing stop
                existing_stop.add_route(route.route_id)
            else:
                # Create new bus stop
                bus_stop = BusStop(stop_x, stop_y, self.grid.tile_size)
                bus_stop.add_route(route.route_id)
                self.bus_stops.append(bus_stop)

    def _get_stop_at(self, grid_x: int, grid_y: int) -> Optional[BusStop]:
        """Get bus stop at a position, if any."""
        for stop in self.bus_stops:
            if stop.grid_x == grid_x and stop.grid_y == grid_y:
                return stop
        return None

    def spawn_buses(self):
        """Spawn buses on all routes."""
        print(f"Spawning buses on {len(self.routes)} routes...")

        for route_id, route in self.routes.items():
            for bus_index in range(self.buses_per_route):
                bus = self._spawn_bus_on_route(route, bus_index)
                if bus:
                    self.buses.append(bus)

        print(f"Spawned {len(self.buses)} buses total")

    def _spawn_bus_on_route(self, route: BusRoute, bus_index: int, is_express: bool = False) -> Optional[Bus]:
        """
        Spawn a bus on a specific route.

        Args:
            route (BusRoute): Route to spawn bus on
            bus_index (int): Index of bus on this route (for staggering)
            is_express (bool): Whether to spawn an express bus

        Returns:
            Bus: Spawned bus, or None if failed
        """
        if not route.stops:
            return None

        # Determine which stops this bus will use
        bus_stops = route.express_stops if (is_express and route.is_express) else route.stops

        if not bus_stops:
            return None

        # Start at a stop position (stagger buses along route)
        start_stop_index = (bus_index * len(bus_stops) // self.buses_per_route) % len(bus_stops)
        start_grid_x, start_grid_y = bus_stops[start_stop_index]

        # Get lane for starting position
        lanes = self.road_network.get_available_lanes(start_grid_x, start_grid_y)
        if not lanes:
            return None

        direction = lanes[0]
        lane_center = self.road_network.get_lane_center(start_grid_x, start_grid_y, direction)

        if lane_center is None:
            return None

        world_x, world_y = lane_center

        # Create bus (express or regular)
        bus = Bus(world_x, world_y, route_id=route.route_id,
                  initial_direction=direction, is_express=is_express)

        # Set route stops (express or all)
        bus.set_route(bus_stops)
        bus.current_stop_index = start_stop_index

        # Set full path as waypoints
        if route.waypoints:
            # Offset waypoints to start from current position
            offset_waypoints = route.waypoints[start_stop_index:] + route.waypoints[:start_stop_index]
            bus.set_path(offset_waypoints)

        return bus

    def update(self, dt: float, npcs=None, game_time: float = None):
        """
        Update all buses and handle scheduled spawning.

        Args:
            dt (float): Delta time in seconds
            npcs (list): List of NPCs for boarding/alighting
            game_time (float): Current game time in hours (0-24) for scheduling
        """
        # Update game time for scheduling
        if game_time is not None:
            self.game_time = game_time

        # Update each bus
        for bus in self.buses:
            bus.update(dt, self.road_network, npcs=npcs, bus_stops=self.bus_stops)

        # Handle scheduled bus spawning (if enabled)
        # This is disabled by default - call enable_scheduling() to activate
        # self._update_scheduled_spawning(dt)

    def render(self, screen, camera):
        """
        Render buses and bus stops.

        Args:
            screen: Pygame surface
            camera: Camera for rendering
        """
        # Render bus stops first (under buses)
        for bus_stop in self.bus_stops:
            bus_stop.render(screen, camera)

        # Render buses
        for bus in self.buses:
            bus.render(screen, camera)

    def get_nearest_bus_stop(self, grid_x: int, grid_y: int) -> Optional[BusStop]:
        """
        Find the nearest bus stop to a position.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position

        Returns:
            BusStop: Nearest bus stop, or None
        """
        if not self.bus_stops:
            return None

        nearest_stop = None
        nearest_distance = float('inf')

        for stop in self.bus_stops:
            distance = abs(stop.grid_x - grid_x) + abs(stop.grid_y - grid_y)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_stop = stop

        return nearest_stop

    def get_route_count(self) -> int:
        """Get number of active routes."""
        return len(self.routes)

    def get_bus_count(self) -> int:
        """Get number of active buses."""
        return len(self.buses)

    def get_stop_count(self) -> int:
        """Get number of bus stops."""
        return len(self.bus_stops)

    def __repr__(self):
        """String representation for debugging."""
        return (f"BusManager(routes={len(self.routes)}, buses={len(self.buses)}, "
                f"stops={len(self.bus_stops)})")
