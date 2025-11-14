"""
Controls/Help Overlay - Displays game controls and help information.

Shows a comprehensive guide to all game controls organized by category.
"""

import pygame
from typing import List, Tuple


class ControlsHelp:
    """
    Help overlay showing all game controls.

    Displays controls organized by category with clear descriptions.
    """

    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize the controls help overlay.

        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Visibility
        self.visible = False

        # Panel dimensions
        self.panel_width = 1000
        self.panel_height = 650
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2

        # Fonts
        self.font_title = pygame.font.Font(None, 56)
        self.font_section = pygame.font.Font(None, 32)
        self.font_key = pygame.font.Font(None, 24)
        self.font_desc = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)

        # Colors
        self.color_bg = (20, 20, 30)
        self.color_panel = (35, 35, 45)
        self.color_title = (100, 200, 255)
        self.color_section = (150, 220, 255)
        self.color_key = (255, 220, 100)
        self.color_desc = (220, 220, 220)
        self.color_border = (100, 150, 255)

        # Scroll state
        self.scroll_offset = 0
        self.max_scroll = 0

        # Controls data organized by category
        self.controls = self._build_controls_data()

    def _build_controls_data(self) -> List[Tuple[str, List[Tuple[str, str]]]]:
        """Build the controls data structure."""
        return [
            ("Camera Controls", [
                ("W/A/S/D", "Move camera up/left/down/right"),
                ("Arrow Keys", "Alternative camera movement"),
                ("Mouse Edge", "Move camera to screen edges"),
            ]),

            ("Robot Controls", [
                ("Left Click", "Select robot"),
                ("Arrow Keys", "Move selected robot (manual mode)"),
                ("R (on robot)", "Toggle autonomous/manual mode"),
                ("1-9", "Quick select robot by number"),
            ]),

            ("Building Controls", [
                ("B", "Open building menu"),
                ("Click Building", "View building info"),
                ("Click + Drag", "Select multiple buildings"),
                ("Delete", "Demolish selected building"),
            ]),

            ("Game Controls", [
                ("SPACE", "Pause/Resume game"),
                ("ESC", "Exit game"),
                ("+/-", "Increase/Decrease game speed"),
                ("G", "Toggle grid display"),
                ("P", "Toggle pollution overlay"),
            ]),

            ("Menus & UI", [
                ("R", "Open/Close research menu"),
                ("I", "Open/Close inventory"),
                ("M", "Toggle minimap"),
                ("H or F1", "Show/Hide this help screen"),
                ("F10", "Open/Close save/load menu"),
            ]),

            ("Save & Load", [
                ("F5", "Quick save"),
                ("F9", "Quick load"),
                ("F10", "Open save/load menu"),
                ("Auto-save", "Saves every 5 game days"),
            ]),

            ("Camera Hacking", [
                ("Click Camera", "Hack security camera (requires research)"),
                ("Hold Shift", "Show camera coverage"),
                ("C", "Toggle camera view overlay"),
            ]),

            ("Advanced", [
                ("Tab", "Cycle through robots"),
                ("Ctrl + Click", "Add to selection"),
                ("Shift + Click", "Queue commands"),
                ("Alt + Click", "Special action (context-dependent)"),
            ]),

            ("Debug (if enabled)", [
                ("F3", "Toggle debug info"),
                ("F4", "Spawn test entities"),
                ("F11", "Toggle fullscreen"),
                ("F12", "Take screenshot"),
            ]),
        ]

    def toggle(self):
        """Toggle help overlay visibility."""
        self.visible = not self.visible
        if self.visible:
            self.scroll_offset = 0  # Reset scroll when opening

    def show(self):
        """Show the help overlay."""
        self.visible = True
        self.scroll_offset = 0

    def hide(self):
        """Hide the help overlay."""
        self.visible = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.

        Args:
            event: Pygame event

        Returns:
            True if event was handled, False otherwise
        """
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            # ESC, H, or F1 to close
            if event.key in (pygame.K_ESCAPE, pygame.K_h, pygame.K_F1):
                self.hide()
                return True

        # Mouse wheel for scrolling
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 30)
            elif event.y < 0:  # Scroll down
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 30)
            return True

        # Consume all events while visible
        return True

    def render(self, screen: pygame.Surface):
        """
        Render the help overlay.

        Args:
            screen: Pygame surface to render to
        """
        if not self.visible:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Main panel
        panel_surface = pygame.Surface((self.panel_width, self.panel_height))
        panel_surface.fill(self.color_bg)
        pygame.draw.rect(panel_surface, self.color_border, (0, 0, self.panel_width, self.panel_height), 3)

        # Title
        title_text = self.font_title.render("Game Controls & Help", True, self.color_title)
        title_rect = title_text.get_rect(centerx=self.panel_width // 2, top=15)
        panel_surface.blit(title_text, title_rect)

        # Close instruction
        close_text = self.font_small.render("Press ESC, H, or F1 to close", True, (150, 150, 150))
        close_rect = close_text.get_rect(centerx=self.panel_width // 2, top=70)
        panel_surface.blit(close_text, close_rect)

        # Scrollable content area
        content_y = 100
        content_height = self.panel_height - 100

        # Create scrollable surface
        # Calculate total content height first
        total_height = self._calculate_content_height()
        self.max_scroll = max(0, total_height - content_height)

        # Create a surface for scrollable content
        scroll_surface = pygame.Surface((self.panel_width - 40, total_height))
        scroll_surface.fill(self.color_bg)

        # Render controls sections
        y_offset = 0
        for section_name, controls in self.controls:
            y_offset = self._render_section(scroll_surface, section_name, controls, 20, y_offset)
            y_offset += 15  # Space between sections

        # Blit visible portion of scroll surface
        visible_rect = pygame.Rect(0, self.scroll_offset, self.panel_width - 40, content_height)
        panel_surface.blit(scroll_surface, (20, content_y), visible_rect)

        # Scroll indicators
        if self.scroll_offset > 0:
            # Up arrow
            arrow_up = self.font_section.render("▲", True, self.color_section)
            panel_surface.blit(arrow_up, (self.panel_width // 2 - 10, content_y + 5))

        if self.scroll_offset < self.max_scroll:
            # Down arrow
            arrow_down = self.font_section.render("▼", True, self.color_section)
            panel_surface.blit(arrow_down, (self.panel_width // 2 - 10, self.panel_height - 35))

        # Blit panel to screen
        screen.blit(panel_surface, (self.panel_x, self.panel_y))

    def _calculate_content_height(self) -> int:
        """Calculate total height of scrollable content."""
        total_height = 0
        for section_name, controls in self.controls:
            total_height += 40  # Section header
            total_height += len(controls) * 28  # Each control item
            total_height += 15  # Space after section
        return total_height

    def _render_section(self, surface: pygame.Surface, section_name: str,
                       controls: List[Tuple[str, str]], x: int, y: int) -> int:
        """
        Render a section of controls.

        Args:
            surface: Surface to render to
            section_name: Name of the section
            controls: List of (key, description) tuples
            x: X position
            y: Y position

        Returns:
            New Y position after rendering
        """
        # Section header
        section_text = self.font_section.render(section_name, True, self.color_section)
        surface.blit(section_text, (x, y))
        y += 40

        # Controls in this section
        for key, description in controls:
            # Key/button
            key_text = self.font_key.render(key, True, self.color_key)
            surface.blit(key_text, (x + 20, y))

            # Description
            desc_text = self.font_desc.render(description, True, self.color_desc)
            surface.blit(desc_text, (x + 250, y))

            y += 28

        return y

    def update(self, dt: float):
        """
        Update help overlay (for animations if needed).

        Args:
            dt: Delta time in seconds
        """
        # Currently no animations, but method here for future use
        pass
