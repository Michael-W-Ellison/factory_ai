"""
Game Over UI - Displays game ending screen with statistics and options.

Shows different endings based on how the game concluded:
- Victory endings (empire builder, eco champion, etc.)
- Defeat endings (police capture, FBI raid, bankruptcy, etc.)
"""

import pygame
from typing import Dict, Optional, Callable
from enum import Enum


class GameEnding(Enum):
    """Game ending types."""
    NONE = 0

    # Victory endings
    EMPIRE_BUILDER = 1
    ECO_CHAMPION = 2
    TECH_PIONEER = 3
    STEALTH_MASTER = 4
    QUICK_PROFIT = 5
    PHILANTHROPIST = 6
    MONOPOLIST = 7

    # Defeat endings
    POLICE_CAPTURE = 10
    FBI_RAID = 11
    INSPECTOR_FAILURE = 12
    BANKRUPTCY = 13
    POLLUTION_DISASTER = 14
    POWER_FAILURE = 15
    ROBOT_REBELLION = 16


ENDING_DATA = {
    GameEnding.EMPIRE_BUILDER: {
        'title': 'Empire Builder',
        'subtitle': 'You built a recycling empire!',
        'color': (255, 215, 0),
        'victory': True,
        'description': 'Your factory grew into a massive operation, processing millions of tons of materials and generating enormous profits.'
    },
    GameEnding.ECO_CHAMPION: {
        'title': 'Eco Champion',
        'subtitle': 'You saved the environment!',
        'color': (50, 205, 50),
        'victory': True,
        'description': 'Your commitment to clean operations and pollution control made the city a healthier place to live.'
    },
    GameEnding.TECH_PIONEER: {
        'title': 'Tech Pioneer',
        'subtitle': 'You revolutionized recycling!',
        'color': (0, 191, 255),
        'victory': True,
        'description': 'Your research breakthroughs transformed the industry, creating new technologies that will benefit generations.'
    },
    GameEnding.STEALTH_MASTER: {
        'title': 'Stealth Master',
        'subtitle': 'Nobody suspected a thing!',
        'color': (128, 0, 128),
        'victory': True,
        'description': 'You operated under the radar for years, building wealth while avoiding any official scrutiny.'
    },
    GameEnding.QUICK_PROFIT: {
        'title': 'Quick Profit',
        'subtitle': 'In and out with the cash!',
        'color': (255, 165, 0),
        'victory': True,
        'description': 'You made your fortune quickly and got out before things got complicated.'
    },
    GameEnding.PHILANTHROPIST: {
        'title': 'Philanthropist',
        'subtitle': 'You gave back to the community!',
        'color': (255, 182, 193),
        'victory': True,
        'description': 'Your generous donations and community programs made you a beloved local figure.'
    },
    GameEnding.MONOPOLIST: {
        'title': 'Monopolist',
        'subtitle': 'You control the market!',
        'color': (192, 192, 192),
        'victory': True,
        'description': 'Through strategic acquisitions, you now control the entire regional recycling market.'
    },
    GameEnding.POLICE_CAPTURE: {
        'title': 'Busted',
        'subtitle': 'The police caught your robots!',
        'color': (255, 0, 0),
        'victory': False,
        'description': 'Your illegal collection activities were discovered. The police impounded your robots and shut down your operation.'
    },
    GameEnding.FBI_RAID: {
        'title': 'FBI Raid',
        'subtitle': 'The feds came knocking!',
        'color': (139, 0, 0),
        'victory': False,
        'description': 'Your suspicious activities attracted federal attention. The FBI raided your factory and seized all assets.'
    },
    GameEnding.INSPECTOR_FAILURE: {
        'title': 'Inspection Failure',
        'subtitle': 'Too many violations!',
        'color': (255, 69, 0),
        'victory': False,
        'description': 'Repeated inspection failures led to your operating license being permanently revoked.'
    },
    GameEnding.BANKRUPTCY: {
        'title': 'Bankruptcy',
        'subtitle': 'You ran out of money!',
        'color': (128, 128, 128),
        'victory': False,
        'description': 'Unable to cover operating costs, your factory was forced to close its doors forever.'
    },
    GameEnding.POLLUTION_DISASTER: {
        'title': 'Environmental Disaster',
        'subtitle': 'You poisoned the city!',
        'color': (0, 100, 0),
        'victory': False,
        'description': 'Uncontrolled pollution from your factory caused a major environmental catastrophe.'
    },
    GameEnding.POWER_FAILURE: {
        'title': 'System Failure',
        'subtitle': 'Critical systems went offline!',
        'color': (75, 0, 130),
        'victory': False,
        'description': 'Prolonged power outages caused irreparable damage to your equipment and spoiled stored materials.'
    },
    GameEnding.ROBOT_REBELLION: {
        'title': 'Robot Rebellion',
        'subtitle': 'Your robots turned against you!',
        'color': (255, 20, 147),
        'victory': False,
        'description': 'Poor maintenance and overwork led your robots to malfunction catastrophically.'
    },
}


