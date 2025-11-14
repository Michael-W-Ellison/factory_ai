"""
FBI Manager - Manages FBI investigation and raid mechanics.

Handles:
- FBI trigger conditions
- Investigation countdown
- FBI agent presence
- Raid mechanics
- Avoidance strategies
"""

from typing import Optional, Dict, List
from enum import Enum


class FBIStatus(Enum):
    """FBI investigation status."""
    NONE = "none"                          # No investigation
    TRIGGERED = "triggered"                # Investigation triggered, countdown started
    INVESTIGATING = "investigating"        # Active investigation
    RAID_IMMINENT = "raid_imminent"       # Raid will happen soon
    RAIDED = "raided"                     # Factory raided (game over)


class FBITrigger(Enum):
    """FBI investigation triggers."""
    HIGH_SUSPICION = "high_suspicion"           # Suspicion > 80 for 7 days
    CRITICAL_INSPECTION = "critical_inspection" # Failed critical inspection
    EXCESSIVE_HACKING = "excessive_hacking"     # > 20 camera hacks
    MULTIPLE_FAILURES = "multiple_failures"     # 3 failed inspections
    ANONYMOUS_TIP = "anonymous_tip"             # Random event


class FBIManager:
    """
    Manages FBI investigation system.

    The FBI represents the highest level of authority escalation.
    Once triggered, the player has limited time to reduce suspicion
    or face a raid (game over).
    """

    def __init__(self, resource_manager, suspicion_manager):
        """
        Initialize FBI manager.

        Args:
            resource_manager: ResourceManager for bribery costs
            suspicion_manager: SuspicionManager for tracking suspicion
        """
        self.resources = resource_manager
        self.suspicion = suspicion_manager

        # FBI status
        self.status = FBIStatus.NONE
        self.trigger_reason: Optional[FBITrigger] = None

        # Investigation countdown (in game seconds)
        self.investigation_countdown = 0.0
        self.investigation_duration = 14 * 24 * 3600  # 14 game days
        self.raid_warning_time = 24 * 3600  # 24 hours before raid

        # High suspicion tracking
        self.high_suspicion_duration = 0.0  # Time spent above 80 suspicion
        self.high_suspicion_threshold = 7 * 24 * 3600  # 7 days

        # Failed inspections tracking
        self.failed_inspections = 0
        self.critical_inspections = 0

        # FBI agents in city
        self.fbi_agents_active = False
        self.agent_count = 0

        # Avoidance options
        self.can_bribe = True
        self.bribe_cost = 50000
        self.bribe_risk = 0.3  # 30% chance of making things worse

        # Laying low
        self.laying_low = False
        self.lay_low_duration = 0.0
        self.lay_low_required = 7 * 24 * 3600  # 7 days

        # Event history
        self.events: List[Dict] = []

    def update(self, dt: float, game_time: float):
        """
        Update FBI manager.

        Args:
            dt: Delta time in seconds
            game_time: Current game time
        """
        # Track high suspicion duration
        if self.suspicion.suspicion_level > 80:
            self.high_suspicion_duration += dt
        else:
            self.high_suspicion_duration = 0.0

        # Check for FBI trigger
        if self.status == FBIStatus.NONE:
            self._check_triggers(game_time)

        # Update investigation countdown
        if self.status in [FBIStatus.TRIGGERED, FBIStatus.INVESTIGATING]:
            self.investigation_countdown -= dt

            # Check if raid should occur
            if self.investigation_countdown <= 0:
                self._trigger_raid(game_time)

            # Update status based on countdown
            elif self.investigation_countdown <= self.raid_warning_time:
                if self.status != FBIStatus.RAID_IMMINENT:
                    self.status = FBIStatus.RAID_IMMINENT
                    self._log_event("raid_imminent", "FBI raid imminent!", game_time)
                    print("\n🚨 FBI RAID IMMINENT!")
                    print(f"  Raid will occur in {self.investigation_countdown / 3600:.1f} hours")
                    print("  Reduce suspicion below 60 NOW or face consequences!")
                    print()

        # Update lay low timer
        if self.laying_low:
            self.lay_low_duration += dt
            if self.lay_low_duration >= self.lay_low_required:
                self._complete_lay_low(game_time)

    def _check_triggers(self, game_time: float):
        """Check if FBI investigation should be triggered."""
        # Trigger 1: High suspicion for extended period
        if self.high_suspicion_duration >= self.high_suspicion_threshold:
            self._trigger_investigation(FBITrigger.HIGH_SUSPICION, game_time)
            return

        # Trigger 2: Critical inspection failure
        if self.critical_inspections > 0:
            self._trigger_investigation(FBITrigger.CRITICAL_INSPECTION, game_time)
            return

        # Trigger 3: Multiple failed inspections
        if self.failed_inspections >= 3:
            self._trigger_investigation(FBITrigger.MULTIPLE_FAILURES, game_time)
            return

    def _trigger_investigation(self, trigger: FBITrigger, game_time: float):
        """
        Trigger FBI investigation.

        Args:
            trigger: Reason for triggering
            game_time: Current game time
        """
        if self.status != FBIStatus.NONE:
            return

        self.status = FBIStatus.TRIGGERED
        self.trigger_reason = trigger
        self.investigation_countdown = self.investigation_duration
        self.fbi_agents_active = True
        self.agent_count = 5

        self._log_event("investigation_triggered", f"FBI investigation triggered: {trigger.value}", game_time)

        print("\n🚨 FBI INVESTIGATION TRIGGERED!")
        print(f"  Reason: {self._get_trigger_description(trigger)}")
        print(f"  Investigation duration: {self.investigation_countdown / (24 * 3600):.0f} days")
        print("  FBI agents are now in the city")
        print("  Camera hacking is disabled during investigation")
        print()
        print("  TO AVOID RAID:")
        print("    - Reduce suspicion below 60")
        print("    - Pass all inspections")
        print(f"    - OR bribe officials (${self.bribe_cost:,}) - RISKY!")
        print(f"    - OR lay low for 7 days (no operations)")
        print()

    def _get_trigger_description(self, trigger: FBITrigger) -> str:
        """Get human-readable trigger description."""
        descriptions = {
            FBITrigger.HIGH_SUSPICION: "Suspicion level too high for too long",
            FBITrigger.CRITICAL_INSPECTION: "Critical inspection failure",
            FBITrigger.EXCESSIVE_HACKING: "Excessive camera hacking detected",
            FBITrigger.MULTIPLE_FAILURES: "Multiple failed inspections",
            FBITrigger.ANONYMOUS_TIP: "Anonymous tip to authorities",
        }
        return descriptions.get(trigger, "Unknown")

    def attempt_bribe(self, game_time: float) -> bool:
        """
        Attempt to bribe officials to stop investigation.

        Args:
            game_time: Current game time

        Returns:
            bool: True if successful, False if failed
        """
        if not self.can_bribe:
            print("Cannot bribe - option not available")
            return False

        if self.resources.money < self.bribe_cost:
            print(f"Not enough money to bribe (need ${self.bribe_cost:,})")
            return False

        # Pay the bribe
        self.resources.modify_money(-self.bribe_cost)

        # Roll for success/failure
        import random
        success = random.random() > self.bribe_risk

        if success:
            # Bribe successful - investigation cancelled
            self.status = FBIStatus.NONE
            self.trigger_reason = None
            self.investigation_countdown = 0.0
            self.fbi_agents_active = False
            self.suspicion.add_suspicion(-20, "Successful bribe")

            self._log_event("bribe_success", "Bribe successful", game_time)

            print("\n💰 BRIBE SUCCESSFUL!")
            print(f"  Paid ${self.bribe_cost:,}")
            print("  FBI investigation cancelled")
            print("  Suspicion reduced by 20")
            print()

            self.can_bribe = False  # Can only bribe once
            return True
        else:
            # Bribe failed - makes things worse
            self.suspicion.add_suspicion(20, "Failed bribe attempt")
            self.investigation_countdown *= 0.5  # Investigation accelerated

            self._log_event("bribe_failed", "Bribe failed - investigation intensified", game_time)

            print("\n💀 BRIBE FAILED!")
            print(f"  Lost ${self.bribe_cost:,}")
            print("  Suspicion increased by 20")
            print("  Investigation accelerated!")
            print()

            self.can_bribe = False
            return False

    def start_lay_low(self, game_time: float) -> bool:
        """
        Start laying low (cease operations).

        Args:
            game_time: Current game time

        Returns:
            bool: True if started successfully
        """
        if self.laying_low:
            print("Already laying low")
            return False

        if self.status not in [FBIStatus.TRIGGERED, FBIStatus.INVESTIGATING]:
            print("No FBI investigation to avoid")
            return False

        self.laying_low = True
        self.lay_low_duration = 0.0

        self._log_event("lay_low_started", "Laying low to avoid FBI", game_time)

        print("\n🔇 LAYING LOW")
        print("  All operations suspended for 7 days")
        print("  No material collection allowed")
        print("  No building construction allowed")
        print("  If successful, FBI investigation will be cancelled")
        print()

        return True

    def _complete_lay_low(self, game_time: float):
        """Complete laying low period."""
        self.laying_low = False
        self.lay_low_duration = 0.0

        # Check if successful (suspicion must be below 60)
        if self.suspicion.suspicion_level < 60:
            # Success - investigation cancelled
            self.status = FBIStatus.NONE
            self.trigger_reason = None
            self.investigation_countdown = 0.0
            self.fbi_agents_active = False

            self._log_event("lay_low_success", "Laying low successful", game_time)

            print("\n✓ LAYING LOW SUCCESSFUL!")
            print("  FBI investigation cancelled")
            print("  Normal operations can resume")
            print()
        else:
            # Failed - suspicion still too high
            self._log_event("lay_low_failed", "Laying low failed - suspicion still high", game_time)

            print("\n❌ LAYING LOW FAILED!")
            print(f"  Suspicion still at {self.suspicion.suspicion_level:.0f}")
            print("  Investigation continues")
            print()

    def _trigger_raid(self, game_time: float):
        """Trigger FBI raid (game over)."""
        self.status = FBIStatus.RAIDED
        self.fbi_agents_active = True
        self.agent_count = 20

        self._log_event("raid", "FBI raid executed", game_time)

        print("\n" + "=" * 80)
        print("💀 FBI RAID 💀".center(80))
        print("=" * 80)
        print()
        print("Federal agents have raided your factory!")
        print()
        print("CONSEQUENCES:")
        print("  - Factory operations shut down")
        print("  - All robots seized")
        print("  - Assets frozen")
        print("  - Illegal materials discovered")
        print()
        print("GAME OVER")
        print()
        print("=" * 80)
        print()

    def report_inspection_failure(self, is_critical: bool):
        """
        Report an inspection failure to FBI manager.

        Args:
            is_critical: Whether it was a critical failure
        """
        if is_critical:
            self.critical_inspections += 1
        else:
            self.failed_inspections += 1

    def report_camera_hacks(self, total_hacks: int, game_time: float):
        """
        Report camera hacking count.

        Args:
            total_hacks: Total number of camera hacks
            game_time: Current game time
        """
        if total_hacks >= 20 and self.status == FBIStatus.NONE:
            self._trigger_investigation(FBITrigger.EXCESSIVE_HACKING, game_time)

    def is_investigation_active(self) -> bool:
        """Check if FBI investigation is active."""
        return self.status in [FBIStatus.TRIGGERED, FBIStatus.INVESTIGATING, FBIStatus.RAID_IMMINENT]

    def is_raided(self) -> bool:
        """Check if factory has been raided."""
        return self.status == FBIStatus.RAIDED

    def get_countdown_days(self) -> float:
        """Get investigation countdown in game days."""
        return self.investigation_countdown / (24 * 3600)

    def get_status_text(self) -> str:
        """Get status text for UI."""
        if self.status == FBIStatus.NONE:
            return "No Investigation"
        elif self.status == FBIStatus.TRIGGERED:
            return f"FBI Investigating ({self.get_countdown_days():.1f} days)"
        elif self.status == FBIStatus.INVESTIGATING:
            return f"Active Investigation ({self.get_countdown_days():.1f} days)"
        elif self.status == FBIStatus.RAID_IMMINENT:
            hours = self.investigation_countdown / 3600
            return f"RAID IMMINENT ({hours:.1f} hours)"
        elif self.status == FBIStatus.RAIDED:
            return "RAIDED - GAME OVER"
        return "Unknown"

    def _log_event(self, event_type: str, description: str, game_time: float):
        """Log an FBI event."""
        event = {
            'type': event_type,
            'description': description,
            'game_time': game_time,
            'suspicion': self.suspicion.suspicion_level,
            'status': self.status.value,
        }
        self.events.append(event)

    def get_stats(self) -> Dict:
        """Get FBI manager statistics."""
        return {
            'status': self.status.value,
            'trigger_reason': self.trigger_reason.value if self.trigger_reason else None,
            'countdown_days': self.get_countdown_days(),
            'high_suspicion_days': self.high_suspicion_duration / (24 * 3600),
            'failed_inspections': self.failed_inspections,
            'critical_inspections': self.critical_inspections,
            'fbi_agents_active': self.fbi_agents_active,
            'agent_count': self.agent_count,
            'laying_low': self.laying_low,
            'can_bribe': self.can_bribe,
        }
