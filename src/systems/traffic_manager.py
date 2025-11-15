"""
TrafficManager - manages spawning and lifecycle of traffic vehicles.

Handles:
- Vehicle spawning at map edges and spawn points
- Vehicle pathfinding and routing
- Vehicle density management
- Vehicle cleanup when off-map
- Parked vehicles near buildings
"""

import random
from typing import List, Optional, Tuple
from src.entities.traffic_vehicle import TrafficVehicle


class ParkedVehicle:
    """
    A static parked vehicle near a building.

    Different from TrafficVehicle - these don't move and are decorative.
    """

    def __init__(self, world_x: float, world_y: float, vehicle_type: str = 'car',
                 facing_direction: str = 'east'):
        """
        Initialize a parked vehicle.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
            vehicle_type (str): Type of vehicle
            facing_direction (str): Direction vehicle is facing
        """
        self.world_x = world_x
        self.world_y = world_y
        self.vehicle_type = vehicle_type
        self.facing_direction = facing_direction

        # Get vehicle config from TrafficVehicle
        config = TrafficVehicle.VEHICLE_TYPES.get(vehicle_type, TrafficVehicle.VEHICLE_TYPES['car'])
        self.width = config['width']
        self.height = config['height']
        self.body_color = random.choice(config['color_choices'])
        self.window_color = (100, 150, 200)
        self.outline_color = tuple(max(0, c - 40) for c in self.body_color)

        # Determine facing angle
        direction_angles = {'east': 0, 'south': 90, 'west': 180, 'north': 270}
        self.facing_angle = direction_angles.get(facing_direction, 0)

    def render(self, screen, camera):
        """
        Render the parked vehicle.

        Args:
            screen: Pygame surface
            camera: Camera for world-to-screen transformation
        """
        import pygame

        # Calculate screen position
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)

        # Apply camera zoom
        width_px = int(self.width * camera.zoom)
        height_px = int(self.height * camera.zoom)

        # Don't render if off screen
        margin = max(width_px, height_px)
        if (screen_x + margin < 0 or screen_x - margin > screen.get_width() or
            screen_y + margin < 0 or screen_y - margin > screen.get_height()):
            return

        # Create temporary surface for rotation
        temp_size = int(max(width_px, height_px) * 1.5)
        temp_surface = pygame.Surface((temp_size, temp_size), pygame.SRCALPHA)

        # Center position on temp surface
        temp_x = temp_size // 2 - width_px // 2
        temp_y = temp_size // 2 - height_px // 2

        # Draw vehicle body
        body_rect = pygame.Rect(temp_x, temp_y, width_px, height_px)
        pygame.draw.rect(temp_surface, self.body_color, body_rect)
        pygame.draw.rect(temp_surface, self.outline_color, body_rect, 2)

        # Draw windows
        window_width = int(width_px * 0.3)
        window_height = int(height_px * 0.5)
        window_y = temp_y + int(height_px * 0.15)

        if window_width > 4 and window_height > 4:
            # Front window
            front_window_x = temp_x + width_px - window_width - 2
            pygame.draw.rect(temp_surface, self.window_color,
                           (front_window_x, window_y, window_width, window_height))

        # Draw wheels
        wheel_radius = max(2, int(height_px * 0.25))
        wheel_y = temp_y + height_px - wheel_radius

        if wheel_radius > 1:
            # Front wheel
            front_wheel_x = temp_x + width_px - int(width_px * 0.2)
            pygame.draw.circle(temp_surface, (40, 40, 40), (front_wheel_x, wheel_y), wheel_radius)

            # Rear wheel
            rear_wheel_x = temp_x + int(width_px * 0.2)
            pygame.draw.circle(temp_surface, (40, 40, 40), (rear_wheel_x, wheel_y), wheel_radius)

        # Rotate based on facing angle
        rotated_surface = pygame.transform.rotate(temp_surface, -self.facing_angle)
        rotated_rect = rotated_surface.get_rect(center=(screen_x, screen_y))

        # Blit to screen
        screen.blit(rotated_surface, rotated_rect.topleft)


