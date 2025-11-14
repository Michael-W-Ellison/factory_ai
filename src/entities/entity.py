"""
Base Entity class - all game objects inherit from this.
"""

import pygame


class Entity:
    """
    Base class for all game entities (robots, objects, buildings, NPCs, etc.).

    Entities exist in the game world and have a position on the grid.
    """

    # Class variable for generating unique IDs
    _next_id = 0

    def __init__(self, x, y, width=32, height=32):
        """
        Initialize an entity.

        Args:
            x (float): World X position (pixels)
            y (float): World Y position (pixels)
            width (int): Width in pixels
            height (int): Height in pixels
        """
        # Unique ID for this entity
        self.id = Entity._next_id
        Entity._next_id += 1

        # Position in world coordinates (pixels)
        self.x = float(x)
        self.y = float(y)

        # Size
        self.width = width
        self.height = height

        # Visual properties
        self.color = (255, 255, 255)  # Default white
        self.visible = True

        # State
        self.active = True  # If False, entity will be removed

    def update(self, dt):
        """
        Update entity state.

        Args:
            dt (float): Delta time in seconds
        """
        pass

    def render(self, screen, camera):
        """
        Render entity to screen.

        Args:
            screen: Pygame surface
            camera: Camera object for coordinate transformation
        """
        if not self.visible:
            return

        # Convert world coordinates to screen coordinates
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)

        # Only render if visible on screen
        if camera.is_visible(self.x, self.y, self.width, self.height):
            # Draw as a rectangle by default (subclasses can override)
            rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
            pygame.draw.rect(screen, self.color, rect)

    def get_center(self):
        """
        Get center position of entity.

        Returns:
            tuple: (center_x, center_y)
        """
        return (self.x + self.width / 2, self.y + self.height / 2)

    def get_grid_position(self, tile_size):
        """
        Get grid coordinates of entity's center.

        Args:
            tile_size (int): Size of tiles in pixels

        Returns:
            tuple: (grid_x, grid_y)
        """
        center_x, center_y = self.get_center()
        grid_x = int(center_x // tile_size)
        grid_y = int(center_y // tile_size)
        return (grid_x, grid_y)

    def collides_with(self, other):
        """
        Check if this entity collides with another entity.

        Args:
            other (Entity): Another entity

        Returns:
            bool: True if colliding
        """
        # AABB (Axis-Aligned Bounding Box) collision detection
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)

    def distance_to(self, other):
        """
        Calculate distance to another entity (center to center).

        Args:
            other (Entity): Another entity

        Returns:
            float: Distance in pixels
        """
        my_center = self.get_center()
        other_center = other.get_center()
        dx = my_center[0] - other_center[0]
        dy = my_center[1] - other_center[1]
        return (dx * dx + dy * dy) ** 0.5

    def __repr__(self):
        """String representation for debugging."""
        return f"{self.__class__.__name__}(id={self.id}, pos=({self.x:.0f}, {self.y:.0f}))"
