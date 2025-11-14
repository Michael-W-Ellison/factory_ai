"""
Comprehensive Test Suite for Phase 8.5: Testing

This master test runner executes all Phase 8 tests:
- 8.1: Camera System
- 8.2: Camera Hacking
- 8.3: Inspection System
- 8.4: Material Inventory & Tagging
- 8.5: Integration & Balance Testing

Run this file to verify complete Phase 8 implementation.
"""

import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import all Phase 8 test modules
from src import test_camera_system
from src import test_camera_hacking
from src import test_inspection_system
from src import test_material_inventory
from src import test_material_source_integration


def print_header(text, char="="):
    """Print a formatted header."""
    width = 80
    print()
    print(char * width)
    print(text.center(width))
    print(char * width)
    print()


def print_section(text):
    """Print a section header."""
    print()
    print("-" * 80)
    print(f"  {text}")
    print("-" * 80)


def run_test_module(module, module_name):
    """Run a test module and return success status."""
    print_section(f"Running: {module_name}")
    try:
        success = module.run_all_tests()
        return success
    except Exception as e:
        print(f"\n❌ ERROR running {module_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 8 tests."""
    start_time = time.time()

    print_header("PHASE 8.5: COMPREHENSIVE TEST SUITE", "=")
    print(f"Test Run Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = {}

    # Phase 8.1: Camera System
    results['8.1 - Camera System'] = run_test_module(
        test_camera_system,
        "Phase 8.1 - Camera System"
    )

    # Phase 8.2: Camera Hacking
    results['8.2 - Camera Hacking'] = run_test_module(
        test_camera_hacking,
        "Phase 8.2 - Camera Hacking"
    )

    # Phase 8.3: Inspection System
    results['8.3 - Inspection System'] = run_test_module(
        test_inspection_system,
        "Phase 8.3 - Inspection System"
    )

    # Phase 8.4: Material Inventory & Tagging
    results['8.4 - Material Inventory & Tagging'] = run_test_module(
        test_material_inventory,
        "Phase 8.4 - Material Inventory & Tagging"
    )

    # Phase 8.4: Material Source Integration
    results['8.4 - Material Source Integration'] = run_test_module(
        test_material_source_integration,
        "Phase 8.4 - Material Source Integration"
    )

    # Print summary
    print_header("TEST SUMMARY", "=")

    all_passed = True
    passed_count = 0
    failed_count = 0

    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name:<45} {status}")
        if passed:
            passed_count += 1
        else:
            failed_count += 1
            all_passed = False

    print()
    print("=" * 80)
    print(f"  Total Tests: {len(results)}")
    print(f"  Passed: {passed_count}")
    print(f"  Failed: {failed_count}")

    elapsed_time = time.time() - start_time
    print(f"  Time Elapsed: {elapsed_time:.2f}s")
    print("=" * 80)

    if all_passed:
        print()
        print("┌" + "─" * 78 + "┐")
        print("│" + " " * 78 + "│")
        print("│" + "ALL PHASE 8 TESTS PASSED!".center(78) + "│")
        print("│" + " " * 78 + "│")
        print("│" + "Phase 8: Camera & Inspection System - COMPLETE ✓".center(78) + "│")
        print("│" + " " * 78 + "│")
        print("└" + "─" * 78 + "┘")
        print()
        print("Phase 8 Features Verified:")
        print("  ✓ Security cameras with 90° vision cones (200px range)")
        print("  ✓ Camera placement system (police stations, roads, buildings)")
        print("  ✓ Camera status management (active, disabled, broken)")
        print("  ✓ Camera hacking with research prerequisites")
        print("  ✓ Hacking consequences (suspicion, security upgrades, FBI)")
        print("  ✓ Inspection system with 60+ suspicion trigger")
        print("  ✓ Countdown timers (24-48 hours)")
        print("  ✓ Inspection pass/fail logic with consequences")
        print("  ✓ Material source tagging (legal vs illegal)")
        print("  ✓ Illegal material detection")
        print("  ✓ Hiding strategies (selling, processing)")
        print("  ✓ End-to-end material tracking integration")
        print()
        return 0
    else:
        print()
        print("❌ SOME TESTS FAILED")
        print(f"   {failed_count} test suite(s) failed")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
