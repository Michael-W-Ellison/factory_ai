"""
Settings UI - Complete settings menu with tabs for Audio, Graphics, Controls, Gameplay.

Provides interactive UI elements:
- Sliders for volume and speed settings
- Toggles for boolean options
- Dropdowns for selection options
- Key capture for control remapping
"""

import pygame
from typing import Dict, List, Optional, Tuple, Callable, Any
from enum import Enum


class SettingsTab(Enum):
    """Settings menu tabs."""
    AUDIO = 0
    GRAPHICS = 1
    CONTROLS = 2
    GAMEPLAY = 3


class UIWidget:
    """Base class for UI widgets."""

    def __init__(self, x: int, y: int, width: int, height: int, label: str):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.focused = False
        self.hovered = False

    def handle_event(self, event: pygame.event.Event, mouse_pos: Tuple[int, int]) -> bool:
        """Handle input event. Returns True if value changed."""
        return False

    def render(self, surface: pygame.Surface, fonts: Dict):
        """Render the widget."""
        pass

    def get_rect(self) -> pygame.Rect:
        """Get widget bounding rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update_hover(self, mouse_pos: Tuple[int, int]):
        """Update hover state."""
        self.hovered = self.get_rect().collidepoint(mouse_pos)


class Slider(UIWidget):
    """Slider widget for numeric values."""

    def __init__(self, x: int, y: int, width: int, label: str,
                 min_val: float, max_val: float, value: float,
                 on_change: Callable[[float], None] = None,
                 format_func: Callable[[float], str] = None):
        super().__init__(x, y, width, 30, label)
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.on_change = on_change
        self.format_func = format_func or (lambda v: f"{v:.0%}" if max_val <= 1 else f"{v:.1f}")
        self.dragging = False

        # Slider track dimensions
        self.track_height = 8
        self.handle_radius = 10

    def handle_event(self, event: pygame.event.Event, mouse_pos: Tuple[int, int]) -> bool:
        local_x = mouse_pos[0] - self.x
        local_y = mouse_pos[1] - self.y

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if click is on slider track area
            track_y = self.height // 2
            if (0 <= local_x <= self.width and
                abs(local_y - track_y) <= self.handle_radius + 5):
                self.dragging = True
                self._update_value_from_pos(local_x)
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._update_value_from_pos(local_x)
                return True

        return False

    def _update_value_from_pos(self, local_x: int):
        """Update value based on mouse position."""
        # Clamp to track bounds
        padding = self.handle_radius
        track_width = self.width - 2 * padding
        relative_x = max(0, min(track_width, local_x - padding))

        # Calculate value
        ratio = relative_x / track_width
        new_value = self.min_val + ratio * (self.max_val - self.min_val)

        if new_value != self.value:
            self.value = new_value
            if self.on_change:
                self.on_change(self.value)

    def render(self, surface: pygame.Surface, fonts: Dict):
        # Colors
        track_color = (60, 60, 80)
        fill_color = (100, 150, 255)
        handle_color = (150, 200, 255) if self.hovered or self.dragging else (120, 170, 230)
        text_color = (220, 220, 220)

        # Calculate positions
        padding = self.handle_radius
        track_width = self.width - 2 * padding
        track_y = self.y + self.height // 2
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.x + padding + int(ratio * track_width)

        # Draw track background
        track_rect = pygame.Rect(self.x + padding, track_y - self.track_height // 2,
                                  track_width, self.track_height)
        pygame.draw.rect(surface, track_color, track_rect, border_radius=4)

        # Draw filled portion
        fill_width = int(ratio * track_width)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.x + padding, track_y - self.track_height // 2,
                                     fill_width, self.track_height)
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=4)

        # Draw handle
        pygame.draw.circle(surface, handle_color, (handle_x, track_y), self.handle_radius)
        pygame.draw.circle(surface, (255, 255, 255), (handle_x, track_y), self.handle_radius, 2)

        # Draw value text
        value_text = fonts['small'].render(self.format_func(self.value), True, text_color)
        value_rect = value_text.get_rect(midleft=(self.x + self.width + 10, track_y))
        surface.blit(value_text, value_rect)


class Toggle(UIWidget):
    """Toggle switch widget for boolean values."""

    def __init__(self, x: int, y: int, label: str, value: bool,
                 on_change: Callable[[bool], None] = None):
        super().__init__(x, y, 50, 26, label)
        self.value = value
        self.on_change = on_change

    def handle_event(self, event: pygame.event.Event, mouse_pos: Tuple[int, int]) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.get_rect().collidepoint(mouse_pos):
                self.value = not self.value
                if self.on_change:
                    self.on_change(self.value)
                return True
        return False

    def render(self, surface: pygame.Surface, fonts: Dict):
        # Colors
        bg_off = (60, 60, 80)
        bg_on = (80, 160, 80)
        handle_color = (255, 255, 255)

        # Draw track
        bg_color = bg_on if self.value else bg_off
        track_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, bg_color, track_rect, border_radius=13)

        # Draw border on hover
        if self.hovered:
            pygame.draw.rect(surface, (150, 200, 255), track_rect, 2, border_radius=13)

        # Draw handle
        handle_radius = self.height // 2 - 3
        handle_x = self.x + self.width - handle_radius - 5 if self.value else self.x + handle_radius + 5
        handle_y = self.y + self.height // 2
        pygame.draw.circle(surface, handle_color, (handle_x, handle_y), handle_radius)


class Dropdown(UIWidget):
    """Dropdown selection widget."""

    def __init__(self, x: int, y: int, width: int, label: str,
                 options: List[str], selected_index: int,
                 on_change: Callable[[int, str], None] = None):
        super().__init__(x, y, width, 30, label)
        self.options = options
        self.selected_index = selected_index
        self.on_change = on_change
        self.expanded = False
        self.hover_index = -1

    def handle_event(self, event: pygame.event.Event, mouse_pos: Tuple[int, int]) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            main_rect = self.get_rect()

            if self.expanded:
                # Check option clicks
                for i, option in enumerate(self.options):
                    option_rect = pygame.Rect(self.x, self.y + self.height + i * 28, self.width, 28)
                    if option_rect.collidepoint(mouse_pos):
                        self.selected_index = i
                        self.expanded = False
                        if self.on_change:
                            self.on_change(i, self.options[i])
                        return True
                # Click outside closes dropdown
                self.expanded = False
                return True
            elif main_rect.collidepoint(mouse_pos):
                self.expanded = not self.expanded
                return True

        elif event.type == pygame.MOUSEMOTION and self.expanded:
            # Update hover index
            for i in range(len(self.options)):
                option_rect = pygame.Rect(self.x, self.y + self.height + i * 28, self.width, 28)
                if option_rect.collidepoint(mouse_pos):
                    self.hover_index = i
                    break
            else:
                self.hover_index = -1

        return False

    def render(self, surface: pygame.Surface, fonts: Dict):
        # Colors
        bg_color = (50, 50, 70)
        border_color = (100, 150, 255) if self.hovered or self.expanded else (80, 80, 100)
        text_color = (220, 220, 220)
        hover_bg = (70, 70, 100)

        # Main dropdown box
        main_rect = self.get_rect()
        pygame.draw.rect(surface, bg_color, main_rect)
        pygame.draw.rect(surface, border_color, main_rect, 2)

        # Selected text
        if 0 <= self.selected_index < len(self.options):
            text = fonts['small'].render(self.options[self.selected_index], True, text_color)
            surface.blit(text, (self.x + 10, self.y + 6))

        # Arrow
        arrow = "▼" if not self.expanded else "▲"
        arrow_text = fonts['small'].render(arrow, True, text_color)
        surface.blit(arrow_text, (self.x + self.width - 25, self.y + 6))

        # Dropdown options
        if self.expanded:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.x, self.y + self.height + i * 28, self.width, 28)
                option_bg = hover_bg if i == self.hover_index else bg_color
                pygame.draw.rect(surface, option_bg, option_rect)
                pygame.draw.rect(surface, border_color, option_rect, 1)

                option_text = fonts['small'].render(option, True, text_color)
                surface.blit(option_text, (option_rect.x + 10, option_rect.y + 5))


class KeyCapture(UIWidget):
    """Key capture widget for control remapping."""

    def __init__(self, x: int, y: int, width: int, label: str,
                 action: str, current_key: str,
                 on_change: Callable[[str, str], None] = None):
        super().__init__(x, y, width, 30, label)
        self.action = action
        self.current_key = current_key
        self.on_change = on_change
        self.capturing = False

    def handle_event(self, event: pygame.event.Event, mouse_pos: Tuple[int, int]) -> bool:
        if self.capturing:
            if event.type == pygame.KEYDOWN:
                # Escape cancels capture
                if event.key == pygame.K_ESCAPE:
                    self.capturing = False
                    return True

                # Get key name
                key_name = pygame.key.name(event.key).upper()
                if key_name:
                    self.current_key = key_name
                    self.capturing = False
                    if self.on_change:
                        self.on_change(self.action, key_name)
                    return True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.get_rect().collidepoint(mouse_pos):
                self.capturing = True
                return True

        return False

    def render(self, surface: pygame.Surface, fonts: Dict):
        # Colors
        bg_color = (50, 50, 70)
        capture_color = (100, 80, 60)
        border_color = (255, 200, 100) if self.capturing else (
            (100, 150, 255) if self.hovered else (80, 80, 100))
        text_color = (220, 220, 220)

        # Button background
        rect = self.get_rect()
        bg = capture_color if self.capturing else bg_color
        pygame.draw.rect(surface, bg, rect)
        pygame.draw.rect(surface, border_color, rect, 2)

        # Text
        if self.capturing:
            display_text = "Press a key..."
        else:
            display_text = self.current_key
        text = fonts['small'].render(display_text, True, text_color)
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)


class SettingsUI:
    """
    Complete settings menu UI.

    Provides tabbed interface for:
    - Audio settings (volume sliders)
    - Graphics settings (resolution, fullscreen, vsync)
    - Controls settings (key remapping)
    - Gameplay settings (difficulty, speed)
    """

    def __init__(self, screen_width: int, screen_height: int, settings_manager, audio_manager=None):
        """
        Initialize settings UI.

        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            settings_manager: SettingsManager instance
            audio_manager: Optional AudioManager for live volume control
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.settings = settings_manager
        self.audio = audio_manager

        # Visibility
        self.visible = False

        # Panel dimensions
        self.panel_width = 900
        self.panel_height = 600
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2

        # Fonts
        self.fonts = {
            'title': pygame.font.Font(None, 48),
            'tab': pygame.font.Font(None, 28),
            'label': pygame.font.Font(None, 24),
            'small': pygame.font.Font(None, 22),
        }

        # Colors
        self.colors = {
            'bg': (25, 25, 35),
            'panel': (35, 35, 50),
            'tab_active': (60, 60, 90),
            'tab_inactive': (40, 40, 55),
            'tab_hover': (50, 50, 70),
            'border': (80, 120, 200),
            'text': (220, 220, 220),
            'text_dim': (150, 150, 150),
            'highlight': (100, 150, 255),
        }

        # Tab state
        self.current_tab = SettingsTab.AUDIO
        self.tab_rects: Dict[SettingsTab, pygame.Rect] = {}

        # Widgets by tab
        self.widgets: Dict[SettingsTab, List[UIWidget]] = {
            SettingsTab.AUDIO: [],
            SettingsTab.GRAPHICS: [],
            SettingsTab.CONTROLS: [],
            SettingsTab.GAMEPLAY: [],
        }

        # Initialize widgets
        self._create_audio_widgets()
        self._create_graphics_widgets()
        self._create_controls_widgets()
        self._create_gameplay_widgets()

        # Button rects
        self.apply_rect = None
        self.reset_rect = None
        self.close_rect = None

        # Pending changes flag
        self.has_changes = False

    def _create_audio_widgets(self):
        """Create audio settings widgets."""
        content_x = self.panel_x + 200
        content_y = self.panel_y + 120
        slider_width = 300

        # Master Volume
        self.widgets[SettingsTab.AUDIO].append(
            Slider(content_x, content_y, slider_width, "Master Volume",
                   0.0, 1.0, self.settings.get('audio', 'master_volume', 1.0),
                   on_change=lambda v: self._on_setting_change('audio', 'master_volume', v))
        )

        # Music Volume
        self.widgets[SettingsTab.AUDIO].append(
            Slider(content_x, content_y + 70, slider_width, "Music Volume",
                   0.0, 1.0, self.settings.get('audio', 'music_volume', 0.7),
                   on_change=lambda v: self._on_setting_change('audio', 'music_volume', v))
        )

        # SFX Volume
        self.widgets[SettingsTab.AUDIO].append(
            Slider(content_x, content_y + 140, slider_width, "SFX Volume",
                   0.0, 1.0, self.settings.get('audio', 'sfx_volume', 0.8),
                   on_change=lambda v: self._on_setting_change('audio', 'sfx_volume', v))
        )

        # Mute Toggle
        self.widgets[SettingsTab.AUDIO].append(
            Toggle(content_x, content_y + 210, "Mute All",
                   self.settings.get('audio', 'mute', False),
                   on_change=lambda v: self._on_setting_change('audio', 'mute', v))
        )

    def _create_graphics_widgets(self):
        """Create graphics settings widgets."""
        content_x = self.panel_x + 200
        content_y = self.panel_y + 120

        # Resolution dropdown
        resolutions = ["1280x720", "1600x900", "1920x1080", "2560x1440", "3840x2160"]
        current_res = f"{self.settings.get('graphics', 'resolution_width', 1280)}x{self.settings.get('graphics', 'resolution_height', 720)}"
        try:
            res_index = resolutions.index(current_res)
        except ValueError:
            res_index = 0

        self.widgets[SettingsTab.GRAPHICS].append(
            Dropdown(content_x, content_y, 200, "Resolution",
                     resolutions, res_index,
                     on_change=self._on_resolution_change)
        )

        # Fullscreen toggle
        self.widgets[SettingsTab.GRAPHICS].append(
            Toggle(content_x, content_y + 70, "Fullscreen",
                   self.settings.get('graphics', 'fullscreen', False),
                   on_change=lambda v: self._on_setting_change('graphics', 'fullscreen', v))
        )

        # VSync toggle
        self.widgets[SettingsTab.GRAPHICS].append(
            Toggle(content_x, content_y + 120, "VSync",
                   self.settings.get('graphics', 'vsync', True),
                   on_change=lambda v: self._on_setting_change('graphics', 'vsync', v))
        )

        # Show FPS toggle
        self.widgets[SettingsTab.GRAPHICS].append(
            Toggle(content_x, content_y + 170, "Show FPS",
                   self.settings.get('graphics', 'show_fps', False),
                   on_change=lambda v: self._on_setting_change('graphics', 'show_fps', v))
        )

        # Particle Quality dropdown
        qualities = ["Low", "Medium", "High"]
        current_quality = self.settings.get('graphics', 'particle_quality', 'high')
        quality_index = {'low': 0, 'medium': 1, 'high': 2}.get(current_quality, 2)

        self.widgets[SettingsTab.GRAPHICS].append(
            Dropdown(content_x, content_y + 220, 150, "Particle Quality",
                     qualities, quality_index,
                     on_change=lambda i, v: self._on_setting_change('graphics', 'particle_quality', v.lower()))
        )

    def _create_controls_widgets(self):
        """Create controls settings widgets."""
        content_x = self.panel_x + 200
        content_y = self.panel_y + 120

        # Key bindings
        key_bindings = self.settings.get('controls', 'key_bindings', {})

        binding_configs = [
            ('camera_up', 'Pan Up'),
            ('camera_down', 'Pan Down'),
            ('camera_left', 'Pan Left'),
            ('camera_right', 'Pan Right'),
            ('pause', 'Pause'),
            ('speed_up', 'Speed Up'),
            ('speed_down', 'Speed Down'),
            ('building_menu', 'Building Menu'),
            ('research_menu', 'Research Menu'),
            ('map_menu', 'Map/Minimap'),
            ('settings_menu', 'Settings'),
            ('help_menu', 'Help'),
            ('quick_save', 'Quick Save'),
            ('quick_load', 'Quick Load'),
        ]

        for i, (action, display_name) in enumerate(binding_configs):
            current_key = key_bindings.get(action, 'NONE')
            row = i % 6
            col = i // 6
            x = content_x + col * 320
            y = content_y + row * 50

            self.widgets[SettingsTab.CONTROLS].append(
                KeyCapture(x, y, 100, display_name, action, current_key,
                           on_change=self._on_key_change)
            )

        # Mouse sensitivity slider
        self.widgets[SettingsTab.CONTROLS].append(
            Slider(content_x, content_y + 320, 250, "Mouse Sensitivity",
                   0.1, 3.0, self.settings.get('controls', 'mouse_sensitivity', 1.0),
                   on_change=lambda v: self._on_setting_change('controls', 'mouse_sensitivity', v),
                   format_func=lambda v: f"{v:.1f}x")
        )

        # Camera/scroll speed slider
        self.widgets[SettingsTab.CONTROLS].append(
            Slider(content_x, content_y + 370, 250, "Camera Speed",
                   0.1, 3.0, self.settings.get('controls', 'scroll_speed', 1.0),
                   on_change=lambda v: self._on_setting_change('controls', 'scroll_speed', v),
                   format_func=lambda v: f"{v:.1f}x")
        )

    def _create_gameplay_widgets(self):
        """Create gameplay settings widgets."""
        content_x = self.panel_x + 200
        content_y = self.panel_y + 120

        # Difficulty dropdown
        difficulties = ["Easy", "Normal", "Hard", "Insane"]
        current_diff = self.settings.get('gameplay', 'difficulty', 'normal')
        diff_index = {'easy': 0, 'normal': 1, 'hard': 2, 'insane': 3}.get(current_diff, 1)

        self.widgets[SettingsTab.GAMEPLAY].append(
            Dropdown(content_x, content_y, 150, "Difficulty",
                     difficulties, diff_index,
                     on_change=lambda i, v: self._on_setting_change('gameplay', 'difficulty', v.lower()))
        )

        # Game Speed slider
        self.widgets[SettingsTab.GAMEPLAY].append(
            Slider(content_x, content_y + 70, 250, "Game Speed",
                   0.5, 4.0, self.settings.get('gameplay', 'game_speed', 1.0),
                   on_change=lambda v: self._on_setting_change('gameplay', 'game_speed', v),
                   format_func=lambda v: f"{v:.1f}x")
        )

        # Auto-save interval slider
        self.widgets[SettingsTab.GAMEPLAY].append(
            Slider(content_x, content_y + 140, 250, "Auto-save Interval",
                   60, 600, self.settings.get('gameplay', 'auto_save_interval', 300),
                   on_change=lambda v: self._on_setting_change('gameplay', 'auto_save_interval', int(v)),
                   format_func=lambda v: f"{int(v)}s")
        )

        # Tutorial toggle
        self.widgets[SettingsTab.GAMEPLAY].append(
            Toggle(content_x, content_y + 210, "Tutorial Enabled",
                   self.settings.get('gameplay', 'tutorial_enabled', True),
                   on_change=lambda v: self._on_setting_change('gameplay', 'tutorial_enabled', v))
        )

        # Edge scrolling toggle
        self.widgets[SettingsTab.GAMEPLAY].append(
            Toggle(content_x, content_y + 260, "Edge Scrolling",
                   self.settings.get('gameplay', 'edge_scrolling', True),
                   on_change=lambda v: self._on_setting_change('gameplay', 'edge_scrolling', v))
        )

        # Pause on notification toggle
        self.widgets[SettingsTab.GAMEPLAY].append(
            Toggle(content_x, content_y + 310, "Pause on Notification",
                   self.settings.get('gameplay', 'pause_on_notification', False),
                   on_change=lambda v: self._on_setting_change('gameplay', 'pause_on_notification', v))
        )

    def _on_setting_change(self, category: str, key: str, value: Any):
        """Handle setting value change."""
        self.settings.set(category, key, value)
        self.has_changes = True

        # Apply audio changes in real-time
        if category == 'audio' and self.audio:
            if key == 'master_volume':
                self.audio.set_master_volume(value)
            elif key == 'music_volume':
                self.audio.set_music_volume(value)
            elif key == 'sfx_volume':
                self.audio.set_sfx_volume(value)
            elif key == 'mute':
                self.audio.set_muted(value)

    def _on_resolution_change(self, index: int, resolution: str):
        """Handle resolution change."""
        width, height = map(int, resolution.split('x'))
        self.settings.set('graphics', 'resolution_width', width)
        self.settings.set('graphics', 'resolution_height', height)
        self.has_changes = True

    def _on_key_change(self, action: str, key: str):
        """Handle key binding change."""
        self.settings.set_key_binding(action, key)
        self.has_changes = True

    def toggle(self):
        """Toggle settings UI visibility."""
        self.visible = not self.visible
        if self.visible:
            self._refresh_widgets()

    def show(self):
        """Show settings UI."""
        self.visible = True
        self._refresh_widgets()

    def hide(self):
        """Hide settings UI."""
        self.visible = False

    def _refresh_widgets(self):
        """Refresh widget values from settings."""
        # Recreate all widgets with current settings values
        self.widgets = {
            SettingsTab.AUDIO: [],
            SettingsTab.GRAPHICS: [],
            SettingsTab.CONTROLS: [],
            SettingsTab.GAMEPLAY: [],
        }
        self._create_audio_widgets()
        self._create_graphics_widgets()
        self._create_controls_widgets()
        self._create_gameplay_widgets()
        self.has_changes = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input event.

        Args:
            event: Pygame event

        Returns:
            True if event was handled
        """
        if not self.visible:
            return False

        mouse_pos = pygame.mouse.get_pos()

        # Check for key capture in controls tab
        if self.current_tab == SettingsTab.CONTROLS:
            for widget in self.widgets[SettingsTab.CONTROLS]:
                if isinstance(widget, KeyCapture) and widget.capturing:
                    if widget.handle_event(event, mouse_pos):
                        return True

        # ESC to close (if not capturing a key)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            capturing = any(
                isinstance(w, KeyCapture) and w.capturing
                for w in self.widgets[SettingsTab.CONTROLS]
            )
            if not capturing:
                self.hide()
                return True

        # Mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check tab clicks
            for tab, rect in self.tab_rects.items():
                if rect.collidepoint(mouse_pos):
                    self.current_tab = tab
                    return True

            # Check button clicks
            if self.apply_rect and self.apply_rect.collidepoint(mouse_pos):
                self._apply_settings()
                return True
            if self.reset_rect and self.reset_rect.collidepoint(mouse_pos):
                self._reset_settings()
                return True
            if self.close_rect and self.close_rect.collidepoint(mouse_pos):
                self.hide()
                return True

        # Pass event to current tab's widgets
        for widget in self.widgets[self.current_tab]:
            if widget.handle_event(event, mouse_pos):
                return True

        # Consume all events while visible
        return True

    def _apply_settings(self):
        """Apply and save settings."""
        self.settings.save_settings()
        self.has_changes = False
        print("Settings saved!")

    def _reset_settings(self):
        """Reset current tab to defaults."""
        category_map = {
            SettingsTab.AUDIO: 'audio',
            SettingsTab.GRAPHICS: 'graphics',
            SettingsTab.CONTROLS: 'controls',
            SettingsTab.GAMEPLAY: 'gameplay',
        }
        category = category_map[self.current_tab]
        self.settings.reset_to_defaults(category)
        self._refresh_widgets()
        print(f"Reset {category} settings to defaults")

    def render(self, screen: pygame.Surface):
        """Render the settings UI."""
        if not self.visible:
            return

        mouse_pos = pygame.mouse.get_pos()

        # Update hover states
        for widget in self.widgets[self.current_tab]:
            widget.update_hover(mouse_pos)

        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Main panel
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(screen, self.colors['bg'], panel_rect)
        pygame.draw.rect(screen, self.colors['border'], panel_rect, 3)

        # Title
        title = self.fonts['title'].render("Settings", True, self.colors['text'])
        title_rect = title.get_rect(centerx=self.panel_x + self.panel_width // 2,
                                     top=self.panel_y + 15)
        screen.blit(title, title_rect)

        # Render tabs
        self._render_tabs(screen, mouse_pos)

        # Render content area background
        content_rect = pygame.Rect(self.panel_x + 170, self.panel_y + 100,
                                    self.panel_width - 190, self.panel_height - 170)
        pygame.draw.rect(screen, self.colors['panel'], content_rect)

        # Render current tab content
        self._render_tab_content(screen, mouse_pos)

        # Render buttons
        self._render_buttons(screen, mouse_pos)

    def _render_tabs(self, screen: pygame.Surface, mouse_pos: Tuple[int, int]):
        """Render tab buttons."""
        tab_names = {
            SettingsTab.AUDIO: "Audio",
            SettingsTab.GRAPHICS: "Graphics",
            SettingsTab.CONTROLS: "Controls",
            SettingsTab.GAMEPLAY: "Gameplay",
        }

        tab_x = self.panel_x + 20
        tab_y = self.panel_y + 100
        tab_width = 130
        tab_height = 40
        tab_spacing = 10

        self.tab_rects.clear()

        for i, tab in enumerate(SettingsTab):
            rect = pygame.Rect(tab_x, tab_y + i * (tab_height + tab_spacing),
                               tab_width, tab_height)
            self.tab_rects[tab] = rect

            # Determine color
            if tab == self.current_tab:
                color = self.colors['tab_active']
            elif rect.collidepoint(mouse_pos):
                color = self.colors['tab_hover']
            else:
                color = self.colors['tab_inactive']

            # Draw tab
            pygame.draw.rect(screen, color, rect, border_radius=5)
            if tab == self.current_tab:
                pygame.draw.rect(screen, self.colors['highlight'], rect, 2, border_radius=5)

            # Tab text
            text = self.fonts['tab'].render(tab_names[tab], True, self.colors['text'])
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

    def _render_tab_content(self, screen: pygame.Surface, mouse_pos: Tuple[int, int]):
        """Render content for current tab."""
        widgets = self.widgets[self.current_tab]
        content_x = self.panel_x + 200

        # Render labels and widgets
        for widget in widgets:
            # Render label
            label = self.fonts['label'].render(widget.label, True, self.colors['text'])
            label_y = widget.y + (widget.height - label.get_height()) // 2
            screen.blit(label, (content_x - 180, label_y))

            # Render widget
            widget.render(screen, self.fonts)

    def _render_buttons(self, screen: pygame.Surface, mouse_pos: Tuple[int, int]):
        """Render action buttons."""
        button_y = self.panel_y + self.panel_height - 55
        button_height = 40
        button_spacing = 20

        # Apply button
        self.apply_rect = pygame.Rect(self.panel_x + self.panel_width - 350,
                                       button_y, 100, button_height)
        apply_color = (60, 120, 60) if self.apply_rect.collidepoint(mouse_pos) else (50, 100, 50)
        pygame.draw.rect(screen, apply_color, self.apply_rect, border_radius=5)
        pygame.draw.rect(screen, (100, 180, 100), self.apply_rect, 2, border_radius=5)
        apply_text = self.fonts['tab'].render("Apply", True, self.colors['text'])
        screen.blit(apply_text, apply_text.get_rect(center=self.apply_rect.center))

        # Reset button
        self.reset_rect = pygame.Rect(self.panel_x + self.panel_width - 230,
                                       button_y, 100, button_height)
        reset_color = (120, 100, 60) if self.reset_rect.collidepoint(mouse_pos) else (100, 80, 50)
        pygame.draw.rect(screen, reset_color, self.reset_rect, border_radius=5)
        pygame.draw.rect(screen, (180, 150, 100), self.reset_rect, 2, border_radius=5)
        reset_text = self.fonts['tab'].render("Reset", True, self.colors['text'])
        screen.blit(reset_text, reset_text.get_rect(center=self.reset_rect.center))

        # Close button
        self.close_rect = pygame.Rect(self.panel_x + self.panel_width - 110,
                                       button_y, 100, button_height)
        close_color = (100, 60, 60) if self.close_rect.collidepoint(mouse_pos) else (80, 50, 50)
        pygame.draw.rect(screen, close_color, self.close_rect, border_radius=5)
        pygame.draw.rect(screen, (180, 100, 100), self.close_rect, 2, border_radius=5)
        close_text = self.fonts['tab'].render("Close", True, self.colors['text'])
        screen.blit(close_text, close_text.get_rect(center=self.close_rect.center))

        # Unsaved changes indicator
        if self.has_changes:
            indicator = self.fonts['small'].render("* Unsaved changes", True, (255, 200, 100))
            screen.blit(indicator, (self.panel_x + 20, button_y + 10))

        # Close hint
        hint = self.fonts['small'].render("ESC to close", True, self.colors['text_dim'])
        screen.blit(hint, (self.panel_x + 20, button_y + 30))
