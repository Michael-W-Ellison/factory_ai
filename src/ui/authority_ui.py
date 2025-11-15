"""
Authority UI - displays law enforcement tier, FBI investigations, and endings.

Handles:
- Authority tier indicator
- FBI investigation progress
- Raid countdown warning
- Social engineering action buttons
- Game ending screens
"""

import pygame
from src.systems.authority_manager import AuthorityTier, GameEnding


class AuthorityUI:
    """UI for authority escalation and FBI system."""

    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize authority UI.

        Args:
            screen_width (int): Screen width in pixels
            screen_height (int): Screen height in pixels
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Colors
        self.color_local = (100, 150, 255)      # Blue - local police
        self.color_state = (255, 200, 100)      # Orange - state police
        self.color_federal = (255, 50, 50)      # Red - FBI
        self.color_warning = (255, 200, 0)
        self.color_danger = (255, 100, 100)
        self.color_success = (100, 255, 100)
        self.color_bg = (30, 30, 30)
        self.color_text = (255, 255, 255)

    def render(self, screen, authority_manager):
        """
        Render authority UI.

        Args:
            screen: Pygame surface
            authority_manager: AuthorityManager instance
        """
        # Render tier indicator in top-left
        self._render_tier_indicator(screen, authority_manager)

        # Render FBI investigation if active
        if authority_manager.fbi_investigation_active:
            self._render_fbi_investigation(screen, authority_manager)

        # Render raid countdown if scheduled
        if authority_manager.raid_scheduled:
            self._render_raid_countdown(screen, authority_manager)

        # Render game ending if triggered
        if authority_manager.game_ending != GameEnding.NONE:
            self._render_game_ending(screen, authority_manager)

    def _render_tier_indicator(self, screen, authority_manager):
        """Render authority tier indicator."""
        tier = authority_manager.current_tier

        # Choose color based on tier
        if tier == AuthorityTier.LOCAL:
            color = self.color_local
            text = "👮 LOCAL POLICE"
        elif tier == AuthorityTier.STATE:
            color = self.color_state
            text = "🚔 STATE POLICE"
        else:  # FEDERAL
            color = self.color_federal
            text = "🚨 FBI"

        # Position in top-left corner
        x = 10
        y = 10
        box_width = 200
        box_height = 40

        # Semi-transparent background
        box_surface = pygame.Surface((box_width, box_height))
        box_surface.set_alpha(200)
        box_surface.fill(self.color_bg)
        screen.blit(box_surface, (x, y))

        # Border
        pygame.draw.rect(screen, color, (x, y, box_width, box_height), 3)

        # Text
        font = pygame.font.Font(None, 24)
        tier_text = font.render(text, True, color)
        tier_rect = tier_text.get_rect(center=(x + box_width // 2, y + box_height // 2))
        screen.blit(tier_text, tier_rect)

        # Tier change animation (flash)
        if authority_manager.tier_changed:
            # Draw flashing border
            for offset in range(3):
                pygame.draw.rect(screen, color,
                               (x - offset * 2, y - offset * 2,
                                box_width + offset * 4, box_height + offset * 4), 2)

    def _render_fbi_investigation(self, screen, authority_manager):
        """Render FBI investigation progress."""
        progress = authority_manager.investigation_progress

        # Position at top-center
        center_x = self.screen_width // 2
        y = 10

        box_width = 400
        box_height = 100
        box_x = center_x - box_width // 2

        # Semi-transparent background
        box_surface = pygame.Surface((box_width, box_height))
        box_surface.set_alpha(220)
        box_surface.fill(self.color_bg)
        screen.blit(box_surface, (box_x, y))

        # Border (danger color)
        pygame.draw.rect(screen, self.color_federal, (box_x, y, box_width, box_height), 3)

        # Title
        font_large = pygame.font.Font(None, 28)
        title = font_large.render("🔍 FBI INVESTIGATION", True, self.color_federal)
        title_rect = title.get_rect(center=(center_x, y + 20))
        screen.blit(title, title_rect)

        # Investigation type
        font_small = pygame.font.Font(None, 20)
        inv_type = authority_manager.investigation_type.name.replace('_', ' ')
        type_text = font_small.render(f"Type: {inv_type}", True, self.color_text)
        type_rect = type_text.get_rect(center=(center_x, y + 42))
        screen.blit(type_text, type_rect)

        # Progress bar
        bar_width = 350
        bar_height = 20
        bar_x = center_x - bar_width // 2
        bar_y = y + 60

        # Background
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # Progress fill (color based on progress)
        fill_width = int(bar_width * (progress / 100.0))
        if progress < 30:
            fill_color = (255, 200, 0)  # Yellow
        elif progress < 70:
            fill_color = (255, 150, 0)  # Orange
        else:
            fill_color = (255, 50, 50)  # Red
        pygame.draw.rect(screen, fill_color, (bar_x, bar_y, fill_width, bar_height))

        # Outline
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)

        # Percentage text
        percent_text = font_small.render(f"{progress:.1f}%", True, self.color_text)
        percent_rect = percent_text.get_rect(center=(center_x, y + 85))
        screen.blit(percent_text, percent_rect)

    def _render_raid_countdown(self, screen, authority_manager):
        """Render FBI raid countdown warning."""
        countdown_hours = authority_manager.raid_countdown / 3600.0

        # Position at center (high priority warning)
        center_x = self.screen_width // 2
        center_y = self.screen_height // 3

        box_width = 500
        box_height = 200
        box_x = center_x - box_width // 2
        box_y = center_y - box_height // 2

        # Semi-transparent background
        box_surface = pygame.Surface((box_width, box_height))
        box_surface.set_alpha(240)
        box_surface.fill(self.color_bg)
        screen.blit(box_surface, (box_x, box_y))

        # Flashing border
        import time
        flash = int(time.time() * 2) % 2  # Flash every 0.5 seconds
        border_color = (255, 0, 0) if flash else (200, 0, 0)
        pygame.draw.rect(screen, border_color, (box_x, box_y, box_width, box_height), 4)

        # Title
        font_large = pygame.font.Font(None, 36)
        title = font_large.render("💥 FBI RAID IMMINENT 💥", True, (255, 0, 0))
        title_rect = title.get_rect(center=(center_x, box_y + 30))
        screen.blit(title, title_rect)

        # Countdown
        font_medium = pygame.font.Font(None, 32)
        countdown_text = f"Tactical team arrives in: {countdown_hours:.1f} hours"
        countdown = font_medium.render(countdown_text, True, self.color_warning)
        countdown_rect = countdown.get_rect(center=(center_x, box_y + 70))
        screen.blit(countdown, countdown_rect)

        # Divider line
        pygame.draw.line(screen, (200, 200, 200),
                        (box_x + 20, box_y + 95),
                        (box_x + box_width - 20, box_y + 95), 2)

        # Options
        font_small = pygame.font.Font(None, 24)
        options = [
            "Available Actions:",
            "  E - Attempt Escape",
            "  P - Negotiate Plea Deal",
            "  (Or continue playing and face raid)",
        ]

        y_offset = box_y + 110
        for option in options:
            option_text = font_small.render(option, True, self.color_text)
            option_rect = option_text.get_rect(center=(center_x, y_offset))
            screen.blit(option_text, option_rect)
            y_offset += 25

    def _render_game_ending(self, screen, authority_manager):
        """Render game ending screen."""
        ending = authority_manager.game_ending
        reason = authority_manager.ending_reason

        # Full-screen overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Center box
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        box_width = 600
        box_height = 400
        box_x = center_x - box_width // 2
        box_y = center_y - box_height // 2

        # Background
        box_surface = pygame.Surface((box_width, box_height))
        box_surface.set_alpha(255)
        box_surface.fill(self.color_bg)
        screen.blit(box_surface, (box_x, box_y))

        # Choose color and title based on ending
        if ending == GameEnding.LEGITIMATE_SUCCESS:
            border_color = self.color_success
            title_text = "🎉 LEGITIMATE SUCCESS! 🎉"
            subtitle = "You built a successful legal business!"
        elif ending == GameEnding.FBI_RAID:
            border_color = (255, 0, 0)
            title_text = "💥 FBI RAID - ARRESTED 💥"
            subtitle = "Federal agents have shut down your operation"
        elif ending == GameEnding.BANKRUPTCY:
            border_color = (150, 150, 150)
            title_text = "💸 BANKRUPTCY 💸"
            subtitle = "Unable to recover from financial losses"
        elif ending == GameEnding.ESCAPE:
            border_color = (200, 200, 100)
            title_text = "✈️ ESCAPED ✈️"
            subtitle = "Living in exile abroad"
        elif ending == GameEnding.PLEA_DEAL:
            border_color = (255, 200, 100)
            title_text = "⚖️ PLEA DEAL ⚖️"
            subtitle = "Negotiated reduced charges"
        else:  # INSPECTOR_FAILURE
            border_color = (255, 50, 50)
            title_text = "💀 INSPECTION FAILURE 💀"
            subtitle = "Critical violations discovered"

        # Border
        pygame.draw.rect(screen, border_color, (box_x, box_y, box_width, box_height), 5)

        # Title
        font_huge = pygame.font.Font(None, 48)
        title = font_huge.render(title_text, True, border_color)
        title_rect = title.get_rect(center=(center_x, box_y + 60))
        screen.blit(title, title_rect)

        # Subtitle
        font_large = pygame.font.Font(None, 32)
        sub = font_large.render(subtitle, True, self.color_text)
        sub_rect = sub.get_rect(center=(center_x, box_y + 110))
        screen.blit(sub, sub_rect)

        # Divider
        pygame.draw.line(screen, border_color,
                        (box_x + 40, box_y + 150),
                        (box_x + box_width - 40, box_y + 150), 3)

        # Reason details
        font_medium = pygame.font.Font(None, 24)
        reason_lines = self._wrap_text(reason, box_width - 80)

        y_offset = box_y + 180
        for line in reason_lines:
            line_text = font_medium.render(line, True, self.color_text)
            line_rect = line_text.get_rect(center=(center_x, y_offset))
            screen.blit(line_text, line_rect)
            y_offset += 30

        # Statistics (if available)
        if hasattr(authority_manager, 'tier_escalations'):
            stats_y = box_y + box_height - 120
            font_small = pygame.font.Font(None, 20)

            stats = [
                f"Authority Escalations: {authority_manager.tier_escalations}",
                f"Bribes Attempted: {authority_manager.bribes_attempted}",
                f"Bribes Successful: {authority_manager.bribes_successful}",
            ]

            for stat in stats:
                stat_text = font_small.render(stat, True, (200, 200, 200))
                stat_rect = stat_text.get_rect(center=(center_x, stats_y))
                screen.blit(stat_text, stat_rect)
                stats_y += 25

        # Exit instruction
        font_small = pygame.font.Font(None, 24)
        exit_text = font_small.render("Press ESC to exit", True, (150, 150, 150))
        exit_rect = exit_text.get_rect(center=(center_x, box_y + box_height - 30))
        screen.blit(exit_text, exit_rect)

    def _wrap_text(self, text: str, max_width: int) -> list:
        """
        Wrap text to fit within width.

        Args:
            text (str): Text to wrap
            max_width (int): Maximum width in pixels

        Returns:
            list: List of text lines
        """
        # Simple word wrapping (could be improved)
        words = text.split()
        lines = []
        current_line = []
        current_width = 0

        font = pygame.font.Font(None, 24)

        for word in words:
            word_surface = font.render(word + ' ', True, (255, 255, 255))
            word_width = word_surface.get_width()

            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def render_hud_indicator(self, screen, authority_manager):
        """
        Render small HUD indicators for authority status.

        Args:
            screen: Pygame surface
            authority_manager: AuthorityManager instance
        """
        # FBI investigation indicator (if active)
        if authority_manager.fbi_investigation_active:
            x = self.screen_width - 220
            y = 60  # Below inspection indicator

            box_width = 210
            box_height = 40

            # Semi-transparent background
            box_surface = pygame.Surface((box_width, box_height))
            box_surface.set_alpha(200)
            box_surface.fill((40, 40, 40))
            screen.blit(box_surface, (x, y))

            # Border
            pygame.draw.rect(screen, self.color_federal, (x, y, box_width, box_height), 2)

            # Text
            font = pygame.font.Font(None, 18)
            progress = authority_manager.investigation_progress
            text = font.render(f"🔍 FBI: {progress:.0f}%", True, self.color_federal)
            text_rect = text.get_rect(center=(x + box_width // 2, y + box_height // 2))
            screen.blit(text, text_rect)
