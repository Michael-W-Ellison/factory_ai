"""
Factory building - the core control center.
"""

from src.entities.building import Building
from src.core.constants import Colors


class Factory(Building):
    """
    Factory Control Center.

    The core building that serves as:
    - Robot command center
    - Basic material storage
    - Basic processing (inefficient)
    - Factory return point for robots
    """

    def __init__(self, grid_x, grid_y):
        """
        Initialize the factory.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        super().__init__(grid_x, grid_y, width_tiles=5, height_tiles=5, building_type="factory")

        # Factory-specific properties
        self.name = "Factory Control Center"
        self.max_level = 5
        self.level = 1

        # Power
        self.power_consumption = 5.0  # Base power consumption

        # Storage
        self.storage_capacity = 10000.0  # kg
        self.stored_materials = {}  # material_type -> quantity

        # Processing (very slow, inefficient)
        self.processing_speed = 10.0  # seconds per kg
        self.processing_efficiency = 0.5  # 50% efficiency (lots of waste)

        # Visual
        self.color = Colors.FACTORY_COLOR
        self.outline_color = (60, 60, 100)

        # Visual upgrades (updated by research)
        self.visual_upgrades = {
            'server_farm': 0,  # 0, 1, 2, 3 (tiers)
            'battery_bank': 0,
            'robot_factory': False,
            'hacking_algorithms': 0,  # 0-5
            'processing_improvements': False,
            'research_active': False,  # Currently researching something
        }

        # Already constructed (starting building)
        self.under_construction = False
        self.construction_progress = 100.0

    def _apply_level_bonuses(self):
        """Apply bonuses for current level."""
        # Each level improves storage, processing speed, and efficiency
        self.storage_capacity = 10000.0 * self.level
        self.processing_speed = 10.0 / (1.0 + (self.level - 1) * 0.3)  # Faster processing
        self.processing_efficiency = 0.5 + (self.level - 1) * 0.1  # Better efficiency
        self.power_consumption = 5.0 + (self.level - 1) * 2.0  # More power needed

    def can_store(self, quantity):
        """
        Check if factory has space to store material.

        Args:
            quantity (float): Amount to store in kg

        Returns:
            bool: True if space available
        """
        current_storage = sum(self.stored_materials.values())
        return (current_storage + quantity) <= self.storage_capacity

    def store_material(self, material_type, quantity):
        """
        Store material in factory.

        Args:
            material_type (str): Type of material
            quantity (float): Amount in kg

        Returns:
            float: Amount actually stored
        """
        current_storage = sum(self.stored_materials.values())
        available_space = self.storage_capacity - current_storage
        amount_to_store = min(quantity, available_space)

        if amount_to_store > 0:
            if material_type not in self.stored_materials:
                self.stored_materials[material_type] = 0.0
            self.stored_materials[material_type] += amount_to_store

        return amount_to_store

    def get_material(self, material_type, quantity):
        """
        Retrieve material from factory storage.

        Args:
            material_type (str): Type of material
            quantity (float): Amount requested in kg

        Returns:
            float: Amount actually retrieved
        """
        available = self.stored_materials.get(material_type, 0.0)
        amount_to_retrieve = min(quantity, available)

        if amount_to_retrieve > 0:
            self.stored_materials[material_type] -= amount_to_retrieve

        return amount_to_retrieve

    def get_storage_info(self):
        """
        Get storage information.

        Returns:
            dict: Storage information
        """
        current_storage = sum(self.stored_materials.values())
        return {
            'current': current_storage,
            'capacity': self.storage_capacity,
            'percent_full': (current_storage / self.storage_capacity * 100.0) if self.storage_capacity > 0 else 0,
            'materials': self.stored_materials.copy()
        }

    def _start_processing(self):
        """Start processing material from input queue."""
        if not self.input_queue:
            return

        item = self.input_queue.pop(0)
        self.processing_current = item
        # Processing time based on quantity and speed
        self.processing_time_remaining = item['quantity'] * self.processing_speed

    def _finish_processing(self):
        """Finish processing current item."""
        if self.processing_current is None:
            return

        material_type = self.processing_current['material_type']
        quantity = self.processing_current['quantity']

        # Apply efficiency (rest is waste)
        output_quantity = quantity * self.processing_efficiency
        waste_quantity = quantity - output_quantity

        # Add to output queue
        if output_quantity > 0:
            self.output_queue.append({
                'material_type': f"processed_{material_type}",
                'quantity': output_quantity
            })

        # Waste is lost
        print(f"Factory processed {quantity:.1f}kg of {material_type} -> {output_quantity:.1f}kg output, {waste_quantity:.1f}kg waste")

        # Clear current processing
        self.processing_current = None
        self.processing_time_remaining = 0.0

    def update_visual_upgrades(self, research_manager):
        """
        Update visual upgrades based on completed research.

        Args:
            research_manager: ResearchManager instance
        """
        # Server farm tiers
        if research_manager.is_completed('server_farm_3'):
            self.visual_upgrades['server_farm'] = 3
        elif research_manager.is_completed('server_farm_2'):
            self.visual_upgrades['server_farm'] = 2
        elif research_manager.is_completed('server_farm_1'):
            self.visual_upgrades['server_farm'] = 1

        # Battery bank tiers
        if research_manager.is_completed('battery_bank_3'):
            self.visual_upgrades['battery_bank'] = 3
        elif research_manager.is_completed('battery_bank_2'):
            self.visual_upgrades['battery_bank'] = 2
        elif research_manager.is_completed('battery_bank_1'):
            self.visual_upgrades['battery_bank'] = 1

        # Robot factory
        self.visual_upgrades['robot_factory'] = research_manager.is_completed('robot_factory')

        # Hacking algorithms (1-5)
        hacking_level = 0
        for i in range(5, 0, -1):
            if research_manager.is_completed(f'hacking_algorithms_{i}'):
                hacking_level = i
                break
        self.visual_upgrades['hacking_algorithms'] = hacking_level

        # Processing improvements
        self.visual_upgrades['processing_improvements'] = research_manager.is_completed('recycling_improvements')

        # Research active
        self.visual_upgrades['research_active'] = research_manager.current_research is not None

    def render(self, screen, camera):
        """
        Render factory with special appearance and visual upgrades.

        Args:
            screen: Pygame surface
            camera: Camera object
        """
        super().render(screen, camera)

        # Additional rendering for factory-specific features
        if not self.under_construction and camera.is_visible(self.x, self.y, self.width, self.height):
            import pygame
            screen_x, screen_y = camera.world_to_screen(self.x, self.y)

            # Draw visual upgrades
            self._render_visual_upgrades(screen, screen_x, screen_y)

            # Show storage fill level as a bar
            storage_info = self.get_storage_info()
            fill_percent = storage_info['percent_full'] / 100.0

            bar_width = self.width - 8
            bar_height = 6
            bar_x = screen_x + 4
            bar_y = screen_y + self.height - bar_height - 4

            # Background
            pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))

            # Fill
            fill_width = int(bar_width * fill_percent)
            fill_color = (0, 255, 0) if fill_percent < 0.8 else (255, 100, 0)
            if fill_width > 0:
                pygame.draw.rect(screen, fill_color, (bar_x, bar_y, fill_width, bar_height))

    def _render_visual_upgrades(self, screen, screen_x, screen_y):
        """
        Render visual upgrade components.

        Args:
            screen: Pygame surface
            screen_x (int): Screen X position
            screen_y (int): Screen Y position
        """
        import pygame
        import math
        import time

        # Server farm - Satellite dish on roof
        if self.visual_upgrades['server_farm'] > 0:
            tier = self.visual_upgrades['server_farm']
            dish_size = 8 + tier * 2
            dish_x = screen_x + self.width - dish_size - 10
            dish_y = screen_y - dish_size // 2

            # Dish
            pygame.draw.circle(screen, (180, 180, 200), (dish_x + dish_size // 2, dish_y + dish_size // 2), dish_size // 2)
            pygame.draw.circle(screen, (100, 100, 120), (dish_x + dish_size // 2, dish_y + dish_size // 2), dish_size // 2, 2)

            # Antenna (more antennas = higher tier)
            for i in range(tier):
                antenna_x = screen_x + 15 + i * 12
                antenna_y = screen_y - 8 - i * 3
                pygame.draw.line(screen, (150, 150, 150), (antenna_x, screen_y), (antenna_x, antenna_y), 2)
                pygame.draw.circle(screen, (255, 100, 100), (antenna_x, antenna_y), 3)

        # Battery bank - Battery units on side
        if self.visual_upgrades['battery_bank'] > 0:
            tier = self.visual_upgrades['battery_bank']
            battery_width = 8
            battery_height = 12 + tier * 4
            battery_x = screen_x - battery_width - 2
            battery_y = screen_y + 20

            for i in range(tier):
                by = battery_y + i * (battery_height + 4)
                # Battery body
                pygame.draw.rect(screen, (80, 120, 80), (battery_x, by, battery_width, battery_height))
                pygame.draw.rect(screen, (60, 100, 60), (battery_x, by, battery_width, battery_height), 1)
                # Battery terminal
                pygame.draw.rect(screen, (150, 150, 150), (battery_x + 2, by - 2, battery_width - 4, 2))

        # Robot factory - Assembly arm
        if self.visual_upgrades['robot_factory']:
            arm_base_x = screen_x + 10
            arm_base_y = screen_y + 30
            arm_length = 20

            # Rotating arm
            angle = math.sin(time.time() * 0.5) * 0.5  # Slow oscillation
            arm_end_x = arm_base_x + int(math.cos(angle) * arm_length)
            arm_end_y = arm_base_y + int(math.sin(angle) * arm_length)

            # Arm
            pygame.draw.line(screen, (120, 120, 140), (arm_base_x, arm_base_y), (arm_end_x, arm_end_y), 3)
            # Base
            pygame.draw.circle(screen, (100, 100, 120), (arm_base_x, arm_base_y), 5)
            # Gripper
            pygame.draw.circle(screen, (180, 180, 200), (arm_end_x, arm_end_y), 4)

        # Hacking algorithms - Server racks with lights
        if self.visual_upgrades['hacking_algorithms'] > 0:
            tier = self.visual_upgrades['hacking_algorithms']
            rack_width = 6
            rack_height = 10
            rack_x = screen_x + self.width + 2
            rack_y = screen_y + 10

            for i in range(min(tier, 3)):  # Max 3 visible racks
                ry = rack_y + i * (rack_height + 4)
                # Rack body
                pygame.draw.rect(screen, (40, 40, 50), (rack_x, ry, rack_width, rack_height))
                pygame.draw.rect(screen, (80, 80, 100), (rack_x, ry, rack_width, rack_height), 1)

                # Blinking lights (based on tier)
                blink = int(time.time() * 2) % tier == i
                light_color = (0, 255, 0) if blink else (0, 100, 0)
                pygame.draw.circle(screen, light_color, (rack_x + rack_width // 2, ry + rack_height // 2), 2)

        # Processing improvements - Smokestack
        if self.visual_upgrades['processing_improvements']:
            stack_width = 8
            stack_height = 20
            stack_x = screen_x + self.width // 2 - stack_width // 2
            stack_y = screen_y - stack_height

            # Stack body
            pygame.draw.rect(screen, (80, 80, 80), (stack_x, stack_y, stack_width, stack_height))
            pygame.draw.rect(screen, (60, 60, 60), (stack_x, stack_y, stack_width, stack_height), 1)
            # Stack top
            pygame.draw.rect(screen, (100, 100, 100), (stack_x - 2, stack_y - 2, stack_width + 4, 3))

            # Smoke particles (animated)
            for i in range(3):
                smoke_offset = (time.time() * 30 + i * 20) % 40
                smoke_x = stack_x + stack_width // 2 + int(math.sin(time.time() + i) * 3)
                smoke_y = stack_y - int(smoke_offset)
                smoke_alpha = 100 - int(smoke_offset * 2.5)
                if smoke_alpha > 0:
                    smoke_size = 3 + int(smoke_offset // 10)
                    smoke_color = (120, 120, 130)
                    pygame.draw.circle(screen, smoke_color, (smoke_x, smoke_y), smoke_size)

        # Research active - Pulsing glow
        if self.visual_upgrades['research_active']:
            pulse = math.sin(time.time() * 3) * 0.5 + 0.5
            glow_size = int(8 + pulse * 6)
            glow_alpha = int(100 + pulse * 100)
            glow_color = (100, 100, 255)

            # Draw glow in top-left corner
            glow_x = screen_x + 10
            glow_y = screen_y + 10
            pygame.draw.circle(screen, glow_color, (glow_x, glow_y), glow_size)
            pygame.draw.circle(screen, (150, 150, 255), (glow_x, glow_y), glow_size, 2)

    def get_info(self):
        """Get factory information including storage."""
        info = super().get_info()
        info.update(self.get_storage_info())
        return info

    def __repr__(self):
        """String representation for debugging."""
        storage_info = self.get_storage_info()
        return (f"Factory(level={self.level}, storage={storage_info['current']:.0f}/{self.storage_capacity:.0f}kg, "
                f"pos=({self.grid_x}, {self.grid_y}))")
