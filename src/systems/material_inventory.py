"""
Material Inventory Manager - tracks materials by source for inspection system.

Handles:
- Material source tagging (legal vs illegal)
- Inventory tracking by source
- Illegal material detection for inspections
- Material disposal/hiding strategies
"""

from enum import Enum
from typing import Dict, List, Tuple
from collections import defaultdict


class MaterialSource(Enum):
    """Material source types (legal vs illegal)."""
    # Legal sources
    LANDFILL = "landfill"  # Materials from landfill
    DECREPIT_HOUSE = "decrepit_house"  # Materials from decrepit/abandoned houses
    SCRAP_VEHICLE = "scrap_vehicle"  # Materials from scrap/abandoned vehicles
    PURCHASED = "purchased"  # Materials bought from market
    PROCESSED = "processed"  # Materials processed from raw materials (removes illegal tag)

    # Illegal sources
    LIVABLE_HOUSE = "livable_house"  # Materials from occupied houses
    WORKING_VEHICLE = "working_vehicle"  # Materials from functional vehicles
    FENCE = "fence"  # Materials from chain link fences
    TREE = "tree"  # Materials from cutting down trees (illegal without permit)

    # Unknown
    UNKNOWN = "unknown"  # Source not tracked

    def is_legal(self) -> bool:
        """Check if this source is legal."""
        legal_sources = {
            MaterialSource.LANDFILL,
            MaterialSource.DECREPIT_HOUSE,
            MaterialSource.SCRAP_VEHICLE,
            MaterialSource.PURCHASED,
            MaterialSource.PROCESSED
        }
        return self in legal_sources

    def is_illegal(self) -> bool:
        """Check if this source is illegal."""
        return not self.is_legal() and self != MaterialSource.UNKNOWN


