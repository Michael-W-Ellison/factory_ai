"""
Detection Manager - coordinates NPC detection of illegal robot activities.

Handles:
- Checking all NPCs for line-of-sight to robots
- Calculating detection chances
- Tracking detection progress
- Generating suspicion reports
- Rendering detection UI indicators
"""

import pygame
import math
from typing import List, Tuple, Optional, Dict


class DetectionLevel:
    """Detection level enumeration."""
    GLANCE = 'glance'          # 0-25%: No effect
    NOTICE = 'notice'          # 25-50%: Minor suspicion
    OBSERVE = 'observe'        # 50-75%: Moderate suspicion
    REPORT = 'report'          # 75-100%: Major suspicion


class DetectionManager:
    """
    Manages detection of robots by NPCs.

    Coordinates vision checks, line-of-sight raycasting, and detection progress
    tracking across all NPCs and robots.
    """

    def __init__(self, grid, npc_manager):
        """
        Initialize the detection manager.

        Args:
            grid: The game world grid
            npc_manager: NPCManager instance
        """
        self.grid = grid
        self.npc_manager = npc_manager

        # Detection tracking
        self.detection_reports: List[Dict] = []
        self.last_report_time = 0.0

        # Detection level thresholds
        self.detection_thresholds = {
            DetectionLevel.GLANCE: 0.0,
            DetectionLevel.NOTICE: 0.25,
            DetectionLevel.OBSERVE: 0.50,
            DetectionLevel.REPORT: 0.75,
        }

        # UI colors
        self.detection_colors = {
            DetectionLevel.GLANCE: (200, 200, 200),   # Light gray
            DetectionLevel.NOTICE: (255, 255, 100),   # Yellow
            DetectionLevel.OBSERVE: (255, 150, 50),   # Orange
            DetectionLevel.REPORT: (255, 50, 50),     # Red
        }

    def get_detection_level(self, detection_progress: float) -> str:
        """
        Get detection level based on progress.

        Args:
            detection_progress (float): Detection progress (0.0-1.0)

        Returns:
            str: Detection level
        """
        if detection_progress >= self.detection_thresholds[DetectionLevel.REPORT]:
            return DetectionLevel.REPORT
        elif detection_progress >= self.detection_thresholds[DetectionLevel.OBSERVE]:
            return DetectionLevel.OBSERVE
        elif detection_progress >= self.detection_thresholds[DetectionLevel.NOTICE]:
            return DetectionLevel.NOTICE
        else:
            return DetectionLevel.GLANCE

    def check_line_of_sight(self, npc_x: float, npc_y: float,
                           robot_x: float, robot_y: float) -> bool:
        """
        Check if NPC has line-of-sight to robot (no obstacles blocking).

        Uses simple raycasting to check for buildings and walls.

        Args:
            npc_x (float): NPC world X
            npc_y (float): NPC world Y
            robot_x (float): Robot world X
            robot_y (float): Robot world Y

        Returns:
            bool: True if line-of-sight is clear
        """
        # Calculate ray direction
        dx = robot_x - npc_x
        dy = robot_y - npc_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 1:
            return True  # Too close to matter

        # Normalize direction
        dx /= distance
        dy /= distance

        # Step along ray and check for obstacles
        step_size = self.grid.tile_size / 2  # Check every half tile
        steps = int(distance / step_size)

        for i in range(1, steps):
            # Calculate point along ray
            check_x = npc_x + dx * step_size * i
            check_y = npc_y + dy * step_size * i

            # Convert to grid coordinates
            grid_x = int(check_x / self.grid.tile_size)
            grid_y = int(check_y / self.grid.tile_size)

            # Check if position is valid
            if not (0 <= grid_x < self.grid.width_tiles and 0 <= grid_y < self.grid.height_tiles):
                continue

            tile = self.grid.get_tile(grid_x, grid_y)
            if not tile:
                continue

            # Check for blocking obstacles
            from src.world.tile import TileType
            if tile.tile_type in [TileType.BUILDING, TileType.FACTORY]:
                return False  # Building blocks line-of-sight

        return True  # No obstacles found

    def update(self, robots: List, dt: float) -> List[Dict]:
        """
        Update detection checks for all NPCs and robots.

        Args:
            robots: List of robot entities
            dt (float): Delta time in seconds

        Returns:
            List of detection reports (when NPCs fully detect robots)
        """
        reports = []
        game_time = self.npc_manager.game_time
        is_daytime = 6 <= game_time < 20  # Day is 6am-8pm

        for npc in self.npc_manager.npcs:
            # Skip if sleeping (can't detect)
            from src.entities.npc import Activity
            if npc.current_activity == Activity.SLEEPING:
                continue

            for robot in robots:
                # Get robot stealth level (default to 0.5 if not present)
                robot_stealth = getattr(robot, 'stealth_level', 0.5)

                # Check line-of-sight first
                has_los = self.check_line_of_sight(npc.world_x, npc.world_y,
                                                   robot.x, robot.y)

                if not has_los:
                    # No line-of-sight, decay detection
                    if robot.id in npc.detecting_robots:
                        npc.detecting_robots[robot.id] -= 0.2 * dt
                        if npc.detecting_robots[robot.id] <= 0:
                            npc.clear_detection(robot.id)
                    continue

                # Calculate detection chance
                detection_chance = npc.calculate_detection_chance(
                    robot.x, robot.y, is_daytime, robot_stealth
                )

                if detection_chance > 0:
                    # Update detection progress
                    detected = npc.update_detection(robot.id, detection_chance, dt)

                    # Get current detection level
                    detection_progress = npc.detecting_robots.get(robot.id, 0.0)
                    detection_level = self.get_detection_level(detection_progress)

                    if detected:
                        # Full detection! Generate report
                        report = {
                            'npc': npc,
                            'robot': robot,
                            'time': game_time,
                            'location': (robot.x, robot.y),
                            'suspicion_increase': 15.0,  # Base suspicion increase
                            'detection_level': DetectionLevel.REPORT
                        }
                        reports.append(report)
                        self.detection_reports.append(report)

                        # Reset detection for this robot
                        npc.clear_detection(robot.id)
                    elif detection_level in [DetectionLevel.NOTICE, DetectionLevel.OBSERVE]:
                        # Partial detection - generate minor suspicion
                        if detection_level == DetectionLevel.NOTICE and detection_progress >= 0.25:
                            # Just crossed notice threshold
                            if not hasattr(npc, f'_noticed_{robot.id}'):
                                report = {
                                    'npc': npc,
                                    'robot': robot,
                                    'time': game_time,
                                    'location': (robot.x, robot.y),
                                    'suspicion_increase': 2.0,
                                    'detection_level': DetectionLevel.NOTICE
                                }
                                reports.append(report)
                                setattr(npc, f'_noticed_{robot.id}', True)
                        elif detection_level == DetectionLevel.OBSERVE and detection_progress >= 0.50:
                            # Just crossed observe threshold
                            if not hasattr(npc, f'_observed_{robot.id}'):
                                report = {
                                    'npc': npc,
                                    'robot': robot,
                                    'time': game_time,
                                    'location': (robot.x, robot.y),
                                    'suspicion_increase': 5.0,
                                    'detection_level': DetectionLevel.OBSERVE
                                }
                                reports.append(report)
                                setattr(npc, f'_observed_{robot.id}', True)
                else:
                    # Robot not in vision, decay detection
                    if robot.id in npc.detecting_robots:
                        npc.detecting_robots[robot.id] -= 0.1 * dt
                        if npc.detecting_robots[robot.id] <= 0:
                            npc.clear_detection(robot.id)
                            # Clear threshold flags
                            if hasattr(npc, f'_noticed_{robot.id}'):
                                delattr(npc, f'_noticed_{robot.id}')
                            if hasattr(npc, f'_observed_{robot.id}'):
                                delattr(npc, f'_observed_{robot.id}')

        return reports

    def render_detection_ui(self, screen: pygame.Surface, camera, robots: List):
        """
        Render detection indicators above robots being watched.

        Args:
            screen: Pygame surface
            camera: Camera for world-to-screen transformation
            robots: List of robot entities
        """
        for robot in robots:
            # Check if any NPC is detecting this robot
            max_detection = 0.0
            detecting_npcs = []

            for npc in self.npc_manager.npcs:
                if robot.id in npc.detecting_robots:
                    detection = npc.detecting_robots[robot.id]
                    if detection > 0:
                        detecting_npcs.append(npc)
                        max_detection = max(max_detection, detection)

            if max_detection > 0.05:  # Only show if > 5% detected
                # Get screen position
                screen_x, screen_y = camera.world_to_screen(robot.x, robot.y)

                # Don't render if off screen
                if (screen_x < -50 or screen_x > screen.get_width() + 50 or
                    screen_y < -50 or screen_y > screen.get_height() + 50):
                    continue

                # Render detection meter
                self._render_detection_meter(screen, screen_x, screen_y - 40,
                                            max_detection, camera.zoom)

                # Render warning icon if detection is high
                if max_detection >= 0.5:
                    self._render_warning_icon(screen, screen_x, screen_y - 60,
                                            max_detection, camera.zoom)

    def _render_detection_meter(self, screen: pygame.Surface, x: int, y: int,
                                detection: float, zoom: float):
        """
        Render detection progress meter.

        Args:
            screen: Pygame surface
            x (int): Screen X position
            y (int): Screen Y position
            detection (float): Detection progress (0.0-1.0)
            zoom (float): Camera zoom level
        """
        # Meter dimensions
        meter_width = int(40 * zoom)
        meter_height = int(6 * zoom)
        meter_x = x - meter_width // 2
        meter_y = y

        # Background
        pygame.draw.rect(screen, (40, 40, 40), (meter_x, meter_y, meter_width, meter_height))

        # Fill based on detection level
        detection_level = self.get_detection_level(detection)
        fill_color = self.detection_colors[detection_level]
        fill_width = int(meter_width * detection)
        pygame.draw.rect(screen, fill_color, (meter_x, meter_y, fill_width, meter_height))

        # Border
        pygame.draw.rect(screen, (200, 200, 200), (meter_x, meter_y, meter_width, meter_height), 1)

    def _render_warning_icon(self, screen: pygame.Surface, x: int, y: int,
                            detection: float, zoom: float):
        """
        Render warning icon above robot.

        Args:
            screen: Pygame surface
            x (int): Screen X position
            y (int): Screen Y position
            detection (float): Detection progress (0.0-1.0)
            zoom (float): Camera zoom level
        """
        # Icon size
        icon_size = int(16 * zoom)

        # Pulsing effect based on detection level
        pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 200.0)
        alpha = int(150 + 105 * pulse * detection)

        # Create warning triangle
        points = [
            (x, y),  # Top
            (x - icon_size // 2, y + icon_size),  # Bottom left
            (x + icon_size // 2, y + icon_size),  # Bottom right
        ]

        # Draw triangle with warning color
        detection_level = self.get_detection_level(detection)
        color = self.detection_colors[detection_level]

        # Draw filled triangle
        pygame.draw.polygon(screen, color, points)
        # Draw border
        pygame.draw.polygon(screen, (0, 0, 0), points, 2)

        # Draw exclamation mark
        if zoom >= 0.8:
            font = pygame.font.Font(None, int(14 * zoom))
            text = font.render('!', True, (0, 0, 0))
            text_rect = text.get_rect(center=(x, y + icon_size // 2))
            screen.blit(text, text_rect)

    def get_recent_reports(self, count: int = 10) -> List[Dict]:
        """
        Get most recent detection reports.

        Args:
            count (int): Number of reports to return

        Returns:
            List of recent detection reports
        """
        return self.detection_reports[-count:] if self.detection_reports else []

    def get_stats(self) -> Dict:
        """
        Get detection system statistics.

        Returns:
            Dictionary with detection stats
        """
        total_reports = len(self.detection_reports)

        # Count by detection level
        by_level = {}
        for report in self.detection_reports:
            level = report.get('detection_level', DetectionLevel.REPORT)
            by_level[level] = by_level.get(level, 0) + 1

        # Count currently being detected
        being_detected = 0
        for npc in self.npc_manager.npcs:
            if npc.detecting_robots:
                being_detected += len(npc.detecting_robots)

        return {
            'total_reports': total_reports,
            'by_level': by_level,
            'currently_being_detected': being_detected,
        }
