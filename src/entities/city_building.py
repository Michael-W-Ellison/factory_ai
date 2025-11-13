"""
CityBuilding - Buildings in the city that can be deconstructed for materials.

These are different from the player's factory buildings. City buildings are
world objects that can be deconstructed by robots to collect materials.
"""

import pygame
import random
from typing import Dict, Optional, Tuple, List


class BuildingVisuals:
    """Manages visual variations for buildings to create unique appearances."""

    # Color palettes for different building types
    HOUSE_WALL_COLORS = [
        (180, 140, 100),  # Tan/brown
        (160, 120, 90),   # Dark tan
        (200, 160, 120),  # Light tan
        (140, 160, 140),  # Sage green
        (180, 170, 150),  # Beige
        (150, 130, 110),  # Brown
    ]

    HOUSE_ROOF_COLORS = [
        (100, 60, 40),    # Dark brown
        (80, 80, 100),    # Dark blue-gray
        (90, 50, 50),     # Dark red
        (60, 60, 60),     # Dark gray
        (70, 90, 70),     # Dark green
    ]

    DECREPIT_WALL_COLORS = [
        (120, 100, 80),   # Faded brown
        (100, 90, 80),    # Dull brown
        (110, 100, 90),   # Weathered gray-brown
        (90, 80, 70),     # Dark weathered
    ]

    STORE_COLORS = [
        (150, 150, 200),  # Light blue
        (200, 150, 150),  # Light red
        (150, 200, 150),  # Light green
        (200, 200, 150),  # Light yellow
        (180, 150, 200),  # Light purple
    ]

    OFFICE_COLORS = [
        (180, 180, 180),  # Light gray
        (160, 160, 170),  # Blue-gray
        (170, 165, 160),  # Warm gray
        (155, 155, 165),  # Cool gray
    ]

    FACTORY_COLORS = [
        (140, 140, 140),  # Gray
        (130, 130, 120),  # Brownish gray
        (120, 130, 140),  # Bluish gray
        (135, 125, 115),  # Warm gray
    ]

    WINDOW_COLORS = [
        (100, 150, 200),  # Light blue (glass)
        (120, 160, 200),  # Sky blue
        (80, 120, 160),   # Darker blue
        (90, 140, 180),   # Medium blue
    ]

    DOOR_COLORS = [
        (100, 60, 40),    # Brown
        (60, 40, 30),     # Dark brown
        (140, 80, 50),    # Light brown
        (80, 50, 40),     # Reddish brown
        (120, 120, 120),  # Gray
    ]

    @staticmethod
    def generate_house_visuals(grid_x: int, grid_y: int, livable: bool) -> Dict:
        """Generate visual variation for a house."""
        # Use position as seed for reproducibility
        rng = random.Random(grid_x * 1000 + grid_y)

        if livable:
            wall_color = rng.choice(BuildingVisuals.HOUSE_WALL_COLORS)
            roof_color = rng.choice(BuildingVisuals.HOUSE_ROOF_COLORS)
            window_color = rng.choice(BuildingVisuals.WINDOW_COLORS)
            door_color = rng.choice(BuildingVisuals.DOOR_COLORS)
            outline_color = tuple(max(0, c - 40) for c in wall_color)

            # Window pattern (rows and columns)
            window_pattern = rng.choice([
                {'rows': 2, 'cols': 2},
                {'rows': 2, 'cols': 3},
                {'rows': 3, 'cols': 2},
            ])

            # Door position (0=left, 1=center, 2=right)
            door_position = rng.randint(0, 2)

        else:
            # Decrepit house - darker, faded colors
            wall_color = rng.choice(BuildingVisuals.DECREPIT_WALL_COLORS)
            roof_color = tuple(max(0, c - 20) for c in rng.choice(BuildingVisuals.HOUSE_ROOF_COLORS))
            window_color = (60, 60, 60)  # Broken/boarded windows
            door_color = (50, 40, 30)
            outline_color = (50, 40, 30)

            window_pattern = {'rows': 2, 'cols': 2}
            door_position = rng.randint(0, 2)

        return {
            'wall_color': wall_color,
            'roof_color': roof_color,
            'window_color': window_color,
            'door_color': door_color,
            'outline_color': outline_color,
            'window_pattern': window_pattern,
            'door_position': door_position,
            'has_chimney': rng.random() < 0.6,
        }

    @staticmethod
    def generate_store_visuals(grid_x: int, grid_y: int) -> Dict:
        """Generate visual variation for a store."""
        rng = random.Random(grid_x * 1000 + grid_y)

        wall_color = rng.choice(BuildingVisuals.STORE_COLORS)
        outline_color = tuple(max(0, c - 40) for c in wall_color)
        window_color = rng.choice(BuildingVisuals.WINDOW_COLORS)
        door_color = rng.choice(BuildingVisuals.DOOR_COLORS)

        # Stores have large display windows
        window_pattern = {'rows': 1, 'cols': 3, 'large': True}
        door_position = rng.randint(0, 1)  # Left or center

        # Awning color (slightly darker than wall)
        awning_color = tuple(max(0, int(c * 0.7)) for c in wall_color)

        return {
            'wall_color': wall_color,
            'outline_color': outline_color,
            'window_color': window_color,
            'door_color': door_color,
            'window_pattern': window_pattern,
            'door_position': door_position,
            'has_awning': rng.random() < 0.7,
            'awning_color': awning_color,
        }

    @staticmethod
    def generate_office_visuals(grid_x: int, grid_y: int) -> Dict:
        """Generate visual variation for an office building."""
        rng = random.Random(grid_x * 1000 + grid_y)

        wall_color = rng.choice(BuildingVisuals.OFFICE_COLORS)
        outline_color = tuple(max(0, c - 30) for c in wall_color)
        window_color = rng.choice(BuildingVisuals.WINDOW_COLORS)
        door_color = (100, 100, 100)  # Gray glass door

        # Office buildings have regular grid of windows
        window_pattern = rng.choice([
            {'rows': 3, 'cols': 3},
            {'rows': 4, 'cols': 3},
            {'rows': 3, 'cols': 4},
        ])

        door_position = 1  # Center

        return {
            'wall_color': wall_color,
            'outline_color': outline_color,
            'window_color': window_color,
            'door_color': door_color,
            'window_pattern': window_pattern,
            'door_position': door_position,
        }

    @staticmethod
    def generate_factory_visuals(grid_x: int, grid_y: int) -> Dict:
        """Generate visual variation for a factory."""
        rng = random.Random(grid_x * 1000 + grid_y)

        wall_color = rng.choice(BuildingVisuals.FACTORY_COLORS)
        outline_color = tuple(max(0, c - 25) for c in wall_color)
        window_color = (80, 80, 80)  # Industrial windows
        door_color = (120, 100, 80)  # Metal door

        # Fewer, larger windows
        window_pattern = {'rows': 2, 'cols': 3, 'industrial': True}
        door_position = rng.randint(0, 1)

        return {
            'wall_color': wall_color,
            'outline_color': outline_color,
            'window_color': window_color,
            'door_color': door_color,
            'window_pattern': window_pattern,
            'door_position': door_position,
            'has_smokestack': rng.random() < 0.5,
        }


