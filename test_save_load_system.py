"""
Test Suite for Phase 13: Save/Load System

Tests:
1. SaveManager creation and initialization
2. Saving game state to file
3. Loading game state from file
4. Quick save/load functionality
5. Auto-save functionality
6. Multiple save slots
7. Save file listing and management
8. Data serialization and deserialization
"""

import sys
import os
import json
import time

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.systems.save_manager import SaveManager


def test_save_manager_init():
    """Test SaveManager initialization."""
    print("\n=== Test 1: SaveManager Initialization ===")

    save_manager = SaveManager()

    assert save_manager is not None, "SaveManager should be created"
    assert save_manager.SAVE_VERSION == "1.0", "Save version should be 1.0"
    assert os.path.exists(save_manager.SAVE_DIRECTORY), "Save directory should exist"
    assert save_manager.auto_save_enabled == True, "Auto-save should be enabled by default"

    print("✓ SaveManager initialized successfully")
    print(f"  - Save directory: {save_manager.SAVE_DIRECTORY}")
    print(f"  - Save version: {save_manager.SAVE_VERSION}")
    print(f"  - Auto-save enabled: {save_manager.auto_save_enabled}")
    return True


def test_save_game():
    """Test saving game state."""
    print("\n=== Test 2: Save Game ===")

    save_manager = SaveManager()

    # Create test game state
    test_state = {
        "time": {"day": 5, "hour": 14, "minute": 30},
        "resources": {"money": 5000, "materials": {"plastic": 100}},
        "buildings": [{"type": "factory", "x": 50, "y": 50}],
        "robots": [{"id": 1, "x": 100, "y": 100}]
    }

    # Save the game
    success = save_manager.save_game(test_state, "test_save")

    assert success == True, "Save should succeed"

    # Verify file exists
    save_path = save_manager._get_save_path("test_save")
    assert os.path.exists(save_path), f"Save file should exist at {save_path}"

    # Verify file contents
    with open(save_path, 'r') as f:
        saved_data = json.load(f)

    assert saved_data["version"] == "1.0", "Version should be saved"
    assert saved_data["save_name"] == "test_save", "Save name should be saved"
    assert "timestamp" in saved_data, "Timestamp should be saved"
    assert saved_data["game_state"]["time"]["day"] == 5, "Game state should be saved correctly"

    print("✓ Game saved successfully")
    print(f"  - File: {save_path}")
    print(f"  - Size: {os.path.getsize(save_path)} bytes")

    # Cleanup
    os.remove(save_path)
    return True


def test_load_game():
    """Test loading game state."""
    print("\n=== Test 3: Load Game ===")

    save_manager = SaveManager()

    # Create and save test game state
    test_state = {
        "time": {"day": 10, "hour": 8, "minute": 15},
        "resources": {"money": 12345, "materials": {"metal": 500}},
        "buildings": [],
        "robots": [{"id": 1, "x": 200, "y": 200}, {"id": 2, "x": 300, "y": 300}]
    }

    save_manager.save_game(test_state, "test_load")

    # Load the game
    loaded_state = save_manager.load_game("test_load")

    assert loaded_state is not None, "Load should succeed"
    assert loaded_state["time"]["day"] == 10, "Day should be loaded correctly"
    assert loaded_state["resources"]["money"] == 12345, "Money should be loaded correctly"
    assert len(loaded_state["robots"]) == 2, "Robots should be loaded correctly"

    print("✓ Game loaded successfully")
    print(f"  - Day: {loaded_state['time']['day']}")
    print(f"  - Money: ${loaded_state['resources']['money']}")
    print(f"  - Robots: {len(loaded_state['robots'])}")

    # Cleanup
    save_path = save_manager._get_save_path("test_load")
    os.remove(save_path)
    return True


