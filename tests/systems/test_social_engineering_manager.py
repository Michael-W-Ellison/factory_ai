"""
Tests for SocialEngineeringManager.

Tests social engineering mechanics including:
- Counter-rumor campaigns
- Donations to city
- Event sponsorship
- Propaganda campaigns
- Community relations
- Good neighbor status
- Statistics tracking
"""

import sys
from unittest.mock import MagicMock

# Mock pygame before any imports that might need it
sys.modules['pygame'] = MagicMock()
sys.modules['pygame.font'] = MagicMock()
sys.modules['pygame.transform'] = MagicMock()
sys.modules['pygame.Surface'] = MagicMock()

import pytest

from src.systems.social_engineering_manager import (
    SocialEngineeringManager,
    CampaignType,
    CampaignStatus
)


class MockResourceManager:
    """Mock resource manager for testing."""

    def __init__(self, initial_money: float = 100000.0):
        self.money = initial_money

    def modify_money(self, amount: float):
        self.money += amount

    def get_money(self) -> float:
        return self.money


class MockSuspicionManager:
    """Mock suspicion manager for testing."""

    def __init__(self, initial_level: float = 0.0):
        self.suspicion_level = initial_level
        self.history = []

    def add_suspicion(self, amount: float, reason: str = ""):
        self.suspicion_level = max(0, min(100, self.suspicion_level + amount))
        self.history.append((amount, reason))


@pytest.fixture
def mock_resource_manager():
    """Provide a mock resource manager."""
    return MockResourceManager()


@pytest.fixture
def mock_suspicion_manager():
    """Provide a mock suspicion manager."""
    return MockSuspicionManager()


@pytest.fixture
def social_manager(mock_resource_manager, mock_suspicion_manager):
    """Provide a social engineering manager with mocked dependencies."""
    return SocialEngineeringManager(mock_resource_manager, mock_suspicion_manager)


class TestCampaignEnums:
    """Tests for campaign enums."""

    def test_campaign_type_values(self):
        """Test CampaignType enum values."""
        assert CampaignType.COUNTER_RUMOR.value == "counter_rumor"
        assert CampaignType.DONATION.value == "donation"
        assert CampaignType.SPONSORSHIP.value == "sponsorship"
        assert CampaignType.PROPAGANDA.value == "propaganda"

    def test_campaign_status_values(self):
        """Test CampaignStatus enum values."""
        assert CampaignStatus.PENDING.value == "pending"
        assert CampaignStatus.ACTIVE.value == "active"
        assert CampaignStatus.COMPLETED.value == "completed"


class TestSocialEngineeringManagerInit:
    """Tests for SocialEngineeringManager initialization."""

    def test_manager_initialization(self, social_manager):
        """Test that SocialEngineeringManager initializes correctly."""
        assert social_manager.community_relations == 50.0
        assert social_manager.good_neighbor_active is False
        assert social_manager.propaganda_active is False
        assert social_manager.active_campaigns == []
        assert social_manager.has_social_engineering_research is False

    def test_manager_costs(self, social_manager):
        """Test that campaign costs are set correctly."""
        assert social_manager.counter_rumor_cost == 1000
        assert social_manager.donation_cost == 5000
        assert social_manager.sponsorship_cost == 10000
        assert social_manager.propaganda_weekly_cost == 2000

    def test_manager_statistics_init(self, social_manager):
        """Test that statistics are initialized to zero."""
        assert social_manager.total_spent == 0.0
        assert social_manager.total_suspicion_reduced == 0.0
        assert social_manager.campaigns_run == 0


