"""
BuildingManager - manages all buildings in the factory.

Provides:
- Building placement and removal
- Grid occupancy tracking
- Building updates and rendering
- Research effect application
"""

from typing import Dict, List, Optional, Tuple, Any
import pygame

from src.core.logger import get_logger
from src.entities.building import Building

logger = get_logger(__name__)


class BuildingManager:
    """
    Manages all buildings in the game.

    Handles placement, removal, updates, and rendering of buildings.
    """

    def __init__(self, grid) -> None:
        """
        Initialize the building manager.

        Args:
            grid: Grid object for placement validation
        """
        self.grid = grid
        self.buildings: Dict[str, Building] = {}
        self.buildings_by_type: Dict[str, List[Building]] = {}
        self.grid_occupancy: Dict[Tuple[int, int], str] = {}

    def place_building(self, building: Building) -> bool:
        """
        Place a building on the grid.

        Args:
            building (Building): Building to place

        Returns:
            bool: True if placement successful, False otherwise
        """
        # Check if location is valid
        if not self._is_valid_placement(building):
            logger.warning(f"Cannot place {building.name} at ({building.grid_x}, {building.grid_y}) - location blocked")
            return False

        # Add to buildings dictionary
        self.buildings[building.id] = building

        # Add to type-based dictionary
        if building.building_type not in self.buildings_by_type:
            self.buildings_by_type[building.building_type] = []
        self.buildings_by_type[building.building_type].append(building)

        # Mark grid tiles as occupied
        for dy in range(building.height_tiles):
            for dx in range(building.width_tiles):
                grid_x = building.grid_x + dx
                grid_y = building.grid_y + dy
                self.grid_occupancy[(grid_x, grid_y)] = building.id

                # Mark tile as occupied in grid
                tile = self.grid.get_tile(grid_x, grid_y)
                if tile:
                    tile.occupied = True

        logger.debug(f"Placed {building}")
        return True

    def remove_building(self, building_id: str) -> bool:
        """
        Remove a building.

        Args:
            building_id: ID of building to remove

        Returns:
            True if removal successful
        """
        if building_id not in self.buildings:
            return False

        building = self.buildings[building_id]

        # Remove from type dictionary
        if building.building_type in self.buildings_by_type:
            self.buildings_by_type[building.building_type].remove(building)

        # Free grid tiles
        for dy in range(building.height_tiles):
            for dx in range(building.width_tiles):
                grid_x = building.grid_x + dx
                grid_y = building.grid_y + dy
                if (grid_x, grid_y) in self.grid_occupancy:
                    del self.grid_occupancy[(grid_x, grid_y)]

                # Mark tile as unoccupied
                tile = self.grid.get_tile(grid_x, grid_y)
                if tile:
                    tile.occupied = False

        # Remove building
        del self.buildings[building_id]
        logger.debug(f"Removed {building}")
        return True

    def get_building_at(self, grid_x: int, grid_y: int) -> Optional[Building]:
        """
        Get building at grid position.

        Args:
            grid_x (int): Grid X coordinate
            grid_y (int): Grid Y coordinate

        Returns:
            Building or None: Building at position
        """
        building_id = self.grid_occupancy.get((grid_x, grid_y))
        if building_id is not None:  # Fix: building_id can be 0 which is falsy
            return self.buildings.get(building_id)
        return None

    def get_buildings_by_type(self, building_type: str) -> List[Building]:
        """
        Get all buildings of a specific type.

        Args:
            building_type (str): Type of building

        Returns:
            list: List of buildings
        """
        return self.buildings_by_type.get(building_type, [])

    def _is_valid_placement(self, building: Building) -> bool:
        """
        Check if building can be placed at its position.

        Args:
            building (Building): Building to check

        Returns:
            bool: True if placement is valid
        """
        # Check all tiles the building will occupy
        for dy in range(building.height_tiles):
            for dx in range(building.width_tiles):
                grid_x = building.grid_x + dx
                grid_y = building.grid_y + dy

                # Check if tile exists
                tile = self.grid.get_tile(grid_x, grid_y)
                if tile is None:
                    return False

                # Check if tile is already occupied
                if tile.occupied:
                    return False

                # Check if tile is walkable (optional - can place on any tile)
                # For now, allow placement anywhere

        return True

    def calculate_total_power_generation(self) -> float:
        """
        Calculate total power generation from all buildings.

        Returns:
            float: Total power generation in units/second
        """
        total = 0.0
        for building in self.buildings.values():
            if building.can_operate():
                total += building.power_generation
        return total

    def calculate_total_power_consumption(self) -> float:
        """
        Calculate total power consumption from all buildings.

        Returns:
            float: Total power consumption in units/second
        """
        total = 0.0
        for building in self.buildings.values():
            if building.operational:  # Include even unpowered buildings
                total += building.power_consumption
        return total

    def update(self, dt: float) -> None:
        """
        Update all buildings.

        Args:
            dt (float): Delta time in seconds
        """
        for building in list(self.buildings.values()):
            building.update(dt)

    def render(self, screen: pygame.Surface, camera) -> None:
        """
        Render all buildings.

        Args:
            screen: Pygame surface
            camera: Camera object
        """
        # Render buildings sorted by Y position for proper layering
        sorted_buildings = sorted(self.buildings.values(), key=lambda b: b.y)
        for building in sorted_buildings:
            building.render(screen, camera)

    def get_building_counts(self) -> Dict[str, int]:
        """
        Get count of buildings by type.

        Returns:
            dict: Building type -> count
        """
        return {btype: len(blist) for btype, blist in self.buildings_by_type.items()}

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about buildings.

        Returns:
            dict: Building statistics
        """
        return {
            'total_buildings': len(self.buildings),
            'by_type': self.get_building_counts(),
            'total_power_generation': self.calculate_total_power_generation(),
            'total_power_consumption': self.calculate_total_power_consumption(),
        }

    def apply_research_effects_to_buildings(self, research_manager) -> None:
        """
        Apply research effects to all buildings that support it.

        Args:
            research_manager: ResearchManager instance
        """
        for building in self.buildings.values():
            # Check if building has apply_research_effects method
            if hasattr(building, 'apply_research_effects'):
                building.apply_research_effects(research_manager)

    def __repr__(self):
        """String representation for debugging."""
        return f"BuildingManager(buildings={len(self.buildings)})"
