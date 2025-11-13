"""
HUD (Heads-Up Display) - displays game information to the player.
"""

import pygame


class HUD:
    """
    Displays game information on screen.

    Shows resources, robot status, money, and other important information.
    """

    def __init__(self, screen_width, screen_height):
        """
        Initialize the HUD.

        Args:
            screen_width (int): Width of game screen
            screen_height (int): Height of game screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Fonts
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 32)

        # Colors
        self.color_text = (255, 255, 255)
        self.color_money = (255, 215, 0)  # Gold
        self.color_good = (0, 255, 0)
        self.color_warning = (255, 255, 0)
        self.color_bad = (255, 100, 100)
        self.color_bg = (0, 0, 0)

    def render(self, screen, resource_manager, entity_manager, clock=None):
        """
        Render the HUD.

        Args:
            screen: Pygame surface
            resource_manager: ResourceManager instance
            entity_manager: EntityManager instance
            clock: Pygame clock (optional, for FPS display)
        """
        # Top-left panel: Resources and money
        self._render_resources_panel(screen, resource_manager, entity_manager)

        # Top-right panel: Robot info
        if entity_manager.selected_robot:
            self._render_robot_panel(screen, entity_manager.selected_robot)

        # Bottom-left: Controls help
        self._render_controls_help(screen)

        # Top-center: FPS (if clock provided)
        if clock:
            self._render_fps(screen, clock)

    def _render_resources_panel(self, screen, resource_manager, entity_manager):
        """Render the resources panel at top-left."""
        panel_x = 10
        panel_y = 10
        line_height = 22

        # Background panel
        panel_width = 250
        panel_height = 120
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(180)
        panel_surface.fill(self.color_bg)
        screen.blit(panel_surface, (panel_x, panel_y))

        # Money
        money_text = self.font_medium.render(
            f"Money: ${resource_manager.money:.2f}",
            True, self.color_money
        )
        screen.blit(money_text, (panel_x + 10, panel_y + 10))

        # Total stored materials
        total_weight = resource_manager.get_total_stored_weight()
        stored_text = self.font_small.render(
            f"Stored: {total_weight:.1f}kg",
            True, self.color_text
        )
        screen.blit(stored_text, (panel_x + 10, panel_y + 35))

        # Stored value
        total_value = resource_manager.get_total_stored_value()
        value_text = self.font_small.render(
            f"Value: ${total_value:.2f}",
            True, self.color_good
        )
        screen.blit(value_text, (panel_x + 10, panel_y + 55))

        # Entity counts
        entity_stats = entity_manager.get_stats()
        entities_text = self.font_small.render(
            f"Robots: {entity_stats['robots']}  Collectibles: {entity_stats['collectibles']}",
            True, self.color_text
        )
        screen.blit(entities_text, (panel_x + 10, panel_y + 80))

    def _render_robot_panel(self, screen, robot):
        """Render selected robot info panel at top-right."""
        panel_width = 220
        panel_height = 165
        panel_x = self.screen_width - panel_width - 10
        panel_y = 10
        line_height = 20

        # Background panel
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(180)
        panel_surface.fill(self.color_bg)
        screen.blit(panel_surface, (panel_x, panel_y))

        # Title
        mode = "AUTO" if robot.autonomous else "MANUAL"
        title_text = self.font_medium.render(
            f"Robot #{robot.id} [{mode}]",
            True, self.color_good
        )
        screen.blit(title_text, (panel_x + 10, panel_y + 10))

        # State (for autonomous robots)
        if robot.autonomous:
            state_name = robot.state.name if hasattr(robot.state, 'name') else str(robot.state)
            state_text = self.font_small.render(
                f"State: {state_name}",
                True, self.color_text
            )
            screen.blit(state_text, (panel_x + 10, panel_y + 35))

        # Inventory load
        load_ratio = robot.current_load / robot.max_capacity if robot.max_capacity > 0 else 0
        if load_ratio >= 0.9:
            load_color = self.color_bad
        elif load_ratio >= 0.7:
            load_color = self.color_warning
        else:
            load_color = self.color_good

        y_offset = 55 if robot.autonomous else 35
        load_text = self.font_small.render(
            f"Load: {robot.current_load:.1f}/{robot.max_capacity}kg",
            True, load_color
        )
        screen.blit(load_text, (panel_x + 10, panel_y + y_offset))

        # Power
        power_ratio = robot.current_power / robot.power_capacity if robot.power_capacity > 0 else 0
        if power_ratio < 0.2:
            power_color = self.color_bad
        elif power_ratio < 0.5:
            power_color = self.color_warning
        else:
            power_color = self.color_good

        y_offset += 20
        power_text = self.font_small.render(
            f"Power: {robot.current_power:.0f}/{robot.power_capacity}",
            True, power_color
        )
        screen.blit(power_text, (panel_x + 10, panel_y + y_offset))

        # Inventory contents (top 3 materials)
        y_offset += 25
        if robot.inventory:
            inv_title = self.font_small.render("Inventory:", True, self.color_text)
            screen.blit(inv_title, (panel_x + 10, panel_y + y_offset))
            y_offset += line_height

            # Sort by quantity (descending) and show top 3
            sorted_inv = sorted(robot.inventory.items(), key=lambda x: x[1], reverse=True)
            for material_type, quantity in sorted_inv[:3]:
                inv_text = self.font_small.render(
                    f"  {material_type}: {quantity:.1f}kg",
                    True, self.color_text
                )
                screen.blit(inv_text, (panel_x + 10, panel_y + y_offset))
                y_offset += line_height
        else:
            empty_text = self.font_small.render("Inventory: Empty", True, self.color_text)
            screen.blit(empty_text, (panel_x + 10, panel_y + y_offset))

    def _render_controls_help(self, screen):
        """Render controls help at bottom-left."""
        panel_x = 10
        panel_y = self.screen_height - 130
        line_height = 22

        # Background panel
        panel_width = 280
        panel_height = 120
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(150)
        panel_surface.fill(self.color_bg)
        screen.blit(panel_surface, (panel_x, panel_y))

        # Controls
        controls = [
            "Arrow Keys: Move robot",
            "Click: Select robot",
            "WASD: Move camera",
            "G: Toggle grid",
            "Space: Pause",
        ]

        for i, control in enumerate(controls):
            text = self.font_small.render(control, True, (200, 200, 200))
            screen.blit(text, (panel_x + 10, panel_y + 10 + i * line_height))

    def _render_fps(self, screen, clock):
        """Render FPS counter at top-center."""
        fps = int(clock.get_fps())

        # Color based on FPS
        if fps >= 55:
            fps_color = self.color_good
        elif fps >= 30:
            fps_color = self.color_warning
        else:
            fps_color = self.color_bad

        fps_text = self.font_medium.render(f"FPS: {fps}", True, fps_color)
        text_rect = fps_text.get_rect(center=(self.screen_width // 2, 20))

        # Background
        bg_rect = pygame.Rect(text_rect.x - 5, text_rect.y - 2, text_rect.width + 10, text_rect.height + 4)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(180)
        bg_surface.fill(self.color_bg)
        screen.blit(bg_surface, bg_rect)

        screen.blit(fps_text, text_rect)

    def render_message(self, screen, message, duration=2.0):
        """
        Render a temporary message in the center of the screen.

        Args:
            screen: Pygame surface
            message (str): Message to display
            duration (float): How long to show (seconds) - not implemented yet
        """
        text = self.font_large.render(message, True, self.color_money)
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))

        # Semi-transparent background
        bg_width = text_rect.width + 40
        bg_height = text_rect.height + 20
        bg_surface = pygame.Surface((bg_width, bg_height))
        bg_surface.set_alpha(200)
        bg_surface.fill(self.color_bg)
        bg_rect = bg_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        screen.blit(bg_surface, bg_rect)

        screen.blit(text, text_rect)
