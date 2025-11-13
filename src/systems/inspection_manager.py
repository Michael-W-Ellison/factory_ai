"""
InspectionManager - manages factory inspections and consequences.

Handles:
- Scheduling inspections when suspicion reaches 60+
- Countdown timers (24-48 game hours warning)
- Inspection process (1 game hour)
- Pass/fail logic based on illegal materials
- Consequences (suspicion changes, fines, restrictions, game over)
"""

import random
from enum import Enum
from typing import Optional, Dict


class InspectionStatus(Enum):
    """Inspection status states."""
    NONE = 0  # No inspection scheduled
    SCHEDULED = 1  # Inspection scheduled, countdown active
    IN_PROGRESS = 2  # Inspector is currently inspecting
    COMPLETED = 3  # Inspection completed, results available


class InspectionResult(Enum):
    """Inspection result outcomes."""
    PASS = 0  # Clean - no illegal materials found
    FAIL_MINOR = 1  # Minor violations - some questionable materials
    FAIL_MAJOR = 2  # Major violations - clear illegal materials
    FAIL_CRITICAL = 3  # Critical violations - game over


class InspectionManager:
    """
    Manages factory inspection system.

    Inspections are triggered when suspicion reaches 60+.
    Players get 24-48 game hours warning before inspection.
    """

    def __init__(self, resource_manager, suspicion_manager):
        """
        Initialize inspection manager.

        Args:
            resource_manager: ResourceManager instance
            suspicion_manager: SuspicionManager instance
        """
        self.resources = resource_manager
        self.suspicion = suspicion_manager

        # Inspection state
        self.status = InspectionStatus.NONE
        self.inspection_scheduled = False
        self.inspection_time = 0.0  # Game time when inspection will occur
        self.countdown = 0.0  # Time remaining until inspection
        self.inspection_progress = 0.0  # Progress during inspection (0-1)

        # Inspection result
        self.last_result: Optional[InspectionResult] = None
        self.last_inspection_time = -999999.0  # Game time of last inspection

        # Thresholds
        self.suspicion_trigger_threshold = 60  # Trigger at 60 suspicion
        self.min_warning_time = 86400.0  # 24 hours in game seconds (24 * 3600)
        self.max_warning_time = 172800.0  # 48 hours in game seconds (48 * 3600)
        self.inspection_duration = 3600.0  # 1 hour in game seconds
        self.immunity_duration = 604800.0  # 7 days in game seconds (for PASS)
        self.reinspection_interval = 259200.0  # 3 days in game seconds (for FAIL_MINOR)

        # Illegal material counts (simplified - will be expanded in Phase 8.4)
        self.illegal_material_count = 0
        self.illegal_material_value = 0

    def update(self, dt: float, game_time: float):
        """
        Update inspection system.

        Args:
            dt (float): Delta time in seconds
            game_time (float): Current game time
        """
        # Check if we should schedule an inspection
        if not self.inspection_scheduled and self.status == InspectionStatus.NONE:
            self._check_schedule_inspection(game_time)

        # Update countdown
        if self.status == InspectionStatus.SCHEDULED:
            self.countdown -= dt

            # Check if inspection should start
            if self.countdown <= 0:
                self._start_inspection(game_time)

        # Update inspection progress
        elif self.status == InspectionStatus.IN_PROGRESS:
            self.inspection_progress += dt / self.inspection_duration

            # Check if inspection is complete
            if self.inspection_progress >= 1.0:
                self._complete_inspection(game_time)

    def _check_schedule_inspection(self, game_time: float):
        """Check if inspection should be scheduled."""
        # Check suspicion threshold
        if self.suspicion.suspicion_level < self.suspicion_trigger_threshold:
            return

        # Check immunity period (after passing inspection)
        if game_time - self.last_inspection_time < self.immunity_duration:
            return

        # Schedule inspection
        self._schedule_inspection(game_time)

    def _schedule_inspection(self, game_time: float):
        """Schedule an inspection with random warning time."""
        # Random warning time (24-48 hours)
        warning_time = random.uniform(self.min_warning_time, self.max_warning_time)

        self.status = InspectionStatus.SCHEDULED
        self.inspection_scheduled = True
        self.inspection_time = game_time + warning_time
        self.countdown = warning_time

        # Calculate countdown in game hours
        hours = warning_time / 3600.0

        print(f"\n⚠️ INSPECTION SCHEDULED!")
        print(f"  Government inspector will arrive in {hours:.1f} game hours")
        print(f"  Current suspicion: {self.suspicion.suspicion_level}")
        print(f"  Prepare your factory for inspection!")

    def _start_inspection(self, game_time: float):
        """Start the inspection process."""
        self.status = InspectionStatus.IN_PROGRESS
        self.inspection_progress = 0.0
        self.last_inspection_time = game_time

        print(f"\n🕵️ INSPECTION STARTED!")
        print(f"  Inspector is searching your factory...")
        print(f"  This will take {self.inspection_duration / 3600.0:.1f} game hour")

    def _complete_inspection(self, game_time: float):
        """Complete inspection and determine result."""
        self.status = InspectionStatus.COMPLETED
        self.inspection_progress = 1.0

        # Determine inspection result
        result = self._calculate_inspection_result()
        self.last_result = result

        # Apply consequences
        self._apply_consequences(result)

        # Reset state
        self._reset_inspection_state()

    def _calculate_inspection_result(self) -> InspectionResult:
        """
        Calculate inspection result based on illegal materials and suspicion.

        For now, uses a probability-based system.
        In Phase 8.4, will check actual illegal material tags.

        Returns:
            InspectionResult: The inspection outcome
        """
        # Simplified probability-based system for now
        # Higher suspicion = higher chance of failing

        # Base probabilities (will be modified by illegal materials in Phase 8.4)
        suspicion_level = self.suspicion.suspicion_level

        if suspicion_level < 60:
            # Should not be inspected, but just in case
            return InspectionResult.PASS

        elif suspicion_level < 80:
            # Low risk - 70% pass, 25% minor fail, 5% major fail
            roll = random.random()
            if roll < 0.70:
                return InspectionResult.PASS
            elif roll < 0.95:
                return InspectionResult.FAIL_MINOR
            else:
                return InspectionResult.FAIL_MAJOR

        elif suspicion_level < 100:
            # Medium risk - 40% pass, 40% minor fail, 15% major fail, 5% critical
            roll = random.random()
            if roll < 0.40:
                return InspectionResult.PASS
            elif roll < 0.80:
                return InspectionResult.FAIL_MINOR
            elif roll < 0.95:
                return InspectionResult.FAIL_MAJOR
            else:
                return InspectionResult.FAIL_CRITICAL

        else:  # >= 100
            # High risk - 10% pass, 30% minor, 40% major, 20% critical
            roll = random.random()
            if roll < 0.10:
                return InspectionResult.PASS
            elif roll < 0.40:
                return InspectionResult.FAIL_MINOR
            elif roll < 0.80:
                return InspectionResult.FAIL_MAJOR
            else:
                return InspectionResult.FAIL_CRITICAL

    def _apply_consequences(self, result: InspectionResult):
        """
        Apply consequences based on inspection result.

        Args:
            result (InspectionResult): The inspection outcome
        """
        print(f"\n📋 INSPECTION RESULTS: {result.name}")

        if result == InspectionResult.PASS:
            # PASS: suspicion -20, no inspection for 7 days
            self.suspicion.add_suspicion(-20, "Passed factory inspection")
            print(f"  ✓ PASSED - Factory is clean!")
            print(f"  ✓ Suspicion reduced by 20")
            print(f"  ✓ No inspection for 7 days")

        elif result == InspectionResult.FAIL_MINOR:
            # FAIL (minor): suspicion +10, fine $5000, reinspection in 3 days
            self.suspicion.add_suspicion(10, "Failed inspection (minor violations)")
            self.resources.modify_money(-5000)
            print(f"  ⚠️ FAILED (Minor) - Some questionable materials found")
            print(f"  ⚠️ Fine: $5,000")
            print(f"  ⚠️ Suspicion increased by 10")
            print(f"  ⚠️ Reinspection in 3 days")
            # TODO: Schedule reinspection in 3 days

        elif result == InspectionResult.FAIL_MAJOR:
            # FAIL (major): suspicion +30, fine $20000, restrictions applied
            self.suspicion.add_suspicion(30, "Failed inspection (major violations)")
            self.resources.modify_money(-20000)
            print(f"  🚨 FAILED (Major) - Illegal materials discovered!")
            print(f"  🚨 Fine: $20,000")
            print(f"  🚨 Suspicion increased by 30")
            print(f"  🚨 Operating restrictions applied")
            # TODO: Apply restrictions

        elif result == InspectionResult.FAIL_CRITICAL:
            # FAIL (critical): game over (FBI raid immediate)
            print(f"  💀 FAILED (Critical) - GAME OVER!")
            print(f"  💀 Extensive illegal operation discovered")
            print(f"  💀 FBI raid in progress")
            print(f"  💀 Factory shut down")
            # TODO: Trigger game over

    def _reset_inspection_state(self):
        """Reset inspection state after completion."""
        self.status = InspectionStatus.NONE
        self.inspection_scheduled = False
        self.inspection_progress = 0.0
        self.countdown = 0.0

    def force_schedule_inspection(self, game_time: float, warning_hours: float = 24.0):
        """
        Force schedule an inspection (for testing).

        Args:
            game_time (float): Current game time
            warning_hours (float): Warning time in game hours
        """
        warning_time = warning_hours * 3600.0  # Convert to seconds

        self.status = InspectionStatus.SCHEDULED
        self.inspection_scheduled = True
        self.inspection_time = game_time + warning_time
        self.countdown = warning_time

    def get_countdown_hours(self) -> float:
        """Get countdown time in game hours."""
        return self.countdown / 3600.0

    def is_inspection_scheduled(self) -> bool:
        """Check if inspection is scheduled."""
        return self.status == InspectionStatus.SCHEDULED

    def is_inspection_in_progress(self) -> bool:
        """Check if inspection is in progress."""
        return self.status == InspectionStatus.IN_PROGRESS

    def get_inspection_progress_percent(self) -> float:
        """Get inspection progress as percentage (0-100)."""
        return self.inspection_progress * 100.0

    def set_illegal_material_count(self, count: int, value: int = 0):
        """
        Set illegal material count (for Phase 8.4 integration).

        Args:
            count (int): Number of illegal materials
            value (int): Total value of illegal materials
        """
        self.illegal_material_count = count
        self.illegal_material_value = value

    def get_status_summary(self) -> Dict:
        """
        Get inspection status summary for UI.

        Returns:
            dict: Status information
        """
        return {
            'status': self.status,
            'scheduled': self.inspection_scheduled,
            'countdown_hours': self.get_countdown_hours(),
            'in_progress': self.is_inspection_in_progress(),
            'progress_percent': self.get_inspection_progress_percent(),
            'last_result': self.last_result,
            'suspicion': self.suspicion.suspicion_level,
            'trigger_threshold': self.suspicion_trigger_threshold
        }

    def __repr__(self):
        """String representation for debugging."""
        return (f"InspectionManager(status={self.status.name}, "
                f"scheduled={self.inspection_scheduled}, "
                f"countdown={self.get_countdown_hours():.1f}h)")
