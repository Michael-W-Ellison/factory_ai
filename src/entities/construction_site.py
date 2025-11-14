"""
ConstructionSite - Placeholder entity during building construction.

Represents a building under construction, showing progress and requirements.
"""

import pygame
from src.entities.entity import Entity
from typing import Dict, Optional


class ConstructionSite(Entity):
    """
    Construction site for buildings.

    Shows visual progress, required materials, required robots, and timer.
    Multiple robots working on the same site speed up construction.
    """

    def __init__(self, grid_x: int, grid_y: int, width_tiles: int, height_tiles: int,
                 building_type: str, construction_time: float, required_materials: Optional[Dict[str, float]] = None):
        """
        Initialize a construction site.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
            width_tiles (int): Width in tiles
            height_tiles (int): Height in tiles
            building_type (str): Type of building being constructed
            construction_time (float): Time to complete construction in seconds
            required_materials (Dict[str, float]): Materials required {type: quantity}
        """
        # Convert grid to world position
        world_x = grid_x * 32
        world_y = grid_y * 32
        world_width = width_tiles * 32
        world_height = height_tiles * 32

        super().__init__(world_x, world_y, width=world_width, height=world_height)

        # Grid position
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.width_tiles = width_tiles
        self.height_tiles = height_tiles

        # Building info
        self.building_type = building_type
        self.name = f"{building_type} (Under Construction)"

        # Construction progress
        self.construction_time = construction_time  # Total time needed
        self.base_construction_time = construction_time
        self.time_remaining = construction_time
        self.progress = 0.0  # 0.0 to 1.0
        self.speed_multiplier = 1.0  # Speed based on worker count

        # Materials
        self.required_materials = required_materials or {}
        self.materials_delivered = {mat: 0.0 for mat in self.required_materials.keys()}

        # Robots working on this site
        self.robots_working = []  # List of robot IDs
        self.base_workers = 1  # Minimum robots for construction
        self.max_workers = 5  # Maximum robots that can work simultaneously

        # Visual
        self.color = (120, 100, 80)  # Construction brown
        self.outline_color = (80, 60, 40)
        self.progress_color = (100, 200, 100)  # Green progress bar

        # State
        self.canceled = False

    def add_robot(self, robot_id):
        """
        Add a robot to work on this construction site.

        Args:
            robot_id: ID of robot to add

        Returns:
            bool: True if robot added successfully
        """
        if len(self.robots_working) >= self.max_workers:
            return False

        if robot_id not in self.robots_working:
            self.robots_working.append(robot_id)
            self._update_construction_speed()
            return True

        return False

    def remove_robot(self, robot_id):
        """
        Remove a robot from this construction site.

        Args:
            robot_id: ID of robot to remove
        """
        if robot_id in self.robots_working:
            self.robots_working.remove(robot_id)
            self._update_construction_speed()

    def _update_construction_speed(self):
        """Update construction speed based on number of workers."""
        # More robots = faster construction (diminishing returns)
        # 1 robot = 1x speed
        # 2 robots = 1.7x speed
        # 3 robots = 2.3x speed
        # 4 robots = 2.8x speed
        # 5 robots = 3.2x speed
        num_robots = max(len(self.robots_working), self.base_workers)

        if num_robots == 0:
            self.speed_multiplier = 0.0
        else:
            # Diminishing returns formula
            self.speed_multiplier = num_robots / (1.0 + (num_robots - 1) * 0.3)

    def deliver_material(self, material_type: str, quantity: float) -> float:
        """
        Deliver material to construction site.

        Args:
            material_type (str): Type of material
            quantity (float): Amount to deliver

        Returns:
            float: Amount actually accepted
        """
        if material_type not in self.required_materials:
            return 0.0

        required = self.required_materials[material_type]
        delivered = self.materials_delivered[material_type]
        needed = required - delivered

        amount_to_accept = min(quantity, needed)
        self.materials_delivered[material_type] += amount_to_accept

        return amount_to_accept

    def are_materials_satisfied(self) -> bool:
        """
        Check if all required materials have been delivered.

        Returns:
            bool: True if all materials delivered
        """
        for material_type, required in self.required_materials.items():
            delivered = self.materials_delivered[material_type]
            if delivered < required:
                return False
        return True

    def update(self, dt: float):
        """
        Update construction progress.

        Args:
            dt (float): Delta time in seconds
        """
        # Only progress if materials are satisfied
        if not self.are_materials_satisfied():
            return

        # Only progress if at least one robot is working (or base_workers = 0)
        if self.base_workers > 0 and len(self.robots_working) == 0:
            return

        # Update progress with speed multiplier
        effective_dt = dt * self.speed_multiplier
        self.time_remaining -= effective_dt
        self.progress = 1.0 - (self.time_remaining / self.construction_time)

        # Clamp progress
        if self.progress >= 1.0:
            self.progress = 1.0
            self.time_remaining = 0.0

    def is_complete(self) -> bool:
        """
        Check if construction is complete.

        Returns:
            bool: True if construction finished
        """
        return self.progress >= 1.0

    def cancel(self) -> Dict[str, float]:
        """
        Cancel construction and return delivered materials.

        Returns:
            Dict[str, float]: Materials to refund
        """
        self.canceled = True
        return self.materials_delivered.copy()

    def render(self, screen: pygame.Surface, camera):
        """
        Render construction site.

        Args:
            screen: Pygame surface
            camera: Camera for world-to-screen transformation
        """
        if not self.visible:
            return

        # Calculate screen position
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)

        if not camera.is_visible(self.x, self.y, self.width, self.height):
            return

        # Draw construction site outline
        site_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)

        # Dashed outline for construction
        dash_length = 8
        for i in range(0, self.width, dash_length * 2):
            pygame.draw.line(screen, self.outline_color,
                           (screen_x + i, screen_y),
                           (screen_x + min(i + dash_length, self.width), screen_y), 2)
            pygame.draw.line(screen, self.outline_color,
                           (screen_x + i, screen_y + self.height),
                           (screen_x + min(i + dash_length, self.width), screen_y + self.height), 2)

        for i in range(0, self.height, dash_length * 2):
            pygame.draw.line(screen, self.outline_color,
                           (screen_x, screen_y + i),
                           (screen_x, screen_y + min(i + dash_length, self.height)), 2)
            pygame.draw.line(screen, self.outline_color,
                           (screen_x + self.width, screen_y + i),
                           (screen_x + self.width, screen_y + min(i + dash_length, self.height)), 2)

        # Draw foundation based on progress
        if self.progress > 0.0:
            foundation_height = int(self.height * min(self.progress * 1.5, 1.0))
            foundation_rect = pygame.Rect(screen_x, screen_y + self.height - foundation_height,
                                        self.width, foundation_height)

            # Foundation color (lighter as progress increases)
            fade = 0.6 + (self.progress * 0.4)
            foundation_color = tuple(int(c * fade) for c in self.color)
            pygame.draw.rect(screen, foundation_color, foundation_rect)
            pygame.draw.rect(screen, self.outline_color, foundation_rect, 1)

        # Draw material status icons
        if self.required_materials and camera.zoom >= 0.5:
            self._render_material_status(screen, screen_x, screen_y)

        # Draw robot worker count
        if len(self.robots_working) > 0:
            self._render_worker_count(screen, screen_x, screen_y)

        # Draw progress bar
        self._render_progress_bar(screen, screen_x, screen_y)

    def _render_material_status(self, screen, screen_x, screen_y):
        """Render material requirement status."""
        icon_size = 8
        icon_spacing = 10
        start_x = screen_x + 4
        start_y = screen_y + 4

        for i, (material_type, required) in enumerate(self.required_materials.items()):
            delivered = self.materials_delivered[material_type]
            satisfied = delivered >= required

            icon_x = start_x + (i * icon_spacing)
            icon_y = start_y

            # Material icon (square)
            icon_color = (0, 255, 0) if satisfied else (255, 100, 0)
            pygame.draw.rect(screen, icon_color, (icon_x, icon_y, icon_size, icon_size))
            pygame.draw.rect(screen, (0, 0, 0), (icon_x, icon_y, icon_size, icon_size), 1)

    def _render_worker_count(self, screen, screen_x, screen_y):
        """Render number of robots working."""
        font = pygame.font.Font(None, 18)
        worker_text = f"👷 {len(self.robots_working)}/{self.max_workers}"
        text_surface = font.render(worker_text, True, (255, 255, 255))

        text_x = screen_x + self.width - text_surface.get_width() - 4
        text_y = screen_y + 4

        # Background
        bg_rect = text_surface.get_rect(topleft=(text_x, text_y))
        bg_rect.inflate_ip(4, 2)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)

        screen.blit(text_surface, (text_x, text_y))

    def _render_progress_bar(self, screen, screen_x, screen_y):
        """Render construction progress bar."""
        bar_width = self.width - 8
        bar_height = 8
        bar_x = screen_x + 4
        bar_y = screen_y + self.height - bar_height - 4

        # Background
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))

        # Progress fill
        fill_width = int(bar_width * self.progress)
        if fill_width > 0:
            pygame.draw.rect(screen, self.progress_color, (bar_x, bar_y, fill_width, bar_height))

        # Outline
        pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height), 1)

        # Progress percentage
        font = pygame.font.Font(None, 16)
        progress_text = f"{int(self.progress * 100)}%"
        text_surface = font.render(progress_text, True, (255, 255, 255))
        text_x = screen_x + (self.width - text_surface.get_width()) // 2
        text_y = bar_y - text_surface.get_height() - 2

        # Text background
        bg_rect = text_surface.get_rect(topleft=(text_x, text_y))
        bg_rect.inflate_ip(4, 2)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)

        screen.blit(text_surface, (text_x, text_y))

    def get_info(self) -> Dict:
        """
        Get construction site information.

        Returns:
            dict: Construction site info
        """
        return {
            'building_type': self.building_type,
            'position': (self.grid_x, self.grid_y),
            'size': (self.width_tiles, self.height_tiles),
            'progress': self.progress,
            'time_remaining': self.time_remaining,
            'workers': len(self.robots_working),
            'max_workers': self.max_workers,
            'materials_required': self.required_materials,
            'materials_delivered': self.materials_delivered,
            'materials_satisfied': self.are_materials_satisfied(),
        }

    def __repr__(self):
        """String representation for debugging."""
        return (f"ConstructionSite({self.building_type}, "
                f"progress={self.progress*100:.0f}%, "
                f"workers={len(self.robots_working)}, "
                f"pos=({self.grid_x}, {self.grid_y}))")
