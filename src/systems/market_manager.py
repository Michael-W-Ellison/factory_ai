"""
MarketManager - manages dynamic market prices and fluctuations.

Handles:
- Dynamic material and product pricing
- Market trends (bullish, bearish, volatile)
- Price fluctuations over time
- Supply/demand mechanics
- Market events and crashes
"""

import random
import math
from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from src.core.logger import get_logger
from src.core.game_config import MARKET, TIME

logger = get_logger(__name__)


class MarketTrend(Enum):
    """Market trend states."""
    STABLE = 0  # Prices relatively stable
    BULLISH = 1  # Prices trending up
    BEARISH = 2  # Prices trending down
    VOLATILE = 3  # Prices fluctuating rapidly
    CRASH = 4  # Market crash - prices plummet


@dataclass
class MarketEvent:
    """
    Market event that affects prices.

    Attributes:
        name: Event name
        description: Event description
        duration: How long event lasts (game seconds)
        price_multipliers: Material -> price multiplier
        start_time: When event started
    """
    name: str
    description: str
    duration: float
    price_multipliers: Dict[str, float]
    start_time: float = 0.0


class MarketManager:
    """
    Manages dynamic market pricing system.

    Prices fluctuate based on trends, events, and player actions.
    """

    def __init__(self):
        """Initialize market manager."""
        # Base prices for materials (buying)
        self.base_buy_prices = {
            'plastic': 2.0,
            'metal': 4.0,
            'glass': 3.0,
            'paper': 1.0,
            'electronics': 20.0,
            'copper': 30.0,
            'rubber': 4.0,
        }

        # Base prices for products (selling)
        self.base_sell_prices = {
            'recycled_plastic': 5.0,
            'recycled_metal': 10.0,
            'recycled_glass': 8.0,
            'recycled_paper': 3.0,
            'recycled_electronics': 50.0,
            'recycled_copper': 75.0,
            'recycled_rubber': 10.0,
        }

        # Current price multipliers (1.0 = base price)
        self.price_multipliers = {
            'plastic': 1.0,
            'metal': 1.0,
            'glass': 1.0,
            'paper': 1.0,
            'electronics': 1.0,
            'copper': 1.0,
            'rubber': 1.0,
        }

        # Market state
        self.current_trend = MarketTrend.STABLE
        self.trend_duration = 0.0  # How long current trend has lasted
        self.trend_change_interval = MARKET.TREND_CHANGE_INTERVAL

        # Price change rates (per game hour)
        self.trend_change_rates = {
            MarketTrend.STABLE: 0.001,  # ±0.1% per hour
            MarketTrend.BULLISH: 0.005,  # +0.5% per hour
            MarketTrend.BEARISH: -0.005,  # -0.5% per hour
            MarketTrend.VOLATILE: 0.02,  # ±2% per hour
            MarketTrend.CRASH: -0.05,  # -5% per hour
        }

        # Price bounds
        self.min_multiplier = MARKET.MIN_PRICE_MULTIPLIER
        self.max_multiplier = MARKET.MAX_PRICE_MULTIPLIER

        # Active events
        self.active_events: List[MarketEvent] = []

        # Event probability
        self.event_check_interval = MARKET.EVENT_CHECK_INTERVAL
        self.last_event_check = 0.0
        self.event_probability = MARKET.EVENT_PROBABILITY

        # Statistics
        self.total_price_changes = 0
        self.total_events = 0
        self.highest_multiplier = 1.0
        self.lowest_multiplier = 1.0

    def update(self, dt: float, game_time: float):
        """
        Update market prices.

        Args:
            dt: Delta time in seconds
            game_time: Current game time
        """
        # Update trend duration
        self.trend_duration += dt

        # Check if trend should change
        if self.trend_duration >= self.trend_change_interval:
            self._change_trend()
            self.trend_duration = 0.0

        # Update prices based on trend
        self._update_prices(dt)

        # Update active events
        self._update_events(game_time, dt)

        # Check for new random events
        if game_time - self.last_event_check >= self.event_check_interval:
            self.last_event_check = game_time
            if random.random() < self.event_probability:
                self._trigger_random_event(game_time)

    def _change_trend(self):
        """Change market trend."""
        # Weight probabilities
        trend_weights = {
            MarketTrend.STABLE: 0.4,  # 40%
            MarketTrend.BULLISH: 0.2,  # 20%
            MarketTrend.BEARISH: 0.2,  # 20%
            MarketTrend.VOLATILE: 0.15,  # 15%
            MarketTrend.CRASH: 0.05,  # 5%
        }

        # Choose new trend
        trends = list(trend_weights.keys())
        weights = list(trend_weights.values())
        self.current_trend = random.choices(trends, weights=weights)[0]

        logger.info(f"Market trend changed: {self.current_trend.name}")

        if self.current_trend == MarketTrend.BULLISH:
            logger.info("Prices trending upward - good time to sell!")
        elif self.current_trend == MarketTrend.BEARISH:
            logger.info("Prices trending downward - good time to buy!")
        elif self.current_trend == MarketTrend.VOLATILE:
            logger.info("Market is unstable - prices fluctuating rapidly!")
        elif self.current_trend == MarketTrend.CRASH:
            logger.warning("MARKET CRASH! Prices plummeting!")

    def _update_prices(self, dt: float):
        """Update prices based on trend."""
        # Get change rate for current trend
        change_rate = self.trend_change_rates[self.current_trend]

        # Update each material
        for material in self.price_multipliers.keys():
            # Calculate change
            if self.current_trend == MarketTrend.VOLATILE:
                # Random fluctuations
                change = random.uniform(-change_rate, change_rate) * (dt / TIME.SECONDS_PER_HOUR)
            else:
                # Directional change with some randomness
                base_change = change_rate * (dt / TIME.SECONDS_PER_HOUR)
                randomness = random.uniform(-0.001, 0.001) * (dt / TIME.SECONDS_PER_HOUR)
                change = base_change + randomness

            # Apply change
            old_multiplier = self.price_multipliers[material]
            new_multiplier = old_multiplier + change

            # Clamp to bounds
            new_multiplier = max(self.min_multiplier, min(self.max_multiplier, new_multiplier))

            # Update
            self.price_multipliers[material] = new_multiplier

            # Track statistics
            if new_multiplier != old_multiplier:
                self.total_price_changes += 1

            self.highest_multiplier = max(self.highest_multiplier, new_multiplier)
            self.lowest_multiplier = min(self.lowest_multiplier, new_multiplier)

    def _update_events(self, game_time: float, dt: float):
        """Update active market events."""
        # Remove expired events
        self.active_events = [
            event for event in self.active_events
            if game_time - event.start_time < event.duration
        ]

    def _trigger_random_event(self, game_time: float):
        """Trigger a random market event."""
        # Define possible events
        events = [
            {
                'name': 'Electronics Shortage',
                'description': 'Global chip shortage drives up electronics prices',
                'duration': MARKET.EVENT_DURATION_MEDIUM,
                'price_multipliers': {'electronics': 1.5, 'copper': 1.3}
            },
            {
                'name': 'Plastic Surplus',
                'description': 'Oversupply of plastic drives prices down',
                'duration': MARKET.EVENT_DURATION_SHORT,
                'price_multipliers': {'plastic': 0.7}
            },
            {
                'name': 'Metal Boom',
                'description': 'Construction boom increases metal demand',
                'duration': MARKET.EVENT_DURATION_LONG,
                'price_multipliers': {'metal': 1.4, 'copper': 1.3}
            },
            {
                'name': 'Paper Mill Strike',
                'description': 'Worker strike reduces paper supply',
                'duration': (MARKET.EVENT_DURATION_SHORT + MARKET.EVENT_DURATION_MEDIUM) / 2,
                'price_multipliers': {'paper': 1.6}
            },
            {
                'name': 'Rubber Crisis',
                'description': 'Natural disaster affects rubber supply',
                'duration': (MARKET.EVENT_DURATION_MEDIUM + MARKET.EVENT_DURATION_LONG) / 2,
                'price_multipliers': {'rubber': 1.8}
            },
            {
                'name': 'Glass Glut',
                'description': 'New recycling facilities oversupply glass market',
                'duration': MARKET.EVENT_DURATION_MEDIUM,
                'price_multipliers': {'glass': 0.6}
            },
        ]

        # Choose random event
        event_data = random.choice(events)

        # Create event
        event = MarketEvent(
            name=event_data['name'],
            description=event_data['description'],
            duration=event_data['duration'],
            price_multipliers=event_data['price_multipliers'],
            start_time=game_time
        )

        self.active_events.append(event)
        self.total_events += 1

        logger.info(f"Market event: {event.name} - {event.description} (Duration: {event.duration / TIME.SECONDS_PER_HOUR:.1f} hours)")

        # Apply event multipliers
        for material, multiplier in event.price_multipliers.items():
            self.price_multipliers[material] *= multiplier
            # Clamp to bounds
            self.price_multipliers[material] = max(
                self.min_multiplier,
                min(self.max_multiplier, self.price_multipliers[material])
            )

    def get_buy_price(self, material: str) -> float:
        """
        Get current buy price for a material.

        Args:
            material: Material name

        Returns:
            float: Current price per unit
        """
        if material not in self.base_buy_prices:
            return 0.0

        base_price = self.base_buy_prices[material]
        multiplier = self.price_multipliers.get(material, 1.0)

        return base_price * multiplier

    def get_sell_price(self, product: str) -> float:
        """
        Get current sell price for a product.

        Args:
            product: Product name

        Returns:
            float: Current price per unit
        """
        if product not in self.base_sell_prices:
            return 0.0

        # Extract material from product name (e.g., "recycled_plastic" -> "plastic")
        material = product.replace('recycled_', '')

        base_price = self.base_sell_prices[product]
        multiplier = self.price_multipliers.get(material, 1.0)

        return base_price * multiplier

    def get_price_trend(self, material: str) -> str:
        """
        Get price trend indicator for a material.

        Args:
            material: Material name

        Returns:
            str: "↑" (up), "↓" (down), "→" (stable), or "↕" (volatile)
        """
        if self.current_trend == MarketTrend.BULLISH:
            return "↑"
        elif self.current_trend == MarketTrend.BEARISH:
            return "↓"
        elif self.current_trend == MarketTrend.VOLATILE:
            return "↕"
        elif self.current_trend == MarketTrend.CRASH:
            return "⇊"
        else:
            return "→"

    def get_price_change_percentage(self, material: str) -> float:
        """
        Get price change percentage from base price.

        Args:
            material: Material name

        Returns:
            float: Percentage change (-100 to +200)
        """
        multiplier = self.price_multipliers.get(material, 1.0)
        return (multiplier - 1.0) * 100.0

    def get_all_prices(self) -> Dict[str, Dict[str, float]]:
        """
        Get all current prices.

        Returns:
            dict: {'buy': {material: price}, 'sell': {product: price}}
        """
        buy_prices = {
            material: self.get_buy_price(material)
            for material in self.base_buy_prices.keys()
        }

        sell_prices = {
            product: self.get_sell_price(product)
            for product in self.base_sell_prices.keys()
        }

        return {
            'buy': buy_prices,
            'sell': sell_prices
        }

    def get_summary(self) -> Dict:
        """
        Get market system summary.

        Returns:
            dict: Summary information
        """
        return {
            'current_trend': self.current_trend.name,
            'trend_duration_hours': self.trend_duration / TIME.SECONDS_PER_HOUR,
            'active_events': len(self.active_events),
            'total_events': self.total_events,
            'price_changes': self.total_price_changes,
            'highest_multiplier': self.highest_multiplier,
            'lowest_multiplier': self.lowest_multiplier,
            'multipliers': dict(self.price_multipliers)
        }

    def __repr__(self):
        """String representation for debugging."""
        return (f"MarketManager(trend={self.current_trend.name}, "
                f"events={len(self.active_events)})")
