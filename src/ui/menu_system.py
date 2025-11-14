"""
Menu System - Manages game menus and UI state.

Handles:
- Menu stack (push/pop menus)
- Menu state tracking
- Input routing to active menu
- Menu transitions
"""

from enum import Enum
from typing import Optional, Dict, List, Callable


class MenuType(Enum):
    """Types of game menus."""
    NONE = "none"
    PAUSE = "pause"
    BUILDING = "building"
    RESEARCH = "research"
    MAP = "map"
    STATISTICS = "statistics"
    SETTINGS = "settings"
    HELP = "help"
    LOAD_GAME = "load_game"
    SAVE_GAME = "save_game"


class Menu:
    """
    Base menu class.

    All menus inherit from this and implement their specific behavior.
    """

    def __init__(self, menu_type: MenuType):
        """Initialize menu."""
        self.menu_type = menu_type
        self.is_active = False
        self.is_visible = True

        # Menu options/buttons
        self.options = []
        self.selected_option = 0

        # Callbacks
        self.on_open = None
        self.on_close = None
        self.on_select = None

    def open(self):
        """Open this menu."""
        self.is_active = True
        self.is_visible = True
        if self.on_open:
            self.on_open()

    def close(self):
        """Close this menu."""
        self.is_active = False
        self.is_visible = False
        if self.on_close:
            self.on_close()

    def handle_input(self, action: str):
        """
        Handle input action.

        Args:
            action: Action string (e.g., "up", "down", "select", "back")
        """
        if action == "up":
            self.selected_option = max(0, self.selected_option - 1)
        elif action == "down":
            self.selected_option = min(len(self.options) - 1, self.selected_option + 1)
        elif action == "select":
            if self.on_select and self.selected_option < len(self.options):
                self.on_select(self.options[self.selected_option])

    def add_option(self, option_name: str, callback: Callable = None):
        """Add menu option."""
        self.options.append({'name': option_name, 'callback': callback})


class PauseMenu(Menu):
    """Pause menu."""

    def __init__(self):
        """Initialize pause menu."""
        super().__init__(MenuType.PAUSE)

        # Add default options
        self.add_option("Resume")
        self.add_option("Settings")
        self.add_option("Save Game")
        self.add_option("Load Game")
        self.add_option("Quit to Menu")


class BuildingMenu(Menu):
    """Building construction menu."""

    def __init__(self):
        """Initialize building menu."""
        super().__init__(MenuType.BUILDING)

        # Building categories
        self.categories = [
            "Power",
            "Processing",
            "Storage",
            "Manufacturing",
            "Advanced",
        ]
        self.current_category = 0
        self.buildings_in_category = {}

    def set_category(self, category_index: int):
        """Set active building category."""
        if 0 <= category_index < len(self.categories):
            self.current_category = category_index

    def get_current_category(self) -> str:
        """Get current category name."""
        return self.categories[self.current_category]


class ResearchMenu(Menu):
    """Research tech tree menu."""

    def __init__(self):
        """Initialize research menu."""
        super().__init__(MenuType.RESEARCH)

        # Research categories
        self.categories = [
            "Robot",
            "Processing",
            "Power",
            "Stealth",
            "Advanced",
        ]
        self.current_category = 0
        self.show_locked = True
        self.show_completed = True


class MapMenu(Menu):
    """Full map overview menu."""

    def __init__(self):
        """Initialize map menu."""
        super().__init__(MenuType.MAP)

        # Map layers
        self.layers = {
            'buildings': True,
            'robots': True,
            'threats': True,
            'control_range': False,
            'fog_of_war': True,
        }

        # Map view
        self.zoom_level = 1.0
        self.center_x = 0
        self.center_y = 0

    def toggle_layer(self, layer_name: str):
        """Toggle map layer visibility."""
        if layer_name in self.layers:
            self.layers[layer_name] = not self.layers[layer_name]
            return self.layers[layer_name]
        return False

    def set_zoom(self, zoom: float):
        """Set map zoom level."""
        self.zoom_level = max(0.25, min(4.0, zoom))