class TrafficManager:
    """
    Manages all traffic vehicles in the game world.

    Spawns vehicles at road edges, assigns routes, and manages
    vehicle lifecycle.
    """

    def __init__(self, grid, road_network):
        """
        Initialize traffic manager.

        Args:
            grid: World grid
            road_network: RoadNetwork for pathfinding
        """
        self.grid = grid
        self.road_network = road_network

        # Active traffic vehicles
        self.vehicles: List[TrafficVehicle] = []

        # Parked vehicles (static decorative vehicles)
        self.parked_vehicles: List[ParkedVehicle] = []

        # Spawn configuration
        self.target_vehicle_count = 15  # Target number of active vehicles
        self.max_vehicle_count = 25     # Maximum vehicles allowed
        self.spawn_timer = 0.0
        self.spawn_interval = 2.0       # Seconds between spawn attempts

        # Vehicle type probabilities (must sum to 1.0)
        self.vehicle_type_weights = {
            'car': 0.6,      # 60% cars
            'truck': 0.15,   # 15% trucks
            'van': 0.15,     # 15% vans
            'bus': 0.07,     # 7% buses
            'police': 0.03   # 3% police
        }

    def update(self, dt: float, npcs=None, time_of_day=None):
        """
        Update all traffic vehicles.

        Args:
            dt (float): Delta time in seconds
            npcs (list, optional): List of NPCs for pedestrian detection
            time_of_day (float, optional): Current time of day (0-24) for headlights
        """
        # Update spawn timer
        self.spawn_timer += dt

        # Spawn new vehicles if below target count
        if (self.spawn_timer >= self.spawn_interval and
            len(self.vehicles) < self.target_vehicle_count):
            self._spawn_vehicle()
            self.spawn_timer = 0.0

        # Update all vehicles
        vehicles_to_remove = []

        for vehicle in self.vehicles:
            # Pass other vehicles for collision avoidance
            vehicle.update(dt, self.road_network,
                          other_vehicles=self.vehicles,
                          npcs=npcs,
                          time_of_day=time_of_day)

            # Check if vehicle is off map (despawn)
            if vehicle.is_off_map(self.grid):
                vehicles_to_remove.append(vehicle)

            # Check if vehicle has no waypoints and is idle
            if (vehicle.current_waypoint_index >= len(vehicle.waypoints) and
                not vehicle.waypoints):
                # Vehicle finished its route, give it a new one or despawn
                if random.random() < 0.3:  # 30% chance to despawn
                    vehicles_to_remove.append(vehicle)
                else:
                    # Give new random route
                    self._assign_random_route(vehicle)

        # Remove despawned vehicles
        for vehicle in vehicles_to_remove:
            self.vehicles.remove(vehicle)

    def _spawn_vehicle(self) -> Optional[TrafficVehicle]:
        """
        Spawn a new traffic vehicle at a random road edge.

        Returns:
            TrafficVehicle: The spawned vehicle, or None if spawn failed
        """
        # Find spawn location (random road tile at edge of map)
        spawn_location = self._find_spawn_location()

        if spawn_location is None:
            return None

        grid_x, grid_y, direction = spawn_location

        # Calculate world position (lane center)
        lane_center = self.road_network.get_lane_center(grid_x, grid_y, direction)

        if lane_center is None:
            return None

        world_x, world_y = lane_center

        # Choose vehicle type
        vehicle_type = self._choose_vehicle_type()

        # Create vehicle
        vehicle = TrafficVehicle(
            world_x=world_x,
            world_y=world_y,
            vehicle_type=vehicle_type,
            initial_direction=direction
        )

        # Assign a random route
        self._assign_random_route(vehicle)

        # Add to active vehicles
        self.vehicles.append(vehicle)

        return vehicle

    def _find_spawn_location(self) -> Optional[Tuple[int, int, str]]:
        """
        Find a random spawn location at a map edge.

        Returns:
            tuple: (grid_x, grid_y, direction) or None if no spawn found
        """
        # Try map edges
        edges = ['north', 'south', 'east', 'west']
        random.shuffle(edges)

        for edge in edges:
            spawn_pos = self._find_spawn_on_edge(edge)
            if spawn_pos:
                return spawn_pos

        # Fallback: spawn at any random road
        return self._find_random_road_spawn()

    def _find_spawn_on_edge(self, edge: str) -> Optional[Tuple[int, int, str]]:
        """
        Find spawn location on a specific map edge.

        Args:
            edge (str): 'north', 'south', 'east', or 'west'

        Returns:
            tuple: (grid_x, grid_y, direction) or None
        """
        # Get road tiles along this edge
        edge_roads = []

        if edge == 'north':
            y = 0
            for x in range(self.grid.width_tiles):
                if self.road_network.is_road(x, y):
                    # Check if road has southbound lane
                    if 'south' in self.road_network.get_available_lanes(x, y):
                        edge_roads.append((x, y, 'south'))

        elif edge == 'south':
            y = self.grid.height_tiles - 1
            for x in range(self.grid.width_tiles):
                if self.road_network.is_road(x, y):
                    # Check if road has northbound lane
                    if 'north' in self.road_network.get_available_lanes(x, y):
                        edge_roads.append((x, y, 'north'))

        elif edge == 'west':
            x = 0
            for y in range(self.grid.height_tiles):
                if self.road_network.is_road(x, y):
                    # Check if road has eastbound lane
                    if 'east' in self.road_network.get_available_lanes(x, y):
                        edge_roads.append((x, y, 'east'))

        elif edge == 'east':
            x = self.grid.width_tiles - 1
            for y in range(self.grid.height_tiles):
                if self.road_network.is_road(x, y):
                    # Check if road has westbound lane
                    if 'west' in self.road_network.get_available_lanes(x, y):
                        edge_roads.append((x, y, 'west'))

        if edge_roads:
            return random.choice(edge_roads)

        return None

    def _find_random_road_spawn(self) -> Optional[Tuple[int, int, str]]:
        """
        Find a spawn location at any random road tile.

        Returns:
            tuple: (grid_x, grid_y, direction) or None
        """
        road_pos = self.road_network.get_random_road_tile()

        if road_pos is None:
            return None

        grid_x, grid_y = road_pos

        # Get available lanes
        lanes = self.road_network.get_available_lanes(grid_x, grid_y)

        if not lanes:
            return None

        direction = random.choice(lanes)

        return (grid_x, grid_y, direction)

    def _choose_vehicle_type(self) -> str:
        """
        Choose a random vehicle type based on configured weights.

        Returns:
            str: Vehicle type
        """
        types = list(self.vehicle_type_weights.keys())
        weights = list(self.vehicle_type_weights.values())

        return random.choices(types, weights=weights, k=1)[0]

    def _assign_random_route(self, vehicle: TrafficVehicle):
        """
        Assign a random route to a vehicle.

        Args:
            vehicle (TrafficVehicle): Vehicle to assign route to
        """
        # Get current position
        tile_size = self.grid.tile_size
        current_grid_x = int(vehicle.world_x // tile_size)
        current_grid_y = int(vehicle.world_y // tile_size)

        # Find a random destination
        destination = self.road_network.get_random_road_tile()

        if destination is None:
            return

        dest_x, dest_y = destination

        # Find path from current to destination
        path = self.road_network.find_path(current_grid_x, current_grid_y, dest_x, dest_y)

        if path:
            vehicle.set_path(path)
            vehicle.set_destination(dest_x, dest_y)

    def spawn_vehicle_at(self, grid_x: int, grid_y: int, vehicle_type: str = 'car',
                         direction: Optional[str] = None) -> Optional[TrafficVehicle]:
        """
        Spawn a specific vehicle at a specific location.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
            vehicle_type (str): Type of vehicle
            direction (str): Initial direction (or None for auto-detect)

        Returns:
            TrafficVehicle: Spawned vehicle or None if failed
        """
        if not self.road_network.is_road(grid_x, grid_y):
            return None

        # Get direction if not specified
        if direction is None:
            lanes = self.road_network.get_available_lanes(grid_x, grid_y)
            if not lanes:
                return None
            direction = random.choice(lanes)

        # Get lane center
        lane_center = self.road_network.get_lane_center(grid_x, grid_y, direction)

        if lane_center is None:
            return None

        world_x, world_y = lane_center

        # Create vehicle
        vehicle = TrafficVehicle(
            world_x=world_x,
            world_y=world_y,
            vehicle_type=vehicle_type,
            initial_direction=direction
        )

        # Assign random route
        self._assign_random_route(vehicle)

        # Add to vehicles list
        self.vehicles.append(vehicle)

        return vehicle

    def generate_parked_vehicles(self, count: int = 30):
        """
        Generate parked vehicles near buildings and along roads.

        Args:
            count (int): Number of parked vehicles to generate
        """
        self.parked_vehicles.clear()

        tile_size = self.grid.tile_size

        for _ in range(count):
            # Find a random road tile
            road_pos = self.road_network.get_random_road_tile()

            if road_pos is None:
                continue

            grid_x, grid_y = road_pos

            # Get available lanes
            lanes = self.road_network.get_available_lanes(grid_x, grid_y)

            if not lanes:
                continue

            # Pick a random lane
            direction = random.choice(lanes)

            # Get lane center and offset to side (parking)
            lane_center = self.road_network.get_lane_center(grid_x, grid_y, direction)

            if lane_center is None:
                continue

            world_x, world_y = lane_center

            # Offset to parking position (to the side of the road)
            parking_offset = 20  # pixels to the side

            if direction in ['east', 'west']:
                # Park to the side (north or south)
                world_y += random.choice([-parking_offset, parking_offset])
            else:
                # Park to the side (east or west)
                world_x += random.choice([-parking_offset, parking_offset])

            # Choose vehicle type (mostly cars for parked vehicles)
            vehicle_type_weights = {
                'car': 0.8,
                'truck': 0.1,
                'van': 0.1
            }
            types = list(vehicle_type_weights.keys())
            weights = list(vehicle_type_weights.values())
            vehicle_type = random.choices(types, weights=weights, k=1)[0]

            # Create parked vehicle
            parked = ParkedVehicle(
                world_x=world_x,
                world_y=world_y,
                vehicle_type=vehicle_type,
                facing_direction=direction
            )

            self.parked_vehicles.append(parked)

        print(f"Generated {len(self.parked_vehicles)} parked vehicles")

    def render(self, screen, camera):
        """
        Render all traffic vehicles and parked vehicles.

        Args:
            screen: Pygame surface
            camera: Camera for rendering
        """
        # Render parked vehicles first (behind moving traffic)
        for parked in self.parked_vehicles:
            parked.render(screen, camera)

        # Render moving vehicles
        for vehicle in self.vehicles:
            vehicle.render(screen, camera)

    def get_vehicle_count(self) -> int:
        """Get current number of active vehicles."""
        return len(self.vehicles)

    def set_target_vehicle_count(self, count: int):
        """
        Set target number of vehicles to maintain.

        Args:
            count (int): Target vehicle count
        """
        self.target_vehicle_count = max(0, min(count, self.max_vehicle_count))

    def clear_all_vehicles(self):
        """Remove all traffic vehicles."""
        self.vehicles.clear()

    def __repr__(self):
        """String representation for debugging."""
        return f"TrafficManager(vehicles={len(self.vehicles)}/{self.target_vehicle_count})"
