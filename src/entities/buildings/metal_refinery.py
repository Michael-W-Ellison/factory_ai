"""
Metal Refinery - processes metal materials.
"""

from src.entities.buildings.processing_building import ProcessingBuilding


class MetalRefinery(ProcessingBuilding):
    """
    Metal Refinery.

    Processes various metals into quality-sorted metal products.
    High power consumption, slower processing, but produces valuable output.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the metal refinery.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        config = {
            'name': 'Metal Refinery',
            'cost': 12000,
            'max_level': 3,
            'power_consumption': 8.0,  # High power consumption
            'processing_speed': 6.0,  # seconds per kg (slow)
            'input_types': ['metal', 'aluminum', 'steel', 'copper', 'iron'],
            'efficiency': 0.90,  # High efficiency for metals
            'quality_distribution': {
                'waste': 0.40,
                'low': 0.35,
                'medium': 0.20,
                'high': 0.05
            },
            'max_input_queue': 1500,
            'max_output_queue': 1500,
            'color': (150, 150, 150),  # Gray/silver
            'outline_color': (100, 100, 100)
        }

        super().__init__(grid_x, grid_y, width_tiles=4, height_tiles=4,
                        building_type="metal_refinery", config=config)

    def __repr__(self):
        """String representation for debugging."""
        return (f"MetalRefinery(level={self.level}, "
                f"queue={len(self.input_queue)}/{len(self.output_queue)}, "
                f"pos=({self.grid_x}, {self.grid_y}))")
