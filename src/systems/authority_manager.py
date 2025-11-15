"""
AuthorityManager - manages law enforcement escalation and FBI investigations.

Handles:
- Authority tier progression (Local → State → Federal)
- FBI investigation mechanics
- FBI raid triggers and execution
- Social engineering countermeasures
- Multiple game ending conditions
"""

import random
from enum import Enum
from typing import Optional, Dict, List


class AuthorityTier(Enum):
    """Law enforcement authority levels."""
    LOCAL = 0      # Local police (0-50 suspicion)
    STATE = 1      # State police (50-100 suspicion)
    FEDERAL = 2    # FBI (100+ suspicion)


class InvestigationType(Enum):
    """Types of FBI investigations."""
    NONE = 0
    SURVEILLANCE = 1        # Basic monitoring
    UNDERCOVER = 2          # Agent infiltration
    WIRETAP = 3            # Communications monitoring
    FINANCIAL_AUDIT = 4    # Financial records investigation
    RAID_PREPARATION = 5   # Preparing for raid


class GameEnding(Enum):
    """Possible game ending scenarios."""
    NONE = 0
    LEGITIMATE_SUCCESS = 1  # Clean business, low suspicion, profitable
    FBI_RAID = 2           # Caught by FBI raid
    BANKRUPTCY = 3         # Ran out of money
    ESCAPE = 4             # Player fled before capture
    PLEA_DEAL = 5          # Negotiated with authorities
    INSPECTOR_FAILURE = 6  # Failed critical inspection (already handled)


