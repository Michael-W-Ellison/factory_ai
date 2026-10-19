"""
Map Manager - Handles custom map creation, validation, saving, and loading.

Allows players to:
- Create custom maps with configurable features
- Validate maps meet minimum playability requirements
- Save maps to disk for later use
- Load and select saved maps during game creation
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Set, Any
from pathlib import Path

from src.core.logger import get_logger
from src.core.game_config import (
    MapSize, CitySize, GeographicFeature, WorldConfig,
    DifficultyLevel
)

logger = get_logger(__name__)


class MapValidationError(Exception):
    """Raised when a map fails validation."""
    pass


class MapFeature(Enum):
    """Features that can be placed on a custom map."""
    FACTORY_SPAWN = "factory_spawn"  # Required: player's factory location
    LANDFILL = "landfill"  # Required: at least one landfill
    CITY_AREA = "city_area"  # Required: city for NPCs and buildings
    ROAD_NETWORK = "road_network"  # Required: roads for traffic
    RIVER = "river"
    OCEAN = "ocean"
    DOCK = "dock"
    BRIDGE = "bridge"
    POLICE_STATION = "police_station"
    PARK = "park"


@dataclass
class MapValidationResult:
    """Result of map validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    feature_count: Dict[str, int] = field(default_factory=dict)

    def add_error(self, error: str):
        """Add a validation error."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        """Add a validation warning (doesn't fail validation)."""
        self.warnings.append(warning)


@dataclass
class CustomMap:
    """
    Represents a custom map configuration.

    Contains all settings needed to generate a playable map.
    """
    # Metadata
    name: str
    description: str = ""
    author: str = "Unknown"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"

    # Map dimensions
    width: int = 100  # Width in tiles
    height: int = 75  # Height in tiles
    tile_size: int = 32

    # Geographic features
    has_ocean: bool = False
    ocean_edges: List[str] = field(default_factory=list)  # 'north', 'south', 'east', 'west'
    ocean_depth: int = 8

    has_rivers: bool = False
    num_rivers: int = 0
    river_width_range: Tuple[int, int] = (3, 5)

    create_bridges: bool = True
    create_docks: bool = True

    # City configuration
    city_enabled: bool = True
    city_coverage: float = 0.5  # 0.0-1.0
    residential_ratio: float = 0.4
    commercial_ratio: float = 0.3
    industrial_ratio: float = 0.2
    park_ratio: float = 0.1

    # Spawn points (grid coordinates)
    factory_spawn: Optional[Tuple[int, int]] = None  # Player factory location
    landfill_areas: List[Tuple[int, int, int, int]] = field(default_factory=list)  # (x, y, width, height)

    # Special features
    police_station_count: int = 1
    camera_density: float = 0.5  # 0.0-1.0

    # Generation settings
    seed: Optional[int] = None

    # Difficulty constraints
    min_difficulty: Optional[str] = None  # Map may have minimum difficulty
    max_difficulty: Optional[str] = None  # Map may have maximum difficulty

    # Thumbnail (base64 encoded, generated after creation)
    thumbnail: Optional[str] = None

    def to_world_config(self) -> WorldConfig:
        """Convert to WorldConfig for game initialization."""
        features = []

        if self.has_ocean:
            for edge in self.ocean_edges:
                feature_map = {
                    'south': GeographicFeature.OCEAN_SOUTH,
                    'north': GeographicFeature.OCEAN_NORTH,
                    'east': GeographicFeature.OCEAN_EAST,
                    'west': GeographicFeature.OCEAN_WEST,
                }
                if edge in feature_map:
                    features.append(feature_map[edge])

        if self.has_rivers:
            features.append(GeographicFeature.RIVER)

        if not features:
            features.append(GeographicFeature.NONE)

        return WorldConfig(
            custom_width=self.width,
            custom_height=self.height,
            city_density=self.city_coverage,
            residential_ratio=self.residential_ratio,
            commercial_ratio=self.commercial_ratio,
            industrial_ratio=self.industrial_ratio,
            park_ratio=self.park_ratio,
            geographic_features=features,
            num_rivers=self.num_rivers,
            ocean_depth=self.ocean_depth,
            create_docks=self.create_docks,
            create_bridges=self.create_bridges,
            seed=self.seed,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert tuples to lists for JSON
        if self.factory_spawn:
            data['factory_spawn'] = list(self.factory_spawn)
        data['river_width_range'] = list(self.river_width_range)
        data['landfill_areas'] = [list(area) for area in self.landfill_areas]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomMap':
        """Create from dictionary."""
        # Convert lists back to tuples
        if data.get('factory_spawn'):
            data['factory_spawn'] = tuple(data['factory_spawn'])
        if data.get('river_width_range'):
            data['river_width_range'] = tuple(data['river_width_range'])
        if data.get('landfill_areas'):
            data['landfill_areas'] = [tuple(area) for area in data['landfill_areas']]
        return cls(**data)


class MapValidator:
    """
    Validates custom maps for playability.

    Checks that maps meet minimum requirements for a playable game.
    """

    # Minimum requirements
    MIN_WIDTH = 30
    MIN_HEIGHT = 25
    MAX_WIDTH = 300
    MAX_HEIGHT = 250
    MIN_LANDFILL_AREA = 100  # Minimum total landfill tiles
    MIN_CITY_COVERAGE = 0.1  # At least 10% city coverage
    MIN_BUILDABLE_AREA = 0.2  # At least 20% must be buildable land

    @classmethod
    def validate(cls, custom_map: CustomMap) -> MapValidationResult:
        """
        Validate a custom map.

        Args:
            custom_map: The map to validate

        Returns:
            MapValidationResult with validation status and any errors/warnings
        """
        result = MapValidationResult(is_valid=True)

        # Check dimensions
        cls._validate_dimensions(custom_map, result)

        # Check required features
        cls._validate_required_features(custom_map, result)

        # Check feature ratios
        cls._validate_ratios(custom_map, result)

        # Check geographic consistency
        cls._validate_geography(custom_map, result)

        # Count features
        cls._count_features(custom_map, result)

        return result

    @classmethod
    def _validate_dimensions(cls, custom_map: CustomMap, result: MapValidationResult):
        """Validate map dimensions."""
        if custom_map.width < cls.MIN_WIDTH:
            result.add_error(f"Map width ({custom_map.width}) is below minimum ({cls.MIN_WIDTH})")
        elif custom_map.width > cls.MAX_WIDTH:
            result.add_error(f"Map width ({custom_map.width}) exceeds maximum ({cls.MAX_WIDTH})")

        if custom_map.height < cls.MIN_HEIGHT:
            result.add_error(f"Map height ({custom_map.height}) is below minimum ({cls.MIN_HEIGHT})")
        elif custom_map.height > cls.MAX_HEIGHT:
            result.add_error(f"Map height ({custom_map.height}) exceeds maximum ({cls.MAX_HEIGHT})")

    @classmethod
    def _validate_required_features(cls, custom_map: CustomMap, result: MapValidationResult):
        """Validate required features exist."""
        # Factory spawn point
        if not custom_map.factory_spawn:
            result.add_error("No factory spawn point defined")
        else:
            x, y = custom_map.factory_spawn
            if x < 0 or x >= custom_map.width or y < 0 or y >= custom_map.height:
                result.add_error(f"Factory spawn ({x}, {y}) is outside map bounds")

        # Landfill areas
        total_landfill = 0
        for area in custom_map.landfill_areas:
            if len(area) != 4:
                result.add_error(f"Invalid landfill area format: {area}")
                continue
            x, y, w, h = area
            if x < 0 or y < 0 or x + w > custom_map.width or y + h > custom_map.height:
                result.add_error(f"Landfill area ({x}, {y}, {w}x{h}) extends outside map bounds")
            total_landfill += w * h

        if total_landfill < cls.MIN_LANDFILL_AREA:
            result.add_error(
                f"Total landfill area ({total_landfill} tiles) is below minimum ({cls.MIN_LANDFILL_AREA})"
            )

        # City requirement
        if not custom_map.city_enabled:
            result.add_error("City must be enabled for a playable map")
        elif custom_map.city_coverage < cls.MIN_CITY_COVERAGE:
            result.add_error(
                f"City coverage ({custom_map.city_coverage:.0%}) is below minimum ({cls.MIN_CITY_COVERAGE:.0%})"
            )

    @classmethod
    def _validate_ratios(cls, custom_map: CustomMap, result: MapValidationResult):
        """Validate zone ratios."""
        total_ratio = (
            custom_map.residential_ratio +
            custom_map.commercial_ratio +
            custom_map.industrial_ratio +
            custom_map.park_ratio
        )

        if abs(total_ratio - 1.0) > 0.01:
            result.add_warning(
                f"Zone ratios sum to {total_ratio:.2f}, should be 1.0. "
                "Ratios will be normalized during generation."
            )

        if custom_map.residential_ratio < 0.1:
            result.add_warning("Very low residential ratio may result in few NPCs")

        if custom_map.commercial_ratio < 0.05:
            result.add_warning("Very low commercial ratio may limit store availability")

    @classmethod
    def _validate_geography(cls, custom_map: CustomMap, result: MapValidationResult):
        """Validate geographic feature consistency."""
        # Calculate water coverage
        water_tiles = 0
        total_tiles = custom_map.width * custom_map.height

        if custom_map.has_ocean:
            for edge in custom_map.ocean_edges:
                if edge in ['north', 'south']:
                    water_tiles += custom_map.width * custom_map.ocean_depth
                elif edge in ['east', 'west']:
                    water_tiles += custom_map.height * custom_map.ocean_depth

        # Rough estimate for rivers
        if custom_map.has_rivers:
            avg_river_length = max(custom_map.width, custom_map.height) * 0.7
            avg_river_width = sum(custom_map.river_width_range) / 2
            water_tiles += custom_map.num_rivers * avg_river_length * avg_river_width

        # Check buildable area
        buildable_ratio = 1.0 - (water_tiles / total_tiles)
        if buildable_ratio < cls.MIN_BUILDABLE_AREA:
            result.add_error(
                f"Estimated buildable area ({buildable_ratio:.0%}) is below minimum ({cls.MIN_BUILDABLE_AREA:.0%}). "
                "Reduce ocean depth or number of rivers."
            )

        # Check for island (all edges ocean)
        if custom_map.has_ocean and len(custom_map.ocean_edges) == 4:
            if custom_map.ocean_depth > min(custom_map.width, custom_map.height) // 4:
                result.add_error(
                    "Island configuration with deep ocean leaves insufficient land area"
                )

        # Bridge warnings
        if custom_map.has_rivers and not custom_map.create_bridges:
            result.add_warning(
                "Rivers without bridges may create inaccessible areas"
            )

    @classmethod
    def _count_features(cls, custom_map: CustomMap, result: MapValidationResult):
        """Count map features for display."""
        result.feature_count = {
            'width': custom_map.width,
            'height': custom_map.height,
            'total_tiles': custom_map.width * custom_map.height,
            'ocean_edges': len(custom_map.ocean_edges) if custom_map.has_ocean else 0,
            'rivers': custom_map.num_rivers if custom_map.has_rivers else 0,
            'landfill_areas': len(custom_map.landfill_areas),
            'police_stations': custom_map.police_station_count,
        }


class MapManager:
    """
    Manages saving, loading, and listing custom maps.
    """

    DEFAULT_MAPS_DIR = "data/maps"
    MAP_FILE_EXTENSION = ".json"

    def __init__(self, maps_dir: Optional[str] = None):
        """
        Initialize map manager.

        Args:
            maps_dir: Directory to store map files
        """
        self.maps_dir = Path(maps_dir or self.DEFAULT_MAPS_DIR)
        self._ensure_maps_dir()

        # Cache of loaded maps
        self._map_cache: Dict[str, CustomMap] = {}

    def _ensure_maps_dir(self):
        """Create maps directory if it doesn't exist."""
        self.maps_dir.mkdir(parents=True, exist_ok=True)

    def _get_map_path(self, map_name: str) -> Path:
        """Get file path for a map."""
        safe_name = "".join(c for c in map_name if c.isalnum() or c in "._- ")
        safe_name = safe_name.strip().replace(" ", "_")
        return self.maps_dir / f"{safe_name}{self.MAP_FILE_EXTENSION}"

    def save_map(self, custom_map: CustomMap, overwrite: bool = False) -> bool:
        """
        Save a custom map to disk.

        Args:
            custom_map: The map to save
            overwrite: Whether to overwrite existing map

        Returns:
            True if saved successfully
        """
        # Validate before saving
        validation = MapValidator.validate(custom_map)
        if not validation.is_valid:
            logger.error(f"Cannot save invalid map: {validation.errors}")
            return False

        map_path = self._get_map_path(custom_map.name)

        if map_path.exists() and not overwrite:
            logger.warning(f"Map '{custom_map.name}' already exists. Use overwrite=True to replace.")
            return False

        try:
            with open(map_path, 'w') as f:
                json.dump(custom_map.to_dict(), f, indent=2)

            # Update cache
            self._map_cache[custom_map.name] = custom_map

            logger.info(f"Saved map '{custom_map.name}' to {map_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save map: {e}")
            return False

    def load_map(self, map_name: str) -> Optional[CustomMap]:
        """
        Load a custom map from disk.

        Args:
            map_name: Name of the map to load

        Returns:
            CustomMap if found and valid, None otherwise
        """
        # Check cache first
        if map_name in self._map_cache:
            return self._map_cache[map_name]

        map_path = self._get_map_path(map_name)

        if not map_path.exists():
            logger.warning(f"Map '{map_name}' not found at {map_path}")
            return None

        try:
            with open(map_path, 'r') as f:
                data = json.load(f)

            custom_map = CustomMap.from_dict(data)

            # Validate loaded map
            validation = MapValidator.validate(custom_map)
            if not validation.is_valid:
                logger.warning(f"Loaded map '{map_name}' failed validation: {validation.errors}")

            # Cache it
            self._map_cache[map_name] = custom_map

            return custom_map

        except Exception as e:
            logger.error(f"Failed to load map '{map_name}': {e}")
            return None

    def delete_map(self, map_name: str) -> bool:
        """
        Delete a custom map.

        Args:
            map_name: Name of the map to delete

        Returns:
            True if deleted successfully
        """
        map_path = self._get_map_path(map_name)

        if not map_path.exists():
            logger.warning(f"Map '{map_name}' not found")
            return False

        try:
            map_path.unlink()

            # Remove from cache
            if map_name in self._map_cache:
                del self._map_cache[map_name]

            logger.info(f"Deleted map '{map_name}'")
            return True

        except Exception as e:
            logger.error(f"Failed to delete map '{map_name}': {e}")
            return False

    def list_maps(self, include_invalid: bool = False) -> List[Dict[str, Any]]:
        """
        List all available custom maps.

        Args:
            include_invalid: Include maps that fail validation

        Returns:
            List of map info dictionaries
        """
        maps = []

        for map_file in self.maps_dir.glob(f"*{self.MAP_FILE_EXTENSION}"):
            try:
                with open(map_file, 'r') as f:
                    data = json.load(f)

                custom_map = CustomMap.from_dict(data)
                validation = MapValidator.validate(custom_map)

                if validation.is_valid or include_invalid:
                    maps.append({
                        'name': custom_map.name,
                        'description': custom_map.description,
                        'author': custom_map.author,
                        'created_at': custom_map.created_at,
                        'width': custom_map.width,
                        'height': custom_map.height,
                        'is_valid': validation.is_valid,
                        'errors': validation.errors if not validation.is_valid else [],
                        'has_ocean': custom_map.has_ocean,
                        'has_rivers': custom_map.has_rivers,
                        'thumbnail': custom_map.thumbnail,
                    })

            except Exception as e:
                logger.warning(f"Failed to read map file {map_file}: {e}")

        # Sort by creation date, newest first
        maps.sort(key=lambda m: m.get('created_at', ''), reverse=True)

        return maps

    def get_builtin_maps(self) -> List[CustomMap]:
        """
        Get list of built-in map presets.

        Returns:
            List of preset CustomMap objects
        """
        return [
            CustomMap(
                name="Classic",
                description="Standard map with ocean to the south and one river",
                author="System",
                width=100,
                height=75,
                has_ocean=True,
                ocean_edges=['south'],
                ocean_depth=4,
                has_rivers=True,
                num_rivers=1,
                city_coverage=0.5,
                factory_spawn=(50, 37),
                landfill_areas=[(5, 10, 20, 20)],
            ),
            CustomMap(
                name="Island Challenge",
                description="Small island surrounded by ocean - limited space!",
                author="System",
                width=80,
                height=60,
                has_ocean=True,
                ocean_edges=['north', 'south', 'east', 'west'],
                ocean_depth=6,
                has_rivers=False,
                num_rivers=0,
                city_coverage=0.6,
                factory_spawn=(40, 30),
                landfill_areas=[(15, 15, 15, 15)],
            ),
            CustomMap(
                name="River Valley",
                description="Multiple rivers crossing the map with bridges",
                author="System",
                width=120,
                height=80,
                has_ocean=False,
                has_rivers=True,
                num_rivers=3,
                create_bridges=True,
                city_coverage=0.45,
                factory_spawn=(60, 40),
                landfill_areas=[(10, 10, 25, 20), (85, 50, 20, 15)],
            ),
            CustomMap(
                name="Metropolis",
                description="Large urban sprawl with minimal nature",
                author="System",
                width=150,
                height=100,
                has_ocean=False,
                has_rivers=False,
                city_coverage=0.8,
                residential_ratio=0.35,
                commercial_ratio=0.35,
                industrial_ratio=0.25,
                park_ratio=0.05,
                police_station_count=3,
                camera_density=0.8,
                factory_spawn=(75, 50),
                landfill_areas=[(5, 5, 30, 25), (115, 70, 25, 20)],
            ),
            CustomMap(
                name="Coastal Town",
                description="Beachside town with docks and light industry",
                author="System",
                width=100,
                height=75,
                has_ocean=True,
                ocean_edges=['south', 'west'],
                ocean_depth=5,
                create_docks=True,
                has_rivers=True,
                num_rivers=1,
                city_coverage=0.4,
                factory_spawn=(60, 35),
                landfill_areas=[(70, 10, 20, 20)],
            ),
        ]

    def create_map_from_preset(self, preset_name: str) -> Optional[CustomMap]:
        """
        Create a new map based on a preset.

        Args:
            preset_name: Name of the preset to use

        Returns:
            New CustomMap based on the preset
        """
        for preset in self.get_builtin_maps():
            if preset.name.lower() == preset_name.lower():
                # Create a copy with new metadata
                new_map = CustomMap.from_dict(preset.to_dict())
                new_map.name = f"Custom {preset.name}"
                new_map.author = "Player"
                new_map.created_at = datetime.now().isoformat()
                return new_map

        return None


# Singleton instance
_map_manager: Optional[MapManager] = None


def get_map_manager() -> MapManager:
    """Get the global MapManager instance."""
    global _map_manager
    if _map_manager is None:
        _map_manager = MapManager()
    return _map_manager
