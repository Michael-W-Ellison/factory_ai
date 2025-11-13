"""
BuildingManager - manages all buildings in the factory.
"""

from src.entities.building import Building


class BuildingManager:
    """
    Manages all buildings in the game.

    Handles placement, removal, updates, and rendering of buildings.
    """

    def __init__(self, grid):
        """
        Initialize the building manager.

        Args:
            grid: Grid object for placement validation
        """
        self.grid = grid
        self.buildings = {}  # building_id -> Building
        self.buildings_by_type = {}  # building_type -> list of buildings
        self.grid_occupancy = {}  # (grid_x, grid_y) -> building_id

    def place_building(self, building):
        """
        Place a building on the grid.

        Args:
            building (Building): Building to place

        Returns:
            bool: True if placement successful, False otherwise
        """
        # Check if location is valid
        if not self._is_valid_placement(building):
            print(f"Cannot place {building.name} at ({building.grid_x}, {building.grid_y}) - location blocked")
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

        print(f"Placed {building}")
        return True

    def remove_building(self, building_id):
        """
        Remove a building.

        Args:
            building_id: ID of building to remove

        Returns:
            bool: True if removal successful
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
        print(f"Removed {building}")
        return True

    def get_building_at(self, grid_x, grid_y):
        """
        Get building at grid position.

        Args:
            grid_x (int): Grid X coordinate
            grid_y (int): Grid Y coordinate

        Returns:
            Building or None: Building at position
        """
        building_id = self.grid_occupancy.get((grid_x, grid_y))
        if building_id:
            return self.buildings.get(building_id)
        return None

    def get_buildings_by_type(self, building_type):
        """
        Get all buildings of a specific type.

        Args:
            building_type (str): Type of building

        Returns:
            list: List of buildings
        """
        return self.buildings_by_type.get(building_type, [])

    def _is_valid_placement(self, building):
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

    def calculate_total_power_generation(self):
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

    def calculate_total_power_consumption(self):
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

    def update(self, dt):
        """
        Update all buildings.

        Args:
            dt (float): Delta time in seconds
        """
        for building in list(self.buildings.values()):
            building.update(dt)

    def render(self, screen, camera):
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

    def get_stats(self):
        """
        Get statistics about buildings.

        Returns:
            dict: Building statistics
        """
        return {
            'total_buildings': len(self.buildings),
            'by_type': {btype: len(blist) for btype, blist in self.buildings_by_type.items()},
            'total_power_generation': self.calculate_total_power_generation(),
            'total_power_consumption': self.calculate_total_power_consumption(),
        }

    def __repr__(self):
        """String representation for debugging."""
        return f"BuildingManager(buildings={len(self.buildings)})"
