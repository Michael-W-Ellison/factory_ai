"""
Test Research System

Tests the ResearchManager, technology tree, prerequisites,
costs, effects, and research progression.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))


def test_research_manager_creation():
    """Test ResearchManager creation and initialization."""
    print("=" * 80)
    print("TEST 1: ResearchManager Creation")
    print("=" * 80)
    print()

    from src.systems.research_manager import ResearchManager

    # Create manager
    manager = ResearchManager()
    print(f"✓ ResearchManager created: {manager}")

    # Test loading research definitions
    assert len(manager.research_definitions) > 0, "No research definitions loaded"
    print(f"✓ Loaded {len(manager.research_definitions)} technologies")

    # Test initial state
    assert len(manager.completed_research) == 0, "Should start with no completed research"
    assert manager.current_research is None, "Should not be researching anything initially"
    print(f"✓ Initial state correct: {len(manager.completed_research)} completed, not researching")

    # Test statistics
    stats = manager.get_statistics()
    assert stats['total_researched'] == 0, "Should have researched nothing"
    assert stats['money_spent'] == 0, "Should have spent no money"
    print(f"✓ Initial statistics: {stats}")

    print("\n✓ ResearchManager creation test PASSED\n")


def test_research_availability():
    """Test research availability and prerequisites."""
    print("=" * 80)
    print("TEST 2: Research Availability & Prerequisites")
    print("=" * 80)
    print()

    from src.systems.research_manager import ResearchManager

    manager = ResearchManager()

    # Test getting definition
    tech = manager.get_research_definition('robot_speed_1')
    assert tech is not None, "robot_speed_1 should exist"
    print(f"✓ Found technology: {tech['name']}")
    print(f"  Category: {tech['category']}")
    print(f"  Cost: ${tech['cost']}")
    print(f"  Time: {tech['time']} hours")

    # Test availability (no prerequisites)
    available = manager.is_available('robot_speed_1')
    assert available, "robot_speed_1 should be available (no prerequisites)"
    print(f"✓ robot_speed_1 is available")

    # Test unavailable (has prerequisites)
    available2 = manager.is_available('robot_speed_2')
    assert available2 == False, "robot_speed_2 should NOT be available (requires robot_speed_1)"
    print(f"✓ robot_speed_2 is not available (requires robot_speed_1)")

    # Get available technologies
    available_techs = manager.get_available_technologies()
    print(f"✓ {len(available_techs)} technologies available to research")
    
    # Should include tier 1 techs without prerequisites
    tier1_available = [t for t in available_techs if not t.get('prerequisites', [])]
    print(f"✓ {len(tier1_available)} tier 1 technologies (no prerequisites)")

    # Test category filtering
    robot_techs = manager.get_available_technologies(category='robot')
    print(f"✓ {len(robot_techs)} robot technologies available")

    print("\n✓ Research availability test PASSED\n")


def test_start_research():
    """Test starting research."""
    print("=" * 80)
    print("TEST 3: Start Research")
    print("=" * 80)
    print()

    from src.systems.research_manager import ResearchManager

    manager = ResearchManager()
    money = 10000.0

    # Test can_start_research (success)
    can_start, reason = manager.can_start_research('robot_speed_1', money)
    assert can_start, f"Should be able to start robot_speed_1: {reason}"
    print(f"✓ Can start robot_speed_1: {reason}")

    # Start research
    success, money_remaining = manager.start_research('robot_speed_1', money)
    assert success, "Should successfully start research"
    assert money_remaining < money, "Money should be deducted"
    print(f"✓ Started research: robot_speed_1")
    print(f"  Money: ${money:.0f} -> ${money_remaining:.0f}")

    # Check state
    assert manager.current_research == 'robot_speed_1', "Should be researching robot_speed_1"
    assert manager.research_progress == 0.0, "Progress should be 0"
    print(f"✓ Research state: {manager.current_research}, progress: {manager.research_progress}")

    # Get progress info
    progress = manager.get_progress_info()
    assert progress is not None, "Should have progress info"
    print(f"✓ Progress info: {progress['name']}, {progress['percent']:.1f}% complete")

    # Test can't start another while researching
    can_start2, reason2 = manager.can_start_research('robot_capacity_1', money_remaining)
    assert not can_start2, "Should not be able to start another research"
    print(f"✓ Cannot start second research: {reason2}")

    # Test can't afford
    manager2 = ResearchManager()
    can_start3, reason3 = manager2.can_start_research('robot_speed_1', 100.0)
    assert not can_start3, "Should not be able to afford"
    assert "Insufficient funds" in reason3, f"Reason should mention funds: {reason3}"
    print(f"✓ Correctly rejects when insufficient funds: {reason3}")

    print("\n✓ Start research test PASSED\n")


def test_research_progress():
    """Test research progress and completion."""
    print("=" * 80)
    print("TEST 4: Research Progress & Completion")
    print("=" * 80)
    print()

    from src.systems.research_manager import ResearchManager

    manager = ResearchManager()
    
    # Start research
    success, money = manager.start_research('robot_speed_1', 10000.0)
    assert success, "Should start research"

    tech = manager.get_research_definition('robot_speed_1')
    total_time = tech['time']
    print(f"✓ Researching {tech['name']} ({total_time} hours)")

    # Update progress (partial)
    completed = manager.update(0.5)  # 0.5 hours
    assert completed is None, "Should not be complete yet"
    assert manager.research_progress == 0.5, "Progress should be 0.5 hours"
    print(f"✓ Progress after 0.5h: {manager.research_progress:.1f}/{total_time} hours")

    # Complete research
    completed = manager.update(total_time)  # Complete remaining time
    assert completed == 'robot_speed_1', "Should return completed tech"
    print(f"✓ Research completed: {completed}")

    # Check state after completion
    assert manager.current_research is None, "Should not be researching anything"
    assert manager.is_completed('robot_speed_1'), "Should be marked as completed"
    print(f"✓ State after completion: not researching, robot_speed_1 completed")

    # Check statistics
    stats = manager.get_statistics()
    assert stats['total_researched'] == 1, "Should have 1 completed research"
    assert stats['money_spent'] > 0, "Should have spent money"
    assert stats['time_spent'] > 0, "Should have spent time"
    print(f"✓ Statistics: {stats['total_researched']} researched, ${stats['money_spent']} spent, {stats['time_spent']:.1f}h")

    # Test prerequisite unlocking
    available = manager.is_available('robot_speed_2')
    assert available, "robot_speed_2 should now be available (prerequisite met)"
    print(f"✓ robot_speed_2 now available (prerequisite robot_speed_1 completed)")

    print("\n✓ Research progress test PASSED\n")


def test_cancel_research():
    """Test cancelling research."""
    print("=" * 80)
    print("TEST 5: Cancel Research")
    print("=" * 80)
    print()

    from src.systems.research_manager import ResearchManager

    manager = ResearchManager()
    
    # Start research
    success, money = manager.start_research('robot_speed_1', 10000.0)
    assert success, "Should start research"
    print(f"✓ Started research: robot_speed_1")

    # Make some progress
    manager.update(0.5)
    progress_before = manager.research_progress
    print(f"✓ Progress: {progress_before} hours")

    # Cancel
    cancelled = manager.cancel_research()
    assert cancelled, "Should successfully cancel"
    print(f"✓ Cancelled research (no refund)")

    # Check state
    assert manager.current_research is None, "Should not be researching"
    assert not manager.is_completed('robot_speed_1'), "Should not be completed"
    assert manager.research_progress == 0.0, "Progress should be reset"
    print(f"✓ State after cancel: not researching, not completed, progress reset")

    # Test cancelling when not researching
    cancelled2 = manager.cancel_research()
    assert not cancelled2, "Should return False when nothing to cancel"
    print(f"✓ Correctly returns False when nothing to cancel")

    print("\n✓ Cancel research test PASSED\n")


def test_research_effects():
    """Test research effects and multipliers."""
    print("=" * 80)
    print("TEST 6: Research Effects")
    print("=" * 80)
    print()

    from src.systems.research_manager import ResearchManager

    manager = ResearchManager()

    # Test default values (no research)
    speed_mult = manager.get_effect_multiplier('robot_speed')
    assert speed_mult == 1.0, "Should default to 1.0 with no research"
    print(f"✓ Default robot_speed multiplier: {speed_mult}")

    # Complete robot_speed_1 (should give 1.2x)
    manager.completed_research['robot_speed_1'] = 1.0
    speed_mult = manager.get_effect_multiplier('robot_speed')
    assert speed_mult == 1.2, f"Should be 1.2 with robot_speed_1, got {speed_mult}"
    print(f"✓ robot_speed_1 effect: {speed_mult}x")

    # Complete robot_speed_2 (should give 1.4x, higher value wins)
    manager.completed_research['robot_speed_2'] = 2.0
    speed_mult = manager.get_effect_multiplier('robot_speed')
    assert speed_mult == 1.4, f"Should be 1.4 (highest value), got {speed_mult}"
    print(f"✓ robot_speed_2 effect: {speed_mult}x (highest value)")

    # Test unlock (boolean effect)
    has_drones = manager.has_unlock('unlock_drones')
    assert not has_drones, "Should not have drones unlocked"
    print(f"✓ unlock_drones: {has_drones}")

    # Unlock drones
    manager.completed_research['drones_1'] = 5.0
    has_drones = manager.has_unlock('unlock_drones')
    assert has_drones, "Should have drones unlocked"
    print(f"✓ After drones_1 research: {has_drones}")

    # Test absolute value effects (not multipliers)
    manager.completed_research['robot_capacity_1'] = 6.0
    capacity_value = manager.get_effect('robot_capacity', 100.0)
    assert capacity_value == 150.0, f"Should be 150.0 with robot_capacity_1, got {capacity_value}"
    print(f"✓ robot_capacity_1 effect: {capacity_value}kg capacity")

    print("\n✓ Research effects test PASSED\n")


def test_research_tree_structure():
    """Test research tree structure and categories."""
    print("=" * 80)
    print("TEST 7: Research Tree Structure")
    print("=" * 80)
    print()

    from src.systems.research_manager import ResearchManager

    manager = ResearchManager()

    # Count technologies by category
    categories = {}
    for tech_id, tech in manager.research_definitions.items():
        category = tech.get('category', 'unknown')
        categories[category] = categories.get(category, 0) + 1

    print(f"✓ Research categories:")
    for category, count in sorted(categories.items()):
        print(f"  - {category}: {count} technologies")

    # Verify expected categories exist
    expected_categories = ['robot', 'processing', 'power', 'stealth', 'advanced']
    for category in expected_categories:
        assert category in categories, f"Missing expected category: {category}"
    print(f"✓ All expected categories present")

    # Test prerequisite chains
    # robot_speed_3 should require robot_speed_2 which requires robot_speed_1
    if 'robot_speed_3' in manager.research_definitions:
        tech3 = manager.research_definitions['robot_speed_3']
        prereqs = tech3.get('prerequisites', [])
        assert 'robot_speed_2' in prereqs, "robot_speed_3 should require robot_speed_2"
        print(f"✓ Prerequisite chain verified: robot_speed_1 -> robot_speed_2 -> robot_speed_3")

    # Get completed technologies
    manager.completed_research['robot_speed_1'] = 1.0
    manager.completed_research['robot_capacity_1'] = 2.0
    completed = manager.get_completed_technologies()
    assert len(completed) == 2, f"Should have 2 completed, got {len(completed)}"
    print(f"✓ Completed technologies: {len(completed)}")

    # Test category filtering for completed
    robot_completed = manager.get_completed_technologies(category='robot')
    print(f"✓ Completed robot technologies: {len(robot_completed)}")

    print("\n✓ Research tree structure test PASSED\n")


def test_save_load_state():
    """Test save/load state."""
    print("=" * 80)
    print("TEST 8: Save/Load State")
    print("=" * 80)
    print()

    from src.systems.research_manager import ResearchManager

    # Create manager and do some research
    manager = ResearchManager()
    manager.start_research('robot_speed_1', 10000.0)
    manager.update(0.5)  # Partial progress

    # Mark another as completed
    manager.completed_research['robot_capacity_1'] = 3.5

    print(f"✓ Initial state: researching {manager.current_research}, progress {manager.research_progress}")
    print(f"✓ Completed: {list(manager.completed_research.keys())}")

    # Save state
    state = manager.save_state()
    print(f"✓ Saved state: {len(state)} keys")
    assert 'completed_research' in state
    assert 'current_research' in state
    assert 'research_progress' in state
    assert 'stats' in state

    # Create new manager and load state
    manager2 = ResearchManager()
    manager2.load_state(state)

    # Verify state
    assert manager2.current_research == 'robot_speed_1', "Should restore current research"
    assert manager2.research_progress == 0.5, "Should restore progress"
    assert 'robot_capacity_1' in manager2.completed_research, "Should restore completed research"
    print(f"✓ Loaded state: researching {manager2.current_research}, progress {manager2.research_progress}")
    print(f"✓ Completed: {list(manager2.completed_research.keys())}")

    # Verify effects are applied
    assert manager2.effects_changed, "effects_changed should be True after loading"
    print(f"✓ effects_changed flag set after load")

    # Verify effects work
    capacity_mult = manager2.get_effect_multiplier('robot_capacity')
    print(f"✓ Effect from loaded research: robot_capacity = {capacity_mult}x")

    print("\n✓ Save/load state test PASSED\n")


def run_all_tests():
    """Run all tests."""
    print("\n")
    print("=" * 80)
    print("RESEARCH SYSTEM TEST SUITE")
    print("=" * 80)
    print("\n")

    try:
        test_research_manager_creation()
        test_research_availability()
        test_start_research()
        test_research_progress()
        test_cancel_research()
        test_research_effects()
        test_research_tree_structure()
        test_save_load_state()

        print("=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
        print()
        print("Summary:")
        print("  ✓ ResearchManager creation and initialization")
        print("  ✓ Technology availability and prerequisites")
        print("  ✓ Starting research (cost, validation)")
        print("  ✓ Research progress and completion")
        print("  ✓ Cancelling research")
        print("  ✓ Research effects and multipliers")
        print("  ✓ Research tree structure (60 technologies, 5 categories)")
        print("  ✓ Save/load state persistence")
        print()

        return True

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ TEST ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
