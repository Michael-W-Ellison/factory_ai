"""
Weather Manager - Manages weather system and its effects on gameplay.

Weather types:
- Clear: Normal conditions
- Cloudy: -30% solar power
- Rain: -50% solar, -20% detection
- Heavy Rain: -75% solar, -40% detection, slower robots
- Fog: -60% detection, -30% visibility
- Storm: risky operations, high detection if seen
- Snow: -50% solar, -30% robot speed, -20% detection
"""

from enum import Enum
import random


class WeatherType(Enum):
    """Weather conditions."""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    FOG = "fog"
    STORM = "storm"
    SNOW = "snow"


class WeatherManager:
    """
    Manages weather conditions and their gameplay effects.

    Weather affects:
    - Solar power generation
    - Detection chances
    - Robot movement speed
    - NPC behavior
    - Visibility range
    """

    def __init__(self):
        """Initialize weather manager."""
        # Current weather
        self.current_weather = WeatherType.CLEAR
        self.weather_duration = 0.0
        self.weather_elapsed = 0.0

        # Weather transition
        self.transitioning = False
        self.next_weather = None
        self.transition_duration = 30 * 60  # 30 minutes
        self.transition_elapsed = 0.0

        # Forecast (requires research)
        self.forecast_enabled = False
        self.forecast = []  # List of (weather, duration) tuples

        # Weather effects (multipliers/modifiers)
        self.weather_effects = {
            WeatherType.CLEAR: {
                'solar_power': 1.0,
                'detection_modifier': 1.0,
                'robot_speed': 1.0,
                'visibility': 1.0,
                'npc_indoors_chance': 0.0,
            },
            WeatherType.CLOUDY: {
                'solar_power': 0.7,
                'detection_modifier': 1.0,
                'robot_speed': 1.0,
                'visibility': 0.9,
                'npc_indoors_chance': 0.1,
            },
            WeatherType.RAIN: {
                'solar_power': 0.5,
                'detection_modifier': 0.8,
                'robot_speed': 0.95,
                'visibility': 0.8,
                'npc_indoors_chance': 0.6,
            },
            WeatherType.HEAVY_RAIN: {
                'solar_power': 0.25,
                'detection_modifier': 0.6,
                'robot_speed': 0.85,
                'visibility': 0.6,
                'npc_indoors_chance': 0.9,
            },
            WeatherType.FOG: {
                'solar_power': 0.6,
                'detection_modifier': 0.4,
                'robot_speed': 0.9,
                'visibility': 0.5,
                'npc_indoors_chance': 0.3,
            },
            WeatherType.STORM: {
                'solar_power': 0.1,
                'detection_modifier': 1.5,  # If seen, very noticeable
                'robot_speed': 0.7,
                'visibility': 0.4,
                'npc_indoors_chance': 0.95,
            },
            WeatherType.SNOW: {
                'solar_power': 0.5,
                'detection_modifier': 0.8,
                'robot_speed': 0.7,
                'visibility': 0.7,
                'npc_indoors_chance': 0.7,
            },
        }

        # Weather probabilities
        self.weather_probabilities = {
            WeatherType.CLEAR: 0.4,
            WeatherType.CLOUDY: 0.25,
            WeatherType.RAIN: 0.15,
            WeatherType.HEAVY_RAIN: 0.05,
            WeatherType.FOG: 0.08,
            WeatherType.STORM: 0.02,
            WeatherType.SNOW: 0.05,
        }

        # Start with clear weather
        self._set_weather(WeatherType.CLEAR, duration=4 * 3600)  # 4 hours

    def update(self, dt: float, game_time: float):
        """
        Update weather system.

        Args:
            dt: Delta time in seconds
            game_time: Current game time
        """
        # Handle weather transition
        if self.transitioning:
            self.transition_elapsed += dt
            if self.transition_elapsed >= self.transition_duration:
                # Transition complete
                self.current_weather = self.next_weather
                self.transitioning = False
                self.transition_elapsed = 0.0
                self.weather_elapsed = 0.0
            return

        # Update weather duration
        self.weather_elapsed += dt

        # Check if weather should change
        if self.weather_elapsed >= self.weather_duration:
            self._transition_to_new_weather()

    def _transition_to_new_weather(self):
        """Start transition to new weather."""
        # Pick new weather
        new_weather = self._pick_new_weather()

        # Start transition
        self.transitioning = True
        self.next_weather = new_weather
        self.transition_elapsed = 0.0

        # Set duration for new weather (2-6 hours)
        self.weather_duration = random.uniform(2 * 3600, 6 * 3600)

        print(f"\n🌤️  Weather changing to {new_weather.value}")

    def _pick_new_weather(self) -> WeatherType:
        """Pick new weather based on probabilities."""
        # Don't repeat same weather immediately
        available_weathers = [w for w in WeatherType if w != self.current_weather]

        # Calculate probabilities (normalize after removing current)
        total_prob = sum(self.weather_probabilities[w] for w in available_weathers)
        normalized_probs = {w: self.weather_probabilities[w] / total_prob for w in available_weathers}

        # Random selection
        rand = random.random()
        cumulative = 0.0
        for weather, prob in normalized_probs.items():
            cumulative += prob
            if rand <= cumulative:
                return weather

        return WeatherType.CLEAR  # Fallback

    def _set_weather(self, weather: WeatherType, duration: float):
        """Set weather immediately (for initialization)."""
        self.current_weather = weather
        self.weather_duration = duration
        self.weather_elapsed = 0.0
        self.transitioning = False

    def get_solar_power_multiplier(self) -> float:
        """Get solar power generation multiplier."""
        return self._get_effect('solar_power')

    def get_detection_modifier(self) -> float:
        """Get detection chance modifier."""
        return self._get_effect('detection_modifier')

    def get_robot_speed_multiplier(self) -> float:
        """Get robot speed multiplier."""
        return self._get_effect('robot_speed')

    def get_visibility_multiplier(self) -> float:
        """Get visibility range multiplier."""
        return self._get_effect('visibility')

    def get_npc_indoors_chance(self) -> float:
        """Get chance of NPCs staying indoors."""
        return self._get_effect('npc_indoors_chance')

    def _get_effect(self, effect_name: str) -> float:
        """Get weather effect value, with transition blending."""
        current_value = self.weather_effects[self.current_weather][effect_name]

        if self.transitioning and self.next_weather:
            # Blend between current and next weather
            next_value = self.weather_effects[self.next_weather][effect_name]
            blend = self.transition_elapsed / self.transition_duration
            return current_value * (1 - blend) + next_value * blend

        return current_value

    def enable_forecast(self):
        """Enable weather forecasting (requires research)."""
        self.forecast_enabled = True
        self._generate_forecast()

    def _generate_forecast(self):
        """Generate 3-day weather forecast."""
        if not self.forecast_enabled:
            return

        self.forecast = []
        current_time = 0.0

        # Add current weather
        remaining_time = self.weather_duration - self.weather_elapsed
        self.forecast.append((self.current_weather, remaining_time))
        current_time += remaining_time

        # Generate next 3 days
        forecast_duration = 3 * 24 * 3600  # 3 days
        last_weather = self.current_weather

        while current_time < forecast_duration:
            # Pick next weather (avoid repeating)
            available = [w for w in WeatherType if w != last_weather]
            total_prob = sum(self.weather_probabilities[w] for w in available)
            normalized = {w: self.weather_probabilities[w] / total_prob for w in available}

            rand = random.random()
            cumulative = 0.0
            next_weather = WeatherType.CLEAR
            for weather, prob in normalized.items():
                cumulative += prob
                if rand <= cumulative:
                    next_weather = weather
                    break

            duration = random.uniform(2 * 3600, 6 * 3600)
            self.forecast.append((next_weather, duration))
            current_time += duration
            last_weather = next_weather

    def get_forecast(self) -> list:
        """Get weather forecast (if enabled)."""
        if not self.forecast_enabled:
            return []
        return self.forecast[:10]  # Return up to 10 weather periods

    def is_good_weather_for_stealth(self) -> bool:
        """Check if current weather is good for stealth operations."""
        return self.current_weather in [WeatherType.FOG, WeatherType.RAIN, WeatherType.HEAVY_RAIN]

    def get_weather_description(self) -> str:
        """Get human-readable weather description."""
        descriptions = {
            WeatherType.CLEAR: "Clear skies",
            WeatherType.CLOUDY: "Cloudy",
            WeatherType.RAIN: "Light rain",
            WeatherType.HEAVY_RAIN: "Heavy rain",
            WeatherType.FOG: "Foggy",
            WeatherType.STORM: "Storm",
            WeatherType.SNOW: "Snow",
        }
        return descriptions.get(self.current_weather, "Unknown")

    def get_stats(self) -> dict:
        """Get weather statistics."""
        return {
            'current_weather': self.current_weather.value,
            'description': self.get_weather_description(),
            'duration_remaining': self.weather_duration - self.weather_elapsed,
            'transitioning': self.transitioning,
            'solar_power_multiplier': self.get_solar_power_multiplier(),
            'detection_modifier': self.get_detection_modifier(),
            'robot_speed_multiplier': self.get_robot_speed_multiplier(),
            'visibility_multiplier': self.get_visibility_multiplier(),
            'forecast_enabled': self.forecast_enabled,
        }
