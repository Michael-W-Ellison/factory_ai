"""
Unit tests for SuspicionManager.

Tests suspicion level tracking, tier transitions, decay mechanics,
and tier-based effects.
"""

import pytest
import time as real_time

from src.systems.suspicion_manager import SuspicionManager, SuspicionTier


class TestSuspicionManagerInitialization:
    """Test SuspicionManager initialization."""

    def test_initialization_defaults(self):
        """Test that SuspicionManager initializes with correct defaults."""
        manager = SuspicionManager()

        assert manager.suspicion_level == 0.0
        assert manager.current_tier == SuspicionTier.NORMAL
        assert manager.suspicion_events == []
        assert manager.tier_changes == []

    def test_tier_thresholds_from_config(self):
        """Test that tier thresholds are loaded from config."""
        manager = SuspicionManager()

        assert SuspicionTier.NORMAL in manager.tier_thresholds
        assert SuspicionTier.RUMORS in manager.tier_thresholds
        assert SuspicionTier.INVESTIGATION in manager.tier_thresholds
        assert SuspicionTier.INSPECTION in manager.tier_thresholds
        assert SuspicionTier.RESTRICTIONS in manager.tier_thresholds

    def test_tier_effects_defined(self):
        """Test that all tiers have effects defined."""
        manager = SuspicionManager()

        for tier in [SuspicionTier.NORMAL, SuspicionTier.RUMORS,
                     SuspicionTier.INVESTIGATION, SuspicionTier.INSPECTION,
                     SuspicionTier.RESTRICTIONS]:
            assert tier in manager.tier_effects
            assert 'police_patrol_multiplier' in manager.tier_effects[tier]
            assert 'npc_alertness_multiplier' in manager.tier_effects[tier]


class TestSuspicionLevelManagement:
    """Test suspicion level modifications."""

    def test_suspicion_increases_on_detection(self):
        """Test that add_suspicion increases suspicion level."""
        manager = SuspicionManager()

        manager.add_suspicion(10, "npc_detection", "NPC saw robot")

        assert manager.suspicion_level == 10.0
        assert len(manager.suspicion_events) == 1
        assert manager.suspicion_events[0]['amount'] == 10

    def test_suspicion_decreases_on_negative_amount(self):
        """Test that negative amounts decrease suspicion."""
        manager = SuspicionManager()
        manager.suspicion_level = 50.0

        manager.add_suspicion(-20, "passed_inspection", "Clean inspection")

        assert manager.suspicion_level == 30.0

    def test_suspicion_capped_at_100(self):
        """Test that suspicion cannot exceed 100."""
        manager = SuspicionManager()

        manager.add_suspicion(150, "massive_exposure", "")

        assert manager.suspicion_level == 100.0

    def test_suspicion_minimum_at_0(self):
        """Test that suspicion cannot go below 0."""
        manager = SuspicionManager()
        manager.suspicion_level = 10.0

        manager.add_suspicion(-50, "large_reduction", "")

        assert manager.suspicion_level == 0.0

    def test_zero_amount_returns_false(self):
        """Test that adding 0 suspicion returns False and does nothing."""
        manager = SuspicionManager()

        result = manager.add_suspicion(0, "no_change", "")

        assert result is False
        assert len(manager.suspicion_events) == 0


class TestTierTransitions:
    """Test tier transition logic."""

    def test_tier_transitions_to_rumors(self):
        """Test transition from Normal to Rumors tier."""
        manager = SuspicionManager()

        tier_changed = manager.add_suspicion(25, "test", "")

        assert tier_changed is True
        assert manager.current_tier == SuspicionTier.RUMORS
        assert len(manager.tier_changes) == 1

    def test_tier_transitions_to_investigation(self):
        """Test transition to Investigation tier."""
        manager = SuspicionManager()

        manager.add_suspicion(45, "test", "")

        assert manager.current_tier == SuspicionTier.INVESTIGATION

    def test_tier_transitions_to_inspection(self):
        """Test transition to Inspection tier."""
        manager = SuspicionManager()

        manager.add_suspicion(65, "test", "")

        assert manager.current_tier == SuspicionTier.INSPECTION

    def test_tier_transitions_to_restrictions(self):
        """Test transition to Restrictions tier."""
        manager = SuspicionManager()

        manager.add_suspicion(85, "test", "")

        assert manager.current_tier == SuspicionTier.RESTRICTIONS

    def test_tier_transitions_records_history(self):
        """Test that tier changes are recorded in history."""
        manager = SuspicionManager()

        manager.add_suspicion(25, "test", "")  # To Rumors
        manager.add_suspicion(25, "test", "")  # To Investigation

        assert len(manager.tier_changes) == 2
        assert manager.tier_changes[0]['old_tier'] == SuspicionTier.NORMAL
        assert manager.tier_changes[0]['new_tier'] == SuspicionTier.RUMORS
        assert manager.tier_changes[1]['old_tier'] == SuspicionTier.RUMORS
        assert manager.tier_changes[1]['new_tier'] == SuspicionTier.INVESTIGATION

    def test_get_current_tier_returns_correct_tier(self):
        """Test get_current_tier method accuracy."""
        manager = SuspicionManager()

        manager.suspicion_level = 0
        assert manager.get_current_tier() == SuspicionTier.NORMAL

        manager.suspicion_level = 25
        assert manager.get_current_tier() == SuspicionTier.RUMORS

        manager.suspicion_level = 50
        assert manager.get_current_tier() == SuspicionTier.INVESTIGATION

        manager.suspicion_level = 70
        assert manager.get_current_tier() == SuspicionTier.INSPECTION

        manager.suspicion_level = 90
        assert manager.get_current_tier() == SuspicionTier.RESTRICTIONS


