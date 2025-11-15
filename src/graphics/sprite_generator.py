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
    # Animals
    BIRD = "bird"
    DOG = "dog"
    CAT = "cat"
    DEER = "deer"
    RAT = "rat"
    RACCOON = "raccoon"
    FISH = "fish"
    BIRD_OF_PREY = "bird_of_prey"


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
            # Animals
            SpriteType.BIRD: (12, 12),
            SpriteType.DOG: (18, 14),
            SpriteType.CAT: (14, 12),
            SpriteType.DEER: (24, 28),
            SpriteType.RAT: (10, 8),
            SpriteType.RACCOON: (16, 14),
            SpriteType.FISH: (14, 10),
            SpriteType.BIRD_OF_PREY: (20, 18),
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
        elif sprite_type == SpriteType.BIRD:
            sprite = self._generate_bird_sprite(direction, frame, variant, **kwargs)
        elif sprite_type == SpriteType.DOG:
            sprite = self._generate_dog_sprite(direction, frame, variant, **kwargs)
        elif sprite_type == SpriteType.CAT:
            sprite = self._generate_cat_sprite(direction, frame, variant, **kwargs)
        elif sprite_type == SpriteType.DEER:
            sprite = self._generate_deer_sprite(direction, frame, variant, **kwargs)
        elif sprite_type == SpriteType.RAT:
            sprite = self._generate_rat_sprite(direction, frame, variant, **kwargs)
        elif sprite_type == SpriteType.RACCOON:
            sprite = self._generate_raccoon_sprite(direction, frame, variant, **kwargs)
        elif sprite_type == SpriteType.FISH:
            sprite = self._generate_fish_sprite(direction, frame, variant, **kwargs)
        elif sprite_type == SpriteType.BIRD_OF_PREY:
            sprite = self._generate_bird_of_prey_sprite(direction, frame, variant, **kwargs)
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

    def _generate_bird_sprite(self, direction: Direction, frame: int, variant: int,
                              **kwargs) -> pygame.Surface:
        """Generate bird sprite with wing flapping animation."""
        width, height = self.sprite_sizes[SpriteType.BIRD]
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)

        cx, cy = width // 2, height // 2

        # Bird colors (different species)
        bird_colors = [
            ((100, 100, 100), (150, 150, 150)),  # Pigeon (gray)
            ((139, 69, 19), (210, 180, 140)),    # Sparrow (brown)
            ((0, 0, 139), (70, 130, 180)),       # Blue jay
            ((255, 0, 0), (255, 100, 100)),      # Cardinal (red)
            ((255, 215, 0), (255, 255, 150)),    # Goldfinch (yellow)
            ((0, 0, 0), (80, 80, 80)),           # Crow (black)
        ]
        body_color, wing_color = bird_colors[variant % len(bird_colors)]

        # Wing flap animation: 0 = wings up, 1 = wings mid, 2 = wings down
        wing_state = frame % 3
        wing_offset = [0, 2, 4][wing_state]

        angle_deg = direction.value

        # Draw based on direction
        if 45 <= angle_deg < 135:  # South (flying toward viewer)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 3, cy - 2, 6, 5))
            # Head
            pygame.draw.circle(sprite, body_color, (cx, cy - 3), 2)
            # Eye
            pygame.draw.circle(sprite, (0, 0, 0), (cx, cy - 3), 1)
            # Wings
            pygame.draw.ellipse(sprite, wing_color, (cx - 5, cy - wing_offset, 4, 3))  # Left wing
            pygame.draw.ellipse(sprite, wing_color, (cx + 1, cy - wing_offset, 4, 3))  # Right wing
            # Beak
            pygame.draw.polygon(sprite, (255, 200, 0), [(cx, cy - 4), (cx - 1, cy - 5), (cx + 1, cy - 5)])

        elif 225 <= angle_deg < 315:  # North (flying away)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 3, cy - 2, 6, 5))
            # Wings (larger when flying away)
            pygame.draw.ellipse(sprite, wing_color, (cx - 5, cy - wing_offset, 4, 4))  # Left wing
            pygame.draw.ellipse(sprite, wing_color, (cx + 1, cy - wing_offset, 4, 4))  # Right wing
            # Head (small from behind)
            pygame.draw.circle(sprite, body_color, (cx, cy - 3), 2)

        elif 135 <= angle_deg < 225:  # West (side view)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 3, cy - 2, 6, 5))
            # Head
            pygame.draw.circle(sprite, body_color, (cx - 3, cy - 3), 2)
            # Eye
            pygame.draw.circle(sprite, (0, 0, 0), (cx - 3, cy - 3), 1)
            # Beak
            pygame.draw.polygon(sprite, (255, 200, 0), [(cx - 4, cy - 3), (cx - 5, cy - 4), (cx - 5, cy - 2)])
            # Wing (side view - up or down)
            if wing_state == 0:  # Up
                pygame.draw.ellipse(sprite, wing_color, (cx - 2, cy - 5, 5, 3))
            elif wing_state == 2:  # Down
                pygame.draw.ellipse(sprite, wing_color, (cx - 2, cy + 1, 5, 3))
            else:  # Mid
                pygame.draw.ellipse(sprite, wing_color, (cx - 2, cy - 2, 5, 3))
            # Tail
            pygame.draw.polygon(sprite, wing_color, [(cx + 3, cy - 1), (cx + 5, cy - 2), (cx + 5, cy + 1)])

        else:  # East (side view)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 3, cy - 2, 6, 5))
            # Head
            pygame.draw.circle(sprite, body_color, (cx + 3, cy - 3), 2)
            # Eye
            pygame.draw.circle(sprite, (0, 0, 0), (cx + 3, cy - 3), 1)
            # Beak
            pygame.draw.polygon(sprite, (255, 200, 0), [(cx + 4, cy - 3), (cx + 5, cy - 4), (cx + 5, cy - 2)])
            # Wing (side view - up or down)
            if wing_state == 0:  # Up
                pygame.draw.ellipse(sprite, wing_color, (cx - 3, cy - 5, 5, 3))
            elif wing_state == 2:  # Down
                pygame.draw.ellipse(sprite, wing_color, (cx - 3, cy + 1, 5, 3))
            else:  # Mid
                pygame.draw.ellipse(sprite, wing_color, (cx - 3, cy - 2, 5, 3))
            # Tail
            pygame.draw.polygon(sprite, wing_color, [(cx - 3, cy - 1), (cx - 5, cy - 2), (cx - 5, cy + 1)])

        return sprite

    def _generate_dog_sprite(self, direction: Direction, frame: int, variant: int,
                             **kwargs) -> pygame.Surface:
        """Generate dog sprite with walking animation."""
        width, height = self.sprite_sizes[SpriteType.DOG]
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)

        cx, cy = width // 2, height // 2

        # Dog breeds/colors
        dog_colors = [
            ((139, 69, 19), (101, 67, 33)),      # Brown
            ((255, 215, 0), (218, 165, 32)),     # Golden
            ((0, 0, 0), (40, 40, 40)),           # Black
            ((255, 255, 255), (200, 200, 200)),  # White
            ((160, 82, 45), (139, 69, 19)),      # Brown-tan
            ((192, 192, 192), (128, 128, 128)),  # Gray
        ]
        body_color, dark_color = dog_colors[variant % len(dog_colors)]

        # Walking animation
        leg_offset = 0
        if frame == 1:
            leg_offset = 1
        elif frame == 2:
            leg_offset = -1

        angle_deg = direction.value

        # Draw based on direction
        if 45 <= angle_deg < 135:  # South (front view)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 6, cy - 3, 12, 8))
            pygame.draw.ellipse(sprite, dark_color, (cx - 6, cy - 3, 12, 8), 1)
            # Head
            pygame.draw.ellipse(sprite, body_color, (cx - 4, cy - 6, 8, 6))
            # Ears
            pygame.draw.ellipse(sprite, dark_color, (cx - 5, cy - 7, 3, 4))  # Left ear
            pygame.draw.ellipse(sprite, dark_color, (cx + 2, cy - 7, 3, 4))  # Right ear
            # Eyes
            pygame.draw.circle(sprite, (0, 0, 0), (cx - 2, cy - 5), 1)
            pygame.draw.circle(sprite, (0, 0, 0), (cx + 2, cy - 5), 1)
            # Nose
            pygame.draw.circle(sprite, (0, 0, 0), (cx, cy - 3), 1)
            # Legs (front view - 4 legs visible)
            pygame.draw.rect(sprite, body_color, (cx - 5, cy + 3, 2, 4 + leg_offset))   # Front left
            pygame.draw.rect(sprite, body_color, (cx + 3, cy + 3, 2, 4 - leg_offset))   # Front right
            pygame.draw.rect(sprite, dark_color, (cx - 3, cy + 3, 2, 4 - leg_offset))   # Back left
            pygame.draw.rect(sprite, dark_color, (cx + 1, cy + 3, 2, 4 + leg_offset))   # Back right
            # Tail
            pygame.draw.arc(sprite, dark_color, (cx + 4, cy - 2, 4, 6), 0, math.pi, 2)

        elif 225 <= angle_deg < 315:  # North (back view)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 6, cy - 3, 12, 8))
            # Tail (raised)
            pygame.draw.ellipse(sprite, dark_color, (cx - 2, cy - 8, 4, 6))
            # Head (barely visible from behind)
            pygame.draw.ellipse(sprite, body_color, (cx - 3, cy - 5, 6, 4))
            # Ears poking up
            pygame.draw.circle(sprite, dark_color, (cx - 2, cy - 6), 1)
            pygame.draw.circle(sprite, dark_color, (cx + 2, cy - 6), 1)
            # Legs
            pygame.draw.rect(sprite, body_color, (cx - 5, cy + 3, 2, 4 - leg_offset))
            pygame.draw.rect(sprite, body_color, (cx + 3, cy + 3, 2, 4 + leg_offset))
            pygame.draw.rect(sprite, dark_color, (cx - 3, cy + 3, 2, 4 + leg_offset))
            pygame.draw.rect(sprite, dark_color, (cx + 1, cy + 3, 2, 4 - leg_offset))

        elif 135 <= angle_deg < 225:  # West (side view - facing left)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 5, cy - 3, 10, 7))
            # Head
            pygame.draw.ellipse(sprite, body_color, (cx - 7, cy - 5, 6, 5))
            # Ear
            pygame.draw.ellipse(sprite, dark_color, (cx - 8, cy - 6, 3, 4))
            # Eye
            pygame.draw.circle(sprite, (0, 0, 0), (cx - 6, cy - 4), 1)
            # Nose
            pygame.draw.circle(sprite, (0, 0, 0), (cx - 8, cy - 3), 1)
            # Legs (side view - 2 visible)
            pygame.draw.rect(sprite, body_color, (cx - 4, cy + 2, 2, 5 + leg_offset))  # Front leg
            pygame.draw.rect(sprite, dark_color, (cx + 2, cy + 2, 2, 5 - leg_offset))  # Back leg
            # Tail
            pygame.draw.arc(sprite, dark_color, (cx + 3, cy - 3, 5, 6), 0, math.pi/2, 2)

        else:  # East (side view - facing right)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 5, cy - 3, 10, 7))
            # Head
            pygame.draw.ellipse(sprite, body_color, (cx + 1, cy - 5, 6, 5))
            # Ear
            pygame.draw.ellipse(sprite, dark_color, (cx + 5, cy - 6, 3, 4))
            # Eye
            pygame.draw.circle(sprite, (0, 0, 0), (cx + 6, cy - 4), 1)
            # Nose
            pygame.draw.circle(sprite, (0, 0, 0), (cx + 8, cy - 3), 1)
            # Legs (side view - 2 visible)
            pygame.draw.rect(sprite, body_color, (cx + 2, cy + 2, 2, 5 + leg_offset))  # Front leg
            pygame.draw.rect(sprite, dark_color, (cx - 4, cy + 2, 2, 5 - leg_offset))  # Back leg
            # Tail
            pygame.draw.arc(sprite, dark_color, (cx - 8, cy - 3, 5, 6), math.pi/2, math.pi, 2)

        return sprite

    def _generate_cat_sprite(self, direction: Direction, frame: int, variant: int,
                             **kwargs) -> pygame.Surface:
        """Generate cat sprite with walking animation."""
        width, height = self.sprite_sizes[SpriteType.CAT]
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)

        cx, cy = width // 2, height // 2

        # Cat colors
        cat_colors = [
            ((255, 140, 0), (200, 100, 0)),      # Orange tabby
            ((128, 128, 128), (80, 80, 80)),     # Gray
            ((0, 0, 0), (40, 40, 40)),           # Black
            ((255, 255, 255), (200, 200, 200)),  # White
            ((139, 69, 19), (101, 67, 33)),      # Brown
            ((210, 180, 140), (160, 130, 90)),   # Tan
        ]
        body_color, stripe_color = cat_colors[variant % len(cat_colors)]

        # Walking animation
        leg_offset = 0
        tail_sway = 0
        if frame == 1:
            leg_offset = 1
            tail_sway = 1
        elif frame == 2:
            leg_offset = -1
            tail_sway = -1

        angle_deg = direction.value

        # Draw based on direction
        if 45 <= angle_deg < 135:  # South (front view)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 5, cy - 3, 10, 7))
            # Head
            pygame.draw.ellipse(sprite, body_color, (cx - 3, cy - 6, 6, 5))
            # Ears (pointed)
            pygame.draw.polygon(sprite, stripe_color, [(cx - 3, cy - 6), (cx - 4, cy - 8), (cx - 2, cy - 6)])
            pygame.draw.polygon(sprite, stripe_color, [(cx + 3, cy - 6), (cx + 2, cy - 6), (cx + 4, cy - 8)])
            # Eyes
            pygame.draw.circle(sprite, (0, 255, 0), (cx - 2, cy - 5), 1)
            pygame.draw.circle(sprite, (0, 255, 0), (cx + 2, cy - 5), 1)
            pygame.draw.circle(sprite, (0, 0, 0), (cx - 2, cy - 5), 1, 1)
            pygame.draw.circle(sprite, (0, 0, 0), (cx + 2, cy - 5), 1, 1)
            # Nose
            pygame.draw.polygon(sprite, (255, 182, 193), [(cx, cy - 3), (cx - 1, cy - 4), (cx + 1, cy - 4)])
            # Legs
            pygame.draw.rect(sprite, body_color, (cx - 4, cy + 2, 2, 4 + leg_offset))
            pygame.draw.rect(sprite, body_color, (cx + 2, cy + 2, 2, 4 - leg_offset))
            # Tail (visible behind)
            pygame.draw.arc(sprite, stripe_color, (cx + 3 + tail_sway, cy - 2, 4, 8), 0, math.pi, 2)

        elif 225 <= angle_deg < 315:  # North (back view)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 5, cy - 3, 10, 7))
            # Tail (raised high)
            pygame.draw.rect(sprite, stripe_color, (cx - 1 + tail_sway, cy - 8, 2, 6))
            # Ears visible
            pygame.draw.polygon(sprite, stripe_color, [(cx - 3, cy - 5), (cx - 4, cy - 7), (cx - 2, cy - 5)])
            pygame.draw.polygon(sprite, stripe_color, [(cx + 3, cy - 5), (cx + 2, cy - 5), (cx + 4, cy - 7)])
            # Legs
            pygame.draw.rect(sprite, body_color, (cx - 4, cy + 2, 2, 4 - leg_offset))
            pygame.draw.rect(sprite, body_color, (cx + 2, cy + 2, 2, 4 + leg_offset))

        elif 135 <= angle_deg < 225:  # West (side view)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 4, cy - 3, 9, 6))
            # Head
            pygame.draw.circle(sprite, body_color, (cx - 5, cy - 4), 3)
            # Ear
            pygame.draw.polygon(sprite, stripe_color, [(cx - 6, cy - 6), (cx - 7, cy - 8), (cx - 5, cy - 6)])
            # Eye
            pygame.draw.circle(sprite, (0, 255, 0), (cx - 5, cy - 5), 1)
            # Nose
            pygame.draw.circle(sprite, (255, 182, 193), (cx - 7, cy - 3), 1)
            # Legs
            pygame.draw.rect(sprite, body_color, (cx - 3, cy + 1, 2, 4 + leg_offset))  # Front
            pygame.draw.rect(sprite, body_color, (cx + 1, cy + 1, 2, 4 - leg_offset))  # Back
            # Tail (curved up)
            pygame.draw.arc(sprite, stripe_color, (cx + 2 + tail_sway, cy - 5, 4, 6), 0, math.pi, 2)

        else:  # East (side view)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 5, cy - 3, 9, 6))
            # Head
            pygame.draw.circle(sprite, body_color, (cx + 5, cy - 4), 3)
            # Ear
            pygame.draw.polygon(sprite, stripe_color, [(cx + 6, cy - 6), (cx + 5, cy - 6), (cx + 7, cy - 8)])
            # Eye
            pygame.draw.circle(sprite, (0, 255, 0), (cx + 5, cy - 5), 1)
            # Nose
            pygame.draw.circle(sprite, (255, 182, 193), (cx + 7, cy - 3), 1)
            # Legs
            pygame.draw.rect(sprite, body_color, (cx + 1, cy + 1, 2, 4 + leg_offset))  # Front
            pygame.draw.rect(sprite, body_color, (cx - 3, cy + 1, 2, 4 - leg_offset))  # Back
            # Tail (curved up)
            pygame.draw.arc(sprite, stripe_color, (cx - 6 + tail_sway, cy - 5, 4, 6), 0, math.pi, 2)

        return sprite

    def _generate_deer_sprite(self, direction: Direction, frame: int, variant: int,
                              **kwargs) -> pygame.Surface:
        """Generate deer sprite with walking animation."""
        width, height = self.sprite_sizes[SpriteType.DEER]
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)

        cx, cy = width // 2, height // 2

        # Deer colors (variations)
        deer_colors = [
            ((139, 90, 43), (101, 67, 33)),      # Brown
            ((160, 82, 45), (139, 69, 19)),      # Reddish-brown
            ((205, 133, 63), (160, 82, 45)),     # Tan
        ]
        body_color, dark_color = deer_colors[variant % len(deer_colors)]

        # Walking animation
        leg_offset = 0
        if frame == 1:
            leg_offset = 2
        elif frame == 2:
            leg_offset = -2

        angle_deg = direction.value

        # Draw based on direction
        if 45 <= angle_deg < 135:  # South (front view)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 7, cy - 5, 14, 12))
            # Neck
            pygame.draw.rect(sprite, body_color, (cx - 3, cy - 10, 6, 6))
            # Head
            pygame.draw.ellipse(sprite, body_color, (cx - 3, cy - 13, 6, 6))
            # Ears
            pygame.draw.ellipse(sprite, dark_color, (cx - 4, cy - 14, 2, 3))
            pygame.draw.ellipse(sprite, dark_color, (cx + 2, cy - 14, 2, 3))
            # Antlers (if male - variant 0, 2, 4...)
            if variant % 2 == 0:
                # Left antler
                pygame.draw.line(sprite, dark_color, (cx - 3, cy - 13), (cx - 5, cy - 16), 1)
                pygame.draw.line(sprite, dark_color, (cx - 5, cy - 16), (cx - 6, cy - 18), 1)
                pygame.draw.line(sprite, dark_color, (cx - 5, cy - 16), (cx - 4, cy - 17), 1)
                # Right antler
                pygame.draw.line(sprite, dark_color, (cx + 3, cy - 13), (cx + 5, cy - 16), 1)
                pygame.draw.line(sprite, dark_color, (cx + 5, cy - 16), (cx + 6, cy - 18), 1)
                pygame.draw.line(sprite, dark_color, (cx + 5, cy - 16), (cx + 4, cy - 17), 1)
            # Eyes
            pygame.draw.circle(sprite, (0, 0, 0), (cx - 2, cy - 12), 1)
            pygame.draw.circle(sprite, (0, 0, 0), (cx + 2, cy - 12), 1)
            # Nose
            pygame.draw.circle(sprite, (0, 0, 0), (cx, cy - 10), 1)
            # Legs
            pygame.draw.rect(sprite, dark_color, (cx - 6, cy + 4, 2, 8 + leg_offset))  # Front left
            pygame.draw.rect(sprite, dark_color, (cx + 4, cy + 4, 2, 8 - leg_offset))  # Front right
            pygame.draw.rect(sprite, body_color, (cx - 3, cy + 4, 2, 8 - leg_offset))  # Back left
            pygame.draw.rect(sprite, body_color, (cx + 1, cy + 4, 2, 8 + leg_offset))  # Back right
            # Tail
            pygame.draw.ellipse(sprite, (255, 255, 255), (cx - 1, cy + 2, 2, 4))  # White tail

        elif 225 <= angle_deg < 315:  # North (back view)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 7, cy - 5, 14, 12))
            # Tail (visible white)
            pygame.draw.ellipse(sprite, (255, 255, 255), (cx - 2, cy - 2, 4, 6))
            # Neck and head barely visible
            pygame.draw.ellipse(sprite, body_color, (cx - 3, cy - 9, 6, 5))
            # Antler tips visible (if male)
            if variant % 2 == 0:
                pygame.draw.line(sprite, dark_color, (cx - 3, cy - 10), (cx - 5, cy - 13), 1)
                pygame.draw.line(sprite, dark_color, (cx + 3, cy - 10), (cx + 5, cy - 13), 1)
            # Ears
            pygame.draw.circle(sprite, dark_color, (cx - 2, cy - 10), 1)
            pygame.draw.circle(sprite, dark_color, (cx + 2, cy - 10), 1)
            # Legs
            pygame.draw.rect(sprite, dark_color, (cx - 6, cy + 4, 2, 8 - leg_offset))
            pygame.draw.rect(sprite, dark_color, (cx + 4, cy + 4, 2, 8 + leg_offset))
            pygame.draw.rect(sprite, body_color, (cx - 3, cy + 4, 2, 8 + leg_offset))
            pygame.draw.rect(sprite, body_color, (cx + 1, cy + 4, 2, 8 - leg_offset))

        elif 135 <= angle_deg < 225:  # West (side view)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 6, cy - 4, 12, 10))
            # Neck
            pygame.draw.rect(sprite, body_color, (cx - 7, cy - 9, 4, 6))
            # Head
            pygame.draw.ellipse(sprite, body_color, (cx - 9, cy - 12, 5, 5))
            # Ear
            pygame.draw.ellipse(sprite, dark_color, (cx - 10, cy - 13, 2, 3))
            # Antler (if male)
            if variant % 2 == 0:
                pygame.draw.line(sprite, dark_color, (cx - 8, cy - 12), (cx - 10, cy - 15), 1)
                pygame.draw.line(sprite, dark_color, (cx - 10, cy - 15), (cx - 11, cy - 17), 1)
                pygame.draw.line(sprite, dark_color, (cx - 10, cy - 15), (cx - 9, cy - 16), 1)
            # Eye
            pygame.draw.circle(sprite, (0, 0, 0), (cx - 8, cy - 11), 1)
            # Nose
            pygame.draw.circle(sprite, (0, 0, 0), (cx - 10, cy - 9), 1)
            # Legs
            pygame.draw.rect(sprite, dark_color, (cx - 5, cy + 3, 2, 9 + leg_offset))  # Front
            pygame.draw.rect(sprite, body_color, (cx + 3, cy + 3, 2, 9 - leg_offset))  # Back
            # Tail
            pygame.draw.ellipse(sprite, (255, 255, 255), (cx + 5, cy + 1, 2, 4))

        else:  # East (side view)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 6, cy - 4, 12, 10))
            # Neck
            pygame.draw.rect(sprite, body_color, (cx + 3, cy - 9, 4, 6))
            # Head
            pygame.draw.ellipse(sprite, body_color, (cx + 4, cy - 12, 5, 5))
            # Ear
            pygame.draw.ellipse(sprite, dark_color, (cx + 8, cy - 13, 2, 3))
            # Antler (if male)
            if variant % 2 == 0:
                pygame.draw.line(sprite, dark_color, (cx + 8, cy - 12), (cx + 10, cy - 15), 1)
                pygame.draw.line(sprite, dark_color, (cx + 10, cy - 15), (cx + 11, cy - 17), 1)
                pygame.draw.line(sprite, dark_color, (cx + 10, cy - 15), (cx + 9, cy - 16), 1)
            # Eye
            pygame.draw.circle(sprite, (0, 0, 0), (cx + 8, cy - 11), 1)
            # Nose
            pygame.draw.circle(sprite, (0, 0, 0), (cx + 10, cy - 9), 1)
            # Legs
            pygame.draw.rect(sprite, dark_color, (cx + 3, cy + 3, 2, 9 + leg_offset))  # Front
            pygame.draw.rect(sprite, body_color, (cx - 5, cy + 3, 2, 9 - leg_offset))  # Back
            # Tail
            pygame.draw.ellipse(sprite, (255, 255, 255), (cx - 7, cy + 1, 2, 4))

        return sprite

    def _generate_rat_sprite(self, direction: Direction, frame: int, variant: int,
                             **kwargs) -> pygame.Surface:
        """Generate rat sprite with scurrying animation."""
        width, height = self.sprite_sizes[SpriteType.RAT]
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)

        cx, cy = width // 2, height // 2

        # Rat colors
        rat_colors = [
            ((100, 100, 100), (60, 60, 60)),     # Gray
            ((80, 80, 80), (40, 40, 40)),        # Dark gray
            ((139, 90, 43), (101, 67, 33)),      # Brown
        ]
        body_color, dark_color = rat_colors[variant % len(rat_colors)]

        # Scurrying animation
        body_crouch = 1 if frame % 2 == 0 else 0

        angle_deg = direction.value

        # Draw based on direction
        if 45 <= angle_deg < 135:  # South
            # Body (low to ground)
            pygame.draw.ellipse(sprite, body_color, (cx - 3, cy - 1 + body_crouch, 6, 4))
            # Head
            pygame.draw.ellipse(sprite, body_color, (cx - 2, cy - 3 + body_crouch, 4, 3))
            # Ears
            pygame.draw.circle(sprite, dark_color, (cx - 2, cy - 3 + body_crouch), 1)
            pygame.draw.circle(sprite, dark_color, (cx + 2, cy - 3 + body_crouch), 1)
            # Eyes
            pygame.draw.circle(sprite, (255, 0, 0), (cx - 1, cy - 2 + body_crouch), 1)
            pygame.draw.circle(sprite, (255, 0, 0), (cx + 1, cy - 2 + body_crouch), 1)
            # Tail
            pygame.draw.line(sprite, dark_color, (cx, cy + 2), (cx - 2, cy + 4), 1)

        elif 225 <= angle_deg < 315:  # North
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 3, cy - 1 + body_crouch, 6, 4))
            # Tail visible
            pygame.draw.line(sprite, dark_color, (cx, cy - 2), (cx + 1, cy - 4), 1)
            # Ears visible
            pygame.draw.circle(sprite, dark_color, (cx - 2, cy - 2 + body_crouch), 1)
            pygame.draw.circle(sprite, dark_color, (cx + 2, cy - 2 + body_crouch), 1)

        elif 135 <= angle_deg < 225:  # West
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 3, cy - 1 + body_crouch, 6, 3))
            # Head
            pygame.draw.circle(sprite, body_color, (cx - 3, cy - 1 + body_crouch), 2)
            # Ear
            pygame.draw.circle(sprite, dark_color, (cx - 4, cy - 2 + body_crouch), 1)
            # Eye
            pygame.draw.circle(sprite, (255, 0, 0), (cx - 3, cy - 1 + body_crouch), 1)
            # Tail (curved)
            pygame.draw.arc(sprite, dark_color, (cx + 1, cy - 2, 3, 4), 0, math.pi, 1)

        else:  # East
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 3, cy - 1 + body_crouch, 6, 3))
            # Head
            pygame.draw.circle(sprite, body_color, (cx + 3, cy - 1 + body_crouch), 2)
            # Ear
            pygame.draw.circle(sprite, dark_color, (cx + 4, cy - 2 + body_crouch), 1)
            # Eye
            pygame.draw.circle(sprite, (255, 0, 0), (cx + 3, cy - 1 + body_crouch), 1)
            # Tail (curved)
            pygame.draw.arc(sprite, dark_color, (cx - 4, cy - 2, 3, 4), 0, math.pi, 1)

        return sprite

    def _generate_raccoon_sprite(self, direction: Direction, frame: int, variant: int,
                                 **kwargs) -> pygame.Surface:
        """Generate raccoon sprite with walking animation."""
        width, height = self.sprite_sizes[SpriteType.RACCOON]
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)

        cx, cy = width // 2, height // 2

        # Raccoon colors (gray with black mask)
        body_color = (128, 128, 128)
        dark_color = (40, 40, 40)
        light_color = (180, 180, 180)

        # Walking animation
        leg_offset = 0
        if frame == 1:
            leg_offset = 1
        elif frame == 2:
            leg_offset = -1

        angle_deg = direction.value

        # Draw based on direction
        if 45 <= angle_deg < 135:  # South
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 5, cy - 3, 10, 8))
            # Head
            pygame.draw.ellipse(sprite, light_color, (cx - 4, cy - 6, 8, 6))
            # Ears
            pygame.draw.circle(sprite, body_color, (cx - 3, cy - 7), 2)
            pygame.draw.circle(sprite, body_color, (cx + 3, cy - 7), 2)
            # Mask (distinctive raccoon feature)
            pygame.draw.ellipse(sprite, dark_color, (cx - 4, cy - 5, 3, 2))
            pygame.draw.ellipse(sprite, dark_color, (cx + 1, cy - 5, 3, 2))
            # Eyes (in mask)
            pygame.draw.circle(sprite, (255, 255, 255), (cx - 2, cy - 5), 1)
            pygame.draw.circle(sprite, (255, 255, 255), (cx + 2, cy - 5), 1)
            # Nose
            pygame.draw.circle(sprite, (0, 0, 0), (cx, cy - 3), 1)
            # Legs
            pygame.draw.rect(sprite, body_color, (cx - 4, cy + 2, 2, 4 + leg_offset))
            pygame.draw.rect(sprite, body_color, (cx + 2, cy + 2, 2, 4 - leg_offset))
            # Tail (ringed - visible behind)
            for i in range(3):
                tail_color = dark_color if i % 2 == 0 else body_color
                pygame.draw.arc(sprite, tail_color, (cx + 3, cy - 2 + i * 2, 4, 4), 0, math.pi, 2)

        elif 225 <= angle_deg < 315:  # North
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 5, cy - 3, 10, 8))
            # Tail (ringed - raised)
            for i in range(4):
                tail_color = dark_color if i % 2 == 0 else body_color
                pygame.draw.ellipse(sprite, tail_color, (cx - 2, cy - 8 + i * 2, 4, 3))
            # Ears visible
            pygame.draw.circle(sprite, body_color, (cx - 2, cy - 6), 1)
            pygame.draw.circle(sprite, body_color, (cx + 2, cy - 6), 1)
            # Legs
            pygame.draw.rect(sprite, body_color, (cx - 4, cy + 2, 2, 4 - leg_offset))
            pygame.draw.rect(sprite, body_color, (cx + 2, cy + 2, 2, 4 + leg_offset))

        elif 135 <= angle_deg < 225:  # West
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 4, cy - 3, 9, 7))
            # Head
            pygame.draw.ellipse(sprite, light_color, (cx - 6, cy - 5, 6, 5))
            # Ear
            pygame.draw.circle(sprite, body_color, (cx - 6, cy - 6), 2)
            # Mask
            pygame.draw.ellipse(sprite, dark_color, (cx - 7, cy - 5, 3, 2))
            # Eye
            pygame.draw.circle(sprite, (255, 255, 255), (cx - 6, cy - 5), 1)
            # Nose
            pygame.draw.circle(sprite, (0, 0, 0), (cx - 7, cy - 3), 1)
            # Legs
            pygame.draw.rect(sprite, body_color, (cx - 3, cy + 1, 2, 4 + leg_offset))
            pygame.draw.rect(sprite, body_color, (cx + 2, cy + 1, 2, 4 - leg_offset))
            # Tail (ringed)
            for i in range(3):
                tail_color = dark_color if i % 2 == 0 else body_color
                pygame.draw.arc(sprite, tail_color, (cx + 2, cy - 4 + i * 2, 4, 4), 0, math.pi/2, 2)

        else:  # East
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 5, cy - 3, 9, 7))
            # Head
            pygame.draw.ellipse(sprite, light_color, (cx, cy - 5, 6, 5))
            # Ear
            pygame.draw.circle(sprite, body_color, (cx + 6, cy - 6), 2)
            # Mask
            pygame.draw.ellipse(sprite, dark_color, (cx + 4, cy - 5, 3, 2))
            # Eye
            pygame.draw.circle(sprite, (255, 255, 255), (cx + 6, cy - 5), 1)
            # Nose
            pygame.draw.circle(sprite, (0, 0, 0), (cx + 7, cy - 3), 1)
            # Legs
            pygame.draw.rect(sprite, body_color, (cx + 1, cy + 1, 2, 4 + leg_offset))
            pygame.draw.rect(sprite, body_color, (cx - 4, cy + 1, 2, 4 - leg_offset))
            # Tail (ringed)
            for i in range(3):
                tail_color = dark_color if i % 2 == 0 else body_color
                pygame.draw.arc(sprite, tail_color, (cx - 6, cy - 4 + i * 2, 4, 4), math.pi/2, math.pi, 2)

        return sprite

    def _generate_fish_sprite(self, direction: Direction, frame: int, variant: int,
                              **kwargs) -> pygame.Surface:
        """Generate fish sprite with swimming animation."""
        width, height = self.sprite_sizes[SpriteType.FISH]
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)

        cx, cy = width // 2, height // 2

        # Fish colors (various species)
        fish_colors = [
            ((255, 140, 0), (255, 69, 0)),       # Goldfish (orange)
            ((0, 100, 200), (0, 50, 150)),       # Blue fish
            ((192, 192, 192), (128, 128, 128)),  # Silver
            ((255, 215, 0), (255, 255, 150)),    # Yellow
            ((34, 139, 34), (0, 100, 0)),        # Green bass
        ]
        body_color, fin_color = fish_colors[variant % len(fish_colors)]

        # Swimming animation (tail wag)
        tail_angle = 0
        if frame == 1:
            tail_angle = 10
        elif frame == 2:
            tail_angle = -10

        angle_deg = direction.value

        # Create sprite facing east, then rotate
        temp_sprite = pygame.Surface((width, height), pygame.SRCALPHA)

        # Body (ellipse)
        pygame.draw.ellipse(temp_sprite, body_color, (cx - 5, cy - 2, 8, 4))
        pygame.draw.ellipse(temp_sprite, fin_color, (cx - 5, cy - 2, 8, 4), 1)

        # Tail (with animation)
        tail_points = [
            (cx - 5, cy),
            (cx - 7, cy - 2 - tail_angle // 10),
            (cx - 7, cy + 2 + tail_angle // 10),
        ]
        pygame.draw.polygon(temp_sprite, fin_color, tail_points)

        # Dorsal fin
        dorsal_points = [
            (cx - 1, cy - 2),
            (cx, cy - 4),
            (cx + 1, cy - 2),
        ]
        pygame.draw.polygon(temp_sprite, fin_color, dorsal_points)

        # Pectoral fin
        pygame.draw.ellipse(temp_sprite, fin_color, (cx - 1, cy + 1, 3, 2))

        # Eye
        pygame.draw.circle(temp_sprite, (0, 0, 0), (cx + 2, cy - 1), 1)

        # Rotate based on direction
        rotation_angle = -angle_deg  # Negative for pygame rotation
        sprite = pygame.transform.rotate(temp_sprite, rotation_angle)

        return sprite

    def _generate_bird_of_prey_sprite(self, direction: Direction, frame: int, variant: int,
                                       **kwargs) -> pygame.Surface:
        """Generate bird of prey (hawk/eagle) sprite with soaring animation."""
        width, height = self.sprite_sizes[SpriteType.BIRD_OF_PREY]
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)

        cx, cy = width // 2, height // 2

        # Bird of prey colors
        prey_colors = [
            ((101, 67, 33), (139, 90, 43)),      # Brown hawk
            ((255, 255, 255), (200, 200, 200)),  # Bald eagle
            ((80, 80, 80), (120, 120, 120)),     # Gray falcon
        ]
        body_color, wing_color = prey_colors[variant % len(prey_colors)]

        # Soaring animation (wing flap - slower than small birds)
        wing_state = 0 if frame < 2 else 1  # Slower flapping
        wing_offset = 3 if wing_state == 0 else 1

        angle_deg = direction.value

        # Draw based on direction
        if 45 <= angle_deg < 135:  # South (flying toward viewer)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 4, cy - 3, 8, 7))
            # Head
            pygame.draw.circle(sprite, body_color, (cx, cy - 5), 3)
            # Eyes (fierce)
            pygame.draw.circle(sprite, (255, 255, 0), (cx - 1, cy - 5), 1)
            pygame.draw.circle(sprite, (255, 255, 0), (cx + 1, cy - 5), 1)
            pygame.draw.circle(sprite, (0, 0, 0), (cx - 1, cy - 5), 1, 1)
            pygame.draw.circle(sprite, (0, 0, 0), (cx + 1, cy - 5), 1, 1)
            # Beak (hooked)
            pygame.draw.polygon(sprite, (255, 200, 0), [(cx, cy - 4), (cx - 1, cy - 3), (cx + 1, cy - 3)])
            # Wings (spread wide)
            pygame.draw.ellipse(sprite, wing_color, (cx - 9, cy - wing_offset, 5, 6))  # Left wing
            pygame.draw.ellipse(sprite, wing_color, (cx + 4, cy - wing_offset, 5, 6))  # Right wing
            # Tail feathers
            pygame.draw.polygon(sprite, wing_color, [(cx - 2, cy + 3), (cx + 2, cy + 3), (cx, cy + 6)])

        elif 225 <= angle_deg < 315:  # North (flying away)
            # Body (smaller from behind)
            pygame.draw.ellipse(sprite, body_color, (cx - 3, cy - 2, 6, 5))
            # Wings (wide spread from behind)
            pygame.draw.ellipse(sprite, wing_color, (cx - 9, cy - wing_offset, 6, 5))  # Left wing
            pygame.draw.ellipse(sprite, wing_color, (cx + 3, cy - wing_offset, 6, 5))  # Right wing
            # Tail (fan shaped)
            pygame.draw.polygon(sprite, wing_color, [(cx - 3, cy + 2), (cx + 3, cy + 2), (cx, cy + 6)])
            # Head barely visible
            pygame.draw.circle(sprite, body_color, (cx, cy - 4), 2)

        elif 135 <= angle_deg < 225:  # West (side view)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 4, cy - 3, 8, 6))
            # Head
            pygame.draw.circle(sprite, body_color, (cx - 5, cy - 5), 3)
            # Eye
            pygame.draw.circle(sprite, (255, 255, 0), (cx - 5, cy - 5), 1)
            # Beak
            pygame.draw.polygon(sprite, (255, 200, 0), [(cx - 6, cy - 5), (cx - 8, cy - 6), (cx - 8, cy - 4)])
            # Wing (side view - large)
            if wing_state == 0:  # Up
                pygame.draw.ellipse(sprite, wing_color, (cx - 3, cy - 8, 7, 5))
            else:  # Down
                pygame.draw.ellipse(sprite, wing_color, (cx - 3, cy, 7, 5))
            # Tail
            pygame.draw.polygon(sprite, wing_color, [(cx + 4, cy - 2), (cx + 8, cy - 3), (cx + 8, cy + 2), (cx + 4, cy + 1)])
            # Talons
            pygame.draw.line(sprite, (0, 0, 0), (cx - 1, cy + 2), (cx - 1, cy + 4), 1)
            pygame.draw.line(sprite, (0, 0, 0), (cx + 1, cy + 2), (cx + 1, cy + 4), 1)

        else:  # East (side view)
            # Body
            pygame.draw.ellipse(sprite, body_color, (cx - 4, cy - 3, 8, 6))
            # Head
            pygame.draw.circle(sprite, body_color, (cx + 5, cy - 5), 3)
            # Eye
            pygame.draw.circle(sprite, (255, 255, 0), (cx + 5, cy - 5), 1)
            # Beak
            pygame.draw.polygon(sprite, (255, 200, 0), [(cx + 6, cy - 5), (cx + 8, cy - 6), (cx + 8, cy - 4)])
            # Wing (side view - large)
            if wing_state == 0:  # Up
                pygame.draw.ellipse(sprite, wing_color, (cx - 4, cy - 8, 7, 5))
            else:  # Down
                pygame.draw.ellipse(sprite, wing_color, (cx - 4, cy, 7, 5))
            # Tail
            pygame.draw.polygon(sprite, wing_color, [(cx - 4, cy - 2), (cx - 8, cy - 3), (cx - 8, cy + 2), (cx - 4, cy + 1)])
            # Talons
            pygame.draw.line(sprite, (0, 0, 0), (cx - 1, cy + 2), (cx - 1, cy + 4), 1)
            pygame.draw.line(sprite, (0, 0, 0), (cx + 1, cy + 2), (cx + 1, cy + 4), 1)

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
