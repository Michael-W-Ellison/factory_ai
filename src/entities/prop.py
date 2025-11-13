"""
Props - Small decorative objects that add visual detail to the city.

Includes:
- Benches (in parks and near buildings)
- Light poles (along roads)
- Trash cans (near buildings and parks)
- Bicycles (near houses and commercial buildings)
"""

import pygame
import random
from typing import Optional


class PropType:
    """Prop type enumeration."""
    BENCH = 0
    LIGHT_POLE = 1
    TRASH_CAN = 2
    BICYCLE = 3


class Prop:
    """
    Base class for city props (small decorative objects).

    Attributes:
        world_x (float): World X position
        world_y (float): World Y position
        prop_type (int): Type of prop (see PropType)
        rotation (int): Rotation angle (0, 90, 180, 270)
        width (int): Width in pixels
        height (int): Height in pixels
    """

    def __init__(self, world_x: float, world_y: float, prop_type: int, rotation: int = 0):
        """
        Initialize a prop.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
            prop_type (int): Type of prop
            rotation (int): Rotation angle (0, 90, 180, 270)
        """
        self.world_x = world_x
        self.world_y = world_y
        self.prop_type = prop_type
        self.rotation = rotation

        # Default size (will be overridden by subclasses)
        self.width = 10
        self.height = 10

        # ID for tracking
        self.id = id(self)

    def render(self, screen: pygame.Surface, camera):
        """
        Render the prop.

        Args:
            screen: Pygame surface
            camera: Camera for world-to-screen transformation
        """
        # Override in subclasses
        pass

    def __repr__(self):
        """String representation for debugging."""
        return f"Prop(type={self.prop_type}, pos=({self.world_x:.0f}, {self.world_y:.0f}))"


class Bench(Prop):
    """
    Park bench prop.

    Placed in parks and near buildings.
    """

    def __init__(self, world_x: float, world_y: float, rotation: int = 0):
        """
        Initialize a bench.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
            rotation (int): Rotation angle
        """
        super().__init__(world_x, world_y, PropType.BENCH, rotation)

        self.width = 16
        self.height = 8

        # Colors
        self.bench_color = (100, 70, 40)  # Brown
        self.leg_color = (60, 40, 20)  # Dark brown

    def render(self, screen: pygame.Surface, camera):
        """Render the bench."""
        # Calculate screen position
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)

        # Apply camera zoom
        width_px = int(self.width * camera.zoom)
        height_px = int(self.height * camera.zoom)

        # Don't render if off screen
        if (screen_x + width_px < 0 or screen_x - width_px > screen.get_width() or
            screen_y + height_px < 0 or screen_y - height_px > screen.get_height()):
            return

        # Create temp surface for rotation
        temp_size = int(max(width_px, height_px) * 1.5)
        temp_surface = pygame.Surface((temp_size, temp_size), pygame.SRCALPHA)

        # Center position on temp surface
        temp_x = temp_size // 2 - width_px // 2
        temp_y = temp_size // 2 - height_px // 2

        # Draw bench seat
        seat_rect = pygame.Rect(temp_x, temp_y, width_px, int(height_px * 0.4))
        pygame.draw.rect(temp_surface, self.bench_color, seat_rect)

        # Draw bench back
        back_rect = pygame.Rect(temp_x, temp_y, int(width_px * 0.2), height_px)
        pygame.draw.rect(temp_surface, self.bench_color, back_rect)

        # Draw legs
        leg_width = max(1, int(width_px * 0.1))
        leg_height = int(height_px * 0.6)

        # Left leg
        left_leg = pygame.Rect(temp_x + 2, temp_y + int(height_px * 0.4), leg_width, leg_height)
        pygame.draw.rect(temp_surface, self.leg_color, left_leg)

        # Right leg
        right_leg = pygame.Rect(temp_x + width_px - leg_width - 2, temp_y + int(height_px * 0.4), leg_width, leg_height)
        pygame.draw.rect(temp_surface, self.leg_color, right_leg)

        # Rotate and blit
        if self.rotation != 0:
            rotated_surface = pygame.transform.rotate(temp_surface, -self.rotation)
            rotated_rect = rotated_surface.get_rect(center=(screen_x, screen_y))
            screen.blit(rotated_surface, rotated_rect.topleft)
        else:
            temp_rect = temp_surface.get_rect(center=(screen_x, screen_y))
            screen.blit(temp_surface, temp_rect.topleft)


