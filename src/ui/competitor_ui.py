"""
Competitor UI - Display AI opponents, rankings, and market information.

Provides UI panels for competitive gameplay.
"""

import pygame
from typing import List, Dict, Optional, Tuple


class CompetitorPanel:
    """UI panel showing competitor information."""

    def __init__(self, x: int, y: int, width: int = 300, height: int = 500):
        """Initialize competitor panel."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True

        # Colors
        self.bg_color = (40, 40, 50, 220)
        self.border_color = (100, 100, 120)
        self.text_color = (255, 255, 255)
        self.highlight_color = (100, 200, 255)
        self.player_color = (100, 255, 100)

        # Fonts
        self.font_title = pygame.font.Font(None, 28)
        self.font_normal = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)

    def render(self, surface: pygame.Surface, leaderboard: List[Dict]):
        """
        Render the competitor panel.

        Args:
            surface: Surface to render on
            leaderboard: List of competitor info dicts
        """
        if not self.visible:
            return

        # Background
        panel_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, self.bg_color, (0, 0, self.width, self.height), border_radius=10)
        pygame.draw.rect(panel_surface, self.border_color, (0, 0, self.width, self.height), 2, border_radius=10)

        # Title
        title = self.font_title.render("Leaderboard", True, self.text_color)
        panel_surface.blit(title, (self.width // 2 - title.get_width() // 2, 10))

        # Headers
        y_offset = 50
        headers = ["Rank", "Company", "Score"]
        header_x = [20, 70, 220]

        for i, header in enumerate(headers):
            text = self.font_small.render(header, True, (180, 180, 180))
            panel_surface.blit(text, (header_x[i], y_offset))

        y_offset += 25

        # Separator line
        pygame.draw.line(panel_surface, self.border_color, (10, y_offset), (self.width - 10, y_offset), 1)
        y_offset += 10

        # Leaderboard entries
        for i, entry in enumerate(leaderboard[:8]):  # Show top 8
            rank = entry['rank']
            name = entry['name']
            score = entry['score']
            is_player = entry.get('is_player', False)

            # Highlight player or top 3
            if is_player:
                entry_color = self.player_color
                pygame.draw.rect(panel_surface, (50, 100, 50, 100),
                               (5, y_offset - 2, self.width - 10, 25), border_radius=5)
            elif rank <= 3:
                entry_color = self.highlight_color
            else:
                entry_color = self.text_color

            # Rank
            rank_text = self.font_normal.render(f"#{rank}", True, entry_color)
            panel_surface.blit(rank_text, (20, y_offset))

            # Company name (truncate if too long)
            if len(name) > 18:
                name = name[:15] + "..."
            name_text = self.font_normal.render(name, True, entry_color)
            panel_surface.blit(name_text, (70, y_offset))

            # Score
            score_str = f"${score:,}" if score > 1000 else str(score)
            score_text = self.font_normal.render(score_str, True, entry_color)
            panel_surface.blit(score_text, (220, y_offset))

            y_offset += 30

            if y_offset > self.height - 40:
                break

        surface.blit(panel_surface, (self.x, self.y))


class MarketPanel:
    """UI panel showing market conditions."""

    def __init__(self, x: int, y: int, width: int = 250, height: int = 200):
        """Initialize market panel."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True

        # Colors
        self.bg_color = (40, 40, 50, 220)
        self.border_color = (100, 100, 120)
        self.text_color = (255, 255, 255)
        self.positive_color = (100, 255, 100)
        self.negative_color = (255, 100, 100)

        # Fonts
        self.font_title = pygame.font.Font(None, 24)
        self.font_normal = pygame.font.Font(None, 18)

    def render(self, surface: pygame.Surface, market_data: Dict):
        """
        Render the market panel.

        Args:
            surface: Surface to render on
            market_data: Market conditions dict
        """
        if not self.visible:
            return

        # Background
        panel_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, self.bg_color, (0, 0, self.width, self.height), border_radius=10)
        pygame.draw.rect(panel_surface, self.border_color, (0, 0, self.width, self.height), 2, border_radius=10)

        # Title
        title = self.font_title.render("Market", True, self.text_color)
        panel_surface.blit(title, (self.width // 2 - title.get_width() // 2, 10))

        y_offset = 45

        # Demand
        demand = market_data.get('market_demand', 1.0)
        demand_color = self.positive_color if demand > 1.0 else self.negative_color if demand < 0.9 else self.text_color
        demand_text = self.font_normal.render(f"Demand: {demand:.2f}x", True, demand_color)
        panel_surface.blit(demand_text, (20, y_offset))
        y_offset += 30

        # Price
        price_mult = market_data.get('price_multiplier', 1.0)
        price_color = self.positive_color if price_mult > 1.1 else self.negative_color if price_mult < 0.9 else self.text_color
        price_text = self.font_normal.render(f"Price: {price_mult:.2f}x", True, price_color)
        panel_surface.blit(price_text, (20, y_offset))
        y_offset += 30

        # Police Activity
        police = market_data.get('police_activity', 0.3)
        police_color = self.negative_color if police > 0.7 else self.text_color
        police_text = self.font_normal.render(f"Police: {int(police * 100)}%", True, police_color)
        panel_surface.blit(police_text, (20, y_offset))
        y_offset += 30

        # Investigation
        investigation = market_data.get('investigation_active', False)
        if investigation:
            inv_text = self.font_normal.render("! INVESTIGATION !", True, self.negative_color)
            panel_surface.blit(inv_text, (20, y_offset))

        surface.blit(panel_surface, (self.x, self.y))


class OpponentDetailPanel:
    """Detailed view of a specific opponent."""

    def __init__(self, x: int, y: int, width: int = 350, height: int = 300):
        """Initialize opponent detail panel."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = False  # Hidden by default

        # Colors
        self.bg_color = (40, 40, 50, 240)
        self.border_color = (100, 100, 120)
        self.text_color = (255, 255, 255)
        self.label_color = (180, 180, 180)

        # Fonts
        self.font_title = pygame.font.Font(None, 26)
        self.font_normal = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)

    def render(self, surface: pygame.Surface, opponent_stats: Dict):
        """
        Render opponent details.

        Args:
            surface: Surface to render on
            opponent_stats: Opponent statistics dict
        """
        if not self.visible or not opponent_stats:
            return

        # Background
        panel_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, self.bg_color, (0, 0, self.width, self.height), border_radius=10)
        pygame.draw.rect(panel_surface, self.border_color, (0, 0, self.width, self.height), 2, border_radius=10)

        # Title (Company name)
        title = self.font_title.render(opponent_stats.get('name', 'Unknown'), True, self.text_color)
        panel_surface.blit(title, (self.width // 2 - title.get_width() // 2, 10))

        # Personality
        personality = opponent_stats.get('personality', 'balanced')
        pers_text = self.font_small.render(f"Strategy: {personality.title()}", True, self.label_color)
        panel_surface.blit(pers_text, (self.width // 2 - pers_text.get_width() // 2, 40))

        y_offset = 70

        # Stats
        stats = [
            ("Money", f"${opponent_stats.get('money', 0):,}"),
            ("Net Worth", f"${opponent_stats.get('net_worth', 0):,}"),
            ("Profit", f"${opponent_stats.get('profit', 0):,}"),
            ("Workers", str(opponent_stats.get('workers', 0))),
            ("Workstations", str(opponent_stats.get('workstations', 0))),
            ("Tech Level", str(opponent_stats.get('technology_level', 1))),
            ("Market Share", f"{opponent_stats.get('market_share', 0) * 100:.1f}%"),
            ("Heat Level", f"{opponent_stats.get('heat_level', 0):.0f}"),
        ]

        for label, value in stats:
            label_text = self.font_small.render(label + ":", True, self.label_color)
            panel_surface.blit(label_text, (20, y_offset))

            value_text = self.font_normal.render(value, True, self.text_color)
            panel_surface.blit(value_text, (180, y_offset))

            y_offset += 25

        # Current goal
        goal = opponent_stats.get('current_goal', 'unknown')
        goal_text = self.font_small.render(f"Goal: {goal.replace('_', ' ').title()}", True, (100, 200, 255))
        panel_surface.blit(goal_text, (20, y_offset + 10))

        surface.blit(panel_surface, (self.x, self.y))

    def toggle(self):
        """Toggle panel visibility."""
        self.visible = not self.visible
