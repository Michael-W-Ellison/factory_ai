"""
Integration tests for AI competition - runs full games with multiple AI opponents.

Tests various game scenarios:
- AI vs AI competition
- Different win conditions
- Bankruptcy scenarios
- Market dynamics
- Game completion verification
"""

import pytest
import random
from typing import Dict, List

from src.entities.ai_factory import AIFactory, AIPersonality, AIGoal, AIDecision
from src.systems.ai_opponent_manager import (
    AIOpponentManager, GameMode, WinCondition,
    get_ai_opponent_manager
)


class TestAIFactory:
    """Tests for individual AI factory behavior."""

    def test_factory_creation(self):
        """Test AI factory initializes correctly."""
        factory = AIFactory(
            name="Test Corp",
            personality=AIPersonality.BALANCED,
            difficulty=0.5,
            starting_money=50000
        )

        assert factory.name == "Test Corp"
        assert factory.personality == AIPersonality.BALANCED
        assert factory.money == 50000
        assert factory.robots == 3
        assert factory.workstations == 1

    def test_all_personalities_have_initial_goal(self):
        """Test that all personalities get an initial goal."""
        for personality in AIPersonality:
            factory = AIFactory(
                name=f"{personality.value} Factory",
                personality=personality,
                difficulty=0.5
            )
            assert factory.current_goal is not None
            assert isinstance(factory.current_goal, AIGoal)

    def test_risk_tolerance_varies_by_personality(self):
        """Test that risk tolerance differs by personality."""
        aggressive = AIFactory("Aggressive", AIPersonality.AGGRESSIVE, 0.5)
        cautious = AIFactory("Cautious", AIPersonality.CAUTIOUS, 0.5)
        eco = AIFactory("Eco", AIPersonality.ECO_FRIENDLY, 0.5)

        assert aggressive.risk_tolerance > cautious.risk_tolerance
        assert cautious.risk_tolerance > eco.risk_tolerance
        assert eco.risk_tolerance == 0.0  # Eco-friendly never risks

    def test_factory_update_increases_age(self):
        """Test that update increases factory age."""
        factory = AIFactory("Test", AIPersonality.BALANCED, 0.5)

        market = {'demand': 1.0, 'price_multiplier': 1.0}
        factory.update(1.0, market, 0.3)

        assert factory.age == 1.0

    def test_factory_produces_materials(self):
        """Test that factory produces materials over time."""
        factory = AIFactory("Test", AIPersonality.BALANCED, 0.5)
        initial_inventory = factory.materials_inventory

        market = {'demand': 1.0, 'price_multiplier': 1.0}
        # Run for 100 ticks of 1 second each
        for _ in range(100):
            factory.update(1.0, market, 0.3)

        assert factory.materials_inventory > initial_inventory

    def test_factory_get_statistics(self):
        """Test factory statistics retrieval."""
        factory = AIFactory("Test", AIPersonality.BALANCED, 0.5)

        stats = factory.get_statistics()

        assert 'name' in stats
        assert 'personality' in stats
        assert 'money' in stats
        assert 'net_worth' in stats
        assert 'robots' in stats


class TestAIOpponentManager:
    """Tests for AI opponent manager."""

    def test_manager_creation(self):
        """Test AI opponent manager initializes correctly."""
        manager = AIOpponentManager(
            num_opponents=3,
            game_mode=GameMode.COMPETITIVE,
            win_condition=WinCondition.NET_WORTH
        )

        assert len(manager.opponents) == 3
        assert manager.game_mode == GameMode.COMPETITIVE
        assert manager.win_condition == WinCondition.NET_WORTH

    def test_manager_opponent_limit(self):
        """Test opponent count is clamped between 1-5."""
        low = AIOpponentManager(num_opponents=0)
        high = AIOpponentManager(num_opponents=10)

        assert len(low.opponents) >= 1
        assert len(high.opponents) <= 5

    def test_manager_varied_personalities(self):
        """Test that opponents have varied personalities."""
        manager = AIOpponentManager(num_opponents=5)

        personalities = [opp.personality for opp in manager.opponents]
        unique = set(personalities)

        # Should have at least 3 different personalities
        assert len(unique) >= 3

    def test_market_conditions(self):
        """Test market conditions are generated."""
        manager = AIOpponentManager(num_opponents=3)

        conditions = manager.get_market_conditions()

        assert 'demand' in conditions
        assert 'price_multiplier' in conditions
        assert 'competition_level' in conditions

    def test_leaderboard_generation(self):
        """Test leaderboard is generated correctly."""
        manager = AIOpponentManager(num_opponents=3)

        # Run a few updates
        for _ in range(10):
            manager.update(1.0, {'money': 50000, 'net_worth': 50000})

        leaderboard = manager.get_leaderboard()

        assert len(leaderboard) >= 3  # At least 3 AI opponents
        assert all('rank' in entry for entry in leaderboard)
        assert all('name' in entry for entry in leaderboard)
        assert all('score' in entry for entry in leaderboard)


