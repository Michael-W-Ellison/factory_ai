"""
Unit tests for AutomationManager.

Tests automation rules, task prioritization, material routing,
and building automation features.
"""

import sys
import os
import pytest
from unittest.mock import Mock, MagicMock

# Mock pygame before any imports that might need it
sys.modules['pygame'] = Mock()

# Import directly to avoid __init__.py cascade
import importlib.util

# Get the path relative to this test file
_test_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_test_dir))
_module_path = os.path.join(_project_root, "src", "systems", "automation_manager.py")

spec = importlib.util.spec_from_file_location(
    "automation_manager",
    _module_path
)
automation_manager_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(automation_manager_module)
AutomationManager = automation_manager_module.AutomationManager
TaskPriority = automation_manager_module.TaskPriority


class MockBuilding:
    """Mock building for testing automation."""

    def __init__(self, building_id: int, input_types=None, output_weight=0.0,
                 max_output=100.0, input_weight=0.0, max_input=100.0):
        self.id = building_id
        self.input_material_types = input_types or ['iron', 'copper']
        self.output_queue = []
        self.input_queue = []
        self.max_output_queue = max_output
        self.max_input_queue = max_input
        self._output_weight = output_weight
        self._input_weight = input_weight
        self.processing_current = None

    def get_current_output_weight(self):
        return self._output_weight

    def get_current_input_weight(self):
        return self._input_weight

    def can_start_manufacturing(self):
        return len(self.input_queue) > 0


class MockWarehouse:
    """Mock warehouse for testing material delivery."""

    def __init__(self, materials=None):
        self._materials = materials or {}

    def get_material_amount(self, material_type):
        return self._materials.get(material_type, 0.0)


class TestAutomationManagerInit:
    """Tests for AutomationManager initialization."""

    def test_init_creates_empty_state(self):
        """Test that initialization creates empty state."""
        manager = AutomationManager()

        assert manager.building_automation == {}
        assert manager.material_routing == {}
        assert manager.pending_tasks == []
        assert manager.active_tasks == {}

    def test_init_creates_statistics(self):
        """Test that initialization creates statistics dictionary."""
        manager = AutomationManager()

        assert manager.stats['deliveries_completed'] == 0
        assert manager.stats['collections_completed'] == 0
        assert manager.stats['materials_delivered'] == 0.0
        assert manager.stats['materials_collected'] == 0.0


class TestBuildingAutomation:
    """Tests for building automation enable/disable."""

    def test_enable_building_automation_defaults(self):
        """Test enabling automation with default settings."""
        manager = AutomationManager()
        manager.enable_building_automation(1)

        assert 1 in manager.building_automation
        assert manager.building_automation[1]['auto_deliver'] is True
        assert manager.building_automation[1]['auto_collect'] is True
        assert manager.building_automation[1]['enabled'] is True

    def test_enable_building_automation_custom(self):
        """Test enabling automation with custom settings."""
        manager = AutomationManager()
        manager.enable_building_automation(2, auto_deliver=False, auto_collect=True)

        assert manager.building_automation[2]['auto_deliver'] is False
        assert manager.building_automation[2]['auto_collect'] is True

    def test_disable_building_automation(self):
        """Test disabling automation for a building."""
        manager = AutomationManager()
        manager.enable_building_automation(1)
        manager.disable_building_automation(1)

        assert manager.building_automation[1]['enabled'] is False

    def test_disable_nonexistent_building_no_error(self):
        """Test that disabling a nonexistent building does not error."""
        manager = AutomationManager()
        manager.disable_building_automation(999)  # Should not raise

    def test_is_automation_enabled_true(self):
        """Test is_automation_enabled returns True for enabled building."""
        manager = AutomationManager()
        manager.enable_building_automation(1)

        assert manager.is_automation_enabled(1) is True

    def test_is_automation_enabled_false_after_disable(self):
        """Test is_automation_enabled returns False after disabling."""
        manager = AutomationManager()
        manager.enable_building_automation(1)
        manager.disable_building_automation(1)

        assert manager.is_automation_enabled(1) is False

    def test_is_automation_enabled_nonexistent(self):
        """Test is_automation_enabled returns False for nonexistent building."""
        manager = AutomationManager()

        assert manager.is_automation_enabled(999) is False


