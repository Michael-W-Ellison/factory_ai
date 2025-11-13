# Comprehensive Development Todo List
# Recycling Factory Game - Complete Implementation

**Status:** Phases 1-4 Complete, Phase 7 (partial) | Current Phase: 5 (Material Processing & Components)
**Last Updated:** 2025-11-13

---

## COMPLETED ✓

### Phase 0: Learning & Setup ✓
- [x] Python 3.10+ installed
- [x] Pygame installed
- [x] Project structure created
- [x] Git initialized

### Phase 1: Core Foundation ✓
- [x] Main game loop
- [x] Window management
- [x] Input handling
- [x] Grid system (100x75 tiles)
- [x] Camera controls (WASD)
- [x] Coordinate transformations

### Phase 2: Basic Gameplay Loop ✓
- [x] Entity base class
- [x] Robot entity with manual movement
- [x] CollectibleObject (8 material types)
- [x] Collision detection (AABB)
- [x] Collection mechanic
- [x] ResourceManager
- [x] Simple HUD

### Phase 3: Robot & Collection Systems ✓
- [x] A* pathfinding algorithm
- [x] Robot state machine (6 states)
- [x] Autonomous robot behavior
- [x] Factory deposit/unload system
- [x] Multiple robots (autonomous + manual)
- [x] Pathfinding integration

### Phase 4: Building System ✓
- [x] Building base class with properties, power tracking, and queues
- [x] BuildingType enum with all 32 building types
- [x] BuildingManager for placement, tracking, and updates
- [x] Factory building (5x5, starting building, upgradeable)
- [x] PowerManager with generation, consumption, brownout/blackout handling
- [x] LandfillGasExtraction (starting power source, degrades over time)
- [x] ConstructionSite entity with progress tracking and robot assignment
- [x] ConstructionManager with queue system and robot building behavior
- [x] Processing buildings: PaperRecycler, PlasticRecycler, MetalRefinery, Glassworks, RubberRecycler
- [x] ProcessingBuilding base class with quality tiers and efficiency
- [x] Storage buildings: Warehouse (4x4, 50,000kg), Silo (3x3, 100,000kg single material)
- [x] Power buildings: SolarArray (time-dependent), MethaneGenerator (fuel-based), BatteryBank (storage)
- [x] Advanced processing: BioWasteTreatment, ToxicIncinerator, CoalOven, CrudeOilRefinery, LandfillGasPlant
- [x] Manufacturing buildings: CircuitBoardFab, MotorAssembly, BatteryFab
- [x] Integration with EntityManager, Grid, ResourceManager, HUD
- [x] Comprehensive test suite (test_construction_system.py, test_power_system.py, test_processing_buildings.py, test_storage_power_buildings.py, test_phase4_integration.py)

### Phase 7: City & World (Partial) ✓
- [x] 7.3: Vehicles in City (spawning, working vs scrap)
- [x] 7.4: Fences and Walls (chain link, wooden, brick)
- [x] 7.5: NPC System (daily schedules, vision, detection)
- [x] 7.6: Detection System (line-of-sight, accumulation, UI)
- [x] 7.7: Police System (patrols, behaviors, suspicion integration)
- [x] 7.8: Suspicion System (tiers, decay, UI meter)
- [x] Directional rendering and animations for NPCs, Police, Vehicles
- [x] Environmental buildings (Fire House, Library, City Hall, Courthouse, School, Bus Terminal, Train Station, Warehouse, Dock)
- [x] Environmental props (Benches, Light Poles, Trash Cans, Bicycles)
- [x] Marketplace system (material sales, delivery vehicles, pricing)

**Note:** Phase 7 sections 7.11-7.14 are documented below but not yet implemented. These cover:
- Geographic features (rivers, ocean, bridges)
- Vehicle traffic system (proper lane usage, movement)
- Bus transportation system (routes, NPCs using buses)
- Environmental content integration (city generator updates)

---

## PHASE 4: BUILDING SYSTEM ✓ (COMPLETED - See above)

### 4.1 Building Base System
- [ ] Create Building base class (src/entities/building.py)
  - [ ] Position, size, rotation properties
  - [ ] Power consumption/generation tracking
  - [ ] Active/inactive state
  - [ ] Construction progress (0-100%)
  - [ ] Level/upgrade tracking
  - [ ] Input/output material queues
  - [ ] Render method with construction animation
  - [ ] Update method for processing

- [ ] Create BuildingType enum in constants.py
  - [ ] Add all 32 building types from buildings.json
  - [ ] FACTORY, SOLAR_ARRAY, PAPER_RECYCLER, etc.

- [ ] Create BuildingManager (src/systems/building_manager.py)
  - [ ] Dictionary of all buildings by ID
  - [ ] Grid occupancy tracking
  - [ ] Place building method (check valid placement)
  - [ ] Remove building method
  - [ ] Get buildings at position
  - [ ] Get buildings by type
  - [ ] Update all buildings
  - [ ] Render all buildings
  - [ ] Calculate total power generation
  - [ ] Calculate total power consumption

### 4.2 Factory Building (Starting Building)
- [ ] Create Factory class extends Building
  - [ ] 5x5 tile footprint
  - [ ] Starting building (level 1)
  - [ ] Basic material storage (10,000kg capacity)
  - [ ] Basic processing capability (very slow)
  - [ ] Robot command center functionality
  - [ ] Upgrade levels 1-5
  - [ ] Each level increases storage and processing

- [ ] Factory rendering
  - [ ] Different visual for each level
  - [ ] Show power status indicator
  - [ ] Show storage fill level
  - [ ] Highlight when selected

- [ ] Factory starting state
  - [ ] Place at world center on game start
  - [ ] Set as robot return point
  - [ ] Initialize with level 1 stats

### 4.3 Power System Foundation
- [ ] Create PowerManager (src/systems/power_manager.py)
  - [ ] Track total generation capacity
  - [ ] Track total consumption
  - [ ] Track current power level
  - [ ] Track max storage capacity
  - [ ] Power distribution logic
  - [ ] Brownout handling (>100% usage)
  - [ ] Blackout handling (0 power)
  - [ ] Building priority system

- [ ] Landfill Gas Extraction (starting power)
  - [ ] Create LandfillGasExtraction class
  - [ ] 2x2 footprint
  - [ ] Generates 10 power
  - [ ] Produces dirty methane (5 units/sec)
  - [ ] Degrades over time as landfill depletes
  - [ ] Place at game start near landfill

- [ ] Power consumption effects
  - [ ] Buildings turn off when insufficient power
  - [ ] Robots charge slower with low power
  - [ ] Processing stops without power
  - [ ] Visual indicators for unpowered buildings

### 4.4 Construction System
- [ ] Create ConstructionSite entity
  - [ ] Placeholder visual during construction
  - [ ] Construction progress bar
  - [ ] Shows required materials
  - [ ] Shows required robots
  - [ ] Timer for construction duration

- [ ] Construction queue system
  - [ ] Player can queue multiple buildings
  - [ ] Show queue in UI
  - [ ] Cancel construction option
  - [ ] Refund materials on cancel

- [ ] Robot building behavior
  - [ ] New state: BUILDING
  - [ ] Pathfind to construction site
  - [ ] Stay at site until construction complete
  - [ ] Multiple robots speed up construction
  - [ ] Animation while building

- [ ] Construction UI
  - [ ] Building menu (B key)
  - [ ] Category tabs (Power, Processing, Storage, etc.)
  - [ ] Building cards with stats
  - [ ] Show costs (money + materials)
  - [ ] Show power usage/generation
  - [ ] Preview placement on hover
  - [ ] Valid/invalid placement indicator
  - [ ] Confirm placement on click

### 4.5 Material Processing Buildings
- [ ] Paper Recycler
  - [ ] Create PaperRecycler class
  - [ ] 3x3 footprint, costs $5000
  - [ ] Power consumption: 3 units
  - [ ] Processing speed: 3 seconds per kg
  - [ ] Input: paper/cardboard (raw)
  - [ ] Outputs: waste (50%), low quality (30%), medium quality (15%), high quality (5%)
  - [ ] Upgrade path: levels 1-3 (speed + quality)

- [ ] Plastic Recycler
  - [ ] Create PlasticRecycler class
  - [ ] 4x4 footprint, costs $8000
  - [ ] Power consumption: 4 units
  - [ ] Processing: 4 seconds per kg
  - [ ] Outputs: waste, low/med/high quality plastic
  - [ ] Requires research: Advanced Plastics for high quality

- [ ] Metal Refinery
  - [ ] Create MetalRefinery class
  - [ ] 5x5 footprint, costs $15000
  - [ ] Power consumption: 6 units
  - [ ] Processing: 5-6 seconds per kg (varies by metal type)
  - [ ] Handles: iron, steel, copper, poor slag
  - [ ] Outputs: refined metals (90% efficiency base)
  - [ ] High heat requirement

- [ ] Glassworks
  - [ ] Create Glassworks class
  - [ ] 4x4 footprint, costs $10000
  - [ ] Power consumption: 5 units
  - [ ] Processing: 4 seconds per kg
  - [ ] Outputs: gray glass blanks, colored glass (with dyes)
  - [ ] Can produce bullet-proof glass with research

- [ ] Rubber Recycler
  - [ ] Create RubberRecycler class
  - [ ] 3x3 footprint, costs $7000
  - [ ] Outputs: waste, low/med/high quality rubber
  - [ ] Similar to plastic recycler