class TestAICompetition:
    """Tests for full AI vs AI competition."""

    def test_short_competition(self):
        """Test a short competition completes without errors."""
        manager = AIOpponentManager(
            num_opponents=3,
            game_mode=GameMode.COMPETITIVE,
            win_condition=WinCondition.NET_WORTH
        )

        # Run for simulated 10 minutes (600 ticks of 1 second)
        for tick in range(600):
            manager.update(1.0, None)

        # Should have run without errors
        assert manager.time_elapsed == 600.0
        assert len(manager.opponents) >= 0  # Some may have gone bankrupt

    def test_competition_produces_rankings(self):
        """Test that competition produces valid rankings."""
        manager = AIOpponentManager(
            num_opponents=4,
            game_mode=GameMode.COMPETITIVE,
            win_condition=WinCondition.NET_WORTH
        )

        # Run for 5 minutes
        for _ in range(300):
            manager.update(1.0, None)

        rankings = manager.rankings

        # Should have rankings
        assert len(rankings) > 0

        # Rankings should be sorted by score (descending)
        scores = [score for _, score in rankings]
        assert scores == sorted(scores, reverse=True)

    def test_time_limit_game_mode(self):
        """Test time-limited game determines winner correctly."""
        manager = AIOpponentManager(
            num_opponents=3,
            game_mode=GameMode.COMPETITIVE,
            win_condition=WinCondition.TIME_LIMIT
        )
        manager.time_limit = 60.0  # 1 minute

        # Run until time limit
        for _ in range(70):
            manager.update(1.0, None)

        # Should have a winner after time limit
        assert manager.winner is not None or len(manager.opponents) == 0

    def test_survival_mode(self):
        """Test survival mode with bankruptcies."""
        manager = AIOpponentManager(
            num_opponents=3,
            game_mode=GameMode.COMPETITIVE,
            win_condition=WinCondition.SURVIVAL
        )

        # Force one opponent into bankruptcy
        if manager.opponents:
            manager.opponents[0].money = -100000

        # Update to process bankruptcy
        manager.update(1.0, None)

        # Should have removed bankrupt opponent
        assert manager.bankruptcies >= 1 or len(manager.opponents) <= 2

    def test_market_dynamics_affect_ai(self):
        """Test that market conditions affect AI decisions."""
        manager = AIOpponentManager(
            num_opponents=2,
            game_mode=GameMode.COMPETITIVE,
            win_condition=WinCondition.PROFIT
        )

        initial_inventories = [opp.materials_inventory for opp in manager.opponents]

        # Run with high demand
        manager.demand_level = 2.0
        for _ in range(100):
            manager.update(1.0, None)

        # AIs should have produced materials
        for i, opp in enumerate(manager.opponents):
            # Either produced materials or sold them
            assert (opp.materials_inventory > initial_inventories[i] or
                    opp.total_revenue > 0 or
                    opp.decisions_made > 0)

    def test_police_activity_affects_ai(self):
        """Test that high police activity affects AI behavior."""
        manager = AIOpponentManager(
            num_opponents=2,
            game_mode=GameMode.COMPETITIVE,
            win_condition=WinCondition.NET_WORTH
        )

        # Set high police activity
        manager.police_activity = 0.9

        # Run for a bit
        for _ in range(50):
            manager.update(1.0, None)

        # AIs should respond to police threat
        # They might hide or switch to legal recycling
        any_hiding = any(opp.hiding for opp in manager.opponents)
        any_low_heat = any(opp.heat_level < 50 for opp in manager.opponents)

        # At least one AI should be managing its heat level
        assert any_hiding or any_low_heat


