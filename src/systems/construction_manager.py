"""
ConstructionManager - manages building construction queue and sites.

Handles:
- Construction queue
- Construction site placement
- Robot assignment to construction sites
- Material delivery tracking
- Construction completion
"""

from typing import List, Dict, Optional, Tuple
from src.entities.construction_site import ConstructionSite


class ConstructionOrder:
    """Represents a queued construction order."""

    def __init__(self, building_type: str, grid_x: int, grid_y: int, width_tiles: int,
                 height_tiles: int, construction_time: float, cost: float,
                 required_materials: Optional[Dict[str, float]] = None):
        """
        Initialize a construction order.

        Args:
            building_type (str): Type of building
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
            width_tiles (int): Width in tiles
            height_tiles (int): Height in tiles
            construction_time (float): Time to construct in seconds
            cost (float): Money cost
            required_materials (Dict[str, float]): Materials needed
        """
        self.building_type = building_type
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.width_tiles = width_tiles
        self.height_tiles = height_tiles
        self.construction_time = construction_time
        self.cost = cost
        self.required_materials = required_materials or {}

        # State
        self.id = id(self)
        self.started = False
        self.construction_site: Optional[ConstructionSite] = None


class ConstructionManager:
    """
    Manages construction queue and active construction sites.

    Handles queuing buildings, placing construction sites,
    assigning robots, and completing construction.
    """

    def __init__(self, building_manager, resource_manager, grid):
        """
        Initialize construction manager.

        Args:
            building_manager: BuildingManager instance
            resource_manager: ResourceManager instance
            grid: World grid
        """
        self.building_manager = building_manager
        self.resource_manager = resource_manager
        self.grid = grid

        # Construction queue
        self.queue: List[ConstructionOrder] = []

        # Active construction sites
        self.active_sites: List[ConstructionSite] = []

        # Maximum concurrent constructions
        self.max_concurrent = 3

    def queue_construction(self, building_type: str, grid_x: int, grid_y: int,
                          width_tiles: int, height_tiles: int, construction_time: float,
                          cost: float, required_materials: Optional[Dict[str, float]] = None) -> Tuple[bool, str]:
        """
        Add a building to the construction queue.

        Args:
            building_type (str): Type of building
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
            width_tiles (int): Width in tiles
            height_tiles (int): Height in tiles
            construction_time (float): Construction time in seconds
            cost (float): Money cost
            required_materials (Dict[str, float]): Required materials

        Returns:
            Tuple[bool, str]: (success, message)
        """
        # Check if location is valid
        if not self._is_valid_location(grid_x, grid_y, width_tiles, height_tiles):
            return False, "Invalid location - already occupied or out of bounds"

        # Check if player can afford it
        if hasattr(self.resource_manager, 'money') and self.resource_manager.money < cost:
            return False, f"Insufficient funds - need ${cost:.0f}"

        # Create construction order
        order = ConstructionOrder(
            building_type=building_type,
            grid_x=grid_x,
            grid_y=grid_y,
            width_tiles=width_tiles,
            height_tiles=height_tiles,
            construction_time=construction_time,
            cost=cost,
            required_materials=required_materials
        )

        # Add to queue
        self.queue.append(order)

        # Deduct cost
        if hasattr(self.resource_manager, 'money'):
            self.resource_manager.money -= cost

        return True, f"Queued {building_type} construction"

    def cancel_construction(self, order_id: int) -> Tuple[bool, str]:
        """
        Cancel a queued or active construction.

        Args:
            order_id: ID of construction order

        Returns:
            Tuple[bool, str]: (success, message)
        """
        # Check queue
        for order in self.queue:
            if order.id == order_id:
                # Refund cost
                if hasattr(self.resource_manager, 'money'):
                    self.resource_manager.money += order.cost

                # Refund delivered materials
                if order.construction_site:
                    refunded_materials = order.construction_site.cancel()
                    for material_type, quantity in refunded_materials.items():
                        self.resource_manager.add_material(material_type, quantity)

                # Remove from queue
                self.queue.remove(order)
                return True, "Construction canceled - refunded"

        # Check active sites
        for site in self.active_sites:
            if site.id == order_id:
                # Find corresponding order
                for order in self.queue:
                    if order.construction_site == site:
                        # Refund
                        if hasattr(self.resource_manager, 'money'):
                            self.resource_manager.money += order.cost

                        refunded_materials = site.cancel()
                        for material_type, quantity in refunded_materials.items():
                            self.resource_manager.add_material(material_type, quantity)

                        # Remove
                        self.active_sites.remove(site)
                        self.queue.remove(order)
                        return True, "Construction canceled - refunded"

        return False, "Construction not found"

    def _is_valid_location(self, grid_x: int, grid_y: int, width: int, height: int) -> bool:
        """
        Check if location is valid for construction.

        Args:
            grid_x (int): Grid X
            grid_y (int): Grid Y
            width (int): Width in tiles
            height (int): Height in tiles

        Returns:
            bool: True if valid
        """
        # Check all tiles
        for dy in range(height):
            for dx in range(width):
                tile_x = grid_x + dx
                tile_y = grid_y + dy

                # Check bounds
                tile = self.grid.get_tile(tile_x, tile_y)
                if tile is None:
                    return False

                # Check occupied
                if tile.occupied:
                    return False

                # Check if there's already a building or construction site
                if self.building_manager.get_building_at(tile_x, tile_y):
                    return False

        # Check for overlapping queued constructions
        for order in self.queue:
            if self._rectangles_overlap(grid_x, grid_y, width, height,
                                       order.grid_x, order.grid_y,
                                       order.width_tiles, order.height_tiles):
                return False

        return True

    def _rectangles_overlap(self, x1: int, y1: int, w1: int, h1: int,
                           x2: int, y2: int, w2: int, h2: int) -> bool:
        """Check if two rectangles overlap."""
        return not (x1 + w1 <= x2 or  # r1 is left of r2
                   x2 + w2 <= x1 or  # r2 is left of r1
                   y1 + h1 <= y2 or  # r1 is above r2
                   y2 + h2 <= y1)    # r2 is above r1

    def update(self, dt: float):
        """
        Update construction manager.

        Args:
            dt (float): Delta time in seconds
        """
        # Start queued constructions if under max concurrent
        while (len(self.active_sites) < self.max_concurrent and
               len(self.queue) > 0):
            order = self.queue[0]
            if not order.started:
                self._start_construction(order)

        # Update active construction sites
        for site in self.active_sites[:]:
            site.update(dt)

            # Check if complete
            if site.is_complete():
                self._complete_construction(site)

    def _start_construction(self, order: ConstructionOrder):
        """
        Start construction for an order.

        Args:
            order: ConstructionOrder to start
        """
        # Create construction site
        site = ConstructionSite(
            grid_x=order.grid_x,
            grid_y=order.grid_y,
            width_tiles=order.width_tiles,
            height_tiles=order.height_tiles,
            building_type=order.building_type,
            construction_time=order.construction_time,
            required_materials=order.required_materials
        )

        # Mark location as occupied
        for dy in range(order.height_tiles):
            for dx in range(order.width_tiles):
                tile = self.grid.get_tile(order.grid_x + dx, order.grid_y + dy)
                if tile:
                    tile.occupied = True

        # Add to active sites
        self.active_sites.append(site)
        order.construction_site = site
        order.started = True

        print(f"Started construction: {order.building_type} at ({order.grid_x}, {order.grid_y})")

    def _complete_construction(self, site: ConstructionSite):
        """
        Complete construction and create the building.

        Args:
            site: Completed ConstructionSite
        """
        # Find the order
        order = None
        for o in self.queue:
            if o.construction_site == site:
                order = o
                break

        if order is None:
            return

        # Import building classes as needed
        # This is a simplified version - in practice you'd have a factory pattern
        from src.entities.buildings.factory import Factory
        from src.entities.buildings.landfill_gas_extraction import LandfillGasExtraction

        # Create the actual building
        building = None
        if order.building_type == "factory":
            building = Factory(order.grid_x, order.grid_y)
        elif order.building_type == "landfill_gas_extraction":
            building = LandfillGasExtraction(order.grid_x, order.grid_y)
        # Add more building types as needed

        if building:
            # Place the building
            self.building_manager.place_building(building)
            print(f"Construction complete: {building.name} at ({order.grid_x}, {order.grid_y})")

        # Free construction site tiles (building manager will re-occupy)
        for dy in range(order.height_tiles):
            for dx in range(order.width_tiles):
                tile = self.grid.get_tile(order.grid_x + dx, order.grid_y + dy)
                if tile:
                    tile.occupied = False

        # Remove from active sites and queue
        self.active_sites.remove(site)
        self.queue.remove(order)

    def assign_robot_to_site(self, robot_id, site: ConstructionSite) -> bool:
        """
        Assign a robot to work on a construction site.

        Args:
            robot_id: ID of robot
            site: ConstructionSite to work on

        Returns:
            bool: True if assigned successfully
        """
        return site.add_robot(robot_id)

    def unassign_robot_from_site(self, robot_id, site: ConstructionSite):
        """
        Remove a robot from a construction site.

        Args:
            robot_id: ID of robot
            site: ConstructionSite
        """
        site.remove_robot(robot_id)

    def get_nearest_construction_site(self, x: float, y: float) -> Optional[ConstructionSite]:
        """
        Get the nearest construction site to a position.

        Args:
            x (float): World X position
            y (float): World Y position

        Returns:
            ConstructionSite or None: Nearest site needing workers
        """
        import math

        nearest_site = None
        nearest_distance = float('inf')

        for site in self.active_sites:
            # Only consider sites that need more workers
            if len(site.robots_working) >= site.max_workers:
                continue

            # Calculate distance
            site_center_x = site.x + site.width / 2
            site_center_y = site.y + site.height / 2
            distance = math.sqrt((x - site_center_x) ** 2 + (y - site_center_y) ** 2)

            if distance < nearest_distance:
                nearest_distance = distance
                nearest_site = site

        return nearest_site

    def render(self, screen, camera):
        """
        Render all construction sites.

        Args:
            screen: Pygame surface
            camera: Camera
        """
        for site in self.active_sites:
            site.render(screen, camera)

    def get_statistics(self) -> Dict:
        """
        Get construction statistics.

        Returns:
            dict: Construction stats
        """
        return {
            'queued': len(self.queue),
            'active': len(self.active_sites),
            'max_concurrent': self.max_concurrent,
        }

    def __repr__(self):
        """String representation for debugging."""
        return f"ConstructionManager(queued={len(self.queue)}, active={len(self.active_sites)})"
