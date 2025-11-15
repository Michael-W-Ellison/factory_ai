"""
DroneManager - manages reconnaissance drones and fog of war system.

Handles:
- Drone deployment and control
- Fog of war visibility tracking
- Drone battery management
- Automatic return to base
- Vision radius and exploration
"""

import math
import random
from enum import Enum
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass


class DroneState(Enum):
    """Drone operational states."""
    IDLE = 0  # At base, ready to deploy
    FLYING = 1  # In flight, exploring
    RETURNING = 2  # Returning to base (low battery)
    CRASHED = 3  # Battery depleted, crashed
    CHARGING = 4  # At base, recharging


@dataclass
class Drone:
    """
    Reconnaissance drone for exploring the map.

    Attributes:
        id: Unique drone identifier
        position: (x, y) position on map
        state: Current operational state
        battery: Battery level (0-100%)
        max_battery: Maximum battery capacity
        speed: Movement speed (tiles/second)
        vision_radius: How far the drone can see (tiles)
        battery_drain_rate: Battery drain per second while flying (%)
        target_position: Target position for movement
    """
    id: int
    position: Tuple[float, float]
    state: DroneState
    battery: float = 100.0
    max_battery: float = 100.0
    speed: float = 5.0  # 5 tiles/second
    vision_radius: float = 10.0  # 10 tile radius
    battery_drain_rate: float = 1.0  # 1% per second
    target_position: Optional[Tuple[float, float]] = None
    base_position: Tuple[float, float] = (0, 0)

    def get_distance_to(self, position: Tuple[float, float]) -> float:
        """Calculate distance to a position."""
        dx = position[0] - self.position[0]
        dy = position[1] - self.position[1]
        return math.sqrt(dx * dx + dy * dy)

    def move_towards(self, target: Tuple[float, float], dt: float) -> bool:
        """
        Move towards target position.

        Returns:
            bool: True if reached target, False otherwise
        """
        distance = self.get_distance_to(target)

        if distance < 0.1:
            return True  # Reached target

        # Calculate movement
        move_distance = self.speed * dt

        if move_distance >= distance:
            # Will reach target this frame
            self.position = target
            return True

        # Move towards target
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]

        # Normalize and scale by move_distance
        norm = math.sqrt(dx * dx + dy * dy)
        dx = (dx / norm) * move_distance
        dy = (dy / norm) * move_distance

        self.position = (self.position[0] + dx, self.position[1] + dy)
        return False


class FogOfWar:
    """
    Fog of war system for map exploration.

    Tracks which tiles have been explored by drones.
    """

    def __init__(self, map_width: int, map_height: int):
        """
        Initialize fog of war.

        Args:
            map_width: Width of map in tiles
            map_height: Height of map in tiles
        """
        self.map_width = map_width
        self.map_height = map_height

        # Explored tiles: set of (x, y) positions
        self.explored_tiles: Set[Tuple[int, int]] = set()

        # Currently visible tiles (updated each frame)
        self.visible_tiles: Set[Tuple[int, int]] = set()

        # Start with factory area explored (10x10 around origin)
        for x in range(-5, 6):
            for y in range(-5, 6):
                self.explored_tiles.add((x, y))

    def reveal_area(self, center: Tuple[float, float], radius: float, is_permanent: bool = True):
        """
        Reveal area around a position.

        Args:
            center: (x, y) center position
            radius: Radius to reveal
            is_permanent: If True, adds to explored_tiles; if False, adds to visible_tiles
        """
        cx, cy = center
        tile_cx = int(cx)
        tile_cy = int(cy)

        # Calculate integer radius
        int_radius = int(radius) + 1

        # Reveal all tiles in radius
        revealed = []
        for dx in range(-int_radius, int_radius + 1):
            for dy in range(-int_radius, int_radius + 1):
                # Check if within circular radius
                if dx * dx + dy * dy <= radius * radius:
                    tile_x = tile_cx + dx
                    tile_y = tile_cy + dy

                    # Check bounds
                    if -self.map_width // 2 <= tile_x < self.map_width // 2 and \
                       -self.map_height // 2 <= tile_y < self.map_height // 2:
                        tile = (tile_x, tile_y)
                        revealed.append(tile)

                        if is_permanent:
                            self.explored_tiles.add(tile)
                        else:
                            self.visible_tiles.add(tile)

        return revealed

    def is_explored(self, position: Tuple[int, int]) -> bool:
        """Check if a tile has been explored."""
        return position in self.explored_tiles

    def is_visible(self, position: Tuple[int, int]) -> bool:
        """Check if a tile is currently visible."""
        return position in self.visible_tiles or position in self.explored_tiles

    def clear_visible_tiles(self):
        """Clear currently visible tiles (call at start of frame)."""
        self.visible_tiles.clear()

    def get_exploration_percentage(self) -> float:
        """Get percentage of map explored."""
        total_tiles = self.map_width * self.map_height
        explored_count = len(self.explored_tiles)
        return (explored_count / total_tiles) * 100.0


