"""
Tests for save/load state restoration.

Tests that buildings, robots, cameras, and weather are properly
serialized and deserialized.
"""

import pytest
import os
import json
import tempfile
from unittest.mock import Mock, MagicMock, patch

# Add src to path
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestBuildingRestoration:
    """Tests for building serialization and restoration."""

    def test_create_building_from_data_factory(self):
        """Test creating a Factory building from saved data."""
        from src.systems.save_manager import SaveManager

        building_data = {
            'type': 'factory',
            'x': 10,
            'y': 20,
            'level': 3,
            'powered': True,
            'active': True,
            'data': {
                'stored_materials': {'plastic': 100.0, 'metal': 50.0}
            }
        }

        building = SaveManager._create_building_from_data(building_data)

        assert building is not None
        assert building.grid_x == 10
        assert building.grid_y == 20
        assert building.level == 3
        assert building.powered is True
        assert building.stored_materials.get('plastic') == 100.0
        assert building.stored_materials.get('metal') == 50.0

    def test_create_building_from_data_warehouse(self):
        """Test creating a Warehouse building from saved data."""
        from src.systems.save_manager import SaveManager

        building_data = {
            'type': 'warehouse',
            'x': 5,
            'y': 10,
            'level': 2,
            'powered': False,
            'data': {
                'stored_materials': {'glass': 200.0}
            }
        }

        building = SaveManager._create_building_from_data(building_data)

        assert building is not None
        assert building.grid_x == 5
        assert building.grid_y == 10
        assert building.level == 2
        assert building.powered is False
        assert building.stored_materials.get('glass') == 200.0

    def test_create_building_from_data_solar_array(self):
        """Test creating a SolarArray from saved data."""
        from src.systems.save_manager import SaveManager

        building_data = {
            'type': 'solar_array',
            'x': 15,
            'y': 25,
            'level': 1,
            'powered': True,
            'data': {
                'current_hour': 14.5
            }
        }

        building = SaveManager._create_building_from_data(building_data)

        assert building is not None
        assert building.grid_x == 15
        assert building.grid_y == 25
        assert building.current_hour == 14.5

    def test_create_building_unknown_type(self):
        """Test that unknown building types return None."""
        from src.systems.save_manager import SaveManager

        building_data = {
            'type': 'unknown_building_type',
            'x': 0,
            'y': 0,
        }

        building = SaveManager._create_building_from_data(building_data)
        assert building is None

    def test_serialize_building_data(self):
        """Test serializing building-specific data."""
        from src.systems.save_manager import SaveManager
        from src.entities.buildings.factory import Factory

        factory = Factory(5, 10)
        factory.stored_materials = {'plastic': 100.0, 'metal': 50.0}

        data = SaveManager._serialize_building_data(factory)

        assert 'stored_materials' in data
        assert data['stored_materials']['plastic'] == 100.0
        assert data['stored_materials']['metal'] == 50.0


class TestRobotRestoration:
    """Tests for robot serialization and restoration."""

    def test_create_robot_from_data(self):
        """Test creating a robot from saved data."""
        from src.systems.save_manager import SaveManager
        from src.systems.entity_manager import EntityManager

        entity_manager = EntityManager()

        robot_data = {
            'x': 100.0,
            'y': 200.0,
            'speed': 150.0,
            'capacity': 200.0,
            'battery': 80.0,
            'autonomous': True,
            'upgrade_level': 3,
            'current_health': 90.0,
            'inventory': {'plastic': 25.0},
            'state': 'IDLE'
        }

        robot = SaveManager._create_robot_from_data(entity_manager, robot_data)

        assert robot is not None
        assert robot.x == 100.0
        assert robot.y == 200.0
        assert robot.speed == 150.0
        assert robot.max_capacity == 200.0
        assert robot.current_power == 80.0
        assert robot.upgrade_level == 3
        assert robot.current_health == 90.0
        assert robot.inventory.get('plastic') == 25.0

    def test_robot_in_entity_manager(self):
        """Test that created robot is added to entity manager."""
        from src.systems.save_manager import SaveManager
        from src.systems.entity_manager import EntityManager

        entity_manager = EntityManager()

        robot_data = {
            'x': 50.0,
            'y': 50.0,
        }

        robot = SaveManager._create_robot_from_data(entity_manager, robot_data)

        assert len(entity_manager.robots) == 1
        assert entity_manager.robots[0] == robot


