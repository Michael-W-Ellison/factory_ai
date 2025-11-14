"""
AutomationManager - Manages automated material delivery and collection.

Handles auto-delivery of materials to processing buildings, auto-collection
of outputs, material routing preferences, and robot task prioritization.
"""

from typing import Dict, List, Optional, Tuple, Set
from enum import Enum, auto


class TaskPriority(Enum):
    """Priority levels for automated tasks."""
    CRITICAL = 1   # Output queue nearly full, must collect
    HIGH = 2       # Building ready for processing, needs materials
    MEDIUM = 3     # Building has some materials, could use more
    LOW = 4        # Building has materials, not urgent
    IDLE = 5       # No urgent tasks


class AutomationManager:
    """
    Manages automated material delivery and collection for buildings.

    Coordinates robots to automatically:
    - Deliver materials from warehouse to processing buildings
    - Collect outputs from processing buildings to warehouse
    - Route specific materials to preferred buildings
    - Prioritize tasks based on urgency
    """

    def __init__(self):
        """Initialize the automation manager."""
        # Building automation settings: {building_id: AutomationSettings}
        self.building_automation = {}

        # Material routing: {material_type: [building_ids]} (preferred buildings)
        self.material_routing = {}

        # Task queue: [(priority, task_type, building_id, material_type, quantity)]
        self.pending_tasks = []

        # Active tasks: {robot_id: task_info}
        self.active_tasks = {}

        # Statistics
        self.stats = {
            'deliveries_completed': 0,
            'collections_completed': 0,
            'materials_delivered': 0.0,
            'materials_collected': 0.0
        }

    def enable_building_automation(self, building_id: int,
                                   auto_deliver: bool = True,
                                   auto_collect: bool = True):
        """
        Enable automation for a building.

        Args:
            building_id (int): Building identifier
            auto_deliver (bool): Enable auto-delivery of materials
            auto_collect (bool): Enable auto-collection of outputs
        """
        self.building_automation[building_id] = {
            'auto_deliver': auto_deliver,
            'auto_collect': auto_collect,
            'enabled': True,
            'priority_boost': 0  # Can be adjusted per building
        }

    def disable_building_automation(self, building_id: int):
        """
        Disable automation for a building.

        Args:
            building_id (int): Building identifier
        """
        if building_id in self.building_automation:
            self.building_automation[building_id]['enabled'] = False

    def is_automation_enabled(self, building_id: int) -> bool:
        """
        Check if automation is enabled for a building.

        Args:
            building_id (int): Building identifier

        Returns:
            bool: True if automation enabled
        """
        settings = self.building_automation.get(building_id)
        return settings is not None and settings.get('enabled', False)

    def set_material_routing(self, material_type: str, building_ids: List[int]):
        """
        Set preferred buildings for a material type.

        Args:
            material_type (str): Material type identifier
            building_ids (list): List of preferred building IDs (in priority order)
        """
        self.material_routing[material_type] = building_ids

    def get_material_routing(self, material_type: str) -> List[int]:
        """
        Get preferred buildings for a material type.

        Args:
            material_type (str): Material type identifier

        Returns:
            list: Preferred building IDs (empty if no routing set)
        """
        return self.material_routing.get(material_type, [])

    def add_routing_preference(self, material_type: str, building_id: int):
        """
        Add a building to the routing preference for a material.

        Args:
            material_type (str): Material type identifier
            building_id (int): Building to add to routing
        """
        if material_type not in self.material_routing:
            self.material_routing[material_type] = []

        if building_id not in self.material_routing[material_type]:
            self.material_routing[material_type].append(building_id)

    def remove_routing_preference(self, material_type: str, building_id: int):
        """
        Remove a building from routing preference.

        Args:
            material_type (str): Material type identifier
            building_id (int): Building to remove
        """
        if material_type in self.material_routing:
            if building_id in self.material_routing[material_type]:
                self.material_routing[material_type].remove(building_id)

    def scan_buildings(self, buildings_dict: Dict, warehouse) -> List[Tuple]:
        """
        Scan all buildings and generate automation tasks.

        Args:
            buildings_dict (dict): Dictionary of building_id -> building object
            warehouse: Warehouse object with material inventory

        Returns:
            list: List of tasks (priority, task_type, building_id, material_type, quantity)
        """
        tasks = []

        for building_id, building in buildings_dict.items():
            # Check if automation enabled
            if not self.is_automation_enabled(building_id):
                continue

            settings = self.building_automation[building_id]

            # Check for output collection (CRITICAL if queue nearly full)
            if settings.get('auto_collect', False):
                output_tasks = self._check_output_collection(building, building_id)
                tasks.extend(output_tasks)

            # Check for material delivery
            if settings.get('auto_deliver', False):
                delivery_tasks = self._check_material_delivery(building, building_id, warehouse)
                tasks.extend(delivery_tasks)

        # Sort by priority
        tasks.sort(key=lambda x: x[0].value)

        return tasks

    def _check_output_collection(self, building, building_id: int) -> List[Tuple]:
        """
        Check if building needs output collection.

        Args:
            building: Building object
            building_id (int): Building identifier

        Returns:
            list: Collection tasks
        """
        tasks = []

        # Check if building has output queue
        if not hasattr(building, 'output_queue'):
            return tasks

        if not hasattr(building, 'max_output_queue'):
            return tasks

        # Calculate output fullness
        output_weight = building.get_current_output_weight()
        max_output = building.max_output_queue
        fullness = output_weight / max_output if max_output > 0 else 0

        # Determine priority based on fullness
        if fullness > 0.9:
            priority = TaskPriority.CRITICAL
        elif fullness > 0.7:
            priority = TaskPriority.HIGH
        elif fullness > 0.4:
            priority = TaskPriority.MEDIUM
        elif fullness > 0.1:
            priority = TaskPriority.LOW
        else:
            return tasks  # Not worth collecting yet

        # Create collection task for each material in output queue
        for item in building.output_queue:
            material_type = item['material_type']
            quantity = item['quantity']

            tasks.append((
                priority,
                'collect',
                building_id,
                material_type,
                quantity
            ))

        return tasks

    def _check_material_delivery(self, building, building_id: int, warehouse) -> List[Tuple]:
        """
        Check if building needs material delivery.

        Args:
            building: Building object
            building_id (int): Building identifier
            warehouse: Warehouse with materials

        Returns:
            list: Delivery tasks
        """
        tasks = []

        # Check if building accepts materials
        if not hasattr(building, 'input_material_types'):
            return tasks

        if not hasattr(building, 'max_input_queue'):
            return tasks

        # Calculate input capacity
        input_weight = building.get_current_input_weight()
        max_input = building.max_input_queue
        available_space = max_input - input_weight

        if available_space < 10:  # Less than 10kg space
            return tasks  # Input queue nearly full

        # Check if building can start processing
        can_process = False
        if hasattr(building, 'can_start_manufacturing'):
            can_process = building.can_start_manufacturing()
        elif hasattr(building, 'processing_current'):
            can_process = (building.processing_current is None and len(building.input_queue) > 0)

        # Check each material type the building accepts
        for material_type in building.input_material_types:
            # Check if this building is preferred for this material
            preferred_buildings = self.get_material_routing(material_type)
            is_preferred = (not preferred_buildings) or (building_id in preferred_buildings)

            if not is_preferred:
                continue  # Skip, not preferred building

            # Check warehouse inventory
            if warehouse:
                available_in_warehouse = warehouse.get_material_amount(material_type)
                if available_in_warehouse < 1.0:  # Less than 1kg available
                    continue

                # Determine how much to deliver
                delivery_amount = min(available_in_warehouse, available_space, 50.0)  # Max 50kg per task

                # Determine priority
                if not can_process:
                    priority = TaskPriority.HIGH  # Building needs materials to start
                elif input_weight < max_input * 0.3:
                    priority = TaskPriority.MEDIUM  # Running low
                else:
                    priority = TaskPriority.LOW  # Has materials

                tasks.append((
                    priority,
                    'deliver',
                    building_id,
                    material_type,
                    delivery_amount
                ))

        return tasks

    def get_next_task(self, robot_id: int, robot_position: Tuple[float, float],
                     buildings_dict: Dict, warehouse) -> Optional[Dict]:
        """
        Get the next automation task for a robot.

        Args:
            robot_id (int): Robot identifier
            robot_position (tuple): Robot's current (x, y) position
            buildings_dict (dict): Dictionary of buildings
            warehouse: Warehouse object

        Returns:
            dict: Task info or None if no tasks available
        """
        # Check if robot already has an active task
        if robot_id in self.active_tasks:
            return self.active_tasks[robot_id]

        # Scan buildings for tasks
        tasks = self.scan_buildings(buildings_dict, warehouse)

        if not tasks:
            return None

        # Get highest priority task
        priority, task_type, building_id, material_type, quantity = tasks[0]

        # Create task
        task = {
            'robot_id': robot_id,
            'task_type': task_type,
            'building_id': building_id,
            'material_type': material_type,
            'quantity': quantity,
            'priority': priority,
            'status': 'pending'
        }

        # Mark as active
        self.active_tasks[robot_id] = task

        return task

    def complete_task(self, robot_id: int, task_type: str, material_type: str, quantity: float):
        """
        Mark a task as completed and update statistics.

        Args:
            robot_id (int): Robot that completed the task
            task_type (str): 'deliver' or 'collect'
            material_type (str): Material type
            quantity (float): Amount processed
        """
        # Remove from active tasks
        if robot_id in self.active_tasks:
            del self.active_tasks[robot_id]

        # Update statistics
        if task_type == 'deliver':
            self.stats['deliveries_completed'] += 1
            self.stats['materials_delivered'] += quantity
        elif task_type == 'collect':
            self.stats['collections_completed'] += 1
            self.stats['materials_collected'] += quantity

    def cancel_task(self, robot_id: int):
        """
        Cancel a robot's active task.

        Args:
            robot_id (int): Robot identifier
        """
        if robot_id in self.active_tasks:
            del self.active_tasks[robot_id]

    def get_statistics(self) -> Dict:
        """
        Get automation statistics.

        Returns:
            dict: Statistics
        """
        return {
            **self.stats,
            'active_tasks': len(self.active_tasks),
            'buildings_automated': sum(1 for s in self.building_automation.values() if s.get('enabled', False)),
            'material_routes': len(self.material_routing)
        }

    def save_state(self) -> Dict:
        """
        Save automation manager state.

        Returns:
            dict: Serialized state
        """
        return {
            'building_automation': self.building_automation,
            'material_routing': self.material_routing,
            'stats': self.stats
        }

    def load_state(self, state: Dict):
        """
        Load automation manager state.

        Args:
            state (dict): Serialized state
        """
        self.building_automation = state.get('building_automation', {})
        self.material_routing = state.get('material_routing', {})
        self.stats = state.get('stats', {
            'deliveries_completed': 0,
            'collections_completed': 0,
            'materials_delivered': 0.0,
            'materials_collected': 0.0
        })

        # Clear runtime state
        self.pending_tasks = []
        self.active_tasks = {}

    def __repr__(self):
        """String representation for debugging."""
        automated = sum(1 for s in self.building_automation.values() if s.get('enabled', False))
        active = len(self.active_tasks)
        routes = len(self.material_routing)
        return f"AutomationManager({automated} buildings automated, {active} active tasks, {routes} material routes)"
