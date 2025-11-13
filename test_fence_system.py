"""
Tests for fence system.

Tests fence entities, fence types, materials, and FenceManager functionality.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.systems.fence_manager import FenceManager
from src.entities.fence import Fence, FenceType
from src.world.grid import Grid


def test_fence_creation():
    """Test creating fences with different types."""
    print("Testing fence creation...")

    # Chain link fence
    fence1 = Fence(100, 100, FenceType.CHAIN_LINK, 'horizontal', 32)
    assert fence1.fence_type == FenceType.CHAIN_LINK
    assert fence1.orientation == 'horizontal'
    assert fence1.width == 32
    assert fence1.height == 8
    assert not fence1.legal_to_deconstruct  # Always illegal
    assert fence1.deconstruction_time == 15.0
    print(f"  Chain link fence: {fence1.width}x{fence1.height}px, time={fence1.deconstruction_time}s")

    # Wooden fence (vertical)
    fence2 = Fence(200, 200, FenceType.WOODEN, 'vertical', 32)
    assert fence2.fence_type == FenceType.WOODEN
    assert fence2.orientation == 'vertical'
    assert fence2.width == 8
    assert fence2.height == 32
    print(f"  Wooden fence: {fence2.width}x{fence2.height}px")

    # Brick fence
    fence3 = Fence(300, 300, FenceType.BRICK, 'horizontal', 32)
    assert fence3.fence_type == FenceType.BRICK
    print(f"  Brick fence: {fence3.fence_type}")

    print(f"  ✓ Fences created with correct properties")
    print()


def test_fence_materials():
    """Test that different fence types have different materials."""
    print("Testing fence materials...")

    chain_link = Fence(100, 100, FenceType.CHAIN_LINK)
    wooden = Fence(200, 200, FenceType.WOODEN)
    brick = Fence(300, 300, FenceType.BRICK)

    # Chain link has metal
    assert 'metal' in chain_link.materials
    assert chain_link.materials['metal'] == 12.0
    print(f"  Chain link: {chain_link.materials}")

    # Wooden has wood and metal (nails)
    assert 'wood' in wooden.materials
    assert 'metal' in wooden.materials
    assert wooden.materials['wood'] == 15.0
    assert wooden.materials['metal'] == 2.0
    print(f"  Wooden: {wooden.materials}")

    # Brick has concrete and slag
    assert 'concrete' in brick.materials
    assert 'slag' in brick.materials
    assert brick.materials['concrete'] == 20.0
    assert brick.materials['slag'] == 5.0
    print(f"  Brick: {brick.materials}")

    print(f"  ✓ Fence materials correct for each type")
    print()


def test_fence_deconstruction():
    """Test fence deconstruction."""
    print("Testing fence deconstruction...")

    fence = Fence(400, 400, FenceType.WOODEN)

    # Initial state
    assert not fence.being_deconstructed
    assert fence.deconstruction_progress == 0.0
    print(f"  Initial: not being deconstructed")

    # Start deconstruction
    result = fence.start_deconstruction()
    assert result == True
    assert fence.being_deconstructed == True
    print(f"  Started deconstruction")

    # Update progress
    complete = fence.update_deconstruction(5.0)  # 5 seconds
    assert not complete
    assert abs(fence.deconstruction_progress - 5.0/15.0) < 0.01  # ~33%
    print(f"  After 5s: {fence.deconstruction_progress:.0%}")

    complete = fence.update_deconstruction(12.0)  # Total 17s (> 15s)
    assert complete
    assert fence.deconstruction_progress >= 1.0
    print(f"  After 17s: {fence.deconstruction_progress:.0%} (complete)")

    # Get materials
    materials = fence.get_materials()
    assert materials['wood'] == 15.0
    print(f"  Materials: {materials}")

    print(f"  ✓ Fence deconstruction works correctly")
    print()


def test_fence_manager_initialization():
    """Test FenceManager initialization."""
    print("Testing FenceManager initialization...")

    grid = Grid(30, 30, 32)
    manager = FenceManager(grid)

    assert manager.grid == grid
    assert len(manager.fences) == 0
    assert len(manager.fence_types) == 3
    print(f"  Fence types: {manager.fence_types}")
    print(f"  Type weights: {manager.fence_type_weights}")
    print(f"  ✓ FenceManager initialized correctly")
    print()


def test_fence_spawning():
    """Test spawning fences around buildings."""
    print("Testing fence spawning...")

    # Create a grid with buildings
    grid = Grid(30, 30, 32)
    grid.create_test_world()

    manager = FenceManager(grid)
    manager.spawn_fences_around_buildings(seed=123, fence_coverage=0.6)

    # Should have spawned some fences
    fence_count = len(manager.fences)
    assert fence_count > 0
    print(f"  Spawned {fence_count} fence segments")

    # Check fence type distribution
    type_counts = {}
    for fence in manager.fences:
        fence_type = fence.fence_type
        type_counts[fence_type] = type_counts.get(fence_type, 0) + 1

    print(f"  Fence type distribution:")
    for ftype, count in type_counts.items():
        percentage = (count / fence_count) * 100 if fence_count > 0 else 0
        print(f"    {ftype}: {count} ({percentage:.1f}%)")

    # Should have some variety
    assert len(type_counts) >= 2

    print(f"  ✓ Fences spawned with variety")
    print()


def test_fence_orientation():
    """Test that fences have correct orientations."""
    print("Testing fence orientations...")

    grid = Grid(25, 25, 32)
    grid.create_test_world()

    manager = FenceManager(grid)
    manager.spawn_fences_around_buildings(seed=456, fence_coverage=0.5)

    # Count orientations
    horizontal_count = sum(1 for f in manager.fences if f.orientation == 'horizontal')
    vertical_count = sum(1 for f in manager.fences if f.orientation == 'vertical')

    total = len(manager.fences)
    print(f"  Total fences: {total}")
    print(f"  Horizontal: {horizontal_count} ({horizontal_count/total*100:.1f}%)")
    print(f"  Vertical: {vertical_count} ({vertical_count/total*100:.1f}%)")

    # Should have both orientations (for perimeter)
    assert horizontal_count > 0
    assert vertical_count > 0

    print(f"  ✓ Fences have both orientations")
    print()


def test_fence_manager_get_fence_at():
    """Test getting fence at a specific location."""
    print("Testing get_fence_at...")

    grid = Grid(20, 20, 32)
    manager = FenceManager(grid)

    # Add fences manually
    fence1 = Fence(500, 500, FenceType.CHAIN_LINK, 'horizontal', 32)
    fence2 = Fence(600, 600, FenceType.WOODEN, 'vertical', 32)
    manager.fences.append(fence1)
    manager.fences.append(fence2)

    # Find fence at location
    found = manager.get_fence_at(505, 505, tolerance=10)
    assert found == fence1
    print(f"  Found fence at (505, 505)")

    # No fence at empty location
    found = manager.get_fence_at(1000, 1000, tolerance=10)
    assert found is None
    print(f"  No fence at (1000, 1000)")

    print(f"  ✓ get_fence_at works correctly")
    print()


def test_fence_removal():
    """Test removing fences."""
    print("Testing fence removal...")

    grid = Grid(20, 20, 32)
    manager = FenceManager(grid)

    # Add fences
    fence1 = Fence(700, 700, FenceType.CHAIN_LINK)
    fence2 = Fence(800, 800, FenceType.WOODEN)
    manager.fences.append(fence1)
    manager.fences.append(fence2)

    assert len(manager.fences) == 2

    # Remove one fence
    manager.remove_fence(fence1)
    assert len(manager.fences) == 1
    assert fence2 in manager.fences
    assert fence1 not in manager.fences
    print(f"  Removed fence 1, count: {len(manager.fences)}")

    # Remove second fence
    manager.remove_fence(fence2)
    assert len(manager.fences) == 0
    print(f"  Removed fence 2, count: {len(manager.fences)}")

    print(f"  ✓ Fence removal works correctly")
    print()


def test_fence_deconstruction_completion():
    """Test that fences are auto-removed when deconstruction completes."""
    print("Testing fence auto-removal on deconstruction...")

    grid = Grid(20, 20, 32)
    manager = FenceManager(grid)

    # Add a fence
    fence = Fence(900, 900, FenceType.CHAIN_LINK)
    manager.fences.append(fence)

    # Start deconstruction
    fence.start_deconstruction()
    assert len(manager.fences) == 1

    # Update with enough time to complete
    manager.update(20.0)  # 15s deconstruction time + buffer

    # Fence should be removed
    assert len(manager.fences) == 0
    print(f"  Fence auto-removed after deconstruction")

    print(f"  ✓ Fence auto-removal on completion works")
    print()


def test_fence_stats():
    """Test fence statistics."""
    print("Testing fence statistics...")

    grid = Grid(20, 20, 32)
    manager = FenceManager(grid)

    # Add mixed fences
    manager.fences.append(Fence(100, 100, FenceType.CHAIN_LINK))
    manager.fences.append(Fence(200, 200, FenceType.CHAIN_LINK))
    manager.fences.append(Fence(300, 300, FenceType.WOODEN))
    manager.fences.append(Fence(400, 400, FenceType.BRICK))

    # Start deconstructing one
    manager.fences[0].start_deconstruction()

    stats = manager.get_stats()

    assert stats['total'] == 4
    assert stats['by_type'][FenceType.CHAIN_LINK] == 2
    assert stats['by_type'][FenceType.WOODEN] == 1
    assert stats['by_type'][FenceType.BRICK] == 1
    assert stats['being_deconstructed'] == 1

    print(f"  Total: {stats['total']}")
    print(f"  By type: {stats['by_type']}")
    print(f"  Being deconstructed: {stats['being_deconstructed']}")

    print(f"  ✓ Fence statistics correct")
    print()


def test_fence_illegality():
    """Test that all fences are illegal to deconstruct."""
    print("Testing fence illegality...")

    # Test all fence types
    chain_link = Fence(100, 100, FenceType.CHAIN_LINK)
    wooden = Fence(200, 200, FenceType.WOODEN)
    brick = Fence(300, 300, FenceType.BRICK)

    assert not chain_link.legal_to_deconstruct
    assert not wooden.legal_to_deconstruct
    assert not brick.legal_to_deconstruct

    print(f"  Chain link: legal={chain_link.legal_to_deconstruct}")
    print(f"  Wooden: legal={wooden.legal_to_deconstruct}")
    print(f"  Brick: legal={brick.legal_to_deconstruct}")

    # All should have noise level
    assert chain_link.noise_level == 6
    assert wooden.noise_level == 6
    assert brick.noise_level == 6

    print(f"  All fences: noise_level={chain_link.noise_level}")

    print(f"  ✓ All fences are illegal and noisy")
    print()


def test_reproducible_spawning():
    """Test that spawning with same seed produces consistent results."""
    print("Testing reproducible spawning...")

    # Create a single grid
    grid = Grid(25, 25, 32)
    grid.create_test_world()

    # Spawn twice with same seed on same grid
    manager1 = FenceManager(grid)
    manager1.spawn_fences_around_buildings(seed=789, fence_coverage=0.5)

    # Record first spawn
    first_spawn = []
    for f in manager1.fences:
        first_spawn.append((f.world_x, f.world_y, f.fence_type, f.orientation))

    # Clear and respawn
    manager2 = FenceManager(grid)
    manager2.spawn_fences_around_buildings(seed=789, fence_coverage=0.5)

    # Should have same number of fences
    assert len(manager1.fences) == len(manager2.fences)
    print(f"  Both spawns created {len(manager1.fences)} fence segments")

    # Should have same fence types at same positions
    for i, (f1, (x, y, ftype, orientation)) in enumerate(zip(manager2.fences, first_spawn)):
        assert f1.fence_type == ftype
        assert f1.orientation == orientation
        assert abs(f1.world_x - x) < 1  # Allow tiny floating point differences
        assert abs(f1.world_y - y) < 1

    print(f"  ✓ Spawning is reproducible with same seed")
    print()


def main():
    """Run all tests."""
    print("=" * 80)
    print("FENCE SYSTEM TESTS")
    print("=" * 80)
    print()

    try:
        test_fence_creation()
        test_fence_materials()
        test_fence_deconstruction()
        test_fence_manager_initialization()
        test_fence_spawning()
        test_fence_orientation()
        test_fence_manager_get_fence_at()
        test_fence_removal()
        test_fence_deconstruction_completion()
        test_fence_stats()
        test_fence_illegality()
        test_reproducible_spawning()

        print("=" * 80)
        print("ALL FENCE SYSTEM TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Phase 7.4 Features Implemented:")
        print()
        print("FENCE TYPES:")
        print("  - Chain link (12kg metal)")
        print("  - Wooden (15kg wood + 2kg metal nails)")
        print("  - Brick (20kg concrete + 5kg slag)")
        print()
        print("FENCE PROPERTIES:")
        print("  - All fences ILLEGAL to deconstruct")
        print("  - 15 seconds deconstruction time")
        print("  - Noise level: 6/10 (moderately noisy)")
        print("  - Horizontal and vertical orientations")
        print()
        print("FENCE MANAGER:")
        print("  - Spawns fences around buildings")
        print("  - Leaves gaps for entrances (facing roads)")
        print("  - 50% chain link, 35% wooden, 15% brick distribution")
        print("  - Reproducible spawning with seeds")
        print("  - Auto-removal when deconstruction completes")
        print("  - Fence tracking and statistics")
        print()
        print("VISUAL FEATURES:")
        print("  - Chain link: mesh pattern with posts")
        print("  - Wooden: plank pattern")
        print("  - Brick: brick pattern with mortar")
        print("  - Deconstruction damage shows progressively")
        print()
        print("INTEGRATION:")
        print("  - Integrated into game update/render loop")
        print("  - Fences rendered after vehicles, before entities")
        print("  - Fence spawning on game initialization")
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