class TestWeatherRestoration:
    """Tests for weather serialization and restoration."""

    def test_serialize_weather_state(self):
        """Test serializing weather state."""
        from src.systems.save_manager import SaveManager
        from src.systems.weather_manager import WeatherManager, WeatherType

        weather_manager = WeatherManager()
        weather_manager.current_weather = WeatherType.RAIN
        weather_manager.weather_duration = 7200
        weather_manager.weather_elapsed = 1800

        # Create mock game
        game = Mock()
        game.weather_manager = weather_manager

        state = SaveManager._serialize_weather_state(game)

        assert state['current'] == 'RAIN'
        assert state['weather_duration'] == 7200
        assert state['weather_elapsed'] == 1800

    def test_serialize_weather_transitioning(self):
        """Test serializing weather during transition."""
        from src.systems.save_manager import SaveManager
        from src.systems.weather_manager import WeatherManager, WeatherType

        weather_manager = WeatherManager()
        weather_manager.current_weather = WeatherType.CLOUDY
        weather_manager.transitioning = True
        weather_manager.next_weather = WeatherType.RAIN
        weather_manager.transition_elapsed = 500

        game = Mock()
        game.weather_manager = weather_manager

        state = SaveManager._serialize_weather_state(game)

        assert state['current'] == 'CLOUDY'
        assert state['transitioning'] is True
        assert state['next_weather'] == 'RAIN'
        assert state['transition_elapsed'] == 500


class TestCameraRestoration:
    """Tests for camera state restoration."""

    def test_camera_state_attributes(self):
        """Test that camera has expected state attributes."""
        from src.entities.security_camera import SecurityCamera, CameraStatus

        camera = SecurityCamera(100.0, 200.0, 45.0)

        # Verify camera has the attributes we restore
        assert hasattr(camera, 'status')
        assert hasattr(camera, 'facing_angle')
        assert hasattr(camera, 'disabled_timer')

        # Test status values
        assert camera.status == CameraStatus.ACTIVE
        camera.disable()
        assert camera.status == CameraStatus.DISABLED


class TestEntityManagerClearAll:
    """Tests for entity manager clear_all method."""

    def test_clear_all(self):
        """Test clearing all entities."""
        from src.systems.entity_manager import EntityManager

        entity_manager = EntityManager()

        # Create some robots
        robot1 = entity_manager.create_robot(100, 100)
        robot2 = entity_manager.create_robot(200, 200)

        assert len(entity_manager.robots) == 2
        assert len(entity_manager.entities) == 2

        # Clear all
        entity_manager.clear_all()

        assert len(entity_manager.robots) == 0
        assert len(entity_manager.entities) == 0
        assert entity_manager.selected_robot is None


class TestFullSaveLoadCycle:
    """Integration tests for full save/load cycle."""

    def test_building_round_trip(self):
        """Test that buildings survive a save/load cycle."""
        from src.systems.save_manager import SaveManager

        # Create original building data
        original_data = {
            'type': 'factory',
            'x': 10,
            'y': 20,
            'level': 2,
            'powered': True,
            'active': True,
            'health': 85.0,
            'data': {
                'stored_materials': {'plastic': 150.0}
            }
        }

        # Create building from data
        building = SaveManager._create_building_from_data(original_data)

        # Serialize back
        serialized = SaveManager._serialize_building_data(building)

        # Verify key data survives
        assert serialized.get('stored_materials', {}).get('plastic') == 150.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
