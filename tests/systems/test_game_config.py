"""
Tests for game configuration system (difficulty levels and world settings).
"""

import pytest
from src.core.game_config import (
    DifficultyLevel, DifficultyModifiers, DIFFICULTY_PRESETS,
    MapSize, CitySize, GeographicFeature,
    WorldConfig, GameSettings,
    get_difficulty_modifiers, create_world_config,
)


class TestDifficultyLevel:
    """Tests for DifficultyLevel enum."""

    def test_difficulty_levels_exist(self):
        """Test all expected difficulty levels exist."""
        assert DifficultyLevel.EASY.value == "easy"
        assert DifficultyLevel.NORMAL.value == "normal"
        assert DifficultyLevel.HARD.value == "hard"
        assert DifficultyLevel.INSANE.value == "insane"


class TestDifficultyModifiers:
    """Tests for DifficultyModifiers dataclass."""

    def test_default_modifiers(self):
        """Test default modifiers are all 1.0."""
        mods = DifficultyModifiers()
        assert mods.police_patrol_frequency == 1.0
        assert mods.police_patrol_count == 1.0
        assert mods.alert_increase_rate == 1.0
        assert mods.suspicion_gain_rate == 1.0
        assert mods.starting_money == 1.0

    def test_custom_modifiers(self):
        """Test custom modifier values."""
        mods = DifficultyModifiers(
            police_patrol_frequency=1.5,
            suspicion_gain_rate=2.0,
            starting_money=0.5,
        )
        assert mods.police_patrol_frequency == 1.5
        assert mods.suspicion_gain_rate == 2.0
        assert mods.starting_money == 0.5
        # Unset values should be default
        assert mods.alert_increase_rate == 1.0


class TestDifficultyPresets:
    """Tests for difficulty preset configurations."""

    def test_all_presets_exist(self):
        """Test presets exist for all difficulty levels."""
        assert DifficultyLevel.EASY in DIFFICULTY_PRESETS
        assert DifficultyLevel.NORMAL in DIFFICULTY_PRESETS
        assert DifficultyLevel.HARD in DIFFICULTY_PRESETS
        assert DifficultyLevel.INSANE in DIFFICULTY_PRESETS

    def test_easy_is_easier(self):
        """Test easy difficulty has favorable modifiers."""
        easy = DIFFICULTY_PRESETS[DifficultyLevel.EASY]
        assert easy.police_patrol_frequency < 1.0
        assert easy.suspicion_gain_rate < 1.0
        assert easy.starting_money > 1.0

    def test_normal_is_default(self):
        """Test normal difficulty has all 1.0 modifiers."""
        normal = DIFFICULTY_PRESETS[DifficultyLevel.NORMAL]
        assert normal.police_patrol_frequency == 1.0
        assert normal.suspicion_gain_rate == 1.0
        assert normal.starting_money == 1.0

    def test_hard_is_harder(self):
        """Test hard difficulty has challenging modifiers."""
        hard = DIFFICULTY_PRESETS[DifficultyLevel.HARD]
        assert hard.police_patrol_frequency > 1.0
        assert hard.suspicion_gain_rate > 1.0
        assert hard.starting_money < 1.0

    def test_insane_is_hardest(self):
        """Test insane difficulty is more extreme than hard."""
        hard = DIFFICULTY_PRESETS[DifficultyLevel.HARD]
        insane = DIFFICULTY_PRESETS[DifficultyLevel.INSANE]
        assert insane.police_patrol_frequency > hard.police_patrol_frequency
        assert insane.suspicion_gain_rate > hard.suspicion_gain_rate


class TestMapSize:
    """Tests for MapSize enum."""

    def test_map_sizes_exist(self):
        """Test all expected map sizes exist."""
        assert MapSize.TINY.value == "tiny"
        assert MapSize.SMALL.value == "small"
        assert MapSize.MEDIUM.value == "medium"
        assert MapSize.LARGE.value == "large"
        assert MapSize.HUGE.value == "huge"


