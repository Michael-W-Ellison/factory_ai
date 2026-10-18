"""
Unit tests for TransmitterManager.

Tests transmitter placement, signal coverage, and management.
"""

import pytest
import math
from unittest.mock import Mock, MagicMock


class MockResourceManager:
    """Mock resource manager for testing."""
    def __init__(self, initial_money=100000):
        self.money = initial_money

    def modify_money(self, amount):
        self.money += amount


@pytest.fixture
def mock_resource_manager():
    """Create mock resource manager."""
    return MockResourceManager()


@pytest.fixture
def transmitter_manager(mock_resource_manager):
    """Create TransmitterManager instance."""
    from src.systems.transmitter_manager import TransmitterManager
    return TransmitterManager(mock_resource_manager)


class TestTransmitterManagerInit:
    """Tests for TransmitterManager initialization."""

    def test_init_with_resource_manager(self, mock_resource_manager):
        """Test initialization with resource manager."""
        from src.systems.transmitter_manager import TransmitterManager
        tm = TransmitterManager(mock_resource_manager)

        assert tm.resources == mock_resource_manager
        assert tm.transmitters == {}
        assert tm.next_transmitter_id == 1

    def test_init_base_position(self, transmitter_manager):
        """Test base position defaults."""
        assert transmitter_manager.base_position == (0.0, 0.0)
        assert transmitter_manager.base_range == 20.0

    def test_init_transmitter_specs(self, transmitter_manager):
        """Test transmitter specifications are defined."""
        from src.systems.transmitter_manager import TransmitterType

        assert TransmitterType.BASIC in transmitter_manager.transmitter_specs
        assert TransmitterType.ADVANCED in transmitter_manager.transmitter_specs
        assert TransmitterType.LONG_RANGE in transmitter_manager.transmitter_specs
        assert TransmitterType.REPEATER in transmitter_manager.transmitter_specs


class TestTransmitterPlacement:
    """Tests for transmitter placement."""

    def test_place_transmitter_success(self, transmitter_manager, mock_resource_manager):
        """Test successful transmitter placement."""
        from src.systems.transmitter_manager import TransmitterType

        # Place within base range
        transmitter_id = transmitter_manager.place_transmitter(
            TransmitterType.BASIC,
            (10.0, 10.0)
        )

        assert transmitter_id is not None
        assert transmitter_id == 1
        assert 1 in transmitter_manager.transmitters

    def test_place_transmitter_insufficient_funds(self, transmitter_manager, mock_resource_manager):
        """Test placement fails with insufficient funds."""
        from src.systems.transmitter_manager import TransmitterType

        mock_resource_manager.money = 100  # Very low

        transmitter_id = transmitter_manager.place_transmitter(
            TransmitterType.BASIC,
            (10.0, 10.0)
        )

        assert transmitter_id is None
        assert len(transmitter_manager.transmitters) == 0

    def test_place_transmitter_out_of_range(self, transmitter_manager, mock_resource_manager):
        """Test placement fails outside signal coverage."""
        from src.systems.transmitter_manager import TransmitterType

        # Try to place far outside base range
        transmitter_id = transmitter_manager.place_transmitter(
            TransmitterType.BASIC,
            (1000.0, 1000.0)
        )

        assert transmitter_id is None

    def test_place_transmitter_increments_id(self, transmitter_manager):
        """Test that transmitter IDs increment."""
        from src.systems.transmitter_manager import TransmitterType

        id1 = transmitter_manager.place_transmitter(TransmitterType.BASIC, (5.0, 5.0))
        id2 = transmitter_manager.place_transmitter(TransmitterType.BASIC, (8.0, 8.0))

        assert id1 == 1
        assert id2 == 2

    def test_place_transmitter_deducts_cost(self, transmitter_manager, mock_resource_manager):
        """Test that placement deducts the correct cost."""
        from src.systems.transmitter_manager import TransmitterType

        initial_money = mock_resource_manager.money
        cost = transmitter_manager.transmitter_specs[TransmitterType.BASIC]['cost']

        transmitter_manager.place_transmitter(TransmitterType.BASIC, (5.0, 5.0))

        assert mock_resource_manager.money == initial_money - cost


class TestTransmitterRemoval:
    """Tests for transmitter removal."""

    def test_remove_transmitter_success(self, transmitter_manager):
        """Test successful transmitter removal."""
        from src.systems.transmitter_manager import TransmitterType

        trans_id = transmitter_manager.place_transmitter(
            TransmitterType.BASIC,
            (5.0, 5.0)
        )

        result = transmitter_manager.remove_transmitter(trans_id)

        assert result is True
        assert trans_id not in transmitter_manager.transmitters

    def test_remove_nonexistent_transmitter(self, transmitter_manager):
        """Test removing a transmitter that doesn't exist."""
        result = transmitter_manager.remove_transmitter(999)
        assert result is False


