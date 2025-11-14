"""
NPC Manager - manages NPC spawning, scheduling, and detection.

Handles:
- Spawning NPCs in houses throughout the city
- Assigning home and work locations
- Updating NPC schedules and movement
- Detection of illegal robot activities
- Suspicion generation from detections
"""

import random
from typing import List, Tuple, Optional
from src.entities.npc import NPC, Activity
from src.world.tile import TileType


class NPCManager:
    """
    Manages all NPCs in the game world.

    Spawns NPCs in houses, assigns them jobs, and handles their daily schedules.
    """

    def __init__(self, grid):
        """
        Initialize the NPC manager.

        Args:
            grid: The game world grid
        """
        self.grid = grid
        self.npcs: List[NPC] = []

        # Game time (0-24 hours, wraps around)
        self.game_time = 8.0  # Start at 8am
        self.time_scale = 60.0  # Game seconds per real second (1 real minute = 1 game hour)

        # NPC spawning parameters
        self.npcs_per_house = 2  # Average NPCs per house
        self.employment_rate = 0.7  # 70% of NPCs have jobs

        # Bus system integration
        self.bus_manager = None  # Set externally after bus system is initialized
        self.bus_usage_rate = 0.4  # 40% of NPCs prefer buses for commuting

    def spawn_npcs_in_city(self, seed: int = 42):
        """
        Spawn NPCs in houses throughout the city.

        Args:
            seed (int): Random seed for reproducible spawning
        """
        rng = random.Random(seed)

        # Find all houses and stores
        houses = self._find_buildings(TileType.BUILDING)

        print(f"Found {len(houses)} buildings for NPC housing")

        # Spawn NPCs in houses
        npc_count = 0
        for house_x, house_y in houses:
            # Random number of NPCs per house (1-3)
            num_npcs = rng.randint(1, 3)

            for i in range(num_npcs):
                # Calculate spawn position (center of house tile)
                world_x = house_x * self.grid.tile_size + self.grid.tile_size // 2
                world_y = house_y * self.grid.tile_size + self.grid.tile_size // 2

                # Add some randomvariation
                world_x += rng.randint(-8, 8)
                world_y += rng.randint(-8, 8)

                # Assign work location (if employed)
                work_x, work_y = None, None
                if rng.random() < self.employment_rate:
                    # Find a random workplace (store or other building)
                    if houses:  # Use houses list as potential workplaces
                        workplace = rng.choice(houses)
                        work_x, work_y = workplace

                # Create NPC
                npc = NPC(world_x, world_y, house_x, house_y, work_x, work_y)
                self.npcs.append(npc)
                npc_count += 1

        employed = sum(1 for npc in self.npcs if npc.has_job)
        print(f"Spawned {npc_count} NPCs ({employed} employed, {npc_count - employed} unemployed)")

    def _find_buildings(self, tile_type: int) -> List[Tuple[int, int]]:
        """
        Find all buildings of a specific type.

        Args:
            tile_type (int): Type of tile to find

        Returns:
            List of (grid_x, grid_y) tuples
        """
        buildings = []

        for y in range(self.grid.height_tiles):
            for x in range(self.grid.width_tiles):
                tile = self.grid.get_tile(x, y)
                if tile and tile.tile_type == tile_type:
                    buildings.append((x, y))

        return buildings

    def update(self, dt: float):
        """
        Update all NPCs and game time.

        Args:
            dt (float): Delta time in seconds
        """
        # Update game time
        self.game_time += (dt * self.time_scale) / 3600.0  # Convert to hours
        self.game_time = self.game_time % 24  # Wrap around at 24 hours

        # Update all NPCs
        for npc in self.npcs:
            npc.update(dt, self.game_time)

        # Handle bus commuting decisions
        if self.bus_manager:
            self._update_bus_commuting()

    def check_detections(self, robots: List, dt: float) -> List[dict]:
        """
        Check if any NPCs detect robots doing illegal activities.

        Args:
            robots: List of robot entities
            dt (float): Delta time

        Returns:
            List of detection reports (when NPCs fully detect robots)
        """
        reports = []
        is_daytime = 6 <= self.game_time < 20  # Day is 6am-8pm

        for npc in self.npcs:
            # Skip if sleeping (can't detect)
            if npc.current_activity == Activity.SLEEPING:
                continue

            for robot in robots:
                # Check if robot is doing something illegal
                # (For now, any robot activity could be suspicious)
                robot_stealth = getattr(robot, 'stealth_level', 0.5)

                # Calculate detection chance
                detection_chance = npc.calculate_detection_chance(
                    robot.x, robot.y, is_daytime, robot_stealth
                )

                if detection_chance > 0:
                    # Update detection progress
                    detected = npc.update_detection(robot.id, detection_chance, dt)

                    if detected:
                        # Full detection! Generate report
                        reports.append({
                            'npc': npc,
                            'robot': robot,
                            'time': self.game_time,
                            'location': (robot.x, robot.y),
                            'suspicion_increase': 10.0  # Base suspicion increase
                        })

                        # Reset detection for this robot
                        npc.clear_detection(robot.id)
                else:
                    # Robot not in vision, decay detection
                    if robot.id in npc.detecting_robots:
                        npc.detecting_robots[robot.id] -= 0.1 * dt
                        if npc.detecting_robots[robot.id] <= 0:
                            npc.clear_detection(robot.id)

        return reports

    def get_npc_at(self, world_x: float, world_y: float, tolerance: float = 16.0) -> Optional[NPC]:
        """
        Get NPC at a specific world position.

        Args:
            world_x (float): World X coordinate
            world_y (float): World Y coordinate
            tolerance (float): Distance tolerance in pixels

        Returns:
            NPC if found, None otherwise
        """
        for npc in self.npcs:
            dx = npc.world_x - world_x
            dy = npc.world_y - world_y
            distance = (dx * dx + dy * dy) ** 0.5

            if distance <= tolerance:
                return npc

        return None

    def render(self, screen, camera):
        """
        Render all NPCs.

        Args:
            screen: Pygame surface
            camera: Camera for world-to-screen transformation
        """
        for npc in self.npcs:
            npc.render(screen, camera)

    def get_stats(self) -> dict:
        """
        Get statistics about NPCs.

        Returns:
            Dictionary with NPC statistics
        """
        total = len(self.npcs)
        employed = sum(1 for npc in self.npcs if npc.has_job)
        unemployed = total - employed

        # Count activities
        activities = {}
        for npc in self.npcs:
            activity = npc.current_activity
            activities[activity] = activities.get(activity, 0) + 1

        return {
            'total': total,
            'employed': employed,
            'unemployed': unemployed,
            'current_time': self.game_time,
            'activities': activities,
        }

    def get_time_string(self) -> str:
        """
        Get formatted time string (HH:MM AM/PM).

        Returns:
            Formatted time string
        """
        hours = int(self.game_time)
        minutes = int((self.game_time - hours) * 60)

        # Convert to 12-hour format
        am_pm = 'AM' if hours < 12 else 'PM'
        display_hours = hours % 12
        if display_hours == 0:
            display_hours = 12

        return f"{display_hours:02d}:{minutes:02d} {am_pm}"

    def _update_bus_commuting(self):
        """
        Update NPCs who are commuting and might use buses.

        Checks NPCs who are commuting and decides if they should use the bus system.
        """
        if not self.bus_manager or not self.bus_manager.bus_stops:
            return

        for npc in self.npcs:
            # Check if NPC is starting a commute and prefers buses
            if (npc.current_activity in [Activity.COMMUTING_TO_WORK, Activity.COMMUTING_HOME] and
                not npc.using_bus and npc.bus_preference > (1.0 - self.bus_usage_rate)):

                # Check if NPC just started commuting (not already en route)
                import math
                distance_to_target = math.sqrt(
                    (npc.target_x - npc.world_x)**2 + (npc.target_y - npc.world_y)**2
                )

                # Only consider bus if destination is far enough (> 200 pixels)
                if distance_to_target > 200:
                    self._assign_bus_journey(npc)

            # Handle NPCs waiting at bus stops - add them to stop's waiting list
            elif npc.current_activity == Activity.WAITING_FOR_BUS and npc.target_bus_stop:
                stop_grid_x, stop_grid_y = npc.target_bus_stop
                bus_stop = self._find_bus_stop_at(stop_grid_x, stop_grid_y)

                if bus_stop and npc.id not in bus_stop.waiting_npcs:
                    bus_stop.add_waiting_npc(npc.id)

    def _assign_bus_journey(self, npc):
        """
        Assign a bus journey to an NPC.

        Args:
            npc: NPC to assign journey to
        """
        # Find nearest bus stop to current position
        current_grid_x = int(npc.world_x // self.grid.tile_size)
        current_grid_y = int(npc.world_y // self.grid.tile_size)

        nearest_start_stop = self.bus_manager.get_nearest_bus_stop(current_grid_x, current_grid_y)

        if not nearest_start_stop:
            return

        # Find nearest bus stop to destination
        dest_grid_x = int(npc.target_x // self.grid.tile_size)
        dest_grid_y = int(npc.target_y // self.grid.tile_size)

        nearest_dest_stop = self.bus_manager.get_nearest_bus_stop(dest_grid_x, dest_grid_y)

        if not nearest_dest_stop or nearest_dest_stop == nearest_start_stop:
            return

        # Start bus journey
        npc.start_bus_journey(
            bus_stop_pos=(nearest_start_stop.grid_x, nearest_start_stop.grid_y),
            destination_stop=(nearest_dest_stop.grid_x, nearest_dest_stop.grid_y),
            final_dest=(npc.target_x, npc.target_y)
        )

    def _find_bus_stop_at(self, grid_x: int, grid_y: int):
        """Find bus stop at a grid position."""
        if not self.bus_manager:
            return None

        for stop in self.bus_manager.bus_stops:
            if stop.grid_x == grid_x and stop.grid_y == grid_y:
                return stop
        return None
