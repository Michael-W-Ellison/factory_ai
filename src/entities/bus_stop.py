"""
BusStop - Small shelter prop where NPCs wait for buses.

Visual representation of a bus stop in the city.
NPCs can wait here for buses to arrive.
"""

import pygame
from typing import Set


class BusStop:
    """
    Bus stop prop - a small shelter where NPCs wait for buses.

    Attributes:
        grid_x (int): Grid X position
        grid_y (int): Grid Y position
        world_x (float): World X position (center)
        world_y (float): World Y position (center)
        route_ids (set): Set of bus route IDs that stop here
        waiting_npcs (set): Set of NPC IDs waiting at this stop
    """

    def __init__(self, grid_x: int, grid_y: int, tile_size: int = 32):
        """
        Initialize a bus stop.

        Args:
            grid_x (int): Grid X position
            grid_y (int): Grid Y position
            tile_size (int): Tile size in pixels
        """
        self.grid_x = grid_x
        self.grid_y = grid_y

        # Calculate world position (center of tile)
        self.world_x = grid_x * tile_size + tile_size / 2
        self.world_y = grid_y * tile_size + tile_size / 2

        # Routes that stop here
        self.route_ids: Set[int] = set()

        # NPCs waiting at this stop
        self.waiting_npcs: Set[int] = set()

        # Visual properties
        self.width = 20  # pixels
        self.height = 24  # pixels

        # Colors
        self.roof_color = (80, 80, 100)  # Gray roof
        self.wall_color = (150, 150, 170)  # Light gray walls
        self.bench_color = (100, 70, 40)  # Brown bench
        self.post_color = (60, 60, 60)  # Dark gray posts

    def add_route(self, route_id: int):
        """
        Add a bus route that stops here.

        Args:
            route_id (int): Bus route ID
        """
        self.route_ids.add(route_id)

    def add_waiting_npc(self, npc_id: int):
        """
        Add an NPC to the waiting list.

        Args:
            npc_id (int): NPC ID
        """
        self.waiting_npcs.add(npc_id)

    def remove_waiting_npc(self, npc_id: int):
        """
        Remove an NPC from the waiting list.

        Args:
            npc_id (int): NPC ID
        """
        self.waiting_npcs.discard(npc_id)

    def get_waiting_count(self) -> int:
        """Get number of NPCs waiting."""
        return len(self.waiting_npcs)

    def render(self, screen: pygame.Surface, camera):
        """
        Render the bus stop shelter.

        Args:
            screen: Pygame surface
            camera: Camera for world-to-screen transformation
        """
        # Calculate screen position
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)

        # Apply camera zoom
        width_px = int(self.width * camera.zoom)
        height_px = int(self.height * camera.zoom)

        # Don't render if off screen
        if (screen_x + width_px < 0 or screen_x - width_px > screen.get_width() or
            screen_y + height_px < 0 or screen_y - height_px > screen.get_height()):
            return

        # Render shelter structure
        self._render_shelter(screen, screen_x, screen_y, width_px, height_px)

        # Render route numbers (if zoomed in enough)
        if camera.zoom >= 0.8 and self.route_ids:
            self._render_route_numbers(screen, screen_x, screen_y, camera.zoom)

    def _render_shelter(self, screen, center_x, center_y, width, height):
        """Render the bus stop shelter structure."""
        # Calculate positions
        left = center_x - width // 2
        top = center_y - height // 2
        right = center_x + width // 2
        bottom = center_y + height // 2

        # Draw support posts (left and right)
        post_width = max(2, int(width * 0.15))
        post_height = int(height * 0.7)

        # Left post
        left_post_rect = pygame.Rect(left, top + int(height * 0.3), post_width, post_height)
        pygame.draw.rect(screen, self.post_color, left_post_rect)

        # Right post
        right_post_rect = pygame.Rect(right - post_width, top + int(height * 0.3), post_width, post_height)
        pygame.draw.rect(screen, self.post_color, right_post_rect)

        # Draw roof
        roof_height = max(3, int(height * 0.2))
        roof_rect = pygame.Rect(left - 2, top, width + 4, roof_height)
        pygame.draw.rect(screen, self.roof_color, roof_rect)
        pygame.draw.rect(screen, (40, 40, 50), roof_rect, 1)  # Outline

        # Draw back wall (partial)
        wall_width = int(width * 0.6)
        wall_height = int(height * 0.5)
        wall_x = left + (width - wall_width) // 2
        wall_y = top + roof_height
        wall_rect = pygame.Rect(wall_x, wall_y, wall_width, wall_height)
        pygame.draw.rect(screen, self.wall_color, wall_rect)
        pygame.draw.rect(screen, (100, 100, 120), wall_rect, 1)  # Outline

        # Draw bench
        bench_width = int(width * 0.7)
        bench_height = max(2, int(height * 0.1))
        bench_x = left + (width - bench_width) // 2
        bench_y = bottom - bench_height - 2
        bench_rect = pygame.Rect(bench_x, bench_y, bench_width, bench_height)
        pygame.draw.rect(screen, self.bench_color, bench_rect)

    def _render_route_numbers(self, screen, center_x, center_y, zoom):
        """Render route numbers on the shelter."""
        # Create route text (e.g., "1,2,3")
        route_text = ",".join(str(r) for r in sorted(self.route_ids))

        font_size = max(12, int(14 * zoom))
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(route_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(center_x, center_y - int(15 * zoom)))

        # Draw background
        bg_rect = text_rect.inflate(4, 2)
        pygame.draw.rect(screen, (0, 0, 0), bg_rect)
        pygame.draw.rect(screen, (200, 150, 50), bg_rect, 1)  # Orange border
        screen.blit(text_surface, text_rect)

    def __repr__(self):
        """String representation for debugging."""
        return (f"BusStop(pos=({self.grid_x}, {self.grid_y}), "
                f"routes={self.route_ids}, waiting={len(self.waiting_npcs)})")
