"""
Bio-Waste Treatment Plant - processes organic materials.
"""

from src.entities.buildings.processing_building import ProcessingBuilding


class BioWasteTreatment(ProcessingBuilding):
    """
    Bio-Waste Treatment Plant.

    Processes organic materials into bio-slop (fertilizer) and produces methane gas.
    Helps reduce pollution and creates valuable byproducts.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the bio-waste treatment plant.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        config = {
            'name': 'Bio-Waste Treatment Plant',
            'cost': 8000,
            'max_level': 3,
            'power_consumption': 4.0,
            'processing_speed': 2.0,  # Fast processing for organic waste
            'input_types': ['organic', 'wood', 'textiles', 'bio_waste'],
            'efficiency': 0.90,  # High efficiency
            'quality_distribution': {
                'waste': 0.10,  # Minimal waste
                'low': 0.50,    # Mostly bio-slop
                'medium': 0.30, # Some methane
                'high': 0.10    # Pure methane
            },
            'max_input_queue': 1500,
            'max_output_queue': 1500,
            'color': (100, 140, 70),  # Greenish-brown
            'outline_color': (70, 100, 40)
        }

        super().__init__(grid_x, grid_y, width_tiles=4, height_tiles=4,
                        building_type="bio_waste_treatment", config=config)

        # Special outputs
        self.methane_production_rate = 0.5  # kg methane per kg input
        self.pollution_reduction = -2.0  # Reduces pollution!

    def _apply_level_bonuses(self):
        """Apply bonuses based on current level."""
        super()._apply_level_bonuses()

        # Better methane production per level
        self.methane_production_rate = 0.5 + (self.level - 1) * 0.2

        # Greater pollution reduction per level
        self.pollution_reduction = -2.0 - (self.level - 1) * 0.5

    def update(self, dt):
        """
        Update the bio-waste treatment plant.

        Args:
            dt (float): Delta time in seconds
        """
        super().update(dt)

        # Actively reduces pollution in the area (future feature)
        # Could integrate with pollution system when implemented

    def __repr__(self):
        """String representation for debugging."""
        return (f"BioWasteTreatment(level={self.level}, "
                f"queue={len(self.input_queue)}/{len(self.output_queue)}, "
                f"methane={self.methane_production_rate:.1f}kg/kg, "
                f"pos=({self.grid_x}, {self.grid_y}))")
