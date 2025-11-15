"""
Animal Entity System - Wildlife and pets for the simulation.

Provides base Animal class and specific animal types with behaviors.
"""

import random
import math
from enum import Enum
from typing import Tuple, Optional, List
import pygame

from graphics import SpriteType, Direction, AnimalAnimationController, BirdAnimationController, FishAnimationController


class AnimalBehavior(Enum):
    """Animal behavior states."""
    IDLE = "idle"
    WANDER = "wander"
    FLEE = "flee"
    CHASE = "chase"
    EAT = "eat"
    SLEEP = "sleep"
    FOLLOW = "follow"  # For pets following NPCs


class Animal:
    """
    Base class for all animals in the simulation.

    Handles movement, behavior AI, and interactions.
    """

    def __init__(self, x: float, y: float, sprite_type: SpriteType, variant: int = 0):
        """
        Initialize an animal.

        Args:
            x: X position in world coordinates
            y: Y position in world coordinates
            sprite_type: Type of sprite for this animal
            variant: Color/style variant number
        """
        self.x = x
        self.y = y
        self.sprite_type = sprite_type
        self.variant = variant

        # Movement
        self.direction = Direction.EAST
        self.speed = 2.0  # Base speed in pixels per frame
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        # Behavior
        self.behavior = AnimalBehavior.IDLE
        self.behavior_timer = 0.0  # Time until next behavior change
        self.target = None  # Target position or entity

        # Detection
        self.vision_range = 100.0  # How far animal can see
        self.flee_distance = 80.0   # Distance at which to flee from threats

        # Animation
        self.animation_controller = AnimalAnimationController()
        self.animation_frame = 0

        # State
        self.alive = True
        self.age = 0.0  # Age in seconds

    def update(self, dt: float):
        """
        Update animal state and behavior.

        Args:
            dt: Delta time in seconds
        """
        if not self.alive:
            return

        self.age += dt
        self.behavior_timer -= dt

        # Update behavior if timer expired
        if self.behavior_timer <= 0:
            self._choose_behavior()

        # Execute current behavior
        self._execute_behavior(dt)

        # Update movement
        self._update_movement(dt)

        # Update animation
        self.animation_frame = self.animation_controller.update_for_behavior(
            self.behavior.value, dt
        )

    def _choose_behavior(self):
        """Choose a new random behavior."""
        # Default: wander or idle
        if random.random() < 0.7:
            self.behavior = AnimalBehavior.WANDER
            self.behavior_timer = random.uniform(2.0, 5.0)
            # Choose random direction
            angle = random.uniform(0, 2 * math.pi)
            self.velocity_x = math.cos(angle) * self.speed
            self.velocity_y = math.sin(angle) * self.speed
        else:
            self.behavior = AnimalBehavior.IDLE
            self.behavior_timer = random.uniform(1.0, 3.0)
            self.velocity_x = 0
            self.velocity_y = 0

    def _execute_behavior(self, dt: float):
        """Execute the current behavior."""
        if self.behavior == AnimalBehavior.FLEE:
            # Flee from threat (target)
            if self.target:
                dx = self.x - self.target[0]
                dy = self.y - self.target[1]
                distance = math.sqrt(dx*dx + dy*dy)
                if distance > 0:
                    # Flee in opposite direction at increased speed
                    flee_speed = self.speed * 1.5
                    self.velocity_x = (dx / distance) * flee_speed
                    self.velocity_y = (dy / distance) * flee_speed

        elif self.behavior == AnimalBehavior.CHASE:
            # Chase target
            if self.target:
                dx = self.target[0] - self.x
                dy = self.target[1] - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                if distance > 0:
                    chase_speed = self.speed * 1.3
                    self.velocity_x = (dx / distance) * chase_speed
                    self.velocity_y = (dy / distance) * chase_speed

        elif self.behavior == AnimalBehavior.EAT:
            # Stop to eat
            self.velocity_x = 0
            self.velocity_y = 0

    def _update_movement(self, dt: float):
        """Update position based on velocity."""
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Update direction based on movement
        if abs(self.velocity_x) > 0.1 or abs(self.velocity_y) > 0.1:
            angle = math.atan2(self.velocity_y, self.velocity_x)
            angle_deg = math.degrees(angle)

            # Convert to 8-way direction
            if angle_deg < 0:
                angle_deg += 360

            if angle_deg < 22.5 or angle_deg >= 337.5:
                self.direction = Direction.EAST
            elif angle_deg < 67.5:
                self.direction = Direction.SOUTHEAST
            elif angle_deg < 112.5:
                self.direction = Direction.SOUTH
            elif angle_deg < 157.5:
                self.direction = Direction.SOUTHWEST
            elif angle_deg < 202.5:
                self.direction = Direction.WEST
            elif angle_deg < 247.5:
                self.direction = Direction.NORTHWEST
            elif angle_deg < 292.5:
                self.direction = Direction.NORTH
            else:
                self.direction = Direction.NORTHEAST

    def flee_from(self, threat_x: float, threat_y: float):
        """
        Start fleeing from a threat.

        Args:
            threat_x: X position of threat
            threat_y: Y position of threat
        """
        self.behavior = AnimalBehavior.FLEE
        self.target = (threat_x, threat_y)
        self.behavior_timer = random.uniform(3.0, 5.0)

    def chase(self, target_x: float, target_y: float):
        """
        Start chasing a target.

        Args:
            target_x: X position of target
            target_y: Y position of target
        """
        self.behavior = AnimalBehavior.CHASE
        self.target = (target_x, target_y)
        self.behavior_timer = random.uniform(2.0, 4.0)

    def check_threat_proximity(self, entities: List) -> bool:
        """
        Check if any threatening entities are nearby.

        Args:
            entities: List of entities to check

        Returns:
            bool: True if threat detected
        """
        for entity in entities:
            # Check distance
            dx = entity.x - self.x
            dy = entity.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance < self.flee_distance:
                # Flee from this entity
                self.flee_from(entity.x, entity.y)
                return True

        return False

    def get_position(self) -> Tuple[float, float]:
        """Get animal position."""
        return (self.x, self.y)

    def get_sprite_params(self) -> dict:
        """Get parameters for sprite rendering."""
        return {
            'sprite_type': self.sprite_type,
            'direction': self.direction,
            'frame': self.animation_frame,
            'variant': self.variant,
        }


