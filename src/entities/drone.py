"""
Drone - Flying reconnaissance entity for revealing fog of war.

Key features:
- Flies over terrain (no ground collision)
- Fast movement speed (200 px/s)
- Limited battery (15 minutes)
- Large vision range (300 tiles)
- Cannot collect materials
- Reveals fog of war
- Returns to pad when low battery
"""

from enum import Enum
import math


class DroneState(Enum):
    """Drone operational states."""
    IDLE = "idle"
    PATROL = "patrol"
    MANUAL = "manual"
    RETURNING = "returning"
    CHARGING = "charging"
    OFFLINE = "offline"


class Drone:
    """
    Flying reconnaissance drone.

    Drones reveal fog of war and scout areas but cannot collect materials.
    They have limited battery and must return to recharge.
    """

    def __init__(self, drone_id, x, y, drone_pad=None):
        """Initialize drone."""
        self.drone_id = drone_id
        self.x = x
        self.y = y
        self.drone_pad = drone_pad

        # Movement
        self.speed = 200.0
        self.target_x = None
        self.target_y = None

        # State
        self.state = DroneState.IDLE

        # Battery
        self.max_battery = 15 * 60  # 15 minutes
        self.battery = self.max_battery
        self.battery_drain_rate = 1.0
        self.charge_rate = 3.0
        self.low_battery_threshold = 3 * 60

        # Vision
        self.vision_range = 300

        # Patrol
        self.patrol_route = []
        self.current_waypoint = 0

        # Research
        self.research_level = 1

        # Statistics
        self.total_distance_traveled = 0.0
        self.total_flight_time = 0.0
        self.area_revealed = 0

    def update(self, dt: float):
        """Update drone state."""
        # Battery drain/charge
        if self.state in [DroneState.PATROL, DroneState.MANUAL, DroneState.RETURNING]:
            self.battery -= self.battery_drain_rate * dt
            self.total_flight_time += dt

            if self.battery <= self.low_battery_threshold and self.state != DroneState.RETURNING:
                self._start_return_to_pad()

            if self.battery <= 0:
                self.battery = 0
                self.state = DroneState.OFFLINE
                return

        elif self.state == DroneState.CHARGING:
            self.battery = min(self.max_battery, self.battery + self.charge_rate * dt)
            if self.battery >= self.max_battery:
                self.state = DroneState.IDLE

        # Movement
        if self.target_x is not None and self.target_y is not None:
            self._move_towards_target(dt)

        # Patrol logic
        if self.state == DroneState.PATROL and len(self.patrol_route) > 0:
            self._follow_patrol_route()

    def _move_towards_target(self, dt: float):
        """Move drone towards target position."""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 5:  # Reached target
            self.x = self.target_x
            self.y = self.target_y
            self.target_x = None
            self.target_y = None

            # Check if returning to pad
            if self.state == DroneState.RETURNING and self.drone_pad:
                self.state = DroneState.CHARGING
        else:
            # Move towards target
            move_distance = self.speed * dt
            if move_distance > distance:
                move_distance = distance

            self.x += (dx / distance) * move_distance
            self.y += (dy / distance) * move_distance
            self.total_distance_traveled += move_distance

    def _follow_patrol_route(self):
        """Follow patrol route waypoints."""
        if len(self.patrol_route) == 0:
            return

        waypoint = self.patrol_route[self.current_waypoint]
        self.target_x, self.target_y = waypoint

        # Check if reached waypoint
        if self.target_x is None:  # Just reached waypoint
            self.current_waypoint = (self.current_waypoint + 1) % len(self.patrol_route)

    def _start_return_to_pad(self):
        """Start returning to drone pad."""
        if self.drone_pad:
            self.state = DroneState.RETURNING
            self.target_x = self.drone_pad.x
            self.target_y = self.drone_pad.y
            print(f"Drone {self.drone_id} returning to pad (low battery)")

    def set_manual_target(self, x: float, y: float):
        """Set manual flight target."""
        self.state = DroneState.MANUAL
        self.target_x = x
        self.target_y = y

    def start_patrol(self, route: list):
        """Start patrol with given route."""
        if len(route) > 0:
            self.patrol_route = route
            self.current_waypoint = 0
            self.state = DroneState.PATROL

    def stop_patrol(self):
        """Stop patrol and hover."""
        self.state = DroneState.IDLE
        self.target_x = None
        self.target_y = None

    def get_battery_percent(self) -> float:
        """Get battery percentage."""
        return (self.battery / self.max_battery) * 100

    def is_operational(self) -> bool:
        """Check if drone is operational."""
        return self.state != DroneState.OFFLINE

    def get_stats(self) -> dict:
        """Get drone statistics."""
        return {
            'drone_id': self.drone_id,
            'state': self.state.value,
            'battery_percent': self.get_battery_percent(),
            'position': (self.x, self.y),
            'total_distance': self.total_distance_traveled,
            'total_flight_time': self.total_flight_time,
            'area_revealed': self.area_revealed,
        }
