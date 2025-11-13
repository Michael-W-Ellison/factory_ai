"""
Test script for Construction System.

Tests:
- ConstructionSite initialization
- Material delivery
- Robot assignment
- Construction progress
- ConstructionManager queue
- Construction completion
"""

import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.entities.construction_site import ConstructionSite
from src.systems.construction_manager import ConstructionManager, ConstructionOrder
from src.systems.building_manager import BuildingManager
from src.systems.resource_manager import ResourceManager
from src.world.grid import Grid


class SimpleCamera:
    """Simple camera for testing."""
    def __init__(self):
        self.x = 0
        self.y = 0
        self.zoom = 1.0

    def world_to_screen(self, world_x, world_y):
        return int(world_x - self.x), int(world_y - self.y)

    def is_visible(self, x, y, width, height):
        return True


def test_construction_site_initialization():
    """Test construction site initialization."""
    print("\nTesting construction site initialization...")

    site = ConstructionSite(
        grid_x=10,
        grid_y=10,
        width_tiles=5,
        height_tiles=5,
        building_type="factory",
        construction_time=60.0,
        required_materials={'metal': 100.0, 'plastic': 50.0}
    )

    print(f"  {site}")
    print(f"  Building type: {site.building_type}")
    print(f"  Size: {site.width_tiles}x{site.height_tiles} tiles")
    print(f"  Position: ({site.grid_x}, {site.grid_y})")
    print(f"  Construction time: {site.construction_time}s")
    print(f"  Progress: {site.progress * 100:.0f}%")
    print(f"  Required materials: {site.required_materials}")

    assert site.building_type == "factory", "Should be factory type"
    assert site.width_tiles == 5, "Should be 5 tiles wide"
    assert site.construction_time == 60.0, "Should take 60 seconds"
    assert site.progress == 0.0, "Should start at 0% progress"

    print("  ✓ Construction site initialization correct")


def test_material_delivery():
    """Test material delivery to construction site."""
    print("\nTesting material delivery...")

    site = ConstructionSite(
        grid_x=10,
        grid_y=10,
        width_tiles=3,
        height_tiles=3,
        building_type="solar_array",
        construction_time=30.0,
        required_materials={'metal': 100.0, 'glass': 50.0}
    )

    print(f"  Required materials: {site.required_materials}")
    print(f"  Materials satisfied: {site.are_materials_satisfied()}")
    assert not site.are_materials_satisfied(), "Should not be satisfied initially"

    # Deliver metal
    accepted = site.deliver_material('metal', 60.0)
    print(f"  Delivered 60kg metal: {accepted}kg accepted")
    assert accepted == 60.0, "Should accept 60kg metal"

    # Deliver more metal
    accepted = site.deliver_material('metal', 60.0)
    print(f"  Delivered 60kg metal: {accepted}kg accepted")
    assert accepted == 40.0, "Should only accept 40kg (to reach 100kg total)"

    # Deliver glass
    accepted = site.deliver_material('glass', 50.0)
    print(f"  Delivered 50kg glass: {accepted}kg accepted")
    assert accepted == 50.0, "Should accept 50kg glass"

    print(f"  Materials delivered: {site.materials_delivered}")
    print(f"  Materials satisfied: {site.are_materials_satisfied()}")
    assert site.are_materials_satisfied(), "Should be satisfied now"

    print("  ✓ Material delivery works correctly")


def test_robot_assignment():
    """Test robot assignment to construction sites."""
    print("\nTesting robot assignment...")

    site = ConstructionSite(
        grid_x=10,
        grid_y=10,
        width_tiles=3,
        height_tiles=3,
        building_type="test_building",
        construction_time=60.0
    )

    print(f"  Initial workers: {len(site.robots_working)}/{site.max_workers}")
    assert len(site.robots_working) == 0, "Should have no workers initially"

    # Add robots
    success = site.add_robot(1)
    print(f"  Added robot 1: {success}")
    assert success, "Should add robot successfully"

    success = site.add_robot(2)
    print(f"  Added robot 2: {success}")
    assert success, "Should add robot successfully"

    print(f"  Current workers: {len(site.robots_working)}/{site.max_workers}")
    assert len(site.robots_working) == 2, "Should have 2 workers"

    # Try to add same robot again
    success = site.add_robot(1)
    print(f"  Added robot 1 again: {success}")
    assert not success, "Should not add duplicate robot"

    # Add robots up to max
    for i in range(3, 7):
        site.add_robot(i)

    print(f"  After filling: {len(site.robots_working)}/{site.max_workers}")
    assert len(site.robots_working) == site.max_workers, "Should be at max workers"

    # Try to add beyond max
    success = site.add_robot(10)
    print(f"  Try to add beyond max: {success}")
    assert not success, "Should not add beyond max workers"

    # Remove a robot
    site.remove_robot(2)
    print(f"  After removing robot 2: {len(site.robots_working)}/{site.max_workers}")
    assert len(site.robots_working) == site.max_workers - 1, "Should have one less worker"

    print("  ✓ Robot assignment works correctly")