### 4.6 Storage Buildings
- [ ] Basic Warehouse
  - [ ] Create Warehouse class
  - [ ] 4x4 footprint, costs $3000
  - [ ] Capacity: 50,000kg
  - [ ] Can store any material type
  - [ ] Organized by material type
  - [ ] Shows fill level
  - [ ] Upgradeable to 100,000kg

- [ ] Silo (bulk storage)
  - [ ] Create Silo class
  - [ ] 3x3 footprint, costs $5000
  - [ ] Capacity: 100,000kg (single material)
  - [ ] Faster loading/unloading
  - [ ] Shows stored material type

### 4.7 Power Buildings
- [ ] Solar Array
  - [ ] Create SolarArray class
  - [ ] 3x3 footprint, costs $2000
  - [ ] Generates 15 power (daytime only)
  - [ ] Requires research: Solar Array I
  - [ ] Upgradeable to levels 2-3
  - [ ] Time-dependent generation (more at noon)

- [ ] Methane Generator
  - [ ] Create MethaneGenerator class
  - [ ] 4x4 footprint, costs $6000
  - [ ] Generates 25 power
  - [ ] Consumes pure methane (2 units/sec)
  - [ ] Always on if fuel available
  - [ ] Pollution: 1.0

- [ ] Battery Bank
  - [ ] Create BatteryBank class
  - [ ] 2x2 footprint, costs $4000
  - [ ] Stores 1000 power units
  - [ ] Charges when excess power
  - [ ] Discharges when deficit
  - [ ] Upgradeable capacity

### 4.8 Integration with Game Systems
- [ ] Update EntityManager to handle buildings
  - [ ] Add buildings list
  - [ ] Create/destroy building methods
  - [ ] Update buildings each frame
  - [ ] Render buildings

- [ ] Update Grid to track building occupancy
  - [ ] Mark tiles occupied by buildings
  - [ ] Check if tiles available for placement
  - [ ] Update pathfinding to avoid buildings

- [ ] Update ResourceManager for building costs
  - [ ] Deduct money for construction
  - [ ] Check if sufficient funds
  - [ ] Deduct required materials

- [ ] Update HUD to show power info
  - [ ] Power generation vs consumption
  - [ ] Power storage level
  - [ ] Battery charge indicator
  - [ ] Warning when power insufficient

### 4.9 Testing Phase 4
- [ ] Test building placement
- [ ] Test construction queue
- [ ] Test robot building behavior
- [ ] Test power system (generation/consumption)
- [ ] Test material processing
- [ ] Test storage capacity
- [ ] Performance test with many buildings
- [ ] Save/load building states

---

## PHASE 5: MATERIAL PROCESSING & COMPONENTS

### 5.1 Expanded Material System
- [ ] Update materials.json with all 15 material types
  - [ ] Organic, Paper, Plastic, Metal, Glass
  - [ ] Hazardous, Wood, Concrete, Steel, Iron
  - [ ] Copper, Textiles, Rubber, Petroleum, Toxic Waste

- [ ] Create Component system
  - [ ] Components are processed outputs
  - [ ] 50+ component types (from JSON)
  - [ ] Each component has quality levels
  - [ ] Components used for upgrades/research

- [ ] Material quality tiers
  - [ ] Waste (10% value)
  - [ ] Low quality (50% value)
  - [ ] Medium quality (100% value)
  - [ ] High quality (200% value)
  - [ ] Ultra quality (500% value - requires advanced research)

### 5.2 Advanced Processing Buildings
- [ ] Bio-Waste Treatment Plant
  - [ ] Processes organic materials
  - [ ] Produces bio-slop (fertilizer)
  - [ ] Produces methane
  - [ ] Reduces pollution

- [ ] Toxic Incinerator
  - [ ] REQUIRED for hazardous/toxic waste
  - [ ] Costs money to run (-$5/kg)
  - [ ] High power consumption (6 units)
  - [ ] Produces ash (sellable)
  - [ ] Reduces toxic waste safely

- [ ] Coal Oven
  - [ ] Processes wood into charcoal
  - [ ] Produces tar as byproduct
  - [ ] Used for fuel or sale

- [ ] Crude Oil Refinery
  - [ ] Processes petroleum
  - [ ] Outputs: refined oil, bitumen
  - [ ] High value products
  - [ ] Requires petroleum source

- [ ] Landfill Gas Plant
  - [ ] Converts bio-slop to methane
  - [ ] Produces dirty methane
  - [ ] Can produce pure/ultra-pure with upgrades
  - [ ] Fuel for generators

### 5.3 Manufacturing Buildings
- [ ] Circuit Board Fabricator
  - [ ] Uses copper + plastic
  - [ ] Produces circuit boards
  - [ ] Used for robot upgrades
  - [ ] Requires cleanroom (research)

- [ ] Motor Assembly
  - [ ] Uses iron + copper + magnets
  - [ ] Produces electric motors
  - [ ] Used for robot construction
  - [ ] Improves robot speed

- [ ] Battery Fabrication
  - [ ] Uses lithium + chemicals
  - [ ] Produces battery cells
  - [ ] Used for power storage
  - [ ] Used for robot upgrades

### 5.4 Processing Queue System
- [ ] Material input queue
  - [ ] Each building has input queue
  - [ ] Capacity based on building size
  - [ ] Robots deliver materials to queue
  - [ ] Auto-pull from warehouse option

- [ ] Processing logic
  - [ ] Process one batch at a time
  - [ ] Processing time based on material + building
  - [ ] Quality randomization (weighted by building level)
  - [ ] Output to output queue

- [ ] Output queue
  - [ ] Stores processed materials
  - [ ] Limited capacity
  - [ ] Processing stops if output full
  - [ ] Robots transport to warehouse

- [ ] UI for processing
  - [ ] Click building to see queues
  - [ ] Input queue status
  - [ ] Current processing item + progress
  - [ ] Output queue status
  - [ ] Efficiency stats

### 5.5 Automation Features
- [ ] Auto-delivery system
  - [ ] Toggle per building
  - [ ] Robots auto-deliver from warehouse
  - [ ] Robots auto-collect outputs
  - [ ] Priority system

- [ ] Material routing
  - [ ] Set preferred buildings for materials
  - [ ] Route plastics to plastic recycler
  - [ ] Route metals to refinery
  - [ ] Manual override option

### 5.6 Testing Phase 5
- [ ] Test all processing buildings
- [ ] Test material quality output
- [ ] Test queue system
- [ ] Test automation
- [ ] Test component production
- [ ] Balance processing times
- [ ] Balance costs and outputs

---

## PHASE 6: RESEARCH SYSTEM

### 6.1 Research Infrastructure
- [ ] Create ResearchManager (src/systems/research_manager.py)
  - [ ] Load research tree from research.json (130+ techs)
  - [ ] Track completed research
  - [ ] Track in-progress research
  - [ ] Check prerequisites
  - [ ] Apply research effects
  - [ ] Save/load research state

- [ ] Research data structure
  - [ ] ID, name, description
  - [ ] Cost (money)
  - [ ] Time (in-game hours)
  - [ ] Prerequisites (list of tech IDs)
  - [ ] Effects (dictionary of modifiers)
  - [ ] Category (robot, processing, stealth, etc.)

### 6.2 Research UI
- [ ] Research menu (R key)
  - [ ] Tech tree visualization
  - [ ] Categories: Robot, Processing, Power, Stealth, Advanced
  - [ ] Node for each technology
  - [ ] Lines showing prerequisites
  - [ ] Color coding: available, locked, completed, in-progress
  - [ ] Click to view details

- [ ] Research details panel
  - [ ] Full description
  - [ ] Cost and time
  - [ ] Prerequisites (grayed if not met)
  - [ ] Effects preview
  - [ ] "Start Research" button
  - [ ] "Cancel" button for in-progress

- [ ] Research progress indicator
  - [ ] Small icon in HUD
  - [ ] Shows current research
  - [ ] Progress bar
  - [ ] Time remaining

### 6.3 Research Categories

#### Robot Research (25 techs)
- [ ] Speed Enhancement I/II/III
  - [ ] +20%/+40%/+60% robot speed
  - [ ] Cost: $1000/$2500/$5000
  - [ ] Time: 1hr/2hr/4hr

- [ ] Capacity Upgrade I/II/III
  - [ ] +50kg/+100kg/+150kg capacity
  - [ ] From 100kg to 250kg max

- [ ] Power Efficiency I/II/III
  - [ ] -20%/-40%/-60% power consumption

- [ ] Durability I/II/III
  - [ ] Robots last longer, take less damage

- [ ] Advanced Sensors
  - [ ] Robots detect threats earlier
  - [ ] See cameras from farther

- [ ] Stealth Mode
  - [ ] Reduces detection chance by 30%
  - [ ] Requires Advanced Sensors

- [ ] Night Vision
  - [ ] Robots work efficiently at night

- [ ] Autonomous Coordination
  - [ ] Robots share task info
  - [ ] No duplicate targets

#### Processing Research (30 techs)
- [ ] Processing Speed I/II/III (per material type)
  - [ ] -20%/-40%/-60% processing time
  - [ ] Separate tree for each material

- [ ] Quality Enhancement I/II/III (per material type)
  - [ ] Improves output quality distribution
  - [ ] More high-quality outputs

- [ ] Efficiency I/II/III (per material type)
  - [ ] Less waste, more usable output

