"""
Phase 10 Test Suite: Advanced Features
Tests drone system, weather system, and wireless transmitter/control range.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from entities.drone import Drone, DroneState
from systems.weather_manager import WeatherManager, WeatherType
from systems.control_range_manager import ControlRangeManager


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


def test_drone_battery_drain():
    """Test drone battery drains during flight."""
    print_test_header("Drone Battery Drain")

    # Create drone
    drone = Drone("drone1", 100, 100)
    initial_battery = drone.battery

    # Set manual target to start flying
    drone.set_manual_target(500, 500)

    # Update for 60 seconds (should drain battery)
    drone.update(60.0)

    assert drone.battery < initial_battery, "Battery should drain during flight"
    assert drone.state in [DroneState.MANUAL, DroneState.RETURNING], "Should be flying or returning"

    print(f"Initial battery: {initial_battery}s")
    print(f"After 60s flight: {drone.battery}s")
    print(f"Battery drained: {initial_battery - drone.battery}s")

    return print_test_result(True, "- Battery drains correctly during flight")


def test_drone_low_battery_return():
    """Test drone returns to pad when battery low."""
    print_test_header("Drone Low Battery Return")

    # Create drone with drone pad
    class MockDronePad:
        def __init__(self):
            self.x = 100
            self.y = 100

    pad = MockDronePad()
    # Start drone AWAY from pad
    drone = Drone("drone2", 500, 500, drone_pad=pad)

    # Drain battery to near low threshold
    drone.battery = drone.low_battery_threshold + 10

    # Start patrol away from pad
    drone.start_patrol([(600, 600), (700, 700)])

    # Update until battery is low (should trigger return)
    drone.update(15.0)  # Drain 15 more seconds

    assert drone.state == DroneState.RETURNING, f"Should be returning, but is {drone.state}"
    assert drone.target_x == pad.x, "Should be targeting pad x"
    assert drone.target_y == pad.y, "Should be targeting pad y"

    print(f"Battery at return trigger: {drone.battery}s")
    print(f"Low battery threshold: {drone.low_battery_threshold}s")
    print(f"Drone position: ({drone.x:.1f}, {drone.y:.1f})")
    print(f"Target (pad): ({drone.target_x}, {drone.target_y})")

    return print_test_result(True, "- Drone returns to pad on low battery")


def test_drone_charging():
    """Test drone charges at pad."""
    print_test_header("Drone Charging")

    class MockDronePad:
        def __init__(self):
            self.x = 100
            self.y = 100

    pad = MockDronePad()
    drone = Drone("drone3", 100, 100, drone_pad=pad)

    # Drain battery
    drone.battery = drone.max_battery * 0.5

    # Set to charging
    drone.state = DroneState.CHARGING
    initial_battery = drone.battery

    # Update for 60 seconds
    drone.update(60.0)

    assert drone.battery > initial_battery, "Battery should charge"
    assert drone.battery <= drone.max_battery, "Battery shouldn't exceed max"

    print(f"Initial battery: {initial_battery}s ({initial_battery / drone.max_battery * 100:.1f}%)")
    print(f"After 60s charge: {drone.battery}s ({drone.battery / drone.max_battery * 100:.1f}%)")
    print(f"Charge rate: {drone.charge_rate}x drain rate")

    return print_test_result(True, "- Drone charges correctly at pad")


def test_drone_movement():
    """Test drone moves towards target."""
    print_test_header("Drone Movement")

    drone = Drone("drone4", 0, 0)
    drone.set_manual_target(200, 0)  # Move 200 pixels right

    # Update for 1 second (speed = 200 px/s, should reach in 1 second)
    drone.update(1.0)

    # Small additional update to ensure target is cleared
    drone.update(0.01)

    # Should reach target in 1 second
    assert abs(drone.x - 200) < 5, f"Should be near target, but at {drone.x}"
    assert drone.target_x is None, f"Target should be cleared when reached, but is {drone.target_x}"

    print(f"Drone speed: {drone.speed} px/s")
    print(f"Distance traveled: {drone.total_distance_traveled:.1f} px")
    print(f"Final position: ({drone.x:.1f}, {drone.y:.1f})")

    return print_test_result(True, "- Drone moves correctly to target")


def test_drone_patrol():
    """Test drone follows patrol route."""
    print_test_header("Drone Patrol Route")

    drone = Drone("drone5", 0, 0)
    route = [(100, 0), (100, 100), (0, 100), (0, 0)]
    drone.start_patrol(route)

    assert drone.state == DroneState.PATROL, "Should be in patrol state"
    assert len(drone.patrol_route) == 4, "Should have 4 waypoints"

    print(f"Patrol route: {len(drone.patrol_route)} waypoints")
    print(f"First waypoint: {drone.patrol_route[0]}")
    print(f"Drone state: {drone.state.value}")

    return print_test_result(True, "- Drone patrol system works")


def test_weather_system_transitions():
    """Test weather transitions between types."""
    print_test_header("Weather System Transitions")

    weather_mgr = WeatherManager()
    initial_weather = weather_mgr.current_weather

    # Force weather duration to complete
    weather_mgr.weather_elapsed = weather_mgr.weather_duration + 1

    # Update to trigger transition
    weather_mgr.update(1.0, 0.0)

    assert weather_mgr.transitioning, "Should be transitioning"
    assert weather_mgr.next_weather is not None, "Should have next weather"
    assert weather_mgr.next_weather != initial_weather, "Should transition to different weather"

    print(f"Initial weather: {initial_weather.value}")
    print(f"Transitioning to: {weather_mgr.next_weather.value}")
    print(f"Transition duration: {weather_mgr.transition_duration}s")

    return print_test_result(True, "- Weather transitions correctly")


def test_weather_effects():
    """Test weather effects on gameplay."""
    print_test_header("Weather Effects")

    weather_mgr = WeatherManager()

    # Test different weather types
    test_cases = [
        (WeatherType.CLEAR, 1.0, 1.0, 1.0),
        (WeatherType.RAIN, 0.5, 0.8, 0.95),
        (WeatherType.FOG, 0.6, 0.4, 0.9),
        (WeatherType.STORM, 0.1, 1.5, 0.7),
    ]

    all_passed = True
    for weather, expected_solar, expected_detection, expected_speed in test_cases:
        weather_mgr._set_weather(weather, 3600)

        solar = weather_mgr.get_solar_power_multiplier()
        detection = weather_mgr.get_detection_modifier()
        speed = weather_mgr.get_robot_speed_multiplier()

        print(f"\n{weather.value}:")
        print(f"  Solar power: {solar:.1f}x (expected {expected_solar}x)")
        print(f"  Detection: {detection:.1f}x (expected {expected_detection}x)")
        print(f"  Robot speed: {speed:.1f}x (expected {expected_speed}x)")

        if solar != expected_solar or detection != expected_detection or speed != expected_speed:
            all_passed = False

    return print_test_result(all_passed, "- Weather effects applied correctly")


def test_weather_forecast():
    """Test weather forecasting system."""
    print_test_header("Weather Forecast")

    weather_mgr = WeatherManager()

    # Initially no forecast
    forecast = weather_mgr.get_forecast()
    assert len(forecast) == 0, "Forecast should be empty without research"

    # Enable forecast (simulating research completion)
    weather_mgr.enable_forecast()

    # Get forecast
    forecast = weather_mgr.get_forecast()
    assert len(forecast) > 0, "Forecast should have entries"

    print(f"Forecast enabled: {weather_mgr.forecast_enabled}")
    print(f"Forecast entries: {len(forecast)}")
    print("\nForecast preview:")
    for i, (weather, duration) in enumerate(forecast[:5]):
        hours = duration / 3600
        print(f"  {i+1}. {weather.value} for {hours:.1f} hours")

    return print_test_result(True, "- Weather forecast system works")


def test_weather_stealth_detection():
    """Test stealth weather detection."""
    print_test_header("Weather Stealth Detection")

    weather_mgr = WeatherManager()

    # Test stealth-friendly weather
    stealth_weather = [WeatherType.FOG, WeatherType.RAIN, WeatherType.HEAVY_RAIN]
    bad_weather = [WeatherType.CLEAR, WeatherType.STORM]

    all_passed = True

    for weather in stealth_weather:
        weather_mgr._set_weather(weather, 3600)
        is_good = weather_mgr.is_good_weather_for_stealth()
        print(f"{weather.value}: {'✓' if is_good else '✗'} good for stealth")
        if not is_good:
            all_passed = False

    for weather in bad_weather:
        weather_mgr._set_weather(weather, 3600)
        is_good = weather_mgr.is_good_weather_for_stealth()
        print(f"{weather.value}: {'✓' if not is_good else '✗'} bad for stealth")
        if is_good:
            all_passed = False

    return print_test_result(all_passed, "- Stealth weather detection works")


def test_control_range_factory():
    """Test factory base control range."""
    print_test_header("Factory Control Range")

    control_mgr = ControlRangeManager(factory_x=500, factory_y=500)

    # Test points within range
    assert control_mgr.is_in_control_range(500, 500), "Factory center should be in range"
    assert control_mgr.is_in_control_range(600, 500), "100 tiles away should be in range"
    assert control_mgr.is_in_control_range(500, 700), "200 tiles away should be in range"

    # Test points outside range
    assert not control_mgr.is_in_control_range(500, 800), "300 tiles away should be out of range"
    assert not control_mgr.is_in_control_range(1000, 500), "500 tiles away should be out of range"

    print(f"Factory position: ({control_mgr.factory_x}, {control_mgr.factory_y})")
    print(f"Factory range: {control_mgr.factory_base_range} tiles")
    print(f"Test point (600, 500): {'IN' if control_mgr.is_in_control_range(600, 500) else 'OUT'}")
    print(f"Test point (500, 800): {'IN' if control_mgr.is_in_control_range(500, 800) else 'OUT'}")

    return print_test_result(True, "- Factory control range works")


def test_control_range_transmitter():
    """Test wireless transmitter extends range."""
    print_test_header("Wireless Transmitter Range")

    control_mgr = ControlRangeManager(factory_x=0, factory_y=0)

    # Point far from factory (out of range)
    test_x, test_y = 1000, 1000
    assert not control_mgr.is_in_control_range(test_x, test_y), "Should be out of factory range"

    # Add transmitter near test point
    control_mgr.add_transmitter(x=1000, y=1000, level=1)  # Range 300

    # Now should be in range
    assert control_mgr.is_in_control_range(test_x, test_y), "Should be in transmitter range"
    assert control_mgr.is_in_control_range(1200, 1000), "Should be in transmitter range (200 away)"

    print(f"Factory range: {control_mgr.factory_base_range} tiles")
    print(f"Transmitters: {len(control_mgr.transmitters)}")
    print(f"Transmitter 1 range: {control_mgr.transmitters[0][2]} tiles")
    print(f"Point (1000, 1000) in range: {control_mgr.is_in_control_range(1000, 1000)}")

    return print_test_result(True, "- Wireless transmitter extends range")


def test_control_range_levels():
    """Test transmitter research levels."""
    print_test_header("Transmitter Research Levels")

    control_mgr = ControlRangeManager(factory_x=0, factory_y=0)

    # Add transmitters of different levels
    control_mgr.add_transmitter(x=500, y=0, level=1)  # Range 300
    control_mgr.add_transmitter(x=1000, y=0, level=2)  # Range 450
    control_mgr.add_transmitter(x=1500, y=0, level=3)  # Range 600

    assert len(control_mgr.transmitters) == 3, "Should have 3 transmitters"

    # Check ranges
    level1_range = control_mgr.transmitters[0][2]
    level2_range = control_mgr.transmitters[1][2]
    level3_range = control_mgr.transmitters[2][2]

    assert level1_range == 300, f"Level 1 should have 300 range, got {level1_range}"
    assert level2_range == 450, f"Level 2 should have 450 range, got {level2_range}"
    assert level3_range == 600, f"Level 3 should have 600 range, got {level3_range}"

    print("Transmitter levels and ranges:")
    for i, (x, y, r, level) in enumerate(control_mgr.transmitters):
        print(f"  {i+1}. Level {level}: Range {r} tiles at ({x}, {y})")

    return print_test_result(True, "- Transmitter levels work correctly")


def test_control_range_distance():
    """Test distance to control range calculation."""
    print_test_header("Distance to Control Range")

    control_mgr = ControlRangeManager(factory_x=0, factory_y=0)

    # Point inside range
    dist_inside = control_mgr.get_distance_to_control_range(50, 0)
    assert dist_inside == 0, f"Point inside should have 0 distance, got {dist_inside}"

    # Point outside range
    dist_outside = control_mgr.get_distance_to_control_range(300, 0)
    assert dist_outside > 0, f"Point outside should have positive distance, got {dist_outside}"
    assert abs(dist_outside - 100) < 1, f"Expected ~100 distance, got {dist_outside}"

    print(f"Factory range: {control_mgr.factory_base_range} tiles")
    print(f"Point (50, 0) distance to range: {dist_inside:.1f}")
    print(f"Point (300, 0) distance to range: {dist_outside:.1f}")

    return print_test_result(True, "- Distance calculation works")


def test_control_range_coverage():
    """Test control coverage percentage."""
    print_test_header("Control Coverage Percentage")

    control_mgr = ControlRangeManager(factory_x=500, factory_y=500)

    # Test small area around factory (should be 100%)
    coverage_full = control_mgr.get_control_coverage_percent(400, 400, 600, 600, sample_points=50)
    assert coverage_full > 95, f"Small area should be fully covered, got {coverage_full}%"

    # Test large area (should be partial)
    coverage_partial = control_mgr.get_control_coverage_percent(0, 0, 2000, 2000, sample_points=100)
    assert 0 < coverage_partial < 100, f"Large area should be partially covered, got {coverage_partial}%"

    print(f"Small area (400-600, 400-600): {coverage_full:.1f}% coverage")
    print(f"Large area (0-2000, 0-2000): {coverage_partial:.1f}% coverage")

    return print_test_result(True, "- Coverage calculation works")


def run_all_tests():
    """Run all Phase 10 tests."""
    print("\n" + "=" * 80)
    print("PHASE 10: ADVANCED FEATURES - TEST SUITE")
    print("Testing: Drones, Weather, Control Range")
    print("=" * 80)

    tests = [
        # Drone tests
        ("Drone Battery Drain", test_drone_battery_drain),
        ("Drone Low Battery Return", test_drone_low_battery_return),
        ("Drone Charging", test_drone_charging),
        ("Drone Movement", test_drone_movement),
        ("Drone Patrol", test_drone_patrol),

        # Weather tests
        ("Weather Transitions", test_weather_system_transitions),
        ("Weather Effects", test_weather_effects),
        ("Weather Forecast", test_weather_forecast),
        ("Weather Stealth", test_weather_stealth_detection),

        # Control Range tests
        ("Factory Control Range", test_control_range_factory),
        ("Wireless Transmitter", test_control_range_transmitter),
        ("Transmitter Levels", test_control_range_levels),
        ("Distance to Range", test_control_range_distance),
        ("Coverage Percentage", test_control_range_coverage),
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
