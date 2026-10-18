"""
Unit tests for ResourceManager.

Tests cover:
- Initialization
- Material deposits and storage
- Selling materials
- Money management
- Price fluctuations
- Storage decay
- Statistics tracking
"""

import pytest
from unittest.mock import MagicMock, patch

from src.systems.resource_manager import ResourceManager


class TestResourceManagerInitialization:
    """Tests for ResourceManager initialization."""

    def test_init_default_money(self):
        """Test that manager initializes with default starting money."""
        manager = ResourceManager()
        assert manager.money == 1000.0

    def test_init_empty_storage(self):
        """Test that manager initializes with empty material storage."""
        manager = ResourceManager()
        assert manager.stored_materials == {}

    def test_init_statistics_zeroed(self):
        """Test that statistics are initialized to zero."""
        manager = ResourceManager()
        assert manager.total_materials_collected == 0.0
        assert manager.total_money_earned == 0.0

    def test_init_material_values_set(self):
        """Test that base material values are set."""
        manager = ResourceManager()
        assert 'plastic' in manager.base_material_values
        assert 'metal' in manager.base_material_values
        assert 'electronic' in manager.base_material_values
        assert manager.base_material_values['electronic'] == 2.50

    def test_init_current_values_match_base(self):
        """Test that current material values match base values initially."""
        manager = ResourceManager()
        for material, base_value in manager.base_material_values.items():
            assert manager.material_values[material] == base_value


class TestMaterialDeposit:
    """Tests for depositing materials."""

    def test_deposit_single_material(self):
        """Test depositing a single material type."""
        manager = ResourceManager()
        deposited = manager.deposit_materials({'plastic': 10.0})

        assert deposited == 10.0
        assert manager.stored_materials['plastic'] == 10.0
        assert manager.total_materials_collected == 10.0

    def test_deposit_multiple_materials(self):
        """Test depositing multiple material types at once."""
        manager = ResourceManager()
        materials = {'plastic': 5.0, 'metal': 10.0, 'glass': 3.0}
        deposited = manager.deposit_materials(materials)

        assert deposited == 18.0
        assert manager.stored_materials['plastic'] == 5.0
        assert manager.stored_materials['metal'] == 10.0
        assert manager.stored_materials['glass'] == 3.0

    def test_deposit_accumulates(self):
        """Test that multiple deposits accumulate."""
        manager = ResourceManager()
        manager.deposit_materials({'plastic': 5.0})
        manager.deposit_materials({'plastic': 7.0})

        assert manager.stored_materials['plastic'] == 12.0
        assert manager.total_materials_collected == 12.0

    def test_deposit_zero_quantity_ignored(self):
        """Test that zero quantity deposits are ignored."""
        manager = ResourceManager()
        deposited = manager.deposit_materials({'plastic': 0.0, 'metal': 5.0})

        assert deposited == 5.0
        assert 'plastic' not in manager.stored_materials

    def test_deposit_negative_quantity_ignored(self):
        """Test that negative quantity deposits are ignored."""
        manager = ResourceManager()
        deposited = manager.deposit_materials({'plastic': -5.0, 'metal': 10.0})

        assert deposited == 10.0
        assert 'plastic' not in manager.stored_materials


class TestMaterialSelling:
    """Tests for selling materials."""

    def test_sell_material_success(self):
        """Test successfully selling material."""
        manager = ResourceManager()
        manager.deposit_materials({'plastic': 20.0})
        initial_money = manager.money

        earned = manager.sell_material('plastic', 10.0)

        expected_value = 10.0 * manager.material_values['plastic']
        assert earned == expected_value
        assert manager.stored_materials['plastic'] == 10.0
        assert manager.money == initial_money + expected_value
        assert manager.total_money_earned == expected_value

    def test_sell_material_insufficient_quantity(self):
        """Test selling when insufficient material in storage."""
        manager = ResourceManager()
        manager.deposit_materials({'plastic': 5.0})
        initial_money = manager.money

        earned = manager.sell_material('plastic', 10.0)

        assert earned == 0.0
        assert manager.stored_materials['plastic'] == 5.0
        assert manager.money == initial_money

    def test_sell_material_nonexistent_type(self):
        """Test selling a material type not in storage."""
        manager = ResourceManager()
        initial_money = manager.money

        earned = manager.sell_material('uranium', 10.0)

        assert earned == 0.0
        assert manager.money == initial_money

    def test_sell_all_materials(self):
        """Test selling all stored materials."""
        manager = ResourceManager()
        manager.deposit_materials({'plastic': 10.0, 'metal': 5.0})
        initial_money = manager.money

        total_earned = manager.sell_all_materials()

        expected = (10.0 * manager.material_values['plastic'] +
                   5.0 * manager.material_values['metal'])
        assert total_earned == expected
        assert manager.stored_materials['plastic'] == 0.0
        assert manager.stored_materials['metal'] == 0.0

    def test_sell_all_with_empty_storage(self):
        """Test sell_all_materials with empty storage."""
        manager = ResourceManager()

        total_earned = manager.sell_all_materials()

        assert total_earned == 0.0


class TestMoneyManagement:
    """Tests for money management operations."""

    def test_modify_money_add(self):
        """Test adding money."""
        manager = ResourceManager()
        initial = manager.money

        manager.modify_money(500.0)

        assert manager.money == initial + 500.0
        assert manager.total_money_earned == 500.0

    def test_modify_money_subtract(self):
        """Test subtracting money."""
        manager = ResourceManager()
        initial = manager.money

        manager.modify_money(-300.0)

        assert manager.money == initial - 300.0
        assert manager.total_money_earned == 0.0  # Negative doesn't count as earned

    def test_money_can_go_negative(self):
        """Test that money can go negative (debt)."""
        manager = ResourceManager()

        manager.modify_money(-2000.0)

        assert manager.money < 0


