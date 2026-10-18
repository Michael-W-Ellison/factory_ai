"""
Unit tests for AIOpponentManager.

Tests AI decision making, market dynamics, rankings, and win conditions.
"""

import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
import random

# Mock pygame before any imports that might need it
sys.modules['pygame'] = Mock()

# Import directly to avoid __init__.py cascade
import importlib.util
spec = importlib.util.spec_from_file_location(
    "ai_opponent_manager",
    "/home/user/factory_ai/src/systems/ai_opponent_manager.py"
)
ai_opponent_manager_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_opponent_manager_module)
AIOpponentManager = ai_opponent_manager_module.AIOpponentManager
GameMode = ai_opponent_manager_module.GameMode
WinCondition = ai_opponent_manager_module.WinCondition
get_ai_opponent_manager = ai_opponent_manager_module.get_ai_opponent_manager
reset_ai_opponent_manager = ai_opponent_manager_module.reset_ai_opponent_manager


class MockAIFactory:
    """Mock AIFactory for testing."""

    def __init__(self, name="TestFactory", money=50000, personality=None):
        self.name = name
        self.money = money
        self.personality = personality or Mock()
        self.market_share = 0.0
        self.sales_this_period = 0
        self.materials_inventory = 0

    def update(self, dt, market_conditions, police_activity):
        pass

    def get_statistics(self):
        return {
            'name': self.name,
            'money': self.money,
            'net_worth': self.money + 50000,
            'market_share': self.market_share,
            'profit': 10000,
            'age': 100,
            'sales': self.sales_this_period
        }


class TestAIOpponentManagerInit:
    """Tests for AIOpponentManager initialization."""

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_init_creates_opponents(self, mock_ai_factory):
        """Test that initialization creates AI opponents."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager(num_opponents=3)

        assert len(manager.opponents) == 3

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_init_clamps_num_opponents(self, mock_ai_factory):
        """Test that num_opponents is clamped to 1-5."""
        mock_ai_factory.return_value = MockAIFactory()

        manager_min = AIOpponentManager(num_opponents=0)
        manager_max = AIOpponentManager(num_opponents=10)

        assert manager_min.num_opponents == 1
        assert manager_max.num_opponents == 5

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_init_sets_game_mode(self, mock_ai_factory):
        """Test that game mode is set correctly."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager(game_mode=GameMode.TOURNAMENT)

        assert manager.game_mode == GameMode.TOURNAMENT

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_init_sets_win_condition(self, mock_ai_factory):
        """Test that win condition is set correctly."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager(win_condition=WinCondition.PROFIT)

        assert manager.win_condition == WinCondition.PROFIT

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_init_market_defaults(self, mock_ai_factory):
        """Test market default values."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager()

        assert manager.total_market_size == 1000
        assert manager.base_price == 1000
        assert manager.price_multiplier == 1.0
        assert manager.demand_level == 1.0


