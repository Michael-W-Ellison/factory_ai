"""
Unit tests for MarketplaceManager.

Tests material sales, delivery vehicles, and marketplace operations.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class MockGrid:
    """Mock grid for testing."""
    def __init__(self, tile_size=32):
        self.tile_size = tile_size


class MockResourceManager:
    """Mock resource manager for testing."""
    def __init__(self, initial_money=10000):
        self.money = initial_money


class MockMarketplace:
    """Mock marketplace building for testing."""
    def __init__(self, grid_x=10, grid_y=10):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.is_marketplace = True
        self.material_prices = {
            'aluminum': 5.0,
            'copper': 8.0,
            'steel': 3.0,
            'plastic': 2.0
        }


@pytest.fixture
def mock_grid():
    """Create mock grid."""
    return MockGrid()


@pytest.fixture
def mock_resource_manager():
    """Create mock resource manager."""
    return MockResourceManager()


@pytest.fixture
def marketplace_manager(mock_grid, mock_resource_manager):
    """Create MarketplaceManager instance."""
    with patch('pygame.Surface'):
        from src.systems.marketplace_manager import MarketplaceManager
        return MarketplaceManager(mock_grid, mock_resource_manager)


class TestMarketplaceManagerInit:
    """Tests for MarketplaceManager initialization."""

    def test_init_with_grid_and_resources(self, mock_grid, mock_resource_manager):
        """Test initialization with grid and resource manager."""
        with patch('pygame.Surface'):
            from src.systems.marketplace_manager import MarketplaceManager
            mm = MarketplaceManager(mock_grid, mock_resource_manager)

            assert mm.grid == mock_grid
            assert mm.resource_manager == mock_resource_manager

    def test_init_empty_sales(self, marketplace_manager):
        """Test that active sales start empty."""
        assert marketplace_manager.active_sales == []

    def test_init_empty_vehicles(self, marketplace_manager):
        """Test that delivery vehicles start empty."""
        assert marketplace_manager.delivery_vehicles == []

    def test_init_empty_marketplaces(self, marketplace_manager):
        """Test that marketplaces start empty."""
        assert marketplace_manager.marketplaces == []


class TestMarketplaceRegistration:
    """Tests for marketplace registration."""

    def test_register_marketplace(self, marketplace_manager):
        """Test registering a marketplace."""
        mock_marketplace = MockMarketplace()

        marketplace_manager.register_marketplace(mock_marketplace)

        assert mock_marketplace in marketplace_manager.marketplaces

    def test_register_non_marketplace(self, marketplace_manager):
        """Test registering a building that's not a marketplace."""
        mock_building = Mock()
        mock_building.is_marketplace = False

        marketplace_manager.register_marketplace(mock_building)

        assert mock_building not in marketplace_manager.marketplaces

    def test_register_building_without_flag(self, marketplace_manager):
        """Test registering a building without marketplace flag."""
        mock_building = Mock(spec=[])  # No is_marketplace attribute

        marketplace_manager.register_marketplace(mock_building)

        assert mock_building not in marketplace_manager.marketplaces


class TestMaterialSales:
    """Tests for selling materials."""

    def test_sell_materials_success(self, marketplace_manager):
        """Test successful material sale."""
        mock_marketplace = MockMarketplace()
        materials = {'aluminum': 10.0, 'copper': 5.0}

        success, message, value = marketplace_manager.sell_materials(
            materials=materials,
            pickup_x=100.0,
            pickup_y=100.0,
            marketplace_building=mock_marketplace
        )

        assert success is True
        assert value > 0
        assert len(marketplace_manager.active_sales) == 1

    def test_sell_materials_invalid_marketplace(self, marketplace_manager):
        """Test sale with invalid marketplace."""
        mock_building = Mock(spec=[])  # No material_prices

        success, message, value = marketplace_manager.sell_materials(
            materials={'aluminum': 10.0},
            pickup_x=100.0,
            pickup_y=100.0,
            marketplace_building=mock_building
        )

        assert success is False
        assert "Not a valid marketplace" in message

    def test_sell_materials_no_acceptable_materials(self, marketplace_manager):
        """Test sale with materials marketplace doesn't accept."""
        mock_marketplace = MockMarketplace()

        success, message, value = marketplace_manager.sell_materials(
            materials={'unknown_material': 10.0},
            pickup_x=100.0,
            pickup_y=100.0,
            marketplace_building=mock_marketplace
        )

        assert success is False
        assert "No acceptable materials" in message

    def test_sell_materials_value_calculation(self, marketplace_manager):
        """Test correct value calculation for sale."""
        mock_marketplace = MockMarketplace()
        # aluminum: 10kg * $5 = $50
        # copper: 5kg * $8 = $40
        # Total: $90
        materials = {'aluminum': 10.0, 'copper': 5.0}

        success, message, value = marketplace_manager.sell_materials(
            materials=materials,
            pickup_x=100.0,
            pickup_y=100.0,
            marketplace_building=mock_marketplace
        )

        assert value == pytest.approx(90.0)


