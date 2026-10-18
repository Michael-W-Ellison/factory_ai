"""
Tests for the PollutionManager class.

Tests pollution spreading, decay, sources, and serialization.
Note: Rendering tests are skipped as they require pygame.
"""

import pytest
from unittest.mock import patch, MagicMock

# Mock pygame before importing PollutionManager
import sys
sys.modules['pygame'] = MagicMock()

from src.systems.pollution_manager import PollutionManager


class TestPollutionManagerInitialization:
    """Tests for PollutionManager initialization."""

    def test_initial_grid_dimensions(self):
        """Test that grid dimensions are set correctly."""
        manager = PollutionManager(100, 50)

        assert manager.grid_width == 100
        assert manager.grid_height == 50

    def test_initial_pollution_empty(self):
        """Test that pollution dict is empty initially."""
        manager = PollutionManager(100, 100)

        assert manager.pollution == {}

    def test_initial_sources_empty(self):
        """Test that sources dict is empty initially."""
        manager = PollutionManager(100, 100)

        assert manager.sources == {}

    def test_overlay_initially_hidden(self):
        """Test that overlay is hidden by default."""
        manager = PollutionManager(100, 100)

        assert manager.overlay_visible is False

    def test_default_parameters(self):
        """Test default spread and decay parameters."""
        manager = PollutionManager(100, 100)

        assert manager.spread_rate == 0.15
        assert manager.decay_rate == 0.5
        assert manager.max_pollution == 100.0


class TestPollutionSources:
    """Tests for pollution source management."""

    def test_add_source(self):
        """Test adding a pollution source."""
        manager = PollutionManager(100, 100)

        manager.add_source(10, 20, 5.0)

        assert (10, 20) in manager.sources
        assert manager.sources[(10, 20)] == 5.0

    def test_remove_source(self):
        """Test removing a pollution source."""
        manager = PollutionManager(100, 100)
        manager.add_source(10, 20, 5.0)

        manager.remove_source(10, 20)

        assert (10, 20) not in manager.sources

    def test_remove_nonexistent_source_no_error(self):
        """Test that removing nonexistent source does not raise error."""
        manager = PollutionManager(100, 100)

        # Should not raise
        manager.remove_source(99, 99)

    def test_update_source_rate(self):
        """Test updating a source's rate."""
        manager = PollutionManager(100, 100)
        manager.add_source(10, 20, 5.0)

        manager.update_source(10, 20, 10.0)

        assert manager.sources[(10, 20)] == 10.0

    def test_update_source_zero_rate_removes(self):
        """Test that updating to zero rate removes the source."""
        manager = PollutionManager(100, 100)
        manager.add_source(10, 20, 5.0)

        manager.update_source(10, 20, 0.0)

        assert (10, 20) not in manager.sources

    def test_update_source_creates_new(self):
        """Test that update_source can create a new source."""
        manager = PollutionManager(100, 100)

        manager.update_source(10, 20, 5.0)

        assert (10, 20) in manager.sources


class TestPollutionLevels:
    """Tests for pollution level management."""

    def test_add_pollution(self):
        """Test adding pollution to a tile."""
        manager = PollutionManager(100, 100)

        manager.add_pollution(5, 5, 10.0)

        assert manager.pollution[(5, 5)] == 10.0

    def test_add_pollution_accumulates(self):
        """Test that pollution accumulates."""
        manager = PollutionManager(100, 100)

        manager.add_pollution(5, 5, 10.0)
        manager.add_pollution(5, 5, 15.0)

        assert manager.pollution[(5, 5)] == 25.0

    def test_add_pollution_capped_at_max(self):
        """Test that pollution is capped at max_pollution."""
        manager = PollutionManager(100, 100)

        manager.add_pollution(5, 5, 150.0)

        assert manager.pollution[(5, 5)] == 100.0

    def test_add_pollution_ignores_out_of_bounds(self):
        """Test that out-of-bounds pollution is ignored."""
        manager = PollutionManager(100, 100)

        manager.add_pollution(-1, 5, 10.0)
        manager.add_pollution(5, 200, 10.0)

        assert len(manager.pollution) == 0

    def test_get_pollution_existing_tile(self):
        """Test getting pollution for a polluted tile."""
        manager = PollutionManager(100, 100)
        manager.add_pollution(5, 5, 25.0)

        result = manager.get_pollution(5, 5)

        assert result == 25.0

    def test_get_pollution_clean_tile(self):
        """Test getting pollution for a clean tile returns 0."""
        manager = PollutionManager(100, 100)

        result = manager.get_pollution(5, 5)

        assert result == 0.0