- [ ] Advanced Plastics
  - [ ] Unlocks high-quality plastic production
  - [ ] Prerequisite for many items

- [ ] Metallurgy I/II/III
  - [ ] Better metal refining
  - [ ] Can process rare metals

- [ ] Chemical Processing
  - [ ] Unlock petroleum refinery
  - [ ] Unlock chemical synthesis

#### Power Research (20 techs)
- [ ] Solar Array I/II/III
  - [ ] Unlocks solar power
  - [ ] Each level: more efficient panels

- [ ] Battery Tech I/II/III
  - [ ] Increases battery capacity
  - [ ] Faster charge/discharge

- [ ] Methane Purification I/II
  - [ ] Pure methane, ultra-pure methane
  - [ ] More power per unit

- [ ] Power Distribution I/II
  - [ ] Better power grid efficiency
  - [ ] Less brownouts

- [ ] Generators I/II/III
  - [ ] More efficient generators
  - [ ] Less fuel consumption

#### Stealth Research (25 techs)
- [ ] Camera Hacking I/II/III
  - [ ] Disable cameras temporarily
  - [ ] Level II: disable longer
  - [ ] Level III: disable multiple cameras

- [ ] Police Distraction
  - [ ] Create false leads
  - [ ] Reduces patrols

- [ ] Rumor Suppression
  - [ ] Slower suspicion growth
  - [ ] Better social engineering

- [ ] Inspection Preparation
  - [ ] Warning before inspections
  - [ ] More time to hide illegal materials

- [ ] Legal Material Disguise
  - [ ] Illegal materials appear legal during inspection
  - [ ] High risk if discovered

- [ ] FBI Countermeasures
  - [ ] Delay FBI investigation
  - [ ] Requires deleting hacking research

#### Advanced Research (30 techs)
- [ ] Drones I/II/III
  - [ ] Unlocks drone construction
  - [ ] Scout city areas
  - [ ] Reveal fog of war

- [ ] Wireless Transmitters I/II/III
  - [ ] Extend control range
  - [ ] Level I: 300 tiles, II: 450, III: 600

- [ ] Weather Forecasting
  - [ ] See 3-day weather forecast
  - [ ] Plan operations around weather

- [ ] Market Analysis I/II/III
  - [ ] See price trends
  - [ ] Level II: 3-day forecast
  - [ ] Level III: event predictions

- [ ] Automated Trading
  - [ ] Auto-sell at favorable prices
  - [ ] Set price thresholds

- [ ] Advanced Manufacturing
  - [ ] Unlock specialized components
  - [ ] Circuit boards, motors, sensors

- [ ] Deconstruction I/II/III
  - [ ] Disassemble buildings
  - [ ] Level II: disassemble vehicles
  - [ ] Level III: disassemble houses

### 6.4 Research Effects Application
- [ ] Robot stat modifiers
  - [ ] Update Robot class with research multipliers
  - [ ] Apply speed, capacity, power modifiers
  - [ ] Recalculate on research complete

- [ ] Building modifiers
  - [ ] Update processing speeds
  - [ ] Update efficiency rates
  - [ ] Update power generation/consumption

- [ ] Unlock new buildings
  - [ ] Check research prereqs before allowing construction
  - [ ] Gray out locked buildings in UI

- [ ] Unlock new features
  - [ ] Drones system
  - [ ] Camera hacking
  - [ ] Market forecasting

### 6.5 Testing Phase 6
- [ ] Test research progression
- [ ] Test prerequisites
- [ ] Test effect application
- [ ] Test UI navigation
- [ ] Balance research costs and times
- [ ] Test save/load research state

---

## PHASE 7: CITY & DETECTION SYSTEM

### 7.1 City Generation
- [ ] Create CityGenerator (src/world/city_generator.py)
  - [ ] Generate grid-based city layout
  - [ ] Place roads (grid pattern)
  - [ ] Place residential zones
  - [ ] Place commercial zones
  - [ ] Place industrial zones
  - [ ] Place police station
  - [ ] Place parks/public areas

- [ ] Building placement algorithm
  - [ ] 10x10 city blocks
  - [ ] Roads every 10 tiles
  - [ ] Mix of building types
  - [ ] Density varies by zone
  - [ ] Leave some empty lots

### 7.2 City Buildings
- [ ] House (Livable)
  - [ ] Create House class
  - [ ] 3x4 footprint
  - [ ] Contains: wood (40%), concrete (20%), steel (10%), etc.
  - [ ] Deconstruction time: 120 seconds
  - [ ] Noise level: 8/10
  - [ ] STATUS: ILLEGAL to deconstruct
  - [ ] Occupied by 1-4 NPCs

- [ ] House (Decrepit)
  - [ ] Same class, different state
  - [ ] Worn down, abandoned
  - [ ] Less valuable materials
  - [ ] 44% unusable junk
  - [ ] Deconstruction time: 60 seconds
  - [ ] STATUS: LEGAL to deconstruct
  - [ ] Not occupied

- [ ] Store
  - [ ] Create Store class
  - [ ] 4x4 footprint
  - [ ] Contains merchandise materials
  - [ ] Operating hours: 8am-9pm
  - [ ] Contains 2-5 NPC employees
  - [ ] Customer traffic

- [ ] Office Building
  - [ ] 5x5 footprint
  - [ ] Contains electronics, office supplies
  - [ ] Operating hours: 9am-5pm
  - [ ] Many NPCs during day

- [ ] Factory (City)
  - [ ] Industrial buildings
  - [ ] 6x6 footprint
  - [ ] Operates 24/7
  - [ ] Few NPCs (night shift)

- [ ] Police Station
  - [ ] 5x5 footprint
  - [ ] Spawns police patrols
  - [ ] Cannot be deconstructed
  - [ ] High security area

### 7.3 Vehicles in City
- [ ] Vehicle spawning
  - [ ] Cars on roads
  - [ ] Parked cars near houses/stores
  - [ ] Working vs scrap condition
  - [ ] Random material composition

- [ ] Vehicle class
  - [ ] Create Vehicle entity
  - [ ] Renders as car sprite
  - [ ] Working vehicle: ILLEGAL
  - [ ] Scrap vehicle: LEGAL
  - [ ] Deconstruction times: 45s / 30s
  - [ ] Contains metals, rubber, plastic, petroleum

### 7.4 Fences and Walls
- [ ] Fence system
  - [ ] Chain link fences (iron)
  - [ ] Wooden fences (wood + iron)
  - [ ] Brick walls (concrete/slag)
  - [ ] Around properties
  - [ ] ILLEGAL to remove

- [ ] Fence generation
  - [ ] Place around houses
  - [ ] Place around businesses
  - [ ] Leave gaps for roads
  - [ ] Random fence types

### 7.5 NPC System
- [ ] Create NPC base class (src/entities/npc.py)
  - [ ] Position, movement
  - [ ] Home location
  - [ ] Work location
  - [ ] Current activity
  - [ ] Daily schedule
  - [ ] Vision range (100 tiles)
  - [ ] Vision cone (180 degrees)
  - [ ] Detection state

- [ ] NPC daily schedule
  - [ ] Sleep: 10pm-6am (at home)
  - [ ] Morning routine: 6am-8am (at home)
  - [ ] Commute to work: 8am-9am
  - [ ] Work: 9am-5pm (at workplace)
  - [ ] Commute home: 5pm-6pm
  - [ ] Evening activities: 6pm-8pm (shopping, leisure)
  - [ ] Home routine: 8pm-10pm (at home)

- [ ] NPC pathfinding
  - [ ] Use A* to navigate city
  - [ ] Follow sidewalks/roads
  - [ ] Avoid obstacles
  - [ ] Speed: 30 pixels/second (walking)

- [ ] NPC vision and detection
  - [ ] Raycasting for line-of-sight
  - [ ] Check if robot in vision cone
  - [ ] Detection chance based on:
    - Distance (closer = higher)
    - Lighting (day vs night)
    - Robot stealth level
    - NPC alertness
  - [ ] Detection accumulates over time
  - [ ] Full detection triggers report

### 7.6 Detection System
- [ ] Create DetectionManager (src/systems/detection_manager.py)
  - [ ] Track all NPCs
  - [ ] Check vision cones each frame
  - [ ] Calculate detection chances
  - [ ] Track partial detections
  - [ ] Generate reports

- [ ] Detection levels
  - [ ] 0-25%: Glance (no effect)
  - [ ] 25-50%: Notice (minor suspicion)
  - [ ] 50-75%: Observe (moderate suspicion)
  - [ ] 75-100%: Report (major suspicion increase)

- [ ] Line-of-sight checks
  - [ ] Raycast from NPC to robot
  - [ ] Check for obstacles (buildings, walls)
  - [ ] Check lighting level
  - [ ] Check distance falloff
  - [ ] Apply stealth modifiers

- [ ] Detection UI
  - [ ] Detection meter above detected robots
  - [ ] Warning icon when being watched
  - [ ] Red flash on full detection
  - [ ] Sound cue (optional)

### 7.7 Police System
- [ ] Create PoliceOfficer class extends NPC
  - [ ] Better vision: 150 tiles
  - [ ] Always alert
  - [ ] Higher detection chance (+50%)
  - [ ] Follows patrol routes
  - [ ] Can chase robots

- [ ] Police patrol system
  - [ ] Generate patrol routes
  - [ ] 2-4 officers per patrol
  - [ ] Day patrols (8am-8pm)
  - [ ] Night patrols (8pm-8am)
  - [ ] More patrols when suspicion high

