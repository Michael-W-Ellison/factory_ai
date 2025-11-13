"""
Warehouse - general purpose storage building.
"""

from src.entities.building import Building


class Warehouse(Building):
    """
    Warehouse.

    General purpose storage for any material type.
    Can store multiple different materials simultaneously.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the warehouse.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        super().__init__(grid_x, grid_y, width_tiles=4, height_tiles=4,
                        building_type="warehouse")

        # Warehouse-specific attributes
        self.name = "Warehouse"
        self.base_cost = 3000
        self.max_level = 3

        # Storage
        self.base_storage_capacity = 50000.0  # kg
        self.storage_capacity = self.base_storage_capacity
        self.stored_materials = {}  # material_type -> quantity

        # Power
        self.power_consumption = 1.0  # Minimal power for lighting/climate control

        # Appearance
        self.color = (180, 140, 100)  # Brown/tan
        self.outline_color = (130, 90, 50)

        self._apply_level_bonuses()

    def store_material(self, material_type, quantity):
        """
        Store material in the warehouse.

        Args:
            material_type (str): The material type to store
            quantity (float): Amount in kg to store

        Returns:
            float: Amount actually stored
        """
        current_storage = sum(self.stored_materials.values())
        available_space = self.storage_capacity - current_storage

        if available_space <= 0:
            return 0.0

        amount_to_store = min(quantity, available_space)

        if amount_to_store > 0:
            self.stored_materials[material_type] = \
                self.stored_materials.get(material_type, 0.0) + amount_to_store

        return amount_to_store

    def get_material(self, material_type, quantity):
        """
        Retrieve material from the warehouse.

        Args:
            material_type (str): The material type to retrieve
            quantity (float): Amount in kg to retrieve

        Returns:
            float: Amount actually retrieved
        """
        available = self.stored_materials.get(material_type, 0.0)

        if available <= 0:
            return 0.0

        amount_to_get = min(quantity, available)
        self.stored_materials[material_type] -= amount_to_get

        if self.stored_materials[material_type] <= 0:
            del self.stored_materials[material_type]

        return amount_to_get

    def get_stored_amount(self, material_type):
        """
        Get the amount of a specific material stored.

        Args:
            material_type (str): The material type to check

        Returns:
            float: Amount stored in kg
        """
        return self.stored_materials.get(material_type, 0.0)

    def get_total_stored(self):
        """
        Get total weight of all materials stored.

        Returns:
            float: Total weight in kg
        """
        return sum(self.stored_materials.values())

    def get_available_space(self):
        """
        Get remaining storage capacity.

        Returns:
            float: Available space in kg
        """
        return self.storage_capacity - self.get_total_stored()

    def get_fill_percentage(self):
        """
        Get storage fill percentage.

        Returns:
            float: Percentage full (0.0 to 1.0)
        """
        if self.storage_capacity <= 0:
            return 0.0
        return self.get_total_stored() / self.storage_capacity

    def _apply_level_bonuses(self):
        """Apply bonuses based on current level."""
        # Level 1: 50,000kg
        # Level 2: 75,000kg (+50%)
        # Level 3: 100,000kg (+100%)
        capacity_multiplier = 1.0 + (self.level - 1) * 0.5
        self.storage_capacity = self.base_storage_capacity * capacity_multiplier

        # Slight power increase per level (climate control for more space)
        self.power_consumption = 1.0 + (self.level - 1) * 0.5

    def update(self, dt):
        """
        Update the warehouse.

        Args:
            dt (float): Delta time in seconds
        """
        super().update(dt)

        # Warehouses don't have processing, just maintain storage
        # Could add spoilage for organic materials in future

    def render(self, screen, camera):
        """
        Render the warehouse.

        Args:
            screen: Pygame screen surface
            camera: Camera object for coordinate conversion
        """
        super().render(screen, camera)

        # TODO: Add fill level indicator (visual bar showing how full)
        # TODO: Add icons showing stored material types

    def __repr__(self):
        """String representation for debugging."""
        return (f"Warehouse(level={self.level}, "
                f"storage={self.get_total_stored():.0f}/{self.storage_capacity:.0f}kg, "
                f"types={len(self.stored_materials)}, "
                f"pos=({self.grid_x}, {self.grid_y}))")
