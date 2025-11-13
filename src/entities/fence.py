"""
Fence - Perimeter barriers around properties that can be deconstructed for materials.

Fences come in different types:
- Chain link (iron)
- Wooden (wood + iron nails)
- Brick walls (concrete/slag)

All fences are ILLEGAL to deconstruct and generate high suspicion.
"""

import pygame
import random
from typing import Dict, Optional


class FenceType:
    """Fence type enumeration."""
    CHAIN_LINK = 'chain_link'
    WOODEN = 'wooden'
    BRICK = 'brick'


class Fence:
    """
    Fence segment entity.

    Fences are placed around properties (houses, stores) to mark boundaries.
    Deconstructing them is highly illegal but provides materials.
    """

    def __init__(self, world_x: float, world_y: float, fence_type: str = FenceType.CHAIN_LINK,
                 orientation: str = 'horizontal', length: int = 32):
        """
        Initialize a fence segment.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
            fence_type (str): Type of fence (chain_link, wooden, brick)
            orientation (str): 'horizontal' or 'vertical'
            length (int): Length in pixels (usually 32 for one tile)
        """
        self.world_x = world_x
        self.world_y = world_y
        self.fence_type = fence_type
        self.orientation = orientation
        self.length = length

        # Size based on orientation
        if orientation == 'horizontal':
            self.width = length
            self.height = 8  # Thin fence
        else:  # vertical
            self.width = 8
            self.height = length

        # Deconstruction
        self.legal_to_deconstruct = False  # Always illegal
        self.deconstruction_time = 15.0  # 15 seconds
        self.noise_level = 6  # Moderately noisy (0-10 scale)
        self.being_deconstructed = False
        self.deconstruction_progress = 0.0  # 0.0-1.0

        # Materials based on fence type
        self.materials: Dict[str, float] = self._get_materials_for_type(fence_type)

        # Visual
        self._generate_visuals()

        # ID for tracking
        self.id = id(self)

    def _get_materials_for_type(self, fence_type: str) -> Dict[str, float]:
        """
        Get materials contained in this fence type.

        Args:
            fence_type (str): Type of fence

        Returns:
            Dictionary of materials and quantities
        """
        if fence_type == FenceType.CHAIN_LINK:
            return {
                'metal': 12.0,  # Iron fencing
            }
        elif fence_type == FenceType.WOODEN:
            return {
                'wood': 15.0,
                'metal': 2.0,  # Nails and posts
            }
        elif fence_type == FenceType.BRICK:
            return {
                'concrete': 20.0,
                'slag': 5.0,
            }
        else:
            return {'metal': 10.0}

    def _generate_visuals(self):
        """Generate visual variation for this fence."""
        # Use position as seed for reproducibility
        rng = random.Random(int(self.world_x * 1000 + self.world_y))

        # Fence colors based on type
        if self.fence_type == FenceType.CHAIN_LINK:
            self.primary_color = (120, 120, 120)  # Gray metal
            self.secondary_color = (100, 100, 100)
            self.pattern = 'mesh'
        elif self.fence_type == FenceType.WOODEN:
            # Wooden fences have slight color variation
            wood_base = 120
            variation = rng.randint(-20, 20)
            self.primary_color = (wood_base + variation, wood_base//2 + variation//2, 30)
            self.secondary_color = tuple(max(0, c - 20) for c in self.primary_color)
            self.pattern = 'planks'
        elif self.fence_type == FenceType.BRICK:
            # Brick walls
            self.primary_color = (140, 80, 60)  # Red brick
            self.secondary_color = (100, 100, 100)  # Mortar
            self.pattern = 'bricks'
        else:
            self.primary_color = (100, 100, 100)
            self.secondary_color = (80, 80, 80)
            self.pattern = 'solid'

    def start_deconstruction(self) -> bool:
        """
        Start deconstructing this fence.

        Returns:
            bool: True if deconstruction started
        """
        if self.being_deconstructed:
            return False

        self.being_deconstructed = True
        self.deconstruction_progress = 0.0
        return True

    def update_deconstruction(self, dt: float) -> bool:
        """
        Update deconstruction progress.

        Args:
            dt (float): Delta time in seconds

        Returns:
            bool: True if deconstruction is complete
        """
        if not self.being_deconstructed:
            return False

        if self.deconstruction_time > 0:
            self.deconstruction_progress += dt / self.deconstruction_time
            self.deconstruction_progress = min(1.0, self.deconstruction_progress)

        return self.deconstruction_progress >= 1.0

    def get_materials(self) -> Dict[str, float]:
        """Get materials from this fence."""
        return self.materials.copy()

    def render(self, screen: pygame.Surface, camera):
        """
        Render the fence with deconstruction states.

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
        if (screen_x + width_px < 0 or screen_x > screen.get_width() or
            screen_y + height_px < 0 or screen_y > screen.get_height()):
            return

        # Color fades as deconstruction progresses
        primary_color = self.primary_color
        secondary_color = self.secondary_color
        if self.being_deconstructed:
            fade = 1.0 - (self.deconstruction_progress * 0.5)
            primary_color = tuple(int(c * fade) for c in primary_color)
            secondary_color = tuple(int(c * fade) for c in secondary_color)

        # Draw fence based on pattern
        if self.pattern == 'mesh':
            self._render_chain_link(screen, screen_x, screen_y, width_px, height_px, primary_color)
        elif self.pattern == 'planks':
            self._render_wooden(screen, screen_x, screen_y, width_px, height_px, primary_color, secondary_color)
        elif self.pattern == 'bricks':
            self._render_brick(screen, screen_x, screen_y, width_px, height_px, primary_color, secondary_color)
        else:
            # Simple solid fence
            pygame.draw.rect(screen, primary_color, (screen_x, screen_y, width_px, height_px))

        # Show deconstruction damage
        if self.being_deconstructed:
            self._render_deconstruction_damage(screen, screen_x, screen_y, width_px, height_px)

        # Show deconstruction progress bar
        if self.being_deconstructed:
            bar_width = max(10, width_px if self.orientation == 'horizontal' else height_px) - 4
            bar_height = 3
            if self.orientation == 'horizontal':
                bar_x = screen_x + 2
                bar_y = screen_y - 5
            else:
                bar_x = screen_x - 5
                bar_y = screen_y + 2

            # Background
            pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            # Progress
            progress_width = int(bar_width * self.deconstruction_progress)
            pygame.draw.rect(screen, (255, 100, 100), (bar_x, bar_y, progress_width, bar_height))

    def _render_chain_link(self, screen, x, y, width, height, color):
        """Render chain link fence pattern."""
        # Draw vertical posts
        post_color = tuple(max(0, c - 20) for c in color)
        if self.orientation == 'horizontal':
            pygame.draw.rect(screen, post_color, (x, y, 2, height))
            pygame.draw.rect(screen, post_color, (x + width - 2, y, 2, height))
        else:
            pygame.draw.rect(screen, post_color, (x, y, width, 2))
            pygame.draw.rect(screen, post_color, (x, y + height - 2, width, 2))

        # Draw mesh (simplified as lines)
        pygame.draw.rect(screen, color, (x, y, width, height))
        # Diagonal pattern
        for i in range(0, max(width, height), 4):
            if self.orientation == 'horizontal':
                pygame.draw.line(screen, post_color, (x + i, y), (x + i, y + height), 1)
            else:
                pygame.draw.line(screen, post_color, (x, y + i), (x + width, y + i), 1)

    def _render_wooden(self, screen, x, y, width, height, wood_color, dark_color):
        """Render wooden plank fence."""
        # Background
        pygame.draw.rect(screen, wood_color, (x, y, width, height))

        # Draw planks
        if self.orientation == 'horizontal':
            plank_width = 6
            for i in range(0, width, plank_width + 2):
                pygame.draw.rect(screen, dark_color, (x + i, y, 1, height))
        else:
            plank_height = 6
            for i in range(0, height, plank_height + 2):
                pygame.draw.rect(screen, dark_color, (x, y + i, width, 1))

    def _render_brick(self, screen, x, y, width, height, brick_color, mortar_color):
        """Render brick wall pattern."""
        # Background mortar
        pygame.draw.rect(screen, mortar_color, (x, y, width, height))

        # Draw bricks
        brick_width = 8
        brick_height = 4
        offset = False

        if self.orientation == 'horizontal':
            for row in range(0, height, brick_height):
                x_offset = brick_width // 2 if offset else 0
                for col in range(-brick_width, width, brick_width):
                    brick_x = x + col + x_offset
                    if brick_x < x + width:
                        pygame.draw.rect(screen, brick_color, (brick_x, y + row, brick_width - 1, brick_height - 1))
                offset = not offset
        else:
            for col in range(0, width, brick_width):
                y_offset = brick_height // 2 if offset else 0
                for row in range(-brick_height, height, brick_height):
                    brick_y = y + row + y_offset
                    if brick_y < y + height:
                        pygame.draw.rect(screen, brick_color, (x + col, brick_y, brick_width - 1, brick_height - 1))
                offset = not offset

    def _render_deconstruction_damage(self, screen, x, y, width, height):
        """Render progressive deconstruction damage on fence."""
        progress = self.deconstruction_progress

        # Stage 1-2 (0-50%): Damage marks
        if progress > 0.0:
            damage_color = (60, 60, 60)
            num_damages = int(progress * 6)
            rng = random.Random(int(self.world_x * 1000 + self.world_y))

            for i in range(num_damages):
                if self.orientation == 'horizontal':
                    damage_x = x + rng.randint(0, max(1, width - 4))
                    damage_y = y + rng.randint(0, max(1, height - 2))
                    pygame.draw.rect(screen, damage_color, (damage_x, damage_y, 3, 2))
                else:
                    damage_x = x + rng.randint(0, max(1, width - 2))
                    damage_y = y + rng.randint(0, max(1, height - 4))
                    pygame.draw.rect(screen, damage_color, (damage_x, damage_y, 2, 3))

        # Stage 3-4 (50-100%): Gaps and holes
        if progress > 0.5:
            gap_color = (20, 20, 20)  # Dark background showing through
            num_gaps = int((progress - 0.5) * 6)
            rng = random.Random(int(self.world_x * 1000 + self.world_y) + 100)

            for i in range(num_gaps):
                if self.orientation == 'horizontal':
                    gap_x = x + rng.randint(0, max(1, width - 6))
                    gap_y = y
                    pygame.draw.rect(screen, gap_color, (gap_x, gap_y, 5, height))
                else:
                    gap_x = x
                    gap_y = y + rng.randint(0, max(1, height - 6))
                    pygame.draw.rect(screen, gap_color, (gap_x, gap_y, width, 5))

    def __repr__(self):
        """String representation for debugging."""
        return f"Fence({self.fence_type}, {self.orientation}, pos=({self.world_x:.0f}, {self.world_y:.0f}))"
