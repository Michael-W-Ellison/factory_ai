"""
Comprehensive tests for the Research System (Phase 6).

Tests research loading, prerequisites, progress, completion, and effects.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.systems.research_manager import ResearchManager


def test_research_loading():
    """Test that research tree loads from JSON."""
    print("Testing research tree loading...")

    manager = ResearchManager()

    # Verify research loaded
    assert len(manager.research_tree) > 0, "Research tree should not be empty"

    print(f"  ✓ Loaded {len(manager.research_tree)} technologies")

    # Test get_research
    legs_1 = manager.get_research('legs_1')
    assert legs_1 is not None, "Should find legs_1 research"
    assert legs_1['name'] == 'Legs Tier 1'
    assert legs_1['cost'] == 500
    assert legs_1['time'] == 30
    assert legs_1['prerequisites'] == []

    print(f"  ✓ Research data structure correct")
    print(f"  ✓ Sample research: {legs_1['name']} - ${legs_1['cost']}")
    print()


def test_research_prerequisites():
    """Test prerequisite checking."""
    print("Testing research prerequisites...")

    manager = ResearchManager()

    # legs_1 has no prerequisites, should be available
    assert manager.is_available('legs_1'), "legs_1 should be available (no prereqs)"

    # legs_2 requires legs_1, should not be available yet
    assert not manager.is_available('legs_2'), "legs_2 should not be available (requires legs_1)"

    # Complete legs_1
    manager.completed_research.add('legs_1')
    manager._complete_research('legs_1')  # Apply effects

    # Now legs_2 should be available
    assert manager.is_available('legs_2'), "legs_2 should be available after completing legs_1"

    # legs_3 requires both legs_2 and frames_2
    assert not manager.is_available('legs_3'), "legs_3 should not be available (missing prereqs)"

    # Complete legs_2 and frames_2
    manager.completed_research.add('legs_2')
    manager.completed_research.add('frames_2')

    # Now legs_3 should be available
    assert manager.is_available('legs_3'), "legs_3 should be available after completing all prereqs"

    print(f"  ✓ Prerequisite checking works correctly")
    print(f"  ✓ Complex prerequisites (multiple prereqs) work")
    print()


def test_research_affordability():
    """Test affordability checking."""
    print("Testing research affordability...")

    manager = ResearchManager()

    # legs_1 costs $500
    assert manager.can_afford('legs_1', 1000), "Should be able to afford legs_1 with $1000"
    assert manager.can_afford('legs_1', 500), "Should be able to afford legs_1 with exactly $500"
    assert not manager.can_afford('legs_1', 400), "Should not be able to afford legs_1 with $400"

    # legs_5 costs $10000
    assert not manager.can_afford('legs_5', 5000), "Should not be able to afford legs_5 with $5000"
    assert manager.can_afford('legs_5', 15000), "Should be able to afford legs_5 with $15000"

    print(f"  ✓ Affordability checking works")
    print()


def test_research_start_and_cancel():
    """Test starting and cancelling research."""
    print("Testing research start and cancel...")

    manager = ResearchManager()

    # Try to start legs_1 with insufficient funds
    result = manager.start_research('legs_1', 100)
    assert not result, "Should not start research with insufficient funds"
    assert manager.current_research is None

    # Start legs_1 with sufficient funds
    result = manager.start_research('legs_1', 1000)
    assert result, "Should start research with sufficient funds"
    assert manager.current_research == 'legs_1'
    assert manager.research_progress == 0.0
    assert manager.research_time_required == 30.0

    print(f"  ✓ Started research: legs_1")

    # Try to start another research while one is in progress
    result = manager.start_research('motor_1', 1000)
    assert not result, "Should not start second research while one is in progress"
    assert manager.current_research == 'legs_1'

    print(f"  ✓ Cannot start multiple research simultaneously")

    # Cancel research
    cancelled = manager.cancel_research()
    assert cancelled == 'legs_1'
    assert manager.current_research is None
    assert manager.research_progress == 0.0

    print(f"  ✓ Cancelled research: {cancelled}")
    print()


def test_research_progress_and_completion():
    """Test research progress over time."""
    print("Testing research progress and completion...")

    manager = ResearchManager()

    # Start legs_1 (30 second research)
    manager.start_research('legs_1', 1000)

    # Update for 15 seconds (50% progress)
    manager.update(15.0)

    progress = manager.get_research_progress()
    assert 0.49 < progress < 0.51, f"Progress should be ~50%, got {progress:.2%}"

    print(f"  ✓ Progress after 15s: {progress:.1%}")

    # Research should not be complete yet
    assert manager.current_research == 'legs_1'
    assert 'legs_1' not in manager.completed_research

    # Update for another 20 seconds (total 35s, should complete)
    manager.update(20.0)

    # Research should be complete
    assert manager.current_research is None
    assert 'legs_1' in manager.completed_research

    print(f"  ✓ Research completed after 35s")

    # Check effects applied
    speed_multiplier = manager.get_effect_multiplier('robot_speed')
    assert speed_multiplier == 1.2, f"Should have 1.2x speed, got {speed_multiplier}"

    print(f"  ✓ Effect applied: robot_speed = {speed_multiplier}x")
    print()


def test_research_effects():
    """Test research effect accumulation."""
    print("Testing research effects...")

    manager = ResearchManager()

    # Complete legs_1 (20% speed boost)
    manager.completed_research.add('legs_1')
    manager._complete_research('legs_1')

    speed_1 = manager.get_effect_multiplier('robot_speed')
    assert speed_1 == 1.2

    print(f"  After legs_1: robot_speed = {speed_1}x")

    # Complete legs_2 (40% speed boost - replaces legs_1)
    manager.completed_research.add('legs_2')
    manager._complete_research('legs_2')

    speed_2 = manager.get_effect_multiplier('robot_speed')
    assert speed_2 == 1.4

    print(f"  After legs_2: robot_speed = {speed_2}x")

    # Complete motor_1 (25% capacity boost)
    manager.completed_research.add('motor_1')
    manager._complete_research('motor_1')

    capacity_1 = manager.get_effect_multiplier('robot_capacity')
    assert capacity_1 == 1.25

    print(f"  After motor_1: robot_capacity = {capacity_1}x")

    # Verify speed still correct
    assert manager.get_effect_multiplier('robot_speed') == 1.4

    print(f"  ✓ Multiple effects track independently")
    print()


def test_research_categories():
    """Test research category filtering."""
    print("Testing research categories...")

    manager = ResearchManager()

    # Get robot category research
    robot_research = manager.get_research_by_category('robot')
    assert len(robot_research) > 0, "Should have robot research"

    print(f"  Found {len(robot_research)} robot technologies")

    # Check that all returned research are in robot category
    for research in robot_research:
        assert research.get('category') == 'robot', f"Research {research['id']} should be in robot category"

    # Test other categories
    processing_research = manager.get_research_by_category('processing')
    print(f"  Found {len(processing_research)} processing technologies")

    power_research = manager.get_research_by_category('power')
    print(f"  Found {len(power_research)} power technologies")

    print(f"  ✓ Category filtering works correctly")
    print()


def test_available_research():
    """Test getting available research."""
    print("Testing available research listing...")

    manager = ResearchManager()

    # Initially, should have several available (those with no prereqs)
    available = manager.get_available_research()
    initial_count = len(available)

    assert initial_count > 0, "Should have some available research at start"
    print(f"  Initial available research: {initial_count}")

    # All should have no prerequisites or met prerequisites
    for research in available:
        prereqs = research.get('prerequisites', [])
        if prereqs:
            for prereq in prereqs:
                assert manager.is_completed(prereq), f"Prerequisite {prereq} should be completed"

    # Complete one research
    manager.completed_research.add('legs_1')
    manager._complete_research('legs_1')

    # Should have different available count (legs_1 no longer available, legs_2 now available)
    available_after = manager.get_available_research()
    print(f"  Available after completing legs_1: {len(available_after)}")

    # legs_1 should not be in available
    legs_1_available = any(r['id'] == 'legs_1' for r in available_after)
    assert not legs_1_available, "Completed research should not be available"

    # legs_2 should be in available
    legs_2_available = any(r['id'] == 'legs_2' for r in available_after)
    assert legs_2_available, "legs_2 should be available after completing legs_1"

    print(f"  ✓ Available research updates correctly")
    print()


def test_research_statistics():
    """Test research statistics."""
    print("Testing research statistics...")

    manager = ResearchManager()

    stats = manager.get_stats()

    print(f"  Total research: {stats['total_research']}")
    print(f"  Completed: {stats['completed']}")
    print(f"  Available: {stats['available']}")
    print(f"  In progress: {stats['in_progress']}")
    print(f"  Completion: {stats['completion_percentage']:.1f}%")

    assert stats['total_research'] > 100, "Should have over 100 technologies"
    assert stats['completed'] == 0, "Should have no completed research initially"
    assert stats['available'] > 0, "Should have some available research"
    assert not stats['in_progress'], "Should have no research in progress"
    assert stats['completion_percentage'] == 0.0

    # Complete some research
    for _ in range(10):
        available = manager.get_available_research()
        if available:
            tech_id = available[0]['id']
            manager.completed_research.add(tech_id)
            manager._complete_research(tech_id)

    stats_after = manager.get_stats()
    print(f"\n  After completing 10 research:")
    print(f"  Completed: {stats_after['completed']}")
    print(f"  Completion: {stats_after['completion_percentage']:.1f}%")

    assert stats_after['completed'] == 10
    assert stats_after['completion_percentage'] > 0

    print(f"  ✓ Statistics tracking works")
    print()


def test_save_load():
    """Test save and load functionality."""
    print("Testing save/load...")

    # Create manager and complete some research
    manager1 = ResearchManager()
    manager1.start_research('legs_1', 1000)
    manager1.update(15.0)  # Partial progress
    manager1.completed_research.add('motor_1')
    manager1._complete_research('motor_1')

    # Save state
    saved_data = manager1.to_dict()

    print(f"  Saved state with {len(saved_data['completed_research'])} completed")
    print(f"  Current research: {saved_data['current_research']}")
    print(f"  Progress: {saved_data['research_progress']:.1f}s")

    # Create new manager and load state
    manager2 = ResearchManager()
    manager2.from_dict(saved_data)

    # Verify state restored
    assert manager2.current_research == 'legs_1'
    assert manager2.research_progress == 15.0
    assert 'motor_1' in manager2.completed_research
    assert manager2.get_effect_multiplier('robot_capacity') == 1.25

    print(f"  ✓ State restored correctly")
    print()


def main():
    """Run all research system tests."""
    print("=" * 80)
    print("RESEARCH SYSTEM TESTS (Phase 6)")
    print("=" * 80)
    print()

    try:
        test_research_loading()
        test_research_prerequisites()
        test_research_affordability()
        test_research_start_and_cancel()
        test_research_progress_and_completion()
        test_research_effects()
        test_research_categories()
        test_available_research()
        test_research_statistics()
        test_save_load()

        print("=" * 80)
        print("ALL RESEARCH TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Research System Features:")
        print("  - 130+ technologies loaded from JSON")
        print("  - Prerequisite tracking and validation")
        print("  - Research progress over time")
        print("  - Effect application and tracking")
        print("  - Category filtering")
        print("  - Save/load support")
        print("  - Multiple effect types (speed, capacity, power, etc.)")
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
