"""
Settings Manager - Manages game settings and configuration.

Handles:
- Graphics settings (resolution, fullscreen, vsync, FPS)
- Audio settings (master, music, SFX volumes)
- Gameplay settings (speed, auto-save, difficulty)
- Controls settings (key bindings, mouse sensitivity)
- Save/load settings from file
"""

import json
import os
from typing import Dict, Any, Optional


class SettingsManager:
    """
    Manages all game settings.

    Settings are organized into categories and can be saved/loaded from JSON.
    """

    def __init__(self, settings_file: str = "settings.json"):
        """
        Initialize settings manager.

        Args:
            settings_file: Path to settings file
        """
        self.settings_file = settings_file

        # Default settings
        self.settings = {
            'graphics': {
                'resolution_width': 1280,
                'resolution_height': 720,
                'fullscreen': False,
                'vsync': True,
                'show_fps': False,
                'particle_quality': 'high',  # low, medium, high
            },
            'audio': {
                'master_volume': 1.0,
                'music_volume': 0.7,
                'sfx_volume': 0.8,
                'mute': False,
            },
            'gameplay': {
                'game_speed': 1.0,
                'auto_save_interval': 300,  # seconds
                'difficulty': 'normal',  # easy, normal, hard, insane
                'tutorial_enabled': True,
                'edge_scrolling': True,
                'pause_on_notification': False,
            },
            'controls': {
                'mouse_sensitivity': 1.0,
                'scroll_speed': 1.0,
                'key_bindings': {
                    'move_up': 'W',
                    'move_down': 'S',
                    'move_left': 'A',
                    'move_right': 'D',
                    'pause': 'ESC',
                    'building_menu': 'B',
                    'research_menu': 'R',
                    'map_menu': 'M',
                    'stats_menu': 'T',
                    'help_menu': 'F1',
                    'quick_save': 'F5',
                    'quick_load': 'F9',
                },
            },
        }

        # Settings constraints
        self.constraints = {
            'graphics': {
                'resolution_width': (800, 3840),
                'resolution_height': (600, 2160),
                'particle_quality': ['low', 'medium', 'high'],
            },
            'audio': {
                'master_volume': (0.0, 1.0),
                'music_volume': (0.0, 1.0),
                'sfx_volume': (0.0, 1.0),
            },
            'gameplay': {
                'game_speed': (0.5, 4.0),
                'auto_save_interval': (60, 3600),
                'difficulty': ['easy', 'normal', 'hard', 'insane'],
            },
            'controls': {
                'mouse_sensitivity': (0.1, 3.0),
                'scroll_speed': (0.1, 3.0),
            },
        }

        # Attempt to load settings from file
        self.load_settings()

    def get(self, category: str, key: str, default: Any = None) -> Any:
        """
        Get a setting value.

        Args:
            category: Settings category (e.g., 'graphics')
            key: Setting key
            default: Default value if not found

        Returns:
            Setting value or default
        """
        if category in self.settings and key in self.settings[category]:
            return self.settings[category][key]
        return default

    def set(self, category: str, key: str, value: Any) -> bool:
        """
        Set a setting value.

        Args:
            category: Settings category
            key: Setting key
            value: New value

        Returns:
            bool: True if successfully set, False if invalid
        """
        # Validate category exists
        if category not in self.settings:
            return False

        # Validate constraints
        if not self._validate_value(category, key, value):
            return False

        # Set value
        self.settings[category][key] = value
        return True

    def _validate_value(self, category: str, key: str, value: Any) -> bool:
        """Validate a setting value against constraints."""
        if category not in self.constraints:
            return True  # No constraints for this category

        if key not in self.constraints[category]:
            return True  # No constraints for this key

        constraint = self.constraints[category][key]

        # Check tuple constraint (min, max)
        if isinstance(constraint, tuple) and len(constraint) == 2:
            min_val, max_val = constraint
            return min_val <= value <= max_val

        # Check list constraint (allowed values)
        elif isinstance(constraint, list):
            return value in constraint

        return True

    def get_resolution(self) -> tuple:
        """Get current resolution."""
        width = self.get('graphics', 'resolution_width', 1280)
        height = self.get('graphics', 'resolution_height', 720)
        return (width, height)

    def set_resolution(self, width: int, height: int) -> bool:
        """Set resolution."""
        success = self.set('graphics', 'resolution_width', width)
        success = self.set('graphics', 'resolution_height', height) and success
        return success

    def is_fullscreen(self) -> bool:
        """Check if fullscreen is enabled."""
        return self.get('graphics', 'fullscreen', False)

    def toggle_fullscreen(self) -> bool:
        """Toggle fullscreen mode."""
        current = self.is_fullscreen()
        self.set('graphics', 'fullscreen', not current)
        return not current

    def get_volume(self, volume_type: str = 'master') -> float:
        """Get volume level (0.0 to 1.0)."""
        return self.get('audio', f'{volume_type}_volume', 1.0)

    def set_volume(self, volume_type: str, level: float) -> bool:
        """Set volume level."""
        return self.set('audio', f'{volume_type}_volume', level)

    def is_muted(self) -> bool:
        """Check if audio is muted."""
        return self.get('audio', 'mute', False)

    def toggle_mute(self) -> bool:
        """Toggle mute."""
        current = self.is_muted()
        self.set('audio', 'mute', not current)
        return not current

    def get_difficulty(self) -> str:
        """Get current difficulty."""
        return self.get('gameplay', 'difficulty', 'normal')

    def set_difficulty(self, difficulty: str) -> bool:
        """Set difficulty."""
        return self.set('gameplay', 'difficulty', difficulty)

    def get_key_binding(self, action: str) -> Optional[str]:
        """Get key binding for action."""
        bindings = self.get('controls', 'key_bindings', {})
        return bindings.get(action)

    def set_key_binding(self, action: str, key: str) -> bool:
        """Set key binding for action."""
        bindings = self.get('controls', 'key_bindings', {})
        if action in bindings:
            bindings[action] = key
            self.set('controls', 'key_bindings', bindings)
            return True
        return False

    def reset_to_defaults(self, category: Optional[str] = None):
        """
        Reset settings to defaults.

        Args:
            category: Specific category to reset, or None for all
        """
        if category is None:
            # Reset all categories
            self.__init__(self.settings_file)
        elif category in self.settings:
            # Reset specific category
            default_settings = SettingsManager(self.settings_file)
            self.settings[category] = default_settings.settings[category]

    def save_settings(self, file_path: Optional[str] = None) -> bool:
        """
        Save settings to file.

        Args:
            file_path: Optional custom file path

        Returns:
            bool: True if successful
        """
        target_file = file_path or self.settings_file

        try:
            with open(target_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def load_settings(self, file_path: Optional[str] = None) -> bool:
        """
        Load settings from file.

        Args:
            file_path: Optional custom file path

        Returns:
            bool: True if successful
        """
        target_file = file_path or self.settings_file

        if not os.path.exists(target_file):
            return False

        try:
            with open(target_file, 'r') as f:
                loaded_settings = json.load(f)

            # Merge loaded settings with defaults (preserves new default settings)
            for category, settings in loaded_settings.items():
                if category in self.settings:
                    for key, value in settings.items():
                        if self._validate_value(category, key, value):
                            self.settings[category][key] = value

            return True
        except Exception as e:
            print(f"Error loading settings: {e}")
            return False

    def get_all_settings(self) -> Dict:
        """Get all settings as dictionary."""
        return self.settings.copy()

    def get_category_settings(self, category: str) -> Dict:
        """Get all settings in a category."""
        return self.settings.get(category, {}).copy()

    def get_stats(self) -> Dict:
        """Get settings manager statistics."""
        return {
            'settings_file': self.settings_file,
            'categories': list(self.settings.keys()),
            'total_settings': sum(len(cat) for cat in self.settings.values()),
            'resolution': self.get_resolution(),
            'fullscreen': self.is_fullscreen(),
            'difficulty': self.get_difficulty(),
            'muted': self.is_muted(),
        }
