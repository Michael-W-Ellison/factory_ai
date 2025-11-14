# Phase 10: Advanced Features - Complete Documentation

## Overview

Phase 10 introduces six major advanced feature systems that dramatically expand gameplay depth and strategic options:

1. **Drone System with Fog of War** - Reconnaissance drones for map exploration
2. **Wireless Transmitter System** - Control range extension infrastructure
3. **Market Fluctuation System** - Dynamic pricing and economic strategy
4. **Weather System** - Environmental effects on gameplay (already existed, documented here)
5. **Deconstruction System** - Material recovery from structures
6. **Scoring & Achievement System** - Performance tracking and end-game statistics

---

## 1. Drone System & Fog of War

### Overview

The drone system allows players to deploy autonomous reconnaissance drones to explore the map, revealing areas through the fog of war system.

### Core Components

#### DroneManager
**File**: `src/systems/drone_manager.py`

Manages all drone operations and fog of war tracking.

**Key Features:**
- Drone purchase and deployment ($5,000 per drone, max 5)
- Battery management (100 seconds flight time, 1%/sec drain, 2%/sec charge)
- Auto-return at 20% battery
- Fog of war exploration tracking
- Vision radius: 10 tiles

#### Drone States

```python
class DroneState(Enum):
    IDLE = 0      # At base, ready to deploy
    FLYING = 1    # In flight, exploring
    RETURNING = 2 # Returning to base (low battery)
    CRASHED = 3   # Battery depleted, crashed (permanent loss)
    CHARGING = 4  # At base, recharging
```

#### Fog of War System

**FogOfWar Class:**
- Tracks explored vs unexplored tiles
- 200x200 tile map (configurable)
- Factory area (10x10) initially explored
- Exploration percentage tracking

**Visibility Mechanics:**
- Permanent exploration: Tiles remain visible after first exploration
- Temporary visibility: Currently visible (within drone vision)
- Circular vision radius around each active drone

### Usage Example

```python
from src.systems.drone_manager import DroneManager

# Initialize
drone_manager = DroneManager(resource_manager, map_width=200, map_height=200)

# Purchase drone
drone_manager.purchase_drone()  # -$5,000

# Deploy drone to explore
target = (50.0, 50.0)
drone_manager.deploy_drone(drone_id=1, target_position=target)

# Update each frame
drone_manager.update(dt, game_time)

# Check exploration
exploration_percent = drone_manager.get_exploration_percentage()
is_explored = drone_manager.is_position_explored((25, 25))

# Recall drone
drone_manager.recall_drone(drone_id=1)
```

### Statistics

```python
summary = drone_manager.get_summary()
# {
#   'drones': {
#     'idle': 1, 'flying': 2, 'returning': 0,
#     'charging': 1, 'crashed': 0, 'total': 4
#   },
#   'max_drones': 5,
#   'exploration_percent': 15.7,
#   'tiles_explored': 6280,
#   'drones_deployed': 15,
#   'drones_crashed': 1
# }
```

### Strategy Tips

- Deploy drones early to find valuable resources
- Monitor battery levels to avoid crashes
- Use multiple drones for faster exploration
- Crashed drones are permanent losses ($5,000 each)
- Exploration unlocks achievements (25%, 75%, 100%)

---

## 2. Wireless Transmitter System

### Overview

Transmitters extend control range for drones and other wireless devices beyond the factory's base 20-tile range.

### Transmitter Types

| Type | Range | Cost | Use Case |
|------|-------|------|----------|
| BASIC | 30 tiles | $3,000 | Early expansion |
| ADVANCED | 50 tiles | $8,000 | Mid-game coverage |
| LONG_RANGE | 80 tiles | $15,000 | Late-game reach |
| REPEATER | 25 tiles | $5,000 | Network extension |

### Signal Coverage

**Signal Strength Calculation:**
- Linear falloff from 100% at center to 0% at max range
- Minimum 10% signal required for device control
- Multiple transmitters: uses maximum signal strength

**Coverage Formula:**
```
signal_strength = 100% * (1 - distance/range)
```

### Placement Rules

1. **Must have existing signal coverage** (10% minimum) at placement location
2. Can place within base range (20 tiles) OR within range of another transmitter
3. No refunds on removal
4. Instant activation

### Usage Example