class StatisticsMenu(Menu):
    """Statistics and graphs menu."""

    def __init__(self):
        """Initialize statistics menu."""
        super().__init__(MenuType.STATISTICS)

        # Statistics tabs
        self.tabs = [
            "Production",
            "Financial",
            "Detection",
            "Robots",
            "Research",
        ]
        self.current_tab = 0

    def set_tab(self, tab_index: int):
        """Set active statistics tab."""
        if 0 <= tab_index < len(self.tabs):
            self.current_tab = tab_index


class SettingsMenu(Menu):
    """Settings menu."""

    def __init__(self):
        """Initialize settings menu."""
        super().__init__(MenuType.SETTINGS)

        # Settings tabs
        self.tabs = [
            "Graphics",
            "Audio",
            "Gameplay",
            "Controls",
        ]
        self.current_tab = 0

    def set_tab(self, tab_index: int):
        """Set active settings tab."""
        if 0 <= tab_index < len(self.tabs):
            self.current_tab = tab_index


class MenuSystem:
    """
    Manages all game menus.

    Uses a stack-based system where menus can be pushed and popped.
    The top menu receives input and is rendered.
    """

    def __init__(self):
        """Initialize menu system."""
        # Menu stack
        self.menu_stack: List[Menu] = []

        # Menu instances
        self.menus: Dict[MenuType, Menu] = {
            MenuType.PAUSE: PauseMenu(),
            MenuType.BUILDING: BuildingMenu(),
            MenuType.RESEARCH: ResearchMenu(),
            MenuType.MAP: MapMenu(),
            MenuType.STATISTICS: StatisticsMenu(),
            MenuType.SETTINGS: SettingsMenu(),
        }

        # State
        self.game_paused = False

    def open_menu(self, menu_type: MenuType):
        """
        Open a menu (push onto stack).

        Args:
            menu_type: Type of menu to open
        """
        if menu_type in self.menus:
            menu = self.menus[menu_type]

            # Deactivate current top menu
            if len(self.menu_stack) > 0:
                self.menu_stack[-1].is_active = False

            # Add new menu to stack
            self.menu_stack.append(menu)
            menu.open()

            # Pause game for pause menu
            if menu_type == MenuType.PAUSE:
                self.game_paused = True

            return True
        return False

    def close_current_menu(self):
        """Close the current (top) menu."""
        if len(self.menu_stack) > 0:
            menu = self.menu_stack.pop()
            menu.close()

            # Reactivate previous menu
            if len(self.menu_stack) > 0:
                self.menu_stack[-1].is_active = True
            else:
                # No menus left, unpause game
                self.game_paused = False

            return True
        return False

    def close_all_menus(self):
        """Close all menus."""
        while len(self.menu_stack) > 0:
            self.close_current_menu()

    def get_active_menu(self) -> Optional[Menu]:
        """Get currently active menu."""
        if len(self.menu_stack) > 0:
            return self.menu_stack[-1]
        return None

    def handle_input(self, action: str):
        """
        Route input to active menu.

        Args:
            action: Input action string
        """
        menu = self.get_active_menu()
        if menu:
            menu.handle_input(action)

    def toggle_pause(self):
        """Toggle pause menu."""
        if self.is_menu_open(MenuType.PAUSE):
            self.close_current_menu()
        else:
            self.open_menu(MenuType.PAUSE)

    def is_menu_open(self, menu_type: MenuType) -> bool:
        """Check if a specific menu is open."""
        return menu_type in self.menus and self.menus[menu_type] in self.menu_stack

    def is_any_menu_open(self) -> bool:
        """Check if any menu is open."""
        return len(self.menu_stack) > 0

    def get_menu(self, menu_type: MenuType) -> Optional[Menu]:
        """Get menu instance by type."""
        return self.menus.get(menu_type)

    def get_stats(self) -> Dict:
        """Get menu system statistics."""
        return {
            'menu_stack_depth': len(self.menu_stack),
            'active_menu': self.get_active_menu().menu_type.value if self.get_active_menu() else None,
            'game_paused': self.game_paused,
            'total_menus': len(self.menus),
        }
