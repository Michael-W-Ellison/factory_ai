"""
MarketplaceManager - Handles selling recycled materials and delivery vehicles.

The marketplace allows players to sell collected materials at various locations
(train station, warehouse, dock). When materials are sold, a delivery vehicle
is dispatched to pick them up and transport them to the marketplace.
"""

import pygame
import random
from typing import List, Dict, Tuple, Optional
from enum import Enum


class DeliveryVehicleType(Enum):
    """Types of delivery vehicles."""
    SEMI_TRUCK = 'semi_truck'
    DELIVERY_VAN = 'delivery_van'
    CARGO_TRUCK = 'cargo_truck'


class DeliveryStatus(Enum):
    """Status of a delivery."""
    EN_ROUTE_TO_PICKUP = 'en_route_to_pickup'
    LOADING = 'loading'
    EN_ROUTE_TO_MARKETPLACE = 'en_route_to_marketplace'
    UNLOADING = 'unloading'
    COMPLETE = 'complete'


class DeliveryVehicle:
    """
    Delivery vehicle that picks up sold materials.

    Vehicles spawn at the marketplace, drive to the pickup location,
    load the materials, and return to the marketplace.
    """

    def __init__(self, vehicle_type: DeliveryVehicleType, spawn_x: float, spawn_y: float,
                 pickup_x: float, pickup_y: float, materials: Dict[str, float]):
        """
        Initialize a delivery vehicle.

        Args:
            vehicle_type: Type of delivery vehicle
            spawn_x: Marketplace X position (spawn point)
            spawn_y: Marketplace Y position (spawn point)
            pickup_x: Pickup location X
            pickup_y: Pickup location Y
            materials: Materials to pick up {type: quantity}
        """
        self.vehicle_type = vehicle_type
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y
        self.pickup_x = pickup_x
        self.pickup_y = pickup_y
        self.materials = materials.copy()

        # Current position
        self.world_x = spawn_x
        self.world_y = spawn_y

        # Movement
        self.speed = 50.0  # pixels per second
        self.target_x = pickup_x
        self.target_y = pickup_y
        self.moving = True
        self.facing_angle = 0.0

        # Status
        self.status = DeliveryStatus.EN_ROUTE_TO_PICKUP
        self.loading_time = 0.0
        self.loading_duration = 10.0  # 10 seconds to load
        self.unloading_time = 0.0
        self.unloading_duration = 10.0  # 10 seconds to unload

        # Visual
        if vehicle_type == DeliveryVehicleType.SEMI_TRUCK:
            self.width = 60
            self.height = 28
            self.color = (180, 180, 200)  # Light blue-gray
        elif vehicle_type == DeliveryVehicleType.CARGO_TRUCK:
            self.width = 48
            self.height = 24
            self.color = (160, 140, 120)  # Tan/brown
        else:  # DELIVERY_VAN
            self.width = 40
            self.height = 22
            self.color = (200, 200, 200)  # White

        self.outline_color = tuple(max(0, c - 40) for c in self.color)

    def update(self, dt: float, grid) -> bool:
        """
        Update delivery vehicle.

        Args:
            dt: Delta time in seconds
            grid: World grid for pathfinding

        Returns:
            bool: True if delivery is complete
        """
        import math

        if self.status == DeliveryStatus.EN_ROUTE_TO_PICKUP:
            # Drive to pickup location
            if self._update_movement(dt):
                # Arrived at pickup
                self.status = DeliveryStatus.LOADING
                self.loading_time = 0.0

        elif self.status == DeliveryStatus.LOADING:
            # Loading materials
            self.loading_time += dt
            if self.loading_time >= self.loading_duration:
                # Loading complete, return to marketplace
                self.status = DeliveryStatus.EN_ROUTE_TO_MARKETPLACE
                self.target_x = self.spawn_x
                self.target_y = self.spawn_y
                self.moving = True

        elif self.status == DeliveryStatus.EN_ROUTE_TO_MARKETPLACE:
            # Drive back to marketplace
            if self._update_movement(dt):
                # Arrived at marketplace
                self.status = DeliveryStatus.UNLOADING
                self.unloading_time = 0.0

        elif self.status == DeliveryStatus.UNLOADING:
            # Unloading materials
            self.unloading_time += dt
            if self.unloading_time >= self.unloading_duration:
                # Unloading complete
                self.status = DeliveryStatus.COMPLETE
                return True

        return False

    def _update_movement(self, dt: float) -> bool:
        """
        Update vehicle movement towards target.

        Args:
            dt: Delta time

        Returns:
            bool: True if reached target
        """
        import math

        if not self.moving:
            return True

        # Calculate direction to target
        dx = self.target_x - self.world_x
        dy = self.target_y - self.world_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 2.0:
            # Reached target
            self.world_x = self.target_x
            self.world_y = self.target_y
            self.moving = False
            return True

        # Move towards target
        move_distance = self.speed * dt
        if move_distance > distance:
            move_distance = distance

        # Normalize direction and move
        self.world_x += (dx / distance) * move_distance
        self.world_y += (dy / distance) * move_distance

        # Update facing angle
        self.facing_angle = math.degrees(math.atan2(dy, dx))

        return False

    def render(self, screen: pygame.Surface, camera):
        """
        Render the delivery vehicle.

        Args:
            screen: Pygame surface
            camera: Camera for world-to-screen transformation
        """
        import math

        # Calculate screen position
        screen_x, screen_y = camera.world_to_screen(self.world_x, self.world_y)

        # Apply camera zoom
        width_px = int(self.width * camera.zoom)
        height_px = int(self.height * camera.zoom)

        # Don't render if off screen
        margin = max(width_px, height_px)
        if (screen_x + margin < 0 or screen_x - margin > screen.get_width() or
            screen_y + margin < 0 or screen_y - margin > screen.get_height()):
            return

        # Create temp surface for rotation
        temp_size = int(max(width_px, height_px) * 1.5)
        temp_surface = pygame.Surface((temp_size, temp_size), pygame.SRCALPHA)

        # Center position on temp surface
        temp_x = temp_size // 2 - width_px // 2
        temp_y = temp_size // 2 - height_px // 2

        # Draw vehicle body
        body_rect = pygame.Rect(temp_x, temp_y, width_px, height_px)
        pygame.draw.rect(temp_surface, self.color, body_rect)
        pygame.draw.rect(temp_surface, self.outline_color, body_rect, 2)

        # Draw cab (front portion)
        cab_width = width_px // 3
        cab_rect = pygame.Rect(temp_x + width_px - cab_width, temp_y, cab_width, height_px)
        pygame.draw.rect(temp_surface, tuple(min(255, c + 20) for c in self.color), cab_rect)
        pygame.draw.rect(temp_surface, self.outline_color, cab_rect, 1)

        # Draw wheels
        wheel_radius = max(2, int(height_px * 0.2))
        wheel_y_front = temp_y + height_px - wheel_radius
        wheel_y_back = temp_y + height_px - wheel_radius

        # Front wheels
        pygame.draw.circle(temp_surface, (40, 40, 40),
                          (temp_x + width_px - cab_width // 2, wheel_y_front), wheel_radius)

        # Back wheels
        pygame.draw.circle(temp_surface, (40, 40, 40),
                          (temp_x + width_px // 4, wheel_y_back), wheel_radius)

        # Rotate and blit
        rotated_surface = pygame.transform.rotate(temp_surface, -self.facing_angle)
        rotated_rect = rotated_surface.get_rect(center=(screen_x, screen_y))
        screen.blit(rotated_surface, rotated_rect.topleft)

        # Draw status indicator (above vehicle)
        if camera.zoom >= 0.5:
            font = pygame.font.Font(None, 12)
            status_text = {
                DeliveryStatus.EN_ROUTE_TO_PICKUP: "→ Pickup",
                DeliveryStatus.LOADING: "Loading...",
                DeliveryStatus.EN_ROUTE_TO_MARKETPLACE: "→ Return",
                DeliveryStatus.UNLOADING: "Unloading...",
            }.get(self.status, "")

            if status_text:
                text_surface = font.render(status_text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(screen_x, screen_y - height_px - 10))
                bg_rect = text_rect.inflate(4, 2)
                pygame.draw.rect(screen, (0, 0, 0), bg_rect)
                screen.blit(text_surface, text_rect)


class MaterialSale:
    """Represents a sale of materials to a marketplace."""

    def __init__(self, marketplace_x: int, marketplace_y: int, pickup_x: float, pickup_y: float,
                 materials: Dict[str, float], total_value: float):
        """
        Initialize a material sale.

        Args:
            marketplace_x: Marketplace grid X
            marketplace_y: Marketplace grid Y
            pickup_x: Pickup location world X
            pickup_y: Pickup location world Y
            materials: Materials sold {type: quantity}
            total_value: Total sale value in currency
        """
        self.marketplace_x = marketplace_x
        self.marketplace_y = marketplace_y
        self.pickup_x = pickup_x
        self.pickup_y = pickup_y
        self.materials = materials
        self.total_value = total_value
        self.delivery_vehicle: Optional[DeliveryVehicle] = None
        self.complete = False


class MarketplaceManager:
    """
    Manages material sales and delivery vehicles.

    Handles:
    - Selling materials at marketplaces
    - Spawning delivery vehicles
    - Vehicle pathfinding and movement
    - Payment upon delivery
    """

    def __init__(self, grid, resource_manager):
        """
        Initialize marketplace manager.

        Args:
            grid: World grid
            resource_manager: Resource manager for currency
        """
        self.grid = grid
        self.resource_manager = resource_manager

        # Active sales
        self.active_sales: List[MaterialSale] = []

        # All delivery vehicles
        self.delivery_vehicles: List[DeliveryVehicle] = []

        # Marketplaces (will be populated by city generator)
        self.marketplaces = []  # List of marketplace buildings

    def register_marketplace(self, building):
        """
        Register a marketplace building.

        Args:
            building: Building with marketplace functionality
        """
        if hasattr(building, 'is_marketplace') and building.is_marketplace:
            self.marketplaces.append(building)

    def sell_materials(self, materials: Dict[str, float], pickup_x: float, pickup_y: float,
                      marketplace_building) -> Tuple[bool, str, float]:
        """
        Sell materials at a marketplace.

        Args:
            materials: Materials to sell {type: quantity}
            pickup_x: Pickup location world X
            pickup_y: Pickup location world Y
            marketplace_building: The marketplace building

        Returns:
            Tuple[bool, str, float]: (success, message, value)
        """
        if not hasattr(marketplace_building, 'material_prices'):
            return False, "Not a valid marketplace", 0.0

        # Calculate total value
        total_value = 0.0
        accepted_materials = {}

        for material_type, quantity in materials.items():
            if material_type in marketplace_building.material_prices:
                price_per_kg = marketplace_building.material_prices[material_type]
                total_value += quantity * price_per_kg
                accepted_materials[material_type] = quantity

        if not accepted_materials:
            return False, "No acceptable materials", 0.0

        # Create sale
        sale = MaterialSale(
            marketplace_x=marketplace_building.grid_x,
            marketplace_y=marketplace_building.grid_y,
            pickup_x=pickup_x,
            pickup_y=pickup_y,
            materials=accepted_materials,
            total_value=total_value
        )

        # Spawn delivery vehicle
        marketplace_world_x = marketplace_building.grid_x * self.grid.tile_size
        marketplace_world_y = marketplace_building.grid_y * self.grid.tile_size

        # Choose vehicle type based on quantity
        total_weight = sum(accepted_materials.values())
        if total_weight > 500:
            vehicle_type = DeliveryVehicleType.SEMI_TRUCK
        elif total_weight > 200:
            vehicle_type = DeliveryVehicleType.CARGO_TRUCK
        else:
            vehicle_type = DeliveryVehicleType.DELIVERY_VAN

        vehicle = DeliveryVehicle(
            vehicle_type=vehicle_type,
            spawn_x=marketplace_world_x,
            spawn_y=marketplace_world_y,
            pickup_x=pickup_x,
            pickup_y=pickup_y,
            materials=accepted_materials
        )

        sale.delivery_vehicle = vehicle
        self.active_sales.append(sale)
        self.delivery_vehicles.append(vehicle)

        return True, f"Sale created: ${total_value:.2f}", total_value

    def update(self, dt: float):
        """
        Update marketplace manager.

        Args:
            dt: Delta time in seconds
        """
        # Update all delivery vehicles
        for vehicle in self.delivery_vehicles[:]:
            complete = vehicle.update(dt, self.grid)

            if complete:
                # Find associated sale
                for sale in self.active_sales:
                    if sale.delivery_vehicle == vehicle:
                        # Pay the player
                        if hasattr(self.resource_manager, 'money'):
                            self.resource_manager.money += sale.total_value
                        sale.complete = True
                        print(f"💰 Delivery complete! Received ${sale.total_value:.2f}")

                # Remove completed vehicle
                self.delivery_vehicles.remove(vehicle)

        # Remove completed sales
        self.active_sales = [s for s in self.active_sales if not s.complete]

    def render(self, screen: pygame.Surface, camera):
        """
        Render all delivery vehicles.

        Args:
            screen: Pygame surface
            camera: Camera
        """
        for vehicle in self.delivery_vehicles:
            vehicle.render(screen, camera)

    def get_statistics(self) -> Dict:
        """Get marketplace statistics."""
        return {
            'active_sales': len(self.active_sales),
            'delivery_vehicles': len(self.delivery_vehicles),
            'marketplaces': len(self.marketplaces),
        }
