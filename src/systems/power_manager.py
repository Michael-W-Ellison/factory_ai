"""
PowerManager - manages power generation, consumption, and distribution.

Features:
- Tracks power generation, consumption, and storage
- Priority-based distribution during blackouts
- Battery storage management
"""

from enum import IntEnum
from typing import List, Dict, Any


class PowerPriority(IntEnum):
    """Power priority levels (higher = more important)."""
    CRITICAL = 100      # Life support, security
    HIGH = 75           # Factory core, main processors
    MEDIUM = 50         # Storage, secondary systems
    LOW = 25            # Lighting, comfort
    OPTIONAL = 10       # Decorative, non-essential


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
        Handle power distribution during blackout using priority system.

        Args:
            building_manager: BuildingManager instance
        """
        # Get available power (generation only, storage is depleted)
        available_power = self.total_generation

        # Get all buildings that consume power, sorted by priority
        consumers = []
        for building in building_manager.buildings.values():
            if building.power_consumption > 0:
                priority = self._get_building_priority(building)
                consumers.append((priority, building.power_consumption, building))

        # Sort by priority (highest first)
        consumers.sort(key=lambda x: x[0], reverse=True)

        # Distribute power by priority
        remaining_power = available_power
        for priority, consumption, building in consumers:
            if remaining_power >= consumption:
                building.powered = True
                remaining_power -= consumption
            else:
                building.powered = False

    def _get_building_priority(self, building) -> int:
        """
        Get power priority for a building.

        Args:
            building: Building instance

        Returns:
            Priority level (higher = more important)
        """
        # Check if building has a custom priority attribute
        if hasattr(building, 'power_priority'):
            return building.power_priority

        # Default priorities based on building type
        building_type = type(building).__name__

        priority_map = {
            # Critical - must stay on
            'Factory': PowerPriority.CRITICAL,
            'SecurityStation': PowerPriority.CRITICAL,

            # High priority - core operations
            'Processor': PowerPriority.HIGH,
            'Sorter': PowerPriority.HIGH,
            'ChargingStation': PowerPriority.HIGH,
            'ResearchLab': PowerPriority.HIGH,

            # Medium priority - useful but not critical
            'Storage': PowerPriority.MEDIUM,
            'Conveyor': PowerPriority.MEDIUM,
            'Battery': PowerPriority.MEDIUM,

            # Low priority - comfort/convenience
            'Lighting': PowerPriority.LOW,

            # Optional - can be shut down
            'Decoration': PowerPriority.OPTIONAL,
        }

        return priority_map.get(building_type, PowerPriority.MEDIUM)

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

    def set_building_priority(self, building, priority: PowerPriority):
        """
        Set custom power priority for a building.

        Args:
            building: Building instance
            priority: PowerPriority level
        """
        building.power_priority = int(priority)

    def get_powered_buildings_count(self, building_manager) -> Dict[str, int]:
        """
        Get count of powered vs unpowered buildings.

        Args:
            building_manager: BuildingManager instance

        Returns:
            Dict with 'powered' and 'unpowered' counts
        """
        powered = 0
        unpowered = 0
        for building in building_manager.buildings.values():
            if building.power_consumption > 0:
                if building.powered:
                    powered += 1
                else:
                    unpowered += 1
        return {'powered': powered, 'unpowered': unpowered}

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
