"""
ResourceManager - tracks materials, money, and resources.

Provides:
- Material storage and tracking
- Money management
- Material selling with market prices
- Statistics tracking
"""

from typing import Dict, Optional, Any, TYPE_CHECKING

from src.core.logger import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from src.systems.material_inventory import MaterialInventory, MaterialSource


class ResourceManager:
    """
    Manages the player's resources including materials and money.

    This tracks all materials collected and processed, as well as money earned.
    """

    def __init__(self) -> None:
        """Initialize the resource manager."""
        import random
        self._random = random.Random()

        # Materials stored in the factory (material_type -> quantity in kg)
        self.stored_materials: Dict[str, float] = {}

        # Money
        self.money = 1000.0  # Starting money in $

        # Statistics
        self.total_materials_collected = 0.0  # Total kg collected all-time
        self.total_money_earned = 0.0  # Total money earned all-time

        # Base material values ($ per kg)
        self.base_material_values: Dict[str, float] = {
            'plastic': 0.50,
            'metal': 1.20,
            'glass': 0.30,
            'paper': 0.20,
            'rubber': 0.80,
            'organic': 0.10,
            'wood': 0.40,
            'electronic': 2.50,
        }

        # Current material values (fluctuate around base)
        self.material_values: Dict[str, float] = self.base_material_values.copy()

        # Market price fluctuation settings
        self._market_timer = 0.0
        self._market_update_interval = 60.0  # Update prices every game minute
        self._price_fluctuation_range = 0.15  # +/- 15% fluctuation

        # Decay settings for organic materials
        self._decay_timer = 0.0
        self._decay_interval = 300.0  # Check decay every 5 game minutes
        self._organic_decay_rate = 0.001  # 0.1% per check
        self._decayable_materials = {'organic', 'wood', 'paper'}

    def deposit_materials(
        self,
        materials_dict: Dict[str, float],
        sources_dict: Optional[Dict[str, 'MaterialSource']] = None,
        material_inventory: Optional['MaterialInventory'] = None
    ) -> float:
        """
        Deposit materials into storage (e.g., from a robot's inventory).

        Args:
            materials_dict (dict): Dictionary of material_type -> quantity
            sources_dict (dict): Dictionary of material_type -> MaterialSource (optional)
            material_inventory (MaterialInventory): MaterialInventory to track sources (optional)

        Returns:
            float: Total quantity deposited
        """
        from src.systems.material_inventory import MaterialSource

        total_deposited = 0.0

        for material_type, quantity in materials_dict.items():
            if quantity > 0:
                # Add to storage
                if material_type not in self.stored_materials:
                    self.stored_materials[material_type] = 0.0
                self.stored_materials[material_type] += quantity

                # Add to material inventory with source tracking (if provided)
                if material_inventory is not None:
                    # Get source for this material, default to LANDFILL if not specified
                    source = MaterialSource.LANDFILL
                    if sources_dict and material_type in sources_dict:
                        source = sources_dict[material_type]
                    material_inventory.add_material(material_type, quantity, source)

                # Update statistics
                total_deposited += quantity
                self.total_materials_collected += quantity

                logger.debug(f"Deposited {quantity:.1f}kg of {material_type}")

        return total_deposited

    def sell_material(self, material_type: str, quantity: float) -> float:
        """
        Sell a specific material for money.

        Args:
            material_type (str): Type of material to sell
            quantity (float): Amount to sell in kg

        Returns:
            float: Money earned, or 0 if not enough material
        """
        # Check if we have enough
        current_quantity = self.stored_materials.get(material_type, 0)
        if current_quantity < quantity:
            logger.warning(f"Not enough {material_type} to sell (have {current_quantity:.1f}kg, need {quantity:.1f}kg)")
            return 0.0

        # Calculate value
        value_per_kg = self.material_values.get(material_type, 0.5)
        money_earned = quantity * value_per_kg

        # Remove from storage
        self.stored_materials[material_type] -= quantity

        # Add money
        self.money += money_earned
        self.total_money_earned += money_earned

        logger.info(f"Sold {quantity:.1f}kg of {material_type} for ${money_earned:.2f}")
        return money_earned

    def sell_all_materials(self) -> float:
        """
        Sell all stored materials.

        Returns:
            float: Total money earned
        """
        total_earned = 0.0

        # Make a copy to iterate over (since we're modifying the dict)
        materials_to_sell = list(self.stored_materials.items())

        for material_type, quantity in materials_to_sell:
            if quantity > 0:
                earned = self.sell_material(material_type, quantity)
                total_earned += earned

        return total_earned

    def get_material_value(self, material_type: str, quantity: float) -> float:
        """
        Calculate the value of a material without selling it.

        Args:
            material_type (str): Type of material
            quantity (float): Amount in kg

        Returns:
            float: Value in $
        """
        value_per_kg = self.material_values.get(material_type, 0.5)
        return quantity * value_per_kg

    def get_total_stored_value(self) -> float:
        """
        Calculate the total value of all stored materials.

        Returns:
            float: Total value in $
        """
        total_value = 0.0
        for material_type, quantity in self.stored_materials.items():
            total_value += self.get_material_value(material_type, quantity)
        return total_value

    def modify_money(self, amount: float) -> None:
        """
        Modify the player's money (add or subtract).

        Args:
            amount (float): Amount to add (positive) or subtract (negative)
        """
        self.money += amount
        if amount > 0:
            self.total_money_earned += amount

    def get_material_quantity(self, material_type: str) -> float:
        """
        Get the quantity of a specific material in storage.

        Args:
            material_type (str): Type of material

        Returns:
            float: Quantity in kg
        """
        return self.stored_materials.get(material_type, 0.0)

    def get_total_stored_weight(self) -> float:
        """
        Get the total weight of all stored materials.

        Returns:
            float: Total weight in kg
        """
        return sum(self.stored_materials.values())

    def update(self, dt: float) -> None:
        """
        Update resource manager state.

        Handles market price fluctuations and organic material decay.

        Args:
            dt (float): Delta time in seconds
        """
        # Update market prices periodically
        self._market_timer += dt
        if self._market_timer >= self._market_update_interval:
            self._market_timer = 0.0
            self._apply_price_fluctuations()

        # Apply decay to organic materials
        self._decay_timer += dt
        if self._decay_timer >= self._decay_interval:
            self._decay_timer = 0.0
            self._apply_storage_decay()

    def _apply_price_fluctuations(self) -> None:
        """Apply small random fluctuations to market prices."""
        for material, base_value in self.base_material_values.items():
            # Random fluctuation within range
            fluctuation = self._random.uniform(
                -self._price_fluctuation_range,
                self._price_fluctuation_range
            )
            new_value = base_value * (1.0 + fluctuation)
            self.material_values[material] = round(new_value, 2)

    def _apply_storage_decay(self) -> None:
        """Apply decay to organic materials in storage."""
        total_decay = 0.0

        for material in self._decayable_materials:
            if material in self.stored_materials:
                current_amount = self.stored_materials[material]
                if current_amount > 0:
                    decay_amount = current_amount * self._organic_decay_rate
                    self.stored_materials[material] = max(0.0, current_amount - decay_amount)
                    total_decay += decay_amount

        if total_decay > 0.01:
            logger.debug(f"Storage decay: {total_decay:.2f}kg of organic materials degraded")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get resource statistics.

        Returns:
            dict: Resource statistics
        """
        return {
            'money': self.money,
            'total_stored_weight': self.get_total_stored_weight(),
            'total_stored_value': self.get_total_stored_value(),
            'total_materials_collected': self.total_materials_collected,
            'total_money_earned': self.total_money_earned,
            'material_types_stored': len([q for q in self.stored_materials.values() if q > 0]),
        }

    def __repr__(self):
        """String representation for debugging."""
        return (f"ResourceManager(money=${self.money:.2f}, "
                f"stored={self.get_total_stored_weight():.1f}kg, "
                f"value=${self.get_total_stored_value():.2f})")
