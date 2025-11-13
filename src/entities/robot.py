"""
Robot entity - the player's collector/builder robots.
"""

import pygame
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

        # Movement
        self.speed = 100.0  # Pixels per second
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        # Inventory
        self.inventory = {}  # material_type -> quantity
        self.max_capacity = 100  # kg
        self.current_load = 0  # kg

        # Power
        self.power_capacity = 1000  # units
        self.current_power = 1000
        self.power_consumption_rate = 1.0  # units per second when moving

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

    def add_material(self, material_type, quantity):
        """
        Add material to inventory.

        Args:
            material_type (str): Type of material
            quantity (float): Amount in kg

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

        return amount_to_add

    def empty_inventory(self):
        """
        Empty the robot's inventory.

        Returns:
            dict: The materials that were in inventory
        """
        materials = self.inventory.copy()
        self.inventory.clear()
        self.current_load = 0
        return materials

    def is_full(self):
        """Check if robot's inventory is full."""
        return self.current_load >= self.max_capacity

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
        # Apply movement
        if self.velocity_x != 0 or self.velocity_y != 0:
            # Normalize diagonal movement
            length = (self.velocity_x ** 2 + self.velocity_y ** 2) ** 0.5
            if length > 0:
                self.velocity_x = (self.velocity_x / length) * self.speed
                self.velocity_y = (self.velocity_y / length) * self.speed

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
            # Deposit all materials to resource manager
            if hasattr(entity_manager, 'resource_manager'):
                entity_manager.resource_manager.deposit_materials(self.inventory)

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
        Render robot to screen.

        Args:
            screen: Pygame surface
            camera: Camera object
        """
        if not self.visible:
            return

        # Convert world coordinates to screen coordinates
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)

        if camera.is_visible(self.x, self.y, self.width, self.height):
            # Draw robot body
            rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
            pygame.draw.rect(screen, self.color, rect)

            # Draw border (darker green)
            pygame.draw.rect(screen, (0, 180, 0), rect, 2)

            # Draw selection indicator if selected
            if self.selected:
                selection_rect = pygame.Rect(screen_x - 2, screen_y - 2,
                                            self.width + 4, self.height + 4)
                pygame.draw.rect(screen, Colors.YELLOW, selection_rect, 2)

            # Draw capacity indicator (small bar showing how full)
            if self.max_capacity > 0:
                bar_width = self.width
                bar_height = 3
                bar_x = screen_x
                bar_y = screen_y - 6

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

    def __repr__(self):
        """String representation for debugging."""
        return (f"Robot(id={self.id}, pos=({self.x:.0f}, {self.y:.0f}), "
                f"load={self.current_load:.1f}/{self.max_capacity}kg)")
