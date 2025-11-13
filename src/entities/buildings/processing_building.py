"""
ProcessingBuilding - base class for material processing buildings.
"""

from src.entities.building import Building
import random


class ProcessingBuilding(Building):
    """
    Base class for buildings that process materials.

    Handles material input, processing with quality tiers, and output.
    """

    def __init__(self, grid_x, grid_y, width_tiles, height_tiles, building_type, config):
        """
        Initialize a processing building.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
            width_tiles (int): Width in tiles
            height_tiles (int): Height in tiles
            building_type (str): Type of building
            config (dict): Building configuration with processing parameters
        """
        super().__init__(grid_x, grid_y, width_tiles, height_tiles, building_type)

        # Apply configuration
        self.name = config['name']
        self.base_cost = config['cost']
        self.max_level = config.get('max_level', 3)

        # Power
        self.base_power_consumption = config['power_consumption']
        self.power_consumption = self.base_power_consumption

        # Processing parameters
        self.base_processing_speed = config['processing_speed']  # seconds per kg
        self.processing_speed = self.base_processing_speed

        self.input_material_types = config['input_types']  # List of accepted materials

        # Quality distribution (chances for each quality tier)
        self.quality_distribution = config.get('quality_distribution', {
            'waste': 0.50,
            'low': 0.30,
            'medium': 0.15,
            'high': 0.05
        })

        # Efficiency (how much material is converted vs lost)
        self.base_efficiency = config.get('efficiency', 0.90)
        self.efficiency = self.base_efficiency

        # Queue limits
        self.max_input_queue = config.get('max_input_queue', 1000)  # kg
        self.max_output_queue = config.get('max_output_queue', 1000)  # kg

        # Visual
        self.color = config.get('color', (100, 100, 100))
        self.outline_color = config.get('outline_color', (80, 80, 80))

    def can_accept_material(self, material_type):
        """
        Check if building can accept this material type.

        Args:
            material_type (str): Type of material

        Returns:
            bool: True if material is accepted
        """
        return material_type in self.input_material_types

    def get_current_input_weight(self):
        """Get total weight in input queue."""
        return sum(item['quantity'] for item in self.input_queue)

    def get_current_output_weight(self):
        """Get total weight in output queue."""
        return sum(item['quantity'] for item in self.output_queue)

    def add_to_input_queue(self, material_type, quantity):
        """
        Add material to input queue.

        Args:
            material_type (str): Type of material
            quantity (float): Amount in kg

        Returns:
            float: Amount actually added
        """
        if not self.can_accept_material(material_type):
            return 0.0

        current_input = self.get_current_input_weight()
        available_space = self.max_input_queue - current_input
        amount_to_add = min(quantity, available_space)

        if amount_to_add > 0:
            self.input_queue.append({
                'material_type': material_type,
                'quantity': amount_to_add
            })

        return amount_to_add

    def _start_processing(self):
        """Start processing the next item in queue."""
        if not self.input_queue:
            return

        item = self.input_queue.pop(0)
        self.processing_current = item
        # Processing time based on quantity and speed
        self.processing_time_remaining = item['quantity'] * self.processing_speed

    def _finish_processing(self):
        """Finish processing current item with quality tiers."""
        if self.processing_current is None:
            return

        material_type = self.processing_current['material_type']
        quantity = self.processing_current['quantity']

        # Apply efficiency - rest is lost
        usable_quantity = quantity * self.efficiency
        waste_quantity = quantity - usable_quantity

        # Distribute usable quantity across quality tiers
        output_materials = self._distribute_quality(material_type, usable_quantity)

        # Add to output queue (check capacity)
        current_output = self.get_current_output_weight()
        for output_material, output_quantity in output_materials.items():
            if output_quantity > 0:
                # Check if we have space
                if current_output + output_quantity <= self.max_output_queue:
                    self.output_queue.append({
                        'material_type': output_material,
                        'quantity': output_quantity
                    })
                    current_output += output_quantity
                else:
                    # Output queue full, material is lost
                    print(f"{self.name} output queue full! Lost {output_quantity:.1f}kg of {output_material}")

        print(f"{self.name} processed {quantity:.1f}kg of {material_type} "
              f"-> {usable_quantity:.1f}kg output, {waste_quantity:.1f}kg waste")

        # Clear current processing
        self.processing_current = None
        self.processing_time_remaining = 0.0

    def _distribute_quality(self, base_material, quantity):
        """
        Distribute material quantity across quality tiers.

        Args:
            base_material (str): Base material type
            quantity (float): Total quantity to distribute

        Returns:
            dict: material_type -> quantity for each quality tier
        """
        output = {}
        remaining = quantity

        # Roll for each quality tier (starting from highest)
        for quality in ['high', 'medium', 'low', 'waste']:
            chance = self.quality_distribution.get(quality, 0.0)
            if chance > 0 and remaining > 0:
                # Random distribution based on chance
                amount = remaining * chance * random.uniform(0.8, 1.2)  # Add variance
                amount = min(amount, remaining)

                if amount > 0.1:  # Only add if significant amount
                    material_name = self._get_material_name(base_material, quality)
                    output[material_name] = amount
                    remaining -= amount

        # Any remaining goes to waste
        if remaining > 0.1:
            waste_name = self._get_material_name(base_material, 'waste')
            output[waste_name] = output.get(waste_name, 0) + remaining

        return output

    def _get_material_name(self, base_material, quality):
        """
        Get output material name for quality tier.

        Args:
            base_material (str): Base material type
            quality (str): Quality tier

        Returns:
            str: Output material name
        """
        if quality == 'waste':
            return f"waste_{base_material}"
        else:
            return f"{quality}_{base_material}"

    def _apply_level_bonuses(self):
        """Apply bonuses for current level."""
        # Each level improves processing speed, efficiency, and quality
        speed_bonus = 1.0 - (self.level - 1) * 0.15  # Faster (-15% per level)
        self.processing_speed = self.base_processing_speed * speed_bonus

        efficiency_bonus = (self.level - 1) * 0.03  # +3% efficiency per level
        self.efficiency = min(0.98, self.base_efficiency + efficiency_bonus)

        # Improve quality distribution (shift towards higher quality)
        quality_shift = (self.level - 1) * 0.05
        self.quality_distribution = {
            'waste': max(0.2, 0.50 - quality_shift * 2),
            'low': 0.30 - quality_shift * 0.5,
            'medium': 0.15 + quality_shift * 1.5,
            'high': 0.05 + quality_shift * 1.0
        }

        # More power needed
        self.power_consumption = self.base_power_consumption + (self.level - 1) * 1.0

    def get_info(self):
        """Get building information including processing stats."""
        info = super().get_info()
        info.update({
            'processing_speed': self.processing_speed,
            'efficiency': self.efficiency * 100.0,
            'input_weight': self.get_current_input_weight(),
            'output_weight': self.get_current_output_weight(),
            'input_capacity': self.max_input_queue,
            'output_capacity': self.max_output_queue,
            'accepts': self.input_material_types,
        })
        return info

    def __repr__(self):
        """String representation for debugging."""
        return (f"{self.name}(level={self.level}, "
                f"queue={len(self.input_queue)}/{len(self.output_queue)}, "
                f"pos=({self.grid_x}, {self.grid_y}))")
