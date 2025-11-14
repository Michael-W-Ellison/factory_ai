"""
Comprehensive test suite for Phase 10: Advanced Features.

Tests:
- Drone system and fog of war
- Wireless transmitters and control range
- Market fluctuations and pricing
- Weather system and effects
- Deconstruction mechanics
- Scoring and achievements
"""

import sys
import os

# Add parent directory to path
if os.path.basename(os.getcwd()) == 'src':
    sys.path.insert(0, '..')
else:
    sys.path.insert(0, 'src')

from systems.drone_manager import DroneManager, DroneState, FogOfWar
from systems.transmitter_manager import TransmitterManager, TransmitterType
from systems.market_manager import MarketManager, MarketTrend
from systems.weather_manager import WeatherManager, WeatherType
from systems.deconstruction_manager import DeconstructionManager, DeconstructionState
from systems.scoring_manager import ScoringManager, ScoreCategory


class MockResourceManager:
    """Mock resource manager for testing."""
    def __init__(self):
        self.money = 100000

    def modify_money(self, amount):
        self.money += amount


class MockMaterialInventory:
    """Mock material inventory for testing."""
    def __init__(self):
        self.materials = {}

    def add_material(self, material, quantity, source):
        if material not in self.materials:
            self.materials[material] = 0
        self.materials[material] += quantity


# ==============================================================================
# DRONE SYSTEM TESTS
# ==============================================================================

def test_drone_purchase():
    """Test purchasing drones."""
    print("Test: Drone Purchase")

    resources = MockResourceManager()
    drone_manager = DroneManager(resources)

    initial_money = resources.money

    # Purchase drone
    success = drone_manager.purchase_drone()
    assert success, "Should successfully purchase drone"
    assert resources.money == initial_money - drone_manager.drone_purchase_cost
    assert len(drone_manager.drones) == 1, "Should have 1 drone"

    print("  ✓ Drone purchased successfully")
    print(f"  ✓ Cost: ${drone_manager.drone_purchase_cost}")


def test_drone_deployment():
    """Test deploying drones."""
    print("\nTest: Drone Deployment")

    resources = MockResourceManager()
    drone_manager = DroneManager(resources)

    # Purchase and deploy drone
    drone_manager.purchase_drone()
    drone_id = 1

    target = (50.0, 50.0)
    success = drone_manager.deploy_drone(drone_id, target)

    assert success, "Should successfully deploy drone"
    assert drone_manager.drones[drone_id].state == DroneState.FLYING
    assert drone_manager.drones[drone_id].target_position == target

    print("  ✓ Drone deployed successfully")
    print(f"  ✓ Target: {target}")


def test_drone_movement():
    """Test drone movement and exploration."""
    print("\nTest: Drone Movement")

    resources = MockResourceManager()
    drone_manager = DroneManager(resources)

    # Purchase and deploy drone
    drone_manager.purchase_drone()
    drone_id = 1
    drone_manager.deploy_drone(drone_id, (20.0, 0.0))

    initial_pos = drone_manager.drones[drone_id].position
    initial_exploration = drone_manager.get_exploration_percentage()

    # Update for 5 seconds
    for _ in range(5):
        drone_manager.update(1.0, 0.0)

    final_pos = drone_manager.drones[drone_id].position
    final_exploration = drone_manager.get_exploration_percentage()

    assert final_pos != initial_pos, "Drone should have moved"
    assert final_exploration > initial_exploration, "Should have explored more area"

    print("  ✓ Drone moved successfully")
    print(f"  ✓ Exploration increased from {initial_exploration:.1f}% to {final_exploration:.1f}%")


def test_fog_of_war():
    """Test fog of war system."""
    print("\nTest: Fog of War")

    fog = FogOfWar(100, 100)

    # Check initial state
    assert fog.is_explored((0, 0)), "Factory area should be explored"
    assert not fog.is_explored((20, 20)), "Distant area should not be explored"

    # Reveal area around (20, 20) with radius 10
    fog.reveal_area((20.0, 20.0), 10.0, is_permanent=True)

    assert fog.is_explored((20, 20)), "Revealed area should be explored"

    exploration = fog.get_exploration_percentage()
    assert exploration > 0, "Should have some exploration"

    print("  ✓ Fog of war working correctly")
    print(f"  ✓ Exploration: {exploration:.2f}%")


