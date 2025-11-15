"""
ComponentManager - Manages component inventory and manufacturing.

Handles component recipes, production tracking, and integration with
the material/resource systems.
"""

import json
import os
from typing import Dict, List, Optional, Tuple


class ComponentManager:
    """
    Manages manufactured components in the game.

    Components are high-value items manufactured from processed materials.
    Used for robot upgrades, research requirements, and advanced building construction.
    """

    def __init__(self):
        """Initialize the component manager."""
        # Load component definitions
        self.component_definitions = self._load_component_definitions()

        # Component inventory: {component_type: {quality: quantity}}
        self.inventory = {}

        # Manufacturing tracking: {building_id: {component_type, progress, etc.}}
        self.active_manufacturing = {}

    def _load_component_definitions(self) -> Dict:
        """
        Load component definitions from JSON file.

        Returns:
            dict: Component definitions
        """
        json_path = os.path.join('data', 'components.json')
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                data = json.load(f)
                return data.get('components', {})
        else:
            print(f"Warning: {json_path} not found, using empty component definitions")
            return {}

    def get_component_definition(self, component_type: str) -> Optional[Dict]:
        """
        Get the definition for a component type.

        Args:
            component_type (str): Component type identifier

        Returns:
            dict: Component definition or None if not found
        """
        return self.component_definitions.get(component_type)

    def get_recipe(self, component_type: str) -> Optional[Dict[str, float]]:
        """
        Get the recipe (material requirements) for a component.

        Args:
            component_type (str): Component type identifier

        Returns:
            dict: Material requirements {material_type: quantity} or None
        """
        definition = self.get_component_definition(component_type)
        if definition:
            return definition.get('recipe', {})
        return None

    def get_processing_time(self, component_type: str) -> float:
        """
        Get the manufacturing time for a component.

        Args:
            component_type (str): Component type identifier

        Returns:
            float: Processing time in seconds (default 10.0)
        """
        definition = self.get_component_definition(component_type)
        if definition:
            return definition.get('processing_time', 10.0)
        return 10.0

    def requires_research(self, component_type: str) -> Optional[str]:
        """
        Check if component requires research to unlock.

        Args:
            component_type (str): Component type identifier

        Returns:
            str: Research requirement or None if no requirement
        """
        definition = self.get_component_definition(component_type)
        if definition:
            return definition.get('requires_research')
        return None

    def is_unlocked(self, component_type: str, research_manager) -> bool:
        """
        Check if component is unlocked (research complete).

        Args:
            component_type (str): Component type identifier
            research_manager: ResearchManager instance

        Returns:
            bool: True if component is unlocked
        """
        research_req = self.requires_research(component_type)
        if research_req is None:
            return True  # No research required

        # Check if research is completed
        if research_manager:
            return research_manager.is_completed(research_req)
        return False

    def add_component(self, component_type: str, quality: str, quantity: float) -> bool:
        """
        Add components to inventory.

        Args:
            component_type (str): Component type identifier
            quality (str): Quality tier (low, medium, high)
            quantity (float): Number of units to add

        Returns:
            bool: True if added successfully
        """
        if component_type not in self.component_definitions:
            print(f"Warning: Unknown component type: {component_type}")
            return False

        # Initialize component entry if needed
        if component_type not in self.inventory:
            self.inventory[component_type] = {}

        # Add to inventory
        current = self.inventory[component_type].get(quality, 0.0)
        self.inventory[component_type][quality] = current + quantity

        return True

    def remove_component(self, component_type: str, quality: str, quantity: float) -> bool:
        """
        Remove components from inventory.

        Args:
            component_type (str): Component type identifier
            quality (str): Quality tier
            quantity (float): Number of units to remove

        Returns:
            bool: True if removed successfully, False if insufficient quantity
        """
        current = self.get_component_count(component_type, quality)
        if current < quantity:
            return False

        self.inventory[component_type][quality] = current - quantity

        # Clean up empty entries
        if self.inventory[component_type][quality] <= 0:
            del self.inventory[component_type][quality]
        if not self.inventory[component_type]:
            del self.inventory[component_type]

        return True

    def get_component_count(self, component_type: str, quality: str = None) -> float:
        """
        Get the count of components in inventory.

        Args:
            component_type (str): Component type identifier
            quality (str, optional): Specific quality tier. If None, returns total.

        Returns:
            float: Number of units in inventory
        """
        if component_type not in self.inventory:
            return 0.0

        if quality is not None:
            return self.inventory[component_type].get(quality, 0.0)
        else:
            # Return total across all qualities
            return sum(self.inventory[component_type].values())

    def get_total_value(self, component_type: str = None) -> float:
        """
        Get the total value of components in inventory.

        Args:
            component_type (str, optional): Specific component type. If None, returns total.

        Returns:
            float: Total value in dollars
        """
        total_value = 0.0

        if component_type is not None:
            # Single component type
            if component_type not in self.inventory:
                return 0.0

            definition = self.get_component_definition(component_type)
            if not definition:
                return 0.0

            base_value = definition.get('base_value', 0)

            for quality, quantity in self.inventory[component_type].items():
                quality_mult = self._get_quality_multiplier(quality)
                total_value += base_value * quality_mult * quantity
        else:
            # All components
            for comp_type, qualities in self.inventory.items():
                total_value += self.get_total_value(comp_type)

        return total_value

    def _get_quality_multiplier(self, quality: str) -> float:
        """
        Get value multiplier for quality tier.

        Args:
            quality (str): Quality tier

        Returns:
            float: Value multiplier
        """
        multipliers = {
            'low': 0.5,
            'medium': 1.0,
            'high': 2.0,
            'ultra': 5.0
        }
        return multipliers.get(quality, 1.0)

    def can_manufacture(self, component_type: str, resource_manager, quality: str = 'medium') -> Tuple[bool, str]:
        """
        Check if we can manufacture a component (have required materials).

        Args:
            component_type (str): Component type identifier
            resource_manager: ResourceManager instance
            quality (str): Desired quality tier

        Returns:
            tuple: (can_manufacture: bool, reason: str)
        """
        recipe = self.get_recipe(component_type)
        if not recipe:
            return False, f"No recipe found for {component_type}"

        # Check each material requirement
        for material_type, required_qty in recipe.items():
            # For materials, check if it's a component or base material
            if material_type in self.component_definitions:
                # It's a component requirement
                available = self.get_component_count(material_type, quality)
                if available < required_qty:
                    return False, f"Insufficient {material_type} ({available:.1f}/{required_qty:.1f})"
            else:
                # It's a base material requirement
                available = resource_manager.get_material_amount(material_type)
                if available < required_qty:
                    return False, f"Insufficient {material_type} ({available:.1f}/{required_qty:.1f})"

        return True, "Can manufacture"

    def start_manufacturing(self, building_id: int, component_type: str,
                          resource_manager, quality: str = 'medium') -> bool:
        """
        Start manufacturing a component at a building.

        Args:
            building_id (int): Building identifier
            component_type (str): Component type to manufacture
            resource_manager: ResourceManager instance
            quality (str): Desired quality tier

        Returns:
            bool: True if manufacturing started
        """
        # Check if can manufacture
        can_make, reason = self.can_manufacture(component_type, resource_manager, quality)
        if not can_make:
            print(f"Cannot start manufacturing {component_type}: {reason}")
            return False

        # Consume materials from resource manager
        recipe = self.get_recipe(component_type)
        for material_type, required_qty in recipe.items():
            if material_type in self.component_definitions:
                # Consume component
                self.remove_component(material_type, quality, required_qty)
            else:
                # Consume base material
                resource_manager.remove_material(material_type, required_qty)

        # Track manufacturing
        processing_time = self.get_processing_time(component_type)
        self.active_manufacturing[building_id] = {
            'component_type': component_type,
            'quality': quality,
            'progress': 0.0,
            'total_time': processing_time
        }

        print(f"Started manufacturing {component_type} ({quality}) at building {building_id}")
        return True

    def update(self, dt: float, buildings_dict: Dict):
        """
        Update manufacturing progress for all buildings.

        Args:
            dt (float): Delta time in seconds
            buildings_dict (dict): Dictionary of building_id -> building object
        """
        completed = []

        for building_id, manufacturing in self.active_manufacturing.items():
            # Check if building still exists
            if building_id not in buildings_dict:
                completed.append(building_id)
                continue

            building = buildings_dict[building_id]

            # Check if building is powered and active
            if not getattr(building, 'powered', True):
                continue  # Skip if unpowered

            # Update progress
            manufacturing['progress'] += dt

            # Check if complete
            if manufacturing['progress'] >= manufacturing['total_time']:
                component_type = manufacturing['component_type']
                quality = manufacturing['quality']

                # Add completed component to inventory
                self.add_component(component_type, quality, 1.0)

                print(f"✓ Completed manufacturing: {component_type} ({quality})")
                completed.append(building_id)

        # Remove completed manufacturing
        for building_id in completed:
            del self.active_manufacturing[building_id]

    def get_inventory_summary(self) -> List[Dict]:
        """
        Get a summary of component inventory.

        Returns:
            list: List of inventory entries with details
        """
        summary = []

        for component_type, qualities in self.inventory.items():
            definition = self.get_component_definition(component_type)
            name = definition.get('name', component_type) if definition else component_type
            base_value = definition.get('base_value', 0) if definition else 0

            for quality, quantity in qualities.items():
                if quantity > 0:
                    quality_mult = self._get_quality_multiplier(quality)
                    value = base_value * quality_mult * quantity

                    summary.append({
                        'component_type': component_type,
                        'name': name,
                        'quality': quality,
                        'quantity': quantity,
                        'unit_value': base_value * quality_mult,
                        'total_value': value
                    })

        return summary

    def save_state(self) -> Dict:
        """
        Save component manager state for serialization.

        Returns:
            dict: Serialized state
        """
        return {
            'inventory': self.inventory,
            'active_manufacturing': self.active_manufacturing
        }

    def load_state(self, state: Dict):
        """
        Load component manager state from serialized data.

        Args:
            state (dict): Serialized state
        """
        self.inventory = state.get('inventory', {})
        self.active_manufacturing = state.get('active_manufacturing', {})

    def __repr__(self):
        """String representation for debugging."""
        component_count = sum(len(qualities) for qualities in self.inventory.values())
        total_value = self.get_total_value()
        active = len(self.active_manufacturing)
        return f"ComponentManager({component_count} types, ${total_value:.0f} value, {active} manufacturing)"
