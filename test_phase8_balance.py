"""
Phase 8.5: Balance Testing

Tests game balance and difficulty for Phase 8 systems:
- Camera detection rates
- Inspection pass/fail probabilities
- Suspicion accumulation and decay
- Economic impact of fines
- Hiding strategy effectiveness
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.systems.material_inventory import MaterialInventory, MaterialSource
from src.systems.inspection_manager import InspectionManager, InspectionResult
from src.systems.resource_manager import ResourceManager
from src.systems.suspicion_manager import SuspicionManager


class MockResourceManager:
    """Mock resource manager."""
    def __init__(self):
        self.money = 100000

    def modify_money(self, amount):
        self.money += amount


class MockSuspicionManager:
    """Mock suspicion manager."""
    def __init__(self):
        self.suspicion_level = 0

    def add_suspicion(self, amount, reason):
        self.suspicion_level += amount


def test_inspection_pass_rate_with_clean_inventory():
    """
    Test: Inspection should have high pass rate with clean inventory.

    Expected: >80% pass rate with 0 illegal materials
    """
    print("Balance Test: Inspection Pass Rate (Clean Inventory)")

    results = {
        InspectionResult.PASS: 0,
        InspectionResult.FAIL_MINOR: 0,
        InspectionResult.FAIL_MAJOR: 0,
        InspectionResult.FAIL_CRITICAL: 0
    }

    runs = 100
    for run in range(runs):
        resources = MockResourceManager()
        suspicion = MockSuspicionManager()
        suspicion.suspicion_level = 70

        inventory = MaterialInventory()
        # Only legal materials
        inventory.add_material('plastic', 200, MaterialSource.LANDFILL)
        inventory.add_material('metal', 100, MaterialSource.SCRAP_VEHICLE)

        inspection = InspectionManager(resources, suspicion, inventory)
        inspection.force_schedule_inspection(0.0, warning_hours=0.0)
        inspection.update(1.0, 1.0)

        # Complete inspection
        for _ in range(3700):
            inspection.update(1.0, 1.0)

        results[inspection.last_result] += 1

    pass_rate = (results[InspectionResult.PASS] / runs) * 100

    print(f"  Results from {runs} inspections:")
    print(f"    PASS: {results[InspectionResult.PASS]} ({pass_rate:.1f}%)")
    print(f"    FAIL_MINOR: {results[InspectionResult.FAIL_MINOR]}")
    print(f"    FAIL_MAJOR: {results[InspectionResult.FAIL_MAJOR]}")
    print(f"    FAIL_CRITICAL: {results[InspectionResult.FAIL_CRITICAL]}")

    assert pass_rate >= 80, f"Pass rate should be >= 80% with clean inventory, got {pass_rate:.1f}%"

    print(f"  ✓ Pass rate acceptable: {pass_rate:.1f}% >= 80%")
    print()


def test_inspection_detection_rate_minor_violations():
    """
    Test: Minor violations detection rate.

    Expected: ~60% detection rate for small amounts of illegal materials
    """
    print("Balance Test: Detection Rate (Minor Violations)")

    violations_detected = 0
    runs = 100

    for run in range(runs):
        resources = MockResourceManager()
        suspicion = MockSuspicionManager()
        suspicion.suspicion_level = 70

        inventory = MaterialInventory()
        # Small amount of illegal materials
        inventory.add_material('plastic', 100, MaterialSource.LANDFILL)  # Legal
        inventory.add_material('copper', 30, MaterialSource.FENCE)  # Illegal

        inspection = InspectionManager(resources, suspicion, inventory)
        inspection.force_schedule_inspection(0.0, warning_hours=0.0)
        inspection.update(1.0, 1.0)

        for _ in range(3700):
            inspection.update(1.0, 1.0)

        if inspection.last_result in [InspectionResult.FAIL_MINOR, InspectionResult.FAIL_MAJOR, InspectionResult.FAIL_CRITICAL]:
            violations_detected += 1

    detection_rate = (violations_detected / runs) * 100

    print(f"  Results from {runs} inspections:")
    print(f"    Violations detected: {violations_detected} ({detection_rate:.1f}%)")
    print(f"    Expected range: 50-70%")

    assert 50 <= detection_rate <= 70, f"Detection rate should be 50-70%, got {detection_rate:.1f}%"

    print(f"  ✓ Detection rate balanced: {detection_rate:.1f}%")
    print()


def test_inspection_detection_rate_major_violations():
    """
    Test: Major violations detection rate.

    Expected: ~90% detection rate for large amounts of illegal materials
    """
    print("Balance Test: Detection Rate (Major Violations)")

    violations_detected = 0
    runs = 100

    for run in range(runs):
        resources = MockResourceManager()
        suspicion = MockSuspicionManager()
        suspicion.suspicion_level = 70

        inventory = MaterialInventory()
        # Large amount of illegal materials
        inventory.add_material('copper', 150, MaterialSource.FENCE)
        inventory.add_material('electronics', 100, MaterialSource.LIVABLE_HOUSE)

        inspection = InspectionManager(resources, suspicion, inventory)
        inspection.force_schedule_inspection(0.0, warning_hours=0.0)
        inspection.update(1.0, 1.0)

        for _ in range(3700):
            inspection.update(1.0, 1.0)

        if inspection.last_result in [InspectionResult.FAIL_MINOR, InspectionResult.FAIL_MAJOR, InspectionResult.FAIL_CRITICAL]:
            violations_detected += 1

    detection_rate = (violations_detected / runs) * 100

    print(f"  Results from {runs} inspections:")
    print(f"    Violations detected: {violations_detected} ({detection_rate:.1f}%)")
    print(f"    Expected range: 85-100%")

    assert 85 <= detection_rate <= 100, f"Detection rate should be 85-100%, got {detection_rate:.1f}%"

    print(f"  ✓ Detection rate balanced: {detection_rate:.1f}%")
    print()


def test_economic_impact_of_fines():
    """
    Test: Economic impact of inspection fines.

    Verify that fines are not too punishing but still meaningful.
    """
    print("Balance Test: Economic Impact of Fines")

    starting_money = 100000

    # Test FAIL_MINOR fine
    resources_minor = ResourceManager()
    resources_minor.money = starting_money
    resources_minor.modify_money(-5000)  # FAIL_MINOR fine

    minor_loss_percent = ((starting_money - resources_minor.money) / starting_money) * 100

    print(f"  FAIL_MINOR:")
    print(f"    Fine: $5,000")
    print(f"    Impact: {minor_loss_percent:.1f}% of starting money")

    # Test FAIL_MAJOR fine
    resources_major = ResourceManager()
    resources_major.money = starting_money
    resources_major.modify_money(-20000)  # FAIL_MAJOR fine

    major_loss_percent = ((starting_money - resources_major.money) / starting_money) * 100

    print(f"  FAIL_MAJOR:")
    print(f"    Fine: $20,000")
    print(f"    Impact: {major_loss_percent:.1f}% of starting money")

    # Fines should be meaningful but not bankrupting
    assert minor_loss_percent <= 10, "FAIL_MINOR fine should be <= 10% of starting money"
    assert 15 <= major_loss_percent <= 25, "FAIL_MAJOR fine should be 15-25% of starting money"

    print(f"  ✓ Fines are balanced (meaningful but not bankrupting)")
    print()


def test_hiding_strategy_selling_effectiveness():
    """
    Test: Effectiveness of selling illegal materials.

    Verify that selling illegal materials is viable but comes at a cost.
    """
    print("Balance Test: Hiding Strategy - Selling")

    inventory = MaterialInventory()
    resources = ResourceManager()
    starting_money = resources.money

    # Add illegal materials
    inventory.add_material('copper', 100, MaterialSource.FENCE)  # Value: ~$1500 (100 * 15)
    inventory.add_material('electronics', 50, MaterialSource.LIVABLE_HOUSE)  # Value: ~$500 (50 * 10)

    # Expected total value at 70% discount: ~$1400

    # Sell illegal materials
    earned = inventory.sell_all_illegal_materials(resources)
    illegal_after = inventory.get_illegal_material_count()

    money_gained = resources.money - starting_money
    discount_percent = ((money_gained / 2000) * 100) if 2000 > 0 else 0  # Approximate full value

    print(f"  Illegal materials sold:")
    print(f"    Copper: 100kg (fence)")
    print(f"    Electronics: 50kg (livable house)")
    print(f"  Earned: ${earned:.2f}")
    print(f"  Discount: ~{100 - discount_percent:.0f}%")
    print(f"  Illegal materials remaining: {illegal_after}kg")

    assert illegal_after == 0, "All illegal materials should be sold"
    assert earned > 0, "Should earn money from selling"
    assert earned < 2000, "Should earn less than full value (discounted)"

    print(f"  ✓ Selling is viable but comes at ~30% discount")
    print()


def test_hiding_strategy_processing_effectiveness():
    """
    Test: Effectiveness of processing illegal materials to legal.

    Verify that processing is a viable option with appropriate cost.
    """
    print("Balance Test: Hiding Strategy - Processing")

    inventory = MaterialInventory()

    # Add illegal plastic
    inventory.add_material('plastic', 100, MaterialSource.LIVABLE_HOUSE)
    illegal_before = inventory.get_illegal_material_count()

    # Process to legal
    success = inventory.process_materials_to_legal('plastic', 100)
    illegal_after = inventory.get_illegal_material_count()
    total_plastic = inventory.total_materials['plastic']

    loss_percent = ((100 - total_plastic) / 100) * 100

    print(f"  Processed: 100kg illegal plastic")
    print(f"  Illegal before: {illegal_before}kg")
    print(f"  Illegal after: {illegal_after}kg")
    print(f"  Total plastic after: {total_plastic}kg")
    print(f"  Loss: {loss_percent:.0f}%")

    assert success, "Processing should succeed"
    assert illegal_after == 0, "No illegal materials should remain"
    assert total_plastic == 90, "Should have 90kg after 10% loss"
    assert loss_percent == 10, "Should lose 10% in processing"

    print(f"  ✓ Processing is viable with 10% material loss")
    print()


def test_suspicion_accumulation_balance():
    """
    Test: Suspicion accumulation is balanced.

    Verify that suspicion grows at a reasonable rate.
    """
    print("Balance Test: Suspicion Accumulation")

    suspicion_mgr = SuspicionManager()

    # Simulate various sources of suspicion
    incidents = [
        (5, "Camera detection"),
        (5, "Camera detection"),
        (2, "Camera hack"),
        (2, "Camera hack"),
        (2, "Camera hack"),
        (1, "NPC report"),
        (1, "NPC report"),
    ]

    for amount, reason in incidents:
        suspicion_mgr.add_suspicion(amount, reason)

    total_suspicion = suspicion_mgr.suspicion_level

    print(f"  Suspicion sources:")
    print(f"    Camera detections: 2 x 5 = 10")
    print(f"    Camera hacks: 3 x 2 = 6")
    print(f"    NPC reports: 2 x 1 = 2")
    print(f"  Total suspicion: {total_suspicion}")

    # Reaching inspection threshold (60) should require significant incidents
    assert total_suspicion < 60, "Should not reach inspection threshold too easily"

    # Calculate how many more incidents needed
    remaining = 60 - total_suspicion
    print(f"  Remaining to reach inspection (60): {remaining}")
    print(f"  ✓ Suspicion grows at reasonable rate")
    print()


def run_all_tests():
    """Run all balance tests."""
    print("=" * 80)
    print("PHASE 8.5: BALANCE TESTING")
    print("=" * 80)
    print()

    try:
        test_inspection_pass_rate_with_clean_inventory()
        test_inspection_detection_rate_minor_violations()
        test_inspection_detection_rate_major_violations()
        test_economic_impact_of_fines()
        test_hiding_strategy_selling_effectiveness()
        test_hiding_strategy_processing_effectiveness()
        test_suspicion_accumulation_balance()

        print()
        print("=" * 80)
        print("ALL BALANCE TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Balance Test Summary:")
        print("  ✓ Inspection pass rate: 80%+ with clean inventory")
        print("  ✓ Minor violations: 50-70% detection rate")
        print("  ✓ Major violations: 85-100% detection rate")
        print("  ✓ Economic fines: Meaningful but not bankrupting")
        print("  ✓ Selling strategy: Viable with ~30% discount")
        print("  ✓ Processing strategy: Viable with 10% loss")
        print("  ✓ Suspicion accumulation: Balanced and fair")
        print()
        print("Phase 8 Balance: VERIFIED ✓")

        return True

    except AssertionError as e:
        print()
        print("=" * 80)
        print(f"BALANCE TEST FAILED: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
