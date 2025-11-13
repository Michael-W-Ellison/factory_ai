"""
Police Manager - manages police patrols and responses to suspicion.

Handles:
- Spawning police patrols
- Generating patrol routes
- Adjusting police presence based on suspicion level
- Coordinating police responses to detections
"""

import random
from typing import List, Tuple
from src.entities.police_officer import PoliceOfficer, PoliceBehavior
from src.world.tile import TileType


class PoliceManager:
    """
    Manages all police officers and patrols in the game world.

    Adjusts police presence based on suspicion level and coordinates
    responses to illegal activities.
    """

    def __init__(self, grid, suspicion_manager):
        """
        Initialize the police manager.

        Args:
            grid: The game world grid
            suspicion_manager: SuspicionManager instance
        """
        self.grid = grid
        self.suspicion_manager = suspicion_manager
        self.police_officers: List[PoliceOfficer] = []

        # Base patrol count (increases with suspicion)
        self.base_patrol_count = 2  # 2 patrols at low suspicion
        self.officers_per_patrol = 2  # 2 officers per patrol

    def spawn_initial_patrols(self, seed: int = 42):
        """
        Spawn initial police patrols.

        Args:
            seed (int): Random seed for reproducible spawning
        """
        rng = random.Random(seed)

        # Generate patrol routes
        patrol_routes = self._generate_patrol_routes(rng, count=self.base_patrol_count)

        # Spawn officers for each route
        for route in patrol_routes:
            self._spawn_patrol(route, rng)

        print(f"Spawned {len(self.police_officers)} police officers in {len(patrol_routes)} patrols")

    def _generate_patrol_routes(self, rng: random.Random, count: int) -> List[List[Tuple[int, int]]]:
        """
        Generate patrol routes through the city.

        Args:
            rng: Random number generator
            count (int): Number of routes to generate

        Returns:
            List of patrol routes (each route is a list of waypoints)
        """
        routes = []

        # Find road tiles for patrol routes
        road_tiles = []
        for y in range(self.grid.height_tiles):
            for x in range(self.grid.width_tiles):
                tile = self.grid.get_tile(x, y)
                if tile and tile.tile_type in [TileType.ROAD_DIRT, TileType.ROAD_TAR, TileType.ROAD_ASPHALT]:
                    road_tiles.append((x, y))

        if not road_tiles:
            print("Warning: No road tiles found for police patrols")
            return routes

        # Generate routes
        for i in range(count):
            route = []
            route_length = rng.randint(8, 16)  # 8-16 waypoints per route

            # Start at random road tile
            current = rng.choice(road_tiles)
            route.append(current)

            # Add waypoints by moving to nearby road tiles
            for j in range(route_length - 1):
                # Find nearby road tiles
                nearby = []
                for tile in road_tiles:
                    dx = tile[0] - current[0]
                    dy = tile[1] - current[1]
                    distance = (dx * dx + dy * dy) ** 0.5
                    if 3 < distance < 15:  # Not too close, not too far
                        nearby.append(tile)

                if nearby:
                    current = rng.choice(nearby)
                    route.append(current)
                else:
                    # No nearby tiles, pick random
                    current = rng.choice(road_tiles)
                    route.append(current)

            routes.append(route)

        return routes

    def _spawn_patrol(self, route: List[Tuple[int, int]], rng: random.Random):
        """
        Spawn a police patrol along a route.

        Args:
            route (List[Tuple[int, int]]): Patrol route waypoints
            rng: Random number generator
        """
        if not route:
            return

        # Spawn officers along the route (spread out)
        for i in range(self.officers_per_patrol):
            # Spread officers along route
            waypoint_index = (i * len(route)) // self.officers_per_patrol
            waypoint = route[waypoint_index]

            # Convert to world coordinates
            world_x = waypoint[0] * self.grid.tile_size + self.grid.tile_size // 2
            world_y = waypoint[1] * self.grid.tile_size + self.grid.tile_size // 2

            # Add some random offset
            world_x += rng.randint(-8, 8)
            world_y += rng.randint(-8, 8)

            # Create police officer
            officer = PoliceOfficer(world_x, world_y, patrol_route=route)
            # Start each officer at a different waypoint
            officer.current_waypoint = waypoint_index

            self.police_officers.append(officer)

    def update_police_presence(self):
        """
        Update police presence based on suspicion level.

        Spawns/removes patrols to match suspicion tier.
        """
        # Determine target patrol count based on suspicion
        suspicion_level = self.suspicion_manager.suspicion_level
        from src.systems.suspicion_manager import SuspicionTier

        if suspicion_level < 20:
            # Normal: base patrols
            target_patrols = self.base_patrol_count
        elif suspicion_level < 40:
            # Rumors: +1 patrol
            target_patrols = self.base_patrol_count + 1
        elif suspicion_level < 60:
            # Investigation: +2 patrols
            target_patrols = self.base_patrol_count + 2
        elif suspicion_level < 80:
            # Inspection: +3 patrols
            target_patrols = self.base_patrol_count + 3
        else:
            # Restrictions: +4 patrols
            target_patrols = self.base_patrol_count + 4

        # Calculate current patrol count
        current_patrol_count = len(self.police_officers) // self.officers_per_patrol

        # Add or remove patrols
        if current_patrol_count < target_patrols:
            # Add patrols
            to_add = target_patrols - current_patrol_count
            rng = random.Random(int(suspicion_level * 1000))
            new_routes = self._generate_patrol_routes(rng, to_add)
            for route in new_routes:
                self._spawn_patrol(route, rng)
            print(f"⚠ Police presence increased: {current_patrol_count} → {target_patrols} patrols (suspicion: {suspicion_level:.1f})")
        elif current_patrol_count > target_patrols and suspicion_level < 20:
            # Remove patrols (only when suspicion is low)
            to_remove = (current_patrol_count - target_patrols) * self.officers_per_patrol
            for i in range(to_remove):
                if self.police_officers:
                    self.police_officers.pop()
            print(f"✓ Police presence decreased: {current_patrol_count} → {target_patrols} patrols")

    def update(self, dt: float, game_time: float):
        """
        Update all police officers.

        Args:
            dt (float): Delta time in seconds
            game_time (float): Current game time in hours (0-24)
        """
        # Update all officers
        for officer in self.police_officers:
            officer.update(dt, game_time)

    def handle_detection_report(self, report: dict):
        """
        Handle a detection report by dispatching police to investigate.

        Args:
            report (dict): Detection report from DetectionManager
        """
        # Only respond to high-level detections
        from src.systems.detection_manager import DetectionLevel
        detection_level = report.get('detection_level', DetectionLevel.GLANCE)

        if detection_level == DetectionLevel.REPORT:
            # Full detection - send nearby officers to investigate
            location = report.get('location', (0, 0))
            robot = report.get('robot', None)

            # Find nearest officer
            nearest_officer = None
            min_distance = float('inf')

            for officer in self.police_officers:
                dx = officer.world_x - location[0]
                dy = officer.world_y - location[1]
                distance = (dx * dx + dy * dy) ** 0.5

                if distance < min_distance:
                    min_distance = distance
                    nearest_officer = officer

            # Dispatch officer
            if nearest_officer and min_distance < 500:  # Within 500 pixels
                if robot and hasattr(robot, 'id'):
                    # Chase the robot if we have a reference
                    nearest_officer.start_chase(robot)
                    print(f"🚨 Police officer dispatched to chase robot at ({location[0]:.0f}, {location[1]:.0f})")
                else:
                    # Just investigate the location
                    nearest_officer.start_investigation(location)
                    print(f"🔍 Police officer investigating suspicious activity at ({location[0]:.0f}, {location[1]:.0f})")

    def check_captures(self, robots: List) -> List:
        """
        Check if any police officers have captured robots.

        Args:
            robots: List of robot entities

        Returns:
            List of captured robots
        """
        captured = []

        for officer in self.police_officers:
            if officer.behavior == PoliceBehavior.CAPTURE and officer.chase_target:
                if officer.chase_target in robots:
                    captured.append(officer.chase_target)
                    print(f"⚠️ POLICE CAPTURED ROBOT! Game Over!")

        return captured

    def render(self, screen, camera):
        """
        Render all police officers.

        Args:
            screen: Pygame surface
            camera: Camera for world-to-screen transformation
        """
        for officer in self.police_officers:
            officer.render(screen, camera)

    def get_stats(self) -> dict:
        """
        Get police statistics.

        Returns:
            Dictionary with police stats
        """
        # Count by behavior
        by_behavior = {}
        for officer in self.police_officers:
            behavior = officer.behavior
            by_behavior[behavior] = by_behavior.get(behavior, 0) + 1

        return {
            'total_officers': len(self.police_officers),
            'patrol_count': len(self.police_officers) // self.officers_per_patrol,
            'by_behavior': by_behavior,
        }
