"""
Notification System - Manages toast notifications and alerts.

Features:
- Different notification types (info, warning, success, error)
- Queued notifications
- Auto-dismiss after timeout
- Priority system
- Click to dismiss or view details
"""

from enum import Enum
from typing import List, Dict, Optional
import time


class NotificationType(Enum):
    """Notification severity types."""
    INFO = "info"
    WARNING = "warning"
    SUCCESS = "success"
    ERROR = "error"


class Notification:
    """Individual notification."""

    def __init__(self, message: str, notification_type: NotificationType = NotificationType.INFO,
                 duration: float = 5.0, priority: int = 0):
        """
        Initialize notification.

        Args:
            message: Notification message
            notification_type: Type/severity of notification
            duration: How long to display (seconds, 0 = persistent)
            priority: Priority level (higher = more important)
        """
        self.message = message
        self.notification_type = notification_type
        self.duration = duration
        self.priority = priority

        # State
        self.creation_time = time.time()
        self.elapsed_time = 0.0
        self.is_dismissed = False
        self.is_read = False

        # Optional details
        self.title = None
        self.details = None
        self.action_callback = None

    def update(self, dt: float):
        """Update notification timer."""
        self.elapsed_time += dt

    def should_auto_dismiss(self) -> bool:
        """Check if notification should auto-dismiss."""
        if self.duration == 0:  # Persistent
            return False
        return self.elapsed_time >= self.duration

    def dismiss(self):
        """Dismiss this notification."""
        self.is_dismissed = True

    def mark_read(self):
        """Mark notification as read."""
        self.is_read = True

    def get_time_remaining(self) -> float:
        """Get time remaining before auto-dismiss."""
        if self.duration == 0:
            return float('inf')
        return max(0, self.duration - self.elapsed_time)


class NotificationSystem:
    """
    Manages all game notifications.

    Handles notification queue, display, and auto-dismissal.
    """

    def __init__(self, max_visible: int = 5):
        """
        Initialize notification system.

        Args:
            max_visible: Maximum number of visible notifications at once
        """
        self.max_visible = max_visible

        # Active notifications (visible)
        self.active_notifications: List[Notification] = []

        # Notification queue (waiting to be shown)
        self.notification_queue: List[Notification] = []

        # History (dismissed notifications)
        self.notification_history: List[Notification] = []
        self.max_history = 100

        # Statistics
        self.total_notifications = 0
        self.notifications_by_type = {
            NotificationType.INFO: 0,
            NotificationType.WARNING: 0,
            NotificationType.SUCCESS: 0,
            NotificationType.ERROR: 0,
        }

    def notify(self, message: str, notification_type: NotificationType = NotificationType.INFO,
               duration: float = 5.0, priority: int = 0) -> Notification:
        """
        Create and queue a notification.

        Args:
            message: Notification message
            notification_type: Type/severity
            duration: Display duration (0 = persistent)
            priority: Priority level

        Returns:
            Notification: The created notification
        """
        notification = Notification(message, notification_type, duration, priority)

        # Update statistics
        self.total_notifications += 1
        self.notifications_by_type[notification_type] += 1

        # Add to queue or active list
        if len(self.active_notifications) < self.max_visible:
            self.active_notifications.append(notification)
            # Sort by priority
            self.active_notifications.sort(key=lambda n: n.priority, reverse=True)
        else:
            self.notification_queue.append(notification)
            # Sort queue by priority
            self.notification_queue.sort(key=lambda n: n.priority, reverse=True)

        return notification

    def info(self, message: str, duration: float = 5.0):
        """Create info notification."""
        return self.notify(message, NotificationType.INFO, duration)

    def warning(self, message: str, duration: float = 7.0):
        """Create warning notification."""
        return self.notify(message, NotificationType.WARNING, duration, priority=1)

    def success(self, message: str, duration: float = 4.0):
        """Create success notification."""
        return self.notify(message, NotificationType.SUCCESS, duration)

    def error(self, message: str, duration: float = 10.0):
        """Create error notification."""
        return self.notify(message, NotificationType.ERROR, duration, priority=2)

    def update(self, dt: float):
        """
        Update notification system.

        Args:
            dt: Delta time in seconds
        """
        # Update active notifications
        for notification in self.active_notifications[:]:
            notification.update(dt)

            # Check for auto-dismiss
            if notification.should_auto_dismiss() or notification.is_dismissed:
                self._dismiss_notification(notification)

        # Fill empty slots from queue
        while len(self.active_notifications) < self.max_visible and len(self.notification_queue) > 0:
            notification = self.notification_queue.pop(0)
            self.active_notifications.append(notification)

    def _dismiss_notification(self, notification: Notification):
        """Dismiss a notification and move to history."""
        if notification in self.active_notifications:
            self.active_notifications.remove(notification)

        # Add to history
        self.notification_history.append(notification)

        # Trim history if too large
        if len(self.notification_history) > self.max_history:
            self.notification_history.pop(0)

    def dismiss(self, notification: Notification):
        """Manually dismiss a notification."""
        notification.dismiss()

    def dismiss_all(self):
        """Dismiss all active notifications."""
        for notification in self.active_notifications[:]:
            self._dismiss_notification(notification)

    def get_active_notifications(self) -> List[Notification]:
        """Get list of active notifications."""
        return self.active_notifications.copy()

    def get_queue_length(self) -> int:
        """Get number of queued notifications."""
        return len(self.notification_queue)

    def get_unread_count(self) -> int:
        """Get number of unread notifications (active + queued)."""
        unread = sum(1 for n in self.active_notifications if not n.is_read)
        unread += len(self.notification_queue)
        return unread

    def get_history(self, limit: int = 20) -> List[Notification]:
        """
        Get notification history.

        Args:
            limit: Maximum number of historical notifications to return

        Returns:
            List of notifications (most recent first)
        """
        return list(reversed(self.notification_history[-limit:]))

    def clear_history(self):
        """Clear notification history."""
        self.notification_history.clear()

    def get_stats(self) -> Dict:
        """Get notification system statistics."""
        return {
            'total_notifications': self.total_notifications,
            'active_count': len(self.active_notifications),
            'queued_count': len(self.notification_queue),
            'unread_count': self.get_unread_count(),
            'history_count': len(self.notification_history),
            'by_type': {
                'info': self.notifications_by_type[NotificationType.INFO],
                'warning': self.notifications_by_type[NotificationType.WARNING],
                'success': self.notifications_by_type[NotificationType.SUCCESS],
                'error': self.notifications_by_type[NotificationType.ERROR],
            },
        }


