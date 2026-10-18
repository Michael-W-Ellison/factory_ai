"""
Unit tests for ScoringManager.

Tests cover:
- Initialization
- Score calculations
- Achievement tracking and unlocking
- Statistics recording
- Final score calculation
- Rank determination
- Score breakdowns
"""

import pytest
from unittest.mock import MagicMock, patch

from src.systems.scoring_manager import ScoringManager, ScoreCategory, Achievement


class TestScoringManagerInitialization:
    """Tests for ScoringManager initialization."""

    def test_init_scores_zeroed(self):
        """Test that all score categories start at zero."""
        manager = ScoringManager()

        for category in ScoreCategory:
            assert manager.scores[category] == 0

    def test_init_score_multipliers_set(self):
        """Test that score multipliers are configured."""
        manager = ScoringManager()

        assert ScoreCategory.MONEY_EARNED in manager.score_multipliers
        assert ScoreCategory.BUILDINGS_BUILT in manager.score_multipliers
        assert manager.score_multipliers[ScoreCategory.BUILDINGS_BUILT] == 50

    def test_init_achievements_created(self):
        """Test that achievements are initialized."""
        manager = ScoringManager()

        assert len(manager.achievements) > 0
        assert 'first_dollar' in manager.achievements
        assert 'millionaire' in manager.achievements

    def test_init_stats_zeroed(self):
        """Test that all statistics start at zero."""
        manager = ScoringManager()

        assert manager.stats['total_money_earned'] == 0
        assert manager.stats['materials_processed'] == 0
        assert manager.stats['buildings_built'] == 0

    def test_init_not_completed(self):
        """Test that game starts as not completed."""
        manager = ScoringManager()

        assert manager.game_completed is False
        assert manager.total_score == 0
        assert manager.rank == "Novice"


class TestMoneyRecording:
    """Tests for money-related recording."""

    def test_record_money_earned(self):
        """Test recording money earned."""
        manager = ScoringManager()

        manager.record_money_earned(500.0)

        assert manager.stats['total_money_earned'] == 500.0

    def test_record_money_earned_accumulates(self):
        """Test that money earned accumulates."""
        manager = ScoringManager()

        manager.record_money_earned(100.0)
        manager.record_money_earned(200.0)

        assert manager.stats['total_money_earned'] == 300.0

    def test_first_dollar_achievement(self):
        """Test first dollar achievement unlocks."""
        manager = ScoringManager()

        manager.record_money_earned(1.0)

        assert manager.achievements['first_dollar'].unlocked is True

    def test_millionaire_achievement(self):
        """Test millionaire achievement at threshold."""
        manager = ScoringManager()

        manager.record_money_earned(1000000.0)

        assert manager.achievements['millionaire'].unlocked is True

    def test_record_money_spent(self):
        """Test recording money spent."""
        manager = ScoringManager()

        manager.record_money_spent(250.0)

        assert manager.stats['total_money_spent'] == 250.0

    def test_big_spender_achievement(self):
        """Test big spender achievement at threshold."""
        manager = ScoringManager()

        manager.record_money_spent(500000.0)

        assert manager.achievements['big_spender'].unlocked is True


class TestMaterialRecording:
    """Tests for material-related recording."""

    def test_record_material_processed(self):
        """Test recording processed materials."""
        manager = ScoringManager()

        manager.record_material_processed(100.0)

        assert manager.stats['materials_processed'] == 100.0

    def test_first_product_achievement(self):
        """Test first product achievement."""
        manager = ScoringManager()

        manager.record_material_processed(1.0)

        assert manager.achievements['first_product'].unlocked is True

    def test_mass_production_achievement(self):
        """Test mass production achievement at 10000."""
        manager = ScoringManager()

        manager.record_material_processed(10000.0)

        assert manager.achievements['mass_production'].unlocked is True

    def test_recycling_master_achievement(self):
        """Test recycling master achievement at 100000."""
        manager = ScoringManager()

        manager.record_material_processed(100000.0)

        assert manager.achievements['recycling_master'].unlocked is True


class TestBuildingRecording:
    """Tests for building-related recording."""

    def test_record_building_built(self):
        """Test recording building construction."""
        manager = ScoringManager()

        manager.record_building_built()

        assert manager.stats['buildings_built'] == 1

    def test_builder_achievement(self):
        """Test builder achievement at 10 buildings."""
        manager = ScoringManager()

        for _ in range(10):
            manager.record_building_built()

        assert manager.achievements['builder'].unlocked is True

    def test_architect_achievement(self):
        """Test architect achievement at 50 buildings."""
        manager = ScoringManager()

        for _ in range(50):
            manager.record_building_built()

        assert manager.achievements['architect'].unlocked is True

    def test_city_planner_achievement(self):
        """Test city planner achievement at 100 buildings."""
        manager = ScoringManager()

        for _ in range(100):
            manager.record_building_built()

        assert manager.achievements['city_planner'].unlocked is True


