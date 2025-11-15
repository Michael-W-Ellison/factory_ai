"""
Render Effects - Visual effects for enhanced graphics rendering.

Provides shadows, highlights, glow effects, and other visual enhancements.
"""

import pygame
import math
from typing import Tuple, Optional


class RenderEffects:
    """
    Utility class for applying visual effects to sprites and game entities.
    """

    @staticmethod
    def draw_shadow(surface: pygame.Surface, position: Tuple[int, int],
                   width: int, height: int, opacity: int = 80):
        """
        Draw a soft shadow under an object.

        Args:
            surface: Surface to draw on
            position: (x, y) position of the object
            width: Width of the shadow
            height: Height of the shadow
            opacity: Shadow opacity (0-255)
        """
        shadow_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Create elliptical shadow
        shadow_color = (0, 0, 0, opacity)
        pygame.draw.ellipse(shadow_surface, shadow_color, (0, 0, width, height))

        # Blur effect (simple approximation)
        shadow_surface = pygame.transform.smoothscale(shadow_surface, (width, height))

        surface.blit(shadow_surface, position)

    @staticmethod
    def draw_glow(surface: pygame.Surface, position: Tuple[int, int],
                  radius: int, color: Tuple[int, int, int],
                  intensity: float = 1.0):
        """
        Draw a glowing effect around a point.

        Args:
            surface: Surface to draw on
            position: (x, y) center position
            radius: Radius of the glow
            color: RGB color of the glow
            intensity: Glow intensity (0-1)
        """
        glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

        # Draw concentric circles with decreasing opacity
        steps = 5
        for i in range(steps):
            alpha = int(255 * intensity * (1 - i / steps))
            glow_color = (*color, alpha)
            glow_radius = radius - (radius * i // steps)

            if glow_radius > 0:
                pygame.draw.circle(glow_surface, glow_color,
                                 (radius, radius), glow_radius)

        surface.blit(glow_surface, (position[0] - radius, position[1] - radius),
                    special_flags=pygame.BLEND_RGBA_ADD)

    @staticmethod
    def draw_highlight(surface: pygame.Surface, rect: pygame.Rect,
                      color: Tuple[int, int, int] = (255, 255, 255),
                      thickness: int = 2):
        """
        Draw a highlight border around a rectangle.

        Args:
            surface: Surface to draw on
            rect: Rectangle to highlight
            color: RGB color of the highlight
            thickness: Thickness of the highlight border
        """
        # Top-left highlight (lighter)
        pygame.draw.line(surface, color, rect.topleft,
                        (rect.right, rect.top), thickness)
        pygame.draw.line(surface, color, rect.topleft,
                        (rect.left, rect.bottom), thickness)

        # Bottom-right shadow (darker)
        shadow_color = tuple(max(0, c // 2) for c in color)
        pygame.draw.line(surface, shadow_color,
                        (rect.left, rect.bottom),
                        (rect.right, rect.bottom), thickness)
        pygame.draw.line(surface, shadow_color,
                        (rect.right, rect.top),
                        (rect.right, rect.bottom), thickness)

    @staticmethod
    def draw_selection_indicator(surface: pygame.Surface, position: Tuple[int, int],
                                 radius: int, color: Tuple[int, int, int] = (255, 255, 0),
                                 pulse_phase: float = 0.0):
        """
        Draw a pulsing selection indicator.

        Args:
            surface: Surface to draw on
            position: (x, y) center position
            radius: Base radius
            color: RGB color
            pulse_phase: Animation phase (0-2π)
        """
        # Pulsing effect
        pulse = math.sin(pulse_phase) * 0.2 + 0.8  # 0.6 to 1.0
        current_radius = int(radius * pulse)

        # Draw concentric circles
        pygame.draw.circle(surface, color, position, current_radius, 2)
        pygame.draw.circle(surface, color, position, current_radius + 4, 1)

    @staticmethod
    def draw_health_bar(surface: pygame.Surface, position: Tuple[int, int],
                       width: int, height: int, health_percent: float,
                       show_background: bool = True):
        """
        Draw a health/status bar.

        Args:
            surface: Surface to draw on
            position: (x, y) top-left position
            width: Width of the bar
            height: Height of the bar
            health_percent: Health percentage (0-100)
            show_background: Whether to show background
        """
        # Background
        if show_background:
            bg_rect = pygame.Rect(position[0] - 1, position[1] - 1, width + 2, height + 2)
            pygame.draw.rect(surface, (50, 50, 50), bg_rect)

        # Health bar color (green to red gradient)
        if health_percent > 66:
            bar_color = (0, 255, 0)  # Green
        elif health_percent > 33:
            bar_color = (255, 200, 0)  # Yellow
        else:
            bar_color = (255, 50, 50)  # Red

        # Fill bar
        fill_width = int(width * (health_percent / 100.0))
        fill_rect = pygame.Rect(position[0], position[1], fill_width, height)
        pygame.draw.rect(surface, bar_color, fill_rect)

        # Border
        border_rect = pygame.Rect(position[0], position[1], width, height)
        pygame.draw.rect(surface, (200, 200, 200), border_rect, 1)

    @staticmethod
    def draw_motion_blur(surface: pygame.Surface, position: Tuple[int, int],
                        velocity: Tuple[float, float], sprite: pygame.Surface,
                        blur_strength: float = 0.5):
        """
        Draw a motion blur effect based on velocity.

        Args:
            surface: Surface to draw on
            position: (x, y) position
            velocity: (vx, vy) velocity vector
            sprite: Sprite to blur
            blur_strength: Strength of the blur effect (0-1)
        """
        speed = math.sqrt(velocity[0]**2 + velocity[1]**2)

        if speed < 10:  # Too slow for visible blur
            surface.blit(sprite, position)
            return

        # Calculate blur direction
        blur_length = int(speed * blur_strength)
        blur_angle = math.atan2(velocity[1], velocity[0])

        # Draw multiple copies with decreasing opacity
        num_copies = min(5, max(2, blur_length // 5))

        for i in range(num_copies):
            alpha = int(100 * (1 - i / num_copies))
            offset_x = -int((blur_length * math.cos(blur_angle) * i) / num_copies)
            offset_y = -int((blur_length * math.sin(blur_angle) * i) / num_copies)

            temp_sprite = sprite.copy()
            temp_sprite.set_alpha(alpha)
            surface.blit(temp_sprite, (position[0] + offset_x, position[1] + offset_y))

        # Draw main sprite on top
        surface.blit(sprite, position)

    @staticmethod
    def draw_particle_trail(surface: pygame.Surface, positions: list,
                           color: Tuple[int, int, int],
                           fade_out: bool = True):
        """
        Draw a particle trail effect.

        Args:
            surface: Surface to draw on
            positions: List of (x, y) positions for the trail
            color: RGB color
            fade_out: Whether to fade out towards the end
        """
        if len(positions) < 2:
            return

        for i in range(len(positions) - 1):
            alpha = 255
            if fade_out:
                alpha = int(255 * (i / len(positions)))

            start_pos = positions[i]
            end_pos = positions[i + 1]

            # Draw connecting line
            particle_color = (*color, alpha)
            temp_surface = pygame.Surface((abs(end_pos[0] - start_pos[0]) + 4,
                                          abs(end_pos[1] - start_pos[1]) + 4),
                                         pygame.SRCALPHA)

            local_start = (2, 2)
            local_end = (end_pos[0] - start_pos[0] + 2, end_pos[1] - start_pos[1] + 2)

            pygame.draw.line(temp_surface, particle_color, local_start, local_end, 2)

            surface.blit(temp_surface, (min(start_pos[0], end_pos[0]) - 2,
                                       min(start_pos[1], end_pos[1]) - 2))

    @staticmethod
    def apply_tint(sprite: pygame.Surface, color: Tuple[int, int, int],
                  intensity: float = 0.5) -> pygame.Surface:
        """
        Apply a color tint to a sprite.

        Args:
            sprite: Original sprite surface
            color: RGB tint color
            intensity: Tint intensity (0-1)

        Returns:
            pygame.Surface: Tinted sprite
        """
        tinted = sprite.copy()
        tint_surface = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
        alpha = int(255 * intensity)
        tint_surface.fill((*color, alpha))
        tinted.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return tinted

    @staticmethod
    def draw_damage_flash(sprite: pygame.Surface, flash_intensity: float = 1.0) -> pygame.Surface:
        """
        Apply a damage flash effect to a sprite.

        Args:
            sprite: Original sprite surface
            flash_intensity: Flash intensity (0-1)

        Returns:
            pygame.Surface: Flashed sprite
        """
        flashed = sprite.copy()
        flash_surface = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
        alpha = int(200 * flash_intensity)
        flash_surface.fill((255, 255, 255, alpha))
        flashed.blit(flash_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return flashed

    @staticmethod
    def draw_outline(surface: pygame.Surface, sprite: pygame.Surface,
                    position: Tuple[int, int], outline_color: Tuple[int, int, int],
                    thickness: int = 1):
        """
        Draw an outline around a sprite.

        Args:
            surface: Surface to draw on
            sprite: Sprite to outline
            position: (x, y) position
            outline_color: RGB outline color
            thickness: Outline thickness in pixels
        """
        # Create mask from sprite
        mask = pygame.mask.from_surface(sprite)

        # Draw outline by offsetting mask in all directions
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if dx == 0 and dy == 0:
                    continue

                outline_surface = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
                surface.blit(outline_surface, (position[0] + dx, position[1] + dy))

        # Draw sprite on top
        surface.blit(sprite, position)


# Global effects instance
_render_effects = RenderEffects()

def get_render_effects() -> RenderEffects:
    """Get the global render effects instance."""
    return _render_effects
