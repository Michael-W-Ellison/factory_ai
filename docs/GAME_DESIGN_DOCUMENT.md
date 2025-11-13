# Recycling Factory - Game Design Document

**Version:** 1.0
**Last Updated:** 2025-11-13
**Project Type:** Top-down RTS Management Game

---

## Table of Contents
1. [Game Overview](#game-overview)
2. [Core Gameplay Loop](#core-gameplay-loop)
3. [Game Systems](#game-systems)
4. [Materials & Resources](#materials--resources)
5. [Robot Systems](#robot-systems)
6. [Factory Systems](#factory-systems)
7. [Research & Technology](#research--technology)
8. [City & Environment](#city--environment)
9. [Detection & Stealth](#detection--stealth)
10. [Authority Response System](#authority-response-system)
11. [Scoring & Win Conditions](#scoring--win-conditions)
12. [Settings & Customization](#settings--customization)
13. [User Interface](#user-interface)
14. [Future Features](#future-features)

---

## Game Overview

### High Concept
An AI-controlled automated recycling factory management game where players balance profit-making with avoiding detection while recycling materials from a landfill and potentially the nearby city.

### Genre
- Top-down RTS/Management Simulation
- Stealth/Strategy elements

### Target Audience
- Strategy game enthusiasts
- Management sim fans
- Players who enjoy morally ambiguous gameplay

### Visual Style
- 2D top-down perspective
- Pixel art or simple geometric graphics (similar to "Songs of Syx")
- Minimalist UI with functional information displays

### Core Tension
**Greed vs. Safety:** Players must decide between maximizing profit (by recycling city infrastructure) and maintaining safety (staying legal in the landfill).

---

## Core Gameplay Loop

```
1. COLLECT: Robots gather materials from landfill/city
   ↓
2. PROCESS: Factory refines materials into valuable components
   ↓
3. SELL: Components delivered to warehouse for profit
   ↓
4. UPGRADE: Invest profits in research/robots/factory expansion
   ↓
5. EXPAND: Unlock new capabilities and collection options
   ↓
(Loop continues until win/loss condition)
```

---

## Game Systems

### 1. Material Collection System
- **Collection Zones:** Player-defined areas where robots search for materials
- **Object Tagging:** Manual selection of specific items for recycling
- **Priority System:** Numbered priorities determine collection order
- **Time Restrictions:** Set allowed collection times per zone (e.g., city at night only)
- **Robot Assignment:** Assign specific robots to specific zones

### 2. Material Processing System
- **Refinement Queue:** Materials wait for processing at factory
- **Processing Speed:** Determined by factory upgrades
- **Component Extraction:** Different materials yield different components
- **Power Requirements:** Processing consumes electricity
- **Storage Limits:** Warehouses have capacity limits

### 3. Economic System
- **Component Pricing:** Market values for different materials
- **Profit Tracking:** Running total of income
- **Costs:** Robot maintenance, power generation, disposal fees
- **Fines:** Penalties for illegal activity
- **Score Calculation:** Final score based on total profit

### 4. Power System
- **Power Generation Sources:**
  - Initial: Grid connection (paid)
  - Biogas: From bio-slop processing
  - Wood burning: Generates pollution
  - Solar panels: Clean but expensive
  - Liquid fuel burning: Petroleum/oil/alcohol

- **Power Storage:** Battery capacity determines operational reserves
- **Power Consumption:** Robots, factory operations, research

### 5. Research System
- **Computation Requirements:** Research speed tied to processing power
- **Tech Tree:** Hierarchical unlock system
- **Robot Upgrades:** Apply research to existing robots
- **Facility Prerequisites:** Some tech requires upgraded facilities

---

## Materials & Resources

### Material Types

| Material | Legal Source | Value | Special Properties |
|----------|-------------|-------|-------------------|
| **Plastic** | Landfill | Low-Medium | Common, lightweight |
| **Glass** | Landfill/City | Low | Fragile, recyclable |
| **Common Metals** | Landfill/City | Medium | Iron, aluminum, copper |
| **Precious Metals** | Landfill/City | High | Gold, silver, rare |
| **Rubber** | Landfill | Low | Tires, various products |
| **Bio-slop** | Landfill | Negative* | *Converts to biogas (positive value) |
| **Wood** | Landfill/City | Low | Burns for power, creates pollution |
| **Liquids** | Landfill | Medium-High | Petroleum, alcohol, oil - fuel or sell |
| **Toxic Materials** | Landfill | Negative | Disposal cost if legal, huge fine if caught illegally dumping |
| **Electronics** | Landfill/City | High | Contains precious metals, complex processing |
| **Concrete** | City only | Low | Heavy, infrastructure |
| **Wire/Cable** | City only | Medium | Copper content, infrastructure |

### Illegal vs. Legal Materials
- **Legal:** Materials from the landfill
- **Illegal (raw form):** Materials from city (vehicles, houses, infrastructure)
- **Evidence Elimination:** Process illegal materials into raw components before inspections

---

## Robot Systems

### Robot Stats
- **Speed:** Movement rate
- **Collection Capacity:** How much material can be carried
- **Power Storage:** Battery capacity (determines operational time)
- **Processing Speed:** How fast they can break down objects
- **Durability:** Resistance to wear and tear
- **Stealth:** How easily detected (later upgrade)

### Robot Lifecycle
1. **Production:** Built at factory (costs resources + time)
2. **Deployment:** Assigned to collection zones
3. **Operation:** Collect materials autonomously
4. **Maintenance:** Requires periodic servicing (costs + downtime)
5. **Upgrade:** Apply research improvements
6. **Repair:** Damage requires resources to fix

### Advanced Robot Capabilities (Unlockable)
- **Construction:** Install solar panels, generators, batteries
- **Combat:** Defend against destruction (late-game, extreme scenarios)
- **Hacking:** Disable cameras remotely
- **Advanced Stealth:** Reduced detection radius

### Robot Behaviors
- Follow zone priorities
- Return to factory when full or low on power
- Avoid detection (if stealth systems researched)
- Coordinate with other robots (advanced research)

---

## Factory Systems

### Core Factory Components
1. **Robot Assembly Bay:** Produces new robots
2. **Material Processing Facility:** Refines raw materials
3. **Power Generation:** Energy production buildings
4. **Power Storage:** Battery banks
5. **Computation Core:** Enables research
6. **Warehouse:** Stores processed components
7. **Loading Bay:** Ships components to city for sale

### Factory Upgrades
- **Processing Speed:** Faster refinement
- **Production Capacity:** Build multiple robots simultaneously
- **Advanced Processing:** Handle complex materials (electronics, toxic waste)
- **Efficiency:** Reduced power consumption
- **Automation:** Reduced player micromanagement needed

### Expansion Mechanics
- Purchase upgrades with profits
- Some upgrades require research first
- Physical expansion increases factory footprint
- Higher tier facilities unlock new capabilities

---

## Research & Technology

### Research Categories

#### 1. Robot Improvements
- Speed Enhancement (Levels 1-5)
- Capacity Increase (Levels 1-5)
- Power Efficiency (Levels 1-5)
- Advanced Sensors (Unlocks better pathfinding)
- Stealth Systems (Reduces detection range)
- Construction Capabilities (Build structures)

#### 2. Processing Technology
- Material Extraction Efficiency (Get more from same material)
- Advanced Refinement (Unlock complex materials)
- Multi-Material Processing (Process multiple types simultaneously)
- Recycling Optimization (Reduce waste)

#### 3. Power Technology
- Solar Panel Installation
- Biogas Generator
- Battery Technology (Increased storage)
- Fusion Research (Late-game, very expensive)
- Grid Hacking (Steal power - risky)

#### 4. Stealth & Security
- Camera Hacking (Basic)
- Advanced Encryption (Harder to trace)
- Signal Jamming (Temporary detection immunity)
- Counter-Surveillance (Detect police investigations early)

#### 5. City Intelligence
- Patrol Pattern Recognition (Shows police routes)
- Citizen Behavior Analysis (Predict NPC movements)
- Infrastructure Mapping (Identifies valuable targets)

### Research Mechanics
- Costs: Time + Computation Power + Sometimes Resources
- Prerequisites: Tech tree with dependencies
- Instant Apply: Upgrades affect all existing robots/facilities
- Re-research: If knowledge deleted (FBI scenario), must research again

---

## City & Environment

### City Zones
1. **Residential:** Houses (various states), vehicles, fences
2. **Commercial:** Stores, parking lots, infrastructure
3. **Industrial:** Warehouses, factories (ironic competition)
4. **Infrastructure:** Roads, lights, traffic signals, power lines
5. **Municipal:** Police station, city hall (high security)

### City Objects & Legality

| Object Type | Legal? | Value | Detection Risk |
|-------------|--------|-------|----------------|
| Abandoned vehicles | Grey area | Medium | Low-Medium |
| Decrepit houses | Grey area | High | Medium |
| Houses under construction | Illegal | High | Medium-High |
| Occupied houses | Illegal | Very High | Very High |
| Empty houses | Illegal | High | Medium |
| Metal fences | Illegal | Low | Low-Medium |
| Light poles | Illegal | Medium | High (public) |
| Traffic lights | Illegal | Medium | Very High |
| Power lines | Illegal | High | Very High |
| Parked vehicles | Illegal | Medium-High | High |
| Moving vehicles | Illegal | High | Extreme |

### Environmental Factors
- **Time of Day:** Day/Night cycle affects visibility and NPC behavior
- **Weather:** (Optional) Rain reduces visibility, helps stealth
- **Lighting:** Streetlights, building lights affect detection
- **Noise Propagation:** Louder operations attract attention

### NPC Behavior
- **Daily Routines:** Citizens follow schedules (work, home, shopping)
- **Sleep Cycles:** Most citizens indoors at night
- **Investigation:** NPCs attracted to noise from robot operations
- **Recording:** Can capture evidence on cell phones in good lighting

---

## Detection & Stealth

### Detection Factors
1. **Visual Range:** Based on lighting conditions
   - Daylight: Maximum visibility
   - Dusk/Dawn: Medium visibility
   - Night + Streetlights: Medium visibility
   - Night + No lights: Minimum visibility

2. **Noise Range:** Operations generate sound radius
   - Large objects: Larger noise radius
   - Multiple robots: Increased noise
   - Stealth upgrades: Reduce noise

3. **Evidence Quality:** Determines suspicion generated
   - Daylight + Clear sight = Phone video (high suspicion)
   - Night + Poor lighting = Blurry photo (low suspicion)
   - Sound only = Minimal suspicion

### Detection Levels
- **Undetected:** No one aware of activity
- **Rumored:** Citizens spotted something, spreading rumors
- **Investigated:** Police aware, beginning surveillance
- **Confirmed:** Police have evidence, inspection scheduled
- **Restricted:** Company restricted from city operations
- **Federal:** FBI involved, tracing activities

### Suspicion Mechanics
- **Suspicion Meter:** 0-100 scale
- **Generation:** Illegal activity witnessed increases suspicion
- **Decay:** Suspicion slowly decreases over time if no new incidents
- **Thresholds:**
  - 0-20: No action
  - 21-40: Increased police patrols
  - 41-60: Police investigation begins
  - 61-80: Factory inspection scheduled
  - 81-100: Severe restrictions/potential shutdown

### Surveillance Systems
1. **Security Cameras:**
   - Fixed positions in important areas
   - Can be hacked temporarily
   - Upgrade after repeated hacks
   - Maximum 5 security levels

2. **Police Patrols:**
   - Vehicle patrols (predictable routes)
   - Foot patrols (less predictable)
   - Increase frequency with higher suspicion

3. **Witness Reports:**
   - Individual citizens can report sightings
   - Report quality affects suspicion increase
   - Repeated reports from same area increase police presence

---

## Authority Response System

### Escalation Tiers

#### Tier 0: Normal Operations
- No suspicion
- Normal police presence
- No restrictions

#### Tier 1: Rumors (Suspicion 21-40)
- Citizens talking about strange sightings
- Slight increase in police patrols
- No direct consequences
- Suspicion decays over time

#### Tier 2: Investigation (Suspicion 41-60)
- Police actively investigating reports
- Increased patrols in affected areas
- Patrol patterns become less predictable
- Suspicion decay slowed

#### Tier 3: Factory Inspection (Suspicion 61-80)
- Inspection scheduled (countdown timer)
- Must clear factory of illegal materials
- If passed: Suspicion reduced, warning issued
- If failed: Fine issued, move to Tier 4

#### Tier 4: Restrictions (After failed inspection)
- Company barred from city operations
- Robots cannot enter city zones
- Requires research to circumvent:
  - "Stealth Override" technology
  - "Corporate Restructuring" (resets legal status, expensive)
- Can still operate in landfill

#### Tier 5: Federal Investigation (After extreme violations)
- FBI involved
- Camera hacking triggers trace countdown
- If trace completes: Game Over countdown begins
- Options:
  - Delete hacking research (prevents trace, loses capability)
  - Stop hacking (safe but limited options)
  - Risk it (continue operations, might trigger game over)

### Inspection Mechanics
- **Warning Time:** 24-48 in-game hours
- **Inspection Process:** Agents check factory for illegal materials
- **Evidence:** Raw materials from city objects (not yet processed)
- **Passing:** All illegal materials processed into generic components
- **Failing:** Illegal materials found
  - Fine proportional to amount found
  - Suspicion increases
  - Advancement to next tier

### Camera Hacking Consequences
- **1-2 hacks:** No response
- **3-5 hacks:** Security upgrade (Level 2)
- **6-10 hacks:** Security upgrade (Level 3)
- **11-15 hacks:** Security upgrade (Level 4)
- **16-20 hacks:** Security upgrade (Level 5 - Maximum)
- **21+ hacks (at max security):** FBI trace begins

### FBI Trace Mechanics
- **Trigger:** Hacking cameras while at maximum security
- **Trace Timer:** Increases with each hack (cumulative)
- **Warning:** UI indicator shows trace progress
- **Completion:** Triggers 48-hour raid countdown
- **Raid Result:** Game Over (Factory shut down)
- **Prevention:** Delete hacking research OR stop hacking

---

## Scoring & Win Conditions

### Win Conditions
1. **Landfill Completion:** (Primary Win)
   - Clean entire landfill
   - Final score based on total profit
   - Bonuses for:
     - Time to completion
     - Low suspicion level
     - No violations

2. **Profit Target:** (Optional Win - if enabled in settings)
   - Reach specific profit threshold
   - Can be set in game settings

### Loss Conditions
1. **FBI Raid:** Factory shut down by federal agents
2. **Bankruptcy:** (Optional - if enabled) Run out of money
3. **Authority Shutdown:** Multiple severe violations

### Score Calculation
```
Base Score = Total Profit Earned

Multipliers:
+ Time Bonus (faster completion = higher bonus)
+ Clean Record Bonus (no violations)
+ Efficiency Bonus (materials processed / materials collected)

Penalties:
- Fines paid
- Suspicion level at end
- Illegal materials improperly disposed

Final Score = Base Score × Multipliers - Penalties
```

### Leaderboard Categories
- Highest Profit
- Fastest Completion
- Cleanest Record (no illegal activity)
- Most Daring (highest profit with highest risk)

---

## Settings & Customization

### Gameplay Settings
- **Landfill Size:** Small / Medium / Large / Massive
- **Landfill Richness:** Low / Medium / High / Extreme
- **City Size:** Small Town / Medium City / Large City / Metropolis
- **Suspicion Generation Rate:** 0.5x to 5x multiplier
- **Suspicion Decay Rate:** 0.5x to 5x multiplier
- **Police Presence:** None / Low / Medium / High / Extreme
- **FBI Raids:** Enabled / Disabled
- **Game End on Landfill Empty:** Enabled / Disabled

### Starting Conditions
- **Starting Robots:** 1-10
- **Starting Money:** $1,000 - $100,000
- **Starting Tech Level:** None / Basic / Advanced
- **Starting Factory Level:** Basic / Intermediate / Advanced

### Difficulty Presets
- **Easy Mode:**
  - Large starting budget
  - Low suspicion generation
  - Fast suspicion decay
  - No FBI raids
  - 3 starting robots

- **Normal Mode:**
  - Balanced settings
  - Standard suspicion mechanics
  - FBI raids enabled
  - 2 starting robots

- **Hard Mode:**
  - Limited starting budget
  - High suspicion generation
  - Slow suspicion decay
  - Aggressive FBI response
  - 1 starting robot

- **Sandbox Mode:**
  - Unlimited money (optional)
  - No suspicion (optional)
  - All research unlocked (optional)
  - Experiment freely

### Research Speed
- 0.25x to 10x multiplier

### Power Generation Rate
- 0.5x to 5x multiplier

### Robot Starting Stats
- Individual sliders for each stat (Speed, Capacity, Power, etc.)

---

## User Interface

### Main Screen Elements
1. **Game View:** Top-down view of factory and surrounding area
2. **Minimap:** Overview of entire game area
3. **Resource Display:** Current materials and components
4. **Power Meter:** Current power generation/consumption
5. **Money Counter:** Current funds
6. **Suspicion Meter:** Current suspicion level with visual warnings
7. **Time Display:** In-game time and date
8. **Robot Status Panel:** List of all robots with status icons

### Control Panels

#### Factory Management
- Building placement/upgrade interface
- Production queue for robots
- Power management (activate/deactivate generators)
- Research selection

#### Robot Management
- Robot list with individual stats
- Zone assignment interface
- Priority settings
- Time restriction settings
- Upgrade application

#### Collection Management
- Zone drawing tool
- Object tagging (click to mark for collection)
- Priority number assignment
- Time restriction editor

#### Map View
- Toggle layers:
  - Terrain
  - Buildings
  - Patrol routes
  - Surveillance cameras
  - Detection ranges
  - Suspicion zones

### Notification System
- **Critical Alerts:** Inspection scheduled, FBI raid, robot destroyed
- **Warnings:** High suspicion, power low, material storage full
- **Info:** Research complete, robot finished, shipment sold

### Tooltips
- Hover over objects for information
- Material values
- Object detection risk
- NPC information

---

## Future Features

### Multiplayer (Competitive)
- Two players compete for highest profit
- Shared city (actions affect both players' suspicion)
- Separate landfills
- Race to profit target or time limit

### Additional Game Modes
- **Story Mode:** Campaign with objectives and narrative
- **Endless Mode:** Infinite landfill, score attack
- **Challenge Mode:** Specific scenarios with unique constraints

### Advanced Features
- **Black Market:** Sell illegal materials directly (higher risk/reward)
- **Corporate Espionage:** Sabotage competing recycling companies
- **Natural Disasters:** Events that create opportunity (more debris) or danger
- **Technology Market:** Buy/sell research with other AI companies
- **Drone Technology:** Aerial robots with different capabilities
- **Underground Expansion:** Hidden factory sections to hide illegal operations

### Quality of Life
- **Auto-save:** Periodic automatic saves
- **Quick-save:** Manual save at any time
- **Speed Controls:** Pause, 1x, 2x, 5x, 10x game speed
- **Camera Controls:** Zoom, pan, rotate
- **Hotkeys:** Customizable keyboard shortcuts
- **Templates:** Save zone configurations for reuse

---

## Design Philosophy

### Core Principles
1. **Player Agency:** Players make meaningful choices with consequences
2. **Risk/Reward Balance:** Higher profits come with higher danger
3. **Emergent Gameplay:** Systems interact to create unique situations
4. **Accessibility:** Easy to learn, difficult to master
5. **Replayability:** Different strategies viable, settings customizable

### Tone
- Darkly humorous
- Morally ambiguous (you're the "bad guy" but in a sympathetic way)
- Tense when operating illegally
- Satisfying when systems work efficiently

---

**End of Game Design Document**