- [ ] Police behaviors
  - [ ] Normal patrol: walk route
  - [ ] Suspicious: investigate area
  - [ ] Alert: chase robot, radio backup
  - [ ] Capture: if catch robot, game over

### 7.8 Suspicion System
- [ ] Create SuspicionManager (src/systems/suspicion_manager.py)
  - [ ] Track suspicion level (0-100)
  - [ ] Track suspicion sources
  - [ ] Track decay rate
  - [ ] Handle tier transitions

- [ ] Suspicion tiers
  - [ ] 0-20: Normal (no effect)
  - [ ] 21-40: Rumors (slight police increase)
  - [ ] 41-60: Investigation (police attention)
  - [ ] 61-80: Inspection scheduled
  - [ ] 81-100: Restrictions/FBI

- [ ] Suspicion sources
  - [ ] NPC reports: +1 to +5
  - [ ] Police reports: +5 to +15
  - [ ] Failed inspection: +20
  - [ ] Illegal deconstruction seen: +10
  - [ ] Camera footage: +5 per camera
  - [ ] Rumors in city: +0.5 per day

- [ ] Suspicion decay
  - [ ] -0.1 per game hour (normal)
  - [ ] -0.5 per game hour (with social engineering)
  - [ ] Stops decaying above 60

- [ ] Suspicion UI
  - [ ] Meter in HUD (0-100)
  - [ ] Color: green, yellow, orange, red
  - [ ] Current tier displayed
  - [ ] Tooltip: recent events
  - [ ] Warning when crossing thresholds

### 7.9 Day/Night Cycle
- [ ] Create TimeManager (src/systems/time_manager.py)
  - [ ] Track hours, minutes, days
  - [ ] Time scale: 1 real sec = 1 game minute (configurable)
  - [ ] Day starts at 6am
  - [ ] Update all time-dependent systems

- [ ] Lighting system
  - [ ] Daytime (6am-8pm): full brightness
  - [ ] Dawn/dusk (5-7am, 7-9pm): partial darkness
  - [ ] Night (9pm-5am): dark
  - [ ] Apply darkness overlay
  - [ ] Reduce detection chances at night (-30%)
  - [ ] Reduce solar power at night

- [ ] Time-based events
  - [ ] NPCs follow schedules
  - [ ] Stores open/close
  - [ ] Police shift changes
  - [ ] Traffic patterns

### 7.11 Geographic Features (Rivers, Ocean, Bridges)
- [ ] Add terrain/water system
  - [ ] Create TerrainType enum (LAND, WATER, BRIDGE, DOCK)
  - [ ] Add terrain_type to Tile class
  - [ ] Update Grid to support terrain types
  - [ ] Render water tiles (animated blue)
  - [ ] Render land vs water boundaries

- [ ] River generation
  - [ ] Create RiverGenerator class
  - [ ] Generate river paths across map (Perlin noise or random walk)
  - [ ] Rivers flow from north to south (or random directions)
  - [ ] River width: 3-5 tiles
  - [ ] Rivers divide cities into sections
  - [ ] Ensure river tiles block normal pathfinding

- [ ] Bridge system
  - [ ] Create Bridge class (special building/terrain)
  - [ ] Place bridges across rivers at regular intervals
  - [ ] Bridge types: road bridge (vehicles), pedestrian bridge (NPCs only)
  - [ ] Bridges connect road networks on both sides
  - [ ] Allow pathfinding across bridges
  - [ ] Visual: raised structure over water

- [ ] Ocean generation
  - [ ] Place ocean on map edges (configurable which edges)
  - [ ] Ocean tiles block pathfinding completely
  - [ ] Dock buildings must be adjacent to ocean/water
  - [ ] Visual: deeper blue, animated waves

- [ ] Waterfront features
  - [ ] Dock building placement adjacent to water
  - [ ] Ships at docks (visual only, or functional for deliveries)
  - [ ] Boardwalk/pier structures
  - [ ] Beach tiles between land and ocean

- [ ] Pathfinding updates
  - [ ] Update A* to respect water tiles (impassable)
  - [ ] Allow pathfinding across bridges
  - [ ] NPCs/vehicles route around rivers via bridges
  - [ ] Calculate bridge crossings in city routes

### 7.12 Vehicle Traffic System
- [ ] Road network graph
  - [ ] Create RoadNetwork class (src/systems/road_network.py)
  - [ ] Build graph of road tiles and connections
  - [ ] Mark road directions (one-way vs two-way)
  - [ ] Identify intersections and turns
  - [ ] Calculate valid lanes per road segment

- [ ] Traffic lanes
  - [ ] Right-side driving (or configurable for region)
  - [ ] Each road has 2 lanes (one each direction)
  - [ ] Vehicles stay in correct lane for direction
  - [ ] Lane switching at intersections only
  - [ ] Mark road centers and lane boundaries

- [ ] Vehicle spawning system
  - [ ] Create TrafficManager (src/systems/traffic_manager.py)
  - [ ] Spawn civilian vehicles at city edges
  - [ ] Spawn delivery vehicles at marketplaces
  - [ ] Spawn police vehicles at police station
  - [ ] Vehicle density: 10-20 vehicles per city block
  - [ ] Vehicle types: car, truck, van, bus, police car

- [ ] Vehicle movement
  - [ ] Vehicles follow road lanes
  - [ ] Turn at intersections (planned routes)
  - [ ] Speed: 40-60 px/s depending on vehicle type
  - [ ] Acceleration/deceleration at stops
  - [ ] Stop at intersections (basic traffic rules)
  - [ ] Yield to vehicles already in intersection

- [ ] Vehicle pathfinding
  - [ ] Use RoadNetwork graph for routes
  - [ ] Calculate shortest path on roads
  - [ ] Vehicles have destinations (random or specific)
  - [ ] Recalculate route if blocked
  - [ ] Park at destination (if building)

- [ ] Traffic behavior
  - [ ] Follow vehicle in front (maintain distance)
  - [ ] Slow down if vehicle ahead
  - [ ] Stop for pedestrians crossing (optional)
  - [ ] Emergency vehicles (police) can speed/ignore rules
  - [ ] Turn signals before turning (visual indicator)

- [ ] Parked vehicles
  - [ ] Spawn parked cars near buildings
  - [ ] Park on side of road (not in lanes)
  - [ ] Parked vehicles are stationary
  - [ ] Working vs scrap condition (existing system)
  - [ ] Random spawn during day, despawn at night

- [ ] Visual updates
  - [ ] Vehicles render with correct rotation (existing)
  - [ ] Brake lights when slowing
  - [ ] Headlights at night
  - [ ] Turn signal indicators

### 7.13 Bus Transportation System
- [ ] Bus infrastructure
  - [ ] Create Bus class extends Vehicle
  - [ ] Larger size: 50x24 pixels
  - [ ] Yellow/orange color (school bus or city bus)
  - [ ] Capacity: 20 NPC passengers
  - [ ] Speed: slower than cars (30 px/s)

- [ ] Bus route system
  - [ ] Create BusRoute class
  - [ ] Routes defined as list of stops
  - [ ] Bus terminal is central hub
  - [ ] Routes connect: terminal ↔ residential ↔ commercial ↔ industrial
  - [ ] 3-5 routes per city
  - [ ] Each route has 5-10 stops

- [ ] Bus stops
  - [ ] Create BusStop prop (small shelter)
  - [ ] Place stops along bus routes
  - [ ] Stops every 15-20 tiles along route
  - [ ] Visual: small shelter with bench
  - [ ] NPCs wait at stops

- [ ] Bus behavior
  - [ ] Bus follows route waypoints
  - [ ] Stops at each bus stop for 5-10 seconds
  - [ ] Loads/unloads passengers
  - [ ] Multiple buses per route (staggered timing)
  - [ ] Buses run 6am-10pm (off schedule at night)

- [ ] NPC bus usage
  - [ ] NPCs pathfind to nearest bus stop
  - [ ] Wait at stop for bus
  - [ ] Board bus if going in desired direction
  - [ ] Ride bus to stop near destination
  - [ ] Disembark and walk to final destination
  - [ ] NPCs prefer bus for distances >50 tiles

- [ ] Bus schedule
  - [ ] Buses arrive at stops on schedule
  - [ ] Every 10-15 game minutes per route
  - [ ] Display arrival time at stops (UI)
  - [ ] NPCs check schedule before going to stop

- [ ] Bus rendering
  - [ ] Large bus sprite with windows
  - [ ] Show passenger count (visual indicator)
  - [ ] Route number displayed on bus
  - [ ] Direction indicator
  - [ ] Animated doors when stopped

### 7.14 Environmental Content Integration
- [ ] City generator updates
  - [ ] Update CityGenerator to place new buildings
  - [ ] Downtown zone: city hall, courthouse, library, train station
  - [ ] Industrial zone: warehouses
  - [ ] Waterfront zone: docks (if ocean/river present)
  - [ ] Residential zone: schools, bus terminals
  - [ ] Emergency services: fire house, police station