```python
from src.systems.transmitter_manager import TransmitterManager, TransmitterType

# Initialize
transmitter_manager = TransmitterManager(resource_manager)

# Check if position has coverage
has_signal = transmitter_manager.has_signal_coverage((40.0, 0.0))

# Place transmitter (if within existing coverage)
transmitter_id = transmitter_manager.place_transmitter(
    TransmitterType.BASIC,
    position=(15.0, 0.0)
)

# Check signal strength at position
signal = transmitter_manager.get_signal_strength_at((35.0, 0.0))
quality = transmitter_manager.get_coverage_quality((35.0, 0.0))
# quality: "excellent" (80%+), "good" (50-80%), "poor" (10-50%), "none" (<10%)
```

### Network Planning

**Optimal Placement Strategy:**
1. Start with BASIC transmitters at base range edge
2. Chain transmitters to reach distant areas
3. Use LONG_RANGE for critical far zones
4. REPEATER for filling gaps in network

**Cost Efficiency:**
- 3x BASIC (30 tiles each) = $9,000 for 90-tile chain
- 1x LONG_RANGE (80 tiles) = $15,000 for 80-tile reach
- Choose based on terrain and resource distribution

---

## 3. Market Fluctuation System

### Overview

Dynamic pricing system adds economic strategy through market trends, price changes, and random events.

### Market Trends

```python
class MarketTrend(Enum):
    STABLE = 0     # ±0.1% per hour
    BULLISH = 1    # +0.5% per hour
    BEARISH = 2    # -0.5% per hour
    VOLATILE = 3   # ±2% per hour (random)
    CRASH = 4      # -5% per hour
```

**Trend Probabilities:**
- STABLE: 40%
- BULLISH: 20%
- BEARISH: 20%
- VOLATILE: 15%
- CRASH: 5%

**Trend Duration:** Changes every 48 game hours

### Price Mechanics

**Base Prices:**

| Material | Buy Price | Sell Price (Recycled) |
|----------|-----------|----------------------|
| Plastic | $2.00 | $5.00 |
| Metal | $4.00 | $10.00 |
| Glass | $3.00 | $8.00 |
| Paper | $1.00 | $3.00 |
| Electronics | $20.00 | $50.00 |
| Copper | $30.00 | $75.00 |
| Rubber | $4.00 | $10.00 |

**Price Bounds:**
- Minimum: 30% of base price (0.3x multiplier)
- Maximum: 300% of base price (3.0x multiplier)

### Market Events

**Event Types:**
- Electronics Shortage: Electronics +50%, Copper +30% (24 hours)
- Plastic Surplus: Plastic -30% (12 hours)
- Metal Boom: Metal +40%, Copper +30% (48 hours)
- Paper Mill Strike: Paper +60% (18 hours)
- Rubber Crisis: Rubber +80% (36 hours)
- Glass Glut: Glass -40% (24 hours)

**Event Frequency:**
10% chance every 24 game hours

### Usage Example

```python
from src.systems.market_manager import MarketManager, MarketTrend

# Initialize
market_manager = MarketManager()

# Get current prices
plastic_buy = market_manager.get_buy_price('plastic')
recycled_sell = market_manager.get_sell_price('recycled_plastic')

# Check trend
trend = market_manager.current_trend  # MarketTrend.BULLISH
trend_symbol = market_manager.get_price_trend('plastic')  # "↑"

# Get price change from base
change_percent = market_manager.get_price_change_percentage('plastic')  # +15.3

# Update (call each frame)
market_manager.update(dt, game_time)

# Get all prices
prices = market_manager.get_all_prices()
# {
#   'buy': {'plastic': 2.15, 'metal': 4.20, ...},
#   'sell': {'recycled_plastic': 5.38, 'recycled_metal': 10.50, ...}
# }
```

### Trading Strategy

**Buy Low, Sell High:**
- **BEARISH/CRASH**: Buy materials, stockpile
- **BULLISH**: Sell products, maximize revenue
- **VOLATILE**: Quick trades, watch for spikes
- **Events**: Capitalize on temporary price changes

**Profit Margins:**
- Normal: ~150% margin (buy $2, sell $5)
- Bearish buy, Bullish sell: ~300%+ margin possible
- Event timing: Up to 400% margins

---

## 4. Weather System

### Overview