class TestDroneRecording:
    """Tests for drone-related recording."""

    def test_record_drone_deployed(self):
        """Test recording drone deployment."""
        manager = ScoringManager()

        manager.record_drone_deployed()

        assert manager.stats['drones_deployed'] == 1

    def test_drone_pilot_achievement(self):
        """Test drone pilot achievement at 10 drones."""
        manager = ScoringManager()

        for _ in range(10):
            manager.record_drone_deployed()

        assert manager.achievements['drone_pilot'].unlocked is True

    def test_record_drone_crashed(self):
        """Test recording drone crash."""
        manager = ScoringManager()

        manager.record_drone_crashed()

        assert manager.stats['drones_crashed'] == 1

    def test_crash_test_achievement(self):
        """Test crash test achievement at 5 crashes."""
        manager = ScoringManager()

        for _ in range(5):
            manager.record_drone_crashed()

        assert manager.achievements['crash_test'].unlocked is True


class TestBribeRecording:
    """Tests for bribe-related recording."""

    def test_record_successful_bribe(self):
        """Test recording successful bribe."""
        manager = ScoringManager()

        manager.record_bribe_attempt(success=True)

        assert manager.stats['bribes_attempted'] == 1
        assert manager.stats['bribes_successful'] == 1

    def test_record_failed_bribe(self):
        """Test recording failed bribe."""
        manager = ScoringManager()

        manager.record_bribe_attempt(success=False)

        assert manager.stats['bribes_attempted'] == 1
        assert manager.stats['bribes_successful'] == 0

    def test_master_negotiator_achievement(self):
        """Test master negotiator achievement at 10 successful bribes."""
        manager = ScoringManager()

        for _ in range(10):
            manager.record_bribe_attempt(success=True)

        assert manager.achievements['master_negotiator'].unlocked is True


class TestInspectionRecording:
    """Tests for inspection recording."""

    def test_record_passed_inspection(self):
        """Test recording passed inspection."""
        manager = ScoringManager()

        manager.record_inspection_result(passed=True)

        assert manager.stats['inspections_passed'] == 1
        assert manager.stats['inspections_failed'] == 0

    def test_record_failed_inspection(self):
        """Test recording failed inspection."""
        manager = ScoringManager()

        manager.record_inspection_result(passed=False)

        assert manager.stats['inspections_passed'] == 0
        assert manager.stats['inspections_failed'] == 1


class TestIllegalMaterialRecording:
    """Tests for illegal material recording."""

    def test_record_illegal_material(self):
        """Test recording illegal material processing."""
        manager = ScoringManager()

        manager.record_illegal_material(50.0)

        assert manager.stats['illegal_materials_processed'] == 50.0
        assert manager.stats['legal_materials_only'] is False

    def test_legal_materials_only_flag(self):
        """Test that legal_materials_only is True initially."""
        manager = ScoringManager()

        assert manager.stats['legal_materials_only'] is True


class TestSuspicionTracking:
    """Tests for suspicion tracking."""

    def test_update_suspicion_tracking(self):
        """Test suspicion tracking updates max."""
        manager = ScoringManager()

        manager.update_suspicion_tracking(50.0)

        assert manager.stats['max_suspicion'] == 50.0

    def test_suspicion_above_20_flag(self):
        """Test that suspicion above 20 sets flag to False."""
        manager = ScoringManager()

        manager.update_suspicion_tracking(25.0)

        assert manager.stats['suspicion_never_above_20'] is False

    def test_suspicion_below_20_keeps_flag(self):
        """Test that suspicion below 20 keeps flag True."""
        manager = ScoringManager()

        manager.update_suspicion_tracking(15.0)

        assert manager.stats['suspicion_never_above_20'] is True


class TestAchievementUnlocking:
    """Tests for achievement unlocking mechanics."""

    def test_unlock_achievement(self):
        """Test basic achievement unlocking."""
        manager = ScoringManager()

        manager.unlock_achievement('first_dollar', 100.0)

        assert manager.achievements['first_dollar'].unlocked is True
        assert manager.achievements['first_dollar'].unlock_time == 100.0

    def test_unlock_already_unlocked(self):
        """Test that re-unlocking doesn't change state."""
        manager = ScoringManager()
        manager.unlock_achievement('first_dollar', 100.0)

        manager.unlock_achievement('first_dollar', 200.0)

        assert manager.achievements['first_dollar'].unlock_time == 100.0

    def test_unlock_nonexistent_achievement(self):
        """Test that unlocking nonexistent achievement does nothing."""
        manager = ScoringManager()

        # Should not raise
        manager.unlock_achievement('fake_achievement', 0)