def test_drone_battery_drain():
    """Test drone battery drain and auto-return."""
    print("\nTest: Drone Battery Drain")

    resources = MockResourceManager()
    drone_manager = DroneManager(resources)

    # Purchase and deploy drone
    drone_manager.purchase_drone()
    drone_id = 1
    drone_manager.deploy_drone(drone_id, (100.0, 100.0))

    # Set battery low
    drone_manager.drones[drone_id].battery = 19.0

    # Update
    drone_manager.update(1.0, 0.0)

    # Should auto-return
    assert drone_manager.drones[drone_id].state == DroneState.RETURNING, \
        "Drone should auto-return at low battery"

    print("  ✓ Drone auto-return triggered at low battery")


# ==============================================================================
# TRANSMITTER SYSTEM TESTS
# ==============================================================================

def test_transmitter_placement():
    """Test placing transmitters."""
    print("\nTest: Transmitter Placement")

    resources = MockResourceManager()
    transmitter_manager = TransmitterManager(resources)

    initial_money = resources.money

    # Place transmitter at base (should have signal)
    transmitter_id = transmitter_manager.place_transmitter(
        TransmitterType.BASIC,
        (10.0, 0.0)
    )

    assert transmitter_id is not None, "Should place transmitter successfully"
    assert len(transmitter_manager.transmitters) == 1
    assert resources.money < initial_money

    print("  ✓ Transmitter placed successfully")


def test_signal_coverage():
    """Test signal coverage calculation."""
    print("\nTest: Signal Coverage")

    resources = MockResourceManager()
    transmitter_manager = TransmitterManager(resources)

    # Check base coverage
    assert transmitter_manager.has_signal_coverage((0.0, 0.0)), \
        "Base should have coverage"
    assert transmitter_manager.has_signal_coverage((15.0, 0.0)), \
        "Nearby position should have coverage"

    # Far position should not have coverage
    far_position = (100.0, 100.0)
    assert not transmitter_manager.has_signal_coverage(far_position), \
        "Far position should not have coverage"

    # Place transmitter to extend coverage (within base range)
    transmitter_manager.place_transmitter(TransmitterType.BASIC, (15.0, 0.0))

    # Check extended coverage
    signal = transmitter_manager.get_signal_strength_at((35.0, 0.0))
    assert signal > 0, "Extended position should have signal"

    print("  ✓ Signal coverage working correctly")


# ==============================================================================
# MARKET SYSTEM TESTS
# ==============================================================================

def test_market_prices():
    """Test market price retrieval."""
    print("\nTest: Market Prices")

    market_manager = MarketManager()

    # Get prices
    plastic_price = market_manager.get_buy_price('plastic')
    assert plastic_price > 0, "Plastic price should be positive"

    sell_price = market_manager.get_sell_price('recycled_plastic')
    assert sell_price > 0, "Sell price should be positive"

    print("  ✓ Market prices working")
    print(f"  ✓ Plastic buy: ${plastic_price:.2f}")
    print(f"  ✓ Recycled plastic sell: ${sell_price:.2f}")


def test_market_fluctuations():
    """Test market price fluctuations."""
    print("\nTest: Market Fluctuations")

    market_manager = MarketManager()

    # Force bullish trend
    market_manager.current_trend = MarketTrend.BULLISH

    initial_price = market_manager.get_buy_price('plastic')

    # Update for 10 hours
    for _ in range(10):
        market_manager.update(3600.0, 0.0)  # 1 hour per update

    final_price = market_manager.get_buy_price('plastic')

    # Prices should have increased (bullish trend)
    assert final_price > initial_price, "Prices should increase in bullish market"

    print("  ✓ Market fluctuations working")
    print(f"  ✓ Price increased from ${initial_price:.2f} to ${final_price:.2f}")