class TestMarketConditions:
    """Tests for market condition management."""

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_get_market_conditions_returns_dict(self, mock_ai_factory):
        """Test that get_market_conditions returns correct dictionary."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager()

        conditions = manager.get_market_conditions()

        assert 'demand' in conditions
        assert 'price_multiplier' in conditions
        assert 'total_market_size' in conditions
        assert 'competition_level' in conditions
        assert 'investigation_active' in conditions

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_update_market_fluctuates_demand(self, mock_ai_factory):
        """Test that market update changes demand level."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager()

        initial_demand = manager.demand_level

        # Update multiple times to allow fluctuation
        random.seed(42)  # Make test deterministic
        for _ in range(10):
            manager._update_market(1.0)

        # Demand should change but stay within bounds
        assert 0.5 <= manager.demand_level <= 2.0

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_update_market_clamps_values(self, mock_ai_factory):
        """Test that market values are clamped to valid ranges."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager()

        # Force extreme values
        manager.demand_level = 100.0
        manager.price_multiplier = 100.0
        manager.police_activity = 100.0

        manager._update_market(1.0)

        # Values should be clamped
        assert manager.demand_level <= 2.0
        assert manager.price_multiplier <= 2.0
        assert manager.police_activity <= 1.0


class TestRankings:
    """Tests for ranking system."""

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_update_rankings_sorts_by_score(self, mock_ai_factory):
        """Test that rankings are sorted by score descending."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager(num_opponents=2)

        # Set different net worths
        manager.opponents[0].name = "Factory A"
        manager.opponents[1].name = "Factory B"

        # Mock get_statistics to return different scores
        manager.opponents[0].get_statistics = lambda: {'net_worth': 100000}
        manager.opponents[1].get_statistics = lambda: {'net_worth': 200000}

        manager._update_rankings(None)

        # Higher score should be first
        assert manager.rankings[0][0] == "Factory B"
        assert manager.rankings[0][1] == 200000

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_update_rankings_includes_player(self, mock_ai_factory):
        """Test that rankings include player when provided."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager(num_opponents=1)

        manager.opponents[0].get_statistics = lambda: {'net_worth': 50000}

        player_factory = {'net_worth': 150000}
        manager._update_rankings(player_factory)

        # Player should be in rankings
        names = [r[0] for r in manager.rankings]
        assert "Player" in names

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_get_leaderboard_format(self, mock_ai_factory):
        """Test leaderboard format."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager(num_opponents=1)

        manager.opponents[0].get_statistics = lambda: {'net_worth': 50000}
        manager._update_rankings({'net_worth': 75000})

        leaderboard = manager.get_leaderboard()

        assert len(leaderboard) == 2
        assert 'rank' in leaderboard[0]
        assert 'name' in leaderboard[0]
        assert 'score' in leaderboard[0]
        assert 'is_player' in leaderboard[0]


class TestWinConditions:
    """Tests for win condition checking."""

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_calculate_score_net_worth(self, mock_ai_factory):
        """Test score calculation for net worth win condition."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager(win_condition=WinCondition.NET_WORTH)

        score = manager._calculate_score({'net_worth': 500000})

        assert score == 500000

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_calculate_score_market_share(self, mock_ai_factory):
        """Test score calculation for market share win condition."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager(win_condition=WinCondition.MARKET_SHARE)

        score = manager._calculate_score({'market_share': 0.5})

        assert score == 500000  # 0.5 * 1000000

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_calculate_score_profit(self, mock_ai_factory):
        """Test score calculation for profit win condition."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager(win_condition=WinCondition.PROFIT)

        score = manager._calculate_score({'profit': 250000})

        assert score == 250000

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_calculate_score_survival(self, mock_ai_factory):
        """Test score calculation for survival win condition."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager(win_condition=WinCondition.SURVIVAL)

        score = manager._calculate_score({'age': 100, 'net_worth': 50000})

        # age * 100 + net_worth
        assert score == 100 * 100 + 50000

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_check_win_condition_time_limit(self, mock_ai_factory):
        """Test win condition check for time limit."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager(win_condition=WinCondition.TIME_LIMIT)

        manager.time_elapsed = 4000.0  # Past time limit
        manager.rankings = [("TestFactory", 100000)]

        manager._check_win_condition(None)

        assert manager.winner == "TestFactory"

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_check_win_condition_already_won(self, mock_ai_factory):
        """Test that winner is not changed once set."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager()

        manager.winner = "PreviousWinner"
        manager.rankings = [("NewLeader", 2000000)]

        manager._check_win_condition(None)

        assert manager.winner == "PreviousWinner"


class TestMarketShares:
    """Tests for market share calculation."""

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_update_market_shares_calculates_correctly(self, mock_ai_factory):
        """Test market share calculation."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager(num_opponents=2)

        manager.opponents[0].sales_this_period = 30
        manager.opponents[1].sales_this_period = 70

        manager._update_market_shares(None)

        assert manager.opponents[0].market_share == 0.3
        assert manager.opponents[1].market_share == 0.7

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_update_market_shares_resets_sales(self, mock_ai_factory):
        """Test that sales are reset after market share update."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager(num_opponents=1)

        manager.opponents[0].sales_this_period = 50

        manager._update_market_shares(None)

        assert manager.opponents[0].sales_this_period == 0


