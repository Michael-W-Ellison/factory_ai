"""
ScoringManager - manages player scoring and achievements.

Handles:
- Score calculation from various activities
- Achievement tracking
- Performance metrics
- End-game statistics
- Leaderboard data
"""

import math
from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


class ScoreCategory(Enum):
    """Score categories for breakdown."""
    MONEY_EARNED = "money_earned"  # Total money earned
    MATERIALS_PROCESSED = "materials_processed"  # Materials recycled
    BUILDINGS_BUILT = "buildings_built"  # Buildings constructed
    ILLEGAL_OPERATIONS = "illegal_operations"  # Illegal activities (penalty)
    TIME_SURVIVED = "time_survived"  # How long player survived
    EFFICIENCY = "efficiency"  # Production efficiency
    STEALTH = "stealth"  # Avoiding detection
    EXPLORATION = "exploration"  # Map exploration
    TECHNOLOGY = "technology"  # Research/upgrades
    ENDING_BONUS = "ending_bonus"  # Bonus for game ending type


@dataclass
class Achievement:
    """
    Player achievement.

    Attributes:
        id: Unique achievement identifier
        name: Achievement name
        description: Achievement description
        points: Points awarded
        unlocked: Whether achievement is unlocked
        unlock_time: When achievement was unlocked
        hidden: Whether achievement is hidden until unlocked
    """
    id: str
    name: str
    description: str
    points: int
    unlocked: bool = False
    unlock_time: float = 0.0
    hidden: bool = False
    icon: str = "🏆"