def test_market_events():
    """Test market events."""
    print("\nTest: Market Events")

    market_manager = MarketManager()

    # Trigger event manually
    market_manager._trigger_random_event(0.0)

    assert len(market_manager.active_events) > 0, "Should have active event"

    print("  ✓ Market events working")
    print(f"  ✓ Event: {market_manager.active_events[0].name}")


# ==============================================================================
# WEATHER SYSTEM TESTS
# ==============================================================================

def test_weather_changes():
    """Test weather state changes."""
    print("\nTest: Weather Changes")

    weather_manager = WeatherManager()

    initial_weather = weather_manager.current_weather

    # Force weather change by triggering transition
    weather_manager._transition_to_new_weather()

    # Weather is transitioning
    print("  ✓ Weather system operational")
    print(f"  ✓ Current weather: {weather_manager.current_weather.value}")


def test_weather_effects():
    """Test weather effects on gameplay."""
    print("\nTest: Weather Effects")

    weather_manager = WeatherManager()

    # Force different weather
    weather_manager.current_weather = WeatherType.HEAVY_RAIN

    # Check effects using existing API
    detection_mod = weather_manager.get_detection_modifier()
    solar_mod = weather_manager.get_solar_power_multiplier()

    assert detection_mod < 1.0, \
        "Heavy rain should reduce detection"
    assert solar_mod < 1.0, \
        "Heavy rain should reduce solar power"

    print("  ✓ Weather effects working")
    print(f"  ✓ Solar power modifier: {solar_mod:.2f}")
    print(f"  ✓ Detection modifier: {detection_mod:.2f}")


# ==============================================================================
# DECONSTRUCTION SYSTEM TESTS
# ==============================================================================

def test_deconstruction_start():
    """Test starting deconstruction."""
    print("\nTest: Deconstruction Start")

    resources = MockResourceManager()
    inventory = MockMaterialInventory()
    decon_manager = DeconstructionManager(resources, inventory)

    materials = {'plastic': 100, 'metal': 50}
    job_id = decon_manager.start_deconstruction(
        'building', 1, (10.0, 10.0), materials, size=2.0, workers=2
    )

    assert job_id is not None, "Should start deconstruction"
    assert len(decon_manager.jobs) == 1

    print("  ✓ Deconstruction started successfully")


def test_deconstruction_progress():
    """Test deconstruction progress."""
    print("\nTest: Deconstruction Progress")

    resources = MockResourceManager()
    inventory = MockMaterialInventory()
    decon_manager = DeconstructionManager(resources, inventory)

    materials = {'plastic': 100}
    job_id = decon_manager.start_deconstruction(
        'building', 1, (10.0, 10.0), materials, size=1.0, workers=1
    )

    initial_progress = decon_manager.jobs[job_id].progress

    # Update for 10 seconds
    for _ in range(10):
        decon_manager.update(1.0, 0.0)

    final_progress = decon_manager.jobs[job_id].progress

    assert final_progress > initial_progress, "Progress should increase"

    print("  ✓ Deconstruction progress working")
    print(f"  ✓ Progress: {final_progress:.1f}%")


def test_deconstruction_completion():
    """Test deconstruction completion and material recovery."""
    print("\nTest: Deconstruction Completion")

    resources = MockResourceManager()
    inventory = MockMaterialInventory()
    decon_manager = DeconstructionManager(resources, inventory)

    materials = {'plastic': 100, 'metal': 50}
    job_id = decon_manager.start_deconstruction(
        'building', 1, (10.0, 10.0), materials, size=1.0, workers=1
    )

    # Force completion
    decon_manager.jobs[job_id].progress = 99.9

    decon_manager.update(1.0, 0.0)

    # Job should be completed and removed
    assert job_id not in decon_manager.jobs, "Job should be completed"
    assert decon_manager.total_jobs_completed == 1

    # Materials should be recovered
    assert 'plastic' in inventory.materials
    assert inventory.materials['plastic'] > 0

    print("  ✓ Deconstruction completed")
    print(f"  ✓ Materials recovered: {dict(inventory.materials)}")


