"""
Unit tests for FBIManager.

Tests FBI investigation triggers, countdown mechanics, raid execution,
and avoidance strategies (bribery, laying low).
"""

import pytest
from unittest.mock import MagicMock, patch

from src.systems.fbi_manager import FBIManager, FBIStatus, FBITrigger
from src.core.game_config import FBI


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
def fbi_manager(mock_resource_manager, mock_suspicion_manager):
    """Create an FBIManager with mocked dependencies."""
    return FBIManager(mock_resource_manager, mock_suspicion_manager)


class TestFBIManagerInitialization:
    """Test FBIManager initialization."""

    def test_initialization_defaults(self, mock_resource_manager, mock_suspicion_manager):
        """Test that FBIManager initializes with correct defaults."""
        manager = FBIManager(mock_resource_manager, mock_suspicion_manager)

        assert manager.status == FBIStatus.NONE
        assert manager.trigger_reason is None
        assert manager.investigation_countdown == 0.0
        assert manager.high_suspicion_duration == 0.0
        assert manager.fbi_agents_active is False
        assert manager.can_bribe is True
        assert manager.laying_low is False
        assert manager.events == []

    def test_config_values_loaded(self, fbi_manager):
        """Test that config values are loaded correctly."""
        assert fbi_manager.investigation_duration == FBI.INVESTIGATION_DURATION
        assert fbi_manager.raid_warning_time == FBI.RAID_WARNING_TIME
        assert fbi_manager.bribe_cost == FBI.BRIBE_COST


class TestHighSuspicionTracking:
    """Test high suspicion duration tracking."""

    def test_high_suspicion_accumulates(self, fbi_manager, mock_suspicion_manager):
        """Test that high suspicion duration accumulates."""
        mock_suspicion_manager.suspicion_level = 85.0  # Above HIGH_SUSPICION_LEVEL (80)

        fbi_manager.update(1000.0, 1000.0)

        assert fbi_manager.high_suspicion_duration == 1000.0

    def test_high_suspicion_resets_when_below_threshold(self, fbi_manager, mock_suspicion_manager):
        """Test that duration resets when suspicion drops."""
        fbi_manager.high_suspicion_duration = 5000.0
        mock_suspicion_manager.suspicion_level = 50.0  # Below threshold

        fbi_manager.update(1000.0, 1000.0)

        assert fbi_manager.high_suspicion_duration == 0.0

    def test_high_suspicion_triggers_investigation(self, fbi_manager, mock_suspicion_manager):
        """Test that prolonged high suspicion triggers investigation."""
        mock_suspicion_manager.suspicion_level = 85.0
        fbi_manager.high_suspicion_duration = FBI.HIGH_SUSPICION_THRESHOLD

        fbi_manager.update(1.0, 1000.0)

        assert fbi_manager.status == FBIStatus.TRIGGERED
        assert fbi_manager.trigger_reason == FBITrigger.HIGH_SUSPICION


class TestInvestigationTriggers:
    """Test various FBI investigation triggers."""

    def test_critical_inspection_triggers_investigation(self, fbi_manager):
        """Test that critical inspection failure triggers investigation."""
        fbi_manager.report_inspection_failure(is_critical=True)

        fbi_manager.update(1.0, 1000.0)

        assert fbi_manager.status == FBIStatus.TRIGGERED
        assert fbi_manager.trigger_reason == FBITrigger.CRITICAL_INSPECTION

    def test_multiple_failures_triggers_investigation(self, fbi_manager):
        """Test that 3 failed inspections trigger investigation."""
        fbi_manager.report_inspection_failure(is_critical=False)
        fbi_manager.report_inspection_failure(is_critical=False)
        fbi_manager.report_inspection_failure(is_critical=False)

        fbi_manager.update(1.0, 1000.0)

        assert fbi_manager.status == FBIStatus.TRIGGERED
        assert fbi_manager.trigger_reason == FBITrigger.MULTIPLE_FAILURES

    def test_excessive_camera_hacks_triggers_investigation(self, fbi_manager):
        """Test that excessive camera hacking triggers investigation."""
        fbi_manager.report_camera_hacks(25, 1000.0)

        assert fbi_manager.status == FBIStatus.TRIGGERED
        assert fbi_manager.trigger_reason == FBITrigger.EXCESSIVE_HACKING

    def test_camera_hacks_below_threshold_no_trigger(self, fbi_manager):
        """Test that camera hacks below threshold do not trigger."""
        fbi_manager.report_camera_hacks(15, 1000.0)

        assert fbi_manager.status == FBIStatus.NONE