class DroneManager:
    """
    Manages reconnaissance drones and fog of war.

    Drones can be deployed to explore the map, revealing areas
    through the fog of war system.
    """

    def __init__(self, resource_manager, map_width: int = 200, map_height: int = 200):
        """
        Initialize drone manager.

        Args:
            resource_manager: ResourceManager instance
            map_width: Width of map in tiles
            map_height: Height of map in tiles
        """
        self.resources = resource_manager
        self.map_width = map_width
        self.map_height = map_height

        # Fog of war system
        self.fog_of_war = FogOfWar(map_width, map_height)

        # Drones
        self.drones: Dict[int, Drone] = {}
        self.next_drone_id = 1
        self.max_drones = 5  # Maximum drones that can be owned

        # Drone costs and stats
        self.drone_purchase_cost = 5000
        self.drone_battery_capacity = 100.0  # 100 seconds of flight
        self.drone_speed = 5.0  # 5 tiles/second
        self.drone_vision_radius = 10.0  # 10 tile radius
        self.drone_battery_drain = 1.0  # 1% per second
        self.drone_charge_rate = 2.0  # 2% per second at base

        # Base position (factory location)
        self.base_position = (0.0, 0.0)

        # Auto-return threshold
        self.auto_return_battery = 20.0  # Return to base at 20% battery

        # Statistics
        self.total_tiles_explored = 0
        self.drones_deployed = 0
        self.drones_crashed = 0

    def purchase_drone(self) -> bool:
        """
        Purchase a new drone.

        Returns:
            bool: True if successful, False if insufficient funds or max drones
        """
        if len(self.drones) >= self.max_drones:
            return False

        if self.resources.money < self.drone_purchase_cost:
            return False

        # Purchase drone
        self.resources.modify_money(-self.drone_purchase_cost)

        # Create drone at base
        drone = Drone(
            id=self.next_drone_id,
            position=self.base_position,
            state=DroneState.IDLE,
            battery=100.0,
            max_battery=self.drone_battery_capacity,
            speed=self.drone_speed,
            vision_radius=self.drone_vision_radius,
            battery_drain_rate=self.drone_battery_drain,
            base_position=self.base_position
        )

        self.drones[self.next_drone_id] = drone
        self.next_drone_id += 1

        print(f"\n🚁 DRONE PURCHASED")
        print(f"  Cost: ${self.drone_purchase_cost:,}")
        print(f"  Total drones: {len(self.drones)}/{self.max_drones}")

        return True

    def deploy_drone(self, drone_id: int, target_position: Tuple[float, float]) -> bool:
        """
        Deploy a drone to a target position.

        Args:
            drone_id: ID of drone to deploy
            target_position: Target (x, y) position

        Returns:
            bool: True if successful, False otherwise
        """
        if drone_id not in self.drones:
            return False

        drone = self.drones[drone_id]

        # Can only deploy idle or charging drones
        if drone.state not in (DroneState.IDLE, DroneState.CHARGING):
            return False

        # Check battery
        if drone.battery < 10.0:
            print(f"⚠️ Drone {drone_id} battery too low to deploy ({drone.battery:.1f}%)")
            return False

        # Deploy drone
        drone.state = DroneState.FLYING
        drone.target_position = target_position

        self.drones_deployed += 1

        print(f"\n🚁 DRONE {drone_id} DEPLOYED")
        print(f"  Target: ({target_position[0]:.0f}, {target_position[1]:.0f})")
        print(f"  Battery: {drone.battery:.1f}%")

        return True

    def recall_drone(self, drone_id: int) -> bool:
        """
        Recall a drone to base.

        Args:
            drone_id: ID of drone to recall

        Returns:
            bool: True if successful, False otherwise
        """
        if drone_id not in self.drones:
            return False

        drone = self.drones[drone_id]

        # Can only recall flying drones
        if drone.state != DroneState.FLYING:
            return False

        # Set to returning
        drone.state = DroneState.RETURNING
        drone.target_position = drone.base_position

        print(f"\n🚁 DRONE {drone_id} RECALLED")
        print(f"  Returning to base")
        print(f"  Battery: {drone.battery:.1f}%")

        return True

    def update(self, dt: float, game_time: float):
        """
        Update all drones and fog of war.

        Args:
            dt: Delta time in seconds
            game_time: Current game time
        """
        # Clear visible tiles
        self.fog_of_war.clear_visible_tiles()

        # Update each drone
        for drone_id, drone in list(self.drones.items()):
            self._update_drone(drone, dt)

        # Update exploration stats
        self.total_tiles_explored = len(self.fog_of_war.explored_tiles)

    def _update_drone(self, drone: Drone, dt: float):
        """Update a single drone."""
        if drone.state == DroneState.IDLE:
            # Idle, do nothing
            pass

        elif drone.state == DroneState.CHARGING:
            # Charge battery
            drone.battery = min(drone.max_battery, drone.battery + self.drone_charge_rate * dt)

            # Once fully charged, become idle
            if drone.battery >= drone.max_battery:
                drone.state = DroneState.IDLE

        elif drone.state == DroneState.FLYING:
            # Drain battery
            drone.battery -= drone.battery_drain_rate * dt

            # Reveal area around drone
            self.fog_of_war.reveal_area(drone.position, drone.vision_radius, is_permanent=True)

            # Move towards target
            if drone.target_position:
                reached = drone.move_towards(drone.target_position, dt)

                if reached:
                    # Reached target, hover in place
                    drone.target_position = None

            # Check battery
            if drone.battery <= 0:
                # Crashed!
                drone.state = DroneState.CRASHED
                drone.battery = 0
                self.drones_crashed += 1
                print(f"\n💥 DRONE {drone.id} CRASHED!")
                print(f"  Position: ({drone.position[0]:.0f}, {drone.position[1]:.0f})")
                print(f"  Battery depleted")

            elif drone.battery <= self.auto_return_battery:
                # Auto-return to base
                drone.state = DroneState.RETURNING
                drone.target_position = drone.base_position
                print(f"\n⚠️ DRONE {drone.id} AUTO-RETURNING")
                print(f"  Low battery: {drone.battery:.1f}%")

        elif drone.state == DroneState.RETURNING:
            # Drain battery
            drone.battery -= drone.battery_drain_rate * dt

            # Reveal area around drone
            self.fog_of_war.reveal_area(drone.position, drone.vision_radius, is_permanent=True)

            # Move towards base
            reached = drone.move_towards(drone.base_position, dt)

            if reached:
                # Reached base
                drone.state = DroneState.CHARGING
                drone.target_position = None
                print(f"\n🚁 DRONE {drone.id} RETURNED TO BASE")
                print(f"  Battery: {drone.battery:.1f}%")
                print(f"  Charging...")

            # Check battery
            if drone.battery <= 0:
                # Crashed during return!
                drone.state = DroneState.CRASHED
                drone.battery = 0
                self.drones_crashed += 1
                print(f"\n💥 DRONE {drone.id} CRASHED DURING RETURN!")
                print(f"  Position: ({drone.position[0]:.0f}, {drone.position[1]:.0f})")

        elif drone.state == DroneState.CRASHED:
            # Crashed, permanently lost
            pass

    def get_drone_count(self) -> Dict[str, int]:
        """Get count of drones by state."""
        counts = {
            'idle': 0,
            'flying': 0,
            'returning': 0,
            'charging': 0,
            'crashed': 0,
            'total': len(self.drones)
        }

        for drone in self.drones.values():
            if drone.state == DroneState.IDLE:
                counts['idle'] += 1
            elif drone.state == DroneState.FLYING:
                counts['flying'] += 1
            elif drone.state == DroneState.RETURNING:
                counts['returning'] += 1
            elif drone.state == DroneState.CHARGING:
                counts['charging'] += 1
            elif drone.state == DroneState.CRASHED:
                counts['crashed'] += 1

        return counts

    def get_exploration_percentage(self) -> float:
        """Get percentage of map explored."""
        return self.fog_of_war.get_exploration_percentage()

    def is_position_explored(self, position: Tuple[int, int]) -> bool:
        """Check if a position has been explored."""
        return self.fog_of_war.is_explored(position)

    def is_position_visible(self, position: Tuple[int, int]) -> bool:
        """Check if a position is currently visible."""
        return self.fog_of_war.is_visible(position)

    def get_summary(self) -> Dict:
        """
        Get drone system summary.

        Returns:
            dict: Summary information
        """
        drone_counts = self.get_drone_count()

        return {
            'drones': drone_counts,
            'max_drones': self.max_drones,
            'exploration_percent': self.get_exploration_percentage(),
            'tiles_explored': self.total_tiles_explored,
            'drones_deployed': self.drones_deployed,
            'drones_crashed': self.drones_crashed,
            'purchase_cost': self.drone_purchase_cost
        }

    def __repr__(self):
        """String representation for debugging."""
        counts = self.get_drone_count()
        return (f"DroneManager(drones={counts['total']}, "
                f"flying={counts['flying']}, "
                f"exploration={self.get_exploration_percentage():.1f}%)")