def test_construction_progress():
    """Test construction progress over time."""
    print("\nTesting construction progress...")

    site = ConstructionSite(
        grid_x=10,
        grid_y=10,
        width_tiles=3,
        height_tiles=3,
        building_type="test_building",
        construction_time=10.0,  # 10 seconds
        required_materials={'metal': 50.0}
    )

    # Deliver materials
    site.deliver_material('metal', 50.0)

    # Add a robot
    site.add_robot(1)

    print(f"  Initial progress: {site.progress * 100:.0f}%")
    assert site.progress == 0.0, "Should start at 0%"

    # Update for 5 seconds (halfway)
    site.update(5.0)
    print(f"  After 5s: {site.progress * 100:.0f}%")
    assert abs(site.progress - 0.5) < 0.01, "Should be ~50% complete"

    # Update for another 5 seconds
    site.update(5.0)
    print(f"  After 10s: {site.progress * 100:.0f}%")
    assert site.is_complete(), "Should be 100% complete"

    print("  ✓ Construction progress works correctly")


def test_construction_speed_with_robots():
    """Test that more robots speed up construction."""
    print("\nTesting construction speed with multiple robots...")

    # Site with 1 robot
    site1 = ConstructionSite(
        grid_x=10,
        grid_y=10,
        width_tiles=3,
        height_tiles=3,
        building_type="test_building",
        construction_time=100.0
    )
    site1.add_robot(1)

    # Site with 3 robots
    site2 = ConstructionSite(
        grid_x=20,
        grid_y=20,
        width_tiles=3,
        height_tiles=3,
        building_type="test_building",
        construction_time=100.0
    )
    site2.add_robot(1)
    site2.add_robot(2)
    site2.add_robot(3)

    # Update both for 10 seconds
    site1.update(10.0)
    site2.update(10.0)

    print(f"  1 robot - Progress: {site1.progress * 100:.1f}%")
    print(f"  3 robots - Progress: {site2.progress * 100:.1f}%")
    print(f"  Speedup: {site2.progress / site1.progress:.2f}x")

    assert site2.progress > site1.progress, "More robots should be faster"

    print("  ✓ Multiple robots speed up construction")


def test_construction_manager_queue():
    """Test construction manager queue system."""
    print("\nTesting construction manager queue...")

    grid = Grid(width_tiles=100, height_tiles=75)
    building_manager = BuildingManager(grid)
    resource_manager = ResourceManager()
    resource_manager.money = 10000.0  # Give player money

    construction_mgr = ConstructionManager(building_manager, resource_manager, grid)

    print(f"  Initial queue: {len(construction_mgr.queue)}")
    print(f"  Initial money: ${resource_manager.money:.0f}")

    # Queue a construction
    success, message = construction_mgr.queue_construction(
        building_type="factory",
        grid_x=50,
        grid_y=50,
        width_tiles=5,
        height_tiles=5,
        construction_time=60.0,
        cost=1000.0,
        required_materials={'metal': 100.0}
    )

    print(f"  Queue result: {success} - {message}")
    print(f"  After queue - Money: ${resource_manager.money:.0f}")
    print(f"  After queue - Queue length: {len(construction_mgr.queue)}")

    assert success, "Should queue successfully"
    assert len(construction_mgr.queue) == 1, "Should have 1 order in queue"
    assert resource_manager.money == 9000.0, "Should have deducted cost"

    # Try to queue at occupied location
    success, message = construction_mgr.queue_construction(
        building_type="factory",
        grid_x=50,  # Same location
        grid_y=50,
        width_tiles=5,
        height_tiles=5,
        construction_time=60.0,
        cost=1000.0
    )

    print(f"  Queue at same location: {success} - {message}")
    assert not success, "Should fail for occupied location"

    print("  ✓ Construction manager queue works correctly")


def test_construction_manager_start():
    """Test construction manager starting construction."""
    print("\nTesting construction manager starting construction...")

    grid = Grid(width_tiles=100, height_tiles=75)
    building_manager = BuildingManager(grid)
    resource_manager = ResourceManager()
    resource_manager.money = 10000.0

    construction_mgr = ConstructionManager(building_manager, resource_manager, grid)

    # Queue construction
    construction_mgr.queue_construction(
        building_type="landfill_gas_extraction",
        grid_x=20,
        grid_y=20,
        width_tiles=2,
        height_tiles=2,
        construction_time=30.0,
        cost=500.0
    )

    print(f"  Queued: {len(construction_mgr.queue)} orders")
    print(f"  Active sites: {len(construction_mgr.active_sites)}")

    # Update to start construction
    construction_mgr.update(0.1)

    print(f"  After update:")
    print(f"    Active sites: {len(construction_mgr.active_sites)}")

    assert len(construction_mgr.active_sites) == 1, "Should have started construction"
    assert construction_mgr.queue[0].started, "Order should be marked as started"

    # Assign a robot to the construction site
    site = construction_mgr.active_sites[0]
    success = construction_mgr.assign_robot_to_site(robot_id=1, site=site)
    print(f"  Assigned robot to site: {success}")
    assert success, "Should assign robot successfully"
    assert len(site.robots_working) == 1, "Site should have 1 robot"

    print("  ✓ Construction manager starts construction correctly")


