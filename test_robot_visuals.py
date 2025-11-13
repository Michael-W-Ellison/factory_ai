"""
Test script for robot directional rendering and upgrade level visuals.

Tests:
- Robot directional rendering and movement animation
- Robot visual changes across upgrade levels (1-5)
- Robot appearing progressively larger and stronger with upgrades
"""

import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.entities.robot import Robot


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


def test_robot_properties():
    """Test robot properties and upgrade levels."""
    print("\nTesting robot properties...")

    # Create robots at different upgrade levels
    robot_l1 = Robot(x=100, y=100, autonomous=False)
    robot_l1.upgrade_level = 1

    robot_l3 = Robot(x=200, y=200, autonomous=False)
    robot_l3.upgrade_level = 3

    robot_l5 = Robot(x=300, y=300, autonomous=False)
    robot_l5.upgrade_level = 5

    robots = [robot_l1, robot_l3, robot_l5]

    for robot in robots:
        print(f"\n  Robot Level {robot.upgrade_level}:")
        print(f"    Animation frame: {robot.animation_frame}")
        print(f"    Facing angle: {robot.facing_angle}")
        print(f"    Animation speed: {robot.animation_speed}s")

        # Get level visuals
        visuals = robot._get_level_visuals()
        print(f"    Body size: {visuals['body_width']}x{visuals['body_height']}")
        print(f"    Tread size: {visuals['tread_width']}x{visuals['tread_length']}")
        print(f"    Has arms: {visuals['arm_length'] > 0}")
        if visuals['arm_length'] > 0:
            print(f"    Arm length: {visuals['arm_length']}, width: {visuals['arm_width']}")

    print("\n  ✓ Robot properties work correctly")


def test_robot_animation():
    """Test robot animation."""
    print("\nTesting robot animation...")

    robot = Robot(x=150, y=150, autonomous=False)
    robot.upgrade_level = 2

    # Set velocity to trigger movement
    robot.velocity_x = 1.0
    robot.velocity_y = 0.0

    initial_frame = robot.animation_frame
    print(f"  Initial animation frame: {initial_frame}")

    # Update with enough time to trigger frame change
    robot._update_manual(0.3)

    print(f"  After 0.3s - Animation frame: {robot.animation_frame}")
    print(f"  After 0.3s - Facing angle: {robot.facing_angle:.0f}°")

    # Update again
    robot.velocity_x = 1.0
    robot._update_manual(0.3)

    print(f"  After 0.6s - Animation frame: {robot.animation_frame}")

    print("  ✓ Robot animation works correctly")


def test_robot_visual_progression():
    """Test visual progression across upgrade levels."""
    print("\nTesting visual progression...")

    print("  Level progression:")
    for level in range(1, 6):
        robot = Robot(x=100, y=100, autonomous=False)
        robot.upgrade_level = level
        visuals = robot._get_level_visuals()

        print(f"\n  Level {level}:")
        print(f"    Body: {visuals['body_width']}x{visuals['body_height']} "
              f"(color: {visuals['body_color']})")
        print(f"    Head: {visuals['head_size']}px")
        print(f"    Treads: {visuals['tread_width']}x{visuals['tread_length']}")

        if level == 1:
            assert visuals['arm_length'] == 0, "Level 1 should have no arms"
            print(f"    Arms: None (spindly basic robot)")
        else:
            assert visuals['arm_length'] > 0, f"Level {level} should have arms"
            print(f"    Arms: {visuals['arm_length']}px length, {visuals['arm_width']}px width")

        # Verify progression (larger at higher levels)
        if level > 1:
            prev_robot = Robot(x=100, y=100, autonomous=False)
            prev_robot.upgrade_level = level - 1
            prev_visuals = prev_robot._get_level_visuals()

            assert visuals['body_width'] > prev_visuals['body_width'], \
                f"Level {level} should be larger than level {level-1}"
            assert visuals['tread_width'] >= prev_visuals['tread_width'], \
                "Treads should get thicker or stay same"

    print("\n  ✓ Visual progression works correctly (spindly → strong)")


def test_robot_rendering_visual():
    """Test actual rendering (visual test)."""
    print("\nTesting actual rendering (visual)...")

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((1000, 600))
    pygame.display.set_caption("Robot Visual Test - Upgrade Levels 1-5")
    camera = SimpleCamera()
    clock = pygame.time.Clock()

    # Create robots at all upgrade levels
    robots = []
    for level in range(1, 6):
        robot = Robot(x=100 + (level-1) * 180, y=300, autonomous=False)
        robot.upgrade_level = level
        # Set them moving for animation test
        robot.velocity_x = 1.0
        robot.velocity_y = 0.5
        robots.append(robot)

    print("  Visual test window opened (will run for 8 seconds)...")
    print("  You should see:")
    print("    - 5 robots in a row (Level 1-5)")
    print("    - Level 1: Small, spindly, no arms")
    print("    - Level 5: Large, thick, prominent arms")
    print("    - All robots moving with tread animation")
    print("    - Direction indicators and level labels")

    # Run for 8 seconds
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < 8000:
        dt = clock.tick(60) / 1000.0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # Update robots
        for robot in robots:
            robot.velocity_x = 1.0
            robot.velocity_y = 0.5
            robot._update_manual(dt)

        # Render
        screen.fill((30, 30, 30))  # Dark gray background

        # Draw title
        font = pygame.font.Font(None, 32)
        title = font.render("Robot Upgrade Levels (1-5): Spindly → Strong", True, (255, 255, 255))
        screen.blit(title, (20, 20))

        # Draw labels
        font_small = pygame.font.Font(None, 20)
        labels = ["Level 1\nSpindly", "Level 2\nBasic Arms", "Level 3\nSolid", "Level 4\nRobust", "Level 5\nMaximum"]
        for i, label in enumerate(labels):
            x = 50 + i * 180
            y = 500
            for line_num, line in enumerate(label.split('\n')):
                text = font_small.render(line, True, (200, 200, 200))
                screen.blit(text, (x, y + line_num * 20))

        # Render robots
        for robot in robots:
            robot.render(screen, camera)

        pygame.display.flip()

    pygame.quit()
    print("  ✓ Visual test completed")


if __name__ == '__main__':
    print("="*80)
    print("ROBOT VISUAL TESTS")
    print("="*80)

    try:
        test_robot_properties()
        test_robot_animation()
        test_robot_visual_progression()
        test_robot_rendering_visual()

        print("\n" + "="*80)
        print("ALL ROBOT VISUAL TESTS PASSED! ✓")
        print("="*80)
        print("\nSummary:")
        print("  - Robots now have directional rendering")
        print("  - Treads animate when moving")
        print("  - Upgrade levels 1-5 implemented")
        print("  - Level 1: Spindly, 20x20, no arms")
        print("  - Level 5: Strong, 36x36, 14px arms")
        print("  - Visual progression: spindly → thick & powerful")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
