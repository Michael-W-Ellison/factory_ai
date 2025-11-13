"""
NPC (Non-Player Character) - Citizens that live and work in the city.

NPCs follow daily schedules, move around the city, and can detect illegal
robot activities. Detection increases suspicion and can lead to reports.
"""

import pygame
import random
import math
from typing import Tuple, Optional, Dict


class Activity:
    """NPC activity enumeration."""
    SLEEPING = 'sleeping'
    MORNING_ROUTINE = 'morning_routine'
    COMMUTING_TO_WORK = 'commuting_to_work'
    WORKING = 'working'
    COMMUTING_HOME = 'commuting_home'
    EVENING_ACTIVITIES = 'evening_activities'
    HOME_ROUTINE = 'home_routine'


class NPC:
    """
    Non-player character entity.

    NPCs have daily schedules, move around the city, and can detect
    illegal robot activities within their vision range.
    """

    def __init__(self, world_x: float, world_y: float, home_x: int, home_y: int,
                 work_x: int = None, work_y: int = None):
        """
        Initialize an NPC.

        Args:
            world_x (float): Initial world X position
            world_y (float): Initial world Y position
            home_x (int): Home grid X position
            home_y (int): Home grid Y position
            work_x (int): Work grid X position (None if unemployed)
            work_y (int): Work grid Y position (None if unemployed)
        """
        self.world_x = world_x
        self.world_y = world_y

        # Home and work locations
        self.home_x = home_x
        self.home_y = home_y
        self.work_x = work_x
        self.work_y = work_y
        self.has_job = work_x is not None and work_y is not None

        # Movement
        self.speed = 30.0  # pixels per second (walking speed)
        self.target_x = world_x
        self.target_y = world_y
        self.moving = False

        # Current activity
        self.current_activity = Activity.HOME_ROUTINE
        self.current_time = 0.0  # Game time in hours (0-24)

        # Vision and detection
        self.vision_range = 100.0  # pixels
        self.vision_angle = 180.0  # degrees (front-facing cone)
        self.facing_angle = 90.0  # degrees (0 = right, 90 = down, 180 = left, 270 = up)
        self.alertness = 0.5  # 0.0-1.0 (affects detection chance)

        # Detection tracking (tracks robots being watched)
        self.detecting_robots = {}  # robot_id -> detection_progress (0.0-1.0)

        # Visual properties
        self.width = 16
        self.height = 16
        self._generate_visuals()

        # Animation properties
        self.animation_frame = 0  # 0 or 1 for walking animation
        self.animation_timer = 0.0  # Time accumulator
        self.animation_speed = 0.3  # Seconds per frame

        # ID for tracking
        self.id = id(self)

    def _generate_visuals(self):
        """Generate visual variation for this NPC."""
        # Use position as seed for reproducibility
        rng = random.Random(int(self.world_x * 1000 + self.world_y))

        # NPC clothing colors (varied)
        clothing_colors = [
            (80, 100, 180),   # Blue
            (180, 80, 80),    # Red
            (80, 180, 80),    # Green
            (150, 120, 80),   # Brown
            (100, 100, 100),  # Gray
            (180, 180, 80),   # Yellow
            (120, 80, 150),   # Purple
        ]

        self.clothing_color = rng.choice(clothing_colors)
        self.skin_color = (220, 180, 140)  # Generic skin tone
        self.outline_color = tuple(max(0, c - 40) for c in self.clothing_color)

    def update_schedule(self, game_time: float):
        """
        Update NPC activity based on current game time.

        Args:
            game_time (float): Current game time in hours (0-24)
        """
        self.current_time = game_time % 24

        # Determine activity based on time
        if 22 <= self.current_time or self.current_time < 6:
            # Sleep: 10pm-6am (at home)
            self.current_activity = Activity.SLEEPING
            self.alertness = 0.1  # Very low alertness while sleeping
            self._move_to_home()

        elif 6 <= self.current_time < 8:
            # Morning routine: 6am-8am (at home)
            self.current_activity = Activity.MORNING_ROUTINE
            self.alertness = 0.4  # Waking up, moderate alertness
            self._move_to_home()

        elif 8 <= self.current_time < 9:
            # Commute to work: 8am-9am
            if self.has_job:
                self.current_activity = Activity.COMMUTING_TO_WORK
                self.alertness = 0.6  # Alert while commuting
                self._move_to_work()
            else:
                self.current_activity = Activity.HOME_ROUTINE
                self._move_to_home()

        elif 9 <= self.current_time < 17:
            # Work: 9am-5pm (at workplace)
            if self.has_job:
                self.current_activity = Activity.WORKING
                self.alertness = 0.5  # Moderate alertness at work
                self._move_to_work()
            else:
                self.current_activity = Activity.HOME_ROUTINE
                self._move_to_home()

        elif 17 <= self.current_time < 18:
            # Commute home: 5pm-6pm
            if self.has_job:
                self.current_activity = Activity.COMMUTING_HOME
                self.alertness = 0.6  # Alert while commuting
                self._move_to_home()
            else:
                self.current_activity = Activity.HOME_ROUTINE
                self._move_to_home()

        elif 18 <= self.current_time < 20:
            # Evening activities: 6pm-8pm (shopping, leisure)
            self.current_activity = Activity.EVENING_ACTIVITIES
            self.alertness = 0.7  # Higher alertness, out and about
            # Could move to stores/leisure locations in future
            self._move_to_home()

        else:  # 20-22
            # Home routine: 8pm-10pm (at home)
            self.current_activity = Activity.HOME_ROUTINE
            self.alertness = 0.5  # Moderate alertness
            self._move_to_home()

    def _move_to_home(self):
        """Set target to home location."""
        self.target_x = self.home_x * 32 + 16  # Center of tile
        self.target_y = self.home_y * 32 + 16
        self.moving = True

    def _move_to_work(self):
        """Set target to work location."""
        if self.has_job:
            self.target_x = self.work_x * 32 + 16  # Center of tile
            self.target_y = self.work_y * 32 + 16
            self.moving = True

    def update(self, dt: float, game_time: float):
        """
        Update NPC state.

        Args:
            dt (float): Delta time in seconds
            game_time (float): Current game time in hours (0-24)
        """
        # Update schedule
        self.update_schedule(game_time)

        # Update animation
        if self.moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0.0
                self.animation_frame = 1 - self.animation_frame  # Toggle between 0 and 1
        else:
            # Reset animation when stopped
            self.animation_frame = 0
            self.animation_timer = 0.0

        # Update movement
        if self.moving:
            # Calculate direction to target
            dx = self.target_x - self.world_x
            dy = self.target_y - self.world_y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < 2.0:
                # Reached target
                self.world_x = self.target_x
                self.world_y = self.target_y
                self.moving = False
            else:
                # Move towards target
                move_distance = self.speed * dt
                if move_distance > distance:
                    move_distance = distance

                # Normalize direction and move
                self.world_x += (dx / distance) * move_distance
                self.world_y += (dy / distance) * move_distance

                # Update facing angle based on movement direction
                self.facing_angle = math.degrees(math.atan2(dy, dx))

    def is_in_vision_cone(self, target_x: float, target_y: float) -> bool:
        """
        Check if a point is within the NPC's vision cone.

        Args:
            target_x (float): Target world X
            target_y (float): Target world Y

        Returns:
            bool: True if target is in vision cone
        """
        # Calculate distance
        dx = target_x - self.world_x
        dy = target_y - self.world_y
        distance = math.sqrt(dx * dx + dy * dy)

        # Check range
        if distance > self.vision_range:
            return False

        # Calculate angle to target
        angle_to_target = math.degrees(math.atan2(dy, dx))

        # Calculate angle difference
        angle_diff = abs(angle_to_target - self.facing_angle)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff

        # Check if within vision cone
        return angle_diff <= self.vision_angle / 2

    def calculate_detection_chance(self, robot_x: float, robot_y: float,
                                   is_daytime: bool, robot_stealth: float) -> float:
        """
        Calculate detection chance for a robot.

        Args:
            robot_x (float): Robot world X
            robot_y (float): Robot world Y
            is_daytime (bool): Whether it's daytime (affects visibility)
            robot_stealth (float): Robot stealth level (0.0-1.0)

        Returns:
            float: Detection chance per second (0.0-1.0)
        """
        # Check if in vision cone first
        if not self.is_in_vision_cone(robot_x, robot_y):
            return 0.0

        # Calculate distance factor (closer = easier to detect)
        dx = robot_x - self.world_x
        dy = robot_y - self.world_y
        distance = math.sqrt(dx * dx + dy * dy)
        distance_factor = 1.0 - (distance / self.vision_range)
        distance_factor = max(0.0, min(1.0, distance_factor))

        # Lighting factor
        lighting_factor = 1.0 if is_daytime else 0.5

        # Stealth penalty (lower stealth = easier to detect)
        stealth_factor = 1.0 - robot_stealth

        # Base detection chance
        base_chance = 0.1  # 10% per second at best conditions

        # Combined detection chance
        detection_chance = base_chance * distance_factor * lighting_factor * stealth_factor * self.alertness

        return detection_chance

    def update_detection(self, robot_id: int, detection_chance: float, dt: float) -> bool:
        """
        Update detection progress for a robot.

        Args:
            robot_id (int): Robot ID
            detection_chance (float): Detection chance per second
            dt (float): Delta time

        Returns:
            bool: True if detection reached 100%
        """
        if robot_id not in self.detecting_robots:
            self.detecting_robots[robot_id] = 0.0

        # Increase detection
        self.detecting_robots[robot_id] += detection_chance * dt

        # Cap at 1.0
        self.detecting_robots[robot_id] = min(1.0, self.detecting_robots[robot_id])

        return self.detecting_robots[robot_id] >= 1.0

    def clear_detection(self, robot_id: int):
        """Clear detection progress for a robot."""
        if robot_id in self.detecting_robots:
            del self.detecting_robots[robot_id]

    def render(self, screen: pygame.Surface, camera):
        """
        Render the NPC with directional orientation and walking animation.

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

        # Determine direction (8-way) based on facing_angle
        # 0=E, 45=SE, 90=S, 135=SW, 180=W, 225=NW, 270=N, 315=NE
        angle = self.facing_angle % 360

        # Convert angle to radians for calculations
        angle_rad = math.radians(angle)

        # Draw legs (animated when moving)
        leg_offset = 3 if self.animation_frame == 1 else -3
        leg_length = max(4, int(height_px * 0.3))
        leg_width = max(2, int(width_px * 0.2))

        # Calculate leg positions relative to facing direction
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        # Left and right leg positions (perpendicular to facing direction)
        leg_spread = width_px // 3
        left_offset_x = -sin_a * leg_spread
        left_offset_y = cos_a * leg_spread
        right_offset_x = sin_a * leg_spread
        right_offset_y = -cos_a * leg_spread

        # Draw left leg
        left_leg_x = int(screen_x + left_offset_x)
        left_leg_y = int(screen_y + left_offset_y + height_px//4)
        if self.moving:
            left_leg_y += leg_offset
        left_leg_rect = pygame.Rect(left_leg_x - leg_width//2, left_leg_y, leg_width, leg_length)
        pygame.draw.rect(screen, self.clothing_color, left_leg_rect)

        # Draw right leg
        right_leg_x = int(screen_x + right_offset_x)
        right_leg_y = int(screen_y + right_offset_y + height_px//4)
        if self.moving:
            right_leg_y -= leg_offset
        right_leg_rect = pygame.Rect(right_leg_x - leg_width//2, right_leg_y, leg_width, leg_length)
        pygame.draw.rect(screen, self.clothing_color, right_leg_rect)

        # Draw body (oriented towards facing direction)
        body_width = width_px
        body_height = int(height_px * 0.6)
        body_rect = pygame.Rect(screen_x - body_width//2, screen_y - body_height//2,
                                body_width, body_height)
        pygame.draw.rect(screen, self.clothing_color, body_rect)
        pygame.draw.rect(screen, self.outline_color, body_rect, 1)

        # Draw head (offset slightly in facing direction)
        head_radius = max(3, int(width_px // 3))
        head_offset_x = cos_a * head_radius * 0.5
        head_offset_y = sin_a * head_radius * 0.5
        head_pos = (int(screen_x + head_offset_x), int(screen_y - body_height//2 + head_offset_y))
        pygame.draw.circle(screen, self.skin_color, head_pos, head_radius)
        pygame.draw.circle(screen, self.outline_color, head_pos, head_radius, 1)

        # Draw facing direction indicator (small dot in front)
        indicator_dist = head_radius + 2
        indicator_x = int(head_pos[0] + cos_a * indicator_dist)
        indicator_y = int(head_pos[1] + sin_a * indicator_dist)
        pygame.draw.circle(screen, (50, 50, 50), (indicator_x, indicator_y), 2)

        # Activity indicator (small text above NPC for debugging)
        if camera.zoom >= 0.8:  # Only show when zoomed in enough
            font = pygame.font.Font(None, 14)
            activity_short = {
                Activity.SLEEPING: 'ZZZ',
                Activity.MORNING_ROUTINE: 'MR',
                Activity.COMMUTING_TO_WORK: '→W',
                Activity.WORKING: 'W',
                Activity.COMMUTING_HOME: '→H',
                Activity.EVENING_ACTIVITIES: 'EA',
                Activity.HOME_ROUTINE: 'HR',
            }
            text = activity_short.get(self.current_activity, '?')
            text_surface = font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(screen_x, screen_y - height_px - 8))
            # Background for text
            bg_rect = text_rect.inflate(4, 2)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            screen.blit(text_surface, text_rect)

    def __repr__(self):
        """String representation for debugging."""
        return f"NPC(pos=({self.world_x:.0f}, {self.world_y:.0f}), activity={self.current_activity})"
