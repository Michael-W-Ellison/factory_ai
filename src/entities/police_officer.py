"""
Police Officer - law enforcement NPC that patrols the city.

Police officers have enhanced vision, higher detection rates, and can
chase robots performing illegal activities.
"""

import pygame
import random
from typing import List, Tuple
from src.entities.npc import NPC, Activity


class PoliceBehavior:
    """Police behavior states."""
    PATROL = 'patrol'           # Normal patrol along route
    SUSPICIOUS = 'suspicious'   # Investigating suspicious activity
    ALERT = 'alert'            # Chasing robot
    CAPTURE = 'capture'        # Caught robot (game over)


class PoliceOfficer(NPC):
    """
    Police officer entity - enhanced NPC with better detection.

    Police officers patrol routes, have better vision, and react
    to illegal activities more aggressively than civilians.
    """

    def __init__(self, world_x: float, world_y: float, patrol_route: List[Tuple[int, int]] = None):
        """
        Initialize a police officer.

        Args:
            world_x (float): Initial world X position
            world_y (float): Initial world Y position
            patrol_route (List[Tuple[int, int]]): List of (grid_x, grid_y) waypoints
        """
        # Initialize as NPC (no home/work, police don't have those)
        super().__init__(world_x, world_y, home_x=0, home_y=0, work_x=None, work_y=None)

        # Override NPC properties for police
        self.vision_range = 150.0  # Better vision (150px vs 100px)
        self.vision_angle = 200.0  # Wider vision cone (200° vs 180°)
        self.alertness = 1.0  # Always fully alert
        self.speed = 35.0  # Slightly faster than civilians (35px/s vs 30px/s)

        # Police-specific properties
        self.is_police = True
        self.behavior = PoliceBehavior.PATROL
        self.patrol_route = patrol_route if patrol_route else []
        self.current_waypoint = 0
        self.patrol_wait_time = 0.0  # Time to wait at waypoint
        self.patrol_wait_duration = 2.0  # Seconds to wait at each waypoint

        # Investigation
        self.investigation_target = None
        self.chase_target = None

        # Override visuals for police
        self._generate_police_visuals()

    def _generate_police_visuals(self):
        """Generate police officer visuals."""
        # Police uniform colors
        self.clothing_color = (40, 60, 120)  # Dark blue uniform
        self.skin_color = (220, 180, 140)
        self.outline_color = (20, 30, 60)  # Darker blue outline

        # Police badge color (for rendering)
        self.badge_color = (200, 180, 100)  # Gold badge

    def update_schedule(self, game_time: float):
        """
        Police don't follow civilian schedules - they patrol 24/7.

        Args:
            game_time (float): Current game time in hours (0-24)
        """
        self.current_time = game_time % 24

        # Police are always on patrol (shift changes could be added later)
        self.current_activity = Activity.WORKING  # Using WORKING as generic "on duty"
        self.alertness = 1.0  # Always alert

        # Night time reduces visibility slightly even for police
        if self.current_time < 6 or self.current_time >= 20:
            # Nighttime - slightly reduced effectiveness
            self.alertness = 0.9
        else:
            self.alertness = 1.0

    def update(self, dt: float, game_time: float):
        """
        Update police officer state.

        Args:
            dt (float): Delta time in seconds
            game_time (float): Current game time in hours (0-24)
        """
        # Update schedule (always on duty)
        self.update_schedule(game_time)

        # Update based on behavior
        if self.behavior == PoliceBehavior.PATROL:
            self._update_patrol(dt)
        elif self.behavior == PoliceBehavior.SUSPICIOUS:
            self._update_suspicious(dt)
        elif self.behavior == PoliceBehavior.ALERT:
            self._update_alert(dt)
        elif self.behavior == PoliceBehavior.CAPTURE:
            self._update_capture(dt)

        # Update movement (inherited from NPC)
        if self.moving:
            # Calculate direction to target
            dx = self.target_x - self.world_x
            dy = self.target_y - self.world_y
            distance = (dx * dx + dy * dy) ** 0.5

            if distance < 2.0:
                # Reached target
                self.world_x = self.target_x
                self.world_y = self.target_y
                self.moving = False
            else:
                # Move towards target
                import math
                move_distance = self.speed * dt
                if move_distance > distance:
                    move_distance = distance

                # Normalize direction and move
                self.world_x += (dx / distance) * move_distance
                self.world_y += (dy / distance) * move_distance

                # Update facing angle
                self.facing_angle = math.degrees(math.atan2(dy, dx))

    def _update_patrol(self, dt: float):
        """Update patrol behavior."""
        if not self.patrol_route:
            return

        # If waiting at waypoint
        if self.patrol_wait_time > 0:
            self.patrol_wait_time -= dt
            return

        # If not moving, set next waypoint
        if not self.moving:
            waypoint = self.patrol_route[self.current_waypoint]
            self.target_x = waypoint[0] * 32 + 16  # Center of tile
            self.target_y = waypoint[1] * 32 + 16
            self.moving = True

        # If reached waypoint
        if not self.moving:
            # Wait at waypoint
            self.patrol_wait_time = self.patrol_wait_duration

            # Move to next waypoint
            self.current_waypoint = (self.current_waypoint + 1) % len(self.patrol_route)

    def _update_suspicious(self, dt: float):
        """Update suspicious behavior (investigating)."""
        # Move towards investigation target
        if self.investigation_target:
            self.target_x, self.target_y = self.investigation_target
            self.moving = True

            # If reached investigation point, switch back to patrol
            dx = self.target_x - self.world_x
            dy = self.target_y - self.world_y
            if (dx * dx + dy * dy) < 16.0:  # Within 4 pixels
                self.behavior = PoliceBehavior.PATROL
                self.investigation_target = None

    def _update_alert(self, dt: float):
        """Update alert behavior (chasing robot)."""
        # Chase the target robot
        if self.chase_target:
            self.target_x = self.chase_target.x
            self.target_y = self.chase_target.y
            self.moving = True

            # Check if caught robot (within range)
            dx = self.target_x - self.world_x
            dy = self.target_y - self.world_y
            distance = (dx * dx + dy * dy) ** 0.5

            if distance < 20.0:  # Caught!
                self.behavior = PoliceBehavior.CAPTURE
        else:
            # Lost target, return to patrol
            self.behavior = PoliceBehavior.PATROL

    def _update_capture(self, dt: float):
        """Update capture behavior (game over state)."""
        # Robot has been caught - this would trigger game over
        # The game will handle this state
        pass

    def calculate_detection_chance(self, robot_x: float, robot_y: float,
                                   is_daytime: bool, robot_stealth: float) -> float:
        """
        Calculate detection chance for a robot (enhanced for police).

        Args:
            robot_x (float): Robot world X
            robot_y (float): Robot world Y
            is_daytime (bool): Whether it's daytime
            robot_stealth (float): Robot stealth level (0.0-1.0)

        Returns:
            float: Detection chance per second (0.0-1.0)
        """
        # Use parent class calculation
        base_chance = super().calculate_detection_chance(robot_x, robot_y, is_daytime, robot_stealth)

        # Police have +50% detection chance
        enhanced_chance = base_chance * 1.5

        return min(1.0, enhanced_chance)  # Cap at 1.0

    def start_investigation(self, location: Tuple[float, float]):
        """
        Start investigating a location.

        Args:
            location (Tuple[float, float]): World (x, y) to investigate
        """
        self.behavior = PoliceBehavior.SUSPICIOUS
        self.investigation_target = location

    def start_chase(self, robot):
        """
        Start chasing a robot.

        Args:
            robot: Robot entity to chase
        """
        self.behavior = PoliceBehavior.ALERT
        self.chase_target = robot

    def render(self, screen: pygame.Surface, camera):
        """
        Render the police officer.

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

        # Draw police uniform (darker blue)
        body_rect = pygame.Rect(screen_x - width_px//2, screen_y - height_px//2 + 4,
                                width_px, height_px - 4)
        pygame.draw.rect(screen, self.clothing_color, body_rect)
        pygame.draw.rect(screen, self.outline_color, body_rect, 1)

        # Draw badge (small gold rectangle)
        badge_size = max(2, int(3 * camera.zoom))
        badge_x = screen_x - badge_size // 2
        badge_y = screen_y - height_px//4
        pygame.draw.rect(screen, self.badge_color, (badge_x, badge_y, badge_size, badge_size))

        # Head
        head_radius = max(3, int(width_px // 3))
        head_pos = (screen_x, screen_y - height_px//2)
        pygame.draw.circle(screen, self.skin_color, head_pos, head_radius)
        pygame.draw.circle(screen, self.outline_color, head_pos, head_radius, 1)

        # Police hat indicator (small rectangle on top of head)
        if camera.zoom >= 0.8:
            hat_width = head_radius * 2
            hat_height = max(2, int(3 * camera.zoom))
            hat_rect = pygame.Rect(screen_x - hat_width//2, head_pos[1] - head_radius - hat_height,
                                  hat_width, hat_height)
            pygame.draw.rect(screen, self.clothing_color, hat_rect)

        # Behavior indicator (when zoomed in)
        if camera.zoom >= 0.8:
            font = pygame.font.Font(None, 14)
            behavior_icons = {
                PoliceBehavior.PATROL: '👮',
                PoliceBehavior.SUSPICIOUS: '🔍',
                PoliceBehavior.ALERT: '🚨',
                PoliceBehavior.CAPTURE: '⚠️',
            }
            icon = behavior_icons.get(self.behavior, 'P')
            text = font.render(icon, True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen_x, screen_y - height_px - 8))
            # Background
            bg_rect = text_rect.inflate(4, 2)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            screen.blit(text, text_rect)

    def __repr__(self):
        """String representation for debugging."""
        return f"PoliceOfficer(pos=({self.world_x:.0f}, {self.world_y:.0f}), behavior={self.behavior})"
