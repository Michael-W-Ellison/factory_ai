"""
Camera class - handles view positioning and controls.
"""

import pygame
import config


class Camera:
    """
    Camera controls the player's view of the game world.

    The camera can pan (move) and zoom (future feature).
    """

    def __init__(self, width, height):
        """
        Initialize the camera.

        Args:
            width (int): Screen width in pixels
            height (int): Screen height in pixels
        """
        self.x = 0  # Camera position in world coordinates
        self.y = 0
        self.width = width
        self.height = height

        # Camera movement
        self.speed = 300  # Pixels per second
        self.zoom = 1.0  # Future feature

        # Bounds (will be set by world)
        self.max_x = 0
        self.max_y = 0

    def set_bounds(self, world_width, world_height):
        """
        Set the maximum bounds for camera movement.

        Args:
            world_width (int): Width of world in pixels
            world_height (int): Height of world in pixels
        """
        self.max_x = max(0, world_width - self.width)
        self.max_y = max(0, world_height - self.height)

    def update(self, dt, settings_manager=None):
        """
        Update camera position based on input.

        Args:
            dt (float): Delta time in seconds
            settings_manager: Optional SettingsManager for custom key bindings
        """
        # Get keyboard state
        keys = pygame.key.get_pressed()

        # Get custom key bindings or use defaults
        if settings_manager:
            key_bindings = settings_manager.get('controls', 'key_bindings', {})
            scroll_speed = settings_manager.get('controls', 'scroll_speed', 1.0)
        else:
            key_bindings = {}
            scroll_speed = 1.0

        # Get custom camera keys (with fallbacks to WASD)
        pan_up_key = self._get_key_code(key_bindings.get('camera_up', 'W'))
        pan_down_key = self._get_key_code(key_bindings.get('camera_down', 'S'))
        pan_left_key = self._get_key_code(key_bindings.get('camera_left', 'A'))
        pan_right_key = self._get_key_code(key_bindings.get('camera_right', 'D'))

        # Calculate movement with speed multiplier
        effective_speed = self.speed * scroll_speed
        move_x = 0
        move_y = 0

        if keys[pan_up_key] or keys[pygame.K_UP]:
            move_y -= effective_speed * dt
        if keys[pan_down_key] or keys[pygame.K_DOWN]:
            move_y += effective_speed * dt
        if keys[pan_left_key] or keys[pygame.K_LEFT]:
            move_x -= effective_speed * dt
        if keys[pan_right_key] or keys[pygame.K_RIGHT]:
            move_x += effective_speed * dt

        # Apply movement
        self.x += move_x
        self.y += move_y

        # Clamp to bounds
        self.x = max(0, min(self.x, self.max_x))
        self.y = max(0, min(self.y, self.max_y))

    def _get_key_code(self, key_name: str) -> int:
        """Convert key name to pygame key code."""
        if not key_name:
            return pygame.K_UNKNOWN
        key_attr = f"K_{key_name.lower()}"
        return getattr(pygame, key_attr, pygame.K_UNKNOWN)

    def world_to_screen(self, world_x, world_y):
        """
        Convert world coordinates to screen coordinates.

        Args:
            world_x (float): X position in world
            world_y (float): Y position in world

        Returns:
            tuple: (screen_x, screen_y)
        """
        screen_x = world_x - self.x
        screen_y = world_y - self.y
        return (screen_x, screen_y)

    def screen_to_world(self, screen_x, screen_y):
        """
        Convert screen coordinates to world coordinates.

        Args:
            screen_x (int): X position on screen
            screen_y (int): Y position on screen

        Returns:
            tuple: (world_x, world_y)
        """
        world_x = screen_x + self.x
        world_y = screen_y + self.y
        return (world_x, world_y)

    def center_on(self, world_x, world_y):
        """
        Center the camera on a world position.

        Args:
            world_x (float): X position in world
            world_y (float): Y position in world
        """
        self.x = world_x - self.width // 2
        self.y = world_y - self.height // 2

        # Clamp to bounds
        self.x = max(0, min(self.x, self.max_x))
        self.y = max(0, min(self.y, self.max_y))

    def is_visible(self, world_x, world_y, width=0, height=0):
        """
        Check if a world position is visible on screen.

        Args:
            world_x (float): X position in world
            world_y (float): Y position in world
            width (int): Width of object (optional)
            height (int): Height of object (optional)

        Returns:
            bool: True if visible
        """
        # Check if position is within camera view
        if world_x + width < self.x or world_x > self.x + self.width:
            return False
        if world_y + height < self.y or world_y > self.y + self.height:
            return False
        return True

    def __repr__(self):
        """String representation for debugging."""
        return f"Camera(x={self.x:.1f}, y={self.y:.1f}, zoom={self.zoom})"
