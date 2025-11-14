"""
Phase 10 UI - UI components for advanced features.

Displays:
- Drone panel with status and controls
- Fog of war overlay
- Transmitter coverage visualization
- Market prices and trends
- Weather display
- Deconstruction progress
- Score and achievements
"""

import pygame
from typing import Dict, List, Tuple, Optional


class Phase10UI:
    """
    UI components for Phase 10 advanced features.

    Handles visualization for:
    - Drones and fog of war
    - Wireless transmitters
    - Market fluctuations
    - Weather system
    - Deconstruction jobs
    - Scoring and achievements
    """

    def __init__(self):
        """Initialize Phase 10 UI."""
        # Colors
        self.color_bg = (40, 40, 50)
        self.color_border = (80, 80, 100)
        self.color_text = (255, 255, 255)
        self.color_good = (100, 255, 100)
        self.color_warning = (255, 200, 50)
        self.color_danger = (255, 100, 100)
        self.color_neutral = (150, 150, 150)

        # Drone colors
        self.color_drone_idle = (100, 200, 255)
        self.color_drone_flying = (50, 255, 100)
        self.color_drone_returning = (255, 200, 50)
        self.color_drone_crashed = (255, 50, 50)

        # Fog of war colors
        self.color_unexplored = (20, 20, 30, 200)  # Dark overlay
        self.color_explored = (0, 0, 0, 0)  # Transparent

        # Panel positions and sizes
        self.drone_panel_rect = pygame.Rect(10, 500, 300, 200)
        self.market_panel_rect = pygame.Rect(1610, 10, 300, 250)
        self.weather_panel_rect = pygame.Rect(10, 10, 250, 120)
        self.score_panel_rect = pygame.Rect(1610, 270, 300, 200)

        # Fonts (will be set in render if not available)
        self.font_small = None
        self.font_medium = None
        self.font_large = None

    def _init_fonts(self):
        """Initialize fonts if not already done."""
        if self.font_small is None:
            self.font_small = pygame.font.Font(None, 18)
            self.font_medium = pygame.font.Font(None, 24)
            self.font_large = pygame.font.Font(None, 32)

    def render(self, screen, drone_manager=None, transmitter_manager=None,
               market_manager=None, weather_manager=None,
               deconstruction_manager=None, scoring_manager=None,
               camera_offset=(0, 0)):
        """
        Render all Phase 10 UI components.

        Args:
            screen: Pygame screen surface
            drone_manager: DroneManager instance
            transmitter_manager: TransmitterManager instance
            market_manager: MarketManager instance
            weather_manager: WeatherManager instance
            deconstruction_manager: DeconstructionManager instance
            scoring_manager: ScoringManager instance
            camera_offset: Camera offset for world-space rendering
        """
        self._init_fonts()

        # Render drone panel
        if drone_manager:
            self._render_drone_panel(screen, drone_manager)

        # Render market panel
        if market_manager:
            self._render_market_panel(screen, market_manager)

        # Render weather panel
        if weather_manager:
            self._render_weather_panel(screen, weather_manager)

        # Render score panel
        if scoring_manager:
            self._render_score_panel(screen, scoring_manager)

        # Render deconstruction jobs (if any)
        if deconstruction_manager:
            self._render_deconstruction_jobs(screen, deconstruction_manager)

    def _render_drone_panel(self, screen, drone_manager):
        """Render drone status panel."""
        # Background
        pygame.draw.rect(screen, self.color_bg, self.drone_panel_rect)
        pygame.draw.rect(screen, self.color_border, self.drone_panel_rect, 2)

        # Title
        title = self.font_medium.render("🚁 Drones", True, self.color_text)
        screen.blit(title, (self.drone_panel_rect.x + 10, self.drone_panel_rect.y + 10))

        # Drone counts
        counts = drone_manager.get_drone_count()
        y = self.drone_panel_rect.y + 45

        # Total drones
        text = self.font_small.render(f"Total: {counts['total']}/{drone_manager.max_drones}",
                                      True, self.color_text)
        screen.blit(text, (self.drone_panel_rect.x + 15, y))
        y += 25

        # Flying
        color = self.color_drone_flying if counts['flying'] > 0 else self.color_neutral
        text = self.font_small.render(f"Flying: {counts['flying']}", True, color)
        screen.blit(text, (self.drone_panel_rect.x + 15, y))
        y += 22

        # Returning
        if counts['returning'] > 0:
            text = self.font_small.render(f"Returning: {counts['returning']}",
                                          True, self.color_drone_returning)
            screen.blit(text, (self.drone_panel_rect.x + 15, y))
            y += 22

        # Charging
        if counts['charging'] > 0:
            text = self.font_small.render(f"Charging: {counts['charging']}",
                                          True, self.color_warning)
            screen.blit(text, (self.drone_panel_rect.x + 15, y))
            y += 22

        # Crashed
        if counts['crashed'] > 0:
            text = self.font_small.render(f"Crashed: {counts['crashed']}",
                                          True, self.color_drone_crashed)
            screen.blit(text, (self.drone_panel_rect.x + 15, y))
            y += 22

        # Exploration percentage
        y += 10
        exploration = drone_manager.get_exploration_percentage()
        text = self.font_small.render(f"Map Explored: {exploration:.1f}%",
                                      True, self.color_text)
        screen.blit(text, (self.drone_panel_rect.x + 15, y))

        # Exploration bar
        bar_rect = pygame.Rect(self.drone_panel_rect.x + 15, y + 22, 270, 15)
        pygame.draw.rect(screen, self.color_border, bar_rect, 1)

        fill_width = int((exploration / 100.0) * 268)
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_rect.x + 1, bar_rect.y + 1, fill_width, 13)
            pygame.draw.rect(screen, self.color_good, fill_rect)

    def _render_market_panel(self, screen, market_manager):
        """Render market prices and trends panel."""
        # Background
        pygame.draw.rect(screen, self.color_bg, self.market_panel_rect)
        pygame.draw.rect(screen, self.color_border, self.market_panel_rect, 2)

        # Title
        title = self.font_medium.render("📈 Market", True, self.color_text)
        screen.blit(title, (self.market_panel_rect.x + 10, self.market_panel_rect.y + 10))

        # Current trend
        trend_text = f"Trend: {market_manager.current_trend.name}"
        trend = self.font_small.render(trend_text, True, self.color_text)
        screen.blit(trend, (self.market_panel_rect.x + 15, self.market_panel_rect.y + 45))

        # Selected materials to show
        materials_to_show = ['plastic', 'metal', 'electronics', 'copper']

        y = self.market_panel_rect.y + 75
        for material in materials_to_show:
            # Material name
            name_text = material.title()[:8]  # Truncate if too long
            name = self.font_small.render(name_text, True, self.color_text)
            screen.blit(name, (self.market_panel_rect.x + 15, y))

            # Price
            price = market_manager.get_buy_price(material)
            price_text = f"${price:.1f}"
            price_surf = self.font_small.render(price_text, True, self.color_text)
            screen.blit(price_surf, (self.market_panel_rect.x + 100, y))

            # Trend indicator
            trend_symbol = market_manager.get_price_trend(material)
            trend_color = self.color_good if trend_symbol == "↑" else \
                         self.color_danger if trend_symbol == "↓" else \
                         self.color_neutral
            trend_surf = self.font_medium.render(trend_symbol, True, trend_color)
            screen.blit(trend_surf, (self.market_panel_rect.x + 170, y - 2))

            # Change percentage
            change = market_manager.get_price_change_percentage(material)
            change_text = f"{change:+.0f}%"
            change_color = self.color_good if change > 0 else \
                          self.color_danger if change < 0 else \
                          self.color_neutral
            change_surf = self.font_small.render(change_text, True, change_color)
            screen.blit(change_surf, (self.market_panel_rect.x + 210, y))

            y += 28

        # Active events
        if len(market_manager.active_events) > 0:
            y += 5
            events_text = f"Events: {len(market_manager.active_events)}"
            events = self.font_small.render(events_text, True, self.color_warning)
            screen.blit(events, (self.market_panel_rect.x + 15, y))

    def _render_weather_panel(self, screen, weather_manager):
        """Render weather status panel."""
        # Background
        pygame.draw.rect(screen, self.color_bg, self.weather_panel_rect)
        pygame.draw.rect(screen, self.color_border, self.weather_panel_rect, 2)

        # Weather description
        description = weather_manager.get_weather_description()
        weather_text = self.font_large.render(description, True, self.color_text)
        screen.blit(weather_text, (self.weather_panel_rect.x + 10, self.weather_panel_rect.y + 10))

        # Season
        season_text = f"Season: {weather_manager.current_season.title()}"
        season = self.font_small.render(season_text, True, self.color_text)
        screen.blit(season, (self.weather_panel_rect.x + 15, self.weather_panel_rect.y + 50))

        # Effects summary
        effects = weather_manager.get_current_effects()

        y = self.weather_panel_rect.y + 75

        # Production modifier
        if effects.production_modifier != 1.0:
            prod_change = (effects.production_modifier - 1.0) * 100
            prod_text = f"Production: {prod_change:+.0f}%"
            color = self.color_good if prod_change > 0 else self.color_danger
            prod = self.font_small.render(prod_text, True, color)
            screen.blit(prod, (self.weather_panel_rect.x + 15, y))
            y += 22

        # Suspicion modifier
        if effects.suspicion_modifier != 1.0:
            sus_change = (effects.suspicion_modifier - 1.0) * 100
            sus_text = f"Suspicion: {sus_change:+.0f}%"
            # Lower suspicion is good
            color = self.color_good if sus_change < 0 else self.color_danger
            sus = self.font_small.render(sus_text, True, color)
            screen.blit(sus, (self.weather_panel_rect.x + 15, y))

    def _render_score_panel(self, screen, scoring_manager):
        """Render score and achievements panel."""
        # Background
        pygame.draw.rect(screen, self.color_bg, self.score_panel_rect)
        pygame.draw.rect(screen, self.color_border, self.score_panel_rect, 2)

        # Title
        title = self.font_medium.render("🏆 Score", True, self.color_text)
        screen.blit(title, (self.score_panel_rect.x + 10, self.score_panel_rect.y + 10))

        # Current score (if game completed)
        y = self.score_panel_rect.y + 45
        if scoring_manager.game_completed:
            score_text = f"Total: {scoring_manager.total_score:,}"
            score = self.font_medium.render(score_text, True, self.color_good)
            screen.blit(score, (self.score_panel_rect.x + 15, y))
            y += 35

            # Rank
            rank_text = f"Rank: {scoring_manager.rank}"
            rank = self.font_small.render(rank_text, True, self.color_warning)
            screen.blit(rank, (self.score_panel_rect.x + 15, y))
            y += 25
        else:
            # Show live statistics
            stats_to_show = [
                ('Money Earned', f"${scoring_manager.stats['total_money_earned']:,.0f}"),
                ('Materials', f"{scoring_manager.stats['materials_processed']:.0f}"),
                ('Buildings', str(scoring_manager.stats['buildings_built'])),
            ]

            for stat_name, stat_value in stats_to_show:
                stat_text = f"{stat_name}: {stat_value}"
                stat = self.font_small.render(stat_text, True, self.color_text)
                screen.blit(stat, (self.score_panel_rect.x + 15, y))
                y += 22

            y += 10

        # Achievements
        unlocked, total = scoring_manager.get_achievement_progress()
        achievements_text = f"Achievements: {unlocked}/{total}"
        achievements = self.font_small.render(achievements_text, True, self.color_text)
        screen.blit(achievements, (self.score_panel_rect.x + 15, y))

        # Achievement bar
        bar_rect = pygame.Rect(self.score_panel_rect.x + 15, y + 22, 270, 12)
        pygame.draw.rect(screen, self.color_border, bar_rect, 1)

        if total > 0:
            fill_width = int((unlocked / total) * 268)
            if fill_width > 0:
                fill_rect = pygame.Rect(bar_rect.x + 1, bar_rect.y + 1, fill_width, 10)
                pygame.draw.rect(screen, self.color_warning, fill_rect)

        # Recent achievements (last 3)
        recent = scoring_manager.get_unlocked_achievements()[-3:]
        if recent:
            y += 45
            recent_text = "Recent:"
            recent_label = self.font_small.render(recent_text, True, self.color_neutral)
            screen.blit(recent_label, (self.score_panel_rect.x + 15, y))
            y += 20

            for achievement in recent:
                ach_text = f"{achievement.icon} {achievement.name[:18]}"
                ach = self.font_small.render(ach_text, True, self.color_good)
                screen.blit(ach, (self.score_panel_rect.x + 20, y))
                y += 18

    def _render_deconstruction_jobs(self, screen, deconstruction_manager):
        """Render active deconstruction jobs."""
        active_jobs = deconstruction_manager.get_active_jobs()

        if not active_jobs:
            return

        # Render job progress bars
        x = 320
        y = 500

        for job_id in active_jobs[:3]:  # Show max 3 jobs
            status = deconstruction_manager.get_job_status(job_id)

            if status:
                # Background
                job_rect = pygame.Rect(x, y, 280, 60)
                pygame.draw.rect(screen, self.color_bg, job_rect)
                pygame.draw.rect(screen, self.color_border, job_rect, 1)

                # Job info
                job_text = f"🔨 {status['target_type'].title()} #{status['target_id']}"
                job_label = self.font_small.render(job_text, True, self.color_text)
                screen.blit(job_label, (x + 10, y + 8))

                # Progress
                progress_text = f"{status['progress']:.0f}%"
                progress_label = self.font_small.render(progress_text, True, self.color_text)
                screen.blit(progress_label, (x + 10, y + 28))

                # Progress bar
                bar_rect = pygame.Rect(x + 80, y + 30, 190, 10)
                pygame.draw.rect(screen, self.color_border, bar_rect, 1)

                fill_width = int((status['progress'] / 100.0) * 188)
                if fill_width > 0:
                    fill_rect = pygame.Rect(bar_rect.x + 1, bar_rect.y + 1, fill_width, 8)
                    pygame.draw.rect(screen, self.color_warning, fill_rect)

                # Time remaining
                time_text = f"{status['time_remaining']:.0f}s"
                time_label = self.font_small.render(time_text, True, self.color_neutral)
                screen.blit(time_label, (x + 220, y + 8))

                y += 70

    def render_fog_of_war(self, screen, drone_manager, tile_size: int, camera_offset: Tuple[int, int]):
        """
        Render fog of war overlay.

        Args:
            screen: Pygame screen surface
            drone_manager: DroneManager instance
            tile_size: Size of each tile in pixels
            camera_offset: Camera offset (x, y)
        """
        if not drone_manager:
            return

        fog_of_war = drone_manager.fog_of_war

        # Create fog surface
        fog_surface = pygame.Surface(screen.get_size())
        fog_surface.set_alpha(200)
        fog_surface.fill((20, 20, 30))  # Dark overlay

        # Clear explored areas
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        # Calculate visible tile range
        cam_x, cam_y = camera_offset
        start_tile_x = int(-cam_x / tile_size) - 1
        start_tile_y = int(-cam_y / tile_size) - 1
        end_tile_x = start_tile_x + int(screen_width / tile_size) + 2
        end_tile_y = start_tile_y + int(screen_height / tile_size) + 2

        # Render only visible tiles
        for tile_x in range(start_tile_x, end_tile_x):
            for tile_y in range(start_tile_y, end_tile_y):
                if fog_of_war.is_explored((tile_x, tile_y)):
                    # Calculate screen position
                    screen_x = tile_x * tile_size + cam_x
                    screen_y = tile_y * tile_size + cam_y

                    # Clear this tile from fog
                    tile_rect = pygame.Rect(screen_x, screen_y, tile_size, tile_size)
                    pygame.draw.rect(fog_surface, (0, 0, 0, 0), tile_rect)

        # Draw fog surface
        screen.blit(fog_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    def render_drones_on_map(self, screen, drone_manager, tile_size: int, camera_offset: Tuple[int, int]):
        """
        Render drones on the map.

        Args:
            screen: Pygame screen surface
            drone_manager: DroneManager instance
            tile_size: Size of each tile in pixels
            camera_offset: Camera offset (x, y)
        """
        if not drone_manager:
            return

        cam_x, cam_y = camera_offset

        for drone in drone_manager.drones.values():
            # Calculate screen position
            screen_x = int(drone.position[0] * tile_size + cam_x)
            screen_y = int(drone.position[1] * tile_size + cam_y)

            # Choose color based on state
            from src.systems.drone_manager import DroneState
            if drone.state == DroneState.IDLE or drone.state == DroneState.CHARGING:
                color = self.color_drone_idle
            elif drone.state == DroneState.FLYING:
                color = self.color_drone_flying
            elif drone.state == DroneState.RETURNING:
                color = self.color_drone_returning
            else:  # CRASHED
                color = self.color_drone_crashed

            # Draw drone
            pygame.draw.circle(screen, color, (screen_x, screen_y), 6)

            # Draw battery indicator
            battery_width = int((drone.battery / 100.0) * 12)
            battery_rect = pygame.Rect(screen_x - 6, screen_y - 12, battery_width, 3)
            pygame.draw.rect(screen, color, battery_rect)

    def __repr__(self):
        """String representation for debugging."""
        return "Phase10UI()"
