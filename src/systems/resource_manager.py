"""
ResourceManager - tracks materials, money, and resources.
"""


class ResourceManager:
    """
    Manages the player's resources including materials and money.

    This tracks all materials collected and processed, as well as money earned.
    """

    def __init__(self):
        """Initialize the resource manager."""
        # Materials stored in the factory (material_type -> quantity in kg)
        self.stored_materials = {}

        # Money
        self.money = 1000.0  # Starting money in $

        # Statistics
        self.total_materials_collected = 0.0  # Total kg collected all-time
        self.total_money_earned = 0.0  # Total money earned all-time

        # Material values ($ per kg) - these will eventually come from market system
        self.material_values = {
            'plastic': 0.50,
            'metal': 1.20,
            'glass': 0.30,
            'paper': 0.20,
            'rubber': 0.80,
            'organic': 0.10,
            'wood': 0.40,
            'electronic': 2.50,
        }

    def deposit_materials(self, materials_dict, sources_dict=None, material_inventory=None):
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

                print(f"Deposited {quantity:.1f}kg of {material_type}")

        return total_deposited

    def sell_material(self, material_type, quantity):
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
            print(f"Not enough {material_type} to sell (have {current_quantity:.1f}kg, need {quantity:.1f}kg)")
            return 0.0

        # Calculate value
        value_per_kg = self.material_values.get(material_type, 0.5)
        money_earned = quantity * value_per_kg

        # Remove from storage
        self.stored_materials[material_type] -= quantity

        # Add money
        self.money += money_earned
        self.total_money_earned += money_earned

        print(f"Sold {quantity:.1f}kg of {material_type} for ${money_earned:.2f}")
        return money_earned

    def sell_all_materials(self):
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

    def get_material_value(self, material_type, quantity):
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

    def get_total_stored_value(self):
        """
        Calculate the total value of all stored materials.

        Returns:
            float: Total value in $
        """
        total_value = 0.0
        for material_type, quantity in self.stored_materials.items():
            total_value += self.get_material_value(material_type, quantity)
        return total_value

    def modify_money(self, amount):
        """
        Modify the player's money (add or subtract).

        Args:
            amount (float): Amount to add (positive) or subtract (negative)
        """
        self.money += amount
        if amount > 0:
            self.total_money_earned += amount

    def get_material_quantity(self, material_type):
        """
        Get the quantity of a specific material in storage.

        Args:
            material_type (str): Type of material

        Returns:
            float: Quantity in kg
        """
        return self.stored_materials.get(material_type, 0.0)

    def get_total_stored_weight(self):
        """
        Get the total weight of all stored materials.

        Returns:
            float: Total weight in kg
        """
        return sum(self.stored_materials.values())

    def update(self, dt):
        """
        Update resource manager (placeholder for future use).

        Args:
            dt (float): Delta time in seconds
        """
        # Future features:
        # - Market price fluctuations
        # - Storage decay
        # - Passive income from processing
        pass

    def get_stats(self):
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
