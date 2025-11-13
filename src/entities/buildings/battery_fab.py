"""
Battery Fabrication - manufactures batteries from lithium and chemicals.
"""

from src.entities.buildings.processing_building import ProcessingBuilding


class BatteryFab(ProcessingBuilding):
    """
    Battery Fabrication Plant.

    Manufacturing building that combines lithium, chemicals, and metals to produce
    rechargeable batteries. Batteries are high-value components with growing demand.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the battery fabrication plant.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        config = {
            'name': 'Battery Fabrication',
            'cost': 20000,
            'max_level': 3,
            'power_consumption': 9.0,
            'processing_speed': 7.0,  # Careful chemical process
            'input_types': ['lithium', 'chemicals', 'copper', 'aluminum', 'plastic'],
            'efficiency': 0.88,
            'quality_distribution': {
                'waste': 0.12,   # Failed cells
                'low': 0.28,     # Low-capacity batteries
                'medium': 0.38,  # Standard batteries
                'high': 0.22     # High-capacity batteries
            },
            'max_input_queue': 1800,
            'max_output_queue': 1200,
            'color': (100, 140, 180),  # Battery blue
            'outline_color': (120, 160, 200)
        }

        super().__init__(grid_x, grid_y, width_tiles=4, height_tiles=4,
                        building_type="battery_fab", config=config)

        # Manufacturing requirements
        self.recipe = {
            'lithium': 1.0,    # 1 kg lithium
            'chemicals': 2.0,  # 2 kg electrolyte/chemicals
            'copper': 0.5,     # 0.5 kg copper for terminals
            'plastic': 0.5     # 0.5 kg plastic for casing
        }
        self.output_per_batch = 1.0  # kg of batteries
        self.batch_value_multiplier = 5.0  # Very high value
        self.hazard_level = 2  # Moderate hazard from chemicals

    def _apply_level_bonuses(self):
        """Apply bonuses based on current level."""
        super()._apply_level_bonuses()

        # Better yield per level
        self.output_per_batch = 1.0 + (self.level - 1) * 0.35

        # Better quality distribution (higher capacity)
        if self.level >= 2:
            self.quality_distribution['high'] += 0.10
            self.quality_distribution['medium'] += 0.05
            self.quality_distribution['low'] -= 0.10
            self.quality_distribution['waste'] -= 0.05

        if self.level >= 3:
            self.quality_distribution['high'] += 0.08
            self.quality_distribution['medium'] += 0.05
            self.quality_distribution['low'] -= 0.13

        # Reduce hazard level with upgrades
        self.hazard_level = max(0, 2 - (self.level - 1))

    def can_start_manufacturing(self):
        """
        Check if we have required materials to start manufacturing.

        Returns:
            bool: True if all recipe materials are available
        """
        material_counts = {}
        for item in self.input_queue:
            mat_type = item['material_type']
            # Allow aluminum as substitute for copper
            if mat_type == 'aluminum' and 'copper' not in material_counts:
                mat_type = 'copper'
            if mat_type in self.recipe:
                material_counts[mat_type] = material_counts.get(mat_type, 0.0) + item['quantity']

        # Check if we have enough of each required material
        for mat_type, required_amount in self.recipe.items():
            if material_counts.get(mat_type, 0.0) < required_amount:
                return False

        return True

    def update(self, dt):
        """
        Update the battery fabrication plant.

        Args:
            dt (float): Delta time in seconds
        """
        super().update(dt)

        # Check if we can start a new manufacturing batch
        if self.processing_current is None and self.can_start_manufacturing():
            # Consume recipe materials from queue
            # This would be implemented more fully in a complete system
            pass

    def __repr__(self):
        """String representation for debugging."""
        return (f"BatteryFab(level={self.level}, "
                f"queue={len(self.input_queue)}/{len(self.output_queue)}, "
                f"yield={self.output_per_batch:.1f}kg/batch, "
                f"hazard={self.hazard_level}, "
                f"pos=({self.grid_x}, {self.grid_y}))")
