"""
Test Geographic Features Logic (No Pygame Required)

Tests the core logic of river generation without rendering.
"""

import sys
import os
import random

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))


def test_river_segment():
    """Test RiverSegment class."""
    print("Testing RiverSegment...")
    from src.world.river_generator import RiverSegment

    segment = RiverSegment(10, 20, 4)
    assert segment.x == 10
    assert segment.y == 20
    assert segment.width == 4
    print("✓ RiverSegment works")


def test_bridge():
    """Test Bridge class."""
    print("Testing Bridge...")
    from src.world.river_generator import Bridge

    # Horizontal bridge
    bridge_h = Bridge(10, 20, 'horizontal', 5)
    assert bridge_h.x == 10
    assert bridge_h.y == 20
    assert bridge_h.direction == 'horizontal'
    assert bridge_h.length == 5
    assert len(bridge_h.tiles) == 5
    assert bridge_h.tiles[0] == (10, 20)
    assert bridge_h.tiles[4] == (14, 20)
    print("✓ Horizontal bridge works")

    # Vertical bridge
    bridge_v = Bridge(10, 20, 'vertical', 3)
    assert bridge_v.direction == 'vertical'
    assert len(bridge_v.tiles) == 3
    assert bridge_v.tiles[0] == (10, 20)
    assert bridge_v.tiles[2] == (10, 22)
    print("✓ Vertical bridge works")


def test_river_generation_logic():
    """Test river generation creates valid data structures."""
    print("Testing RiverGenerator logic...")
    from src.world.river_generator import RiverGenerator

    gen = RiverGenerator(100, 75, seed=42)
    
    # Generate river
    river_data = gen.generate(num_rivers=1, flow_direction='south')
    
    # Check data structure
    assert 'rivers' in river_data
    assert 'river_tiles' in river_data
    assert 'bridges' in river_data
    assert 'bridge_tiles' in river_data
    print("✓ River data structure correct")
    
    # Check river exists
    assert len(gen.rivers) == 1
    assert len(gen.river_tiles) > 0
    print(f"✓ Generated river with {len(gen.river_tiles)} tiles")
    
    # Check river flows south
    river = gen.rivers[0]
    first_y = river[0].y
    last_y = river[-1].y
    assert last_y > first_y, f"River should flow south: {first_y} -> {last_y}"
    print(f"✓ River flows south: Y {first_y} -> {last_y}")
    
    # Check statistics
    stats = gen.get_statistics()
    assert stats['num_rivers'] == 1
    assert stats['river_tiles'] > 0
    print(f"✓ Statistics: {stats}")


def test_ocean_logic():
    """Test ocean generation logic."""
    print("Testing ocean generation...")
    from src.world.river_generator import RiverGenerator

    gen = RiverGenerator(100, 75, seed=42)
    
    # Add south ocean
    ocean_tiles = gen.add_ocean_edge('south', depth=8)
    
    assert len(ocean_tiles) > 0
    print(f"✓ South ocean: {len(ocean_tiles)} tiles")
    
    # Check tiles are at south edge
    for x, y in list(ocean_tiles)[:5]:
        assert y >= 75 - 8, f"Ocean Y should be >= {75-8}, got {y}"
    print("✓ Ocean tiles at correct edge")
    
    # Add north ocean
    north_ocean = gen.add_ocean_edge('north', depth=5)
    assert len(north_ocean) > 0
    print(f"✓ North ocean: {len(north_ocean)} tiles")
    
    for x, y in list(north_ocean)[:5]:
        assert y < 5, f"North ocean Y should be < 5, got {y}"
    print("✓ North ocean tiles at correct edge")


def test_bridge_placement_logic():
    """Test bridge placement logic."""
    print("Testing bridge placement...")
    from src.world.river_generator import RiverGenerator

    gen = RiverGenerator(100, 75, seed=42)
    gen.generate(num_rivers=1, flow_direction='south')
    
    # Create road tiles crossing river
    road_tiles = set()
    
    # Find a river tile
    sample_tile = list(gen.river_tiles)[25]
    river_x, river_y = sample_tile
    
    # Create horizontal road
    for x in range(max(0, river_x - 10), min(100, river_x + 10)):
        road_tiles.add((x, river_y))
    
    print(f"✓ Created test road at Y={river_y}")
    
    # Place bridges
    gen.place_bridges(road_tiles, min_spacing=5)
    
    # Check if bridges placed
    if road_tiles & gen.river_tiles:
        assert len(gen.bridges) > 0, "Should have bridges"
        print(f"✓ Placed {len(gen.bridges)} bridge(s)")
        
        for bridge in gen.bridges:
            assert bridge.length >= 2
            print(f"✓ Bridge: {bridge.direction}, {bridge.length} tiles")
    else:
        print("✓ No crossing found")


def test_reproducibility():
    """Test deterministic generation with seeds."""
    print("Testing reproducibility...")
    from src.world.river_generator import RiverGenerator

    # Generate twice with same seed
    gen1 = RiverGenerator(100, 75, seed=999)
    gen1.generate(num_rivers=1, flow_direction='south')
    
    gen2 = RiverGenerator(100, 75, seed=999)
    gen2.generate(num_rivers=1, flow_direction='south')
    
    assert len(gen1.river_tiles) == len(gen2.river_tiles)
    assert gen1.river_tiles == gen2.river_tiles
    print(f"✓ Same seed produces {len(gen1.river_tiles)} identical tiles")


def run_tests():
    """Run all logic tests."""
    print("\n" + "=" * 80)
    print("GEOGRAPHIC FEATURES LOGIC TESTS (No Pygame)")
    print("=" * 80 + "\n")
    
    try:
        test_river_segment()
        test_bridge()
        test_river_generation_logic()
        test_ocean_logic()
        test_bridge_placement_logic()
        test_reproducibility()
        
        print("\n" + "=" * 80)
        print("ALL LOGIC TESTS PASSED ✓")
        print("=" * 80)
        print("\nSummary:")
        print("  ✓ RiverSegment and Bridge classes work correctly")
        print("  ✓ River generation creates valid data structures")
        print("  ✓ Rivers flow in correct direction")
        print("  ✓ Ocean edges placed correctly")
        print("  ✓ Bridge placement logic works")
        print("  ✓ Reproducible with seeds")
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
    success = run_tests()
    sys.exit(0 if success else 1)