class TestSignalCoverage:
    """Tests for signal coverage calculations."""

    def test_has_signal_coverage_at_base(self, transmitter_manager):
        """Test signal coverage at base position."""
        assert transmitter_manager.has_signal_coverage((0.0, 0.0)) is True

    def test_has_signal_coverage_within_base_range(self, transmitter_manager):
        """Test signal coverage within base range."""
        # Within 20 tiles of base
        assert transmitter_manager.has_signal_coverage((10.0, 10.0)) is True

    def test_no_signal_coverage_outside_range(self, transmitter_manager):
        """Test no signal coverage far from base."""
        # Far outside base range
        assert transmitter_manager.has_signal_coverage((500.0, 500.0)) is False

    def test_get_signal_strength_at_base(self, transmitter_manager):
        """Test maximum signal strength at base."""
        strength = transmitter_manager.get_signal_strength_at((0.0, 0.0))
        assert strength == 100.0

    def test_get_signal_strength_decreases_with_distance(self, transmitter_manager):
        """Test signal strength decreases with distance."""
        strength_close = transmitter_manager.get_signal_strength_at((5.0, 0.0))
        strength_far = transmitter_manager.get_signal_strength_at((15.0, 0.0))

        assert strength_close > strength_far

    def test_get_signal_strength_zero_outside_range(self, transmitter_manager):
        """Test signal strength is zero outside range."""
        strength = transmitter_manager.get_signal_strength_at((500.0, 500.0))
        assert strength == 0.0


class TestCoverageQuality:
    """Tests for coverage quality assessment."""

    def test_coverage_quality_excellent(self, transmitter_manager):
        """Test excellent coverage near base."""
        quality = transmitter_manager.get_coverage_quality((0.0, 0.0))
        assert quality == "excellent"

    def test_coverage_quality_none_outside_range(self, transmitter_manager):
        """Test no coverage quality far from transmitters."""
        quality = transmitter_manager.get_coverage_quality((500.0, 500.0))
        assert quality == "none"


class TestTransmitterStats:
    """Tests for transmitter statistics."""

    def test_get_transmitter_count_by_type_empty(self, transmitter_manager):
        """Test type count with no transmitters."""
        from src.systems.transmitter_manager import TransmitterType

        counts = transmitter_manager.get_transmitter_count_by_type()

        for t in TransmitterType:
            assert counts[t] == 0

    def test_get_transmitter_count_by_type(self, transmitter_manager):
        """Test type count with transmitters."""
        from src.systems.transmitter_manager import TransmitterType

        transmitter_manager.place_transmitter(TransmitterType.BASIC, (5.0, 5.0))
        transmitter_manager.place_transmitter(TransmitterType.BASIC, (8.0, 8.0))

        counts = transmitter_manager.get_transmitter_count_by_type()

        assert counts[TransmitterType.BASIC] == 2

    def test_get_total_coverage_area(self, transmitter_manager):
        """Test total coverage area calculation."""
        area = transmitter_manager.get_total_coverage_area()

        # Should include base coverage
        expected_base = math.pi * transmitter_manager.base_range ** 2
        assert area == pytest.approx(expected_base)

    def test_get_summary(self, transmitter_manager):
        """Test summary generation."""
        summary = transmitter_manager.get_summary()

        assert 'total_transmitters' in summary
        assert 'transmitters_by_type' in summary
        assert 'coverage_area' in summary
        assert 'base_range' in summary


class TestTransmitterDataclass:
    """Tests for Transmitter dataclass."""

    def test_transmitter_distance_calculation(self):
        """Test distance calculation method."""
        from src.systems.transmitter_manager import Transmitter, TransmitterType

        transmitter = Transmitter(
            id=1,
            position=(0.0, 0.0),
            transmitter_type=TransmitterType.BASIC,
            range=30.0
        )

        distance = transmitter.get_distance_to((3.0, 4.0))
        assert distance == 5.0  # 3-4-5 triangle

    def test_transmitter_signal_strength_in_range(self):
        """Test signal strength calculation within range."""
        from src.systems.transmitter_manager import Transmitter, TransmitterType

        transmitter = Transmitter(
            id=1,
            position=(0.0, 0.0),
            transmitter_type=TransmitterType.BASIC,
            range=100.0,
            power=100.0
        )

        # At center
        strength = transmitter.get_signal_strength_at((0.0, 0.0))
        assert strength == 100.0

        # At half range
        strength = transmitter.get_signal_strength_at((50.0, 0.0))
        assert strength == 50.0

    def test_transmitter_signal_strength_out_of_range(self):
        """Test signal strength is zero outside range."""
        from src.systems.transmitter_manager import Transmitter, TransmitterType

        transmitter = Transmitter(
            id=1,
            position=(0.0, 0.0),
            transmitter_type=TransmitterType.BASIC,
            range=50.0,
            power=100.0
        )

        strength = transmitter.get_signal_strength_at((100.0, 0.0))
        assert strength == 0.0


class TestTransmitterRepr:
    """Tests for string representation."""

    def test_repr(self, transmitter_manager):
        """Test repr output."""
        result = repr(transmitter_manager)

        assert 'TransmitterManager' in result
        assert 'transmitters=' in result
        assert 'coverage_area=' in result
