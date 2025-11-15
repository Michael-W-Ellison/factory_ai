"""
AI Factory - Competing AI-controlled factory opponent.

Provides strategic AI decision-making for factory management and competition.
"""

import random
import math
from enum import Enum
from typing import Dict, List, Optional, Tuple


class AIPersonality(Enum):
    """AI opponent personality types."""
    AGGRESSIVE = "aggressive"      # High risk, fast expansion
    BALANCED = "balanced"          # Moderate risk, steady growth
    CAUTIOUS = "cautious"          # Low risk, slow but safe
    OPPORTUNIST = "opportunist"    # Adapts to market conditions
    INNOVATOR = "innovator"        # Focuses on technology/upgrades


class AIGoal(Enum):
    """AI strategic goals."""
    EXPAND_PRODUCTION = "expand_production"
    INCREASE_EFFICIENCY = "increase_efficiency"
    MAXIMIZE_PROFIT = "maximize_profit"
    AVOID_DETECTION = "avoid_detection"
    DOMINATE_MARKET = "dominate_market"
    UPGRADE_TECHNOLOGY = "upgrade_technology"


class AIDecision(Enum):
    """AI decision types."""
    BUILD_WORKSTATION = "build_workstation"
    HIRE_ROBOT = "hire_robot"
    UPGRADE_MACHINE = "upgrade_machine"
    INCREASE_PRODUCTION = "increase_production"
    DECREASE_PRODUCTION = "decrease_production"
    HIDE_OPERATION = "hide_operation"
    EXPAND_BUILDING = "expand_building"
    SELL_PRODUCTS = "sell_products"
    SAVE_MONEY = "save_money"
    BRIBE_OFFICIALS = "bribe_officials"


