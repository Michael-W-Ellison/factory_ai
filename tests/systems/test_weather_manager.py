"""
Tests for the WeatherManager class.

Tests weather conditions, transitions, effects, and forecasting.
"""

import sys
from unittest.mock import MagicMock

# Mock pygame before importing any src modules
sys.modules['pygame'] = MagicMock()

import pytest
from unittest.mock import patch

from src.systems.weather_manager import WeatherManager, WeatherType


class TestWeatherManagerInitialization:
    """Tests for WeatherManager initialization."""

    def test_initial_weather_is_clear(self):
        """Test that initial weather is set to CLEAR."""
        manager = WeatherManager()
        assert manager.current_weather == WeatherType.CLEAR

    def test_initial_state_not_transitioning(self):
        """Test that manager is not transitioning on initialization."""
        manager = WeatherManager()
        assert manager.transitioning is False
        assert manager.next_weather is None

    def test_forecast_initially_disabled(self):
        """Test that forecast is disabled by default."""
        manager = WeatherManager()
        assert manager.forecast_enabled is False
        assert manager.forecast == []

    def test_weather_effects_defined_for_all_types(self):
        """Test that all weather types have effects defined."""
        manager = WeatherManager()
        for weather_type in WeatherType:
            assert weather_type in manager.weather_effects
            effects = manager.weather_effects[weather_type]
            assert 'solar_power' in effects
            assert 'detection_modifier' in effects
            assert 'robot_speed' in effects
            assert 'visibility' in effects
            assert 'npc_indoors_chance' in effects


class TestWeatherEffects:
    """Tests for weather effect retrieval."""

    def test_clear_weather_effects(self):
        """Test CLEAR weather has baseline effects (1.0)."""
        manager = WeatherManager()
        manager.current_weather = WeatherType.CLEAR

        assert manager.get_solar_power_multiplier() == 1.0
        assert manager.get_detection_modifier() == 1.0
        assert manager.get_robot_speed_multiplier() == 1.0
        assert manager.get_visibility_multiplier() == 1.0
        assert manager.get_npc_indoors_chance() == 0.0

    def test_heavy_rain_reduces_solar_power(self):
        """Test that HEAVY_RAIN significantly reduces solar power."""
        manager = WeatherManager()
        manager.current_weather = WeatherType.HEAVY_RAIN

        assert manager.get_solar_power_multiplier() == 0.25

    def test_fog_reduces_detection(self):
        """Test that FOG reduces detection modifier."""
        manager = WeatherManager()
        manager.current_weather = WeatherType.FOG

        assert manager.get_detection_modifier() == 0.4

    def test_storm_increases_detection_if_seen(self):
        """Test that STORM increases detection modifier."""
        manager = WeatherManager()
        manager.current_weather = WeatherType.STORM

        assert manager.get_detection_modifier() == 1.5

    def test_snow_reduces_robot_speed(self):
        """Test that SNOW reduces robot speed."""
        manager = WeatherManager()
        manager.current_weather = WeatherType.SNOW

        assert manager.get_robot_speed_multiplier() == 0.7


class TestWeatherTransitions:
    """Tests for weather transition mechanics."""

    def test_transition_starts_when_duration_expires(self):
        """Test that transition starts when weather duration expires."""
        manager = WeatherManager()
        # Set short duration
        manager.weather_duration = 1.0
        manager.weather_elapsed = 0.0

        # Update past duration
        manager.update(1.5, 0)

        assert manager.transitioning is True
        assert manager.next_weather is not None

    def test_transition_completes_after_transition_duration(self):
        """Test that transition completes after transition duration."""
        manager = WeatherManager()
        manager.transitioning = True
        manager.next_weather = WeatherType.RAIN
        manager.transition_elapsed = 0.0

        # Update past transition duration
        manager.update(manager.transition_duration + 1.0, 0)

        assert manager.transitioning is False
        assert manager.current_weather == WeatherType.RAIN

    def test_effects_blend_during_transition(self):
        """Test that effects blend between weathers during transition."""
        manager = WeatherManager()
        manager.current_weather = WeatherType.CLEAR
        manager.transitioning = True
        manager.next_weather = WeatherType.HEAVY_RAIN
        manager.transition_elapsed = manager.transition_duration / 2  # 50% through

        # Should be blend of CLEAR (1.0) and HEAVY_RAIN (0.25) solar power
        solar = manager.get_solar_power_multiplier()
        # At 50%, should be 0.5 * 1.0 + 0.5 * 0.25 = 0.625
        assert abs(solar - 0.625) < 0.01

    def test_new_weather_different_from_current(self):
        """Test that new weather is always different from current."""
        manager = WeatherManager()
        manager.current_weather = WeatherType.CLEAR

        # Pick new weather multiple times
        for _ in range(20):
            new_weather = manager._pick_new_weather()
            assert new_weather != WeatherType.CLEAR


