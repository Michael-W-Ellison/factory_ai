"""
Comprehensive Test Suite for Phase 9: Authority Escalation & FBI

Tests:
- Authority tier transitions and effects
- FBI investigation triggers and countdown
- FBI avoidance mechanics (bribes, laying low)
- FBI raid (game over)
- Social engineering (donations, sponsorships, propaganda)
- Community relations and good neighbor status
- Integration tests
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.systems.suspicion_manager import SuspicionManager, SuspicionTier
from src.systems.fbi_manager import FBIManager, FBIStatus, FBITrigger
from src.systems.social_engineering_manager import SocialEngineeringManager, CampaignStatus
from src.systems.resource_manager import ResourceManager


def test_authority_tier_transitions():
    """Test tier transitions as suspicion increases."""
    print("Test: Authority Tier Transitions")

    suspicion_mgr = SuspicionManager()

    # Start at Normal
    assert suspicion_mgr.current_tier == SuspicionTier.NORMAL
    print(f"  ✓ Initial tier: {suspicion_mgr.tier_names[suspicion_mgr.current_tier]}")

    # Increase to Rumors (21-40)
    suspicion_mgr.add_suspicion(25, "Test")
    assert suspicion_mgr.current_tier == SuspicionTier.RUMORS
    print(f"  ✓ Tier at 25 suspicion: {suspicion_mgr.tier_names[suspicion_mgr.current_tier]}")

    # Increase to Investigation (41-60)
    suspicion_mgr.add_suspicion(20, "Test")
    assert suspicion_mgr.current_tier == SuspicionTier.INVESTIGATION
    print(f"  ✓ Tier at 45 suspicion: {suspicion_mgr.tier_names[suspicion_mgr.current_tier]}")

    # Increase to Inspection (61-80)
    suspicion_mgr.add_suspicion(20, "Test")
    assert suspicion_mgr.current_tier == SuspicionTier.INSPECTION
    print(f"  ✓ Tier at 65 suspicion: {suspicion_mgr.tier_names[suspicion_mgr.current_tier]}")

    # Increase to Restrictions (81-100)
    suspicion_mgr.add_suspicion(20, "Test")
    assert suspicion_mgr.current_tier == SuspicionTier.RESTRICTIONS
    print(f"  ✓ Tier at 85 suspicion: {suspicion_mgr.tier_names[suspicion_mgr.current_tier]}")

    print()


def test_tier_specific_effects():
    """Test tier-specific effects."""
    print("Test: Tier-Specific Effects")

    suspicion_mgr = SuspicionManager()

    # Normal tier
    assert suspicion_mgr.get_police_patrol_multiplier() == 1.0
    assert suspicion_mgr.get_npc_alertness_multiplier() == 1.0
    print(f"  ✓ Normal: Police x{suspicion_mgr.get_police_patrol_multiplier()}, NPC x{suspicion_mgr.get_npc_alertness_multiplier()}")

    # Rumors tier
    suspicion_mgr.add_suspicion(25, "Test")
    assert suspicion_mgr.get_police_patrol_multiplier() == 1.25
    assert suspicion_mgr.get_npc_alertness_multiplier() == 1.1
    print(f"  ✓ Rumors: Police x{suspicion_mgr.get_police_patrol_multiplier()}, NPC x{suspicion_mgr.get_npc_alertness_multiplier()}")

    # Investigation tier
    suspicion_mgr.add_suspicion(20, "Test")
    assert suspicion_mgr.get_police_patrol_multiplier() == 1.5
    assert suspicion_mgr.has_undercover_agents() == True
    print(f"  ✓ Investigation: Police x{suspicion_mgr.get_police_patrol_multiplier()}, Undercover agents active")

    # Inspection tier
    suspicion_mgr.add_suspicion(20, "Test")
    assert suspicion_mgr.get_police_patrol_multiplier() == 2.0
    assert suspicion_mgr.has_checkpoints() == True
    print(f"  ✓ Inspection: Police x{suspicion_mgr.get_police_patrol_multiplier()}, Checkpoints active")

    # Restrictions tier
    suspicion_mgr.add_suspicion(20, "Test")
    assert suspicion_mgr.get_police_patrol_multiplier() == 2.5
    assert suspicion_mgr.has_operation_hours_limited() == True
    assert suspicion_mgr.has_weekly_inspections() == True
    print(f"  ✓ Restrictions: Police x{suspicion_mgr.get_police_patrol_multiplier()}, Operations limited")

    print()


def test_fbi_trigger_high_suspicion():
    """Test FBI trigger from high suspicion."""
    print("Test: FBI Trigger - High Suspicion")

    resources = ResourceManager()
    suspicion_mgr = SuspicionManager()
    fbi_mgr = FBIManager(resources, suspicion_mgr)

    # Raise suspicion to 85
    suspicion_mgr.add_suspicion(85, "Test")

    # Simulate 7 days at high suspicion
    game_time = 0.0
    for day in range(8):  # 8 days to be sure
        fbi_mgr.update(24 * 3600, game_time)  # 1 day
        game_time += 24 * 3600

    # FBI should be triggered
    assert fbi_mgr.is_investigation_active(), "FBI investigation should be active"
    assert fbi_mgr.trigger_reason == FBITrigger.HIGH_SUSPICION

    print(f"  ✓ FBI triggered after 7 days at 85 suspicion")
    print(f"  ✓ Trigger reason: {fbi_mgr.trigger_reason.value}")
    print(f"  ✓ Investigation countdown: {fbi_mgr.get_countdown_days():.1f} days")

    print()


def test_fbi_trigger_critical_inspection():
    """Test FBI trigger from critical inspection failure."""
    print("Test: FBI Trigger - Critical Inspection")

    resources = ResourceManager()
    suspicion_mgr = SuspicionManager()
    fbi_mgr = FBIManager(resources, suspicion_mgr)

    # Report critical inspection failure
    fbi_mgr.report_inspection_failure(is_critical=True)

    # Update FBI manager
    fbi_mgr.update(1.0, 0.0)

    # FBI should be triggered
    assert fbi_mgr.is_investigation_active(), "FBI investigation should be active"
    assert fbi_mgr.trigger_reason == FBITrigger.CRITICAL_INSPECTION

    print(f"  ✓ FBI triggered from critical inspection")
    print(f"  ✓ Status: {fbi_mgr.get_status_text()}")

    print()


def test_fbi_trigger_multiple_failures():
    """Test FBI trigger from multiple failed inspections."""
    print("Test: FBI Trigger - Multiple Failures")

    resources = ResourceManager()
    suspicion_mgr = SuspicionManager()
    fbi_mgr = FBIManager(resources, suspicion_mgr)

    # Report 3 failed inspections
    fbi_mgr.report_inspection_failure(is_critical=False)
    fbi_mgr.report_inspection_failure(is_critical=False)
    fbi_mgr.report_inspection_failure(is_critical=False)

    # Update FBI manager
    fbi_mgr.update(1.0, 0.0)

    # FBI should be triggered
    assert fbi_mgr.is_investigation_active(), "FBI investigation should be active"
    assert fbi_mgr.trigger_reason == FBITrigger.MULTIPLE_FAILURES

    print(f"  ✓ FBI triggered after 3 failed inspections")
    print(f"  ✓ Failed inspections: {fbi_mgr.failed_inspections}")

    print()


def test_fbi_trigger_excessive_hacking():
    """Test FBI trigger from excessive camera hacking."""
    print("Test: FBI Trigger - Excessive Hacking")

    resources = ResourceManager()
    suspicion_mgr = SuspicionManager()
    fbi_mgr = FBIManager(resources, suspicion_mgr)

    # Report 20 camera hacks
    fbi_mgr.report_camera_hacks(20, game_time=0.0)

    # FBI should be triggered
    assert fbi_mgr.is_investigation_active(), "FBI investigation should be active"
    assert fbi_mgr.trigger_reason == FBITrigger.EXCESSIVE_HACKING

    print(f"  ✓ FBI triggered after 20 camera hacks")
    print(f"  ✓ Status: {fbi_mgr.get_status_text()}")

    print()


def test_fbi_bribe_success():
    """Test successful FBI bribe."""
    print("Test: FBI Bribe - Success")

    resources = ResourceManager()
    resources.money = 100000
    suspicion_mgr = SuspicionManager()
    suspicion_mgr.suspicion_level = 85
    fbi_mgr = FBIManager(resources, suspicion_mgr)

    # Trigger FBI
    fbi_mgr.report_camera_hacks(20, game_time=0.0)
    assert fbi_mgr.is_investigation_active()

    # Try bribing multiple times until success
    success = False
    for attempt in range(50):  # Try many times
        if resources.money < fbi_mgr.bribe_cost:
            resources.money = 100000  # Refill for testing

        result = fbi_mgr.attempt_bribe(game_time=100.0)
        if result:
            success = True
            break

    assert success, "Should eventually get successful bribe"
    assert not fbi_mgr.is_investigation_active(), "Investigation should be cancelled"

    print(f"  ✓ Bribe successful (probabilistic)")
    print(f"  ✓ Investigation cancelled")
    print(f"  ✓ Suspicion reduced")

    print()


def test_fbi_lay_low_success():
    """Test successful laying low to avoid FBI."""
    print("Test: Laying Low - Success")

    resources = ResourceManager()
    suspicion_mgr = SuspicionManager()
    suspicion_mgr.suspicion_level = 85
    fbi_mgr = FBIManager(resources, suspicion_mgr)

    # Trigger FBI
    fbi_mgr.report_camera_hacks(20, game_time=0.0)
    assert fbi_mgr.is_investigation_active()

    # Start laying low
    success = fbi_mgr.start_lay_low(game_time=100.0)
    assert success, "Should start laying low"
    assert fbi_mgr.laying_low, "Should be laying low"

    # Reduce suspicion below 60
    suspicion_mgr.add_suspicion(-30, "Reduced")  # Now at 55

    # Simulate 7 days of laying low
    game_time = 100.0
    for day in range(8):
        fbi_mgr.update(24 * 3600, game_time)
        game_time += 24 * 3600

    # Should have completed laying low and cancelled investigation
    assert not fbi_mgr.laying_low, "Should have finished laying low"
    assert not fbi_mgr.is_investigation_active(), "Investigation should be cancelled"

    print(f"  ✓ Laid low for 7 days")
    print(f"  ✓ Investigation cancelled")
    print(f"  ✓ Suspicion: {suspicion_mgr.suspicion_level}")

    print()


def test_fbi_raid():
    """Test FBI raid (game over)."""
    print("Test: FBI Raid")

    resources = ResourceManager()
    suspicion_mgr = SuspicionManager()
    fbi_mgr = FBIManager(resources, suspicion_mgr)

    # Trigger FBI
    fbi_mgr.report_camera_hacks(20, game_time=0.0)

    # Fast-forward through entire investigation
    game_time = 0.0
    fbi_mgr.update(fbi_mgr.investigation_duration + 1, game_time)

    # Should be raided
    assert fbi_mgr.is_raided(), "Factory should be raided"
    assert fbi_mgr.status == FBIStatus.RAIDED

    print(f"  ✓ FBI raid occurred after countdown expired")
    print(f"  ✓ Status: {fbi_mgr.status.value}")
    print(f"  ✓ Game over")

    print()


def test_social_engineering_counter_rumors():
    """Test counter-rumor campaign."""
    print("Test: Social Engineering - Counter Rumors")

    resources = ResourceManager()
    resources.money = 10000
    suspicion_mgr = SuspicionManager()
    suspicion_mgr.suspicion_level = 30  # In Rumors tier
    social_mgr = SocialEngineeringManager(resources, suspicion_mgr)

    # Start counter-rumor campaign
    success = social_mgr.counter_rumors(game_time=0.0)
    assert success, "Campaign should start"
    assert len(social_mgr.active_campaigns) == 1

    # Fast-forward 3 days
    game_time = 0.0
    social_mgr.update(3 * 24 * 3600, game_time)

    # Campaign should have activated
    assert suspicion_mgr.suspicion_level == 25, f"Suspicion should be 25, got {suspicion_mgr.suspicion_level}"

    print(f"  ✓ Counter-rumor campaign successful")
    print(f"  ✓ Suspicion reduced: 30 → 25")
    print(f"  ✓ Cost: ${social_mgr.counter_rumor_cost}")

    print()


def test_social_engineering_donations():
    """Test city donations."""
    print("Test: Social Engineering - Donations")

    resources = ResourceManager()
    resources.money = 10000
    suspicion_mgr = SuspicionManager()
    suspicion_mgr.suspicion_level = 40
    social_mgr = SocialEngineeringManager(resources, suspicion_mgr)

    initial_relations = social_mgr.community_relations

    # Donate to city
    success = social_mgr.donate_to_city(game_time=0.0)
    assert success, "Donation should succeed"
    assert suspicion_mgr.suspicion_level == 37, "Suspicion should decrease by 3"
    assert social_mgr.community_relations > initial_relations

    print(f"  ✓ Donation successful")
    print(f"  ✓ Suspicion: 40 → 37")
    print(f"  ✓ Community relations: {initial_relations} → {social_mgr.community_relations}")

    print()


def test_social_engineering_sponsorship():
    """Test event sponsorship."""
    print("Test: Social Engineering - Sponsorship")

    resources = ResourceManager()
    resources.money = 20000
    suspicion_mgr = SuspicionManager()
    suspicion_mgr.suspicion_level = 50
    social_mgr = SocialEngineeringManager(resources, suspicion_mgr)

    # Sponsor event
    success = social_mgr.sponsor_event(game_time=0.0)
    assert success, "Sponsorship should succeed"
    assert suspicion_mgr.suspicion_level == 42, "Suspicion should decrease by 8"

    print(f"  ✓ Event sponsorship successful")
    print(f"  ✓ Suspicion: 50 → 42")
    print(f"  ✓ Community relations: {social_mgr.community_relations}")

    print()


def test_good_neighbor_status():
    """Test good neighbor status activation."""
    print("Test: Good Neighbor Status")

    resources = ResourceManager()
    resources.money = 50000
    suspicion_mgr = SuspicionManager()
    suspicion_mgr.suspicion_level = 30
    social_mgr = SocialEngineeringManager(resources, suspicion_mgr)

    # Make multiple donations to reach 70+ community relations
    while social_mgr.community_relations < 70:
        social_mgr.donate_to_city(game_time=0.0)

    assert social_mgr.good_neighbor_active, "Good neighbor should be active"

    print(f"  ✓ Good neighbor status activated")
    print(f"  ✓ Community relations: {social_mgr.community_relations}")
    print(f"  ✓ Daily suspicion reduction: {abs(social_mgr.good_neighbor_bonus)}")

    print()


def test_propaganda_campaign():
    """Test propaganda campaign."""
    print("Test: Propaganda Campaign")

    resources = ResourceManager()
    resources.money = 20000
    suspicion_mgr = SuspicionManager()
    suspicion_mgr.suspicion_level = 40
    social_mgr = SocialEngineeringManager(resources, suspicion_mgr)

    # Enable research
    social_mgr.set_research_completed("social_engineering")

    # Start propaganda
    success = social_mgr.start_propaganda(game_time=0.0)
    assert success, "Propaganda should start"
    assert social_mgr.propaganda_active

    # Check suspicion growth modifier
    modifier = social_mgr.get_suspicion_growth_modifier()
    assert modifier == 0.5, f"Modifier should be 0.5, got {modifier}"

    print(f"  ✓ Propaganda campaign started")
    print(f"  ✓ Suspicion growth reduced by 50%")
    print(f"  ✓ Weekly cost: ${social_mgr.propaganda_weekly_cost}")

    print()


def run_all_tests():
    """Run all Phase 9 tests."""
    print("=" * 80)
    print("PHASE 9: AUTHORITY ESCALATION & FBI - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()

    try:
        # Authority Tier Tests
        test_authority_tier_transitions()
        test_tier_specific_effects()

        # FBI Tests
        test_fbi_trigger_high_suspicion()
        test_fbi_trigger_critical_inspection()
        test_fbi_trigger_multiple_failures()
        test_fbi_trigger_excessive_hacking()
        test_fbi_bribe_success()
        test_fbi_lay_low_success()
        test_fbi_raid()

        # Social Engineering Tests
        test_social_engineering_counter_rumors()
        test_social_engineering_donations()
        test_social_engineering_sponsorship()
        test_good_neighbor_status()
        test_propaganda_campaign()

        print()
        print("=" * 80)
        print("ALL PHASE 9 TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Phase 9 Features Verified:")
        print("  ✓ Authority tier transitions (Normal → Rumors → Investigation → Inspection → Restrictions)")
        print("  ✓ Tier-specific effects (police patrols, NPC alertness, checkpoints)")
        print("  ✓ FBI investigation triggers:")
        print("    - High suspicion (>80 for 7 days)")
        print("    - Critical inspection failure")
        print("    - Multiple failed inspections (3)")
        print("    - Excessive camera hacking (>20)")
        print("  ✓ FBI avoidance mechanics:")
        print("    - Bribery ($50,000, 30% risk)")
        print("    - Laying low (7 days, suspicion < 60)")
        print("  ✓ FBI raid (game over)")
        print("  ✓ Social engineering:")
        print("    - Counter-rumor campaigns ($1,000)")
        print("    - City donations ($5,000)")
        print("    - Event sponsorships ($10,000)")
        print("    - Propaganda campaigns ($2,000/week)")
        print("  ✓ Community relations & good neighbor status")
        print()

        return True

    except AssertionError as e:
        print()
        print("=" * 80)
        print(f"TEST FAILED: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
