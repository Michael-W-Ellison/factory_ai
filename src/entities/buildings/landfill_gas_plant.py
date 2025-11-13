"""
Landfill Gas Plant - converts bio-slop and organic waste into methane.
"""

from src.entities.buildings.processing_building import ProcessingBuilding


class LandfillGasPlant(ProcessingBuilding):
    """
    Landfill Gas Plant.

    Processes bio-slop, organic waste, and food waste through anaerobic digestion to
    produce methane gas. The methane can be used as fuel for power generation or sold.
    Environmentally friendly and reduces pollution.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the landfill gas plant.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        config = {
            'name': 'Landfill Gas Plant',
            'cost': 9000,
            'max_level': 3,
            'power_consumption': 2.0,
            'processing_speed': 6.0,  # Slow digestion process
            'input_types': ['bio_waste', 'organic', 'food_waste', 'bio_slop'],
            'efficiency': 0.88,
            'quality_distribution': {
                'waste': 0.12,   # Solid digestate
                'low': 0.30,     # Impure biogas
                'medium': 0.38,  # Standard methane
                'high': 0.20     # Pure methane
            },
            'max_input_queue': 2500,
            'max_output_queue': 2000,
            'color': (140, 160, 80),  # Yellow-green
            'outline_color': (110, 130, 60)
        }

        super().__init__(grid_x, grid_y, width_tiles=4, height_tiles=4,
                        building_type="landfill_gas_plant", config=config)

        # Special attributes
        self.methane_production_rate = 0.60  # kg methane per kg input
        self.pollution_reduction = -1.5  # Reduces pollution
        self.digestate_production = 0.25  # Solid fertilizer byproduct

    def _apply_level_bonuses(self):
        """Apply bonuses based on current level."""
        super()._apply_level_bonuses()

        # Better methane yield per level
        self.methane_production_rate = 0.60 + (self.level - 1) * 0.10

        # More pollution reduction per level
        self.pollution_reduction = -1.5 - (self.level - 1) * 0.5

        # Better quality distribution (more pure methane)
        if self.level >= 2:
            self.quality_distribution['high'] += 0.10
            self.quality_distribution['low'] -= 0.10

    def update(self, dt):
        """
        Update the landfill gas plant.

        Args:
            dt (float): Delta time in seconds
        """
        super().update(dt)

        # Actively reduces pollution in the area
        # Future integration with pollution system

    def get_methane_output(self, input_quantity):
        """
        Calculate expected methane output for given input.

        Args:
            input_quantity (float): Input material in kg

        Returns:
            float: Expected methane output in kg
        """
        return input_quantity * self.methane_production_rate * self.efficiency

    def __repr__(self):
        """String representation for debugging."""
        return (f"LandfillGasPlant(level={self.level}, "
                f"queue={len(self.input_queue)}/{len(self.output_queue)}, "
                f"methane={self.methane_production_rate:.1%}, "
                f"pollution={self.pollution_reduction:.1f}, "
                f"pos=({self.grid_x}, {self.grid_y}))")
