"""
Unit tests for ControlRangeManager.

Tests control range calculation, transmitters, and coverage.
"""

import pytest
import math
from unittest.mock import Mock, patch


@pytest.fixture
def control_range_manager():
    """Create ControlRangeManager instance."""
    from src.systems.control_range_manager import ControlRangeManager
    return ControlRangeManager(factory_x=100.0, factory_y=100.0)


class TestControlRangeManagerInit:
    """Tests for ControlRangeManager initialization."""

    def test_init_factory_position(self):
        """Test initialization with factory position."""
        from src.systems.control_range_manager import ControlRangeManager
        crm = ControlRangeManager(factory_x=200.0, factory_y=300.0)

        assert crm.factory_x == 200.0
        assert crm.factory_y == 300.0

    def test_init_base_range(self, control_range_manager):
        """Test base range default value."""
        assert control_range_manager.factory_base_range == 200

    def test_init_empty_transmitters(self, control_range_manager):
        """Test transmitters start empty."""
        assert control_range_manager.transmitters == []

    def test_init_transmitter_ranges(self, control_range_manager):
        """Test transmitter range configurations."""
        assert 1 in control_range_manager.transmitter_ranges
        assert 2 in control_range_manager.transmitter_ranges
        assert 3 in control_range_manager.transmitter_ranges
        assert control_range_manager.transmitter_ranges[1] == 300


class TestTransmitterManagement:
    """Tests for transmitter add/remove operations."""

    def test_add_transmitter(self, control_range_manager):
        """Test adding a transmitter."""
        control_range_manager.add_transmitter(500.0, 500.0, level=1)

        assert len(control_range_manager.transmitters) == 1
        tx, ty, trans_range, level = control_range_manager.transmitters[0]
        assert tx == 500.0
        assert ty == 500.0
        assert level == 1

    def test_add_transmitter_level2(self, control_range_manager):
        """Test adding level 2 transmitter with extended range."""
        control_range_manager.add_transmitter(500.0, 500.0, level=2)

        _, _, trans_range, _ = control_range_manager.transmitters[0]
        assert trans_range == 450  # Level 2 range

    def test_add_multiple_transmitters(self, control_range_manager):
        """Test adding multiple transmitters."""
        control_range_manager.add_transmitter(200.0, 200.0, level=1)
        control_range_manager.add_transmitter(400.0, 400.0, level=2)
        control_range_manager.add_transmitter(600.0, 600.0, level=3)

        assert len(control_range_manager.transmitters) == 3

    def test_remove_transmitter(self, control_range_manager):
        """Test removing a transmitter."""
        control_range_manager.add_transmitter(500.0, 500.0, level=1)

        result = control_range_manager.remove_transmitter(500.0, 500.0)

        assert result is True
        assert len(control_range_manager.transmitters) == 0

    def test_remove_transmitter_nearby(self, control_range_manager):
        """Test removing transmitter with nearby position."""
        control_range_manager.add_transmitter(500.0, 500.0, level=1)

        # Remove with position slightly off (within tolerance)
        result = control_range_manager.remove_transmitter(505.0, 505.0)

        assert result is True
        assert len(control_range_manager.transmitters) == 0

    def test_remove_nonexistent_transmitter(self, control_range_manager):
        """Test removing non-existent transmitter."""
        result = control_range_manager.remove_transmitter(999.0, 999.0)
        assert result is False


class TestControlRangeChecks:
    """Tests for control range checking."""

    def test_is_in_control_range_at_factory(self, control_range_manager):
        """Test position at factory is in range."""
        result = control_range_manager.is_in_control_range(100.0, 100.0)
        assert result is True

    def test_is_in_control_range_within_factory_range(self, control_range_manager):
        """Test position within factory range."""
        # Factory at (100, 100) with range 200
        result = control_range_manager.is_in_control_range(200.0, 100.0)
        assert result is True

    def test_is_not_in_control_range_outside_factory(self, control_range_manager):
        """Test position outside factory range."""
        # Factory at (100, 100) with range 200
        result = control_range_manager.is_in_control_range(1000.0, 1000.0)
        assert result is False

    def test_is_in_control_range_via_transmitter(self, control_range_manager):
        """Test position within transmitter range."""
        control_range_manager.add_transmitter(500.0, 500.0, level=1)

        # Within transmitter range (level 1 = 300 range)
        result = control_range_manager.is_in_control_range(500.0, 600.0)
        assert result is True


