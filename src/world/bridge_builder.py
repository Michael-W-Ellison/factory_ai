"""
BridgeBuilder - automatic and manual bridge placement system.

Handles:
- Finding optimal bridge crossing points
- Placing bridges across water
- Bridge cost calculation
- Pathfinding integration
"""

from src.world.tile import TerrainType
import math


class BridgeBuilder:
    """
    Manages bridge placement across water.

    Can automatically find optimal crossing points or place bridges manually.
    """

    def __init__(self, grid, resource_manager=None):
        """
        Initialize bridge builder.

        Args:
            grid: World grid
            resource_manager: ResourceManager for costs (optional)
        """
        self.grid = grid
        self.resource_manager = resource_manager

        # Bridge costs
        self.cost_per_tile = 100.0  # Money cost per bridge tile
        self.material_per_tile = {'wood': 5.0}  # Materials needed per tile

    def find_narrow_crossings(self, max_width=10, min_width=2):
        """
        Find narrow water crossings suitable for bridges.

        Args:
            max_width (int): Maximum bridge length to consider
            min_width (int): Minimum water width to bridge

        Returns:
            list: List of crossing dictionaries with start, end, width, direction
        """
        crossings = []

        # Scan horizontally for vertical crossings
        for y in range(self.grid.height_tiles):
            water_start = None
            for x in range(self.grid.width_tiles):
                tile = self.grid.get_tile(x, y)
                if not tile:
                    continue

                is_water = tile.terrain_type in [TerrainType.WATER, TerrainType.OCEAN]

                if is_water and water_start is None:
                    # Start of water crossing
                    water_start = x
                elif not is_water and water_start is not None:
                    # End of water crossing
                    width = x - water_start

                    if min_width <= width <= max_width:
                        # Check if land on both sides
                        if self._is_land(water_start - 1, y) and self._is_land(x, y):
                            crossings.append({
                                'start_x': water_start,
                                'start_y': y,
                                'end_x': x - 1,
                                'end_y': y,
                                'width': width,
                                'direction': 'horizontal'
                            })

                    water_start = None

        # Scan vertically for horizontal crossings
        for x in range(self.grid.width_tiles):
            water_start = None
            for y in range(self.grid.height_tiles):
                tile = self.grid.get_tile(x, y)
                if not tile:
                    continue

                is_water = tile.terrain_type in [TerrainType.WATER, TerrainType.OCEAN]

                if is_water and water_start is None:
                    # Start of water crossing
                    water_start = y
                elif not is_water and water_start is not None:
                    # End of water crossing
                    width = y - water_start

                    if min_width <= width <= max_width:
                        # Check if land on both sides
                        if self._is_land(x, water_start - 1) and self._is_land(x, y):
                            crossings.append({
                                'start_x': x,
                                'start_y': water_start,
                                'end_x': x,
                                'end_y': y - 1,
                                'width': width,
                                'direction': 'vertical'
                            })

                    water_start = None

        return crossings

    def place_bridge(self, start_x, start_y, end_x, end_y, pay_cost=True):
        """
        Place a bridge from start to end position.

        Args:
            start_x (int): Starting grid X
            start_y (int): Starting grid Y
            end_x (int): Ending grid X
            end_y (int): Ending grid Y
            pay_cost (bool): Whether to deduct costs (default True)

        Returns:
            tuple: (success: bool, message: str, tiles_placed: int)
        """
        # Determine direction and validate
        if start_x == end_x:
            # Vertical bridge
            direction = 'vertical'
            length = abs(end_y - start_y) + 1
            min_y, max_y = min(start_y, end_y), max(start_y, end_y)
        elif start_y == end_y:
            # Horizontal bridge
            direction = 'horizontal'
            length = abs(end_x - start_x) + 1
            min_x, max_x = min(start_x, end_x), max(start_x, end_x)
        else:
            return False, "Bridges must be straight (horizontal or vertical)", 0

        # Calculate cost
        total_cost = length * self.cost_per_tile
        total_materials = {mat: amount * length
                          for mat, amount in self.material_per_tile.items()}

        # Check if player can afford it
        if pay_cost and self.resource_manager:
            if hasattr(self.resource_manager, 'money'):
                if self.resource_manager.money < total_cost:
                    return False, f"Insufficient funds - need ${total_cost:.0f}", 0

            # Check materials
            for material, amount in total_materials.items():
                if not self.resource_manager.has_material(material, amount):
                    return False, f"Insufficient {material} - need {amount:.0f}", 0

        # Validate all tiles are water
        tiles_to_bridge = []
        if direction == 'vertical':
            for y in range(min_y, max_y + 1):
                tile = self.grid.get_tile(start_x, y)
                if not tile:
                    return False, f"Invalid tile at ({start_x}, {y})", 0
                if tile.terrain_type not in [TerrainType.WATER, TerrainType.OCEAN]:
                    return False, f"Can only bridge over water at ({start_x}, {y})", 0
                tiles_to_bridge.append(tile)
        else:  # horizontal
            for x in range(min_x, max_x + 1):
                tile = self.grid.get_tile(x, start_y)
                if not tile:
                    return False, f"Invalid tile at ({x}, {start_y})", 0
                if tile.terrain_type not in [TerrainType.WATER, TerrainType.OCEAN]:
                    return False, f"Can only bridge over water at ({x}, {start_y})", 0
                tiles_to_bridge.append(tile)

        # Deduct costs if required
        if pay_cost and self.resource_manager:
            if hasattr(self.resource_manager, 'money'):
                self.resource_manager.money -= total_cost

            for material, amount in total_materials.items():
                self.resource_manager.remove_material(material, amount)

        # Place bridge tiles
        for tile in tiles_to_bridge:
            tile.set_terrain_type(TerrainType.BRIDGE)

        return True, f"Bridge placed ({length} tiles, ${total_cost:.0f})", length

    def auto_place_bridges(self, max_bridges=5, max_width=8, min_width=2, pay_cost=True):
        """
        Automatically place bridges at optimal crossing points.

        Args:
            max_bridges (int): Maximum number of bridges to place
            max_width (int): Maximum bridge length
            min_width (int): Minimum water width to bridge
            pay_cost (bool): Whether to pay for bridges

        Returns:
            list: List of (success, message, tiles_placed) for each bridge
        """
        # Find all narrow crossings
        crossings = self.find_narrow_crossings(max_width=max_width, min_width=min_width)

        # Sort by width (narrowest first)
        crossings.sort(key=lambda c: c['width'])

        # Place bridges at narrowest crossings
        results = []
        bridges_placed = 0

        for crossing in crossings:
            if bridges_placed >= max_bridges:
                break

            # Try to place bridge
            success, message, tiles = self.place_bridge(
                crossing['start_x'],
                crossing['start_y'],
                crossing['end_x'],
                crossing['end_y'],
                pay_cost=pay_cost
            )

            results.append((success, message, tiles))

            if success:
                bridges_placed += 1

        return results

    def remove_bridge(self, x, y, refund=True):
        """
        Remove a bridge tile and optionally refund cost.

        Args:
            x (int): Grid X
            y (int): Grid Y
            refund (bool): Whether to refund costs

        Returns:
            tuple: (success: bool, message: str)
        """
        tile = self.grid.get_tile(x, y)
        if not tile:
            return False, "Invalid tile position"

        if tile.terrain_type != TerrainType.BRIDGE:
            return False, "No bridge at this location"

        # Refund costs
        if refund and self.resource_manager:
            if hasattr(self.resource_manager, 'money'):
                self.resource_manager.money += self.cost_per_tile * 0.5  # 50% refund

            for material, amount in self.material_per_tile.items():
                self.resource_manager.add_material(material, amount * 0.5)

        # Revert to water
        tile.set_terrain_type(TerrainType.WATER)

        return True, "Bridge removed"

    def get_bridge_cost(self, length):
        """
        Calculate cost for a bridge of given length.

        Args:
            length (int): Bridge length in tiles

        Returns:
            dict: {'money': float, 'materials': {material: amount}}
        """
        return {
            'money': length * self.cost_per_tile,
            'materials': {mat: amount * length
                         for mat, amount in self.material_per_tile.items()}
        }

    def _is_land(self, x, y):
        """
        Check if tile is land (not water, not bridge).

        Args:
            x (int): Grid X
            y (int): Grid Y

        Returns:
            bool: True if land
        """
        tile = self.grid.get_tile(x, y)
        if not tile:
            return False

        return tile.terrain_type == TerrainType.LAND

    def count_bridges(self):
        """
        Count total bridge tiles on the map.

        Returns:
            int: Number of bridge tiles
        """
        count = 0
        for y in range(self.grid.height_tiles):
            for x in range(self.grid.width_tiles):
                tile = self.grid.get_tile(x, y)
                if tile and tile.terrain_type == TerrainType.BRIDGE:
                    count += 1
        return count

    def __repr__(self):
        """String representation for debugging."""
        return f"BridgeBuilder(bridges={self.count_bridges()})"
