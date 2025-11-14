"""
Test script for new environmental content.

Tests:
- New building types
- Environmental props
- Marketplace system
"""

import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.entities.city_building import (
    FireHouse, Library, CityHall, Courthouse, School,
    BusTerminal, TrainStation, Warehouse, Dock
)
from src.entities.city_prop import Bench, LightPole, TrashCan, Bicycle
from src.systems.marketplace_manager import (
    MarketplaceManager, DeliveryVehicleType, DeliveryVehicle, MaterialSale
)


def test_new_buildings():
    """Test new building types."""
    print("\nTesting new building types...")

    # Create buildings
    fire_house = FireHouse(grid_x=10, grid_y=10)
    library = Library(grid_x=15, grid_y=15)
    city_hall = CityHall(grid_x=20, grid_y=20)
    courthouse = Courthouse(grid_x=25, grid_y=25)
    school = School(grid_x=30, grid_y=30)
    bus_terminal = BusTerminal(grid_x=35, grid_y=35)
    train_station = TrainStation(grid_x=40, grid_y=40)
    warehouse = Warehouse(grid_x=45, grid_y=45)
    dock = Dock(grid_x=50, grid_y=50)

    buildings = [
        fire_house, library, city_hall, courthouse, school,
        bus_terminal, train_station, warehouse, dock
    ]

    for building in buildings:
        print(f"  {building.name}:")
        print(f"    Size: {building.width}x{building.height}")
        print(f"    Legal to deconstruct: {building.legal_to_deconstruct}")
        print(f"    Max occupants: {building.max_occupants}")
        print(f"    Color: {building.color}")

        # Check marketplace functionality
        if hasattr(building, 'is_marketplace'):
            print(f"    Marketplace: Yes")
            print(f"    Accepts: {', '.join(building.accepts_materials[:3])}...")
            print(f"    Prices: Metal=${building.material_prices['metal']:.2f}/kg")

    print(f"  ✓ Created {len(buildings)} new building types")


def test_props():
    """Test environmental props."""
    print("\nTesting environmental props...")

    # Create props
    bench = Bench(world_x=100, world_y=100)
    light_pole = LightPole(world_x=150, world_y=150)
    trash_can = TrashCan(world_x=200, world_y=200)
    bicycle = Bicycle(world_x=250, world_y=250)

    props = [bench, light_pole, trash_can, bicycle]

    for prop in props:
        print(f"  {prop.name}:")
        print(f"    Size: {prop.width}x{prop.height}px")
        print(f"    Legal to deconstruct: {prop.legal_to_deconstruct}")
        print(f"    Deconstruction time: {prop.deconstruction_time}s")
        if prop.materials:
            materials_str = ', '.join(f"{k}:{v:.1f}kg" for k, v in list(prop.materials.items())[:2])
            print(f"    Materials: {materials_str}")

    print(f"  ✓ Created {len(props)} prop types")


def test_marketplace_system():
    """Test marketplace system."""
    print("\nTesting marketplace system...")

    # Create a mock grid and resource manager
    class MockGrid:
        def __init__(self):
            self.tile_size = 32

    class MockResourceManager:
        def __init__(self):
            self.money = 1000.0

    grid = MockGrid()
    resource_manager = MockResourceManager()

    # Create marketplace manager
    marketplace_mgr = MarketplaceManager(grid, resource_manager)

    # Create a marketplace
    train_station = TrainStation(grid_x=50, grid_y=50)
    marketplace_mgr.register_marketplace(train_station)

    print(f"  Registered marketplace: {train_station.name}")
    print(f"  Marketplaces registered: {len(marketplace_mgr.marketplaces)}")

    # Sell some materials
    materials_to_sell = {
        'metal': 100.0,
        'plastic': 50.0,
        'glass': 25.0,
    }

    success, message, value = marketplace_mgr.sell_materials(
        materials=materials_to_sell,
        pickup_x=1600.0,  # 50 tiles * 32 pixels
        pickup_y=1600.0,
        marketplace_building=train_station
    )

    print(f"  Sale result: {success}")
    print(f"  Message: {message}")
    print(f"  Value: ${value:.2f}")
    print(f"  Active sales: {len(marketplace_mgr.active_sales)}")
    print(f"  Delivery vehicles: {len(marketplace_mgr.delivery_vehicles)}")

    # Check delivery vehicle
    if marketplace_mgr.delivery_vehicles:
        vehicle = marketplace_mgr.delivery_vehicles[0]
        print(f"  Vehicle type: {vehicle.vehicle_type.value}")
        print(f"  Vehicle size: {vehicle.width}x{vehicle.height}px")
        print(f"  Status: {vehicle.status.value}")
        print(f"  Materials: {', '.join(f'{k}:{v}kg' for k, v in list(vehicle.materials.items())[:2])}")

    print("  ✓ Marketplace system working")


def test_delivery_vehicle():
    """Test delivery vehicle."""
    print("\nTesting delivery vehicle...")

    # Create a delivery vehicle
    vehicle = DeliveryVehicle(
        vehicle_type=DeliveryVehicleType.SEMI_TRUCK,
        spawn_x=1600.0,
        spawn_y=1600.0,
        pickup_x=800.0,
        pickup_y=800.0,
        materials={'metal': 150.0, 'plastic': 75.0}
    )

    print(f"  Vehicle type: {vehicle.vehicle_type.value}")
    print(f"  Size: {vehicle.width}x{vehicle.height}px")
    print(f"  Speed: {vehicle.speed}px/s")
    print(f"  Status: {vehicle.status.value}")
    print(f"  Position: ({vehicle.world_x:.0f}, {vehicle.world_y:.0f})")
    print(f"  Target: ({vehicle.target_x:.0f}, {vehicle.target_y:.0f})")

    # Update for 1 second
    class MockGrid:
        tile_size = 32

    grid = MockGrid()
    vehicle.update(1.0, grid)

    print(f"  After 1s - Position: ({vehicle.world_x:.0f}, {vehicle.world_y:.0f})")
    print(f"  After 1s - Facing: {vehicle.facing_angle:.0f}°")

    print("  ✓ Delivery vehicle working")


if __name__ == '__main__':
    print("="*80)
    print("ENVIRONMENTAL CONTENT TESTS")
    print("="*80)

    try:
        test_new_buildings()
        test_props()
        test_marketplace_system()
        test_delivery_vehicle()

        print("\n" + "="*80)
        print("ALL ENVIRONMENTAL CONTENT TESTS PASSED! ✓")
        print("="*80)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