class Bird(Animal):
    """Small bird (pigeon, sparrow, etc.)."""

    def __init__(self, x: float, y: float, variant: int = 0):
        super().__init__(x, y, SpriteType.BIRD, variant)
        self.speed = 3.0  # Birds are fast
        self.vision_range = 120.0
        self.flee_distance = 100.0
        self.animation_controller = BirdAnimationController()

        # Birds fly, so they're less affected by ground obstacles
        self.flying = True


class BirdOfPrey(Animal):
    """Large bird of prey (hawk, eagle, etc.)."""

    def __init__(self, x: float, y: float, variant: int = 0):
        super().__init__(x, y, SpriteType.BIRD_OF_PREY, variant)
        self.speed = 4.0  # Fast predator
        self.vision_range = 200.0  # Excellent vision
        self.flee_distance = 50.0  # Not easily scared
        self.animation_controller = BirdAnimationController()

        self.flying = True
        self.hunting = True  # Can catch fish and small animals


class Dog(Animal):
    """Dog - can be pet or stray."""

    def __init__(self, x: float, y: float, variant: int = 0, is_pet: bool = True):
        super().__init__(x, y, SpriteType.DOG, variant)
        self.speed = 2.5
        self.vision_range = 150.0
        self.flee_distance = 60.0  # Dogs are braver

        self.is_pet = is_pet
        self.owner = None  # NPC owner if pet

    def _choose_behavior(self):
        """Dogs have different behavior if they're pets."""
        if self.is_pet and self.owner:
            # Pet dogs follow their owner
            self.behavior = AnimalBehavior.FOLLOW
            self.target = self.owner
            self.behavior_timer = 1.0
        else:
            # Stray dogs wander
            super()._choose_behavior()

    def _execute_behavior(self, dt: float):
        """Execute dog-specific behaviors."""
        if self.behavior == AnimalBehavior.FOLLOW and self.owner:
            # Follow owner
            dx = self.owner.x - self.x
            dy = self.owner.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)

            # Stay within certain distance
            if distance > 50:  # Too far, catch up
                self.velocity_x = (dx / distance) * self.speed
                self.velocity_y = (dy / distance) * self.speed
            elif distance < 20:  # Too close, slow down
                self.velocity_x = 0
                self.velocity_y = 0
            else:
                # Match owner's speed
                self.velocity_x = (dx / distance) * self.speed * 0.5
                self.velocity_y = (dy / distance) * self.speed * 0.5
        else:
            super()._execute_behavior(dt)


