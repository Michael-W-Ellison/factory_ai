"""
Rubber Recycler - processes rubber materials.
"""

from src.entities.buildings.processing_building import ProcessingBuilding


class RubberRecycler(ProcessingBuilding):
    """
    Rubber Recycler.

    Processes rubber and tire materials into quality-sorted rubber products.
    Lower efficiency due to difficult processing, but valuable output.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the rubber recycler.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        config = {
            'name': 'Rubber Recycler',
            'cost': 9500,
            'max_level': 3,
            'power_consumption': 6.0,
            'processing_speed': 5.0,  # seconds per kg (slow due to difficulty)
            'input_types': ['rubber', 'tire', 'synthetic_rubber', 'latex'],
            'efficiency': 0.70,  # Lower efficiency (difficult material)
            'quality_distribution': {
                'waste': 0.60,
                'low': 0.25,
                'medium': 0.10,
                'high': 0.05
            },
            'max_input_queue': 1200,
            'max_output_queue': 1200,
            'color': (40, 40, 40),  # Dark gray/black
            'outline_color': (20, 20, 20)
        }

        super().__init__(grid_x, grid_y, width_tiles=3, height_tiles=3,
                        building_type="rubber_recycler", config=config)

    def __repr__(self):
        """String representation for debugging."""
        return (f"RubberRecycler(level={self.level}, "
                f"queue={len(self.input_queue)}/{len(self.output_queue)}, "
                f"pos=({self.grid_x}, {self.grid_y}))")