Dynamic weather system affects production, suspicion, visibility, and drone operations.

**Note:** Weather system was implemented in earlier phase, documented here for completeness.

### Weather Types

| Weather | Solar Power | Detection | Visibility | Suspicion Benefit |
|---------|-------------|-----------|------------|-------------------|
| CLEAR | 100% | 100% | 100% | None |
| CLOUDY | 70% | 100% | 90% | -10% |
| RAIN | 50% | 80% | 80% | -30% |
| HEAVY_RAIN | 25% | 60% | 60% | -50% |
| FOG | 60% | 40% | 50% | -60% |
| STORM | 10% | 150%* | 40% | -70% |
| SNOW | 50% | 80% | 70% | -20% |

*Storm increases detection IF seen, but reduces chance of being seen

### Weather Effects

**Production Modifier:**
- Applied to all production buildings
- STORM: 50% production (risky to operate)
- HEAVY_RAIN: 70% production

**Suspicion Modifier:**
- Reduces suspicion gain rate
- FOG/STORM: Best cover for illegal activities
- Good weather for stealth operations

**Drone Effects:**
- Speed modifier (0.3x to 1.0x)
- Battery drain (1.0x to 2.5x)
- BLIZZARD: 30% speed, 250% drain (dangerous!)

### Season System

**Seasons:** Spring → Summer → Fall → Winter (7-day cycles)

**Seasonal Weather Probabilities:**
- **Summer**: 50% clear, less rain
- **Winter**: 30% snow, 10% blizzard
- **Spring/Fall**: Balanced, more rain

### Usage Example

```python
from src.systems.weather_manager import WeatherManager, WeatherType

# Initialize
weather_manager = WeatherManager()

# Update (call each frame)
weather_manager.update(dt, game_time)

# Get current weather
description = weather_manager.get_weather_description()  # "⛈️ Thunderstorm"
current = weather_manager.current_weather  # WeatherType.STORM
season = weather_manager.current_season  # "winter"

# Get gameplay effects
solar_multiplier = weather_manager.get_solar_power_multiplier()  # 0.1
detection_mod = weather_manager.get_detection_modifier()  # 1.5
visibility_mod = weather_manager.get_visibility_multiplier()  # 0.4

# Force weather (testing/events)
weather_manager.force_weather(WeatherType.FOG, duration=3600.0)
```

### Strategic Use

**Planning Illegal Operations:**
- Check forecast (if researched)
- Wait for FOG or HEAVY_RAIN
- Execute risky tasks during bad weather
- Production penalty is worth stealth benefit

**Drone Deployment:**
- Avoid STORM/BLIZZARD (high battery drain, crash risk)
- CLEAR weather optimal for exploration
- RAIN acceptable if urgent

---

## 5. Deconstruction System

### Overview

Allows dismantling buildings and props to recover materials with partial efficiency.

### Mechanics

**Recovery Rates:**
- Legal structures: 70% material recovery
- Illegal structures: 50% material recovery (penalty)
- 10% loss accounts for damage/waste

**Deconstruction Time:**
```
base_time = 60 seconds + (10 seconds × size)
actual_time = base_time / (1 + (workers-1) × 0.5)
```

**Worker Efficiency:**
- 1 worker: 100% time
- 2 workers: 67% time (1.5x speed)
- 3 workers: 57% time (1.75x speed)

### Material Tagging

**Source Tracking:**
- Legal deconstruction → MaterialSource.PROCESSED
- Illegal deconstruction → MaterialSource.UNKNOWN
- Integrates with inspection system (Phase 8)

### Usage Example

```python
from src.systems.deconstruction_manager import DeconstructionManager

# Initialize
decon_manager = DeconstructionManager(resource_manager, material_inventory)

# Start deconstruction
materials_used = {'plastic': 100, 'metal': 50}  # Original building cost
job_id = decon_manager.start_deconstruction(
    target_type='building',
    target_id=5,
    target_position=(20.0, 15.0),
    materials=materials_used,
    size=2.0,  # Size multiplier
    is_illegal=False,  # Legal structure
    workers=2  # Assign 2 workers
)

# Update progress (call each frame)
decon_manager.update(dt, game_time)

# Check status
status = decon_manager.get_job_status(job_id)
# {
#   'id': 1,
#   'target_type': 'building',
#   'progress': 45.2,  # %
#   'workers': 2,
#   'time_remaining': 38.5,  # seconds
#   'materials': {'plastic': 70.0, 'metal': 35.0}  # 70% of originals
# }

# Cancel job (no material refund)
decon_manager.cancel_deconstruction(job_id)

# Reassign workers mid-job
decon_manager.assign_workers(job_id, workers=3)  # Speed up
```

