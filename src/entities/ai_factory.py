"""
AI Factory - Competing AI-controlled recycling factory opponent.

Provides strategic AI decision-making for automated recycling factory management.
Factories can choose between legal (green) and illegal (profitable) recycling.
"""

import random
import math
from enum import Enum
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from src.core.logger import get_logger

if TYPE_CHECKING:
    from src.core.game_config import DifficultyModifiers

logger = get_logger(__name__)


class AIPersonality(Enum):
    """AI opponent personality types."""
    AGGRESSIVE = "aggressive"      # High risk, fast expansion, profit-focused
    BALANCED = "balanced"          # Moderate risk, balances profit and legality
    CAUTIOUS = "cautious"          # Low risk, mostly legal recycling
    OPPORTUNIST = "opportunist"    # Adapts to market and police pressure
    INNOVATOR = "innovator"        # Focuses on technology/robot upgrades
    ECO_FRIENDLY = "eco_friendly"  # Only recycles legal materials (green path)


class AIGoal(Enum):
    """AI strategic goals."""
    EXPAND_PRODUCTION = "expand_production"
    INCREASE_EFFICIENCY = "increase_efficiency"
    MAXIMIZE_PROFIT = "maximize_profit"
    AVOID_DETECTION = "avoid_detection"
    DOMINATE_MARKET = "dominate_market"
    UPGRADE_TECHNOLOGY = "upgrade_technology"
    GO_GREEN = "go_green"  # Achieve high green reputation
    MAXIMIZE_VOLUME = "maximize_volume"  # Recycle maximum materials


class AIDecision(Enum):
    """AI decision types."""
    BUILD_WORKSTATION = "build_workstation"
    BUILD_ROBOT = "build_robot"  # Build more robots from resources
    UPGRADE_ROBOTS = "upgrade_robots"  # Upgrade robot performance
    RECYCLE_LEGAL = "recycle_legal"  # Only legal materials (green, low profit)
    RECYCLE_ILLEGAL = "recycle_illegal"  # Illegal materials too (high profit, risky)
    INCREASE_PRODUCTION = "increase_production"
    DECREASE_PRODUCTION = "decrease_production"
    HIDE_OPERATION = "hide_operation"
    EXPAND_BUILDING = "expand_building"
    SELL_MATERIALS = "sell_materials"
    SAVE_MONEY = "save_money"
    BRIBE_OFFICIALS = "bribe_officials"


