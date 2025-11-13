"""
Glassworks - processes glass materials.
"""

from src.entities.buildings.processing_building import ProcessingBuilding


class Glassworks(ProcessingBuilding):
    """
    Glassworks.

    Processes glass into quality-sorted glass products.
    Moderate efficiency, produces clean high-quality output.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the glassworks.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        config = {
            'name': 'Glassworks',
            'cost': 8500,
            'max_level': 3,
            'power_consumption': 5.0,
            'processing_speed': 4.5,  # seconds per kg
            'input_types': ['glass', 'clear_glass', 'colored_glass', 'bottles'],
            'efficiency': 0.88,  # Good efficiency
            'quality_distribution': {
                'waste': 0.35,
                'low': 0.35,
                'medium': 0.20,
                'high': 0.10  # Better high-quality output
            },
            'max_input_queue': 1000,
            'max_output_queue': 1000,
            'color': (150, 220, 220),  # Cyan/glass color
            'outline_color': (100, 170, 170)
        }

        super().__init__(grid_x, grid_y, width_tiles=3, height_tiles=3,
                        building_type="glassworks", config=config)

    def __repr__(self):
        """String representation for debugging."""
        return (f"Glassworks(level={self.level}, "
                f"queue={len(self.input_queue)}/{len(self.output_queue)}, "
                f"pos=({self.grid_x}, {self.grid_y}))")
