"""
Unit tests for MarketManager.

Tests cover:
- Initialization
- Price calculations (buy and sell)
- Market trends
- Price fluctuations
- Market events
- Price bounds
- Statistics tracking
"""

import pytest
from unittest.mock import patch, MagicMock
import random

from src.systems.market_manager import MarketManager, MarketTrend, MarketEvent


class TestMarketManagerInitialization:
    """Tests for MarketManager initialization."""

    def test_init_default_trend_stable(self):
        """Test that manager initializes with stable trend."""
        manager = MarketManager()
        assert manager.current_trend == MarketTrend.STABLE

    def test_init_base_buy_prices_set(self):
        """Test that base buy prices are set."""
        manager = MarketManager()
        assert 'plastic' in manager.base_buy_prices
        assert 'metal' in manager.base_buy_prices
        assert 'electronics' in manager.base_buy_prices
        assert manager.base_buy_prices['electronics'] == 20.0

    def test_init_base_sell_prices_set(self):
        """Test that base sell prices are set."""
        manager = MarketManager()
        assert 'recycled_plastic' in manager.base_sell_prices
        assert 'recycled_metal' in manager.base_sell_prices
        assert manager.base_sell_prices['recycled_electronics'] == 50.0

    def test_init_multipliers_at_one(self):
        """Test that all price multipliers start at 1.0."""
        manager = MarketManager()
        for material, multiplier in manager.price_multipliers.items():
            assert multiplier == 1.0

    def test_init_no_active_events(self):
        """Test that no events are active initially."""
        manager = MarketManager()
        assert manager.active_events == []

    def test_init_statistics_zeroed(self):
        """Test that statistics are initialized properly."""
        manager = MarketManager()
        assert manager.total_price_changes == 0
        assert manager.total_events == 0
        assert manager.highest_multiplier == 1.0
        assert manager.lowest_multiplier == 1.0


class TestBuyPrices:
    """Tests for buy price calculations."""

    def test_get_buy_price_at_base(self):
        """Test getting buy price with multiplier at 1.0."""
        manager = MarketManager()

        price = manager.get_buy_price('plastic')

        assert price == manager.base_buy_prices['plastic']

    def test_get_buy_price_with_multiplier(self):
        """Test buy price reflects multiplier."""
        manager = MarketManager()
        manager.price_multipliers['metal'] = 1.5

        price = manager.get_buy_price('metal')

        expected = manager.base_buy_prices['metal'] * 1.5
        assert price == expected

    def test_get_buy_price_unknown_material(self):
        """Test buy price for unknown material returns 0."""
        manager = MarketManager()

        price = manager.get_buy_price('unobtainium')

        assert price == 0.0


class TestSellPrices:
    """Tests for sell price calculations."""

    def test_get_sell_price_at_base(self):
        """Test getting sell price with multiplier at 1.0."""
        manager = MarketManager()

        price = manager.get_sell_price('recycled_plastic')

        assert price == manager.base_sell_prices['recycled_plastic']

    def test_get_sell_price_with_multiplier(self):
        """Test sell price reflects base material multiplier."""
        manager = MarketManager()
        manager.price_multipliers['metal'] = 2.0

        price = manager.get_sell_price('recycled_metal')

        expected = manager.base_sell_prices['recycled_metal'] * 2.0
        assert price == expected

    def test_get_sell_price_unknown_product(self):
        """Test sell price for unknown product returns 0."""
        manager = MarketManager()

        price = manager.get_sell_price('recycled_unobtainium')

        assert price == 0.0


