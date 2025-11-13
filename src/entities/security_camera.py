"""
SecurityCamera - Surveillance cameras that detect robots in their vision cone.

Cameras are placed throughout the city and automatically detect robots.
Can be hacked with research upgrades to temporarily disable them.
"""

import pygame
import math
from typing import Optional, List, Tuple


class CameraStatus:
    """Camera status enumeration."""
    ACTIVE = 0
    DISABLED = 1  # Temporarily disabled by hacking
    BROKEN = 2     # Permanently broken


class SecurityCamera:
    """
    Security camera that detects robots in its vision cone.

    Attributes:
        world_x (float): World X position
        world_y (float): World Y position
        facing_angle (float): Direction camera faces (degrees, 0=East)
        vision_range (float): Detection range in pixels
        vision_angle (float): Vision cone angle in degrees
        status (int): Camera status (active, disabled, broken)
        disabled_timer (float): Time remaining disabled (seconds)
    """

    def __init__(self, world_x: float, world_y: float, facing_angle: float = 0):
        """
        Initialize a security camera.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
            facing_angle (float): Direction camera faces (degrees, 0=East)
        """
        self.world_x = world_x
        self.world_y = world_y
        self.facing_angle = facing_angle  # 0=East, 90=South, 180=West, 270=North

        # Detection properties
        self.vision_range = 200.0  # Detection range in pixels
        self.vision_angle = 90.0   # Vision cone angle (90 degrees)

        # Status
        self.status = CameraStatus.ACTIVE
        self.disabled_timer = 0.0  # Seconds remaining disabled
        self.disabled_duration = 300.0  # 5 minutes default disable time

        # Detection tracking
        self.last_detection_time = 0.0
        self.detection_cooldown = 2.0  # Seconds between detections of same robot

        # Visual properties
        self.camera_size = 8
        self.camera_color = (60, 60, 60)  # Dark gray
        self.lens_color = (200, 50, 50)  # Red lens

        # ID for tracking
        self.id = id(self)

    def update(self, dt: float):
        """
        Update camera state.

        Args:
            dt (float): Delta time in seconds
        """
        # Update disabled timer
        if self.status == CameraStatus.DISABLED:
            self.disabled_timer -= dt

            if self.disabled_timer <= 0:
                # Re-enable camera
                self.status = CameraStatus.ACTIVE
                self.disabled_timer = 0.0

    def is_active(self) -> bool:
        """Check if camera is currently active."""
        return self.status == CameraStatus.ACTIVE

    def is_disabled(self) -> bool:
        """Check if camera is currently disabled."""
        return self.status == CameraStatus.DISABLED

    def is_broken(self) -> bool:
        """Check if camera is broken."""
        return self.status == CameraStatus.BROKEN

    def disable(self, duration: Optional[float] = None):
        """
        Disable the camera temporarily.

        Args:
            duration (float): How long to disable (seconds), or use default
        """
        if self.status == CameraStatus.BROKEN:
            return  # Can't disable broken camera

        self.status = CameraStatus.DISABLED
        self.disabled_timer = duration if duration is not None else self.disabled_duration

    def break_camera(self):
        """Permanently break the camera."""
        self.status = CameraStatus.BROKEN
        self.disabled_timer = 0.0

    def repair(self):
        """Repair a broken camera."""
        if self.status == CameraStatus.BROKEN:
            self.status = CameraStatus.ACTIVE
            self.disabled_timer = 0.0

    def is_point_in_vision_cone(self, x: float, y: float) -> bool:
        """
        Check if a point is within the camera's vision cone.

        Args:
            x (float): World X position
            y (float): World Y position

        Returns:
            bool: True if point is in vision cone
        """
        if not self.is_active():
            return False

        # Calculate distance
        dx = x - self.world_x
        dy = y - self.world_y
        distance = math.sqrt(dx * dx + dy * dy)

        # Check if within range
        if distance > self.vision_range:
            return False

        # Calculate angle to point
        angle_to_point = math.degrees(math.atan2(dy, dx))

        # Normalize angles to 0-360
        angle_to_point = (angle_to_point + 360) % 360
        facing = (self.facing_angle + 360) % 360

        # Calculate angle difference
        angle_diff = abs(angle_to_point - facing)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff

        # Check if within vision cone
        return angle_diff <= self.vision_angle / 2

    def detect_robot(self, robot) -> bool:
        """
        Check if a robot is detected by this camera.

        Args:
            robot: Robot entity to check

        Returns:
            bool: True if robot is detected
        """
        if not self.is_active():
            return False

        # Check if robot is in vision cone
        return self.is_point_in_vision_cone(robot.world_x, robot.world_y)

    def render(self, screen: pygame.Surface, camera):
        """
        Render the camera and its vision cone.

        Args:
            screen: Pygame surface
            camera: Camera for world-to-screen transformation
        """
        # Calculate screen position
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)

        # Apply camera zoom
        size = max(4, int(self.camera_size * camera.zoom))

        # Don't render if off screen
        if (screen_x + size < 0 or screen_x - size > screen.get_width() or
            screen_y + size < 0 or screen_y - size > screen.get_height()):
            return

        # Render vision cone (if active and zoomed in enough)
        if camera.zoom >= 0.5:
            self._render_vision_cone(screen, camera, screen_x, screen_y)

        # Render camera body
        self._render_camera_body(screen, screen_x, screen_y, size)

    def _render_vision_cone(self, screen, cam, screen_x, screen_y):
        """Render the camera's vision cone."""
        if not self.is_active():
            return

        # Calculate vision cone arc
        range_pixels = int(self.vision_range * cam.zoom)

        # Convert facing angle to radians
        facing_rad = math.radians(self.facing_angle)
        half_angle_rad = math.radians(self.vision_angle / 2)

        # Calculate arc points
        num_points = 20
        arc_points = [(screen_x, screen_y)]

        for i in range(num_points + 1):
            # Angle from -half to +half
            angle = facing_rad - half_angle_rad + (2 * half_angle_rad * i / num_points)
            px = screen_x + int(range_pixels * math.cos(angle))
            py = screen_y + int(range_pixels * math.sin(angle))
            arc_points.append((px, py))

        arc_points.append((screen_x, screen_y))

        # Draw vision cone (semi-transparent)
        if len(arc_points) >= 3:
            # Draw filled cone
            cone_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            cone_color = (255, 100, 100, 30)  # Semi-transparent red
            pygame.draw.polygon(cone_surface, cone_color, arc_points)
            screen.blit(cone_surface, (0, 0))

            # Draw cone outline
            pygame.draw.lines(screen, (255, 100, 100), False, arc_points, 1)

    def _render_camera_body(self, screen, screen_x, screen_y, size):
        """Render the camera body."""
        # Choose color based on status
        if self.status == CameraStatus.ACTIVE:
            body_color = self.camera_color
            lens_color = self.lens_color
        elif self.status == CameraStatus.DISABLED:
            body_color = (100, 100, 100)  # Gray
            lens_color = (150, 150, 150)  # Light gray
        else:  # BROKEN
            body_color = (40, 40, 40)  # Dark gray
            lens_color = (80, 80, 80)  # Darker gray

        # Draw camera body (rectangle)
        camera_rect = pygame.Rect(screen_x - size // 2, screen_y - size // 2, size, size)
        pygame.draw.rect(screen, body_color, camera_rect)
        pygame.draw.rect(screen, (0, 0, 0), camera_rect, 1)  # Outline

        # Draw lens (circle)
        lens_radius = max(2, size // 3)
        pygame.draw.circle(screen, lens_color, (screen_x, screen_y), lens_radius)

        # Draw direction indicator (small line)
        if size >= 6:
            facing_rad = math.radians(self.facing_angle)
            end_x = screen_x + int((size // 2 + 3) * math.cos(facing_rad))
            end_y = screen_y + int((size // 2 + 3) * math.sin(facing_rad))
            pygame.draw.line(screen, lens_color, (screen_x, screen_y), (end_x, end_y), 2)

    def get_status_string(self) -> str:
        """Get a string representation of camera status."""
        if self.status == CameraStatus.ACTIVE:
            return "ACTIVE"
        elif self.status == CameraStatus.DISABLED:
            return f"DISABLED ({int(self.disabled_timer)}s)"
        else:
            return "BROKEN"

    def __repr__(self):
        """String representation for debugging."""
        return (f"SecurityCamera(pos=({self.world_x:.0f}, {self.world_y:.0f}), "
                f"facing={self.facing_angle:.0f}°, status={self.get_status_string()})")
