"""
Vehicle Manager - manages vehicle spawning and tracking in the game world.

Handles:
- Spawning vehicles in appropriate locations (roads, parking areas)
- Tracking all vehicles in the world
- Managing working vs scrap vehicle distribution
- Vehicle removal when deconstructed
"""

import random
from typing import List, Tuple, Optional
from src.entities.vehicle import Vehicle
from src.world.tile import TileType


class VehicleManager:
    """
    Manages all vehicles in the game world.

    Spawns vehicles near buildings and on roads, with appropriate
    working/scrap distribution.
    """

    def __init__(self, grid):
        """
        Initialize the vehicle manager.

        Args:
            grid: The game world grid
        """
        self.grid = grid
        self.vehicles: List[Vehicle] = []

        # Spawn parameters
        self.scrap_ratio = 0.3  # 30% of vehicles are scrap (legal to deconstruct)
        self.vehicle_types = ['car', 'truck', 'van']
        self.vehicle_type_weights = [0.7, 0.15, 0.15]  # 70% cars, 15% trucks, 15% vans

    def spawn_vehicles_in_city(self, seed: int = 42, vehicle_density: float = 0.4):
        """
        Spawn vehicles throughout the city.

        Args:
            seed (int): Random seed for reproducible spawning
            vehicle_density (float): Probability of spawning a vehicle near a building (0.0-1.0)
        """
        rng = random.Random(seed)

        # Find all suitable spawn locations
        spawn_locations = self._find_spawn_locations()

        print(f"Found {len(spawn_locations)} potential vehicle spawn locations")

        # Spawn vehicles at selected locations
        spawned = 0
        for grid_x, grid_y, location_type in spawn_locations:
            # Random chance to spawn based on density
            if rng.random() > vehicle_density:
                continue

            # Choose vehicle type
            vehicle_type = rng.choices(self.vehicle_types, self.vehicle_type_weights)[0]

            # Determine if scrap or working
            is_scrap = rng.random() < self.scrap_ratio

            # Convert grid to world coordinates (center of tile)
            world_x = grid_x * self.grid.tile_size + self.grid.tile_size // 2
            world_y = grid_y * self.grid.tile_size + self.grid.tile_size // 2

            # Add some random offset within the tile for variety
            offset_x = rng.randint(-10, 10)
            offset_y = rng.randint(-10, 10)
            world_x += offset_x
            world_y += offset_y

            # Create vehicle
            vehicle = Vehicle(world_x, world_y, vehicle_type, is_scrap)
            self.vehicles.append(vehicle)
            spawned += 1

        print(f"Spawned {spawned} vehicles ({int(spawned * self.scrap_ratio)} scrap, {spawned - int(spawned * self.scrap_ratio)} working)")

    def _find_spawn_locations(self) -> List[Tuple[int, int, str]]:
        """
        Find all suitable locations to spawn vehicles.

        Returns:
            List of (grid_x, grid_y, location_type) tuples
        """
        locations = []

        # Check all tiles in the grid
        for y in range(self.grid.height_tiles):
            for x in range(self.grid.width_tiles):
                tile = self.grid.get_tile(x, y)
                if not tile:
                    continue

                # Spawn near buildings (parking)
                if tile.tile_type == TileType.BUILDING:
                    # Check adjacent tiles for parking spots (grass/dirt)
                    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                        check_x = x + dx
                        check_y = y + dy
                        if 0 <= check_x < self.grid.width_tiles and 0 <= check_y < self.grid.height_tiles:
                            check_tile = self.grid.get_tile(check_x, check_y)
                            if check_tile and check_tile.tile_type in [TileType.GRASS, TileType.DIRT]:
                                if not check_tile.occupied:
                                    locations.append((check_x, check_y, 'parking'))

                # Spawn on roads
                if tile.tile_type in [TileType.ROAD_DIRT, TileType.ROAD_TAR, TileType.ROAD_ASPHALT]:
                    if not tile.occupied:
                        locations.append((x, y, 'road'))

        return locations

    def get_vehicle_at(self, world_x: float, world_y: float, tolerance: float = 20.0) -> Optional[Vehicle]:
        """
        Get vehicle at a specific world position.

        Args:
            world_x (float): World X coordinate
            world_y (float): World Y coordinate
            tolerance (float): Distance tolerance in pixels

        Returns:
            Vehicle if found, None otherwise
        """
        for vehicle in self.vehicles:
            dx = vehicle.world_x - world_x
            dy = vehicle.world_y - world_y
            distance = (dx * dx + dy * dy) ** 0.5

            if distance <= tolerance:
                return vehicle

        return None

    def remove_vehicle(self, vehicle: Vehicle):
        """
        Remove a vehicle from the world.

        Args:
            vehicle: The vehicle to remove
        """
        if vehicle in self.vehicles:
            self.vehicles.remove(vehicle)

    def get_all_vehicles(self) -> List[Vehicle]:
        """
        Get all vehicles in the world.

        Returns:
            List of all vehicles
        """
        return self.vehicles.copy()

    def update(self, dt: float):
        """
        Update all vehicles.

        Args:
            dt (float): Delta time in seconds
        """
        # Update vehicle deconstruction
        for vehicle in self.vehicles[:]:  # Copy list to allow removal during iteration
            if vehicle.being_deconstructed:
                complete = vehicle.update_deconstruction(dt)
                if complete:
                    # Vehicle fully deconstructed - remove it
                    self.remove_vehicle(vehicle)

    def render(self, screen, camera):
        """
        Render all vehicles.

        Args:
            screen: Pygame surface
            camera: Camera for world-to-screen transformation
        """
        for vehicle in self.vehicles:
            vehicle.render(screen, camera)

    def get_stats(self) -> dict:
        """
        Get statistics about vehicles in the world.

        Returns:
            Dictionary with vehicle statistics
        """
        total = len(self.vehicles)
        scrap_count = sum(1 for v in self.vehicles if v.is_scrap)
        working_count = total - scrap_count
        being_deconstructed = sum(1 for v in self.vehicles if v.being_deconstructed)

        return {
            'total': total,
            'scrap': scrap_count,
            'working': working_count,
            'being_deconstructed': being_deconstructed,
        }