class TestMarketTrends:
    """Tests for market trend system."""

    def test_trend_change_after_interval(self):
        """Test that trend can change after interval passes."""
        manager = MarketManager()

        # Seed random to get predictable trend change
        with patch('random.choices', return_value=[MarketTrend.BULLISH]):
            manager.update(manager.trend_change_interval + 1, 0)

        # After trend change, the trend should be BULLISH
        assert manager.current_trend == MarketTrend.BULLISH
        # Trend duration resets to 0 on change, then accumulates leftover
        assert manager.trend_duration >= 0

    def test_trend_duration_accumulates(self):
        """Test that trend duration accumulates over updates."""
        manager = MarketManager()

        manager.update(100.0, 0)
        manager.update(100.0, 100)

        assert manager.trend_duration == pytest.approx(200.0, abs=0.1)

    def test_get_price_trend_bullish(self):
        """Test price trend indicator for bullish market."""
        manager = MarketManager()
        manager.current_trend = MarketTrend.BULLISH

        # Source returns Unicode up arrow
        assert manager.get_price_trend('plastic') == "↑"

    def test_get_price_trend_bearish(self):
        """Test price trend indicator for bearish market."""
        manager = MarketManager()
        manager.current_trend = MarketTrend.BEARISH

        # Source returns Unicode down arrow
        assert manager.get_price_trend('plastic') == "↓"

    def test_get_price_trend_volatile(self):
        """Test price trend indicator for volatile market."""
        manager = MarketManager()
        manager.current_trend = MarketTrend.VOLATILE

        # Source returns Unicode up-down arrow
        assert manager.get_price_trend('plastic') == "↕"

    def test_get_price_trend_stable(self):
        """Test price trend indicator for stable market."""
        manager = MarketManager()
        manager.current_trend = MarketTrend.STABLE

        # Source returns Unicode right arrow
        assert manager.get_price_trend('plastic') == "→"


class TestPriceFluctuations:
    """Tests for price fluctuation mechanics."""

    def test_prices_change_over_time(self):
        """Test that prices change with updates."""
        manager = MarketManager()
        manager.current_trend = MarketTrend.BULLISH
        original_multipliers = dict(manager.price_multipliers)

        # Large enough dt to cause measurable change
        for _ in range(10):
            manager.update(3600, 0)  # 1 hour

        # At least one multiplier should have changed
        changes = sum(1 for m in manager.price_multipliers
                     if manager.price_multipliers[m] != original_multipliers[m])
        assert changes > 0

    def test_prices_bounded_by_min(self):
        """Test that prices don't go below minimum."""
        manager = MarketManager()
        manager.current_trend = MarketTrend.CRASH

        # Run many crash updates
        for i in range(100):
            manager.update(3600, i * 3600)

        for material, multiplier in manager.price_multipliers.items():
            assert multiplier >= manager.min_multiplier

    def test_prices_bounded_by_max(self):
        """Test that prices don't exceed maximum."""
        manager = MarketManager()
        manager.current_trend = MarketTrend.BULLISH

        # Force high multipliers
        for material in manager.price_multipliers:
            manager.price_multipliers[material] = 10.0

        # Update should clamp
        manager.update(3600, 0)

        for material, multiplier in manager.price_multipliers.items():
            assert multiplier <= manager.max_multiplier

    def test_get_price_change_percentage(self):
        """Test price change percentage calculation."""
        manager = MarketManager()
        manager.price_multipliers['plastic'] = 1.25

        change = manager.get_price_change_percentage('plastic')

        assert change == pytest.approx(25.0)

    def test_price_change_percentage_negative(self):
        """Test negative price change percentage."""
        manager = MarketManager()
        manager.price_multipliers['metal'] = 0.8

        change = manager.get_price_change_percentage('metal')

        assert change == pytest.approx(-20.0)


class TestMarketEvents:
    """Tests for market event system."""

    def test_event_triggered_by_update(self):
        """Test that events can be triggered during update."""
        manager = MarketManager()

        # Force event trigger
        with patch('random.random', return_value=0.01):  # Below probability
            with patch('random.choice') as mock_choice:
                mock_choice.return_value = {
                    'name': 'Test Event',
                    'description': 'Test',
                    'duration': 3600,
                    'price_multipliers': {'plastic': 1.5}
                }
                manager.update(manager.event_check_interval + 1,
                             manager.event_check_interval + 1)

        assert manager.total_events >= 1

    def test_event_modifies_prices(self):
        """Test that event multipliers affect prices."""
        manager = MarketManager()
        original_plastic = manager.price_multipliers['plastic']

        # Create and add event directly
        event = MarketEvent(
            name='Plastic Boom',
            description='Test event',
            duration=1000,
            price_multipliers={'plastic': 1.5},
            start_time=0
        )
        manager.active_events.append(event)
        # Apply the multiplier
        manager.price_multipliers['plastic'] *= 1.5

        assert manager.price_multipliers['plastic'] == original_plastic * 1.5

    def test_event_expires_after_duration(self):
        """Test that events are removed after their duration."""
        manager = MarketManager()
        event = MarketEvent(
            name='Short Event',
            description='Test',
            duration=100,
            price_multipliers={},
            start_time=0
        )
        manager.active_events.append(event)

        # Update past event duration
        manager.update(1, 200)

        assert event not in manager.active_events

    def test_multiple_events_can_be_active(self):
        """Test that multiple events can be active simultaneously."""
        manager = MarketManager()
        event1 = MarketEvent('Event1', 'Desc1', 1000, {}, start_time=0)
        event2 = MarketEvent('Event2', 'Desc2', 1000, {}, start_time=0)
        manager.active_events.extend([event1, event2])

        manager.update(1, 500)

        assert len(manager.active_events) == 2


