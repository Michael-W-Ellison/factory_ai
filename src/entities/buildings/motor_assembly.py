"""
Motor Assembly - manufactures electric motors from iron, copper, and magnets.
"""

from src.entities.buildings.processing_building import ProcessingBuilding


class MotorAssembly(ProcessingBuilding):
    """
    Motor Assembly Plant.

    Manufacturing building that combines iron, copper, and magnetic materials to
    produce electric motors. Motors are valuable components used in various products.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the motor assembly plant.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        config = {
            'name': 'Motor Assembly',
            'cost': 16000,
            'max_level': 3,
            'power_consumption': 7.0,
            'processing_speed': 10.0,  # Precision assembly
            'input_types': ['iron', 'steel', 'copper', 'magnets', 'aluminum'],
            'efficiency': 0.90,
            'quality_distribution': {
                'waste': 0.10,   # Damaged/defective motors
                'low': 0.25,     # Low-power motors
                'medium': 0.40,  # Standard motors
                'high': 0.25     # High-efficiency motors
            },
            'max_input_queue': 2000,
            'max_output_queue': 1200,
            'color': (150, 150, 160),  # Metallic gray
            'outline_color': (180, 180, 190)
        }

        super().__init__(grid_x, grid_y, width_tiles=4, height_tiles=4,
                        building_type="motor_assembly", config=config)

        # Manufacturing requirements
        self.recipe = {
            'iron': 3.0,     # 3 kg iron/steel for housing
            'copper': 1.5,   # 1.5 kg copper for windings
            'magnets': 0.5   # 0.5 kg magnetic materials
        }
        self.output_per_batch = 1.0  # 1 motor per batch
        self.batch_value_multiplier = 4.0  # Very high value output

    def _apply_level_bonuses(self):
        """Apply bonuses based on current level."""
        super()._apply_level_bonuses()

        # Better yield per level
        self.output_per_batch = 1.0 + (self.level - 1) * 0.25

        # Better quality distribution
        if self.level >= 2:
            self.quality_distribution['high'] += 0.10
            self.quality_distribution['waste'] -= 0.05
            self.quality_distribution['low'] -= 0.05

        if self.level >= 3:
            self.quality_distribution['high'] += 0.10
            self.quality_distribution['medium'] += 0.05
            self.quality_distribution['low'] -= 0.15

    def can_start_manufacturing(self):
        """
        Check if we have required materials to start manufacturing.

        Returns:
            bool: True if all recipe materials are available
        """
        material_counts = {}
        for item in self.input_queue:
            mat_type = item['material_type']
            # Allow steel as substitute for iron
            if mat_type == 'steel':
                mat_type = 'iron'
            if mat_type in self.recipe:
                material_counts[mat_type] = material_counts.get(mat_type, 0.0) + item['quantity']

        # Check if we have enough of each required material
        for mat_type, required_amount in self.recipe.items():
            if material_counts.get(mat_type, 0.0) < required_amount:
                return False

        return True

    def update(self, dt):
        """
        Update the motor assembly plant.

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
        return (f"MotorAssembly(level={self.level}, "
                f"queue={len(self.input_queue)}/{len(self.output_queue)}, "
                f"yield={self.output_per_batch:.1f} motors/batch, "
                f"pos=({self.grid_x}, {self.grid_y}))")
