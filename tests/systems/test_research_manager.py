"""
Tests for the ResearchManager class.

Tests research unlocks, prerequisites, progress, and effects.
"""

import sys
from unittest.mock import MagicMock

# Mock pygame before importing any src modules
sys.modules['pygame'] = MagicMock()

import pytest
from unittest.mock import patch, mock_open

from src.systems.research_manager import ResearchManager


class TestResearchManagerInitialization:
    """Tests for ResearchManager initialization."""

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_initial_state(self, mock_load):
        """Test that manager initializes with empty research state."""
        mock_load.return_value = {}
        manager = ResearchManager()

        assert manager.completed_research == {}
        assert manager.current_research is None
        assert manager.research_progress == 0.0
        assert manager.research_total_time == 0.0
        assert manager.effects_changed is False

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_initial_statistics(self, mock_load):
        """Test that initial statistics are zeroed."""
        mock_load.return_value = {}
        manager = ResearchManager()

        assert manager.stats['total_researched'] == 0
        assert manager.stats['money_spent'] == 0
        assert manager.stats['time_spent'] == 0.0


class TestResearchDefinitions:
    """Tests for research definition loading and retrieval."""

    @patch('os.path.exists')
    def test_load_definitions_missing_file(self, mock_exists):
        """Test that missing file returns empty dict."""
        mock_exists.return_value = False
        manager = ResearchManager()

        # Should have empty definitions
        assert manager.research_definitions == {}

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_research_definition_exists(self, mock_file, mock_exists):
        """Test getting an existing research definition."""
        mock_exists.return_value = True
        tech_data = {
            'technologies': {
                'basic_robots': {
                    'name': 'Basic Robots',
                    'cost': 1000,
                    'time': 2.0
                }
            }
        }

        with patch('json.load', return_value=tech_data):
            manager = ResearchManager()

        result = manager.get_research_definition('basic_robots')
        assert result is not None
        assert result['name'] == 'Basic Robots'

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_get_research_definition_not_exists(self, mock_load):
        """Test getting a non-existent research definition."""
        mock_load.return_value = {}
        manager = ResearchManager()

        result = manager.get_research_definition('nonexistent')
        assert result is None


class TestResearchCompletion:
    """Tests for research completion checks."""

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_is_completed_false_initially(self, mock_load):
        """Test that research is not completed initially."""
        mock_load.return_value = {'tech1': {}}
        manager = ResearchManager()

        assert manager.is_completed('tech1') is False

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_is_completed_true_after_completion(self, mock_load):
        """Test that is_completed returns True after completion."""
        mock_load.return_value = {'tech1': {}}
        manager = ResearchManager()
        manager.completed_research['tech1'] = 1.0

        assert manager.is_completed('tech1') is True


class TestResearchAvailability:
    """Tests for research availability checks."""

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_is_available_no_prerequisites(self, mock_load):
        """Test research with no prerequisites is available."""
        mock_load.return_value = {
            'basic_tech': {'name': 'Basic', 'prerequisites': []}
        }
        manager = ResearchManager()

        assert manager.is_available('basic_tech') is True

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_is_available_prerequisites_not_met(self, mock_load):
        """Test research with unmet prerequisites is not available."""
        mock_load.return_value = {
            'basic_tech': {'name': 'Basic', 'prerequisites': []},
            'advanced_tech': {'name': 'Advanced', 'prerequisites': ['basic_tech']}
        }
        manager = ResearchManager()

        assert manager.is_available('advanced_tech') is False

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_is_available_prerequisites_met(self, mock_load):
        """Test research with met prerequisites is available."""
        mock_load.return_value = {
            'basic_tech': {'name': 'Basic', 'prerequisites': []},
            'advanced_tech': {'name': 'Advanced', 'prerequisites': ['basic_tech']}
        }
        manager = ResearchManager()
        manager.completed_research['basic_tech'] = 1.0

        assert manager.is_available('advanced_tech') is True

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_is_available_already_completed(self, mock_load):
        """Test that completed research is not available."""
        mock_load.return_value = {
            'basic_tech': {'name': 'Basic', 'prerequisites': []}
        }
        manager = ResearchManager()
        manager.completed_research['basic_tech'] = 1.0

        assert manager.is_available('basic_tech') is False


