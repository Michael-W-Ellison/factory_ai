# Recycling Factory - Technical Design Document

**Version:** 1.0
**Last Updated:** 2025-11-13

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Core Systems Architecture](#core-systems-architecture)
3. [Data Structures](#data-structures)
4. [Algorithms](#algorithms)
5. [File Organization](#file-organization)
6. [Module Specifications](#module-specifications)
7. [Performance Considerations](#performance-considerations)
8. [Save/Load System](#saveload-system)
9. [Testing Strategy](#testing-strategy)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Game Loop                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Input   │→ │  Update  │→ │  Render  │→ │  Display │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Game Systems                           │
├─────────────────┬─────────────────┬────────────────────────┤
│  World Manager  │  Entity Manager │   Resource Manager     │
│                 │                 │                         │
│ • Map/Grid      │ • Robots        │ • Materials            │
│ • City          │ • NPCs          │ • Components           │
│ • Factory       │ • Buildings     │ • Power                │
│ • Landfill      │ • Objects       │ • Money                │
└─────────────────┴─────────────────┴────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Gameplay Systems                         │
├──────────────┬──────────────┬──────────────┬──────────────┤
│  Collection  │  Processing  │  Detection   │   Research   │
│   System     │    System    │    System    │    System    │
└──────────────┴──────────────┴──────────────┴──────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                             │
├──────────────────────┬──────────────────────────────────────┤
│   Game State         │         Configuration                │
│   • Current game     │         • Settings                   │
│   • Save data        │         • Balancing values           │
└──────────────────────┴──────────────────────────────────────┘
```

### Design Pattern: Entity-Component System (Simplified)

We'll use a simplified Entity-Component System (ECS) pattern:
- **Entities:** Objects in the game (robots, buildings, NPCs, materials)
- **Components:** Data that defines entity properties (position, stats, inventory)
- **Systems:** Logic that operates on entities with specific components

This makes the code modular and easier to extend.

---

## Core Systems Architecture

### 1. Game Engine Core

```python
class Game:
    """Main game controller"""
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.game_speed = 1.0

        # System managers
        self.world = WorldManager()
        self.entities = EntityManager()
        self.resources = ResourceManager()
        self.ui = UIManager()
        self.input = InputHandler()

    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds

            self.handle_input()
            self.update(dt)
            self.render()

    def handle_input(self):
        """Process user input"""
        events = pygame.event.get()
        self.input.process(events)

    def update(self, dt):
        """Update all game systems"""
        if not self.paused:
            adjusted_dt = dt * self.game_speed

            self.world.update(adjusted_dt)
            self.entities.update(adjusted_dt)
            self.resources.update(adjusted_dt)

    def render(self):
        """Render game to screen"""
        self.world.render()
        self.entities.render()
        self.ui.render()
```

### 2. World Manager

```python
class WorldManager:
    """Manages the game world (map, grid, zones)"""
    def __init__(self, width, height, tile_size=32):
        self.width = width
        self.height = height
        self.tile_size = tile_size

        # Grid-based world representation
        self.grid = Grid(width // tile_size, height // tile_size)

        # World regions
        self.landfill = Landfill(...)
        self.city = City(...)
        self.factory = Factory(...)

        # Time system
        self.time = GameTime()

    def update(self, dt):
        self.time.update(dt)
        self.landfill.update(dt)
        self.city.update(dt)
        self.factory.update(dt)
```

### 3. Entity Manager

```python
class EntityManager:
    """Manages all entities (robots, NPCs, buildings, objects)"""
    def __init__(self):
        self.entities = {}  # id -> Entity
        self.next_id = 0

        # Entity type groups for efficient iteration
        self.robots = []
        self.npcs = []
        self.buildings = []
        self.objects = []

    def create_entity(self, entity_type, **kwargs):
        """Factory method to create entities"""
        entity_id = self.next_id
        self.next_id += 1

        if entity_type == "robot":
            entity = Robot(entity_id, **kwargs)
            self.robots.append(entity)
        elif entity_type == "npc":
            entity = NPC(entity_id, **kwargs)
            self.npcs.append(entity)
        # ... etc

        self.entities[entity_id] = entity
        return entity

    def update(self, dt):
        """Update all entities"""
        for robot in self.robots:
            robot.update(dt)
        for npc in self.npcs:
            npc.update(dt)
        # ... etc
```

### 4. Resource Manager

```python
class ResourceManager:
    """Manages materials, components, money, power"""
    def __init__(self):
        self.materials = {}  # material_type -> quantity
        self.components = {}  # component_type -> quantity
        self.money = 10000  # Starting money

        self.power = PowerSystem()

    def add_material(self, material_type, quantity):
        """Add material to inventory"""
        if material_type not in self.materials:
            self.materials[material_type] = 0
        self.materials[material_type] += quantity

    def process_material(self, material_type, quantity):
        """Convert material to components"""
        if self.can_process(material_type, quantity):
            # Consume material
            self.materials[material_type] -= quantity

            # Generate components based on material type
            components = get_components_from_material(material_type, quantity)
            for comp_type, comp_qty in components.items():
                self.add_component(comp_type, comp_qty)
```

---

## Data Structures

### Core Entity Classes

#### Robot

```python
class Robot:
    """Autonomous robot collector"""
    def __init__(self, robot_id, x, y):
        # Identity
        self.id = robot_id

        # Position & Movement
        self.x = x
        self.y = y
        self.target_x = None
        self.target_y = None
        self.path = []  # List of waypoints

        # Stats
        self.speed = 2.0  # tiles per second
        self.collection_capacity = 100  # kg
        self.power_capacity = 1000  # units
        self.processing_speed = 1.0  # multiplier

        # Current state
        self.current_power = self.power_capacity
        self.inventory = {}  # material_type -> quantity
        self.state = RobotState.IDLE

        # Assignment
        self.assigned_zone = None
        self.current_task = None

    def update(self, dt):
        """Update robot behavior"""
        if self.state == RobotState.TRAVELING:
            self.move_along_path(dt)
        elif self.state == RobotState.COLLECTING:
            self.collect_material(dt)
        elif self.state == RobotState.RETURNING:
            self.return_to_factory(dt)

        self.consume_power(dt)

    def move_along_path(self, dt):
        """Move toward next waypoint"""
        if not self.path:
            self.state = RobotState.IDLE
            return

        next_waypoint = self.path[0]
        # Calculate movement vector
        # Update position
        # If reached waypoint, remove from path
```

#### NPC (Non-Player Character)

```python
class NPC:
    """City inhabitant"""
    def __init__(self, npc_id, x, y):
        self.id = npc_id
        self.x = x
        self.y = y

        # Daily routine
        self.schedule = DailySchedule()
        self.home_location = (x, y)
        self.work_location = None

        # Detection
        self.vision_range = 100  # pixels
        self.hearing_range = 150

        # State
        self.current_activity = NPCActivity.SLEEPING
        self.alert_level = 0  # 0-100

    def update(self, dt, current_time):
        """Update NPC behavior based on schedule"""
        activity = self.schedule.get_activity(current_time)

        if activity != self.current_activity:
            self.transition_to(activity)

        # Check for robot detection
        self.check_for_suspicious_activity()
```

#### Building

```python
class Building:
    """Generic building (house, factory, store, etc.)"""
    def __init__(self, building_id, x, y, building_type):
        self.id = building_id
        self.x = x
        self.y = y
        self.width = 64
        self.height = 64
        self.type = building_type

        # State
        self.occupied = True
        self.construction_state = ConstructionState.COMPLETE
        self.condition = 100  # 0-100, affects value

        # Materials
        self.material_composition = self._calculate_materials()

    def _calculate_materials(self):
        """Determine what materials this building contains"""
        # Based on building type and size
        materials = {}

        if self.type == BuildingType.HOUSE:
            materials['wood'] = random.randint(500, 1000)
            materials['metal'] = random.randint(200, 400)
            materials['glass'] = random.randint(50, 150)
            materials['concrete'] = random.randint(1000, 2000)
            # etc.

        return materials
```

#### Collection Zone

```python
class CollectionZone:
    """Player-defined area for robot collection"""
    def __init__(self, zone_id, points):
        self.id = zone_id
        self.polygon = points  # List of (x, y) tuples
        self.priority = 1

        # Time restrictions
        self.allowed_hours = range(0, 24)  # All hours by default

        # Assigned robots
        self.assigned_robots = []

        # Zone type
        self.zone_type = ZoneType.LANDFILL  # or CITY

    def is_active(self, current_hour):
        """Check if zone is active at this time"""
        return current_hour in self.allowed_hours

    def contains_point(self, x, y):
        """Check if point is inside zone polygon"""
        # Ray casting algorithm for point-in-polygon test
        return point_in_polygon((x, y), self.polygon)
```

### Enumerations

```python
from enum import Enum, auto

class RobotState(Enum):
    IDLE = auto()
    TRAVELING = auto()
    COLLECTING = auto()
    RETURNING = auto()
    CHARGING = auto()
    UPGRADING = auto()
    BROKEN = auto()

class MaterialType(Enum):
    PLASTIC = auto()
    GLASS = auto()
    METAL = auto()
    PRECIOUS_METAL = auto()
    RUBBER = auto()
    BIO_SLOP = auto()
    WOOD = auto()
    LIQUID = auto()
    TOXIC = auto()
    ELECTRONIC = auto()
    CONCRETE = auto()
    WIRE = auto()

class BuildingType(Enum):
    HOUSE = auto()
    STORE = auto()
    FACTORY = auto()
    WAREHOUSE = auto()
    POLICE_STATION = auto()

class SuspicionLevel(Enum):
    NONE = 0
    RUMORS = 20
    INVESTIGATION = 40
    INSPECTION = 60
    RESTRICTED = 80
    FEDERAL = 100
```

### Configuration Data

```python
# config/materials.py
MATERIAL_CONFIG = {
    MaterialType.PLASTIC: {
        'value_per_kg': 0.5,
        'processing_time': 2.0,  # seconds
        'power_cost': 1.0,
        'components': {
            'recycled_plastic': 0.8,  # 80% yield
        }
    },
    MaterialType.METAL: {
        'value_per_kg': 2.0,
        'processing_time': 5.0,
        'power_cost': 3.0,
        'components': {
            'scrap_metal': 0.9,
            'precious_metal': 0.01,  # 1% contains precious metals
        }
    },
    # ... etc for all materials
}

# config/research.py
RESEARCH_TREE = {
    'speed_1': {
        'name': 'Speed Enhancement I',
        'cost': 1000,
        'time': 60,  # seconds
        'prerequisites': [],
        'effects': {
            'robot_speed': 1.2  # 20% increase
        }
    },
    'speed_2': {
        'name': 'Speed Enhancement II',
        'cost': 2500,
        'time': 120,
        'prerequisites': ['speed_1'],
        'effects': {
            'robot_speed': 1.5  # 50% total increase
        }
    },
    # ... etc
}
```

---

## Algorithms

### 1. Pathfinding - A* Algorithm

```python
def find_path(start, goal, grid, avoid_detection=False):
    """
    A* pathfinding algorithm

    Args:
        start: (x, y) tuple
        goal: (x, y) tuple
        grid: Grid object with obstacle information
        avoid_detection: If True, prefer paths with lower detection risk

    Returns:
        List of (x, y) waypoints, or None if no path exists
    """
    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(current, grid):
            # Calculate movement cost
            tentative_g = g_score[current] + distance(current, neighbor)

            # Add detection penalty if avoiding detection
            if avoid_detection:
                detection_risk = grid.get_detection_risk(neighbor)
                tentative_g += detection_risk * 10

            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None  # No path found

def heuristic(a, b):
    """Manhattan distance heuristic"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
```

### 2. Detection System

```python
def check_detection(robot, npcs, cameras, city):
    """
    Check if robot is detected by NPCs or cameras

    Returns:
        (detected, evidence_quality, witness_type)
    """
    robot_pos = (robot.x, robot.y)

    # Check NPC line of sight
    for npc in npcs:
        if npc.can_see(robot_pos, city.time):
            # Calculate evidence quality based on conditions
            quality = calculate_evidence_quality(
                robot_pos,
                npc.pos,
                city.time.get_lighting(),
                robot.stealth_level
            )
            return (True, quality, 'citizen')

    # Check camera coverage
    for camera in cameras:
        if not camera.disabled and camera.can_see(robot_pos):
            quality = 1.0  # Cameras always get good evidence
            return (True, quality, 'camera')

    return (False, 0, None)

def calculate_evidence_quality(robot_pos, observer_pos, lighting, stealth):
    """
    Calculate quality of evidence (0.0 to 1.0)

    Factors:
    - Distance: Closer = better evidence
    - Lighting: More light = better evidence
    - Stealth level: Higher stealth = worse evidence
    """
    distance = euclidean_distance(robot_pos, observer_pos)

    # Distance factor (0.0 to 1.0, decreases with distance)
    distance_factor = max(0, 1.0 - (distance / 300))

    # Lighting factor (0.0 to 1.0)
    lighting_factor = lighting.get_brightness_at(robot_pos)

    # Stealth factor (reduces evidence quality)
    stealth_factor = 1.0 - (stealth * 0.1)  # Each stealth level reduces by 10%

    quality = distance_factor * lighting_factor * stealth_factor

    return max(0.0, min(1.0, quality))
```

### 3. Suspicion System

```python
class SuspicionManager:
    """Manages suspicion level and consequences"""
    def __init__(self):
        self.suspicion = 0  # 0-100
        self.decay_rate = 0.1  # Per minute of game time
        self.inspection_scheduled = False
        self.inspection_time = None

    def add_suspicion(self, evidence_quality, witness_type):
        """Add suspicion based on detection event"""
        base_amount = 0

        if witness_type == 'citizen':
            base_amount = 5
        elif witness_type == 'police':
            base_amount = 15
        elif witness_type == 'camera':
            base_amount = 10

        # Multiply by evidence quality
        amount = base_amount * evidence_quality

        self.suspicion = min(100, self.suspicion + amount)

        # Check for threshold events
        self.check_thresholds()

    def update(self, dt):
        """Update suspicion (decay over time)"""
        if self.suspicion > 0:
            decay = self.decay_rate * dt
            self.suspicion = max(0, self.suspicion - decay)

    def check_thresholds(self):
        """Check if suspicion crossed important thresholds"""
        if self.suspicion >= 60 and not self.inspection_scheduled:
            self.schedule_inspection()
        elif self.suspicion >= 80:
            self.activate_restrictions()
```

### 4. NPC Daily Routine

```python
class DailySchedule:
    """NPC daily schedule"""
    def __init__(self, npc_type):
        self.schedule = self._generate_schedule(npc_type)

    def _generate_schedule(self, npc_type):
        """Generate realistic daily schedule"""
        if npc_type == NPCType.WORKING_ADULT:
            return {
                (0, 6): NPCActivity.SLEEPING,
                (6, 7): NPCActivity.HOME_ROUTINE,
                (7, 8): NPCActivity.COMMUTING,
                (8, 17): NPCActivity.WORKING,
                (17, 18): NPCActivity.COMMUTING,
                (18, 19): NPCActivity.SHOPPING,
                (19, 22): NPCActivity.HOME_ROUTINE,
                (22, 24): NPCActivity.SLEEPING,
            }
        # Other NPC types...

    def get_activity(self, game_time):
        """Get current activity based on time"""
        hour = game_time.hour

        for (start, end), activity in self.schedule.items():
            if start <= hour < end:
                return activity

        return NPCActivity.SLEEPING
```

### 5. Grid-based Spatial Partitioning

```python
class Grid:
    """
    Grid system for efficient spatial queries
    Divides world into cells to quickly find nearby entities
    """
    def __init__(self, width, height, cell_size=64):
        self.cell_size = cell_size
        self.cols = width // cell_size
        self.rows = height // cell_size

        # Each cell contains list of entity IDs
        self.cells = [[[] for _ in range(self.cols)] for _ in range(self.rows)]

    def add_entity(self, entity):
        """Add entity to appropriate grid cell"""
        cell_x, cell_y = self.world_to_grid(entity.x, entity.y)
        if self.is_valid_cell(cell_x, cell_y):
            self.cells[cell_y][cell_x].append(entity.id)

    def get_nearby_entities(self, x, y, radius):
        """Get all entities within radius of point"""
        # Calculate which cells to check
        cell_radius = (radius // self.cell_size) + 1
        center_cell_x, center_cell_y = self.world_to_grid(x, y)

        nearby = []
        for dy in range(-cell_radius, cell_radius + 1):
            for dx in range(-cell_radius, cell_radius + 1):
                cell_x = center_cell_x + dx
                cell_y = center_cell_y + dy

                if self.is_valid_cell(cell_x, cell_y):
                    nearby.extend(self.cells[cell_y][cell_x])

        return nearby
```

---

## File Organization

```
factory_ai/
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── config.py              # Game configuration
│
├── docs/                  # Documentation
│   ├── GAME_DESIGN_DOCUMENT.md
│   ├── TECHNICAL_DESIGN_DOCUMENT.md
│   └── DEVELOPMENT_ROADMAP.md
│
├── src/                   # Source code
│   ├── __init__.py
│   │
│   ├── core/              # Core game engine
│   │   ├── __init__.py
│   │   ├── game.py        # Main game class
│   │   ├── game_time.py   # Time management
│   │   └── constants.py   # Game constants
│   │
│   ├── entities/          # Game entities
│   │   ├── __init__.py
│   │   ├── entity.py      # Base entity class
│   │   ├── robot.py       # Robot implementation
│   │   ├── npc.py         # NPC implementation
│   │   ├── building.py    # Building implementation
│   │   └── object.py      # Collectible object
│   │
│   ├── systems/           # Game systems
│   │   ├── __init__.py
│   │   ├── entity_manager.py
│   │   ├── resource_manager.py
│   │   ├── collection_system.py
│   │   ├── processing_system.py
│   │   ├── detection_system.py
│   │   ├── suspicion_system.py
│   │   ├── research_system.py
│   │   └── power_system.py
│   │
│   ├── world/             # World management
│   │   ├── __init__.py
│   │   ├── world_manager.py
│   │   ├── grid.py        # Spatial grid
│   │   ├── landfill.py    # Landfill generation
│   │   ├── city.py        # City generation
│   │   └── factory.py     # Factory management
│   │
│   ├── ai/                # AI behaviors
│   │   ├── __init__.py
│   │   ├── pathfinding.py # A* pathfinding
│   │   ├── robot_ai.py    # Robot behavior
│   │   └── npc_ai.py      # NPC behavior
│   │
│   ├── ui/                # User interface
│   │   ├── __init__.py
│   │   ├── ui_manager.py
│   │   ├── hud.py         # Heads-up display
│   │   ├── panels.py      # UI panels
│   │   └── notifications.py
│   │
│   ├── rendering/         # Rendering system
│   │   ├── __init__.py
│   │   ├── renderer.py    # Main renderer
│   │   ├── camera.py      # Camera controls
│   │   └── sprites.py     # Sprite management
│   │
│   └── utils/             # Utility functions
│       ├── __init__.py
│       ├── math_utils.py  # Math helpers
│       ├── geometry.py    # Geometric calculations
│       └── save_load.py   # Save/load system
│
├── data/                  # Game data
│   ├── config/            # Configuration files
│   │   ├── materials.json
│   │   ├── research.json
│   │   ├── buildings.json
│   │   └── settings.json
│   │
│   ├── saves/             # Save files
│   │
│   └── assets/            # Game assets
│       ├── sprites/       # Sprite images
│       ├── ui/            # UI graphics
│       └── sounds/        # Sound effects (future)
│
└── tests/                 # Unit tests
    ├── __init__.py
    ├── test_pathfinding.py
    ├── test_detection.py
    └── test_resource_manager.py
```

---

## Module Specifications

### Core Game Loop (src/core/game.py)

**Purpose:** Main game controller and loop

**Key Methods:**
- `__init__()`: Initialize all systems
- `run()`: Main game loop
- `handle_input()`: Process user input
- `update(dt)`: Update all systems
- `render()`: Render game state

**Dependencies:**
- pygame for window management and rendering
- All manager classes

### Entity Manager (src/systems/entity_manager.py)

**Purpose:** Centralized entity creation and management

**Key Methods:**
- `create_entity(type, **kwargs)`: Factory method for entities
- `get_entity(id)`: Retrieve entity by ID
- `delete_entity(id)`: Remove entity
- `update(dt)`: Update all entities
- `get_entities_of_type(type)`: Get all entities of specific type

**Data Structures:**
- Dictionary of all entities (ID -> Entity)
- Lists for each entity type (for efficient iteration)

### Resource Manager (src/systems/resource_manager.py)

**Purpose:** Track and manage all resources (materials, money, power)

**Key Methods:**
- `add_material(type, quantity)`
- `remove_material(type, quantity)`
- `process_material(type, quantity)`: Convert to components
- `sell_components()`: Sell to warehouse
- `add_money(amount)`
- `spend_money(amount)`
- `get_power_status()`: Current power generation/consumption

### Pathfinding System (src/ai/pathfinding.py)

**Purpose:** Calculate paths for entities

**Key Methods:**
- `find_path(start, goal, grid, options)`: A* pathfinding
- `smooth_path(path)`: Remove unnecessary waypoints
- `is_path_clear(start, end, grid)`: Quick line-of-sight check

**Algorithm:** A* with configurable heuristics

### Detection System (src/systems/detection_system.py)

**Purpose:** Handle visibility and detection mechanics

**Key Methods:**
- `check_detection(robot)`: See if robot detected
- `calculate_evidence_quality(...)`: Determine evidence quality
- `process_detection_event(...)`: Handle detection consequences

**Integration:**
- Works with SuspicionSystem
- Queries NPCs and cameras
- Considers lighting and line-of-sight

---

## Performance Considerations

### Optimization Strategies

#### 1. Spatial Partitioning
- Use grid-based spatial partitioning for entity queries
- Only check nearby entities for collisions/detection
- Cell size should be tuned to typical entity interaction range

#### 2. Update Frequency
- Update nearby entities every frame
- Update distant entities less frequently (every 5-10 frames)
- NPCs far from player/robots can use simplified AI

#### 3. Rendering Optimization
- Only render entities within camera view (frustum culling)
- Use sprite batching to reduce draw calls
- Cache rendered text and UI elements

#### 4. Pathfinding Optimization
- Cache paths and reuse if still valid
- Use hierarchical pathfinding for long distances
- Limit pathfinding calculations per frame (async if needed)

#### 5. Memory Management
- Pool frequently created/destroyed objects (projectiles, particles)
- Limit number of active entities
- Clear destroyed entities from memory promptly

### Performance Targets

For smooth gameplay:
- **Frame Rate:** 60 FPS minimum
- **Entity Limit:** 1000+ active entities
- **Pathfinding:** < 16ms for typical path (60 FPS = 16ms per frame)
- **Memory:** < 500MB for typical game session

---

## Save/Load System

### Save File Format (JSON)

```json
{
    "version": "1.0",
    "timestamp": "2025-11-13T12:34:56",
    "game_time": {
        "day": 15,
        "hour": 14,
        "minute": 30
    },
    "resources": {
        "money": 45000,
        "power_stored": 500,
        "materials": {
            "plastic": 1200,
            "metal": 800
        },
        "components": {
            "recycled_plastic": 5000,
            "scrap_metal": 3000
        }
    },
    "factory": {
        "buildings": [
            {
                "type": "processing_facility",
                "level": 2,
                "x": 100,
                "y": 100
            }
        ],
        "upgrades": ["speed_1", "capacity_2"]
    },
    "robots": [
        {
            "id": 0,
            "x": 150,
            "y": 200,
            "stats": {
                "speed": 3.5,
                "capacity": 150,
                "power": 1200
            },
            "current_power": 800,
            "inventory": {"plastic": 50}
        }
    ],
    "world": {
        "landfill_objects": [...],
        "city_state": {...}
    },
    "suspicion": {
        "level": 25,
        "inspection_scheduled": false
    },
    "research": {
        "completed": ["speed_1", "capacity_1"],
        "in_progress": {
            "tech": "hacking_1",
            "time_remaining": 45
        }
    },
    "settings": {
        "difficulty": "normal",
        "game_speed": 1.0
    }
}
```

### Save/Load Implementation

```python
class SaveLoadSystem:
    """Handle saving and loading game state"""

    @staticmethod
    def save_game(game, filename):
        """Save current game state to file"""
        save_data = {
            'version': '1.0',
            'timestamp': datetime.now().isoformat(),
            'game_time': game.world.time.to_dict(),
            'resources': game.resources.to_dict(),
            'factory': game.world.factory.to_dict(),
            'robots': [robot.to_dict() for robot in game.entities.robots],
            'world': game.world.to_dict(),
            'suspicion': game.suspicion.to_dict(),
            'research': game.research.to_dict(),
            'settings': game.settings.to_dict(),
        }

        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)

    @staticmethod
    def load_game(filename):
        """Load game state from file"""
        with open(filename, 'r') as f:
            save_data = json.load(f)

        # Verify version compatibility
        if save_data['version'] != '1.0':
            raise ValueError("Incompatible save file version")

        # Create new game instance
        game = Game()

        # Restore state
        game.world.time.from_dict(save_data['game_time'])
        game.resources.from_dict(save_data['resources'])
        # ... etc for all systems

        return game
```

---

## Testing Strategy

### Unit Tests

Test individual components in isolation:

```python
# tests/test_pathfinding.py
def test_straight_line_path():
    """Test pathfinding on clear straight path"""
    grid = Grid(100, 100)
    path = find_path((0, 0), (10, 0), grid)
    assert len(path) == 11  # 11 tiles including start and end

def test_obstacle_avoidance():
    """Test pathfinding around obstacle"""
    grid = Grid(100, 100)
    grid.add_obstacle(5, 0)  # Block direct path
    path = find_path((0, 0), (10, 0), grid)
    assert path is not None
    assert (5, 0) not in path  # Path should avoid obstacle
```

### Integration Tests

Test system interactions:

```python
# tests/test_collection_system.py
def test_robot_collection_workflow():
    """Test complete robot collection workflow"""
    game = Game()
    robot = game.entities.create_entity('robot', x=0, y=0)
    zone = CollectionZone(0, [(10, 10), (20, 10), (20, 20), (10, 20)])

    # Add object to zone
    obj = game.entities.create_entity('object', x=15, y=15, material='plastic', quantity=50)

    # Assign robot to zone
    robot.assigned_zone = zone

    # Simulate until robot collects object
    while robot.inventory.get('plastic', 0) < 50:
        game.update(0.016)  # ~60 FPS

    assert robot.inventory['plastic'] == 50
    assert obj not in game.entities.objects
```

### Manual Testing Checklist

- [ ] Robot pathfinding works correctly
- [ ] Collection zones function properly
- [ ] Factory processing produces correct components
- [ ] Research unlocks apply correctly
- [ ] Detection system triggers at appropriate times
- [ ] Suspicion increases/decreases as expected
- [ ] Save/Load preserves game state
- [ ] UI responds to all inputs
- [ ] Performance stable with many entities

---

**End of Technical Design Document**
