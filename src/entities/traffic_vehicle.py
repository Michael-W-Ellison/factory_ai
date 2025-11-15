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

        # Following distance and collision avoidance
        self.safe_following_distance = 40.0  # pixels
        self.vehicle_ahead = None  # Reference to vehicle ahead in same lane
        self.stopping_for_vehicle = False

        # Pedestrian detection
        self.stopping_for_pedestrian = False
        self.pedestrian_wait_timer = 0.0

        # Turn signals
        self.turn_signal = None  # 'left', 'right', or None
        self.turn_signal_timer = 0.0
        self.turn_signal_blink_timer = 0.0

        # Visual states
        self.braking = False  # Show brake lights when true
        self.headlights_on = False  # Show headlights at night

        # Emergency vehicle behavior
        self.is_emergency = (vehicle_type == 'police')
        self.emergency_active = False  # Lights/sirens active
        self.emergency_timer = 0.0

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

    def update(self, dt: float, road_network, other_vehicles=None, npcs=None, time_of_day=None):
        """
        Update vehicle position and behavior.

        Args:
            dt (float): Delta time in seconds
            road_network: RoadNetwork for navigation
            other_vehicles (list, optional): List of other vehicles for collision avoidance
            npcs (list, optional): List of NPCs for pedestrian detection
            time_of_day (float, optional): Current time of day (0-24) for headlights
        """
        # Update headlights based on time of day
        if time_of_day is not None:
            self.headlights_on = (time_of_day < 6.0 or time_of_day >= 20.0)

        # Emergency vehicle behavior
        if self.is_emergency:
            self._update_emergency_behavior(dt)

        # Detect vehicle ahead (for following distance)
        self.vehicle_ahead = None
        self.stopping_for_vehicle = False
        if other_vehicles:
            self.vehicle_ahead = self._detect_vehicle_ahead(other_vehicles)
            if self.vehicle_ahead:
                distance = self._distance_to(self.vehicle_ahead.world_x, self.vehicle_ahead.world_y)
                if distance < self.safe_following_distance:
                    self.stopping_for_vehicle = True
                    # Match speed of vehicle ahead or slow down
                    self.target_speed = min(self.vehicle_ahead.speed * 0.9, self.target_speed)

        # Detect pedestrians crossing
        self.stopping_for_pedestrian = False
        if npcs and not self.is_emergency:  # Emergency vehicles don't stop for pedestrians
            if self._detect_pedestrian_crossing(npcs):
                self.stopping_for_pedestrian = True
                self.target_speed = 0.0
                self.pedestrian_wait_timer += dt
            else:
                self.pedestrian_wait_timer = max(0.0, self.pedestrian_wait_timer - dt)

        # Update turn signals
        self._update_turn_signals(dt, road_network)

        # Determine if braking (slowing down)
        old_speed = self.speed

        # Accelerate/decelerate to target speed
        if self.speed < self.target_speed:
            self.speed = min(self.speed + self.acceleration * dt, self.target_speed)
            self.braking = False
        elif self.speed > self.target_speed:
            # Braking
            decel_rate = self.acceleration * 2  # Brake faster than accelerate
            if self.stopping_for_pedestrian or self.stopping_for_vehicle:
                decel_rate *= 2  # Emergency braking
            self.speed = max(self.speed - decel_rate * dt, self.target_speed)
            self.braking = True
        else:
            self.braking = False

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

    def _update_emergency_behavior(self, dt: float):
        """Update emergency vehicle behavior (police)."""
        # Randomly activate emergency mode
        self.emergency_timer += dt
        if self.emergency_timer > 10.0:  # Change state every 10 seconds
            self.emergency_active = random.random() < 0.3  # 30% chance to activate
            self.emergency_timer = 0.0

        # When emergency mode active, can exceed speed limits
        if self.emergency_active:
            self.target_speed = self.max_speed * 1.3  # 30% faster
        else:
            self.target_speed = self.max_speed

    def _detect_vehicle_ahead(self, other_vehicles: List) -> Optional['TrafficVehicle']:
        """
        Detect if there's a vehicle ahead in the same lane.

        Args:
            other_vehicles (list): List of other traffic vehicles

        Returns:
            TrafficVehicle: Vehicle ahead, or None
        """
        closest_vehicle = None
        closest_distance = float('inf')

        for other in other_vehicles:
            if other.id == self.id:
                continue  # Skip self

            # Check if in same lane direction
            if other.current_lane != self.current_lane:
                continue

            # Calculate distance
            distance = self._distance_to(other.world_x, other.world_y)

            # Check if ahead (in direction of movement)
            if self._is_ahead(other.world_x, other.world_y):
                if distance < closest_distance and distance < self.safe_following_distance * 3:
                    closest_vehicle = other
                    closest_distance = distance

        return closest_vehicle

    def _distance_to(self, x: float, y: float) -> float:
        """Calculate distance to a point."""
        return math.sqrt((self.world_x - x)**2 + (self.world_y - y)**2)

    def _is_ahead(self, x: float, y: float) -> bool:
        """Check if a point is ahead in direction of travel."""
        dx = x - self.world_x
        dy = y - self.world_y

        # Check based on direction
        if self.current_lane == 'east':
            return dx > 0
        elif self.current_lane == 'west':
            return dx < 0
        elif self.current_lane == 'south':
            return dy > 0
        elif self.current_lane == 'north':
            return dy < 0

        return False

    def _detect_pedestrian_crossing(self, npcs: List) -> bool:
        """
        Detect if pedestrians are crossing in front of vehicle.

        Args:
            npcs (list): List of NPCs (and robots)

        Returns:
            bool: True if pedestrian detected in path
        """
        # Check area ahead of vehicle
        check_distance = 30.0  # pixels ahead to check

        for npc in npcs:
            # Get NPC position
            if hasattr(npc, 'world_x') and hasattr(npc, 'world_y'):
                npc_x = npc.world_x
                npc_y = npc.world_y
            else:
                continue

            # Calculate distance
            distance = self._distance_to(npc_x, npc_y)

            # Check if close and ahead
            if distance < check_distance and self._is_ahead(npc_x, npc_y):
                # Check if in our lane (perpendicular check)
                lane_width = 16.0  # Half lane width

                if self.current_lane in ['east', 'west']:
                    # Check Y distance (perpendicular to direction)
                    perp_distance = abs(npc_y - self.world_y)
                else:
                    # Check X distance (perpendicular to direction)
                    perp_distance = abs(npc_x - self.world_x)

                if perp_distance < lane_width:
                    return True

        return False

    def _update_turn_signals(self, dt: float, road_network):
        """Update turn signal state."""
        # Update blink timer
        self.turn_signal_blink_timer += dt
        if self.turn_signal_blink_timer > 1.0:
            self.turn_signal_blink_timer = 0.0

        # Check if approaching intersection
        tile_size = road_network.grid.tile_size
        grid_x = int(self.world_x // tile_size)
        grid_y = int(self.world_y // tile_size)

        # Look ahead for intersections
        look_ahead = 3  # tiles
        approaching_intersection = False

        for i in range(1, look_ahead + 1):
            check_x = grid_x
            check_y = grid_y

            if self.current_lane == 'east':
                check_x += i
            elif self.current_lane == 'west':
                check_x -= i
            elif self.current_lane == 'south':
                check_y += i
            elif self.current_lane == 'north':
                check_y -= i

            if road_network.is_intersection(check_x, check_y):
                approaching_intersection = True
                break

        # Activate turn signal if approaching intersection and planning to turn
        if approaching_intersection and self.waypoints:
            # Determine if next waypoint requires a turn
            if self.current_waypoint_index < len(self.waypoints):
                next_waypoint = self.waypoints[self.current_waypoint_index]
                next_x, next_y = next_waypoint

                # Calculate turn direction
                dx = next_x - grid_x
                dy = next_y - grid_y

                # Determine if turning left or right based on current direction
                if self.current_lane == 'east':
                    if dy < 0:
                        self.turn_signal = 'left'
                    elif dy > 0:
                        self.turn_signal = 'right'
                    else:
                        self.turn_signal = None
                elif self.current_lane == 'west':
                    if dy > 0:
                        self.turn_signal = 'left'
                    elif dy < 0:
                        self.turn_signal = 'right'
                    else:
                        self.turn_signal = None
                elif self.current_lane == 'south':
                    if dx > 0:
                        self.turn_signal = 'left'
                    elif dx < 0:
                        self.turn_signal = 'right'
                    else:
                        self.turn_signal = None
                elif self.current_lane == 'north':
                    if dx < 0:
                        self.turn_signal = 'left'
                    elif dx > 0:
                        self.turn_signal = 'right'
                    else:
                        self.turn_signal = None
        else:
            self.turn_signal = None

    def _update_intersection_state(self, road_network):
        """Update state when at intersections."""
        # Get tile size from grid
        tile_size = road_network.grid.tile_size

        # Get current grid position
        grid_x = int(self.world_x // tile_size)
        grid_y = int(self.world_y // tile_size)

        was_at_intersection = self.at_intersection
        self.at_intersection = road_network.is_intersection(grid_x, grid_y)

        # Basic traffic rule: slow down at intersections (unless emergency)
        if self.at_intersection and not was_at_intersection:
            # Just entered intersection, slow down
            if not (self.is_emergency and self.emergency_active):
                self.target_speed = self.max_speed * 0.5
        elif not self.at_intersection and was_at_intersection:
            # Just left intersection, speed up
            if not (self.is_emergency and self.emergency_active):
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
        """Render vehicle details (windows, wheels, lights)."""
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

        # Headlights (front of vehicle)
        if self.headlights_on and width > 10:
            light_size = max(2, int(height * 0.15))
            light_x = base_x + width - 2
            light_y1 = base_y + int(height * 0.25)
            light_y2 = base_y + int(height * 0.75) - light_size

            # Two headlights
            pygame.draw.circle(surface, (255, 255, 200), (light_x, light_y1), light_size)
            pygame.draw.circle(surface, (255, 255, 200), (light_x, light_y2), light_size)

        # Brake lights (rear of vehicle)
        if self.braking and width > 10:
            light_size = max(2, int(height * 0.15))
            light_x = base_x + 2
            light_y1 = base_y + int(height * 0.25)
            light_y2 = base_y + int(height * 0.75) - light_size

            # Two brake lights (red)
            pygame.draw.circle(surface, (255, 50, 50), (light_x, light_y1), light_size)
            pygame.draw.circle(surface, (255, 50, 50), (light_x, light_y2), light_size)

        # Turn signals (blink on/off)
        if self.turn_signal and width > 10:
            # Blink every 0.5 seconds
            if self.turn_signal_blink_timer < 0.5:
                light_size = max(3, int(height * 0.2))
                light_color = (255, 180, 0)  # Orange/amber

                if self.turn_signal == 'left':
                    # Left side light
                    light_x = base_x + width - 4
                    light_y = base_y + 2
                    pygame.draw.circle(surface, light_color, (light_x, light_y), light_size)
                elif self.turn_signal == 'right':
                    # Right side light
                    light_x = base_x + width - 4
                    light_y = base_y + height - 2
                    pygame.draw.circle(surface, light_color, (light_x, light_y), light_size)

        # Emergency lights (police) - flash red and blue
        if self.is_emergency and self.emergency_active and width > 10:
            light_size = max(3, int(height * 0.25))
            # Flash at different rates
            if int(self.emergency_timer * 4) % 2 == 0:
                # Red light (left)
                light_x = base_x + width // 2 - light_size
                light_y = base_y + 2
                pygame.draw.circle(surface, (255, 0, 0), (light_x, light_y), light_size)
            else:
                # Blue light (right)
                light_x = base_x + width // 2 + light_size
                light_y = base_y + 2
                pygame.draw.circle(surface, (0, 100, 255), (light_x, light_y), light_size)

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