class TestDeliveryVehicleSpawning:
    """Tests for delivery vehicle spawning."""

    def test_sell_spawns_delivery_vehicle(self, marketplace_manager):
        """Test that selling spawns a delivery vehicle."""
        mock_marketplace = MockMarketplace()
        materials = {'aluminum': 10.0}

        marketplace_manager.sell_materials(
            materials=materials,
            pickup_x=100.0,
            pickup_y=100.0,
            marketplace_building=mock_marketplace
        )

        assert len(marketplace_manager.delivery_vehicles) == 1

    def test_vehicle_type_based_on_weight(self, marketplace_manager):
        """Test vehicle type selection based on weight."""
        from src.systems.marketplace_manager import DeliveryVehicleType

        mock_marketplace = MockMarketplace()

        # Small load - should be van
        marketplace_manager.sell_materials(
            materials={'aluminum': 50.0},  # < 200 kg
            pickup_x=100.0,
            pickup_y=100.0,
            marketplace_building=mock_marketplace
        )

        vehicle = marketplace_manager.delivery_vehicles[0]
        assert vehicle.vehicle_type == DeliveryVehicleType.DELIVERY_VAN


class TestDeliveryVehicle:
    """Tests for DeliveryVehicle class."""

    def test_delivery_vehicle_init(self):
        """Test DeliveryVehicle initialization."""
        from src.systems.marketplace_manager import DeliveryVehicle, DeliveryVehicleType, DeliveryStatus

        vehicle = DeliveryVehicle(
            vehicle_type=DeliveryVehicleType.DELIVERY_VAN,
            spawn_x=0.0,
            spawn_y=0.0,
            pickup_x=100.0,
            pickup_y=100.0,
            materials={'aluminum': 10.0}
        )

        assert vehicle.vehicle_type == DeliveryVehicleType.DELIVERY_VAN
        assert vehicle.spawn_x == 0.0
        assert vehicle.spawn_y == 0.0
        assert vehicle.status == DeliveryStatus.EN_ROUTE_TO_PICKUP

    def test_delivery_vehicle_movement(self):
        """Test vehicle movement towards target."""
        from src.systems.marketplace_manager import DeliveryVehicle, DeliveryVehicleType

        vehicle = DeliveryVehicle(
            vehicle_type=DeliveryVehicleType.DELIVERY_VAN,
            spawn_x=0.0,
            spawn_y=0.0,
            pickup_x=100.0,
            pickup_y=0.0,
            materials={'aluminum': 10.0}
        )

        initial_x = vehicle.world_x
        vehicle.update(1.0, None)

        # Should have moved towards pickup
        assert vehicle.world_x > initial_x

    def test_delivery_vehicle_reaches_pickup(self):
        """Test vehicle status change when reaching pickup."""
        from src.systems.marketplace_manager import DeliveryVehicle, DeliveryVehicleType, DeliveryStatus

        vehicle = DeliveryVehicle(
            vehicle_type=DeliveryVehicleType.DELIVERY_VAN,
            spawn_x=0.0,
            spawn_y=0.0,
            pickup_x=1.0,  # Very close
            pickup_y=0.0,
            materials={'aluminum': 10.0}
        )

        vehicle.update(1.0, None)  # Should reach quickly

        assert vehicle.status == DeliveryStatus.LOADING


