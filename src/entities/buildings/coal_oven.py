"""
Coal Oven - converts wood into charcoal and coal products.
"""

from src.entities.buildings.processing_building import ProcessingBuilding


class CoalOven(ProcessingBuilding):
    """
    Coal Oven.

    Processes wood and organic materials through pyrolysis to produce charcoal and coal.
    Can also process bio-waste into fuel. Produces valuable fuel products but generates
    some pollution.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the coal oven.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        config = {
            'name': 'Coal Oven',
            'cost': 6000,
            'max_level': 3,
            'power_consumption': 3.0,
            'processing_speed': 4.0,  # Slow heating process
            'input_types': ['wood', 'organic', 'textiles', 'bio_waste'],
            'efficiency': 0.80,
            'quality_distribution': {
                'waste': 0.15,   # Ash and residue
                'low': 0.40,     # Low-grade charcoal
                'medium': 0.30,  # Standard charcoal
                'high': 0.15     # High-grade coal
            },
            'max_input_queue': 2000,
            'max_output_queue': 1500,
            'color': (60, 60, 60),  # Dark gray
            'outline_color': (90, 90, 90)
        }

        super().__init__(grid_x, grid_y, width_tiles=3, height_tiles=3,
                        building_type="coal_oven", config=config)

        # Special attributes
        self.charcoal_yield = 0.40  # 40% of input becomes charcoal
        self.pollution_output = 2.0  # Moderate pollution
        self.heat_output = 5.0  # Heat generated (could power other buildings)

    def _apply_level_bonuses(self):
        """Apply bonuses based on current level."""
        super()._apply_level_bonuses()

        # Better charcoal yield per level
        self.charcoal_yield = 0.40 + (self.level - 1) * 0.10

        # Less pollution per level (better sealing)
        self.pollution_output = 2.0 - (self.level - 1) * 0.3

    def update(self, dt):
        """
        Update the coal oven.

        Args:
            dt (float): Delta time in seconds
        """
        super().update(dt)

        # Generate heat when processing (future feature)
        # Could be used to provide heat energy to nearby buildings

    def __repr__(self):
        """String representation for debugging."""
        return (f"CoalOven(level={self.level}, "
                f"queue={len(self.input_queue)}/{len(self.output_queue)}, "
                f"yield={self.charcoal_yield:.1%}, "
                f"pollution={self.pollution_output:.1f}, "
                f"pos=({self.grid_x}, {self.grid_y}))")
