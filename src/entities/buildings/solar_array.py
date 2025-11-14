"""
Solar Array - clean renewable power generation.
"""

import math
from src.entities.building import Building


class SolarArray(Building):
    """
    Solar Array.

    Generates power from sunlight during daytime hours.
    Output varies based on time of day (peak at noon).
    No pollution, requires research to unlock.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the solar array.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        super().__init__(grid_x, grid_y, width_tiles=3, height_tiles=3,
                        building_type="solar_array")

        # Solar Array attributes
        self.name = "Solar Array"
        self.base_cost = 2000
        self.max_level = 3

        # Power generation (daytime only)
        self.base_max_power_generation = 15.0  # Peak power at noon
        self.max_power_generation = self.base_max_power_generation
        self.power_generation = 0.0  # Current output (varies by time)

        # Time tracking
        self.current_hour = 12.0  # Start at noon (0-24)
        self.sunrise_hour = 6.0
        self.sunset_hour = 18.0

        # Efficiency
        self.base_efficiency = 0.85  # 85% efficient at converting sunlight
        self.efficiency = self.base_efficiency
        self.weather_modifier = 1.0  # Reduced in clouds/rain (future feature)

        # Power consumption (minimal for tracking motors)
        self.power_consumption = 0.1

        # Pollution
        self.pollution = 0.0  # Clean energy!

        # Appearance
        self.color = (50, 100, 200)  # Blue (solar panels)
        self.outline_color = (30, 70, 150)

        self._apply_level_bonuses()

    def set_time_of_day(self, hour):
        """
        Set the current time of day to calculate power output.

        Args:
            hour (float): Hour of day (0-24)
        """
        self.current_hour = hour % 24.0
        self._update_power_generation()

    def _update_power_generation(self):
        """Update power generation based on time of day."""
        if not self.can_operate():
            self.power_generation = 0.0
            return

        hour = self.current_hour

        # No power at night
        if hour < self.sunrise_hour or hour > self.sunset_hour:
            self.power_generation = 0.0
            return

        # Calculate sun intensity (0.0 to 1.0)
        # Peak at noon (12.0), ramps up/down at sunrise/sunset
        day_length = self.sunset_hour - self.sunrise_hour
        day_progress = (hour - self.sunrise_hour) / day_length

        # Use sine wave for smooth power curve
        # Peak at 0.5 progress (noon), 0 at sunrise/sunset
        sun_intensity = math.sin(day_progress * math.pi)

        # Calculate actual power generation
        self.power_generation = (
            self.max_power_generation *
            sun_intensity *
            self.efficiency *
            self.weather_modifier
        )

    def _apply_level_bonuses(self):
        """Apply bonuses based on current level."""
        # Level 1: 15 power
        # Level 2: 22.5 power (+50%)
        # Level 3: 30 power (+100%)
        power_multiplier = 1.0 + (self.level - 1) * 0.5
        self.max_power_generation = self.base_max_power_generation * power_multiplier

        # Better efficiency per level
        # Level 1: 85%
        # Level 2: 90%
        # Level 3: 95%
        self.efficiency = min(0.95, self.base_efficiency + (self.level - 1) * 0.05)

        # Recalculate current generation
        self._update_power_generation()

    def update(self, dt):
        """
        Update the solar array.

        Args:
            dt (float): Delta time in seconds
        """
        super().update(dt)

        # Update power generation based on current time
        # Note: Time is updated by game systems, not here
        self._update_power_generation()

        # Future: Could add tracking motors that follow the sun
        # Future: Could add maintenance/cleaning requirements

    def render(self, screen, camera):
        """
        Render the solar array.

        Args:
            screen: Pygame screen surface
            camera: Camera object for coordinate conversion
        """
        super().render(screen, camera)

        # TODO: Add visual indicator of current power output
        # TODO: Add sun tracking animation
        # TODO: Show efficiency/weather effects

    def get_power_percentage(self):
        """
        Get current power output as percentage of max.

        Returns:
            float: Percentage (0.0 to 1.0)
        """
        if self.max_power_generation <= 0:
            return 0.0
        return self.power_generation / self.max_power_generation

    def __repr__(self):
        """String representation for debugging."""
        return (f"SolarArray(level={self.level}, "
                f"power={self.power_generation:.1f}/{self.max_power_generation:.1f}W, "
                f"time={self.current_hour:.1f}h, "
                f"pos=({self.grid_x}, {self.grid_y}))")