class TestWeatherForecast:
    """Tests for weather forecasting functionality."""

    def test_enable_forecast(self):
        """Test enabling weather forecast."""
        manager = WeatherManager()
        manager.enable_forecast()

        assert manager.forecast_enabled is True
        assert len(manager.forecast) > 0

    def test_get_forecast_returns_empty_when_disabled(self):
        """Test that get_forecast returns empty list when disabled."""
        manager = WeatherManager()
        assert manager.get_forecast() == []

    def test_get_forecast_returns_list_when_enabled(self):
        """Test that get_forecast returns forecast when enabled."""
        manager = WeatherManager()
        manager.enable_forecast()

        forecast = manager.get_forecast()
        assert isinstance(forecast, list)
        assert len(forecast) > 0

    def test_forecast_contains_weather_and_duration_tuples(self):
        """Test that forecast entries are (weather, duration) tuples."""
        manager = WeatherManager()
        manager.enable_forecast()

        forecast = manager.get_forecast()
        for entry in forecast:
            assert isinstance(entry, tuple)
            assert len(entry) == 2
            assert isinstance(entry[0], WeatherType)
            assert isinstance(entry[1], float)


class TestStealthWeather:
    """Tests for stealth weather checks."""

    def test_fog_is_good_for_stealth(self):
        """Test that FOG is considered good for stealth."""
        manager = WeatherManager()
        manager.current_weather = WeatherType.FOG
        assert manager.is_good_weather_for_stealth() is True

    def test_rain_is_good_for_stealth(self):
        """Test that RAIN is considered good for stealth."""
        manager = WeatherManager()
        manager.current_weather = WeatherType.RAIN
        assert manager.is_good_weather_for_stealth() is True

    def test_heavy_rain_is_good_for_stealth(self):
        """Test that HEAVY_RAIN is considered good for stealth."""
        manager = WeatherManager()
        manager.current_weather = WeatherType.HEAVY_RAIN
        assert manager.is_good_weather_for_stealth() is True

    def test_clear_is_not_good_for_stealth(self):
        """Test that CLEAR is not good for stealth."""
        manager = WeatherManager()
        manager.current_weather = WeatherType.CLEAR
        assert manager.is_good_weather_for_stealth() is False


class TestWeatherDescriptions:
    """Tests for weather description generation."""

    def test_get_description_for_all_weather_types(self):
        """Test that all weather types have descriptions."""
        manager = WeatherManager()
        for weather_type in WeatherType:
            manager.current_weather = weather_type
            description = manager.get_weather_description()
            assert isinstance(description, str)
            assert len(description) > 0

    def test_clear_description(self):
        """Test CLEAR weather description."""
        manager = WeatherManager()
        manager.current_weather = WeatherType.CLEAR
        assert manager.get_weather_description() == "Clear skies"


class TestWeatherStats:
    """Tests for weather statistics."""

    def test_get_stats_returns_dict(self):
        """Test that get_stats returns a dictionary."""
        manager = WeatherManager()
        stats = manager.get_stats()
        assert isinstance(stats, dict)

    def test_stats_contains_required_keys(self):
        """Test that stats contains all required keys."""
        manager = WeatherManager()
        stats = manager.get_stats()

        required_keys = [
            'current_weather',
            'description',
            'duration_remaining',
            'transitioning',
            'solar_power_multiplier',
            'detection_modifier',
            'robot_speed_multiplier',
            'visibility_multiplier',
            'forecast_enabled',
        ]
        for key in required_keys:
            assert key in stats

    def test_stats_values_are_correct_types(self):
        """Test that stats values have correct types."""
        manager = WeatherManager()
        stats = manager.get_stats()

        assert isinstance(stats['current_weather'], str)
        assert isinstance(stats['description'], str)
        assert isinstance(stats['duration_remaining'], float)
        assert isinstance(stats['transitioning'], bool)
        assert isinstance(stats['forecast_enabled'], bool)
