"""
Battery Bank - stores electrical power for later use.
"""

from src.entities.building import Building


class BatteryBank(Building):
    """
    Battery Bank.

    Stores excess electrical power and releases it when needed.
    Charges when generation exceeds consumption.
    Discharges when consumption exceeds generation.
    Essential for balancing intermittent sources like solar.
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the battery bank.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        super().__init__(grid_x, grid_y, width_tiles=2, height_tiles=2,
                        building_type="battery_bank")

        # Battery Bank attributes
        self.name = "Battery Bank"
        self.base_cost = 4000
        self.max_level = 3

        # Energy storage
        self.base_max_storage = 1000.0  # Power units
        self.max_storage = self.base_max_storage
        self.stored_power = 0.0  # Current charge

        # Charge/discharge rates
        self.base_max_charge_rate = 50.0  # Units/sec max charge
        self.base_max_discharge_rate = 50.0  # Units/sec max discharge
        self.max_charge_rate = self.base_max_charge_rate
        self.max_discharge_rate = self.base_max_discharge_rate

        # Efficiency
        self.base_charge_efficiency = 0.90  # 90% efficient when charging
        self.base_discharge_efficiency = 0.95  # 95% efficient when discharging
        self.charge_efficiency = self.base_charge_efficiency
        self.discharge_efficiency = self.base_discharge_efficiency

        # Self-discharge (small power loss over time)
        self.self_discharge_rate = 0.1  # Units/sec when idle

        # Power consumption (minimal for battery management system)
        self.power_consumption = 0.5

        # Pollution
        self.pollution = 0.0  # No pollution (storage only)

        # Operational state
        self.charging = False
        self.discharging = False
        self.current_charge_rate = 0.0  # Current charge/discharge rate
        self.current_discharge_rate = 0.0

        # Appearance
        self.color = (50, 150, 50)  # Green (battery)
        self.outline_color = (30, 100, 30)

        self._apply_level_bonuses()

    def charge(self, power_available, dt):
        """
        Charge the battery with available power.

        Args:
            power_available (float): Power units available for charging
            dt (float): Delta time in seconds

        Returns:
            float: Power units actually consumed for charging
        """
        if not self.can_operate():
            self.charging = False
            self.current_charge_rate = 0.0
            return 0.0

        # Calculate how much we can charge
        available_capacity = self.max_storage - self.stored_power

        if available_capacity <= 0:
            # Battery full
            self.charging = False
            self.current_charge_rate = 0.0
            return 0.0

        # Limit by charge rate
        max_charge_this_frame = self.max_charge_rate * dt

        # Limit by available power
        power_to_consume = min(power_available, max_charge_this_frame)

        # Apply efficiency and add to storage
        power_stored = power_to_consume * self.charge_efficiency
        power_stored = min(power_stored, available_capacity)

        self.stored_power += power_stored
        self.charging = True
        self.discharging = False
        self.current_charge_rate = power_stored / dt if dt > 0 else 0.0

        # Return actual power consumed from grid
        return power_to_consume

    def discharge(self, power_needed, dt):
        """
        Discharge the battery to provide power.

        Args:
            power_needed (float): Power units needed
            dt (float): Delta time in seconds

        Returns:
            float: Power units actually provided
        """
        if not self.can_operate():
            self.discharging = False
            self.current_discharge_rate = 0.0
            return 0.0

        if self.stored_power <= 0:
            # Battery empty
            self.discharging = False
            self.current_discharge_rate = 0.0
            return 0.0

        # Limit by discharge rate
        max_discharge_this_frame = self.max_discharge_rate * dt

        # Limit by stored power
        power_available = min(self.stored_power, max_discharge_this_frame)

        # Limit by what's needed
        power_to_discharge = min(power_available, power_needed)

        # Remove from storage and apply efficiency
        self.stored_power -= power_to_discharge
        power_provided = power_to_discharge * self.discharge_efficiency

        self.discharging = True
        self.charging = False
        self.current_discharge_rate = power_to_discharge / dt if dt > 0 else 0.0

        return power_provided

    def get_charge_percentage(self):
        """
        Get battery charge level as percentage.

        Returns:
            float: Percentage (0.0 to 1.0)
        """
        if self.max_storage <= 0:
            return 0.0
        return self.stored_power / self.max_storage

    def _apply_self_discharge(self, dt):
        """
        Apply self-discharge (batteries lose charge over time).

        Args:
            dt (float): Delta time in seconds
        """
        if self.stored_power > 0:
            discharge_amount = self.self_discharge_rate * dt
            self.stored_power = max(0.0, self.stored_power - discharge_amount)

    def _apply_level_bonuses(self):
        """Apply bonuses based on current level."""
        # Level 1: 1000 units
        # Level 2: 2000 units (+100%)
        # Level 3: 4000 units (+300%)
        storage_multiplier = 2.0 ** (self.level - 1)  # Exponential growth
        self.max_storage = self.base_max_storage * storage_multiplier

        # Faster charge/discharge rates per level
        # Level 1: 50 units/sec
        # Level 2: 75 units/sec
        # Level 3: 100 units/sec
        rate_multiplier = 1.0 + (self.level - 1) * 0.5
        self.max_charge_rate = self.base_max_charge_rate * rate_multiplier
        self.max_discharge_rate = self.base_max_discharge_rate * rate_multiplier

        # Better efficiency per level
        # Charge: 90% -> 93% -> 96%
        # Discharge: 95% -> 97% -> 99%
        self.charge_efficiency = min(0.96, self.base_charge_efficiency + (self.level - 1) * 0.03)
        self.discharge_efficiency = min(0.99, self.base_discharge_efficiency + (self.level - 1) * 0.02)

        # Lower self-discharge per level
        # Level 1: 0.1 units/sec
        # Level 2: 0.07 units/sec
        # Level 3: 0.04 units/sec
        self.self_discharge_rate = 0.1 * (1.0 - (self.level - 1) * 0.3)

    def update(self, dt):
        """
        Update the battery bank.

        Args:
            dt (float): Delta time in seconds
        """
        super().update(dt)

        # Apply self-discharge when idle
        if not self.charging and not self.discharging:
            self._apply_self_discharge(dt)
            self.current_charge_rate = 0.0
            self.current_discharge_rate = 0.0

    def render(self, screen, camera):
        """
        Render the battery bank.

        Args:
            screen: Pygame screen surface
            camera: Camera object for coordinate conversion
        """
        super().render(screen, camera)

        # TODO: Add charge level indicator (battery icon with fill level)
        # TODO: Add charging/discharging animation (arrows in/out)
        # TODO: Show current rate

    def __repr__(self):
        """String representation for debugging."""
        status = "charging" if self.charging else ("discharging" if self.discharging else "idle")
        return (f"BatteryBank(level={self.level}, "
                f"charge={self.stored_power:.1f}/{self.max_storage:.0f}, "
                f"{status}, "
                f"pos=({self.grid_x}, {self.grid_y}))")
