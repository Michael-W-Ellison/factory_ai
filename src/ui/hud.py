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

    def render(self, screen, resource_manager, entity_manager, clock=None, power_manager=None, building_manager=None, research_manager=None, suspicion_manager=None):
        """
        Render the HUD.

        Args:
            screen: Pygame surface
            resource_manager: ResourceManager instance
            entity_manager: EntityManager instance
            clock: Pygame clock (optional, for FPS display)
            power_manager: PowerManager instance (optional)
            building_manager: BuildingManager instance (optional)
            research_manager: ResearchManager instance (optional)
            suspicion_manager: SuspicionManager instance (optional)
        """
        # Top-left panel: Resources and money
        self._render_resources_panel(screen, resource_manager, entity_manager)

        # Top-right panel: Robot info or Power info
        if entity_manager.selected_robot:
            self._render_robot_panel(screen, entity_manager.selected_robot)
        elif power_manager and building_manager:
            self._render_power_panel(screen, power_manager, building_manager)

        # Bottom-left: Controls help
        self._render_controls_help(screen)

        # Top-center: FPS (if clock provided)
        if clock:
            self._render_fps(screen, clock)

        # Top-center: Research progress (if active)
        if research_manager and research_manager.current_research:
            self._render_research_progress(screen, research_manager)

        # Bottom-center: Suspicion meter (if available)
        if suspicion_manager:
            self._render_suspicion_meter(screen, suspicion_manager)

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

    def _render_power_panel(self, screen, power_manager, building_manager):
        """Render power system info panel at top-right."""
        panel_width = 240
        panel_height = 200
        panel_x = self.screen_width - panel_width - 10
        panel_y = 10
        line_height = 20

        # Background panel
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(180)
        panel_surface.fill(self.color_bg)
        screen.blit(panel_surface, (panel_x, panel_y))

        # Title
        title_text = self.font_medium.render("Power System", True, self.color_good)
        screen.blit(title_text, (panel_x + 10, panel_y + 10))

        y_offset = 35

        # Power generation
        generation = power_manager.total_generation
        gen_text = self.font_small.render(
            f"Generation: {generation:.1f}W",
            True, self.color_good
        )
        screen.blit(gen_text, (panel_x + 10, panel_y + y_offset))
        y_offset += line_height

        # Power consumption
        consumption = power_manager.total_consumption
        cons_color = self.color_warning if consumption > generation else self.color_text
        cons_text = self.font_small.render(
            f"Consumption: {consumption:.1f}W",
            True, cons_color
        )
        screen.blit(cons_text, (panel_x + 10, panel_y + y_offset))
        y_offset += line_height

        # Net power
        net_power = generation - consumption
        if net_power > 0:
            net_color = self.color_good
            net_label = "Surplus:"
        elif net_power < 0:
            net_color = self.color_bad
            net_label = "Deficit:"
        else:
            net_color = self.color_text
            net_label = "Net:"

        net_text = self.font_small.render(
            f"{net_label} {abs(net_power):.1f}W",
            True, net_color
        )
        screen.blit(net_text, (panel_x + 10, panel_y + y_offset))
        y_offset += line_height + 5

        # Stored power
        stored = power_manager.current_power
        max_storage = power_manager.max_storage
        storage_ratio = stored / max_storage if max_storage > 0 else 0

        if storage_ratio < 0.2:
            storage_color = self.color_bad
        elif storage_ratio < 0.5:
            storage_color = self.color_warning
        else:
            storage_color = self.color_good

        storage_text = self.font_small.render(
            f"Storage: {stored:.0f}/{max_storage:.0f}",
            True, storage_color
        )
        screen.blit(storage_text, (panel_x + 10, panel_y + y_offset))
        y_offset += line_height

        # Storage bar
        bar_x = panel_x + 10
        bar_y = panel_y + y_offset
        bar_width = panel_width - 20
        bar_height = 15

        # Background bar
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # Fill bar
        if storage_ratio > 0:
            fill_width = int(bar_width * storage_ratio)
            pygame.draw.rect(screen, storage_color, (bar_x, bar_y, fill_width, bar_height))

        # Border
        pygame.draw.rect(screen, (150, 150, 150), (bar_x, bar_y, bar_width, bar_height), 1)

        y_offset += line_height + 5

        # System status
        if power_manager.blackout:
            status = "STATUS: BLACKOUT"
            status_color = self.color_bad
        elif power_manager.brownout:
            status = "STATUS: BROWNOUT"
            status_color = self.color_warning
        elif net_power > 0:
            status = "STATUS: NORMAL"
            status_color = self.color_good
        else:
            status = "STATUS: BALANCED"
            status_color = self.color_text

        status_text = self.font_small.render(status, True, status_color)
        screen.blit(status_text, (panel_x + 10, panel_y + y_offset))
        y_offset += line_height + 5

        # Building counts
        building_stats = building_manager.get_building_counts()
        total_buildings = sum(building_stats.values())

        buildings_text = self.font_small.render(
            f"Buildings: {total_buildings}",
            True, self.color_text
        )
        screen.blit(buildings_text, (panel_x + 10, panel_y + y_offset))

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

    def _render_research_progress(self, screen, research_manager):
        """
        Render research progress indicator at top-center.

        Args:
            screen: Pygame surface
            research_manager: ResearchManager instance
        """
        if not research_manager.current_research:
            return

        research = research_manager.get_research(research_manager.current_research)
        if not research:
            return

        # Panel dimensions
        panel_width = 300
        panel_height = 80
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = 50  # Below FPS display

        # Background
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(180)
        panel_surface.fill(self.color_bg)
        screen.blit(panel_surface, (panel_x, panel_y))

        # Research name
        name = research.get('name', 'Unknown')
        if len(name) > 30:
            name = name[:27] + "..."
        name_text = self.font_medium.render(name, True, self.color_text)
        name_rect = name_text.get_rect(centerx=panel_x + panel_width // 2, top=panel_y + 5)
        screen.blit(name_text, name_rect)

        # Progress bar
        progress = research_manager.get_research_progress()
        bar_width = panel_width - 20
        bar_height = 20
        bar_x = panel_x + 10
        bar_y = panel_y + 35

        # Background
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))

        # Fill (yellow/orange for in-progress)
        fill_width = int(bar_width * progress)
        fill_color = (255, 200, 50)
        pygame.draw.rect(screen, fill_color, (bar_x, bar_y, fill_width, bar_height))

        # Border
        pygame.draw.rect(screen, (150, 150, 150), (bar_x, bar_y, bar_width, bar_height), 2)

        # Percentage and time remaining
        progress_pct = progress * 100
        time_elapsed = research_manager.research_progress
        time_total = research_manager.research_time_required
        time_remaining = max(0, time_total - time_elapsed)

        info_text = self.font_small.render(
            f"{progress_pct:.0f}%  •  {time_remaining:.0f}s remaining",
            True, self.color_text
        )
        info_rect = info_text.get_rect(centerx=panel_x + panel_width // 2, top=bar_y + bar_height + 5)
        screen.blit(info_text, info_rect)
    def _render_suspicion_meter(self, screen, suspicion_manager):
        """Render the suspicion meter at bottom-center."""
        meter_width = 300
        meter_height = 40
        meter_x = (self.screen_width - meter_width) // 2
        meter_y = self.screen_height - meter_height - 60

        # Background panel
        panel_surface = pygame.Surface((meter_width, meter_height))
        panel_surface.set_alpha(200)
        panel_surface.fill(self.color_bg)
        screen.blit(panel_surface, (meter_x, meter_y))

        # Tier and level
        tier_name = suspicion_manager.tier_names[suspicion_manager.current_tier]
        level = suspicion_manager.suspicion_level

        # Tier color
        tier_color = suspicion_manager.tier_colors[suspicion_manager.current_tier]

        # Title
        title_text = self.font_small.render("SUSPICION", True, self.color_text)
        screen.blit(title_text, (meter_x + 10, meter_y + 5))

        # Progress bar
        bar_width = meter_width - 20
        bar_height = 12
        bar_x = meter_x + 10
        bar_y = meter_y + 23

        # Background
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))

        # Fill based on suspicion level
        fill_width = int(bar_width * (level / 100.0))
        pygame.draw.rect(screen, tier_color, (bar_x, bar_y, fill_width, bar_height))

        # Tier markers (20, 40, 60, 80)
        for threshold in [20, 40, 60, 80]:
            marker_x = bar_x + int(bar_width * (threshold / 100.0))
            pygame.draw.line(screen, (150, 150, 150), (marker_x, bar_y), (marker_x, bar_y + bar_height), 2)

        # Border
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)

        # Level and tier text
        info_text = self.font_small.render(
            f"{level:.1f}  •  {tier_name}",
            True, tier_color
        )
        info_rect = info_text.get_rect(right=meter_x + meter_width - 10, centery=meter_y + 12)
        screen.blit(info_text, info_rect)
