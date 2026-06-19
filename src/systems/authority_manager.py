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

from src.core.logger import get_logger
from src.core.game_config import AUTHORITY, TIME

logger = get_logger(__name__)


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
    # Positive endings (victory)
    LEGITIMATE_SUCCESS = 1   # Clean business, low suspicion, profitable
    PERFECT_CLEANUP = 2      # Environmental Hero - perfect run
    EFFICIENT_OPERATOR = 3   # Completed efficiently with minor issues
    ECO_WARRIOR = 4          # Environmental focus, renewable energy
    CRIMINAL_MASTERMIND = 5  # High illegal profit, evaded all authorities
    SPEED_DEMON = 6          # Fast completion with high risk
    SLOW_AND_STEADY = 7      # Safe approach, took time
    MORALLY_FLEXIBLE = 8     # Maximized profits through "creative" methods
    URBAN_RECYCLER = 9       # Aggressive city material collection
    # Negative endings (failure)
    FBI_RAID = 10            # Caught by FBI raid
    BANKRUPTCY = 11          # Ran out of money
    ESCAPE = 12              # Player fled before capture
    PLEA_DEAL = 13           # Negotiated with authorities
    INSPECTOR_FAILURE = 14   # Failed critical inspection


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
        self.state_threshold = AUTHORITY.STATE_THRESHOLD
        self.federal_threshold = AUTHORITY.FEDERAL_THRESHOLD

        # FBI Investigation
        self.fbi_investigation_active = False
        self.investigation_type = InvestigationType.NONE
        self.investigation_progress = 0.0  # 0-100%
        self.investigation_speed = 0.5     # Progress per game hour
        self.investigation_start_time = 0.0

        # FBI Raid
        self.raid_scheduled = False
        self.raid_countdown = 0.0  # Time until raid (game seconds)
        self.raid_min_warning = AUTHORITY.RAID_WARNING_MIN
        self.raid_max_warning = AUTHORITY.RAID_WARNING_MAX

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
        logger.warning(f"Authority escalation: {old_tier.name} -> {new_tier.name}")

        if new_tier == AuthorityTier.STATE:
            logger.warning("State police monitoring - increased investigation capabilities")

        elif new_tier == AuthorityTier.FEDERAL:
            logger.error("FBI has taken over! Federal resources deployed, risk of federal charges")
            # Automatically start FBI investigation
            self._start_fbi_investigation()

    def _on_tier_deescalation(self, old_tier: AuthorityTier, new_tier: AuthorityTier):
        """Handle tier de-escalation (suspicion decreased)."""
        logger.info(f"Authority de-escalation: {old_tier.name} -> {new_tier.name} - reduced law enforcement attention")

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

        logger.warning(f"FBI investigation initiated! Type: {self.investigation_type.name} - building case")

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
        logger.error("FBI investigation complete! Federal warrant issued, raid imminent")

        # Schedule raid with warning
        warning_time = random.uniform(self.raid_min_warning, self.raid_max_warning)
        self.raid_countdown = warning_time
        self.raid_scheduled = True

        # Calculate hours
        hours = warning_time / 3600.0
        logger.error(f"FBI tactical team arrives in {hours:.1f} game hours - limited time to act")

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

        logger.error("FBI RAID - GAME OVER! Federal agents stormed factory, under federal arrest")

        self._trigger_ending(GameEnding.FBI_RAID, "FBI raid - Federal arrest")

    def _check_ending_conditions(self, game_time: float):
        """Check for various game ending conditions."""
        if self.game_ending != GameEnding.NONE:
            return  # Already ended

        # Check bankruptcy
        if self.resources.money < AUTHORITY.BANKRUPTCY_THRESHOLD:
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

    def check_victory_conditions(self, scoring_manager, game_time: float) -> bool:
        """
        Check if player has achieved a victory condition.

        This should be called when the landfill is cleared or other
        victory triggers occur.

        Args:
            scoring_manager: ScoringManager instance with game stats
            game_time: Current game time in seconds

        Returns:
            bool: True if a victory ending was triggered
        """
        if self.game_ending != GameEnding.NONE:
            return False  # Already ended

        stats = scoring_manager.stats

        # Check if landfill is cleared (primary victory condition)
        if stats['landfill_cleared_percent'] < 100.0:
            return False  # Not complete yet

        # Determine which victory ending to award based on playstyle
        ending = self._evaluate_victory_ending(stats, game_time)

        if ending != GameEnding.NONE:
            self._trigger_victory_ending(ending, stats, game_time)
            return True

        return False

    def _evaluate_victory_ending(self, stats: dict, game_time: float) -> GameEnding:
        """
        Evaluate which victory ending the player has earned.

        Endings are checked in order of priority (best to worst).

        Args:
            stats: Player statistics from scoring_manager
            game_time: Current game time

        Returns:
            GameEnding: The appropriate ending type
        """
        suspicion_level = self.suspicion.suspicion_level
        max_suspicion = stats['max_suspicion']
        illegal_processed = stats['illegal_materials_processed']
        city_materials = stats['city_materials_collected']
        game_days = game_time / TIME.SECONDS_PER_DAY
        violations = stats['violations_count']
        fines = stats['fines_paid']
        renewable_ratio = (stats['renewable_energy_used'] / max(1, stats['total_energy_used']))
        litter_cleaned = stats['litter_cleaned']
        high_risk_ops = stats['high_risk_operations']
        money = self.resources.money

        # PERFECT_CLEANUP - Environmental Hero (hardest to achieve)
        # No violations, no fines, low suspicion, 100% landfill cleared
        if (violations == 0 and fines == 0 and
            max_suspicion == 0 and suspicion_level == 0 and
            not self.fbi_investigation_active):
            return GameEnding.PERFECT_CLEANUP

        # CRIMINAL_MASTERMIND - High illegal profits, evaded all authorities
        # High illegal materials, no FBI raid, high profit
        if (illegal_processed >= 10000 and
            not self.fbi_investigation_active and
            money >= 500000):
            return GameEnding.CRIMINAL_MASTERMIND

        # ECO_WARRIOR - Environmental focus
        # High renewable energy usage, lots of litter cleaned, low pollution
        if (renewable_ratio >= 0.8 and
            litter_cleaned >= 5000 and
            stats['air_pollution_total'] < 1000):
            return GameEnding.ECO_WARRIOR

        # SPEED_DEMON - Fast completion with high risk
        # Completed in under 15 game days
        if game_days <= 15 and high_risk_ops >= 10:
            return GameEnding.SPEED_DEMON

        # MORALLY_FLEXIBLE - Maximized profits through creative methods
        # High illegal materials but passed all inspections
        if (illegal_processed >= 1000 and illegal_processed < 10000 and
            stats['inspections_failed'] == 0 and
            money >= 200000):
            return GameEnding.MORALLY_FLEXIBLE

        # URBAN_RECYCLER - Aggressive city material collection
        # 30-70% of materials from city
        total_materials = stats['materials_collected']
        city_ratio = city_materials / max(1, total_materials)
        if 0.3 <= city_ratio <= 0.7 and money > 0:
            return GameEnding.URBAN_RECYCLER

        # SLOW_AND_STEADY - Safe approach, took time
        # Suspicion never above 20, minimal risk
        if (stats['suspicion_never_above_20'] and
            high_risk_ops < 5 and
            game_days >= 60):
            return GameEnding.SLOW_AND_STEADY

        # EFFICIENT_OPERATOR - Good efficiency with minor issues
        # Good completion, some violations but recovered
        if (violations <= 3 and
            stats['inspections_passed'] > stats['inspections_failed'] and
            money > 50000):
            return GameEnding.EFFICIENT_OPERATOR

        # LEGITIMATE_SUCCESS - Default positive ending
        # Clean business, low suspicion, profitable
        if (suspicion_level < 50 and
            money > 0 and
            not self.fbi_investigation_active):
            return GameEnding.LEGITIMATE_SUCCESS

        # If somehow none of the above matched but landfill is complete
        return GameEnding.LEGITIMATE_SUCCESS

    def _trigger_victory_ending(self, ending: GameEnding, stats: dict, game_time: float):
        """
        Trigger a victory ending with appropriate messaging.

        Args:
            ending: The victory ending type
            stats: Player statistics
            game_time: Current game time
        """
        ending_info = {
            GameEnding.PERFECT_CLEANUP: {
                'title': '🌟 ENVIRONMENTAL HERO 🌟',
                'description': 'Perfect cleanup with no incidents!',
                'details': 'You completed the landfill cleanup perfectly. '
                          'No violations, no fines, no suspicion. '
                          'The city praises your efficiency and ethics.',
            },
            GameEnding.CRIMINAL_MASTERMIND: {
                'title': '🎭 CRIMINAL MASTERMIND 🎭',
                'description': 'Maximum profit, zero consequences!',
                'details': 'You processed massive amounts of illegal materials '
                          'while evading all authorities. '
                          'The FBI never caught on. Impressive... and concerning.',
            },
            GameEnding.ECO_WARRIOR: {
                'title': '🌱 ECO WARRIOR 🌱',
                'description': 'Champion of the environment!',
                'details': 'You cleaned the landfill using renewable energy '
                          'and even cleaned up city litter. '
                          'The environment thanks you.',
            },
            GameEnding.SPEED_DEMON: {
                'title': '⚡ SPEED DEMON ⚡',
                'description': 'Blazing fast completion!',
                'details': 'You completed the cleanup in record time. '
                          'High risk, high reward gameplay. '
                          'The city is impressed by your efficiency.',
            },
            GameEnding.MORALLY_FLEXIBLE: {
                'title': '💼 MORALLY FLEXIBLE ENTREPRENEUR 💼',
                'description': 'Creative interpretation of regulations!',
                'details': 'You maximized profits through creative methods '
                          'while somehow passing every inspection. '
                          'Clever business practices indeed.',
            },
            GameEnding.URBAN_RECYCLER: {
                'title': '🏙️ URBAN MINING SPECIALIST 🏙️',
                'description': 'Aggressive but effective!',
                'details': 'You aggressively recycled city infrastructure '
                          'while managing the heat from authorities. '
                          'A bold strategy that paid off.',
            },
            GameEnding.SLOW_AND_STEADY: {
                'title': '🐢 SLOW AND STEADY 🐢',
                'description': 'Safe approach wins the race!',
                'details': 'You took your time and played it safe. '
                          'The landfill is clean, and you avoided all trouble. '
                          'Patience is a virtue.',
            },
            GameEnding.EFFICIENT_OPERATOR: {
                'title': '⚙️ EFFICIENT OPERATOR ⚙️',
                'description': 'Job well done!',
                'details': 'You cleaned the landfill efficiently with minimal issues. '
                          'Some bumps along the way, but you recovered well. '
                          'A solid performance.',
            },
            GameEnding.LEGITIMATE_SUCCESS: {
                'title': '🏆 LEGITIMATE SUCCESS 🏆',
                'description': 'Clean business victory!',
                'details': 'You completed the cleanup through legitimate means. '
                          'Low suspicion, positive profit, no FBI involvement. '
                          'A respectable achievement.',
            },
        }

        info = ending_info.get(ending, {
            'title': '🏆 VICTORY 🏆',
            'description': 'Landfill cleanup complete!',
            'details': 'You have successfully completed the landfill cleanup.',
        })

        game_days = game_time / TIME.SECONDS_PER_DAY

        logger.info(f"GAME COMPLETE - {info['title']}: {game_days:.1f} days, ${self.resources.money:,.0f}")

        self._trigger_ending(ending, info['description'])

    def trigger_landfill_complete(self, scoring_manager, game_time: float):
        """
        Called when the landfill is 100% cleared.

        This is the primary trigger for positive victory endings.

        Args:
            scoring_manager: ScoringManager instance
            game_time: Current game time
        """
        scoring_manager.update_landfill_progress(100.0)
        self.check_victory_conditions(scoring_manager, game_time)

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
            logger.warning(f"Cannot bribe yet. Wait {hours_remaining:.1f} game hours.")
            return False

        if self.resources.money < amount:
            logger.warning(f"Insufficient funds for bribe (need ${amount:,})")
            return False

        self.bribes_attempted += 1

        # Bribe success probability based on authority tier
        if self.current_tier == AuthorityTier.LOCAL:
            success_rate = AUTHORITY.LOCAL_BRIBE_SUCCESS_RATE
        elif self.current_tier == AuthorityTier.STATE:
            success_rate = AUTHORITY.STATE_BRIBE_SUCCESS_RATE
        else:  # FEDERAL
            success_rate = AUTHORITY.FEDERAL_BRIBE_SUCCESS_RATE

        # Attempt bribe
        if random.random() < success_rate:
            # Success!
            self.bribes_successful += 1
            self.resources.modify_money(-amount)

            # Reduce investigation progress
            if self.fbi_investigation_active:
                reduction = random.uniform(15, 30)  # 15-30% reduction
                self.investigation_progress = max(0, self.investigation_progress - reduction)
                logger.info(f"Bribe successful! Paid ${amount:,}, investigation progress reduced by {reduction:.1f}%")
            else:
                # Reduce suspicion
                suspicion_reduction = random.randint(10, 20)
                self.suspicion.add_suspicion(-suspicion_reduction, "Successful bribe")
                logger.info(f"Bribe successful! Paid ${amount:,}, suspicion reduced by {suspicion_reduction}")

            # Set cooldown
            self.bribe_cooldown = random.uniform(
                AUTHORITY.BRIBE_COOLDOWN_MIN, AUTHORITY.BRIBE_COOLDOWN_MAX
            )

            return True
        else:
            # Failed! Increases suspicion and costs money anyway
            self.resources.modify_money(-amount)
            suspicion_increase = 20 + (10 if self.current_tier == AuthorityTier.FEDERAL else 0)
            self.suspicion.add_suspicion(suspicion_increase, "Failed bribe attempt")

            logger.error(f"Bribe failed! Lost ${amount:,}, official reported, suspicion +{suspicion_increase}")

            # Double cooldown on failure
            self.bribe_cooldown = random.uniform(
                AUTHORITY.BRIBE_COOLDOWN_FAILURE_MIN, AUTHORITY.BRIBE_COOLDOWN_FAILURE_MAX
            )

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
            logger.debug("False evidence already planted")
            return False

        if not self.fbi_investigation_active:
            logger.debug("No active investigation to misdirect")
            return False

        if self.resources.money < cost:
            logger.warning(f"Insufficient funds for false evidence (need ${cost:,})")
            return False

        if random.random() < AUTHORITY.FALSE_EVIDENCE_SUCCESS_RATE:
            self.resources.modify_money(-cost)
            self.evidence_planted = True

            # Set disruption factor
            self.disruption_factor = 0.5  # Halves investigation speed

            logger.info(f"False evidence planted! Cost ${cost:,}, investigation speed -50%")

            return True
        else:
            # Failed - costs money and increases suspicion
            self.resources.modify_money(-cost)
            self.suspicion.add_suspicion(25, "Caught planting false evidence")

            logger.error(f"False evidence plot discovered! Lost ${cost:,}, suspicion +25, FBI accelerated")

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
            logger.debug("No immediate threat - no need to flee yet")
            return False

        # Success rate based on investigation progress
        # Lower progress = easier escape
        success_rate = 1.0 - (self.investigation_progress / 100.0)

        if random.random() < success_rate:
            logger.info(f"Escape successful! Fled country, assets liquidated: ${int(self.resources.money * 0.3):,} - GAME OVER")

            self._trigger_ending(GameEnding.ESCAPE, "Fled the country to avoid arrest")
            return True
        else:
            logger.error("Escape failed! Caught at border, immediate FBI raid")

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
            logger.debug("No investigation to negotiate with")
            return False

        # Can only negotiate if investigation is 30-80% complete
        if self.investigation_progress < 30:
            logger.warning("Investigation not far enough - authorities not interested in deal")
            return False

        if self.investigation_progress > 80:
            logger.warning("Investigation too far along - authorities want full prosecution")
            return False

        # Plea deal cost: forfeit significant money and assets
        deal_cost = max(int(self.resources.money * 0.7), 30000)

        logger.info(f"Plea deal offered: Forfeit ${deal_cost:,} (70% assets), avoid prison, continue operating")

        # For now, auto-accept
        # In full implementation, would wait for player input
        accept = True

        if accept:
            self.resources.modify_money(-deal_cost)

            logger.info(f"Plea deal accepted! Paid ${deal_cost:,}, charges reduced - GAME OVER")

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

        logger.info(f"GAME ENDED: {ending.name} - {reason}")

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
