"""
Robot entity - the player's collector/builder robots.
"""

import pygame
from src.entities.entity import Entity
from src.core.constants import Colors


class Robot(Entity):
    """
    Robot collector/builder.

    Robots can move around the world, collect materials, and build structures.
    """

    def __init__(self, x, y):
        """
        Initialize a robot.

        Args:
            x (float): World X position
            y (float): World Y position
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

    def update(self, dt):
        """
        Update robot state.

        Args:
            dt (float): Delta time in seconds
        """
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