class TestFinalScoreCalculation:
    """Tests for final score calculation."""

    def test_calculate_final_score_basic(self):
        """Test basic final score calculation."""
        manager = ScoringManager()
        manager.record_money_earned(10000.0)
        manager.record_material_processed(100.0)
        manager.record_building_built()

        score = manager.calculate_final_score(
            game_time=86400.0,  # 1 day
            ending_type='LEGITIMATE_SUCCESS',
            current_money=5000.0,
            max_suspicion=30.0,
            exploration_percent=50.0
        )

        assert score > 0
        assert manager.game_completed is True

    def test_ending_bonus_applied(self):
        """Test that ending bonus affects score."""
        manager = ScoringManager()

        score_good = manager.calculate_final_score(
            game_time=86400.0,
            ending_type='PERFECT_CLEANUP',
            current_money=0,
            max_suspicion=0,
            exploration_percent=0
        )

        # Reset for comparison
        manager2 = ScoringManager()
        score_bad = manager2.calculate_final_score(
            game_time=86400.0,
            ending_type='BANKRUPTCY',
            current_money=0,
            max_suspicion=0,
            exploration_percent=0
        )

        assert score_good > score_bad

    def test_efficiency_score_calculation(self):
        """Test efficiency score based on collection vs processing."""
        manager = ScoringManager()
        manager.stats['materials_collected'] = 100
        manager.stats['materials_processed'] = 80

        manager.calculate_final_score(
            game_time=86400.0,
            ending_type='LEGITIMATE_SUCCESS',
            current_money=0,
            max_suspicion=0,
            exploration_percent=0
        )

        assert manager.efficiency_score == pytest.approx(0.8, rel=0.01)

    def test_stealth_score_calculation(self):
        """Test stealth score based on max suspicion."""
        manager = ScoringManager()

        manager.calculate_final_score(
            game_time=86400.0,
            ending_type='LEGITIMATE_SUCCESS',
            current_money=0,
            max_suspicion=75.0,  # 50% of 150 max
            exploration_percent=0
        )

        assert manager.stealth_score == pytest.approx(0.5, rel=0.01)

    def test_exploration_score_calculation(self):
        """Test exploration score based on percentage."""
        manager = ScoringManager()

        manager.calculate_final_score(
            game_time=86400.0,
            ending_type='LEGITIMATE_SUCCESS',
            current_money=0,
            max_suspicion=0,
            exploration_percent=75.0
        )

        assert manager.exploration_score == pytest.approx(0.75, rel=0.01)


class TestRankCalculation:
    """Tests for rank calculation."""

    def test_rank_novice(self):
        """Test Novice rank for low scores."""
        manager = ScoringManager()
        manager.total_score = 500

        manager._calculate_rank()

        assert manager.rank == "Novice"

    def test_rank_amateur(self):
        """Test Amateur rank."""
        manager = ScoringManager()
        manager.total_score = 3000

        manager._calculate_rank()

        assert manager.rank == "Amateur"

    def test_rank_professional(self):
        """Test Professional rank."""
        manager = ScoringManager()
        manager.total_score = 8000

        manager._calculate_rank()

        assert manager.rank == "Professional"

    def test_rank_expert(self):
        """Test Expert rank."""
        manager = ScoringManager()
        manager.total_score = 20000

        manager._calculate_rank()

        assert manager.rank == "Expert"

    def test_rank_grandmaster(self):
        """Test Grandmaster rank for highest scores."""
        manager = ScoringManager()
        manager.total_score = 150000

        manager._calculate_rank()

        assert manager.rank == "Grandmaster"


class TestScoreBreakdown:
    """Tests for score breakdown."""

    def test_get_score_breakdown_structure(self):
        """Test that breakdown contains all categories."""
        manager = ScoringManager()
        manager.scores[ScoreCategory.MONEY_EARNED] = 10000
        manager.scores[ScoreCategory.BUILDINGS_BUILT] = 5

        breakdown = manager.get_score_breakdown()

        assert 'money_earned' in breakdown
        assert 'buildings_built' in breakdown
        assert isinstance(breakdown['money_earned'], tuple)
        assert len(breakdown['money_earned']) == 2

    def test_breakdown_values_correct(self):
        """Test that breakdown values are correct."""
        manager = ScoringManager()
        manager.scores[ScoreCategory.BUILDINGS_BUILT] = 10

        breakdown = manager.get_score_breakdown()
        raw_value, points = breakdown['buildings_built']

        assert raw_value == 10
        assert points == 10 * 50  # 50 points per building


