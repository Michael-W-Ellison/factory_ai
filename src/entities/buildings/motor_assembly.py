"""
Motor Assembly - manufactures electric motors from iron, copper, and magnets.
"""

from src.entities.buildings.manufacturing_building import ManufacturingBuilding


class MotorAssembly(ManufacturingBuilding):
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
            'processing_speed': 10.0,  # Precision assembly (seconds per unit)
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
            'outline_color': (180, 180, 190),
            # Manufacturing-specific
            'recipe': {
                'iron': 3.0,     # 3 kg iron/steel for housing
                'copper': 1.5,   # 1.5 kg copper for windings
                'magnets': 0.5   # 0.5 kg magnetic materials
            },
            'output_component': 'electric_motor',
            'output_per_batch': 1.0,  # units per batch
            'batch_value_multiplier': 4.0
        }

        super().__init__(grid_x, grid_y, width_tiles=4, height_tiles=4,
                        building_type="motor_assembly", config=config)

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

    def __repr__(self):
        """String representation for debugging."""
        return (f"MotorAssembly(level={self.level}, "
                f"queue={len(self.input_queue)}/{len(self.output_queue)}, "
                f"yield={self.output_per_batch:.1f} motors/batch, "
                f"pos=({self.grid_x}, {self.grid_y}))")
