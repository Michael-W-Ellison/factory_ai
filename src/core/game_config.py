"""
Centralized game configuration values.

This module contains all magic numbers and configuration constants
used throughout the game, organized by category. Using these constants
instead of hardcoded values makes the game easier to tune and maintain.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class TimeConfig:
    """Time-related constants."""
    SECONDS_PER_MINUTE: int = 60
    SECONDS_PER_HOUR: int = 3600
    SECONDS_PER_DAY: int = 86400
    SECONDS_PER_WEEK: int = 604800
    GAME_MINUTES_PER_REAL_SECOND: int = 60


@dataclass(frozen=True)
class InspectionConfig:
    """Inspection system constants."""
    WARNING_TIME_MIN: float = 86400.0  # 24 hours
    WARNING_TIME_MAX: float = 172800.0  # 48 hours
    DURATION: float = 3600.0  # 1 hour
    IMMUNITY_PERIOD: float = 604800.0  # 7 days
    SUSPICION_THRESHOLD: int = 60
    FINE_MINOR: int = 5000
    FINE_MAJOR: int = 20000
    REINSPECTION_INTERVAL: float = 259200.0  # 3 days for reinspection after minor fail
    RESTRICTION_DURATION: float = 604800.0  # 7 days of restrictions after major fail
    RESTRICTION_PENALTY: float = 0.5  # 50% production penalty


@dataclass(frozen=True)
class EntityConfig:
    """Entity spawn and limit constants."""
    TARGET_CAMERA_COUNT: int = 25
    MAX_DRONES: int = 5
    BUS_MAX_CAPACITY: int = 20
    PARKED_VEHICLE_COUNT: int = 30
    TARGET_PROP_COUNT: int = 100
    MAX_ROBOTS: int = 50
    MAX_BUILDINGS: int = 200


@dataclass(frozen=True)
class SuspicionConfig:
    """Suspicion system constants."""
    TIER_NONE: int = 0
    TIER_RUMORS: int = 21
    TIER_INVESTIGATION: int = 41
    TIER_INSPECTION: int = 61
    TIER_RESTRICTED: int = 81
    MAX_SUSPICION: int = 100
    BASE_DECAY_RATE: float = 0.1
    DECAY_STOP_LEVEL: float = 60.0


@dataclass(frozen=True)
class RobotConfig:
    """Robot default values."""
    BASE_SPEED: float = 100.0
    BASE_CAPACITY: float = 100.0
    BASE_POWER_CAPACITY: float = 1000.0
    BASE_HEALTH: float = 100.0
    POWER_CONSUMPTION_RATE: float = 1.0
    COLLECTION_RADIUS: float = 50.0
    MAX_UPGRADE_LEVEL: int = 5


@dataclass(frozen=True)
class BuildingConfig:
    """Building system constants."""
    BASE_CONSTRUCTION_TIME: float = 60.0
    TIME_PER_SIZE_UNIT: float = 10.0
    WORKER_SPEED_MULTIPLIER: float = 0.5
    DEFAULT_RECOVERY_RATE: float = 0.7
    ILLEGAL_RECOVERY_RATE: float = 0.5


@dataclass(frozen=True)
class WeatherConfig:
    """Weather system constants."""
    DEFAULT_DURATION_MIN: float = 7200.0  # 2 hours
    DEFAULT_DURATION_MAX: float = 21600.0  # 6 hours
    TRANSITION_DURATION: float = 1800.0  # 30 minutes
    FORECAST_DURATION: float = 259200.0  # 3 days forecast window


@dataclass(frozen=True)
class MarketConfig:
    """Market/economy constants."""
    PRICE_FLUCTUATION_RANGE: float = 0.15  # +/- 15%
    PRICE_UPDATE_INTERVAL: float = 60.0  # Every game minute
    ORGANIC_DECAY_RATE: float = 0.001  # 0.1% per check
    DECAY_CHECK_INTERVAL: float = 300.0  # Every 5 game minutes
    TREND_CHANGE_INTERVAL: float = 172800.0  # 48 game hours
    EVENT_CHECK_INTERVAL: float = 86400.0  # 24 game hours
    EVENT_PROBABILITY: float = 0.1  # 10% chance per check
    MIN_PRICE_MULTIPLIER: float = 0.3  # Prices can't go below 30% of base
    MAX_PRICE_MULTIPLIER: float = 3.0  # Prices can't go above 300% of base
    # Event durations
    EVENT_DURATION_SHORT: float = 43200.0  # 12 hours
    EVENT_DURATION_MEDIUM: float = 86400.0  # 24 hours
    EVENT_DURATION_LONG: float = 172800.0  # 48 hours


@dataclass(frozen=True)
class CameraConfig:
    """Security camera constants."""
    DEFAULT_VISION_RANGE: float = 200.0
    DEFAULT_VISION_ANGLE: float = 90.0
    DEFAULT_DISABLE_DURATION: float = 300.0  # 5 minutes
    DETECTION_COOLDOWN: float = 2.0
    SUSPICION_PER_DETECTION: float = 5.0


@dataclass(frozen=True)
class UIConfig:
    """UI-related constants."""
    NOTIFICATION_DEFAULT_DURATION: float = 5.0
    NOTIFICATION_FADE_TIME: float = 0.5
    MAX_VISIBLE_NOTIFICATIONS: int = 5
    TOOLTIP_DELAY: float = 0.5
    PANEL_ALPHA: int = 180


@dataclass(frozen=True)
class FBIConfig:
    """FBI investigation system constants."""
    INVESTIGATION_DURATION: float = 1209600.0  # 14 days in seconds
    RAID_WARNING_TIME: float = 86400.0  # 24 hours before raid
    HIGH_SUSPICION_THRESHOLD: float = 604800.0  # 7 days of high suspicion
    LAY_LOW_DURATION: float = 604800.0  # 7 days to lay low
    BRIBE_COST: int = 50000
    BRIBE_FAILURE_RISK: float = 0.3  # 30% chance of making things worse
    INITIAL_AGENT_COUNT: int = 5
    RAID_AGENT_COUNT: int = 20
    HIGH_SUSPICION_LEVEL: int = 80  # Level above which suspicion is "high"
    LAY_LOW_SUCCESS_THRESHOLD: int = 60  # Must be below this to succeed


@dataclass(frozen=True)
class AuthorityConfig:
    """Authority escalation system constants."""
    CHECK_INTERVAL: float = 3600.0  # 1 hour
    RESPONSE_TIME_MIN: float = 300.0  # 5 minutes minimum response
    RESPONSE_TIME_MAX: float = 1800.0  # 30 minutes maximum response
    PATROL_DURATION: float = 7200.0  # 2 hours patrol duration
    ALERT_DECAY_RATE: float = 0.05  # Alert level decay per check
    STATE_THRESHOLD: int = 50  # Suspicion level for state police
    FEDERAL_THRESHOLD: int = 100  # Suspicion level for FBI
    RAID_WARNING_MIN: float = 7200.0  # 2 hours minimum warning before raid
    RAID_WARNING_MAX: float = 14400.0  # 4 hours maximum warning before raid
    BRIBE_COOLDOWN_MIN: float = 86400.0  # 24 hours minimum bribe cooldown
    BRIBE_COOLDOWN_MAX: float = 172800.0  # 48 hours maximum bribe cooldown
    BRIBE_COOLDOWN_FAILURE_MIN: float = 172800.0  # 48 hours on failure
    BRIBE_COOLDOWN_FAILURE_MAX: float = 345600.0  # 96 hours on failure
    LOCAL_BRIBE_SUCCESS_RATE: float = 0.7  # 70% with local police
    STATE_BRIBE_SUCCESS_RATE: float = 0.4  # 40% with state police
    FEDERAL_BRIBE_SUCCESS_RATE: float = 0.15  # 15% with FBI
    FALSE_EVIDENCE_COST: int = 15000
    FALSE_EVIDENCE_SUCCESS_RATE: float = 0.6
    BANKRUPTCY_THRESHOLD: int = -50000


class DifficultyLevel(Enum):
    """Game difficulty levels."""
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    INSANE = "insane"


@dataclass
class DifficultyModifiers:
    """
    Modifiers applied based on difficulty level.

    All modifiers are multipliers (1.0 = normal, <1.0 = easier, >1.0 = harder).
    """
    # Police and authority modifiers
    police_patrol_frequency: float = 1.0  # How often patrols spawn
    police_patrol_count: float = 1.0  # Number of patrol officers
    police_vision_range: float = 1.0  # How far police can see
    police_response_time: float = 1.0  # How fast police respond (lower = faster)

    # Alert and suspicion modifiers
    alert_increase_rate: float = 1.0  # How fast alert level rises
    alert_cooldown_rate: float = 1.0  # How fast alert level decreases
    suspicion_gain_rate: float = 1.0  # How fast suspicion accumulates
    suspicion_decay_rate: float = 1.0  # How fast suspicion decays

    # NPC awareness modifiers
    npc_detection_range: float = 1.0  # How far NPCs can detect robot
    npc_alertness: float = 1.0  # Base NPC alertness level
    npc_report_chance: float = 1.0  # Chance NPC reports suspicious activity

    # Camera/security modifiers
    camera_detection_range: float = 1.0  # Camera vision range
    camera_rotation_speed: float = 1.0  # How fast cameras rotate
    security_response_time: float = 1.0  # Security reaction speed

    # Economy modifiers
    starting_money: float = 1.0  # Starting cash multiplier
    income_rate: float = 1.0  # Money earned multiplier
    expense_rate: float = 1.0  # Costs and fines multiplier
    fine_multiplier: float = 1.0  # Penalty fines

    # Game progression modifiers
    inspection_frequency: float = 1.0  # How often inspections occur
    inspection_strictness: float = 1.0  # How thorough inspections are
    research_speed: float = 1.0  # Research completion rate

    # Robot modifiers
    robot_power_drain: float = 1.0  # Power consumption rate
    robot_damage_rate: float = 1.0  # How fast robots take damage
    robot_repair_cost: float = 1.0  # Cost to repair robots

    # AI opponent modifiers
    ai_starting_money: float = 1.0  # AI starting capital multiplier
    ai_production_rate: float = 1.0  # AI production speed multiplier
    ai_expansion_rate: float = 1.0  # How fast AI expands (builds/upgrades)
    ai_decision_quality: float = 1.0  # AI decision intelligence (higher = smarter)
    ai_risk_tolerance: float = 1.0  # AI willingness to take risks
    ai_income_rate: float = 1.0  # AI income multiplier
    ai_expense_rate: float = 1.0  # AI expense multiplier


# Preset difficulty configurations
DIFFICULTY_PRESETS: Dict[DifficultyLevel, DifficultyModifiers] = {
    DifficultyLevel.EASY: DifficultyModifiers(
        police_patrol_frequency=0.5,
        police_patrol_count=0.75,
        police_vision_range=0.8,
        police_response_time=1.5,
        alert_increase_rate=0.6,
        alert_cooldown_rate=1.5,
        suspicion_gain_rate=0.5,
        suspicion_decay_rate=1.5,
        npc_detection_range=0.7,
        npc_alertness=0.6,
        npc_report_chance=0.5,
        camera_detection_range=0.8,
        camera_rotation_speed=0.7,
        security_response_time=1.5,
        starting_money=1.5,
        income_rate=1.25,
        expense_rate=0.75,
        fine_multiplier=0.5,
        inspection_frequency=0.5,
        inspection_strictness=0.6,
        research_speed=1.5,
        robot_power_drain=0.75,
        robot_damage_rate=0.5,
        robot_repair_cost=0.5,
        # AI opponents are weaker on easy
        ai_starting_money=0.7,
        ai_production_rate=0.6,
        ai_expansion_rate=0.5,
        ai_decision_quality=0.6,
        ai_risk_tolerance=0.8,
        ai_income_rate=0.7,
        ai_expense_rate=1.3,
    ),
    DifficultyLevel.NORMAL: DifficultyModifiers(),  # All defaults (1.0)
    DifficultyLevel.HARD: DifficultyModifiers(
        police_patrol_frequency=1.5,
        police_patrol_count=1.5,
        police_vision_range=1.2,
        police_response_time=0.7,
        alert_increase_rate=1.5,
        alert_cooldown_rate=0.7,
        suspicion_gain_rate=1.5,
        suspicion_decay_rate=0.7,
        npc_detection_range=1.25,
        npc_alertness=1.3,
        npc_report_chance=1.5,
        camera_detection_range=1.2,
        camera_rotation_speed=1.3,
        security_response_time=0.7,
        starting_money=0.75,
        income_rate=0.85,
        expense_rate=1.25,
        fine_multiplier=1.5,
        inspection_frequency=1.5,
        inspection_strictness=1.3,
        research_speed=0.8,
        robot_power_drain=1.25,
        robot_damage_rate=1.5,
        robot_repair_cost=1.5,
        # AI opponents are stronger on hard
        ai_starting_money=1.3,
        ai_production_rate=1.4,
        ai_expansion_rate=1.5,
        ai_decision_quality=1.3,
        ai_risk_tolerance=1.2,
        ai_income_rate=1.3,
        ai_expense_rate=0.8,
    ),
    DifficultyLevel.INSANE: DifficultyModifiers(
        police_patrol_frequency=2.0,
        police_patrol_count=2.0,
        police_vision_range=1.5,
        police_response_time=0.5,
        alert_increase_rate=2.0,
        alert_cooldown_rate=0.5,
        suspicion_gain_rate=2.0,
        suspicion_decay_rate=0.5,
        npc_detection_range=1.5,
        npc_alertness=1.5,
        npc_report_chance=2.0,
        camera_detection_range=1.5,
        camera_rotation_speed=1.5,
        security_response_time=0.5,
        starting_money=0.5,
        income_rate=0.7,
        expense_rate=1.5,
        fine_multiplier=2.0,
        inspection_frequency=2.0,
        inspection_strictness=1.5,
        research_speed=0.6,
        robot_power_drain=1.5,
        robot_damage_rate=2.0,
        robot_repair_cost=2.0,
        # AI opponents are much stronger on insane
        ai_starting_money=1.5,
        ai_production_rate=1.8,
        ai_expansion_rate=2.0,
        ai_decision_quality=1.5,
        ai_risk_tolerance=1.4,
        ai_income_rate=1.5,
        ai_expense_rate=0.6,
    ),
}


class MapSize(Enum):
    """Predefined map sizes."""
    TINY = "tiny"        # 50x40 tiles
    SMALL = "small"      # 75x60 tiles
    MEDIUM = "medium"    # 100x75 tiles (default)
    LARGE = "large"      # 150x100 tiles
    HUGE = "huge"        # 200x150 tiles


class CitySize(Enum):
    """City density/coverage options."""
    MINIMAL = "minimal"    # Small settlement
    SMALL = "small"        # Small town
    MEDIUM = "medium"      # Standard city
    LARGE = "large"        # Major city
    METROPOLIS = "metropolis"  # Dense urban sprawl


class GeographicFeature(Enum):
    """Types of geographic features."""
    NONE = "none"
    RIVER = "river"
    OCEAN_SOUTH = "ocean_south"
    OCEAN_WEST = "ocean_west"
    OCEAN_EAST = "ocean_east"
    OCEAN_NORTH = "ocean_north"
    COASTAL_SOUTHWEST = "coastal_southwest"
    COASTAL_SOUTHEAST = "coastal_southeast"
    ISLAND = "island"


@dataclass
class WorldConfig:
    """
    World generation configuration options.

    Controls map size, city generation, and geographic features.
    """
    # Map dimensions
    map_size: MapSize = MapSize.MEDIUM
    custom_width: Optional[int] = None  # Override for custom size
    custom_height: Optional[int] = None  # Override for custom size

    # City configuration
    city_size: CitySize = CitySize.MEDIUM
    city_density: float = 0.6  # 0.0-1.0, how packed buildings are
    residential_ratio: float = 0.4  # Proportion of residential zones
    commercial_ratio: float = 0.3  # Proportion of commercial zones
    industrial_ratio: float = 0.2  # Proportion of industrial zones
    park_ratio: float = 0.1  # Proportion of park zones

    # Geographic features
    geographic_features: List[GeographicFeature] = field(
        default_factory=lambda: [GeographicFeature.NONE]
    )
    num_rivers: int = 0  # Number of rivers (0-3)
    ocean_depth: int = 8  # Ocean tile depth from edge
    create_docks: bool = True  # Whether to create dock areas
    create_bridges: bool = True  # Whether to create bridges over rivers

    # Terrain options
    seed: Optional[int] = None  # Random seed for reproducible generation

    def get_dimensions(self) -> tuple:
        """Get map dimensions in tiles based on size setting."""
        if self.custom_width and self.custom_height:
            return (self.custom_width, self.custom_height)

        size_map = {
            MapSize.TINY: (50, 40),
            MapSize.SMALL: (75, 60),
            MapSize.MEDIUM: (100, 75),
            MapSize.LARGE: (150, 100),
            MapSize.HUGE: (200, 150),
        }
        return size_map.get(self.map_size, (100, 75))

    def get_city_block_ratio(self) -> float:
        """Get target ratio of city blocks to fill."""
        ratio_map = {
            CitySize.MINIMAL: 0.2,
            CitySize.SMALL: 0.35,
            CitySize.MEDIUM: 0.5,
            CitySize.LARGE: 0.7,
            CitySize.METROPOLIS: 0.85,
        }
        return ratio_map.get(self.city_size, 0.5)

    def get_ocean_edges(self) -> List[str]:
        """Get list of ocean edges based on geographic features."""
        edges = []
        edge_map = {
            GeographicFeature.OCEAN_SOUTH: ['south'],
            GeographicFeature.OCEAN_WEST: ['west'],
            GeographicFeature.OCEAN_EAST: ['east'],
            GeographicFeature.OCEAN_NORTH: ['north'],
            GeographicFeature.COASTAL_SOUTHWEST: ['south', 'west'],
            GeographicFeature.COASTAL_SOUTHEAST: ['south', 'east'],
            GeographicFeature.ISLAND: ['north', 'south', 'east', 'west'],
        }
        for feature in self.geographic_features:
            if feature in edge_map:
                edges.extend(edge_map[feature])
        return list(set(edges))  # Remove duplicates

    def has_rivers(self) -> bool:
        """Check if rivers should be generated."""
        return (
            self.num_rivers > 0 or
            GeographicFeature.RIVER in self.geographic_features
        )


@dataclass
class GameSettings:
    """
    Complete game settings combining difficulty and world config.

    This is the main configuration object passed to the game.
    """
    difficulty: DifficultyLevel = DifficultyLevel.NORMAL
    world: WorldConfig = field(default_factory=WorldConfig)

    # Custom difficulty modifiers (optional override)
    custom_modifiers: Optional[DifficultyModifiers] = None

    def get_modifiers(self) -> DifficultyModifiers:
        """Get difficulty modifiers, using custom if set."""
        if self.custom_modifiers:
            return self.custom_modifiers
        return DIFFICULTY_PRESETS.get(self.difficulty, DifficultyModifiers())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameSettings':
        """Create GameSettings from a dictionary."""
        difficulty = DifficultyLevel(data.get('difficulty', 'normal'))

        world_data = data.get('world', {})
        world = WorldConfig(
            map_size=MapSize(world_data.get('map_size', 'medium')),
            custom_width=world_data.get('custom_width'),
            custom_height=world_data.get('custom_height'),
            city_size=CitySize(world_data.get('city_size', 'medium')),
            city_density=world_data.get('city_density', 0.6),
            num_rivers=world_data.get('num_rivers', 0),
            ocean_depth=world_data.get('ocean_depth', 8),
            create_docks=world_data.get('create_docks', True),
            create_bridges=world_data.get('create_bridges', True),
            seed=world_data.get('seed'),
        )

        # Parse geographic features
        features = world_data.get('geographic_features', ['none'])
        if isinstance(features, list):
            world.geographic_features = [GeographicFeature(f) for f in features]

        return cls(difficulty=difficulty, world=world)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'difficulty': self.difficulty.value,
            'world': {
                'map_size': self.world.map_size.value,
                'custom_width': self.world.custom_width,
                'custom_height': self.world.custom_height,
                'city_size': self.world.city_size.value,
                'city_density': self.world.city_density,
                'residential_ratio': self.world.residential_ratio,
                'commercial_ratio': self.world.commercial_ratio,
                'industrial_ratio': self.world.industrial_ratio,
                'park_ratio': self.world.park_ratio,
                'geographic_features': [f.value for f in self.world.geographic_features],
                'num_rivers': self.world.num_rivers,
                'ocean_depth': self.world.ocean_depth,
                'create_docks': self.world.create_docks,
                'create_bridges': self.world.create_bridges,
                'seed': self.world.seed,
            },
        }


# Create singleton instances
TIME = TimeConfig()
INSPECTION = InspectionConfig()
ENTITY = EntityConfig()
SUSPICION = SuspicionConfig()
ROBOT = RobotConfig()
BUILDING = BuildingConfig()
WEATHER = WeatherConfig()
MARKET = MarketConfig()
CAMERA = CameraConfig()
UI = UIConfig()
FBI = FBIConfig()
AUTHORITY = AuthorityConfig()

# Default game settings (can be overridden at game start)
DEFAULT_GAME_SETTINGS = GameSettings()


def get_difficulty_modifiers(difficulty: str) -> DifficultyModifiers:
    """
    Get difficulty modifiers for a difficulty string.

    Args:
        difficulty: Difficulty level string ('easy', 'normal', 'hard', 'insane')

    Returns:
        DifficultyModifiers for the specified level
    """
    try:
        level = DifficultyLevel(difficulty.lower())
        return DIFFICULTY_PRESETS.get(level, DifficultyModifiers())
    except ValueError:
        return DifficultyModifiers()  # Return normal if invalid


def create_world_config(
    map_size: str = 'medium',
    city_size: str = 'medium',
    has_ocean: bool = False,
    ocean_side: str = 'south',
    has_river: bool = False,
    num_rivers: int = 1,
    seed: Optional[int] = None,
) -> WorldConfig:
    """
    Create a WorldConfig with common presets.

    Args:
        map_size: 'tiny', 'small', 'medium', 'large', 'huge'
        city_size: 'minimal', 'small', 'medium', 'large', 'metropolis'
        has_ocean: Whether to include ocean
        ocean_side: Which side for ocean ('south', 'west', 'east', 'north')
        has_river: Whether to include a river
        num_rivers: Number of rivers (1-3)
        seed: Random seed for reproducibility

    Returns:
        Configured WorldConfig
    """
    features = []

    if has_ocean:
        ocean_map = {
            'south': GeographicFeature.OCEAN_SOUTH,
            'west': GeographicFeature.OCEAN_WEST,
            'east': GeographicFeature.OCEAN_EAST,
            'north': GeographicFeature.OCEAN_NORTH,
        }
        features.append(ocean_map.get(ocean_side, GeographicFeature.OCEAN_SOUTH))

    if has_river:
        features.append(GeographicFeature.RIVER)

    if not features:
        features.append(GeographicFeature.NONE)

    return WorldConfig(
        map_size=MapSize(map_size),
        city_size=CitySize(city_size),
        geographic_features=features,
        num_rivers=num_rivers if has_river else 0,
        seed=seed,
    )
