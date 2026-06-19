"""
Centralized game configuration values.

This module contains all magic numbers and configuration constants
used throughout the game, organized by category. Using these constants
instead of hardcoded values makes the game easier to tune and maintain.
"""

from dataclasses import dataclass


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


@dataclass(frozen=True)
class MarketConfig:
    """Market/economy constants."""
    PRICE_FLUCTUATION_RANGE: float = 0.15  # +/- 15%
    PRICE_UPDATE_INTERVAL: float = 60.0  # Every game minute
    ORGANIC_DECAY_RATE: float = 0.001  # 0.1% per check
    DECAY_CHECK_INTERVAL: float = 300.0  # Every 5 game minutes


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