class TestNearestControlPoint:
    """Tests for finding nearest control point."""

    def test_get_nearest_control_point_factory_only(self, control_range_manager):
        """Test nearest point with only factory."""
        point = control_range_manager.get_nearest_control_point(150.0, 150.0)

        assert point == (100.0, 100.0)

    def test_get_nearest_control_point_with_transmitter(self, control_range_manager):
        """Test nearest point when transmitter is closer."""
        control_range_manager.add_transmitter(300.0, 300.0, level=1)

        # Position closer to transmitter
        point = control_range_manager.get_nearest_control_point(350.0, 350.0)

        assert point == (300.0, 300.0)

    def test_get_nearest_control_point_factory_closer(self, control_range_manager):
        """Test nearest point when factory is closer."""
        control_range_manager.add_transmitter(500.0, 500.0, level=1)

        # Position closer to factory
        point = control_range_manager.get_nearest_control_point(110.0, 110.0)

        assert point == (100.0, 100.0)


class TestDistanceToControlRange:
    """Tests for distance to control range calculations."""

    def test_get_distance_inside_range(self, control_range_manager):
        """Test distance when inside control range."""
        distance = control_range_manager.get_distance_to_control_range(100.0, 100.0)
        assert distance == 0

    def test_get_distance_outside_range(self, control_range_manager):
        """Test distance when outside control range."""
        # Very far from factory
        distance = control_range_manager.get_distance_to_control_range(1000.0, 100.0)

        # Should be positive (outside range)
        assert distance > 0


class TestCoveragePercentage:
    """Tests for coverage percentage calculations."""

    def test_get_control_coverage_percent_full(self, control_range_manager):
        """Test coverage when area is fully within range."""
        # Small area fully within factory range
        percent = control_range_manager.get_control_coverage_percent(
            100.0, 100.0, 150.0, 150.0, sample_points=100
        )

        assert percent == 100.0

    def test_get_control_coverage_percent_none(self, control_range_manager):
        """Test coverage when area is fully outside range."""
        # Area far outside all control ranges
        percent = control_range_manager.get_control_coverage_percent(
            5000.0, 5000.0, 5100.0, 5100.0, sample_points=100
        )

        assert percent == 0.0


class TestAllControlPoints:
    """Tests for getting all control points."""

    def test_get_all_control_points_factory_only(self, control_range_manager):
        """Test getting control points with factory only."""
        points = control_range_manager.get_all_control_points()

        assert len(points) == 1
        x, y, range_val = points[0]
        assert x == 100.0
        assert y == 100.0
        assert range_val == 200

    def test_get_all_control_points_with_transmitters(self, control_range_manager):
        """Test getting control points with transmitters."""
        control_range_manager.add_transmitter(300.0, 300.0, level=1)
        control_range_manager.add_transmitter(500.0, 500.0, level=2)

        points = control_range_manager.get_all_control_points()

        assert len(points) == 3


class TestVisualization:
    """Tests for range visualization toggle."""

    def test_toggle_range_visualization_on(self, control_range_manager):
        """Test toggling visualization on."""
        assert control_range_manager.show_range is False

        result = control_range_manager.toggle_range_visualization()

        assert result is True
        assert control_range_manager.show_range is True

    def test_toggle_range_visualization_off(self, control_range_manager):
        """Test toggling visualization off."""
        control_range_manager.show_range = True

        result = control_range_manager.toggle_range_visualization()

        assert result is False
        assert control_range_manager.show_range is False


class TestStats:
    """Tests for control range statistics."""

    def test_get_stats(self, control_range_manager):
        """Test getting statistics."""
        control_range_manager.add_transmitter(300.0, 300.0, level=1)

        stats = control_range_manager.get_stats()

        assert stats['factory_position'] == (100.0, 100.0)
        assert stats['factory_range'] == 200
        assert stats['transmitter_count'] == 1
        assert stats['total_control_points'] == 2

    def test_get_stats_empty_transmitters(self, control_range_manager):
        """Test stats with no transmitters."""
        stats = control_range_manager.get_stats()

        assert stats['transmitter_count'] == 0
        assert stats['total_control_points'] == 1


class TestDistanceCalculation:
    """Tests for internal distance calculation."""

    def test_distance_calculation(self, control_range_manager):
        """Test the internal distance calculation."""
        # 3-4-5 triangle
        distance = control_range_manager._distance(0, 0, 3, 4)
        assert distance == 5.0

    def test_distance_zero(self, control_range_manager):
        """Test distance when points are same."""
        distance = control_range_manager._distance(100, 100, 100, 100)
        assert distance == 0.0
