"""
Bus - Public transportation vehicle that follows routes and picks up NPCs.

Extends TrafficVehicle with bus-specific behavior:
- Stops at designated bus stops
- Loads and unloads NPC passengers
- Follows predefined routes
- Larger size and slower speed than cars
"""

import pygame
from typing import List, Optional, Set
from src.entities.traffic_vehicle import TrafficVehicle


class Bus(TrafficVehicle):
    """
    Bus vehicle for public transportation.

    Extends TrafficVehicle with passenger management and route following.

    Attributes:
        route_id (int): ID of the bus route this bus follows
        passengers (set): Set of NPC IDs currently on the bus
        max_capacity (int): Maximum number of passengers
        current_stop_index (int): Index of current/next stop in route
        stopped_at_stop (bool): Whether bus is currently stopped at a stop
        stop_timer (float): Time spent at current stop
    """

    def __init__(self, world_x: float, world_y: float, route_id: int = 0,
                 initial_direction: str = 'east'):
        """
        Initialize a bus.

        Args:
            world_x (float): Starting world X position
            world_y (float): Starting world Y position
            route_id (int): ID of the route this bus follows
            initial_direction (str): Initial lane direction
        """
        # Initialize as traffic vehicle (bus type)
        super().__init__(world_x, world_y, vehicle_type='bus', initial_direction=initial_direction)

        # Bus-specific properties
        self.route_id = route_id
        self.passengers: Set[int] = set()  # NPC IDs
        self.max_capacity = 20

        # Route following
        self.route_stops: List[tuple] = []  # List of (grid_x, grid_y) stop positions
        self.current_stop_index = 0
        self.stopped_at_stop = False
        self.stop_timer = 0.0
        self.stop_duration = 5.0  # Seconds to wait at each stop

        # Override vehicle type configuration for bus
        self.width = 50
        self.height = 24
        self.max_speed = 30.0  # Slower than cars
        self.acceleration = 15.0
        self.target_speed = self.max_speed

        # Bus colors (yellow/orange for school bus or city bus)
        self.body_color = (200, 150, 50)  # Orange-yellow
        self.window_color = (100, 150, 200)
        self.outline_color = (140, 100, 30)  # Darker orange

        # Visual properties
        self.door_open = False  # Animated doors when stopped

    def set_route(self, stops: List[tuple]):
        """
        Set the bus route as a list of stops.

        Args:
            stops (list): List of (grid_x, grid_y) stop positions
        """
        self.route_stops = stops
        self.current_stop_index = 0

    def update(self, dt: float, road_network):
        """
        Update bus position and behavior.

        Args:
            dt (float): Delta time in seconds
            road_network: RoadNetwork for navigation
        """
        # If stopped at a stop, handle waiting
        if self.stopped_at_stop:
            self.stop_timer += dt
            self.door_open = True

            # Check if we've waited long enough
            if self.stop_timer >= self.stop_duration:
                self._depart_from_stop()

        # Normal movement when not stopped
        if not self.stopped_at_stop:
            # Update as normal traffic vehicle
            super().update(dt, road_network)

            # Check if we're approaching next stop
            self._check_for_stop_arrival(road_network)

    def _check_for_stop_arrival(self, road_network):
        """Check if bus has arrived at the next stop."""
        if not self.route_stops or self.stopped_at_stop:
            return

        # Get current stop position
        if self.current_stop_index >= len(self.route_stops):
            # Loop back to first stop
            self.current_stop_index = 0

        stop_grid_x, stop_grid_y = self.route_stops[self.current_stop_index]

        # Get tile size from grid
        tile_size = road_network.grid.tile_size

        # Calculate stop world position (center of tile)
        stop_world_x = stop_grid_x * tile_size + tile_size / 2
        stop_world_y = stop_grid_y * tile_size + tile_size / 2

        # Check distance to stop
        import math
        distance = math.sqrt((self.world_x - stop_world_x)**2 + (self.world_y - stop_world_y)**2)

        # If close enough, stop at the bus stop
        if distance < 20.0:  # Within 20 pixels
            self._arrive_at_stop()

    def _arrive_at_stop(self):
        """Bus has arrived at a stop."""
        self.stopped_at_stop = True
        self.stop_timer = 0.0
        self.speed = 0.0
        self.target_speed = 0.0
        self.door_open = True

    def _depart_from_stop(self):
        """Bus is departing from a stop."""
        self.stopped_at_stop = False
        self.stop_timer = 0.0
        self.target_speed = self.max_speed
        self.door_open = False

        # Move to next stop
        self.current_stop_index += 1
        if self.current_stop_index >= len(self.route_stops):
            self.current_stop_index = 0

    def add_passenger(self, npc_id: int) -> bool:
        """
        Add a passenger to the bus.

        Args:
            npc_id (int): ID of NPC boarding

        Returns:
            bool: True if passenger was added, False if bus is full
        """
        if len(self.passengers) >= self.max_capacity:
            return False

        self.passengers.add(npc_id)
        return True

    def remove_passenger(self, npc_id: int) -> bool:
        """
        Remove a passenger from the bus.

        Args:
            npc_id (int): ID of NPC disembarking

        Returns:
            bool: True if passenger was removed
        """
        if npc_id in self.passengers:
            self.passengers.remove(npc_id)
            return True
        return False

    def get_passenger_count(self) -> int:
        """Get current number of passengers."""
        return len(self.passengers)

    def is_full(self) -> bool:
        """Check if bus is at capacity."""
        return len(self.passengers) >= self.max_capacity

    def render(self, screen: pygame.Surface, camera):
        """
        Render the bus with passenger count and route number.

        Args:
            screen: Pygame surface
            camera: Camera for world-to-screen transformation
        """
        # Render base vehicle
        super().render(screen, camera)

        # Calculate screen position
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)

        # Apply camera zoom
        width_px = int(self.width * camera.zoom)
        height_px = int(self.height * camera.zoom)

        # Don't render extras if off screen
        margin = max(width_px, height_px)
        if (screen_x + margin < 0 or screen_x - margin > screen.get_width() or
            screen_y + margin < 0 or screen_y - margin > screen.get_height()):
            return

        # Render route number on top of bus
        if camera.zoom >= 0.8:  # Only show when zoomed in enough
            font = pygame.font.Font(None, max(16, int(20 * camera.zoom)))
            route_text = font.render(f"#{self.route_id}", True, (255, 255, 255))
            text_rect = route_text.get_rect(center=(screen_x, screen_y - height_px // 2 - 8))

            # Draw background for route number
            bg_rect = text_rect.inflate(4, 2)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            screen.blit(route_text, text_rect)

        # Render passenger count indicator (if carrying passengers)
        if self.passengers and camera.zoom >= 0.6:
            passenger_count = len(self.passengers)
            font_small = pygame.font.Font(None, max(14, int(16 * camera.zoom)))
            passenger_text = font_small.render(f"{passenger_count}/{self.max_capacity}", True, (255, 255, 0))
            passenger_rect = passenger_text.get_rect(center=(screen_x, screen_y + height_px // 2 + 8))

            # Draw background
            bg_rect = passenger_rect.inflate(4, 2)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            screen.blit(passenger_text, passenger_rect)

    def _render_vehicle_details(self, surface, base_x, base_y, width, height):
        """Render bus-specific details (windows, wheels, doors)."""
        # Multiple windows along the side
        num_windows = 4
        window_width = int(width * 0.15)
        window_height = int(height * 0.4)
        window_y = base_y + int(height * 0.2)

        if window_width > 3 and window_height > 3:
            for i in range(num_windows):
                window_x = base_x + int(width * 0.15) + i * int(width * 0.18)
                if window_x + window_width < base_x + width - int(width * 0.1):
                    pygame.draw.rect(surface, self.window_color,
                                   (window_x, window_y, window_width, window_height))
                    pygame.draw.rect(surface, (40, 40, 40),
                                   (window_x, window_y, window_width, window_height), 1)

        # Wheels (bus has visible wheels on both sides)
        wheel_radius = max(3, int(height * 0.3))
        wheel_y = base_y + height - wheel_radius

        if wheel_radius > 2:
            # Front wheels
            front_wheel_x = base_x + width - int(width * 0.15)
            pygame.draw.circle(surface, (40, 40, 40), (front_wheel_x, wheel_y), wheel_radius)
            pygame.draw.circle(surface, (80, 80, 80), (front_wheel_x, wheel_y), wheel_radius // 2)

            # Rear wheels (bus has double rear wheels)
            rear_wheel_x = base_x + int(width * 0.2)
            pygame.draw.circle(surface, (40, 40, 40), (rear_wheel_x, wheel_y), wheel_radius)
            pygame.draw.circle(surface, (80, 80, 80), (rear_wheel_x, wheel_y), wheel_radius // 2)

        # Draw door indicator (if stopped and door open)
        if self.door_open and width > 20:
            door_width = int(width * 0.12)
            door_height = int(height * 0.6)
            door_x = base_x + int(width * 0.35)
            door_y = base_y + int(height * 0.2)

            # Open door shows as darker rectangle
            pygame.draw.rect(surface, (100, 70, 30), (door_x, door_y, door_width, door_height))
            pygame.draw.rect(surface, (60, 40, 20), (door_x, door_y, door_width, door_height), 1)

    def __repr__(self):
        """String representation for debugging."""
        return (f"Bus(route={self.route_id}, pos=({self.world_x:.0f}, {self.world_y:.0f}), "
                f"passengers={len(self.passengers)}/{self.max_capacity}, "
                f"stop={self.current_stop_index}/{len(self.route_stops)})")
