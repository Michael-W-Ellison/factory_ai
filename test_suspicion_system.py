"""
Tests for suspicion system.

Tests SuspicionManager, suspicion tiers, decay, and event tracking.
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.systems.suspicion_manager import SuspicionManager, SuspicionTier


def test_suspicion_manager_initialization():
    """Test SuspicionManager initialization."""
    print("Testing SuspicionManager initialization...")

    manager = SuspicionManager()

    assert manager.suspicion_level == 0.0
    assert manager.current_tier == SuspicionTier.NORMAL
    assert len(manager.suspicion_events) == 0
    assert len(manager.tier_changes) == 0

    print(f"  Initial level: {manager.suspicion_level}")
    print(f"  Initial tier: {manager.current_tier}")
    print(f"  Tiers: {list(manager.tier_thresholds.keys())}")
    print(f"  ✓ SuspicionManager initialized correctly")
    print()


def test_suspicion_tiers():
    """Test suspicion tier classification."""
    print("Testing suspicion tiers...")

    manager = SuspicionManager()

    tests = [
        (0, SuspicionTier.NORMAL),
        (10, SuspicionTier.NORMAL),
        (20, SuspicionTier.NORMAL),
        (21, SuspicionTier.RUMORS),
        (30, SuspicionTier.RUMORS),
        (40, SuspicionTier.RUMORS),
        (41, SuspicionTier.INVESTIGATION),
        (50, SuspicionTier.INVESTIGATION),
        (60, SuspicionTier.INVESTIGATION),
        (61, SuspicionTier.INSPECTION),
        (70, SuspicionTier.INSPECTION),
        (80, SuspicionTier.INSPECTION),
        (81, SuspicionTier.RESTRICTIONS),
        (90, SuspicionTier.RESTRICTIONS),
        (100, SuspicionTier.RESTRICTIONS),
    ]

    for level, expected_tier in tests:
        manager.suspicion_level = level
        tier = manager.get_current_tier()
        assert tier == expected_tier, f"Failed at level {level}"
        print(f"  Level {level:3d}: {tier}")

    print(f"  ✓ Suspicion tiers correct")
    print()


def test_add_suspicion():
    """Test adding suspicion."""
    print("Testing add suspicion...")

    manager = SuspicionManager()

    # Add small amount
    tier_changed = manager.add_suspicion(5.0, 'npc_detection', 'Test detection')
    assert manager.suspicion_level == 5.0
    assert not tier_changed  # Still in Normal tier
    assert len(manager.suspicion_events) == 1
    print(f"  After +5: level={manager.suspicion_level}, tier={manager.current_tier}")

    # Add more to cross into Rumors tier
    tier_changed = manager.add_suspicion(20.0, 'npc_detection', 'Another detection')
    assert manager.suspicion_level == 25.0
    assert tier_changed  # Should change to Rumors
    assert manager.current_tier == SuspicionTier.RUMORS
    assert len(manager.tier_changes) == 1
    print(f"  After +20: level={manager.suspicion_level}, tier={manager.current_tier}")

    print(f"  ✓ Add suspicion works correctly")
    print()


def test_suspicion_capping():
    """Test that suspicion caps at 100."""
    print("Testing suspicion capping...")

    manager = SuspicionManager()

    # Add way more than 100
    manager.add_suspicion(150.0, 'test', 'Overfill test')

    assert manager.suspicion_level == 100.0
    assert manager.current_tier == SuspicionTier.RESTRICTIONS
    print(f"  After +150: level={manager.suspicion_level} (capped at 100)")

    print(f"  ✓ Suspicion caps at 100")
    print()


def test_suspicion_decay():
    """Test suspicion decay over time."""
    print("Testing suspicion decay...")

    manager = SuspicionManager()

    # Start with some suspicion
    manager.add_suspicion(30.0, 'test', 'Initial suspicion')
    print(f"  Initial: level={manager.suspicion_level}")

    # Update for 1 game hour (should decay by 0.1 * time)
    # With 60x time scale: 60 real seconds = 1 game hour
    # dt * 60 / 3600 = game hours
    # For 60 seconds: 60 * 60 / 3600 = 1 hour
    manager.update(60.0, 12.0)  # 60 real seconds, noon

    # Should have decayed (roughly 0.1 per game hour)
    print(f"  After 60s: level={manager.suspicion_level:.2f}")
    assert manager.suspicion_level < 30.0

    print(f"  ✓ Suspicion decays correctly")
    print()


def test_suspicion_decay_stops():
    """Test that decay stops above threshold."""
    print("Testing suspicion decay stops at 60...")

    manager = SuspicionManager()

    # Set suspicion above decay threshold
    manager.suspicion_level = 70.0
    initial_level = manager.suspicion_level
    print(f"  Initial: level={manager.suspicion_level}")

    # Update - should not decay
    manager.update(60.0, 12.0)

    assert manager.suspicion_level == initial_level
    print(f"  After 60s: level={manager.suspicion_level} (no decay)")

    print(f"  ✓ Decay stops above 60")
    print()


def test_tier_transitions():
    """Test tier transitions and notifications."""
    print("Testing tier transitions...")

    manager = SuspicionManager()

    # Transition through tiers
    transitions = [
        (25, SuspicionTier.RUMORS),
        (45, SuspicionTier.INVESTIGATION),
        (65, SuspicionTier.INSPECTION),
        (85, SuspicionTier.RESTRICTIONS),
    ]

    for amount, expected_tier in transitions:
        current = manager.suspicion_level
        to_add = amount - current
        tier_changed = manager.add_suspicion(to_add, 'test', f'Transition to {expected_tier}')

        assert tier_changed
        assert manager.current_tier == expected_tier
        print(f"  Level {amount}: {expected_tier}")

    # Check tier change history
    assert len(manager.tier_changes) == 4
    print(f"  Total tier changes: {len(manager.tier_changes)}")

    print(f"  ✓ Tier transitions work correctly")
    print()


def test_detection_report_processing():
    """Test processing detection reports."""
    print("Testing detection report processing...")

    manager = SuspicionManager()

    # Create a mock detection report
    report = {
        'suspicion_increase': 15.0,
        'detection_level': 'report',
        'npc': None,
        'robot': None,
        'time': 12.0,
        'location': (100, 100),
    }

    tier_changed = manager.process_detection_report(report)

    assert manager.suspicion_level == 15.0
    assert not tier_changed  # Still in Normal
    assert len(manager.suspicion_events) == 1

    event = manager.suspicion_events[0]
    assert event['source'] == 'npc_detection'
    assert event['amount'] == 15.0
    print(f"  After report: level={manager.suspicion_level}")
    print(f"  Event recorded: {event['description']}")

    print(f"  ✓ Detection report processing works")
    print()


def test_suspicion_events_history():
    """Test suspicion events history."""
    print("Testing suspicion events history...")

    manager = SuspicionManager()

    # Add multiple suspicion events
    for i in range(5):
        manager.add_suspicion(2.0, f'source_{i}', f'Event {i}')

    # Get recent events
    recent = manager.get_recent_events(3)

    assert len(recent) == 3
    assert recent[-1]['amount'] == 2.0
    assert 'Event 4' in recent[-1]['description']
    print(f"  Total events: {len(manager.suspicion_events)}")
    print(f"  Recent 3: {[e['description'] for e in recent]}")

    print(f"  ✓ Events history works correctly")
    print()


def test_tier_consequences():
    """Test tier consequences."""
    print("Testing tier consequences...")

    manager = SuspicionManager()

    # Test each tier's consequences
    tiers_to_test = [
        (0, SuspicionTier.NORMAL),
        (25, SuspicionTier.RUMORS),
        (45, SuspicionTier.INVESTIGATION),
        (65, SuspicionTier.INSPECTION),
        (85, SuspicionTier.RESTRICTIONS),
    ]

    for level, tier in tiers_to_test:
        manager.suspicion_level = level
        manager.current_tier = tier
        consequences = manager.get_tier_consequences()

        assert len(consequences) > 0
        print(f"  {tier}: {len(consequences)} consequences")
        for consequence in consequences:
            print(f"    - {consequence}")

    print(f"  ✓ Tier consequences defined")
    print()


def test_tier_progress():
    """Test tier progress calculation."""
    print("Testing tier progress...")

    manager = SuspicionManager()

    # Test progress within Normal tier (0-20)
    manager.suspicion_level = 10.0
    progress = manager.get_tier_progress()
    expected = 10.0 / 21.0  # (10 - 0) / (21 - 0)
    assert abs(progress - expected) < 0.01
    print(f"  Level 10 in Normal tier: {progress:.1%} progress")

    # Test progress within Rumors tier (21-40)
    manager.suspicion_level = 30.0
    manager.current_tier = SuspicionTier.RUMORS
    progress = manager.get_tier_progress()
    expected = (30.0 - 21.0) / (41.0 - 21.0)  # 9 / 20 = 0.45
    assert abs(progress - expected) < 0.01
    print(f"  Level 30 in Rumors tier: {progress:.1%} progress")

    print(f"  ✓ Tier progress calculation works")
    print()


def test_suspicion_stats():
    """Test suspicion statistics."""
    print("Testing suspicion statistics...")

    manager = SuspicionManager()

    # Add some suspicion
    manager.add_suspicion(35.0, 'test', 'Test event')

    stats = manager.get_stats()

    assert stats['level'] == 35.0
    assert stats['tier'] == SuspicionTier.RUMORS
    assert stats['tier_name'] == 'Rumors'
    assert stats['total_events'] == 1
    assert stats['tier_changes'] == 1
    assert stats['decaying'] == True

    print(f"  Level: {stats['level']}")
    print(f"  Tier: {stats['tier_name']}")
    print(f"  Total events: {stats['total_events']}")
    print(f"  Tier changes: {stats['tier_changes']}")
    print(f"  Decaying: {stats['decaying']}")

    print(f"  ✓ Suspicion statistics correct")
    print()


def main():
    """Run all tests."""
    print("=" * 80)
    print("SUSPICION SYSTEM TESTS")
    print("=" * 80)
    print()

    try:
        test_suspicion_manager_initialization()
        test_suspicion_tiers()
        test_add_suspicion()
        test_suspicion_capping()
        test_suspicion_decay()
        test_suspicion_decay_stops()
        test_tier_transitions()
        test_detection_report_processing()
        test_suspicion_events_history()
        test_tier_consequences()
        test_tier_progress()
        test_suspicion_stats()

        print("=" * 80)
        print("ALL SUSPICION SYSTEM TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Phase 7.8 Features Implemented:")
        print()
        print("SUSPICION MANAGER:")
        print("  - Tracks suspicion level (0-100)")
        print("  - Manages suspicion tiers and transitions")
        print("  - Processes detection reports")
        print("  - Suspicion decay over time")
        print("  - Event history tracking")
        print()
        print("SUSPICION TIERS:")
        print("  - Normal (0-20): No effect")
        print("  - Rumors (21-40): Slight police increase")
        print("  - Investigation (41-60): Police attention")
        print("  - Inspection (61-80): Inspection scheduled")
        print("  - Restrictions (81-100): FBI/severe restrictions")
        print()
        print("SUSPICION MECHANICS:")
        print("  - Caps at 100 (cannot exceed)")
        print("  - Decays at -0.1 per game hour")
        print("  - Decay stops above level 60")
        print("  - Tier transitions logged")
        print("  - Consequences per tier")
        print()
        print("SUSPICION SOURCES:")
        print("  - NPC detection reports (+2 to +15)")
        print("  - Configurable for future sources")
        print("  - (Police, inspections, etc. can be added)")
        print()
        print("SUSPICION UI:")
        print("  - Meter at bottom-center of screen")
        print("  - Color-coded by tier:")
        print("    * Green (Normal)")
        print("    * Yellow (Rumors)")
        print("    * Orange (Investigation)")
        print("    * Dark Orange (Inspection)")
        print("    * Red (Restrictions)")
        print("  - Progress bar with tier markers")
        print("  - Shows level and tier name")
        print()
        print("INTEGRATION:")
        print("  - Integrated into game update loop")
        print("  - Processes detection reports automatically")
        print("  - Updates decay each frame")
        print("  - Displayed in HUD")
        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
