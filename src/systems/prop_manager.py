"""
PropManager - manages placement and rendering of city props.

Handles:
- Prop placement near buildings, parks, and roads
- Prop lifecycle and management
- Prop rendering
"""

import random
from typing import List, Optional
from src.entities.prop import Prop, Bench, LightPole, TrashCan, Bicycle, PropType
from src.world.tile import TileType


class PropManager:
    """
    Manages all city props (benches, light poles, trash cans, bicycles).

    Handles automatic placement based on city layout.
    """

    def __init__(self, grid, road_network=None):
        """
        Initialize prop manager.

        Args:
            grid: World grid
            road_network: RoadNetwork for road-based placement (optional)
        """
        self.grid = grid
        self.road_network = road_network

        # All props
        self.props: List[Prop] = []

        # Placement configuration
        self.target_prop_count = 80  # Target number of props
        self.light_pole_spacing = 8  # Tiles between light poles
        self.bench_density = 0.3  # Chance of bench near grass
        self.trash_can_density = 0.2  # Chance of trash can near building
        self.bicycle_density = 0.15  # Chance of bicycle near building

    def generate_props(self):
        """Generate props throughout the city."""
        print("Generating city props...")

        # Clear existing props
        self.props.clear()

        # Place different types of props
        self._place_light_poles()
        self._place_benches()
        self._place_trash_cans()
        self._place_bicycles()

        print(f"Generated {len(self.props)} props total:")
        print(f"  {self._count_props(PropType.LIGHT_POLE)} light poles")
        print(f"  {self._count_props(PropType.BENCH)} benches")
        print(f"  {self._count_props(PropType.TRASH_CAN)} trash cans")
        print(f"  {self._count_props(PropType.BICYCLE)} bicycles")

    def _place_light_poles(self):
        """Place light poles along roads."""
        if self.road_network is None:
            return

        placed_count = 0
        tile_size = self.grid.tile_size

        # Get all road tiles
        road_tiles = list(self.road_network.road_tiles)

        # Place light poles at regular intervals
        for i, (grid_x, grid_y) in enumerate(road_tiles):
            # Skip most tiles (only place every Nth tile)
            if i % self.light_pole_spacing != 0:
                continue

            # Don't place at intersections
            if self.road_network.is_intersection(grid_x, grid_y):
                continue

            # Calculate world position (offset to side of road)
            world_x = grid_x * tile_size + tile_size / 2
            world_y = grid_y * tile_size + tile_size / 2

            # Offset to side of road
            neighbors = self.road_network._get_road_neighbors(grid_x, grid_y)

            if 'north' in neighbors or 'south' in neighbors:
                # Vertical road, offset to east side
                world_x += tile_size * 0.4
            else:
                # Horizontal road, offset to south side
                world_y += tile_size * 0.4

            # Create light pole
            light_pole = LightPole(world_x, world_y)
            self.props.append(light_pole)
            placed_count += 1

    def _place_benches(self):
        """Place benches near grass tiles (parks)."""
        tile_size = self.grid.tile_size
        placed_count = 0

        # Scan grid for grass tiles
        for y in range(self.grid.height_tiles):
            for x in range(self.grid.width_tiles):
                tile = self.grid.get_tile(x, y)

                if tile and tile.tile_type == TileType.GRASS:
                    # Random chance to place bench
                    if random.random() < self.bench_density:
                        # Check if there's already a prop nearby
                        world_x = x * tile_size + tile_size / 2
                        world_y = y * tile_size + tile_size / 2

                        if self._is_position_clear(world_x, world_y, min_distance=20):
                            # Random rotation
                            rotation = random.choice([0, 90, 180, 270])

                            # Create bench
                            bench = Bench(world_x, world_y, rotation)
                            self.props.append(bench)
                            placed_count += 1

    def _place_trash_cans(self):
        """Place trash cans near buildings."""
        tile_size = self.grid.tile_size
        placed_count = 0

        # Scan grid for building tiles
        for y in range(self.grid.height_tiles):
            for x in range(self.grid.width_tiles):
                tile = self.grid.get_tile(x, y)

                if tile and tile.tile_type == TileType.BUILDING:
                    # Random chance to place trash can
                    if random.random() < self.trash_can_density:
                        # Place near building entrance (offset)
                        world_x = x * tile_size + tile_size / 2 + random.randint(-10, 10)
                        world_y = y * tile_size + tile_size / 2 + random.randint(-10, 10)

                        if self._is_position_clear(world_x, world_y, min_distance=15):
                            # Create trash can
                            trash_can = TrashCan(world_x, world_y)
                            self.props.append(trash_can)
                            placed_count += 1

    def _place_bicycles(self):
        """Place bicycles near houses and commercial buildings."""
        tile_size = self.grid.tile_size
        placed_count = 0

        # Scan grid for building and grass tiles (near buildings)
        for y in range(self.grid.height_tiles):
            for x in range(self.grid.width_tiles):
                tile = self.grid.get_tile(x, y)

                if tile and tile.tile_type in [TileType.BUILDING, TileType.GRASS]:
                    # Random chance to place bicycle
                    if random.random() < self.bicycle_density:
                        # Place with slight offset
                        world_x = x * tile_size + tile_size / 2 + random.randint(-8, 8)
                        world_y = y * tile_size + tile_size / 2 + random.randint(-8, 8)

                        if self._is_position_clear(world_x, world_y, min_distance=12):
                            # Random rotation (leaning angle)
                            rotation = random.choice([0, 90, 180, 270])

                            # Create bicycle
                            bicycle = Bicycle(world_x, world_y, rotation)
                            self.props.append(bicycle)
                            placed_count += 1

    def _is_position_clear(self, world_x: float, world_y: float, min_distance: float = 10.0) -> bool:
        """
        Check if a position is clear of other props.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
            min_distance (float): Minimum distance from other props

        Returns:
            bool: True if position is clear
        """
        for prop in self.props:
            distance = ((prop.world_x - world_x) ** 2 + (prop.world_y - world_y) ** 2) ** 0.5
            if distance < min_distance:
                return False
        return True

    def _count_props(self, prop_type: int) -> int:
        """Count props of a specific type."""
        return sum(1 for prop in self.props if prop.prop_type == prop_type)

    def update(self, dt: float, is_night: bool = False):
        """
        Update props (e.g., turn lights on/off at night).

        Args:
            dt (float): Delta time in seconds
            is_night (bool): Whether it's currently night time
        """
        # Update light poles (turn on at night)
        for prop in self.props:
            if prop.prop_type == PropType.LIGHT_POLE:
                prop.is_on = is_night

    def render(self, screen, camera):
        """
        Render all props.

        Args:
            screen: Pygame surface
            camera: Camera for rendering
        """
        for prop in self.props:
            prop.render(screen, camera)

    def get_prop_count(self) -> int:
        """Get total number of props."""
        return len(self.props)

    def clear_all_props(self):
        """Remove all props."""
        self.props.clear()

    def add_prop(self, prop: Prop):
        """
        Add a prop manually.

        Args:
            prop (Prop): Prop to add
        """
        self.props.append(prop)

    def remove_prop(self, prop: Prop):
        """
        Remove a prop.

        Args:
            prop (Prop): Prop to remove
        """
        if prop in self.props:
            self.props.remove(prop)

    def __repr__(self):
        """String representation for debugging."""
        return f"PropManager(props={len(self.props)})"