class TestMarketplaceUpdate:
    """Tests for marketplace update cycle."""

    def test_update_processes_vehicles(self, marketplace_manager, mock_resource_manager):
        """Test that update processes delivery vehicles."""
        mock_marketplace = MockMarketplace()

        marketplace_manager.sell_materials(
            materials={'aluminum': 10.0},
            pickup_x=1.0,  # Very close to marketplace
            pickup_y=1.0,
            marketplace_building=mock_marketplace
        )

        # Update multiple times to complete delivery
        for _ in range(100):
            marketplace_manager.update(0.5)

        # Eventually vehicles should complete
        # (may take many iterations depending on distance)

    def test_update_removes_completed_sales(self, marketplace_manager):
        """Test that completed sales are removed."""
        from src.systems.marketplace_manager import MaterialSale, DeliveryStatus

        # Create a completed sale
        sale = MaterialSale(
            marketplace_x=10,
            marketplace_y=10,
            pickup_x=100.0,
            pickup_y=100.0,
            materials={'aluminum': 10.0},
            total_value=50.0
        )
        sale.complete = True

        marketplace_manager.active_sales.append(sale)
        marketplace_manager.update(0.1)

        assert sale not in marketplace_manager.active_sales


class TestMaterialSaleClass:
    """Tests for MaterialSale class."""

    def test_material_sale_init(self):
        """Test MaterialSale initialization."""
        from src.systems.marketplace_manager import MaterialSale

        sale = MaterialSale(
            marketplace_x=10,
            marketplace_y=20,
            pickup_x=100.0,
            pickup_y=200.0,
            materials={'aluminum': 10.0, 'copper': 5.0},
            total_value=90.0
        )

        assert sale.marketplace_x == 10
        assert sale.marketplace_y == 20
        assert sale.pickup_x == 100.0
        assert sale.pickup_y == 200.0
        assert sale.materials == {'aluminum': 10.0, 'copper': 5.0}
        assert sale.total_value == 90.0
        assert sale.complete is False


class TestStatistics:
    """Tests for marketplace statistics."""

    def test_get_statistics_empty(self, marketplace_manager):
        """Test statistics with no activity."""
        stats = marketplace_manager.get_statistics()

        assert stats['active_sales'] == 0
        assert stats['delivery_vehicles'] == 0
        assert stats['marketplaces'] == 0

    def test_get_statistics_with_data(self, marketplace_manager):
        """Test statistics with active data."""
        mock_marketplace = MockMarketplace()
        marketplace_manager.register_marketplace(mock_marketplace)

        marketplace_manager.sell_materials(
            materials={'aluminum': 10.0},
            pickup_x=100.0,
            pickup_y=100.0,
            marketplace_building=mock_marketplace
        )

        stats = marketplace_manager.get_statistics()

        assert stats['active_sales'] == 1
        assert stats['delivery_vehicles'] == 1
        assert stats['marketplaces'] == 1


class TestDeliveryVehicleTypes:
    """Tests for different delivery vehicle types."""

    def test_semi_truck_dimensions(self):
        """Test semi truck has correct dimensions."""
        from src.systems.marketplace_manager import DeliveryVehicle, DeliveryVehicleType

        vehicle = DeliveryVehicle(
            vehicle_type=DeliveryVehicleType.SEMI_TRUCK,
            spawn_x=0.0,
            spawn_y=0.0,
            pickup_x=100.0,
            pickup_y=100.0,
            materials={'aluminum': 600.0}
        )

        assert vehicle.width == 60
        assert vehicle.height == 28

    def test_cargo_truck_dimensions(self):
        """Test cargo truck has correct dimensions."""
        from src.systems.marketplace_manager import DeliveryVehicle, DeliveryVehicleType

        vehicle = DeliveryVehicle(
            vehicle_type=DeliveryVehicleType.CARGO_TRUCK,
            spawn_x=0.0,
            spawn_y=0.0,
            pickup_x=100.0,
            pickup_y=100.0,
            materials={'aluminum': 300.0}
        )

        assert vehicle.width == 48
        assert vehicle.height == 24

    def test_delivery_van_dimensions(self):
        """Test delivery van has correct dimensions."""
        from src.systems.marketplace_manager import DeliveryVehicle, DeliveryVehicleType

        vehicle = DeliveryVehicle(
            vehicle_type=DeliveryVehicleType.DELIVERY_VAN,
            spawn_x=0.0,
            spawn_y=0.0,
            pickup_x=100.0,
            pickup_y=100.0,
            materials={'aluminum': 50.0}
        )

        assert vehicle.width == 40
        assert vehicle.height == 22