class TestAchievementQueries:
    """Tests for achievement query methods."""

    def test_get_unlocked_achievements(self):
        """Test getting list of unlocked achievements."""
        manager = ScoringManager()
        manager.unlock_achievement('first_dollar', 0)
        manager.unlock_achievement('first_product', 0)

        unlocked = manager.get_unlocked_achievements()

        assert len(unlocked) == 2
        assert all(a.unlocked for a in unlocked)

    def test_get_locked_achievements(self):
        """Test getting list of locked achievements."""
        manager = ScoringManager()

        locked = manager.get_locked_achievements()

        # Should be many locked achievements
        assert len(locked) > 0
        assert all(not a.unlocked for a in locked)
        # Hidden achievements should not be included
        assert all(not a.hidden for a in locked)

    def test_get_achievement_progress(self):
        """Test achievement progress calculation."""
        manager = ScoringManager()
        manager.unlock_achievement('first_dollar', 0)

        unlocked, total = manager.get_achievement_progress()

        assert unlocked == 1
        assert total > 1


class TestUpdate:
    """Tests for update method."""

    def test_update_increments_time(self):
        """Test that update increments time played."""
        manager = ScoringManager()

        manager.update(10.0, 0)

        assert manager.stats['time_played'] == 10.0

    def test_slow_burn_achievement(self):
        """Test slow burn achievement at 100 days."""
        manager = ScoringManager()

        # Simulate 100 days of game time
        game_time = 100 * 24 * 3600
        manager.update(1.0, game_time)

        assert manager.achievements['slow_burn'].unlocked is True


class TestSummary:
    """Tests for summary method."""

    def test_get_summary_structure(self):
        """Test that summary contains expected keys."""
        manager = ScoringManager()

        summary = manager.get_summary()

        assert 'total_score' in summary
        assert 'rank' in summary
        assert 'achievements_unlocked' in summary
        assert 'achievements_total' in summary
        assert 'score_breakdown' in summary
        assert 'statistics' in summary
        assert 'efficiency' in summary
        assert 'stealth' in summary
        assert 'exploration' in summary
        assert 'game_completed' in summary


class TestRepr:
    """Tests for string representation."""

    def test_repr_contains_score_info(self):
        """Test that repr contains score information."""
        manager = ScoringManager()
        manager.total_score = 5000
        manager.rank = "Amateur"

        repr_str = repr(manager)

        assert 'ScoringManager' in repr_str
        assert 'score=5000' in repr_str
        assert 'Amateur' in repr_str


class TestMiscellaneousRecording:
    """Tests for other recording methods."""

    def test_record_city_material(self):
        """Test recording city material collection."""
        manager = ScoringManager()

        manager.record_city_material(100.0)

        assert manager.stats['city_materials_collected'] == 100.0

    def test_record_violation(self):
        """Test recording violation."""
        manager = ScoringManager()

        manager.record_violation()

        assert manager.stats['violations_count'] == 1

    def test_record_fine_paid(self):
        """Test recording fine payment."""
        manager = ScoringManager()

        manager.record_fine_paid(5000.0)

        assert manager.stats['fines_paid'] == 5000.0

    def test_record_energy_usage(self):
        """Test recording energy usage."""
        manager = ScoringManager()

        manager.record_energy_usage(total=1000.0, renewable=400.0)

        assert manager.stats['total_energy_used'] == 1000.0
        assert manager.stats['renewable_energy_used'] == 400.0

    def test_record_litter_cleaned(self):
        """Test recording litter cleaned."""
        manager = ScoringManager()

        manager.record_litter_cleaned(50.0)

        assert manager.stats['litter_cleaned'] == 50.0

    def test_record_pollution(self):
        """Test recording pollution."""
        manager = ScoringManager()

        manager.record_pollution(25.0)

        assert manager.stats['air_pollution_total'] == 25.0

    def test_record_high_risk_operation(self):
        """Test recording high risk operation."""
        manager = ScoringManager()

        manager.record_high_risk_operation()

        assert manager.stats['high_risk_operations'] == 1

    def test_update_landfill_progress(self):
        """Test updating landfill progress."""
        manager = ScoringManager()

        manager.update_landfill_progress(45.5)

        assert manager.stats['landfill_cleared_percent'] == 45.5
