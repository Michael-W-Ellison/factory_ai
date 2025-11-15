"""
ManufacturingBuilding - base class for component manufacturing buildings.

Extends ProcessingBuilding to handle multi-material recipes and component production.
"""

from src.entities.buildings.processing_building import ProcessingBuilding


class ManufacturingBuilding(ProcessingBuilding):
    """
    Base class for buildings that manufacture components from multiple materials.

    Handles complex recipes requiring multiple input materials/components,
    and produces high-value components for robot upgrades and research.
    """

    def __init__(self, grid_x, grid_y, width_tiles, height_tiles, building_type, config):
        """
        Initialize a manufacturing building.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
            width_tiles (int): Width in tiles
            height_tiles (int): Height in tiles
            building_type (str): Type of building
            config (dict): Building configuration including recipe
        """
        super().__init__(grid_x, grid_y, width_tiles, height_tiles, building_type, config)

        # Manufacturing-specific properties
        self.recipe = config.get('recipe', {})  # {material: quantity}
        self.output_component = config.get('output_component', 'circuit_board')
        self.output_per_batch = config.get('output_per_batch', 1.0)
        self.batch_value_multiplier = config.get('batch_value_multiplier', 2.0)

        # Recipe checking
        self.recipe_checking_interval = 1.0  # Check every second
        self.time_since_recipe_check = 0.0

    def can_start_manufacturing(self) -> bool:
        """
        Check if we have required materials to start manufacturing a batch.

        Returns:
            bool: True if all recipe materials are available in input queue
        """
        if not self.recipe:
            return False  # No recipe defined

        # Count available materials in input queue
        material_counts = {}
        for item in self.input_queue:
            mat_type = item['material_type']
            material_counts[mat_type] = material_counts.get(mat_type, 0.0) + item['quantity']

        # Check if we have enough of each required material
        for mat_type, required_amount in self.recipe.items():
            available = material_counts.get(mat_type, 0.0)
            if available < required_amount:
                return False

        return True

    def consume_recipe_materials(self) -> bool:
        """
        Consume materials from input queue according to recipe.

        Returns:
            bool: True if materials consumed successfully
        """
        if not self.can_start_manufacturing():
            return False

        # Consume materials
        for mat_type, required_amount in self.recipe.items():
            remaining_to_consume = required_amount

            # Remove from input queue
            i = 0
            while i < len(self.input_queue) and remaining_to_consume > 0:
                item = self.input_queue[i]

                if item['material_type'] == mat_type:
                    if item['quantity'] <= remaining_to_consume:
                        # Consume entire item
                        remaining_to_consume -= item['quantity']
                        self.input_queue.pop(i)
                    else:
                        # Consume part of item
                        item['quantity'] -= remaining_to_consume
                        remaining_to_consume = 0.0
                        i += 1
                else:
                    i += 1

            # Verify we consumed enough
            if remaining_to_consume > 0.01:
                print(f"ERROR: Failed to consume {remaining_to_consume}kg of {mat_type}")
                return False

        return True

    def _start_processing(self):
        """Start manufacturing a batch of components."""
        if not self.can_start_manufacturing():
            return

        # Consume recipe materials
        if not self.consume_recipe_materials():
            return

        # Set up processing
        self.processing_current = {
            'component_type': self.output_component,
            'quantity': self.output_per_batch
        }

        # Processing time is base speed * batch size
        self.processing_time_remaining = self.processing_speed * self.output_per_batch

        print(f"{self.name} started manufacturing {self.output_component} "
              f"(batch size: {self.output_per_batch:.1f})")

    def _finish_processing(self):
        """Finish manufacturing and output components with quality tiers."""
        if self.processing_current is None:
            return

        component_type = self.processing_current['component_type']
        quantity = self.processing_current['quantity']

        # Apply efficiency
        usable_quantity = quantity * self.efficiency

        # Distribute across quality tiers
        output_components = self._distribute_quality(component_type, usable_quantity)

        # Add to output queue
        current_output = self.get_current_output_weight()
        for output_comp, output_qty in output_components.items():
            if output_qty > 0:
                # Check if we have space
                if current_output + output_qty <= self.max_output_queue:
                    self.output_queue.append({
                        'material_type': output_comp,  # Components use same structure
                        'quantity': output_qty
                    })
                    current_output += output_qty
                else:
                    print(f"{self.name} output queue full! Lost {output_qty:.1f} units of {output_comp}")

        print(f"{self.name} completed manufacturing: {usable_quantity:.2f} units of {component_type}")

        # Clear current processing
        self.processing_current = None
        self.processing_time_remaining = 0.0

    def update(self, dt):
        """
        Update the manufacturing building.

        Args:
            dt (float): Delta time in seconds
        """
        # Check if powered
        if not self.powered:
            return

        # Update processing
        if self.processing_current is not None:
            # Currently manufacturing
            self.processing_time_remaining -= dt

            if self.processing_time_remaining <= 0:
                self._finish_processing()

        elif self.input_queue:
            # Not processing, but have materials - try to start
            self.time_since_recipe_check += dt

            if self.time_since_recipe_check >= self.recipe_checking_interval:
                self.time_since_recipe_check = 0.0

                if self.can_start_manufacturing():
                    self._start_processing()

    def get_recipe_status(self) -> dict:
        """
        Get current recipe fulfillment status.

        Returns:
            dict: {material_type: (available, required)}
        """
        # Count available materials in input queue
        material_counts = {}
        for item in self.input_queue:
            mat_type = item['material_type']
            material_counts[mat_type] = material_counts.get(mat_type, 0.0) + item['quantity']

        # Build status
        status = {}
        for mat_type, required_amount in self.recipe.items():
            available = material_counts.get(mat_type, 0.0)
            status[mat_type] = (available, required_amount)

        return status

    def get_info(self):
        """Get building information including manufacturing stats."""
        info = super().get_info()

        # Add manufacturing-specific info
        info.update({
            'output_component': self.output_component,
            'batch_size': self.output_per_batch,
            'recipe': self.recipe,
            'recipe_status': self.get_recipe_status(),
            'can_manufacture': self.can_start_manufacturing()
        })

        return info

    def __repr__(self):
        """String representation for debugging."""
        recipe_ready = "✓" if self.can_start_manufacturing() else "✗"
        return (f"{self.name}(level={self.level}, "
                f"recipe={recipe_ready}, "
                f"output={self.output_component}, "
                f"pos=({self.grid_x}, {self.grid_y}))")