class TestValueCalculations:
    """Tests for material value calculations."""

    def test_get_material_value(self):
        """Test calculating value of a material quantity."""
        manager = ResourceManager()

        value = manager.get_material_value('metal', 10.0)

        expected = 10.0 * manager.material_values['metal']
        assert value == expected

    def test_get_material_value_unknown_type(self):
        """Test calculating value of unknown material type uses default."""
        manager = ResourceManager()

        value = manager.get_material_value('unknown_material', 10.0)

        assert value == 10.0 * 0.5  # Default value per kg

    def test_get_total_stored_value(self):
        """Test calculating total value of stored materials."""
        manager = ResourceManager()
        manager.deposit_materials({'plastic': 10.0, 'metal': 5.0})

        total_value = manager.get_total_stored_value()

        expected = (10.0 * manager.material_values['plastic'] +
                   5.0 * manager.material_values['metal'])
        assert total_value == expected

    def test_get_total_stored_value_empty(self):
        """Test total stored value with empty storage."""
        manager = ResourceManager()

        assert manager.get_total_stored_value() == 0.0


class TestStorageQueries:
    """Tests for querying storage state."""

    def test_get_material_quantity(self):
        """Test getting quantity of stored material."""
        manager = ResourceManager()
        manager.deposit_materials({'plastic': 15.5})

        assert manager.get_material_quantity('plastic') == 15.5

    def test_get_material_quantity_not_stored(self):
        """Test getting quantity of material not in storage."""
        manager = ResourceManager()

        assert manager.get_material_quantity('gold') == 0.0

    def test_get_total_stored_weight(self):
        """Test getting total weight of stored materials."""
        manager = ResourceManager()
        manager.deposit_materials({'plastic': 10.0, 'metal': 5.0, 'glass': 3.0})

        assert manager.get_total_stored_weight() == 18.0


class TestPriceFluctuations:
    """Tests for market price fluctuation mechanics."""

    def test_update_triggers_price_fluctuation(self):
        """Test that update eventually triggers price changes."""
        manager = ResourceManager()
        # Set a controlled random seed for predictable results
        manager._random.seed(42)
        original_prices = dict(manager.material_values)

        # Update past the market update interval
        manager.update(manager._market_update_interval + 1)

        # At least one price should have changed
        changes = sum(1 for m in manager.material_values
                     if manager.material_values[m] != original_prices[m])
        assert changes > 0

    def test_price_fluctuation_within_range(self):
        """Test that price fluctuations stay within configured range."""
        manager = ResourceManager()
        manager._random.seed(123)

        # Run multiple update cycles
        for _ in range(10):
            manager.update(manager._market_update_interval + 1)

        for material, current_value in manager.material_values.items():
            base_value = manager.base_material_values[material]
            min_allowed = base_value * (1 - manager._price_fluctuation_range)
            max_allowed = base_value * (1 + manager._price_fluctuation_range)
            assert min_allowed <= current_value <= max_allowed


class TestStorageDecay:
    """Tests for organic material decay mechanics."""

    def test_decay_affects_organic_materials(self):
        """Test that decay affects organic, wood, and paper."""
        manager = ResourceManager()
        manager.deposit_materials({
            'organic': 100.0,
            'wood': 100.0,
            'paper': 100.0,
            'metal': 100.0  # Should not decay
        })

        # Trigger decay
        manager.update(manager._decay_interval + 1)

        assert manager.stored_materials['organic'] < 100.0
        assert manager.stored_materials['wood'] < 100.0
        assert manager.stored_materials['paper'] < 100.0
        assert manager.stored_materials['metal'] == 100.0

    def test_decay_rate_is_small(self):
        """Test that decay rate is the configured small amount."""
        manager = ResourceManager()
        initial_amount = 1000.0
        manager.deposit_materials({'organic': initial_amount})

        manager.update(manager._decay_interval + 1)

        expected_decay = initial_amount * manager._organic_decay_rate
        actual_amount = manager.stored_materials['organic']
        assert actual_amount == pytest.approx(initial_amount - expected_decay, rel=0.01)

    def test_decay_does_not_go_negative(self):
        """Test that decay cannot make quantity negative."""
        manager = ResourceManager()
        manager.deposit_materials({'organic': 0.001})

        # Run many decay cycles
        for _ in range(100):
            manager.update(manager._decay_interval + 1)

        assert manager.stored_materials['organic'] >= 0.0


class TestStatistics:
    """Tests for statistics tracking."""

    def test_get_stats_structure(self):
        """Test that get_stats returns expected keys."""
        manager = ResourceManager()
        stats = manager.get_stats()

        assert 'money' in stats
        assert 'total_stored_weight' in stats
        assert 'total_stored_value' in stats
        assert 'total_materials_collected' in stats
        assert 'total_money_earned' in stats
        assert 'material_types_stored' in stats

    def test_stats_reflect_operations(self):
        """Test that stats accurately reflect operations."""
        manager = ResourceManager()
        manager.deposit_materials({'plastic': 10.0, 'metal': 5.0})
        manager.sell_material('plastic', 5.0)

        stats = manager.get_stats()

        assert stats['total_materials_collected'] == 15.0
        assert stats['total_stored_weight'] == 10.0  # 5 plastic + 5 metal left
        assert stats['material_types_stored'] == 2
        assert stats['total_money_earned'] > 0


class TestRepr:
    """Tests for string representation."""

    def test_repr_contains_key_info(self):
        """Test that repr contains key information."""
        manager = ResourceManager()
        manager.deposit_materials({'plastic': 10.0})

        repr_str = repr(manager)

        assert 'ResourceManager' in repr_str
        assert 'money' in repr_str
        assert 'stored' in repr_str
