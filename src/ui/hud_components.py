"""
HUD Components - Manages heads-up display panels.

Components:
- Resource Panel: Money and materials
- Power Panel: Generation, consumption, storage
- Time Panel: Game time, day counter, speed controls
- Suspicion Meter: Current suspicion level
"""

from typing import Dict, List, Optional


class ResourcePanel:
    """
    Resource panel showing money and materials.

    Displays current money, material counts, and total storage.
    """

    def __init__(self):
        """Initialize resource panel."""
        self.is_visible = True
        self.is_expanded = False

        # Display settings
        self.show_value = True  # Show material values
        self.show_weight = True  # Show material weights
        self.max_materials_shown = 5  # Max materials to show when collapsed

    def update(self, resource_manager):
        """
        Update panel with current resource data.

        Args:
            resource_manager: ResourceManager instance
        """
        self.money = resource_manager.money
        self.materials = resource_manager.stored_materials.copy()
        self.total_weight = resource_manager.get_total_stored_weight()
        self.total_value = resource_manager.get_total_stored_value()

    def toggle_expand(self):
        """Toggle expanded/collapsed state."""
        self.is_expanded = not self.is_expanded
        return self.is_expanded

    def get_display_materials(self) -> List[tuple]:
        """
        Get materials to display based on expand state.

        Returns:
            List of (material_type, quantity) tuples
        """
        if not hasattr(self, 'materials'):
            return []

        sorted_materials = sorted(self.materials.items(), key=lambda x: x[1], reverse=True)

        if self.is_expanded:
            return sorted_materials
        else:
            return sorted_materials[:self.max_materials_shown]

    def get_summary(self) -> Dict:
        """Get summary data for display."""
        return {
            'money': getattr(self, 'money', 0),
            'total_weight': getattr(self, 'total_weight', 0),
            'total_value': getattr(self, 'total_value', 0),
            'material_types': len(getattr(self, 'materials', {})),
            'is_expanded': self.is_expanded,
        }


class PowerPanel:
    """
    Power panel showing generation, consumption, and storage.

    Displays power status and warnings for low power situations.
    """

    def __init__(self):
        """Initialize power panel."""
        self.is_visible = True

        # Power data
        self.generation = 0
        self.consumption = 0
        self.storage_current = 0
        self.storage_max = 0

        # Warning states
        self.is_brownout = False  # Consumption > generation
        self.is_blackout = False  # No power at all

    def update(self, power_manager):
        """
        Update panel with current power data.

        Args:
            power_manager: PowerManager instance
        """
        if hasattr(power_manager, 'total_generation'):
            self.generation = power_manager.total_generation
        if hasattr(power_manager, 'total_consumption'):
            self.consumption = power_manager.total_consumption
        if hasattr(power_manager, 'current_storage'):
            self.storage_current = power_manager.current_storage
        if hasattr(power_manager, 'max_storage'):
            self.storage_max = power_manager.max_storage

        # Update warning states
        self.is_brownout = self.consumption > self.generation
        self.is_blackout = self.generation == 0 and self.consumption > 0

    def get_net_power(self) -> float:
        """Get net power (generation - consumption)."""
        return self.generation - self.consumption

    def get_storage_percent(self) -> float:
        """Get storage percentage (0-100)."""
        if self.storage_max == 0:
            return 0
        return (self.storage_current / self.storage_max) * 100

    def get_status_text(self) -> str:
        """Get power status text."""
        if self.is_blackout:
            return "BLACKOUT"
        elif self.is_brownout:
            return "BROWNOUT"
        elif self.get_net_power() > 0:
            return "SURPLUS"
        else:
            return "STABLE"

    def get_status_color(self) -> str:
        """Get status color for UI."""
        if self.is_blackout:
            return "red"
        elif self.is_brownout:
            return "orange"
        elif self.get_net_power() > 0:
            return "green"
        else:
            return "yellow"

    def get_summary(self) -> Dict:
        """Get summary data for display."""
        return {
            'generation': self.generation,
            'consumption': self.consumption,
            'net_power': self.get_net_power(),
            'storage_percent': self.get_storage_percent(),
            'status': self.get_status_text(),
            'is_brownout': self.is_brownout,
            'is_blackout': self.is_blackout,
        }


