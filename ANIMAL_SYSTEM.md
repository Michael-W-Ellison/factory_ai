# Animal System Documentation

## Overview

The Animal System adds living wildlife and pets to the Factory AI simulation, bringing the world to life with realistic animal behaviors and interactions. Animals include birds, dogs, cats, deer, rats, raccoons, fish, and birds of prey, each with unique AI behaviors.

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Animal Types](#animal-types)
4. [Behaviors](#behaviors)
5. [Interactions](#interactions)
6. [API Reference](#api-reference)
7. [Integration Guide](#integration-guide)
8. [Examples](#examples)

---

## Features

### Core Features

- **8 Animal Types**: Birds, dogs, cats, deer, rats, raccoons, fish, and birds of prey
- **8-Way Directional Sprites**: All animals have smooth directional movement
- **Color Variants**: Multiple color/breed variants for each species
- **AI Behaviors**: Idle, wander, flee, chase, eat, sleep, and follow
- **Animal Interactions**: Dogs chase cats, cats chase birds/rats, birds of prey hunt fish
- **NPC Interactions**: Animals flee from NPCs/robots, pets follow owners
- **Fish Schooling**: Fish swim together in coordinated schools
- **Habitat-Based Spawning**: Animals spawn in appropriate locations

### Visual Features

- **Procedural Sprites**: All animals generated programmatically
- **Smooth Animation**: Walking, flying, and swimming animations
- **Shadow Effects**: Dynamic shadows based on animal type
- **Behavioral Indicators**: Visual cues for chase/flee states

---

## Architecture

### Component Structure

```
src/
├── entities/
│   └── animal.py           # Animal entity classes
├── systems/
│   └── animal_manager.py   # Spawning and lifecycle management
└── graphics/
    ├── sprite_generator.py # Animal sprite generation
    └── animation_controller.py  # Animal animations
```

### Class Hierarchy

```
Animal (Base Class)
├── Bird
├── BirdOfPrey
├── Dog
├── Cat
├── Deer
├── Rat
├── Raccoon
└── Fish
```

---

## Animal Types

### 1. Bird (Small Birds)

**Species**: Pigeon, sparrow, blue jay, cardinal, goldfinch, crow

**Characteristics**:
- Speed: 3.0
- Vision range: 120 pixels
- Flee distance: 100 pixels
- Can fly (ignores ground obstacles)

**Variants**:
- 0: Pigeon (gray)
- 1: Sparrow (brown)
- 2: Blue jay (blue)
- 3: Cardinal (red)
- 4: Goldfinch (yellow)
- 5: Crow (black)

**Behaviors**:
- Wanders freely
- Flees from cats and NPCs
- Gentle wing flapping animation

**Code Example**:
```python
from entities.animal import Bird

# Spawn a blue jay
bird = Bird(x=100, y=100, variant=2)
```

---

### 2. Bird of Prey (Hawks, Eagles)

**Species**: Brown hawk, bald eagle, gray falcon

**Characteristics**:
- Speed: 4.0
- Vision range: 200 pixels (excellent vision)
- Flee distance: 50 pixels (brave)
- Hunts fish and small animals

**Variants**:
- 0: Brown hawk
- 1: Bald eagle (white head)
- 2: Gray falcon

**Behaviors**:
- Soars in wide circles
- Hunts fish from rivers/lakes
- Slower wing flapping (soaring)

**Code Example**:
```python
from entities.animal import BirdOfPrey

# Spawn a bald eagle
eagle = BirdOfPrey(x=500, y=200, variant=1)
```

---

### 3. Dog

**Breeds**: Brown, golden, black, white, brown-tan, gray

**Characteristics**:
- Speed: 2.5
- Vision range: 150 pixels
- Flee distance: 60 pixels (braver than other animals)
- Can be pet or stray

**Variants**:
- 0: Brown
- 1: Golden retriever
- 2: Black
- 3: White
- 4: Brown-tan
- 5: Gray

**Behaviors**:
- **Pet dogs**: Follow their NPC owner
- **Stray dogs**: Wander freely
- Chase cats that get too close
- Loyal and protective

**Code Example**:
```python
from entities.animal import Dog

# Spawn a pet golden retriever
dog = Dog(x=300, y=400, variant=1, is_pet=True)

# Assign to NPC
animal_manager.assign_dog_to_npc(dog, npc_owner)
```

---

### 4. Cat

**Colors**: Orange tabby, gray, black, white, brown, tan

**Characteristics**:
- Speed: 3.0 (quick and agile)
- Vision range: 100 pixels
- Flee distance: 70 pixels
- Hunts birds and rats

**Variants**:
- 0: Orange tabby
- 1: Gray
- 2: Black
- 3: White
- 4: Brown
- 5: Tan

**Behaviors**:
- Independent wandering
- Hunts small animals (birds, rats)
- Flees from dogs
- Tail sway animation

**Code Example**:
```python
from entities.animal import Cat

# Spawn a black cat
cat = Cat(x=200, y=300, variant=2)
```

---

### 5. Deer

**Types**: Brown, reddish-brown, tan

**Characteristics**:
- Speed: 3.5 (fast when fleeing)
- Vision range: 150 pixels
- Flee distance: 120 pixels (very timid)
- Grazes on grass

**Variants**:
- 0: Brown (male with antlers)
- 1: Reddish-brown (female, no antlers)
- 2: Tan (male with antlers)

**Behaviors**:
- Emerges from forest edges
- Grazes in clearings
- Flees at first sign of danger
- Males have antlers

**Code Example**:
```python
from entities.animal import Deer

# Spawn a buck (male with antlers)
buck = Deer(x=1200, y=300, variant=0)
```

---

### 6. Rat

**Colors**: Gray, dark gray, brown

**Characteristics**:
- Speed: 2.0
- Vision range: 60 pixels (poor vision)
- Flee distance: 80 pixels (very skittish)
- Small and quick

**Variants**:
- 0: Gray
- 1: Dark gray
- 2: Brown

**Behaviors**:
- Short, scurrying movements
- Hides frequently
- Flees from cats and NPCs
- Red eyes glow

**Code Example**:
```python
from entities.animal import Rat

# Spawn a gray rat
rat = Rat(x=250, y=350, variant=0)
```

---

### 7. Raccoon

**Characteristics**:
- Speed: 2.0
- Vision range: 100 pixels
- Flee distance: 90 pixels
- Distinctive black mask

**Features**:
- Gray body with black/light striped tail
- Black mask around eyes
- Nocturnal (more active at night)
- Curious scavenger

**Behaviors**:
- Investigates objects
- Ringed tail animation
- Flees when startled

**Code Example**:
```python
from entities.animal import Raccoon

# Spawn a raccoon
raccoon = Raccoon(x=400, y=600)
```

---

### 8. Fish

**Species**: Goldfish, blue fish, silver, yellow, green bass

**Characteristics**:
- Speed: 1.5
- Vision range: 80 pixels
- Flee distance: 100 pixels
- Must stay in water

**Variants**:
- 0: Goldfish (orange)
- 1: Blue fish
- 2: Silver
- 3: Yellow
- 4: Green bass

**Behaviors**:
- Swims in schools
- Tail wagging animation
- Flees from birds of prey
- Stays in water zones

**Code Example**:
```python
from entities.animal import Fish

# Spawn a school of fish
school = []
for i in range(10):
    fish = Fish(x=200 + i*5, y=700, variant=i % 5)
    fish.school = school
    school.append(fish)
```

---

## Behaviors

### Behavior States

All animals use the `AnimalBehavior` enum:

```python
class AnimalBehavior(Enum):
    IDLE = "idle"       # Standing still
    WANDER = "wander"   # Random movement
    FLEE = "flee"       # Running from threat
    CHASE = "chase"     # Pursuing target
    EAT = "eat"         # Eating/grazing
    SLEEP = "sleep"     # Sleeping
    FOLLOW = "follow"   # Following owner (pets)
```

### Behavior Transitions

Animals automatically transition between behaviors based on:
- **Timers**: Each behavior has a duration
- **Proximity**: Detecting threats or prey nearby
- **State**: Pet status, hunger, etc.

### AI Decision Making

**Default Behavior Cycle**:
1. Animal chooses random behavior (wander 70%, idle 30%)
2. Executes behavior for random duration (2-5 seconds)
3. Checks for threats/interactions
4. Repeats

**Threat Detection**:
- Animals continuously scan for threats within `flee_distance`
- When threat detected, immediately switch to FLEE behavior
- Flee direction is opposite of threat position

**Hunting/Chasing**:
- Predators (cats, birds of prey) scan for prey
- When prey nearby, switch to CHASE behavior
- Chase until caught or prey escapes

---

## Interactions

### Animal-Animal Interactions

The system supports the following predator-prey and social interactions:

#### Dog ↔ Cat
- **Behavior**: Dogs chase cats (50% chance on proximity)
- **Result**: Dog enters CHASE state, cat enters FLEE state
- **Duration**: 2-4 seconds

#### Cat → Bird
- **Behavior**: Cats hunt small birds (40% chance)
- **Result**: Cat chases, bird flees
- **Note**: Represents natural hunting behavior

#### Cat → Rat
- **Behavior**: Cats hunt rats (60% chance - higher than birds)
- **Result**: Cat chases, rat flees rapidly

#### Bird of Prey → Fish
- **Behavior**: Hawks/eagles hunt fish (30% chance)
- **Result**: Bird dives toward water, fish flees deeper
- **Special**: Only happens near water zones

#### Fish Schooling
- **Behavior**: Fish swim together in coordinated groups
- **Mechanism**: Each fish calculates school center and moves toward it
- **Result**: Realistic schooling behavior

### NPC-Animal Interactions

#### Wild Animals Flee
- All wild animals (non-pets) flee from NPCs and robots
- Flee distance varies by species (50-120 pixels)
- Deer are most timid, rats and birds moderate, raccoons least timid

#### Pet Dogs Follow
- Pet dogs assigned to NPCs follow their owner
- Maintain distance of 20-50 pixels
- Match owner's movement speed when far

#### Feeding Birds (Planned)
- NPCs in parks can feed birds
- Birds gather around feeding NPCs
- Behavior: IDLE with periodic pecking animation

---

## API Reference

### Animal Class

Base class for all animals.

```python
class Animal:
    def __init__(self, x: float, y: float, sprite_type: SpriteType, variant: int = 0)
```

**Methods**:

```python
def update(self, dt: float)
"""Update animal state and behavior."""

def flee_from(self, threat_x: float, threat_y: float)
"""Start fleeing from a threat."""

def chase(self, target_x: float, target_y: float)
"""Start chasing a target."""

def check_threat_proximity(self, entities: List) -> bool
"""Check if any threatening entities are nearby."""

def get_position(self) -> Tuple[float, float]
"""Get animal position."""

def get_sprite_params(self) -> dict
"""Get parameters for sprite rendering."""
```

---

### AnimalManager Class

Manages all animals in the simulation.

```python
class AnimalManager:
    def __init__(self, world_width: int = 2000, world_height: int = 2000)
```

**Methods**:

```python
def add_spawn_zone(self, zone_type: str, x: int, y: int, radius: int)
"""Add a spawn zone for certain animal types."""
# zone_type: 'water', 'forest', 'urban', 'park'

def spawn_initial_animals(self)
"""Spawn initial animal population."""

def spawn_animal(self, animal_type: str, **kwargs) -> Optional[Animal]
"""Spawn a single animal."""
# animal_type: 'bird', 'dog', 'cat', 'deer', 'rat', 'raccoon', 'fish', 'bird_of_prey'

def spawn_fish_schools(self, num_schools: int)
"""Spawn schools of fish in water zones."""

def update(self, dt: float, npcs: List = None, robots: List = None)
"""Update all animals."""

def assign_dog_to_npc(self, dog: Dog, npc)
"""Assign a pet dog to an NPC."""

def get_animals_in_radius(self, x: float, y: float, radius: float) -> List[Animal]
"""Get all animals within radius of a point."""

def get_statistics(self) -> Dict
"""Get animal manager statistics."""
```

---

### Animation Controllers

#### AnimalAnimationController

Base animation controller for land animals.

```python
class AnimalAnimationController(AnimationController):
    def update_for_behavior(self, behavior: str, dt: float) -> int
```

**Behavior Mapping**:
- `idle`, `eating` → IDLE animation (frame 0)
- `walking`, `wander` → WALK animation (frames 0, 1, 0, 2)
- `running`, `fleeing`, `chasing` → RUN animation (fast walk)

#### BirdAnimationController

Animation controller for flying animals.

```python
class BirdAnimationController(AnimalAnimationController):
    # Animations:
    # IDLE: [0, 1, 2] - gentle flapping
    # WALK: [0, 1, 2] - faster flapping
```

#### FishAnimationController

Animation controller for swimming animals.

```python
class FishAnimationController(AnimalAnimationController):
    # Animations:
    # IDLE: [0, 1, 2] - slow tail wag
    # WALK: [0, 1, 2] - fast tail wag
```

---

## Integration Guide

### Basic Setup

```python
from systems.animal_manager import get_animal_manager

# Initialize animal manager
animal_mgr = get_animal_manager(world_width=2000, world_height=2000)

# Define spawn zones
animal_mgr.add_spawn_zone('water', x=500, y=1500, radius=200)
animal_mgr.add_spawn_zone('forest', x=1700, y=300, radius=150)
animal_mgr.add_spawn_zone('park', x=1000, y=1000, radius=300)
animal_mgr.add_spawn_zone('urban', x=300, y=300, radius=250)

# Spawn initial population
animal_mgr.spawn_initial_animals()
```

### Game Loop Integration

```python
# In your game loop
def update(dt):
    # Update animal manager
    animal_mgr.update(dt, npcs=npc_list, robots=robot_list)

    # Render animals
    for animal in animal_mgr.animals:
        params = animal.get_sprite_params()
        sprite = sprite_generator.get_sprite(**params)
        screen.blit(sprite, (animal.x - camera_x, animal.y - camera_y))
```

### Spawning Custom Animals

```python
# Spawn specific animal type
bird = animal_mgr.spawn_animal('bird', variant=2)  # Blue jay

# Spawn pet dog for NPC
dog = animal_mgr.spawn_animal('dog', is_pet=True)
animal_mgr.assign_dog_to_npc(dog, npc)

# Spawn fish school
animal_mgr.spawn_fish_schools(num_schools=5)

# Spawn deer near forest
deer = Deer(x=1700, y=320, variant=0)
animal_mgr.animals.append(deer)
```

### Querying Animals

```python
# Get animals near a point
nearby_animals = animal_mgr.get_animals_in_radius(x=500, y=500, radius=100)

# Get statistics
stats = animal_mgr.get_statistics()
print(f"Total animals: {stats['total_animals']}")
print(f"Birds: {stats['type_counts']['birds']}")
print(f"Interactions: {stats['interactions']}")
```

---

## Examples

### Example 1: NPC Walking Dog in Park

```python
# Create NPC
npc = NPC(x=700, y=450)

# Create pet dog
dog = Dog(x=720, y=450, variant=1, is_pet=True)  # Golden retriever
animal_mgr.animals.append(dog)
animal_mgr.assign_dog_to_npc(dog, npc)

# Dog will now follow NPC automatically
# In update loop, dog maintains 20-50 pixel distance from owner
```

### Example 2: Deer Grazing Near Forest

```python
# Spawn deer near forest edge
for i in range(4):
    variant = i % 2  # Alternating male/female
    deer = Deer(
        x=1700 + random.uniform(-50, 50),
        y=300 + random.uniform(-50, 50),
        variant=variant
    )
    animal_mgr.animals.append(deer)

# Deer will:
# - Graze (EAT behavior) 40% of the time
# - Wander slowly
# - Flee if NPC approaches within 120 pixels
```

### Example 3: Fish School in River

```python
# Define river zone
animal_mgr.add_spawn_zone('water', x=200, y=700, radius=150)

# Spawn school of 10 fish
school = []
for i in range(10):
    fish = Fish(
        x=200 + random.uniform(-30, 30),
        y=700 + random.uniform(-30, 30),
        variant=i % 5  # Mix of colors
    )
    fish.school = school
    school.append(fish)
    animal_mgr.animals.append(fish)

animal_mgr.fish_schools.append(school)

# Fish will swim together, maintaining school cohesion
```

### Example 4: Cat Hunting in Alley

```python
# Spawn cat in urban area
cat = Cat(x=300, y=300, variant=0)  # Orange tabby
animal_mgr.animals.append(cat)

# Spawn some birds nearby
for _ in range(5):
    bird = Bird(
        x=300 + random.uniform(-100, 100),
        y=300 + random.uniform(-100, 100),
        variant=random.randint(0, 5)
    )
    animal_mgr.animals.append(bird)

# When cat gets within 30 pixels of a bird:
# - 40% chance cat chases bird
# - Bird flees
# - Interaction logged in statistics
```

### Example 5: Bird of Prey Hunting Fish

```python
# Spawn eagle above river
eagle = BirdOfPrey(x=200, y=600, variant=1)  # Bald eagle
animal_mgr.animals.append(eagle)

# Eagle will:
# - Soar in wide circles
# - Detect fish within 200 pixel vision range
# - Dive to hunt (CHASE behavior) when fish spotted
# - Fish flee to deeper water
```

---

## Performance Considerations

### Population Limits

Default maximum populations:
- Birds: 20
- Dogs: 5
- Cats: 8
- Deer: 6
- Rats: 10
- Raccoons: 4
- Fish: 30
- Birds of Prey: 3

**Total: ~86 animals**

### Optimization Tips

1. **Spatial Partitioning**:
   - Use quadtree or grid for proximity checks
   - Only check interactions for nearby animals

2. **Update Culling**:
   - Don't update animals far from camera
   - Reduce update frequency for distant animals

3. **Interaction Cooldowns**:
   - System includes 2-second cooldown between interactions
   - Prevents spamming chase/flee behaviors

4. **Sprite Caching**:
   - All sprites cached after first generation
   - ~200 cached sprites for full animal population

---

## Testing

### Running the Demo

```bash
python test_animal_system.py
```

**Demo Features**:
- Visualizes all 8 animal types
- Shows spawn zones (water, forest, park, urban)
- Displays real-time statistics
- Demonstrates interactions
- Camera controls for exploration

**Controls**:
- Arrow keys: Move camera
- Space: Spawn random animal at center
- ESC: Exit

### Expected Behaviors

When running the demo, you should observe:

1. **Birds** flying around, flapping wings
2. **Deer** grazing near forest, fleeing when NPCs approach
3. **Fish** swimming in schools in the water zone
4. **Cats** chasing birds and rats
5. **Dogs** following NPCs (if assigned)
6. **Rats** scurrying in short bursts
7. **Raccoons** wandering with distinctive ringed tails
8. **Birds of prey** soaring and diving for fish

---

## Troubleshooting

### Animals Not Moving

**Problem**: Animals spawn but don't move
**Solution**: Check that `update()` is called with valid `dt` parameter

```python
# Correct
animal_mgr.update(dt=0.016)  # 60 FPS

# Incorrect
animal_mgr.update(dt=0)  # No movement
```

### Animals Escaping World Bounds

**Problem**: Animals move off-screen and don't return
**Solution**: Boundary checking is built-in, but ensure world dimensions are set correctly

```python
# Set correct world size
animal_mgr = get_animal_manager(world_width=2000, world_height=2000)
```

### No Interactions Occurring

**Problem**: Animals don't chase/flee
**Solution**: Check that interaction distance is sufficient

```python
# Interactions occur within 30 pixels
# Ensure animals can get close enough:
# 1. Spawn animals near each other
# 2. Check flee_distance and vision_range values
# 3. Verify NPCs/robots passed to update()

animal_mgr.update(dt, npcs=npc_list)  # Don't forget NPCs!
```

### Fish Not Schooling

**Problem**: Fish swim independently
**Solution**: Ensure fish are added to the same school

```python
# Correct - assign school reference
school = []
for i in range(10):
    fish = Fish(x=200, y=700, variant=i % 5)
    fish.school = school  # IMPORTANT
    school.append(fish)

# Incorrect - no school reference
for i in range(10):
    fish = Fish(x=200, y=700, variant=i % 5)
    # fish.school not set - will swim solo
```

---

## Future Enhancements

Potential additions to the animal system:

1. **Sounds**: Animal sound effects (barking, chirping, etc.)
2. **Feeding System**: NPCs can feed animals
3. **Breeding**: Animals reproduce over time
4. **Health System**: Animals can get sick or injured
5. **Weather Reactions**: Animals seek shelter in rain
6. **Day/Night Cycle**: Nocturnal animals (raccoons) more active at night
7. **Predation**: Successful hunts remove prey
8. **Nests/Dens**: Animals have home locations
9. **Footprints**: Leave tracks on certain surfaces
10. **Seasonal Behavior**: Migration, hibernation

---

## License

This animal system is part of the Factory AI simulation project.

---

## Credits

**Procedural Sprite Generation**: All animal sprites generated programmatically
**AI Behaviors**: Finite state machine with random transitions
**Schooling Algorithm**: Boids-inspired flocking for fish

---

**Last Updated**: 2025-11-15
**Version**: 1.0.0
**Author**: Factory AI Development Team