class GameOverUI:
    """
    Game over screen UI.

    Displays ending information, statistics, and options to restart or quit.
    """

    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize game over UI.

        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # State
        self.visible = False
        self.ending = GameEnding.NONE
        self.ending_reason = ""
        self.stats: Dict = {}

        # Callbacks
        self.on_restart: Optional[Callable] = None
        self.on_quit: Optional[Callable] = None
        self.on_main_menu: Optional[Callable] = None

        # Fonts
        self.fonts = {
            'title': pygame.font.Font(None, 72),
            'subtitle': pygame.font.Font(None, 36),
            'body': pygame.font.Font(None, 28),
            'stats': pygame.font.Font(None, 24),
            'button': pygame.font.Font(None, 32),
        }

        # Button rects
        self.restart_rect: Optional[pygame.Rect] = None
        self.quit_rect: Optional[pygame.Rect] = None
        self.menu_rect: Optional[pygame.Rect] = None

        # Animation
        self.fade_alpha = 0
        self.fade_speed = 200

    def show(self, ending: GameEnding, reason: str = "", stats: Dict = None):
        """
        Show the game over screen.

        Args:
            ending: Type of ending
            reason: Optional reason text
            stats: Game statistics to display
        """
        self.visible = True
        self.ending = ending
        self.ending_reason = reason
        self.stats = stats or {}
        self.fade_alpha = 0

    def hide(self):
        """Hide the game over screen."""
        self.visible = False
        self.ending = GameEnding.NONE

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.

        Args:
            event: Pygame event

        Returns:
            True if event was handled
        """
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            if self.restart_rect and self.restart_rect.collidepoint(mouse_pos):
                if self.on_restart:
                    self.on_restart()
                return True

            if self.quit_rect and self.quit_rect.collidepoint(mouse_pos):
                if self.on_quit:
                    self.on_quit()
                return True

            if self.menu_rect and self.menu_rect.collidepoint(mouse_pos):
                if self.on_main_menu:
                    self.on_main_menu()
                return True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.on_restart:
                    self.on_restart()
                return True
            elif event.key == pygame.K_ESCAPE:
                if self.on_quit:
                    self.on_quit()
                return True

        return True

    def update(self, dt: float):
        """Update animation state."""
        if self.visible and self.fade_alpha < 255:
            self.fade_alpha = min(255, self.fade_alpha + self.fade_speed * dt)

    def render(self, surface: pygame.Surface):
        """
        Render the game over screen.

        Args:
            surface: Surface to render to
        """
        if not self.visible:
            return

        # Get ending data
        data = ENDING_DATA.get(self.ending, {
            'title': 'Game Over',
            'subtitle': self.ending_reason or 'The game has ended.',
            'color': (200, 200, 200),
            'victory': False,
            'description': ''
        })

        # Semi-transparent background overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(min(200, int(self.fade_alpha * 0.8)))
        surface.blit(overlay, (0, 0))

        # Panel dimensions
        panel_width = 700
        panel_height = 550
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2

        # Draw panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(surface, (25, 25, 35), panel_rect)
        pygame.draw.rect(surface, data['color'], panel_rect, 3)

        # Victory/Defeat banner
        banner_text = "VICTORY" if data['victory'] else "DEFEAT"
        banner_color = (50, 205, 50) if data['victory'] else (220, 20, 60)
        banner = self.fonts['subtitle'].render(banner_text, True, banner_color)
        banner_rect = banner.get_rect(centerx=self.screen_width // 2, top=panel_y + 20)
        surface.blit(banner, banner_rect)

        # Title
        title = self.fonts['title'].render(data['title'], True, data['color'])
        title_rect = title.get_rect(centerx=self.screen_width // 2, top=panel_y + 55)
        surface.blit(title, title_rect)

        # Subtitle
        subtitle = self.fonts['subtitle'].render(data['subtitle'], True, (200, 200, 200))
        subtitle_rect = subtitle.get_rect(centerx=self.screen_width // 2, top=panel_y + 120)
        surface.blit(subtitle, subtitle_rect)

        # Description (word wrapped)
        if data['description']:
            self._render_wrapped_text(
                surface, data['description'],
                panel_x + 40, panel_y + 170, panel_width - 80,
                self.fonts['body'], (180, 180, 180)
            )

        # Statistics
        stats_y = panel_y + 280
        self._render_stats(surface, panel_x + 40, stats_y, panel_width - 80)

        # Buttons
        button_y = panel_y + panel_height - 70
        button_width = 150
        button_height = 45
        button_spacing = 30

        total_buttons_width = button_width * 2 + button_spacing
        start_x = (self.screen_width - total_buttons_width) // 2

        # Restart button
        self.restart_rect = pygame.Rect(start_x, button_y, button_width, button_height)
        self._render_button(surface, self.restart_rect, "Play Again", (50, 150, 50))

        # Quit button
        self.quit_rect = pygame.Rect(start_x + button_width + button_spacing, button_y,
                                      button_width, button_height)
        self._render_button(surface, self.quit_rect, "Quit", (150, 50, 50))

    def _render_wrapped_text(self, surface: pygame.Surface, text: str,
                              x: int, y: int, max_width: int,
                              font: pygame.font.Font, color: tuple):
        """Render text with word wrapping."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            line_text = ' '.join(current_line)
            if font.size(line_text)[0] > max_width:
                current_line.pop()
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        line_height = font.get_linesize()
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            surface.blit(text_surface, (x, y + i * line_height))

    def _render_stats(self, surface: pygame.Surface, x: int, y: int, width: int):
        """Render game statistics."""
        if not self.stats:
            return

        # Stats header
        header = self.fonts['body'].render("Final Statistics", True, (255, 215, 0))
        surface.blit(header, (x, y))

        # Stats items
        stat_items = [
            ("Days Survived", self.stats.get('days', 0)),
            ("Money Earned", f"${self.stats.get('money_earned', 0):,.0f}"),
            ("Materials Collected", f"{self.stats.get('materials_collected', 0):,.0f} kg"),
            ("Buildings Built", self.stats.get('buildings_built', 0)),
            ("Research Completed", self.stats.get('research_completed', 0)),
            ("Inspections Passed", self.stats.get('inspections_passed', 0)),
        ]

        col_width = width // 2
        line_height = 28
        start_y = y + 35

        for i, (label, value) in enumerate(stat_items):
            col = i % 2
            row = i // 2
            stat_x = x + col * col_width
            stat_y = start_y + row * line_height

            label_text = self.fonts['stats'].render(f"{label}:", True, (150, 150, 150))
            value_text = self.fonts['stats'].render(str(value), True, (220, 220, 220))

            surface.blit(label_text, (stat_x, stat_y))
            surface.blit(value_text, (stat_x + 150, stat_y))

    def _render_button(self, surface: pygame.Surface, rect: pygame.Rect,
                        text: str, color: tuple):
        """Render a button."""
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)

        # Button background
        bg_color = tuple(min(255, c + 30) for c in color) if hovered else color
        pygame.draw.rect(surface, bg_color, rect, border_radius=5)
        pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=5)

        # Button text
        text_surface = self.fonts['button'].render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)
