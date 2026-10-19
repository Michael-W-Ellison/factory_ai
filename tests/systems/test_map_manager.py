"""
Tests for custom map creation, validation, saving, and loading.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.systems.map_manager import (
    CustomMap, MapValidator, MapManager, MapValidationResult,
    MapFeature, MapValidationError
)
from src.core.game_config import GeographicFeature


class TestCustomMap:
    """Tests for CustomMap dataclass."""

    def test_default_map(self):
        """Test default map creation."""
        map = CustomMap(name="Test Map")
        assert map.name == "Test Map"
        assert map.width == 100
        assert map.height == 75
        assert map.city_enabled is True

    def test_map_with_ocean(self):
        """Test map with ocean configuration."""
        map = CustomMap(
            name="Ocean Map",
            has_ocean=True,
            ocean_edges=['south', 'west'],
            ocean_depth=6
        )
        assert map.has_ocean is True
        assert 'south' in map.ocean_edges
        assert map.ocean_depth == 6

    def test_map_with_rivers(self):
        """Test map with river configuration."""
        map = CustomMap(
            name="River Map",
            has_rivers=True,
            num_rivers=2,
            river_width_range=(3, 5)
        )
        assert map.has_rivers is True
        assert map.num_rivers == 2

    def test_to_world_config(self):
        """Test conversion to WorldConfig."""
        map = CustomMap(
            name="Test",
            width=120,
            height=90,
            has_ocean=True,
            ocean_edges=['south'],
            has_rivers=True,
            num_rivers=2
        )
        config = map.to_world_config()

        assert config.custom_width == 120
        assert config.custom_height == 90
        assert GeographicFeature.OCEAN_SOUTH in config.geographic_features
        assert config.num_rivers == 2

    def test_to_dict_and_back(self):
        """Test serialization round-trip."""
        original = CustomMap(
            name="Test Map",
            description="A test",
            width=80,
            height=60,
            factory_spawn=(40, 30),
            landfill_areas=[(10, 10, 20, 15)],
            has_ocean=True,
            ocean_edges=['south']
        )

        data = original.to_dict()
        restored = CustomMap.from_dict(data)

        assert restored.name == original.name
        assert restored.width == original.width
        assert restored.factory_spawn == original.factory_spawn
        assert restored.landfill_areas == original.landfill_areas


class TestMapValidator:
    """Tests for MapValidator."""

    def test_valid_map(self):
        """Test validation of a valid map."""
        map = CustomMap(
            name="Valid Map",
            width=100,
            height=75,
            factory_spawn=(50, 37),
            landfill_areas=[(10, 10, 15, 15)],  # 225 tiles > 100 minimum
            city_coverage=0.5
        )

        result = MapValidator.validate(map)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_invalid_dimensions_too_small(self):
        """Test validation fails for too small map."""
        map = CustomMap(
            name="Small Map",
            width=20,  # Below minimum of 30
            height=20,  # Below minimum of 25
            factory_spawn=(10, 10),
            landfill_areas=[(0, 0, 10, 10)]
        )

        result = MapValidator.validate(map)

        assert result.is_valid is False
        assert any("width" in e.lower() for e in result.errors)
        assert any("height" in e.lower() for e in result.errors)

    def test_invalid_no_factory_spawn(self):
        """Test validation fails without factory spawn."""
        map = CustomMap(
            name="No Spawn",
            factory_spawn=None,
            landfill_areas=[(10, 10, 15, 15)]
        )

        result = MapValidator.validate(map)

        assert result.is_valid is False
        assert any("factory spawn" in e.lower() for e in result.errors)

    def test_invalid_insufficient_landfill(self):
        """Test validation fails with insufficient landfill."""
        map = CustomMap(
            name="Small Landfill",
            factory_spawn=(50, 37),
            landfill_areas=[(10, 10, 5, 5)]  # Only 25 tiles, need 100
        )

        result = MapValidator.validate(map)

        assert result.is_valid is False
        assert any("landfill" in e.lower() for e in result.errors)

    def test_invalid_city_disabled(self):
        """Test validation fails with city disabled."""
        map = CustomMap(
            name="No City",
            factory_spawn=(50, 37),
            landfill_areas=[(10, 10, 15, 15)],
            city_enabled=False
        )

        result = MapValidator.validate(map)

        assert result.is_valid is False
        assert any("city" in e.lower() for e in result.errors)

    def test_invalid_low_city_coverage(self):
        """Test validation fails with too low city coverage."""
        map = CustomMap(
            name="Low City",
            factory_spawn=(50, 37),
            landfill_areas=[(10, 10, 15, 15)],
            city_coverage=0.05  # Below 0.1 minimum
        )

        result = MapValidator.validate(map)

        assert result.is_valid is False
        assert any("coverage" in e.lower() for e in result.errors)

    def test_warning_ratio_sum(self):
        """Test warning for zone ratio sum not equal to 1."""
        map = CustomMap(
            name="Bad Ratios",
            factory_spawn=(50, 37),
            landfill_areas=[(10, 10, 15, 15)],
            residential_ratio=0.3,
            commercial_ratio=0.3,
            industrial_ratio=0.3,
            park_ratio=0.3  # Sum = 1.2
        )

        result = MapValidator.validate(map)

        # Should be valid but with warning
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert any("ratio" in w.lower() for w in result.warnings)

    def test_warning_no_bridges_with_rivers(self):
        """Test warning when rivers have no bridges."""
        map = CustomMap(
            name="No Bridges",
            factory_spawn=(50, 37),
            landfill_areas=[(10, 10, 15, 15)],
            has_rivers=True,
            num_rivers=2,
            create_bridges=False
        )

        result = MapValidator.validate(map)

        # Valid but with warning
        assert result.is_valid is True
        assert any("bridge" in w.lower() for w in result.warnings)

    def test_invalid_too_much_water(self):
        """Test validation fails with too much water coverage."""
        map = CustomMap(
            name="Water World",
            width=50,
            height=40,
            factory_spawn=(25, 20),
            landfill_areas=[(10, 10, 15, 15)],
            has_ocean=True,
            ocean_edges=['north', 'south', 'east', 'west'],
            ocean_depth=15  # Too deep for map size
        )

        result = MapValidator.validate(map)

        assert result.is_valid is False
        assert any("buildable" in e.lower() or "island" in e.lower() for e in result.errors)

    def test_feature_count(self):
        """Test that validation counts features."""
        map = CustomMap(
            name="Feature Test",
            width=100,
            height=75,
            factory_spawn=(50, 37),
            landfill_areas=[(10, 10, 15, 15), (60, 50, 10, 10)],
            has_ocean=True,
            ocean_edges=['south'],
            has_rivers=True,
            num_rivers=2,
            police_station_count=2
        )

        result = MapValidator.validate(map)

        assert result.feature_count['width'] == 100
        assert result.feature_count['height'] == 75
        assert result.feature_count['ocean_edges'] == 1
        assert result.feature_count['rivers'] == 2
        assert result.feature_count['landfill_areas'] == 2
        assert result.feature_count['police_stations'] == 2


class TestMapManager:
    """Tests for MapManager."""

    @pytest.fixture
    def temp_maps_dir(self):
        """Create a temporary directory for maps."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def manager(self, temp_maps_dir):
        """Create a MapManager with temporary directory."""
        return MapManager(maps_dir=temp_maps_dir)

    def test_save_valid_map(self, manager):
        """Test saving a valid map."""
        map = CustomMap(
            name="Test Save",
            factory_spawn=(50, 37),
            landfill_areas=[(10, 10, 15, 15)]
        )

        result = manager.save_map(map)

        assert result is True
        assert (manager.maps_dir / "Test_Save.json").exists()

    def test_save_invalid_map(self, manager):
        """Test saving an invalid map fails."""
        map = CustomMap(
            name="Invalid",
            factory_spawn=None,  # Invalid - no spawn
            landfill_areas=[]
        )

        result = manager.save_map(map)

        assert result is False

    def test_save_no_overwrite(self, manager):
        """Test saving doesn't overwrite by default."""
        map = CustomMap(
            name="No Overwrite",
            factory_spawn=(50, 37),
            landfill_areas=[(10, 10, 15, 15)]
        )

        manager.save_map(map)
        result = manager.save_map(map, overwrite=False)

        assert result is False

    def test_save_with_overwrite(self, manager):
        """Test saving with overwrite enabled."""
        map = CustomMap(
            name="With Overwrite",
            factory_spawn=(50, 37),
            landfill_areas=[(10, 10, 15, 15)]
        )

        manager.save_map(map)
        map.description = "Updated"
        result = manager.save_map(map, overwrite=True)

        assert result is True

    def test_load_map(self, manager):
        """Test loading a saved map."""
        original = CustomMap(
            name="Load Test",
            description="Testing load",
            factory_spawn=(50, 37),
            landfill_areas=[(10, 10, 15, 15)]
        )
        manager.save_map(original)

        # Clear cache
        manager._map_cache.clear()

        loaded = manager.load_map("Load Test")

        assert loaded is not None
        assert loaded.name == "Load Test"
        assert loaded.description == "Testing load"

    def test_load_nonexistent_map(self, manager):
        """Test loading a map that doesn't exist."""
        loaded = manager.load_map("Does Not Exist")

        assert loaded is None

    def test_delete_map(self, manager):
        """Test deleting a map."""
        map = CustomMap(
            name="Delete Me",
            factory_spawn=(50, 37),
            landfill_areas=[(10, 10, 15, 15)]
        )
        manager.save_map(map)

        result = manager.delete_map("Delete Me")

        assert result is True
        assert not (manager.maps_dir / "Delete_Me.json").exists()

    def test_list_maps(self, manager):
        """Test listing saved maps."""
        for i in range(3):
            map = CustomMap(
                name=f"Map {i}",
                factory_spawn=(50, 37),
                landfill_areas=[(10, 10, 15, 15)]
            )
            manager.save_map(map)

        maps = manager.list_maps()

        assert len(maps) == 3
        assert all('name' in m for m in maps)
        assert all('is_valid' in m for m in maps)

    def test_get_builtin_maps(self, manager):
        """Test getting built-in map presets."""
        builtins = manager.get_builtin_maps()

        assert len(builtins) >= 3
        assert any(m.name == "Classic" for m in builtins)
        assert any(m.name == "Island Challenge" for m in builtins)

    def test_builtin_maps_are_valid(self, manager):
        """Test that all built-in maps pass validation."""
        for map in manager.get_builtin_maps():
            result = MapValidator.validate(map)
            assert result.is_valid, f"Built-in map '{map.name}' failed validation: {result.errors}"

    def test_create_from_preset(self, manager):
        """Test creating a map from a preset."""
        new_map = manager.create_map_from_preset("Classic")

        assert new_map is not None
        assert "Custom" in new_map.name
        assert new_map.author == "Player"

    def test_create_from_nonexistent_preset(self, manager):
        """Test creating from a preset that doesn't exist."""
        new_map = manager.create_map_from_preset("Nonexistent")

        assert new_map is None


class TestMapValidationResult:
    """Tests for MapValidationResult."""

    def test_initial_valid(self):
        """Test result starts as valid."""
        result = MapValidationResult(is_valid=True)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_add_error_invalidates(self):
        """Test adding an error invalidates the result."""
        result = MapValidationResult(is_valid=True)
        result.add_error("Test error")

        assert result.is_valid is False
        assert "Test error" in result.errors

    def test_add_warning_keeps_valid(self):
        """Test adding a warning doesn't invalidate."""
        result = MapValidationResult(is_valid=True)
        result.add_warning("Test warning")

        assert result.is_valid is True
        assert "Test warning" in result.warnings
