"""
Methane Generator - converts methane fuel into electrical power.
"""

from src.entities.building import Building


class MethaneGenerator(Building):
    """
    Methane Generator.

    Consumes pure methane to generate electrical power.
    Always on if fuel is available. Produces some pollution.
    More reliable than solar but requires fuel supply.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the methane generator.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        super().__init__(grid_x, grid_y, width_tiles=4, height_tiles=4,
                        building_type="methane_generator")

        # Methane Generator attributes
        self.name = "Methane Generator"
        self.base_cost = 6000
        self.max_level = 3

        # Power generation
        self.base_power_generation = 25.0  # 25 units when fueled
        self.power_generation = 0.0  # Current output (depends on fuel)

        # Fuel consumption
        self.base_fuel_consumption_rate = 2.0  # kg/sec of pure_methane
        self.fuel_consumption_rate = self.base_fuel_consumption_rate
        self.fuel_type = "pure_methane"
        self.fuel_stored = 0.0  # Internal fuel buffer
        self.max_fuel_storage = 100.0  # kg buffer

        # Efficiency
        self.base_efficiency = 0.75  # 75% efficient at converting fuel to power
        self.efficiency = self.base_efficiency

        # Pollution
        self.base_pollution = 1.0
        self.pollution = self.base_pollution

        # Power consumption (minimal - startup/control systems)
        self.power_consumption = 0.5

        # Appearance
        self.color = (100, 100, 80)  # Brownish/industrial
        self.outline_color = (70, 70, 50)

        self._apply_level_bonuses()

    def add_fuel(self, quantity):
        """
        Add fuel to the generator's internal buffer.

        Args:
            quantity (float): Amount of fuel in kg

        Returns:
            float: Amount actually added
        """
        available_space = self.max_fuel_storage - self.fuel_stored

        if available_space <= 0:
            return 0.0

        amount_to_add = min(quantity, available_space)
        self.fuel_stored += amount_to_add

        return amount_to_add

    def get_fuel_level(self):
        """
        Get current fuel level.

        Returns:
            float: Fuel stored in kg
        """
        return self.fuel_stored

    def get_fuel_percentage(self):
        """
        Get fuel level as percentage of capacity.

        Returns:
            float: Percentage (0.0 to 1.0)
        """
        if self.max_fuel_storage <= 0:
            return 0.0
        return self.fuel_stored / self.max_fuel_storage

    def _consume_fuel(self, dt):
        """
        Consume fuel to generate power.

        Args:
            dt (float): Delta time in seconds

        Returns:
            bool: True if fuel was available, False if empty
        """
        fuel_needed = self.fuel_consumption_rate * dt

        if self.fuel_stored >= fuel_needed:
            self.fuel_stored -= fuel_needed
            return True
        else:
            # Not enough fuel - try to use what's left
            if self.fuel_stored > 0:
                # Partial power based on available fuel
                fuel_ratio = self.fuel_stored / fuel_needed
                self.fuel_stored = 0.0
                # Return True but generator will produce partial power
                return fuel_ratio > 0.5  # Need at least 50% fuel to run
            else:
                self.fuel_stored = 0.0
                return False

    def _update_power_generation(self):
        """Update power generation based on operational status and fuel."""
        if not self.can_operate():
            self.power_generation = 0.0
            return

        # Check if we have fuel
        if self.fuel_stored > 0:
            # Generate power
            self.power_generation = self.base_power_generation * self.efficiency
        else:
            # No fuel - no power
            self.power_generation = 0.0

    def _apply_level_bonuses(self):
        """Apply bonuses based on current level."""
        # Level 1: 25 power
        # Level 2: 37.5 power (+50%)
        # Level 3: 50 power (+100%)
        power_multiplier = 1.0 + (self.level - 1) * 0.5
        self.base_power_generation = 25.0 * power_multiplier

        # Better efficiency per level (less fuel waste)
        # Level 1: 75%
        # Level 2: 82.5%
        # Level 3: 90%
        self.efficiency = min(0.90, self.base_efficiency + (self.level - 1) * 0.075)

        # More fuel storage per level
        # Level 1: 100kg
        # Level 2: 150kg
        # Level 3: 200kg
        storage_multiplier = 1.0 + (self.level - 1) * 0.5
        self.max_fuel_storage = 100.0 * storage_multiplier

        # Lower fuel consumption per level (same power, less fuel)
        # Level 1: 2.0 kg/sec
        # Level 2: 1.7 kg/sec (-15%)
        # Level 3: 1.4 kg/sec (-30%)
        consumption_multiplier = 1.0 - (self.level - 1) * 0.15
        self.fuel_consumption_rate = self.base_fuel_consumption_rate * consumption_multiplier

        # Less pollution per level
        # Level 1: 1.0
        # Level 2: 0.7
        # Level 3: 0.4
        pollution_reduction = 1.0 - (self.level - 1) * 0.3
        self.pollution = max(0.1, self.base_pollution * pollution_reduction)

        self._update_power_generation()

    def update(self, dt):
        """
        Update the methane generator.

        Args:
            dt (float): Delta time in seconds
        """
        super().update(dt)

        if self.can_operate():
            # Try to consume fuel
            has_fuel = self._consume_fuel(dt)

            if has_fuel:
                # Update power generation
                self._update_power_generation()
            else:
                # Out of fuel
                self.power_generation = 0.0
        else:
            self.power_generation = 0.0

    def render(self, screen, camera):
        """
        Render the methane generator.

        Args:
            screen: Pygame screen surface
            camera: Camera object for coordinate conversion
        """
        super().render(screen, camera)

        # TODO: Add fuel level indicator
        # TODO: Add smoke/exhaust particles when running
        # TODO: Show power output indicator

    def __repr__(self):
        """String representation for debugging."""
        return (f"MethaneGenerator(level={self.level}, "
                f"power={self.power_generation:.1f}W, "
                f"fuel={self.fuel_stored:.1f}/{self.max_fuel_storage:.0f}kg, "
                f"pos=({self.grid_x}, {self.grid_y}))")
