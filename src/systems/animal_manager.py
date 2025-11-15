"""
Animal Manager - Manages wildlife and pet spawning, behaviors, and interactions.

Handles animal lifecycle, spawning based on habitat, and animal-to-animal/NPC interactions.
"""

import random
import math
from typing import List, Dict, Tuple, Optional

from entities.animal import (
    Animal, Bird, BirdOfPrey, Dog, Cat, Deer, Rat, Raccoon, Fish,
    AnimalBehavior
)


class AnimalManager:
    """
    Manages all animals in the simulation.

    Handles spawning, lifecycle, and interactions.
    """

    def __init__(self, world_width: int = 2000, world_height: int = 2000):
        """
        Initialize the animal manager.

        Args:
            world_width: Width of the world in pixels
            world_height: Height of the world in pixels
        """
        self.world_width = world_width
        self.world_height = world_height

        # Animal collections
        self.animals: List[Animal] = []
        self.fish_schools: List[List[Fish]] = []  # Groups of fish

        # Spawning parameters
        self.max_animals = {
            'birds': 20,
            'dogs': 5,
            'cats': 8,
            'deer': 6,
            'rats': 10,
            'raccoons': 4,
            'fish': 30,
            'birds_of_prey': 3,
        }

        # Spawn zones (will be updated based on terrain)
        self.spawn_zones = {
            'birds': [],       # Can spawn anywhere
            'water': [],       # Water bodies for fish
            'forest': [],      # Forest edges for deer
            'urban': [],       # Urban areas for rats, cats, dogs
            'park': [],        # Parks for birds, dogs
        }

        # Interaction cooldowns (to prevent spam)
        self.interaction_cooldowns: Dict[Tuple[int, int], float] = {}

        # Statistics
        self.stats = {
            'total_spawned': 0,
            'interactions': 0,
        }

    def add_spawn_zone(self, zone_type: str, x: int, y: int, radius: int):
        """
        Add a spawn zone for certain animal types.

        Args:
            zone_type: Type of zone (water, forest, urban, park)
            x: Center X coordinate
            y: Center Y coordinate
            radius: Radius of the zone
        """
        if zone_type in self.spawn_zones:
            self.spawn_zones[zone_type].append({
                'x': x,
                'y': y,
                'radius': radius
            })

    def spawn_initial_animals(self):
        """Spawn initial animal population."""
        # Spawn birds
        for _ in range(random.randint(10, self.max_animals['birds'])):
            self.spawn_animal('bird')

        # Spawn dogs (mostly pets)
        for _ in range(random.randint(2, self.max_animals['dogs'])):
            self.spawn_animal('dog', is_pet=True)

        # Spawn cats
        for _ in range(random.randint(3, self.max_animals['cats'])):
            self.spawn_animal('cat')

        # Spawn deer near forests
        for _ in range(random.randint(2, self.max_animals['deer'])):
            self.spawn_animal('deer')

        # Spawn rats in urban areas
        for _ in range(random.randint(5, self.max_animals['rats'])):
            self.spawn_animal('rat')

        # Spawn raccoons
        for _ in range(random.randint(1, self.max_animals['raccoons'])):
            self.spawn_animal('raccoon')

        # Spawn fish in schools
        self.spawn_fish_schools(3)  # 3 schools of fish

        # Spawn birds of prey
        for _ in range(random.randint(1, self.max_animals['birds_of_prey'])):
            self.spawn_animal('bird_of_prey')

    def spawn_animal(self, animal_type: str, **kwargs) -> Optional[Animal]:
        """
        Spawn a single animal.

        Args:
            animal_type: Type of animal to spawn
            **kwargs: Additional parameters for animal creation

        Returns:
            Animal: The spawned animal, or None if failed
        """
        # Determine spawn position based on zones
        x, y = self._get_spawn_position(animal_type)

        # Create the animal
        variant = random.randint(0, 5)  # Random color variant

        animal = None
        if animal_type == 'bird':
            animal = Bird(x, y, variant)
        elif animal_type == 'bird_of_prey':
            animal = BirdOfPrey(x, y, variant)
        elif animal_type == 'dog':
            is_pet = kwargs.get('is_pet', False)
            animal = Dog(x, y, variant, is_pet)
            # If pet, assign to NPC (would need NPC reference)
        elif animal_type == 'cat':
            animal = Cat(x, y, variant)
        elif animal_type == 'deer':
            animal = Deer(x, y, variant)
        elif animal_type == 'rat':
            animal = Rat(x, y, variant)
        elif animal_type == 'raccoon':
            animal = Raccoon(x, y, variant)
        elif animal_type == 'fish':
            animal = Fish(x, y, variant)

        if animal:
            self.animals.append(animal)
            self.stats['total_spawned'] += 1
            return animal

        return None

    def spawn_fish_schools(self, num_schools: int):
        """
        Spawn schools of fish in water zones.

        Args:
            num_schools: Number of schools to spawn
        """
        for _ in range(num_schools):
            school: List[Fish] = []
            school_size = random.randint(5, 10)

            # Choose a water zone
            if self.spawn_zones['water']:
                zone = random.choice(self.spawn_zones['water'])
                center_x = zone['x']
                center_y = zone['y']
            else:
                # Random water location
                center_x = random.randint(100, self.world_width - 100)
                center_y = random.randint(100, self.world_height - 100)

            # Spawn fish near each other
            for i in range(school_size):
                offset_x = random.uniform(-30, 30)
                offset_y = random.uniform(-30, 30)
                fish = Fish(center_x + offset_x, center_y + offset_y, variant=i % 5)
                fish.school = school
                school.append(fish)
                self.animals.append(fish)

            self.fish_schools.append(school)
            self.stats['total_spawned'] += school_size

    def _get_spawn_position(self, animal_type: str) -> Tuple[float, float]:
        """
        Get appropriate spawn position for animal type.

        Args:
            animal_type: Type of animal

        Returns:
            Tuple: (x, y) spawn position
        """
        # Check if we have specific zones for this type
        zone_map = {
            'fish': 'water',
            'deer': 'forest',
            'rat': 'urban',
        }

        zone_type = zone_map.get(animal_type)
        if zone_type and self.spawn_zones[zone_type]:
            # Spawn in appropriate zone
            zone = random.choice(self.spawn_zones[zone_type])
            # Random position within zone radius
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, zone['radius'])
            x = zone['x'] + math.cos(angle) * distance
            y = zone['y'] + math.sin(angle) * distance
            return (x, y)

        # Default: random position in world
        x = random.uniform(100, self.world_width - 100)
        y = random.uniform(100, self.world_height - 100)
        return (x, y)

    def update(self, dt: float, npcs: List = None, robots: List = None):
        """
        Update all animals.

        Args:
            dt: Delta time in seconds
            npcs: List of NPCs for interaction checks
            robots: List of robots for threat detection
        """
        # Update each animal
        for animal in self.animals[:]:  # Copy list to allow removal
            if not animal.alive:
                self.animals.remove(animal)
                continue

            # Check for threats (NPCs, robots)
            threats = []
            if npcs:
                threats.extend(npcs)
            if robots:
                threats.extend(robots)

            # Wild animals flee from threats
            if not isinstance(animal, Dog) or not animal.is_pet:
                animal.check_threat_proximity(threats)

            # Update animal
            animal.update(dt)

            # Boundary checking
            if animal.x < 0 or animal.x > self.world_width or \
               animal.y < 0 or animal.y > self.world_height:
                # Bounce back or wrap around
                if animal.x < 0:
                    animal.x = 0
                    animal.velocity_x = abs(animal.velocity_x)
                elif animal.x > self.world_width:
                    animal.x = self.world_width
                    animal.velocity_x = -abs(animal.velocity_x)

                if animal.y < 0:
                    animal.y = 0
                    animal.velocity_y = abs(animal.velocity_y)
                elif animal.y > self.world_height:
                    animal.y = self.world_height
                    animal.velocity_y = -abs(animal.velocity_y)

        # Process animal-animal interactions
        self._process_interactions(dt)

        # Update cooldowns
        for key in list(self.interaction_cooldowns.keys()):
            self.interaction_cooldowns[key] -= dt
            if self.interaction_cooldowns[key] <= 0:
                del self.interaction_cooldowns[key]

    def _process_interactions(self, dt: float):
        """Process animal-to-animal interactions."""
        # Check pairs of animals for interactions
        for i, animal1 in enumerate(self.animals):
            for animal2 in self.animals[i+1:]:
                # Calculate distance
                dx = animal2.x - animal1.x
                dy = animal2.y - animal1.y
                distance = math.sqrt(dx*dx + dy*dy)

                # Check interaction range (30 pixels)
                if distance < 30:
                    self._handle_interaction(animal1, animal2)

    def _handle_interaction(self, animal1: Animal, animal2: Animal):
        """
        Handle interaction between two animals.

        Args:
            animal1: First animal
            animal2: Second animal
        """
        # Check cooldown
        pair_id = (id(animal1), id(animal2))
        if pair_id in self.interaction_cooldowns:
            return

        # Set cooldown
        self.interaction_cooldowns[pair_id] = 2.0

        # Dog chases cat
        if isinstance(animal1, Dog) and isinstance(animal2, Cat):
            if random.random() < 0.5:  # 50% chance
                animal1.chase(animal2.x, animal2.y)
                animal2.flee_from(animal1.x, animal1.y)
                self.stats['interactions'] += 1

        elif isinstance(animal1, Cat) and isinstance(animal2, Dog):
            if random.random() < 0.5:
                animal2.chase(animal1.x, animal1.y)
                animal1.flee_from(animal2.x, animal2.y)
                self.stats['interactions'] += 1

        # Cat chases bird
        elif isinstance(animal1, Cat) and isinstance(animal2, Bird):
            if random.random() < 0.4:
                animal1.chase(animal2.x, animal2.y)
                animal2.flee_from(animal1.x, animal1.y)
                self.stats['interactions'] += 1

        elif isinstance(animal1, Bird) and isinstance(animal2, Cat):
            if random.random() < 0.4:
                animal2.chase(animal1.x, animal1.y)
                animal1.flee_from(animal2.x, animal2.y)
                self.stats['interactions'] += 1

        # Cat chases rat
        elif isinstance(animal1, Cat) and isinstance(animal2, Rat):
            if random.random() < 0.6:
                animal1.chase(animal2.x, animal2.y)
                animal2.flee_from(animal1.x, animal1.y)
                self.stats['interactions'] += 1

        elif isinstance(animal1, Rat) and isinstance(animal2, Cat):
            if random.random() < 0.6:
                animal2.chase(animal1.x, animal1.y)
                animal1.flee_from(animal2.x, animal2.y)
                self.stats['interactions'] += 1

        # Bird of prey catches fish
        elif isinstance(animal1, BirdOfPrey) and isinstance(animal2, Fish):
            if random.random() < 0.3:
                animal1.chase(animal2.x, animal2.y)
                animal2.flee_from(animal1.x, animal1.y)
                self.stats['interactions'] += 1

        elif isinstance(animal1, Fish) and isinstance(animal2, BirdOfPrey):
            if random.random() < 0.3:
                animal2.chase(animal1.x, animal1.y)
                animal1.flee_from(animal2.x, animal2.y)
                self.stats['interactions'] += 1

    def assign_dog_to_npc(self, dog: Dog, npc):
        """
        Assign a pet dog to an NPC.

        Args:
            dog: The dog to assign
            npc: The NPC owner
        """
        dog.is_pet = True
        dog.owner = npc

    def get_animals_in_radius(self, x: float, y: float, radius: float) -> List[Animal]:
        """
        Get all animals within radius of a point.

        Args:
            x: Center X coordinate
            y: Center Y coordinate
            radius: Search radius

        Returns:
            List[Animal]: Animals within radius
        """
        nearby = []
        radius_sq = radius * radius

        for animal in self.animals:
            dx = animal.x - x
            dy = animal.y - y
            dist_sq = dx*dx + dy*dy

            if dist_sq < radius_sq:
                nearby.append(animal)

        return nearby

    def get_statistics(self) -> Dict:
        """Get animal manager statistics."""
        counts = {
            'birds': 0,
            'dogs': 0,
            'cats': 0,
            'deer': 0,
            'rats': 0,
            'raccoons': 0,
            'fish': 0,
            'birds_of_prey': 0,
        }

        for animal in self.animals:
            if isinstance(animal, BirdOfPrey):
                counts['birds_of_prey'] += 1
            elif isinstance(animal, Bird):
                counts['birds'] += 1
            elif isinstance(animal, Dog):
                counts['dogs'] += 1
            elif isinstance(animal, Cat):
                counts['cats'] += 1
            elif isinstance(animal, Deer):
                counts['deer'] += 1
            elif isinstance(animal, Rat):
                counts['rats'] += 1
            elif isinstance(animal, Raccoon):
                counts['raccoons'] += 1
            elif isinstance(animal, Fish):
                counts['fish'] += 1

        return {
            'total_animals': len(self.animals),
            'fish_schools': len(self.fish_schools),
            'type_counts': counts,
            'total_spawned': self.stats['total_spawned'],
            'interactions': self.stats['interactions'],
        }


# Global animal manager instance
_animal_manager = None


def get_animal_manager(world_width: int = 2000, world_height: int = 2000) -> AnimalManager:
    """
    Get the global animal manager instance.

    Args:
        world_width: Width of the world
        world_height: Height of the world

    Returns:
        AnimalManager: The global instance
    """
    global _animal_manager
    if _animal_manager is None:
        _animal_manager = AnimalManager(world_width, world_height)
    return _animal_manager
