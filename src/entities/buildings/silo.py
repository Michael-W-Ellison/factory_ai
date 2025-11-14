"""
Silo - bulk storage for a single material type.
"""

from src.entities.building import Building


class Silo(Building):
    """
    Silo.

    Bulk storage for a single material type.
    Higher capacity than warehouse but can only store one material at a time.
    Faster loading and unloading speed.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the silo.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        super().__init__(grid_x, grid_y, width_tiles=3, height_tiles=3,
                        building_type="silo")

        # Silo-specific attributes
        self.name = "Silo"
        self.base_cost = 5000
        self.max_level = 3

        # Storage - single material type
        self.base_storage_capacity = 100000.0  # kg (2x warehouse capacity)
        self.storage_capacity = self.base_storage_capacity
        self.stored_material_type = None  # Only one material type allowed
        self.stored_quantity = 0.0

        # Loading/unloading speed
        self.base_transfer_speed = 100.0  # kg/sec (fast loading)
        self.transfer_speed = self.base_transfer_speed

        # Power
        self.power_consumption = 2.0  # Slightly more than warehouse (conveyor systems)

        # Appearance
        self.color = (160, 160, 160)  # Gray (metal silo)
        self.outline_color = (100, 100, 100)

        self._apply_level_bonuses()

    def store_material(self, material_type, quantity):
        """
        Store material in the silo.

        Args:
            material_type (str): The material type to store
            quantity (float): Amount in kg to store

        Returns:
            float: Amount actually stored
        """
        # Check if silo is empty or already storing this material
        if self.stored_material_type is None:
            # Empty silo - accept this material type
            self.stored_material_type = material_type
        elif self.stored_material_type != material_type:
            # Different material - reject
            return 0.0

        # Calculate available space
        available_space = self.storage_capacity - self.stored_quantity

        if available_space <= 0:
            return 0.0

        amount_to_store = min(quantity, available_space)

        if amount_to_store > 0:
            self.stored_quantity += amount_to_store

        return amount_to_store

    def get_material(self, material_type, quantity):
        """
        Retrieve material from the silo.

        Args:
            material_type (str): The material type to retrieve
            quantity (float): Amount in kg to retrieve

        Returns:
            float: Amount actually retrieved
        """
        # Check if requesting the right material
        if self.stored_material_type != material_type:
            return 0.0

        if self.stored_quantity <= 0:
            return 0.0

        amount_to_get = min(quantity, self.stored_quantity)
        self.stored_quantity -= amount_to_get

        # If silo is now empty, reset material type
        if self.stored_quantity <= 0:
            self.stored_quantity = 0.0
            self.stored_material_type = None

        return amount_to_get

    def get_stored_amount(self, material_type=None):
        """
        Get the amount stored.

        Args:
            material_type (str, optional): The material type to check (for compatibility)

        Returns:
            float: Amount stored in kg
        """
        if material_type is None:
            return self.stored_quantity

        if self.stored_material_type == material_type:
            return self.stored_quantity

        return 0.0

    def get_total_stored(self):
        """
        Get total weight stored.

        Returns:
            float: Total weight in kg
        """
        return self.stored_quantity

    def get_available_space(self):
        """
        Get remaining storage capacity.

        Returns:
            float: Available space in kg
        """
        return self.storage_capacity - self.stored_quantity

    def get_fill_percentage(self):
        """
        Get storage fill percentage.

        Returns:
            float: Percentage full (0.0 to 1.0)
        """
        if self.storage_capacity <= 0:
            return 0.0
        return self.stored_quantity / self.storage_capacity

    def clear_silo(self):
        """
        Clear the silo (for testing or manual emptying).
        Materials are lost - use get_material() to retrieve safely.
        """
        self.stored_material_type = None
        self.stored_quantity = 0.0

    def _apply_level_bonuses(self):
        """Apply bonuses based on current level."""
        # Level 1: 100,000kg
        # Level 2: 150,000kg (+50%)
        # Level 3: 200,000kg (+100%)
        capacity_multiplier = 1.0 + (self.level - 1) * 0.5
        self.storage_capacity = self.base_storage_capacity * capacity_multiplier

        # Faster transfer speed per level
        # Level 1: 100 kg/sec
        # Level 2: 150 kg/sec
        # Level 3: 200 kg/sec
        speed_multiplier = 1.0 + (self.level - 1) * 0.5
        self.transfer_speed = self.base_transfer_speed * speed_multiplier

        # Power consumption increases with level (more automation)
        self.power_consumption = 2.0 + (self.level - 1) * 1.0

    def update(self, dt):
        """
        Update the silo.

        Args:
            dt (float): Delta time in seconds
        """
        super().update(dt)

        # Silos don't have active processing, just maintain storage
        # Transfer speed is used by robots/conveyors during loading/unloading

    def render(self, screen, camera):
        """
        Render the silo.

        Args:
            screen: Pygame screen surface
            camera: Camera object for coordinate conversion
        """
        super().render(screen, camera)

        # TODO: Add fill level indicator (vertical bar showing fill)
        # TODO: Add material type icon/label
        # TODO: Show transfer rate indicator when actively loading/unloading

    def __repr__(self):
        """String representation for debugging."""
        material_str = self.stored_material_type if self.stored_material_type else "empty"
        return (f"Silo(level={self.level}, "
                f"storage={self.stored_quantity:.0f}/{self.storage_capacity:.0f}kg, "
                f"material={material_str}, "
                f"pos=({self.grid_x}, {self.grid_y}))")