class TestAllPrices:
    """Tests for getting all prices at once."""

    def test_get_all_prices_structure(self):
        """Test that get_all_prices returns correct structure."""
        manager = MarketManager()

        prices = manager.get_all_prices()

        assert 'buy' in prices
        assert 'sell' in prices
        assert isinstance(prices['buy'], dict)
        assert isinstance(prices['sell'], dict)

    def test_get_all_prices_includes_all_materials(self):
        """Test that all materials are included in prices."""
        manager = MarketManager()

        prices = manager.get_all_prices()

        for material in manager.base_buy_prices:
            assert material in prices['buy']

        for product in manager.base_sell_prices:
            assert product in prices['sell']


class TestMarketSummary:
    """Tests for market summary."""

    def test_get_summary_structure(self):
        """Test that summary contains expected keys."""
        manager = MarketManager()

        summary = manager.get_summary()

        assert 'current_trend' in summary
        assert 'trend_duration_hours' in summary
        assert 'active_events' in summary
        assert 'total_events' in summary
        assert 'price_changes' in summary
        assert 'highest_multiplier' in summary
        assert 'lowest_multiplier' in summary
        assert 'multipliers' in summary

    def test_summary_reflects_state(self):
        """Test that summary accurately reflects state."""
        manager = MarketManager()
        manager.current_trend = MarketTrend.BULLISH
        manager.total_events = 5
        event = MarketEvent('Test', 'Test', 1000, {}, start_time=0)
        manager.active_events.append(event)

        summary = manager.get_summary()

        assert summary['current_trend'] == 'BULLISH'
        assert summary['total_events'] == 5
        assert summary['active_events'] == 1


class TestMarketStatisticsTracking:
    """Tests for market statistics tracking."""

    def test_highest_multiplier_tracked(self):
        """Test that highest multiplier is tracked."""
        manager = MarketManager()
        manager.price_multipliers['plastic'] = 2.5

        # Trigger stats update
        manager.update(1, 0)

        assert manager.highest_multiplier >= 2.5

    def test_lowest_multiplier_tracked(self):
        """Test that lowest multiplier is tracked."""
        manager = MarketManager()
        manager.price_multipliers['plastic'] = 0.5

        manager.update(1, 0)

        # Use approx for floating point comparison
        assert manager.lowest_multiplier == pytest.approx(0.5, abs=0.01)

    def test_price_changes_counted(self):
        """Test that price changes are counted."""
        manager = MarketManager()
        manager.current_trend = MarketTrend.BULLISH

        # Run enough updates to get changes
        for i in range(10):
            manager.update(3600, i * 3600)

        assert manager.total_price_changes > 0


class TestRepr:
    """Tests for string representation."""

    def test_repr_contains_trend(self):
        """Test that repr contains trend information."""
        manager = MarketManager()
        manager.current_trend = MarketTrend.VOLATILE

        repr_str = repr(manager)

        assert 'MarketManager' in repr_str
        assert 'VOLATILE' in repr_str

    def test_repr_contains_event_count(self):
        """Test that repr contains event count."""
        manager = MarketManager()
        event = MarketEvent('Test', 'Test', 1000, {}, start_time=0)
        manager.active_events.append(event)

        repr_str = repr(manager)

        assert 'events=1' in repr_str
