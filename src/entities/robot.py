"""
Robot entity - the player's collector/builder robots.
"""

import pygame
import math
from src.entities.entity import Entity
from src.core.constants import Colors, RobotState


class Robot(Entity):
    """
    Robot collector/builder.

    Robots can move around the world, collect materials, and build structures.
    """

    def __init__(self, x, y, autonomous=True):
        """
        Initialize a robot.

        Args:
            x (float): World X position
            y (float): World Y position
            autonomous (bool): If True, robot operates autonomously
        """
        super().__init__(x, y, width=28, height=28)

        # Visual
        self.color = Colors.ROBOT_COLOR  # Green

        # Movement (base values before research)
        self.base_speed = 100.0  # Pixels per second
        self.speed = 100.0
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        # Inventory (base values before research)
        self.base_capacity = 100  # kg
        self.inventory = {}  # material_type -> quantity
        self.material_sources = {}  # material_type -> MaterialSource (for inspection tracking)
        self.max_capacity = 100  # kg
        self.current_load = 0  # kg

        # Power (base values before research)
        self.base_power_capacity = 1000  # units
        self.power_capacity = 1000  # units
        self.current_power = 1000
        self.power_consumption_rate = 1.0  # units per second when moving

        # Health/Durability (base values before research)
        self.base_health = 100
        self.max_health = 100
        self.current_health = 100

        # State
        self.selected = False  # For UI purposes
        self.autonomous = autonomous
        self.state = RobotState.IDLE if autonomous else RobotState.MANUAL

        # Pathfinding and AI
        self.path = []  # List of (grid_x, grid_y) positions
        self.current_path_index = 0
        self.target_object = None  # CollectibleObject we're moving towards
        self.factory_pos = None  # Position of factory for returning
        self.collection_radius = 50.0  # How close we need to be to collect

        # Upgrade level (1-5, affects visuals and capabilities)
        self.upgrade_level = 1

        # Movement direction and animation
        self.facing_angle = 90.0  # degrees (0=right, 90=down, 180=left, 270=up)
        self.animation_frame = 0  # 0 or 1 for movement animation
        self.animation_timer = 0.0
        self.animation_speed = 0.25  # Seconds per frame (faster than NPCs)

    def add_material(self, material_type, quantity, source=None):
        """
        Add material to inventory.

        Args:
            material_type (str): Type of material
            quantity (float): Amount in kg
            source (MaterialSource): Source of the material (optional, for inspection tracking)

        Returns:
            float: Amount actually added (limited by capacity)
        """
        # Calculate how much we can actually carry
        available_space = self.max_capacity - self.current_load
        amount_to_add = min(quantity, available_space)

        if amount_to_add > 0:
            if material_type not in self.inventory:
                self.inventory[material_type] = 0
            self.inventory[material_type] += amount_to_add
            self.current_load += amount_to_add

            # Track source for inspection system
            if source is not None:
                self.material_sources[material_type] = source

        return amount_to_add

    def empty_inventory(self):
        """
        Empty the robot's inventory.

        Returns:
            tuple: (materials_dict, sources_dict) - materials and their sources
        """
        materials = self.inventory.copy()
        sources = self.material_sources.copy()
        self.inventory.clear()
        self.material_sources.clear()
        self.current_load = 0
        return materials, sources

    def is_full(self):
        """Check if robot's inventory is full."""
        return self.current_load >= self.max_capacity

    def apply_research_effects(self, research_manager):
        """
        Apply research bonuses to robot stats.

        Args:
            research_manager: ResearchManager instance with active effects
        """
        # Get multipliers from research (default to 1.0 if not researched)
        speed_mult = research_manager.get_effect_multiplier('robot_speed')
        capacity_mult = research_manager.get_effect_multiplier('robot_capacity')
        power_mult = research_manager.get_effect_multiplier('robot_power_capacity')
        health_mult = research_manager.get_effect_multiplier('robot_health')

        # Apply multipliers to base values
        old_speed = self.speed
        old_capacity = self.max_capacity
        old_power_capacity = self.power_capacity
        old_max_health = self.max_health

        self.speed = self.base_speed * speed_mult
        self.max_capacity = self.base_capacity * capacity_mult
        self.power_capacity = self.base_power_capacity * power_mult
        self.max_health = self.base_health * health_mult

        # If power capacity increased, add the difference to current power (don't lose energy)
        if self.power_capacity > old_power_capacity:
            power_increase = self.power_capacity - old_power_capacity
            self.current_power = min(self.power_capacity, self.current_power + power_increase)

        # If health increased, add the difference to current health
        if self.max_health > old_max_health:
            health_increase = self.max_health - old_max_health
            self.current_health = min(self.max_health, self.current_health + health_increase)

    def update(self, dt, grid=None, entity_manager=None):
        """
        Update robot state.

        Args:
            dt (float): Delta time in seconds
            grid: Grid object (needed for pathfinding)
            entity_manager: EntityManager (needed for finding objects)
        """
        # Update based on state
        if self.autonomous and self.state != RobotState.MANUAL:
            self._update_autonomous(dt, grid, entity_manager)
        else:
            self._update_manual(dt)

    def _update_manual(self, dt):
        """Update robot in manual control mode."""
        moving = (self.velocity_x != 0 or self.velocity_y != 0)

        # Update animation
        if moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0.0
                self.animation_frame = 1 - self.animation_frame
        else:
            self.animation_frame = 0
            self.animation_timer = 0.0

        # Apply movement
        if moving:
            # Normalize diagonal movement
            length = (self.velocity_x ** 2 + self.velocity_y ** 2) ** 0.5
            if length > 0:
                self.velocity_x = (self.velocity_x / length) * self.speed
                self.velocity_y = (self.velocity_y / length) * self.speed

            # Update facing angle
            self.facing_angle = math.degrees(math.atan2(self.velocity_y, self.velocity_x))

            # Move
            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt

            # Consume power when moving
            self.current_power -= self.power_consumption_rate * dt
            self.current_power = max(0, self.current_power)

        # Reset velocity (will be set by input handler)
        self.velocity_x = 0
        self.velocity_y = 0

    def _update_autonomous(self, dt, grid, entity_manager):
        """Update robot in autonomous mode."""
        if self.state == RobotState.IDLE:
            self._state_idle(entity_manager)
        elif self.state == RobotState.MOVING_TO_OBJECT:
            self._state_moving_to_object(dt, grid)
        elif self.state == RobotState.COLLECTING:
            self._state_collecting()
        elif self.state == RobotState.RETURNING_TO_FACTORY:
            self._state_returning(dt, grid)
        elif self.state == RobotState.UNLOADING:
            self._state_unloading(entity_manager)

    def _state_idle(self, entity_manager):
        """IDLE state: Look for something to collect."""
        if entity_manager is None:
            return

        # If inventory is full, return to factory
        if self.is_full():
            if self.factory_pos:
                self.state = RobotState.RETURNING_TO_FACTORY
                return

        # Find nearest collectible
        center_x, center_y = self.get_center()
        nearby = entity_manager.get_collectibles_near(center_x, center_y, 500)

        if nearby:
            # Pick closest one
            closest = min(nearby, key=lambda obj: self.distance_to(obj))
            self.target_object = closest
            self.state = RobotState.MOVING_TO_OBJECT

    def _state_moving_to_object(self, dt, grid):
        """MOVING_TO_OBJECT state: Follow path to target."""
        if self.target_object is None or not self.target_object.active:
            # Target disappeared
            self.target_object = None
            self.path = []
            self.state = RobotState.IDLE
            return

        # Check if we're close enough to collect
        distance = self.distance_to(self.target_object)
        if distance <= self.collection_radius:
            self.state = RobotState.COLLECTING
            return

        # Follow path or recalculate if needed
        if not self.path or self.current_path_index >= len(self.path):
            # Need new path
            self._calculate_path_to_target(grid)

        # Move along path
        if self.path and self.current_path_index < len(self.path):
            self._follow_path(dt, grid)

    def _state_collecting(self):
        """COLLECTING state: Pick up the target object."""
        if self.target_object is None or not self.target_object.active:
            self.target_object = None
            self.state = RobotState.IDLE
            return

        # Collection is handled by EntityManager's collection system
        # We just need to check if we're done
        if self.is_full():
            self.target_object = None
            if self.factory_pos:
                self.state = RobotState.RETURNING_TO_FACTORY
            else:
                self.state = RobotState.IDLE
        else:
            # Go back to idle to find next object
            self.target_object = None
            self.state = RobotState.IDLE

    def _state_returning(self, dt, grid):
        """RETURNING_TO_FACTORY state: Navigate back to factory."""
        if not self.factory_pos:
            # No factory set, just go idle
            self.state = RobotState.IDLE
            return

        # Check if we're at the factory
        factory_world_x, factory_world_y = self.factory_pos
        dx = self.x - factory_world_x
        dy = self.y - factory_world_y
        distance = (dx * dx + dy * dy) ** 0.5

        if distance <= 50:  # Within 50 pixels of factory
            self.state = RobotState.UNLOADING
            return

        # Follow path to factory
        if not self.path or self.current_path_index >= len(self.path):
            self._calculate_path_to_factory(grid)

        if self.path and self.current_path_index < len(self.path):
            self._follow_path(dt, grid)

    def _state_unloading(self, entity_manager):
        """UNLOADING state: Deposit materials at factory."""
        if self.current_load > 0 and entity_manager:
            # Deposit all materials to resource manager with source tracking
            if hasattr(entity_manager, 'resource_manager'):
                material_inventory = getattr(entity_manager, 'material_inventory', None)
                entity_manager.resource_manager.deposit_materials(
                    self.inventory,
                    self.material_sources,
                    material_inventory
                )

            # Empty inventory
            self.empty_inventory()

        # Go back to idle
        self.state = RobotState.IDLE

    def _calculate_path_to_target(self, grid):
        """Calculate path to target object."""
        if not self.target_object or not grid:
            return

        from src.systems.pathfinding import Pathfinder

        # Convert positions to grid coordinates
        start_grid = grid.world_to_grid(self.x, self.y)
        target_center = self.target_object.get_center()
        goal_grid = grid.world_to_grid(target_center[0], target_center[1])

        # Find path
        pathfinder = Pathfinder(grid)
        path = pathfinder.find_path(start_grid, goal_grid)

        if path:
            self.path = path
            self.current_path_index = 0
        else:
            # No path found, give up on this target
            self.target_object = None
            self.state = RobotState.IDLE

    def _calculate_path_to_factory(self, grid):
        """Calculate path to factory."""
        if not self.factory_pos or not grid:
            return

        from src.systems.pathfinding import Pathfinder

        # Convert positions to grid coordinates
        start_grid = grid.world_to_grid(self.x, self.y)
        goal_grid = grid.world_to_grid(self.factory_pos[0], self.factory_pos[1])

        # Find path
        pathfinder = Pathfinder(grid)
        path = pathfinder.find_path(start_grid, goal_grid)

        if path:
            self.path = path
            self.current_path_index = 0
        else:
            # No path to factory, just idle
            self.state = RobotState.IDLE

    def _follow_path(self, dt, grid):
        """Follow the current path."""
        if not self.path or self.current_path_index >= len(self.path):
            # Not moving, reset animation
            self.animation_frame = 0
            self.animation_timer = 0.0
            return

        # Get current waypoint
        waypoint_grid = self.path[self.current_path_index]
        waypoint_world = (
            waypoint_grid[0] * grid.tile_size + grid.tile_size // 2,
            waypoint_grid[1] * grid.tile_size + grid.tile_size // 2
        )

        # Calculate direction to waypoint
        dx = waypoint_world[0] - self.x
        dy = waypoint_world[1] - self.y
        distance = (dx * dx + dy * dy) ** 0.5

        # If close enough, move to next waypoint
        if distance < 5:
            self.current_path_index += 1
            return

        # Move towards waypoint
        if distance > 0:
            # Update animation
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0.0
                self.animation_frame = 1 - self.animation_frame

            # Update facing angle
            self.facing_angle = math.degrees(math.atan2(dy, dx))

            self.velocity_x = (dx / distance) * self.speed
            self.velocity_y = (dy / distance) * self.speed

            # Apply movement
            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt

            # Consume power
            self.current_power -= self.power_consumption_rate * dt
            self.current_power = max(0, self.current_power)

            # Reset velocity
            self.velocity_x = 0
            self.velocity_y = 0
        else:
            # Not moving, reset animation
            self.animation_frame = 0
            self.animation_timer = 0.0

    def move(self, dx, dy):
        """
        Set movement direction.

        Args:
            dx (float): X direction (-1, 0, or 1)
            dy (float): Y direction (-1, 0, or 1)
        """
        self.velocity_x = dx
        self.velocity_y = dy

    def render(self, screen, camera):
        """
        Render robot to screen with directional orientation and upgrade-based visuals.

        Args:
            screen: Pygame surface
            camera: Camera object
        """
        if not self.visible:
            return

        # Convert world coordinates to screen coordinates
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)

        if not camera.is_visible(self.x, self.y, self.width, self.height):
            return

        # Apply camera zoom
        width_px = int(self.width * camera.zoom)
        height_px = int(self.height * camera.zoom)

        # Get upgrade level visual properties
        level_props = self._get_level_visuals()

        # Calculate direction
        angle = self.facing_angle % 360
        angle_rad = math.radians(angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        # Draw treads/wheels (animated when moving)
        tread_offset = 2 if self.animation_frame == 1 else -2
        tread_width = level_props['tread_width']
        tread_length = level_props['tread_length']

        # Calculate tread positions (perpendicular to facing direction)
        tread_spread = width_px // 2
        left_offset_x = -sin_a * tread_spread
        left_offset_y = cos_a * tread_spread
        right_offset_x = sin_a * tread_spread
        right_offset_y = -cos_a * tread_spread

        # Left tread
        left_tread_x = int(screen_x + left_offset_x)
        left_tread_y = int(screen_y + left_offset_y + tread_offset)
        left_tread_rect = pygame.Rect(left_tread_x - tread_width//2, left_tread_y - tread_length//2,
                                       tread_width, tread_length)
        pygame.draw.rect(screen, (40, 40, 40), left_tread_rect)
        pygame.draw.rect(screen, (20, 20, 20), left_tread_rect, 1)

        # Right tread
        right_tread_x = int(screen_x + right_offset_x)
        right_tread_y = int(screen_y + right_offset_y - tread_offset)
        right_tread_rect = pygame.Rect(right_tread_x - tread_width//2, right_tread_y - tread_length//2,
                                        tread_width, tread_length)
        pygame.draw.rect(screen, (40, 40, 40), right_tread_rect)
        pygame.draw.rect(screen, (20, 20, 20), right_tread_rect, 1)

        # Draw main body (chassis)
        body_width = level_props['body_width']
        body_height = level_props['body_height']
        body_rect = pygame.Rect(screen_x - body_width//2, screen_y - body_height//2,
                                body_width, body_height)
        pygame.draw.rect(screen, level_props['body_color'], body_rect)
        pygame.draw.rect(screen, level_props['outline_color'], body_rect, 2)

        # Draw "head" or sensor array (offset in facing direction)
        head_size = level_props['head_size']
        head_offset_x = cos_a * body_width * 0.3
        head_offset_y = sin_a * body_height * 0.3
        head_pos = (int(screen_x + head_offset_x), int(screen_y + head_offset_y))
        head_rect = pygame.Rect(head_pos[0] - head_size//2, head_pos[1] - head_size//2,
                                head_size, head_size)
        pygame.draw.rect(screen, level_props['head_color'], head_rect)
        pygame.draw.rect(screen, (0, 150, 0), head_rect, 1)

        # Draw facing direction indicator/sensor (small glowing dot)
        indicator_dist = head_size // 2 + 3
        indicator_x = int(head_pos[0] + cos_a * indicator_dist)
        indicator_y = int(head_pos[1] + sin_a * indicator_dist)
        pygame.draw.circle(screen, (0, 255, 0), (indicator_x, indicator_y), 2)  # Green sensor dot

        # Draw arms/manipulators (if upgraded enough)
        if self.upgrade_level >= 2:
            arm_length = level_props['arm_length']
            arm_width = level_props['arm_width']

            # Left arm
            left_arm_x = int(screen_x + left_offset_x * 0.7)
            left_arm_y = int(screen_y + left_offset_y * 0.7)
            left_arm_end_x = int(left_arm_x + cos_a * arm_length)
            left_arm_end_y = int(left_arm_y + sin_a * arm_length)
            pygame.draw.line(screen, (120, 120, 120), (left_arm_x, left_arm_y),
                           (left_arm_end_x, left_arm_end_y), arm_width)

            # Right arm
            right_arm_x = int(screen_x + right_offset_x * 0.7)
            right_arm_y = int(screen_y + right_offset_y * 0.7)
            right_arm_end_x = int(right_arm_x + cos_a * arm_length)
            right_arm_end_y = int(right_arm_y + sin_a * arm_length)
            pygame.draw.line(screen, (120, 120, 120), (right_arm_x, right_arm_y),
                           (right_arm_end_x, right_arm_end_y), arm_width)

        # Draw selection indicator if selected
        if self.selected:
            selection_rect = pygame.Rect(screen_x - body_width//2 - 2, screen_y - body_height//2 - 2,
                                        body_width + 4, body_height + 4)
            pygame.draw.rect(screen, Colors.YELLOW, selection_rect, 2)

        # Draw capacity indicator (small bar showing how full)
        if self.max_capacity > 0:
            bar_width = body_width
            bar_height = 3
            bar_x = screen_x - bar_width//2
            bar_y = screen_y - body_height//2 - 8

            # Background (gray)
            pygame.draw.rect(screen, (60, 60, 60),
                           (bar_x, bar_y, bar_width, bar_height))

            # Fill (green -> yellow -> red as it fills)
            fill_ratio = self.current_load / self.max_capacity
            fill_width = int(bar_width * fill_ratio)

            if fill_ratio < 0.5:
                fill_color = (0, 255, 0)  # Green
            elif fill_ratio < 0.8:
                fill_color = (255, 255, 0)  # Yellow
            else:
                fill_color = (255, 100, 0)  # Orange

            if fill_width > 0:
                pygame.draw.rect(screen, fill_color,
                               (bar_x, bar_y, fill_width, bar_height))

        # Draw upgrade level indicator (when zoomed in)
        if camera.zoom >= 0.8:
            font = pygame.font.Font(None, 12)
            level_text = f"L{self.upgrade_level}"
            text_surface = font.render(level_text, True, (0, 255, 0))
            text_rect = text_surface.get_rect(center=(screen_x, screen_y + body_height//2 + 8))
            # Background
            bg_rect = text_rect.inflate(4, 2)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            screen.blit(text_surface, text_rect)

    def _get_level_visuals(self):
        """
        Get visual properties based on upgrade level.

        Returns:
            dict: Visual properties for current level
        """
        # Base sizes that scale with upgrade level
        # Level 1: Spindly, fragile-looking
        # Level 5: Thick, strong, advanced-looking

        if self.upgrade_level == 1:
            # Spindly, basic robot
            return {
                'body_width': 20,
                'body_height': 20,
                'body_color': (80, 200, 80),  # Light green
                'outline_color': (40, 100, 40),
                'head_size': 8,
                'head_color': (100, 220, 100),
                'tread_width': 4,
                'tread_length': 12,
                'arm_length': 0,  # No arms at level 1
                'arm_width': 0,
            }
        elif self.upgrade_level == 2:
            # Improved, slightly thicker
            return {
                'body_width': 24,
                'body_height': 24,
                'body_color': (70, 200, 70),
                'outline_color': (35, 100, 35),
                'head_size': 10,
                'head_color': (90, 220, 90),
                'tread_width': 5,
                'tread_length': 14,
                'arm_length': 8,
                'arm_width': 2,
            }
        elif self.upgrade_level == 3:
            # Advanced, solid build
            return {
                'body_width': 28,
                'body_height': 28,
                'body_color': (60, 200, 60),
                'outline_color': (30, 100, 30),
                'head_size': 12,
                'head_color': (80, 220, 80),
                'tread_width': 6,
                'tread_length': 16,
                'arm_length': 10,
                'arm_width': 3,
            }
        elif self.upgrade_level == 4:
            # Heavy-duty, robust
            return {
                'body_width': 32,
                'body_height': 32,
                'body_color': (50, 180, 50),
                'outline_color': (25, 90, 25),
                'head_size': 14,
                'head_color': (70, 200, 70),
                'tread_width': 7,
                'tread_length': 18,
                'arm_length': 12,
                'arm_width': 4,
            }
        else:  # Level 5
            # Maximum upgrade, powerful and imposing
            return {
                'body_width': 36,
                'body_height': 36,
                'body_color': (40, 160, 40),
                'outline_color': (20, 80, 20),
                'head_size': 16,
                'head_color': (60, 180, 60),
                'tread_width': 8,
                'tread_length': 20,
                'arm_length': 14,
                'arm_width': 5,
            }

    def __repr__(self):
        """String representation for debugging."""
        return (f"Robot(id={self.id}, pos=({self.x:.0f}, {self.y:.0f}), "
                f"load={self.current_load:.1f}/{self.max_capacity}kg)")