class TestCounterRumors:
    """Tests for counter-rumor campaigns."""

    def test_counter_rumors_success(self, social_manager, mock_suspicion_manager, mock_resource_manager):
        """Test successfully starting a counter-rumor campaign."""
        mock_suspicion_manager.suspicion_level = 30.0
        initial_money = mock_resource_manager.money

        result = social_manager.counter_rumors(game_time=0.0)

        assert result is True
        assert len(social_manager.active_campaigns) == 1
        assert social_manager.active_campaigns[0]['type'] == CampaignType.COUNTER_RUMOR
        assert mock_resource_manager.money == initial_money - 1000

    def test_counter_rumors_low_suspicion_fails(self, social_manager, mock_suspicion_manager):
        """Test that counter-rumors fails when suspicion is too low."""
        mock_suspicion_manager.suspicion_level = 10.0  # Below 20 threshold

        result = social_manager.counter_rumors(game_time=0.0)

        assert result is False
        assert len(social_manager.active_campaigns) == 0

    def test_counter_rumors_insufficient_funds(self, social_manager, mock_suspicion_manager, mock_resource_manager):
        """Test that counter-rumors fails with insufficient funds."""
        mock_suspicion_manager.suspicion_level = 30.0
        mock_resource_manager.money = 500.0  # Not enough

        result = social_manager.counter_rumors(game_time=0.0)

        assert result is False
        assert len(social_manager.active_campaigns) == 0

    def test_counter_rumors_tracks_spending(self, social_manager, mock_suspicion_manager):
        """Test that counter-rumors tracks spending."""
        mock_suspicion_manager.suspicion_level = 30.0

        social_manager.counter_rumors(game_time=0.0)

        assert social_manager.total_spent == 1000.0
        assert social_manager.campaigns_run == 1

    def test_counter_rumors_campaign_status(self, social_manager, mock_suspicion_manager):
        """Test counter-rumors campaign starts as pending."""
        mock_suspicion_manager.suspicion_level = 30.0

        social_manager.counter_rumors(game_time=0.0)

        campaign = social_manager.active_campaigns[0]
        assert campaign['status'] == CampaignStatus.PENDING
        assert campaign['time_elapsed'] == 0.0


class TestDonateToCity:
    """Tests for city donations."""

    def test_donate_to_city_success(self, social_manager, mock_resource_manager):
        """Test successfully donating to city."""
        initial_money = mock_resource_manager.money

        result = social_manager.donate_to_city(game_time=0.0)

        assert result is True
        assert mock_resource_manager.money == initial_money - 5000

    def test_donate_to_city_insufficient_funds(self, social_manager, mock_resource_manager):
        """Test donation fails with insufficient funds."""
        mock_resource_manager.money = 1000.0

        result = social_manager.donate_to_city(game_time=0.0)

        assert result is False

    def test_donate_to_city_reduces_suspicion(self, social_manager, mock_suspicion_manager):
        """Test that donation reduces suspicion by 3."""
        mock_suspicion_manager.suspicion_level = 50.0

        social_manager.donate_to_city(game_time=0.0)

        # Check suspicion was reduced
        assert (-3, "City donation") in mock_suspicion_manager.history

    def test_donate_to_city_improves_relations(self, social_manager):
        """Test that donation improves community relations."""
        initial_relations = social_manager.community_relations

        social_manager.donate_to_city(game_time=0.0)

        assert social_manager.community_relations == initial_relations + 5

    def test_donate_to_city_activates_good_neighbor(self, social_manager):
        """Test that donation can activate good neighbor status."""
        social_manager.community_relations = 66.0  # Just below 70 threshold

        social_manager.donate_to_city(game_time=0.0)

        # Now at 71
        assert social_manager.community_relations >= 70
        assert social_manager.good_neighbor_active is True

    def test_donate_to_city_tracks_stats(self, social_manager):
        """Test that donation tracks spending and suspicion reduced."""
        social_manager.donate_to_city(game_time=0.0)

        assert social_manager.total_spent == 5000.0
        assert social_manager.total_suspicion_reduced == 3.0


class TestSponsorEvent:
    """Tests for event sponsorship."""

    def test_sponsor_event_success(self, social_manager, mock_resource_manager):
        """Test successfully sponsoring an event."""
        initial_money = mock_resource_manager.money

        result = social_manager.sponsor_event(game_time=0.0)

        assert result is True
        assert mock_resource_manager.money == initial_money - 10000

    def test_sponsor_event_insufficient_funds(self, social_manager, mock_resource_manager):
        """Test sponsorship fails with insufficient funds."""
        mock_resource_manager.money = 5000.0

        result = social_manager.sponsor_event(game_time=0.0)

        assert result is False

    def test_sponsor_event_reduces_suspicion(self, social_manager, mock_suspicion_manager):
        """Test that sponsorship reduces suspicion by 8."""
        mock_suspicion_manager.suspicion_level = 50.0

        social_manager.sponsor_event(game_time=0.0)

        assert (-8, "Event sponsorship") in mock_suspicion_manager.history

    def test_sponsor_event_improves_relations_significantly(self, social_manager):
        """Test that sponsorship improves relations by 15."""
        initial_relations = social_manager.community_relations

        social_manager.sponsor_event(game_time=0.0)

        assert social_manager.community_relations == initial_relations + 15

    def test_sponsor_event_tracks_stats(self, social_manager):
        """Test that sponsorship tracks spending and suspicion reduced."""
        social_manager.sponsor_event(game_time=0.0)

        assert social_manager.total_spent == 10000.0
        assert social_manager.total_suspicion_reduced == 8.0


