"""
PollutionManager - Manages pollution spreading across the world grid.

Handles:
- Pollution generation from sources (robots, buildings)
- Pollution spreading/diffusion
- Pollution decay over time
- Pollution level tracking per tile
- Visual overlay rendering (Factorio-style)
"""

import pygame
from typing import Dict, Tuple, List, Optional


class PollutionManager:
    """
    Manages pollution spreading and visualization.

    Pollution spreads from sources and dissipates over time.
    High pollution increases detection chances and has gameplay effects.
    """

    def __init__(self, grid_width: int, grid_height: int):
        """
        Initialize pollution manager.

        Args:
            grid_width (int): Grid width in tiles
            grid_height (int): Grid height in tiles
        """
        self.grid_width = grid_width
        self.grid_height = grid_height

        # Pollution levels per tile (0.0 - 100.0)
        self.pollution: Dict[Tuple[int, int], float] = {}

        # Pollution sources (position -> generation rate per second)
        self.sources: Dict[Tuple[int, int], float] = {}

        # Pollution overlay visibility
        self.overlay_visible = False

        # Spreading and decay parameters
        self.spread_rate = 0.15  # How much pollution spreads to neighbors per second
        self.decay_rate = 0.5    # How much pollution decays per second
        self.max_pollution = 100.0

        # Update timer (don't update every frame)
        self.update_timer = 0.0
        self.update_interval = 0.5  # Update every 0.5 seconds

        print(f"PollutionManager initialized for {grid_width}x{grid_height} grid")

    def add_source(self, grid_x: int, grid_y: int, rate: float):
        """
        Add a pollution source.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
            rate (float): Pollution generation per second
        """
        self.sources[(grid_x, grid_y)] = rate

    def remove_source(self, grid_x: int, grid_y: int):
        """
        Remove a pollution source.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
        """
        if (grid_x, grid_y) in self.sources:
            del self.sources[(grid_x, grid_y)]

    def update_source(self, grid_x: int, grid_y: int, rate: float):
        """
        Update a pollution source's generation rate.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
            rate (float): New pollution generation per second
        """
        if rate > 0:
            self.sources[(grid_x, grid_y)] = rate
        elif (grid_x, grid_y) in self.sources:
            # Remove if rate is 0
            del self.sources[(grid_x, grid_y)]

    def add_pollution(self, grid_x: int, grid_y: int, amount: float):
        """
        Add pollution to a tile.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
            amount (float): Amount of pollution to add
        """
        if not (0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height):
            return

        pos = (grid_x, grid_y)
        current = self.pollution.get(pos, 0.0)
        self.pollution[pos] = min(self.max_pollution, current + amount)

    def get_pollution(self, grid_x: int, grid_y: int) -> float:
        """
        Get pollution level at tile.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position

        Returns:
            float: Pollution level (0.0 - 100.0)
        """
        return self.pollution.get((grid_x, grid_y), 0.0)

    def toggle_overlay(self):
        """Toggle pollution overlay visibility."""
        self.overlay_visible = not self.overlay_visible
        print(f"Pollution overlay: {'ON' if self.overlay_visible else 'OFF'}")

    def update(self, dt: float):
        """
        Update pollution spreading and decay.

        Args:
            dt (float): Delta time in seconds
        """
        self.update_timer += dt

        # Only update periodically for performance
        if self.update_timer < self.update_interval:
            return

        dt = self.update_timer
        self.update_timer = 0.0

        # Generate pollution from sources
        for pos, rate in self.sources.items():
            self.add_pollution(pos[0], pos[1], rate * dt)

        # Spread and decay pollution
        self._spread_pollution(dt)
        self._decay_pollution(dt)

    def _spread_pollution(self, dt: float):
        """Spread pollution to neighboring tiles."""
        # Create new pollution dict for spreading
        spread_changes: Dict[Tuple[int, int], float] = {}

        # Iterate through all polluted tiles
        for pos, amount in list(self.pollution.items()):
            if amount < 1.0:
                continue

            grid_x, grid_y = pos

            # Spread to 4 neighbors (not diagonal)
            neighbors = [
                (grid_x - 1, grid_y),
                (grid_x + 1, grid_y),
                (grid_x, grid_y - 1),
                (grid_x, grid_y + 1),
            ]

            spread_amount = amount * self.spread_rate * dt / 4.0

            for nx, ny in neighbors:
                if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                    neighbor_pos = (nx, ny)
                    neighbor_amount = self.pollution.get(neighbor_pos, 0.0)

                    # Only spread if neighbor has less pollution
                    if neighbor_amount < amount:
                        spread_changes[neighbor_pos] = spread_changes.get(neighbor_pos, 0.0) + spread_amount
                        spread_changes[pos] = spread_changes.get(pos, 0.0) - spread_amount

        # Apply spread changes
        for pos, change in spread_changes.items():
            current = self.pollution.get(pos, 0.0)
            new_amount = max(0.0, min(self.max_pollution, current + change))
            if new_amount > 0.1:
                self.pollution[pos] = new_amount
            elif pos in self.pollution:
                del self.pollution[pos]

    def _decay_pollution(self, dt: float):
        """Decay pollution over time."""
        to_remove = []

        for pos, amount in self.pollution.items():
            # Decay
            decay_amount = self.decay_rate * dt
            new_amount = max(0.0, amount - decay_amount)

            if new_amount < 0.1:
                to_remove.append(pos)
            else:
                self.pollution[pos] = new_amount

        # Remove negligible pollution
        for pos in to_remove:
            del self.pollution[pos]

    def render_overlay(self, screen: pygame.Surface, camera, tile_size: int):
        """
        Render pollution overlay (Factorio-style).

        Args:
            screen: Pygame surface
            camera: Camera for view transformation
            tile_size (int): Size of tiles in pixels
        """
        if not self.overlay_visible:
            return

        # Calculate visible area
        start_x = max(0, int(camera.x // tile_size))
        start_y = max(0, int(camera.y // tile_size))
        end_x = min(self.grid_width, int((camera.x + camera.width) // tile_size) + 2)
        end_y = min(self.grid_height, int((camera.y + camera.height) // tile_size) + 2)

        # Create overlay surface with alpha
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)

        # Render pollution
        for grid_y in range(start_y, end_y):
            for grid_x in range(start_x, end_x):
                pollution = self.get_pollution(grid_x, grid_y)

                if pollution < 1.0:
                    continue

                # Convert to screen coordinates
                world_x = grid_x * tile_size
                world_y = grid_y * tile_size
                screen_x = world_x - camera.x
                screen_y = world_y - camera.y

                # Calculate color based on pollution level
                color = self._get_pollution_color(pollution)

                # Draw pollution tile
                pygame.draw.rect(overlay, color, (screen_x, screen_y, tile_size, tile_size))

        # Blit overlay to screen
        screen.blit(overlay, (0, 0))

    def _get_pollution_color(self, pollution: float) -> Tuple[int, int, int, int]:
        """
        Get color for pollution level (Factorio-style gradient).

        Args:
            pollution (float): Pollution level (0.0 - 100.0)

        Returns:
            tuple: RGBA color
        """
        # Normalize to 0-1
        intensity = min(1.0, pollution / self.max_pollution)

        # Color gradient: transparent -> yellow -> orange -> red -> dark red
        if intensity < 0.25:
            # Transparent to yellow
            t = intensity / 0.25
            r = int(255 * t)
            g = int(255 * t)
            b = 0
            a = int(60 * t)
        elif intensity < 0.5:
            # Yellow to orange
            t = (intensity - 0.25) / 0.25
            r = 255
            g = int(255 - 80 * t)
            b = 0
            a = int(60 + 40 * t)
        elif intensity < 0.75:
            # Orange to red
            t = (intensity - 0.5) / 0.25
            r = 255
            g = int(175 - 100 * t)
            b = 0
            a = int(100 + 50 * t)
        else:
            # Red to dark red
            t = (intensity - 0.75) / 0.25
            r = int(255 - 100 * t)
            g = int(75 - 75 * t)
            b = 0
            a = int(150 + 50 * t)

        return (r, g, b, a)

    def get_stats(self) -> Dict:
        """
        Get pollution statistics.

        Returns:
            dict: Statistics
        """
        if not self.pollution:
            return {
                'total_tiles': 0,
                'avg_pollution': 0.0,
                'max_pollution_level': 0.0,
                'total_pollution': 0.0,
                'sources': len(self.sources)
            }

        total = sum(self.pollution.values())
        max_level = max(self.pollution.values())
        avg = total / len(self.pollution)

        return {
            'total_tiles': len(self.pollution),
            'avg_pollution': avg,
            'max_pollution_level': max_level,
            'total_pollution': total,
            'sources': len(self.sources)
        }

    def to_dict(self) -> Dict:
        """Serialize pollution state for saving."""
        return {
            'pollution': {f"{x},{y}": v for (x, y), v in self.pollution.items()},
            'sources': {f"{x},{y}": v for (x, y), v in self.sources.items()},
            'overlay_visible': self.overlay_visible
        }

    def from_dict(self, data: Dict):
        """Load pollution state from saved data."""
        # Load pollution
        pollution_data = data.get('pollution', {})
        self.pollution = {}
        for key, value in pollution_data.items():
            x, y = map(int, key.split(','))
            self.pollution[(x, y)] = value

        # Load sources
        sources_data = data.get('sources', {})
        self.sources = {}
        for key, value in sources_data.items():
            x, y = map(int, key.split(','))
            self.sources[(x, y)] = value

        self.overlay_visible = data.get('overlay_visible', False)

    def __repr__(self):
        """String representation for debugging."""
        stats = self.get_stats()
        return (f"PollutionManager(tiles={stats['total_tiles']}, "
                f"sources={stats['sources']}, "
                f"avg={stats['avg_pollution']:.1f})")