class TestPollutionOverlay:
    """Tests for pollution overlay visibility."""

    def test_toggle_overlay_on(self):
        """Test toggling overlay on."""
        manager = PollutionManager(100, 100)

        manager.toggle_overlay()

        assert manager.overlay_visible is True

    def test_toggle_overlay_off(self):
        """Test toggling overlay off."""
        manager = PollutionManager(100, 100)
        manager.overlay_visible = True

        manager.toggle_overlay()

        assert manager.overlay_visible is False


class TestPollutionUpdate:
    """Tests for pollution update (spreading and decay)."""

    def test_update_generates_pollution_from_sources(self):
        """Test that update generates pollution from sources."""
        manager = PollutionManager(100, 100)
        manager.add_source(10, 10, 10.0)
        manager.update_interval = 0.0  # Force immediate update

        manager.update(1.0)

        assert manager.get_pollution(10, 10) > 0

    def test_update_respects_interval(self):
        """Test that update respects the update interval."""
        manager = PollutionManager(100, 100)
        manager.add_source(10, 10, 10.0)
        manager.update_interval = 1.0

        manager.update(0.1)

        # Should not have updated yet
        assert manager.update_timer == 0.1
        assert manager.get_pollution(10, 10) == 0


class TestPollutionSpread:
    """Tests for pollution spreading mechanics."""

    def test_pollution_spreads_to_neighbors(self):
        """Test that pollution spreads to neighboring tiles."""
        manager = PollutionManager(100, 100)
        manager.pollution[(50, 50)] = 50.0

        # Force spread
        manager._spread_pollution(1.0)

        # Check that neighbors have some pollution
        neighbors = [(49, 50), (51, 50), (50, 49), (50, 51)]
        has_spread = any(manager.get_pollution(x, y) > 0 for x, y in neighbors)
        assert has_spread

    def test_pollution_spread_respects_bounds(self):
        """Test that spread respects grid boundaries."""
        manager = PollutionManager(100, 100)
        manager.pollution[(0, 0)] = 50.0

        # Force spread - should not crash
        manager._spread_pollution(1.0)

        # Out-of-bounds tiles should not be created
        assert manager.get_pollution(-1, 0) == 0.0


class TestPollutionDecay:
    """Tests for pollution decay mechanics."""

    def test_pollution_decays_over_time(self):
        """Test that pollution decays over time."""
        manager = PollutionManager(100, 100)
        manager.pollution[(50, 50)] = 50.0

        manager._decay_pollution(1.0)

        # Should be less than original
        assert manager.get_pollution(50, 50) < 50.0

    def test_negligible_pollution_removed(self):
        """Test that very low pollution is removed."""
        manager = PollutionManager(100, 100)
        manager.pollution[(50, 50)] = 0.05  # Below threshold

        manager._decay_pollution(0.1)

        # Should be removed
        assert (50, 50) not in manager.pollution


class TestPollutionColors:
    """Tests for pollution color generation."""

    def test_low_pollution_color(self):
        """Test color for low pollution level."""
        manager = PollutionManager(100, 100)

        color = manager._get_pollution_color(10.0)

        # Should be RGBA tuple
        assert len(color) == 4
        # Low alpha for low pollution
        assert color[3] < 100

    def test_high_pollution_color(self):
        """Test color for high pollution level."""
        manager = PollutionManager(100, 100)

        color = manager._get_pollution_color(90.0)

        # Should be RGBA tuple
        assert len(color) == 4
        # High alpha and red for high pollution
        assert color[0] > 100  # Red component
        assert color[3] > 100  # Alpha

    def test_max_pollution_color(self):
        """Test color for max pollution level."""
        manager = PollutionManager(100, 100)

        color = manager._get_pollution_color(100.0)

        # Should be RGBA tuple
        assert len(color) == 4