class TestOpponentManagement:
    """Tests for opponent management."""

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_get_opponent_by_rank_valid(self, mock_ai_factory):
        """Test getting opponent by valid rank."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager(num_opponents=2)

        manager.opponents[0].name = "First"
        manager.opponents[0].get_statistics = lambda: {'net_worth': 100000}
        manager.opponents[1].name = "Second"
        manager.opponents[1].get_statistics = lambda: {'net_worth': 50000}

        manager._update_rankings(None)

        opponent = manager.get_opponent_by_rank(0)

        assert opponent is not None
        assert opponent.name == "First"

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_get_opponent_by_rank_invalid(self, mock_ai_factory):
        """Test getting opponent by invalid rank returns None."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager(num_opponents=1)

        manager.rankings = [("Test", 1000)]

        opponent = manager.get_opponent_by_rank(99)

        assert opponent is None

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_update_removes_bankrupt_opponents(self, mock_ai_factory):
        """Test that bankrupt opponents are removed."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager(num_opponents=2)

        manager.opponents[0].money = -100000  # Bankrupt
        manager.opponents[1].money = 50000  # Healthy

        manager.update(1.0, None)

        assert len(manager.opponents) == 1
        assert manager.bankruptcies == 1


class TestStatistics:
    """Tests for statistics retrieval."""

    @patch('src.systems.ai_opponent_manager.AIFactory')
    def test_get_statistics_includes_all_fields(self, mock_ai_factory):
        """Test that get_statistics returns all expected fields."""
        mock_ai_factory.return_value = MockAIFactory()
        manager = AIOpponentManager(game_mode=GameMode.TOURNAMENT)

        stats = manager.get_statistics()

        assert stats['game_mode'] == 'tournament'
        assert stats['win_condition'] == 'net_worth'
        assert 'num_opponents' in stats
        assert 'time_elapsed' in stats
        assert 'time_limit' in stats
        assert 'market_demand' in stats
        assert 'price_multiplier' in stats
        assert 'police_activity' in stats
        assert 'investigation_active' in stats
        assert 'bankruptcies' in stats
        assert 'winner' in stats
        assert 'rankings' in stats


class TestGlobalInstance:
    """Tests for global instance management."""

    def test_get_ai_opponent_manager_creates_instance(self):
        """Test that get_ai_opponent_manager creates singleton."""
        reset_ai_opponent_manager()

        with patch('src.systems.ai_opponent_manager.AIFactory') as mock_factory:
            mock_factory.return_value = MockAIFactory()
            manager1 = get_ai_opponent_manager()
            manager2 = get_ai_opponent_manager()

        assert manager1 is manager2

        # Clean up
        reset_ai_opponent_manager()

    def test_reset_ai_opponent_manager(self):
        """Test that reset_ai_opponent_manager clears singleton."""
        with patch('src.systems.ai_opponent_manager.AIFactory') as mock_factory:
            mock_factory.return_value = MockAIFactory()
            manager1 = get_ai_opponent_manager()
            reset_ai_opponent_manager()
            manager2 = get_ai_opponent_manager()

        assert manager1 is not manager2

        # Clean up
        reset_ai_opponent_manager()


class TestGameModeEnum:
    """Tests for GameMode enum values."""

    def test_game_mode_values(self):
        """Test that GameMode enum has expected values."""
        assert GameMode.SOLO.value == "solo"
        assert GameMode.COMPETITIVE.value == "competitive"
        assert GameMode.TOURNAMENT.value == "tournament"


class TestWinConditionEnum:
    """Tests for WinCondition enum values."""

    def test_win_condition_values(self):
        """Test that WinCondition enum has expected values."""
        assert WinCondition.NET_WORTH.value == "net_worth"
        assert WinCondition.MARKET_SHARE.value == "market_share"
        assert WinCondition.PROFIT.value == "profit"
        assert WinCondition.SURVIVAL.value == "survival"
        assert WinCondition.TIME_LIMIT.value == "time_limit"