- [ ] Building placement rules
  - [ ] Fire house: near residential, 1 per 20 blocks
  - [ ] Library: near downtown or residential, 1-2 per city
  - [ ] School: in residential zones, 1 per 15 blocks
  - [ ] City hall: downtown center, 1 per city
  - [ ] Courthouse: near city hall, 1 per city
  - [ ] Bus terminal: central location, 1 per city (larger cities)
  - [ ] Train station: industrial or downtown, 1 per city
  - [ ] Warehouse: industrial zone, 2-4 per city
  - [ ] Dock: waterfront only, 1-2 per city (if water present)

- [ ] Prop placement system
  - [ ] Create PropManager (src/systems/prop_manager.py)
  - [ ] Place benches in parks (3-5 per park)
  - [ ] Place light poles along roads (every 5-10 tiles)
  - [ ] Place trash cans near buildings and parks (random)
  - [ ] Place bicycles near houses and commercial buildings (random)
  - [ ] Density: 50-100 props per city

- [ ] Prop rendering
  - [ ] Render props after ground, before buildings
  - [ ] Benches face random directions
  - [ ] Light poles illuminate at night (visual glow)
  - [ ] Trash cans near building entrances
  - [ ] Bicycles lean against walls/fences

- [ ] Marketplace integration
  - [ ] Integrate MarketplaceManager into game loop
  - [ ] Register marketplaces during city generation
  - [ ] Add "Sell Materials" UI near player factory
  - [ ] Show marketplace locations on map
  - [ ] Calculate delivery routes for vehicles
  - [ ] Update resource manager with sales income

- [ ] Delivery vehicle integration
  - [ ] Spawn delivery vehicles at marketplaces
  - [ ] Vehicles pathfind to player factory on roads
  - [ ] Use TrafficManager for road navigation
  - [ ] Load materials at factory (animation)
  - [ ] Return to marketplace with materials
  - [ ] Despawn after delivery complete

- [ ] UI updates for new content
  - [ ] Add building info tooltips (hover over buildings)
  - [ ] Show NPC count in buildings
  - [ ] Marketplace prices display
  - [ ] Bus route map (optional)
  - [ ] Delivery status notifications
  - [ ] Environmental stats (total props, vehicles, etc.)

### 7.15 Testing Phase 7 (Updated)
- [ ] Test city generation with new buildings
- [ ] Test geographic features (rivers, bridges, ocean)
- [ ] Test vehicle traffic and lane usage
- [ ] Test bus routes and NPC bus usage
- [ ] Test prop placement and rendering
- [ ] Test marketplace sales and deliveries
- [ ] Test NPC schedules and pathfinding
- [ ] Test detection system
- [ ] Test police patrols
- [ ] Test suspicion accumulation/decay
- [ ] Test day/night transitions
- [ ] Performance test with 100+ NPCs + vehicles + props
- [ ] Balance detection chances
- [ ] Verify pathfinding across bridges
- [ ] Test traffic flow at intersections
- [ ] Test delivery vehicle routes

---

## PHASE 8: CAMERA & INSPECTION SYSTEM

### 8.1 Camera System
- [ ] Create SecurityCamera class (src/entities/camera.py)
  - [ ] Position (on buildings/poles)
  - [ ] Vision cone (90 degrees)
  - [ ] Range: 200 tiles
  - [ ] Always detects robots in range
  - [ ] Can be hacked (with research)

- [ ] Camera placement
  - [ ] Place cameras in city
  - [ ] Near police station: many cameras
  - [ ] Main roads: some cameras
  - [ ] Random buildings: occasional cameras
  - [ ] Total: 20-30 cameras

- [ ] Camera detection
  - [ ] Always on (24/7)
  - [ ] Instant detection if robot in cone
  - [ ] Adds suspicion: +5 per detection
  - [ ] Records timestamp and location

- [ ] Camera rendering
  - [ ] Show camera sprite
  - [ ] Show vision cone (red when in view)
  - [ ] Show status: active, disabled, broken

### 8.2 Camera Hacking
- [ ] Hacking research prerequisites
  - [ ] Camera Hacking I: disable 1 camera, 5 minutes
  - [ ] Camera Hacking II: disable 1 camera, 15 minutes
  - [ ] Camera Hacking III: disable 3 cameras, 15 minutes

- [ ] Hacking UI
  - [ ] Click camera to hack
  - [ ] Shows hacking progress
  - [ ] Shows time remaining disabled
  - [ ] Can re-hack when expires

- [ ] Hacking consequences
  - [ ] Each hack: +2 suspicion
  - [ ] Too many hacks (>10): triggers security upgrade
  - [ ] Security upgrade: more cameras, better detection
  - [ ] Excessive hacking (>20): FBI investigation

### 8.3 Inspection System
- [ ] Create InspectionManager (src/systems/inspection_manager.py)
  - [ ] Schedule inspections at 60+ suspicion
  - [ ] Countdown timer (24-48 game hours warning)
  - [ ] Inspection day notification
  - [ ] Inspection process
  - [ ] Pass/fail logic
  - [ ] Consequences

- [ ] Inspection scheduling
  - [ ] Trigger when suspicion reaches 60
  - [ ] Random time: 1-2 game days from trigger
  - [ ] Warning message appears
  - [ ] Countdown in UI

- [ ] Inspection process
  - [ ] Inspector arrives at factory
  - [ ] Searches buildings for illegal materials
  - [ ] Checks material records
  - [ ] Looks for inconsistencies
  - [ ] Takes 1 game hour

- [ ] Illegal materials
  - [ ] Materials from livable houses
  - [ ] Materials from working vehicles
  - [ ] Materials from chain fences
  - [ ] Any material marked "illegal source"
  - [ ] Suspiciously large amounts of copper/electronics

- [ ] Inspection results
  - [ ] PASS: suspicion -20, no inspection for 7 days
  - [ ] FAIL (minor): suspicion +10, fine $5000, reinspection in 3 days
  - [ ] FAIL (major): suspicion +30, fine $20000, restrictions applied
  - [ ] FAIL (critical): game over (FBI raid immediate)

- [ ] Inspection UI
  - [ ] Warning countdown
  - [ ] Inspector arrival cutscene
  - [ ] Progress during inspection
  - [ ] Results screen
  - [ ] Consequences summary

### 8.4 Hiding Illegal Materials
- [ ] Material tagging system
  - [ ] Tag source when collected
  - [ ] Legal sources: landfill, decrepit houses, scrap vehicles
  - [ ] Illegal sources: livable houses, working vehicles, fences
  - [ ] Track in material metadata

- [ ] Hiding strategies
  - [ ] Sell all illegal materials before inspection
  - [ ] Use "Legal Disguise" research (risky)
  - [ ] Store in hidden warehouse (advanced research)
  - [ ] Process into components (removes tag)
  - [ ] Dump into landfill (lose materials)

- [ ] Inspection preparation
  - [ ] "Prepare for Inspection" button
  - [ ] Shows all illegal materials
  - [ ] Offers quick-sell option
  - [ ] Warns about suspicious amounts

### 8.5 Testing Phase 8
- [ ] Test camera detection
- [ ] Test camera hacking
- [ ] Test inspection scheduling
- [ ] Test inspection pass/fail
- [ ] Test material tagging
- [ ] Test hiding strategies
- [ ] Balance inspection difficulty

---

## PHASE 9: AUTHORITY ESCALATION & FBI

### 9.1 Authority Tiers
- [ ] Tier 0: Normal (0-20 suspicion)
  - [ ] Normal police patrols
  - [ ] Normal NPC alertness
  - [ ] No restrictions

- [ ] Tier 1: Rumors (21-40 suspicion)
  - [ ] +25% police patrols
  - [ ] NPCs slightly more alert
  - [ ] No concrete evidence yet

- [ ] Tier 2: Investigation (41-60 suspicion)
  - [ ] +50% police patrols
  - [ ] Undercover agents in city
  - [ ] Police check factory perimeter
  - [ ] Inspection scheduled soon

- [ ] Tier 3: Inspection (61-80 suspicion)
  - [ ] Inspections scheduled
  - [ ] Heavy police presence
  - [ ] Checkpoints near factory
  - [ ] Must pass inspection to continue

- [ ] Tier 4: Restrictions (81-100 suspicion)
  - [ ] Factory operations limited
  - [ ] Reduced operation hours
  - [ ] Mandatory inspections weekly
  - [ ] FBI investigation triggered

### 9.2 FBI System
- [ ] Create FBIManager (src/systems/fbi_manager.py)
  - [ ] FBI trigger conditions
  - [ ] Investigation progress
  - [ ] Countdown timer
  - [ ] Raid mechanics
  - [ ] Avoidance mechanics

- [ ] FBI triggers
  - [ ] Suspicion above 80 for 7 days
  - [ ] Failed inspection (critical)
  - [ ] Camera hacking count > 20
  - [ ] Three failed inspections
  - [ ] Anonymous tip (random event)

- [ ] FBI investigation
  - [ ] Warning: "FBI Opening Investigation"
  - [ ] Countdown: 14 game days
  - [ ] Visible FBI agents in city
  - [ ] Cannot hack cameras during investigation
  - [ ] Increased police patrols (+100%)

- [ ] Avoiding FBI raid
  - [ ] Reduce suspicion below 60
  - [ ] Pass all inspections
  - [ ] Delete hacking research (if hacking was trigger)
  - [ ] Bribe official ($50,000) - risky
  - [ ] Lay low (no operations for 7 days)

- [ ] FBI raid (game over)
  - [ ] Raid cutscene
  - [ ] Factory seized
  - [ ] All robots captured
  - [ ] Assets frozen
  - [ ] Game over screen with stats
  - [ ] Option to view ending

