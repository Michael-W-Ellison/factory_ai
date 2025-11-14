"""
Test Automation System

Tests the AutomationManager, material routing, auto-delivery,
auto-collection, and priority task system.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))


class MockWarehouse:
    """Mock warehouse for testing."""
    def __init__(self):
        self.materials = {
            'copper': 100.0,
            'plastic': 80.0,
            'iron': 150.0,
            'chemicals': 50.0
        }

    def get_material_amount(self, material_type):
        """Get amount of material in warehouse."""
        return self.materials.get(material_type, 0.0)

    def add_material(self, material_type, amount):
        """Add material to warehouse."""
        self.materials[material_type] = self.materials.get(material_type, 0.0) + amount

    def remove_material(self, material_type, amount):
        """Remove material from warehouse."""
        current = self.materials.get(material_type, 0.0)
        removed = min(amount, current)
        self.materials[material_type] = current - removed
        return removed


class MockBuilding:
    """Mock processing building for testing."""
    def __init__(self, building_id, accepts_materials=None):
        self.building_id = building_id
        self.input_material_types = accepts_materials or ['plastic', 'metal']
        self.max_input_queue = 1000.0
        self.max_output_queue = 1000.0
        self.input_queue = []
        self.output_queue = []
        self.processing_current = None

    def get_current_input_weight(self):
        """Get total weight in input queue."""
        return sum(item['quantity'] for item in self.input_queue)

    def get_current_output_weight(self):
        """Get total weight in output queue."""
        return sum(item['quantity'] for item in self.output_queue)

    def add_to_input_queue(self, material_type, quantity):
        """Add material to input queue."""
        if material_type in self.input_material_types:
            current_input = self.get_current_input_weight()
            available_space = self.max_input_queue - current_input
            amount_to_add = min(quantity, available_space)

            if amount_to_add > 0:
                self.input_queue.append({
                    'material_type': material_type,
                    'quantity': amount_to_add
                })
            return amount_to_add
        return 0.0

    def add_to_output_queue(self, material_type, quantity):
        """Add material to output queue."""
        current_output = self.get_current_output_weight()
        available_space = self.max_output_queue - current_output
        amount_to_add = min(quantity, available_space)

        if amount_to_add > 0:
            self.output_queue.append({
                'material_type': material_type,
                'quantity': amount_to_add
            })
        return amount_to_add

    def can_start_manufacturing(self):
        """Check if can start processing."""
        return len(self.input_queue) > 0


def test_automation_manager_creation():
    """Test AutomationManager creation."""
    print("=" * 80)
    print("TEST 1: AutomationManager Creation")
    print("=" * 80)
    print()

    from src.systems.automation_manager import AutomationManager

    manager = AutomationManager()
    print(f"✓ Created: {manager}")

    # Check initial state
    assert len(manager.building_automation) == 0, "Should start with no automated buildings"
    assert len(manager.material_routing) == 0, "Should start with no material routes"
    assert len(manager.active_tasks) == 0, "Should start with no active tasks"
    print("✓ Initial state correct")

    # Check statistics
    stats = manager.get_statistics()
    print(f"✓ Statistics: {stats}")
    assert stats['buildings_automated'] == 0
    assert stats['active_tasks'] == 0

    print("\n✓ AutomationManager creation test PASSED\n")


def test_building_automation_enable():
    """Test enabling/disabling building automation."""
    print("=" * 80)
    print("TEST 2: Building Automation Enable/Disable")
    print("=" * 80)
    print()

    from src.systems.automation_manager import AutomationManager

    manager = AutomationManager()

    # Enable automation for building 1
    manager.enable_building_automation(1, auto_deliver=True, auto_collect=True)
    assert manager.is_automation_enabled(1), "Building 1 should be automated"
    print("✓ Enabled automation for building 1")

    # Enable automation for building 2 (only delivery)
    manager.enable_building_automation(2, auto_deliver=True, auto_collect=False)
    assert manager.is_automation_enabled(2), "Building 2 should be automated"
    print("✓ Enabled automation for building 2 (delivery only)")

    # Check settings
    settings1 = manager.building_automation[1]
    assert settings1['auto_deliver'] == True
    assert settings1['auto_collect'] == True
    print("✓ Building 1 settings correct")

    settings2 = manager.building_automation[2]
    assert settings2['auto_deliver'] == True
    assert settings2['auto_collect'] == False
    print("✓ Building 2 settings correct")

    # Disable automation
    manager.disable_building_automation(1)
    assert not manager.is_automation_enabled(1), "Building 1 should be disabled"
    print("✓ Disabled automation for building 1")

    # Statistics
    stats = manager.get_statistics()
    assert stats['buildings_automated'] == 1, f"Expected 1, got {stats['buildings_automated']}"
    print(f"✓ Statistics: {stats['buildings_automated']} buildings automated")

    print("\n✓ Building automation enable/disable test PASSED\n")


def test_material_routing():
    """Test material routing configuration."""
    print("=" * 80)
    print("TEST 3: Material Routing")
    print("=" * 80)
    print()

    from src.systems.automation_manager import AutomationManager

    manager = AutomationManager()

    # Set routing for plastic -> building 1, 2
    manager.set_material_routing('plastic', [1, 2])
    routing = manager.get_material_routing('plastic')
    assert routing == [1, 2], f"Expected [1, 2], got {routing}"
    print("✓ Set routing: plastic -> buildings 1, 2")

    # Set routing for metal -> building 3
    manager.set_material_routing('metal', [3])
    routing = manager.get_material_routing('metal')
    assert routing == [3]
    print("✓ Set routing: metal -> building 3")

    # Add preference
    manager.add_routing_preference('plastic', 3)
    routing = manager.get_material_routing('plastic')
    assert 3 in routing, "Building 3 should be in plastic routing"
    print("✓ Added building 3 to plastic routing")

    # Remove preference
    manager.remove_routing_preference('plastic', 2)
    routing = manager.get_material_routing('plastic')
    assert 2 not in routing, "Building 2 should not be in plastic routing"
    print("✓ Removed building 2 from plastic routing")

    # Check non-existent material
    routing = manager.get_material_routing('nonexistent')
    assert routing == [], "Should return empty list for unknown material"
    print("✓ Unknown material returns empty list")

    print("\n✓ Material routing test PASSED\n")


def test_output_collection_tasks():
    """Test auto-collection task generation."""
    print("=" * 80)
    print("TEST 4: Output Collection Tasks")
    print("=" * 80)
    print()

    from src.systems.automation_manager import AutomationManager, TaskPriority

    manager = AutomationManager()
    warehouse = MockWarehouse()

    # Create building with output
    building = MockBuilding(1, accepts_materials=['plastic', 'copper'])
    manager.enable_building_automation(1, auto_deliver=False, auto_collect=True)

    # Add materials to output queue (95% full - CRITICAL)
    building.add_to_output_queue('processed_plastic', 950.0)

    # Scan for tasks
    buildings_dict = {1: building}
    tasks = manager.scan_buildings(buildings_dict, warehouse)

    print(f"✓ Generated {len(tasks)} tasks")
    assert len(tasks) > 0, "Should generate collection task"

    priority, task_type, building_id, material_type, quantity = tasks[0]
    assert task_type == 'collect', f"Expected 'collect', got {task_type}"
    assert priority == TaskPriority.CRITICAL, f"Expected CRITICAL, got {priority}"
    assert building_id == 1
    print(f"✓ Task: {task_type} {quantity:.1f}kg of {material_type} from building {building_id}")
    print(f"  Priority: {priority.name}")

    # Test with 50% full (MEDIUM priority)
    building.output_queue.clear()
    building.add_to_output_queue('processed_plastic', 500.0)

    tasks = manager.scan_buildings(buildings_dict, warehouse)
    priority, task_type, _, _, _ = tasks[0]
    assert priority == TaskPriority.MEDIUM, f"Expected MEDIUM, got {priority}"
    print(f"✓ 50% full -> {priority.name} priority")

    print("\n✓ Output collection tasks test PASSED\n")


def test_material_delivery_tasks():
    """Test auto-delivery task generation."""
    print("=" * 80)
    print("TEST 5: Material Delivery Tasks")
    print("=" * 80)
    print()

    from src.systems.automation_manager import AutomationManager, TaskPriority

    manager = AutomationManager()
    warehouse = MockWarehouse()

    # Create building that needs materials
    building = MockBuilding(1, accepts_materials=['copper', 'plastic'])
    manager.enable_building_automation(1, auto_deliver=True, auto_collect=False)

    # Set material routing
    manager.set_material_routing('copper', [1])
    manager.set_material_routing('plastic', [1])

    # Scan for tasks (building has empty input queue)
    buildings_dict = {1: building}
    tasks = manager.scan_buildings(buildings_dict, warehouse)

    print(f"✓ Generated {len(tasks)} delivery tasks")
    assert len(tasks) >= 1, "Should generate delivery tasks"

    # Check first task
    priority, task_type, building_id, material_type, quantity = tasks[0]
    assert task_type == 'deliver', f"Expected 'deliver', got {task_type}"
    assert priority in [TaskPriority.HIGH, TaskPriority.MEDIUM], f"Unexpected priority: {priority}"
    assert building_id == 1
    assert material_type in ['copper', 'plastic']
    print(f"✓ Task: {task_type} {quantity:.1f}kg of {material_type} to building {building_id}")
    print(f"  Priority: {priority.name}")

    # Test with input queue partially full
    building.add_to_input_queue('copper', 400.0)
    tasks = manager.scan_buildings(buildings_dict, warehouse)
    print(f"✓ With 40% full input: generated {len(tasks)} tasks")

    print("\n✓ Material delivery tasks test PASSED\n")


def test_task_assignment():
    """Test robot task assignment."""
    print("=" * 80)
    print("TEST 6: Robot Task Assignment")
    print("=" * 80)
    print()

    from src.systems.automation_manager import AutomationManager

    manager = AutomationManager()
    warehouse = MockWarehouse()

    # Setup building with output to collect
    building = MockBuilding(1, accepts_materials=['copper'])
    building.add_to_output_queue('processed_copper', 800.0)
    manager.enable_building_automation(1, auto_deliver=True, auto_collect=True)

    buildings_dict = {1: building}

    # Get task for robot 1
    task = manager.get_next_task(
        robot_id=1,
        robot_position=(100, 100),
        buildings_dict=buildings_dict,
        warehouse=warehouse
    )

    assert task is not None, "Should assign a task"
    print(f"✓ Assigned task to robot 1:")
    print(f"  Type: {task['task_type']}")
    print(f"  Building: {task['building_id']}")
    print(f"  Material: {task['material_type']}")
    print(f"  Quantity: {task['quantity']:.1f}kg")
    print(f"  Priority: {task['priority'].name}")

    # Check active tasks
    assert 1 in manager.active_tasks, "Robot 1 should have active task"
    print("✓ Task marked as active")

    # Try to get another task for same robot (should return same task)
    task2 = manager.get_next_task(
        robot_id=1,
        robot_position=(100, 100),
        buildings_dict=buildings_dict,
        warehouse=warehouse
    )
    assert task2 == task, "Should return same task for robot with active task"
    print("✓ Robot with active task gets same task")

    # Complete task
    manager.complete_task(1, 'collect', 'processed_copper', 800.0)
    assert 1 not in manager.active_tasks, "Robot 1 should not have active task"
    print("✓ Task completed and removed")

    # Check statistics
    stats = manager.get_statistics()
    assert stats['collections_completed'] == 1
    assert stats['materials_collected'] == 800.0
    print(f"✓ Statistics updated: {stats['collections_completed']} collections, {stats['materials_collected']:.1f}kg collected")

    print("\n✓ Robot task assignment test PASSED\n")


def test_priority_system():
    """Test task priority system."""
    print("=" * 80)
    print("TEST 7: Task Priority System")
    print("=" * 80)
    print()

    from src.systems.automation_manager import AutomationManager, TaskPriority

    manager = AutomationManager()
    warehouse = MockWarehouse()

    # Create multiple buildings with different urgencies
    building1 = MockBuilding(1, accepts_materials=['copper'])
    building1.add_to_output_queue('processed_copper', 950.0)  # CRITICAL (95% full)

    building2 = MockBuilding(2, accepts_materials=['plastic'])
    building2.add_to_output_queue('processed_plastic', 500.0)  # MEDIUM (50% full)

    building3 = MockBuilding(3, accepts_materials=['iron'])
    building3.add_to_output_queue('processed_iron', 200.0)  # LOW (20% full)

    # Enable automation
    for bid in [1, 2, 3]:
        manager.enable_building_automation(bid, auto_deliver=False, auto_collect=True)

    buildings_dict = {1: building1, 2: building2, 3: building3}

    # Scan for tasks
    tasks = manager.scan_buildings(buildings_dict, warehouse)

    print(f"✓ Generated {len(tasks)} tasks from 3 buildings")

    # Verify tasks are sorted by priority
    priorities = [task[0] for task in tasks]
    print("✓ Task priorities:")
    for i, (priority, task_type, building_id, material, qty) in enumerate(tasks):
        print(f"  {i+1}. Building {building_id}: {priority.name} - {task_type} {qty:.0f}kg {material}")

    # First task should be CRITICAL
    assert priorities[0] == TaskPriority.CRITICAL, f"First task should be CRITICAL, got {priorities[0]}"
    print("✓ Highest priority task is CRITICAL")

    # Verify sorting (lower enum value = higher priority)
    for i in range(len(priorities) - 1):
        assert priorities[i].value <= priorities[i+1].value, "Tasks should be sorted by priority"
    print("✓ Tasks correctly sorted by priority")

    print("\n✓ Task priority system test PASSED\n")


def test_save_load_state():
    """Test save/load automation state."""
    print("=" * 80)
    print("TEST 8: Save/Load State")
    print("=" * 80)
    print()

    from src.systems.automation_manager import AutomationManager

    manager = AutomationManager()

    # Configure automation
    manager.enable_building_automation(1, auto_deliver=True, auto_collect=True)
    manager.enable_building_automation(2, auto_deliver=True, auto_collect=False)
    manager.set_material_routing('copper', [1, 2])
    manager.set_material_routing('plastic', [3])

    # Update stats
    manager.complete_task(1, 'deliver', 'copper', 50.0)
    manager.complete_task(2, 'collect', 'processed_plastic', 100.0)

    # Save state
    state = manager.save_state()
    print(f"✓ Saved state: {len(state)} keys")

    # Create new manager and load state
    manager2 = AutomationManager()
    manager2.load_state(state)

    # Verify automation settings
    assert manager2.is_automation_enabled(1), "Building 1 should be automated"
    assert manager2.is_automation_enabled(2), "Building 2 should be automated"
    print("✓ Building automation settings restored")

    # Verify material routing
    routing = manager2.get_material_routing('copper')
    assert routing == [1, 2], f"Expected [1, 2], got {routing}"
    print("✓ Material routing restored")

    # Verify statistics
    stats = manager2.get_statistics()
    assert stats['deliveries_completed'] == 1
    assert stats['collections_completed'] == 1
    assert stats['materials_delivered'] == 50.0
    assert stats['materials_collected'] == 100.0
    print("✓ Statistics restored")

    print("\n✓ Save/load state test PASSED\n")


def run_all_tests():
    """Run all automation tests."""
    print("\n")
    print("=" * 80)
    print("AUTOMATION SYSTEM TEST SUITE")
    print("=" * 80)
    print("\n")

    try:
        test_automation_manager_creation()
        test_building_automation_enable()
        test_material_routing()
        test_output_collection_tasks()
        test_material_delivery_tasks()
        test_task_assignment()
        test_priority_system()
        test_save_load_state()

        print("=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
        print()
        print("Summary:")
        print("  ✓ AutomationManager (creation, enable/disable)")
        print("  ✓ Material routing (set, add, remove preferences)")
        print("  ✓ Output collection (CRITICAL/HIGH/MEDIUM/LOW priorities)")
        print("  ✓ Material delivery (warehouse -> buildings)")
        print("  ✓ Robot task assignment (next task, completion)")
        print("  ✓ Priority system (CRITICAL > HIGH > MEDIUM > LOW)")
        print("  ✓ Save/load state (automation settings, routing, stats)")
        print()
        print("Phase 5.4-5.5 Complete:")
        print("  ✓ Processing queue management")
        print("  ✓ Auto-delivery system with priorities")
        print("  ✓ Auto-collection system with priorities")
        print("  ✓ Material routing preferences")
        print("  ✓ Robot task prioritization")
        print()

        return True

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ TEST ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