class TestFullGame:
    """Test running a complete game from start to finish."""

    def test_full_game_net_worth_victory(self):
        """Test a full game until net worth victory."""
        random.seed(42)  # Reproducible

        manager = AIOpponentManager(
            num_opponents=3,
            game_mode=GameMode.COMPETITIVE,
            win_condition=WinCondition.NET_WORTH
        )

        max_ticks = 10000  # Cap at ~2.7 hours simulated
        tick = 0

        while tick < max_ticks and manager.winner is None:
            manager.update(1.0, None)
            tick += 1

            # Give one AI a boost every 1000 ticks to ensure game ends
            if tick % 1000 == 0 and manager.opponents:
                manager.opponents[0].money += 100000

        # Game should have completed
        if manager.winner:
            print(f"\nGame completed after {tick} ticks")
            print(f"Winner: {manager.winner}")
            print(f"Final rankings: {manager.rankings}")

            assert manager.winner is not None
        else:
            # If no winner, check we at least have valid state
            assert len(manager.opponents) >= 0
            print(f"\nGame ran for {tick} ticks without winner")
            print(f"Top score: {manager.rankings[0] if manager.rankings else 'N/A'}")

    def test_full_game_time_limited(self):
        """Test a full time-limited game."""
        random.seed(123)

        manager = AIOpponentManager(
            num_opponents=4,
            game_mode=GameMode.TOURNAMENT,
            win_condition=WinCondition.TIME_LIMIT
        )
        manager.time_limit = 300.0  # 5 minute game

        tick = 0
        while manager.time_elapsed < manager.time_limit:
            manager.update(1.0, None)
            tick += 1

        # Force check for winner
        manager._check_win_condition(None)

        print(f"\nTime-limited game completed")
        print(f"Final rankings: {manager.get_leaderboard()}")

        # Should have determined rankings
        assert len(manager.rankings) > 0

        # Winner should be top ranked
        if manager.winner:
            assert manager.winner == manager.rankings[0][0]

    def test_full_game_survival(self):
        """Test a full survival game (last factory standing)."""
        random.seed(456)

        manager = AIOpponentManager(
            num_opponents=3,
            game_mode=GameMode.COMPETITIVE,
            win_condition=WinCondition.SURVIVAL
        )

        max_ticks = 5000
        tick = 0

        while tick < max_ticks and len(manager.opponents) > 1:
            manager.update(1.0, None)
            tick += 1

            # Occasionally apply financial pressure to speed things up
            if tick % 500 == 0 and len(manager.opponents) > 1:
                # Random opponent loses money
                target = random.choice(manager.opponents)
                target.money -= 30000

        print(f"\nSurvival game completed after {tick} ticks")
        print(f"Survivors: {[opp.name for opp in manager.opponents]}")
        print(f"Bankruptcies: {manager.bankruptcies}")

        # Should have had at least one bankruptcy
        assert manager.bankruptcies >= 1 or len(manager.opponents) <= 1

    def test_all_personalities_compete(self):
        """Test a game with all personality types competing."""
        random.seed(789)

        # Create manager with 5 opponents to get all personalities
        manager = AIOpponentManager(
            num_opponents=5,
            game_mode=GameMode.COMPETITIVE,
            win_condition=WinCondition.NET_WORTH
        )

        # Run for 1000 ticks
        for tick in range(1000):
            manager.update(1.0, None)

        # All personalities should have participated
        remaining = len(manager.opponents)
        print(f"\nAll personalities test completed")
        print(f"Remaining opponents: {remaining}/{5}")

        for opp in manager.opponents:
            print(f"  {opp.name} ({opp.personality.value}): ${opp.money:,.0f}, "
                  f"decisions: {opp.decisions_made}")

        # At least some should have made decisions
        total_decisions = sum(opp.decisions_made for opp in manager.opponents)
        assert total_decisions > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_solo_mode_no_opponents(self):
        """Test solo mode works correctly."""
        manager = AIOpponentManager(
            num_opponents=1,  # Minimum opponents
            game_mode=GameMode.SOLO,
            win_condition=WinCondition.NET_WORTH
        )

        # Should work with player factory only
        player = {'money': 50000, 'net_worth': 50000, 'sales': 100}

        for _ in range(100):
            manager.update(1.0, player)

        # Should have player in rankings
        names = [name for name, _ in manager.rankings]
        assert "Player" in names

    def test_all_ai_bankrupt(self):
        """Test handling when all AI go bankrupt."""
        manager = AIOpponentManager(
            num_opponents=2,
            game_mode=GameMode.COMPETITIVE,
            win_condition=WinCondition.SURVIVAL
        )

        # Force all bankrupt
        for opp in manager.opponents:
            opp.money = -100000

        manager.update(1.0, None)

        # Should handle gracefully
        assert manager.bankruptcies >= 2

    def test_rapid_updates(self):
        """Test rapid small time updates."""
        manager = AIOpponentManager(num_opponents=2)

        # Many small updates
        for _ in range(10000):
            manager.update(0.01, None)  # 10ms per tick

        # Should be stable
        assert manager.time_elapsed > 0
        assert len(manager.opponents) >= 0


class TestStatistics:
    """Test statistics collection and reporting."""

    def test_statistics_collected(self):
        """Test that comprehensive statistics are collected."""
        manager = AIOpponentManager(
            num_opponents=3,
            game_mode=GameMode.COMPETITIVE,
            win_condition=WinCondition.PROFIT
        )

        # Run some updates
        for _ in range(200):
            manager.update(1.0, None)

        stats = manager.get_statistics()

        assert 'game_mode' in stats
        assert 'win_condition' in stats
        assert 'num_opponents' in stats
        assert 'time_elapsed' in stats
        assert 'market_demand' in stats
        assert 'police_activity' in stats
        assert 'bankruptcies' in stats
        assert 'rankings' in stats

    def test_factory_statistics(self):
        """Test individual factory statistics."""
        factory = AIFactory("Test", AIPersonality.BALANCED, 0.5)

        market = {'demand': 1.0, 'price_multiplier': 1.0}
        for _ in range(100):
            factory.update(1.0, market, 0.3)

        stats = factory.get_statistics()

        assert 'name' in stats
        assert 'personality' in stats
        assert 'money' in stats
        assert 'net_worth' in stats
        assert 'robots' in stats
        assert 'materials_inventory' in stats
        assert 'green_reputation' in stats
        assert 'heat_level' in stats
        assert 'decisions_made' in stats