class TestInvestigationCountdown:
    """Test investigation countdown mechanics."""

    def test_investigation_countdown_starts(self, fbi_manager):
        """Test that countdown starts when investigation is triggered."""
        fbi_manager._trigger_investigation(FBITrigger.HIGH_SUSPICION, 1000.0)

        assert fbi_manager.investigation_countdown == FBI.INVESTIGATION_DURATION
        assert fbi_manager.fbi_agents_active is True

    def test_countdown_decreases_over_time(self, fbi_manager):
        """Test that countdown decreases during update."""
        fbi_manager.status = FBIStatus.TRIGGERED
        fbi_manager.investigation_countdown = 10000.0

        fbi_manager.update(1000.0, 2000.0)

        assert fbi_manager.investigation_countdown == 9000.0

    def test_raid_imminent_status(self, fbi_manager, mock_suspicion_manager):
        """Test transition to RAID_IMMINENT status."""
        mock_suspicion_manager.suspicion_level = 50.0  # Below high suspicion
        fbi_manager.status = FBIStatus.TRIGGERED
        fbi_manager.investigation_countdown = FBI.RAID_WARNING_TIME - 100

        fbi_manager.update(0.1, 5000.0)

        assert fbi_manager.status == FBIStatus.RAID_IMMINENT

    def test_raid_triggered_when_countdown_expires(self, fbi_manager, mock_suspicion_manager):
        """Test that raid is triggered when countdown reaches zero."""
        mock_suspicion_manager.suspicion_level = 50.0
        fbi_manager.status = FBIStatus.TRIGGERED
        fbi_manager.investigation_countdown = 100.0

        fbi_manager.update(200.0, 5000.0)

        assert fbi_manager.status == FBIStatus.RAIDED


class TestBribeMechanic:
    """Test bribery mechanics."""

    def test_attempt_bribe_insufficient_funds(self, fbi_manager, mock_resource_manager):
        """Test that bribe fails with insufficient funds."""
        mock_resource_manager.money = 1000.0

        result = fbi_manager.attempt_bribe(5000.0)

        assert result is False
        mock_resource_manager.modify_money.assert_not_called()

    def test_attempt_bribe_not_available(self, fbi_manager):
        """Test that bribe fails when not available."""
        fbi_manager.can_bribe = False

        result = fbi_manager.attempt_bribe(5000.0)

        assert result is False

    def test_attempt_bribe_success(self, fbi_manager, mock_resource_manager, mock_suspicion_manager):
        """Test successful bribe clears investigation."""
        mock_resource_manager.money = 100000.0
        fbi_manager.status = FBIStatus.TRIGGERED
        fbi_manager.investigation_countdown = 50000.0
        fbi_manager.fbi_agents_active = True

        # Patch random to force success
        with patch('random.random', return_value=0.99):  # Above bribe_risk
            result = fbi_manager.attempt_bribe(5000.0)

        assert result is True
        assert fbi_manager.status == FBIStatus.NONE
        assert fbi_manager.investigation_countdown == 0.0
        assert fbi_manager.fbi_agents_active is False
        assert fbi_manager.can_bribe is False  # Only one attempt allowed
        mock_resource_manager.modify_money.assert_called_with(-FBI.BRIBE_COST)

    def test_attempt_bribe_failure_increases_suspicion(
            self, fbi_manager, mock_resource_manager, mock_suspicion_manager):
        """Test that failed bribe increases suspicion and accelerates investigation."""
        mock_resource_manager.money = 100000.0
        fbi_manager.status = FBIStatus.TRIGGERED
        fbi_manager.investigation_countdown = 50000.0

        # Patch random to force failure
        with patch('random.random', return_value=0.1):  # Below bribe_risk
            result = fbi_manager.attempt_bribe(5000.0)

        assert result is False
        mock_suspicion_manager.add_suspicion.assert_called()
        assert fbi_manager.investigation_countdown < 50000.0  # Accelerated
        assert fbi_manager.can_bribe is False


