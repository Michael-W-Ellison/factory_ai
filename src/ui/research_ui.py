"""
Research UI - Interface for viewing and starting research.

Provides a menu for browsing technologies, viewing details, and starting research.
"""

import pygame
from typing import Optional, Dict, List


class ResearchUI:
    """
    Research menu UI.

    Shows available research, details, and allows starting/cancelling research.
    """

    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize the research UI.

        Args:
            screen_width (int): Screen width in pixels
            screen_height (int): Screen height in pixels
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # UI state
        self.visible = False
        self.selected_research = None
        self.scroll_offset = 0
        self.selected_category = "all"  # all, robot, processing, power, stealth, advanced

        # Layout constants
        self.panel_width = 900
        self.panel_height = 600
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2

        self.list_width = 350
        self.details_width = self.panel_width - self.list_width - 30

        # Colors
        self.bg_color = (30, 30, 40, 230)
        self.panel_color = (40, 40, 50)
        self.available_color = (50, 200, 50)
        self.locked_color = (150, 150, 150)
        self.completed_color = (100, 150, 255)
        self.in_progress_color = (255, 200, 50)
        self.text_color = (255, 255, 255)
        self.button_color = (60, 120, 180)
        self.button_hover_color = (80, 140, 200)

        # Fonts
        try:
            self.font_title = pygame.font.Font(None, 32)
            self.font_normal = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 20)
        except:
            self.font_title = pygame.font.SysFont('arial', 32)
            self.font_normal = pygame.font.SysFont('arial', 24)
            self.font_small = pygame.font.SysFont('arial', 20)

        # Category buttons
        self.categories = ["all", "robot", "processing", "power", "stealth", "advanced"]
        self.category_buttons = {}
        self._setup_category_buttons()

        # Button rects (for mouse interaction)
        self.start_button_rect = None
        self.cancel_button_rect = None
        self.close_button_rect = None

    def _setup_category_buttons(self):
        """Setup category button rectangles."""
        button_width = 120
        button_height = 30
        button_spacing = 10
        start_x = self.panel_x + 10
        start_y = self.panel_y + 50

        for i, category in enumerate(self.categories):
            x = start_x + (button_width + button_spacing) * (i % 3)
            y = start_y + (button_height + button_spacing) * (i // 3)
            self.category_buttons[category] = pygame.Rect(x, y, button_width, button_height)

    def toggle(self):
        """Toggle visibility of research menu."""
        self.visible = not self.visible
        if self.visible:
            self.scroll_offset = 0
            self.selected_research = None

    def show(self):
        """Show the research menu."""
        self.visible = True

    def hide(self):
        """Hide the research menu."""
        self.visible = False

    def handle_event(self, event, research_manager, money: float):
        """
        Handle input events for the research UI.

        Args:
            event: Pygame event
            research_manager: ResearchManager instance
            money (float): Available money

        Returns:
            bool: True if event was handled
        """
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Check close button
            if self.close_button_rect and self.close_button_rect.collidepoint(mouse_x, mouse_y):
                self.hide()
                return True

            # Check category buttons
            for category, rect in self.category_buttons.items():
                if rect.collidepoint(mouse_x, mouse_y):
                    self.selected_category = category
                    self.scroll_offset = 0
                    self.selected_research = None
                    return True

            # Check research list items
            research_list = self._get_filtered_research(research_manager)
            list_x = self.panel_x + 10
            list_y = self.panel_y + 120
            item_height = 60

            for i, research in enumerate(research_list):
                item_y = list_y + (i * item_height) - self.scroll_offset
                if list_y <= item_y < list_y + 400:  # Visible area
                    item_rect = pygame.Rect(list_x, item_y, self.list_width - 20, item_height - 5)
                    if item_rect.collidepoint(mouse_x, mouse_y):
                        self.selected_research = research['id']
                        return True

            # Check start button
            if self.start_button_rect and self.start_button_rect.collidepoint(mouse_x, mouse_y):
                if self.selected_research:
                    if research_manager.start_research(self.selected_research, money):
                        print(f"Started research: {self.selected_research}")
                        return True

            # Check cancel button
            if self.cancel_button_rect and self.cancel_button_rect.collidepoint(mouse_x, mouse_y):
                cancelled = research_manager.cancel_research()
                if cancelled:
                    print(f"Cancelled research: {cancelled}")
                    return True

        elif event.type == pygame.MOUSEWHEEL:
            # Scroll the research list
            if self.visible:
                self.scroll_offset -= event.y * 30
                self.scroll_offset = max(0, self.scroll_offset)
                return True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_r:
                self.hide()
                return True

        return False

    def _get_filtered_research(self, research_manager) -> List[Dict]:
        """Get research list filtered by selected category."""
        if self.selected_category == "all":
            return list(research_manager.research_tree.values())
        else:
            return research_manager.get_research_by_category(self.selected_category)

    def render(self, screen, research_manager, money: float):
        """
        Render the research menu.

        Args:
            screen: Pygame surface
            research_manager: ResearchManager instance
            money (float): Available money
        """
        if not self.visible:
            return

        # Semi-transparent background overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        # Main panel
        panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.bg_color)

        # Title
        title_text = self.font_title.render("Research", True, self.text_color)
        panel_surface.blit(title_text, (10, 10))

        # Close button
        close_x = self.panel_width - 40
        close_y = 10
        self.close_button_rect = pygame.Rect(
            self.panel_x + close_x, self.panel_y + close_y, 30, 30
        )
        pygame.draw.rect(panel_surface, (200, 50, 50), (close_x, close_y, 30, 30))
        close_text = self.font_normal.render("X", True, self.text_color)
        panel_surface.blit(close_text, (close_x + 8, close_y + 2))

        # Category buttons
        for category, rect in self.category_buttons.items():
            local_rect = pygame.Rect(
                rect.x - self.panel_x, rect.y - self.panel_y,
                rect.width, rect.height
            )

            if category == self.selected_category:
                color = self.button_hover_color
            else:
                color = self.button_color

            pygame.draw.rect(panel_surface, color, local_rect)
            pygame.draw.rect(panel_surface, self.text_color, local_rect, 1)

            text = self.font_small.render(category.title(), True, self.text_color)
            text_x = local_rect.centerx - text.get_width() // 2
            text_y = local_rect.centery - text.get_height() // 2
            panel_surface.blit(text, (text_x, text_y))

        # Research list area
        list_y_start = 120
        self._render_research_list(panel_surface, research_manager, money, list_y_start)

        # Research details panel
        if self.selected_research:
            details_x = self.list_width + 20
            self._render_research_details(
                panel_surface, research_manager, money,
                details_x, list_y_start
            )

        # Statistics
        stats = research_manager.get_stats()
        stats_text = self.font_small.render(
            f"Completed: {stats['completed']}/{stats['total_research']} ({stats['completion_percentage']:.1f}%)",
            True, self.text_color
        )
        panel_surface.blit(stats_text, (10, self.panel_height - 30))

        # Blit panel to screen
        screen.blit(panel_surface, (self.panel_x, self.panel_y))

    def _render_research_list(self, surface, research_manager, money: float, start_y: int):
        """Render the list of research items."""
        research_list = self._get_filtered_research(research_manager)

        list_x = 10
        list_width = self.list_width - 20
        item_height = 60
        visible_height = self.panel_height - start_y - 40

        # Create clipping rect for scrolling
        clip_rect = pygame.Rect(list_x, start_y, list_width, visible_height)

        for i, research in enumerate(research_list):
            tech_id = research['id']
            item_y = start_y + (i * item_height) - self.scroll_offset

            # Skip if outside visible area
            if item_y + item_height < start_y or item_y > start_y + visible_height:
                continue

            # Determine status and color
            if research_manager.is_completed(tech_id):
                status_color = self.completed_color
                status = "✓"
            elif research_manager.current_research == tech_id:
                status_color = self.in_progress_color
                status = "⏳"
            elif research_manager.is_available(tech_id):
                if research_manager.can_afford(tech_id, money):
                    status_color = self.available_color
                    status = "●"
                else:
                    status_color = (200, 150, 50)
                    status = "●"
            else:
                status_color = self.locked_color
                status = "🔒"

            # Draw item background
            item_rect = pygame.Rect(list_x, item_y, list_width, item_height - 5)

            if tech_id == self.selected_research:
                bg_color = (60, 60, 80)
            else:
                bg_color = self.panel_color

            pygame.draw.rect(surface, bg_color, item_rect)
            pygame.draw.rect(surface, status_color, item_rect, 2)

            # Status indicator
            status_text = self.font_normal.render(status, True, status_color)
            surface.blit(status_text, (list_x + 5, item_y + 5))

            # Name
            name = research.get('name', tech_id)
            name_text = self.font_normal.render(name, True, self.text_color)
            if name_text.get_width() > list_width - 40:
                # Truncate if too long
                name = name[:20] + "..."
                name_text = self.font_normal.render(name, True, self.text_color)
            surface.blit(name_text, (list_x + 30, item_y + 5))

            # Cost and time
            cost = research.get('cost', 0)
            time = research.get('time', 0)
            info_text = self.font_small.render(
                f"${cost}  •  {time}s",
                True, (200, 200, 200)
            )
            surface.blit(info_text, (list_x + 30, item_y + 32))

    def _render_research_details(self, surface, research_manager, money: float, start_x: int, start_y: int):
        """Render detailed view of selected research."""
        research = research_manager.get_research(self.selected_research)
        if not research:
            return

        tech_id = research['id']
        y = start_y

        # Panel background
        details_rect = pygame.Rect(start_x, start_y, self.details_width, self.panel_height - start_y - 40)
        pygame.draw.rect(surface, self.panel_color, details_rect)
        pygame.draw.rect(surface, self.text_color, details_rect, 1)

        # Name
        name = research.get('name', tech_id)
        name_text = self.font_normal.render(name, True, self.text_color)
        surface.blit(name_text, (start_x + 10, y + 10))
        y += 40

        # Description
        desc = research.get('description', 'No description available')
        # Wrap text
        words = desc.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if self.font_small.size(test_line)[0] > self.details_width - 30:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        for line in lines[:3]:  # Max 3 lines
            line_text = self.font_small.render(line, True, (220, 220, 220))
            surface.blit(line_text, (start_x + 10, y))
            y += 22

        y += 20

        # Cost
        cost = research.get('cost', 0)
        cost_color = self.available_color if money >= cost else (200, 50, 50)
        cost_text = self.font_normal.render(f"Cost: ${cost}", True, cost_color)
        surface.blit(cost_text, (start_x + 10, y))
        y += 30

        # Time
        time = research.get('time', 0)
        time_text = self.font_normal.render(f"Time: {time} seconds", True, self.text_color)
        surface.blit(time_text, (start_x + 10, y))
        y += 30

        # Prerequisites
        prereqs = research.get('prerequisites', [])
        prereq_text = self.font_normal.render("Prerequisites:", True, self.text_color)
        surface.blit(prereq_text, (start_x + 10, y))
        y += 25

        if not prereqs:
            none_text = self.font_small.render("None", True, (150, 150, 150))
            surface.blit(none_text, (start_x + 20, y))
            y += 25
        else:
            for prereq_id in prereqs:
                prereq_research = research_manager.get_research(prereq_id)
                prereq_name = prereq_research.get('name', prereq_id) if prereq_research else prereq_id

                if research_manager.is_completed(prereq_id):
                    prereq_color = self.completed_color
                    status = "✓"
                else:
                    prereq_color = (200, 50, 50)
                    status = "✗"

                prereq_text = self.font_small.render(f"{status} {prereq_name}", True, prereq_color)
                surface.blit(prereq_text, (start_x + 20, y))
                y += 22

        y += 20

        # Effects
        effects = research.get('effects', {})
        if effects:
            effects_text = self.font_normal.render("Effects:", True, self.text_color)
            surface.blit(effects_text, (start_x + 10, y))
            y += 25

            for effect_name, effect_value in effects.items():
                effect_str = effect_name.replace('_', ' ').title()
                multiplier = (effect_value - 1.0) * 100
                sign = "+" if multiplier >= 0 else ""
                effect_text = self.font_small.render(
                    f"{effect_str}: {sign}{multiplier:.0f}%",
                    True, self.available_color
                )
                surface.blit(effect_text, (start_x + 20, y))
                y += 22

        # Buttons
        button_y = self.panel_height - 80

        # Start button (if available)
        if research_manager.current_research is None:
            if research_manager.is_available(tech_id) and not research_manager.is_completed(tech_id):
                can_afford = research_manager.can_afford(tech_id, money)
                button_color = self.button_color if can_afford else self.locked_color

                self.start_button_rect = pygame.Rect(
                    self.panel_x + start_x + 10,
                    self.panel_y + button_y,
                    150, 40
                )

                local_rect = pygame.Rect(start_x + 10, button_y, 150, 40)
                pygame.draw.rect(surface, button_color, local_rect)
                pygame.draw.rect(surface, self.text_color, local_rect, 2)

                button_text = self.font_normal.render("Start Research", True, self.text_color)
                text_x = local_rect.centerx - button_text.get_width() // 2
                text_y = local_rect.centery - button_text.get_height() // 2
                surface.blit(button_text, (text_x, text_y))

        # Cancel button (if in progress)
        if research_manager.current_research == tech_id:
            self.cancel_button_rect = pygame.Rect(
                self.panel_x + start_x + 10,
                self.panel_y + button_y,
                150, 40
            )

            local_rect = pygame.Rect(start_x + 10, button_y, 150, 40)
            pygame.draw.rect(surface, (200, 50, 50), local_rect)
            pygame.draw.rect(surface, self.text_color, local_rect, 2)

            button_text = self.font_normal.render("Cancel", True, self.text_color)
            text_x = local_rect.centerx - button_text.get_width() // 2
            text_y = local_rect.centery - button_text.get_height() // 2
            surface.blit(button_text, (text_x, text_y))

            # Show progress
            progress = research_manager.get_research_progress()
            progress_y = button_y - 30
            progress_width = 150
            progress_height = 20

            # Background
            progress_rect = pygame.Rect(start_x + 10, progress_y, progress_width, progress_height)
            pygame.draw.rect(surface, (60, 60, 60), progress_rect)

            # Fill
            fill_width = int(progress_width * progress)
            fill_rect = pygame.Rect(start_x + 10, progress_y, fill_width, progress_height)
            pygame.draw.rect(surface, self.in_progress_color, fill_rect)

            # Border
            pygame.draw.rect(surface, self.text_color, progress_rect, 1)

            # Percentage text
            progress_text = self.font_small.render(f"{progress * 100:.0f}%", True, self.text_color)
            surface.blit(progress_text, (start_x + 170, progress_y + 2))
