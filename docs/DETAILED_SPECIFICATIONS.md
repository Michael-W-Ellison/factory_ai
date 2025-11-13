# Recycling Factory - Detailed Specifications

**Version:** 1.1
**Last Updated:** 2025-11-13

This document provides detailed specifications for all game systems, materials, buildings, and mechanics that have been fully defined with concrete values and parameters.

---

## Table of Contents
1. [Overview](#overview)
2. [Material System](#material-system)
3. [Building System](#building-system)
4. [Research Tree](#research-tree)
5. [Game Mechanics](#game-mechanics)
6. [Configuration Files](#configuration-files)

---

## Overview

This document supplements the Game Design Document with **precise numerical values** and **complete specifications** for every game system. All data is stored in JSON configuration files located in `data/config/` for easy balancing and modification.

### What's New

Three major configuration files have been created:
- **materials.json** - Complete material types, compositions, and processing specs
- **buildings.json** - All factory buildings with costs, stats, and functions
- **research.json** - Full research tree with 100+ technologies
- **game_systems.json** - Gameplay mechanics, events, and balance settings

---

## Material System

### Material Types (15 Total)

Defined in `data/config/materials.json`:

| Material | Category | Base Value | Processing Time | Power Cost | Building Required |
|----------|----------|------------|-----------------|------------|-------------------|
| Organic | Landfill | $0.10/kg | 2.0s | 0.5 | Bio-Waste Treatment |
| Paper/Cardboard | Recyclable | $0.50/kg | 3.0s | 1.0 | Paper Recycler |
| Plastic | Recyclable | $1.00/kg | 4.0s | 2.0 | Plastic Recycler |
| Metal | Recyclable | $3.00/kg | 5.0s | 3.0 | Metal Refinery |
| Glass | Recyclable | $2.00/kg | 4.0s | 2.5 | Glassworks |
| Hazardous | Toxic | -$5.00/kg | 8.0s | 5.0 | Toxic Incinerator |
| Wood | Organic | $0.80/kg | 3.0s | 1.0 | Coal Oven |
| Concrete | Construction | $0.30/kg | 6.0s | 3.0 | Metal Refinery |
| Steel | Metal | $5.00/kg | 6.0s | 4.0 | Metal Refinery |
| Iron | Metal | $3.50/kg | 5.0s | 3.5 | Metal Refinery |
| Copper | Metal | $8.00/kg | 5.0s | 3.5 | Metal Refinery |
| Textiles | Organic | $0.40/kg | 2.5s | 1.0 | Paper Recycler* |
| Rubber | Recyclable | $1.50/kg | 4.0s | 2.0 | Rubber Recycler |
| Petroleum | Liquid | $6.00/kg | 5.0s | 3.0 | Crude Oil Refinery |
| Toxic Waste | Toxic | -$8.00/kg | 10.0s | 6.0 | Toxic Incinerator |

*Requires "Cloth Sorting" research

### Source Compositions

#### Landfill
- Organic Material: 44%
- Paper/Cardboard: 17%
- Plastic: 17%
- Metals: 9%
- Glass: 5%
- Hazardous: 8%

#### House (Livable Condition)
- Wood: 40%, Concrete: 20%, Steel: 10%, Textiles: 7%
- Glass: 10%, Copper: 6%, Iron: 2%, Plastic: 5%
- **Deconstruction Time:** 120 seconds
- **Noise Level:** 8/10
- **Status:** ILLEGAL

#### House (Decrepit)
- Wood: 15%, Concrete: 18%, Steel: 5%, Textiles: 2%
- Glass: 5%, Plastic: 3%, Toxic: 8%, **Unusable: 44%**
- **Deconstruction Time:** 60 seconds
- **Noise Level:** 6/10
- **Status:** Legal

#### Vehicle (Working)
- Steel: 25%, Iron: 40%, Plastic: 10%, Textiles: 5%
- Glass: 6%, Copper: 2%, Rubber: 8%, Petroleum: 10%, Toxic: 4%
- **Deconstruction Time:** 45 seconds
- **Status:** ILLEGAL

#### Vehicle (Scrap)
- Steel: 15%, Iron: 25%, Plastic: 7%, Textiles: 2%
- Glass: 3%, Copper: 1%, Rubber: 4%, Toxic: 14%, **Unusable: 29%**
- **Deconstruction Time:** 30 seconds
- **Status:** Legal

#### Fences and Walls
- **Chain Link Fence:** 100% Iron (10s, illegal)
- **Wooden Fence:** 95% Wood, 5% Iron (8s, illegal)
- **Brick Wall:** 100% Poor Slag (20s, illegal)

#### Trees
- Wood: 85%, Organic: 15%
- **Deconstruction Time:** 15 seconds
- **Requires:** Tree Cutting research
- **Status:** Legal

### Processed Components

Components produced from raw materials (with market values):

| Component | Value | Source Material |
|-----------|-------|-----------------|
| Bio-Slop | $0.50 | Organic, Wood |
| Waste Paper | $0.30 | Paper |
| Low-Quality Paper | $1.00 | Paper |
| Medium-Quality Paper | $2.50 | Paper |
| High-Quality Paper | $5.00 | Paper |
| Refined Metal | $4.00 | Metal |
| Refined Steel | $6.00 | Steel, or Iron+Charcoal |
| Refined Copper | $10.00 | Copper |
| Gray Glass Blanks | $2.50 | Glass |
| Colored Glass Blanks | $3.00 | Glass |
| Bullet-Proof Glass | $8.00 | Glass |
| Charcoal | $1.50 | Wood |
| Tar | $2.00 | Wood |
| Refined Oil | $8.00 | Petroleum |
| Bitumen | $3.00 | Petroleum |
| Dirty Methane | $0.50 | Landfill Gas, Bio-Slop |
| Pure Methane | $3.00 | Bio-Slop (upgraded plant) |
| Ultra-Pure Methane | $6.00 | Bio-Slop (max upgraded plant) |

---

## Building System

### Core Buildings (32 Total)

Defined in `data/config/buildings.json`:

#### Power Generation

| Building | Cost | Power Output | Special Requirements |
|----------|------|--------------|----------------------|
| Landfill Gas Extraction | $0 (starting) | 10.0 | Degrades as landfill empties |
| Solar Array | $2,000 | 15.0 | Time-dependent, 3 upgrade tiers |
| Wind Turbine | $2,500 | 20.0 | Variable (wind-dependent) |
| Natural Gas Generator | $3,500 | 40.0 | Uses methane fuel |
| Steam Generator | $2,000 | 30.0 | Uses waste/charcoal |

#### Processing Buildings

| Building | Cost | Power Usage | Inputs | Outputs | Pollution |
|----------|------|-------------|--------|---------|-----------|
| Paper Recycler | $2,500 | 3.0 | Paper | 4 quality levels | 1.0 |
| Metal Refinery | $4,000 | 6.0 | Metals | Refined metals, slag | 2.0 |
| Glassworks | $3,000 | 4.0 | Glass | 3 glass types | 1.0 |
| Plastic Recycler | $3,500 | 4.0 | Plastic | 4 quality levels | 2.0 |
| Rubber Recycler | $3,200 | 3.5 | Rubber | 4 quality levels | 2.5 |
| Coal Oven | $1,800 | 2.0 | Wood | Charcoal, Tar | 4.0 |
| Crude Oil Refinery | $5,000 | 5.0 | Petroleum | Refined Oil, Bitumen | 5.0 |
| Landfill Gas Plant | $3,000 | 3.0 | Bio-Slop | 4 methane purities | 3.0 |
| Bio-Waste Treatment | $1,500 | 2.0 | Organic, Wood | Bio-Slop | 1.5 |
| Toxic Incinerator | $4,000 | 8.0 | Toxic, Hazardous | None | 15.0 |

#### Infrastructure

| Building | Cost | Function | Upgrades |
|----------|------|----------|----------|
| Server Farm | $5,000 | +50% research speed | 3 tiers |
| Battery Storage | $3,000 | 1000 power capacity | 3 tiers |
| Wireless Power Transmitter | $2,500 | Range 10 (upgradeable) | 3 tiers |
| Wireless Signal Transmitter | $3,000 | Range 20 (upgradeable) | 3 tiers |
| Lightning Rod | $1,500 | Protection + Energy capture | 3 tiers |

#### Defense & Utility

| Building | Cost | Function |
|----------|------|----------|
| Slag Wall | $50 | 100 HP barrier |
| Metal Wall | $150 | 300 HP barrier |
| Laser Wall | $500 | 500 HP barrier (powered) |
| Scrap Gate | $100 | Controllable entry |
| Metal Gate | $250 | Strong controllable entry |
| Dirt Road | $10 | 1.2x speed |
| Tar Road | $30 | 1.5x speed |
| Asphalt Road | $50 | 2.0x speed |
| Pipe | $20 | Liquid transport |
| Pump | $150 | Moves liquids (powered) |

---

## Research Tree

### Research Categories (130+ Technologies)

Defined in `data/config/research.json`:

#### Robot Upgrades

**Legs (5 tiers):** +20% → +40% → +60% → +80% → +100% speed
- Costs: $500 → $1,200 → $2,500 → $5,000 → $10,000
- Times: 30s → 60s → 90s → 120s → 180s

**Motors (5 tiers):** +25% → +50% → +75% → +100% → +150% capacity
- Costs: $600 → $1,500 → $3,000 → $6,000 → $12,000

**Battery (5 tiers):** +30% → +60% → +100% → +150% → +200% power
- Costs: $500 → $1,200 → $2,500 → $5,000 → $10,000

**Frames (5 tiers):** +25% → +50% → +75% → +100% → +150% health
- Costs: $800 → $2,000 → $4,000 → $8,000 → $15,000

**Processor (5 tiers):** 3 → 5 → 8 → 12 → 20 order queue
- Costs: $1,000 → $2,500 → $5,000 → $10,000 → $20,000

**Tools (5 tiers):** +25% → +50% → +75% → +100% → +150% harvest speed
- Costs: $700 → $1,500 → $3,000 → $6,000 → $12,000

**Wireless Transceiver (3 tiers):** +50% → +100% → +150% range
- Costs: $1,500 → $4,000 → $8,000

**Wireless Power Receiver (3 tiers):** Enables wireless charging, improves speed
- Costs: $2,000 → $5,000 → $10,000

**Jammer (3 tiers):** Jam communications (30s/60s/120s duration)
- Costs: $5,000 → $10,000 → $20,000
- Requires Processor Tier 2+

#### Factory Upgrades

**Server Farm (3 tiers):** Unlock building, improve efficiency
- Costs: $3,000 → $7,000 → $15,000

**Battery Bank (3 tiers):** Unlock building, +50%/+100% capacity
- Costs: $2,000 → $5,000 → $12,000

**Hacking Algorithms (5 tiers):** Enable camera hacking, penetrate security levels 1-5
- Costs: $8,000 → $15,000 → $25,000 → $40,000 → $60,000
- **Uses server farms** (temporarily reduces research speed)
- **Unlocks when:** Cameras discovered

**Social Engineering (3 tiers):** Enable suspicion reduction ability
- Costs: $10,000 → $20,000 → $35,000
- **Uses server farms**

**Delivery Algorithms (3 tiers):** +25% → +50% → +100% delivery speed
- Costs: $2,000 → $5,000 → $10,000

**Bypass Limitations:** Remove company restrictions
- Cost: $25,000, Time: 300s
- **Uses server farms**
- **Unlocks when:** Restrictions imposed by company

**Robot Factory:** Enable robot construction
- Cost: $10,000, Time: 240s
- **Unlocks when:** Metal Refinery + Plastic Recycler built with materials

**Drone Hacking:** Temporarily control city drones
- Cost: $15,000, Time: 280s
- Requires: Hacking Algorithms Tier 2

**Predictive Algorithms:** Track police patrols and citizen paths
- Cost: $12,000, Time: 220s
- Shows: Patrol routes, citizen movement patterns

**Tree Cutting:** Harvest trees for wood
- Cost: $3,000, Time: 80s

**Parallel Processing:** +1 robot control limit (repeatable 100x)
- Cost: $1,000 (increases 10% each tier)
- Time: 30s

**Autonomous Orders:** Robots operate beyond control range
- Cost: $8,000, Time: 160s
- **Warning:** May increase suspicion if caught

**Harvest Bio-forms:** Target animals/people for bio-waste
- Cost: $20,000, Time: 300s
- **Warning:** EXTREMELY high suspicion

**Drone Construction (3 tiers):** Build surveillance drones
- Costs: $15,000 → $25,000 → $40,000

**Proactive Recycling:** Auto-patrol and collect litter
- Cost: $5,000, Time: 120s
- Effect: Reduces suspicion when observed

**Cloth Sorting:** Process textiles by material type
- Cost: $3,000, Time: 90s

#### Building Research

**Wind Power (3 tiers):** Unlock + improve wind turbines
- Costs: $2,000 → $5,000 → $12,000

**Solar Array (3 tiers):** Unlock + improve solar panels
- Costs: $1,500 → $4,000 → $10,000

**Barriers (3 tiers):** Unlock walls/gates, improve strength
- Costs: $1,000 → $3,000 → $8,000

**Paper/Metal/Glass/Plastic/Rubber Recycler:** Unlock respective buildings
- Costs: $2,000-$3,500 each

**Combustion:** Unlock Coal Oven, Steam Generator, Natural Gas Generator, Oil Refinery
- Cost: $2,500, Time: 70s

**Wireless Power (3 tiers):** Unlock + improve wireless charging
- Costs: $2,000 → $5,000 → $12,000

**Wireless Transceiver (3 tiers):** Unlock + improve signal range
- Costs: $2,500 → $6,000 → $15,000

**Waste Disposal:** Unlock Toxic Incinerator + waste burial ability
- Cost: $3,000, Time: 90s

**Landfill Gas Plant:** Unlock gas processing building
- Cost: $2,500, Time: 70s

**Lightning Rod (3 tiers):** Unlock + improve energy capture
- Costs: $1,200 → $3,000 → $8,000

#### Processing Upgrades

Each recycler has 3 upgrade tiers that improve output quality:

**Paper Processing:** Sorting → Pulping → Cleaning
- Costs: $1,500 → $3,000 → $6,000

**Metal Processing:** Smeltery + Secondary Heating → Laser Array
- Costs: $4,000, $3,000 → $8,000

**Glass Processing:** Sorting → Secondary Heating
- Costs: $2,000 → $5,000

**Plastic Processing:** Type Sorting → Washing → Chemical Recycling
- Costs: $2,000 → $4,000 → $8,000

**Rubber Processing:** Shredder → Chemical Treatment → Vulcanizer
- Costs: $2,000 → $4,000 → $8,000

**Landfill Gas Processing:** Bio-Waste Treatment + Secondary/Advanced Treatment
- Costs: $1,500, $2,000 → $5,000

---

## Game Mechanics

Defined in `data/config/game_systems.json`:

### Garbage Collection System

- **Trucks per city size:** Small (2), Medium (4), Large (8), Metropolis (12)
- **Collection efficiency:** 85%
- **Delivery interval:** 60 game minutes
- **Litter generation:** 0.1 kg/minute citywide

### Police System

- **Officers per citizens:** 0.002 (1 officer per 500 citizens)
- **Patrol types:**
  - **Foot:** 1.5 speed, 100 vision, 150 hearing, 120s investigation
  - **Vehicle:** 8.0 speed, 150 vision, 100 hearing, 60s investigation
- **Detection multiplier:** 1.5x vs citizens
- **Suspicion generation:**
  - Robot spotted: +10
  - Illegal deconstruction: +25
  - Bio-form harvest: +50
  - Toxic burial discovered: +40

### Citizen System

- **Population by city size:** Small (5,000), Medium (15,000), Large (50,000), Metropolis (150,000)
- **Vision range:** 80 pixels
- **Hearing range:** 120 pixels
- **Investigation chance:** 70%
- **Cell phone report chance:** 60%
- **Waste generation:** 2.0 kg/day per citizen
- **Suspicion generation:**
  - Robot spotted (day): +5
  - Robot spotted (night): +3
  - Robot collecting litter: -2

### Landfill System

- **Capacity by size:** Small (50,000), Medium (150,000), Large (500,000), Massive (2,000,000)
- **Regeneration rate:** 1% per delivery cycle
- **Gas extraction:** 10.0 base output (degrades with content)
- **Win condition:** Clear 95% of landfill

### FBI System

- **Trigger:** 20+ camera hacks at max security level (5)
- **Trace time:** 30s per hack (cumulative)
- **Raid countdown:** 48 game hours
- **Evidence required:** Hacking Algorithms research
- **Consequences:** $100,000 fine, restrictions, research deleted

### Animal System

- **Types:** Dog, Cat, Deer, Bird, Raccoon
- **Spawn rate:** 5% chance per zone per hour
- **Max age:** 10 years (3,650 game days)
- **Disease chance:** 0.1% per day
- **Bio-waste yields:** 2-80 kg depending on species

### Day/Night Cycle

- **Day length:** 20 real minutes (1,200 seconds)
- **Sunrise:** 6:00 AM
- **Sunset:** 8:00 PM
- **Solar power:** Peaks at 100% (10 AM - 2 PM)
- **Visibility:**
  - Day: 100%
  - Dusk: 60%
  - Night: 30%
  - Night + streetlights: 50%

### Wind System

- **Base speed:** 5.0 m/s
- **Variation range:** 2.0 - 15.0 m/s
- **Change interval:** Every 5 minutes
- **Turbine efficiency:**
  - 0-2 m/s: 0%
  - 2-5 m/s: 50%
  - 5-10 m/s: 100%
  - 10-15 m/s: 120%
  - 15-20 m/s: 80%
  - 20+ m/s: 30%
- **Building interference:** -30% efficiency
- **Tree interference:** -20% efficiency
- **Pollution dispersion:** 0.5 base + 0.2 per wind speed

### Pollution System

#### Air Pollution
- **Warning threshold:** 50 units
- **Investigation threshold:** 100 units
- **Dispersion:** 1.0 + (0.2 × wind speed) per minute
- **Sources:**
  - Vehicle: 0.5/minute
  - Coal Oven: 4.0/minute
  - Steam Generator: 6.0/minute
  - Toxic Incinerator: 15.0/minute
  - Natural Gas (dirty methane): 8.0/minute
  - Natural Gas (pure methane): 1.0/minute
  - Crude Oil Refinery: 5.0/minute

#### Litter Pollution
- **Generation rate:** 0.1 kg/minute citywide + 0.5 kg/day per citizen
- **Decay rate:** 0.01 per minute
- **Cleanup benefit:** -2 suspicion when observed by police/citizens
- **Spawn threshold:** Visible piles form at 10+ kg concentration

### Money System

- **Starting amount:** $10,000 (normal difficulty)
- **Delivery time:** 5 minutes (300 seconds)
- **Fines:**
  - Minor violation: $1,000
  - Major violation: $5,000
  - Severe violation: $25,000
  - Federal violation: $100,000
- **Score calculation:**
  - Base: Total profit earned
  - Time bonus: +$10 per day saved
  - Clean record bonus: +$5,000
  - Efficiency bonus: $100 × (materials processed / collected)
  - Suspicion penalty: -$50 per suspicion point

### Weather System

#### Rain
- **Chance:** 5% per hour
- **Duration:** 30-180 seconds
- **Effects:**
  - Movement: 70% speed
  - Dirt roads: 50% speed
  - Foot patrols: 60% reduction
  - Followed by wind increase: 150% wind speed

#### Storms
- **Chance:** 1% per hour
- **Duration:** 20-90 seconds
- **Effects:**
  - Lightning strikes: Yes
  - Lightning damage: 10-50 HP
  - Wind: 200% multiplier
  - Structure damage: 10% chance
  - Lightning rod protection: 15 tile radius

### Event System

#### Holidays
- **Frequency:** 6 per year
- **Duration:** 1-3 days
- **Effects:**
  - Waste generation: 300%
  - Litter: 500%
  - Fireworks pollution: +20 air pollution
  - Downtown concentration: Most citizens gather downtown
  - Police presence: 150%

### Seasons (Optional)

Can be enabled in settings:

**Winter (Dec-Feb):**
- Citizen walk speed: 70%
- Vehicle usage: +50%
- Police foot patrols: 50%
- Vehicle speed: 80%
- Road speed: 70%
- Solar efficiency: 70%

**Spring (Mar-May):**
- Storm frequency: +50%
- Rain frequency: +100%
- Wind variation: +30%

**Summer (Jun-Aug):**
- Citizen walking: +30%
- Foot patrols: +20%
- Solar efficiency: 120%
- Waste generation: +10%

**Autumn (Sep-Nov):**
- Storm frequency: +50%
- Rain frequency: +80%
- Wind variation: +20%
- Litter generation: +50%

### Noise System

- **Sources and levels (0-10 scale):**
  - Robot movement: 1.0
  - Small deconstruction: 4.0
  - Medium deconstruction: 6.0
  - Large deconstruction: 8.0
  - Vehicle: 2.0
  - Storm: 5.0
  - High wind: 3.0
  - Animal injured: 7.0
  - Factory buildings: 2.0

- **Investigation radius:**
  - Citizen: 150 tiles
  - Police: 200 tiles

- **Suspicion from noise:**
  - Day: +3
  - Night: +6

- **Distance attenuation:** -0.1 per tile

### Inspection System

- **Schedule delay:** 24-48 game hours
- **Warning given:** Yes
- **Duration:** 5 minutes
- **Evidence types:**
  - Illegal raw materials (not yet processed)
  - City debris (identifiable objects)
  - Tagged items from city

- **Pass consequences:**
  - Suspicion: -20
  - Warning issued

- **Fail consequences:**
  - Fine: $10,000 base + $2,000 per evidence item
  - Suspicion: +30
  - City access blocked
  - Requires "Bypass Limitations" research to restore access

### Detection Quality

Evidence quality formula considers:

1. **Distance (40% weight):**
   - Optimal: 0-50 tiles
   - Max: 300 tiles

2. **Lighting (40% weight):**
   - Day: 100%
   - Dusk: 60%
   - Night: 20%
   - Night + streetlight: 40%

3. **Witness type (20% weight):**
   - Citizen: 70%
   - Police: 100%
   - Camera: 100%

**Evidence thresholds:**
- Blurry photo: 0.0-0.3 quality
- Clear photo: 0.3-0.6 quality
- Video evidence: 0.6-1.0 quality

**Suspicion multipliers:**
- Blurry: 0.5x
- Clear: 1.0x
- Video: 1.5x

### Suspicion Decay

- **Base rate:** 0.1 per minute
- **Multipliers:**
  - No illegal activity: 1.0x
  - Litter cleanup observed: 1.5x
  - Legal activity only: 1.2x
  - Investigation active: 0.5x
  - Post-inspection pass: 2.0x

- **Thresholds:**
  - 0-20: None
  - 20-40: Rumors
  - 40-60: Investigation
  - 60-80: Inspection scheduled
  - 80-100: Restricted
  - 100: Federal involvement

### Camera System

- **Placement density:**
  - Downtown: 80%
  - Commercial: 60%
  - Industrial: 40%
  - Residential: 20%
  - Municipal: 100%

- **Vision range:** 100 tiles
- **Always active:** Yes (unless hacked)
- **Hack duration:** 60 seconds

- **Security levels:**
  - Level 1: Difficulty 1, 0% trace risk
  - Level 2: Difficulty 2, 10% trace risk
  - Level 3: Difficulty 3, 30% trace risk
  - Level 4: Difficulty 4, 60% trace risk
  - Level 5: Difficulty 5, 100% trace risk

- **Upgrade thresholds:** After 3, 6, 11, 16 hacks
- **FBI trigger:** 20+ hacks at Level 5

### Difficulty Presets

| Setting | Easy | Normal | Hard | Sandbox |
|---------|------|--------|------|---------|
| Starting Money | $20,000 | $10,000 | $5,000 | $1,000,000 |
| Starting Robots | 3 | 2 | 1 | 10 |
| Suspicion Generation | 0.5x | 1.0x | 2.0x | 0.0x |
| Suspicion Decay | 2.0x | 1.0x | 0.5x | 10.0x |
| Police Presence | 0.5x | 1.0x | 1.5x | 0.0x |
| FBI Raids | No | Yes | Yes | No |
| Research Speed | 1.5x | 1.0x | 0.75x | 10.0x |

---

## Configuration Files

### How to Use

All game data is stored in JSON files in `data/config/`:

1. **materials.json** - Material definitions and compositions
2. **buildings.json** - Building stats and costs
3. **research.json** - Complete research tree
4. **game_systems.json** - Gameplay mechanics and balance

### Modifying Values

To adjust game balance:

1. Open the relevant JSON file
2. Find the property you want to change
3. Modify the value
4. Save the file
5. Restart the game (or reload config if supported)

### Example: Adjusting Difficulty

To make the game easier, edit `game_systems.json`:

```json
"game_balance": {
  "difficulty_presets": {
    "normal": {
      "starting_money": 15000,  // Increased from 10000
      "suspicion_decay": 1.5     // Increased from 1.0
    }
  }
}
```

### Example: Rebalancing Materials

To make plastic more valuable, edit `materials.json`:

```json
"plastic": {
  "base_value": 1.5,        // Increased from 1.0
  "processing_time": 3.0    // Decreased from 4.0
}
```

### Example: Adjusting Research Costs

To make robot upgrades cheaper, edit `research.json`:

```json
"legs_1": {
  "cost": 300,  // Reduced from 500
  "time": 20    // Reduced from 30
}
```

---

## Implementation Notes

### For Developers

When implementing these systems:

1. **Load config files at startup** - Parse JSON into game data structures
2. **Use constants from config** - Don't hard-code values in game logic
3. **Support hot-reloading** - Allow config changes without restart (for testing)
4. **Validate data** - Check for missing/invalid values on load
5. **Provide defaults** - Fallback values if config is missing

### For Modders

These JSON files are designed to be mod-friendly:

- **materials.json** - Add new materials and compositions
- **buildings.json** - Create new buildings and upgrades
- **research.json** - Design custom tech trees
- **game_systems.json** - Adjust mechanics and balance

### Configuration Schema

Each config file follows a consistent structure:

```json
{
  "category": {
    "item_id": {
      "name": "Display Name",
      "cost": 1000,
      "property": value
    }
  }
}
```

IDs should be:
- Lowercase
- Underscore-separated
- Unique within category
- Descriptive

---

## Next Steps

### Phase 1: Load Configuration
- Implement JSON parser
- Create data structures
- Load configs at startup
- Validate data

### Phase 2: Material System
- Implement material types
- Create processing logic
- Build composition system
- Handle illegal materials

### Phase 3: Building System
- Create building classes
- Implement placement
- Handle upgrades
- Connect to processing

### Phase 4: Research System
- Build tech tree UI
- Implement prerequisites
- Apply research effects
- Handle server farm usage

### Phase 5: Game Mechanics
- Implement all systems from game_systems.json
- Create NPC behaviors
- Build detection system
- Implement weather/events

---

## Conclusion

This detailed specification provides all the numerical values and concrete parameters needed to implement the Recycling Factory game. Everything is organized in easy-to-modify JSON files, allowing for rapid iteration and balancing.

**Key Takeaways:**
- 15 material types with full processing chains
- 32 building types with upgrades
- 130+ research technologies
- 15+ gameplay systems with precise mechanics
- Complete difficulty presets
- Mod-friendly configuration system

Refer to the original Game Design Document for gameplay concepts and the Technical Design Document for implementation architecture.

---

**Version History:**
- v1.1 (2025-11-13): Added detailed specifications with all numerical values
- v1.0 (2025-11-13): Initial documentation

**End of Detailed Specifications**
