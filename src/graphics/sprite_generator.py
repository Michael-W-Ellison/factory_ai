"""
Sprite Generator - Creates procedural sprite graphics for game entities.

Generates high-quality sprites for NPCs, vehicles, robots, and other moving assets.
All sprites are created programmatically and cached for performance.
"""

import pygame
import math
from typing import Dict, List, Tuple, Optional
from enum import Enum


class Direction(Enum):
    """8-way directional sprites."""
    EAST = 0
    SOUTHEAST = 45
    SOUTH = 90
    SOUTHWEST = 135
    WEST = 180
    NORTHWEST = 225
    NORTH = 270
    NORTHEAST = 315


class SpriteType(Enum):
    """Types of sprites that can be generated."""
    NPC = "npc"
    CAR = "car"
    TRUCK = "truck"
    VAN = "van"
    BUS = "bus"
    POLICE_CAR = "police_car"
    ROBOT = "robot"
    DRONE = "drone"


class SpriteGenerator:
    """
    Generates procedural sprites for game entities.

    All sprites are cached after first generation for performance.
    Supports multiple directions and animation frames.
    """

    def __init__(self):
        """Initialize the sprite generator."""
        # Sprite cache: {(sprite_type, direction, frame, variant): Surface}
        self._cache: Dict[Tuple, pygame.Surface] = {}

        # Default sizes for each sprite type
        self.sprite_sizes = {
            SpriteType.NPC: (16, 16),
            SpriteType.CAR: (32, 20),
            SpriteType.TRUCK: (48, 24),
            SpriteType.VAN: (40, 22),
            SpriteType.BUS: (50, 24),
            SpriteType.POLICE_CAR: (32, 20),
            SpriteType.ROBOT: (20, 20),
            SpriteType.DRONE: (24, 24),
        }

    def get_sprite(self, sprite_type: SpriteType, direction: Direction = Direction.SOUTH,
                   frame: int = 0, variant: int = 0, **kwargs) -> pygame.Surface:
        """
        Get or generate a sprite.

        Args:
            sprite_type: Type of sprite to generate
            direction: Facing direction (8-way)
            frame: Animation frame number
            variant: Color/style variant number
            **kwargs: Additional parameters (colors, special flags, etc.)

        Returns:
            pygame.Surface: The generated sprite
        """
        cache_key = (sprite_type, direction, frame, variant, tuple(sorted(kwargs.items())))

        if cache_key in self._cache:
            return self._cache[cache_key]

        # Generate the sprite
        if sprite_type == SpriteType.NPC:
            sprite = self._generate_npc_sprite(direction, frame, variant, **kwargs)
        elif sprite_type in (SpriteType.CAR, SpriteType.TRUCK, SpriteType.VAN,
                            SpriteType.BUS, SpriteType.POLICE_CAR):
            sprite = self._generate_vehicle_sprite(sprite_type, direction, frame, variant, **kwargs)
        elif sprite_type == SpriteType.ROBOT:
            sprite = self._generate_robot_sprite(direction, frame, variant, **kwargs)
        elif sprite_type == SpriteType.DRONE:
            sprite = self._generate_drone_sprite(direction, frame, variant, **kwargs)
        else:
            # Fallback: simple colored square
            size = self.sprite_sizes.get(sprite_type, (16, 16))
            sprite = pygame.Surface(size, pygame.SRCALPHA)
            sprite.fill((255, 0, 255))  # Magenta for missing sprites

        # Cache and return
        self._cache[cache_key] = sprite
        return sprite

    def _generate_npc_sprite(self, direction: Direction, frame: int, variant: int,
                            clothing_color: Tuple[int, int, int] = None,
                            skin_color: Tuple[int, int, int] = (220, 180, 140)) -> pygame.Surface:
        """Generate NPC sprite with walking animation."""
        width, height = self.sprite_sizes[SpriteType.NPC]
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)

        # Default clothing colors (7 variants)
        clothing_colors = [
            (80, 100, 180),   # Blue
            (180, 80, 80),    # Red
            (80, 180, 80),    # Green
            (150, 120, 80),   # Brown
            (100, 100, 100),  # Gray
            (180, 180, 80),   # Yellow
            (120, 80, 150),   # Purple
        ]

        if clothing_color is None:
            clothing_color = clothing_colors[variant % len(clothing_colors)]

        outline_color = tuple(max(0, c - 40) for c in clothing_color)

        # Center position
        cx, cy = width // 2, height // 2

        # Animation: 0 = standing, 1 = left foot forward, 2 = right foot forward
        leg_offset = 0
        if frame == 1:
            leg_offset = 2
        elif frame == 2:
            leg_offset = -2

        # Draw based on direction
        angle_deg = direction.value

        # Simplified: draw front/back/side views
        if 45 <= angle_deg < 135:  # South (front view)
            # Legs
            pygame.draw.rect(sprite, clothing_color, (cx - 4, cy + 2, 3, 6))  # Left leg
            pygame.draw.rect(sprite, clothing_color, (cx + 1, cy + 2 - leg_offset, 3, 6))  # Right leg

            # Body
            pygame.draw.ellipse(sprite, clothing_color, (cx - 5, cy - 4, 10, 8))
            pygame.draw.ellipse(sprite, outline_color, (cx - 5, cy - 4, 10, 8), 1)

            # Head
            pygame.draw.circle(sprite, skin_color, (cx, cy - 6), 4)
            pygame.draw.circle(sprite, outline_color, (cx, cy - 6), 4, 1)

            # Eyes
            pygame.draw.circle(sprite, (50, 50, 50), (cx - 2, cy - 7), 1)
            pygame.draw.circle(sprite, (50, 50, 50), (cx + 2, cy - 7), 1)

        elif 225 <= angle_deg < 315:  # North (back view)
            # Legs
            pygame.draw.rect(sprite, clothing_color, (cx - 4, cy + 2 + leg_offset, 3, 6))  # Left leg
            pygame.draw.rect(sprite, clothing_color, (cx + 1, cy + 2, 3, 6))  # Right leg

            # Body
            pygame.draw.ellipse(sprite, clothing_color, (cx - 5, cy - 4, 10, 8))
            pygame.draw.ellipse(sprite, outline_color, (cx - 5, cy - 4, 10, 8), 1)

            # Head (back of head)
            pygame.draw.circle(sprite, skin_color, (cx, cy - 6), 4)
            pygame.draw.circle(sprite, outline_color, (cx, cy - 6), 4, 1)

        elif 135 <= angle_deg < 225:  # West (left side view)
            # Legs (one behind the other)
            pygame.draw.rect(sprite, clothing_color, (cx - 1, cy + 2 + leg_offset, 3, 6))  # Back leg
            pygame.draw.rect(sprite, clothing_color, (cx - 1, cy + 2 - leg_offset, 3, 6))  # Front leg

            # Body
            pygame.draw.ellipse(sprite, clothing_color, (cx - 4, cy - 4, 8, 8))
            pygame.draw.ellipse(sprite, outline_color, (cx - 4, cy - 4, 8, 8), 1)

            # Head
            pygame.draw.circle(sprite, skin_color, (cx - 1, cy - 6), 4)
            pygame.draw.circle(sprite, outline_color, (cx - 1, cy - 6), 4, 1)

            # Eye
            pygame.draw.circle(sprite, (50, 50, 50), (cx - 2, cy - 7), 1)

        else:  # East (right side view)
            # Legs (one behind the other)
            pygame.draw.rect(sprite, clothing_color, (cx - 1, cy + 2 - leg_offset, 3, 6))  # Back leg
            pygame.draw.rect(sprite, clothing_color, (cx - 1, cy + 2 + leg_offset, 3, 6))  # Front leg

            # Body
            pygame.draw.ellipse(sprite, clothing_color, (cx - 4, cy - 4, 8, 8))
            pygame.draw.ellipse(sprite, outline_color, (cx - 4, cy - 4, 8, 8), 1)

            # Head
            pygame.draw.circle(sprite, skin_color, (cx + 1, cy - 6), 4)
            pygame.draw.circle(sprite, outline_color, (cx + 1, cy - 6), 4, 1)

            # Eye
            pygame.draw.circle(sprite, (50, 50, 50), (cx + 2, cy - 7), 1)

        # Add shadow below
        shadow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 80), (cx - 6, cy + 7, 12, 4))
        sprite.blit(shadow_surface, (0, 0))

        return sprite

    def _generate_vehicle_sprite(self, vehicle_type: SpriteType, direction: Direction,
                                 frame: int, variant: int,
                                 body_color: Tuple[int, int, int] = None,
                                 lights_on: bool = False,
                                 braking: bool = False) -> pygame.Surface:
        """Generate vehicle sprite with proper orientation."""
        width, height = self.sprite_sizes[vehicle_type]

        # Create larger surface to accommodate rotation
        max_dim = int(math.sqrt(width**2 + height**2)) + 4
        sprite = pygame.Surface((max_dim, max_dim), pygame.SRCALPHA)

        # Center position on sprite
        cx, cy = max_dim // 2, max_dim // 2

        # Get body color for variant
        if body_color is None:
            if vehicle_type == SpriteType.POLICE_CAR:
                body_colors = [(40, 40, 40), (200, 200, 200)]  # Black or white
                body_color = body_colors[variant % 2]
            elif vehicle_type == SpriteType.BUS:
                body_colors = [(200, 150, 50), (180, 180, 50)]  # Orange/yellow
                body_color = body_colors[variant % 2]
            elif vehicle_type == SpriteType.CAR:
                body_colors = [(180, 50, 50), (50, 50, 180), (50, 150, 50),
                              (150, 150, 150), (80, 80, 80), (200, 200, 200)]
                body_color = body_colors[variant % len(body_colors)]
            elif vehicle_type == SpriteType.TRUCK:
                body_colors = [(100, 80, 60), (180, 50, 50), (50, 50, 180), (80, 80, 80)]
                body_color = body_colors[variant % len(body_colors)]
            else:  # VAN
                body_colors = [(180, 180, 50), (200, 200, 200), (50, 50, 180), (150, 150, 150)]
                body_color = body_colors[variant % len(body_colors)]

        outline_color = tuple(max(0, c - 60) for c in body_color)
        window_color = (100, 150, 200, 180)  # Light blue semi-transparent

        # Draw vehicle facing east (will be rotated)
        body_rect = pygame.Rect(cx - width//2, cy - height//2, width, height)

        # Main body
        pygame.draw.rect(sprite, body_color, body_rect, border_radius=2)
        pygame.draw.rect(sprite, outline_color, body_rect, 2, border_radius=2)

        # Windows (front and rear)
        window_width = int(width * 0.25)
        window_height = int(height * 0.6)

        # Front window
        front_window = pygame.Rect(cx + width//2 - window_width - 2,
                                   cy - window_height//2,
                                   window_width, window_height)
        pygame.draw.rect(sprite, window_color, front_window)

        # Rear window
        rear_window = pygame.Rect(cx - width//2 + 2,
                                 cy - window_height//2,
                                 window_width, window_height)
        pygame.draw.rect(sprite, window_color, rear_window)

        # Wheels
        wheel_radius = int(height * 0.3)
        wheel_color = (40, 40, 40)

        # Front wheel
        pygame.draw.circle(sprite, wheel_color,
                          (cx + width//2 - width//4, cy + height//2), wheel_radius)
        # Rear wheel
        pygame.draw.circle(sprite, wheel_color,
                          (cx - width//2 + width//4, cy + height//2), wheel_radius)

        # Headlights (when on)
        if lights_on:
            light_color = (255, 255, 200)
            light_radius = int(height * 0.2)
            pygame.draw.circle(sprite, light_color,
                              (cx + width//2, cy - height//4), light_radius)
            pygame.draw.circle(sprite, light_color,
                              (cx + width//2, cy + height//4), light_radius)

        # Brake lights (when braking)
        if braking:
            brake_color = (255, 50, 50)
            light_radius = int(height * 0.2)
            pygame.draw.circle(sprite, brake_color,
                              (cx - width//2, cy - height//4), light_radius)
            pygame.draw.circle(sprite, brake_color,
                              (cx - width//2, cy + height//4), light_radius)

        # Police car special features
        if vehicle_type == SpriteType.POLICE_CAR:
            # Light bar on top
            light_bar_rect = pygame.Rect(cx - width//4, cy - height//2 - 2, width//2, 2)
            pygame.draw.rect(sprite, (200, 0, 0) if frame % 2 == 0 else (0, 0, 200), light_bar_rect)

            # Police badge/text
            font = pygame.font.Font(None, 10)
            text = font.render("POLICE", True, (255, 255, 255))
            text_rect = text.get_rect(center=(cx, cy))
            sprite.blit(text, text_rect)

        # Bus special features
        elif vehicle_type == SpriteType.BUS:
            # Multiple windows along side
            for i in range(3):
                window_x = cx - width//2 + width//4 + i * width//4
                small_window = pygame.Rect(window_x, cy - height//3, width//6, height//2)
                pygame.draw.rect(sprite, window_color, small_window)

        # Rotate sprite to face correct direction
        angle = -direction.value  # Negative for pygame rotation
        rotated = pygame.transform.rotate(sprite, angle)

        return rotated

    def _generate_robot_sprite(self, direction: Direction, frame: int, variant: int,
                               **kwargs) -> pygame.Surface:
        """Generate robot sprite with animation."""
        width, height = self.sprite_sizes[SpriteType.ROBOT]
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)

        cx, cy = width // 2, height // 2

        # Robot colors (metallic variants)
        robot_colors = [
            (150, 150, 180),  # Silver
            (180, 160, 120),  # Gold
            (120, 120, 120),  # Dark gray
            (180, 100, 100),  # Copper
        ]
        robot_color = robot_colors[variant % len(robot_colors)]
        outline_color = tuple(max(0, c - 60) for c in robot_color)

        # Animation: bobbing up and down
        bob_offset = 1 if frame % 2 == 0 else 0

        # Main body (rounded rectangle)
        body_rect = pygame.Rect(cx - 6, cy - 5 + bob_offset, 12, 10)
        pygame.draw.rect(sprite, robot_color, body_rect, border_radius=2)
        pygame.draw.rect(sprite, outline_color, body_rect, 1, border_radius=2)

        # Head
        head_rect = pygame.Rect(cx - 4, cy - 8 + bob_offset, 8, 5)
        pygame.draw.rect(sprite, robot_color, head_rect, border_radius=1)
        pygame.draw.rect(sprite, outline_color, head_rect, 1, border_radius=1)

        # Eyes (LED style)
        eye_color = (0, 255, 255) if frame % 2 == 0 else (0, 200, 200)  # Blinking
        pygame.draw.circle(sprite, eye_color, (cx - 2, cy - 6 + bob_offset), 1)
        pygame.draw.circle(sprite, eye_color, (cx + 2, cy - 6 + bob_offset), 1)

        # Wheels/tracks
        pygame.draw.circle(sprite, (40, 40, 40), (cx - 4, cy + 6), 2)
        pygame.draw.circle(sprite, (40, 40, 40), (cx + 4, cy + 6), 2)

        # Antenna
        pygame.draw.line(sprite, outline_color, (cx, cy - 8 + bob_offset), (cx, cy - 11 + bob_offset), 1)
        pygame.draw.circle(sprite, (255, 100, 100), (cx, cy - 11 + bob_offset), 2)

        # Shadow
        shadow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 80), (cx - 8, cy + 6, 16, 4))
        sprite.blit(shadow_surface, (0, 0))

        return sprite

    def _generate_drone_sprite(self, direction: Direction, frame: int, variant: int,
                               battery_level: float = 100.0) -> pygame.Surface:
        """Generate drone sprite with rotor animation."""
        width, height = self.sprite_sizes[SpriteType.DRONE]
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)

        cx, cy = width // 2, height // 2

        # Drone body color
        body_color = (80, 80, 100)
        outline_color = (40, 40, 50)
        rotor_color = (150, 150, 150)

        # Rotor animation (rotating blades)
        rotor_angle = (frame * 45) % 360

        # Draw rotors (4 corners)
        rotor_positions = [
            (cx - 8, cy - 8),  # Top-left
            (cx + 8, cy - 8),  # Top-right
            (cx - 8, cy + 8),  # Bottom-left
            (cx + 8, cy + 8),  # Bottom-right
        ]

        for rotor_x, rotor_y in rotor_positions:
            # Rotor disk (spinning)
            for angle_offset in range(0, 360, 60):
                angle_rad = math.radians(rotor_angle + angle_offset)
                blade_len = 4
                end_x = rotor_x + int(blade_len * math.cos(angle_rad))
                end_y = rotor_y + int(blade_len * math.sin(angle_rad))
                pygame.draw.line(sprite, rotor_color, (rotor_x, rotor_y), (end_x, end_y), 1)

        # Central body
        body_rect = pygame.Rect(cx - 6, cy - 4, 12, 8)
        pygame.draw.ellipse(sprite, body_color, body_rect)
        pygame.draw.ellipse(sprite, outline_color, body_rect, 1)

        # Camera/sensor
        pygame.draw.circle(sprite, (50, 100, 150), (cx, cy + 2), 2)

        # Battery indicator
        battery_color = (0, 255, 0) if battery_level > 50 else \
                       (255, 200, 0) if battery_level > 20 else (255, 50, 50)
        battery_width = max(2, int(8 * (battery_level / 100.0)))
        pygame.draw.rect(sprite, battery_color, (cx - 4, cy - 6, battery_width, 2))

        # LED lights
        led_color = (255, 100, 100) if frame % 2 == 0 else (100, 255, 100)
        pygame.draw.circle(sprite, led_color, (cx - 4, cy - 2), 1)
        pygame.draw.circle(sprite, led_color, (cx + 4, cy - 2), 1)

        return sprite

    def clear_cache(self):
        """Clear the sprite cache to free memory."""
        self._cache.clear()

    def get_cache_info(self) -> Dict:
        """Get information about cached sprites."""
        return {
            'cached_sprites': len(self._cache),
            'memory_estimate_kb': len(self._cache) * 2  # Rough estimate
        }


# Global sprite generator instance
_sprite_generator = None

def get_sprite_generator() -> SpriteGenerator:
    """Get the global sprite generator instance."""
    global _sprite_generator
    if _sprite_generator is None:
        _sprite_generator = SpriteGenerator()
    return _sprite_generator