class CityBuilding:
    """
    Base class for city buildings (houses, stores, etc.).

    City buildings can be deconstructed to collect materials.
    Some are legal to deconstruct, others are illegal.
    """

    def __init__(self, grid_x: int, grid_y: int, width: int, height: int, building_type: str, visuals: Optional[Dict] = None):
        """
        Initialize a city building.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
            width (int): Width in tiles
            height (int): Height in tiles
            building_type (str): Type of building
            visuals (dict, optional): Visual variation data
        """
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.width = width
        self.height = height
        self.building_type = building_type

        # Deconstruction
        self.legal_to_deconstruct = False
        self.deconstruction_time = 0.0  # Seconds to fully deconstruct
        self.noise_level = 0  # 0-10 scale
        self.being_deconstructed = False
        self.deconstruction_progress = 0.0  # 0.0-1.0

        # Materials contained
        self.materials: Dict[str, float] = {}  # material_type -> quantity (kg)

        # Visual (defaults, will be overridden by visuals)
        self.color = (100, 100, 100)
        self.outline_color = (80, 80, 80)
        self.name = "City Building"

        # Visual variations
        self.visuals = visuals or {}
        if self.visuals:
            self.color = self.visuals.get('wall_color', self.color)
            self.outline_color = self.visuals.get('outline_color', self.outline_color)

        # NPCs
        self.max_occupants = 0
        self.current_occupants = []

    def start_deconstruction(self) -> bool:
        """
        Start deconstructing this building.

        Returns:
            bool: True if deconstruction started
        """
        if self.being_deconstructed:
            return False

        if not self.legal_to_deconstruct:
            # Illegal deconstruction increases suspicion (handled by detection system)
            pass

        self.being_deconstructed = True
        self.deconstruction_progress = 0.0
        return True

    def update_deconstruction(self, dt: float) -> bool:
        """
        Update deconstruction progress.

        Args:
            dt (float): Delta time in seconds

        Returns:
            bool: True if deconstruction complete
        """
        if not self.being_deconstructed:
            return False

        if self.deconstruction_time <= 0:
            self.being_deconstructed = False
            return True

        # Update progress
        progress_rate = dt / self.deconstruction_time
        self.deconstruction_progress += progress_rate

        # Check if complete
        if self.deconstruction_progress >= 1.0:
            self.being_deconstructed = False
            self.deconstruction_progress = 1.0
            return True

        return False

    def get_materials(self) -> Dict[str, float]:
        """
        Get materials from this building (when fully deconstructed).

        Returns:
            dict: material_type -> quantity (kg)
        """
        return self.materials.copy()

    def get_bounds(self) -> Tuple[int, int, int, int]:
        """
        Get building bounds in grid coordinates.

        Returns:
            tuple: (x, y, width, height)
        """
        return (self.grid_x, self.grid_y, self.width, self.height)

    def contains_point(self, grid_x: int, grid_y: int) -> bool:
        """
        Check if point is inside building.

        Args:
            grid_x (int): Grid X coordinate
            grid_y (int): Grid Y coordinate

        Returns:
            bool: True if point is inside
        """
        return (self.grid_x <= grid_x < self.grid_x + self.width and
                self.grid_y <= grid_y < self.grid_y + self.height)

    def render(self, screen: pygame.Surface, camera, tile_size: int):
        """
        Render the building with detailed visual components.

        Args:
            screen: Pygame surface
            camera: Camera for world-to-screen transformation
            tile_size (int): Size of tiles in pixels
        """
        # Calculate screen position
        world_x = self.grid_x * tile_size
        world_y = self.grid_y * tile_size
        screen_x, screen_y = camera.world_to_screen(world_x, world_y)

        # Calculate size
        width_px = self.width * tile_size
        height_px = self.height * tile_size

        # Apply camera zoom
        width_px = int(width_px * camera.zoom)
        height_px = int(height_px * camera.zoom)

        # Don't render if off screen
        if (screen_x + width_px < 0 or screen_x > screen.get_width() or
            screen_y + height_px < 0 or screen_y > screen.get_height()):
            return

        # Fill color (show progress if being deconstructed)
        fill_color = self.color
        if self.being_deconstructed:
            # Fade to darker as deconstruction progresses
            fade = 1.0 - (self.deconstruction_progress * 0.5)
            fill_color = tuple(int(c * fade) for c in self.color)

        # Draw main building body
        pygame.draw.rect(screen, fill_color, (screen_x, screen_y, width_px, height_px))

        # Draw roof if specified
        if self.visuals.get('roof_color'):
            roof_color = self.visuals['roof_color']
            if self.being_deconstructed:
                fade = 1.0 - (self.deconstruction_progress * 0.5)
                roof_color = tuple(int(c * fade) for c in roof_color)

            roof_height = int(height_px * 0.2)
            # Simple peaked roof
            roof_points = [
                (screen_x, screen_y),
                (screen_x + width_px // 2, screen_y - roof_height),
                (screen_x + width_px, screen_y),
            ]
            pygame.draw.polygon(screen, roof_color, roof_points)
            pygame.draw.polygon(screen, self.outline_color, roof_points, 2)

        # Draw chimney if specified
        if self.visuals.get('has_chimney'):
            chimney_width = max(3, int(width_px * 0.1))
            chimney_height = max(6, int(height_px * 0.25))
            chimney_x = screen_x + int(width_px * 0.7)
            chimney_y = screen_y - chimney_height
            if self.visuals.get('roof_color'):
                chimney_y -= int(height_px * 0.2)
            chimney_color = tuple(max(0, c - 30) for c in fill_color)
            pygame.draw.rect(screen, chimney_color, (chimney_x, chimney_y, chimney_width, chimney_height))
            pygame.draw.rect(screen, self.outline_color, (chimney_x, chimney_y, chimney_width, chimney_height), 1)

        # Draw awning if specified
        if self.visuals.get('has_awning'):
            awning_color = self.visuals['awning_color']
            awning_height = max(3, int(height_px * 0.1))
            awning_y = screen_y + int(height_px * 0.3)
            pygame.draw.rect(screen, awning_color, (screen_x, awning_y, width_px, awning_height))
            pygame.draw.rect(screen, self.outline_color, (screen_x, awning_y, width_px, awning_height), 1)

        # Draw smokestack if specified
        if self.visuals.get('has_smokestack'):
            stack_width = max(4, int(width_px * 0.12))
            stack_height = max(10, int(height_px * 0.4))
            stack_x = screen_x + int(width_px * 0.75)
            stack_y = screen_y - stack_height
            stack_color = (80, 80, 80)
            pygame.draw.rect(screen, stack_color, (stack_x, stack_y, stack_width, stack_height))
            pygame.draw.rect(screen, (60, 60, 60), (stack_x, stack_y, stack_width, stack_height), 1)

        # Draw windows
        window_pattern = self.visuals.get('window_pattern', {})
        window_color = self.visuals.get('window_color', (100, 150, 200))
        if window_pattern:
            self._draw_windows(screen, screen_x, screen_y, width_px, height_px, window_pattern, window_color)

        # Draw door
        door_color = self.visuals.get('door_color', (100, 60, 40))
        door_position = self.visuals.get('door_position', 1)
        self._draw_door(screen, screen_x, screen_y, width_px, height_px, door_color, door_position)

        # Draw outline
        pygame.draw.rect(screen, self.outline_color, (screen_x, screen_y, width_px, height_px), 2)

        # Show deconstruction progress
        if self.being_deconstructed:
            bar_width = width_px - 4
            bar_height = 6
            bar_x = screen_x + 2
            bar_y = screen_y + 2

            # Background
            pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            # Progress
            progress_width = int(bar_width * self.deconstruction_progress)
            pygame.draw.rect(screen, (255, 200, 0), (bar_x, bar_y, progress_width, bar_height))

    def _draw_windows(self, screen, base_x, base_y, width, height, pattern, color):
        """Draw windows based on pattern."""
        rows = pattern.get('rows', 2)
        cols = pattern.get('cols', 2)
        large = pattern.get('large', False)
        industrial = pattern.get('industrial', False)

        # Calculate window size and spacing
        if large:
            window_width = int(width / cols * 0.7)
            window_height = int(height * 0.25)
            margin_x = (width - (window_width * cols)) // (cols + 1)
            margin_y = int(height * 0.15)
            start_y = base_y + margin_y
        elif industrial:
            window_width = int(width / cols * 0.6)
            window_height = int(height / rows * 0.5)
            margin_x = (width - (window_width * cols)) // (cols + 1)
            margin_y = (height - (window_height * rows)) // (rows + 1)
            start_y = base_y + margin_y
        else:
            window_width = max(4, int(width / (cols + 2) * 0.8))
            window_height = max(4, int(height / (rows + 3) * 0.7))
            margin_x = (width - (window_width * cols)) // (cols + 1)
            margin_y = (height - (window_height * rows)) // (rows + 2)
            start_y = base_y + margin_y

        # Draw windows
        for row in range(rows):
            for col in range(cols):
                win_x = base_x + margin_x + col * (window_width + margin_x)
                win_y = start_y + row * (window_height + margin_y)

                # Window frame
                pygame.draw.rect(screen, (40, 40, 40), (win_x, win_y, window_width, window_height))
                # Window glass
                pygame.draw.rect(screen, color, (win_x + 1, win_y + 1, window_width - 2, window_height - 2))

    def _draw_door(self, screen, base_x, base_y, width, height, color, position):
        """Draw door at specified position."""
        door_width = max(6, int(width * 0.25))
        door_height = max(8, int(height * 0.35))

        # Position: 0=left, 1=center, 2=right
        if position == 0:
            door_x = base_x + int(width * 0.15)
        elif position == 1:
            door_x = base_x + (width - door_width) // 2
        else:
            door_x = base_x + width - int(width * 0.15) - door_width

        door_y = base_y + height - door_height - 2

        # Door
        pygame.draw.rect(screen, color, (door_x, door_y, door_width, door_height))
        pygame.draw.rect(screen, (40, 40, 40), (door_x, door_y, door_width, door_height), 1)

        # Door knob
        knob_size = max(2, int(door_width * 0.15))
        knob_x = door_x + door_width - knob_size - 2
        knob_y = door_y + door_height // 2
        pygame.draw.circle(screen, (200, 180, 100), (knob_x, knob_y), knob_size)

    def __repr__(self):
        """String representation for debugging."""
        legal = "legal" if self.legal_to_deconstruct else "illegal"
        return f"{self.name}({legal}, pos=({self.grid_x}, {self.grid_y}))"


class House(CityBuilding):
    """House building - can be livable or decrepit."""

    def __init__(self, grid_x: int, grid_y: int, livable: bool = True):
        """
        Initialize a house.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
            livable (bool): True for livable house, False for decrepit
        """
        # Generate visual variations
        visuals = BuildingVisuals.generate_house_visuals(grid_x, grid_y, livable)

        super().__init__(grid_x, grid_y, width=3, height=4, building_type='house', visuals=visuals)

        self.livable = livable

        if livable:
            # Livable house - ILLEGAL to deconstruct
            self.name = "Livable House"
            self.legal_to_deconstruct = False
            self.deconstruction_time = 120.0
            self.noise_level = 8
            self.max_occupants = 4

            # Materials (better quality, more materials)
            self.materials = {
                'wood': 80.0,
                'concrete': 40.0,
                'steel': 20.0,
                'glass': 15.0,
                'plastic': 10.0,
                'copper': 8.0,  # Wiring
                'electronic': 5.0  # Appliances
            }

        else:
            # Decrepit house - LEGAL to deconstruct
            self.name = "Decrepit House"
            self.legal_to_deconstruct = True
            self.deconstruction_time = 60.0
            self.noise_level = 6
            self.max_occupants = 0

            # Materials (lower quality, more waste)
            self.materials = {
                'wood': 40.0,
                'concrete': 20.0,
                'steel': 8.0,
                'glass': 5.0,
                'plastic': 4.0,
                'rubber': 3.0,
                # 44% of materials are unusable junk (not included)
            }


class Store(CityBuilding):
    """Store building - commercial."""

    def __init__(self, grid_x: int, grid_y: int):
        """
        Initialize a store.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        # Generate visual variations
        visuals = BuildingVisuals.generate_store_visuals(grid_x, grid_y)

        super().__init__(grid_x, grid_y, width=4, height=4, building_type='store', visuals=visuals)

        self.name = "Store"
        self.legal_to_deconstruct = False  # ILLEGAL
        self.deconstruction_time = 100.0
        self.noise_level = 7
        self.max_occupants = 5

        # Materials
        self.materials = {
            'wood': 60.0,
            'concrete': 50.0,
            'steel': 30.0,
            'glass': 40.0,  # Display windows
            'plastic': 25.0,  # Merchandise
            'paper': 20.0,  # Packaging
            'electronic': 15.0  # Cash registers, etc.
        }


class Office(CityBuilding):
    """Office building - commercial."""

    def __init__(self, grid_x: int, grid_y: int):
        """
        Initialize an office building.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        # Generate visual variations
        visuals = BuildingVisuals.generate_office_visuals(grid_x, grid_y)

        super().__init__(grid_x, grid_y, width=5, height=5, building_type='office', visuals=visuals)

        self.name = "Office Building"
        self.legal_to_deconstruct = False  # ILLEGAL
        self.deconstruction_time = 150.0
        self.noise_level = 8
        self.max_occupants = 10

        # Materials
        self.materials = {
            'wood': 50.0,
            'concrete': 80.0,
            'steel': 40.0,
            'glass': 60.0,
            'plastic': 30.0,
            'paper': 40.0,  # Documents
            'electronic': 35.0,  # Computers, printers
            'copper': 15.0  # Wiring
        }


class CityFactory(CityBuilding):
    """Industrial factory building - different from player's factory."""

    def __init__(self, grid_x: int, grid_y: int):
        """
        Initialize a city factory.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        # Generate visual variations
        visuals = BuildingVisuals.generate_factory_visuals(grid_x, grid_y)

        super().__init__(grid_x, grid_y, width=6, height=6, building_type='city_factory', visuals=visuals)

        self.name = "Industrial Factory"
        self.legal_to_deconstruct = False  # ILLEGAL
        self.deconstruction_time = 200.0
        self.noise_level = 9
        self.max_occupants = 6

        # Materials (heavy industrial)
        self.materials = {
            'wood': 40.0,
            'concrete': 120.0,
            'steel': 100.0,
            'glass': 30.0,
            'plastic': 40.0,
            'metal': 80.0,  # Various metals
            'copper': 30.0,
            'electronic': 25.0,
            'rubber': 20.0
        }


class PoliceStation(CityBuilding):
    """Police station - cannot be deconstructed."""

    def __init__(self, grid_x: int, grid_y: int):
        """
        Initialize a police station.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        super().__init__(grid_x, grid_y, width=5, height=5, building_type='police_station')

        self.name = "Police Station"
        self.legal_to_deconstruct = False  # Cannot deconstruct at all
        self.deconstruction_time = 9999.0  # Effectively impossible
        self.noise_level = 10
        self.color = (100, 100, 200)  # Blue
        self.outline_color = (50, 50, 150)
        self.max_occupants = 15

        # No materials - cannot be deconstructed
        self.materials = {}

    def start_deconstruction(self) -> bool:
        """Police station cannot be deconstructed."""
        return False