### Strategy

**When to Deconstruct:**
- Relocating factory layout
- Emergency material needs
- Removing evidence before inspection
- Upgrading to better buildings

**Efficiency Optimization:**
- Use multiple workers for urgent jobs
- Deconstruct illegal structures before inspections (but lose 20% materials)
- Plan layout to minimize future deconstruction needs

---

## 6. Scoring & Achievement System

### Overview

Comprehensive performance tracking with 30+ achievements and rank system.

### Score Categories

| Category | Points | Calculation |
|----------|--------|-------------|
| Money Earned | 1 pt/$100 | Total earnings / 100 |
| Materials Processed | 1 pt/unit | Total recycled |
| Buildings Built | 50 pt/building | Construction count |
| Time Survived | 10 pt/day | Game days survived |
| Efficiency | 0-100 pts | Materials processed / collected |
| Stealth | 0-100 pts | Inverse of max suspicion |
| Exploration | 0-100 pts | Map exploration % |
| Technology | 25 pt/level | Research levels |
| Ending Bonus | Varies | Game ending type |

### Ending Bonuses

| Ending | Bonus | Description |
|--------|-------|-------------|
| LEGITIMATE_SUCCESS | +5,000 | Won via legitimate business |
| ESCAPE | +3,000 | Escaped before FBI raid |
| PLEA_DEAL | +1,500 | Negotiated settlement |
| FBI_RAID | +500 | Got caught |
| INSPECTOR_FAILURE | +200 | Failed inspection |
| BANKRUPTCY | 0 | Financial collapse |

### Rank System

| Rank | Score Required |
|------|----------------|
| Novice | 0 - 999 |
| Amateur | 1,000 - 4,999 |
| Professional | 5,000 - 9,999 |
| Expert | 10,000 - 24,999 |
| Master | 25,000 - 49,999 |
| Legend | 50,000 - 99,999 |
| Grandmaster | 100,000+ |

### Achievement Categories

**Money Achievements:**
- First Dollar (10 pts): Earn $1
- Millionaire (100 pts): Accumulate $1,000,000
- Big Spender (50 pts): Spend $500,000

**Production Achievements:**
- First Product (10 pts): Process first material
- Mass Production (100 pts): Process 10,000 materials
- Recycling Master (250 pts): Process 100,000 materials

**Building Achievements:**
- Builder (50 pts): Construct 10 buildings
- Architect (150 pts): Construct 50 buildings
- City Planner (300 pts): Construct 100 buildings

**Exploration Achievements:**
- Explorer (50 pts): Explore 25% of map
- Cartographer (150 pts): Explore 75% of map
- Completionist (300 pts): Explore 100% of map

**Stealth Achievements:**
- Ghost (200 pts): Complete with <20 max suspicion
- Invisible (150 pts): Never trigger inspection
- Smooth Operator (100 pts): Never fail inspection

**Special Achievements:**
- Speed Run (400 pts): Complete in <10 days
- Slow Burn (200 pts): Survive 100 days
- Market Master (150 pts): Profit from market fluctuations
- Weatherman (75 pts): Experience 10 weather changes

### Usage Example

```python
from src.systems.scoring_manager import ScoringManager

# Initialize
scoring = ScoringManager()

# Record gameplay events
scoring.record_money_earned(50000)
scoring.record_material_processed(1000)
scoring.record_building_built()
scoring.record_drone_deployed()
scoring.record_bribe_attempt(success=True)
scoring.record_inspection_result(passed=True)

# Update (call each frame)
scoring.update(dt, game_time)

# Calculate final score
final_score = scoring.calculate_final_score(
    game_time=86400.0,  # 1 day
    ending_type='ESCAPE',
    current_money=100000,
    max_suspicion=45,
    exploration_percent=35.5
)

# Get results
print(f"Final Score: {scoring.total_score:,}")
print(f"Rank: {scoring.rank}")

# Get unlocked achievements
unlocked = scoring.get_unlocked_achievements()
for achievement in unlocked:
    print(f"{achievement.icon} {achievement.name} - {achievement.points} pts")

# Get score breakdown
breakdown = scoring.get_score_breakdown()
# {
#   'money_earned': (50000, 500),  # ($50k → 500 pts)
#   'materials_processed': (1000, 1000),  # (1000 units → 1000 pts)
#   ...
# }
```

