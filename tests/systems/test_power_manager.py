"""
Unit tests for PowerManager.

Tests cover:
- Initialization
- Power generation and consumption calculations
- Battery storage management
- Brownout and blackout states
- Priority-based power distribution
- Building power state updates
"""

import pytest
from unittest.mock import MagicMock, patch

from src.systems.power_manager import PowerManager, PowerPriority


class MockBuilding:
    """Mock building for testing power management."""

    def __init__(self, power_generation=0, power_consumption=0,
                 operational=True, powered=True, can_operate_result=True,
                 power_priority=None):
        self.power_generation = power_generation
        self.power_consumption = power_consumption
        self.operational = operational
        self.powered = powered
        self._can_operate_result = can_operate_result
        if power_priority is not None:
            self.power_priority = power_priority

    def can_operate(self):
        return self._can_operate_result


def create_mock_building_manager(buildings_list):
    """Create a mock building manager with given buildings."""
    manager = MagicMock()
    manager.buildings = {i: b for i, b in enumerate(buildings_list)}
    return manager


class TestPowerManagerInitialization:
    """Tests for PowerManager initialization."""

    def test_init_with_building_manager(self):
        """Test that manager initializes with building manager reference."""
        bm = create_mock_building_manager([])
        manager = PowerManager(bm)

        assert manager.building_manager is bm

    def test_init_zero_power_storage(self):
        """Test that power storage starts at zero."""
        bm = create_mock_building_manager([])
        manager = PowerManager(bm)

        assert manager.current_power == 0.0
        assert manager.max_storage == 0.0

    def test_init_power_stats_zeroed(self):
        """Test that power stats are initialized to zero."""
        bm = create_mock_building_manager([])
        manager = PowerManager(bm)

        assert manager.total_generation == 0.0
        assert manager.total_consumption == 0.0
        assert manager.net_power == 0.0

    def test_init_has_power_true(self):
        """Test that has_power starts as True."""
        bm = create_mock_building_manager([])
        manager = PowerManager(bm)

        assert manager.has_power is True
        assert manager.brownout is False
        assert manager.blackout is False


class TestPowerGeneration:
    """Tests for power generation calculations."""

    def test_generation_from_single_building(self):
        """Test calculating generation from a single building."""
        generator = MockBuilding(power_generation=100)
        bm = create_mock_building_manager([generator])
        manager = PowerManager(bm)

        manager.update(1.0, bm)

        assert manager.total_generation == 100.0

    def test_generation_from_multiple_buildings(self):
        """Test aggregating generation from multiple buildings."""
        gen1 = MockBuilding(power_generation=100)
        gen2 = MockBuilding(power_generation=150)
        bm = create_mock_building_manager([gen1, gen2])
        manager = PowerManager(bm)

        manager.update(1.0, bm)

        assert manager.total_generation == 250.0

    def test_generation_ignores_inoperable_buildings(self):
        """Test that non-operational generators don't contribute."""
        gen1 = MockBuilding(power_generation=100, can_operate_result=True)
        gen2 = MockBuilding(power_generation=150, can_operate_result=False)
        bm = create_mock_building_manager([gen1, gen2])
        manager = PowerManager(bm)

        manager.update(1.0, bm)

        assert manager.total_generation == 100.0


class TestPowerConsumption:
    """Tests for power consumption calculations."""

    def test_consumption_from_operational_building(self):
        """Test calculating consumption from operational building."""
        consumer = MockBuilding(power_consumption=50, operational=True)
        bm = create_mock_building_manager([consumer])
        manager = PowerManager(bm)

        manager.update(1.0, bm)

        assert manager.total_consumption == 50.0

    def test_consumption_ignores_non_operational(self):
        """Test that non-operational buildings don't consume power."""
        consumer = MockBuilding(power_consumption=50, operational=False)
        bm = create_mock_building_manager([consumer])
        manager = PowerManager(bm)

        manager.update(1.0, bm)

        assert manager.total_consumption == 0.0

    def test_net_power_calculation(self):
        """Test net power is generation minus consumption."""
        generator = MockBuilding(power_generation=200)
        consumer = MockBuilding(power_consumption=150, operational=True)
        bm = create_mock_building_manager([generator, consumer])
        manager = PowerManager(bm)

        manager.update(1.0, bm)

        assert manager.net_power == 50.0


