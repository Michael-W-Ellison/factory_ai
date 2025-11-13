"""
Factory building - the core control center.
"""

from src.entities.building import Building
from src.core.constants import Colors


class Factory(Building):
    """
    Factory Control Center.

    The core building that serves as:
    - Robot command center
    - Basic material storage
    - Basic processing (inefficient)
    - Factory return point for robots
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the factory.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        super().__init__(grid_x, grid_y, width_tiles=5, height_tiles=5, building_type="factory")

        # Factory-specific properties
        self.name = "Factory Control Center"
        self.max_level = 5
        self.level = 1

        # Power
        self.power_consumption = 5.0  # Base power consumption

        # Storage
        self.storage_capacity = 10000.0  # kg
        self.stored_materials = {}  # material_type -> quantity

        # Processing (very slow, inefficient)
        self.processing_speed = 10.0  # seconds per kg
        self.processing_efficiency = 0.5  # 50% efficiency (lots of waste)

        # Visual
        self.color = Colors.FACTORY_COLOR
        self.outline_color = (60, 60, 100)

        # Already constructed (starting building)
        self.under_construction = False
        self.construction_progress = 100.0

    def _apply_level_bonuses(self):
        """Apply bonuses for current level."""
        # Each level improves storage, processing speed, and efficiency
        self.storage_capacity = 10000.0 * self.level
        self.processing_speed = 10.0 / (1.0 + (self.level - 1) * 0.3)  # Faster processing
        self.processing_efficiency = 0.5 + (self.level - 1) * 0.1  # Better efficiency
        self.power_consumption = 5.0 + (self.level - 1) * 2.0  # More power needed

    def can_store(self, quantity):
        """
        Check if factory has space to store material.

        Args:
            quantity (float): Amount to store in kg

        Returns:
            bool: True if space available
        """
        current_storage = sum(self.stored_materials.values())
        return (current_storage + quantity) <= self.storage_capacity

    def store_material(self, material_type, quantity):
        """
        Store material in factory.

        Args:
            material_type (str): Type of material
            quantity (float): Amount in kg

        Returns:
            float: Amount actually stored
        """
        current_storage = sum(self.stored_materials.values())
        available_space = self.storage_capacity - current_storage
        amount_to_store = min(quantity, available_space)

        if amount_to_store > 0:
            if material_type not in self.stored_materials:
                self.stored_materials[material_type] = 0.0
            self.stored_materials[material_type] += amount_to_store

        return amount_to_store

    def get_material(self, material_type, quantity):
        """
        Retrieve material from factory storage.

        Args:
            material_type (str): Type of material
            quantity (float): Amount requested in kg

        Returns:
            float: Amount actually retrieved
        """
        available = self.stored_materials.get(material_type, 0.0)
        amount_to_retrieve = min(quantity, available)

        if amount_to_retrieve > 0:
            self.stored_materials[material_type] -= amount_to_retrieve

        return amount_to_retrieve

    def get_storage_info(self):
        """
        Get storage information.

        Returns:
            dict: Storage information
        """
        current_storage = sum(self.stored_materials.values())
        return {
            'current': current_storage,
            'capacity': self.storage_capacity,
            'percent_full': (current_storage / self.storage_capacity * 100.0) if self.storage_capacity > 0 else 0,
            'materials': self.stored_materials.copy()
        }

    def _start_processing(self):
        """Start processing material from input queue."""
        if not self.input_queue:
            return

        item = self.input_queue.pop(0)
        self.processing_current = item
        # Processing time based on quantity and speed
        self.processing_time_remaining = item['quantity'] * self.processing_speed

    def _finish_processing(self):
        """Finish processing current item."""
        if self.processing_current is None:
            return

        material_type = self.processing_current['material_type']
        quantity = self.processing_current['quantity']

        # Apply efficiency (rest is waste)
        output_quantity = quantity * self.processing_efficiency
        waste_quantity = quantity - output_quantity

        # Add to output queue
        if output_quantity > 0:
            self.output_queue.append({
                'material_type': f"processed_{material_type}",
                'quantity': output_quantity
            })

        # Waste is lost
        print(f"Factory processed {quantity:.1f}kg of {material_type} -> {output_quantity:.1f}kg output, {waste_quantity:.1f}kg waste")

        # Clear current processing
        self.processing_current = None
        self.processing_time_remaining = 0.0

    def render(self, screen, camera):
        """
        Render factory with special appearance.

        Args:
            screen: Pygame surface
            camera: Camera object
        """
        super().render(screen, camera)

        # Additional rendering for factory-specific features
        if not self.under_construction and camera.is_visible(self.x, self.y, self.width, self.height):
            import pygame
            screen_x, screen_y = camera.world_to_screen(self.x, self.y)

            # Show storage fill level as a bar
            storage_info = self.get_storage_info()
            fill_percent = storage_info['percent_full'] / 100.0

            bar_width = self.width - 8
            bar_height = 6
            bar_x = screen_x + 4
            bar_y = screen_y + self.height - bar_height - 4

            # Background
            pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))

            # Fill
            fill_width = int(bar_width * fill_percent)
            fill_color = (0, 255, 0) if fill_percent < 0.8 else (255, 100, 0)
            if fill_width > 0:
                pygame.draw.rect(screen, fill_color, (bar_x, bar_y, fill_width, bar_height))

    def get_info(self):
        """Get factory information including storage."""
        info = super().get_info()
        info.update(self.get_storage_info())
        return info

    def __repr__(self):
        """String representation for debugging."""
        storage_info = self.get_storage_info()
        return (f"Factory(level={self.level}, storage={storage_info['current']:.0f}/{self.storage_capacity:.0f}kg, "
                f"pos=({self.grid_x}, {self.grid_y}))")