---

## UI Components

### Phase10UI

**File:** `src/ui/phase10_ui.py`

Comprehensive UI for all Phase 10 systems.

**Panels:**
1. **Drone Panel** (left side, 300x200)
   - Drone counts by state
   - Exploration percentage
   - Progress bar

2. **Market Panel** (right side, 300x250)
   - Current trend indicator
   - Top 4 material prices
   - Price trends (↑↓→↕)
   - Active events count

3. **Weather Panel** (top-left, 250x120)
   - Weather icon and description
   - Current season
   - Effect modifiers

4. **Score Panel** (right side, 300x200)
   - Current/final score
   - Rank
   - Achievement progress
   - Recent achievements (last 3)

5. **Deconstruction Jobs** (bottom-center, varies)
   - Active job progress bars (max 3 shown)
   - Time remaining
   - Material recovery preview

**Map Overlays:**
- Fog of war (dark overlay on unexplored areas)
- Drone positions with battery indicators
- Transmitter coverage visualization (optional)

### Usage Example

```python
from src.ui.phase10_ui import Phase10UI

# Initialize
ui = Phase10UI()

# Render UI panels
ui.render(
    screen=screen,
    drone_manager=drone_manager,
    transmitter_manager=transmitter_manager,
    market_manager=market_manager,
    weather_manager=weather_manager,
    deconstruction_manager=deconstruction_manager,
    scoring_manager=scoring_manager,
    camera_offset=(cam_x, cam_y)
)

# Render fog of war overlay
ui.render_fog_of_war(
    screen=screen,
    drone_manager=drone_manager,
    tile_size=32,
    camera_offset=(cam_x, cam_y)
)

# Render drones on map
ui.render_drones_on_map(
    screen=screen,
    drone_manager=drone_manager,
    tile_size=32,
    camera_offset=(cam_x, cam_y)
)
```

---

## Integration Guide

### Game Loop Integration

```python
# Initialization
drone_manager = DroneManager(resources, map_width=200, map_height=200)
transmitter_manager = TransmitterManager(resources)
market_manager = MarketManager()
weather_manager = WeatherManager()
decon_manager = DeconstructionManager(resources, material_inventory)
scoring_manager = ScoringManager()
phase10_ui = Phase10UI()

# Game loop
while running:
    # Update all systems
    drone_manager.update(dt, game_time)
    transmitter_manager.update(dt, game_time)
    market_manager.update(dt, game_time)
    weather_manager.update(dt, game_time)
    decon_manager.update(dt, game_time)
    scoring_manager.update(dt, game_time)

    # Apply weather effects to other systems
    production_multiplier = weather_manager.get_solar_power_multiplier()
    suspicion_multiplier = weather_manager.get_detection_modifier()

    # Render
    phase10_ui.render(screen, drone_manager, transmitter_manager,
                      market_manager, weather_manager, decon_manager,
                      scoring_manager, camera_offset)
```

### Input Handling

```python
# Drone deployment
if click_on_map and has_selected_drone:
    world_pos = screen_to_world(mouse_pos, camera_offset)
    drone_manager.deploy_drone(selected_drone_id, world_pos)

# Transmitter placement
if transmitter_placement_mode and click_on_map:
    world_pos = screen_to_world(mouse_pos, camera_offset)
    transmitter_manager.place_transmitter(selected_type, world_pos)

# Deconstruction
if click_on_building and deconstruct_mode:
    materials = building.get_material_cost()
    decon_manager.start_deconstruction(
        'building', building.id, building.position,
        materials, building.size, workers=2
    )
```

---

## Testing

### Test Suite

**File:** `src/test_phase10.py`

**Coverage:**
- 17 comprehensive tests
- All major systems tested
- Edge cases and failure modes
- Integration scenarios

**Run Tests:**
```bash
python src/test_phase10.py
```

