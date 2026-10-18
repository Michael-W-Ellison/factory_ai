"""
Unit tests for AuthorityManager.

Tests law enforcement tier escalation, FBI investigation mechanics,
social engineering countermeasures, and game ending conditions.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.systems.authority_manager import (
    AuthorityManager, AuthorityTier, InvestigationType, GameEnding
)
from src.core.game_config import AUTHORITY


@pytest.fixture
def mock_resource_manager():
    """Create a mock resource manager."""
    mock = MagicMock()
    mock.money = 100000.0
    mock.modify_money = MagicMock()
    return mock


@pytest.fixture
def mock_suspicion_manager():
    """Create a mock suspicion manager."""
    mock = MagicMock()
    mock.suspicion_level = 0.0
    mock.add_suspicion = MagicMock()
    return mock


@pytest.fixture
def mock_inspection_manager():
    """Create a mock inspection manager."""
    mock = MagicMock()
    mock.last_result = None
    mock.is_game_over = MagicMock(return_value=False)
    mock.game_over_reason = ""
    return mock


@pytest.fixture
def authority_manager(mock_suspicion_manager, mock_resource_manager, mock_inspection_manager):
    """Create an AuthorityManager with mocked dependencies."""
    return AuthorityManager(
        mock_suspicion_manager,
        mock_resource_manager,
        mock_inspection_manager
    )


class TestAuthorityManagerInitialization:
    """Test AuthorityManager initialization."""

    def test_initialization_defaults(
            self, mock_suspicion_manager, mock_resource_manager, mock_inspection_manager):
        """Test that AuthorityManager initializes with correct defaults."""
        manager = AuthorityManager(
            mock_suspicion_manager, mock_resource_manager, mock_inspection_manager
        )

        assert manager.current_tier == AuthorityTier.LOCAL
        assert manager.tier_changed is False
        assert manager.fbi_investigation_active is False
        assert manager.investigation_type == InvestigationType.NONE
        assert manager.investigation_progress == 0.0
        assert manager.raid_scheduled is False
        assert manager.game_ending == GameEnding.NONE
        assert manager.tier_escalations == 0
        assert manager.bribes_attempted == 0

    def test_config_thresholds_loaded(self, authority_manager):
        """Test that config thresholds are loaded."""
        assert authority_manager.state_threshold == AUTHORITY.STATE_THRESHOLD
        assert authority_manager.federal_threshold == AUTHORITY.FEDERAL_THRESHOLD


class TestTierEscalation:
    """Test authority tier escalation logic."""

    def test_tier_escalation_to_state(self, authority_manager, mock_suspicion_manager):
        """Test escalation from Local to State tier."""
        mock_suspicion_manager.suspicion_level = 60.0  # Above STATE_THRESHOLD (50)

        authority_manager.update(1.0, 1000.0)

        assert authority_manager.current_tier == AuthorityTier.STATE
        assert authority_manager.tier_changed is True
        assert authority_manager.tier_escalations == 1

    def test_tier_escalation_to_federal(self, authority_manager, mock_suspicion_manager):
        """Test escalation to Federal tier."""
        mock_suspicion_manager.suspicion_level = 110.0  # Above FEDERAL_THRESHOLD (100)

        authority_manager.update(1.0, 1000.0)

        assert authority_manager.current_tier == AuthorityTier.FEDERAL
        assert authority_manager.fbi_investigation_active is True

    def test_tier_deescalation(self, authority_manager, mock_suspicion_manager):
        """Test tier de-escalation when suspicion drops."""
        authority_manager.current_tier = AuthorityTier.STATE
        mock_suspicion_manager.suspicion_level = 30.0  # Below STATE_THRESHOLD

        authority_manager.update(1.0, 1000.0)

        assert authority_manager.current_tier == AuthorityTier.LOCAL
        assert authority_manager.tier_changed is True

    def test_no_tier_change_same_level(self, authority_manager, mock_suspicion_manager):
        """Test no tier change when suspicion stays in same range."""
        mock_suspicion_manager.suspicion_level = 30.0  # Still LOCAL

        authority_manager.update(1.0, 1000.0)
        authority_manager.update(1.0, 2000.0)

        assert authority_manager.tier_changed is False


class TestFBIInvestigation:
    """Test FBI investigation mechanics."""

    def test_fbi_investigation_starts_at_federal(self, authority_manager, mock_suspicion_manager):
        """Test that FBI investigation starts when reaching Federal tier."""
        mock_suspicion_manager.suspicion_level = 110.0

        authority_manager.update(1.0, 1000.0)

        assert authority_manager.fbi_investigation_active is True
        assert authority_manager.investigation_type != InvestigationType.NONE
        # Progress may be slightly above 0 due to update in same call
        assert authority_manager.investigation_progress < 0.01

    def test_investigation_progress_increases(self, authority_manager, mock_suspicion_manager):
        """Test that investigation progress increases over time."""
        mock_suspicion_manager.suspicion_level = 50.0  # Avoid triggering new escalation
        authority_manager.fbi_investigation_active = True
        authority_manager.investigation_progress = 0.0

        # Update for 2 game hours (7200 seconds)
        authority_manager.update(7200.0, 10000.0)

        assert authority_manager.investigation_progress > 0.0

    def test_investigation_progress_affected_by_disruption(
            self, authority_manager, mock_suspicion_manager):
        """Test that disruption factor slows investigation."""
        mock_suspicion_manager.suspicion_level = 50.0
        authority_manager.fbi_investigation_active = True
        authority_manager.investigation_progress = 0.0
        authority_manager.disruption_factor = 0.5  # 50% disruption

        authority_manager.update(3600.0, 5000.0)
        progress_with_disruption = authority_manager.investigation_progress

        # Reset and test without disruption
        authority_manager.investigation_progress = 0.0
        authority_manager.disruption_factor = 0.0

        authority_manager.update(3600.0, 5000.0)
        progress_without_disruption = authority_manager.investigation_progress

        assert progress_with_disruption < progress_without_disruption

    def test_raid_scheduled_when_investigation_completes(
            self, authority_manager, mock_suspicion_manager):
        """Test that raid is scheduled when investigation reaches 100%."""
        mock_suspicion_manager.suspicion_level = 50.0
        authority_manager.fbi_investigation_active = True
        authority_manager.investigation_progress = 99.9

        # Update to complete investigation
        authority_manager.update(3600.0, 50000.0)

        assert authority_manager.raid_scheduled is True
        assert authority_manager.raid_countdown > 0


class TestRaidMechanics:
    """Test FBI raid mechanics."""

    def test_raid_countdown_decreases(self, authority_manager, mock_suspicion_manager):
        """Test that raid countdown decreases."""
        mock_suspicion_manager.suspicion_level = 50.0
        authority_manager.raid_scheduled = True
        authority_manager.raid_countdown = 10000.0

        authority_manager.update(2000.0, 5000.0)

        assert authority_manager.raid_countdown == 8000.0

    def test_raid_executes_when_countdown_expires(
            self, authority_manager, mock_suspicion_manager):
        """Test that raid executes when countdown reaches zero."""
        mock_suspicion_manager.suspicion_level = 50.0
        authority_manager.raid_scheduled = True
        authority_manager.raid_countdown = 100.0

        authority_manager.update(200.0, 5000.0)

        assert authority_manager.game_ending == GameEnding.FBI_RAID
        assert authority_manager.raid_scheduled is False


class TestBribeMechanic:
    """Test bribery mechanics."""

    def test_bribe_on_cooldown_fails(self, authority_manager):
        """Test that bribe fails during cooldown."""
        authority_manager.bribe_cooldown = 1000.0

        result = authority_manager.attempt_bribe()

        assert result is False

    def test_bribe_insufficient_funds_fails(self, authority_manager, mock_resource_manager):
        """Test that bribe fails with insufficient funds."""
        mock_resource_manager.money = 5000.0  # Less than default 10000

        result = authority_manager.attempt_bribe(amount=10000)

        assert result is False

    def test_bribe_success_at_local_tier(
            self, authority_manager, mock_resource_manager, mock_suspicion_manager):
        """Test that bribe is more likely to succeed at Local tier."""
        mock_resource_manager.money = 50000.0
        authority_manager.current_tier = AuthorityTier.LOCAL

        # Patch random to force success (below LOCAL_BRIBE_SUCCESS_RATE)
        with patch('random.random', return_value=0.5):
            result = authority_manager.attempt_bribe()

        assert result is True
        assert authority_manager.bribes_successful == 1
        mock_resource_manager.modify_money.assert_called()

    def test_bribe_reduces_suspicion_when_no_investigation(
            self, authority_manager, mock_resource_manager, mock_suspicion_manager):
        """Test that successful bribe reduces suspicion."""
        mock_resource_manager.money = 50000.0
        authority_manager.fbi_investigation_active = False

        with patch('random.random', return_value=0.1):
            with patch('random.randint', return_value=15):
                authority_manager.attempt_bribe()

        mock_suspicion_manager.add_suspicion.assert_called()

    def test_bribe_reduces_investigation_progress(
            self, authority_manager, mock_resource_manager, mock_suspicion_manager):
        """Test that successful bribe reduces investigation progress."""
        mock_resource_manager.money = 50000.0
        authority_manager.fbi_investigation_active = True
        authority_manager.investigation_progress = 50.0

        with patch('random.random', return_value=0.1):
            with patch('random.uniform', return_value=20.0):
                authority_manager.attempt_bribe()

        assert authority_manager.investigation_progress < 50.0

    def test_bribe_failure_increases_suspicion(
            self, authority_manager, mock_resource_manager, mock_suspicion_manager):
        """Test that failed bribe increases suspicion."""
        mock_resource_manager.money = 50000.0

        # Patch random to force failure
        with patch('random.random', return_value=0.99):
            authority_manager.attempt_bribe()

        mock_suspicion_manager.add_suspicion.assert_called()
        # Check suspicion was increased (positive value)
        call_args = mock_suspicion_manager.add_suspicion.call_args[0]
        assert call_args[0] > 0

    def test_bribe_sets_cooldown(self, authority_manager, mock_resource_manager):
        """Test that bribe attempt sets cooldown."""
        mock_resource_manager.money = 50000.0
        authority_manager.bribe_cooldown = 0.0

        with patch('random.random', return_value=0.1):
            with patch('random.uniform', return_value=100000.0):
                authority_manager.attempt_bribe()

        assert authority_manager.bribe_cooldown > 0


class TestFalseEvidence:
    """Test false evidence planting mechanics."""

    def test_plant_false_evidence_success(
            self, authority_manager, mock_resource_manager, mock_suspicion_manager):
        """Test successful false evidence planting."""
        mock_resource_manager.money = 50000.0
        authority_manager.fbi_investigation_active = True

        with patch('random.random', return_value=0.1):
            result = authority_manager.plant_false_evidence()

        assert result is True
        assert authority_manager.evidence_planted is True
        assert authority_manager.disruption_factor == 0.5
        mock_resource_manager.modify_money.assert_called_with(-15000)

    def test_plant_false_evidence_already_planted(self, authority_manager):
        """Test that cannot plant evidence twice."""
        authority_manager.evidence_planted = True
        authority_manager.fbi_investigation_active = True

        result = authority_manager.plant_false_evidence()

        assert result is False

    def test_plant_false_evidence_no_investigation(self, authority_manager):
        """Test that cannot plant evidence without investigation."""
        authority_manager.fbi_investigation_active = False

        result = authority_manager.plant_false_evidence()

        assert result is False

    def test_plant_false_evidence_failure_increases_suspicion(
            self, authority_manager, mock_resource_manager, mock_suspicion_manager):
        """Test that failed evidence planting increases suspicion."""
        mock_resource_manager.money = 50000.0
        authority_manager.fbi_investigation_active = True
        original_speed = authority_manager.investigation_speed

        with patch('random.random', return_value=0.99):
            result = authority_manager.plant_false_evidence()

        assert result is False
        mock_suspicion_manager.add_suspicion.assert_called()
        assert authority_manager.investigation_speed > original_speed


class TestEscape:
    """Test escape mechanics."""

    def test_attempt_escape_without_investigation_fails(self, authority_manager):
        """Test that cannot escape without active investigation."""
        authority_manager.fbi_investigation_active = False

        result = authority_manager.attempt_escape()

        assert result is False

    def test_attempt_escape_success(self, authority_manager):
        """Test successful escape."""
        authority_manager.fbi_investigation_active = True
        authority_manager.investigation_progress = 10.0  # Low progress = high success rate

        with patch('random.random', return_value=0.1):
            result = authority_manager.attempt_escape()

        assert result is True
        assert authority_manager.game_ending == GameEnding.ESCAPE

    def test_attempt_escape_failure_triggers_raid(self, authority_manager, mock_suspicion_manager):
        """Test that failed escape triggers immediate raid."""
        mock_suspicion_manager.suspicion_level = 50.0
        authority_manager.fbi_investigation_active = True
        authority_manager.investigation_progress = 90.0  # High progress = low success rate

        with patch('random.random', return_value=0.99):
            result = authority_manager.attempt_escape()

        assert result is False
        assert authority_manager.game_ending == GameEnding.FBI_RAID


class TestPleaDeal:
    """Test plea deal mechanics."""

    def test_plea_deal_without_investigation_fails(self, authority_manager):
        """Test that cannot negotiate without investigation."""
        authority_manager.fbi_investigation_active = False

        result = authority_manager.negotiate_plea_deal()

        assert result is False

    def test_plea_deal_too_early_fails(self, authority_manager):
        """Test that cannot negotiate if investigation is too early."""
        authority_manager.fbi_investigation_active = True
        authority_manager.investigation_progress = 20.0

        result = authority_manager.negotiate_plea_deal()

        assert result is False

    def test_plea_deal_too_late_fails(self, authority_manager):
        """Test that cannot negotiate if investigation is too late."""
        authority_manager.fbi_investigation_active = True
        authority_manager.investigation_progress = 90.0

        result = authority_manager.negotiate_plea_deal()

        assert result is False

    def test_plea_deal_success(self, authority_manager, mock_resource_manager):
        """Test successful plea deal."""
        mock_resource_manager.money = 100000.0
        authority_manager.fbi_investigation_active = True
        authority_manager.investigation_progress = 50.0

        result = authority_manager.negotiate_plea_deal()

        assert result is True
        assert authority_manager.game_ending == GameEnding.PLEA_DEAL
        mock_resource_manager.modify_money.assert_called()


class TestGameEndingConditions:
    """Test various game ending conditions."""

    def test_bankruptcy_triggers_ending(
            self, authority_manager, mock_resource_manager, mock_suspicion_manager):
        """Test that bankruptcy triggers game ending."""
        mock_resource_manager.money = -60000  # Below BANKRUPTCY_THRESHOLD
        mock_suspicion_manager.suspicion_level = 30.0

        authority_manager.update(1.0, 5000.0)

        assert authority_manager.game_ending == GameEnding.BANKRUPTCY

    def test_inspection_failure_triggers_ending(
            self, authority_manager, mock_inspection_manager, mock_suspicion_manager):
        """Test that inspection failure triggers game ending."""
        mock_inspection_manager.is_game_over.return_value = True
        mock_inspection_manager.game_over_reason = "Critical failure"
        mock_suspicion_manager.suspicion_level = 30.0

        authority_manager.update(1.0, 5000.0)

        assert authority_manager.game_ending == GameEnding.INSPECTOR_FAILURE

    def test_already_ended_game_not_retriggered(
            self, authority_manager, mock_resource_manager, mock_suspicion_manager):
        """Test that game ending is not retriggered."""
        mock_suspicion_manager.suspicion_level = 30.0
        authority_manager.game_ending = GameEnding.ESCAPE
        mock_resource_manager.money = -60000

        authority_manager.update(1.0, 5000.0)

        # Should still be ESCAPE, not changed to BANKRUPTCY
        assert authority_manager.game_ending == GameEnding.ESCAPE


class TestVictoryConditions:
    """Test victory condition evaluation."""

    def test_check_victory_conditions_incomplete_landfill(self, authority_manager):
        """Test that victory requires complete landfill."""
        mock_scoring = MagicMock()
        mock_scoring.stats = {'landfill_cleared_percent': 50.0}

        result = authority_manager.check_victory_conditions(mock_scoring, 100000.0)

        assert result is False
        assert authority_manager.game_ending == GameEnding.NONE

    def test_perfect_cleanup_ending(
            self, authority_manager, mock_suspicion_manager, mock_resource_manager):
        """Test perfect cleanup victory ending."""
        mock_suspicion_manager.suspicion_level = 0.0
        mock_resource_manager.money = 100000.0
        authority_manager.fbi_investigation_active = False

        mock_scoring = MagicMock()
        mock_scoring.stats = {
            'landfill_cleared_percent': 100.0,
            'max_suspicion': 0,
            'violations_count': 0,
            'fines_paid': 0,
            'illegal_materials_processed': 0,
            'city_materials_collected': 0,
            'materials_collected': 1000,
            'renewable_energy_used': 800,
            'total_energy_used': 1000,
            'litter_cleaned': 100,
            'air_pollution_total': 500,
            'high_risk_operations': 0,
            'inspections_passed': 3,
            'inspections_failed': 0,
            'suspicion_never_above_20': True,
        }

        result = authority_manager.check_victory_conditions(mock_scoring, 100000.0)

        assert result is True
        assert authority_manager.game_ending == GameEnding.PERFECT_CLEANUP

    def test_legitimate_success_ending(
            self, authority_manager, mock_suspicion_manager, mock_resource_manager):
        """Test legitimate success victory ending."""
        mock_suspicion_manager.suspicion_level = 30.0
        mock_resource_manager.money = 50000.0
        authority_manager.fbi_investigation_active = False

        mock_scoring = MagicMock()
        mock_scoring.stats = {
            'landfill_cleared_percent': 100.0,
            'max_suspicion': 40,
            'violations_count': 5,
            'fines_paid': 10000,
            'illegal_materials_processed': 100,
            'city_materials_collected': 100,
            'materials_collected': 1000,
            'renewable_energy_used': 500,
            'total_energy_used': 1000,
            'litter_cleaned': 100,
            'air_pollution_total': 2000,
            'high_risk_operations': 3,
            'inspections_passed': 2,
            'inspections_failed': 1,
            'suspicion_never_above_20': False,
        }

        result = authority_manager.check_victory_conditions(mock_scoring, 300000.0)

        assert result is True
        assert authority_manager.game_ending in [
            GameEnding.LEGITIMATE_SUCCESS,
            GameEnding.EFFICIENT_OPERATOR,
            GameEnding.URBAN_RECYCLER
        ]


class TestStatusSummary:
    """Test status summary generation."""

    def test_get_status_summary_complete(self, authority_manager):
        """Test that status summary contains all fields."""
        authority_manager.current_tier = AuthorityTier.STATE
        authority_manager.fbi_investigation_active = True
        authority_manager.investigation_progress = 50.0
        authority_manager.raid_scheduled = True
        authority_manager.raid_countdown = 7200.0
        authority_manager.bribe_cooldown = 3600.0

        summary = authority_manager.get_status_summary()

        assert 'current_tier' in summary
        assert 'tier_name' in summary
        assert 'fbi_investigation_active' in summary
        assert 'investigation_type' in summary
        assert 'investigation_progress' in summary
        assert 'raid_scheduled' in summary
        assert 'raid_countdown_hours' in summary
        assert 'bribe_available' in summary
        assert 'bribe_cooldown_hours' in summary
        assert 'game_ending' in summary
        assert 'can_escape' in summary
        assert 'can_plea_deal' in summary

        assert summary['tier_name'] == 'STATE'
        assert summary['raid_countdown_hours'] == pytest.approx(2.0, rel=0.01)
        assert summary['bribe_available'] is False

    def test_is_game_over(self, authority_manager):
        """Test is_game_over helper method."""
        assert authority_manager.is_game_over() is False

        authority_manager.game_ending = GameEnding.FBI_RAID

        assert authority_manager.is_game_over() is True

    def test_get_game_ending(self, authority_manager):
        """Test get_game_ending method."""
        assert authority_manager.get_game_ending() == GameEnding.NONE

        authority_manager.game_ending = GameEnding.ESCAPE

        assert authority_manager.get_game_ending() == GameEnding.ESCAPE


class TestCooldowns:
    """Test cooldown mechanics."""

    def test_bribe_cooldown_decreases(self, authority_manager, mock_suspicion_manager):
        """Test that bribe cooldown decreases over time."""
        mock_suspicion_manager.suspicion_level = 30.0
        authority_manager.bribe_cooldown = 5000.0

        authority_manager.update(1000.0, 5000.0)

        assert authority_manager.bribe_cooldown == 4000.0

    def test_bribe_cooldown_does_not_go_negative(
            self, authority_manager, mock_suspicion_manager):
        """Test that bribe cooldown stops at zero."""
        mock_suspicion_manager.suspicion_level = 30.0
        authority_manager.bribe_cooldown = 100.0

        authority_manager.update(200.0, 5000.0)

        assert authority_manager.bribe_cooldown <= 0


class TestRepr:
    """Test string representation."""

    def test_repr_basic(self, authority_manager):
        """Test basic __repr__ format."""
        repr_str = repr(authority_manager)

        assert "AuthorityManager" in repr_str
        assert "LOCAL" in repr_str

    def test_repr_with_investigation(self, authority_manager):
        """Test __repr__ with active investigation."""
        authority_manager.fbi_investigation_active = True
        authority_manager.investigation_progress = 45.5

        repr_str = repr(authority_manager)

        assert "FBI_INVESTIGATION" in repr_str
        assert "45.5" in repr_str

    def test_repr_with_raid_scheduled(self, authority_manager):
        """Test __repr__ with scheduled raid."""
        authority_manager.raid_scheduled = True

        repr_str = repr(authority_manager)

        assert "RAID_SCHEDULED" in repr_str

    def test_repr_with_ending(self, authority_manager):
        """Test __repr__ with game ending."""
        authority_manager.game_ending = GameEnding.FBI_RAID

        repr_str = repr(authority_manager)

        assert "ENDING=FBI_RAID" in repr_str


class TestLandfillComplete:
    """Test landfill completion handling."""

    def test_trigger_landfill_complete(
            self, authority_manager, mock_suspicion_manager, mock_resource_manager):
        """Test trigger_landfill_complete method."""
        mock_suspicion_manager.suspicion_level = 20.0
        mock_resource_manager.money = 100000.0

        mock_scoring = MagicMock()
        mock_scoring.update_landfill_progress = MagicMock()
        mock_scoring.stats = {
            'landfill_cleared_percent': 100.0,
            'max_suspicion': 30,
            'violations_count': 0,
            'fines_paid': 0,
            'illegal_materials_processed': 0,
            'city_materials_collected': 200,
            'materials_collected': 1000,
            'renewable_energy_used': 500,
            'total_energy_used': 1000,
            'litter_cleaned': 100,
            'air_pollution_total': 500,
            'high_risk_operations': 0,
            'inspections_passed': 2,
            'inspections_failed': 0,
            'suspicion_never_above_20': True,
        }

        authority_manager.trigger_landfill_complete(mock_scoring, 100000.0)

        mock_scoring.update_landfill_progress.assert_called_with(100.0)
        assert authority_manager.game_ending != GameEnding.NONE
