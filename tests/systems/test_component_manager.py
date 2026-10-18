"""
Unit tests for ComponentManager.

Tests component inventory, manufacturing, and recipes.
"""

import pytest
import json
import os
from unittest.mock import Mock, MagicMock, patch, mock_open


@pytest.fixture
def component_definitions():
    """Sample component definitions for testing."""
    return {
        'circuit_board': {
            'name': 'Circuit Board',
            'base_value': 100,
            'processing_time': 5.0,
            'recipe': {'copper': 2.0, 'silicon': 1.0},
            'requires_research': None
        },
        'motor': {
            'name': 'Electric Motor',
            'base_value': 200,
            'processing_time': 10.0,
            'recipe': {'copper': 3.0, 'iron': 2.0},
            'requires_research': 'advanced_components'
        },
        'sensor': {
            'name': 'Sensor Module',
            'base_value': 150,
            'processing_time': 8.0,
            'recipe': {'circuit_board': 1.0, 'copper': 1.0},
            'requires_research': None
        }
    }


@pytest.fixture
def component_manager(component_definitions):
    """Create ComponentManager with mock definitions."""
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data=json.dumps({'components': component_definitions}))):
            from src.systems.component_manager import ComponentManager
            return ComponentManager()


@pytest.fixture
def component_manager_no_file():
    """Create ComponentManager with no definitions file."""
    with patch('os.path.exists', return_value=False):
        from src.systems.component_manager import ComponentManager
        return ComponentManager()


class TestComponentManagerInit:
    """Tests for ComponentManager initialization."""

    def test_init_loads_definitions(self, component_manager, component_definitions):
        """Test that initialization loads component definitions."""
        assert 'circuit_board' in component_manager.component_definitions
        assert 'motor' in component_manager.component_definitions

    def test_init_empty_inventory(self, component_manager):
        """Test that inventory starts empty."""
        assert component_manager.inventory == {}

    def test_init_no_active_manufacturing(self, component_manager):
        """Test that no manufacturing is active initially."""
        assert component_manager.active_manufacturing == {}

    def test_init_missing_file(self, component_manager_no_file):
        """Test initialization with missing definitions file."""
        assert component_manager_no_file.component_definitions == {}


class TestComponentDefinitions:
    """Tests for component definition access."""

    def test_get_component_definition(self, component_manager):
        """Test getting a valid component definition."""
        definition = component_manager.get_component_definition('circuit_board')

        assert definition is not None
        assert definition['name'] == 'Circuit Board'
        assert definition['base_value'] == 100

    def test_get_component_definition_not_found(self, component_manager):
        """Test getting a non-existent component definition."""
        definition = component_manager.get_component_definition('unknown_component')
        assert definition is None

    def test_get_recipe(self, component_manager):
        """Test getting component recipe."""
        recipe = component_manager.get_recipe('circuit_board')

        assert recipe is not None
        assert 'copper' in recipe
        assert recipe['copper'] == 2.0

    def test_get_recipe_not_found(self, component_manager):
        """Test getting recipe for unknown component."""
        recipe = component_manager.get_recipe('unknown_component')
        assert recipe is None

    def test_get_processing_time(self, component_manager):
        """Test getting processing time."""
        time = component_manager.get_processing_time('circuit_board')
        assert time == 5.0

    def test_get_processing_time_default(self, component_manager):
        """Test default processing time for unknown component."""
        time = component_manager.get_processing_time('unknown_component')
        assert time == 10.0


class TestResearchRequirements:
    """Tests for research requirement checking."""

    def test_requires_research_none(self, component_manager):
        """Test component with no research requirement."""
        requirement = component_manager.requires_research('circuit_board')
        assert requirement is None

    def test_requires_research_exists(self, component_manager):
        """Test component with research requirement."""
        requirement = component_manager.requires_research('motor')
        assert requirement == 'advanced_components'

    def test_is_unlocked_no_requirement(self, component_manager):
        """Test unlocked status when no research required."""
        result = component_manager.is_unlocked('circuit_board', None)
        assert result is True

    def test_is_unlocked_with_completed_research(self, component_manager):
        """Test unlocked status with completed research."""
        mock_research = Mock()
        mock_research.is_completed.return_value = True

        result = component_manager.is_unlocked('motor', mock_research)
        assert result is True

    def test_is_locked_without_research(self, component_manager):
        """Test locked status without completed research."""
        mock_research = Mock()
        mock_research.is_completed.return_value = False

        result = component_manager.is_unlocked('motor', mock_research)
        assert result is False