class AuthorityManager:
    """
    Manages law enforcement escalation and FBI investigations.

    Authority tiers escalate based on suspicion level.
    FBI investigations trigger at high suspicion or repeated failures.
    """

    def __init__(self, suspicion_manager, resource_manager, inspection_manager):
        """
        Initialize authority manager.

        Args:
            suspicion_manager: SuspicionManager instance
            resource_manager: ResourceManager instance
            inspection_manager: InspectionManager instance
        """
        self.suspicion = suspicion_manager
        self.resources = resource_manager
        self.inspection = inspection_manager

        # Current authority tier
        self.current_tier = AuthorityTier.LOCAL
        self.tier_changed = False  # Flag for tier change events

        # Tier thresholds
        self.state_threshold = 50
        self.federal_threshold = 100

        # FBI Investigation
        self.fbi_investigation_active = False
        self.investigation_type = InvestigationType.NONE
        self.investigation_progress = 0.0  # 0-100%
        self.investigation_speed = 0.5     # Progress per game hour
        self.investigation_start_time = 0.0

        # FBI Raid
        self.raid_scheduled = False
        self.raid_countdown = 0.0  # Time until raid (game seconds)
        self.raid_min_warning = 7200.0   # 2 hours minimum warning
        self.raid_max_warning = 14400.0  # 4 hours maximum warning

        # Social Engineering
        self.bribe_cooldown = 0.0  # Time until next bribe possible
        self.evidence_planted = False
        self.witness_intimidation_level = 0  # 0-100, reduces testimony effectiveness

        # Investigation disruption
        self.disruption_factor = 0.0  # 0-1, reduces investigation speed

        # Ending tracking
        self.game_ending = GameEnding.NONE
        self.ending_reason = ""

        # Statistics
        self.tier_escalations = 0
        self.bribes_attempted = 0
        self.bribes_successful = 0

    def update(self, dt: float, game_time: float):
        """
        Update authority system.

        Args:
            dt (float): Delta time in seconds
            game_time (float): Current game time
        """
        # Update authority tier based on suspicion
        self._update_authority_tier()

        # Update FBI investigation if active
        if self.fbi_investigation_active:
            self._update_fbi_investigation(dt, game_time)

        # Update raid countdown if scheduled
        if self.raid_scheduled:
            self._update_raid_countdown(dt, game_time)

        # Update cooldowns
        if self.bribe_cooldown > 0:
            self.bribe_cooldown -= dt

        # Check for game ending conditions
        self._check_ending_conditions(game_time)

    def _update_authority_tier(self):
        """Update authority tier based on suspicion level."""
        suspicion_level = self.suspicion.suspicion_level
        old_tier = self.current_tier

        # Determine appropriate tier
        if suspicion_level >= self.federal_threshold:
            new_tier = AuthorityTier.FEDERAL
        elif suspicion_level >= self.state_threshold:
            new_tier = AuthorityTier.STATE
        else:
            new_tier = AuthorityTier.LOCAL

        # Check for tier escalation
        if new_tier.value > old_tier.value:
            self.current_tier = new_tier
            self.tier_changed = True
            self.tier_escalations += 1
            self._on_tier_escalation(old_tier, new_tier)
        elif new_tier.value < old_tier.value:
            # De-escalation (rare)
            self.current_tier = new_tier
            self.tier_changed = True
            self._on_tier_deescalation(old_tier, new_tier)
        else:
            self.tier_changed = False

    def _on_tier_escalation(self, old_tier: AuthorityTier, new_tier: AuthorityTier):
        """
        Handle tier escalation event.

        Args:
            old_tier (AuthorityTier): Previous tier
            new_tier (AuthorityTier): New tier
        """
        print(f"\n⚠️ AUTHORITY ESCALATION!")
        print(f"  {old_tier.name} → {new_tier.name}")

        if new_tier == AuthorityTier.STATE:
            print(f"  State police are now monitoring your operations")
            print(f"  Increased investigation capabilities")
            print(f"  More frequent patrols")

        elif new_tier == AuthorityTier.FEDERAL:
            print(f"  🚨 FBI HAS TAKEN OVER THE INVESTIGATION!")
            print(f"  Federal resources deployed")
            print(f"  Advanced surveillance and forensics")
            print(f"  Risk of federal charges")
            # Automatically start FBI investigation
            self._start_fbi_investigation()

    def _on_tier_deescalation(self, old_tier: AuthorityTier, new_tier: AuthorityTier):
        """Handle tier de-escalation (suspicion decreased)."""
        print(f"\n✓ AUTHORITY DE-ESCALATION")
        print(f"  {old_tier.name} → {new_tier.name}")
        print(f"  Reduced law enforcement attention")

    def _start_fbi_investigation(self):
        """Start FBI investigation."""
        if self.fbi_investigation_active:
            return  # Already investigating

        self.fbi_investigation_active = True
        self.investigation_progress = 0.0

        # Determine investigation type based on circumstances
        investigation_types = [
            InvestigationType.SURVEILLANCE,
            InvestigationType.FINANCIAL_AUDIT,
            InvestigationType.WIRETAP,
        ]

        # If multiple inspection failures, escalate to undercover
        if hasattr(self.inspection, 'last_result') and self.inspection.last_result:
            investigation_types.append(InvestigationType.UNDERCOVER)

        self.investigation_type = random.choice(investigation_types)

        print(f"\n🔍 FBI INVESTIGATION INITIATED!")
        print(f"  Investigation Type: {self.investigation_type.name}")
        print(f"  The FBI is building a case against you")
        print(f"  Evidence collection in progress...")

    def _update_fbi_investigation(self, dt: float, game_time: float):
        """Update FBI investigation progress."""
        if not self.fbi_investigation_active:
            return

        # Calculate effective investigation speed (affected by disruption)
        effective_speed = self.investigation_speed * (1.0 - self.disruption_factor)

        # Progress investigation (in % per hour)
        # dt is in seconds, convert to hours
        progress_increase = effective_speed * (dt / 3600.0)
        self.investigation_progress += progress_increase

        # Clamp to 100%
        if self.investigation_progress >= 100.0:
            self.investigation_progress = 100.0
            self._complete_fbi_investigation(game_time)

    def _complete_fbi_investigation(self, game_time: float):
        """Complete FBI investigation and schedule raid."""
        print(f"\n🚨 FBI INVESTIGATION COMPLETE!")
        print(f"  Sufficient evidence has been gathered")
        print(f"  Federal warrant issued for raid")
        print(f"  FBI raid imminent...")

        # Schedule raid with warning
        warning_time = random.uniform(self.raid_min_warning, self.raid_max_warning)
        self.raid_countdown = warning_time
        self.raid_scheduled = True

        # Calculate hours
        hours = warning_time / 3600.0
        print(f"  FBI tactical team arrives in {hours:.1f} game hours")
        print(f"\n  You have limited time to:")
        print(f"    - Destroy evidence")
        print(f"    - Flee the country")
        print(f"    - Negotiate a plea deal")

    def _update_raid_countdown(self, dt: float, game_time: float):
        """Update FBI raid countdown."""
        if not self.raid_scheduled:
            return

        self.raid_countdown -= dt

        if self.raid_countdown <= 0:
            self._execute_fbi_raid(game_time)

    def _execute_fbi_raid(self, game_time: float):
        """Execute FBI raid (game over)."""
        # Clear raid scheduled flag to prevent multiple executions
        self.raid_scheduled = False

        print(f"\n💥💥💥 FBI RAID IN PROGRESS! 💥💥💥")
        print(f"  Federal agents have stormed your factory!")
        print(f"  All illegal operations have been shut down")
        print(f"  Evidence has been seized")
        print(f"  You are under federal arrest")
        print(f"\n  Charges:")
        print(f"    - Operating illegal waste processing facility")
        print(f"    - Environmental violations")
        print(f"    - Fraud and money laundering")
        print(f"    - Obstruction of justice")
        print(f"\n  GAME OVER")

        self._trigger_ending(GameEnding.FBI_RAID, "FBI raid - Federal arrest")

    def _check_ending_conditions(self, game_time: float):
        """Check for various game ending conditions."""
        if self.game_ending != GameEnding.NONE:
            return  # Already ended

        # Check bankruptcy
        if self.resources.money < -50000:
            self._trigger_ending(
                GameEnding.BANKRUPTCY,
                "Bankruptcy - Cannot recover from debt"
            )

        # Inspection critical failure is handled by InspectionManager
        # We can check it here too
        if self.inspection.is_game_over():
            self._trigger_ending(
                GameEnding.INSPECTOR_FAILURE,
                self.inspection.game_over_reason
            )

    def attempt_bribe(self, amount: int = 10000) -> bool:
        """
        Attempt to bribe officials to slow investigation.

        Args:
            amount (int): Bribe amount (default $10,000)

        Returns:
            bool: True if bribe successful
        """
        if self.bribe_cooldown > 0:
            hours_remaining = self.bribe_cooldown / 3600.0
            print(f"Cannot bribe yet. Wait {hours_remaining:.1f} game hours.")
            return False

        if self.resources.money < amount:
            print(f"Insufficient funds for bribe (need ${amount:,})")
            return False

        self.bribes_attempted += 1

        # Bribe success probability based on authority tier
        if self.current_tier == AuthorityTier.LOCAL:
            success_rate = 0.7  # 70% success with local police
        elif self.current_tier == AuthorityTier.STATE:
            success_rate = 0.4  # 40% success with state police
        else:  # FEDERAL
            success_rate = 0.15  # 15% success with FBI (very risky)

        # Attempt bribe
        if random.random() < success_rate:
            # Success!
            self.bribes_successful += 1
            self.resources.modify_money(-amount)

            # Reduce investigation progress
            if self.fbi_investigation_active:
                reduction = random.uniform(15, 30)  # 15-30% reduction
                self.investigation_progress = max(0, self.investigation_progress - reduction)
                print(f"\n💰 BRIBE SUCCESSFUL")
                print(f"  Paid: ${amount:,}")
                print(f"  Investigation progress reduced by {reduction:.1f}%")
            else:
                # Reduce suspicion
                suspicion_reduction = random.randint(10, 20)
                self.suspicion.add_suspicion(-suspicion_reduction, "Successful bribe")
                print(f"\n💰 BRIBE SUCCESSFUL")
                print(f"  Paid: ${amount:,}")
                print(f"  Suspicion reduced by {suspicion_reduction}")

            # Set cooldown (24-48 hours)
            self.bribe_cooldown = random.uniform(86400.0, 172800.0)

            return True
        else:
            # Failed! Increases suspicion and costs money anyway
            self.resources.modify_money(-amount)
            suspicion_increase = 20 + (10 if self.current_tier == AuthorityTier.FEDERAL else 0)
            self.suspicion.add_suspicion(suspicion_increase, "Failed bribe attempt")

            print(f"\n⚠️ BRIBE FAILED!")
            print(f"  Lost: ${amount:,}")
            print(f"  Official reported the bribe attempt!")
            print(f"  Suspicion increased by {suspicion_increase}")

            # Double cooldown on failure
            self.bribe_cooldown = random.uniform(172800.0, 345600.0)  # 48-96 hours

            return False

    def plant_false_evidence(self, cost: int = 15000) -> bool:
        """
        Plant false evidence to misdirect investigation.

        Args:
            cost (int): Cost to plant evidence

        Returns:
            bool: True if successful
        """
        if self.evidence_planted:
            print("False evidence already planted")
            return False

        if not self.fbi_investigation_active:
            print("No active investigation to misdirect")
            return False

        if self.resources.money < cost:
            print(f"Insufficient funds (need ${cost:,})")
            return False

        # 60% success rate
        if random.random() < 0.6:
            self.resources.modify_money(-cost)
            self.evidence_planted = True

            # Set disruption factor
            self.disruption_factor = 0.5  # Halves investigation speed

            print(f"\n🎭 FALSE EVIDENCE PLANTED")
            print(f"  Cost: ${cost:,}")
            print(f"  Investigation misdirected")
            print(f"  Investigation speed reduced by 50%")

            return True
        else:
            # Failed - costs money and increases suspicion
            self.resources.modify_money(-cost)
            self.suspicion.add_suspicion(25, "Caught planting false evidence")

            print(f"\n⚠️ FALSE EVIDENCE PLOT DISCOVERED!")
            print(f"  Lost: ${cost:,}")
            print(f"  Suspicion increased by 25")
            print(f"  FBI investigation accelerated")

            # Increase investigation speed as punishment
            self.investigation_speed *= 1.5

            return False

    def attempt_escape(self) -> bool:
        """
        Attempt to flee the country before capture.

        Returns:
            bool: True if escape successful
        """
        # Can only escape if FBI is close
        if not self.fbi_investigation_active:
            print("No immediate threat - no need to flee yet")
            return False

        # Success rate based on investigation progress
        # Lower progress = easier escape
        success_rate = 1.0 - (self.investigation_progress / 100.0)

        if random.random() < success_rate:
            print(f"\n✈️ ESCAPE SUCCESSFUL!")
            print(f"  You have fled the country")
            print(f"  Assets liquidated: ${int(self.resources.money * 0.3):,}")
            print(f"  Living in exile abroad")
            print(f"\n  GAME OVER - Escaped justice")

            self._trigger_ending(GameEnding.ESCAPE, "Fled the country to avoid arrest")
            return True
        else:
            print(f"\n⚠️ ESCAPE FAILED!")
            print(f"  Caught at the border")
            print(f"  Immediate FBI raid")

            # Immediate raid
            self._execute_fbi_raid(0.0)
            return False

    def negotiate_plea_deal(self) -> bool:
        """
        Attempt to negotiate a plea deal with authorities.

        Returns:
            bool: True if deal accepted
        """
        if not self.fbi_investigation_active:
            print("No investigation to negotiate with")
            return False

        # Can only negotiate if investigation is 30-80% complete
        if self.investigation_progress < 30:
            print("Investigation not far enough - authorities not interested in deal")
            return False

        if self.investigation_progress > 80:
            print("Investigation too far along - authorities want full prosecution")
            return False

        # Plea deal cost: forfeit significant money and assets
        deal_cost = max(int(self.resources.money * 0.7), 30000)

        print(f"\n⚖️ PLEA DEAL OFFERED")
        print(f"  Forfeit: ${deal_cost:,} (70% of assets)")
        print(f"  Penalty: Temporary business restrictions")
        print(f"  Benefit: Avoid prison, continue operating")
        print(f"\n  Accept deal? (This is a game ending)")

        # For now, auto-accept
        # In full implementation, would wait for player input
        accept = True

        if accept:
            self.resources.modify_money(-deal_cost)

            print(f"\n✓ PLEA DEAL ACCEPTED")
            print(f"  Paid: ${deal_cost:,}")
            print(f"  Charges reduced to misdemeanors")
            print(f"  Business allowed to continue with oversight")
            print(f"\n  GAME OVER - Plea bargain")

            self._trigger_ending(GameEnding.PLEA_DEAL, "Negotiated plea deal with FBI")
            return True

        return False

    def _trigger_ending(self, ending: GameEnding, reason: str):
        """
        Trigger a game ending.

        Args:
            ending (GameEnding): Type of ending
            reason (str): Reason description
        """
        self.game_ending = ending
        self.ending_reason = reason

        print(f"\n{'='*60}")
        print(f"GAME ENDED: {ending.name}")
        print(f"Reason: {reason}")
        print(f"{'='*60}")

    def get_status_summary(self) -> Dict:
        """
        Get authority status summary for UI.

        Returns:
            dict: Status information
        """
        return {
            'current_tier': self.current_tier,
            'tier_name': self.current_tier.name,
            'tier_changed': self.tier_changed,
            'fbi_investigation_active': self.fbi_investigation_active,
            'investigation_type': self.investigation_type,
            'investigation_progress': self.investigation_progress,
            'raid_scheduled': self.raid_scheduled,
            'raid_countdown_hours': self.raid_countdown / 3600.0 if self.raid_scheduled else 0,
            'bribe_available': self.bribe_cooldown <= 0,
            'bribe_cooldown_hours': self.bribe_cooldown / 3600.0,
            'game_ending': self.game_ending,
            'ending_reason': self.ending_reason,
            'can_escape': self.fbi_investigation_active,
            'can_plea_deal': self.fbi_investigation_active and 30 <= self.investigation_progress <= 80,
        }

    def is_game_over(self) -> bool:
        """Check if game has ended."""
        return self.game_ending != GameEnding.NONE

    def get_game_ending(self) -> GameEnding:
        """Get current game ending type."""
        return self.game_ending

    def __repr__(self):
        """String representation for debugging."""
        fbi_str = f", FBI_INVESTIGATION={self.investigation_progress:.1f}%" if self.fbi_investigation_active else ""
        raid_str = ", RAID_SCHEDULED" if self.raid_scheduled else ""
        ending_str = f", ENDING={self.game_ending.name}" if self.game_ending != GameEnding.NONE else ""
        return (f"AuthorityManager(tier={self.current_tier.name}"
                f"{fbi_str}{raid_str}{ending_str})")