class TestSuspicionDecay:
    """Test suspicion decay mechanics."""

    def test_suspicion_decay_over_time(self):
        """Test that suspicion decays over time when below threshold."""
        manager = SuspicionManager()
        manager.suspicion_level = 30.0

        # Simulate 1 second of game time
        manager.update(1.0, 0.0)

        assert manager.suspicion_level < 30.0

    def test_decay_stops_at_threshold(self):
        """Test that decay stops when suspicion is at or above decay threshold."""
        manager = SuspicionManager()
        manager.suspicion_level = 70.0  # Above decay_stops_at (60)
        initial_level = manager.suspicion_level

        manager.update(1.0, 0.0)

        assert manager.suspicion_level == initial_level

    def test_decay_triggers_tier_downgrade(self):
        """Test that decay can trigger tier downgrade."""
        manager = SuspicionManager()
        # Set to just above RUMORS threshold
        manager.suspicion_level = 22.0
        manager.current_tier = SuspicionTier.RUMORS

        # Large time step to ensure decay happens
        manager.update(100.0, 0.0)

        # Should have decayed and potentially downgraded
        assert manager.suspicion_level < 22.0


class TestDetectionReports:
    """Test detection report processing."""

    def test_process_detection_report_adds_suspicion(self):
        """Test that detection reports add appropriate suspicion."""
        manager = SuspicionManager()

        report = {
            'suspicion_increase': 15.0,
            'detection_level': 'confirmed'
        }

        tier_changed = manager.process_detection_report(report)

        assert manager.suspicion_level == 15.0
        assert len(manager.suspicion_events) == 1
        assert "NPC detected robot" in manager.suspicion_events[0]['description']

    def test_process_detection_report_handles_missing_fields(self):
        """Test that reports with missing fields are handled gracefully."""
        manager = SuspicionManager()

        report = {}

        tier_changed = manager.process_detection_report(report)

        assert manager.suspicion_level == 0.0
        assert tier_changed is False


class TestTierEffects:
    """Test tier effect methods."""

    def test_get_tier_effects_returns_current_tier(self):
        """Test that get_tier_effects returns effects for current tier."""
        manager = SuspicionManager()
        manager.current_tier = SuspicionTier.RUMORS

        effects = manager.get_tier_effects()

        assert effects['police_patrol_multiplier'] == 1.25
        assert effects['npc_alertness_multiplier'] == 1.1

    def test_police_patrol_multiplier_by_tier(self):
        """Test police patrol multiplier varies by tier."""
        manager = SuspicionManager()

        manager.current_tier = SuspicionTier.NORMAL
        assert manager.get_police_patrol_multiplier() == 1.0

        manager.current_tier = SuspicionTier.RUMORS
        assert manager.get_police_patrol_multiplier() == 1.25

        manager.current_tier = SuspicionTier.RESTRICTIONS
        assert manager.get_police_patrol_multiplier() == 2.5

    def test_npc_alertness_multiplier_by_tier(self):
        """Test NPC alertness multiplier varies by tier."""
        manager = SuspicionManager()

        manager.current_tier = SuspicionTier.NORMAL
        assert manager.get_npc_alertness_multiplier() == 1.0

        manager.current_tier = SuspicionTier.RESTRICTIONS
        assert manager.get_npc_alertness_multiplier() == 2.0

    def test_camera_detection_bonus_by_tier(self):
        """Test camera detection bonus varies by tier."""
        manager = SuspicionManager()

        manager.current_tier = SuspicionTier.NORMAL
        assert manager.get_camera_detection_bonus() == 0.0

        manager.current_tier = SuspicionTier.INVESTIGATION
        assert manager.get_camera_detection_bonus() == 0.1

    def test_has_undercover_agents(self):
        """Test undercover agents flag at Investigation tier."""
        manager = SuspicionManager()

        manager.current_tier = SuspicionTier.NORMAL
        assert manager.has_undercover_agents() is False

        manager.current_tier = SuspicionTier.INVESTIGATION
        assert manager.has_undercover_agents() is True

    def test_has_checkpoints(self):
        """Test checkpoints flag at Inspection tier."""
        manager = SuspicionManager()

        manager.current_tier = SuspicionTier.NORMAL
        assert manager.has_checkpoints() is False

        manager.current_tier = SuspicionTier.INSPECTION
        assert manager.has_checkpoints() is True

    def test_has_operation_hours_limited(self):
        """Test operation hours limitation at Restrictions tier."""
        manager = SuspicionManager()

        manager.current_tier = SuspicionTier.INSPECTION
        assert manager.has_operation_hours_limited() is False

        manager.current_tier = SuspicionTier.RESTRICTIONS
        assert manager.has_operation_hours_limited() is True