class AIFactory:
    """
    AI-controlled competing factory.

    Manages resources, makes strategic decisions, and competes with player.
    """

    def __init__(self, name: str, personality: AIPersonality = AIPersonality.BALANCED,
                 difficulty: float = 0.5, starting_money: int = 50000):
        """
        Initialize AI factory.

        Args:
            name: Factory/company name
            personality: AI personality type
            difficulty: Difficulty level (0.0 = easy, 1.0 = hard)
            starting_money: Initial capital
        """
        self.name = name
        self.personality = personality
        self.difficulty = difficulty

        # Resources
        self.money = starting_money
        self.robots = 2  # Start with 2 robots
        self.workstations = 1  # Start with 1 workstation
        self.technology_level = 1  # Tech level for upgrades

        # Production
        self.production_rate = 1.0  # Units per hour
        self.production_active = True
        self.inventory = 0  # Finished products
        self.quality_level = 0.7  # Product quality (0.0-1.0)

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
            return random.choice([AIGoal.EXPAND_PRODUCTION, AIGoal.DOMINATE_MARKET])
        elif self.personality == AIPersonality.CAUTIOUS:
            return random.choice([AIGoal.AVOID_DETECTION, AIGoal.MAXIMIZE_PROFIT])
        elif self.personality == AIPersonality.INNOVATOR:
            return AIGoal.UPGRADE_TECHNOLOGY
        elif self.personality == AIPersonality.OPPORTUNIST:
            return AIGoal.MAXIMIZE_PROFIT
        else:  # BALANCED
            return random.choice(list(AIGoal))

    def _calculate_risk_tolerance(self) -> float:
        """Calculate risk tolerance based on personality and difficulty."""
        base_tolerance = {
            AIPersonality.AGGRESSIVE: 0.8,
            AIPersonality.BALANCED: 0.5,
            AIPersonality.CAUTIOUS: 0.2,
            AIPersonality.OPPORTUNIST: 0.6,
            AIPersonality.INNOVATOR: 0.4,
        }

        tolerance = base_tolerance.get(self.personality, 0.5)
        # Higher difficulty = more willing to take risks
        tolerance += (self.difficulty - 0.5) * 0.3
        return max(0.1, min(0.9, tolerance))

    def update(self, dt: float, market_conditions: Dict, police_activity: float):
        """
        Update AI factory state and make decisions.

        Args:
            dt: Delta time in seconds
            market_conditions: Dict with market data (demand, price_multiplier, etc.)
            police_activity: Current police activity level (0.0-1.0)
        """
        self.age += dt
        self.decision_cooldown -= dt

        # Produce goods
        if self.production_active and not self.hiding:
            production_this_tick = self.production_rate * self.workstations * dt / 3600.0
            self.inventory += production_this_tick

        # Heat naturally decreases over time
        self.heat_level = max(0, self.heat_level - dt * 0.5)

        # Make strategic decisions periodically
        if self.decision_cooldown <= 0:
            self._make_decision(market_conditions, police_activity)
            # Decision frequency based on difficulty
            self.decision_cooldown = random.uniform(5.0, 15.0) / (1.0 + self.difficulty)

        # Update goal progress
        self._update_goal_progress(dt)

        # Try to sell products
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
            'inventory_high': self.inventory > 50,
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
        # Critical situations override personality
        if situation['money_situation'] == 'critical':
            return AIDecision.SELL_PRODUCTS if self.inventory > 5 else AIDecision.SAVE_MONEY

        if situation['heat_critical'] or (situation['police_threat'] and self.heat_level > 50):
            return AIDecision.HIDE_OPERATION

        # Personality-based decisions
        if self.personality == AIPersonality.AGGRESSIVE:
            if situation['expansion_viable'] and random.random() < 0.7:
                return random.choice([AIDecision.BUILD_WORKSTATION, AIDecision.HIRE_ROBOT])
            elif situation['inventory_high']:
                return AIDecision.INCREASE_PRODUCTION
            else:
                return random.choice([AIDecision.BUILD_WORKSTATION, AIDecision.INCREASE_PRODUCTION])

        elif self.personality == AIPersonality.CAUTIOUS:
            if situation['police_threat']:
                return AIDecision.HIDE_OPERATION
            elif self.money < 30000:
                return AIDecision.SAVE_MONEY
            elif situation['robots_needed']:
                return AIDecision.HIRE_ROBOT
            else:
                return AIDecision.INCREASE_PRODUCTION if random.random() < 0.5 else AIDecision.SAVE_MONEY

        elif self.personality == AIPersonality.INNOVATOR:
            if self.money > 80000 and random.random() < 0.6:
                return AIDecision.UPGRADE_MACHINE
            elif situation['expansion_viable']:
                return AIDecision.BUILD_WORKSTATION
            else:
                return AIDecision.INCREASE_PRODUCTION

        elif self.personality == AIPersonality.OPPORTUNIST:
            if situation['price_favorable'] and self.inventory > 10:
                return AIDecision.SELL_PRODUCTS
            elif situation['market_demand'] > 1.5:
                return AIDecision.INCREASE_PRODUCTION
            elif situation['expansion_viable']:
                return AIDecision.BUILD_WORKSTATION
            else:
                return AIDecision.SAVE_MONEY

        else:  # BALANCED
            # Weighted random choice based on situation
            if situation['expansion_viable'] and random.random() < 0.5:
                return AIDecision.BUILD_WORKSTATION
            elif situation['robots_needed'] and random.random() < 0.6:
                return AIDecision.HIRE_ROBOT
            elif situation['inventory_high']:
                return AIDecision.SELL_PRODUCTS
            else:
                return random.choice([AIDecision.INCREASE_PRODUCTION, AIDecision.SAVE_MONEY])

    def _execute_decision(self, decision: AIDecision, market_conditions: Dict):
        """
        Execute a decision.

        Args:
            decision: Decision to execute
            market_conditions: Current market conditions
        """
        if decision == AIDecision.BUILD_WORKSTATION:
            cost = 30000 + (self.workstations * 5000)  # Increasing cost
            if self.money >= cost:
                self.money -= cost
                self.workstations += 1
                self.total_expenses += cost
                self.heat_level += 10  # Building attracts attention

        elif decision == AIDecision.HIRE_ROBOT:
            cost = 8000  # Robot purchase cost
            if self.money >= cost:
                self.money -= cost
                self.robots += 1
                self.total_expenses += cost

        elif decision == AIDecision.UPGRADE_MACHINE:
            cost = 50000 * self.technology_level
            if self.money >= cost:
                self.money -= cost
                self.technology_level += 1
                self.production_rate *= 1.2  # 20% increase
                self.quality_level = min(1.0, self.quality_level + 0.1)
                self.total_expenses += cost

        elif decision == AIDecision.INCREASE_PRODUCTION:
            if not self.production_active:
                self.production_active = True
            # Increase production rate (risky)
            self.production_rate = min(5.0, self.production_rate * 1.1)
            self.heat_level += 5

        elif decision == AIDecision.DECREASE_PRODUCTION:
            self.production_rate = max(0.5, self.production_rate * 0.9)
            self.heat_level = max(0, self.heat_level - 10)

        elif decision == AIDecision.HIDE_OPERATION:
            self.hiding = True
            self.production_active = False
            self.heat_level = max(0, self.heat_level - 20)
            # Resume after cooldown
            if random.random() < 0.3:  # 30% chance to resume
                self.hiding = False
                self.production_active = True

        elif decision == AIDecision.SELL_PRODUCTS:
            self._attempt_sales(market_conditions, force=True)

        elif decision == AIDecision.SAVE_MONEY:
            # Reduce expenses, lower production
            self.production_rate = max(0.5, self.production_rate * 0.95)

        elif decision == AIDecision.BRIBE_OFFICIALS:
            bribe_cost = 10000
            if self.money >= bribe_cost:
                self.money -= bribe_cost
                self.heat_level = max(0, self.heat_level - 30)
                self.total_expenses += bribe_cost

    def _attempt_sales(self, market_conditions: Dict, force: bool = False):
        """
        Attempt to sell products.

        Args:
            market_conditions: Current market conditions
            force: Force sale regardless of conditions
        """
        if self.inventory < 1:
            return

        # Determine how much to sell
        demand = market_conditions.get('demand', 1.0)
        price_mult = market_conditions.get('price_multiplier', 1.0)

        # AI considers market conditions
        should_sell = force or (
            (price_mult > 1.0 and random.random() < 0.8) or
            (self.inventory > 20) or
            (self.money < 20000)
        )

        if should_sell:
            # Sell portion of inventory
            units_to_sell = min(self.inventory, math.ceil(self.inventory * 0.5 * demand))
            base_price = 1000  # Base price per unit
            actual_price = base_price * price_mult * (0.9 + self.quality_level * 0.2)

            revenue = int(units_to_sell * actual_price)
            self.money += revenue
            self.inventory -= units_to_sell
            self.sales_this_period += units_to_sell
            self.total_revenue += revenue

            # Selling increases heat slightly
            self.heat_level += units_to_sell * 0.5

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

        # Choose new goal if achieved
        if goal_achieved or self.goal_progress > 600:  # 10 minutes
            self.current_goal = random.choice(list(AIGoal))
            self.goal_progress = 0.0
            self.successful_operations += 1

    def get_net_worth(self) -> int:
        """Calculate net worth of factory."""
        asset_value = (
            self.workstations * 25000 +
            self.robots * 5000 +
            self.technology_level * 30000 +
            self.inventory * 800
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
            'workstations': self.workstations,
            'technology_level': self.technology_level,
            'production_rate': self.production_rate,
            'inventory': self.inventory,
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
        }

    def __repr__(self):
        """String representation."""
        return f"AIFactory({self.name}, {self.personality.value}, ${self.money:,})"
