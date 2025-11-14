"""
Phase 11 Test Suite: UI/UX Polish
Tests menu system, notifications, settings, and HUD components.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui.menu_system import MenuSystem, MenuType, PauseMenu, BuildingMenu
from ui.notification_system import NotificationSystem, NotificationType, GameNotifications
from ui.settings_manager import SettingsManager
from ui.hud_components import HUDManager, ResourcePanel, PowerPanel, TimePanel, SuspicionMeter


def print_test_header(test_name):
    """Print test header."""
    print(f"\n{'=' * 80}")
    print(f"TEST: {test_name}")
    print('=' * 80)


def print_test_result(success, message=""):
    """Print test result."""
    if success:
        print(f"✓ PASS {message}")
    else:
        print(f"✗ FAIL {message}")
    return success


# ===== MENU SYSTEM TESTS =====

def test_menu_system_open_close():
    """Test menu opening and closing."""
    print_test_header("Menu System Open/Close")

    menu_system = MenuSystem()

    # Initially no menus
    assert not menu_system.is_any_menu_open(), "No menus should be open initially"

    # Open pause menu
    menu_system.open_menu(MenuType.PAUSE)
    assert menu_system.is_menu_open(MenuType.PAUSE), "Pause menu should be open"
    assert menu_system.game_paused, "Game should be paused"

    # Close menu
    menu_system.close_current_menu()
    assert not menu_system.is_any_menu_open(), "No menus should be open after close"
    assert not menu_system.game_paused, "Game should be unpaused"

    print("Opened and closed pause menu")
    print(f"Game paused state toggles correctly")

    return print_test_result(True, "- Menu open/close works")


def test_menu_system_stack():
    """Test menu stacking."""
    print_test_header("Menu System Stack")

    menu_system = MenuSystem()

    # Open multiple menus
    menu_system.open_menu(MenuType.PAUSE)
    menu_system.open_menu(MenuType.SETTINGS)

    stats = menu_system.get_stats()
    assert stats['menu_stack_depth'] == 2, "Should have 2 menus stacked"

    # Active menu should be settings
    active = menu_system.get_active_menu()
    assert active.menu_type == MenuType.SETTINGS, "Settings should be active"

    # Close one menu
    menu_system.close_current_menu()
    active = menu_system.get_active_menu()
    assert active.menu_type == MenuType.PAUSE, "Pause menu should be active again"

    print(f"Menu stack depth: {stats['menu_stack_depth']}")
    print("Menus stack and unstack correctly")

    return print_test_result(True, "- Menu stacking works")


def test_building_menu_categories():
    """Test building menu categories."""
    print_test_header("Building Menu Categories")

    menu = BuildingMenu()

    assert len(menu.categories) > 0, "Should have categories"

    # Test category switching
    initial_category = menu.get_current_category()
    menu.set_category(1)
    new_category = menu.get_current_category()

    assert new_category != initial_category, "Category should change"

    print(f"Categories: {menu.categories}")
    print(f"Switched from {initial_category} to {new_category}")

    return print_test_result(True, "- Building menu categories work")


# ===== NOTIFICATION SYSTEM TESTS =====

def test_notification_creation():
    """Test notification creation."""
    print_test_header("Notification Creation")

    notif_system = NotificationSystem()

    # Create notification
    notif = notif_system.info("Test message")

    assert notif.message == "Test message", "Message should match"
    assert notif.notification_type == NotificationType.INFO, "Type should be INFO"
    assert len(notif_system.get_active_notifications()) == 1, "Should have 1 active notification"

    print(f"Created notification: {notif.message}")
    print(f"Type: {notif.notification_type.value}")
    print(f"Active notifications: {len(notif_system.get_active_notifications())}")

    return print_test_result(True, "- Notification creation works")


def test_notification_priority():
    """Test notification priority."""
    print_test_header("Notification Priority")

    notif_system = NotificationSystem(max_visible=2)

    # Create low priority notification
    notif1 = notif_system.info("Low priority")

    # Create high priority notification
    notif2 = notif_system.error("High priority")

    active = notif_system.get_active_notifications()

    # Error should be first (higher priority)
    assert active[0].notification_type == NotificationType.ERROR, "Error should be first"

    print("Created low and high priority notifications")
    print(f"Order: {[n.notification_type.value for n in active]}")

    return print_test_result(True, "- Priority ordering works")


def test_notification_queue():
    """Test notification queuing."""
    print_test_header("Notification Queue")

    notif_system = NotificationSystem(max_visible=2)

    # Create 4 notifications (2 will queue)
    for i in range(4):
        notif_system.info(f"Message {i+1}")

    assert len(notif_system.get_active_notifications()) == 2, "Should have 2 active"
    assert notif_system.get_queue_length() == 2, "Should have 2 queued"

    print(f"Active: {len(notif_system.get_active_notifications())}")
    print(f"Queued: {notif_system.get_queue_length()}")

    return print_test_result(True, "- Notification queuing works")


def test_notification_auto_dismiss():
    """Test notification auto-dismiss."""
    print_test_header("Notification Auto-Dismiss")

    notif_system = NotificationSystem()

    # Create notification with short duration
    notif = notif_system.notify("Test", duration=1.0)

    # Update past duration
    notif_system.update(1.5)

    assert len(notif_system.get_active_notifications()) == 0, "Should be dismissed"
    assert len(notif_system.get_history()) == 1, "Should be in history"

    print("Notification auto-dismissed after duration")
    print(f"History count: {len(notif_system.get_history())}")

    return print_test_result(True, "- Auto-dismiss works")


def test_game_notifications_templates():
    """Test pre-configured notification templates."""
    print_test_header("Game Notification Templates")

    notif_system = NotificationSystem()

    # Test various templates
    GameNotifications.research_complete("Solar Array I", notif_system)
    GameNotifications.low_power(notif_system)
    GameNotifications.fbi_investigation(notif_system)

    assert len(notif_system.get_active_notifications()) == 3, "Should have 3 notifications"

    active = notif_system.get_active_notifications()
    types = [n.notification_type for n in active]

    print(f"Created {len(active)} template notifications")
    print(f"Types: {[t.value for t in types]}")

    return print_test_result(True, "- Notification templates work")


# ===== SETTINGS MANAGER TESTS =====

def test_settings_get_set():
    """Test settings get/set."""
    print_test_header("Settings Get/Set")

    settings = SettingsManager()

    # Get default value
    volume = settings.get('audio', 'master_volume')
    assert volume == 1.0, f"Default master volume should be 1.0, got {volume}"

    # Set new value
    success = settings.set('audio', 'master_volume', 0.5)
    assert success, "Should successfully set value"

    new_volume = settings.get('audio', 'master_volume')
    assert new_volume == 0.5, f"Volume should be 0.5, got {new_volume}"

    print(f"Initial volume: {volume}")
    print(f"After set: {new_volume}")

    return print_test_result(True, "- Settings get/set works")


def test_settings_validation():
    """Test settings validation."""
    print_test_header("Settings Validation")

    settings = SettingsManager()

    # Try to set invalid value (out of range)
    success = settings.set('audio', 'master_volume', 5.0)  # Max is 1.0
    assert not success, "Should reject out-of-range value"

    # Volume should remain unchanged
    volume = settings.get('audio', 'master_volume')
    assert volume == 1.0, "Volume should not have changed"

    # Try to set invalid difficulty
    success = settings.set('gameplay', 'difficulty', 'impossible')
    assert not success, "Should reject invalid difficulty"

    print("Invalid values correctly rejected")
    print(f"Volume still at: {volume}")

    return print_test_result(True, "- Settings validation works")


def test_settings_convenience_methods():
    """Test settings convenience methods."""
    print_test_header("Settings Convenience Methods")

    settings = SettingsManager()

    # Test resolution methods
    width, height = settings.get_resolution()
    assert width == 1280 and height == 720, "Default resolution should be 1280x720"

    settings.set_resolution(1920, 1080)
    new_width, new_height = settings.get_resolution()
    assert new_width == 1920 and new_height == 1080, "Resolution should update"

    # Test fullscreen toggle
    initial_fullscreen = settings.is_fullscreen()
    settings.toggle_fullscreen()
    assert settings.is_fullscreen() != initial_fullscreen, "Fullscreen should toggle"

    print(f"Resolution: {new_width}x{new_height}")
    print(f"Fullscreen toggled correctly")

    return print_test_result(True, "- Convenience methods work")


def test_settings_save_load():
    """Test settings save/load."""
    print_test_header("Settings Save/Load")

    import tempfile
    import os

    # Create temp file
    temp_file = tempfile.mktemp(suffix='.json')

    try:
        # Create settings and modify
        settings1 = SettingsManager(temp_file)
        settings1.set('audio', 'master_volume', 0.3)
        settings1.set('gameplay', 'difficulty', 'hard')

        # Save
        success = settings1.save_settings()
        assert success, "Should save successfully"
        assert os.path.exists(temp_file), "File should exist"

        # Load into new instance
        settings2 = SettingsManager(temp_file)
        volume = settings2.get('audio', 'master_volume')
        difficulty = settings2.get('gameplay', 'difficulty')

        assert volume == 0.3, f"Loaded volume should be 0.3, got {volume}"
        assert difficulty == 'hard', f"Loaded difficulty should be hard, got {difficulty}"

        print(f"Saved and loaded settings successfully")
        print(f"Volume: {volume}, Difficulty: {difficulty}")

        return print_test_result(True, "- Save/load works")

    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)


# ===== HUD COMPONENTS TESTS =====

def test_resource_panel():
    """Test resource panel."""
    print_test_header("Resource Panel")

    panel = ResourcePanel()

    # Mock resource manager
    class MockResourceManager:
        def __init__(self):
            self.money = 50000
            self.stored_materials = {'plastic': 1000, 'metal': 500}

        def get_total_stored_weight(self):
            return 1500

        def get_total_stored_value(self):
            return 10000

    resource_mgr = MockResourceManager()
    panel.update(resource_mgr)

    summary = panel.get_summary()
    assert summary['money'] == 50000, "Money should match"
    assert summary['total_weight'] == 1500, "Weight should match"

    print(f"Money: ${summary['money']:,}")
    print(f"Total weight: {summary['total_weight']}kg")

    return print_test_result(True, "- Resource panel works")


def test_power_panel():
    """Test power panel."""
    print_test_header("Power Panel")

    panel = PowerPanel()

    # Mock power manager
    class MockPowerManager:
        def __init__(self):
            self.total_generation = 100
            self.total_consumption = 80
            self.current_storage = 500
            self.max_storage = 1000

    power_mgr = MockPowerManager()
    panel.update(power_mgr)

    summary = panel.get_summary()
    assert summary['generation'] == 100, "Generation should match"
    assert summary['net_power'] == 20, "Net power should be 20"
    assert summary['status'] == "SURPLUS", "Status should be SURPLUS"

    print(f"Generation: {summary['generation']}")
    print(f"Consumption: {summary['consumption']}")
    print(f"Status: {summary['status']}")

    return print_test_result(True, "- Power panel works")


def test_time_panel():
    """Test time panel."""
    print_test_header("Time Panel")

    panel = TimePanel()

    # Set some values
    panel.day = 5
    panel.hour = 14
    panel.minute = 30

    assert panel.get_time_string() == "14:30", "Time string should match"
    assert panel.get_day_string() == "Day 5", "Day string should match"

    # Test speed control
    initial_speed = panel.speed
    panel.increase_speed()
    assert panel.speed > initial_speed, "Speed should increase"

    print(f"Time: {panel.get_time_string()}")
    print(f"{panel.get_day_string()}")
    print(f"Speed: {panel.speed}x")

    return print_test_result(True, "- Time panel works")


def test_suspicion_meter():
    """Test suspicion meter."""
    print_test_header("Suspicion Meter")

    meter = SuspicionMeter()

    # Mock suspicion manager
    class MockSuspicionManager:
        def __init__(self):
            self.suspicion_level = 35

        def get_tier_name(self):
            return "Rumors"

    suspicion_mgr = MockSuspicionManager()
    meter.update(suspicion_mgr)

    summary = meter.get_summary()
    assert summary['level'] == 35, "Level should match"
    assert summary['tier'] == "Rumors", "Tier should match"
    assert summary['color'] == "yellow", "Color should be yellow for Rumors tier"

    print(f"Suspicion: {summary['level']}/100")
    print(f"Tier: {summary['tier']}")
    print(f"Color: {summary['color']}")

    return print_test_result(True, "- Suspicion meter works")


def test_hud_manager():
    """Test HUD manager integration."""
    print_test_header("HUD Manager")

    hud = HUDManager()

    assert hud.is_visible, "HUD should be visible initially"

    # Toggle visibility
    hud.toggle_visibility()
    assert not hud.is_visible, "HUD should be hidden"

    # Get all summaries
    summaries = hud.get_all_summaries()
    assert 'resource' in summaries, "Should have resource summary"
    assert 'power' in summaries, "Should have power summary"
    assert 'time' in summaries, "Should have time summary"
    assert 'suspicion' in summaries, "Should have suspicion summary"

    print(f"HUD visible: {hud.is_visible}")
    print(f"Summary keys: {list(summaries.keys())}")

    return print_test_result(True, "- HUD manager works")


def run_all_tests():
    """Run all Phase 11 tests."""
    print("\n" + "=" * 80)
    print("PHASE 11: UI/UX POLISH - TEST SUITE")
    print("Testing: Menus, Notifications, Settings, HUD")
    print("=" * 80)

    tests = [
        # Menu System Tests
        ("Menu Open/Close", test_menu_system_open_close),
        ("Menu Stack", test_menu_system_stack),
        ("Building Menu Categories", test_building_menu_categories),

        # Notification System Tests
        ("Notification Creation", test_notification_creation),
        ("Notification Priority", test_notification_priority),
        ("Notification Queue", test_notification_queue),
        ("Notification Auto-Dismiss", test_notification_auto_dismiss),
        ("Notification Templates", test_game_notifications_templates),

        # Settings Manager Tests
        ("Settings Get/Set", test_settings_get_set),
        ("Settings Validation", test_settings_validation),
        ("Settings Convenience Methods", test_settings_convenience_methods),
        ("Settings Save/Load", test_settings_save_load),

        # HUD Components Tests
        ("Resource Panel", test_resource_panel),
        ("Power Panel", test_power_panel),
        ("Time Panel", test_time_panel),
        ("Suspicion Meter", test_suspicion_meter),
        ("HUD Manager", test_hud_manager),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            success = test_func()
            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ EXCEPTION in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {passed + failed}")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"Success rate: {passed / (passed + failed) * 100:.1f}%")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
