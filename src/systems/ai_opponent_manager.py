"""
AI Opponent Manager - Manages competing AI factories and competitive market.

Handles multiple AI opponents, market dynamics, rankings, and win conditions.
"""

import random
import math
from typing import List, Dict, Optional, Tuple
from enum import Enum

from entities.ai_factory import AIFactory, AIPersonality


class GameMode(Enum):
    """Game mode types."""
    SOLO = "solo"                    # Player vs environment only
    COMPETITIVE = "competitive"      # Player vs AI opponents
    TOURNAMENT = "tournament"        # Timed competition with rankings


class WinCondition(Enum):
    """Win condition types."""
    NET_WORTH = "net_worth"          # Highest net worth
    MARKET_SHARE = "market_share"    # Largest market share
    PROFIT = "profit"                # Most profit
    SURVIVAL = "survival"            # Last factory standing
    TIME_LIMIT = "time_limit"        # Best position after time limit


class AIOpponentManager:
    """
    Manages AI opponents and competitive market dynamics.

    Handles AI factories, market competition, rankings, and win conditions.
    """

    def __init__(self, num_opponents: int = 3, game_mode: GameMode = GameMode.COMPETITIVE,
                 win_condition: WinCondition = WinCondition.NET_WORTH):
        """
        Initialize AI opponent manager.

        Args:
            num_opponents: Number of AI opponents (1-5)
            game_mode: Game mode type
            win_condition: Victory condition
        """
        self.game_mode = game_mode
        self.win_condition = win_condition
        self.num_opponents = max(1, min(5, num_opponents))

        # AI opponents
        self.opponents: List[AIFactory] = []
        self._spawn_opponents()

        # Market
        self.total_market_size = 1000  # Total market units per period
        self.base_price = 1000  # Base price per unit
        self.price_multiplier = 1.0  # Market price multiplier
        self.demand_level = 1.0  # Market demand (0.5-2.0)

        # Competition
        self.market_period = 0
        self.time_elapsed = 0.0
        self.time_limit = 3600.0  # 1 hour for timed modes

        # Police/Environment
        self.police_activity = 0.3  # Base police activity level
        self.investigation_active = False

        # Rankings
        self.rankings: List[Tuple[str, int]] = []  # (name, score)
        self.winner: Optional[str] = None

        # Statistics
        self.total_production = 0
        self.total_sales = 0
        self.bankruptcies = 0

    def _spawn_opponents(self):
        """Spawn AI opponents with varied personalities."""
        company_names = [
            "GreenCycle Solutions",
            "EcoReclaim Industries",
            "Salvage Masters Inc.",
            "Planet Renewal Corp.",
            "ResourceReborn Ltd.",
            "CleanTech Recyclers",
            "SecondLife Materials Co.",
            "Sustainable Recovery Systems",
        ]

        random.shuffle(company_names)

        personalities = [
            AIPersonality.AGGRESSIVE,
            AIPersonality.BALANCED,
            AIPersonality.CAUTIOUS,
            AIPersonality.OPPORTUNIST,
            AIPersonality.INNOVATOR,
        ]

        for i in range(self.num_opponents):
            name = company_names[i]
            personality = personalities[i % len(personalities)]
            difficulty = random.uniform(0.3, 0.8)  # Varied difficulty

            opponent = AIFactory(
                name=name,
                personality=personality,
                difficulty=difficulty,
                starting_money=50000
            )
            self.opponents.append(opponent)

    def update(self, dt: float, player_factory: Optional[Dict] = None):
        """
        Update AI opponents and market.

        Args:
            dt: Delta time in seconds
            player_factory: Player's factory stats (optional)
        """
        self.time_elapsed += dt

        # Update market conditions
        self._update_market(dt)

        # Get current market conditions
        market_conditions = self.get_market_conditions()

        # Update each AI opponent
        for opponent in self.opponents[:]:  # Copy list to allow removal
            opponent.update(dt, market_conditions, self.police_activity)

            # Check for bankruptcy
            if opponent.money < -50000:  # Allow some debt
                self.opponents.remove(opponent)
                self.bankruptcies += 1

        # Update market shares
        self._update_market_shares(player_factory)

        # Update rankings
        self._update_rankings(player_factory)

        # Check win conditions
        if self.game_mode == GameMode.COMPETITIVE:
            self._check_win_condition(player_factory)

    def _update_market(self, dt: float):
        """Update market conditions."""
        # Market cycles
        cycle_time = self.time_elapsed / 60.0  # Minutes

        # Demand fluctuates
        demand_wave = math.sin(cycle_time * 0.1) * 0.3
        self.demand_level = 1.0 + demand_wave + random.uniform(-0.1, 0.1)
        self.demand_level = max(0.5, min(2.0, self.demand_level))

        # Price follows supply/demand
        total_inventory = sum(opp.materials_inventory for opp in self.opponents)
        supply_pressure = total_inventory / max(1, self.total_market_size)

        # High supply = lower prices, low supply = higher prices
        self.price_multiplier = 1.0 + (1.0 - supply_pressure) * 0.5
        self.price_multiplier += random.uniform(-0.1, 0.1)  # Random fluctuation
        self.price_multiplier = max(0.5, min(2.0, self.price_multiplier))

        # Police activity varies
        self.police_activity += random.uniform(-0.05, 0.05)
        self.police_activity = max(0.1, min(0.9, self.police_activity))

        # Occasional investigations
        if random.random() < 0.001:  # 0.1% chance per tick
            self.investigation_active = True
            self.police_activity = min(1.0, self.police_activity + 0.3)

        if self.investigation_active and random.random() < 0.01:
            self.investigation_active = False

    def _update_market_shares(self, player_factory: Optional[Dict]):
        """Calculate market shares for all participants."""
        total_sales = sum(opp.sales_this_period for opp in self.opponents)

        if player_factory:
            total_sales += player_factory.get('sales', 0)

        if total_sales > 0:
            for opponent in self.opponents:
                opponent.market_share = opponent.sales_this_period / total_sales

            if player_factory and 'market_share' in player_factory:
                player_sales = player_factory.get('sales', 0)
                player_factory['market_share'] = player_sales / total_sales

        # Reset period sales
        for opponent in self.opponents:
            opponent.sales_this_period = 0

    def _update_rankings(self, player_factory: Optional[Dict]):
        """Update competitive rankings."""
        scores = []

        # Score AI opponents
        for opponent in self.opponents:
            score = self._calculate_score(opponent.get_statistics())
            scores.append((opponent.name, score, False))  # False = AI

        # Score player
        if player_factory:
            player_score = self._calculate_score(player_factory)
            scores.append(("Player", player_score, True))  # True = player

        # Sort by score (descending)
        scores.sort(key=lambda x: x[1], reverse=True)

        self.rankings = [(name, score) for name, score, _ in scores]

    def _calculate_score(self, factory_stats: Dict) -> int:
        """
        Calculate competitive score based on win condition.

        Args:
            factory_stats: Factory statistics

        Returns:
            int: Calculated score
        """
        if self.win_condition == WinCondition.NET_WORTH:
            return factory_stats.get('net_worth', 0)
        elif self.win_condition == WinCondition.MARKET_SHARE:
            return int(factory_stats.get('market_share', 0) * 1000000)
        elif self.win_condition == WinCondition.PROFIT:
            return factory_stats.get('profit', 0)
        elif self.win_condition == WinCondition.SURVIVAL:
            # Score based on time survived + net worth
            return int(factory_stats.get('age', 0) * 100 + factory_stats.get('net_worth', 0))
        else:  # TIME_LIMIT
            return factory_stats.get('net_worth', 0)

    def _check_win_condition(self, player_factory: Optional[Dict]):
        """Check if win condition is met."""
        if self.winner:
            return  # Already have a winner

        if self.win_condition == WinCondition.SURVIVAL:
            # Win if only one factory remains
            remaining = len(self.opponents)
            if player_factory and player_factory.get('money', 0) < -50000:
                remaining -= 1  # Player bankrupt

            if remaining <= 1:
                # Find survivor
                if self.opponents:
                    self.winner = self.opponents[0].name
                elif player_factory:
                    self.winner = "Player"

        elif self.win_condition == WinCondition.TIME_LIMIT:
            # Win if time limit reached
            if self.time_elapsed >= self.time_limit:
                if self.rankings:
                    self.winner = self.rankings[0][0]

        else:
            # Win if score threshold reached
            threshold = {
                WinCondition.NET_WORTH: 1000000,
                WinCondition.MARKET_SHARE: 500000,  # 50% market share
                WinCondition.PROFIT: 500000,
            }.get(self.win_condition, 1000000)

            for name, score in self.rankings:
                if score >= threshold:
                    self.winner = name
                    break

    def get_market_conditions(self) -> Dict:
        """Get current market conditions for AI decision-making."""
        return {
            'demand': self.demand_level,
            'price_multiplier': self.price_multiplier,
            'total_market_size': self.total_market_size,
            'competition_level': len(self.opponents),
            'investigation_active': self.investigation_active,
        }

    def get_opponent_by_rank(self, rank: int) -> Optional[AIFactory]:
        """
        Get opponent by their current rank.

        Args:
            rank: Rank position (0 = first place)

        Returns:
            AIFactory or None
        """
        if 0 <= rank < len(self.rankings):
            name = self.rankings[rank][0]
            for opponent in self.opponents:
                if opponent.name == name:
                    return opponent
        return None

    def get_leaderboard(self) -> List[Dict]:
        """
        Get formatted leaderboard.

        Returns:
            List of dicts with rank info
        """
        leaderboard = []
        for i, (name, score) in enumerate(self.rankings):
            is_player = name == "Player"
            leaderboard.append({
                'rank': i + 1,
                'name': name,
                'score': score,
                'is_player': is_player,
            })
        return leaderboard

    def get_statistics(self) -> Dict:
        """Get comprehensive statistics."""
        return {
            'game_mode': self.game_mode.value,
            'win_condition': self.win_condition.value,
            'num_opponents': len(self.opponents),
            'time_elapsed': self.time_elapsed,
            'time_limit': self.time_limit if self.game_mode == GameMode.TOURNAMENT else None,
            'market_demand': self.demand_level,
            'price_multiplier': self.price_multiplier,
            'police_activity': self.police_activity,
            'investigation_active': self.investigation_active,
            'bankruptcies': self.bankruptcies,
            'winner': self.winner,
            'rankings': self.rankings,
        }


# Global AI opponent manager instance
_ai_opponent_manager = None


def get_ai_opponent_manager(num_opponents: int = 3,
                            game_mode: GameMode = GameMode.COMPETITIVE,
                            win_condition: WinCondition = WinCondition.NET_WORTH) -> AIOpponentManager:
    """
    Get the global AI opponent manager instance.

    Args:
        num_opponents: Number of AI opponents
        game_mode: Game mode
        win_condition: Win condition

    Returns:
        AIOpponentManager: The global instance
    """
    global _ai_opponent_manager
    if _ai_opponent_manager is None:
        _ai_opponent_manager = AIOpponentManager(num_opponents, game_mode, win_condition)
    return _ai_opponent_manager


def reset_ai_opponent_manager():
    """Reset the global AI opponent manager."""
    global _ai_opponent_manager
    _ai_opponent_manager = None