class TestLayingLowMechanic:
    """Test laying low mechanics."""

    def test_start_lay_low_success(self, fbi_manager):
        """Test starting to lay low."""
        fbi_manager.status = FBIStatus.TRIGGERED

        result = fbi_manager.start_lay_low(1000.0)

        assert result is True
        assert fbi_manager.laying_low is True
        assert fbi_manager.lay_low_duration == 0.0

    def test_start_lay_low_when_already_laying_low(self, fbi_manager):
        """Test that cannot start laying low if already doing so."""
        fbi_manager.status = FBIStatus.TRIGGERED
        fbi_manager.laying_low = True

        result = fbi_manager.start_lay_low(1000.0)

        assert result is False

    def test_start_lay_low_without_investigation(self, fbi_manager):
        """Test that cannot lay low without active investigation."""
        fbi_manager.status = FBIStatus.NONE

        result = fbi_manager.start_lay_low(1000.0)

        assert result is False

    def test_lay_low_duration_accumulates(self, fbi_manager, mock_suspicion_manager):
        """Test that lay low duration accumulates."""
        mock_suspicion_manager.suspicion_level = 50.0
        fbi_manager.status = FBIStatus.TRIGGERED
        fbi_manager.laying_low = True
        fbi_manager.lay_low_duration = 0.0

        fbi_manager.update(10000.0, 5000.0)

        assert fbi_manager.lay_low_duration == 10000.0

    def test_lay_low_success_clears_investigation(self, fbi_manager, mock_suspicion_manager):
        """Test that successful lay low clears investigation."""
        mock_suspicion_manager.suspicion_level = 40.0  # Below success threshold (60)
        fbi_manager.status = FBIStatus.TRIGGERED
        fbi_manager.laying_low = True
        fbi_manager.lay_low_duration = FBI.LAY_LOW_DURATION - 100

        fbi_manager.update(200.0, 10000.0)

        assert fbi_manager.laying_low is False
        assert fbi_manager.status == FBIStatus.NONE
        assert fbi_manager.fbi_agents_active is False

    def test_lay_low_failure_suspicion_too_high(self, fbi_manager, mock_suspicion_manager):
        """Test that lay low fails if suspicion still too high."""
        mock_suspicion_manager.suspicion_level = 70.0  # Above success threshold
        fbi_manager.status = FBIStatus.TRIGGERED
        fbi_manager.laying_low = True
        fbi_manager.lay_low_duration = FBI.LAY_LOW_DURATION - 100
        # Set high countdown to prevent raid during update
        fbi_manager.investigation_countdown = 999999.0

        fbi_manager.update(200.0, 10000.0)

        assert fbi_manager.laying_low is False
        # Investigation should continue (not NONE, not RAIDED)
        assert fbi_manager.status in [FBIStatus.TRIGGERED, FBIStatus.INVESTIGATING]


class TestStatusHelpers:
    """Test status helper methods."""

    def test_is_investigation_active(self, fbi_manager):
        """Test is_investigation_active helper."""
        assert fbi_manager.is_investigation_active() is False

        fbi_manager.status = FBIStatus.TRIGGERED
        assert fbi_manager.is_investigation_active() is True

        fbi_manager.status = FBIStatus.INVESTIGATING
        assert fbi_manager.is_investigation_active() is True

        fbi_manager.status = FBIStatus.RAID_IMMINENT
        assert fbi_manager.is_investigation_active() is True

        fbi_manager.status = FBIStatus.RAIDED
        assert fbi_manager.is_investigation_active() is False

    def test_is_raided(self, fbi_manager):
        """Test is_raided helper."""
        assert fbi_manager.is_raided() is False

        fbi_manager.status = FBIStatus.RAIDED
        assert fbi_manager.is_raided() is True

    def test_get_countdown_days(self, fbi_manager):
        """Test get_countdown_days calculation."""
        fbi_manager.investigation_countdown = 172800.0  # 2 days in seconds

        days = fbi_manager.get_countdown_days()

        assert days == pytest.approx(2.0, rel=0.01)


