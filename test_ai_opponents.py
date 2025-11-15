"""
AI Opponent System Test - Demonstrates competitive gameplay.

Run this to see AI factories competing against each other in real-time.
"""

import pygame
import sys

# Add src to path
sys.path.insert(0, 'src')

from systems.ai_opponent_manager import (
    get_ai_opponent_manager, reset_ai_opponent_manager,
    GameMode, WinCondition
)
from ui.competitor_ui import CompetitorPanel, MarketPanel, OpponentDetailPanel


def test_ai_opponents():
    """Test and demonstrate AI opponent competition."""
    pygame.init()

    # Create display
    screen = pygame.display.set_mode((1400, 900))
    pygame.display.set_caption("Factory AI - Competitive Mode Demo")
    clock = pygame.time.Clock()

    # Create AI opponent manager
    reset_ai_opponent_manager()
    ai_manager = get_ai_opponent_manager(
        num_opponents=4,
        game_mode=GameMode.COMPETITIVE,
        win_condition=WinCondition.NET_WORTH
    )

    # Create UI panels
    leaderboard_panel = CompetitorPanel(x=20, y=20, width=350, height=600)
    market_panel = MarketPanel(x=20, y=640, width=350, height=240)
    detail_panel = OpponentDetailPanel(x=400, y=20, width=400, height=400)

    # Mock player factory (simulated)
    player_factory = {
        'name': 'Player',
        'money': 50000,
        'net_worth': 50000,
        'profit': 0,
        'robots': 2,
        'workstations': 1,
        'technology_level': 1,
        'market_share': 0.0,
        'sales': 0,
        'age': 0.0,
    }

    # Test state
    running = True
    paused = False
    time_scale = 1.0
    selected_opponent_idx = None

    # Fonts
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 20)

    print("=" * 80)
    print("AI OPPONENT SYSTEM DEMO")
    print("=" * 80)
    print("\nDemonstrating:")
    print("  - 4 AI opponents with different personalities")
    print("  - Competitive market with dynamic prices")
    print("  - Real-time decision-making and strategy")
    print("  - Rankings and leaderboard")
    print("  - Win conditions")
    print("\nControls:")
    print("  SPACE: Pause/Resume")
    print("  UP/DOWN: Adjust simulation speed")
    print("  1-4: View opponent details")
    print("  H: Hide/Show detail panel")
    print("  ESC: Exit")
    print("=" * 80)

    while running:
        dt = clock.tick(60) / 1000.0 * time_scale  # Delta time with time scale

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_UP:
                    time_scale = min(5.0, time_scale + 0.5)
                    print(f"Speed: {time_scale}x")
                elif event.key == pygame.K_DOWN:
                    time_scale = max(0.5, time_scale - 0.5)
                    print(f"Speed: {time_scale}x")
                elif event.key == pygame.K_h:
                    detail_panel.toggle()
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    selected_opponent_idx = event.key - pygame.K_1
                    detail_panel.visible = True

        # Update simulation
        if not paused:
            # Simple player growth simulation
            player_factory['age'] += dt
            player_factory['money'] += 100 * dt  # $100/sec income
            player_factory['net_worth'] = player_factory['money']

            # Update AI opponents
            ai_manager.update(dt, player_factory)

        # Get data for rendering
        leaderboard = ai_manager.get_leaderboard()
        market_data = ai_manager.get_statistics()
        market_conditions = ai_manager.get_market_conditions()
        market_data.update(market_conditions)

        # Clear screen
        screen.fill((30, 30, 40))

        # Draw title
        title = font_large.render("AI Opponent Competition", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 20))

        # Draw status
        status_y = 80
        if ai_manager.winner:
            winner_text = font_medium.render(f"WINNER: {ai_manager.winner}!", True, (255, 215, 0))
            screen.blit(winner_text, (screen.get_width()//2 - winner_text.get_width()//2, status_y))
        else:
            time_text = font_small.render(f"Time: {int(ai_manager.time_elapsed)}s", True, (200, 200, 200))
            screen.blit(time_text, (screen.get_width()//2 - time_text.get_width()//2, status_y))

        # Draw panels
        leaderboard_panel.render(screen, leaderboard)
        market_panel.render(screen, market_data)

        # Draw opponent details if selected
        if selected_opponent_idx is not None and selected_opponent_idx < len(ai_manager.opponents):
            opponent = ai_manager.opponents[selected_opponent_idx]
            detail_panel.render(screen, opponent.get_statistics())

        # Draw visualization area (center)
        viz_x = 420
        viz_y = 450
        viz_width = 960
        viz_height = 430

        # Background
        pygame.draw.rect(screen, (50, 50, 60), (viz_x, viz_y, viz_width, viz_height), border_radius=10)
        pygame.draw.rect(screen, (100, 100, 120), (viz_x, viz_y, viz_width, viz_height), 2, border_radius=10)

        # Draw opponent factories as bars
        bar_y = viz_y + 50
        bar_height = 40
        bar_spacing = 60

        viz_title = font_medium.render("Factory Comparison", True, (255, 255, 255))
        screen.blit(viz_title, (viz_x + viz_width//2 - viz_title.get_width()//2, viz_y + 10))

        # Get max values for scaling
        all_factories = [player_factory] + [opp.get_statistics() for opp in ai_manager.opponents]
        max_money = max(f.get('money', f.get('net_worth', 1)) for f in all_factories)
        max_robots = max(f.get('robots', 1) for f in all_factories)
        max_workstations = max(f.get('workstations', 1) for f in all_factories)

        for i, factory in enumerate(all_factories):
            name = factory.get('name', 'Unknown')
            money = factory.get('money', factory.get('net_worth', 0))
            robots = factory.get('robots', 0)
            workstations = factory.get('workstations', 0)

            is_player = (name == "Player")
            color = (100, 255, 100) if is_player else (100, 150, 255)

            # Name
            name_text = font_small.render(name[:20], True, (255, 255, 255))
            screen.blit(name_text, (viz_x + 20, bar_y + i * bar_spacing))

            # Money bar
            bar_width = int((money / max_money) * (viz_width - 250))
            pygame.draw.rect(screen, color, (viz_x + 200, bar_y + i * bar_spacing, bar_width, bar_height), border_radius=5)
            pygame.draw.rect(screen, (200, 200, 200), (viz_x + 200, bar_y + i * bar_spacing, viz_width - 250, bar_height), 2, border_radius=5)

            # Value text
            value_text = font_small.render(f"${money:,}", True, (255, 255, 255))
            screen.blit(value_text, (viz_x + 220, bar_y + i * bar_spacing + 12))

            # Stats
            stats_text = font_small.render(f"R:{robots} | M:{workstations}", True, (200, 200, 200))
            screen.blit(stats_text, (viz_x + viz_width - 150, bar_y + i * bar_spacing + 12))

        # Draw instructions
        instructions = [
            "SPACE: Pause/Resume",
            "UP/DOWN: Speed",
            "1-4: View Opponent",
            "H: Hide/Show Details",
        ]

        inst_x = viz_x + 20
        inst_y = screen.get_height() - 100
        for instruction in instructions:
            inst_text = font_small.render(instruction, True, (150, 150, 150))
            screen.blit(inst_text, (inst_x, inst_y))
            inst_y += 20

        # Simulation speed indicator
        speed_text = font_small.render(f"Speed: {time_scale}x", True, (255, 255, 100))
        screen.blit(speed_text, (screen.get_width() - 150, screen.get_height() - 40))

        # Pause indicator
        if paused:
            pause_text = font_large.render("PAUSED", True, (255, 100, 100))
            screen.blit(pause_text, (screen.get_width()//2 - pause_text.get_width()//2, screen.get_height()//2))

        # FPS counter
        fps_text = font_small.render(f"FPS: {int(clock.get_fps())}", True, (100, 255, 100))
        screen.blit(fps_text, (screen.get_width() - 100, 20))

        # Update display
        pygame.display.flip()

    pygame.quit()
    print("\nAI opponent demo completed!")
    print(f"Final statistics: {ai_manager.get_statistics()}")


if __name__ == "__main__":
    try:
        test_ai_opponents()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        pygame.quit()
        sys.exit(0)
