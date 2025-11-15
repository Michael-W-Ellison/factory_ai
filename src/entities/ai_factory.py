"""
AI Factory - Competing AI-controlled recycling factory opponent.

Provides strategic AI decision-making for automated recycling factory management.
Factories can choose between legal (green) and illegal (profitable) recycling.
"""

import random
import math
from enum import Enum
from typing import Dict, List, Optional, Tuple


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
                 difficulty: float = 0.5, starting_money: int = 50000):
        """
        Initialize AI recycling factory.

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
        self.robots = 3  # Start with 3 automated recycling robots
        self.robot_efficiency = 1.0  # Robot performance multiplier
        self.workstations = 1  # Start with 1 recycling workstation
        self.technology_level = 1  # Tech level for upgrades

        # Production/Recycling
        self.recycling_rate = 1.0  # Materials processed per hour
        self.production_active = True
        self.materials_inventory = 0  # Recycled materials ready to sell
        self.quality_level = 0.7  # Output quality (0.0-1.0)

        # Ethical stance
        self.recycling_illegal_materials = False  # Whether recycling prohibited items
        self.green_reputation = 100  # Eco-friendly reputation (0-100)
        self.illegal_profit_multiplier = 2.5  # Illegal materials worth 2.5x more

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
        """Calculate risk tolerance based on personality and difficulty."""
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
        return max(0.0, min(0.9, tolerance))

    def update(self, dt: float, market_conditions: Dict, police_activity: float):
        """
        Update AI recycling factory state and make decisions.

        Args:
            dt: Delta time in seconds
            market_conditions: Dict with market data (demand, price_multiplier, etc.)
            police_activity: Current police activity level (0.0-1.0)
        """
        self.age += dt
        self.decision_cooldown -= dt

        # Recycle materials
        if self.production_active and not self.hiding:
            # Robots process materials
            recycling_this_tick = (self.recycling_rate * self.robots *
                                   self.robot_efficiency * self.workstations * dt / 3600.0)
            self.materials_inventory += recycling_this_tick

        # Heat/suspicion naturally decreases over time
        self.heat_level = max(0, self.heat_level - dt * 0.5)

        # Green reputation slowly recovers if recycling legally
        if not self.recycling_illegal_materials:
            self.green_reputation = min(100, self.green_reputation + dt * 0.1)
        else:
            # Slowly loses green reputation when recycling illegally
            self.green_reputation = max(0, self.green_reputation - dt * 0.05)

        # Make strategic decisions periodically
        if self.decision_cooldown <= 0:
            self._make_decision(market_conditions, police_activity)
            # Decision frequency based on difficulty
            self.decision_cooldown = random.uniform(5.0, 15.0) / (1.0 + self.difficulty)

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
        # Critical situations override personality
        if situation['money_situation'] == 'critical':
            return AIDecision.SELL_MATERIALS if self.materials_inventory > 5 else AIDecision.SAVE_MONEY

        if situation['heat_critical'] or (situation['police_threat'] and self.heat_level > 50):
            return AIDecision.HIDE_OPERATION

        # Personality-based decisions
        if self.personality == AIPersonality.AGGRESSIVE:
            # Aggressive AI prioritizes profit, willing to recycle illegal materials
            if not self.recycling_illegal_materials and random.random() < 0.8:
                return AIDecision.RECYCLE_ILLEGAL  # Go for max profit
            elif situation['expansion_viable'] and random.random() < 0.7:
                return random.choice([AIDecision.BUILD_WORKSTATION, AIDecision.BUILD_ROBOT])
            elif situation['inventory_high']:
                return AIDecision.INCREASE_PRODUCTION
            else:
                return random.choice([AIDecision.BUILD_WORKSTATION, AIDecision.INCREASE_PRODUCTION])

        elif self.personality == AIPersonality.ECO_FRIENDLY:
            # Eco-friendly AI ONLY recycles legal materials
            if self.recycling_illegal_materials:
                return AIDecision.RECYCLE_LEGAL  # Switch back to legal
            elif situation['expansion_viable']:
                return AIDecision.BUILD_WORKSTATION
            elif situation['robots_needed']:
                return AIDecision.BUILD_ROBOT
            else:
                return AIDecision.UPGRADE_ROBOTS if random.random() < 0.4 else AIDecision.INCREASE_PRODUCTION

        elif self.personality == AIPersonality.CAUTIOUS:
            # Cautious AI avoids illegal recycling unless very profitable
            if self.recycling_illegal_materials and (situation['police_threat'] or situation['heat_critical']):
                return AIDecision.RECYCLE_LEGAL  # Switch to legal when risky
            elif situation['police_threat']:
                return AIDecision.HIDE_OPERATION
            elif self.money < 30000:
                return AIDecision.SAVE_MONEY
            elif situation['robots_needed']:
                return AIDecision.BUILD_ROBOT
            else:
                return AIDecision.INCREASE_PRODUCTION if random.random() < 0.5 else AIDecision.SAVE_MONEY

        elif self.personality == AIPersonality.INNOVATOR:
            # Innovator focuses on robot upgrades and technology
            if self.money > 80000 and random.random() < 0.6:
                return AIDecision.UPGRADE_ROBOTS
            elif situation['expansion_viable']:
                return AIDecision.BUILD_WORKSTATION
            elif situation['robots_needed']:
                return AIDecision.BUILD_ROBOT
            else:
                return AIDecision.INCREASE_PRODUCTION

        elif self.personality == AIPersonality.OPPORTUNIST:
            # Opportunist adapts to market and switches between legal/illegal
            if situation['price_favorable'] and self.materials_inventory > 10:
                return AIDecision.SELL_MATERIALS
            elif situation['market_demand'] > 1.5 and not self.recycling_illegal_materials:
                # High demand = try illegal for profit
                return AIDecision.RECYCLE_ILLEGAL if random.random() < 0.6 else AIDecision.INCREASE_PRODUCTION
            elif situation['police_threat'] and self.recycling_illegal_materials:
                # Police threat = switch to legal
                return AIDecision.RECYCLE_LEGAL
            elif situation['expansion_viable']:
                return AIDecision.BUILD_WORKSTATION
            else:
                return AIDecision.SAVE_MONEY

        else:  # BALANCED
            # Balanced approach: mix of legal/illegal based on situation
            if not self.recycling_illegal_materials and self.money < 50000 and random.random() < 0.4:
                # Sometimes recycle illegal when money is tight
                return AIDecision.RECYCLE_ILLEGAL
            elif self.recycling_illegal_materials and situation['heat_critical']:
                # Switch to legal when heat is high
                return AIDecision.RECYCLE_LEGAL
            elif situation['expansion_viable'] and random.random() < 0.5:
                return AIDecision.BUILD_WORKSTATION
            elif situation['robots_needed'] and random.random() < 0.6:
                return AIDecision.BUILD_ROBOT
            elif situation['inventory_high']:
                return AIDecision.SELL_MATERIALS
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

        elif decision == AIDecision.BUILD_ROBOT:
            # Build robot from collected resources (requires materials inventory)
            materials_cost = 5  # Materials needed to build a robot
            money_cost = 3000  # Assembly/programming cost
            if self.materials_inventory >= materials_cost and self.money >= money_cost:
                self.materials_inventory -= materials_cost
                self.money -= money_cost
                self.robots += 1
                self.total_expenses += money_cost

        elif decision == AIDecision.UPGRADE_ROBOTS:
            # Upgrade robot efficiency
            cost = 20000 + (int(self.robot_efficiency * 30000))  # Increasing cost
            if self.money >= cost:
                self.money -= cost
                self.robot_efficiency += 0.15  # 15% efficiency boost
                self.technology_level += 1
                self.quality_level = min(1.0, self.quality_level + 0.05)
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
                self.heat_level += 20

        elif decision == AIDecision.INCREASE_PRODUCTION:
            if not self.production_active:
                self.production_active = True
            # Increase recycling rate (risky)
            self.recycling_rate = min(5.0, self.recycling_rate * 1.1)
            if self.recycling_illegal_materials:
                self.heat_level += 8
            else:
                self.heat_level += 3

        elif decision == AIDecision.DECREASE_PRODUCTION:
            self.recycling_rate = max(0.5, self.recycling_rate * 0.9)
            self.heat_level = max(0, self.heat_level - 10)

        elif decision == AIDecision.HIDE_OPERATION:
            self.hiding = True
            self.production_active = False
            self.heat_level = max(0, self.heat_level - 20)
            # Resume after cooldown
            if random.random() < 0.3:  # 30% chance to resume
                self.hiding = False
                self.production_active = True

        elif decision == AIDecision.SELL_MATERIALS:
            self._attempt_sales(market_conditions, force=True)

        elif decision == AIDecision.SAVE_MONEY:
            # Reduce expenses, lower recycling
            self.recycling_rate = max(0.5, self.recycling_rate * 0.95)

        elif decision == AIDecision.BRIBE_OFFICIALS:
            bribe_cost = 10000
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
        if self.materials_inventory < 1:
            return

        # Determine how much to sell
        demand = market_conditions.get('demand', 1.0)
        price_mult = market_conditions.get('price_multiplier', 1.0)

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

            actual_price = base_price * price_mult * illegal_bonus * (0.9 + self.quality_level * 0.2)

            revenue = int(units_to_sell * actual_price)
            self.money += revenue
            self.materials_inventory -= units_to_sell
            self.sales_this_period += units_to_sell
            self.total_revenue += revenue

            # Selling illegal materials increases heat more
            if self.recycling_illegal_materials:
                self.heat_level += units_to_sell * 1.0  # Higher heat for illegal sales
            else:
                self.heat_level += units_to_sell * 0.2  # Lower heat for legal sales

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
        asset_value = (
            self.workstations * 25000 +
            self.robots * 5000 +
            self.technology_level * 30000 +
            self.materials_inventory * 800
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
