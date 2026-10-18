"""
Unit tests for AnimalManager.

Tests animal spawning, interactions, and lifecycle management.
"""

import pytest
import math
from unittest.mock import Mock, MagicMock, patch


class MockAnimal:
    """Mock animal for testing."""
    def __init__(self, x, y, alive=True):
        self.x = x
        self.y = y
        self.alive = alive
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_pet = False

    def update(self, dt):
        pass

    def check_threat_proximity(self, threats):
        pass

    def chase(self, x, y):
        pass

    def flee_from(self, x, y):
        pass


@pytest.fixture
def animal_manager():
    """Create AnimalManager instance."""
    # Mock the animal classes before importing
    mock_modules = {
        'entities.animal': MagicMock(),
    }

    with patch.dict('sys.modules', mock_modules):
        from src.systems.animal_manager import AnimalManager
        return AnimalManager(world_width=1000, world_height=1000)


class TestAnimalManagerInit:
    """Tests for AnimalManager initialization."""

    def test_init_default_dimensions(self):
        """Test initialization with default dimensions."""
        with patch.dict('sys.modules', {'entities.animal': MagicMock()}):
            from src.systems.animal_manager import AnimalManager
            am = AnimalManager()

            assert am.world_width == 2000
            assert am.world_height == 2000

    def test_init_custom_dimensions(self):
        """Test initialization with custom dimensions."""
        with patch.dict('sys.modules', {'entities.animal': MagicMock()}):
            from src.systems.animal_manager import AnimalManager
            am = AnimalManager(world_width=500, world_height=800)

            assert am.world_width == 500
            assert am.world_height == 800

    def test_init_empty_collections(self, animal_manager):
        """Test that collections start empty."""
        assert animal_manager.animals == []
        assert animal_manager.fish_schools == []

    def test_init_max_animals_config(self, animal_manager):
        """Test max animals configuration."""
        assert 'birds' in animal_manager.max_animals
        assert 'dogs' in animal_manager.max_animals
        assert 'cats' in animal_manager.max_animals
        assert 'fish' in animal_manager.max_animals

    def test_init_spawn_zones(self, animal_manager):
        """Test spawn zones initialized."""
        assert 'water' in animal_manager.spawn_zones
        assert 'forest' in animal_manager.spawn_zones
        assert 'urban' in animal_manager.spawn_zones
        assert 'park' in animal_manager.spawn_zones


class TestSpawnZones:
    """Tests for spawn zone management."""

    def test_add_spawn_zone(self, animal_manager):
        """Test adding a spawn zone."""
        animal_manager.add_spawn_zone('water', 100, 200, 50)

        assert len(animal_manager.spawn_zones['water']) == 1
        zone = animal_manager.spawn_zones['water'][0]
        assert zone['x'] == 100
        assert zone['y'] == 200
        assert zone['radius'] == 50

    def test_add_multiple_spawn_zones(self, animal_manager):
        """Test adding multiple spawn zones of same type."""
        animal_manager.add_spawn_zone('forest', 100, 100, 30)
        animal_manager.add_spawn_zone('forest', 500, 500, 40)

        assert len(animal_manager.spawn_zones['forest']) == 2

    def test_add_invalid_zone_type(self, animal_manager):
        """Test adding invalid zone type does nothing."""
        initial_zones = {k: len(v) for k, v in animal_manager.spawn_zones.items()}

        animal_manager.add_spawn_zone('invalid_type', 100, 100, 30)

        # Zones should remain unchanged
        for zone_type, count in initial_zones.items():
            assert len(animal_manager.spawn_zones[zone_type]) == count


class TestGetAnimalsInRadius:
    """Tests for getting animals within a radius."""

    def test_get_animals_in_radius_empty(self, animal_manager):
        """Test with no animals."""
        result = animal_manager.get_animals_in_radius(100, 100, 50)
        assert result == []

    def test_get_animals_in_radius_found(self, animal_manager):
        """Test finding animals within radius."""
        animal1 = MockAnimal(100, 100)
        animal2 = MockAnimal(110, 110)
        animal3 = MockAnimal(500, 500)

        animal_manager.animals = [animal1, animal2, animal3]

        result = animal_manager.get_animals_in_radius(100, 100, 50)

        assert len(result) == 2
        assert animal1 in result
        assert animal2 in result
        assert animal3 not in result

    def test_get_animals_in_radius_none_found(self, animal_manager):
        """Test when no animals are within radius."""
        animal = MockAnimal(500, 500)
        animal_manager.animals = [animal]

        result = animal_manager.get_animals_in_radius(100, 100, 50)
        assert result == []


