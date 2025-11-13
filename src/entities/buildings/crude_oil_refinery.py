"""
Crude Oil Refinery - processes petroleum and oil-based materials.
"""

from src.entities.buildings.processing_building import ProcessingBuilding


class CrudeOilRefinery(ProcessingBuilding):
    """
    Crude Oil Refinery.

    Processes crude oil, petroleum, and oil-contaminated materials into refined products
    like diesel, gasoline, lubricants, and petrochemicals. High-value outputs but requires
    significant power and generates pollution.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the crude oil refinery.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        config = {
            'name': 'Crude Oil Refinery',
            'cost': 15000,
            'max_level': 3,
            'power_consumption': 8.0,
            'processing_speed': 5.0,  # Complex refining process
            'input_types': ['petroleum', 'oil', 'lubricants', 'plastic', 'rubber'],
            'efficiency': 0.85,
            'quality_distribution': {
                'waste': 0.10,   # Tar and heavy residues
                'low': 0.25,     # Low-grade fuel oil
                'medium': 0.40,  # Diesel and kerosene
                'high': 0.25     # High-grade gasoline and petrochemicals
            },
            'max_input_queue': 3000,
            'max_output_queue': 2500,
            'color': (80, 80, 100),  # Steel blue-gray
            'outline_color': (100, 100, 120)
        }

        super().__init__(grid_x, grid_y, width_tiles=5, height_tiles=5,
                        building_type="crude_oil_refinery", config=config)

        # Special attributes
        self.refining_efficiency = 0.85
        self.pollution_output = 4.0  # High pollution from refining
        self.valuable_byproducts = ['gasoline', 'diesel', 'petrochemicals']

    def _apply_level_bonuses(self):
        """Apply bonuses based on current level."""
        super()._apply_level_bonuses()

        # Better refining efficiency per level
        self.refining_efficiency = 0.85 + (self.level - 1) * 0.05

        # Better quality distribution (more high-grade outputs)
        if self.level >= 2:
            self.quality_distribution['high'] += 0.10
            self.quality_distribution['low'] -= 0.10

        if self.level >= 3:
            self.quality_distribution['high'] += 0.05
            self.quality_distribution['waste'] -= 0.05

    def update(self, dt):
        """
        Update the crude oil refinery.

        Args:
            dt (float): Delta time in seconds
        """
        super().update(dt)

        # Generate pollution when processing
        if self.processing_current is not None:
            # Active processing generates more pollution
            pass  # Future pollution system integration

    def __repr__(self):
        """String representation for debugging."""
        return (f"CrudeOilRefinery(level={self.level}, "
                f"queue={len(self.input_queue)}/{len(self.output_queue)}, "
                f"efficiency={self.refining_efficiency:.1%}, "
                f"pollution={self.pollution_output:.1f}, "
                f"pos=({self.grid_x}, {self.grid_y}))")