class TestEventHistory:
    """Test event history and statistics."""

    def test_get_recent_events_returns_latest(self):
        """Test that get_recent_events returns most recent events."""
        manager = SuspicionManager()

        for i in range(15):
            manager.add_suspicion(1, f"event_{i}", "")

        recent = manager.get_recent_events(5)

        assert len(recent) == 5
        assert recent[-1]['source'] == "event_14"

    def test_get_recent_events_empty_history(self):
        """Test get_recent_events with no events."""
        manager = SuspicionManager()

        recent = manager.get_recent_events()

        assert recent == []

    def test_get_stats_returns_complete_info(self):
        """Test that get_stats returns complete statistics."""
        manager = SuspicionManager()
        manager.add_suspicion(30, "test", "")

        stats = manager.get_stats()

        assert 'level' in stats
        assert 'tier' in stats
        assert 'tier_name' in stats
        assert 'total_events' in stats
        assert 'tier_changes' in stats
        assert 'decaying' in stats
        assert stats['level'] == 30.0
        assert stats['total_events'] == 1


class TestTierProgress:
    """Test tier progress calculation."""

    def test_tier_progress_at_tier_start(self):
        """Test tier progress at the start of a tier."""
        manager = SuspicionManager()
        # Set to exactly at RUMORS threshold (21)
        manager.suspicion_level = manager.tier_thresholds[SuspicionTier.RUMORS]
        manager.current_tier = SuspicionTier.RUMORS

        progress = manager.get_tier_progress()

        # At exactly the tier start, progress should be 0
        assert 0.0 <= progress <= 0.1  # Allow small tolerance

    def test_tier_progress_mid_tier(self):
        """Test tier progress in the middle of a tier."""
        manager = SuspicionManager()
        # Set to middle of RUMORS tier (21-41)
        manager.suspicion_level = 31
        manager.current_tier = SuspicionTier.RUMORS

        progress = manager.get_tier_progress()

        # Should be about 50% (10 out of 20)
        assert progress == pytest.approx(0.5, abs=0.1)

    def test_tier_progress_at_max_tier(self):
        """Test tier progress at max tier."""
        manager = SuspicionManager()
        manager.suspicion_level = 90
        manager.current_tier = SuspicionTier.RESTRICTIONS

        progress = manager.get_tier_progress()

        # Should be between 0 and 1
        assert 0.0 <= progress <= 1.0


class TestTierConsequences:
    """Test tier consequence descriptions."""

    def test_normal_tier_consequences(self):
        """Test consequences for Normal tier."""
        manager = SuspicionManager()
        manager.current_tier = SuspicionTier.NORMAL

        consequences = manager.get_tier_consequences()

        assert "No special attention" in consequences

    def test_restrictions_tier_consequences(self):
        """Test consequences for Restrictions tier."""
        manager = SuspicionManager()
        manager.current_tier = SuspicionTier.RESTRICTIONS

        consequences = manager.get_tier_consequences()

        assert len(consequences) > 0
        assert any("FBI" in c for c in consequences)


class TestRepr:
    """Test string representation."""

    def test_repr_format(self):
        """Test __repr__ returns expected format."""
        manager = SuspicionManager()
        # Use add_suspicion to properly trigger tier update
        manager.add_suspicion(25.5, "test", "")

        repr_str = repr(manager)

        assert "SuspicionManager" in repr_str
        assert "25.5" in repr_str
        assert "Rumors" in repr_str
