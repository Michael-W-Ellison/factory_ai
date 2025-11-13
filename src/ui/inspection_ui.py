"""
Inspection UI - displays inspection warnings, progress, and results.

Handles:
- Countdown warning when inspection is scheduled
- Progress bar during inspection
- Results screen after inspection completes
"""

import pygame
from src.systems.inspection_manager import InspectionStatus, InspectionResult


class InspectionUI:
    """UI for inspection system."""

    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize inspection UI.

        Args:
            screen_width (int): Screen width in pixels
            screen_height (int): Screen height in pixels
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # UI state
        self.show_results = False
        self.results_display_time = 0.0
        self.results_display_duration = 5.0  # Show results for 5 seconds

        # Colors
        self.color_warning = (255, 200, 0)
        self.color_danger = (255, 100, 100)
        self.color_success = (100, 255, 100)
        self.color_bg = (30, 30, 30)
        self.color_text = (255, 255, 255)

    def render(self, screen, inspection_manager, dt: float):
        """
        Render inspection UI.

        Args:
            screen: Pygame surface
            inspection_manager: InspectionManager instance
            dt (float): Delta time for animations
        """
        status = inspection_manager.status

        if status == InspectionStatus.SCHEDULED:
            self._render_countdown_warning(screen, inspection_manager)

        elif status == InspectionStatus.IN_PROGRESS:
            self._render_inspection_progress(screen, inspection_manager)

        elif status == InspectionStatus.COMPLETED or self.show_results:
            self._render_results(screen, inspection_manager, dt)

    def _render_countdown_warning(self, screen, inspection_manager):
        """Render countdown warning."""
        countdown_hours = inspection_manager.get_countdown_hours()

        # Position at top center
        center_x = self.screen_width // 2
        y = 50

        # Background box
        box_width = 400
        box_height = 80
        box_x = center_x - box_width // 2

        # Draw semi-transparent background
        box_surface = pygame.Surface((box_width, box_height))
        box_surface.set_alpha(220)
        box_surface.fill(self.color_bg)
        screen.blit(box_surface, (box_x, y))

        # Draw border (warning color)
        pygame.draw.rect(screen, self.color_warning, (box_x, y, box_width, box_height), 3)

        # Title
        font_large = pygame.font.Font(None, 32)
        title = font_large.render("⚠️ INSPECTION SCHEDULED", True, self.color_warning)
        title_rect = title.get_rect(center=(center_x, y + 20))
        screen.blit(title, title_rect)

        # Countdown
        font_medium = pygame.font.Font(None, 28)
        countdown_text = f"Inspector arrives in: {countdown_hours:.1f} game hours"
        countdown = font_medium.render(countdown_text, True, self.color_text)
        countdown_rect = countdown.get_rect(center=(center_x, y + 50))
        screen.blit(countdown, countdown_rect)

    def _render_inspection_progress(self, screen, inspection_manager):
        """Render inspection progress bar."""
        progress_percent = inspection_manager.get_inspection_progress_percent()

        # Position at top center
        center_x = self.screen_width // 2
        y = 50

        # Background box
        box_width = 400
        box_height = 100
        box_x = center_x - box_width // 2

        # Draw semi-transparent background
        box_surface = pygame.Surface((box_width, box_height))
        box_surface.set_alpha(220)
        box_surface.fill(self.color_bg)
        screen.blit(box_surface, (box_x, y))

        # Draw border (danger color)
        pygame.draw.rect(screen, self.color_danger, (box_x, y, box_width, box_height), 3)

        # Title
        font_large = pygame.font.Font(None, 32)
        title = font_large.render("🕵️ INSPECTION IN PROGRESS", True, self.color_danger)
        title_rect = title.get_rect(center=(center_x, y + 20))
        screen.blit(title, title_rect)

        # Progress bar
        bar_width = 350
        bar_height = 20
        bar_x = center_x - bar_width // 2
        bar_y = y + 50

        # Background
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # Progress fill
        fill_width = int(bar_width * (progress_percent / 100.0))
        pygame.draw.rect(screen, self.color_danger, (bar_x, bar_y, fill_width, bar_height))

        # Outline
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)

        # Percentage text
        font_small = pygame.font.Font(None, 24)
        percent_text = font_small.render(f"{progress_percent:.0f}%", True, self.color_text)
        percent_rect = percent_text.get_rect(center=(center_x, y + 80))
        screen.blit(percent_text, percent_rect)

    def _render_results(self, screen, inspection_manager, dt: float):
        """Render inspection results."""
        if inspection_manager.last_result is None:
            return

        # Update results display timer
        if self.show_results:
            self.results_display_time += dt
            if self.results_display_time >= self.results_display_duration:
                self.show_results = False
                self.results_display_time = 0.0
                return

        # Show results when inspection just completed
        if inspection_manager.status == InspectionStatus.COMPLETED:
            self.show_results = True
            self.results_display_time = 0.0

        result = inspection_manager.last_result

        # Position at center
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # Box size depends on result
        box_width = 500
        box_height = 250
        box_x = center_x - box_width // 2
        box_y = center_y - box_height // 2

        # Draw semi-transparent background
        box_surface = pygame.Surface((box_width, box_height))
        box_surface.set_alpha(240)
        box_surface.fill(self.color_bg)
        screen.blit(box_surface, (box_x, box_y))

        # Choose color based on result
        if result == InspectionResult.PASS:
            border_color = self.color_success
            title_text = "✓ INSPECTION PASSED"
            details = [
                "Factory is clean!",
                "Suspicion reduced by 20",
                "No inspection for 7 days"
            ]
        elif result == InspectionResult.FAIL_MINOR:
            border_color = self.color_warning
            title_text = "⚠️ INSPECTION FAILED (Minor)"
            details = [
                "Some questionable materials found",
                "Fine: $5,000",
                "Suspicion increased by 10",
                "Reinspection in 3 days"
            ]
        elif result == InspectionResult.FAIL_MAJOR:
            border_color = self.color_danger
            title_text = "🚨 INSPECTION FAILED (Major)"
            details = [
                "Illegal materials discovered!",
                "Fine: $20,000",
                "Suspicion increased by 30",
                "Operating restrictions applied"
            ]
        else:  # FAIL_CRITICAL
            border_color = (255, 0, 0)
            title_text = "💀 INSPECTION FAILED (Critical)"
            details = [
                "GAME OVER",
                "Extensive illegal operation discovered",
                "FBI raid in progress",
                "Factory shut down"
            ]

        # Draw border
        pygame.draw.rect(screen, border_color, (box_x, box_y, box_width, box_height), 4)

        # Title
        font_large = pygame.font.Font(None, 36)
        title = font_large.render(title_text, True, border_color)
        title_rect = title.get_rect(center=(center_x, box_y + 30))
        screen.blit(title, title_rect)

        # Divider line
        pygame.draw.line(screen, border_color, (box_x + 20, box_y + 60), (box_x + box_width - 20, box_y + 60), 2)

        # Details
        font_medium = pygame.font.Font(None, 24)
        detail_y = box_y + 80
        for detail in details:
            detail_text = font_medium.render(detail, True, self.color_text)
            detail_rect = detail_text.get_rect(center=(center_x, detail_y))
            screen.blit(detail_text, detail_rect)
            detail_y += 30

        # Press key to continue (if critical)
        if result == InspectionResult.FAIL_CRITICAL:
            font_small = pygame.font.Font(None, 20)
            continue_text = font_small.render("Press ESC to exit", True, (200, 200, 200))
            continue_rect = continue_text.get_rect(center=(center_x, box_y + box_height - 20))
            screen.blit(continue_text, continue_rect)

    def render_hud_indicator(self, screen, inspection_manager):
        """
        Render small indicator in HUD when inspection is scheduled.

        Args:
            screen: Pygame surface
            inspection_manager: InspectionManager instance
        """
        if inspection_manager.status != InspectionStatus.SCHEDULED:
            return

        # Position in top-right corner
        x = self.screen_width - 220
        y = 10

        # Small box
        box_width = 210
        box_height = 40

        # Semi-transparent background
        box_surface = pygame.Surface((box_width, box_height))
        box_surface.set_alpha(200)
        box_surface.fill((40, 40, 40))
        screen.blit(box_surface, (x, y))

        # Border
        pygame.draw.rect(screen, self.color_warning, (x, y, box_width, box_height), 2)

        # Text
        font = pygame.font.Font(None, 20)
        countdown_hours = inspection_manager.get_countdown_hours()
        text = font.render(f"⚠️ Inspection: {countdown_hours:.1f}h", True, self.color_warning)
        text_rect = text.get_rect(center=(x + box_width // 2, y + box_height // 2))
        screen.blit(text, text_rect)