def test_quick_save_load():
    """Test quick save/load functionality."""
    print("\n=== Test 4: Quick Save/Load ===")

    save_manager = SaveManager()

    # Create test state
    test_state = {
        "time": {"day": 3, "hour": 20, "minute": 45},
        "resources": {"money": 7777},
        "robots": []
    }

    # Quick save
    success = save_manager.quick_save(test_state)
    assert success == True, "Quick save should succeed"

    # Verify quicksave file exists
    quicksave_path = save_manager._get_save_path(save_manager.QUICK_SAVE_NAME)
    assert os.path.exists(quicksave_path), "Quicksave file should exist"

    # Quick load
    loaded_state = save_manager.quick_load()
    assert loaded_state is not None, "Quick load should succeed"
    assert loaded_state["time"]["day"] == 3, "Quick load should restore correct state"
    assert loaded_state["resources"]["money"] == 7777, "Quick load should restore money"

    print("✓ Quick save/load successful")
    print(f"  - Quick save file: {quicksave_path}")

    # Cleanup
    os.remove(quicksave_path)
    return True


def test_auto_save():
    """Test auto-save functionality."""
    print("\n=== Test 5: Auto-Save ===")

    save_manager = SaveManager()
    save_manager.auto_save_interval_days = 2  # Auto-save every 2 days

    # Create test state
    test_state = {
        "time": {"day": 1, "hour": 0, "minute": 0},
        "resources": {"money": 1000}
    }

    # Day 1 - should not auto-save (not enough days passed)
    result = save_manager.auto_save(test_state, current_day=1)
    assert result == False, "Should not auto-save on day 1"

    # Day 2 - should auto-save (2 days passed since day 0)
    test_state["time"]["day"] = 2
    result = save_manager.auto_save(test_state, current_day=2)
    assert result == True, "Should auto-save on day 2 (interval reached)"

    # Day 3 - should not auto-save (only 1 day since last auto-save)
    test_state["time"]["day"] = 3
    result = save_manager.auto_save(test_state, current_day=3)
    assert result == False, "Should not auto-save on day 3 (too soon)"

    # Day 4 - should auto-save (2 days since last auto-save on day 2)
    test_state["time"]["day"] = 4
    result = save_manager.auto_save(test_state, current_day=4)
    assert result == True, "Should auto-save on day 4 (interval reached again)"

    # Verify autosave file exists
    autosave_path = save_manager._get_save_path(save_manager.AUTO_SAVE_NAME)
    assert os.path.exists(autosave_path), "Auto-save file should exist"

    print("✓ Auto-save working correctly")
    print(f"  - Auto-save interval: {save_manager.auto_save_interval_days} days")
    print(f"  - Last auto-save: Day {save_manager.last_auto_save_day}")

    # Cleanup
    os.remove(autosave_path)
    return True


def test_save_list():
    """Test getting list of save files."""
    print("\n=== Test 6: Save File Listing ===")

    save_manager = SaveManager()

    # Create multiple saves
    for i in range(3):
        test_state = {
            "time": {"day": i + 1, "hour": 0, "minute": 0},
            "resources": {"money": (i + 1) * 1000}
        }
        save_manager.save_game(test_state, f"test_save_{i}")
        time.sleep(0.1)  # Small delay to ensure different timestamps

    # Get save list
    saves = save_manager.get_save_list()

    assert len(saves) >= 3, "Should have at least 3 saves"

    print("✓ Save file listing working")
    print(f"  - Found {len(saves)} save files:")
    for save_info in saves[:5]:  # Show first 5
        print(f"    • {save_info['name']}")
        print(f"      Timestamp: {save_info.get('timestamp', 'N/A')}")
        if 'day' in save_info:
            print(f"      Day: {save_info['day']}, Money: ${save_info.get('money', 0)}")

    # Cleanup
    for i in range(3):
        save_path = save_manager._get_save_path(f"test_save_{i}")
        if os.path.exists(save_path):
            os.remove(save_path)

    return True


def test_delete_save():
    """Test deleting save files."""
    print("\n=== Test 7: Delete Save ===")

    save_manager = SaveManager()

    # Create a test save
    test_state = {"time": {"day": 1}}
    save_manager.save_game(test_state, "test_delete")

    # Verify it exists
    save_path = save_manager._get_save_path("test_delete")
    assert os.path.exists(save_path), "Save should exist before deletion"

    # Delete it
    success = save_manager.delete_save("test_delete")
    assert success == True, "Delete should succeed"
    assert not os.path.exists(save_path), "Save should not exist after deletion"

    print("✓ Save deletion working")

    return True


