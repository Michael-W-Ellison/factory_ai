"""
TransmitterManager - manages wireless transmitters and control range.

Handles:
- Wireless transmitter placement
- Signal coverage calculation
- Control range for drones and devices
- Signal strength and interference
- Network connectivity
"""

import math
from enum import Enum
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass


class TransmitterType(Enum):
    """Types of wireless transmitters."""
    BASIC = 0  # Basic range, low cost
    ADVANCED = 1  # Extended range, medium cost
    LONG_RANGE = 2  # Very long range, high cost
    REPEATER = 3  # Signal repeater, extends network


@dataclass
class Transmitter:
    """
    Wireless transmitter for extending control range.

    Attributes:
        id: Unique transmitter identifier
        position: (x, y) position on map
        transmitter_type: Type of transmitter
        range: Signal range in tiles
        power: Signal power (0-100)
        is_active: Whether transmitter is operational
        cost: Purchase cost
    """
    id: int
    position: Tuple[float, float]
    transmitter_type: TransmitterType
    range: float
    power: float = 100.0
    is_active: bool = True
    cost: int = 0

    def get_distance_to(self, position: Tuple[float, float]) -> float:
        """Calculate distance to a position."""
        dx = position[0] - self.position[0]
        dy = position[1] - self.position[1]
        return math.sqrt(dx * dx + dy * dy)

    def get_signal_strength_at(self, position: Tuple[float, float]) -> float:
        """
        Calculate signal strength at a position (0-100).

        Signal strength decreases with distance from transmitter.
        """
        distance = self.get_distance_to(position)

        if distance > self.range:
            return 0.0  # Out of range

        # Linear falloff: 100% at center, 0% at max range
        strength = 100.0 * (1.0 - (distance / self.range))

        # Apply power multiplier
        strength *= (self.power / 100.0)

        return max(0.0, min(100.0, strength))