class TimePanel:
    """
    Time panel showing game time and speed controls.

    Displays current time, day counter, and allows speed adjustment.
    """

    def __init__(self):
        """Initialize time panel."""
        self.is_visible = True

        # Time data
        self.current_time = 0  # Game time in seconds
        self.day = 1
        self.hour = 6
        self.minute = 0

        # Speed control
        self.speed = 1.0
        self.available_speeds = [0.5, 1.0, 2.0, 4.0]
        self.is_paused = False

    def update(self, time_manager):
        """
        Update panel with current time data.

        Args:
            time_manager: TimeManager instance (if exists)
        """
        if time_manager:
            if hasattr(time_manager, 'current_time'):
                self.current_time = time_manager.current_time
            if hasattr(time_manager, 'day'):
                self.day = time_manager.day
            if hasattr(time_manager, 'hour'):
                self.hour = time_manager.hour
            if hasattr(time_manager, 'minute'):
                self.minute = time_manager.minute
            if hasattr(time_manager, 'speed'):
                self.speed = time_manager.speed
            if hasattr(time_manager, 'is_paused'):
                self.is_paused = time_manager.is_paused

    def increase_speed(self):
        """Increase game speed to next level."""
        current_index = self.available_speeds.index(self.speed) if self.speed in self.available_speeds else 1
        next_index = min(len(self.available_speeds) - 1, current_index + 1)
        self.speed = self.available_speeds[next_index]
        return self.speed

    def decrease_speed(self):
        """Decrease game speed to previous level."""
        current_index = self.available_speeds.index(self.speed) if self.speed in self.available_speeds else 1
        prev_index = max(0, current_index - 1)
        self.speed = self.available_speeds[prev_index]
        return self.speed

    def toggle_pause(self):
        """Toggle pause state."""
        self.is_paused = not self.is_paused
        return self.is_paused

    def get_time_string(self) -> str:
        """Get formatted time string (HH:MM)."""
        return f"{self.hour:02d}:{self.minute:02d}"

    def get_day_string(self) -> str:
        """Get day string."""
        return f"Day {self.day}"

    def get_speed_string(self) -> str:
        """Get speed string."""
        if self.is_paused:
            return "PAUSED"
        return f"{self.speed}x"

    def get_summary(self) -> Dict:
        """Get summary data for display."""
        return {
            'day': self.day,
            'time': self.get_time_string(),
            'speed': self.speed,
            'is_paused': self.is_paused,
            'speed_string': self.get_speed_string(),
        }


class SuspicionMeter:
    """
    Suspicion meter showing current suspicion level.

    Visual meter with color coding based on suspicion tier.
    """

    def __init__(self):
        """Initialize suspicion meter."""
        self.is_visible = True

        # Suspicion data
        self.suspicion_level = 0
        self.suspicion_tier = "Normal"

        # Tier thresholds
        self.tier_thresholds = [
            (0, 20, "Normal", "green"),
            (21, 40, "Rumors", "yellow"),
            (41, 60, "Investigation", "orange"),
            (61, 80, "Inspection", "red"),
            (81, 100, "Restrictions", "darkred"),
        ]

    def update(self, suspicion_manager):
        """
        Update meter with current suspicion data.

        Args:
            suspicion_manager: SuspicionManager instance
        """
        if hasattr(suspicion_manager, 'suspicion_level'):
            self.suspicion_level = suspicion_manager.suspicion_level
        if hasattr(suspicion_manager, 'get_tier_name'):
            self.suspicion_tier = suspicion_manager.get_tier_name()

    def get_tier_color(self) -> str:
        """Get color for current tier."""
        for min_val, max_val, tier, color in self.tier_thresholds:
            if min_val <= self.suspicion_level <= max_val:
                return color
        return "gray"

    def get_summary(self) -> Dict:
        """Get summary data for display."""
        return {
            'level': self.suspicion_level,
            'tier': self.suspicion_tier,
            'color': self.get_tier_color(),
        }


class HUDManager:
    """
    Manages all HUD components.

    Coordinates updates and visibility of all HUD panels.
    """

    def __init__(self):
        """Initialize HUD manager."""
        # HUD panels
        self.resource_panel = ResourcePanel()
        self.power_panel = PowerPanel()
        self.time_panel = TimePanel()
        self.suspicion_meter = SuspicionMeter()

        # HUD state
        self.is_visible = True

    def update(self, resource_manager=None, power_manager=None,
               time_manager=None, suspicion_manager=None):
        """
        Update all HUD components.

        Args:
            resource_manager: Optional ResourceManager
            power_manager: Optional PowerManager
            time_manager: Optional TimeManager
            suspicion_manager: Optional SuspicionManager
        """
        if resource_manager:
            self.resource_panel.update(resource_manager)

        if power_manager:
            self.power_panel.update(power_manager)

        if time_manager:
            self.time_panel.update(time_manager)

        if suspicion_manager:
            self.suspicion_meter.update(suspicion_manager)

    def toggle_visibility(self):
        """Toggle HUD visibility."""
        self.is_visible = not self.is_visible
        return self.is_visible

    def get_all_summaries(self) -> Dict:
        """Get summaries from all panels."""
        return {
            'resource': self.resource_panel.get_summary(),
            'power': self.power_panel.get_summary(),
            'time': self.time_panel.get_summary(),
            'suspicion': self.suspicion_meter.get_summary(),
            'hud_visible': self.is_visible,
        }