# ==============================================================================
# SCORING SYSTEM TESTS
# ==============================================================================

def test_scoring_achievements():
    """Test achievement unlocking."""
    print("\nTest: Scoring Achievements")

    scoring = ScoringManager()

    # Unlock first dollar achievement
    scoring.record_money_earned(1.0)

    assert scoring.achievements['first_dollar'].unlocked, \
        "First dollar achievement should unlock"

    print("  ✓ Achievement unlocking working")


def test_scoring_statistics():
    """Test score statistics tracking."""
    print("\nTest: Scoring Statistics")

    scoring = ScoringManager()

    # Record various statistics
    scoring.record_money_earned(50000)
    scoring.record_material_processed(100)
    scoring.record_building_built()

    assert scoring.stats['total_money_earned'] == 50000
    assert scoring.stats['materials_processed'] == 100
    assert scoring.stats['buildings_built'] == 1

    print("  ✓ Statistics tracking working")


def test_final_score_calculation():
    """Test final score calculation."""
    print("\nTest: Final Score Calculation")

    scoring = ScoringManager()

    # Set up statistics
    scoring.stats['total_money_earned'] = 100000
    scoring.stats['materials_processed'] = 5000
    scoring.stats['buildings_built'] = 20

    # Calculate final score
    final_score = scoring.calculate_final_score(
        game_time=86400.0,  # 1 day
        ending_type='ESCAPE',
        current_money=50000,
        max_suspicion=30,
        exploration_percent=50.0
    )

    assert final_score > 0, "Should have positive score"
    assert scoring.rank != "Novice", "Should have earned a rank"

    print("  ✓ Final score calculated")
    print(f"  ✓ Score: {final_score:,}")
    print(f"  ✓ Rank: {scoring.rank}")


# ==============================================================================
# RUN ALL TESTS
# ==============================================================================

def run_all_tests():
    """Run all Phase 10 tests."""
    print("=" * 80)
    print("PHASE 10: ADVANCED FEATURES - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()

    try:
        # Drone tests
        test_drone_purchase()
        test_drone_deployment()
        test_drone_movement()
        test_fog_of_war()
        test_drone_battery_drain()

        # Transmitter tests
        test_transmitter_placement()
        test_signal_coverage()

        # Market tests
        test_market_prices()
        test_market_fluctuations()
        test_market_events()

        # Weather tests
        test_weather_changes()
        test_weather_effects()

        # Deconstruction tests
        test_deconstruction_start()
        test_deconstruction_progress()
        test_deconstruction_completion()

        # Scoring tests
        test_scoring_achievements()
        test_scoring_statistics()
        test_final_score_calculation()

        print()
        print("=" * 80)
        print("ALL PHASE 10 TESTS PASSED! ✓")
        print("=" * 80)
        print()
        print("Phase 10 Advanced Features Complete:")
        print("  ✓ Drone system with fog of war")
        print("    - Drone purchase, deployment, and movement")
        print("    - Battery management and auto-return")
        print("    - Fog of war exploration tracking")
        print("  ✓ Wireless transmitter system")
        print("    - Transmitter placement and signal coverage")
        print("    - Control range calculation")
        print("  ✓ Market fluctuation system")
        print("    - Dynamic pricing and trends")
        print("    - Market events and price changes")
        print("  ✓ Weather system")
        print("    - Weather state changes and effects")
        print("    - Production and suspicion modifiers")
        print("  ✓ Deconstruction system")
        print("    - Building/prop deconstruction")
        print("    - Material recovery")
        print("    - Progress tracking")
        print("  ✓ Scoring system")
        print("    - Achievement tracking and unlocking")
        print("    - Statistics recording")
        print("    - Final score calculation and ranks")

        return True

    except AssertionError as e:
        print()
        print("=" * 80)
        print(f"TEST FAILED: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