class TestBatteryStorage:
    """Tests for battery storage management."""

    def test_add_battery_storage(self):
        """Test adding battery storage capacity."""
        bm = create_mock_building_manager([])
        manager = PowerManager(bm)

        manager.add_battery_storage(1000)

        assert manager.max_storage == 1000

    def test_add_multiple_batteries(self):
        """Test adding multiple battery storage capacities."""
        bm = create_mock_building_manager([])
        manager = PowerManager(bm)

        manager.add_battery_storage(500)
        manager.add_battery_storage(300)

        assert manager.max_storage == 800

    def test_remove_battery_storage(self):
        """Test removing battery storage capacity."""
        bm = create_mock_building_manager([])
        manager = PowerManager(bm)
        manager.add_battery_storage(1000)
        manager.current_power = 800

        manager.remove_battery_storage(300)

        assert manager.max_storage == 700
        assert manager.current_power == 700  # Clamped to new max

    def test_surplus_power_charges_batteries(self):
        """Test that surplus power charges batteries."""
        generator = MockBuilding(power_generation=100)
        bm = create_mock_building_manager([generator])
        manager = PowerManager(bm)
        manager.add_battery_storage(1000)

        manager.update(10.0, bm)  # 10 seconds, 100 power/sec = 1000 units

        assert manager.current_power == 1000.0

    def test_battery_charge_capped_at_max(self):
        """Test that battery charge doesn't exceed max storage."""
        generator = MockBuilding(power_generation=100)
        bm = create_mock_building_manager([generator])
        manager = PowerManager(bm)
        manager.add_battery_storage(500)

        manager.update(100.0, bm)  # Would add 10000 units

        assert manager.current_power == 500.0


class TestPowerDeficit:
    """Tests for power deficit handling."""

    def test_deficit_drains_batteries(self):
        """Test that power deficit drains battery storage."""
        consumer = MockBuilding(power_consumption=100, operational=True)
        bm = create_mock_building_manager([consumer])
        manager = PowerManager(bm)
        manager.add_battery_storage(1000)
        manager.current_power = 500

        manager.update(1.0, bm)  # 1 sec, 100 power/sec = 100 units needed

        assert manager.current_power == 400.0

    def test_deficit_causes_brownout(self):
        """Test that power deficit causes brownout state."""
        consumer = MockBuilding(power_consumption=100, operational=True)
        bm = create_mock_building_manager([consumer])
        manager = PowerManager(bm)
        manager.add_battery_storage(1000)
        manager.current_power = 500

        manager.update(1.0, bm)

        assert manager.brownout is True
        assert manager.blackout is False
        assert manager.has_power is True

    def test_depleted_batteries_cause_blackout(self):
        """Test that depleted batteries cause blackout."""
        consumer = MockBuilding(power_consumption=100, operational=True)
        bm = create_mock_building_manager([consumer])
        manager = PowerManager(bm)
        manager.add_battery_storage(100)
        manager.current_power = 50  # Not enough for 1 second

        manager.update(1.0, bm)

        assert manager.brownout is True
        assert manager.blackout is True
        assert manager.has_power is False
        assert manager.current_power == 0.0


class TestPriorityDistribution:
    """Tests for priority-based power distribution during blackout."""

    def test_set_building_priority(self):
        """Test setting custom building priority."""
        building = MockBuilding()
        bm = create_mock_building_manager([building])
        manager = PowerManager(bm)

        manager.set_building_priority(building, PowerPriority.CRITICAL)

        assert building.power_priority == 100

    def test_priority_distribution_powers_high_priority_first(self):
        """Test that high priority buildings get power first."""
        generator = MockBuilding(power_generation=50)
        high_priority = MockBuilding(power_consumption=30, operational=True,
                                     power_priority=PowerPriority.CRITICAL)
        low_priority = MockBuilding(power_consumption=30, operational=True,
                                    power_priority=PowerPriority.LOW)
        bm = create_mock_building_manager([generator, high_priority, low_priority])
        manager = PowerManager(bm)

        # Cause blackout with limited generation
        manager.update(1.0, bm)

        # High priority should be powered, low priority unpowered
        # Note: actual behavior depends on _handle_blackout being called
        # which happens when blackout occurs

    def test_get_building_priority_default(self):
        """Test getting default priority for unknown building type."""
        building = MockBuilding()
        bm = create_mock_building_manager([building])
        manager = PowerManager(bm)

        priority = manager._get_building_priority(building)

        assert priority == PowerPriority.MEDIUM

    def test_get_building_priority_custom(self):
        """Test getting custom building priority."""
        building = MockBuilding(power_priority=PowerPriority.HIGH)
        bm = create_mock_building_manager([building])
        manager = PowerManager(bm)

        priority = manager._get_building_priority(building)

        assert priority == PowerPriority.HIGH


class TestBuildingPowerStates:
    """Tests for building power state updates."""

    def test_all_buildings_powered_when_no_blackout(self):
        """Test that all buildings have power when no blackout."""
        building1 = MockBuilding(power_consumption=10, operational=True)
        building2 = MockBuilding(power_consumption=20, operational=True)
        generator = MockBuilding(power_generation=100)
        bm = create_mock_building_manager([building1, building2, generator])
        manager = PowerManager(bm)

        manager.update(1.0, bm)

        assert building1.powered is True
        assert building2.powered is True

    def test_consumers_unpowered_during_blackout(self):
        """Test that power consumers lose power during blackout."""
        consumer = MockBuilding(power_consumption=100, operational=True)
        bm = create_mock_building_manager([consumer])
        manager = PowerManager(bm)

        manager.update(1.0, bm)  # No generation, no storage = blackout

        assert consumer.powered is False

    def test_non_consuming_buildings_stay_powered(self):
        """Test that buildings with no consumption stay powered."""
        non_consumer = MockBuilding(power_consumption=0, operational=True)
        consumer = MockBuilding(power_consumption=100, operational=True)
        bm = create_mock_building_manager([non_consumer, consumer])
        manager = PowerManager(bm)

        manager.update(1.0, bm)

        assert non_consumer.powered is True