# Convenient pre-configured notification templates
class GameNotifications:
    """Pre-configured notification templates for common game events."""

    @staticmethod
    def research_complete(research_name: str, notification_system: NotificationSystem):
        """Notification for research completion."""
        return notification_system.success(f"Research Complete: {research_name}")

    @staticmethod
    def building_complete(building_name: str, notification_system: NotificationSystem):
        """Notification for building completion."""
        return notification_system.success(f"Construction Complete: {building_name}")

    @staticmethod
    def low_power(notification_system: NotificationSystem):
        """Notification for low power."""
        return notification_system.warning("Low Power! Some buildings may shut down.")

    @staticmethod
    def inspection_scheduled(days: int, notification_system: NotificationSystem):
        """Notification for scheduled inspection."""
        return notification_system.warning(f"Inspection scheduled in {days} days!")

    @staticmethod
    def fbi_investigation(notification_system: NotificationSystem):
        """Notification for FBI investigation."""
        return notification_system.error("FBI Investigation Triggered!")

    @staticmethod
    def robot_detected(robot_id: str, notification_system: NotificationSystem):
        """Notification for robot detection."""
        return notification_system.warning(f"Robot {robot_id} detected by camera!")

    @staticmethod
    def material_sold(amount: float, material: str, notification_system: NotificationSystem):
        """Notification for material sale."""
        return notification_system.info(f"Sold {amount:.0f}kg of {material}")

    @staticmethod
    def suspicion_high(level: float, notification_system: NotificationSystem):
        """Notification for high suspicion."""
        return notification_system.error(f"Suspicion Critical: {level:.0f}/100")

    @staticmethod
    def drone_low_battery(drone_id: str, notification_system: NotificationSystem):
        """Notification for drone low battery."""
        return notification_system.info(f"Drone {drone_id} returning (low battery)")
