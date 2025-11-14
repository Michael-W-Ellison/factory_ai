"""
TrafficVehicle - Moving vehicles that follow roads and lanes.

Different from the static Vehicle class used for deconstruction.
These vehicles actively navigate the road network.
"""

import pygame
import math
import random
from typing import Optional, List, Tuple


class TrafficVehicle:
    """
    A vehicle that navigates the road network following lanes and traffic rules.

    Attributes:
        world_x (float): World X position
        world_y (float): World Y position
        vehicle_type (str): Type of vehicle (car, truck, van, bus, police)
        current_lane (str): Current lane direction ('north', 'south', 'east', 'west')
        speed (float): Current speed in px/s
    """

    # Vehicle type configurations
    VEHICLE_TYPES = {
        'car': {
            'width': 32,
            'height': 20,
            'max_speed': 50.0,  # px/s
            'acceleration': 30.0,
            'color_choices': [
                (180, 50, 50),    # Red
                (50, 50, 180),    # Blue
                (50, 150, 50),    # Green
                (150, 150, 150),  # Silver
                (80, 80, 80),     # Dark gray
                (200, 200, 200),  # White
            ]
        },
        'truck': {
            'width': 48,
            'height': 24,
            'max_speed': 40.0,
            'acceleration': 20.0,
            'color_choices': [
                (100, 80, 60),    # Brown
                (180, 50, 50),    # Red
                (50, 50, 180),    # Blue
                (80, 80, 80),     # Gray
            ]
        },
        'van': {
            'width': 40,
            'height': 22,
            'max_speed': 45.0,
            'acceleration': 25.0,
            'color_choices': [
                (180, 180, 50),   # Yellow
                (200, 200, 200),  # White
                (50, 50, 180),    # Blue
                (150, 150, 150),  # Silver
            ]
        },
        'bus': {
            'width': 50,
            'height': 24,
            'max_speed': 30.0,
            'acceleration': 15.0,
            'color_choices': [
                (200, 150, 50),   # Orange/yellow
                (180, 180, 50),   # Yellow
            ]
        },
        'police': {
            'width': 32,
            'height': 20,
            'max_speed': 60.0,  # Faster than civilian vehicles
            'acceleration': 40.0,
            'color_choices': [
                (40, 40, 40),     # Black
                (200, 200, 200),  # White
            ]
        }
    }

    def __init__(self, world_x: float, world_y: float, vehicle_type: str = 'car',
                 initial_direction: str = 'east'):
        """
        Initialize a traffic vehicle.

        Args:
            world_x (float): Starting world X position
            world_y (float): Starting world Y position
            vehicle_type (str): Type of vehicle
            initial_direction (str): Initial lane direction
        """
        self.world_x = world_x
        self.world_y = world_y
        self.vehicle_type = vehicle_type

        # Get vehicle configuration
        config = self.VEHICLE_TYPES.get(vehicle_type, self.VEHICLE_TYPES['car'])
        self.width = config['width']
        self.height = config['height']
        self.max_speed = config['max_speed']
        self.acceleration = config['acceleration']

        # Visual properties
        self.body_color = random.choice(config['color_choices'])
        self.window_color = (100, 150, 200)
        self.outline_color = tuple(max(0, c - 40) for c in self.body_color)

        # Movement
        self.current_lane = initial_direction  # 'north', 'south', 'east', 'west'
        self.speed = 0.0  # Current speed (will accelerate to max_speed)
        self.target_speed = self.max_speed
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        # Pathfinding
        self.waypoints: List[Tuple[int, int]] = []  # List of (grid_x, grid_y) waypoints
        self.current_waypoint_index = 0
        self.destination: Optional[Tuple[int, int]] = None

        # Traffic state
        self.at_intersection = False
        self.stopping_for_intersection = False
        self.wait_timer = 0.0  # Time waiting at intersection

        # Rotation (for rendering)
        self.facing_angle = 0  # Degrees: 0=East, 90=South, 180=West, 270=North

        # ID for tracking
        self.id = id(self)

        # Update initial velocity based on direction
        self._update_velocity_from_direction()

    def _update_velocity_from_direction(self):
        """Update velocity components based on current lane direction."""
        # Direction to angle mapping
        direction_angles = {
            'east': 0,
            'south': 90,
            'west': 180,
            'north': 270
        }

        self.facing_angle = direction_angles.get(self.current_lane, 0)

        # Calculate velocity components
        angle_rad = math.radians(self.facing_angle)
        self.velocity_x = math.cos(angle_rad) * self.speed
        self.velocity_y = math.sin(angle_rad) * self.speed

    def set_path(self, waypoints: List[Tuple[int, int]]):
        """
        Set a path of waypoints for the vehicle to follow.

        Args:
            waypoints (list): List of (grid_x, grid_y) waypoints
        """
        self.waypoints = waypoints
        self.current_waypoint_index = 0

    def set_destination(self, grid_x: int, grid_y: int):
        """
        Set a destination for the vehicle to navigate to.

        Args:
            grid_x (int): Destination grid X
            grid_y (int): Destination grid Y
        """
        self.destination = (grid_x, grid_y)

    def update(self, dt: float, road_network):
        """
        Update vehicle position and behavior.

        Args:
            dt (float): Delta time in seconds
            road_network: RoadNetwork for navigation
        """
        # Accelerate/decelerate to target speed
        if self.speed < self.target_speed:
            self.speed = min(self.speed + self.acceleration * dt, self.target_speed)
        elif self.speed > self.target_speed:
            self.speed = max(self.speed - self.acceleration * 2 * dt, self.target_speed)

        # Update velocity from speed
        self._update_velocity_from_direction()

        # Move vehicle
        self.world_x += self.velocity_x * dt
        self.world_y += self.velocity_y * dt

        # Follow waypoints if available
        if self.waypoints and self.current_waypoint_index < len(self.waypoints):
            self._follow_waypoint(road_network)

        # Update intersection state
        self._update_intersection_state(road_network)

    def _follow_waypoint(self, road_network):
        """Follow the current waypoint in the path."""
        if self.current_waypoint_index >= len(self.waypoints):
            return

        # Get tile size from grid
        tile_size = road_network.grid.tile_size

        target_grid_x, target_grid_y = self.waypoints[self.current_waypoint_index]

        # Get lane center for current direction
        lane_center = road_network.get_lane_center(target_grid_x, target_grid_y, self.current_lane)

        if lane_center is None:
            # No valid lane, try to get any available lane
            available_lanes = road_network.get_available_lanes(target_grid_x, target_grid_y)
            if available_lanes:
                self.current_lane = available_lanes[0]
                lane_center = road_network.get_lane_center(target_grid_x, target_grid_y, self.current_lane)

        if lane_center:
            target_x, target_y = lane_center

            # Check if we've reached this waypoint (within 10 pixels)
            distance = math.sqrt((self.world_x - target_x)**2 + (self.world_y - target_y)**2)

            if distance < 10.0:
                # Reached waypoint, advance to next
                self.current_waypoint_index += 1

                # If at intersection, choose next direction
                if road_network.is_intersection(target_grid_x, target_grid_y):
                    self._choose_turn_at_intersection(road_network, target_grid_x, target_grid_y)

    def _choose_turn_at_intersection(self, road_network, grid_x: int, grid_y: int):
        """
        Choose which direction to turn at an intersection.

        Args:
            road_network: RoadNetwork
            grid_x (int): Intersection grid X
            grid_y (int): Intersection grid Y
        """
        # Get valid turns from current direction
        valid_turns = road_network.get_valid_turns(grid_x, grid_y, self.current_lane)

        if not valid_turns:
            return

        # If we have more waypoints, choose turn towards next waypoint
        if self.current_waypoint_index < len(self.waypoints):
            next_waypoint = self.waypoints[self.current_waypoint_index]
            next_x, next_y = next_waypoint

            # Calculate which direction to go
            dx = next_x - grid_x
            dy = next_y - grid_y

            if abs(dx) > abs(dy):
                # More horizontal movement
                desired_direction = 'east' if dx > 0 else 'west'
            else:
                # More vertical movement
                desired_direction = 'south' if dy > 0 else 'north'

            # Use desired direction if valid, otherwise pick random valid turn
            if desired_direction in valid_turns:
                self.current_lane = desired_direction
            else:
                self.current_lane = random.choice(valid_turns)
        else:
            # No more waypoints, pick random turn
            self.current_lane = random.choice(valid_turns)

        self._update_velocity_from_direction()

    def _update_intersection_state(self, road_network):
        """Update state when at intersections."""
        # Get tile size from grid
        tile_size = road_network.grid.tile_size

        # Get current grid position
        grid_x = int(self.world_x // tile_size)
        grid_y = int(self.world_y // tile_size)

        was_at_intersection = self.at_intersection
        self.at_intersection = road_network.is_intersection(grid_x, grid_y)

        # Basic traffic rule: slow down at intersections
        if self.at_intersection and not was_at_intersection:
            # Just entered intersection, slow down
            self.target_speed = self.max_speed * 0.5
        elif not self.at_intersection and was_at_intersection:
            # Just left intersection, speed up
            self.target_speed = self.max_speed

    def render(self, screen: pygame.Surface, camera):
        """
        Render the vehicle.

        Args:
            screen: Pygame surface
            camera: Camera for world-to-screen transformation
        """
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

        # Draw vehicle details
        self._render_vehicle_details(temp_surface, temp_x, temp_y, width_px, height_px)

        # Rotate based on facing angle
        rotated_surface = pygame.transform.rotate(temp_surface, -self.facing_angle)
        rotated_rect = rotated_surface.get_rect(center=(screen_x, screen_y))

        # Blit to screen
        screen.blit(rotated_surface, rotated_rect.topleft)

    def _render_vehicle_details(self, surface, base_x, base_y, width, height):
        """Render vehicle details (windows, wheels)."""
        # Windows
        window_width = int(width * 0.3)
        window_height = int(height * 0.5)
        window_y = base_y + int(height * 0.15)

        if window_width > 4 and window_height > 4:
            # Front window
            front_window_x = base_x + width - window_width - 2
            pygame.draw.rect(surface, self.window_color,
                           (front_window_x, window_y, window_width, window_height))

            # Rear window
            rear_window_x = base_x + 2
            pygame.draw.rect(surface, self.window_color,
                           (rear_window_x, window_y, window_width, window_height))

        # Wheels
        wheel_radius = max(2, int(height * 0.25))
        wheel_y = base_y + height - wheel_radius

        if wheel_radius > 1:
            # Front wheel
            front_wheel_x = base_x + width - int(width * 0.2)
            pygame.draw.circle(surface, (40, 40, 40), (front_wheel_x, wheel_y), wheel_radius)

            # Rear wheel
            rear_wheel_x = base_x + int(width * 0.2)
            pygame.draw.circle(surface, (40, 40, 40), (rear_wheel_x, wheel_y), wheel_radius)

    def is_off_map(self, grid) -> bool:
        """
        Check if vehicle is off the map.

        Args:
            grid: World grid

        Returns:
            bool: True if vehicle is outside map bounds
        """
        # Get tile size from grid
        tile_size = grid.tile_size

        grid_x = int(self.world_x // tile_size)
        grid_y = int(self.world_y // tile_size)

        return (grid_x < 0 or grid_x >= grid.width_tiles or
                grid_y < 0 or grid_y >= grid.height_tiles)

    def __repr__(self):
        """String representation for debugging."""
        return (f"TrafficVehicle({self.vehicle_type}, pos=({self.world_x:.0f}, {self.world_y:.0f}), "
                f"lane={self.current_lane}, speed={self.speed:.1f})")