class TestStatusText:
    """Test status text generation."""

    def test_get_status_text_none(self, fbi_manager):
        """Test status text when no investigation."""
        fbi_manager.status = FBIStatus.NONE

        text = fbi_manager.get_status_text()

        assert text == "No Investigation"

    def test_get_status_text_triggered(self, fbi_manager):
        """Test status text when triggered."""
        fbi_manager.status = FBIStatus.TRIGGERED
        fbi_manager.investigation_countdown = 86400.0  # 1 day

        text = fbi_manager.get_status_text()

        assert "FBI Investigating" in text
        assert "days" in text

    def test_get_status_text_raid_imminent(self, fbi_manager):
        """Test status text when raid imminent."""
        fbi_manager.status = FBIStatus.RAID_IMMINENT
        fbi_manager.investigation_countdown = 7200.0  # 2 hours

        text = fbi_manager.get_status_text()

        assert "RAID IMMINENT" in text
        assert "hours" in text

    def test_get_status_text_raided(self, fbi_manager):
        """Test status text when raided."""
        fbi_manager.status = FBIStatus.RAIDED

        text = fbi_manager.get_status_text()

        assert "RAIDED" in text
        assert "GAME OVER" in text


class TestEventLogging:
    """Test event logging."""

    def test_log_event_records_details(self, fbi_manager, mock_suspicion_manager):
        """Test that events are logged with details."""
        mock_suspicion_manager.suspicion_level = 75.0
        fbi_manager._log_event("test_event", "Test description", 5000.0)

        assert len(fbi_manager.events) == 1
        event = fbi_manager.events[0]
        assert event['type'] == "test_event"
        assert event['description'] == "Test description"
        assert event['game_time'] == 5000.0
        assert event['suspicion'] == 75.0


class TestGetStats:
    """Test statistics retrieval."""

    def test_get_stats_complete(self, fbi_manager):
        """Test that get_stats returns all fields."""
        fbi_manager.status = FBIStatus.TRIGGERED
        fbi_manager.trigger_reason = FBITrigger.HIGH_SUSPICION
        fbi_manager.investigation_countdown = 86400.0
        fbi_manager.high_suspicion_duration = 10000.0
        fbi_manager.failed_inspections = 2
        fbi_manager.fbi_agents_active = True
        fbi_manager.agent_count = 5
        fbi_manager.laying_low = True

        stats = fbi_manager.get_stats()

        assert stats['status'] == FBIStatus.TRIGGERED.value
        assert stats['trigger_reason'] == FBITrigger.HIGH_SUSPICION.value
        assert stats['countdown_days'] == pytest.approx(1.0, rel=0.01)
        assert stats['failed_inspections'] == 2
        assert stats['fbi_agents_active'] is True
        assert stats['agent_count'] == 5
        assert stats['laying_low'] is True
        assert stats['can_bribe'] is True

    def test_get_stats_no_trigger_reason(self, fbi_manager):
        """Test get_stats when no trigger reason."""
        stats = fbi_manager.get_stats()

        assert stats['trigger_reason'] is None


class TestReportInspectionFailure:
    """Test inspection failure reporting."""

    def test_report_critical_failure(self, fbi_manager):
        """Test reporting critical inspection failure."""
        fbi_manager.report_inspection_failure(is_critical=True)

        assert fbi_manager.critical_inspections == 1
        assert fbi_manager.failed_inspections == 0

    def test_report_non_critical_failure(self, fbi_manager):
        """Test reporting non-critical inspection failure."""
        fbi_manager.report_inspection_failure(is_critical=False)

        assert fbi_manager.critical_inspections == 0
        assert fbi_manager.failed_inspections == 1

    def test_multiple_failure_reports(self, fbi_manager):
        """Test accumulation of failure reports."""
        fbi_manager.report_inspection_failure(is_critical=False)
        fbi_manager.report_inspection_failure(is_critical=True)
        fbi_manager.report_inspection_failure(is_critical=False)

        assert fbi_manager.failed_inspections == 2
        assert fbi_manager.critical_inspections == 1


class TestTriggerDescription:
    """Test trigger description generation."""

    def test_get_trigger_description_high_suspicion(self, fbi_manager):
        """Test description for high suspicion trigger."""
        desc = fbi_manager._get_trigger_description(FBITrigger.HIGH_SUSPICION)

        assert "suspicion" in desc.lower()

    def test_get_trigger_description_critical_inspection(self, fbi_manager):
        """Test description for critical inspection trigger."""
        desc = fbi_manager._get_trigger_description(FBITrigger.CRITICAL_INSPECTION)

        assert "inspection" in desc.lower()

    def test_get_trigger_description_unknown(self, fbi_manager):
        """Test description for unknown trigger."""
        desc = fbi_manager._get_trigger_description(FBITrigger.ANONYMOUS_TIP)

        assert len(desc) > 0
