"""
Circuit Board Fabricator - manufactures circuit boards from copper and plastic.
"""

from src.entities.buildings.processing_building import ProcessingBuilding


class CircuitBoardFab(ProcessingBuilding):
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
            'processing_speed': 8.0,  # Complex manufacturing
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
            'outline_color': (60, 140, 60)
        }

        super().__init__(grid_x, grid_y, width_tiles=4, height_tiles=4,
                        building_type="circuit_board_fab", config=config)

        # Manufacturing requirements
        self.recipe = {
            'copper': 2.0,   # 2 kg copper
            'plastic': 1.0,  # 1 kg plastic
            'chemicals': 0.5 # 0.5 kg chemicals (etchant)
        }
        self.output_per_batch = 1.0  # kg of circuit boards
        self.batch_value_multiplier = 3.0  # High value output

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

    def can_start_manufacturing(self):
        """
        Check if we have required materials to start manufacturing.

        Returns:
            bool: True if all recipe materials are available
        """
        # Check if we have at least one recipe worth of materials
        material_counts = {}
        for item in self.input_queue:
            mat_type = item['material_type']
            if mat_type in self.recipe:
                material_counts[mat_type] = material_counts.get(mat_type, 0.0) + item['quantity']

        # Check if we have enough of each required material
        for mat_type, required_amount in self.recipe.items():
            if material_counts.get(mat_type, 0.0) < required_amount:
                return False

        return True

    def update(self, dt):
        """
        Update the circuit board fabricator.

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
        return (f"CircuitBoardFab(level={self.level}, "
                f"queue={len(self.input_queue)}/{len(self.output_queue)}, "
                f"yield={self.output_per_batch:.1f}kg/batch, "
                f"pos=({self.grid_x}, {self.grid_y}))")