### 9.3 Social Engineering
- [ ] Create SocialEngineeringManager
  - [ ] Manage rumors in city
  - [ ] Community relations
  - [ ] Propaganda campaigns
  - [ ] Bribery system

- [ ] Rumor management
  - [ ] Rumors spread when suspicion > 20
  - [ ] Can counter with social engineering
  - [ ] Cost: $1000 per campaign
  - [ ] Effect: -5 suspicion, slower growth
  - [ ] Takes 3 days to take effect

- [ ] Community relations
  - [ ] Donate to city: $5000 = -3 suspicion
  - [ ] Sponsor events: $10000 = -8 suspicion
  - [ ] "Good neighbor" bonus: -0.2 suspicion/day
  - [ ] Improves city opinion

- [ ] Propaganda
  - [ ] Requires research: Social Engineering
  - [ ] Weekly cost: $2000
  - [ ] Effect: reduces suspicion growth by 50%
  - [ ] Can fail if evidence too strong

### 9.4 Testing Phase 9
- [ ] Test tier transitions
- [ ] Test FBI triggers
- [ ] Test FBI avoidance
- [ ] Test FBI raid (game over)
- [ ] Test social engineering
- [ ] Balance authority escalation speed

---

## PHASE 10: ADVANCED FEATURES

### 10.1 Drone System
- [ ] Create Drone class (src/entities/drone.py)
  - [ ] Flying entity (no collision with ground)
  - [ ] Fast speed (200 pixels/sec)
  - [ ] Limited battery (15 minutes)
  - [ ] Vision range: 300 tiles
  - [ ] Cannot collect materials
  - [ ] Reveals fog of war

- [ ] Drone construction
  - [ ] Requires research: Drones I
  - [ ] Cost: $5000 + components
  - [ ] Built by robots like buildings
  - [ ] Launches from drone pad

- [ ] Drone controls
  - [ ] Select drone like robot
  - [ ] Manual control or autonomous
  - [ ] Autonomous: patrol route
  - [ ] Returns to pad when low battery

- [ ] Fog of war system
  - [ ] Unexplored areas: dark
  - [ ] Explored areas: visible
  - [ ] Drones reveal large areas
  - [ ] Robots reveal small areas
  - [ ] City starts partially explored

### 10.2 Wireless Transmitters
- [ ] Create WirelessTransmitter building
  - [ ] Requires research: Wireless Transmitters I/II/III
  - [ ] 2x2 footprint
  - [ ] Cost: $3000/$6000/$10000
  - [ ] Range: 300/450/600 tiles
  - [ ] Power consumption: 2/3/4 units

- [ ] Control range system
  - [ ] Factory base range: 200 tiles
  - [ ] Transmitters extend range
  - [ ] Overlapping ranges merge
  - [ ] Show control range on map (toggle)

- [ ] Inside control range
  - [ ] Full robot control
  - [ ] See real-time robot status
  - [ ] Issue immediate commands
  - [ ] See threats (police, NPCs, cameras)

- [ ] Outside control range
  - [ ] Robots fully autonomous
  - [ ] No manual control
  - [ ] No real-time status
  - [ ] Higher risk (no warnings)
  - [ ] Higher reward (can reach distant areas)

### 10.3 Market Fluctuation System
- [ ] Create MarketManager (src/systems/market_manager.py)
  - [ ] Load market data from advanced_systems.json
  - [ ] Track prices for all materials/components
  - [ ] Update prices every 30 game minutes
  - [ ] Generate price trends
  - [ ] Trigger market events

- [ ] Material price categories
  - [ ] Paper products: base volatility 15%
  - [ ] Plastics: volatility 20%
  - [ ] Metals: volatility 25%
  - [ ] Glass: volatility 10%
  - [ ] Rubber: volatility 18%
  - [ ] Energy products: volatility 30%
  - [ ] Organics: volatility 12%

- [ ] Price trends
  - [ ] Bull trend: prices rising (48-120 hours)
  - [ ] Bear trend: prices falling
  - [ ] Stable: minor fluctuations
  - [ ] Event-driven: sudden spike/crash

- [ ] Market events
  - [ ] Construction boom: metals +40%, glass +30%
  - [ ] Energy crisis: energy products +80%, plastics +30%
  - [ ] Manufacturing boom: plastics +50%, metals +30%
  - [ ] Market crash: all materials -40%
  - [ ] Scarcity event: one material +100%

- [ ] Market forecasting (research required)
  - [ ] 3-day forecast with 70% accuracy
  - [ ] Shows trend direction
  - [ ] Shows event probability
  - [ ] Helps plan sales

- [ ] Automated trading (research required)
  - [ ] Set price thresholds
  - [ ] Auto-sell when price high
  - [ ] Hold when price low
  - [ ] Notification system

### 10.4 Weather System
- [ ] Create WeatherManager (src/systems/weather_manager.py)
  - [ ] Track current weather
  - [ ] Generate weather patterns
  - [ ] Weather affects gameplay
  - [ ] Weather forecast (with research)

- [ ] Weather types
  - [ ] Clear: normal conditions
  - [ ] Cloudy: -30% solar power
  - [ ] Rain: -50% solar, -20% detection
  - [ ] Heavy rain: -75% solar, -40% detection, slower robots
  - [ ] Fog: -60% detection, -30% visibility
  - [ ] Storm: operations risky, high detection if seen
  - [ ] Snow: -50% solar, -30% robot speed, -20% detection

- [ ] Weather effects
  - [ ] Solar power generation
  - [ ] Detection chances
  - [ ] Robot movement speed
  - [ ] NPC behavior (stay indoors in bad weather)
  - [ ] Visibility range

- [ ] Weather forecasting (research required)
  - [ ] 3-day forecast
  - [ ] Plan operations around weather
  - [ ] Best time for risky operations: fog or rain at night

- [ ] Weather UI
  - [ ] Current weather icon
  - [ ] Temperature (optional)
  - [ ] Forecast panel (if researched)
  - [ ] Weather alert warnings

### 10.5 Deconstruction System
- [ ] Deconstruction research
  - [ ] Deconstruction I: buildings (requires specific conditions)
  - [ ] Deconstruction II: vehicles
  - [ ] Deconstruction III: livable houses (VERY ILLEGAL)

- [ ] Building deconstruction
  - [ ] Robot selects target building
  - [ ] Deconstruction takes time (30-120 seconds)
  - [ ] Robot makes noise
  - [ ] Produces materials based on building type
  - [ ] Highly visible (noise level 8-10)

- [ ] Vehicle deconstruction
  - [ ] Select parked vehicle
  - [ ] Time: 30-45 seconds
  - [ ] Noise level: 6-8
  - [ ] Working vehicle: ILLEGAL (+10 suspicion if seen)
  - [ ] Scrap vehicle: LEGAL

- [ ] House deconstruction
  - [ ] Decrepit house: LEGAL, 60 seconds, noise 6/10
  - [ ] Livable house: ILLEGAL, 120 seconds, noise 8/10
  - [ ] If occupied: game over (police immediate)
  - [ ] If seen by NPCs: +20 suspicion, police called
  - [ ] Best done at night when residents out

- [ ] Noise system
  - [ ] Noise propagates based on distance
  - [ ] NPCs hear noise and investigate
  - [ ] Police hear noise from farther
  - [ ] Noise level affects detection radius
  - [ ] Visual: sound wave animation

### 10.6 Multiple Endings
- [ ] Ending system
  - [ ] Track ending conditions
  - [ ] Ending cutscenes
  - [ ] Ending stats screen
  - [ ] Replay option

- [ ] 10 Endings (from advanced_systems.json)

1. [ ] **The Bust** - FBI raid successful
   - Trigger: FBI countdown reaches 0
   - Cutscene: Factory raided, player arrested
   - Stats: Total earnings, robots lost

2. [ ] **The Meltdown** - Caught red-handed
   - Trigger: Deconstructing occupied house
   - Cutscene: Police response, immediate arrest
   - Stats: Time survived

3. [ ] **The Close Call** - Narrowly escape raid
   - Trigger: Avoid FBI with <1 day remaining
   - Cutscene: FBI leaves, operation continues
   - Ending: Can continue playing

4. [ ] **Honest Work** - Stay 100% legal for 30 days
   - Trigger: 0 suspicion for 30 days, only legal materials
   - Cutscene: Praised as legitimate business
   - Reward: Bonus money, reputation

5. [ ] **The Kingpin** - Master criminal
   - Trigger: Earn $1,000,000, suspicion never above 40
   - Cutscene: Evaded all detection, untouchable empire
   - Stats: Total illegal materials processed

6. [ ] **The Gambler** - Risky strategy pays off
   - Trigger: Operate at 60-80 suspicion for 20 days, then reduce to 20
   - Cutscene: Lived on the edge, mastered the game
   - Stats: Close calls avoided

7. [ ] **The Ghost** - Perfect stealth
   - Trigger: 50 days, suspicion never above 20
   - Cutscene: Operated undetected, true professional
   - Stats: Total operations completed

8. [ ] **The Mogul** - Economic victory
   - Trigger: Earn $5,000,000
   - Cutscene: Built recycling empire, retire wealthy
   - Stats: Net worth, buildings owned

9. [ ] **The Speedrunner** - Fast completion
   - Trigger: Earn $500,000 in under 30 days
   - Cutscene: Rapid growth, aggressive strategy
   - Stats: Days taken, earnings per day

