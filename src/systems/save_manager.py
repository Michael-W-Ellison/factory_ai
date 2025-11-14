"""
SaveManager - Manages saving and loading game state.

Handles:
- Serializing game state to JSON
- Saving to file
- Loading from file
- Auto-save functionality
- Multiple save slots
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional


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

        # Update current save name
        self.current_save_name = save_name

        # Create save data structure
        save_data = {
            "version": self.SAVE_VERSION,
            "timestamp": datetime.now().isoformat(),
            "save_name": save_name,
            "game_state": game_state
        }

        # Save to file
        file_path = self._get_save_path(save_name)
        try:
            with open(file_path, 'w') as f:
                json.dump(save_data, f, indent=2)
            print(f"Game saved to: {file_path}")
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self, save_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a game state from a file.

        Args:
            save_name: Name of the save file (without extension)

        Returns:
            Game state dictionary if successful, None otherwise
        """
        file_path = self._get_save_path(save_name)

        if not os.path.exists(file_path):
            print(f"Save file not found: {file_path}")
            return None

        try:
            with open(file_path, 'r') as f:
                save_data = json.load(f)

            # Validate save version
            if save_data.get("version") != self.SAVE_VERSION:
                print(f"Warning: Save file version mismatch. Expected {self.SAVE_VERSION}, got {save_data.get('version')}")
                # Could implement version migration here

            # Update current save name
            self.current_save_name = save_name

            print(f"Game loaded from: {file_path}")
            print(f"Save timestamp: {save_data.get('timestamp')}")

            return save_data.get("game_state")

        except Exception as e:
            print(f"Error loading game: {e}")
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
                print(f"Auto-save completed at day {current_day}")
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
                    with open(file_path, 'r') as f:
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
                    print(f"Error reading save file {filename}: {e}")

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
        file_path = self._get_save_path(save_name)

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Deleted save: {save_name}")
                return True
            except Exception as e:
                print(f"Error deleting save: {e}")
                return False
        else:
            print(f"Save file not found: {save_name}")
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
                    "type": building.building_type.name,
                    "x": building.x,
                    "y": building.y,
                    "level": building.level,
                    "powered": building.powered,
                    "active": building.active,
                    # Add building-specific data if available
                    "data": building.to_dict() if hasattr(building, 'to_dict') else {}
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
                    "capacity": robot.capacity,
                    "battery": robot.battery if hasattr(robot, 'battery') else 100,
                    "inventory": robot.inventory.copy() if hasattr(robot, 'inventory') else {},
                    "state": robot.state.name if hasattr(robot.state, 'name') else str(robot.state),
                    "target_x": robot.target_x if hasattr(robot, 'target_x') else None,
                    "target_y": robot.target_y if hasattr(robot, 'target_y') else None
                }
                for robot in game.entity_manager.get_entities_by_type("robot")
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
            "weather": {
                "current": game.weather_manager.current_weather.name if hasattr(game, 'weather_manager') else "CLEAR",
                "intensity": game.weather_manager.weather_intensity if hasattr(game, 'weather_manager') else 0
            },

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
    def deserialize_game_state(game, game_state: Dict[str, Any]) -> bool:
        """
        Restore the game state from a dictionary.

        Args:
            game: The Game object to restore state to
            game_state: Dictionary containing saved game state

        Returns:
            True if successful, False otherwise
        """
        try:
            # Restore time
            time_data = game_state.get("time", {})
            game.day = time_data.get("day", 1)
            game.hour = time_data.get("hour", 6)
            game.minute = time_data.get("minute", 0)
            game.time_speed = time_data.get("time_speed", 1)
            game.paused = time_data.get("paused", False)

            # Restore resources
            resources_data = game_state.get("resources", {})
            game.resource_manager.money = resources_data.get("money", 10000)
            game.resource_manager.materials = resources_data.get("materials", {}).copy()

            # Clear existing entities
            game.entity_manager.clear_all()
            game.building_manager.buildings.clear()

            # Restore buildings
            for building_data in game_state.get("buildings", []):
                # This would need to call building_manager.create_building() with proper parameters
                # Implementation depends on your building creation system
                pass

            # Restore robots
            for robot_data in game_state.get("robots", []):
                # This would need to call entity_manager.create_robot() with proper parameters
                # Implementation depends on your robot creation system
                pass

            # Restore research
            research_data = game_state.get("research", {})
            game.research_manager.completed_research = set(research_data.get("completed", []))
            game.research_manager.current_research = research_data.get("current")
            game.research_manager.research_progress = research_data.get("progress", 0)
            game.research_manager.research_time_required = research_data.get("time_required", 0)

            # Restore suspicion
            if hasattr(game, 'suspicion_manager'):
                suspicion_data = game_state.get("suspicion", {})
                game.suspicion_manager.suspicion_level = suspicion_data.get("level", 0)
                game.suspicion_manager.suspicion_sources = suspicion_data.get("sources", {}).copy()

            # Restore cameras
            if hasattr(game, 'camera_manager'):
                for camera_data in game_state.get("cameras", []):
                    # Restore camera states
                    pass

            # Restore inspection
            if hasattr(game, 'inspection_manager'):
                inspection_data = game_state.get("inspection", {})
                game.inspection_manager.inspection_scheduled = inspection_data.get("scheduled", False)
                game.inspection_manager.inspection_countdown = inspection_data.get("countdown", 0)

            # Restore FBI
            if hasattr(game, 'fbi_manager'):
                fbi_data = game_state.get("fbi", {})
                game.fbi_manager.investigation_level = fbi_data.get("investigation_level", 0)
                game.fbi_manager.investigation_active = fbi_data.get("active", False)

            # Restore weather
            if hasattr(game, 'weather_manager'):
                weather_data = game_state.get("weather", {})
                # This would need to set weather state properly
                pass

            # Restore statistics
            if hasattr(game, 'stats'):
                game.stats = game_state.get("stats", {}).copy()

            print("Game state restored successfully")
            return True

        except Exception as e:
            print(f"Error restoring game state: {e}")
            import traceback
            traceback.print_exc()
            return False
