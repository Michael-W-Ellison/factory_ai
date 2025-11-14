"""
CameraManager - manages security camera placement and robot detection.

Handles:
- Camera placement in city (near police stations, main roads, buildings)
- Robot detection through camera vision cones
- Suspicion increase on detection
- Camera status management (active, disabled, broken)
"""

import random
from typing import List, Optional, Tuple
from src.entities.security_camera import SecurityCamera, CameraStatus


class CameraManager:
    """
    Manages all security cameras in the city.

    Handles camera placement, robot detection, and suspicion tracking.
    """

    def __init__(self, grid, road_network=None):
        """
        Initialize camera manager.

        Args:
            grid: World grid
            road_network: RoadNetwork for road-based placement (optional)
        """
        self.grid = grid
        self.road_network = road_network

        # All cameras
        self.cameras: List[SecurityCamera] = []

        # Placement configuration
        self.target_camera_count = 25  # Target number of cameras
        self.police_station_camera_density = 5  # Cameras per police station
        self.main_road_camera_spacing = 50  # Tiles between road cameras
        self.building_camera_chance = 0.05  # 5% of buildings get cameras

        # Detection configuration
        self.suspicion_per_detection = 5  # Suspicion added per detection
        self.detection_cooldown = 5.0  # Seconds between detections of same robot by same camera

        # Detection tracking
        self.recent_detections = {}  # {(camera_id, robot_id): timestamp}

    def place_cameras(self, police_stations: Optional[List] = None):
        """
        Place security cameras throughout the city.

        Args:
            police_stations (list): List of police station positions (optional)
        """
        print("Placing security cameras...")

        # Clear existing cameras
        self.cameras.clear()

        # Place cameras near police stations (if provided)
        if police_stations:
            self._place_police_station_cameras(police_stations)

        # Place cameras along main roads
        if self.road_network:
            self._place_road_cameras()

        # Place cameras on random buildings
        self._place_building_cameras()

        print(f"Placed {len(self.cameras)} security cameras")

    def _place_police_station_cameras(self, police_stations: List):
        """
        Place multiple cameras near each police station.

        Args:
            police_stations (list): List of police station objects or positions
        """
        tile_size = self.grid.tile_size

        for station in police_stations:
            # Get police station position
            if hasattr(station, 'grid_x') and hasattr(station, 'grid_y'):
                station_x = station.grid_x * tile_size + tile_size / 2
                station_y = station.grid_y * tile_size + tile_size / 2
            elif isinstance(station, tuple):
                station_x, station_y = station
            else:
                continue

            # Place multiple cameras around police station
            for i in range(self.police_station_camera_density):
                # Random offset from station
                offset_x = random.randint(-30, 30)
                offset_y = random.randint(-30, 30)

                camera_x = station_x + offset_x
                camera_y = station_y + offset_y

                # Random facing direction
                facing_angle = random.choice([0, 90, 180, 270])

                # Create camera
                camera = SecurityCamera(camera_x, camera_y, facing_angle)
                self.cameras.append(camera)

    def _place_road_cameras(self):
        """Place cameras along main roads."""
        if not self.road_network or not self.road_network.road_tiles:
            return

        tile_size = self.grid.tile_size
        placed_count = 0

        # Get road tiles as list
        road_tiles = list(self.road_network.road_tiles)

        # Place camera every N tiles
        for i, (grid_x, grid_y) in enumerate(road_tiles):
            if i % self.main_road_camera_spacing != 0:
                continue

            # Don't place at intersections (too obvious)
            if self.road_network.is_intersection(grid_x, grid_y):
                continue

            # Calculate world position (offset to side of road)
            world_x = grid_x * tile_size + tile_size / 2
            world_y = grid_y * tile_size + tile_size / 2

            # Get road orientation
            neighbors = self.road_network._get_road_neighbors(grid_x, grid_y)

            if 'north' in neighbors or 'south' in neighbors:
                # Vertical road, offset to side
                world_x += tile_size * random.choice([-0.5, 0.5])
                # Face across road
                facing_angle = 0 if world_x > grid_x * tile_size + tile_size / 2 else 180
            else:
                # Horizontal road, offset to side
                world_y += tile_size * random.choice([-0.5, 0.5])
                # Face across road
                facing_angle = 90 if world_y > grid_y * tile_size + tile_size / 2 else 270

            # Create camera
            camera = SecurityCamera(world_x, world_y, facing_angle)
            self.cameras.append(camera)
            placed_count += 1

            # Stop if we have enough cameras
            if len(self.cameras) >= self.target_camera_count:
                break

    def _place_building_cameras(self):
        """Place cameras on random buildings."""
        from src.world.tile import TileType

        tile_size = self.grid.tile_size
        placed_count = 0

        # Scan grid for buildings
        for y in range(self.grid.height_tiles):
            for x in range(self.grid.width_tiles):
                tile = self.grid.get_tile(x, y)

                if tile and tile.tile_type == TileType.BUILDING:
                    # Random chance to place camera
                    if random.random() < self.building_camera_chance:
                        # Place on building corner
                        world_x = x * tile_size + tile_size / 2 + random.randint(-10, 10)
                        world_y = y * tile_size + tile_size / 2 + random.randint(-10, 10)

                        # Random facing direction
                        facing_angle = random.choice([0, 90, 180, 270])

                        # Create camera
                        camera = SecurityCamera(world_x, world_y, facing_angle)
                        self.cameras.append(camera)
                        placed_count += 1

                        # Stop if we have enough cameras
                        if len(self.cameras) >= self.target_camera_count:
                            return

    def update(self, dt: float):
        """
        Update all cameras.

        Args:
            dt (float): Delta time in seconds
        """
        # Update each camera
        for camera in self.cameras:
            camera.update(dt)

    def detect_robots(self, robots: List, game_time: float) -> List[Tuple[SecurityCamera, any]]:
        """
        Check for robot detections by cameras.

        Args:
            robots (list): List of robot entities
            game_time (float): Current game time (for cooldown tracking)

        Returns:
            list: List of (camera, robot) tuples for detections
        """
        detections = []

        for camera in self.cameras:
            if not camera.is_active():
                continue

            for robot in robots:
                # Check if robot is in vision cone
                if camera.detect_robot(robot):
                    # Check detection cooldown
                    detection_key = (camera.id, robot.id)
                    last_detection = self.recent_detections.get(detection_key, -999)

                    if game_time - last_detection >= self.detection_cooldown:
                        # New detection!
                        detections.append((camera, robot))
                        self.recent_detections[detection_key] = game_time

        return detections

    def get_camera_count(self) -> int:
        """Get total number of cameras."""
        return len(self.cameras)

    def get_active_camera_count(self) -> int:
        """Get number of active cameras."""
        return sum(1 for cam in self.cameras if cam.is_active())

    def get_disabled_camera_count(self) -> int:
        """Get number of disabled cameras."""
        return sum(1 for cam in self.cameras if cam.is_disabled())

    def get_broken_camera_count(self) -> int:
        """Get number of broken cameras."""
        return sum(1 for cam in self.cameras if cam.is_broken())

    def get_nearest_camera(self, world_x: float, world_y: float) -> Optional[SecurityCamera]:
        """
        Find the nearest camera to a position.

        Args:
            world_x (float): World X position
            world_y (float): World Y position

        Returns:
            SecurityCamera: Nearest camera, or None
        """
        if not self.cameras:
            return None

        nearest_camera = None
        nearest_distance = float('inf')

        for camera in self.cameras:
            dx = camera.world_x - world_x
            dy = camera.world_y - world_y
            distance = (dx * dx + dy * dy) ** 0.5

            if distance < nearest_distance:
                nearest_distance = distance
                nearest_camera = camera

        return nearest_camera

    def disable_camera(self, camera: SecurityCamera, duration: float = 300.0):
        """
        Disable a specific camera.

        Args:
            camera (SecurityCamera): Camera to disable
            duration (float): Disable duration in seconds
        """
        camera.disable(duration)

    def render(self, screen, camera):
        """
        Render all cameras and their vision cones.

        Args:
            screen: Pygame surface
            camera: Camera for rendering
        """
        for cam in self.cameras:
            cam.render(screen, camera)

    def clear_all_cameras(self):
        """Remove all cameras."""
        self.cameras.clear()
        self.recent_detections.clear()

    def __repr__(self):
        """String representation for debugging."""
        return (f"CameraManager(total={self.get_camera_count()}, "
                f"active={self.get_active_camera_count()}, "
                f"disabled={self.get_disabled_camera_count()})")
