"""
Suspicion Manager - tracks overall suspicion level and manages consequences.

Handles:
- Tracking suspicion level (0-100)
- Processing suspicion increases from various sources
- Suspicion decay over time
- Tier transitions (Normal → Rumors → Investigation → Inspection → Restrictions)
- Tier-based consequences
"""

from typing import List, Dict, Optional
import time


class SuspicionTier:
    """Suspicion tier enumeration."""
    NORMAL = 'normal'                    # 0-20: No effect
    RUMORS = 'rumors'                    # 21-40: Slight police increase
    INVESTIGATION = 'investigation'      # 41-60: Police attention
    INSPECTION = 'inspection'            # 61-80: Inspection scheduled
    RESTRICTIONS = 'restrictions'        # 81-100: Restrictions/FBI


class SuspicionManager:
    """
    Manages suspicion level and consequences.

    Tracks suspicion from various sources, handles decay, and manages
    tier transitions with their associated consequences.
    """

    def __init__(self):
        """Initialize the suspicion manager."""
        # Suspicion level (0-100)
        self.suspicion_level = 0.0

        # Current tier
        self.current_tier = SuspicionTier.NORMAL

        # Tier thresholds
        self.tier_thresholds = {
            SuspicionTier.NORMAL: 0,
            SuspicionTier.RUMORS: 21,
            SuspicionTier.INVESTIGATION: 41,
            SuspicionTier.INSPECTION: 61,
            SuspicionTier.RESTRICTIONS: 81,
        }

        # Suspicion decay rates (per game hour)
        self.base_decay_rate = 0.1  # Normal decay
        self.decay_stops_at = 60.0  # Decay stops above this level

        # Event history
        self.suspicion_events: List[Dict] = []
        self.tier_changes: List[Dict] = []

        # Tier names for display
        self.tier_names = {
            SuspicionTier.NORMAL: 'Normal',
            SuspicionTier.RUMORS: 'Rumors',
            SuspicionTier.INVESTIGATION: 'Investigation',
            SuspicionTier.INSPECTION: 'Inspection Scheduled',
            SuspicionTier.RESTRICTIONS: 'Restrictions',
        }

        # Tier colors for UI
        self.tier_colors = {
            SuspicionTier.NORMAL: (100, 200, 100),      # Green
            SuspicionTier.RUMORS: (200, 200, 100),      # Yellow
            SuspicionTier.INVESTIGATION: (255, 150, 50), # Orange
            SuspicionTier.INSPECTION: (255, 100, 50),    # Dark orange
            SuspicionTier.RESTRICTIONS: (255, 50, 50),   # Red
        }

        # Tier-specific effects
        self.tier_effects = {
            SuspicionTier.NORMAL: {
                'police_patrol_multiplier': 1.0,
                'npc_alertness_multiplier': 1.0,
                'camera_detection_bonus': 0.0,
                'description': 'No effect - operations normal',
            },
            SuspicionTier.RUMORS: {
                'police_patrol_multiplier': 1.25,
                'npc_alertness_multiplier': 1.1,
                'camera_detection_bonus': 0.05,
                'description': '+25% police patrols, NPCs slightly more alert',
            },
            SuspicionTier.INVESTIGATION: {
                'police_patrol_multiplier': 1.5,
                'npc_alertness_multiplier': 1.25,
                'camera_detection_bonus': 0.1,
                'undercover_agents': True,
                'description': '+50% police patrols, undercover agents in city',
            },
            SuspicionTier.INSPECTION: {
                'police_patrol_multiplier': 2.0,
                'npc_alertness_multiplier': 1.5,
                'camera_detection_bonus': 0.15,
                'checkpoints': True,
                'description': 'Heavy police presence, checkpoints near factory',
            },
            SuspicionTier.RESTRICTIONS: {
                'police_patrol_multiplier': 2.5,
                'npc_alertness_multiplier': 2.0,
                'camera_detection_bonus': 0.25,
                'operation_hours_limited': True,
                'weekly_inspections': True,
                'description': 'Factory operations limited, mandatory weekly inspections',
            },
        }

    def get_current_tier(self) -> str:
        """
        Get current suspicion tier based on level.

        Returns:
            str: Current tier
        """
        if self.suspicion_level >= self.tier_thresholds[SuspicionTier.RESTRICTIONS]:
            return SuspicionTier.RESTRICTIONS
        elif self.suspicion_level >= self.tier_thresholds[SuspicionTier.INSPECTION]:
            return SuspicionTier.INSPECTION
        elif self.suspicion_level >= self.tier_thresholds[SuspicionTier.INVESTIGATION]:
            return SuspicionTier.INVESTIGATION
        elif self.suspicion_level >= self.tier_thresholds[SuspicionTier.RUMORS]:
            return SuspicionTier.RUMORS
        else:
            return SuspicionTier.NORMAL

    def add_suspicion(self, amount: float, source: str, description: str = "") -> bool:
        """
        Add or subtract suspicion from a source.

        Args:
            amount (float): Amount of suspicion to add (positive) or subtract (negative)
            source (str): Source of suspicion (e.g., 'npc_report', 'police_report')
            description (str): Optional description of the event

        Returns:
            bool: True if tier changed
        """
        if amount == 0:
            return False

        old_level = self.suspicion_level
        old_tier = self.current_tier

        # Add or subtract suspicion (capped at 0-100)
        self.suspicion_level = max(0.0, min(100.0, self.suspicion_level + amount))

        # Record event
        event = {
            'timestamp': time.time(),
            'amount': amount,
            'source': source,
            'description': description,
            'level_before': old_level,
            'level_after': self.suspicion_level,
        }
        self.suspicion_events.append(event)

        # Check for tier change
        new_tier = self.get_current_tier()
        tier_changed = new_tier != old_tier

        if tier_changed:
            self.current_tier = new_tier
            tier_change = {
                'timestamp': time.time(),
                'old_tier': old_tier,
                'new_tier': new_tier,
                'suspicion_level': self.suspicion_level,
            }
            self.tier_changes.append(tier_change)
            print(f"⚠ Suspicion tier changed: {self.tier_names[old_tier]} → {self.tier_names[new_tier]} ({self.suspicion_level:.1f})")

        return tier_changed

    def update(self, dt: float, game_time_hours: float):
        """
        Update suspicion decay.

        Args:
            dt (float): Delta time in seconds
            game_time_hours (float): Current game time in hours (for decay calculation)
        """
        # Don't decay if above threshold
        if self.suspicion_level >= self.decay_stops_at:
            return

        # Calculate decay (per game hour, converted from dt)
        # Assuming 60x time scale: 1 real second = 1 game minute
        # So 60 real seconds = 1 game hour
        decay_per_second = self.base_decay_rate / 3600.0  # Convert per-hour to per-second
        decay_amount = decay_per_second * dt * 60.0  # Adjust for time scale

        old_level = self.suspicion_level
        self.suspicion_level = max(0.0, self.suspicion_level - decay_amount)

        # Check for tier downgrade
        if self.suspicion_level < old_level:
            new_tier = self.get_current_tier()
            if new_tier != self.current_tier:
                old_tier = self.current_tier
                self.current_tier = new_tier
                tier_change = {
                    'timestamp': time.time(),
                    'old_tier': old_tier,
                    'new_tier': new_tier,
                    'suspicion_level': self.suspicion_level,
                }
                self.tier_changes.append(tier_change)
                print(f"✓ Suspicion tier lowered: {self.tier_names[old_tier]} → {self.tier_names[new_tier]} ({self.suspicion_level:.1f})")

    def process_detection_report(self, report: Dict) -> bool:
        """
        Process a detection report from DetectionManager.

        Args:
            report (dict): Detection report containing suspicion_increase

        Returns:
            bool: True if tier changed
        """
        suspicion_increase = report.get('suspicion_increase', 0.0)
        detection_level = report.get('detection_level', 'unknown')

        description = f"NPC detected robot ({detection_level})"

        return self.add_suspicion(suspicion_increase, 'npc_detection', description)

    def get_recent_events(self, count: int = 10) -> List[Dict]:
        """
        Get recent suspicion events.

        Args:
            count (int): Number of events to return

        Returns:
            List of recent events
        """
        return self.suspicion_events[-count:] if self.suspicion_events else []

    def get_tier_effects(self) -> Dict:
        """
        Get effects for current tier.

        Returns:
            Dict: Dictionary of tier effects
        """
        return self.tier_effects.get(self.current_tier, {})

    def get_police_patrol_multiplier(self) -> float:
        """Get police patrol multiplier for current tier."""
        effects = self.get_tier_effects()
        return effects.get('police_patrol_multiplier', 1.0)

    def get_npc_alertness_multiplier(self) -> float:
        """Get NPC alertness multiplier for current tier."""
        effects = self.get_tier_effects()
        return effects.get('npc_alertness_multiplier', 1.0)

    def get_camera_detection_bonus(self) -> float:
        """Get camera detection bonus for current tier."""
        effects = self.get_tier_effects()
        return effects.get('camera_detection_bonus', 0.0)

    def has_undercover_agents(self) -> bool:
        """Check if tier has undercover agents."""
        effects = self.get_tier_effects()
        return effects.get('undercover_agents', False)

    def has_checkpoints(self) -> bool:
        """Check if tier has checkpoints."""
        effects = self.get_tier_effects()
        return effects.get('checkpoints', False)

    def has_operation_hours_limited(self) -> bool:
        """Check if tier has limited operation hours."""
        effects = self.get_tier_effects()
        return effects.get('operation_hours_limited', False)

    def has_weekly_inspections(self) -> bool:
        """Check if tier requires weekly inspections."""
        effects = self.get_tier_effects()
        return effects.get('weekly_inspections', False)

    def get_tier_consequences(self) -> List[str]:
        """
        Get list of consequences for current tier.

        Returns:
            List of consequence strings
        """
        tier = self.current_tier

        if tier == SuspicionTier.NORMAL:
            return ["No special attention"]
        elif tier == SuspicionTier.RUMORS:
            return [
                "Slight increase in police patrols",
                "NPCs slightly more alert"
            ]
        elif tier == SuspicionTier.INVESTIGATION:
            return [
                "Increased police presence",
                "NPCs more suspicious",
                "Occasional drive-bys near factory"
            ]
        elif tier == SuspicionTier.INSPECTION:
            return [
                "Inspection scheduled",
                "Heavy police presence",
                "Cannot perform illegal activities during inspection",
                "Must pass inspection or face consequences"
            ]
        elif tier == SuspicionTier.RESTRICTIONS:
            return [
                "FBI investigation",
                "Severe restrictions on operations",
                "High chance of game over",
                "Must drastically reduce suspicion"
            ]
        else:
            return []

    def get_stats(self) -> Dict:
        """
        Get suspicion statistics.

        Returns:
            Dictionary with suspicion stats
        """
        return {
            'level': self.suspicion_level,
            'tier': self.current_tier,
            'tier_name': self.tier_names[self.current_tier],
            'total_events': len(self.suspicion_events),
            'tier_changes': len(self.tier_changes),
            'decaying': self.suspicion_level < self.decay_stops_at,
        }

    def get_tier_progress(self) -> float:
        """
        Get progress towards next tier (0.0-1.0).

        Returns:
            float: Progress within current tier
        """
        current_tier = self.current_tier
        tier_list = [
            SuspicionTier.NORMAL,
            SuspicionTier.RUMORS,
            SuspicionTier.INVESTIGATION,
            SuspicionTier.INSPECTION,
            SuspicionTier.RESTRICTIONS
        ]

        current_index = tier_list.index(current_tier)

        # Get thresholds
        current_threshold = self.tier_thresholds[current_tier]
        if current_index < len(tier_list) - 1:
            next_threshold = self.tier_thresholds[tier_list[current_index + 1]]
        else:
            next_threshold = 100  # Max level

        # Calculate progress
        tier_range = next_threshold - current_threshold
        progress_in_tier = self.suspicion_level - current_threshold

        if tier_range > 0:
            return progress_in_tier / tier_range
        else:
            return 1.0

    def __repr__(self):
        """String representation for debugging."""
        return f"SuspicionManager(level={self.suspicion_level:.1f}, tier={self.tier_names[self.current_tier]})"