class TestMaterialRouting:
    """Tests for material routing preferences."""

    def test_set_material_routing(self):
        """Test setting material routing preferences."""
        manager = AutomationManager()
        manager.set_material_routing('iron', [1, 2, 3])

        assert manager.material_routing['iron'] == [1, 2, 3]

    def test_get_material_routing_exists(self):
        """Test getting existing material routing."""
        manager = AutomationManager()
        manager.set_material_routing('copper', [4, 5])

        assert manager.get_material_routing('copper') == [4, 5]

    def test_get_material_routing_nonexistent(self):
        """Test getting nonexistent material routing returns empty list."""
        manager = AutomationManager()

        assert manager.get_material_routing('nonexistent') == []

    def test_add_routing_preference_new_material(self):
        """Test adding routing preference for new material."""
        manager = AutomationManager()
        manager.add_routing_preference('steel', 10)

        assert 10 in manager.material_routing['steel']

    def test_add_routing_preference_existing_material(self):
        """Test adding routing preference to existing material."""
        manager = AutomationManager()
        manager.set_material_routing('steel', [1])
        manager.add_routing_preference('steel', 2)

        assert manager.material_routing['steel'] == [1, 2]

    def test_add_routing_preference_no_duplicates(self):
        """Test that adding duplicate building does not create duplicate."""
        manager = AutomationManager()
        manager.set_material_routing('steel', [1])
        manager.add_routing_preference('steel', 1)

        assert manager.material_routing['steel'] == [1]

    def test_remove_routing_preference(self):
        """Test removing routing preference."""
        manager = AutomationManager()
        manager.set_material_routing('iron', [1, 2, 3])
        manager.remove_routing_preference('iron', 2)

        assert manager.material_routing['iron'] == [1, 3]

    def test_remove_routing_preference_nonexistent(self):
        """Test removing nonexistent preference does not error."""
        manager = AutomationManager()
        manager.set_material_routing('iron', [1])
        manager.remove_routing_preference('iron', 999)  # Should not raise

        assert manager.material_routing['iron'] == [1]


class TestOutputCollection:
    """Tests for output collection task generation."""

    def test_check_output_collection_critical_priority(self):
        """Test that high output generates critical priority task."""
        manager = AutomationManager()
        building = MockBuilding(1, output_weight=95.0, max_output=100.0)
        building.output_queue = [{'material_type': 'iron', 'quantity': 50}]

        tasks = manager._check_output_collection(building, 1)

        assert len(tasks) == 1
        assert tasks[0][0] == TaskPriority.CRITICAL

    def test_check_output_collection_high_priority(self):
        """Test that moderate output generates high priority task."""
        manager = AutomationManager()
        building = MockBuilding(1, output_weight=75.0, max_output=100.0)
        building.output_queue = [{'material_type': 'iron', 'quantity': 30}]

        tasks = manager._check_output_collection(building, 1)

        assert len(tasks) == 1
        assert tasks[0][0] == TaskPriority.HIGH

    def test_check_output_collection_low_output_no_task(self):
        """Test that very low output does not generate task."""
        manager = AutomationManager()
        building = MockBuilding(1, output_weight=5.0, max_output=100.0)
        building.output_queue = [{'material_type': 'iron', 'quantity': 2}]

        tasks = manager._check_output_collection(building, 1)

        assert len(tasks) == 0

    def test_check_output_collection_no_queue_attribute(self):
        """Test handling building without output_queue attribute."""
        manager = AutomationManager()
        building = Mock()
        del building.output_queue

        tasks = manager._check_output_collection(building, 1)

        assert tasks == []


class TestMaterialDelivery:
    """Tests for material delivery task generation."""

    def test_check_material_delivery_building_needs_materials(self):
        """Test delivery task when building needs materials."""
        manager = AutomationManager()
        building = MockBuilding(1, input_weight=10.0, max_input=100.0)
        building.processing_current = None
        building.input_queue = []
        warehouse = MockWarehouse({'iron': 100.0})

        tasks = manager._check_material_delivery(building, 1, warehouse)

        assert len(tasks) > 0
        assert tasks[0][1] == 'deliver'

    def test_check_material_delivery_respects_routing(self):
        """Test that delivery respects material routing preferences."""
        manager = AutomationManager()
        manager.set_material_routing('iron', [2, 3])  # Building 1 not preferred

        building = MockBuilding(1, input_weight=10.0, max_input=100.0)
        building.input_queue = []
        warehouse = MockWarehouse({'iron': 100.0})

        tasks = manager._check_material_delivery(building, 1, warehouse)

        # No iron delivery because building 1 is not preferred
        iron_tasks = [t for t in tasks if t[3] == 'iron']
        assert len(iron_tasks) == 0

    def test_check_material_delivery_input_full_no_task(self):
        """Test no delivery when input queue nearly full."""
        manager = AutomationManager()
        building = MockBuilding(1, input_weight=95.0, max_input=100.0)
        warehouse = MockWarehouse({'iron': 100.0})

        tasks = manager._check_material_delivery(building, 1, warehouse)

        assert len(tasks) == 0