class AIFactory:
    """
    AI-controlled competing recycling factory.

    Manages automated recycling operation with robots.
    Makes ethical decisions between legal (green) and illegal (profitable) recycling.
    """

    def __init__(self, name: str, personality: AIPersonality = AIPersonality.BALANCED,
                 difficulty: float = 0.5, starting_money: int = 50000,
                 difficulty_modifiers: Optional['DifficultyModifiers'] = None):
        """
        Initialize AI recycling factory.

        Args:
            name: Factory/company name
            personality: AI personality type
            difficulty: Difficulty level (0.0 = easy, 1.0 = hard)
            starting_money: Initial capital
            difficulty_modifiers: Game difficulty modifiers affecting AI behavior
        """
        self.name = name
        self.personality = personality
        self.difficulty = difficulty

        # Store difficulty modifiers (use defaults if not provided)
        self.difficulty_modifiers = difficulty_modifiers

        # Extract AI-specific modifiers (default to 1.0 if not provided)
        ai_starting_mult = getattr(difficulty_modifiers, 'ai_starting_money', 1.0) if difficulty_modifiers else 1.0
        self.ai_production_mult = getattr(difficulty_modifiers, 'ai_production_rate', 1.0) if difficulty_modifiers else 1.0
        self.ai_expansion_mult = getattr(difficulty_modifiers, 'ai_expansion_rate', 1.0) if difficulty_modifiers else 1.0
        self.ai_decision_quality = getattr(difficulty_modifiers, 'ai_decision_quality', 1.0) if difficulty_modifiers else 1.0
        self.ai_risk_mult = getattr(difficulty_modifiers, 'ai_risk_tolerance', 1.0) if difficulty_modifiers else 1.0
        self.ai_income_mult = getattr(difficulty_modifiers, 'ai_income_rate', 1.0) if difficulty_modifiers else 1.0
        self.ai_expense_mult = getattr(difficulty_modifiers, 'ai_expense_rate', 1.0) if difficulty_modifiers else 1.0

        # Resources (apply starting money modifier, ensure non-negative)
        self.money = max(0, int(starting_money * ai_starting_mult))
        self.robots = 3  # Start with 3 automated recycling robots
        self.workstations = 1  # Start with 1 recycling workstation

        # All personalities start equal - strategy determines outcome
        self.technology_level = 1
        self.robot_efficiency = 1.0

        # Production/Recycling (base rate affected by ai_production_mult)
        self.recycling_rate = 3.0 * self.ai_production_mult  # Materials processed per hour (increased from 1.0)
        self.production_active = True
        self.materials_inventory = 0  # Recycled materials ready to sell
        self.quality_level = 0.7  # Output quality (0.0-1.0)

        # Ethical stance
        self.recycling_illegal_materials = False  # Whether recycling prohibited items
        self.green_reputation = 100  # Eco-friendly reputation (0-100)
        self.illegal_profit_multiplier = 1.5  # Illegal materials worth 1.5x more (modest bonus)

        # Market
        self.market_share = 0.0  # Percentage of total market
        self.reputation = 50  # Reputation (0-100)
        self.sales_this_period = 0
        self.revenue_history: List[int] = []

        # Strategy
        self.current_goal = self._choose_initial_goal()
        self.goal_progress = 0.0
        self.risk_tolerance = self._calculate_risk_tolerance()
        self.decision_cooldown = 0.0  # Time until next decision

        # Detection/Police
        self.heat_level = 0  # Police suspicion (0-100)
        self.hiding = False
        self.bribe_budget = 0

        # Statistics
        self.age = 0.0  # Time in business (seconds)
        self.total_revenue = 0
        self.total_expenses = 0
        self.decisions_made = 0
        self.successful_operations = 0

    def _choose_initial_goal(self) -> AIGoal:
        """Choose initial strategic goal based on personality."""
        if self.personality == AIPersonality.AGGRESSIVE:
            return random.choice([AIGoal.EXPAND_PRODUCTION, AIGoal.DOMINATE_MARKET, AIGoal.MAXIMIZE_PROFIT])
        elif self.personality == AIPersonality.CAUTIOUS:
            return random.choice([AIGoal.AVOID_DETECTION, AIGoal.GO_GREEN])
        elif self.personality == AIPersonality.INNOVATOR:
            return AIGoal.UPGRADE_TECHNOLOGY
        elif self.personality == AIPersonality.OPPORTUNIST:
            return AIGoal.MAXIMIZE_PROFIT
        elif self.personality == AIPersonality.ECO_FRIENDLY:
            return AIGoal.GO_GREEN
        else:  # BALANCED
            return random.choice([AIGoal.EXPAND_PRODUCTION, AIGoal.MAXIMIZE_PROFIT, AIGoal.UPGRADE_TECHNOLOGY])

    def _calculate_risk_tolerance(self) -> float:
        """Calculate risk tolerance based on personality, difficulty, and modifiers."""
        base_tolerance = {
            AIPersonality.AGGRESSIVE: 0.9,  # Very likely to recycle illegal materials
            AIPersonality.BALANCED: 0.5,
            AIPersonality.CAUTIOUS: 0.2,
            AIPersonality.OPPORTUNIST: 0.6,
            AIPersonality.INNOVATOR: 0.4,
            AIPersonality.ECO_FRIENDLY: 0.0,  # Never recycles illegal materials
        }

        tolerance = base_tolerance.get(self.personality, 0.5)
        # Higher difficulty = more willing to take risks
        tolerance += (self.difficulty - 0.5) * 0.3
        # Apply AI risk tolerance modifier from difficulty settings
        tolerance *= self.ai_risk_mult
        return max(0.0, min(0.95, tolerance))

    def update(self, dt: float, market_conditions: Dict, police_activity: float):
        """
        Update AI recycling factory state and make decisions.

        Args:
            dt: Delta time in seconds
            market_conditions: Dict with market data (demand, price_multiplier, etc.)
            police_activity: Current police activity level (0.0-1.0)
        """
        # Clamp dt to prevent exploits (max 10 seconds per tick)
        dt = max(0.0, min(10.0, dt))

        # Clamp police activity to valid range
        police_activity = max(0.0, min(1.0, police_activity))

        self.age += dt
        self.decision_cooldown = max(0.0, self.decision_cooldown - dt)  # Prevent negative cooldown

        # Recycle materials
        if self.production_active and not self.hiding:
            # Robots process materials
            recycling_this_tick = (self.recycling_rate * self.robots *
                                   self.robot_efficiency * self.workstations * dt / 3600.0)
            self.materials_inventory += recycling_this_tick

        # Heat/suspicion naturally decreases over time (clamped to 0-100)
        self.heat_level = max(0, min(100, self.heat_level - dt * 0.5))

        # Green reputation slowly recovers if recycling legally (clamped to 0-100)
        if not self.recycling_illegal_materials:
            self.green_reputation = min(100, self.green_reputation + dt * 0.1)
        else:
            # Slowly loses green reputation when recycling illegally
            self.green_reputation = max(0, self.green_reputation - dt * 0.05)

        # Ensure green reputation stays in bounds
        self.green_reputation = max(0, min(100, self.green_reputation))

        # Make strategic decisions periodically
        if self.decision_cooldown <= 0:
            self._make_decision(market_conditions, police_activity)
            # Decision frequency based on difficulty and expansion rate
            base_cooldown = random.uniform(5.0, 15.0) / (1.0 + self.difficulty)
            self.decision_cooldown = base_cooldown / self.ai_expansion_mult

        # Update goal progress
        self._update_goal_progress(dt)

        # Try to sell materials
        self._attempt_sales(market_conditions)

    def _make_decision(self, market_conditions: Dict, police_activity: float):
        """Make a strategic decision based on current state."""
        # Assess current situation
        situation = self._assess_situation(market_conditions, police_activity)

        # Choose decision based on personality and situation
        decision = self._choose_decision(situation)

        # Execute decision
        self._execute_decision(decision, market_conditions)

        self.decisions_made += 1

    def _assess_situation(self, market_conditions: Dict, police_activity: float) -> Dict:
        """
        Assess current situation for decision-making.

        Returns:
            Dict with situation analysis
        """
        return {
            'money_situation': 'good' if self.money > 100000 else 'tight' if self.money > 20000 else 'critical',
            'market_demand': market_conditions.get('demand', 1.0),
            'price_favorable': market_conditions.get('price_multiplier', 1.0) > 1.2,
            'police_threat': police_activity > 0.7,
            'heat_critical': self.heat_level > 70,
            'inventory_high': self.materials_inventory > 50,
            'robots_needed': self.workstations > self.robots,
            'expansion_viable': self.money > 50000 and self.market_share < 0.4,
        }

    def _choose_decision(self, situation: Dict) -> AIDecision:
        """
        Choose best decision based on situation and personality.

        Args:
            situation: Current situation analysis

        Returns:
            AIDecision: Chosen decision
        """
        # AI decision quality affects chance to make suboptimal choices
        # Low quality = sometimes makes random/poor decisions
        if self.ai_decision_quality < 1.0 and random.random() > self.ai_decision_quality:
            # Make a suboptimal random decision
            suboptimal_choices = [
                AIDecision.SAVE_MONEY,
                AIDecision.DECREASE_PRODUCTION,
                AIDecision.INCREASE_PRODUCTION,
            ]
            return random.choice(suboptimal_choices)

        # Critical situations override personality
        if situation['money_situation'] == 'critical':
            if self.materials_inventory > 5:
                return AIDecision.SELL_MATERIALS
            elif self.materials_inventory > 1:
                # Sell what we have
                return AIDecision.SELL_MATERIALS
            else:
                # Need to produce more materials - don't save money, increase production!
                return AIDecision.INCREASE_PRODUCTION

        if situation['heat_critical'] or (situation['police_threat'] and self.heat_level > 50):
            return AIDecision.HIDE_OPERATION

        # Personality-based decisions
        if self.personality == AIPersonality.AGGRESSIVE:
            # Aggressive: high-risk high-reward with good heat management
            # Key: cycle between illegal (profit) and legal (cool down)
            if self.heat_level > 65:
                if self.recycling_illegal_materials:
                    return AIDecision.RECYCLE_LEGAL  # Cool down
                return AIDecision.DECREASE_PRODUCTION  # Lay low
            elif self.heat_level > 50 and self.recycling_illegal_materials:
                if random.random() < 0.5:
                    return AIDecision.RECYCLE_LEGAL  # Sometimes cool early
            # When heat is manageable, go aggressive
            if not self.recycling_illegal_materials and self.heat_level < 30:
                return AIDecision.RECYCLE_ILLEGAL  # Max profit mode
            elif self.money > 25000 and self.robots < 6 and random.random() < 0.6:
                return AIDecision.BUILD_ROBOT  # Build army
            elif situation['expansion_viable'] and random.random() < 0.4:
                return AIDecision.BUILD_WORKSTATION
            elif self.materials_inventory > 5:
                return AIDecision.SELL_MATERIALS
            else:
                return AIDecision.INCREASE_PRODUCTION

        elif self.personality == AIPersonality.ECO_FRIENDLY:
            # Eco-friendly AI ONLY recycles legal materials, maximizes green premium
            # Strategy: high volume + green reputation = consistent premium income
            if self.recycling_illegal_materials:
                return AIDecision.RECYCLE_LEGAL  # Always stay green
            elif self.money > 25000 and self.robots < 6 and random.random() < 0.6:
                return AIDecision.BUILD_ROBOT  # Volume is key for eco
            elif self.money > 35000 and self.technology_level < 5 and random.random() < 0.5:
                return AIDecision.UPGRADE_ROBOTS  # Efficiency + quality
            elif situation['expansion_viable'] and self.workstations < 3 and random.random() < 0.5:
                return AIDecision.BUILD_WORKSTATION  # Scale up
            elif self.materials_inventory > 5:
                return AIDecision.SELL_MATERIALS  # Sell often for green premium
            else:
                return AIDecision.INCREASE_PRODUCTION

        elif self.personality == AIPersonality.CAUTIOUS:
            # Cautious AI avoids risks but invests consistently
            if self.recycling_illegal_materials:
                return AIDecision.RECYCLE_LEGAL
            elif self.money > 20000 and self.robots < 6 and random.random() < 0.55:
                return AIDecision.BUILD_ROBOT  # Solid expansion
            elif self.money > 25000 and self.technology_level < 4 and random.random() < 0.45:
                return AIDecision.UPGRADE_ROBOTS  # Good tech investment
            elif self.money > 40000 and self.workstations < 2:
                return AIDecision.BUILD_WORKSTATION
            elif self.materials_inventory > 5:
                return AIDecision.SELL_MATERIALS
            else:
                return AIDecision.INCREASE_PRODUCTION

        elif self.personality == AIPersonality.INNOVATOR:
            # Innovator: tech-focused but needs production base first
            if self.money > 20000 and self.robots < 4 and random.random() < 0.5:
                return AIDecision.BUILD_ROBOT  # Build production first
            elif self.money > 18000 and self.technology_level < 4 and random.random() < 0.5:
                return AIDecision.UPGRADE_ROBOTS  # Then upgrade
            elif self.money > 30000 and self.workstations < 2:
                return AIDecision.BUILD_WORKSTATION
            elif self.materials_inventory > 5:
                return AIDecision.SELL_MATERIALS
            else:
                return AIDecision.INCREASE_PRODUCTION

        elif self.personality == AIPersonality.OPPORTUNIST:
            # Opportunist adapts to market conditions - flexible investor
            if situation['price_favorable'] and self.materials_inventory > 5:
                return AIDecision.SELL_MATERIALS
            elif situation['market_demand'] > 1.3 and not self.recycling_illegal_materials and self.heat_level < 35:
                return AIDecision.RECYCLE_ILLEGAL if random.random() < 0.45 else AIDecision.INCREASE_PRODUCTION
            elif situation['police_threat'] and self.recycling_illegal_materials:
                return AIDecision.RECYCLE_LEGAL
            elif self.money > 22000 and self.robots < 6 and random.random() < 0.5:
                return AIDecision.BUILD_ROBOT
            elif self.money > 30000 and self.technology_level < 4 and random.random() < 0.4:
                return AIDecision.UPGRADE_ROBOTS
            elif self.money > 45000 and self.workstations < 2:
                return AIDecision.BUILD_WORKSTATION
            elif self.materials_inventory > 5:
                return AIDecision.SELL_MATERIALS
            else:
                return AIDecision.INCREASE_PRODUCTION

        else:  # BALANCED
            # Balanced approach: diversified investment strategy
            if self.recycling_illegal_materials and self.heat_level > 35:
                return AIDecision.RECYCLE_LEGAL
            elif self.money > 20000 and self.robots < 6 and random.random() < 0.55:
                return AIDecision.BUILD_ROBOT  # Priority on robots
            elif self.money > 30000 and self.technology_level < 4 and random.random() < 0.45:
                return AIDecision.UPGRADE_ROBOTS  # Good tech investment
            elif self.money > 40000 and self.workstations < 2:
                return AIDecision.BUILD_WORKSTATION
            elif self.materials_inventory > 5:
                return AIDecision.SELL_MATERIALS
            else:
                return AIDecision.INCREASE_PRODUCTION

    def _execute_decision(self, decision: AIDecision, market_conditions: Dict):
        """
        Execute a decision.

        Args:
            decision: Decision to execute
            market_conditions: Current market conditions
        """
        if decision == AIDecision.BUILD_WORKSTATION:
            # Cap workstations at 20 to prevent spam
            if self.workstations >= 20:
                return  # Already at max workstations
            base_cost = 30000 + (self.workstations * 5000)  # Increasing cost
            cost = int(base_cost * self.ai_expense_mult)
            if self.money >= cost:
                self.money -= cost
                self.workstations += 1
                self.total_expenses += cost
                self.heat_level = min(100, self.heat_level + 10)  # Building attracts attention

        elif decision == AIDecision.BUILD_ROBOT:
            # Build robot - can use materials OR just money
            # Cap robots at 50 to prevent memory issues
            if self.robots >= 50:
                return  # Already at max robots
            materials_cost = 2  # Materials needed (if using materials)
            money_cost_with_materials = int(3000 * self.ai_expense_mult)  # Cheaper with materials
            money_cost_pure = int(10000 * self.ai_expense_mult)  # Cheaper robots overall

            if self.materials_inventory >= materials_cost and self.money >= money_cost_with_materials:
                # Build using materials (cheaper)
                self.materials_inventory -= materials_cost
                self.money -= money_cost_with_materials
                self.robots += 1
                self.total_expenses += money_cost_with_materials
            elif self.money >= money_cost_pure:
                # Buy robot outright (more expensive)
                self.money -= money_cost_pure
                self.robots += 1
                self.total_expenses += money_cost_pure

        elif decision == AIDecision.UPGRADE_ROBOTS:
            # Upgrade robot efficiency - balanced cost and returns
            # Cap tech level at 10 to prevent unbounded efficiency
            if self.technology_level >= 10:
                return  # Already at max tech
            cost = int(12000 * self.ai_expense_mult)
            if self.money >= cost:
                self.money -= cost
                self.robot_efficiency = min(5.0, self.robot_efficiency + 0.20)  # Cap efficiency at 5x
                self.technology_level += 1
                self.quality_level = min(1.0, self.quality_level + 0.06)
                self.total_expenses += cost

        elif decision == AIDecision.RECYCLE_LEGAL:
            # Switch to legal-only recycling (green path)
            if self.recycling_illegal_materials:
                self.recycling_illegal_materials = False
                # Reduce heat when switching to legal
                self.heat_level = max(0, self.heat_level - 15)

        elif decision == AIDecision.RECYCLE_ILLEGAL:
            # Switch to recycling illegal materials (profit path)
            if not self.recycling_illegal_materials:
                self.recycling_illegal_materials = True
                # Increase heat when starting illegal recycling
                self.heat_level += 15

        elif decision == AIDecision.INCREASE_PRODUCTION:
            if not self.production_active:
                self.production_active = True
            # Increase recycling rate
            self.recycling_rate = min(5.0, self.recycling_rate * 1.1)
            # Higher tech = stealthier operations (less heat from production)
            tech_stealth = max(0.5, 1.0 - (self.technology_level - 1) * 0.1)
            if self.recycling_illegal_materials:
                self.heat_level += 4 * tech_stealth  # Reduced from 8
            else:
                self.heat_level += 1 * tech_stealth  # Reduced from 3

        elif decision == AIDecision.DECREASE_PRODUCTION:
            self.recycling_rate = max(0.5, self.recycling_rate * 0.9)
            self.heat_level = max(0, self.heat_level - 10)

        elif decision == AIDecision.HIDE_OPERATION:
            if not self.hiding:
                # Only hide if not already hiding
                self.hiding = True
                self.production_active = False
                self.heat_level = max(0, self.heat_level - 20)
            else:
                # Already hiding - consider resuming based on heat level
                if self.heat_level < 30 or random.random() < 0.5:
                    self.hiding = False
                    self.production_active = True

        elif decision == AIDecision.SELL_MATERIALS:
            self._attempt_sales(market_conditions, force=True)

        elif decision == AIDecision.SAVE_MONEY:
            # Reduce expenses, lower recycling
            self.recycling_rate = max(0.5, self.recycling_rate * 0.95)

        elif decision == AIDecision.BRIBE_OFFICIALS:
            bribe_cost = int(10000 * self.ai_expense_mult)  # Apply expense modifier
            if self.money >= bribe_cost:
                self.money -= bribe_cost
                self.heat_level = max(0, self.heat_level - 30)
                self.total_expenses += bribe_cost

    def _attempt_sales(self, market_conditions: Dict, force: bool = False):
        """
        Attempt to sell recycled materials.

        Args:
            market_conditions: Current market conditions
            force: Force sale regardless of conditions
        """
        if self.materials_inventory is None or self.materials_inventory < 1:
            return

        # Determine how much to sell (clamp market values to reasonable bounds)
        demand = max(0.1, min(5.0, market_conditions.get('demand', 1.0)))
        price_mult = max(0.1, min(5.0, market_conditions.get('price_multiplier', 1.0)))

        # AI considers market conditions
        should_sell = force or (
            (price_mult > 1.0 and random.random() < 0.8) or
            (self.materials_inventory > 20) or
            (self.money < 20000)
        )

        if should_sell:
            # Sell portion of inventory
            units_to_sell = min(self.materials_inventory, math.ceil(self.materials_inventory * 0.5 * demand))
            base_price = 1000  # Base price per unit of recycled materials

            # Apply illegal profit multiplier if recycling illegal materials
            illegal_bonus = self.illegal_profit_multiplier if self.recycling_illegal_materials else 1.0

            # Green reputation provides premium for legal materials (eco-certified)
            green_bonus = 1.0
            if not self.recycling_illegal_materials and self.green_reputation > 70:
                green_bonus = 1.0 + (self.green_reputation - 70) * 0.01  # Up to +30% at 100 rep

            # Quality impacts price (0.7 to 1.0 quality = 0.85x to 1.15x price)
            quality_bonus = 0.85 + self.quality_level * 0.3

            # Technology level provides modest price premium
            tech_bonus = 1.0 + (self.technology_level - 1) * 0.05  # +5% per tech level

            # Calculate total multiplier and cap to prevent extreme profits
            total_multiplier = price_mult * illegal_bonus * green_bonus * quality_bonus * tech_bonus
            total_multiplier = min(10.0, total_multiplier)  # Cap total bonus at 10x
            actual_price = base_price * total_multiplier

            # Apply AI income modifier from difficulty settings
            revenue = int(units_to_sell * actual_price * self.ai_income_mult)
            self.money += revenue
            self.materials_inventory -= units_to_sell
            self.sales_this_period += units_to_sell
            self.total_revenue += revenue

            # Selling illegal materials increases heat
            # Higher tech = stealthier operations (up to 50% heat reduction at tech 5)
            tech_stealth = max(0.5, 1.0 - (self.technology_level - 1) * 0.1)
            if self.recycling_illegal_materials:
                self.heat_level += units_to_sell * 1.2 * tech_stealth
            else:
                self.heat_level += units_to_sell * 0.25 * tech_stealth

            # Clamp heat to valid range
            self.heat_level = max(0, min(100, self.heat_level))

    def _update_goal_progress(self, dt: float):
        """Update progress toward current goal."""
        self.goal_progress += dt

        # Check if goal is achieved
        goal_achieved = False

        if self.current_goal == AIGoal.EXPAND_PRODUCTION:
            if self.workstations >= 5:
                goal_achieved = True
        elif self.current_goal == AIGoal.MAXIMIZE_PROFIT:
            if self.total_revenue > 500000:
                goal_achieved = True
        elif self.current_goal == AIGoal.DOMINATE_MARKET:
            if self.market_share > 0.4:
                goal_achieved = True
        elif self.current_goal == AIGoal.AVOID_DETECTION:
            if self.heat_level < 10 and self.goal_progress > 300:
                goal_achieved = True
        elif self.current_goal == AIGoal.UPGRADE_TECHNOLOGY:
            if self.technology_level >= 5:
                goal_achieved = True
        elif self.current_goal == AIGoal.GO_GREEN:
            if self.green_reputation > 90 and not self.recycling_illegal_materials:
                goal_achieved = True
        elif self.current_goal == AIGoal.MAXIMIZE_VOLUME:
            if self.sales_this_period > 100 or self.total_revenue > 300000:
                goal_achieved = True
        elif self.current_goal == AIGoal.INCREASE_EFFICIENCY:
            if self.robot_efficiency > 2.0:
                goal_achieved = True

        # Choose new goal if achieved
        if goal_achieved or self.goal_progress > 600:  # 10 minutes
            self.current_goal = random.choice(list(AIGoal))
            self.goal_progress = 0.0
            self.successful_operations += 1

    def get_net_worth(self) -> int:
        """Calculate net worth of recycling factory."""
        # Value assets at purchase cost equivalent
        asset_value = (
            self.workstations * 30000 +  # Base workstation cost
            self.robots * 10000 +  # Robot purchase cost
            (self.technology_level - 1) * 12000 +  # Tech upgrade cost
            self.materials_inventory * 900
        )
        return self.money + asset_value

    def get_profit(self) -> int:
        """Get total profit."""
        return self.total_revenue - self.total_expenses

    def get_statistics(self) -> Dict:
        """Get comprehensive statistics."""
        return {
            'name': self.name,
            'personality': self.personality.value,
            'money': self.money,
            'net_worth': self.get_net_worth(),
            'profit': self.get_profit(),
            'robots': self.robots,
            'robot_efficiency': self.robot_efficiency,
            'workstations': self.workstations,
            'technology_level': self.technology_level,
            'recycling_rate': self.recycling_rate,
            'materials_inventory': self.materials_inventory,
            'recycling_illegal_materials': self.recycling_illegal_materials,
            'green_reputation': self.green_reputation,
            'market_share': self.market_share,
            'reputation': self.reputation,
            'heat_level': self.heat_level,
            'hiding': self.hiding,
            'current_goal': self.current_goal.value,
            'age': self.age,
            'total_revenue': self.total_revenue,
            'total_expenses': self.total_expenses,
            'decisions_made': self.decisions_made,
            'successful_operations': self.successful_operations,
            'sales': self.sales_this_period,
        }

    def __repr__(self):
        """String representation."""
        return f"AIFactory({self.name}, {self.personality.value}, ${self.money:,})"
