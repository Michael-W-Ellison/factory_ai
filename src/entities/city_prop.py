"""
CityProp - Environmental objects in the city (benches, light poles, etc.).

These are decorative/functional objects that add detail to the city.
Some can be deconstructed for materials, others cannot.
"""

import pygame
import random
from typing import Dict, Optional


class CityProp:
    """
    Base class for city props (benches, light poles, trash cans, etc.).

    Props are smaller than buildings and add environmental detail.
    """

    def __init__(self, world_x: float, world_y: float, prop_type: str, width: int = 1, height: int = 1):
        """
        Initialize a city prop.

        Args:
            world_x (float): World X position in pixels
            world_y (float): World Y position in pixels
            prop_type (str): Type of prop
            width (int): Width in pixels
            height (int): Height in pixels
        """
        self.world_x = world_x
        self.world_y = world_y
        self.prop_type = prop_type
        self.width = width
        self.height = height

        # Deconstruction
        self.legal_to_deconstruct = False
        self.deconstruction_time = 0.0
        self.noise_level = 0
        self.being_deconstructed = False
        self.deconstruction_progress = 0.0

        # Materials
        self.materials: Dict[str, float] = {}

        # Visual
        self.color = (100, 100, 100)
        self.outline_color = (80, 80, 80)
        self.name = "City Prop"

        # ID for tracking
        self.id = id(self)

    def start_deconstruction(self) -> bool:
        """
        Start deconstructing this prop.

        Returns:
            bool: True if deconstruction started
        """
        if self.being_deconstructed or not self.legal_to_deconstruct:
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
            bool: True if deconstruction complete
        """
        if not self.being_deconstructed or self.deconstruction_time <= 0:
            return False

        self.deconstruction_progress += dt / self.deconstruction_time
        return self.deconstruction_progress >= 1.0

    def get_materials(self) -> Dict[str, float]:
        """Get materials from this prop."""
        return self.materials.copy()

    def render(self, screen: pygame.Surface, camera):
        """
        Render the prop.

        Args:
            screen: Pygame surface
            camera: Camera for world-to-screen transformation
        """
        # Calculate screen position
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)

        # Apply camera zoom
        width_px = int(self.width * camera.zoom)
        height_px = int(self.height * camera.zoom)

        # Don't render if off screen or too small
        if (width_px < 1 or height_px < 1 or
            screen_x + width_px < 0 or screen_x > screen.get_width() or
            screen_y + height_px < 0 or screen_y > screen.get_height()):
            return

        # Simple rectangle rendering (override in subclasses for custom rendering)
        color = self.color
        if self.being_deconstructed:
            fade = 1.0 - (self.deconstruction_progress * 0.5)
            color = tuple(int(c * fade) for c in color)

        rect = pygame.Rect(screen_x, screen_y, width_px, height_px)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, self.outline_color, rect, 1)


class Bench(CityProp):
    """Park bench - decorative prop."""

    def __init__(self, world_x: float, world_y: float):
        """
        Initialize a bench.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
        """
        super().__init__(world_x, world_y, 'bench', width=24, height=12)

        self.name = "Bench"
        self.legal_to_deconstruct = True  # Can scrap for materials
        self.deconstruction_time = 15.0  # 15 seconds
        self.noise_level = 3
        self.color = (120, 80, 60)  # Brown wood
        self.outline_color = (80, 40, 20)

        # Small amount of materials
        self.materials = {
            'wood': 15.0,
            'metal': 5.0,
        }

    def render(self, screen: pygame.Surface, camera):
        """Render bench with simple visual."""
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)
        width_px = int(self.width * camera.zoom)
        height_px = int(self.height * camera.zoom)

        if width_px < 1 or height_px < 1:
            return

        color = self.color
        if self.being_deconstructed:
            fade = 1.0 - (self.deconstruction_progress * 0.5)
            color = tuple(int(c * fade) for c in color)

        # Seat
        seat_rect = pygame.Rect(screen_x, screen_y, width_px, height_px // 2)
        pygame.draw.rect(screen, color, seat_rect)
        pygame.draw.rect(screen, self.outline_color, seat_rect, 1)

        # Backrest
        back_rect = pygame.Rect(screen_x + width_px // 4, screen_y - height_px // 2, width_px // 2, height_px // 2)
        pygame.draw.rect(screen, color, back_rect)
        pygame.draw.rect(screen, self.outline_color, back_rect, 1)


class LightPole(CityProp):
    """Street light pole."""

    def __init__(self, world_x: float, world_y: float):
        """
        Initialize a light pole.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
        """
        super().__init__(world_x, world_y, 'light_pole', width=8, height=32)

        self.name = "Light Pole"
        self.legal_to_deconstruct = False  # Public property
        self.deconstruction_time = 30.0
        self.noise_level = 5
        self.color = (180, 180, 180)  # Gray metal
        self.outline_color = (120, 120, 120)

        # Materials (if illegally deconstructed)
        self.materials = {
            'metal': 25.0,
            'electronic': 5.0,
        }

    def render(self, screen: pygame.Surface, camera):
        """Render light pole with lamp."""
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)
        width_px = max(1, int(self.width * camera.zoom))
        height_px = max(2, int(self.height * camera.zoom))

        if height_px < 2:
            return

        color = self.color
        if self.being_deconstructed:
            fade = 1.0 - (self.deconstruction_progress * 0.5)
            color = tuple(int(c * fade) for c in color)

        # Pole
        pole_rect = pygame.Rect(screen_x + width_px // 3, screen_y, width_px // 3, height_px)
        pygame.draw.rect(screen, color, pole_rect)

        # Lamp
        lamp_size = max(2, width_px)
        lamp_rect = pygame.Rect(screen_x, screen_y - lamp_size // 2, lamp_size, lamp_size)
        pygame.draw.rect(screen, (255, 255, 200), lamp_rect)  # Yellow light
        pygame.draw.rect(screen, self.outline_color, lamp_rect, 1)


class TrashCan(CityProp):
    """Trash can - can contain random materials."""

    def __init__(self, world_x: float, world_y: float):
        """
        Initialize a trash can.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
        """
        super().__init__(world_x, world_y, 'trash_can', width=12, height=16)

        self.name = "Trash Can"
        self.legal_to_deconstruct = True  # Can scavenge
        self.deconstruction_time = 5.0  # Quick to open
        self.noise_level = 2
        self.color = (60, 100, 60)  # Green/gray
        self.outline_color = (40, 70, 40)

        # Random trash materials
        rng = random.Random(int(world_x * 1000 + world_y))
        self.materials = {
            'plastic': rng.uniform(1.0, 5.0),
            'paper': rng.uniform(2.0, 8.0),
            'metal': rng.uniform(0.5, 3.0),
            'glass': rng.uniform(0.5, 2.0),
        }

    def render(self, screen: pygame.Surface, camera):
        """Render trash can."""
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)
        width_px = max(1, int(self.width * camera.zoom))
        height_px = max(1, int(self.height * camera.zoom))

        if width_px < 1 or height_px < 1:
            return

        color = self.color
        if self.being_deconstructed:
            fade = 1.0 - (self.deconstruction_progress * 0.5)
            color = tuple(int(c * fade) for c in color)

        # Can body
        can_rect = pygame.Rect(screen_x, screen_y, width_px, height_px)
        pygame.draw.rect(screen, color, can_rect)
        pygame.draw.rect(screen, self.outline_color, can_rect, 1)

        # Lid
        lid_rect = pygame.Rect(screen_x - 1, screen_y - 2, width_px + 2, 3)
        pygame.draw.rect(screen, color, lid_rect)


class Bicycle(CityProp):
    """Bicycle - can be deconstructed for materials."""

    def __init__(self, world_x: float, world_y: float):
        """
        Initialize a bicycle.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
        """
        super().__init__(world_x, world_y, 'bicycle', width=20, height=12)

        self.name = "Bicycle"
        self.legal_to_deconstruct = False  # Stealing
        self.deconstruction_time = 20.0
        self.noise_level = 4
        self.color = random.choice([
            (180, 50, 50),   # Red
            (50, 50, 180),   # Blue
            (50, 180, 50),   # Green
            (180, 180, 50),  # Yellow
            (150, 150, 150), # Silver
        ])
        self.outline_color = (40, 40, 40)

        # Materials
        self.materials = {
            'metal': 12.0,
            'rubber': 3.0,
            'plastic': 2.0,
        }

        # Facing direction (for rendering)
        self.facing_angle = random.choice([0, 90, 180, 270])

    def render(self, screen: pygame.Surface, camera):
        """Render bicycle with simple wheels and frame."""
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)
        width_px = max(1, int(self.width * camera.zoom))
        height_px = max(1, int(self.height * camera.zoom))

        if width_px < 2 or height_px < 2:
            return

        color = self.color
        if self.being_deconstructed:
            fade = 1.0 - (self.deconstruction_progress * 0.5)
            color = tuple(int(c * fade) for c in color)

        # Frame (simplified)
        frame_rect = pygame.Rect(screen_x, screen_y, width_px, height_px // 2)
        pygame.draw.rect(screen, color, frame_rect)

        # Wheels
        wheel_radius = max(1, height_px // 3)
        wheel_y = screen_y + height_px - wheel_radius

        # Front wheel
        pygame.draw.circle(screen, (40, 40, 40), (screen_x + wheel_radius, wheel_y), wheel_radius)
        pygame.draw.circle(screen, (80, 80, 80), (screen_x + wheel_radius, wheel_y), wheel_radius // 2)

        # Rear wheel
        pygame.draw.circle(screen, (40, 40, 40), (screen_x + width_px - wheel_radius, wheel_y), wheel_radius)
        pygame.draw.circle(screen, (80, 80, 80), (screen_x + width_px - wheel_radius, wheel_y), wheel_radius // 2)