class Cat(Animal):
    """Cat - independent hunter."""

    def __init__(self, x: float, y: float, variant: int = 0):
        super().__init__(x, y, SpriteType.CAT, variant)
        self.speed = 3.0  # Cats are quick
        self.vision_range = 100.0
        self.flee_distance = 70.0

        self.hunting = True  # Cats hunt birds and rats


class Deer(Animal):
    """Deer - timid herbivore."""

    def __init__(self, x: float, y: float, variant: int = 0):
        super().__init__(x, y, SpriteType.DEER, variant)
        self.speed = 3.5  # Fast when fleeing
        self.vision_range = 150.0
        self.flee_distance = 120.0  # Very timid

        self.grazing = True  # Deer graze on grass

    def _choose_behavior(self):
        """Deer spend time grazing."""
        if random.random() < 0.4:
            self.behavior = AnimalBehavior.EAT  # Grazing
            self.behavior_timer = random.uniform(3.0, 8.0)
            self.velocity_x = 0
            self.velocity_y = 0
        else:
            super()._choose_behavior()


class Rat(Animal):
    """Small rodent - scurries around."""

    def __init__(self, x: float, y: float, variant: int = 0):
        super().__init__(x, y, SpriteType.RAT, variant)
        self.speed = 2.0
        self.vision_range = 60.0  # Poor vision
        self.flee_distance = 80.0  # Very skittish

    def _choose_behavior(self):
        """Rats prefer to hide and scurry."""
        if random.random() < 0.5:
            # Short, quick movements
            self.behavior = AnimalBehavior.WANDER
            self.behavior_timer = random.uniform(0.5, 1.5)
            angle = random.uniform(0, 2 * math.pi)
            self.velocity_x = math.cos(angle) * self.speed
            self.velocity_y = math.sin(angle) * self.speed
        else:
            self.behavior = AnimalBehavior.IDLE
            self.behavior_timer = random.uniform(1.0, 2.0)
            self.velocity_x = 0
            self.velocity_y = 0


class Raccoon(Animal):
    """Raccoon - curious scavenger."""

    def __init__(self, x: float, y: float, variant: int = 0):
        super().__init__(x, y, SpriteType.RACCOON, variant)
        self.speed = 2.0
        self.vision_range = 100.0
        self.flee_distance = 90.0

        self.nocturnal = True  # More active at night


class Fish(Animal):
    """Fish - swims in water bodies."""

    def __init__(self, x: float, y: float, variant: int = 0):
        super().__init__(x, y, SpriteType.FISH, variant)
        self.speed = 1.5
        self.vision_range = 80.0
        self.flee_distance = 100.0
        self.animation_controller = FishAnimationController()

        self.in_water = True  # Must stay in water
        self.school = None  # Fish can be part of a school

    def _choose_behavior(self):
        """Fish school together and swim in patterns."""
        if self.school and len(self.school) > 1:
            # Follow school
            # Calculate center of school
            center_x = sum(f.x for f in self.school) / len(self.school)
            center_y = sum(f.y for f in self.school) / len(self.school)

            # Move towards center
            dx = center_x - self.x
            dy = center_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance > 0:
                self.velocity_x = (dx / distance) * self.speed
                self.velocity_y = (dy / distance) * self.speed

            self.behavior = AnimalBehavior.WANDER
            self.behavior_timer = random.uniform(2.0, 4.0)
        else:
            # Solo fish wander
            super()._choose_behavior()
