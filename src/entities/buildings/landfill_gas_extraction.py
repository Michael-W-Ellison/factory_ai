"""
Landfill Gas Extraction building - starting power source.
"""

from src.entities.building import Building


class LandfillGasExtraction(Building):
    """
    Landfill Gas Extraction Wells and Piping.

    Extracts methane from the landfill to generate power.
    Degrades over time as the landfill is depleted.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the landfill gas extraction.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        super().__init__(grid_x, grid_y, width_tiles=2, height_tiles=2,
                        building_type="landfill_gas_extraction")

        # Properties
        self.name = "Landfill Gas Extraction"
        self.max_level = 1  # Not upgradeable

        # Power generation
        self.base_power_generation = 10.0
        self.power_generation = self.base_power_generation
        self.power_consumption = 0.0  # Generates power, doesn't consume

        # Methane production
        self.methane_production_rate = 5.0  # units per second
        self.methane_type = "dirty_methane"

        # Degradation
        self.degradation_rate = 0.0001  # Power decreases over time
        self.min_power_generation = 3.0  # Minimum power (never goes to zero)

        # Environmental
        self.pollution = 2.0  # Pollution units per second

        # Visual
        self.color = (100, 80, 60)  # Brown
        self.outline_color = (70, 60, 50)

        # Already constructed (starting building)
        self.under_construction = False
        self.construction_progress = 100.0

    def update(self, dt):
        """
        Update the landfill gas extraction.

        Args:
            dt (float): Delta time in seconds
        """
        super().update(dt)

        # Degrade power generation over time
        if self.power_generation > self.min_power_generation:
            self.power_generation -= self.degradation_rate * dt
            self.power_generation = max(self.power_generation, self.min_power_generation)

        # Produce methane (if needed by other systems)
        # This would be handled by a material flow system in the future

    def get_info(self):
        """Get building information including degradation."""
        info = super().get_info()
        info['methane_production'] = self.methane_production_rate
        info['degradation_percent'] = (1.0 - (self.power_generation / self.base_power_generation)) * 100.0
        info['pollution'] = self.pollution
        return info

    def __repr__(self):
        """String representation for debugging."""
        return (f"LandfillGasExtraction(power={self.power_generation:.1f}W, "
                f"degradation={((1.0 - self.power_generation/self.base_power_generation)*100):.1f}%, "
                f"pos=({self.grid_x}, {self.grid_y}))")