class TestStartResearch:
    """Tests for starting research."""

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_can_start_research_with_funds(self, mock_load):
        """Test can_start_research returns True with sufficient funds."""
        mock_load.return_value = {
            'tech1': {'name': 'Tech', 'cost': 500, 'prerequisites': []}
        }
        manager = ResearchManager()

        can_start, reason = manager.can_start_research('tech1', money=1000)
        assert can_start is True

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_cannot_start_research_insufficient_funds(self, mock_load):
        """Test can_start_research returns False with insufficient funds."""
        mock_load.return_value = {
            'tech1': {'name': 'Tech', 'cost': 500, 'prerequisites': []}
        }
        manager = ResearchManager()

        can_start, reason = manager.can_start_research('tech1', money=100)
        assert can_start is False
        assert "Insufficient funds" in reason

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_cannot_start_unknown_research(self, mock_load):
        """Test can_start_research returns False for unknown tech."""
        mock_load.return_value = {}
        manager = ResearchManager()

        can_start, reason = manager.can_start_research('unknown', money=1000)
        assert can_start is False
        assert "Unknown technology" in reason

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_cannot_start_already_researching(self, mock_load):
        """Test can_start_research returns False when already researching."""
        mock_load.return_value = {
            'tech1': {'name': 'Tech1', 'cost': 500, 'prerequisites': []},
            'tech2': {'name': 'Tech2', 'cost': 500, 'prerequisites': []}
        }
        manager = ResearchManager()
        manager.current_research = 'tech1'

        can_start, reason = manager.can_start_research('tech2', money=1000)
        assert can_start is False
        assert "Already researching" in reason

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_start_research_deducts_cost(self, mock_load):
        """Test that start_research deducts the cost from money."""
        mock_load.return_value = {
            'tech1': {'name': 'Tech', 'cost': 500, 'time': 2.0, 'prerequisites': []}
        }
        manager = ResearchManager()

        success, remaining = manager.start_research('tech1', money=1000)

        assert success is True
        assert remaining == 500

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_start_research_sets_current_research(self, mock_load):
        """Test that start_research sets current_research."""
        mock_load.return_value = {
            'tech1': {'name': 'Tech', 'cost': 500, 'time': 2.0, 'prerequisites': []}
        }
        manager = ResearchManager()

        manager.start_research('tech1', money=1000)

        assert manager.current_research == 'tech1'
        assert manager.research_total_time == 2.0
        assert manager.research_progress == 0.0


class TestResearchProgress:
    """Tests for research progress updates."""

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_update_increments_progress(self, mock_load):
        """Test that update increments research progress."""
        mock_load.return_value = {
            'tech1': {'name': 'Tech', 'cost': 500, 'time': 2.0, 'prerequisites': []}
        }
        manager = ResearchManager()
        manager.start_research('tech1', money=1000)

        manager.update(0.5)

        assert manager.research_progress == 0.5

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_update_completes_research(self, mock_load):
        """Test that update completes research when time is met."""
        mock_load.return_value = {
            'tech1': {'name': 'Tech', 'cost': 500, 'time': 2.0, 'prerequisites': []}
        }
        manager = ResearchManager()
        manager.start_research('tech1', money=1000)

        completed = manager.update(2.5)

        assert completed == 'tech1'
        assert manager.is_completed('tech1')
        assert manager.current_research is None

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_update_returns_none_when_not_researching(self, mock_load):
        """Test that update returns None when not researching."""
        mock_load.return_value = {}
        manager = ResearchManager()

        result = manager.update(1.0)

        assert result is None

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_update_sets_effects_changed_on_completion(self, mock_load):
        """Test that effects_changed is set on research completion."""
        mock_load.return_value = {
            'tech1': {'name': 'Tech', 'cost': 500, 'time': 1.0, 'prerequisites': []}
        }
        manager = ResearchManager()
        manager.start_research('tech1', money=1000)
        manager.effects_changed = False

        manager.update(1.5)

        assert manager.effects_changed is True


class TestCancelResearch:
    """Tests for cancelling research."""

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_cancel_research_clears_state(self, mock_load):
        """Test that cancel_research clears current research."""
        mock_load.return_value = {
            'tech1': {'name': 'Tech', 'cost': 500, 'time': 2.0, 'prerequisites': []}
        }
        manager = ResearchManager()
        manager.start_research('tech1', money=1000)

        result = manager.cancel_research()

        assert result is True
        assert manager.current_research is None
        assert manager.research_progress == 0.0

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_cancel_research_returns_false_when_not_researching(self, mock_load):
        """Test that cancel_research returns False when not researching."""
        mock_load.return_value = {}
        manager = ResearchManager()

        result = manager.cancel_research()

        assert result is False


