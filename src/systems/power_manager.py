"""
PowerManager - manages power generation, consumption, and distribution.
"""


class PowerManager:
    """
    Manages the power system for the factory.

    Tracks power generation, consumption, storage, and distribution.
    Handles brownouts and blackouts when power is insufficient.
    """

    def __init__(self, building_manager):
        """
        Initialize the power manager.

        Args:
            building_manager: BuildingManager instance
        """
        self.building_manager = building_manager

        # Power storage (from batteries)
        self.current_power = 0.0  # Current stored power
        self.max_storage = 0.0  # Maximum storage capacity

        # Power stats
        self.total_generation = 0.0  # Units per second
        self.total_consumption = 0.0  # Units per second
        self.net_power = 0.0  # Generation - consumption

        # Power state
        self.has_power = True
        self.brownout = False  # True when consumption > generation (using reserves)
        self.blackout = False  # True when no power available

    def update(self, dt, building_manager):
        """
        Update power system.

        Args:
            dt (float): Delta time in seconds
            building_manager: BuildingManager instance
        """
        # Calculate total generation from all powered buildings
        self.total_generation = 0.0
        for building in building_manager.buildings.values():
            if building.can_operate() and building.power_generation > 0:
                self.total_generation += building.power_generation

        # Calculate total consumption from operational buildings
        self.total_consumption = 0.0
        for building in building_manager.buildings.values():
            if building.operational and building.power_consumption > 0:
                self.total_consumption += building.power_consumption

        # Calculate net power
        self.net_power = self.total_generation - self.total_consumption

        # Update power storage
        if self.net_power > 0:
            # Surplus power - charge batteries
            power_to_store = self.net_power * dt
            self.current_power = min(self.current_power + power_to_store, self.max_storage)
            self.brownout = False
            self.blackout = False
            self.has_power = True

        elif self.net_power < 0:
            # Deficit - use stored power
            power_needed = abs(self.net_power) * dt

            if self.current_power >= power_needed:
                # Have enough stored power
                self.current_power -= power_needed
                self.brownout = True  # Using reserves
                self.blackout = False
                self.has_power = True
            else:
                # Not enough power - blackout
                self.current_power = 0.0
                self.brownout = True
                self.blackout = True
                self.has_power = False

                # Distribute available power by priority
                self._handle_blackout(building_manager)

        else:
            # Exactly balanced (rare)
            self.brownout = False
            self.blackout = False
            self.has_power = True

        # Update building power states
        self._update_building_power_states(building_manager)

    def _update_building_power_states(self, building_manager):
        """
        Update which buildings have power.

        Args:
            building_manager: BuildingManager instance
        """
        if not self.blackout:
            # All buildings have power
            for building in building_manager.buildings.values():
                building.powered = True
        else:
            # No power - all buildings unpowered
            for building in building_manager.buildings.values():
                if building.power_consumption > 0:
                    building.powered = False
                else:
                    building.powered = True  # Buildings that don't consume power stay on

    def _handle_blackout(self, building_manager):
        """
        Handle power distribution during blackout.

        Args:
            building_manager: BuildingManager instance
        """
        # During blackout, shut down non-essential buildings
        # Priority: Power generation > Factory > Processing > Storage

        # For now, simple approach: shut down everything
        # TODO: Implement priority system
        pass

    def add_battery_storage(self, capacity):
        """
        Add battery storage capacity.

        Args:
            capacity (float): Storage capacity to add
        """
        self.max_storage += capacity

    def remove_battery_storage(self, capacity):
        """
        Remove battery storage capacity.

        Args:
            capacity (float): Storage capacity to remove
        """
        self.max_storage -= capacity
        self.current_power = min(self.current_power, self.max_storage)

    def get_power_status(self):
        """
        Get power system status.

        Returns:
            dict: Power status information
        """
        return {
            'generation': self.total_generation,
            'consumption': self.total_consumption,
            'net': self.net_power,
            'stored': self.current_power,
            'storage_capacity': self.max_storage,
            'storage_percent': (self.current_power / self.max_storage * 100.0) if self.max_storage > 0 else 0,
            'has_power': self.has_power,
            'brownout': self.brownout,
            'blackout': self.blackout,
        }

    def __repr__(self):
        """String representation for debugging."""
        return (f"PowerManager(gen={self.total_generation:.1f}, "
                f"cons={self.total_consumption:.1f}, "
                f"net={self.net_power:.1f}, "
                f"stored={self.current_power:.0f}/{self.max_storage:.0f})")