class TestPropaganda:
    """Tests for propaganda campaigns."""

    def test_start_propaganda_requires_research(self, social_manager):
        """Test that starting propaganda requires research."""
        social_manager.has_social_engineering_research = False

        result = social_manager.start_propaganda(game_time=0.0)

        assert result is False
        assert social_manager.propaganda_active is False

    def test_start_propaganda_success(self, social_manager, mock_resource_manager):
        """Test successfully starting propaganda."""
        social_manager.has_social_engineering_research = True
        initial_money = mock_resource_manager.money

        result = social_manager.start_propaganda(game_time=0.0)

        assert result is True
        assert social_manager.propaganda_active is True
        assert mock_resource_manager.money == initial_money - 2000

    def test_start_propaganda_insufficient_funds(self, social_manager, mock_resource_manager):
        """Test that propaganda fails with insufficient funds."""
        social_manager.has_social_engineering_research = True
        mock_resource_manager.money = 1000.0

        result = social_manager.start_propaganda(game_time=0.0)

        assert result is False
        assert social_manager.propaganda_active is False

    def test_start_propaganda_already_active(self, social_manager):
        """Test that starting propaganda fails if already active."""
        social_manager.has_social_engineering_research = True
        social_manager.propaganda_active = True

        result = social_manager.start_propaganda(game_time=0.0)

        assert result is False

    def test_stop_propaganda_success(self, social_manager):
        """Test successfully stopping propaganda."""
        social_manager.propaganda_active = True

        result = social_manager.stop_propaganda()

        assert result is True
        assert social_manager.propaganda_active is False

    def test_stop_propaganda_not_active(self, social_manager):
        """Test stopping propaganda when not active returns False."""
        social_manager.propaganda_active = False

        result = social_manager.stop_propaganda()

        assert result is False


class TestSuspicionGrowthModifier:
    """Tests for suspicion growth modifier."""

    def test_modifier_without_propaganda(self, social_manager):
        """Test that modifier is 1.0 without propaganda."""
        social_manager.propaganda_active = False

        modifier = social_manager.get_suspicion_growth_modifier()

        assert modifier == 1.0

    def test_modifier_with_propaganda(self, social_manager, mock_suspicion_manager):
        """Test that modifier is reduced with propaganda."""
        social_manager.propaganda_active = True
        mock_suspicion_manager.suspicion_level = 50.0

        modifier = social_manager.get_suspicion_growth_modifier()

        assert modifier == 0.5

    def test_modifier_propaganda_ineffective_high_suspicion(self, social_manager, mock_suspicion_manager):
        """Test that propaganda is ineffective at high suspicion."""
        social_manager.propaganda_active = True
        mock_suspicion_manager.suspicion_level = 85.0  # Above 80 threshold

        modifier = social_manager.get_suspicion_growth_modifier()

        assert modifier == 1.0


class TestCommunityRelations:
    """Tests for community relations system."""

    def test_community_relations_tier_hostile(self, social_manager):
        """Test hostile tier below 30."""
        social_manager.community_relations = 20.0

        tier = social_manager.get_community_relations_tier()

        assert tier == "Hostile"

    def test_community_relations_tier_suspicious(self, social_manager):
        """Test suspicious tier 30-49."""
        social_manager.community_relations = 40.0

        tier = social_manager.get_community_relations_tier()

        assert tier == "Suspicious"

    def test_community_relations_tier_neutral(self, social_manager):
        """Test neutral tier 50-69."""
        social_manager.community_relations = 60.0

        tier = social_manager.get_community_relations_tier()

        assert tier == "Neutral"

    def test_community_relations_tier_good_neighbor(self, social_manager):
        """Test good neighbor tier 70-79."""
        social_manager.community_relations = 75.0

        tier = social_manager.get_community_relations_tier()

        assert tier == "Good Neighbor"

    def test_community_relations_tier_beloved(self, social_manager):
        """Test beloved tier 80+."""
        social_manager.community_relations = 90.0

        tier = social_manager.get_community_relations_tier()

        assert tier == "Beloved"

    def test_community_relations_capped_at_100(self, social_manager):
        """Test that community relations don't exceed 100."""
        social_manager.community_relations = 95.0

        social_manager.sponsor_event(game_time=0.0)  # Would add 15

        assert social_manager.community_relations == 100.0