def test_construction_completion():
    """Test construction completion."""
    print("\nTesting construction completion...")

    grid = Grid(width_tiles=100, height_tiles=75)
    building_manager = BuildingManager(grid)
    resource_manager = ResourceManager()
    resource_manager.money = 10000.0

    construction_mgr = ConstructionManager(building_manager, resource_manager, grid)

    # Queue construction
    construction_mgr.queue_construction(
        building_type="landfill_gas_extraction",
        grid_x=30,
        grid_y=30,
        width_tiles=2,
        height_tiles=2,
        construction_time=1.0,  # Very fast for testing
        cost=500.0
    )

    # Start construction
    construction_mgr.update(0.1)

    print(f"  Active sites: {len(construction_mgr.active_sites)}")
    print(f"  Buildings: {len(building_manager.buildings)}")

    # Assign a robot to the construction site
    site = construction_mgr.active_sites[0]
    construction_mgr.assign_robot_to_site(robot_id=1, site=site)
    print(f"  Assigned robot to construction site")

    # Complete construction (1 second + a bit)
    construction_mgr.update(1.5)

    print(f"  After completion:")
    print(f"    Active sites: {len(construction_mgr.active_sites)}")
    print(f"    Buildings: {len(building_manager.buildings)}")
    print(f"    Queue: {len(construction_mgr.queue)}")

    assert len(construction_mgr.active_sites) == 0, "Site should be removed"
    assert len(building_manager.buildings) == 1, "Building should be created"
    assert len(construction_mgr.queue) == 0, "Order should be removed"

    print("  ✓ Construction completion works correctly")


def test_construction_visual():
    """Test construction site visual rendering."""
    print("\nTesting construction site visual...")

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Construction Site Visual Test")
    camera = SimpleCamera()
    clock = pygame.time.Clock()

    # Create construction sites at different progress levels
    sites = []
    for i in range(5):
        site = ConstructionSite(
            grid_x=10 + i * 10,
            grid_y=10,
            width_tiles=3,
            height_tiles=3,
            building_type="test_building",
            construction_time=10.0,
            required_materials={'metal': 50.0, 'plastic': 25.0}
        )
        # Position for display
        site.x = 50 + i * 150
        site.y = 200

        # Set different progress levels
        site.progress = i * 0.25
        site.time_remaining = 10.0 * (1.0 - site.progress)

        # Add workers to some
        if i >= 2:
            for j in range(i):
                site.add_robot(j)

        # Deliver materials to some
        if i >= 3:
            site.deliver_material('metal', 50.0)
            site.deliver_material('plastic', 25.0)

        sites.append(site)

    print("  Visual test window opened (will run for 5 seconds)...")
    print("  You should see:")
    print("    - 5 construction sites in a row")
    print("    - Progress bars showing 0%, 25%, 50%, 75%, 100%")
    print("    - Worker counts on later sites")
    print("    - Material status icons")

    # Run for 5 seconds
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < 5000:
        dt = clock.tick(60) / 1000.0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # Render
        screen.fill((30, 30, 30))

        # Draw title
        font = pygame.font.Font(None, 32)
        title = font.render("Construction Site Progress Visualization", True, (255, 255, 255))
        screen.blit(title, (20, 20))

        # Draw labels
        font_small = pygame.font.Font(None, 20)
        progress_labels = ["0%", "25%", "50%", "75%", "100%"]
        for i, label in enumerate(progress_labels):
            x = 50 + i * 150
            y = 450
            text = font_small.render(f"Progress: {label}", True, (200, 200, 200))
            screen.blit(text, (x, y))

        # Render construction sites
        for site in sites:
            site.render(screen, camera)

        pygame.display.flip()

    pygame.quit()
    print("  ✓ Visual test completed")


if __name__ == '__main__':
    print("=" * 80)
    print("CONSTRUCTION SYSTEM TESTS")
    print("=" * 80)

    try:
        test_construction_site_initialization()
        test_material_delivery()
        test_robot_assignment()
        test_construction_progress()
        test_construction_speed_with_robots()
        test_construction_manager_queue()
        test_construction_manager_start()
        test_construction_completion()
        test_construction_visual()

        print("\n" + "=" * 80)
        print("ALL CONSTRUCTION SYSTEM TESTS PASSED! ✓")
        print("=" * 80)
        print("\nSummary:")
        print("  - ConstructionSite initialization: ✓")
        print("  - Material delivery: ✓")
        print("  - Robot assignment: ✓")
        print("  - Construction progress: ✓")
        print("  - Multi-robot speedup: ✓")
        print("  - Construction queue: ✓")
        print("  - Construction starting: ✓")
        print("  - Construction completion: ✓")
        print("  - Visual rendering: ✓")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
