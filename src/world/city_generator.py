"""
CityGenerator - Procedurally generates city layouts with buildings, roads, and zones.

Handles:
- Grid-based city layout (10x10 blocks)
- Road placement
- Zone generation (residential, commercial, industrial, police)
- Building placement with varying density
- Parks and public areas
"""

import random
from enum import Enum
from typing import List, Tuple, Dict, Optional


class ZoneType(Enum):
    """Types of zones in the city."""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    POLICE = "police"
    PARK = "park"
    ROAD = "road"
    EMPTY = "empty"


class CityBlock:
    """Represents a 10x10 city block."""

    def __init__(self, x: int, y: int, zone_type: ZoneType):
        """
        Initialize a city block.

        Args:
            x (int): Block X position (in blocks, not tiles)
            y (int): Block Y position (in blocks, not tiles)
            zone_type (ZoneType): Type of zone for this block
        """
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.buildings = []  # List of buildings in this block
        self.density = 0.0  # 0.0-1.0, how full the block is


class CityGenerator:
    """
    Generates procedural city layouts.

    Creates a grid-based city with roads, zones, and buildings.
    """

    def __init__(self, world_width: int, world_height: int, tile_size: int):
        """
        Initialize the city generator.

        Args:
            world_width (int): World width in pixels
            world_height (int): World height in pixels
            tile_size (int): Size of each tile in pixels
        """
        self.world_width = world_width
        self.world_height = world_height
        self.tile_size = tile_size

        # Calculate grid dimensions in tiles
        self.grid_width = world_width // tile_size
        self.grid_height = world_height // tile_size

        # Block size (10x10 tiles per block)
        self.block_size = 10

        # Calculate city dimensions in blocks
        self.blocks_wide = self.grid_width // self.block_size
        self.blocks_high = self.grid_height // self.block_size

        # City blocks grid
        self.blocks: List[List[Optional[CityBlock]]] = []

        # Placed buildings
        self.buildings = []

        # Road tiles (grid coordinates)
        self.road_tiles = set()

        # City center (for police station placement)
        self.center_x = self.blocks_wide // 2
        self.center_y = self.blocks_high // 2

        print(f"CityGenerator initialized: {self.blocks_wide}x{self.blocks_high} blocks "
              f"({self.grid_width}x{self.grid_height} tiles)")

    def generate(self, seed: Optional[int] = None) -> Dict:
        """
        Generate a complete city layout.

        Args:
            seed (int, optional): Random seed for reproducible generation

        Returns:
            dict: City data with blocks, buildings, and roads
        """
        if seed is not None:
            random.seed(seed)

        print("Generating city layout...")

        # Initialize blocks grid
        self._initialize_blocks()

        # Place roads (grid pattern)
        self._place_roads()

        # Assign zones to blocks
        self._assign_zones()

        # Place buildings in zones
        self._place_buildings()

        # Generate statistics
        stats = self._get_statistics()

        print(f"City generation complete!")
        print(f"  Blocks: {stats['total_blocks']}")
        print(f"  Roads: {stats['road_tiles']} tiles")
        print(f"  Residential: {stats['residential_blocks']} blocks")
        print(f"  Commercial: {stats['commercial_blocks']} blocks")
        print(f"  Industrial: {stats['industrial_blocks']} blocks")
        print(f"  Parks: {stats['park_blocks']} blocks")
        print(f"  Buildings: {stats['total_buildings']}")

        return {
            'blocks': self.blocks,
            'buildings': self.buildings,
            'road_tiles': self.road_tiles,
            'stats': stats
        }

    def _initialize_blocks(self):
        """Initialize the city blocks grid."""
        self.blocks = []
        for by in range(self.blocks_high):
            row = []
            for bx in range(self.blocks_wide):
                # Default to empty
                block = CityBlock(bx, by, ZoneType.EMPTY)
                row.append(block)
            self.blocks.append(row)

    def _place_roads(self):
        """Place roads in a grid pattern (every 10 tiles)."""
        # Horizontal roads (every block_size tiles)
        for by in range(self.blocks_high + 1):
            road_y = by * self.block_size
            if road_y < self.grid_height:
                for x in range(self.grid_width):
                    self.road_tiles.add((x, road_y))

        # Vertical roads (every block_size tiles)
        for bx in range(self.blocks_wide + 1):
            road_x = bx * self.block_size
            if road_x < self.grid_width:
                for y in range(self.grid_height):
                    self.road_tiles.add((road_x, y))

    def _assign_zones(self):
        """Assign zone types to blocks."""
        # Center area: police station
        police_x = self.center_x
        police_y = self.center_y
        if 0 <= police_x < self.blocks_wide and 0 <= police_y < self.blocks_high:
            self.blocks[police_y][police_x].zone_type = ZoneType.POLICE

        # Assign zones to non-road blocks
        for by in range(self.blocks_high):
            for bx in range(self.blocks_wide):
                block = self.blocks[by][bx]

                # Skip roads and police
                if block.zone_type in [ZoneType.ROAD, ZoneType.POLICE]:
                    continue

                # Calculate distance from center
                dist_x = abs(bx - self.center_x)
                dist_y = abs(by - self.center_y)
                dist = dist_x + dist_y  # Manhattan distance

                # Zone assignment based on distance from center
                rand = random.random()

                if dist < 3:
                    # Near center: commercial
                    if rand < 0.7:
                        block.zone_type = ZoneType.COMMERCIAL
                    elif rand < 0.9:
                        block.zone_type = ZoneType.PARK
                    else:
                        block.zone_type = ZoneType.RESIDENTIAL

                elif dist < 8:
                    # Mid distance: mixed residential/commercial
                    if rand < 0.5:
                        block.zone_type = ZoneType.RESIDENTIAL
                    elif rand < 0.75:
                        block.zone_type = ZoneType.COMMERCIAL
                    elif rand < 0.85:
                        block.zone_type = ZoneType.PARK
                    else:
                        block.zone_type = ZoneType.INDUSTRIAL

                else:
                    # Far from center: mostly residential, some industrial
                    if rand < 0.6:
                        block.zone_type = ZoneType.RESIDENTIAL
                    elif rand < 0.75:
                        block.zone_type = ZoneType.INDUSTRIAL
                    elif rand < 0.85:
                        block.zone_type = ZoneType.PARK
                    else:
                        block.zone_type = ZoneType.EMPTY

    def _place_buildings(self):
        """Place buildings in zones based on zone type."""
        for by in range(self.blocks_high):
            for bx in range(self.blocks_wide):
                block = self.blocks[by][bx]

                # Get density for this zone type
                density = self._get_zone_density(block.zone_type)
                block.density = density

                # Place buildings based on density
                if block.zone_type == ZoneType.RESIDENTIAL:
                    self._place_residential_buildings(block, density)
                elif block.zone_type == ZoneType.COMMERCIAL:
                    self._place_commercial_buildings(block, density)
                elif block.zone_type == ZoneType.INDUSTRIAL:
                    self._place_industrial_buildings(block, density)
                elif block.zone_type == ZoneType.POLICE:
                    self._place_police_station(block)
                elif block.zone_type == ZoneType.PARK:
                    self._place_park_features(block)

    def _get_zone_density(self, zone_type: ZoneType) -> float:
        """
        Get building density for zone type.

        Args:
            zone_type (ZoneType): Type of zone

        Returns:
            float: Density from 0.0 to 1.0
        """
        base_densities = {
            ZoneType.RESIDENTIAL: 0.6,
            ZoneType.COMMERCIAL: 0.7,
            ZoneType.INDUSTRIAL: 0.5,
            ZoneType.POLICE: 1.0,
            ZoneType.PARK: 0.2,
            ZoneType.ROAD: 0.0,
            ZoneType.EMPTY: 0.0
        }

        base = base_densities.get(zone_type, 0.0)
        # Add random variation (-20% to +20%)
        variation = random.uniform(-0.2, 0.2)
        return max(0.0, min(1.0, base + variation))

    def _place_residential_buildings(self, block: CityBlock, density: float):
        """Place houses in residential block."""
        # Number of houses based on density (0-4 houses per block)
        num_houses = int(density * 4)

        for _ in range(num_houses):
            # Random position within block (avoid roads)
            x = block.x * self.block_size + random.randint(1, self.block_size - 4)
            y = block.y * self.block_size + random.randint(1, self.block_size - 5)

            # 70% livable, 30% decrepit
            is_livable = random.random() < 0.7

            building = {
                'type': 'house',
                'subtype': 'livable' if is_livable else 'decrepit',
                'x': x,
                'y': y,
                'width': 3,
                'height': 4,
                'legal': not is_livable,  # Decrepit houses are legal to deconstruct
                'block': (block.x, block.y)
            }

            block.buildings.append(building)
            self.buildings.append(building)

    def _place_commercial_buildings(self, block: CityBlock, density: float):
        """Place stores and offices in commercial block."""
        # Number of buildings based on density (0-3 per block)
        num_buildings = int(density * 3)

        for _ in range(num_buildings):
            # Random position within block
            x = block.x * self.block_size + random.randint(1, self.block_size - 5)
            y = block.y * self.block_size + random.randint(1, self.block_size - 5)

            # 60% stores, 40% offices
            is_store = random.random() < 0.6

            building = {
                'type': 'store' if is_store else 'office',
                'x': x,
                'y': y,
                'width': 4 if is_store else 5,
                'height': 4 if is_store else 5,
                'legal': False,  # Commercial buildings illegal to deconstruct
                'block': (block.x, block.y)
            }

            block.buildings.append(building)
            self.buildings.append(building)

    def _place_industrial_buildings(self, block: CityBlock, density: float):
        """Place factories in industrial block."""
        # Number of factories based on density (0-2 per block)
        num_factories = int(density * 2)

        for _ in range(num_factories):
            # Random position within block
            x = block.x * self.block_size + random.randint(1, self.block_size - 7)
            y = block.y * self.block_size + random.randint(1, self.block_size - 7)

            building = {
                'type': 'city_factory',
                'x': x,
                'y': y,
                'width': 6,
                'height': 6,
                'legal': False,  # Factories illegal to deconstruct
                'block': (block.x, block.y)
            }

            block.buildings.append(building)
            self.buildings.append(building)

    def _place_police_station(self, block: CityBlock):
        """Place police station in police block."""
        # Center of block
        x = block.x * self.block_size + 2
        y = block.y * self.block_size + 2

        building = {
            'type': 'police_station',
            'x': x,
            'y': y,
            'width': 5,
            'height': 5,
            'legal': False,  # Cannot deconstruct police station
            'block': (block.x, block.y)
        }

        block.buildings.append(building)
        self.buildings.append(building)

    def _place_park_features(self, block: CityBlock):
        """Place park features (trees, benches, etc.)."""
        # Parks have minimal structures
        # Could add decorative elements in the future
        pass

    def _get_statistics(self) -> Dict:
        """Get statistics about the generated city."""
        stats = {
            'total_blocks': self.blocks_wide * self.blocks_high,
            'road_tiles': len(self.road_tiles),
            'residential_blocks': 0,
            'commercial_blocks': 0,
            'industrial_blocks': 0,
            'park_blocks': 0,
            'police_blocks': 0,
            'empty_blocks': 0,
            'total_buildings': len(self.buildings),
            'houses': 0,
            'stores': 0,
            'offices': 0,
            'factories': 0,
            'police_stations': 0
        }

        # Count blocks by type
        for row in self.blocks:
            for block in row:
                if block.zone_type == ZoneType.RESIDENTIAL:
                    stats['residential_blocks'] += 1
                elif block.zone_type == ZoneType.COMMERCIAL:
                    stats['commercial_blocks'] += 1
                elif block.zone_type == ZoneType.INDUSTRIAL:
                    stats['industrial_blocks'] += 1
                elif block.zone_type == ZoneType.PARK:
                    stats['park_blocks'] += 1
                elif block.zone_type == ZoneType.POLICE:
                    stats['police_blocks'] += 1
                elif block.zone_type == ZoneType.EMPTY:
                    stats['empty_blocks'] += 1

        # Count buildings by type
        for building in self.buildings:
            if building['type'] == 'house':
                stats['houses'] += 1
            elif building['type'] == 'store':
                stats['stores'] += 1
            elif building['type'] == 'office':
                stats['offices'] += 1
            elif building['type'] == 'city_factory':
                stats['factories'] += 1
            elif building['type'] == 'police_station':
                stats['police_stations'] += 1

        return stats

    def get_building_at(self, grid_x: int, grid_y: int) -> Optional[Dict]:
        """
        Get building at grid position.

        Args:
            grid_x (int): Grid X coordinate
            grid_y (int): Grid Y coordinate

        Returns:
            dict: Building data or None
        """
        for building in self.buildings:
            if (building['x'] <= grid_x < building['x'] + building['width'] and
                building['y'] <= grid_y < building['y'] + building['height']):
                return building
        return None

    def is_road(self, grid_x: int, grid_y: int) -> bool:
        """
        Check if tile is a road.

        Args:
            grid_x (int): Grid X coordinate
            grid_y (int): Grid Y coordinate

        Returns:
            bool: True if tile is a road
        """
        return (grid_x, grid_y) in self.road_tiles

    def get_block(self, block_x: int, block_y: int) -> Optional[CityBlock]:
        """
        Get block at block coordinates.

        Args:
            block_x (int): Block X coordinate
            block_y (int): Block Y coordinate

        Returns:
            CityBlock: Block or None
        """
        if 0 <= block_y < len(self.blocks) and 0 <= block_x < len(self.blocks[0]):
            return self.blocks[block_y][block_x]
        return None

    def __repr__(self):
        """String representation for debugging."""
        return (f"CityGenerator({self.blocks_wide}x{self.blocks_high} blocks, "
                f"{len(self.buildings)} buildings, {len(self.road_tiles)} road tiles)")
