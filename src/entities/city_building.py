"""
CityBuilding - Buildings in the city that can be deconstructed for materials.

These are different from the player's factory buildings. City buildings are
world objects that can be deconstructed by robots to collect materials.
"""

import pygame
from typing import Dict, Optional, Tuple


class CityBuilding:
    """
    Base class for city buildings (houses, stores, etc.).

    City buildings can be deconstructed to collect materials.
    Some are legal to deconstruct, others are illegal.
    """

    def __init__(self, grid_x: int, grid_y: int, width: int, height: int, building_type: str):
        """
        Initialize a city building.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
            width (int): Width in tiles
            height (int): Height in tiles
            building_type (str): Type of building
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

        # Visual
        self.color = (100, 100, 100)
        self.outline_color = (80, 80, 80)
        self.name = "City Building"

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
        Render the building.

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

        # Draw building
        pygame.draw.rect(screen, fill_color, (screen_x, screen_y, width_px, height_px))
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
        super().__init__(grid_x, grid_y, width=3, height=4, building_type='house')

        self.livable = livable

        if livable:
            # Livable house - ILLEGAL to deconstruct
            self.name = "Livable House"
            self.legal_to_deconstruct = False
            self.deconstruction_time = 120.0
            self.noise_level = 8
            self.color = (180, 140, 100)  # Brown/tan
            self.outline_color = (140, 100, 60)
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
            self.color = (120, 100, 80)  # Darker brown
            self.outline_color = (80, 60, 40)
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
        super().__init__(grid_x, grid_y, width=4, height=4, building_type='store')

        self.name = "Store"
        self.legal_to_deconstruct = False  # ILLEGAL
        self.deconstruction_time = 100.0
        self.noise_level = 7
        self.color = (150, 150, 200)  # Light blue
        self.outline_color = (100, 100, 150)
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
        super().__init__(grid_x, grid_y, width=5, height=5, building_type='office')

        self.name = "Office Building"
        self.legal_to_deconstruct = False  # ILLEGAL
        self.deconstruction_time = 150.0
        self.noise_level = 8
        self.color = (180, 180, 180)  # Gray
        self.outline_color = (120, 120, 120)
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
        super().__init__(grid_x, grid_y, width=6, height=6, building_type='city_factory')

        self.name = "Industrial Factory"
        self.legal_to_deconstruct = False  # ILLEGAL
        self.deconstruction_time = 200.0
        self.noise_level = 9
        self.color = (140, 140, 140)  # Dark gray
        self.outline_color = (80, 80, 80)
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