class LightPole(Prop):
    """
    Street light pole.

    Placed along roads for lighting (visual glow at night).
    """

    def __init__(self, world_x: float, world_y: float):
        """
        Initialize a light pole.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
        """
        super().__init__(world_x, world_y, PropType.LIGHT_POLE, rotation=0)

        self.width = 4
        self.height = 20

        # Colors
        self.pole_color = (80, 80, 80)  # Gray
        self.light_color = (255, 255, 200)  # Warm white
        self.glow_color = (255, 255, 150, 100)  # Yellowish glow (with alpha)

        # Light state
        self.is_on = False  # Will be turned on at night

    def render(self, screen: pygame.Surface, camera):
        """Render the light pole."""
        # Calculate screen position
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)

        # Apply camera zoom
        width_px = max(2, int(self.width * camera.zoom))
        height_px = int(self.height * camera.zoom)

        # Don't render if off screen
        if (screen_x + width_px < 0 or screen_x - width_px > screen.get_width() or
            screen_y + height_px < 0 or screen_y - height_px > screen.get_height()):
            return

        # Draw glow if light is on (night time)
        if self.is_on and camera.zoom >= 0.5:
            glow_radius = int(15 * camera.zoom)
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, self.glow_color, (glow_radius, glow_radius), glow_radius)
            glow_rect = glow_surface.get_rect(center=(screen_x, screen_y - height_px // 2))
            screen.blit(glow_surface, glow_rect.topleft)

        # Draw pole
        pole_rect = pygame.Rect(screen_x - width_px // 2, screen_y - height_px // 2,
                               width_px, height_px)
        pygame.draw.rect(screen, self.pole_color, pole_rect)

        # Draw light fixture at top
        if height_px > 10:
            fixture_size = max(3, int(6 * camera.zoom))
            fixture_rect = pygame.Rect(screen_x - fixture_size // 2,
                                      screen_y - height_px // 2 - fixture_size,
                                      fixture_size, fixture_size)
            light_color = self.light_color if self.is_on else (150, 150, 150)
            pygame.draw.rect(screen, light_color, fixture_rect)


class TrashCan(Prop):
    """
    Trash can prop.

    Placed near buildings and parks.
    """

    def __init__(self, world_x: float, world_y: float):
        """
        Initialize a trash can.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
        """
        super().__init__(world_x, world_y, PropType.TRASH_CAN, rotation=0)

        self.width = 8
        self.height = 10

        # Colors
        self.can_color = (60, 120, 60)  # Green
        self.lid_color = (50, 100, 50)  # Darker green

    def render(self, screen: pygame.Surface, camera):
        """Render the trash can."""
        # Calculate screen position
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)

        # Apply camera zoom
        width_px = max(4, int(self.width * camera.zoom))
        height_px = max(5, int(self.height * camera.zoom))

        # Don't render if off screen
        if (screen_x + width_px < 0 or screen_x - width_px > screen.get_width() or
            screen_y + height_px < 0 or screen_y - height_px > screen.get_height()):
            return

        # Draw can body (trapezoid shape)
        can_points = [
            (screen_x - width_px // 2, screen_y + height_px // 2),  # Bottom left
            (screen_x + width_px // 2, screen_y + height_px // 2),  # Bottom right
            (screen_x + int(width_px * 0.4), screen_y - height_px // 2),  # Top right
            (screen_x - int(width_px * 0.4), screen_y - height_px // 2),  # Top left
        ]
        pygame.draw.polygon(screen, self.can_color, can_points)
        pygame.draw.polygon(screen, (40, 80, 40), can_points, 1)  # Outline

        # Draw lid
        lid_width = int(width_px * 1.1)
        lid_height = max(2, int(height_px * 0.15))
        lid_rect = pygame.Rect(screen_x - lid_width // 2,
                               screen_y - height_px // 2 - lid_height,
                               lid_width, lid_height)
        pygame.draw.rect(screen, self.lid_color, lid_rect)


class Bicycle(Prop):
    """
    Bicycle prop.

    Placed near houses and commercial buildings.
    """

    def __init__(self, world_x: float, world_y: float, rotation: int = 0):
        """
        Initialize a bicycle.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
            rotation (int): Rotation angle
        """
        super().__init__(world_x, world_y, PropType.BICYCLE, rotation)

        self.width = 16
        self.height = 10

        # Random color
        colors = [
            (180, 50, 50),    # Red
            (50, 50, 180),    # Blue
            (50, 150, 50),    # Green
            (150, 150, 150),  # Silver
            (200, 200, 50),   # Yellow
        ]
        self.frame_color = random.choice(colors)
        self.wheel_color = (40, 40, 40)  # Black wheels

    def render(self, screen: pygame.Surface, camera):
        """Render the bicycle."""
        # Calculate screen position
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)

        # Apply camera zoom
        width_px = int(self.width * camera.zoom)
        height_px = int(self.height * camera.zoom)

        # Don't render if off screen or too small
        if (screen_x + width_px < 0 or screen_x - width_px > screen.get_width() or
            screen_y + height_px < 0 or screen_y - height_px > screen.get_height()):
            return

        if width_px < 8:
            # Too small to render details, just draw a simple rectangle
            rect = pygame.Rect(screen_x - width_px // 2, screen_y - height_px // 2,
                             width_px, height_px)
            pygame.draw.rect(screen, self.frame_color, rect)
            return

        # Create temp surface for rotation
        temp_size = int(max(width_px, height_px) * 1.5)
        temp_surface = pygame.Surface((temp_size, temp_size), pygame.SRCALPHA)

        # Center position on temp surface
        temp_x = temp_size // 2 - width_px // 2
        temp_y = temp_size // 2 - height_px // 2

        # Draw wheels (two circles)
        wheel_radius = max(2, int(height_px * 0.4))
        wheel_y = temp_y + height_px // 2

        # Front wheel
        front_wheel_x = temp_x + width_px - wheel_radius
        pygame.draw.circle(temp_surface, self.wheel_color, (front_wheel_x, wheel_y), wheel_radius)
        pygame.draw.circle(temp_surface, (100, 100, 100), (front_wheel_x, wheel_y), wheel_radius // 2)

        # Rear wheel
        rear_wheel_x = temp_x + wheel_radius
        pygame.draw.circle(temp_surface, self.wheel_color, (rear_wheel_x, wheel_y), wheel_radius)
        pygame.draw.circle(temp_surface, (100, 100, 100), (rear_wheel_x, wheel_y), wheel_radius // 2)

        # Draw frame (simplified)
        frame_thickness = max(1, int(2 * camera.zoom))

        # Top tube (horizontal)
        pygame.draw.line(temp_surface, self.frame_color,
                        (rear_wheel_x, temp_y + int(height_px * 0.3)),
                        (front_wheel_x, temp_y + int(height_px * 0.3)),
                        frame_thickness)

        # Seat tube (diagonal)
        pygame.draw.line(temp_surface, self.frame_color,
                        (rear_wheel_x, wheel_y),
                        (rear_wheel_x, temp_y),
                        frame_thickness)

        # Down tube (diagonal)
        pygame.draw.line(temp_surface, self.frame_color,
                        (front_wheel_x, wheel_y),
                        (rear_wheel_x, temp_y + int(height_px * 0.3)),
                        frame_thickness)

        # Rotate and blit
        if self.rotation != 0:
            rotated_surface = pygame.transform.rotate(temp_surface, -self.rotation)
            rotated_rect = rotated_surface.get_rect(center=(screen_x, screen_y))
            screen.blit(rotated_surface, rotated_rect.topleft)
        else:
            temp_rect = temp_surface.get_rect(center=(screen_x, screen_y))
            screen.blit(temp_surface, temp_rect.topleft)