class TestInventoryManagement:
    """Tests for inventory operations."""

    def test_add_component(self, component_manager):
        """Test adding components to inventory."""
        result = component_manager.add_component('circuit_board', 'medium', 5.0)

        assert result is True
        assert component_manager.get_component_count('circuit_board', 'medium') == 5.0

    def test_add_component_unknown_type(self, component_manager):
        """Test adding unknown component type."""
        result = component_manager.add_component('unknown_component', 'medium', 5.0)
        assert result is False

    def test_add_component_accumulates(self, component_manager):
        """Test that adding components accumulates."""
        component_manager.add_component('circuit_board', 'medium', 5.0)
        component_manager.add_component('circuit_board', 'medium', 3.0)

        assert component_manager.get_component_count('circuit_board', 'medium') == 8.0

    def test_remove_component(self, component_manager):
        """Test removing components from inventory."""
        component_manager.add_component('circuit_board', 'medium', 10.0)

        result = component_manager.remove_component('circuit_board', 'medium', 3.0)

        assert result is True
        assert component_manager.get_component_count('circuit_board', 'medium') == 7.0

    def test_remove_component_insufficient(self, component_manager):
        """Test removing more components than available."""
        component_manager.add_component('circuit_board', 'medium', 5.0)

        result = component_manager.remove_component('circuit_board', 'medium', 10.0)

        assert result is False
        assert component_manager.get_component_count('circuit_board', 'medium') == 5.0

    def test_get_component_count_total(self, component_manager):
        """Test getting total count across qualities."""
        component_manager.add_component('circuit_board', 'low', 3.0)
        component_manager.add_component('circuit_board', 'medium', 5.0)
        component_manager.add_component('circuit_board', 'high', 2.0)

        total = component_manager.get_component_count('circuit_board')
        assert total == 10.0


class TestComponentValue:
    """Tests for component value calculations."""

    def test_get_total_value_empty(self, component_manager):
        """Test total value with empty inventory."""
        value = component_manager.get_total_value()
        assert value == 0.0

    def test_get_total_value_single_component(self, component_manager):
        """Test total value with one component type."""
        component_manager.add_component('circuit_board', 'medium', 2.0)

        # base_value=100, quality_mult=1.0, quantity=2.0
        expected = 100 * 1.0 * 2.0
        assert component_manager.get_total_value('circuit_board') == expected

    def test_quality_multipliers(self, component_manager):
        """Test quality multipliers affect value."""
        component_manager.add_component('circuit_board', 'low', 1.0)
        component_manager.add_component('circuit_board', 'high', 1.0)

        # low: 100 * 0.5 = 50
        # high: 100 * 2.0 = 200
        expected = 250
        assert component_manager.get_total_value('circuit_board') == expected


class TestManufacturing:
    """Tests for manufacturing operations."""

    def test_can_manufacture_with_resources(self, component_manager):
        """Test can_manufacture when resources are available."""
        mock_resources = Mock()
        mock_resources.get_material_amount = Mock(return_value=10.0)

        can_make, reason = component_manager.can_manufacture('circuit_board', mock_resources)

        assert can_make is True
        assert reason == "Can manufacture"

    def test_can_manufacture_insufficient_resources(self, component_manager):
        """Test can_manufacture when resources are insufficient."""
        mock_resources = Mock()
        mock_resources.get_material_amount = Mock(return_value=0.0)

        can_make, reason = component_manager.can_manufacture('circuit_board', mock_resources)

        assert can_make is False
        assert "Insufficient" in reason

    def test_start_manufacturing(self, component_manager):
        """Test starting manufacturing process."""
        mock_resources = Mock()
        mock_resources.get_material_amount = Mock(return_value=10.0)
        mock_resources.remove_material = Mock()

        result = component_manager.start_manufacturing(
            building_id=1,
            component_type='circuit_board',
            resource_manager=mock_resources,
            quality='medium'
        )

        assert result is True
        assert 1 in component_manager.active_manufacturing


class TestSaveLoad:
    """Tests for save/load state operations."""

    def test_save_state(self, component_manager):
        """Test saving state."""
        component_manager.add_component('circuit_board', 'medium', 5.0)

        state = component_manager.save_state()

        assert 'inventory' in state
        assert 'active_manufacturing' in state
        assert state['inventory']['circuit_board']['medium'] == 5.0

    def test_load_state(self, component_manager):
        """Test loading state."""
        state = {
            'inventory': {'circuit_board': {'high': 10.0}},
            'active_manufacturing': {}
        }

        component_manager.load_state(state)

        assert component_manager.get_component_count('circuit_board', 'high') == 10.0


class TestComponentManagerRepr:
    """Tests for string representation."""

    def test_repr(self, component_manager):
        """Test repr output."""
        component_manager.add_component('circuit_board', 'medium', 5.0)

        result = repr(component_manager)

        assert 'ComponentManager' in result
        assert 'types' in result
        assert 'value' in result
