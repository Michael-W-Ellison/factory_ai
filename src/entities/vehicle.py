"""
Vehicle - Cars, trucks, and other vehicles that can be deconstructed for materials.

Vehicles are world objects that can be found in the city and deconstructed
by robots to collect metal, plastic, rubber, and other materials.
"""

import pygame
import random
from typing import Dict, Optional


class Vehicle:
    """
    Base class for vehicles that can be deconstructed.

    Vehicles provide materials when deconstructed, but doing so
    is highly illegal and generates suspicion.
    """

    def __init__(self, world_x: float, world_y: float, vehicle_type: str = 'car'):
        """
        Initialize a vehicle.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
            vehicle_type (str): Type of vehicle (car, truck, van)
        """
        self.world_x = world_x
        self.world_y = world_y
        self.vehicle_type = vehicle_type

        # Size based on vehicle type
        if vehicle_type == 'truck':
            self.width = 48
            self.height = 24
        elif vehicle_type == 'van':
            self.width = 40
            self.height = 22
        else:  # car
            self.width = 32
            self.height = 20

        # Deconstruction
        self.legal_to_deconstruct = False  # Always illegal
        self.deconstruction_time = 120.0  # 2 minutes (longer than houses)
        self.noise_level = 8  # Very noisy (0-10 scale)
        self.being_deconstructed = False
        self.deconstruction_progress = 0.0  # 0.0-1.0

        # Materials contained (more metal than buildings)
        self.materials: Dict[str, float] = {
            'metal': 150.0 if vehicle_type == 'truck' else 100.0,
            'plastic': 30.0,
            'rubber': 25.0,
            'glass': 15.0,
            'electronic': 10.0,
        }

        # Visual
        self._generate_visuals()

        # ID for tracking
        self.id = id(self)

    def _generate_visuals(self):
        """Generate visual variation for this vehicle."""
        # Use position as seed for reproducibility
        rng = random.Random(int(self.world_x * 1000 + self.world_y))

        # Vehicle colors
        car_colors = [
            (180, 50, 50),    # Red
            (50, 50, 180),    # Blue
            (50, 150, 50),    # Green
            (180, 180, 50),   # Yellow
            (150, 150, 150),  # Silver
            (80, 80, 80),     # Dark gray
            (200, 200, 200),  # White
            (100, 50, 50),    # Dark red
        ]

        self.body_color = rng.choice(car_colors)
        self.window_color = (100, 150, 200)
        self.wheel_color = (40, 40, 40)
        self.outline_color = tuple(max(0, c - 40) for c in self.body_color)

    def start_deconstruction(self) -> bool:
        """
        Start deconstructing this vehicle.

        Returns:
            bool: True if deconstruction started
        """
        if self.being_deconstructed:
            return False

        self.being_deconstructed = True
        self.deconstruction_progress = 0.0
        return True

    def update_deconstruction(self, dt: float) -> bool:
        """
        Update deconstruction progress.

        Args:
            dt (float): Delta time in seconds

        Returns:
            bool: True if deconstruction is complete
        """
        if not self.being_deconstructed:
            return False

        if self.deconstruction_time > 0:
            self.deconstruction_progress += dt / self.deconstruction_time
            self.deconstruction_progress = min(1.0, self.deconstruction_progress)

        return self.deconstruction_progress >= 1.0

    def get_materials(self) -> Dict[str, float]:
        """Get materials from this vehicle."""
        return self.materials.copy()

    def render(self, screen: pygame.Surface, camera):
        """
        Render the vehicle with deconstruction states.

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
        if (screen_x + width_px < 0 or screen_x > screen.get_width() or
            screen_y + height_px < 0 or screen_y > screen.get_height()):
            return

        # Color fades as deconstruction progresses
        body_color = self.body_color
        if self.being_deconstructed:
            fade = 1.0 - (self.deconstruction_progress * 0.6)
            body_color = tuple(int(c * fade) for c in body_color)

        # Draw main vehicle body
        body_rect = pygame.Rect(screen_x, screen_y, width_px, height_px)
        pygame.draw.rect(screen, body_color, body_rect)
        pygame.draw.rect(screen, self.outline_color, body_rect, 2)

        # Draw deconstruction damage
        if self.being_deconstructed:
            self._render_deconstruction_damage(screen, screen_x, screen_y, width_px, height_px)
        else:
            # Draw normal vehicle details when not being deconstructed
            self._render_vehicle_details(screen, screen_x, screen_y, width_px, height_px)

        # Show deconstruction progress bar
        if self.being_deconstructed:
            bar_width = width_px - 4
            bar_height = 4
            bar_x = screen_x + 2
            bar_y = screen_y + 2

            # Background
            pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            # Progress
            progress_width = int(bar_width * self.deconstruction_progress)
            pygame.draw.rect(screen, (255, 200, 0), (bar_x, bar_y, progress_width, bar_height))

    def _render_vehicle_details(self, screen, base_x, base_y, width, height):
        """Render normal vehicle details (windows, wheels)."""
        # Windows
        window_width = int(width * 0.3)
        window_height = int(height * 0.5)
        window_y = base_y + int(height * 0.15)

        # Front window
        front_window_x = base_x + width - window_width - 4
        pygame.draw.rect(screen, self.window_color, (front_window_x, window_y, window_width, window_height))
        pygame.draw.rect(screen, (40, 40, 40), (front_window_x, window_y, window_width, window_height), 1)

        # Rear window
        rear_window_x = base_x + 4
        pygame.draw.rect(screen, self.window_color, (rear_window_x, window_y, window_width, window_height))
        pygame.draw.rect(screen, (40, 40, 40), (rear_window_x, window_y, window_width, window_height), 1)

        # Wheels
        wheel_radius = max(3, int(height * 0.3))
        wheel_y = base_y + height - wheel_radius

        # Front wheel
        front_wheel_x = base_x + width - int(width * 0.2)
        pygame.draw.circle(screen, self.wheel_color, (front_wheel_x, wheel_y), wheel_radius)
        pygame.draw.circle(screen, (80, 80, 80), (front_wheel_x, wheel_y), wheel_radius // 2)

        # Rear wheel
        rear_wheel_x = base_x + int(width * 0.2)
        pygame.draw.circle(screen, self.wheel_color, (rear_wheel_x, wheel_y), wheel_radius)
        pygame.draw.circle(screen, (80, 80, 80), (rear_wheel_x, wheel_y), wheel_radius // 2)

    def _render_deconstruction_damage(self, screen, base_x, base_y, width, height):
        """Render progressive deconstruction damage."""
        import random

        progress = self.deconstruction_progress
        damage_seed = int(self.world_x * 1000 + self.world_y)
        rng = random.Random(damage_seed)

        # Stage 1 (0-25%): Broken windows
        if progress > 0.0:
            window_width = int(width * 0.3)
            window_height = int(height * 0.5)
            window_y = base_y + int(height * 0.15)

            # Break windows progressively
            if rng.random() < (progress / 0.25):
                # Front window broken
                front_window_x = base_x + width - window_width - 4
                pygame.draw.rect(screen, (20, 20, 20), (front_window_x, window_y, window_width, window_height))
                pygame.draw.line(screen, (40, 40, 40), (front_window_x, window_y),
                               (front_window_x + window_width, window_y + window_height), 1)

            if rng.random() < (progress / 0.25):
                # Rear window broken
                rear_window_x = base_x + 4
                pygame.draw.rect(screen, (20, 20, 20), (rear_window_x, window_y, window_width, window_height))
                pygame.draw.line(screen, (40, 40, 40), (rear_window_x, window_y),
                               (rear_window_x + window_width, window_y + window_height), 1)

        # Stage 2 (25-50%): Dents and damage
        if progress > 0.25:
            num_dents = int((progress - 0.25) / 0.25 * 4)
            for i in range(num_dents):
                dent_x = base_x + rng.randint(int(width * 0.1), int(width * 0.9))
                dent_y = base_y + rng.randint(int(height * 0.3), int(height * 0.7))
                dent_size = rng.randint(3, 6)
                dent_color = tuple(max(0, int(c * 0.6)) for c in self.body_color)
                pygame.draw.circle(screen, dent_color, (dent_x, dent_y), dent_size)

        # Stage 3 (50-75%): Missing parts (doors, hood)
        if progress > 0.5:
            # Missing door sections (show as dark rectangles)
            door_width = int(width * 0.2)
            door_height = int(height * 0.6)
            door_y = base_y + int(height * 0.2)

            if progress > 0.55:
                # Left door missing
                door_x = base_x + int(width * 0.3)
                pygame.draw.rect(screen, (40, 40, 40), (door_x, door_y, door_width, door_height))

            if progress > 0.65:
                # Right door missing
                door_x = base_x + int(width * 0.5)
                pygame.draw.rect(screen, (40, 40, 40), (door_x, door_y, door_width, door_height))

        # Stage 4 (75-100%): Just frame and wheels
        if progress > 0.75:
            # Draw frame outline only
            frame_color = (60, 60, 60)
            frame_thickness = 2

            # Horizontal frame lines
            pygame.draw.line(screen, frame_color, (base_x, base_y + height // 3),
                           (base_x + width, base_y + height // 3), frame_thickness)
            pygame.draw.line(screen, frame_color, (base_x, base_y + height * 2 // 3),
                           (base_x + width, base_y + height * 2 // 3), frame_thickness)

            # Wheels still visible (but damaged)
            wheel_radius = max(3, int(height * 0.3))
            wheel_y = base_y + height - wheel_radius

            front_wheel_x = base_x + width - int(width * 0.2)
            rear_wheel_x = base_x + int(width * 0.2)

            pygame.draw.circle(screen, self.wheel_color, (front_wheel_x, wheel_y), wheel_radius)
            pygame.draw.circle(screen, self.wheel_color, (rear_wheel_x, wheel_y), wheel_radius)

    def __repr__(self):
        """String representation for debugging."""
        return f"Vehicle({self.vehicle_type}, pos=({self.world_x:.0f}, {self.world_y:.0f}))"