class TestWorldConfig:
    """Tests for WorldConfig dataclass."""

    def test_default_config(self):
        """Test default world configuration."""
        config = WorldConfig()
        assert config.map_size == MapSize.MEDIUM
        assert config.city_size == CitySize.MEDIUM
        assert config.num_rivers == 0

    def test_get_dimensions(self):
        """Test dimension calculations for different sizes."""
        tiny = WorldConfig(map_size=MapSize.TINY)
        assert tiny.get_dimensions() == (50, 40)

        medium = WorldConfig(map_size=MapSize.MEDIUM)
        assert medium.get_dimensions() == (100, 75)

        huge = WorldConfig(map_size=MapSize.HUGE)
        assert huge.get_dimensions() == (200, 150)

    def test_custom_dimensions(self):
        """Test custom dimension override."""
        config = WorldConfig(custom_width=120, custom_height=90)
        assert config.get_dimensions() == (120, 90)

    def test_city_block_ratio(self):
        """Test city block ratio based on city size."""
        minimal = WorldConfig(city_size=CitySize.MINIMAL)
        assert minimal.get_city_block_ratio() == 0.2

        metropolis = WorldConfig(city_size=CitySize.METROPOLIS)
        assert metropolis.get_city_block_ratio() == 0.85

    def test_ocean_edges(self):
        """Test ocean edge detection."""
        # No ocean
        no_ocean = WorldConfig(geographic_features=[GeographicFeature.NONE])
        assert no_ocean.get_ocean_edges() == []

        # South ocean
        south = WorldConfig(geographic_features=[GeographicFeature.OCEAN_SOUTH])
        assert south.get_ocean_edges() == ['south']

        # Coastal southwest
        coastal = WorldConfig(geographic_features=[GeographicFeature.COASTAL_SOUTHWEST])
        edges = coastal.get_ocean_edges()
        assert 'south' in edges
        assert 'west' in edges

        # Island (all edges)
        island = WorldConfig(geographic_features=[GeographicFeature.ISLAND])
        edges = island.get_ocean_edges()
        assert len(edges) == 4

    def test_has_rivers(self):
        """Test river detection."""
        no_river = WorldConfig(num_rivers=0)
        assert no_river.has_rivers() is False

        has_river = WorldConfig(num_rivers=2)
        assert has_river.has_rivers() is True

        river_feature = WorldConfig(
            geographic_features=[GeographicFeature.RIVER]
        )
        assert river_feature.has_rivers() is True


class TestGameSettings:
    """Tests for GameSettings dataclass."""

    def test_default_settings(self):
        """Test default game settings."""
        settings = GameSettings()
        assert settings.difficulty == DifficultyLevel.NORMAL
        assert settings.world.map_size == MapSize.MEDIUM

    def test_get_modifiers(self):
        """Test getting difficulty modifiers."""
        easy = GameSettings(difficulty=DifficultyLevel.EASY)
        mods = easy.get_modifiers()
        assert mods.police_patrol_frequency < 1.0

    def test_custom_modifiers(self):
        """Test custom modifier override."""
        custom = DifficultyModifiers(police_patrol_frequency=3.0)
        settings = GameSettings(
            difficulty=DifficultyLevel.NORMAL,
            custom_modifiers=custom
        )
        mods = settings.get_modifiers()
        assert mods.police_patrol_frequency == 3.0

    def test_to_dict(self):
        """Test serialization to dictionary."""
        settings = GameSettings(
            difficulty=DifficultyLevel.HARD,
            world=WorldConfig(
                map_size=MapSize.LARGE,
                num_rivers=2,
            )
        )
        data = settings.to_dict()
        assert data['difficulty'] == 'hard'
        assert data['world']['map_size'] == 'large'
        assert data['world']['num_rivers'] == 2

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            'difficulty': 'easy',
            'world': {
                'map_size': 'small',
                'city_size': 'large',
                'num_rivers': 1,
            }
        }
        settings = GameSettings.from_dict(data)
        assert settings.difficulty == DifficultyLevel.EASY
        assert settings.world.map_size == MapSize.SMALL
        assert settings.world.city_size == CitySize.LARGE
        assert settings.world.num_rivers == 1


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_difficulty_modifiers(self):
        """Test getting modifiers by string."""
        easy = get_difficulty_modifiers('easy')
        assert easy.police_patrol_frequency < 1.0

        normal = get_difficulty_modifiers('normal')
        assert normal.police_patrol_frequency == 1.0

        # Invalid should return normal
        invalid = get_difficulty_modifiers('invalid')
        assert invalid.police_patrol_frequency == 1.0

    def test_create_world_config(self):
        """Test world config creation helper."""
        # Basic config
        basic = create_world_config()
        assert basic.map_size == MapSize.MEDIUM
        assert basic.num_rivers == 0

        # With ocean
        ocean = create_world_config(has_ocean=True, ocean_side='south')
        assert GeographicFeature.OCEAN_SOUTH in ocean.geographic_features

        # With river
        river = create_world_config(has_river=True, num_rivers=2)
        assert GeographicFeature.RIVER in river.geographic_features
        assert river.num_rivers == 2

        # Custom seed
        seeded = create_world_config(seed=12345)
        assert seeded.seed == 12345
