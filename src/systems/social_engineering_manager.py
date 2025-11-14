"""
Social Engineering Manager - Manages propaganda, community relations, and bribery.

Handles:
- Rumor management
- Community relations
- Propaganda campaigns
- Donations and sponsorships
"""

from typing import List, Dict, Optional
from enum import Enum


class CampaignType(Enum):
    """Types of social engineering campaigns."""
    COUNTER_RUMOR = "counter_rumor"
    DONATION = "donation"
    SPONSORSHIP = "sponsorship"
    PROPAGANDA = "propaganda"


class CampaignStatus(Enum):
    """Campaign status."""
    PENDING = "pending"      # Campaign started, not yet effective
    ACTIVE = "active"        # Campaign is having effect
    COMPLETED = "completed"  # Campaign finished


class SocialEngineeringManager:
    """
    Manages social engineering and community relations.

    Players can use social engineering to reduce suspicion growth,
    improve their standing in the community, and counter negative rumors.
    """

    def __init__(self, resource_manager, suspicion_manager):
        """
        Initialize social engineering manager.

        Args:
            resource_manager: ResourceManager for campaign costs
            suspicion_manager: SuspicionManager for tracking suspicion
        """
        self.resources = resource_manager
        self.suspicion = suspicion_manager

        # Campaign costs
        self.counter_rumor_cost = 1000
        self.donation_cost = 5000
        self.sponsorship_cost = 10000
        self.propaganda_weekly_cost = 2000

        # Community relation level (0-100)
        self.community_relations = 50.0  # Start neutral

        # Good neighbor bonus
        self.good_neighbor_active = False
        self.good_neighbor_bonus = -0.2  # Suspicion per day

        # Active campaigns
        self.active_campaigns: List[Dict] = []

        # Propaganda system
        self.propaganda_active = False
        self.propaganda_next_payment = 0.0
        self.propaganda_effectiveness = 0.5  # 50% suspicion growth reduction

        # Research requirements
        self.has_social_engineering_research = False

        # Statistics
        self.total_spent = 0.0
        self.total_suspicion_reduced = 0.0
        self.campaigns_run = 0

    def update(self, dt: float, game_time: float):
        """
        Update social engineering manager.

        Args:
            dt: Delta time in seconds
            game_time: Current game time
        """
        # Update active campaigns
        self._update_campaigns(dt, game_time)

        # Handle propaganda payments
        if self.propaganda_active:
            self._handle_propaganda_payment(game_time)

        # Apply good neighbor bonus
        if self.good_neighbor_active:
            # Apply daily suspicion reduction
            daily_bonus = self.good_neighbor_bonus * (dt / (24 * 3600))
            if daily_bonus < 0:  # Make sure we're reducing
                self.suspicion.add_suspicion(daily_bonus, "Good neighbor bonus")

    def _update_campaigns(self, dt: float, game_time: float):
        """Update active campaigns."""
        for campaign in self.active_campaigns[:]:  # Copy to allow removal
            if campaign['status'] == CampaignStatus.PENDING:
                # Check if campaign should become active
                campaign['time_elapsed'] += dt
                if campaign['time_elapsed'] >= campaign['activation_time']:
                    campaign['status'] = CampaignStatus.ACTIVE
                    self._activate_campaign(campaign, game_time)

            elif campaign['status'] == CampaignStatus.ACTIVE:
                # Check if campaign should complete
                campaign['time_elapsed'] += dt
                if campaign['time_elapsed'] >= campaign['duration']:
                    campaign['status'] = CampaignStatus.COMPLETED
                    self.active_campaigns.remove(campaign)

    def _activate_campaign(self, campaign: Dict, game_time: float):
        """Activate a campaign's effects."""
        campaign_type = campaign['type']

        if campaign_type == CampaignType.COUNTER_RUMOR:
            # Reduce suspicion by 5
            self.suspicion.add_suspicion(-5, "Counter-rumor campaign")
            self.total_suspicion_reduced += 5
            print(f"\n📢 Counter-rumor campaign taking effect")
            print(f"   Suspicion reduced by 5")
            print()

        # Community relations improvement happens over time
        # This is handled in the campaign duration

    def counter_rumors(self, game_time: float) -> bool:
        """
        Start a counter-rumor campaign.

        Costs $1,000, reduces suspicion by 5 after 3 days.

        Args:
            game_time: Current game time

        Returns:
            bool: True if campaign started successfully
        """
        # Check if rumors are present (suspicion > 20)
        if self.suspicion.suspicion_level < 20:
            print("No rumors to counter (suspicion too low)")
            return False

        # Check money
        if self.resources.money < self.counter_rumor_cost:
            print(f"Not enough money (need ${self.counter_rumor_cost:,})")
            return False

        # Pay cost
        self.resources.modify_money(-self.counter_rumor_cost)
        self.total_spent += self.counter_rumor_cost

        # Create campaign
        campaign = {
            'type': CampaignType.COUNTER_RUMOR,
            'status': CampaignStatus.PENDING,
            'start_time': game_time,
            'activation_time': 3 * 24 * 3600,  # 3 game days
            'duration': 3 * 24 * 3600 + 1,  # Just past activation
            'time_elapsed': 0.0,
        }
        self.active_campaigns.append(campaign)
        self.campaigns_run += 1

        print(f"\n📢 Counter-Rumor Campaign Started")
        print(f"   Cost: ${self.counter_rumor_cost:,}")
        print(f"   Takes effect in 3 game days")
        print(f"   Effect: -5 suspicion")
        print()

        return True

    def donate_to_city(self, game_time: float) -> bool:
        """
        Donate to the city.

        Costs $5,000, reduces suspicion by 3 immediately.

        Args:
            game_time: Current game time

        Returns:
            bool: True if donation successful
        """
        # Check money
        if self.resources.money < self.donation_cost:
            print(f"Not enough money (need ${self.donation_cost:,})")
            return False

        # Pay cost
        self.resources.modify_money(-self.donation_cost)
        self.total_spent += self.donation_cost

        # Reduce suspicion
        self.suspicion.add_suspicion(-3, "City donation")
        self.total_suspicion_reduced += 3

        # Improve community relations
        self.community_relations = min(100.0, self.community_relations + 5)

        # Check for good neighbor status
        if self.community_relations >= 70 and not self.good_neighbor_active:
            self.good_neighbor_active = True
            print("\n✓ GOOD NEIGHBOR STATUS ACTIVATED!")
            print(f"   Passive suspicion reduction: {abs(self.good_neighbor_bonus)} per day")
            print()

        print(f"\n💰 City Donation")
        print(f"   Donated: ${self.donation_cost:,}")
        print(f"   Suspicion reduced by 3")
        print(f"   Community relations: {self.community_relations:.0f}/100")
        print()

        return True

    def sponsor_event(self, game_time: float) -> bool:
        """
        Sponsor a city event.

        Costs $10,000, reduces suspicion by 8, major community relations boost.

        Args:
            game_time: Current game time

        Returns:
            bool: True if sponsorship successful
        """
        # Check money
        if self.resources.money < self.sponsorship_cost:
            print(f"Not enough money (need ${self.sponsorship_cost:,})")
            return False

        # Pay cost
        self.resources.modify_money(-self.sponsorship_cost)
        self.total_spent += self.sponsorship_cost

        # Reduce suspicion
        self.suspicion.add_suspicion(-8, "Event sponsorship")
        self.total_suspicion_reduced += 8

        # Improve community relations significantly
        self.community_relations = min(100.0, self.community_relations + 15)

        # Check for good neighbor status
        if self.community_relations >= 70 and not self.good_neighbor_active:
            self.good_neighbor_active = True
            print("\n✓ GOOD NEIGHBOR STATUS ACTIVATED!")
            print(f"   Passive suspicion reduction: {abs(self.good_neighbor_bonus)} per day")
            print()

        print(f"\n🎉 Event Sponsorship")
        print(f"   Sponsored event for ${self.sponsorship_cost:,}")
        print(f"   Suspicion reduced by 8")
        print(f"   Community relations: {self.community_relations:.0f}/100")
        print()

        return True

    def start_propaganda(self, game_time: float) -> bool:
        """
        Start propaganda campaign.

        Requires Social Engineering research.
        Costs $2,000 per week, reduces suspicion growth by 50%.

        Args:
            game_time: Current game time

        Returns:
            bool: True if propaganda started successfully
        """
        if not self.has_social_engineering_research:
            print("Requires Social Engineering research")
            return False

        if self.propaganda_active:
            print("Propaganda already active")
            return False

        # Check money for first payment
        if self.resources.money < self.propaganda_weekly_cost:
            print(f"Not enough money (need ${self.propaganda_weekly_cost:,})")
            return False

        # Pay first week
        self.resources.modify_money(-self.propaganda_weekly_cost)
        self.total_spent += self.propaganda_weekly_cost

        self.propaganda_active = True
        self.propaganda_next_payment = game_time + (7 * 24 * 3600)  # Next week

        print(f"\n📺 Propaganda Campaign Started")
        print(f"   Weekly cost: ${self.propaganda_weekly_cost:,}")
        print(f"   Effect: Reduces suspicion growth by 50%")
        print(f"   Warning: Can fail if evidence is too strong")
        print()

        return True

    def stop_propaganda(self):
        """Stop propaganda campaign."""
        if not self.propaganda_active:
            return False

        self.propaganda_active = False
        print("\n📺 Propaganda Campaign Stopped")
        print()
        return True

    def _handle_propaganda_payment(self, game_time: float):
        """Handle weekly propaganda payments."""
        if game_time >= self.propaganda_next_payment:
            # Check if can afford
            if self.resources.money >= self.propaganda_weekly_cost:
                self.resources.modify_money(-self.propaganda_weekly_cost)
                self.total_spent += self.propaganda_weekly_cost
                self.propaganda_next_payment = game_time + (7 * 24 * 3600)

                print(f"\n📺 Propaganda weekly payment: ${self.propaganda_weekly_cost:,}")
            else:
                # Can't afford - propaganda stops
                print("\n📺 Propaganda campaign ended (insufficient funds)")
                self.propaganda_active = False

    def get_suspicion_growth_modifier(self) -> float:
        """
        Get modifier for suspicion growth.

        Returns:
            float: Multiplier for suspicion growth (0.5 = 50% growth)
        """
        if self.propaganda_active:
            # Check if propaganda can work (fails if suspicion too high)
            if self.suspicion.suspicion_level >= 80:
                return 1.0  # Propaganda ineffective at high suspicion
            return self.propaganda_effectiveness
        return 1.0

    def can_use_social_engineering(self) -> bool:
        """Check if can use advanced social engineering (requires research)."""
        return self.has_social_engineering_research

    def set_research_completed(self, research_id: str):
        """
        Mark research as completed.

        Args:
            research_id: Research ID
        """
        if research_id == "social_engineering":
            self.has_social_engineering_research = True

    def get_community_relations_tier(self) -> str:
        """Get community relations tier name."""
        if self.community_relations >= 80:
            return "Beloved"
        elif self.community_relations >= 70:
            return "Good Neighbor"
        elif self.community_relations >= 50:
            return "Neutral"
        elif self.community_relations >= 30:
            return "Suspicious"
        else:
            return "Hostile"

    def get_stats(self) -> Dict:
        """Get social engineering statistics."""
        return {
            'community_relations': self.community_relations,
            'community_tier': self.get_community_relations_tier(),
            'good_neighbor_active': self.good_neighbor_active,
            'active_campaigns': len(self.active_campaigns),
            'propaganda_active': self.propaganda_active,
            'total_spent': self.total_spent,
            'total_suspicion_reduced': self.total_suspicion_reduced,
            'campaigns_run': self.campaigns_run,
        }

    def get_active_campaigns_info(self) -> List[Dict]:
        """Get information about active campaigns."""
        campaigns_info = []
        for campaign in self.active_campaigns:
            info = {
                'type': campaign['type'].value,
                'status': campaign['status'].value,
                'time_elapsed': campaign['time_elapsed'],
                'activation_time': campaign['activation_time'],
            }
            campaigns_info.append(info)
        return campaigns_info
