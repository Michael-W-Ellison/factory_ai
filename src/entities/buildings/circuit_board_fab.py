"""
Circuit Board Fabricator - manufactures circuit boards from copper and plastic.
"""

from src.entities.buildings.manufacturing_building import ManufacturingBuilding


class CircuitBoardFab(ManufacturingBuilding):
    """
    Circuit Board Fabricator.

    Manufacturing building that combines copper and plastic materials to produce
    electronic circuit boards. Requires multiple input materials and produces
    high-value electronic components.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the circuit board fabricator.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        config = {
            'name': 'Circuit Board Fabricator',
            'cost': 18000,
            'max_level': 3,
            'power_consumption': 10.0,
            'processing_speed': 8.0,  # Complex manufacturing (seconds per unit)
            'input_types': ['copper', 'plastic', 'chemicals', 'silver'],
            'efficiency': 0.92,
            'quality_distribution': {
                'waste': 0.08,   # Manufacturing defects
                'low': 0.20,     # Basic PCBs
                'medium': 0.45,  # Standard circuit boards
                'high': 0.27     # High-quality boards
            },
            'max_input_queue': 1500,
            'max_output_queue': 1000,
            'color': (40, 120, 40),  # Circuit board green
            'outline_color': (60, 140, 60),
            # Manufacturing-specific
            'recipe': {
                'copper': 2.0,   # 2 kg copper
                'plastic': 1.0,  # 1 kg plastic
                'chemicals': 0.5 # 0.5 kg chemicals (etchant)
            },
            'output_component': 'circuit_board',
            'output_per_batch': 1.0,  # units per batch
            'batch_value_multiplier': 3.0
        }

        super().__init__(grid_x, grid_y, width_tiles=4, height_tiles=4,
                        building_type="circuit_board_fab", config=config)

    def _apply_level_bonuses(self):
        """Apply bonuses based on current level."""
        super()._apply_level_bonuses()

        # Better yield per level
        self.output_per_batch = 1.0 + (self.level - 1) * 0.3

        # Better quality distribution
        if self.level >= 2:
            self.quality_distribution['high'] += 0.08
            self.quality_distribution['low'] -= 0.08

        if self.level >= 3:
            self.quality_distribution['high'] += 0.05
            self.quality_distribution['waste'] -= 0.05

    def __repr__(self):
        """String representation for debugging."""
        return (f"CircuitBoardFab(level={self.level}, "
                f"queue={len(self.input_queue)}/{len(self.output_queue)}, "
                f"yield={self.output_per_batch:.1f}kg/batch, "
                f"pos=({self.grid_x}, {self.grid_y}))")
