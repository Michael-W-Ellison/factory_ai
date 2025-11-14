"""
CollectibleObject - materials that can be collected by robots.
"""

import pygame
from src.entities.entity import Entity
from src.systems.material_inventory import MaterialSource


class CollectibleObject(Entity):
    """
    Represents a collectible material object in the world.

    These are materials lying in the landfill or debris that robots can collect.
    """

    def __init__(self, x, y, material_type, quantity, source=MaterialSource.LANDFILL):
        """
        Initialize a collectible object.

        Args:
            x (float): World X position
            y (float): World Y position
            material_type (str): Type of material (plastic, metal, glass, etc.)
            quantity (float): Amount in kg
            source (MaterialSource): Source of the material (default: LANDFILL for legal materials)
        """
        # Size varies slightly by material type
        size = self._get_size_for_quantity(quantity)
        super().__init__(x, y, width=size, height=size)

        self.material_type = material_type
        self.quantity = quantity
        self.source = source  # Track material source for inspection system

        # Visual
        self.color = self._get_color_for_material(material_type)

    def _get_color_for_material(self, material_type):
        """Get color based on material type."""
        color_map = {
            'plastic': (255, 100, 100),      # Red
            'metal': (180, 180, 180),        # Gray
            'glass': (100, 200, 255),        # Light blue
            'paper': (245, 222, 179),        # Wheat
            'rubber': (50, 50, 50),          # Dark gray
            'organic': (139, 90, 43),        # Brown
            'wood': (160, 82, 45),           # Sienna
            'electronic': (100, 149, 237),   # Cornflower blue
        }
        return color_map.get(material_type, (255, 255, 255))

    def _get_size_for_quantity(self, quantity):
        """Calculate visual size based on quantity."""
        # Small objects (5-20kg) = 12-20 pixels
        # Medium objects (20-50kg) = 20-28 pixels
        # Large objects (50+kg) = 28-32 pixels
        if quantity < 20:
            return int(12 + (quantity / 20) * 8)
        elif quantity < 50:
            return int(20 + ((quantity - 20) / 30) * 8)
        else:
            return min(32, int(28 + ((quantity - 50) / 50) * 4))

    def collect(self, amount):
        """
        Collect some or all of this material.

        Args:
            amount (float): Amount to collect in kg

        Returns:
            float: Amount actually collected
        """
        collected = min(amount, self.quantity)
        self.quantity -= collected

        # Mark for removal if fully collected
        if self.quantity <= 0:
            self.active = False

        return collected

    def render(self, screen, camera):
        """
        Render collectible object to screen.

        Args:
            screen: Pygame surface
            camera: Camera object
        """
        if not self.visible:
            return

        screen_x, screen_y = camera.world_to_screen(self.x, self.y)

        if camera.is_visible(self.x, self.y, self.width, self.height):
            # Draw as a circle for organic materials
            if self.material_type in ['organic', 'rubber', 'plastic']:
                center_x = int(screen_x + self.width / 2)
                center_y = int(screen_y + self.height / 2)
                radius = int(self.width / 2)
                pygame.draw.circle(screen, self.color, (center_x, center_y), radius)
                # Dark outline
                pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), radius, 1)
            else:
                # Draw as a rectangle for other materials
                rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
                pygame.draw.rect(screen, self.color, rect)
                # Dark outline
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)

    def __repr__(self):
        """String representation for debugging."""
        return (f"CollectibleObject(id={self.id}, type={self.material_type}, "
                f"qty={self.quantity:.1f}kg, pos=({self.x:.0f}, {self.y:.0f}))")