class ScoringManager:
    """
    Manages player scoring and achievements.

    Tracks performance across multiple metrics and calculates final score.
    """

    def __init__(self):
        """Initialize scoring manager."""
        # Score components
        self.scores = {
            ScoreCategory.MONEY_EARNED: 0,
            ScoreCategory.MATERIALS_PROCESSED: 0,
            ScoreCategory.BUILDINGS_BUILT: 0,
            ScoreCategory.ILLEGAL_OPERATIONS: 0,
            ScoreCategory.TIME_SURVIVED: 0,
            ScoreCategory.EFFICIENCY: 0,
            ScoreCategory.STEALTH: 0,
            ScoreCategory.EXPLORATION: 0,
            ScoreCategory.TECHNOLOGY: 0,
            ScoreCategory.ENDING_BONUS: 0,
        }

        # Score multipliers
        self.score_multipliers = {
            ScoreCategory.MONEY_EARNED: 0.01,  # 1 point per $100
            ScoreCategory.MATERIALS_PROCESSED: 1.0,  # 1 point per material
            ScoreCategory.BUILDINGS_BUILT: 50,  # 50 points per building
            ScoreCategory.ILLEGAL_OPERATIONS: -100,  # -100 per illegal op
            ScoreCategory.TIME_SURVIVED: 10,  # 10 points per game day
            ScoreCategory.EFFICIENCY: 100,  # Up to 100 points for efficiency
            ScoreCategory.STEALTH: 100,  # Up to 100 points for stealth
            ScoreCategory.EXPLORATION: 100,  # Up to 100 points for exploration
            ScoreCategory.TECHNOLOGY: 25,  # 25 points per tech level
            ScoreCategory.ENDING_BONUS: 1,  # Multiplier for ending bonus
        }

        # Achievements
        self.achievements: Dict[str, Achievement] = {}
        self._initialize_achievements()

        # Statistics tracking
        self.stats = {
            'total_money_earned': 0,
            'total_money_spent': 0,
            'materials_collected': 0,
            'materials_processed': 0,
            'products_sold': 0,
            'buildings_built': 0,
            'buildings_demolished': 0,
            'drones_deployed': 0,
            'drones_crashed': 0,
            'workers_hired': 0,
            'inspections_passed': 0,
            'inspections_failed': 0,
            'bribes_attempted': 0,
            'bribes_successful': 0,
            'escape_attempts': 0,
            'tiles_explored': 0,
            'time_played': 0.0,
            'max_suspicion': 0,
            'min_money': 0,
            'max_money': 0,
        }

        # Performance metrics
        self.efficiency_score = 0.0  # 0-1
        self.stealth_score = 0.0  # 0-1
        self.exploration_score = 0.0  # 0-1

        # Final score
        self.total_score = 0
        self.rank = "Novice"
        self.game_completed = False

    def _initialize_achievements(self):
        """Initialize achievement list."""
        achievements = [
            # Money achievements
            Achievement("first_dollar", "First Dollar", "Earn your first dollar", 10, icon="💵"),
            Achievement("millionaire", "Millionaire", "Accumulate $1,000,000", 100, icon="💰"),
            Achievement("big_spender", "Big Spender", "Spend $500,000", 50, icon="💸"),

            # Production achievements
            Achievement("first_product", "First Product", "Process your first material", 10, icon="♻️"),
            Achievement("mass_production", "Mass Production", "Process 10,000 materials", 100, icon="🏭"),
            Achievement("recycling_master", "Recycling Master", "Process 100,000 materials", 250, icon="🌟"),

            # Building achievements
            Achievement("builder", "Builder", "Construct 10 buildings", 50, icon="🏗️"),
            Achievement("architect", "Architect", "Construct 50 buildings", 150, icon="🏛️"),
            Achievement("city_planner", "City Planner", "Construct 100 buildings", 300, icon="🌆"),

            # Exploration achievements
            Achievement("explorer", "Explorer", "Explore 25% of the map", 50, icon="🗺️"),
            Achievement("cartographer", "Cartographer", "Explore 75% of the map", 150, icon="🧭"),
            Achievement("completionist", "Completionist", "Explore 100% of the map", 300, icon="🌍"),

            # Stealth achievements
            Achievement("ghost", "Ghost", "Complete game with <20 max suspicion", 200, icon="👻"),
            Achievement("invisible", "Invisible", "Never trigger inspection", 150, icon="🔍"),
            Achievement("smooth_operator", "Smooth Operator", "Never fail inspection", 100, icon="😎"),

            # Drone achievements
            Achievement("drone_pilot", "Drone Pilot", "Deploy 10 drones", 50, icon="🚁"),
            Achievement("air_force", "Air Force", "Own 5 drones simultaneously", 100, icon="✈️"),
            Achievement("crash_test", "Crash Test", "Crash 5 drones", 25, icon="💥", hidden=True),

            # Authority achievements
            Achievement("law_abiding", "Law Abiding Citizen", "Complete game at LOCAL tier", 150, icon="👮"),
            Achievement("federal_attention", "Federal Attention", "Reach FEDERAL tier", 50, icon="🚨"),
            Achievement("master_negotiator", "Master Negotiator", "Successfully bribe 10 times", 100, icon="🤝"),

            # Ending achievements
            Achievement("legitimate_success", "Legitimate Success", "Win via legitimate business", 500, icon="🏆"),
            Achievement("great_escape", "Great Escape", "Escape before FBI raid", 300, icon="✈️"),
            Achievement("deal_maker", "Deal Maker", "Negotiate plea deal", 200, icon="⚖️"),
            Achievement("caught", "Caught", "Get raided by FBI", 50, icon="🚔", hidden=True),

            # Special achievements
            Achievement("speed_run", "Speed Run", "Complete game in <10 game days", 400, icon="⚡"),
            Achievement("slow_burn", "Slow Burn", "Survive 100 game days", 200, icon="🐢"),
            Achievement("market_master", "Market Master", "Profit from market fluctuations", 150, icon="📈"),
            Achievement("weatherman", "Weatherman", "Operate through 10 different weather changes", 75, icon="🌤️"),
        ]

        for achievement in achievements:
            self.achievements[achievement.id] = achievement

    def update(self, dt: float, game_time: float):
        """
        Update scoring system.

        Args:
            dt: Delta time in seconds
            game_time: Current game time
        """
        # Update time played
        self.stats['time_played'] += dt

        # Check for time-based achievements
        days_survived = game_time / (24 * 3600)
        if days_survived >= 100:
            self.unlock_achievement("slow_burn", game_time)

    def record_money_earned(self, amount: float):
        """Record money earned."""
        self.stats['total_money_earned'] += amount

        if amount > 0 and not self.achievements["first_dollar"].unlocked:
            self.unlock_achievement("first_dollar", 0)

        if self.stats['total_money_earned'] >= 1000000:
            self.unlock_achievement("millionaire", 0)

    def record_money_spent(self, amount: float):
        """Record money spent."""
        self.stats['total_money_spent'] += abs(amount)

        if self.stats['total_money_spent'] >= 500000:
            self.unlock_achievement("big_spender", 0)

    def record_material_processed(self, quantity: float):
        """Record materials processed."""
        self.stats['materials_processed'] += quantity

        if quantity > 0 and not self.achievements["first_product"].unlocked:
            self.unlock_achievement("first_product", 0)

        if self.stats['materials_processed'] >= 10000:
            self.unlock_achievement("mass_production", 0)

        if self.stats['materials_processed'] >= 100000:
            self.unlock_achievement("recycling_master", 0)

    def record_building_built(self):
        """Record building construction."""
        self.stats['buildings_built'] += 1

        if self.stats['buildings_built'] >= 10:
            self.unlock_achievement("builder", 0)
        if self.stats['buildings_built'] >= 50:
            self.unlock_achievement("architect", 0)
        if self.stats['buildings_built'] >= 100:
            self.unlock_achievement("city_planner", 0)

    def record_drone_deployed(self):
        """Record drone deployment."""
        self.stats['drones_deployed'] += 1

        if self.stats['drones_deployed'] >= 10:
            self.unlock_achievement("drone_pilot", 0)

    def record_drone_crashed(self):
        """Record drone crash."""
        self.stats['drones_crashed'] += 1

        if self.stats['drones_crashed'] >= 5:
            self.unlock_achievement("crash_test", 0)

    def record_bribe_attempt(self, success: bool):
        """Record bribe attempt."""
        self.stats['bribes_attempted'] += 1
        if success:
            self.stats['bribes_successful'] += 1

            if self.stats['bribes_successful'] >= 10:
                self.unlock_achievement("master_negotiator", 0)

    def record_inspection_result(self, passed: bool):
        """Record inspection result."""
        if passed:
            self.stats['inspections_passed'] += 1
        else:
            self.stats['inspections_failed'] += 1

    def unlock_achievement(self, achievement_id: str, game_time: float):
        """
        Unlock an achievement.

        Args:
            achievement_id: ID of achievement to unlock
            game_time: Current game time
        """
        if achievement_id not in self.achievements:
            return

        achievement = self.achievements[achievement_id]

        if achievement.unlocked:
            return  # Already unlocked

        achievement.unlocked = True
        achievement.unlock_time = game_time

        print(f"\n🏆 ACHIEVEMENT UNLOCKED!")
        print(f"  {achievement.icon} {achievement.name}")
        print(f"  {achievement.description}")
        print(f"  +{achievement.points} points")

    def calculate_final_score(self, game_time: float, ending_type: str,
                              current_money: float, max_suspicion: float,
                              exploration_percent: float) -> int:
        """
        Calculate final score.

        Args:
            game_time: Total game time
            ending_type: Type of game ending
            current_money: Current money
            max_suspicion: Maximum suspicion reached
            exploration_percent: Percentage of map explored

        Returns:
            int: Total score
        """
        self.game_completed = True

        # Money score
        self.scores[ScoreCategory.MONEY_EARNED] = self.stats['total_money_earned']

        # Materials processed score
        self.scores[ScoreCategory.MATERIALS_PROCESSED] = self.stats['materials_processed']

        # Buildings score
        self.scores[ScoreCategory.BUILDINGS_BUILT] = self.stats['buildings_built']

        # Time survived score (in days)
        days_survived = game_time / (24 * 3600)
        self.scores[ScoreCategory.TIME_SURVIVED] = days_survived

        # Efficiency score (based on materials processed vs collected)
        if self.stats['materials_collected'] > 0:
            efficiency = self.stats['materials_processed'] / self.stats['materials_collected']
            self.efficiency_score = min(1.0, efficiency)
        self.scores[ScoreCategory.EFFICIENCY] = self.efficiency_score

        # Stealth score (inverse of max suspicion)
        self.stealth_score = max(0.0, 1.0 - (max_suspicion / 150.0))
        self.scores[ScoreCategory.STEALTH] = self.stealth_score

        # Exploration score
        self.exploration_score = exploration_percent / 100.0
        self.scores[ScoreCategory.EXPLORATION] = self.exploration_score

        # Ending bonus
        ending_bonuses = {
            'LEGITIMATE_SUCCESS': 5000,
            'ESCAPE': 3000,
            'PLEA_DEAL': 1500,
            'FBI_RAID': 500,
            'BANKRUPTCY': 0,
            'INSPECTOR_FAILURE': 200,
        }
        self.scores[ScoreCategory.ENDING_BONUS] = ending_bonuses.get(ending_type, 0)

        # Calculate total score
        total = 0
        for category, value in self.scores.items():
            multiplier = self.score_multipliers[category]
            total += int(value * multiplier)

        # Add achievement points
        achievement_points = sum(
            a.points for a in self.achievements.values() if a.unlocked
        )
        total += achievement_points

        self.total_score = max(0, total)  # Can't have negative score

        # Determine rank
        self._calculate_rank()

        # Check ending-specific achievements
        if ending_type == 'LEGITIMATE_SUCCESS':
            self.unlock_achievement("legitimate_success", game_time)
        elif ending_type == 'ESCAPE':
            self.unlock_achievement("great_escape", game_time)
        elif ending_type == 'PLEA_DEAL':
            self.unlock_achievement("deal_maker", game_time)
        elif ending_type == 'FBI_RAID':
            self.unlock_achievement("caught", game_time)

        # Check max suspicion achievements
        if max_suspicion < 20 and ending_type != 'FBI_RAID':
            self.unlock_achievement("ghost", game_time)

        # Check inspection achievements
        if self.stats['inspections_failed'] == 0 and self.stats['inspections_passed'] > 0:
            self.unlock_achievement("smooth_operator", game_time)

        # Check exploration achievements
        if exploration_percent >= 25:
            self.unlock_achievement("explorer", game_time)
        if exploration_percent >= 75:
            self.unlock_achievement("cartographer", game_time)
        if exploration_percent >= 100:
            self.unlock_achievement("completionist", game_time)

        # Check speed run
        if days_survived <= 10:
            self.unlock_achievement("speed_run", game_time)

        return self.total_score

    def _calculate_rank(self):
        """Calculate player rank based on score."""
        if self.total_score < 1000:
            self.rank = "Novice"
        elif self.total_score < 5000:
            self.rank = "Amateur"
        elif self.total_score < 10000:
            self.rank = "Professional"
        elif self.total_score < 25000:
            self.rank = "Expert"
        elif self.total_score < 50000:
            self.rank = "Master"
        elif self.total_score < 100000:
            self.rank = "Legend"
        else:
            self.rank = "Grandmaster"

    def get_score_breakdown(self) -> Dict[str, Tuple[int, int]]:
        """
        Get score breakdown by category.

        Returns:
            dict: {category_name: (raw_value, score_points)}
        """
        breakdown = {}
        for category, value in self.scores.items():
            multiplier = self.score_multipliers[category]
            points = int(value * multiplier)
            breakdown[category.value] = (value, points)

        return breakdown

    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get list of unlocked achievements."""
        return [a for a in self.achievements.values() if a.unlocked]

    def get_locked_achievements(self) -> List[Achievement]:
        """Get list of locked achievements (non-hidden)."""
        return [a for a in self.achievements.values() if not a.unlocked and not a.hidden]

    def get_achievement_progress(self) -> Tuple[int, int]:
        """
        Get achievement progress.

        Returns:
            tuple: (unlocked_count, total_count)
        """
        unlocked = len(self.get_unlocked_achievements())
        total = len([a for a in self.achievements.values() if not a.hidden])
        return (unlocked, total)

    def get_summary(self) -> Dict:
        """
        Get scoring system summary.

        Returns:
            dict: Summary information
        """
        unlocked, total = self.get_achievement_progress()

        return {
            'total_score': self.total_score,
            'rank': self.rank,
            'achievements_unlocked': unlocked,
            'achievements_total': total,
            'score_breakdown': self.get_score_breakdown(),
            'statistics': dict(self.stats),
            'efficiency': self.efficiency_score,
            'stealth': self.stealth_score,
            'exploration': self.exploration_score,
            'game_completed': self.game_completed
        }

    def __repr__(self):
        """String representation for debugging."""
        return (f"ScoringManager(score={self.total_score}, "
                f"rank={self.rank}, "
                f"achievements={len(self.get_unlocked_achievements())}/{len(self.achievements)})")