def test_serialization():
    """Test complex game state serialization."""
    print("\n=== Test 8: Complex State Serialization ===")

    save_manager = SaveManager()

    # Create complex game state
    complex_state = {
        "time": {"day": 42, "hour": 15, "minute": 23, "time_speed": 1.5},
        "resources": {
            "money": 99999.50,
            "materials": {
                "plastic": 1234,
                "metal": 5678,
                "glass": 910,
                "paper": 1112
            }
        },
        "buildings": [
            {"id": 1, "type": "factory", "x": 50, "y": 50, "level": 3},
            {"id": 2, "type": "warehouse", "x": 100, "y": 100, "level": 1},
            {"id": 3, "type": "solar_array", "x": 150, "y": 150, "level": 2}
        ],
        "robots": [
            {"id": 1, "x": 200, "y": 200, "battery": 85, "state": "collecting"},
            {"id": 2, "x": 300, "y": 300, "battery": 100, "state": "returning"}
        ],
        "research": {
            "completed": ["speed_1", "capacity_1", "battery_1"],
            "current": "speed_2",
            "progress": 1234.5
        },
        "suspicion": {
            "level": 45.7,
            "sources": {"illegal_materials": 20, "hacked_cameras": 15}
        },
        "stats": {
            "materials_collected": 50000,
            "money_earned": 125000,
            "buildings_built": 25
        }
    }

    # Save
    success = save_manager.save_game(complex_state, "test_complex")
    assert success == True, "Complex save should succeed"

    # Load
    loaded = save_manager.load_game("test_complex")
    assert loaded is not None, "Complex load should succeed"

    # Verify deep equality
    assert loaded["time"]["day"] == 42, "Day should match"
    assert loaded["resources"]["money"] == 99999.50, "Money should match"
    assert len(loaded["buildings"]) == 3, "Buildings count should match"
    assert len(loaded["robots"]) == 2, "Robots count should match"
    assert len(loaded["research"]["completed"]) == 3, "Completed research should match"
    assert loaded["suspicion"]["level"] == 45.7, "Suspicion level should match"
    assert loaded["stats"]["materials_collected"] == 50000, "Stats should match"

    print("✓ Complex state serialization working")
    print(f"  - Time: Day {loaded['time']['day']}, {loaded['time']['hour']}:{loaded['time']['minute']:02d}")
    print(f"  - Money: ${loaded['resources']['money']:.2f}")
    print(f"  - Buildings: {len(loaded['buildings'])}")
    print(f"  - Robots: {len(loaded['robots'])}")
    print(f"  - Research completed: {len(loaded['research']['completed'])}")
    print(f"  - Suspicion: {loaded['suspicion']['level']}")

    # Cleanup
    save_path = save_manager._get_save_path("test_complex")
    os.remove(save_path)

    return True


def run_all_tests():
    """Run all save/load system tests."""
    print("=" * 80)
    print("PHASE 13: SAVE/LOAD SYSTEM - TEST SUITE")
    print("=" * 80)

    tests = [
        ("SaveManager Initialization", test_save_manager_init),
        ("Save Game", test_save_game),
        ("Load Game", test_load_game),
        ("Quick Save/Load", test_quick_save_load),
        ("Auto-Save", test_auto_save),
        ("Save File Listing", test_save_list),
        ("Delete Save", test_delete_save),
        ("Complex State Serialization", test_serialization)
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"\n✗ {name} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ {name} ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n✓ ALL TESTS PASSED!")
        print("\nPhase 13.1 Save System Architecture - COMPLETE")
        print("\nFeatures Verified:")
        print("  ✓ SaveManager initialization and configuration")
        print("  ✓ Game state serialization to JSON")
        print("  ✓ Save to file with metadata (version, timestamp)")
        print("  ✓ Load from file with validation")
        print("  ✓ Quick save/load to dedicated slot")
        print("  ✓ Auto-save based on game day intervals")
        print("  ✓ Multiple save slot support")
        print("  ✓ Save file listing and management")
        print("  ✓ Save file deletion")
        print("  ✓ Complex game state handling")
        return 0
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
