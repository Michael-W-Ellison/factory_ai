"""
CameraHackingManager - manages camera hacking interactions and consequences.

Handles:
- Camera hacking interactions (click to hack)
- Hacking progress tracking
- Camera disabling with timers
- Suspicion increase on hacks
- Security upgrades after excessive hacking
- FBI investigation trigger
"""

import pygame
from typing import List, Optional, Tuple
from src.entities.security_camera import SecurityCamera


class CameraHackingManager:
    """
    Manages camera hacking system.

    Allows players to hack cameras to temporarily disable them,
    but tracks hacking activity and triggers consequences.
    """

    def __init__(self, camera_manager, research_manager, suspicion_manager):
        """
        Initialize camera hacking manager.

        Args:
            camera_manager: CameraManager instance
            research_manager: ResearchManager instance
            suspicion_manager: SuspicionManager instance
        """
        self.camera_manager = camera_manager
        self.research = research_manager
        self.suspicion = suspicion_manager

        # Hacking state
        self.hacking_enabled = False
        self.hack_count_limit = 1  # How many cameras can be hacked at once
        self.hack_duration = 300.0  # Default 5 minutes

        # Hacking progress
        self.currently_hacking = False
        self.hack_target: Optional[SecurityCamera] = None
        self.hack_progress = 0.0
        self.hack_time_required = 3.0  # 3 seconds to hack

        # Hacking history
        self.total_hacks = 0  # Total hacks performed this game
        self.recent_hacks = []  # List of (camera, timestamp) for cooldown

        # Consequences
        self.suspicion_per_hack = 2  # Suspicion added per hack
        self.security_upgrade_threshold = 10  # Hacks before security upgrade
        self.fbi_threshold = 20  # Hacks before FBI investigation
        self.security_upgrade_triggered = False
        self.fbi_investigation_triggered = False

        # UI state
        self.selected_camera: Optional[SecurityCamera] = None
        self.mouse_hover_camera: Optional[SecurityCamera] = None

    def update_from_research(self):
        """Update hacking capabilities from research."""
        # Check if camera hacking is unlocked
        self.hacking_enabled = self.research.is_completed("camera_hacking_1")

        if not self.hacking_enabled:
            return

        # Get hack count limit (how many cameras can be hacked at once)
        if self.research.is_completed("camera_hacking_3"):
            self.hack_count_limit = 3
        elif self.research.is_completed("camera_hacking_2"):
            self.hack_count_limit = 1
        elif self.research.is_completed("camera_hacking_1"):
            self.hack_count_limit = 1

        # Get hack duration
        effects = self.research.active_effects
        self.hack_duration = effects.get("camera_hack_duration", 300.0)

    def update(self, dt: float, game_time: float):
        """
        Update hacking progress and check for consequences.

        Args:
            dt (float): Delta time in seconds
            game_time (float): Current game time
        """
        # Update research effects
        self.update_from_research()

        # Update hacking progress
        if self.currently_hacking and self.hack_target:
            self.hack_progress += dt

            if self.hack_progress >= self.hack_time_required:
                # Hacking complete!
                self._complete_hack(game_time)

        # Check for consequences
        self._check_consequences()

    def handle_click(self, world_x: float, world_y: float, game_time: float) -> bool:
        """
        Handle click on camera to start hacking.

        Args:
            world_x (float): World X position of click
            world_y (float): World Y position of click
            game_time (float): Current game time

        Returns:
            bool: True if click was handled (started hacking)
        """
        if not self.hacking_enabled:
            return False

        # Check if already hacking
        if self.currently_hacking:
            return False

        # Find camera at click position
        camera = self._get_camera_at_position(world_x, world_y)

        if camera is None:
            return False

        # Check if camera is already disabled
        if camera.is_disabled():
            print("Camera is already disabled")
            return False

        # Check if we've reached hack count limit
        currently_hacked = self.camera_manager.get_disabled_camera_count()
        if currently_hacked >= self.hack_count_limit:
            print(f"Hack limit reached ({self.hack_count_limit} cameras)")
            return False

        # Start hacking
        self._start_hack(camera)
        return True

    def _start_hack(self, camera: SecurityCamera):
        """Start hacking a camera."""
        self.currently_hacking = True
        self.hack_target = camera
        self.hack_progress = 0.0
        print(f"Started hacking camera at ({camera.world_x:.0f}, {camera.world_y:.0f})")

    def _complete_hack(self, game_time: float):
        """Complete the hack and disable the camera."""
        if self.hack_target is None:
            return

        # Disable the camera
        self.camera_manager.disable_camera(self.hack_target, self.hack_duration)

        # Track the hack
        self.total_hacks += 1
        self.recent_hacks.append((self.hack_target, game_time))

        # Add suspicion
        self.suspicion.add_suspicion(
            self.suspicion_per_hack,
            f"Camera hacked at ({self.hack_target.world_x:.0f}, {self.hack_target.world_y:.0f})"
        )

        print(f"✓ Camera hacked! Disabled for {self.hack_duration:.0f}s")
        print(f"  Total hacks: {self.total_hacks}, Suspicion: +{self.suspicion_per_hack}")

        # Reset hacking state
        self.currently_hacking = False
        self.hack_target = None
        self.hack_progress = 0.0

    def _get_camera_at_position(self, world_x: float, world_y: float, radius: float = 20.0) -> Optional[SecurityCamera]:
        """
        Find camera near a world position.

        Args:
            world_x (float): World X position
            world_y (float): World Y position
            radius (float): Click radius

        Returns:
            SecurityCamera: Camera at position, or None
        """
        for camera in self.camera_manager.cameras:
            dx = camera.world_x - world_x
            dy = camera.world_y - world_y
            distance = (dx * dx + dy * dy) ** 0.5

            if distance <= radius:
                return camera

        return None

    def _check_consequences(self):
        """Check and trigger consequences of excessive hacking."""
        # Security upgrade after 10 hacks
        if self.total_hacks >= self.security_upgrade_threshold and not self.security_upgrade_triggered:
            self._trigger_security_upgrade()

        # FBI investigation after 20 hacks
        if self.total_hacks >= self.fbi_threshold and not self.fbi_investigation_triggered:
            self._trigger_fbi_investigation()

    def _trigger_security_upgrade(self):
        """Trigger security upgrade (more cameras, better detection)."""
        self.security_upgrade_triggered = True

        # Add more cameras (5-10 new cameras)
        import random
        new_cameras = random.randint(5, 10)

        print(f"\n⚠️ SECURITY UPGRADE TRIGGERED!")
        print(f"  City is adding {new_cameras} new security cameras")
        print(f"  Detection systems upgraded")

        # Add new cameras at random road/building locations
        grid = self.camera_manager.grid
        tile_size = grid.tile_size
        placed_count = 0

        # Try to place cameras at random locations
        max_attempts = new_cameras * 5
        for _ in range(max_attempts):
            if placed_count >= new_cameras:
                break

            # Random position in grid
            grid_x = random.randint(0, grid.width_tiles - 1)
            grid_y = random.randint(0, grid.height_tiles - 1)

            # Convert to world position
            world_x = grid_x * tile_size + tile_size / 2
            world_y = grid_y * tile_size + tile_size / 2

            # Random facing direction
            facing_angle = random.choice([0, 90, 180, 270])

            # Create and add camera
            camera = SecurityCamera(world_x, world_y, facing_angle)
            self.camera_manager.cameras.append(camera)
            placed_count += 1

        print(f"  Successfully placed {placed_count} new cameras")

        # Add suspicion
        self.suspicion.add_suspicion(10, "Security upgrade due to excessive camera hacking")

    def _trigger_fbi_investigation(self):
        """Trigger FBI investigation (major consequence)."""
        self.fbi_investigation_triggered = True

        print(f"\n🚨 FBI INVESTIGATION TRIGGERED!")
        print(f"  Excessive camera hacking detected ({self.total_hacks} hacks)")
        print(f"  Federal authorities are investigating")

        # Major suspicion increase
        self.suspicion.add_suspicion(30, "FBI investigation triggered by excessive hacking")

        # TODO: In future, integrate with FBI system (Phase 9)

    def cancel_hack(self):
        """Cancel current hacking attempt."""
        if self.currently_hacking:
            print("Hacking cancelled")
            self.currently_hacking = False
            self.hack_target = None
            self.hack_progress = 0.0

    def get_hack_progress_percent(self) -> float:
        """Get current hacking progress as percentage (0-100)."""
        if not self.currently_hacking:
            return 0.0
        return (self.hack_progress / self.hack_time_required) * 100.0

    def can_hack_cameras(self) -> bool:
        """Check if camera hacking is currently available."""
        if not self.hacking_enabled:
            return False

        currently_hacked = self.camera_manager.get_disabled_camera_count()
        return currently_hacked < self.hack_count_limit

    def render_ui(self, screen, camera, font=None):
        """
        Render hacking UI (progress bar, info).

        Args:
            screen: Pygame surface
            camera: Camera for world-to-screen conversion
            font: Font for text (optional)
        """
        if font is None:
            font = pygame.font.Font(None, 24)

        # Render hacking progress
        if self.currently_hacking and self.hack_target:
            self._render_hack_progress(screen, camera, font)

        # Render camera info on hover
        if self.mouse_hover_camera:
            self._render_camera_info(screen, camera, font)

    def _render_hack_progress(self, screen, camera_view, font):
        """Render hacking progress bar."""
        if self.hack_target is None:
            return

        # Get screen position of target camera
        screen_x, screen_y = camera_view.world_to_screen(
            self.hack_target.world_x,
            self.hack_target.world_y
        )

        # Draw progress bar above camera
        bar_width = 80
        bar_height = 10
        bar_x = screen_x - bar_width // 2
        bar_y = screen_y - 30

        # Background
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # Progress
        progress = self.get_hack_progress_percent() / 100.0
        fill_width = int(bar_width * progress)
        pygame.draw.rect(screen, (255, 200, 0), (bar_x, bar_y, fill_width, bar_height))

        # Outline
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 1)

        # Text
        text = font.render("Hacking...", True, (255, 200, 0))
        text_rect = text.get_rect(center=(screen_x, bar_y - 12))
        screen.blit(text, text_rect)

    def _render_camera_info(self, screen, camera_view, font):
        """Render camera info on mouse hover."""
        cam = self.mouse_hover_camera

        # Get screen position
        screen_x, screen_y = camera_view.world_to_screen(cam.world_x, cam.world_y)

        # Draw info box
        info_lines = [
            f"Camera",
            f"Status: {cam.get_status_string()}",
        ]

        if cam.is_disabled():
            info_lines.append(f"Time: {int(cam.disabled_timer)}s")

        # Calculate box size
        line_height = 18
        box_height = len(info_lines) * line_height + 10
        box_width = 150

        box_x = screen_x + 20
        box_y = screen_y - box_height // 2

        # Draw background
        box_surface = pygame.Surface((box_width, box_height))
        box_surface.set_alpha(200)
        box_surface.fill((30, 30, 30))
        screen.blit(box_surface, (box_x, box_y))

        # Draw border
        pygame.draw.rect(screen, (100, 100, 100), (box_x, box_y, box_width, box_height), 1)

        # Draw text
        small_font = pygame.font.Font(None, 18)
        for i, line in enumerate(info_lines):
            text = small_font.render(line, True, (200, 200, 200))
            screen.blit(text, (box_x + 5, box_y + 5 + i * line_height))

    def update_mouse_hover(self, world_x: float, world_y: float):
        """Update which camera is being hovered."""
        self.mouse_hover_camera = self._get_camera_at_position(world_x, world_y)

    def __repr__(self):
        """String representation for debugging."""
        return (f"CameraHackingManager(enabled={self.hacking_enabled}, "
                f"total_hacks={self.total_hacks}, "
                f"limit={self.hack_count_limit})")