10. [ ] **The Survivor** - Long-term operation
    - Trigger: Operate for 365 days
    - Cutscene: Year in the life, master operator
    - Stats: Total materials processed, robots built

### 10.7 Scoring System
- [ ] Create ScoreManager (src/systems/score_manager.py)
  - [ ] Track all score components
  - [ ] Calculate final score
  - [ ] Score breakdown display
  - [ ] Leaderboard (local)

- [ ] Score components
  - [ ] Base earnings: $1 = 1 point
  - [ ] Time bonus: -10 points per day
  - [ ] Speed bonus: earn $500k in 30 days = +5000 points
  - [ ] Stealth bonus: suspicion never above 20 = +3000 points
  - [ ] Risk bonus: operate at 60-80 suspicion = +2000 points
  - [ ] Efficiency bonus: materials processed per robot-hour
  - [ ] Building bonus: +100 per building constructed
  - [ ] Research bonus: +200 per technology researched
  - [ ] Ending bonus: varies by ending (1000-10000 points)

- [ ] Score modifiers
  - [ ] Failed inspections: -1000 each
  - [ ] Camera hacks: -50 each
  - [ ] FBI investigation: -5000
  - [ ] Legal operation (30 days): +3000

- [ ] Final score screen
  - [ ] Total score
  - [ ] Breakdown by category
  - [ ] Rank: D, C, B, A, S, SS, SSS
  - [ ] Achievements unlocked
  - [ ] Compare to previous runs

### 10.8 Testing Phase 10
- [ ] Test drones
- [ ] Test wireless transmitters
- [ ] Test control range system
- [ ] Test market fluctuations
- [ ] Test weather system
- [ ] Test deconstruction
- [ ] Test all 10 endings
- [ ] Test scoring system
- [ ] Balance risk vs reward

---

## PHASE 11: UI/UX POLISH

### 11.1 Main Menu
- [ ] Title screen
  - [ ] Game logo
  - [ ] Background animation (robots working)
  - [ ] Menu buttons: New Game, Load Game, Settings, Quit
  - [ ] Version number
  - [ ] Credits button

- [ ] New game setup
  - [ ] Difficulty selection: Easy, Normal, Hard, Insane
  - [ ] Name your operation
  - [ ] Starting money modifier
  - [ ] Tutorial option

- [ ] Load game screen
  - [ ] List saved games
  - [ ] Show date, time played, money
  - [ ] Preview screenshot
  - [ ] Delete save option

### 11.2 In-Game Menus
- [ ] Pause menu (ESC)
  - [ ] Resume
  - [ ] Settings
  - [ ] Save Game
  - [ ] Load Game
  - [ ] Quit to Menu

- [ ] Building menu (B)
  - [ ] Category tabs
  - [ ] Search/filter
  - [ ] Building cards with preview
  - [ ] Stats and costs
  - [ ] Build button

- [ ] Research menu (R)
  - [ ] Tech tree visualization
  - [ ] Zoom/pan controls
  - [ ] Tech details panel
  - [ ] Progress indicator
  - [ ] Filter by category

- [ ] Map menu (M)
  - [ ] Full map view
  - [ ] Toggle layers: buildings, robots, threats, control range
  - [ ] Click to move camera
  - [ ] Legend

- [ ] Statistics menu (T)
  - [ ] Production stats
  - [ ] Financial stats
  - [ ] Detection stats
  - [ ] Robot stats
  - [ ] Graphs over time

### 11.3 HUD Improvements
- [ ] Redesign resource panel
  - [ ] Cleaner layout
  - [ ] Icons for materials
  - [ ] Tooltips with details
  - [ ] Click to see detailed inventory

- [ ] Add power panel
  - [ ] Generation vs consumption
  - [ ] Battery charge
  - [ ] Warning indicators
  - [ ] Click to see power grid

- [ ] Add time panel
  - [ ] Current time
  - [ ] Day counter
  - [ ] Season (optional)
  - [ ] Speed controls (pause, 1x, 2x, 4x)

- [ ] Add notifications system
  - [ ] Toast notifications
  - [ ] Warning, info, success colors
  - [ ] Queue multiple notifications
  - [ ] Click to dismiss or view details

- [ ] Add minimap
  - [ ] Bottom-right corner
  - [ ] Shows: factory, robots, threats
  - [ ] Click to move camera
  - [ ] Toggle visibility

### 11.4 Tooltips and Help
- [ ] Tooltip system
  - [ ] Hover over anything for tooltip
  - [ ] Shows name, description, stats
  - [ ] Hotkey hints
  - [ ] Context-sensitive

- [ ] Tutorial system
  - [ ] First-time player guide
  - [ ] Step-by-step instructions
  - [ ] Highlight UI elements
  - [ ] Can skip or disable

- [ ] Help menu (F1)
  - [ ] Controls reference
  - [ ] Game concepts
  - [ ] Building guide
  - [ ] Research guide
  - [ ] Tips and tricks

### 11.5 Visual Feedback
- [ ] Selection indicators
  - [ ] Selected units: thick border
  - [ ] Hovered units: thin border
  - [ ] Multiple selection: shift-click

- [ ] Action feedback
  - [ ] Construction started: checkmark animation
  - [ ] Research complete: fanfare
  - [ ] Material collected: particle effect
  - [ ] Building placed: build animation
  - [ ] Level up: glow effect

- [ ] Warning indicators
  - [ ] Low power: red flash
  - [ ] Low funds: money icon blinks
  - [ ] High suspicion: meter pulses
  - [ ] Detection: warning triangle
  - [ ] Inspection coming: countdown blinks

### 11.6 Settings Menu
- [ ] Graphics settings
  - [ ] Resolution
  - [ ] Fullscreen toggle
  - [ ] VSync toggle
  - [ ] Show FPS
  - [ ] Particle effects quality

- [ ] Audio settings
  - [ ] Master volume
  - [ ] Music volume
  - [ ] SFX volume
  - [ ] Mute toggle

- [ ] Gameplay settings
  - [ ] Game speed
  - [ ] Auto-save interval
  - [ ] Tutorial enabled
  - [ ] Difficulty
  - [ ] Edge scrolling

- [ ] Controls settings
  - [ ] Key bindings (rebindable)
  - [ ] Mouse sensitivity
  - [ ] Scroll speed

### 11.7 Testing Phase 11
- [ ] Test all menus
- [ ] Test tooltip system
- [ ] Test tutorial
- [ ] Test settings
- [ ] Usability testing with fresh players

---

## PHASE 12: GRAPHICS & AUDIO

### 12.1 Sprite Creation
- [ ] Robot sprites
  - [ ] Idle animation
  - [ ] Moving animation (8 directions)
  - [ ] Collecting animation
  - [ ] Building animation
  - [ ] Damaged states

- [ ] Building sprites
  - [ ] All 32 building types
  - [ ] Multiple angles (isometric optional)
  - [ ] Construction stages
  - [ ] Active vs inactive states
  - [ ] Upgrade variations

- [ ] NPC sprites
  - [ ] Walking animation (4 directions)
  - [ ] Different NPC types (civilian, police, FBI)
  - [ ] Idle animations
  - [ ] Alert states

- [ ] Vehicle sprites
  - [ ] Cars (working and scrap)
  - [ ] Trucks
  - [ ] Police cars
  - [ ] Multiple angles

- [ ] UI sprites
  - [ ] Icons for all materials
  - [ ] Icons for all buildings
  - [ ] Icons for research
  - [ ] Button sprites
  - [ ] Panel backgrounds

### 12.2 Animations
- [ ] Particle effects
  - [ ] Material collection sparkle
  - [ ] Processing smoke
  - [ ] Power surge
  - [ ] Explosions (deconstruction)
  - [ ] Rain/snow effects

- [ ] Building animations
  - [ ] Smoke stacks puffing
  - [ ] Solar panels tilting
  - [ ] Conveyor belts moving
  - [ ] Lights blinking

- [ ] Environmental animations
  - [ ] Day/night transition
  - [ ] Weather transitions
  - [ ] Trees swaying
  - [ ] Traffic lights

### 12.3 Sound Effects
- [ ] UI sounds
  - [ ] Button click
  - [ ] Menu open/close
  - [ ] Notification pop
  - [ ] Research complete
  - [ ] Building placed

- [ ] Robot sounds
  - [ ] Movement (mechanical hum)
  - [ ] Collecting (pickup sound)
  - [ ] Depositing materials
  - [ ] Low power warning

- [ ] Building sounds
  - [ ] Processing (machinery)
  - [ ] Construction (hammering, drilling)
  - [ ] Power generator (humming)
  - [ ] Factory ambience

- [ ] Detection sounds
  - [ ] Detection warning (tense music)
  - [ ] Police siren (distant)
  - [ ] Camera alert beep
  - [ ] Inspection notification

- [ ] Ambient sounds
  - [ ] City noise (day)
  - [ ] Quiet night
  - [ ] Rain/wind
  - [ ] Birds chirping

### 12.4 Music
- [ ] Main menu theme
  - [ ] Mysterious, industrial
  - [ ] Loop: 2-3 minutes

- [ ] Gameplay themes
  - [ ] Day theme (relaxed, productive)
  - [ ] Night theme (tense, sneaky)
  - [ ] High suspicion theme (nervous, urgent)
  - [ ] FBI investigation theme (intense)