class TransmitterManager:
    """
    Manages wireless transmitters and control range system.

    Transmitters extend control range for drones and other devices.
    """

    def __init__(self, resource_manager):
        """
        Initialize transmitter manager.

        Args:
            resource_manager: ResourceManager instance
        """
        self.resources = resource_manager

        # Transmitters
        self.transmitters: Dict[int, Transmitter] = {}
        self.next_transmitter_id = 1

        # Base transmitter (always active at factory)
        self.base_position = (0.0, 0.0)
        self.base_range = 20.0  # 20 tile radius from factory

        # Transmitter types and specs
        self.transmitter_specs = {
            TransmitterType.BASIC: {
                'range': 30.0,  # 30 tiles
                'cost': 3000,
                'power': 100.0,
                'name': 'Basic Transmitter'
            },
            TransmitterType.ADVANCED: {
                'range': 50.0,  # 50 tiles
                'cost': 8000,
                'power': 100.0,
                'name': 'Advanced Transmitter'
            },
            TransmitterType.LONG_RANGE: {
                'range': 80.0,  # 80 tiles
                'cost': 15000,
                'power': 100.0,
                'name': 'Long-Range Transmitter'
            },
            TransmitterType.REPEATER: {
                'range': 25.0,  # 25 tiles (smaller but extends network)
                'cost': 5000,
                'power': 100.0,
                'name': 'Signal Repeater'
            }
        }

        # Signal quality thresholds
        self.min_signal_for_control = 10.0  # Minimum 10% signal to control devices
        self.good_signal_threshold = 50.0  # 50%+ is considered good signal

        # Coverage cache (updated each frame)
        self.coverage_map: Dict[Tuple[int, int], float] = {}

        # Statistics
        self.total_transmitters_placed = 0

    def place_transmitter(self, transmitter_type: TransmitterType,
                         position: Tuple[float, float]) -> Optional[int]:
        """
        Place a new transmitter.

        Args:
            transmitter_type: Type of transmitter to place
            position: (x, y) position

        Returns:
            int: Transmitter ID if successful, None otherwise
        """
        specs = self.transmitter_specs[transmitter_type]

        # Check if player can afford it
        if self.resources.money < specs['cost']:
            print(f"⚠️ Insufficient funds for {specs['name']}")
            print(f"  Cost: ${specs['cost']:,}")
            print(f"  Current: ${self.resources.money:,}")
            return None

        # Check if position has signal coverage
        # Must be within range of base or another transmitter
        if not self.has_signal_coverage(position):
            print(f"⚠️ Cannot place transmitter - no signal coverage at position")
            print(f"  Must be within range of factory or another transmitter")
            return None

        # Purchase transmitter
        self.resources.modify_money(-specs['cost'])

        # Create transmitter
        transmitter = Transmitter(
            id=self.next_transmitter_id,
            position=position,
            transmitter_type=transmitter_type,
            range=specs['range'],
            power=specs['power'],
            is_active=True,
            cost=specs['cost']
        )

        self.transmitters[self.next_transmitter_id] = transmitter
        self.next_transmitter_id += 1
        self.total_transmitters_placed += 1

        print(f"\n📡 {specs['name'].upper()} PLACED")
        print(f"  Position: ({position[0]:.0f}, {position[1]:.0f})")
        print(f"  Range: {specs['range']} tiles")
        print(f"  Cost: ${specs['cost']:,}")

        return transmitter.id

    def remove_transmitter(self, transmitter_id: int) -> bool:
        """
        Remove a transmitter.

        Args:
            transmitter_id: ID of transmitter to remove

        Returns:
            bool: True if successful, False otherwise
        """
        if transmitter_id not in self.transmitters:
            return False

        transmitter = self.transmitters[transmitter_id]

        # Remove transmitter (no refund)
        del self.transmitters[transmitter_id]

        print(f"\n📡 TRANSMITTER {transmitter_id} REMOVED")
        print(f"  Position: ({transmitter.position[0]:.0f}, {transmitter.position[1]:.0f})")

        return True

    def has_signal_coverage(self, position: Tuple[float, float]) -> bool:
        """
        Check if a position has signal coverage.

        Args:
            position: (x, y) position to check

        Returns:
            bool: True if position has coverage, False otherwise
        """
        signal_strength = self.get_signal_strength_at(position)
        return signal_strength >= self.min_signal_for_control

    def get_signal_strength_at(self, position: Tuple[float, float]) -> float:
        """
        Get signal strength at a position (0-100).

        Takes the maximum signal from base or any transmitter.

        Args:
            position: (x, y) position

        Returns:
            float: Signal strength (0-100)
        """
        max_signal = 0.0

        # Check base transmitter
        dx = position[0] - self.base_position[0]
        dy = position[1] - self.base_position[1]
        distance_to_base = math.sqrt(dx * dx + dy * dy)

        if distance_to_base <= self.base_range:
            # Linear falloff from base
            base_signal = 100.0 * (1.0 - (distance_to_base / self.base_range))
            max_signal = max(max_signal, base_signal)

        # Check all transmitters
        for transmitter in self.transmitters.values():
            if transmitter.is_active:
                signal = transmitter.get_signal_strength_at(position)
                max_signal = max(max_signal, signal)

        return max_signal

    def get_coverage_quality(self, position: Tuple[float, float]) -> str:
        """
        Get signal coverage quality at a position.

        Args:
            position: (x, y) position

        Returns:
            str: "excellent", "good", "poor", or "none"
        """
        signal = self.get_signal_strength_at(position)

        if signal >= 80.0:
            return "excellent"
        elif signal >= self.good_signal_threshold:
            return "good"
        elif signal >= self.min_signal_for_control:
            return "poor"
        else:
            return "none"

    def update(self, dt: float, game_time: float):
        """
        Update transmitter system.

        Args:
            dt: Delta time in seconds
            game_time: Current game time
        """
        # Update transmitters (future: power drain, maintenance, etc.)
        for transmitter in self.transmitters.values():
            # Currently transmitters are always on
            # Could add power management, maintenance, etc.
            pass

    def get_transmitter_count_by_type(self) -> Dict[TransmitterType, int]:
        """Get count of transmitters by type."""
        counts = {t: 0 for t in TransmitterType}

        for transmitter in self.transmitters.values():
            counts[transmitter.transmitter_type] += 1

        return counts

    def get_total_coverage_area(self) -> float:
        """
        Get total coverage area (approximate).

        Returns:
            float: Total area in square tiles
        """
        # Base coverage
        total_area = math.pi * self.base_range * self.base_range

        # Add transmitter coverage (rough approximation, doesn't account for overlap)
        for transmitter in self.transmitters.values():
            if transmitter.is_active:
                total_area += math.pi * transmitter.range * transmitter.range

        return total_area

    def get_summary(self) -> Dict:
        """
        Get transmitter system summary.

        Returns:
            dict: Summary information
        """
        type_counts = self.get_transmitter_count_by_type()

        return {
            'total_transmitters': len(self.transmitters),
            'transmitters_by_type': {t.name: count for t, count in type_counts.items()},
            'coverage_area': self.get_total_coverage_area(),
            'total_placed': self.total_transmitters_placed,
            'base_range': self.base_range
        }

    def __repr__(self):
        """String representation for debugging."""
        return (f"TransmitterManager(transmitters={len(self.transmitters)}, "
                f"coverage_area={self.get_total_coverage_area():.0f} tiles²)")