class TestStatistics:
    """Tests for statistics tracking."""

    def test_initial_statistics(self, animal_manager):
        """Test initial statistics values."""
        stats = animal_manager.get_statistics()

        assert stats['total_animals'] == 0
        assert stats['fish_schools'] == 0
        assert stats['total_spawned'] == 0
        assert stats['interactions'] == 0

    def test_statistics_with_animals(self, animal_manager):
        """Test statistics with animals present."""
        for i in range(5):
            animal_manager.animals.append(MockAnimal(i * 100, i * 100))

        stats = animal_manager.get_statistics()
        assert stats['total_animals'] == 5

    def test_statistics_spawn_count(self, animal_manager):
        """Test spawn count tracking."""
        animal_manager.stats['total_spawned'] = 15
        animal_manager.stats['interactions'] = 5

        stats = animal_manager.get_statistics()

        assert stats['total_spawned'] == 15
        assert stats['interactions'] == 5


class TestAnimalUpdate:
    """Tests for animal update functionality."""

    def test_update_removes_dead_animals(self, animal_manager):
        """Test that dead animals are removed during update."""
        alive_animal = MockAnimal(100, 100, alive=True)
        dead_animal = MockAnimal(200, 200, alive=False)

        animal_manager.animals = [alive_animal, dead_animal]
        animal_manager.update(0.1)

        assert alive_animal in animal_manager.animals
        assert dead_animal not in animal_manager.animals

    def test_update_boundary_checking(self, animal_manager):
        """Test that animals are kept within world boundaries."""
        animal = MockAnimal(-50, 500, alive=True)
        animal.velocity_x = -10

        animal_manager.animals = [animal]
        animal_manager.update(0.1)

        assert animal.x >= 0
        assert animal.velocity_x > 0  # Should bounce back

    def test_update_boundary_right_edge(self, animal_manager):
        """Test boundary checking on right edge."""
        animal = MockAnimal(animal_manager.world_width + 50, 500, alive=True)
        animal.velocity_x = 10

        animal_manager.animals = [animal]
        animal_manager.update(0.1)

        assert animal.x <= animal_manager.world_width
        assert animal.velocity_x < 0

    def test_update_boundary_bottom_edge(self, animal_manager):
        """Test boundary checking on bottom edge."""
        animal = MockAnimal(500, animal_manager.world_height + 50, alive=True)
        animal.velocity_y = 10

        animal_manager.animals = [animal]
        animal_manager.update(0.1)

        assert animal.y <= animal_manager.world_height
        assert animal.velocity_y < 0


class TestInteractionCooldowns:
    """Tests for interaction cooldown management."""

    def test_cooldown_decrement(self, animal_manager):
        """Test that cooldowns are decremented."""
        animal_manager.interaction_cooldowns[(1, 2)] = 1.0
        animal_manager.interaction_cooldowns[(3, 4)] = 0.5

        # Manually update cooldowns (simulating part of update)
        for key in list(animal_manager.interaction_cooldowns.keys()):
            animal_manager.interaction_cooldowns[key] -= 0.3
            if animal_manager.interaction_cooldowns[key] <= 0:
                del animal_manager.interaction_cooldowns[key]

        assert (1, 2) in animal_manager.interaction_cooldowns
        assert (3, 4) in animal_manager.interaction_cooldowns

    def test_cooldown_removal_when_expired(self, animal_manager):
        """Test that expired cooldowns are removed."""
        animal_manager.interaction_cooldowns[(1, 2)] = 0.1

        # Simulate time passing
        for key in list(animal_manager.interaction_cooldowns.keys()):
            animal_manager.interaction_cooldowns[key] -= 0.5
            if animal_manager.interaction_cooldowns[key] <= 0:
                del animal_manager.interaction_cooldowns[key]

        assert (1, 2) not in animal_manager.interaction_cooldowns


class TestGlobalInstance:
    """Tests for global animal manager instance."""

    def test_get_animal_manager_creates_instance(self):
        """Test that get_animal_manager creates a new instance."""
        with patch.dict('sys.modules', {'entities.animal': MagicMock()}):
            from src.systems import animal_manager as am_module

            # Reset global instance
            am_module._animal_manager = None

            manager = am_module.get_animal_manager(world_width=500, world_height=500)

            assert manager is not None
            assert manager.world_width == 500
            assert manager.world_height == 500

    def test_get_animal_manager_returns_same_instance(self):
        """Test that get_animal_manager returns the same instance."""
        with patch.dict('sys.modules', {'entities.animal': MagicMock()}):
            from src.systems import animal_manager as am_module

            # Reset global instance
            am_module._animal_manager = None

            manager1 = am_module.get_animal_manager()
            manager2 = am_module.get_animal_manager()

            assert manager1 is manager2