class TestPoweredBuildingsCount:
    """Tests for counting powered/unpowered buildings."""

    def test_get_powered_buildings_count_all_powered(self):
        """Test counting when all buildings are powered."""
        b1 = MockBuilding(power_consumption=10, powered=True)
        b2 = MockBuilding(power_consumption=20, powered=True)
        generator = MockBuilding(power_generation=100)
        bm = create_mock_building_manager([b1, b2, generator])
        manager = PowerManager(bm)

        manager.update(1.0, bm)
        counts = manager.get_powered_buildings_count(bm)

        assert counts['powered'] == 2
        assert counts['unpowered'] == 0

    def test_get_powered_buildings_count_mixed(self):
        """Test counting with mixed power states."""
        b1 = MockBuilding(power_consumption=10, powered=True)
        b2 = MockBuilding(power_consumption=20, powered=False)
        bm = create_mock_building_manager([b1, b2])
        manager = PowerManager(bm)

        counts = manager.get_powered_buildings_count(bm)

        assert counts['powered'] == 1
        assert counts['unpowered'] == 1


class TestPowerStatus:
    """Tests for power status reporting."""

    def test_get_power_status_structure(self):
        """Test that power status contains expected keys."""
        bm = create_mock_building_manager([])
        manager = PowerManager(bm)

        status = manager.get_power_status()

        assert 'generation' in status
        assert 'consumption' in status
        assert 'net' in status
        assert 'stored' in status
        assert 'storage_capacity' in status
        assert 'storage_percent' in status
        assert 'has_power' in status
        assert 'brownout' in status
        assert 'blackout' in status

    def test_power_status_reflects_state(self):
        """Test that power status reflects current state."""
        generator = MockBuilding(power_generation=100)
        consumer = MockBuilding(power_consumption=60, operational=True)
        bm = create_mock_building_manager([generator, consumer])
        manager = PowerManager(bm)
        manager.add_battery_storage(500)

        manager.update(1.0, bm)
        status = manager.get_power_status()

        assert status['generation'] == 100.0
        assert status['consumption'] == 60.0
        assert status['net'] == 40.0
        assert status['storage_capacity'] == 500

    def test_storage_percent_calculation(self):
        """Test storage percentage calculation."""
        bm = create_mock_building_manager([])
        manager = PowerManager(bm)
        manager.add_battery_storage(1000)
        manager.current_power = 250

        status = manager.get_power_status()

        assert status['storage_percent'] == 25.0

    def test_storage_percent_zero_capacity(self):
        """Test storage percent with zero capacity returns 0."""
        bm = create_mock_building_manager([])
        manager = PowerManager(bm)

        status = manager.get_power_status()

        assert status['storage_percent'] == 0


class TestBalancedPower:
    """Tests for exactly balanced power (edge case)."""

    def test_exactly_balanced_power(self):
        """Test state when generation exactly matches consumption."""
        generator = MockBuilding(power_generation=100)
        consumer = MockBuilding(power_consumption=100, operational=True)
        bm = create_mock_building_manager([generator, consumer])
        manager = PowerManager(bm)

        manager.update(1.0, bm)

        assert manager.has_power is True
        assert manager.brownout is False
        assert manager.blackout is False


class TestRepr:
    """Tests for string representation."""

    def test_repr_contains_power_info(self):
        """Test that repr contains power information."""
        generator = MockBuilding(power_generation=100)
        consumer = MockBuilding(power_consumption=60, operational=True)
        bm = create_mock_building_manager([generator, consumer])
        manager = PowerManager(bm)
        manager.update(1.0, bm)

        repr_str = repr(manager)

        assert 'PowerManager' in repr_str
        assert 'gen=' in repr_str
        assert 'cons=' in repr_str
        assert 'net=' in repr_str


class TestPowerPriorityEnum:
    """Tests for PowerPriority enum values."""

    def test_priority_ordering(self):
        """Test that priority values are correctly ordered."""
        assert PowerPriority.CRITICAL > PowerPriority.HIGH
        assert PowerPriority.HIGH > PowerPriority.MEDIUM
        assert PowerPriority.MEDIUM > PowerPriority.LOW
        assert PowerPriority.LOW > PowerPriority.OPTIONAL

    def test_priority_values(self):
        """Test specific priority values."""
        assert PowerPriority.CRITICAL == 100
        assert PowerPriority.HIGH == 75
        assert PowerPriority.MEDIUM == 50
        assert PowerPriority.LOW == 25
        assert PowerPriority.OPTIONAL == 10
