"""
SaveManager - Manages saving and loading game state.

Handles:
- Serializing game state to JSON
- Saving to file with atomic writes
- Loading from file with validation
- Auto-save functionality
- Multiple save slots
"""

import json
import os
import re
import shutil
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

from src.core.logger import get_logger

logger = get_logger(__name__)


class SaveValidationError(Exception):
    """Raised when save file validation fails."""
    pass


class SaveManager:
    """
    Manages the save/load system for the game.

    Serializes all game state to JSON and saves to disk.
    Loads saved games and reconstructs game state.
    """

    SAVE_VERSION = "1.0"
    SAVE_DIRECTORY = "data/saves"
    AUTO_SAVE_NAME = "autosave"
    QUICK_SAVE_NAME = "quicksave"

    def __init__(self):
        """Initialize the save manager."""
        # Ensure save directory exists
        os.makedirs(self.SAVE_DIRECTORY, exist_ok=True)

        # Auto-save settings
        self.auto_save_enabled = True
        self.auto_save_interval_days = 5  # Game days between auto-saves
        self.last_auto_save_day = 0

        # Current save file name (for quick save)
        self.current_save_name: Optional[str] = None

    def _sanitize_save_name(self, save_name: str) -> str:
        """
        Sanitize a save name to prevent path traversal and invalid characters.

        Args:
            save_name: The raw save name input

        Returns:
            Sanitized save name

        Raises:
            ValueError: If save name is invalid or potentially malicious
        """
        if not save_name:
            raise ValueError("Save name cannot be empty")

        # Convert to string and strip whitespace
        save_name = str(save_name).strip()

        if not save_name:
            raise ValueError("Save name cannot be empty or whitespace only")

        # Check for path traversal attempts
        if '..' in save_name:
            raise ValueError("Save name cannot contain '..'")

        if save_name.startswith('/') or save_name.startswith('\\'):
            raise ValueError("Save name cannot be an absolute path")

        # Check for path separators
        if '/' in save_name or '\\' in save_name:
            raise ValueError("Save name cannot contain path separators")

        # Check for other dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\x00']
        for char in dangerous_chars:
            if char in save_name:
                raise ValueError(f"Save name cannot contain '{char}'")

        # Validate against whitelist pattern: alphanumeric, underscore, hyphen, space, period
        if not re.match(r'^[\w\-. ]+$', save_name):
            raise ValueError("Save name contains invalid characters. Use only letters, numbers, underscore, hyphen, space, or period")

        # Limit length
        max_length = 50
        if len(save_name) > max_length:
            raise ValueError(f"Save name cannot exceed {max_length} characters")

        # Don't allow names that are only dots/spaces
        if save_name.replace('.', '').replace(' ', '') == '':
            raise ValueError("Save name must contain at least one alphanumeric character")

        return save_name

    def _validate_path_security(self, file_path: str) -> bool:
        """
        Validate that a file path is within the allowed save directory.

        Args:
            file_path: The file path to validate

        Returns:
            True if path is safe

        Raises:
            ValueError: If path escapes the save directory
        """
        # Get absolute paths for comparison
        save_dir_abs = os.path.abspath(self.SAVE_DIRECTORY)
        file_path_abs = os.path.abspath(file_path)

        # Resolve any symlinks
        save_dir_real = os.path.realpath(save_dir_abs)
        file_path_real = os.path.realpath(file_path_abs)

        # Check that file path starts with save directory
        if not file_path_real.startswith(save_dir_real + os.sep) and file_path_real != save_dir_real:
            raise ValueError(f"Path '{file_path}' escapes save directory")

        return True

    def _validate_save_schema(self, save_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate save file structure and data types.

        Args:
            save_data: The loaded save data dictionary

        Returns:
            Tuple of (is_valid, list of warning messages)
        """
        warnings = []

        # Check required top-level keys
        required_keys = ['version', 'timestamp', 'game_state']
        for key in required_keys:
            if key not in save_data:
                warnings.append(f"Missing required key: {key}")

        # Validate version
        version = save_data.get('version')
        if version is not None and not isinstance(version, str):
            warnings.append(f"Invalid version type: expected str, got {type(version).__name__}")

        # Validate timestamp
        timestamp = save_data.get('timestamp')
        if timestamp is not None and not isinstance(timestamp, str):
            warnings.append(f"Invalid timestamp type: expected str, got {type(timestamp).__name__}")

        # Validate game_state structure
        game_state = save_data.get('game_state')
        if game_state is None:
            warnings.append("game_state is missing or null")
        elif not isinstance(game_state, dict):
            warnings.append(f"Invalid game_state type: expected dict, got {type(game_state).__name__}")
        else:
            # Validate game_state sub-structures
            self._validate_game_state_schema(game_state, warnings)

        is_valid = len([w for w in warnings if 'Missing required' in w or 'is missing' in w]) == 0
        return is_valid, warnings

    def _validate_game_state_schema(self, game_state: Dict[str, Any], warnings: List[str]):
        """Validate game_state structure and types."""
        # Validate time section
        time_data = game_state.get('time', {})
        if not isinstance(time_data, dict):
            warnings.append("time should be a dictionary")
        else:
            if 'day' in time_data and not isinstance(time_data['day'], (int, float)):
                warnings.append(f"time.day should be numeric, got {type(time_data['day']).__name__}")
            if 'hour' in time_data and not isinstance(time_data['hour'], (int, float)):
                warnings.append(f"time.hour should be numeric, got {type(time_data['hour']).__name__}")

        # Validate resources section
        resources = game_state.get('resources', {})
        if not isinstance(resources, dict):
            warnings.append("resources should be a dictionary")
        else:
            if 'money' in resources and not isinstance(resources['money'], (int, float)):
                warnings.append(f"resources.money should be numeric, got {type(resources['money']).__name__}")

        # Validate buildings section
        buildings = game_state.get('buildings', [])
        if not isinstance(buildings, list):
            warnings.append("buildings should be a list")

        # Validate robots section
        robots = game_state.get('robots', [])
        if not isinstance(robots, list):
            warnings.append("robots should be a list")

        # Validate research section
        research = game_state.get('research', {})
        if not isinstance(research, dict):
            warnings.append("research should be a dictionary")

    def save_game(self, game_state: Dict[str, Any], save_name: str = None) -> bool:
        """
        Save the game state to a file.

        Args:
            game_state: Dictionary containing all game state data
            save_name: Name of the save file (without extension). If None, uses current_save_name.

        Returns:
            True if save successful, False otherwise
        """
        if save_name is None:
            save_name = self.current_save_name or self.AUTO_SAVE_NAME

        # Sanitize save name for security
        try:
            save_name = self._sanitize_save_name(save_name)
        except ValueError as e:
            logger.error(f"Invalid save name: {e}")
            return False

        # Update current save name
        self.current_save_name = save_name

        # Create save data structure
        save_data = {
            "version": self.SAVE_VERSION,
            "timestamp": datetime.now().isoformat(),
            "save_name": save_name,
            "game_state": game_state
        }

        # Get and validate file path
        file_path = self._get_save_path(save_name)
        try:
            self._validate_path_security(file_path)
        except ValueError as e:
            logger.error(f"Security error: {e}")
            return False

        # Save to file using atomic write
        try:
            save_dir = os.path.dirname(file_path)
            fd, temp_path = tempfile.mkstemp(
                suffix='.json.tmp',
                prefix=f'{save_name}_',
                dir=save_dir
            )
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                shutil.move(temp_path, file_path)
                logger.info(f"Game saved to: {file_path}")
                return True
            except Exception:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise

        except PermissionError as e:
            logger.error(f"Permission denied saving game: {e}")
            return False
        except OSError as e:
            logger.error(f"OS error saving game: {e}")
            return False
        except Exception as e:
            logger.exception(f"Error saving game: {e}")
            return False

    def load_game(self, save_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a game state from a file.

        Args:
            save_name: Name of the save file (without extension)

        Returns:
            Game state dictionary if successful, None otherwise
        """
        # Sanitize save name for security
        try:
            save_name = self._sanitize_save_name(save_name)
        except ValueError as e:
            logger.error(f"Invalid save name: {e}")
            return None

        file_path = self._get_save_path(save_name)

        # Validate path security
        try:
            self._validate_path_security(file_path)
        except ValueError as e:
            logger.error(f"Security error: {e}")
            return None

        if not os.path.exists(file_path):
            logger.warning(f"Save file not found: {file_path}")
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)

            # Validate save file schema
            is_valid, warnings = self._validate_save_schema(save_data)
            for warning in warnings:
                logger.warning(f"Save validation: {warning}")

            if not is_valid:
                logger.error("Save file failed validation - required fields missing")
                return None

            # Validate save version
            if save_data.get("version") != self.SAVE_VERSION:
                logger.warning(f"Save version mismatch. Expected {self.SAVE_VERSION}, got {save_data.get('version')}")

            # Update current save name
            self.current_save_name = save_name

            logger.info(f"Game loaded from: {file_path}")
            logger.debug(f"Save timestamp: {save_data.get('timestamp')}")

            return save_data.get("game_state")

        except json.JSONDecodeError as e:
            logger.error(f"Save file is not valid JSON: {e}")
            return None
        except PermissionError as e:
            logger.error(f"Permission denied reading save: {e}")
            return None
        except Exception as e:
            logger.exception(f"Error loading game: {e}")
            return None

    def quick_save(self, game_state: Dict[str, Any]) -> bool:
        """
        Quick save to the quicksave slot.

        Args:
            game_state: Dictionary containing all game state data

        Returns:
            True if save successful, False otherwise
        """
        return self.save_game(game_state, self.QUICK_SAVE_NAME)

    def quick_load(self) -> Optional[Dict[str, Any]]:
        """
        Quick load from the quicksave slot.

        Returns:
            Game state dictionary if successful, None otherwise
        """
        return self.load_game(self.QUICK_SAVE_NAME)

    def auto_save(self, game_state: Dict[str, Any], current_day: int) -> bool:
        """
        Auto-save if enough game days have passed.

        Args:
            game_state: Dictionary containing all game state data
            current_day: Current game day

        Returns:
            True if auto-save was performed, False otherwise
        """
        if not self.auto_save_enabled:
            return False

        if current_day - self.last_auto_save_day >= self.auto_save_interval_days:
            success = self.save_game(game_state, self.AUTO_SAVE_NAME)
            if success:
                self.last_auto_save_day = current_day
                logger.info(f"Auto-save completed at day {current_day}")
            return success

        return False

    def get_save_list(self) -> list:
        """
        Get list of all save files.

        Returns:
            List of save file info dictionaries
        """
        save_files = []

        if not os.path.exists(self.SAVE_DIRECTORY):
            return save_files

        for filename in os.listdir(self.SAVE_DIRECTORY):
            if filename.endswith('.json'):
                save_name = filename[:-5]  # Remove .json extension
                file_path = os.path.join(self.SAVE_DIRECTORY, filename)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)

                    save_info = {
                        "name": save_name,
                        "timestamp": save_data.get("timestamp", "Unknown"),
                        "version": save_data.get("version", "Unknown"),
                        "file_path": file_path
                    }

                    # Extract some game state info if available
                    game_state = save_data.get("game_state", {})
                    if game_state:
                        save_info["day"] = game_state.get("time", {}).get("day", 0)
                        save_info["money"] = game_state.get("resources", {}).get("money", 0)

                    save_files.append(save_info)

                except Exception as e:
                    logger.warning(f"Error reading save file {filename}: {e}")

        # Sort by timestamp (newest first)
        save_files.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return save_files

    def delete_save(self, save_name: str) -> bool:
        """
        Delete a save file.

        Args:
            save_name: Name of the save file to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        # Sanitize save name for security
        try:
            save_name = self._sanitize_save_name(save_name)
        except ValueError as e:
            logger.error(f"Invalid save name: {e}")
            return False

        file_path = self._get_save_path(save_name)

        # Validate path security
        try:
            self._validate_path_security(file_path)
        except ValueError as e:
            logger.error(f"Security error: {e}")
            return False

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Deleted save: {save_name}")
                return True
            except PermissionError as e:
                logger.error(f"Permission denied deleting save: {e}")
                return False
            except Exception as e:
                logger.exception(f"Error deleting save: {e}")
                return False
        else:
            logger.warning(f"Save file not found: {save_name}")
            return False

    def _get_save_path(self, save_name: str) -> str:
        """
        Get the full path for a save file.

        Args:
            save_name: Name of the save file

        Returns:
            Full path to the save file
        """
        return os.path.join(self.SAVE_DIRECTORY, f"{save_name}.json")

    @staticmethod
    def _serialize_weather_state(game) -> Dict[str, Any]:
        """
        Serialize weather manager state.

        Args:
            game: Game instance

        Returns:
            Dictionary of weather state
        """
        if not hasattr(game, 'weather_manager') or game.weather_manager is None:
            return {"current": "CLEAR"}

        wm = game.weather_manager
        state = {
            "current": wm.current_weather.name if hasattr(wm.current_weather, 'name') else "CLEAR",
            "weather_duration": getattr(wm, 'weather_duration', 3600),
            "weather_elapsed": getattr(wm, 'weather_elapsed', 0),
            "transitioning": getattr(wm, 'transitioning', False),
            "transition_elapsed": getattr(wm, 'transition_elapsed', 0),
        }

        # Add next weather if transitioning
        if wm.transitioning and hasattr(wm, 'next_weather') and wm.next_weather:
            state["next_weather"] = (wm.next_weather.name
                                     if hasattr(wm.next_weather, 'name')
                                     else str(wm.next_weather))

        # Add intensity if available (backward compatibility)
        if hasattr(wm, 'weather_intensity'):
            state["intensity"] = wm.weather_intensity

        return state

    @staticmethod
    def _serialize_building_data(building) -> Dict[str, Any]:
        """
        Serialize building-specific data for storage.

        Args:
            building: Building instance to serialize

        Returns:
            Dictionary of building-specific data
        """
        data = {}

        # Stored materials (Factory, Warehouse, Silo)
        if hasattr(building, 'stored_materials') and building.stored_materials:
            data['stored_materials'] = building.stored_materials.copy()

        # Processing queues (processing buildings)
        if hasattr(building, 'input_queue') and building.input_queue:
            data['input_queue'] = building.input_queue.copy()

        if hasattr(building, 'output_queue') and building.output_queue:
            data['output_queue'] = building.output_queue.copy()

        # Current processing state
        if hasattr(building, 'processing_current') and building.processing_current:
            data['processing_current'] = building.processing_current

        if hasattr(building, 'processing_time_remaining'):
            data['processing_time_remaining'] = building.processing_time_remaining

        # Solar array state
        if hasattr(building, 'current_hour'):
            data['current_hour'] = building.current_hour

        # Battery bank state
        if hasattr(building, 'stored_power'):
            data['stored_power'] = building.stored_power

        # Methane generator fuel
        if hasattr(building, 'fuel_level'):
            data['fuel_level'] = building.fuel_level

        # Power generation for power buildings
        if hasattr(building, 'power_generation'):
            data['power_generation'] = building.power_generation

        return data

    @staticmethod
    def serialize_game_state(game) -> Dict[str, Any]:
        """
        Serialize the entire game state to a dictionary.

        Args:
            game: The Game object

        Returns:
            Dictionary containing all game state
        """
        game_state = {
            # Time
            "time": {
                "day": game.day,
                "hour": game.hour,
                "minute": game.minute,
                "time_speed": game.time_speed,
                "paused": game.paused
            },

            # Resources
            "resources": {
                "money": game.resource_manager.money,
                "materials": game.resource_manager.materials.copy()
            },

            # Buildings
            "buildings": [
                {
                    "id": building.id,
                    "type": (building.building_type.name
                            if hasattr(building.building_type, 'name')
                            else str(building.building_type)),
                    "x": building.grid_x,
                    "y": building.grid_y,
                    "level": building.level,
                    "powered": building.powered,
                    "active": getattr(building, 'active', True),
                    "health": getattr(building, 'health', 100.0),
                    "construction_progress": getattr(building, 'construction_progress', 100.0),
                    "under_construction": getattr(building, 'under_construction', False),
                    # Add building-specific data
                    "data": SaveManager._serialize_building_data(building)
                }
                for building in game.building_manager.buildings.values()
            ],

            # Robots
            "robots": [
                {
                    "id": robot.id,
                    "x": robot.x,
                    "y": robot.y,
                    "speed": robot.speed,
                    "capacity": robot.max_capacity,
                    "battery": robot.current_power if hasattr(robot, 'current_power') else 100,
                    "inventory": robot.inventory.copy() if hasattr(robot, 'inventory') else {},
                    "state": robot.state.name if hasattr(robot.state, 'name') else str(robot.state),
                    "autonomous": getattr(robot, 'autonomous', True),
                    "current_health": getattr(robot, 'current_health', 100),
                    "upgrade_level": getattr(robot, 'upgrade_level', 1),
                    "target_x": getattr(robot, 'target_x', None),
                    "target_y": getattr(robot, 'target_y', None)
                }
                for robot in game.entity_manager.robots
            ],

            # Research
            "research": {
                "completed": list(game.research_manager.completed_research),
                "current": game.research_manager.current_research,
                "progress": game.research_manager.research_progress,
                "time_required": game.research_manager.research_time_required
            },

            # Suspicion and Detection
            "suspicion": {
                "level": game.suspicion_manager.suspicion_level if hasattr(game, 'suspicion_manager') else 0,
                "sources": game.suspicion_manager.suspicion_sources.copy() if hasattr(game, 'suspicion_manager') else {}
            },

            # Police
            "police": {
                "patrol_routes": [
                    {
                        "route": route.waypoints if hasattr(route, 'waypoints') else [],
                        "active": route.active if hasattr(route, 'active') else True
                    }
                    for route in (game.police_manager.patrol_routes if hasattr(game, 'police_manager') else [])
                ]
            },

            # Cameras
            "cameras": [
                {
                    "id": camera.id,
                    "x": camera.x,
                    "y": camera.y,
                    "angle": camera.angle if hasattr(camera, 'angle') else 0,
                    "active": camera.active if hasattr(camera, 'active') else True,
                    "hacked": camera.hacked if hasattr(camera, 'hacked') else False
                }
                for camera in (game.camera_manager.cameras if hasattr(game, 'camera_manager') else [])
            ],

            # Inspection
            "inspection": {
                "scheduled": game.inspection_manager.inspection_scheduled if hasattr(game, 'inspection_manager') else False,
                "countdown": game.inspection_manager.inspection_countdown if hasattr(game, 'inspection_manager') else 0
            },

            # FBI
            "fbi": {
                "investigation_level": game.fbi_manager.investigation_level if hasattr(game, 'fbi_manager') else 0,
                "active": game.fbi_manager.investigation_active if hasattr(game, 'fbi_manager') else False
            },

            # Weather
            "weather": SaveManager._serialize_weather_state(game),

            # Material Inventory (if exists)
            "material_inventory": {
                "tagged_materials": game.material_inventory.tagged_materials.copy() if hasattr(game, 'material_inventory') else {}
            },

            # Statistics
            "stats": {
                "total_materials_collected": game.stats.get("materials_collected", 0) if hasattr(game, 'stats') else 0,
                "total_money_earned": game.stats.get("money_earned", 0) if hasattr(game, 'stats') else 0,
                "total_buildings_built": game.stats.get("buildings_built", 0) if hasattr(game, 'stats') else 0
            }
        }

        return game_state

    @staticmethod
    def _safe_int(value: Any, default: int) -> int:
        """Safely convert value to int with default fallback."""
        if value is None:
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _safe_float(value: Any, default: float) -> float:
        """Safely convert value to float with default fallback."""
        if value is None:
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _safe_bool(value: Any, default: bool) -> bool:
        """Safely convert value to bool with default fallback."""
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes')
        return bool(value)

    @staticmethod
    def _safe_dict(value: Any, default: Dict = None) -> Dict:
        """Safely get dictionary with default fallback."""
        if default is None:
            default = {}
        if value is None:
            return default.copy() if default else {}
        if isinstance(value, dict):
            return value.copy()
        return default.copy() if default else {}

    @staticmethod
    def _safe_list(value: Any, default: list = None) -> list:
        """Safely get list with default fallback."""
        if default is None:
            default = []
        if value is None:
            return default.copy() if default else []
        if isinstance(value, list):
            return value.copy()
        return default.copy() if default else []

    @staticmethod
    def _create_building_from_data(building_data: Dict[str, Any]):
        """
        Create a building instance from saved data.

        Args:
            building_data: Dictionary containing building state

        Returns:
            Building instance or None if creation failed
        """
        building_type = building_data.get('type', '').lower()
        grid_x = SaveManager._safe_int(building_data.get('x'), 0)
        grid_y = SaveManager._safe_int(building_data.get('y'), 0)

        # Import building classes
        from src.entities.buildings.factory import Factory
        from src.entities.buildings.landfill_gas_extraction import LandfillGasExtraction
        from src.entities.buildings.paper_recycler import PaperRecycler
        from src.entities.buildings.plastic_recycler import PlasticRecycler
        from src.entities.buildings.metal_refinery import MetalRefinery
        from src.entities.buildings.glassworks import Glassworks
        from src.entities.buildings.rubber_recycler import RubberRecycler
        from src.entities.buildings.warehouse import Warehouse
        from src.entities.buildings.silo import Silo
        from src.entities.buildings.solar_array import SolarArray
        from src.entities.buildings.methane_generator import MethaneGenerator
        from src.entities.buildings.battery_bank import BatteryBank
        from src.entities.buildings.bio_waste_treatment import BioWasteTreatment
        from src.entities.buildings.toxic_incinerator import ToxicIncinerator
        from src.entities.buildings.coal_oven import CoalOven
        from src.entities.buildings.crude_oil_refinery import CrudeOilRefinery
        from src.entities.buildings.landfill_gas_plant import LandfillGasPlant
        from src.entities.buildings.circuit_board_fab import CircuitBoardFab
        from src.entities.buildings.motor_assembly import MotorAssembly
        from src.entities.buildings.battery_fab import BatteryFab

        # Map building type strings to classes
        building_classes = {
            'factory': Factory,
            'landfill_gas_extraction': LandfillGasExtraction,
            'paper_recycler': PaperRecycler,
            'plastic_recycler': PlasticRecycler,
            'metal_refinery': MetalRefinery,
            'glassworks': Glassworks,
            'rubber_recycler': RubberRecycler,
            'warehouse': Warehouse,
            'silo': Silo,
            'solar_array': SolarArray,
            'methane_generator': MethaneGenerator,
            'battery_bank': BatteryBank,
            'bio_waste_treatment': BioWasteTreatment,
            'bio_waste_treatment_tank': BioWasteTreatment,
            'toxic_incinerator': ToxicIncinerator,
            'coal_oven': CoalOven,
            'crude_oil_refinery': CrudeOilRefinery,
            'landfill_gas_plant': LandfillGasPlant,
            'circuit_board_fab': CircuitBoardFab,
            'motor_assembly': MotorAssembly,
            'battery_fab': BatteryFab,
        }

        # Get building class
        building_class = building_classes.get(building_type)
        if building_class is None:
            logger.warning(f"Unknown building type: {building_type}")
            return None

        try:
            # Create building instance
            building = building_class(grid_x, grid_y)

            # Restore common building state
            building.level = SaveManager._safe_int(building_data.get('level'), 1)
            building.powered = SaveManager._safe_bool(building_data.get('powered'), True)

            # Restore active state (some buildings may not have this attribute)
            if hasattr(building, 'active'):
                building.active = SaveManager._safe_bool(building_data.get('active'), True)

            # Restore health
            if hasattr(building, 'health'):
                building.health = SaveManager._safe_float(building_data.get('health'), 100.0)

            # Restore construction state
            if hasattr(building, 'construction_progress'):
                building.construction_progress = SaveManager._safe_float(
                    building_data.get('construction_progress'), 100.0
                )

            if hasattr(building, 'under_construction'):
                building.under_construction = SaveManager._safe_bool(
                    building_data.get('under_construction'), False
                )

            # Restore building ID if provided
            if 'id' in building_data:
                building.id = building_data['id']

            # Restore additional building-specific data
            extra_data = SaveManager._safe_dict(building_data.get('data'))
            if extra_data:
                SaveManager._restore_building_extra_data(building, extra_data)

            # Apply level bonuses after restoring level
            if hasattr(building, '_apply_level_bonuses'):
                building._apply_level_bonuses()

            logger.debug(
                f"Restored building {building.name} at ({grid_x}, {grid_y}), level {building.level}"
            )
            return building

        except Exception as e:
            logger.error(f"Failed to create building {building_type}: {e}")
            return None

    @staticmethod
    def _restore_building_extra_data(building, data: Dict[str, Any]):
        """
        Restore building-specific extra data.

        Args:
            building: Building instance to restore data to
            data: Dictionary of extra building data
        """
        # Restore stored materials (for Factory, Warehouse, Silo)
        if 'stored_materials' in data and hasattr(building, 'stored_materials'):
            stored = SaveManager._safe_dict(data.get('stored_materials'))
            building.stored_materials = {
                str(k): SaveManager._safe_float(v, 0) for k, v in stored.items()
            }

        # Restore input/output queues (for processing buildings)
        if 'input_queue' in data and hasattr(building, 'input_queue'):
            building.input_queue = SaveManager._safe_list(data.get('input_queue'))

        if 'output_queue' in data and hasattr(building, 'output_queue'):
            building.output_queue = SaveManager._safe_list(data.get('output_queue'))

        # Restore processing state
        if 'processing_current' in data and hasattr(building, 'processing_current'):
            building.processing_current = data.get('processing_current')

        if 'processing_time_remaining' in data and hasattr(building, 'processing_time_remaining'):
            building.processing_time_remaining = SaveManager._safe_float(
                data.get('processing_time_remaining'), 0
            )

        # Restore construction state
        if 'construction_progress' in data and hasattr(building, 'construction_progress'):
            building.construction_progress = SaveManager._safe_float(
                data.get('construction_progress'), 100.0
            )

        if 'under_construction' in data and hasattr(building, 'under_construction'):
            building.under_construction = SaveManager._safe_bool(
                data.get('under_construction'), False
            )

        # Restore health
        if 'health' in data and hasattr(building, 'health'):
            building.health = SaveManager._safe_float(data.get('health'), 100.0)

        # Restore power generation/consumption overrides
        if 'power_generation' in data and hasattr(building, 'power_generation'):
            building.power_generation = SaveManager._safe_float(
                data.get('power_generation'), building.power_generation
            )

        # Restore solar array time state
        if 'current_hour' in data and hasattr(building, 'current_hour'):
            building.current_hour = SaveManager._safe_float(data.get('current_hour'), 12.0)

        # Restore battery bank state
        if 'stored_power' in data and hasattr(building, 'stored_power'):
            building.stored_power = SaveManager._safe_float(data.get('stored_power'), 0)

        # Restore methane generator fuel
        if 'fuel_level' in data and hasattr(building, 'fuel_level'):
            building.fuel_level = SaveManager._safe_float(data.get('fuel_level'), 0)

    @staticmethod
    def _create_robot_from_data(entity_manager, robot_data: Dict[str, Any]):
        """
        Create a robot instance from saved data.

        Args:
            entity_manager: EntityManager to create robot through
            robot_data: Dictionary containing robot state

        Returns:
            Robot instance or None if creation failed
        """
        from src.core.constants import RobotState

        x = SaveManager._safe_float(robot_data.get('x'), 0)
        y = SaveManager._safe_float(robot_data.get('y'), 0)
        autonomous = SaveManager._safe_bool(robot_data.get('autonomous'), True)

        try:
            # Create robot through entity manager
            robot = entity_manager.create_robot(x, y, autonomous=autonomous)

            # Restore robot ID if provided
            if 'id' in robot_data:
                old_id = robot.id
                robot.id = robot_data['id']
                # Update entity manager's reference
                if old_id in entity_manager.entities:
                    del entity_manager.entities[old_id]
                entity_manager.entities[robot.id] = robot

            # Restore speed
            robot.speed = SaveManager._safe_float(robot_data.get('speed'), robot.base_speed)

            # Restore capacity
            robot.max_capacity = SaveManager._safe_float(
                robot_data.get('capacity'), robot.base_capacity
            )

            # Restore battery/power
            if 'battery' in robot_data:
                robot.current_power = SaveManager._safe_float(
                    robot_data.get('battery'), robot.power_capacity
                )

            # Restore health
            if 'current_health' in robot_data:
                robot.current_health = SaveManager._safe_float(
                    robot_data.get('current_health'), robot.max_health
                )

            # Restore upgrade level
            if 'upgrade_level' in robot_data:
                robot.upgrade_level = SaveManager._safe_int(
                    robot_data.get('upgrade_level'), 1
                )

            # Restore inventory
            inventory = SaveManager._safe_dict(robot_data.get('inventory'))
            for material_type, quantity in inventory.items():
                robot.add_material(material_type, SaveManager._safe_float(quantity, 0))

            # Restore state
            state_str = robot_data.get('state', 'IDLE')
            try:
                if hasattr(RobotState, state_str):
                    robot.state = getattr(RobotState, state_str)
                else:
                    robot.state = RobotState.IDLE
            except (ValueError, AttributeError):
                robot.state = RobotState.IDLE

            # Restore target position (for path continuation)
            target_x = robot_data.get('target_x')
            target_y = robot_data.get('target_y')
            if target_x is not None and target_y is not None:
                robot.target_x = SaveManager._safe_float(target_x)
                robot.target_y = SaveManager._safe_float(target_y)

            logger.debug(f"Restored robot at ({x:.0f}, {y:.0f}), level {robot.upgrade_level}")
            return robot

        except Exception as e:
            logger.error(f"Failed to create robot: {e}")
            return None

    @staticmethod
    def deserialize_game_state(game, game_state: Dict[str, Any]) -> bool:
        """
        Restore the game state from a dictionary.

        Args:
            game: The Game object to restore state to
            game_state: Dictionary containing saved game state

        Returns:
            True if successful, False otherwise
        """
        if not isinstance(game_state, dict):
            logger.error("game_state must be a dictionary")
            return False

        try:
            # Restore time with type validation
            time_data = SaveManager._safe_dict(game_state.get("time"))
            game.day = SaveManager._safe_int(time_data.get("day"), 1)
            game.hour = SaveManager._safe_int(time_data.get("hour"), 6)
            game.minute = SaveManager._safe_int(time_data.get("minute"), 0)
            game.time_speed = SaveManager._safe_float(time_data.get("time_speed"), 1.0)
            game.paused = SaveManager._safe_bool(time_data.get("paused"), False)

            # Validate time ranges
            game.day = max(1, game.day)
            game.hour = max(0, min(23, game.hour))
            game.minute = max(0, min(59, game.minute))
            game.time_speed = max(0.1, min(10.0, game.time_speed))

            # Restore resources with type validation
            resources_data = SaveManager._safe_dict(game_state.get("resources"))
            game.resource_manager.money = SaveManager._safe_float(resources_data.get("money"), 10000)
            game.resource_manager.money = max(0, game.resource_manager.money)  # No negative money

            materials = SaveManager._safe_dict(resources_data.get("materials"))
            # Validate materials dict has numeric values
            game.resource_manager.materials = {
                str(k): SaveManager._safe_float(v, 0)
                for k, v in materials.items()
            }

            # Clear existing entities
            game.entity_manager.clear_all()
            game.building_manager.buildings.clear()

            # Restore buildings with validation
            buildings_data = SaveManager._safe_list(game_state.get("buildings"))
            restored_building_count = 0
            for building_data in buildings_data:
                if not isinstance(building_data, dict):
                    logger.warning(f"Skipping invalid building data: {type(building_data)}")
                    continue

                # Create building from saved data
                building = SaveManager._create_building_from_data(building_data)
                if building is None:
                    continue

                # Place building through building manager
                if game.building_manager.place_building(building):
                    restored_building_count += 1
                else:
                    logger.warning(
                        f"Failed to place building {building.name} at "
                        f"({building.grid_x}, {building.grid_y})"
                    )

            logger.info(f"Restored {restored_building_count} buildings")

            # Restore robots with validation
            robots_data = SaveManager._safe_list(game_state.get("robots"))
            restored_robot_count = 0
            for robot_data in robots_data:
                if not isinstance(robot_data, dict):
                    logger.warning(f"Skipping invalid robot data: {type(robot_data)}")
                    continue

                # Create robot from saved data
                robot = SaveManager._create_robot_from_data(game.entity_manager, robot_data)
                if robot is not None:
                    restored_robot_count += 1

            # Apply research effects to restored robots
            if game.research_manager:
                game.entity_manager.apply_research_effects_to_robots(game.research_manager)

            logger.info(f"Restored {restored_robot_count} robots")

            # Restore research with type validation
            research_data = SaveManager._safe_dict(game_state.get("research"))
            completed = SaveManager._safe_list(research_data.get("completed"))
            # Filter to only valid string values
            game.research_manager.completed_research = set(
                str(item) for item in completed if item is not None
            )
            game.research_manager.current_research = research_data.get("current")
            game.research_manager.research_progress = SaveManager._safe_float(
                research_data.get("progress"), 0
            )
            game.research_manager.research_time_required = SaveManager._safe_float(
                research_data.get("time_required"), 0
            )

            # Restore suspicion with validation
            if hasattr(game, 'suspicion_manager'):
                suspicion_data = SaveManager._safe_dict(game_state.get("suspicion"))
                game.suspicion_manager.suspicion_level = SaveManager._safe_float(
                    suspicion_data.get("level"), 0
                )
                game.suspicion_manager.suspicion_level = max(0, min(100,
                    game.suspicion_manager.suspicion_level))
                game.suspicion_manager.suspicion_sources = SaveManager._safe_dict(
                    suspicion_data.get("sources")
                )

            # Restore cameras with validation
            if hasattr(game, 'camera_manager') and game.camera_manager is not None:
                cameras_data = SaveManager._safe_list(game_state.get("cameras"))
                restored_camera_count = 0

                # Build a lookup of saved camera data by ID
                saved_cameras_by_id = {}
                for camera_data in cameras_data:
                    if isinstance(camera_data, dict) and 'id' in camera_data:
                        saved_cameras_by_id[camera_data['id']] = camera_data

                # Restore camera states for existing cameras
                for camera in game.camera_manager.cameras:
                    camera_data = saved_cameras_by_id.get(camera.id)
                    if camera_data is None:
                        continue

                    # Restore camera state
                    from src.entities.security_camera import CameraStatus

                    # Restore active/hacked status
                    is_active = SaveManager._safe_bool(camera_data.get('active'), True)
                    is_hacked = SaveManager._safe_bool(camera_data.get('hacked'), False)

                    if is_hacked:
                        camera.status = CameraStatus.DISABLED
                        camera.disabled_timer = camera.disabled_duration
                    elif not is_active:
                        camera.status = CameraStatus.BROKEN
                    else:
                        camera.status = CameraStatus.ACTIVE

                    # Restore angle if provided
                    if 'angle' in camera_data:
                        camera.facing_angle = SaveManager._safe_float(
                            camera_data.get('angle'), camera.facing_angle
                        )

                    restored_camera_count += 1

                logger.info(f"Restored state for {restored_camera_count} cameras")

            # Restore inspection with validation
            if hasattr(game, 'inspection_manager'):
                inspection_data = SaveManager._safe_dict(game_state.get("inspection"))
                game.inspection_manager.inspection_scheduled = SaveManager._safe_bool(
                    inspection_data.get("scheduled"), False
                )
                game.inspection_manager.inspection_countdown = SaveManager._safe_float(
                    inspection_data.get("countdown"), 0
                )

            # Restore FBI with validation
            if hasattr(game, 'fbi_manager'):
                fbi_data = SaveManager._safe_dict(game_state.get("fbi"))
                game.fbi_manager.investigation_level = SaveManager._safe_int(
                    fbi_data.get("investigation_level"), 0
                )
                game.fbi_manager.investigation_active = SaveManager._safe_bool(
                    fbi_data.get("active"), False
                )

            # Restore weather with validation
            if hasattr(game, 'weather_manager') and game.weather_manager is not None:
                weather_data = SaveManager._safe_dict(game_state.get("weather"))

                if weather_data:
                    from src.systems.weather_manager import WeatherType

                    # Restore current weather type
                    weather_str = weather_data.get('current', 'CLEAR')
                    try:
                        if hasattr(WeatherType, weather_str):
                            game.weather_manager.current_weather = getattr(WeatherType, weather_str)
                        else:
                            game.weather_manager.current_weather = WeatherType.CLEAR
                    except (ValueError, AttributeError):
                        game.weather_manager.current_weather = WeatherType.CLEAR

                    # Restore weather intensity if saved (for backward compatibility)
                    if 'intensity' in weather_data:
                        intensity = SaveManager._safe_float(weather_data.get('intensity'), 0)
                        if hasattr(game.weather_manager, 'weather_intensity'):
                            game.weather_manager.weather_intensity = intensity

                    # Restore transition state if saved
                    if 'transitioning' in weather_data:
                        game.weather_manager.transitioning = SaveManager._safe_bool(
                            weather_data.get('transitioning'), False
                        )

                    if 'transition_elapsed' in weather_data:
                        game.weather_manager.transition_elapsed = SaveManager._safe_float(
                            weather_data.get('transition_elapsed'), 0
                        )

                    if 'next_weather' in weather_data:
                        next_str = weather_data.get('next_weather')
                        if next_str and hasattr(WeatherType, next_str):
                            game.weather_manager.next_weather = getattr(WeatherType, next_str)

                    # Restore duration state
                    if 'weather_duration' in weather_data:
                        game.weather_manager.weather_duration = SaveManager._safe_float(
                            weather_data.get('weather_duration'), 3600
                        )

                    if 'weather_elapsed' in weather_data:
                        game.weather_manager.weather_elapsed = SaveManager._safe_float(
                            weather_data.get('weather_elapsed'), 0
                        )

                    logger.info(
                        f"Restored weather: {game.weather_manager.current_weather.value}"
                    )

            # Restore statistics with validation
            if hasattr(game, 'stats'):
                stats_data = SaveManager._safe_dict(game_state.get("stats"))
                game.stats = {
                    "materials_collected": SaveManager._safe_int(
                        stats_data.get("total_materials_collected"), 0
                    ),
                    "money_earned": SaveManager._safe_float(
                        stats_data.get("total_money_earned"), 0
                    ),
                    "buildings_built": SaveManager._safe_int(
                        stats_data.get("total_buildings_built"), 0
                    ),
                }

            logger.info("Game state restored successfully")
            return True

        except KeyError as e:
            logger.error(f"Missing required key in save data: {e}")
            return False
        except TypeError as e:
            logger.error(f"Invalid data type in save data: {e}")
            return False
        except Exception as e:
            logger.exception(f"Error restoring game state: {e}")
            return False