class TestResearchEffects:
    """Tests for research effects."""

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_get_effect_returns_default_when_no_research(self, mock_load):
        """Test that get_effect returns default when no research completed."""
        mock_load.return_value = {}
        manager = ResearchManager()

        result = manager.get_effect('robot_speed', default=1.0)

        assert result == 1.0

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_get_effect_returns_effect_value(self, mock_load):
        """Test that get_effect returns the effect value."""
        mock_load.return_value = {
            'speed_boost': {
                'name': 'Speed Boost',
                'effects': {'robot_speed': 1.5}
            }
        }
        manager = ResearchManager()
        manager.completed_research['speed_boost'] = 1.0

        result = manager.get_effect('robot_speed', default=1.0)

        assert result == 1.5

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_get_effect_multiplier(self, mock_load):
        """Test get_effect_multiplier method."""
        mock_load.return_value = {
            'capacity_boost': {
                'name': 'Capacity Boost',
                'effects': {'robot_capacity': 2.0}
            }
        }
        manager = ResearchManager()
        manager.completed_research['capacity_boost'] = 1.0

        result = manager.get_effect_multiplier('robot_capacity')

        assert result == 2.0

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_has_unlock_false_when_not_researched(self, mock_load):
        """Test has_unlock returns False when not unlocked."""
        mock_load.return_value = {
            'drones': {
                'name': 'Drones',
                'effects': {'unlock_drones': True}
            }
        }
        manager = ResearchManager()

        result = manager.has_unlock('unlock_drones')

        assert result is False

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_has_unlock_true_when_researched(self, mock_load):
        """Test has_unlock returns True when unlocked."""
        mock_load.return_value = {
            'drones': {
                'name': 'Drones',
                'effects': {'unlock_drones': True}
            }
        }
        manager = ResearchManager()
        manager.completed_research['drones'] = 1.0

        result = manager.has_unlock('unlock_drones')

        assert result is True


class TestGetTechnologies:
    """Tests for getting technology lists."""

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_get_available_technologies(self, mock_load):
        """Test get_available_technologies returns available techs."""
        mock_load.return_value = {
            'tech1': {'name': 'Tech1', 'cost': 100, 'prerequisites': []},
            'tech2': {'name': 'Tech2', 'cost': 200, 'prerequisites': ['tech1']}
        }
        manager = ResearchManager()

        available = manager.get_available_technologies()

        assert len(available) == 1
        assert available[0]['id'] == 'tech1'

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_get_available_technologies_filtered_by_category(self, mock_load):
        """Test get_available_technologies can filter by category."""
        mock_load.return_value = {
            'tech1': {'name': 'Tech1', 'cost': 100, 'category': 'robots', 'prerequisites': []},
            'tech2': {'name': 'Tech2', 'cost': 200, 'category': 'buildings', 'prerequisites': []}
        }
        manager = ResearchManager()

        available = manager.get_available_technologies(category='robots')

        assert len(available) == 1
        assert available[0]['category'] == 'robots'

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_get_completed_technologies(self, mock_load):
        """Test get_completed_technologies returns completed techs."""
        mock_load.return_value = {
            'tech1': {'name': 'Tech1'},
            'tech2': {'name': 'Tech2'}
        }
        manager = ResearchManager()
        manager.completed_research['tech1'] = 1.0

        completed = manager.get_completed_technologies()

        assert len(completed) == 1
        assert completed[0]['id'] == 'tech1'


class TestProgressInfo:
    """Tests for progress information."""

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_get_progress_info_when_not_researching(self, mock_load):
        """Test get_progress_info returns None when not researching."""
        mock_load.return_value = {}
        manager = ResearchManager()

        result = manager.get_progress_info()

        assert result is None

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_get_progress_info_when_researching(self, mock_load):
        """Test get_progress_info returns info when researching."""
        mock_load.return_value = {
            'tech1': {'name': 'Tech1', 'cost': 100, 'time': 4.0, 'prerequisites': []}
        }
        manager = ResearchManager()
        manager.start_research('tech1', money=1000)
        manager.update(1.0)

        info = manager.get_progress_info()

        assert info is not None
        assert info['tech_id'] == 'tech1'
        assert info['progress'] == 1.0
        assert info['total_time'] == 4.0
        assert info['percent'] == 25.0
        assert info['remaining'] == 3.0


class TestSaveLoadState:
    """Tests for save and load state."""

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_save_state(self, mock_load):
        """Test save_state returns serializable state."""
        mock_load.return_value = {
            'tech1': {'name': 'Tech1', 'cost': 100, 'time': 2.0, 'prerequisites': []}
        }
        manager = ResearchManager()
        manager.start_research('tech1', money=1000)
        manager.update(0.5)

        state = manager.save_state()

        assert 'completed_research' in state
        assert 'current_research' in state
        assert state['current_research'] == 'tech1'
        assert state['research_progress'] == 0.5

    @patch.object(ResearchManager, '_load_research_definitions')
    def test_load_state(self, mock_load):
        """Test load_state restores manager state."""
        mock_load.return_value = {
            'tech1': {'name': 'Tech1'},
            'tech2': {'name': 'Tech2'}
        }
        manager = ResearchManager()

        state = {
            'completed_research': {'tech1': 1.0},
            'current_research': 'tech2',
            'research_progress': 0.75,
            'research_total_time': 2.0,
            'stats': {'total_researched': 1, 'money_spent': 500, 'time_spent': 1.0}
        }

        manager.load_state(state)

        assert manager.is_completed('tech1')
        assert manager.current_research == 'tech2'
        assert manager.research_progress == 0.75
        assert manager.stats['total_researched'] == 1
        assert manager.effects_changed is True
