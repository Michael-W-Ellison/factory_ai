"""
Paper Recycler - processes paper and cardboard materials.
"""

from src.entities.buildings.processing_building import ProcessingBuilding


class PaperRecycler(ProcessingBuilding):
    """
    Paper Recycler.

    Processes paper and cardboard into quality-sorted paper products.
    Relatively efficient and low power consumption.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the paper recycler.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        config = {
            'name': 'Paper Recycler',
            'cost': 5000,
            'max_level': 3,
            'power_consumption': 3.0,
            'processing_speed': 3.0,  # seconds per kg
            'input_types': ['paper', 'cardboard'],
            'efficiency': 0.85,  # 85% of material becomes usable
            'quality_distribution': {
                'waste': 0.45,
                'low': 0.35,
                'medium': 0.15,
                'high': 0.05
            },
            'max_input_queue': 800,
            'max_output_queue': 800,
            'color': (210, 180, 140),  # Tan
            'outline_color': (160, 130, 90)
        }

        super().__init__(grid_x, grid_y, width_tiles=3, height_tiles=3,
                        building_type="paper_recycler", config=config)

    def __repr__(self):
        """String representation for debugging."""
        return (f"PaperRecycler(level={self.level}, "
                f"queue={len(self.input_queue)}/{len(self.output_queue)}, "
                f"pos=({self.grid_x}, {self.grid_y}))")
