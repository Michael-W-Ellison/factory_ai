"""
Building entity - base class for all factory buildings.
"""

import pygame
from src.entities.entity import Entity


class Building(Entity):
    """
    Base class for all buildings in the game.

    Buildings are stationary structures that perform various functions:
    - Processing materials
    - Generating/consuming power
    - Storing resources
    - Controlling robots
    """

    def __init__(self, grid_x, grid_y, width_tiles, height_tiles, building_type):
        """
        Initialize a building.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
            width_tiles (int): Width in tiles
            height_tiles (int): Height in tiles
            building_type (str): Type of building
        """
        # Convert grid position to world position
        from src.world.grid import Grid
        world_x = grid_x * 32  # Assuming 32px tile size
        world_y = grid_y * 32
        world_width = width_tiles * 32
        world_height = height_tiles * 32

        super().__init__(world_x, world_y, width=world_width, height=world_height)

        # Grid position and size
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.width_tiles = width_tiles
        self.height_tiles = height_tiles

        # Building properties
        self.building_type = building_type
        self.name = building_type
        self.level = 1
        self.max_level = 1

        # Construction
        self.construction_progress = 100.0  # 0-100%, 100 = complete
        self.construction_time = 0.0  # seconds
        self.under_construction = False

        # Power
        self.power_consumption = 0.0  # Power units per second
        self.power_generation = 0.0  # Power units per second
        self.powered = True  # Whether building has power

        # State
        self.operational = True  # Whether building is working
        self.health = 100.0  # 0-100%

        # Material processing
        self.input_queue = []  # Materials waiting to be processed
        self.output_queue = []  # Processed materials waiting for pickup
        self.processing_current = None  # Currently processing item
        self.processing_time_remaining = 0.0

        # Visual
        self.color = (100, 100, 100)  # Default gray
        self.outline_color = (80, 80, 80)

    def can_operate(self):
        """
        Check if building can currently operate.

        Returns:
            bool: True if building can operate
        """
        if self.under_construction:
            return False
        if not self.powered:
            return False
        if not self.operational:
            return False
        if self.health <= 0:
            return False
        return True

    def add_to_input_queue(self, material_type, quantity):
        """
        Add material to input queue for processing.

        Args:
            material_type (str): Type of material
            quantity (float): Amount in kg
        """
        self.input_queue.append({
            'material_type': material_type,
            'quantity': quantity
        })

    def get_output(self):
        """
        Get all processed materials from output queue.

        Returns:
            list: List of material dictionaries
        """
        output = self.output_queue.copy()
        self.output_queue.clear()
        return output

    def upgrade(self):
        """Upgrade building to next level."""
        if self.level < self.max_level:
            self.level += 1
            self._apply_level_bonuses()
            return True
        return False

    def _apply_level_bonuses(self):
        """Apply bonuses for current level (override in subclasses)."""
        pass

    def update(self, dt):
        """
        Update building state.

        Args:
            dt (float): Delta time in seconds
        """
        # Update construction progress
        if self.under_construction:
            self.construction_progress += (100.0 / self.construction_time) * dt
            if self.construction_progress >= 100.0:
                self.construction_progress = 100.0
                self.under_construction = False
                self.on_construction_complete()

        # Only operate if conditions are met
        if not self.can_operate():
            return

        # Process materials if available
        if self.processing_current is None and self.input_queue:
            self._start_processing()

        # Continue processing
        if self.processing_current is not None:
            self.processing_time_remaining -= dt
            if self.processing_time_remaining <= 0:
                self._finish_processing()

    def _start_processing(self):
        """Start processing the next item in queue (override in subclasses)."""
        pass

    def _finish_processing(self):
        """Finish processing current item (override in subclasses)."""
        pass

    def on_construction_complete(self):
        """Called when construction finishes."""
        print(f"{self.name} construction complete at ({self.grid_x}, {self.grid_y})")

    def _render_construction(self, screen, screen_x, screen_y, rect):
        """
        Render progressive construction states.

        Args:
            screen: Pygame surface
            screen_x (int): Screen X position
            screen_y (int): Screen Y position
            rect: Building rectangle
        """
        progress = self.construction_progress / 100.0

        # Stage 1 (0-25%): Foundation and base
        if progress < 0.25:
            # Ground/foundation
            foundation_height = int(self.height * 0.15)
            foundation_rect = pygame.Rect(screen_x, screen_y + self.height - foundation_height,
                                         self.width, foundation_height)
            pygame.draw.rect(screen, (80, 80, 80), foundation_rect)
            pygame.draw.rect(screen, (60, 60, 60), foundation_rect, 2)

            # Construction materials piles
            import random
            rng = random.Random(self.grid_x * 1000 + self.grid_y)
            for i in range(3):
                pile_x = screen_x + rng.randint(10, self.width - 20)
                pile_y = screen_y + self.height - rng.randint(10, 30)
                pile_size = rng.randint(4, 8)
                pygame.draw.circle(screen, (120, 100, 80), (pile_x, pile_y), pile_size)

        # Stage 2 (25-50%): Walls starting
        elif progress < 0.5:
            # Partial walls (rising from bottom)
            wall_progress = (progress - 0.25) / 0.25
            wall_height = int(self.height * wall_progress)
            wall_rect = pygame.Rect(screen_x, screen_y + self.height - wall_height,
                                    self.width, wall_height)

            # Wall color (lighter than final)
            construction_color = tuple(min(255, int(c * 1.3)) for c in self.color)
            pygame.draw.rect(screen, construction_color, wall_rect)

            # Wall outlines
            pygame.draw.rect(screen, (100, 100, 100), wall_rect, 2)

            # Vertical lines showing wall sections
            for i in range(1, 4):
                line_x = screen_x + (self.width // 4) * i
                pygame.draw.line(screen, (90, 90, 90),
                               (line_x, screen_y + self.height - wall_height),
                               (line_x, screen_y + self.height), 1)

        # Stage 3 (50-75%): Walls complete, adding details
        elif progress < 0.75:
            # Full walls
            pygame.draw.rect(screen, self.color, rect)
            pygame.draw.rect(screen, self.outline_color, rect, 2)

            # Scaffolding on sides
            scaffold_color = (150, 120, 80)
            scaffold_width = 6

            # Left scaffolding
            for i in range(0, self.height, 16):
                pygame.draw.rect(screen, scaffold_color,
                               (screen_x - scaffold_width, screen_y + i,
                                scaffold_width, 2))
                pygame.draw.line(screen, scaffold_color,
                               (screen_x - scaffold_width // 2, screen_y + i),
                               (screen_x - scaffold_width // 2, screen_y + i + 16), 2)

            # Right scaffolding
            for i in range(0, self.height, 16):
                pygame.draw.rect(screen, scaffold_color,
                               (screen_x + self.width, screen_y + i,
                                scaffold_width, 2))
                pygame.draw.line(screen, scaffold_color,
                               (screen_x + self.width + scaffold_width // 2, screen_y + i),
                               (screen_x + self.width + scaffold_width // 2, screen_y + i + 16), 2)

        # Stage 4 (75-100%): Nearly complete, minimal scaffolding
        else:
            # Complete building
            pygame.draw.rect(screen, self.color, rect)
            pygame.draw.rect(screen, self.outline_color, rect, 2)

            # Minimal scaffolding at top only
            scaffold_color = (150, 120, 80)
            scaffold_height = int(self.height * 0.2)

            # Top scaffolding
            pygame.draw.rect(screen, scaffold_color,
                           (screen_x, screen_y,
                            self.width, 3))
            for i in range(0, self.width, 20):
                pygame.draw.line(screen, scaffold_color,
                               (screen_x + i, screen_y),
                               (screen_x + i, screen_y + scaffold_height), 2)

        # Progress bar at bottom
        bar_width = self.width - 8
        bar_height = 6
        bar_x = screen_x + 4
        bar_y = screen_y + self.height - bar_height - 2

        # Background
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
        # Progress
        progress_width = int(bar_width * progress)
        pygame.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, progress_width, bar_height))

        # Progress percentage text
        font = pygame.font.Font(None, 20)
        progress_text = font.render(f"{int(progress * 100)}%", True, (255, 255, 255))
        text_x = screen_x + (self.width - progress_text.get_width()) // 2
        text_y = screen_y + self.height - bar_height - 18
        pygame.draw.rect(screen, (0, 0, 0), (text_x - 2, text_y - 2,
                                            progress_text.get_width() + 4,
                                            progress_text.get_height() + 4))
        screen.blit(progress_text, (text_x, text_y))

    def render(self, screen, camera):
        """
        Render building to screen.

        Args:
            screen: Pygame surface
            camera: Camera object
        """
        if not self.visible:
            return

        # Convert world coordinates to screen coordinates
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)

        if camera.is_visible(self.x, self.y, self.width, self.height):
            # Draw building body
            rect = pygame.Rect(screen_x, screen_y, self.width, self.height)

            # Different appearance if under construction
            if self.under_construction:
                self._render_construction(screen, screen_x, screen_y, rect)
            else:
                # Normal appearance
                building_color = self.color if self.powered else (50, 50, 50)
                pygame.draw.rect(screen, building_color, rect)

            # Outline
            outline_color = self.outline_color if self.powered else (30, 30, 30)
            pygame.draw.rect(screen, outline_color, rect, 2)

            # Power indicator (small dot in corner)
            if not self.under_construction:
                indicator_color = (0, 255, 0) if self.powered else (255, 0, 0)
                indicator_pos = (screen_x + self.width - 6, screen_y + 4)
                pygame.draw.circle(screen, indicator_color, indicator_pos, 3)

            # Level indicator (for upgraded buildings)
            if self.level > 1:
                font = pygame.font.Font(None, 20)
                level_text = font.render(f"L{self.level}", True, (255, 255, 0))
                screen.blit(level_text, (screen_x + 4, screen_y + 4))

    def get_info(self):
        """
        Get building information for UI.

        Returns:
            dict: Building information
        """
        return {
            'name': self.name,
            'type': self.building_type,
            'level': self.level,
            'position': (self.grid_x, self.grid_y),
            'size': (self.width_tiles, self.height_tiles),
            'power_consumption': self.power_consumption,
            'power_generation': self.power_generation,
            'powered': self.powered,
            'operational': self.operational,
            'health': self.health,
            'input_queue_size': len(self.input_queue),
            'output_queue_size': len(self.output_queue),
            'construction_progress': self.construction_progress,
        }

    def __repr__(self):
        """String representation for debugging."""
        return (f"{self.name}(level={self.level}, pos=({self.grid_x}, {self.grid_y}), "
                f"powered={self.powered})")
