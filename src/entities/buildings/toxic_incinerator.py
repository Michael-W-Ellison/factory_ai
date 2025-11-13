"""
Toxic Incinerator - processes hazardous and toxic waste.
"""

from src.entities.buildings.processing_building import ProcessingBuilding


class ToxicIncinerator(ProcessingBuilding):
    """
    Toxic Incinerator.

    Processes hazardous and toxic materials safely through high-temperature incineration.
    Costs money to operate but reduces dangerous waste. Produces ash as a sellable byproduct.
    Has high pollution output.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the toxic incinerator.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        config = {
            'name': 'Toxic Incinerator',
            'cost': 10000,
            'max_level': 3,
            'power_consumption': 6.0,
            'processing_speed': 3.0,  # Slower due to safety protocols
            'input_types': ['hazardous', 'toxic', 'chemicals', 'batteries'],
            'efficiency': 0.95,  # Very efficient at destruction
            'quality_distribution': {
                'waste': 0.05,   # Minimal waste
                'low': 0.60,     # Mostly contaminated ash
                'medium': 0.25,  # Clean ash
                'high': 0.10     # Pure ash (sellable)
            },
            'max_input_queue': 1000,
            'max_output_queue': 500,
            'color': (120, 50, 50),  # Dark red
            'outline_color': (180, 60, 60)
        }

        super().__init__(grid_x, grid_y, width_tiles=3, height_tiles=3,
                        building_type="toxic_incinerator", config=config)

        # Special attributes
        self.processing_cost = 5.0  # Costs $5 per kg to process
        self.pollution_output = 3.0  # High pollution
        self.ash_production_rate = 0.15  # Only 15% becomes ash, rest destroyed

    def _apply_level_bonuses(self):
        """Apply bonuses based on current level."""
        super()._apply_level_bonuses()

        # Reduce processing cost per level
        self.processing_cost = 5.0 - (self.level - 1) * 1.0

        # Reduce pollution per level (better filtration)
        self.pollution_output = 3.0 - (self.level - 1) * 0.5

    def update(self, dt):
        """
        Update the toxic incinerator.

        Args:
            dt (float): Delta time in seconds
        """
        super().update(dt)

        # Apply pollution (future feature integration point)
        # Could integrate with pollution system when implemented

    def get_processing_cost(self, quantity):
        """
        Calculate the cost to process a given quantity.

        Args:
            quantity (float): Amount in kg

        Returns:
            float: Cost in dollars
        """
        return quantity * self.processing_cost

    def __repr__(self):
        """String representation for debugging."""
        return (f"ToxicIncinerator(level={self.level}, "
                f"queue={len(self.input_queue)}/{len(self.output_queue)}, "
                f"cost=${self.processing_cost:.1f}/kg, "
                f"pollution={self.pollution_output:.1f}, "
                f"pos=({self.grid_x}, {self.grid_y}))")