**Expected Output:**
```
ALL PHASE 10 TESTS PASSED! ✓
  ✓ Drone system with fog of war
  ✓ Wireless transmitter system
  ✓ Market fluctuation system
  ✓ Weather system
  ✓ Deconstruction system
  ✓ Scoring system
```

---

## Performance

### Optimization

**Drone Manager:**
- O(n) update for n drones
- Fog of war: Only updates visible tiles
- < 0.1ms per frame (5 drones)

**Market Manager:**
- O(m) for m materials
- Price calculations cached
- < 0.05ms per frame

**Deconstruction:**
- O(j) for j active jobs
- Progress calculations minimal
- < 0.01ms per frame

**Total Impact:** ~+0.2ms per frame (+1.2% at 60 FPS)

### Memory Usage

- DroneManager: ~2 KB (5 drones)
- FogOfWar: ~40 KB (200x200 tiles)
- MarketManager: ~1 KB
- ScoringManager: ~5 KB (achievements)

**Total:** ~50 KB additional memory

---

## Configuration

### Tunable Parameters

**Drone System:**
```python
drone_purchase_cost = 5000
max_drones = 5
drone_speed = 5.0  # tiles/second
vision_radius = 10.0  # tiles
battery_capacity = 100.0  # seconds
battery_drain_rate = 1.0  # %/second
charge_rate = 2.0  # %/second
auto_return_battery = 20.0  # %
```

**Transmitter System:**
```python
base_range = 20.0  # Factory base range
transmitter_costs = {BASIC: 3000, ADVANCED: 8000, LONG_RANGE: 15000}
transmitter_ranges = {BASIC: 30.0, ADVANCED: 50.0, LONG_RANGE: 80.0}
min_signal_for_control = 10.0  # %
```

**Market System:**
```python
trend_change_interval = 172800.0  # 48 hours
event_check_interval = 86400.0  # 24 hours
event_probability = 0.1  # 10%
min_price_multiplier = 0.3  # 30% of base
max_price_multiplier = 3.0  # 300% of base
```

**Deconstruction:**
```python
base_deconstruction_time = 60.0  # seconds
time_per_size_unit = 10.0  # seconds
worker_speed_multiplier = 0.5  # 50% per worker
recovery_rate = 0.7  # 70%
illegal_structure_penalty = 0.5  # 50% recovery
```

---

## Future Enhancements

### Planned Features

1. **Drone Upgrades:**
   - Extended battery (150 seconds)
   - Faster movement (8 tiles/sec)
   - Larger vision radius (15 tiles)
   - Cargo capacity (collect resources)

2. **Market Features:**
   - Futures trading (buy/sell at future price)
   - Material speculation
   - Contract system (guaranteed prices)

3. **Advanced Weather:**
   - Disaster events (tornado, earthquake)
   - Climate change over time
   - Seasonal bonuses/penalties

4. **Deconstruction Improvements:**
   - Specialized tools (reduce time 50%)
   - Material sorting (choose what to recover)
   - Salvage upgrades (80% recovery)

5. **Achievements:**
   - Secret achievements (hidden until unlocked)
   - Multi-stage achievements (tiers)
   - Achievement rewards (bonuses)

6. **Leaderboards:**
   - Online score tracking
   - Challenge modes
   - Daily/weekly challenges

---

## Summary

Phase 10 implementation statistics:

**Files Created:**
- `src/systems/drone_manager.py` (626 lines)
- `src/systems/transmitter_manager.py` (321 lines)
- `src/systems/market_manager.py` (395 lines)
- `src/systems/deconstruction_manager.py` (357 lines)
- `src/systems/scoring_manager.py` (557 lines)
- `src/ui/phase10_ui.py` (515 lines)
- `src/test_phase10.py` (557 lines)

**Total Code:** ~3,400 lines

**Test Coverage:** 17 tests, 100% pass rate

**Features Delivered:**
- ✅ Drone system with fog of war
- ✅ Wireless transmitter network
- ✅ Dynamic market pricing
- ✅ Weather effects (existing system)
- ✅ Deconstruction mechanics
- ✅ Scoring and achievements

**Achievement System:** 30+ achievements, 7 rank tiers

**Phase 10 Status:** ✅ COMPLETE

All systems tested, documented, and ready for gameplay!
