"""
Game constants and enumerations.
"""

from enum import Enum, auto


# Colors (RGB)
class Colors:
    """Standard colors used throughout the game."""
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (192, 192, 192)

    # Game-specific colors
    ROBOT_COLOR = (0, 255, 0)
    NPC_COLOR = (255, 200, 0)
    BUILDING_COLOR = (150, 75, 0)
    LANDFILL_COLOR = (100, 80, 60)
    CITY_COLOR = (128, 128, 128)
    FACTORY_COLOR = (80, 80, 120)


# Entity states
class RobotState(Enum):
    """Robot behavior states."""
    IDLE = auto()
    MANUAL = auto()  # Player is manually controlling
    MOVING_TO_OBJECT = auto()
    COLLECTING = auto()
    RETURNING_TO_FACTORY = auto()
    UNLOADING = auto()
    CHARGING = auto()
    UPGRADING = auto()
    BROKEN = auto()


class NPCActivity(Enum):
    """NPC daily activities."""
    SLEEPING = auto()
    HOME_ROUTINE = auto()
    COMMUTING = auto()
    WORKING = auto()
    SHOPPING = auto()
    LEISURE = auto()


# Material types
class MaterialType(Enum):
    """Types of collectible materials."""
    PLASTIC = auto()
    GLASS = auto()
    METAL = auto()
    PRECIOUS_METAL = auto()
    RUBBER = auto()
    BIO_SLOP = auto()
    WOOD = auto()
    LIQUID = auto()
    TOXIC = auto()
    ELECTRONIC = auto()
    CONCRETE = auto()
    WIRE = auto()


# Building types
class BuildingType(Enum):
    """Types of buildings (matches buildings.json)."""
    # Core buildings
    FACTORY = auto()
    WAREHOUSE = auto()

    # Power buildings
    LANDFILL_GAS_EXTRACTION = auto()
    SOLAR_ARRAY = auto()
    WIND_TURBINE = auto()
    NATURAL_GAS_GENERATOR = auto()
    STEAM_GENERATOR = auto()
    BATTERY_STORAGE = auto()

    # Processing buildings
    LANDFILL_GAS_PLANT = auto()
    BIO_WASTE_TREATMENT_TANK = auto()
    CRUDE_OIL_REFINERY = auto()
    COAL_OVEN = auto()
    METAL_REFINERY = auto()
    GLASSWORKS = auto()
    PLASTIC_RECYCLER = auto()
    RUBBER_RECYCLER = auto()
    PAPER_RECYCLER = auto()
    TOXIC_INCINERATOR = auto()

    # Infrastructure buildings
    SERVER_FARM = auto()
    WIRELESS_POWER_TRANSMITTER = auto()
    WIRELESS_SIGNAL_TRANSMITTER = auto()
    LIGHTNING_ROD = auto()
    ROAD_DIRT = auto()
    ROAD_TAR = auto()
    ROAD_ASPHALT = auto()
    PIPE = auto()
    PUMP = auto()

    # Defense buildings
    WALL_SLAG = auto()
    WALL_METAL = auto()
    WALL_LASER = auto()
    GATE_SCRAP = auto()
    GATE_METAL = auto()

    # City buildings
    HOUSE = auto()
    STORE = auto()
    POLICE_STATION = auto()
    OFFICE = auto()
    SCHOOL = auto()


class ConstructionState(Enum):
    """Building construction states."""
    COMPLETE = auto()
    UNDER_CONSTRUCTION = auto()
    DECREPIT = auto()
    ABANDONED = auto()


# Zone types
class ZoneType(Enum):
    """Collection zone types."""
    LANDFILL = auto()
    CITY = auto()


# Suspicion levels
class SuspicionLevel(Enum):
    """Authority response levels."""
    NONE = 0
    RUMORS = 20
    INVESTIGATION = 40
    INSPECTION = 60
    RESTRICTED = 80
    FEDERAL = 100
