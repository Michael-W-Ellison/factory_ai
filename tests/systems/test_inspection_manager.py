"""
Unit tests for InspectionManager.

Tests inspection scheduling, countdown, pass/fail logic,
and consequences.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.systems.inspection_manager import (
    InspectionManager, InspectionStatus, InspectionResult
)


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
def mock_material_inventory():
    """Create a mock material inventory."""
    mock = MagicMock()
    mock.get_illegal_material_count = MagicMock(return_value=0)
    mock.get_illegal_material_value = MagicMock(return_value=0)
    mock.has_suspicious_amounts = MagicMock(return_value=[])
    return mock


@pytest.fixture
def inspection_manager(mock_resource_manager, mock_suspicion_manager):
    """Create an InspectionManager with mocked dependencies."""
    return InspectionManager(mock_resource_manager, mock_suspicion_manager)


class TestInspectionManagerInitialization:
    """Test InspectionManager initialization."""

    def test_initialization_defaults(self, mock_resource_manager, mock_suspicion_manager):
        """Test that InspectionManager initializes with correct defaults."""
        manager = InspectionManager(mock_resource_manager, mock_suspicion_manager)

        assert manager.status == InspectionStatus.NONE
        assert manager.inspection_scheduled is False
        assert manager.countdown == 0.0
        assert manager.inspection_progress == 0.0
        assert manager.last_result is None
        assert manager.game_over is False
        assert manager.has_restrictions is False

    def test_initialization_with_material_inventory(
            self, mock_resource_manager, mock_suspicion_manager, mock_material_inventory):
        """Test initialization with material inventory."""
        manager = InspectionManager(
            mock_resource_manager,
            mock_suspicion_manager,
            mock_material_inventory
        )

        assert manager.material_inventory is mock_material_inventory


class TestInspectionScheduling:
    """Test inspection scheduling logic."""

    def test_schedule_inspection_on_high_suspicion(self, inspection_manager, mock_suspicion_manager):
        """Test that inspection is scheduled when suspicion exceeds threshold."""
        mock_suspicion_manager.suspicion_level = 70.0  # Above threshold (60)

        inspection_manager.update(0.1, 10000.0)

        assert inspection_manager.status == InspectionStatus.SCHEDULED
        assert inspection_manager.inspection_scheduled is True
        assert inspection_manager.countdown > 0

    def test_no_schedule_below_threshold(self, inspection_manager, mock_suspicion_manager):
        """Test that no inspection is scheduled below threshold."""
        mock_suspicion_manager.suspicion_level = 40.0  # Below threshold

        inspection_manager.update(0.1, 10000.0)

        assert inspection_manager.status == InspectionStatus.NONE
        assert inspection_manager.inspection_scheduled is False

    def test_immunity_period_prevents_scheduling(self, inspection_manager, mock_suspicion_manager):
        """Test that immunity period prevents new inspection scheduling."""
        mock_suspicion_manager.suspicion_level = 70.0
        # Set last inspection time to be within immunity period
        inspection_manager.last_inspection_time = 5000.0

        # Try to update at time still within immunity
        inspection_manager.update(0.1, 5500.0)

        assert inspection_manager.status == InspectionStatus.NONE

    def test_force_schedule_inspection(self, inspection_manager):
        """Test force_schedule_inspection sets up inspection correctly."""
        inspection_manager.force_schedule_inspection(1000.0, warning_hours=12.0)

        assert inspection_manager.status == InspectionStatus.SCHEDULED
        assert inspection_manager.inspection_scheduled is True
        assert inspection_manager.countdown == pytest.approx(12.0 * 3600.0, rel=0.01)


class TestInspectionCountdown:
    """Test inspection countdown mechanics."""

    def test_countdown_decreases_over_time(self, inspection_manager):
        """Test that countdown decreases as time passes."""
        inspection_manager.force_schedule_inspection(0.0, warning_hours=24.0)
        initial_countdown = inspection_manager.countdown

        inspection_manager.update(1000.0, 1000.0)

        assert inspection_manager.countdown < initial_countdown
        assert inspection_manager.countdown == initial_countdown - 1000.0

    def test_countdown_triggers_inspection_start(self, inspection_manager):
        """Test that countdown reaching zero starts inspection."""
        inspection_manager.force_schedule_inspection(0.0, warning_hours=1.0)

        # Advance time past countdown
        inspection_manager.update(4000.0, 4000.0)

        assert inspection_manager.status == InspectionStatus.IN_PROGRESS

    def test_get_countdown_hours(self, inspection_manager):
        """Test get_countdown_hours returns correct value."""
        inspection_manager.countdown = 7200.0  # 2 hours in seconds

        hours = inspection_manager.get_countdown_hours()

        assert hours == pytest.approx(2.0, rel=0.01)


class TestInspectionProgress:
    """Test inspection progress mechanics."""

    def test_inspection_progress_increases(self, inspection_manager):
        """Test that inspection progress increases over time."""
        inspection_manager.status = InspectionStatus.IN_PROGRESS
        inspection_manager.inspection_progress = 0.0

        inspection_manager.update(1800.0, 1000.0)  # 30 minutes

        assert inspection_manager.inspection_progress > 0.0

    def test_inspection_completes_at_100_percent(
            self, inspection_manager, mock_suspicion_manager, mock_resource_manager):
        """Test that inspection completes when progress reaches 100%."""
        inspection_manager.status = InspectionStatus.IN_PROGRESS
        inspection_manager.inspection_progress = 0.9
        mock_suspicion_manager.suspicion_level = 50.0

        # Update with enough time to complete
        inspection_manager.update(3600.0, 5000.0)

        assert inspection_manager.status == InspectionStatus.NONE
        assert inspection_manager.last_result is not None

    def test_get_inspection_progress_percent(self, inspection_manager):
        """Test get_inspection_progress_percent returns percentage."""
        inspection_manager.inspection_progress = 0.75

        percent = inspection_manager.get_inspection_progress_percent()

        assert percent == pytest.approx(75.0, rel=0.01)


class TestInspectionResults:
    """Test inspection result calculation and consequences."""

    def test_pass_result_reduces_suspicion(
            self, mock_resource_manager, mock_suspicion_manager, mock_material_inventory):
        """Test that passing inspection reduces suspicion."""
        mock_material_inventory.get_illegal_material_count.return_value = 0
        mock_material_inventory.get_illegal_material_value.return_value = 0
        mock_material_inventory.has_suspicious_amounts.return_value = []

        manager = InspectionManager(
            mock_resource_manager, mock_suspicion_manager, mock_material_inventory
        )
        manager.status = InspectionStatus.IN_PROGRESS
        manager.inspection_progress = 0.99

        manager.update(3600.0, 5000.0)

        # Check suspicion was reduced
        mock_suspicion_manager.add_suspicion.assert_called()
        call_args = mock_suspicion_manager.add_suspicion.call_args[0]
        assert call_args[0] == -20  # Suspicion reduction

    def test_minor_fail_applies_fine(
            self, mock_resource_manager, mock_suspicion_manager):
        """Test that minor failure applies $5000 fine."""
        manager = InspectionManager(mock_resource_manager, mock_suspicion_manager)

        # Force minor fail result
        with patch.object(manager, '_calculate_inspection_result',
                          return_value=InspectionResult.FAIL_MINOR):
            manager._complete_inspection(5000.0)

        assert manager.last_result == InspectionResult.FAIL_MINOR
        mock_resource_manager.modify_money.assert_called_with(-5000)

    def test_major_fail_applies_restrictions(
            self, mock_resource_manager, mock_suspicion_manager):
        """Test that major failure applies restrictions."""
        manager = InspectionManager(mock_resource_manager, mock_suspicion_manager)

        with patch.object(manager, '_calculate_inspection_result',
                          return_value=InspectionResult.FAIL_MAJOR):
            manager._complete_inspection(5000.0)

        assert manager.last_result == InspectionResult.FAIL_MAJOR
        assert manager.has_restrictions is True
        assert manager.production_penalty > 0

    def test_critical_fail_triggers_game_over(
            self, mock_resource_manager, mock_suspicion_manager):
        """Test that critical failure triggers game over."""
        manager = InspectionManager(mock_resource_manager, mock_suspicion_manager)

        with patch.object(manager, '_calculate_inspection_result',
                          return_value=InspectionResult.FAIL_CRITICAL):
            manager._complete_inspection(5000.0)

        assert manager.last_result == InspectionResult.FAIL_CRITICAL
        assert manager.game_over is True
        assert manager.game_over_reason != ""


class TestRestrictions:
    """Test operating restrictions mechanics."""

    def test_restrictions_apply_production_penalty(
            self, mock_resource_manager, mock_suspicion_manager):
        """Test that restrictions apply production penalty."""
        manager = InspectionManager(mock_resource_manager, mock_suspicion_manager)
        manager._apply_restrictions(1000.0, duration=86400.0, penalty=0.5)

        assert manager.has_restrictions is True
        assert manager.production_penalty == 0.5
        assert manager.restrictions_end_time == 87400.0

    def test_restrictions_expire_after_duration(
            self, mock_resource_manager, mock_suspicion_manager):
        """Test that restrictions expire after set duration."""
        manager = InspectionManager(mock_resource_manager, mock_suspicion_manager)
        manager.has_restrictions = True
        manager.production_penalty = 0.5
        manager.restrictions_end_time = 5000.0

        # Update past expiration time
        manager.update(0.1, 6000.0)

        assert manager.has_restrictions is False
        assert manager.production_penalty == 0.0

    def test_get_production_penalty(
            self, mock_resource_manager, mock_suspicion_manager):
        """Test get_production_penalty returns correct value."""
        manager = InspectionManager(mock_resource_manager, mock_suspicion_manager)

        # No restrictions
        assert manager.get_production_penalty() == 0.0

        # With restrictions
        manager.has_restrictions = True
        manager.production_penalty = 0.5
        assert manager.get_production_penalty() == 0.5


class TestReinspection:
    """Test reinspection scheduling."""

    def test_minor_fail_schedules_reinspection(
            self, mock_resource_manager, mock_suspicion_manager):
        """Test that minor failure schedules reinspection."""
        manager = InspectionManager(mock_resource_manager, mock_suspicion_manager)

        with patch.object(manager, '_calculate_inspection_result',
                          return_value=InspectionResult.FAIL_MINOR):
            manager._complete_inspection(5000.0)

        # After completion, reinspection should be scheduled
        assert manager.status == InspectionStatus.SCHEDULED
        assert manager.countdown > 0


class TestProbabilisticResults:
    """Test probability-based inspection results (fallback mode)."""

    def test_low_suspicion_likely_passes(
            self, mock_resource_manager, mock_suspicion_manager):
        """Test that low suspicion (< 60) likely passes."""
        mock_suspicion_manager.suspicion_level = 50.0
        manager = InspectionManager(mock_resource_manager, mock_suspicion_manager)

        result = manager._calculate_result_probabilistic()

        assert result == InspectionResult.PASS

    def test_high_suspicion_increases_fail_chance(
            self, mock_resource_manager, mock_suspicion_manager):
        """Test that high suspicion affects probabilities."""
        mock_suspicion_manager.suspicion_level = 100.0
        manager = InspectionManager(mock_resource_manager, mock_suspicion_manager)

        # Run multiple times to check distribution
        results = [manager._calculate_result_probabilistic() for _ in range(100)]

        # Should have some failures at this high suspicion
        fail_count = sum(1 for r in results if r != InspectionResult.PASS)
        assert fail_count > 0


class TestMaterialBasedResults:
    """Test material-based inspection results."""

    def test_no_illegal_materials_passes(
            self, mock_resource_manager, mock_suspicion_manager, mock_material_inventory):
        """Test that no illegal materials results in pass."""
        mock_material_inventory.get_illegal_material_count.return_value = 0
        mock_material_inventory.get_illegal_material_value.return_value = 0
        mock_material_inventory.has_suspicious_amounts.return_value = []

        manager = InspectionManager(
            mock_resource_manager, mock_suspicion_manager, mock_material_inventory
        )

        result = manager._calculate_result_from_materials()

        assert result == InspectionResult.PASS

    def test_massive_illegal_materials_critical_fail(
            self, mock_resource_manager, mock_suspicion_manager, mock_material_inventory):
        """Test that massive illegal materials result in critical failure."""
        mock_material_inventory.get_illegal_material_count.return_value = 500
        mock_material_inventory.get_illegal_material_value.return_value = 10000
        mock_material_inventory.has_suspicious_amounts.return_value = ['material_x']

        manager = InspectionManager(
            mock_resource_manager, mock_suspicion_manager, mock_material_inventory
        )

        result = manager._calculate_result_from_materials()

        assert result == InspectionResult.FAIL_CRITICAL


class TestStatusSummary:
    """Test status summary methods."""

    def test_get_status_summary_complete(
            self, mock_resource_manager, mock_suspicion_manager):
        """Test that get_status_summary returns all fields."""
        mock_suspicion_manager.suspicion_level = 50.0
        manager = InspectionManager(mock_resource_manager, mock_suspicion_manager)
        manager.force_schedule_inspection(1000.0, warning_hours=24.0)

        summary = manager.get_status_summary()

        assert 'status' in summary
        assert 'scheduled' in summary
        assert 'countdown_hours' in summary
        assert 'in_progress' in summary
        assert 'progress_percent' in summary
        assert 'last_result' in summary
        assert 'suspicion' in summary
        assert 'trigger_threshold' in summary
        assert 'has_restrictions' in summary
        assert 'game_over' in summary

    def test_is_inspection_scheduled(self, inspection_manager):
        """Test is_inspection_scheduled helper method."""
        assert inspection_manager.is_inspection_scheduled() is False

        inspection_manager.force_schedule_inspection(0.0, warning_hours=1.0)

        assert inspection_manager.is_inspection_scheduled() is True

    def test_is_inspection_in_progress(self, inspection_manager):
        """Test is_inspection_in_progress helper method."""
        assert inspection_manager.is_inspection_in_progress() is False

        inspection_manager.status = InspectionStatus.IN_PROGRESS

        assert inspection_manager.is_inspection_in_progress() is True

    def test_is_game_over(self, inspection_manager):
        """Test is_game_over helper method."""
        assert inspection_manager.is_game_over() is False

        inspection_manager.game_over = True

        assert inspection_manager.is_game_over() is True


class TestSetIllegalMaterialCount:
    """Test illegal material count setter."""

    def test_set_illegal_material_count(self, inspection_manager):
        """Test setting illegal material count for Phase 8.4 integration."""
        inspection_manager.set_illegal_material_count(100, 5000)

        assert inspection_manager.illegal_material_count == 100
        assert inspection_manager.illegal_material_value == 5000


class TestRepr:
    """Test string representation."""

    def test_repr_normal_state(self, inspection_manager):
        """Test __repr__ in normal state."""
        repr_str = repr(inspection_manager)

        assert "InspectionManager" in repr_str
        assert "NONE" in repr_str

    def test_repr_with_restrictions(self, inspection_manager):
        """Test __repr__ with active restrictions."""
        inspection_manager.has_restrictions = True

        repr_str = repr(inspection_manager)

        assert "restrictions=True" in repr_str

    def test_repr_game_over(self, inspection_manager):
        """Test __repr__ in game over state."""
        inspection_manager.game_over = True

        repr_str = repr(inspection_manager)

        assert "GAME_OVER" in repr_str