class TestResearchCompletion:
    """Tests for research completion."""

    def test_set_research_completed_social_engineering(self, social_manager):
        """Test setting social engineering research as completed."""
        social_manager.set_research_completed("social_engineering")

        assert social_manager.has_social_engineering_research is True

    def test_set_research_completed_other(self, social_manager):
        """Test that other research IDs don't affect social engineering."""
        social_manager.set_research_completed("other_research")

        assert social_manager.has_social_engineering_research is False

    def test_can_use_social_engineering(self, social_manager):
        """Test can_use_social_engineering checks research."""
        assert social_manager.can_use_social_engineering() is False

        social_manager.has_social_engineering_research = True

        assert social_manager.can_use_social_engineering() is True


class TestUpdateCampaigns:
    """Tests for campaign update logic."""

    def test_update_campaign_progress(self, social_manager, mock_suspicion_manager):
        """Test that campaigns progress over time."""
        mock_suspicion_manager.suspicion_level = 30.0
        social_manager.counter_rumors(game_time=0.0)

        # Update with some time
        social_manager.update(dt=1000.0, game_time=1000.0)

        campaign = social_manager.active_campaigns[0]
        assert campaign['time_elapsed'] == 1000.0

    def test_update_activates_campaign(self, social_manager, mock_suspicion_manager):
        """Test that campaigns activate after activation time."""
        mock_suspicion_manager.suspicion_level = 30.0
        social_manager.counter_rumors(game_time=0.0)

        # Update past activation time (3 days = 3 * 24 * 3600 seconds)
        activation_time = 3 * 24 * 3600
        social_manager.update(dt=activation_time + 1, game_time=activation_time + 1)

        campaign = social_manager.active_campaigns[0]
        assert campaign['status'] == CampaignStatus.ACTIVE

    def test_update_completes_campaign(self, social_manager, mock_suspicion_manager):
        """Test that campaigns complete after duration."""
        mock_suspicion_manager.suspicion_level = 30.0
        social_manager.counter_rumors(game_time=0.0)

        # Update well past duration
        long_time = 10 * 24 * 3600  # 10 days
        social_manager.update(dt=long_time, game_time=long_time)

        # Campaign should be removed after completion
        assert len(social_manager.active_campaigns) == 0


class TestStatistics:
    """Tests for statistics retrieval."""

    def test_get_stats(self, social_manager, mock_suspicion_manager):
        """Test getting full statistics."""
        mock_suspicion_manager.suspicion_level = 30.0
        social_manager.donate_to_city(game_time=0.0)
        social_manager.counter_rumors(game_time=0.0)

        stats = social_manager.get_stats()

        assert 'community_relations' in stats
        assert 'community_tier' in stats
        assert 'good_neighbor_active' in stats
        assert 'active_campaigns' in stats
        assert 'propaganda_active' in stats
        assert 'total_spent' in stats
        assert 'total_suspicion_reduced' in stats
        assert 'campaigns_run' in stats
        assert stats['total_spent'] == 6000.0  # 5000 + 1000
        assert stats['active_campaigns'] == 1

    def test_get_active_campaigns_info(self, social_manager, mock_suspicion_manager):
        """Test getting active campaigns info."""
        mock_suspicion_manager.suspicion_level = 30.0
        social_manager.counter_rumors(game_time=100.0)

        campaigns_info = social_manager.get_active_campaigns_info()

        assert len(campaigns_info) == 1
        assert campaigns_info[0]['type'] == "counter_rumor"
        assert campaigns_info[0]['status'] == "pending"
        assert 'time_elapsed' in campaigns_info[0]
        assert 'activation_time' in campaigns_info[0]