class TestTaskManagement:
    """Tests for task management."""

    def test_scan_buildings_filters_non_automated(self):
        """Test that scan_buildings filters non-automated buildings."""
        manager = AutomationManager()
        manager.enable_building_automation(1)

        building1 = MockBuilding(1)
        building2 = MockBuilding(2)
        buildings = {1: building1, 2: building2}
        warehouse = MockWarehouse()

        tasks = manager.scan_buildings(buildings, warehouse)

        # Only building 1 should be scanned
        building_ids = set(t[2] for t in tasks)
        assert 2 not in building_ids

    def test_get_next_task_assigns_task(self):
        """Test that get_next_task assigns and tracks task."""
        manager = AutomationManager()
        manager.enable_building_automation(1)

        building = MockBuilding(1, output_weight=95.0, max_output=100.0)
        building.output_queue = [{'material_type': 'iron', 'quantity': 50}]
        buildings = {1: building}
        warehouse = MockWarehouse()

        task = manager.get_next_task(1, (0, 0), buildings, warehouse)

        assert task is not None
        assert 1 in manager.active_tasks

    def test_get_next_task_returns_existing_active_task(self):
        """Test that get_next_task returns existing active task."""
        manager = AutomationManager()
        existing_task = {'robot_id': 1, 'task_type': 'deliver'}
        manager.active_tasks[1] = existing_task

        task = manager.get_next_task(1, (0, 0), {}, None)

        assert task == existing_task

    def test_complete_task_updates_delivery_stats(self):
        """Test that completing delivery task updates statistics."""
        manager = AutomationManager()
        manager.active_tasks[1] = {'task_type': 'deliver'}

        manager.complete_task(1, 'deliver', 'iron', 50.0)

        assert manager.stats['deliveries_completed'] == 1
        assert manager.stats['materials_delivered'] == 50.0
        assert 1 not in manager.active_tasks

    def test_complete_task_updates_collection_stats(self):
        """Test that completing collection task updates statistics."""
        manager = AutomationManager()
        manager.active_tasks[1] = {'task_type': 'collect'}

        manager.complete_task(1, 'collect', 'copper', 30.0)

        assert manager.stats['collections_completed'] == 1
        assert manager.stats['materials_collected'] == 30.0

    def test_cancel_task_removes_active_task(self):
        """Test that cancel_task removes active task."""
        manager = AutomationManager()
        manager.active_tasks[1] = {'task_type': 'deliver'}

        manager.cancel_task(1)

        assert 1 not in manager.active_tasks


class TestStatistics:
    """Tests for statistics and state management."""

    def test_get_statistics_includes_all_fields(self):
        """Test that get_statistics returns all expected fields."""
        manager = AutomationManager()
        manager.enable_building_automation(1)
        manager.enable_building_automation(2)
        manager.set_material_routing('iron', [1])
        manager.active_tasks[10] = {}

        stats = manager.get_statistics()

        assert stats['deliveries_completed'] == 0
        assert stats['collections_completed'] == 0
        assert stats['active_tasks'] == 1
        assert stats['buildings_automated'] == 2
        assert stats['material_routes'] == 1

    def test_save_state_captures_configuration(self):
        """Test that save_state captures configuration."""
        manager = AutomationManager()
        manager.enable_building_automation(1)
        manager.set_material_routing('iron', [1, 2])
        manager.stats['deliveries_completed'] = 5

        state = manager.save_state()

        assert 1 in state['building_automation']
        assert state['material_routing']['iron'] == [1, 2]
        assert state['stats']['deliveries_completed'] == 5

    def test_load_state_restores_configuration(self):
        """Test that load_state restores configuration."""
        manager = AutomationManager()
        state = {
            'building_automation': {1: {'enabled': True}},
            'material_routing': {'copper': [3, 4]},
            'stats': {
                'deliveries_completed': 10,
                'collections_completed': 5,
                'materials_delivered': 100.0,
                'materials_collected': 50.0
            }
        }

        manager.load_state(state)

        assert 1 in manager.building_automation
        assert manager.material_routing['copper'] == [3, 4]
        assert manager.stats['deliveries_completed'] == 10

    def test_load_state_clears_runtime_state(self):
        """Test that load_state clears runtime state."""
        manager = AutomationManager()
        manager.pending_tasks = [('task',)]
        manager.active_tasks = {1: {}}

        manager.load_state({})

        assert manager.pending_tasks == []
        assert manager.active_tasks == {}

    def test_repr_format(self):
        """Test string representation format."""
        manager = AutomationManager()
        manager.enable_building_automation(1)
        manager.set_material_routing('iron', [1])

        repr_str = repr(manager)

        assert 'AutomationManager' in repr_str
        assert '1 buildings automated' in repr_str
        assert '1 material routes' in repr_str
