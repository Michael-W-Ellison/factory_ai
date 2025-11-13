"""
Plastic Recycler - processes plastic materials.
"""

from src.entities.buildings.processing_building import ProcessingBuilding


class PlasticRecycler(ProcessingBuilding):
    """
    Plastic Recycler.

    Processes various types of plastic into quality-sorted plastic products.
    Moderate efficiency, produces more waste than paper recycling.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the plastic recycler.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        config = {
            'name': 'Plastic Recycler',
            'cost': 7500,
            'max_level': 3,
            'power_consumption': 4.0,
            'processing_speed': 4.0,  # seconds per kg (slower than paper)
            'input_types': ['plastic', 'hdpe', 'pet', 'pvc', 'ldpe'],
            'efficiency': 0.75,  # 75% efficiency (more waste)
            'quality_distribution': {
                'waste': 0.55,
                'low': 0.30,
                'medium': 0.10,
                'high': 0.05
            },
            'max_input_queue': 1000,
            'max_output_queue': 1000,
            'color': (100, 150, 200),  # Light blue
            'outline_color': (70, 110, 160)
        }

        super().__init__(grid_x, grid_y, width_tiles=3, height_tiles=3,
                        building_type="plastic_recycler", config=config)

    def __repr__(self):
        """String representation for debugging."""
        return (f"PlasticRecycler(level={self.level}, "
                f"queue={len(self.input_queue)}/{len(self.output_queue)}, "
                f"pos=({self.grid_x}, {self.grid_y}))")