class TestPollutionStats:
    """Tests for pollution statistics."""

    def test_stats_empty_pollution(self):
        """Test stats with no pollution."""
        manager = PollutionManager(100, 100)

        stats = manager.get_stats()

        assert stats['total_tiles'] == 0
        assert stats['avg_pollution'] == 0.0
        assert stats['max_pollution_level'] == 0.0
        assert stats['total_pollution'] == 0.0

    def test_stats_with_pollution(self):
        """Test stats with pollution."""
        manager = PollutionManager(100, 100)
        manager.pollution[(0, 0)] = 20.0
        manager.pollution[(1, 1)] = 40.0

        stats = manager.get_stats()

        assert stats['total_tiles'] == 2
        assert stats['avg_pollution'] == 30.0
        assert stats['max_pollution_level'] == 40.0
        assert stats['total_pollution'] == 60.0

    def test_stats_includes_source_count(self):
        """Test that stats includes source count."""
        manager = PollutionManager(100, 100)
        manager.add_source(10, 10, 5.0)
        manager.add_source(20, 20, 3.0)

        stats = manager.get_stats()

        assert stats['sources'] == 2


class TestPollutionSerialization:
    """Tests for pollution serialization (save/load)."""

    def test_to_dict_empty(self):
        """Test to_dict with no pollution."""
        manager = PollutionManager(100, 100)

        data = manager.to_dict()

        assert data['pollution'] == {}
        assert data['sources'] == {}
        assert data['overlay_visible'] is False

    def test_to_dict_with_data(self):
        """Test to_dict with pollution and sources."""
        manager = PollutionManager(100, 100)
        manager.pollution[(5, 10)] = 25.0
        manager.sources[(15, 20)] = 5.0
        manager.overlay_visible = True

        data = manager.to_dict()

        assert data['pollution']['5,10'] == 25.0
        assert data['sources']['15,20'] == 5.0
        assert data['overlay_visible'] is True

    def test_from_dict_restores_pollution(self):
        """Test from_dict restores pollution state."""
        manager = PollutionManager(100, 100)
        data = {
            'pollution': {'5,10': 25.0, '20,30': 50.0},
            'sources': {'15,20': 5.0},
            'overlay_visible': True
        }

        manager.from_dict(data)

        assert manager.pollution[(5, 10)] == 25.0
        assert manager.pollution[(20, 30)] == 50.0
        assert manager.sources[(15, 20)] == 5.0
        assert manager.overlay_visible is True

    def test_from_dict_handles_empty_data(self):
        """Test from_dict handles empty data gracefully."""
        manager = PollutionManager(100, 100)
        manager.pollution[(1, 1)] = 10.0  # Pre-existing

        manager.from_dict({})

        assert manager.pollution == {}
        assert manager.sources == {}
        assert manager.overlay_visible is False


class TestPollutionRepr:
    """Tests for string representation."""

    def test_repr_empty(self):
        """Test repr with no pollution."""
        manager = PollutionManager(100, 100)

        result = repr(manager)

        assert "PollutionManager" in result
        assert "tiles=0" in result

    def test_repr_with_data(self):
        """Test repr with pollution data."""
        manager = PollutionManager(100, 100)
        manager.pollution[(0, 0)] = 50.0
        manager.add_source(10, 10, 5.0)

        result = repr(manager)

        assert "tiles=1" in result
        assert "sources=1" in result


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_zero_grid_dimensions(self):
        """Test with zero grid dimensions."""
        manager = PollutionManager(0, 0)

        # Should not crash
        manager.add_pollution(0, 0, 10.0)
        assert len(manager.pollution) == 0

    def test_single_tile_grid(self):
        """Test with single tile grid."""
        manager = PollutionManager(1, 1)

        manager.add_pollution(0, 0, 50.0)
        manager._spread_pollution(1.0)

        # Should still have pollution, no neighbors to spread to
        assert manager.get_pollution(0, 0) > 0

    def test_negative_pollution_amount(self):
        """Test adding negative pollution amount."""
        manager = PollutionManager(100, 100)
        manager.pollution[(5, 5)] = 50.0

        # Adding negative should reduce (but this is add, so just adds negative)
        manager.add_pollution(5, 5, -10.0)

        # Result depends on implementation - should cap at 0 or add
        assert manager.get_pollution(5, 5) >= 0