- [ ] Event music
  - [ ] Inspection cutscene
  - [ ] FBI raid
  - [ ] Victory themes (per ending)

### 12.5 Testing Phase 12
- [ ] Test all sprites display correctly
- [ ] Test animations smooth
- [ ] Test sound triggers
- [ ] Test music transitions
- [ ] Volume balance
- [ ] Performance with all effects

---

## PHASE 13: SAVE/LOAD SYSTEM

### 13.1 Save System Architecture
- [ ] Create SaveManager (src/systems/save_manager.py)
  - [ ] Serialize game state to JSON
  - [ ] Save to file
  - [ ] Load from file
  - [ ] Validate save data
  - [ ] Handle save versions

- [ ] Saveable data
  - [ ] Game time (day, hour, minute)
  - [ ] Resources (money, materials, components)
  - [ ] Buildings (type, position, level, state)
  - [ ] Robots (position, inventory, state, upgrades)
  - [ ] Research (completed, in-progress)
  - [ ] Suspicion level and sources
  - [ ] NPCs (positions, schedules, states)
  - [ ] Police patrols
  - [ ] Camera states (hacked, active)
  - [ ] Inspection schedule
  - [ ] FBI investigation status
  - [ ] Weather state
  - [ ] Market prices
  - [ ] Statistics
  - [ ] Settings

### 13.2 Save File Management
- [ ] Save file format
  - [ ] JSON format for readability
  - [ ] Compressed optional
  - [ ] Version number
  - [ ] Timestamp
  - [ ] Save name

- [ ] Auto-save
  - [ ] Every 5 game days
  - [ ] Before major events (inspection, FBI)
  - [ ] On game exit
  - [ ] Configurable interval

- [ ] Manual save
  - [ ] Quick save (F5)
  - [ ] Save menu (with name)
  - [ ] Multiple save slots (unlimited)
  - [ ] Save screenshot

- [ ] Load system
  - [ ] Load menu
  - [ ] Quick load (F9)
  - [ ] Load validates data
  - [ ] Load rebuilds game state

### 13.3 Data Serialization
- [ ] Entity serialization
  - [ ] Save entity ID, type, position
  - [ ] Save entity-specific data
  - [ ] Rebuild entity on load

- [ ] Manager serialization
  - [ ] Each manager has to_dict() method
  - [ ] Each manager has from_dict() method
  - [ ] Handles circular references

- [ ] Grid serialization
  - [ ] Save tile types
  - [ ] Save tile occupancy
  - [ ] Rebuild grid on load

### 13.4 Testing Phase 13
- [ ] Test save during various game states
- [ ] Test load restores exact state
- [ ] Test auto-save
- [ ] Test quick save/load
- [ ] Test save file corruption handling
- [ ] Test save version migration

---

## PHASE 14: BALANCE & POLISH

### 14.1 Economic Balance
- [ ] Material values
  - [ ] Balance sell prices vs collection effort
  - [ ] Ensure progression: landfill → houses → advanced
  - [ ] Make high-risk worth the reward

- [ ] Building costs
  - [ ] Early buildings affordable
  - [ ] Advanced buildings require planning
  - [ ] Upgrade costs scale reasonably

- [ ] Research costs and times
  - [ ] Essential research accessible
  - [ ] Advanced research expensive
  - [ ] Times feel meaningful but not tedious

- [ ] Income progression
  - [ ] Early game: $1000-5000/day
  - [ ] Mid game: $10000-50000/day
  - [ ] Late game: $100000+/day

### 14.2 Gameplay Balance
- [ ] Detection difficulty
  - [ ] Easy to avoid at start
  - [ ] Harder as expand operations
  - [ ] Possible to operate stealthily with skill

- [ ] Suspicion rates
  - [ ] Slow growth allows recovery
  - [ ] Fast growth punishes carelessness
  - [ ] Decay rate balanced with growth

- [ ] Police effectiveness
  - [ ] Challenging but beatable
  - [ ] Patrol patterns learnable
  - [ ] Can be avoided with planning

- [ ] Robot efficiency
  - [ ] Starting robots useful but limited
  - [ ] Upgrades feel impactful
  - [ ] Multiple robots scale well

- [ ] Processing speeds
  - [ ] Fast enough to feel productive
  - [ ] Slow enough to require planning
  - [ ] Upgrades meaningful

### 14.3 Difficulty Levels
- [ ] Easy mode
  - [ ] +50% starting money ($15000)
  - [ ] -30% suspicion growth
  - [ ] -20% detection chances
  - [ ] +20% material values
  - [ ] Longer inspection warnings

- [ ] Normal mode
  - [ ] Default values
  - [ ] Balanced challenge

- [ ] Hard mode
  - [ ] -20% starting money ($8000)
  - [ ] +30% suspicion growth
  - [ ] +20% detection chances
  - [ ] -10% material values
  - [ ] More police patrols

- [ ] Insane mode
  - [ ] -50% starting money ($5000)
  - [ ] +50% suspicion growth
  - [ ] +40% detection chances
  - [ ] -20% material values
  - [ ] Double police patrols
  - [ ] FBI triggers easier

### 14.4 Bug Fixing
- [ ] Gameplay bugs
  - [ ] Robots getting stuck
  - [ ] Pathfinding failures
  - [ ] Collection not working
  - [ ] Buildings not processing

- [ ] UI bugs
  - [ ] Menus not closing
  - [ ] Tooltips incorrect
  - [ ] HUD display errors
  - [ ] Click detection issues

- [ ] Logic bugs
  - [ ] Suspicion calculation errors
  - [ ] Money duplication exploits
  - [ ] Research not applying
  - [ ] Save/load inconsistencies

- [ ] Performance bugs
  - [ ] Frame rate drops
  - [ ] Memory leaks
  - [ ] Slow pathfinding
  - [ ] Lag with many entities

### 14.5 Testing Phase 14
- [ ] Full playthrough on each difficulty
- [ ] Balance testing with testers
- [ ] Bug squashing
- [ ] Performance optimization
- [ ] Final polish pass

---

## PHASE 15: LAUNCH PREPARATION

### 15.1 Documentation
- [ ] README.md
  - [ ] Game description
  - [ ] Installation instructions
  - [ ] Controls
  - [ ] Basic strategy guide

- [ ] CHANGELOG.md
  - [ ] Version history
  - [ ] Features added
  - [ ] Bugs fixed

- [ ] LICENSE
  - [ ] Choose license (MIT, GPL, etc.)
  - [ ] Include license text

### 15.2 Distribution
- [ ] Package game
  - [ ] PyInstaller for standalone exe
  - [ ] Include all assets
  - [ ] Test on clean machine

- [ ] Platform builds
  - [ ] Windows build
  - [ ] Mac build (if possible)
  - [ ] Linux build

- [ ] Upload to platforms
  - [ ] itch.io
  - [ ] GitHub releases
  - [ ] Steam (requires Steamworks integration)

### 15.3 Marketing Materials
- [ ] Screenshots
  - [ ] 5-10 high-quality screenshots
  - [ ] Show different game stages
  - [ ] Show exciting moments

- [ ] Trailer
  - [ ] 1-2 minute gameplay trailer
  - [ ] Show key features
  - [ ] Background music

- [ ] Description
  - [ ] Elevator pitch
  - [ ] Feature list
  - [ ] System requirements

### 15.4 Launch
- [ ] Launch checklist
  - [ ] All features complete
  - [ ] All bugs fixed
  - [ ] Performance acceptable
  - [ ] Documentation complete
  - [ ] Builds tested
  - [ ] Marketing ready

- [ ] Post-launch
  - [ ] Monitor feedback
  - [ ] Fix critical bugs
  - [ ] Plan updates
  - [ ] Community engagement

---

## ESTIMATED TOTALS

**Total Tasks: ~800 granular tasks**

**Estimated Timeline:**
- Phase 4 (Building): 4-6 weeks
- Phase 5 (Processing): 3-4 weeks
- Phase 6 (Research): 3-4 weeks
- Phase 7 (City/Detection): 6-8 weeks
- Phase 8 (Camera/Inspection): 2-3 weeks
- Phase 9 (Authority/FBI): 2-3 weeks
- Phase 10 (Advanced Features): 6-8 weeks
- Phase 11 (UI/UX): 3-4 weeks
- Phase 12 (Graphics/Audio): 6-10 weeks
- Phase 13 (Save/Load): 1-2 weeks
- Phase 14 (Balance/Polish): 4-8 weeks
- Phase 15 (Launch): 1-2 weeks

**Total remaining: 6-12 months** (depending on pace and prior experience)

**Current completion: ~25%** (Phases 1-3 done)

---

## PRIORITY ORDERING

**Critical path for MVP (Minimum Viable Product):**
1. Phase 4: Building System → Core gameplay mechanic
2. Phase 5: Material Processing → Makes buildings useful
3. Phase 6: Research System → Progression system
4. Phase 7: City & Detection → Core challenge
5. Phase 8: Camera & Inspection → Win/lose conditions
6. Phase 13: Save/Load → QoL essential
7. Phase 14: Balance → Make it fun

**Can defer to v1.1+:**
- Phase 9: FBI (but keep inspections from Phase 8)
- Phase 10: Drones, market system, weather
- Phase 11: UI polish (keep functional)
- Phase 12: Graphics (can use placeholders initially)

**Recommended focus:**
Start with Phase 4 (Building System) as it's the foundation for everything else.

---

END OF COMPREHENSIVE TODO LIST
