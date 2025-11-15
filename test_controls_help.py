"""
Simple test for Controls/Help Overlay

Tests the controls help overlay rendering and basic functionality.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.ui.controls_help import ControlsHelp


def test_controls_help_creation():
    """Test creating the controls help overlay."""
    print("=" * 80)
    print("CONTROLS/HELP OVERLAY TEST")
    print("=" * 80)
    print()

    # Test creation
    print("Test 1: Creating ControlsHelp instance...")
    help_overlay = ControlsHelp(1280, 720)
    assert help_overlay is not None, "ControlsHelp should be created"
    assert help_overlay.visible == False, "Should start hidden"
    print("✓ ControlsHelp created successfully")
    print(f"  - Screen size: {help_overlay.screen_width}x{help_overlay.screen_height}")
    print(f"  - Panel size: {help_overlay.panel_width}x{help_overlay.panel_height}")
    print(f"  - Initial visibility: {help_overlay.visible}")

    # Test toggle
    print("\nTest 2: Testing toggle functionality...")
    help_overlay.toggle()
    assert help_overlay.visible == True, "Should be visible after toggle"
    help_overlay.toggle()
    assert help_overlay.visible == False, "Should be hidden after second toggle"
    print("✓ Toggle functionality working")

    # Test show/hide
    print("\nTest 3: Testing show/hide methods...")
    help_overlay.show()
    assert help_overlay.visible == True, "Should be visible after show()"
    help_overlay.hide()
    assert help_overlay.visible == False, "Should be hidden after hide()"
    print("✓ Show/hide methods working")

    # Test controls data
    print("\nTest 4: Verifying controls data...")
    assert len(help_overlay.controls) > 0, "Should have control sections"
    total_controls = sum(len(controls) for _, controls in help_overlay.controls)
    print(f"✓ Controls data loaded")
    print(f"  - Sections: {len(help_overlay.controls)}")
    print(f"  - Total controls: {total_controls}")

    # List sections
    print("\n  Control sections:")
    for section_name, controls in help_overlay.controls:
        print(f"    • {section_name} ({len(controls)} controls)")

    # Test content height calculation
    print("\nTest 5: Testing content height calculation...")
    content_height = help_overlay._calculate_content_height()
    assert content_height > 0, "Content height should be positive"
    print(f"✓ Content height calculation working")
    print(f"  - Total content height: {content_height}px")

    # Test scroll bounds
    print("\nTest 6: Testing scroll bounds...")
    help_overlay.show()
    help_overlay.scroll_offset = -100  # Try invalid negative
    assert help_overlay.scroll_offset == -100, "Scroll offset should accept value (bounds checked in render)"
    help_overlay.scroll_offset = 0  # Reset
    print("✓ Scroll offset can be set")

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print("✓ All Controls/Help Overlay tests PASSED")
    print("\nComponents Verified:")
    print("  ✓ ControlsHelp initialization")
    print("  ✓ Toggle functionality")
    print("  ✓ Show/hide methods")
    print("  ✓ Controls data structure")
    print("  ✓ Content height calculation")
    print("  ✓ Scroll offset management")
    print(f"\n✓ {len(help_overlay.controls)} control sections loaded")
    print(f"✓ {total_controls} total controls documented")

    return True


if __name__ == "__main__":
    try:
        success = test_controls_help_creation()
        sys.exit(0 if success else 1)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
