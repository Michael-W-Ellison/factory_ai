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
    TREE = 4
    FLOWER_BED = 5
    FIRE_HYDRANT = 6
    MAILBOX = 7
    PARKING_METER = 8
    NEWSPAPER_STAND = 9


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


class Tree(Prop):
    """
    Tree prop.

    Placed in parks and near roads for decoration.
    Provides visual variety with different sizes and shades.
    """

    def __init__(self, world_x: float, world_y: float, size_variation: float = 1.0):
        """
        Initialize a tree.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
            size_variation (float): Size multiplier (0.8-1.2)
        """
        super().__init__(world_x, world_y, PropType.TREE, rotation=0)

        # Size variation
        self.size_variation = max(0.8, min(1.2, size_variation))
        self.width = int(20 * self.size_variation)
        self.height = int(32 * self.size_variation)

        # Random tree type
        self.tree_type = random.choice(['oak', 'pine', 'maple'])

        # Colors based on tree type
        if self.tree_type == 'oak':
            self.trunk_color = (100, 70, 40)
            self.leaf_color = (60, 140, 60)
        elif self.tree_type == 'pine':
            self.trunk_color = (80, 60, 40)
            self.leaf_color = (40, 100, 40)
        else:  # maple
            self.trunk_color = (90, 65, 35)
            self.leaf_color = (70, 150, 50)

        # Seasonal variation (will be set by manager)
        self.season = 'summer'  # spring, summer, autumn, winter

    def render(self, screen: pygame.Surface, camera):
        """Render the tree."""
        # Calculate screen position
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)

        # Apply camera zoom
        width_px = int(self.width * camera.zoom)
        height_px = int(self.height * camera.zoom)

        # Don't render if off screen
        if (screen_x + width_px < 0 or screen_x - width_px > screen.get_width() or
            screen_y + height_px < 0 or screen_y - height_px > screen.get_height()):
            return

        # Adjust colors based on season
        leaf_color = self.leaf_color
        if self.season == 'autumn':
            # Orange/red leaves
            leaf_color = (200, 100, 40)
        elif self.season == 'winter':
            # No leaves, show bare branches (gray-brown)
            leaf_color = (120, 100, 80)
        elif self.season == 'spring':
            # Light green
            leaf_color = tuple(min(255, c + 30) for c in self.leaf_color)

        # Draw trunk
        trunk_width = max(2, int(width_px * 0.2))
        trunk_height = int(height_px * 0.4)
        trunk_rect = pygame.Rect(screen_x - trunk_width // 2,
                                 screen_y + height_px // 2 - trunk_height,
                                 trunk_width, trunk_height)
        pygame.draw.rect(screen, self.trunk_color, trunk_rect)

        # Draw canopy
        if self.tree_type == 'pine':
            # Triangular canopy (pine tree shape)
            canopy_points = [
                (screen_x, screen_y - height_px // 2),  # Top
                (screen_x - width_px // 2, screen_y + height_px // 2 - trunk_height),  # Bottom left
                (screen_x + width_px // 2, screen_y + height_px // 2 - trunk_height),  # Bottom right
            ]
            pygame.draw.polygon(screen, leaf_color, canopy_points)
            if width_px > 10:
                pygame.draw.polygon(screen, tuple(max(0, c - 40) for c in leaf_color), canopy_points, 1)
        else:
            # Circular canopy (oak/maple)
            canopy_radius = width_px // 2
            canopy_y = screen_y - height_px // 2 + canopy_radius
            pygame.draw.circle(screen, leaf_color, (screen_x, canopy_y), canopy_radius)
            # Darker outline
            if width_px > 10:
                pygame.draw.circle(screen, tuple(max(0, c - 40) for c in leaf_color), (screen_x, canopy_y), canopy_radius, 1)


class FlowerBed(Prop):
    """
    Flower bed prop.

    Colorful flowers in a small garden bed. Placed in parks and near buildings.
    """

    def __init__(self, world_x: float, world_y: float):
        """
        Initialize a flower bed.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
        """
        super().__init__(world_x, world_y, PropType.FLOWER_BED, rotation=0)

        self.width = 16
        self.height = 12

        # Colors
        self.soil_color = (90, 70, 50)
        # Random flower colors
        flower_color_options = [
            (255, 100, 100),  # Red
            (255, 200, 100),  # Yellow
            (200, 100, 255),  # Purple
            (255, 150, 200),  # Pink
            (100, 150, 255),  # Blue
        ]
        self.flower_color = random.choice(flower_color_options)
        self.leaf_color = (80, 150, 80)

    def render(self, screen: pygame.Surface, camera):
        """Render the flower bed."""
        # Calculate screen position
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)

        # Apply camera zoom
        width_px = int(self.width * camera.zoom)
        height_px = int(self.height * camera.zoom)

        # Don't render if off screen or too small
        if (screen_x + width_px < 0 or screen_x - width_px > screen.get_width() or
            screen_y + height_px < 0 or screen_y - height_px > screen.get_height()):
            return

        if width_px < 6:
            # Too small, just draw colored rectangle
            rect = pygame.Rect(screen_x - width_px // 2, screen_y - height_px // 2,
                             width_px, height_px)
            pygame.draw.rect(screen, self.flower_color, rect)
            return

        # Draw soil bed
        bed_rect = pygame.Rect(screen_x - width_px // 2, screen_y - height_px // 2,
                               width_px, height_px)
        pygame.draw.rect(screen, self.soil_color, bed_rect)
        pygame.draw.rect(screen, (70, 55, 40), bed_rect, 1)

        # Draw flowers (small circles)
        if width_px >= 8:
            flower_size = max(2, int(3 * camera.zoom))
            num_flowers = min(6, max(3, width_px // 4))

            for i in range(num_flowers):
                x_offset = (i - num_flowers // 2) * int(width_px / num_flowers)
                y_offset = random.randint(-2, 2)
                flower_x = screen_x + x_offset
                flower_y = screen_y + y_offset

                # Draw leaves first
                pygame.draw.circle(screen, self.leaf_color, (flower_x, flower_y + 1), flower_size - 1)
                # Draw flower on top
                pygame.draw.circle(screen, self.flower_color, (flower_x, flower_y), flower_size)


class FireHydrant(Prop):
    """
    Fire hydrant prop.

    Placed near roads and buildings for fire safety visualization.
    """

    def __init__(self, world_x: float, world_y: float):
        """
        Initialize a fire hydrant.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
        """
        super().__init__(world_x, world_y, PropType.FIRE_HYDRANT, rotation=0)

        self.width = 8
        self.height = 12

        # Colors (classic red fire hydrant)
        self.body_color = (200, 40, 40)
        self.cap_color = (180, 30, 30)
        self.valve_color = (220, 220, 220)

    def render(self, screen: pygame.Surface, camera):
        """Render the fire hydrant."""
        # Calculate screen position
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)

        # Apply camera zoom
        width_px = max(4, int(self.width * camera.zoom))
        height_px = max(6, int(self.height * camera.zoom))

        # Don't render if off screen
        if (screen_x + width_px < 0 or screen_x - width_px > screen.get_width() or
            screen_y + height_px < 0 or screen_y - height_px > screen.get_height()):
            return

        # Draw main body
        body_rect = pygame.Rect(screen_x - width_px // 2, screen_y - height_px // 2,
                               width_px, int(height_px * 0.7))
        pygame.draw.rect(screen, self.body_color, body_rect)
        pygame.draw.rect(screen, (160, 30, 30), body_rect, 1)

        # Draw top cap
        cap_width = int(width_px * 1.2)
        cap_height = max(2, int(height_px * 0.2))
        cap_rect = pygame.Rect(screen_x - cap_width // 2,
                               screen_y - height_px // 2 - cap_height,
                               cap_width, cap_height)
        pygame.draw.rect(screen, self.cap_color, cap_rect)

        # Draw side valves if large enough
        if width_px >= 6:
            valve_size = max(2, int(3 * camera.zoom))
            # Left valve
            pygame.draw.circle(screen, self.valve_color,
                             (screen_x - width_px // 2 - 1, screen_y), valve_size)
            # Right valve
            pygame.draw.circle(screen, self.valve_color,
                             (screen_x + width_px // 2 + 1, screen_y), valve_size)


class Mailbox(Prop):
    """
    Mailbox prop.

    Placed near residential buildings for mail delivery visualization.
    """

    def __init__(self, world_x: float, world_y: float):
        """
        Initialize a mailbox.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
        """
        super().__init__(world_x, world_y, PropType.MAILBOX, rotation=0)

        self.width = 8
        self.height = 14

        # Colors (blue mailbox)
        self.box_color = (50, 80, 150)
        self.post_color = (80, 80, 80)
        self.flag_color = (200, 50, 50)

        # Mailbox state
        self.flag_up = random.choice([True, False])  # Mail indicator

    def render(self, screen: pygame.Surface, camera):
        """Render the mailbox."""
        # Calculate screen position
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)

        # Apply camera zoom
        width_px = max(4, int(self.width * camera.zoom))
        height_px = max(7, int(self.height * camera.zoom))

        # Don't render if off screen
        if (screen_x + width_px < 0 or screen_x - width_px > screen.get_width() or
            screen_y + height_px < 0 or screen_y - height_px > screen.get_height()):
            return

        # Draw post
        post_width = max(2, int(width_px * 0.3))
        post_height = int(height_px * 0.6)
        post_rect = pygame.Rect(screen_x - post_width // 2,
                                screen_y + height_px // 2 - post_height,
                                post_width, post_height)
        pygame.draw.rect(screen, self.post_color, post_rect)

        # Draw mailbox body (rounded rectangle)
        box_width = width_px
        box_height = int(height_px * 0.4)
        box_y = screen_y - height_px // 2
        box_rect = pygame.Rect(screen_x - box_width // 2, box_y,
                               box_width, box_height)
        pygame.draw.rect(screen, self.box_color, box_rect)
        pygame.draw.rect(screen, (40, 60, 120), box_rect, 1)

        # Draw flag if up
        if self.flag_up and width_px >= 6:
            flag_width = max(2, int(4 * camera.zoom))
            flag_height = max(2, int(3 * camera.zoom))
            flag_rect = pygame.Rect(screen_x + box_width // 2,
                                    box_y + box_height // 3,
                                    flag_width, flag_height)
            pygame.draw.rect(screen, self.flag_color, flag_rect)


class ParkingMeter(Prop):
    """
    Parking meter prop.

    Placed along roads near commercial areas.
    """

    def __init__(self, world_x: float, world_y: float):
        """
        Initialize a parking meter.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
        """
        super().__init__(world_x, world_y, PropType.PARKING_METER, rotation=0)

        self.width = 6
        self.height = 16

        # Colors
        self.post_color = (80, 80, 80)
        self.meter_color = (200, 200, 200)
        self.screen_color = (100, 200, 100)  # Green display

    def render(self, screen: pygame.Surface, camera):
        """Render the parking meter."""
        # Calculate screen position
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)

        # Apply camera zoom
        width_px = max(3, int(self.width * camera.zoom))
        height_px = max(8, int(self.height * camera.zoom))

        # Don't render if off screen
        if (screen_x + width_px < 0 or screen_x - width_px > screen.get_width() or
            screen_y + height_px < 0 or screen_y - height_px > screen.get_height()):
            return

        # Draw post
        post_width = max(2, int(width_px * 0.4))
        post_height = int(height_px * 0.6)
        post_rect = pygame.Rect(screen_x - post_width // 2,
                                screen_y + height_px // 2 - post_height,
                                post_width, post_height)
        pygame.draw.rect(screen, self.post_color, post_rect)

        # Draw meter head
        meter_width = width_px
        meter_height = int(height_px * 0.4)
        meter_y = screen_y - height_px // 2
        meter_rect = pygame.Rect(screen_x - meter_width // 2, meter_y,
                                 meter_width, meter_height)
        pygame.draw.rect(screen, self.meter_color, meter_rect)
        pygame.draw.rect(screen, (160, 160, 160), meter_rect, 1)

        # Draw screen if large enough
        if width_px >= 5:
            screen_width = max(2, int(width_px * 0.6))
            screen_height = max(2, int(meter_height * 0.4))
            screen_rect = pygame.Rect(screen_x - screen_width // 2,
                                      meter_y + int(meter_height * 0.3),
                                      screen_width, screen_height)
            pygame.draw.rect(screen, self.screen_color, screen_rect)


class NewspaperStand(Prop):
    """
    Newspaper stand prop.

    Placed near commercial buildings and busy streets.
    """

    def __init__(self, world_x: float, world_y: float):
        """
        Initialize a newspaper stand.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
        """
        super().__init__(world_x, world_y, PropType.NEWSPAPER_STAND, rotation=0)

        self.width = 14
        self.height = 18

        # Colors
        self.stand_color = (180, 50, 50)  # Red stand
        self.roof_color = (160, 40, 40)
        self.window_color = (220, 220, 220)
        self.newspaper_color = (240, 240, 240)

    def render(self, screen: pygame.Surface, camera):
        """Render the newspaper stand."""
        # Calculate screen position
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)

        # Apply camera zoom
        width_px = int(self.width * camera.zoom)
        height_px = int(self.height * camera.zoom)

        # Don't render if off screen or too small
        if (screen_x + width_px < 0 or screen_x - width_px > screen.get_width() or
            screen_y + height_px < 0 or screen_y - height_px > screen.get_height()):
            return

        if width_px < 6:
            # Too small, just draw simple rectangle
            rect = pygame.Rect(screen_x - width_px // 2, screen_y - height_px // 2,
                             width_px, height_px)
            pygame.draw.rect(screen, self.stand_color, rect)
            return

        # Draw main body
        body_width = width_px
        body_height = int(height_px * 0.7)
        body_rect = pygame.Rect(screen_x - body_width // 2,
                                screen_y + height_px // 2 - body_height,
                                body_width, body_height)
        pygame.draw.rect(screen, self.stand_color, body_rect)
        pygame.draw.rect(screen, (140, 30, 30), body_rect, 1)

        # Draw roof
        roof_width = int(body_width * 1.1)
        roof_height = max(2, int(height_px * 0.15))
        roof_rect = pygame.Rect(screen_x - roof_width // 2,
                                screen_y - height_px // 2,
                                roof_width, roof_height)
        pygame.draw.rect(screen, self.roof_color, roof_rect)

        # Draw window/display area
        if width_px >= 10:
            window_width = int(body_width * 0.7)
            window_height = int(body_height * 0.5)
            window_rect = pygame.Rect(screen_x - window_width // 2,
                                      screen_y + height_px // 2 - body_height + int(body_height * 0.2),
                                      window_width, window_height)
            pygame.draw.rect(screen, self.window_color, window_rect)
            pygame.draw.rect(screen, (180, 180, 180), window_rect, 1)

            # Draw newspaper stack
            news_width = int(window_width * 0.6)
            news_height = max(2, int(window_height * 0.6))
            news_rect = pygame.Rect(screen_x - news_width // 2,
                                    window_rect.centery - news_height // 2,
                                    news_width, news_height)
            pygame.draw.rect(screen, self.newspaper_color, news_rect)
            # Draw text lines on newspaper
            if news_height >= 4:
                for i in range(2):
                    line_y = news_rect.top + 2 + i * 2
                    pygame.draw.line(screen, (100, 100, 100),
                                   (news_rect.left + 2, line_y),
                                   (news_rect.right - 2, line_y), 1)