class MaterialInventory:
    """
    Tracks materials in inventory by source.

    Integrates with inspection system to detect illegal materials.
    """

    def __init__(self):
        """Initialize material inventory."""
        # Materials by source: {source: {material_type: quantity}}
        self.materials_by_source: Dict[MaterialSource, Dict[str, float]] = defaultdict(lambda: defaultdict(float))

        # Total materials: {material_type: quantity}
        self.total_materials: Dict[str, float] = defaultdict(float)

        # Illegal material threshold for suspicion
        # Large amounts of valuable materials (copper, electronics) are suspicious
        self.suspicious_thresholds = {
            'copper': 500,  # >500 copper is suspicious
            'electronics': 300,  # >300 electronics is suspicious
            'metal': 1000,  # >1000 metal is suspicious
        }

    def add_material(self, material_type: str, quantity: float, source: MaterialSource):
        """
        Add material to inventory with source tracking.

        Args:
            material_type (str): Type of material (e.g., 'plastic', 'metal')
            quantity (float): Amount to add
            source (MaterialSource): Source of the material
        """
        self.materials_by_source[source][material_type] += quantity
        self.total_materials[material_type] += quantity

    def remove_material(self, material_type: str, quantity: float, prefer_illegal: bool = False) -> bool:
        """
        Remove material from inventory.

        Args:
            material_type (str): Type of material
            quantity (float): Amount to remove
            prefer_illegal (bool): If True, remove illegal materials first

        Returns:
            bool: True if successful, False if not enough material
        """
        if self.total_materials[material_type] < quantity:
            return False

        # Determine removal order (illegal first if prefer_illegal)
        sources = list(self.materials_by_source.keys())
        if prefer_illegal:
            # Sort so illegal sources come first
            sources.sort(key=lambda s: (not s.is_illegal(), s.value))

        remaining = quantity
        for source in sources:
            if remaining <= 0:
                break

            available = self.materials_by_source[source][material_type]
            if available > 0:
                take = min(available, remaining)
                self.materials_by_source[source][material_type] -= take
                remaining -= take

        self.total_materials[material_type] -= quantity
        return True

    def get_illegal_materials(self) -> Dict[str, float]:
        """
        Get all illegal materials in inventory.

        Returns:
            dict: {material_type: quantity} of illegal materials
        """
        illegal_materials = defaultdict(float)

        for source, materials in self.materials_by_source.items():
            if source.is_illegal():
                for material_type, quantity in materials.items():
                    illegal_materials[material_type] += quantity

        return dict(illegal_materials)

    def get_illegal_material_count(self) -> int:
        """Get total count of illegal material units."""
        illegal = self.get_illegal_materials()
        return int(sum(illegal.values()))

    def get_illegal_material_value(self) -> float:
        """
        Get estimated value of illegal materials.

        Uses simplified pricing.
        """
        illegal = self.get_illegal_materials()

        # Simplified material values
        material_values = {
            'plastic': 1.0,
            'metal': 2.0,
            'glass': 1.5,
            'paper': 0.5,
            'electronics': 10.0,
            'copper': 15.0,
            'rubber': 2.0,
        }

        total_value = 0
        for material_type, quantity in illegal.items():
            value_per_unit = material_values.get(material_type, 1.0)
            total_value += quantity * value_per_unit

        return total_value

    def has_suspicious_amounts(self) -> List[str]:
        """
        Check if inventory has suspicious amounts of valuable materials.

        Returns:
            list: List of material types with suspicious amounts
        """
        suspicious = []

        for material_type, threshold in self.suspicious_thresholds.items():
            if self.total_materials[material_type] > threshold:
                suspicious.append(material_type)

        return suspicious

    def sell_all_illegal_materials(self, resource_manager) -> float:
        """
        Sell all illegal materials (emergency preparation for inspection).

        Args:
            resource_manager: ResourceManager instance

        Returns:
            float: Amount of money earned
        """
        illegal = self.get_illegal_materials()
        total_earned = 0

        # Sell at discounted price (70% of value) due to suspicious nature
        material_values = {
            'plastic': 1.0 * 0.7,
            'metal': 2.0 * 0.7,
            'glass': 1.5 * 0.7,
            'paper': 0.5 * 0.7,
            'electronics': 10.0 * 0.7,
            'copper': 15.0 * 0.7,
            'rubber': 2.0 * 0.7,
        }

        for material_type, quantity in illegal.items():
            value_per_unit = material_values.get(material_type, 1.0)
            earned = quantity * value_per_unit
            total_earned += earned

            # Remove the material
            self.remove_material(material_type, quantity, prefer_illegal=True)

        # Add money to resources
        resource_manager.modify_money(total_earned)

        return total_earned

    def process_materials_to_legal(self, material_type: str, quantity: float) -> bool:
        """
        Process materials into components, removing illegal tag.

        This represents breaking down materials into base components,
        making them untraceable.

        Args:
            material_type (str): Type of material to process
            quantity (float): Amount to process

        Returns:
            bool: True if successful
        """
        if self.total_materials[material_type] < quantity:
            return False

        # Remove from current sources
        if not self.remove_material(material_type, quantity, prefer_illegal=True):
            return False

        # Re-add as processed (legal) source
        # Processing has 10% loss
        processed_amount = quantity * 0.9
        self.add_material(material_type, processed_amount, MaterialSource.PROCESSED)

        return True

    def get_inventory_summary(self) -> Dict:
        """
        Get summary of inventory for UI display.

        Returns:
            dict: Inventory statistics
        """
        illegal_materials = self.get_illegal_materials()
        suspicious = self.has_suspicious_amounts()

        return {
            'total_materials': dict(self.total_materials),
            'illegal_materials': illegal_materials,
            'illegal_count': self.get_illegal_material_count(),
            'illegal_value': self.get_illegal_material_value(),
            'suspicious_amounts': suspicious,
            'has_illegal': len(illegal_materials) > 0,
            'is_suspicious': len(suspicious) > 0
        }

    def clear_all(self):
        """Clear all materials (for testing)."""
        self.materials_by_source.clear()
        self.total_materials.clear()

    def __repr__(self):
        """String representation for debugging."""
        illegal_count = self.get_illegal_material_count()
        total_count = int(sum(self.total_materials.values()))
        return f"MaterialInventory(total={total_count}, illegal={illegal_count})"
