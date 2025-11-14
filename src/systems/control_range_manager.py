"""
Control Range Manager - Manages robot control range and wireless transmitters.

Key features:
- Factory base control range: 200 tiles
- Wireless transmitters extend range
- Overlapping ranges merge
- Robots outside range are autonomous only
- Inside range: full control, real-time status, threat warnings
- Outside range: no manual control, higher risk
"""

from typing import List, Tuple, Dict
import math


class ControlRangeManager:
    """
    Manages control range for robots.

    Control range determines where the player can manually control robots
    and receive real-time information. Outside this range, robots operate
    autonomously with higher risk.
    """

    def __init__(self, factory_x: float, factory_y: float):
        """
        Initialize control range manager.

        Args:
            factory_x: Factory x position
            factory_y: Factory y position
        """
        # Factory position (main control center)
        self.factory_x = factory_x
        self.factory_y = factory_y
        self.factory_base_range = 200  # tiles

        # Wireless transmitters (list of (x, y, range, level))
        self.transmitters = []

        # Research levels affect transmitter range
        self.transmitter_ranges = {
            1: 300,  # Wireless Transmitters I
            2: 450,  # Wireless Transmitters II
            3: 600,  # Wireless Transmitters III
        }

        # Control range visualization
        self.show_range = False

    def add_transmitter(self, x: float, y: float, level: int = 1):
        """
        Add wireless transmitter.

        Args:
            x: Transmitter x position
            y: Transmitter y position
            level: Research level (1, 2, or 3)
        """
        transmitter_range = self.transmitter_ranges.get(level, 300)
        self.transmitters.append((x, y, transmitter_range, level))
        print(f"\n📡 Wireless Transmitter added at ({x}, {y})")
        print(f"   Range: {transmitter_range} tiles")
        print(f"   Level: {level}")
        print()

    def remove_transmitter(self, x: float, y: float):
        """
        Remove wireless transmitter at position.

        Args:
            x: Transmitter x position
            y: Transmitter y position
        """
        for i, (tx, ty, _, _) in enumerate(self.transmitters):
            if abs(tx - x) < 10 and abs(ty - y) < 10:  # Nearby
                self.transmitters.pop(i)
                print(f"\n📡 Wireless Transmitter removed from ({x}, {y})")
                return True
        return False

    def is_in_control_range(self, x: float, y: float) -> bool:
        """
        Check if position is within control range.

        Args:
            x: Position x
            y: Position y

        Returns:
            bool: True if in control range
        """
        # Check factory range
        dist_to_factory = self._distance(x, y, self.factory_x, self.factory_y)
        if dist_to_factory <= self.factory_base_range:
            return True

        # Check each transmitter
        for tx, ty, trans_range, _ in self.transmitters:
            dist_to_transmitter = self._distance(x, y, tx, ty)
            if dist_to_transmitter <= trans_range:
                return True

        return False

    def get_nearest_control_point(self, x: float, y: float) -> Tuple[float, float]:
        """
        Get nearest control point (factory or transmitter) from position.

        Args:
            x: Position x
            y: Position y

        Returns:
            Tuple of (point_x, point_y)
        """
        min_dist = float('inf')
        nearest_point = (self.factory_x, self.factory_y)

        # Check factory
        dist = self._distance(x, y, self.factory_x, self.factory_y)
        if dist < min_dist:
            min_dist = dist
            nearest_point = (self.factory_x, self.factory_y)

        # Check transmitters
        for tx, ty, _, _ in self.transmitters:
            dist = self._distance(x, y, tx, ty)
            if dist < min_dist:
                min_dist = dist
                nearest_point = (tx, ty)

        return nearest_point

    def get_distance_to_control_range(self, x: float, y: float) -> float:
        """
        Get distance from position to nearest control range edge.

        Args:
            x: Position x
            y: Position y

        Returns:
            float: Distance to control range (0 if inside, positive if outside)
        """
        # Check factory range
        dist_to_factory = self._distance(x, y, self.factory_x, self.factory_y)
        min_dist_to_range = dist_to_factory - self.factory_base_range

        # Check each transmitter
        for tx, ty, trans_range, _ in self.transmitters:
            dist_to_transmitter = self._distance(x, y, tx, ty)
            dist_to_range = dist_to_transmitter - trans_range
            if dist_to_range < min_dist_to_range:
                min_dist_to_range = dist_to_range

        return max(0, min_dist_to_range)

    def get_control_coverage_percent(self, x1: float, y1: float, x2: float, y2: float,
                                     sample_points: int = 100) -> float:
        """
        Get percentage of area covered by control range.

        Args:
            x1, y1: Top-left corner of area
            x2, y2: Bottom-right corner of area
            sample_points: Number of sample points to check

        Returns:
            float: Percentage of area in control range (0-100)
        """
        points_in_range = 0

        for _ in range(sample_points):
            import random
            x = random.uniform(x1, x2)
            y = random.uniform(y1, y2)

            if self.is_in_control_range(x, y):
                points_in_range += 1

        return (points_in_range / sample_points) * 100

    def get_all_control_points(self) -> List[Tuple[float, float, float]]:
        """
        Get all control points with their ranges.

        Returns:
            List of (x, y, range) tuples
        """
        points = [(self.factory_x, self.factory_y, self.factory_base_range)]

        for tx, ty, trans_range, _ in self.transmitters:
            points.append((tx, ty, trans_range))

        return points

    def _distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate distance between two points."""
        dx = x2 - x1
        dy = y2 - y1
        return math.sqrt(dx * dx + dy * dy)

    def toggle_range_visualization(self):
        """Toggle control range visualization."""
        self.show_range = not self.show_range
        return self.show_range

    def get_stats(self) -> Dict:
        """Get control range statistics."""
        return {
            'factory_position': (self.factory_x, self.factory_y),
            'factory_range': self.factory_base_range,
            'transmitter_count': len(self.transmitters),
            'total_control_points': len(self.transmitters) + 1,
            'show_range': self.show_range,
        }
