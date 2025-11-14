# Phase 7.13: Bus Transportation System Enhancements

**Implementation Date:** 2025-11-14
**Author:** Claude AI
**Status:** ✅ Complete

## Overview

This document describes the comprehensive enhancements made to the bus transportation system (Phase 7.13) to add realistic NPC passenger behavior, express routes, crowding visualization, and intelligent commuting AI.

---

## 1. NPC Passenger System

### 1.1 New NPC Activities

Added three new activities to the `Activity` enum in `src/entities/npc.py`:

- **`WALKING_TO_BUS_STOP`**: NPC is walking to a bus stop to catch a bus
- **`WAITING_FOR_BUS`**: NPC is standing at a bus stop waiting for a bus to arrive
- **`RIDING_BUS`**: NPC is currently on a bus traveling to their destination

### 1.2 NPC Bus Fields

Added the following fields to the `NPC` class:

```python
self.using_bus = False              # Whether NPC is currently using bus system
self.target_bus_stop = None         # (grid_x, grid_y) of stop NPC is walking to
self.current_bus_id = None          # ID of bus NPC is riding
self.bus_destination_stop = None   # (grid_x, grid_y) where NPC wants to alight
self.final_destination = None       # (world_x, world_y) ultimate destination after bus
self.bus_preference = random.random()  # 0.0-1.0, higher = more likely to use bus
```

### 1.3 NPC Bus Methods

Added comprehensive bus journey methods to `NPC` class:

#### `start_bus_journey(bus_stop_pos, destination_stop, final_dest)`
Initiates a bus journey. Sets the NPC to walk to the nearest bus stop.

#### `arrive_at_bus_stop()`
Called when NPC reaches the bus stop. Changes activity to `WAITING_FOR_BUS`.

#### `board_bus(bus_id)`
Called when NPC boards a bus. Changes activity to `RIDING_BUS` and tracks bus ID.

#### `alight_from_bus()`
Called when NPC gets off at their destination stop. Resumes walking to final destination.

#### `cancel_bus_journey()`
Cancels the bus journey (e.g., if bus doesn't arrive in time). Reverts to walking.

#### `is_at_destination_stop(bus_grid_x, bus_grid_y)`
Checks if the bus is at the NPC's destination stop.

---

## 2. Bus Class Enhancements

### 2.1 Express Bus Support

Added `is_express` flag to `Bus` class:

```python
def __init__(self, world_x, world_y, route_id=0, initial_direction='east', is_express=False):
    self.is_express = is_express
    self.stop_duration = 3.0 if is_express else 5.0  # Express buses wait less
```

Express buses:
- Wait only 3 seconds at stops (vs 5 seconds for regular)
- Only stop at express stops (every other stop)
- Display "EXP" label with orange background

### 2.2 Real-Time Boarding/Alighting

Enhanced `Bus.update()` to accept NPCs and bus stops:

```python
def update(self, dt, road_network, npcs=None, bus_stops=None):
    # Handle NPC boarding/alighting when stopped
    if self.stopped_at_stop and npcs and bus_stops:
        self._handle_passenger_boarding_alighting(npcs, bus_stops)

    # Update passenger positions
    if npcs:
        self._update_passenger_positions(npcs)
```

#### Boarding/Alighting Logic (`_handle_passenger_boarding_alighting`)

1. **Alighting First**: NPCs whose destination is this stop get off
2. **Boarding Second**: Waiting NPCs at this stop board if space available
3. **Bus Stop Integration**: Updates BusStop waiting lists

#### Passenger Position Updates (`_update_passenger_positions`)

NPCs riding the bus have their `world_x` and `world_y` synchronized with the bus position, creating the visual effect of riding inside the bus.

### 2.3 Crowding Visualization

Added `get_crowding_level()` method that returns:
- **'empty'** (0% full) - Gray text
- **'comfortable'** (0-50% full) - Green text
- **'crowded'** (50-90% full) - Yellow-orange text
- **'full'** (90-100% full) - Red text

Passenger count display now color-codes based on crowding level for instant visual feedback.

---

## 3. NPCManager AI Enhancements

### 3.1 Bus Manager Integration

Added connection to bus system:

```python
self.bus_manager = None  # Set externally after bus system is initialized
self.bus_usage_rate = 0.4  # 40% of NPCs prefer buses for commuting
```

### 3.2 Commuting Decision AI (`_update_bus_commuting`)

NPCs decide to use buses based on:

1. **Bus Preference**: Each NPC has a random `bus_preference` value (0.0-1.0)
2. **Usage Rate**: Only NPCs with `bus_preference > 0.6` use buses (40% overall)
3. **Distance Threshold**: Only consider bus if destination is > 200 pixels away
4. **Activity**: Only during `COMMUTING_TO_WORK` or `COMMUTING_HOME` activities

### 3.3 Bus Journey Assignment (`_assign_bus_journey`)

When an NPC decides to use the bus:

1. Find nearest bus stop to current position
2. Find nearest bus stop to destination
3. Verify stops are different
4. Call `npc.start_bus_journey()` with:
   - Start stop position
   - Destination stop position
   - Final destination (work/home)

### 3.4 Waiting List Management

NPCs in `WAITING_FOR_BUS` activity are automatically added to the BusStop's `waiting_npcs` set, allowing buses to detect and board them.

---

## 4. Express Route System

### 4.1 BusRoute Express Support

Enhanced `BusRoute` class:

```python
def __init__(self, route_id, name=None, is_express=False):
    self.is_express = is_express
    self.stops = []              # All stops
    self.express_stops = []      # Subset for express buses
    self.frequency_minutes = 10 if not is_express else 15
```

#### `calculate_express_stops(skip_factor=2)`

Calculates express stops by:
1. Always including first stop
2. Including every nth stop (skip_factor=2 means every other stop)
3. Always including last stop

Example: If stops are [A, B, C, D, E, F], express stops are [A, C, E, F]

### 4.2 Route Generation

BusManager generates express routes:

```python
self.express_route_chance = 0.3  # 30% of routes are express
```

When generating a route:
1. Randomly decide if route is express (30% chance)
2. Generate all stops normally
3. If express, calculate express stop subset
4. Place bus stop props at ALL stops (not just express)

---

## 5. Bus Scheduling System

### 5.1 Schedule Fields

Added to `BusRoute`:

```python
self.frequency_minutes = 10  # Regular buses every 10 game-minutes
self.active_hours = (6, 22)  # Buses run 6am-10pm
```

Express routes run every 15 game-minutes.

### 5.2 Game Time Tracking

BusManager now tracks game time:

```python
self.game_time = 0.0
self.spawn_timers = {}  # route_id -> time until next spawn
```

Updated via `bus_manager.update(dt, npcs, game_time=time_of_day)`

### 5.3 Scheduled Spawning (Framework)

Infrastructure added for time-based bus spawning:

```python
def update(self, dt, npcs=None, game_time=None):
    if game_time is not None:
        self.game_time = game_time

    # Framework for scheduled spawning
    # self._update_scheduled_spawning(dt)  # Disabled by default
```

Can be enabled for dynamic bus spawning based on time of day and route frequency.

---

## 6. Visual Enhancements

### 6.1 Express Bus Indicators

Express buses display:
- Route label: `"#1 EXP"` (vs `"#1"` for regular)
- Orange background (vs black for regular)
- Located above the bus sprite

### 6.2 Crowding Color Coding

Passenger count displays with color coding:
- `0/20` - Gray (empty)
- `8/20` - Green (comfortable)
- `16/20` - Yellow-orange (crowded)
- `19/20` - Red (full)

Located below the bus sprite.

### 6.3 NPC Activity Icons

Updated activity display to show bus-related activities:
- `→🚏` - Walking to bus stop
- `🚏` - Waiting for bus
- `🚌` - Riding bus

---

## 7. Game Integration

### 7.1 Update Loop Integration

Modified `game.py` update loop:

```python
# Get NPC list and game time
npc_list = self.npcs.npcs
time_of_day = self.npcs.game_time

# Pass to bus manager
self.bus_manager.update(adjusted_dt, npcs=npc_list, game_time=time_of_day)
```

### 7.2 Manager Connection

Connected NPCManager to BusManager during initialization:

```python
# After spawning NPCs
self.npcs.bus_manager = self.bus_manager
```

This allows NPCs to:
- Find nearest bus stops
- Access bus routes
- Check bus schedules

---

## 8. Implementation Files

### Modified Files

| File | Lines Changed | Description |
|------|--------------|-------------|
| `src/entities/npc.py` | +120 | Added bus passenger states, fields, and methods |
| `src/entities/bus.py` | +100 | Added boarding/alighting, express support, crowding |
| `src/systems/npc_manager.py` | +85 | Added commuting AI and bus journey assignment |
| `src/systems/bus_route.py` | +25 | Added express route support |
| `src/systems/bus_manager.py` | +30 | Added scheduling framework and express spawning |
| `src/core/game.py` | +5 | Updated integration to pass NPCs and game time |

**Total**: ~365 lines of new/modified code

---

## 9. Testing Checklist

### Basic Functionality
- [x] NPCs decide to use buses during commute (40% usage rate)
- [x] NPCs walk to nearest bus stop
- [x] NPCs wait at bus stops (added to waiting list)
- [x] NPCs board buses when they arrive
- [x] NPCs ride buses (position follows bus)
- [x] NPCs alight at destination stops
- [x] NPCs walk to final destination after alighting

### Express Routes
- [x] Express routes generated (30% of routes)
- [x] Express stops calculated correctly (every other stop)
- [x] Express buses only stop at express stops
- [x] Express buses wait less time (3s vs 5s)
- [x] Express buses display "EXP" label with orange background

### Crowding Visualization
- [x] Empty buses show gray passenger count
- [x] Comfortable buses show green passenger count
- [x] Crowded buses show yellow-orange passenger count
- [x] Full buses show red passenger count
- [x] Crowding level updates dynamically

### Edge Cases
- [x] NPCs don't use bus for short distances (< 200px)
- [x] NPCs handle when no bus stops are nearby
- [x] Buses handle when no NPCs are waiting
- [x] Multiple NPCs can board same bus (up to capacity)
- [x] NPCs get off at correct destination stop

---

## 10. Configuration Parameters

### NPC Behavior

```python
# In NPCManager
self.bus_usage_rate = 0.4        # 40% of NPCs prefer buses
distance_threshold = 200          # Min distance to consider bus (pixels)
```

### Bus Routes

```python
# In BusManager
self.express_route_chance = 0.3  # 30% routes are express
skip_factor = 2                   # Express stops every 2nd stop
```

### Bus Timing

```python
# In Bus class
regular_stop_duration = 5.0      # Seconds at each stop
express_stop_duration = 3.0      # Seconds for express buses

# In BusRoute class
regular_frequency = 10           # Minutes between buses
express_frequency = 15           # Minutes for express buses
active_hours = (6, 22)          # 6am-10pm operation
```

### Crowding Thresholds

```python
empty:       ratio == 0
comfortable: ratio < 0.5         # < 50% full
crowded:     ratio < 0.9         # 50-90% full
full:        ratio >= 0.9        # >= 90% full
```

---

## 11. Performance Considerations

### Computational Complexity

- **NPC Bus Decision**: O(N) where N = number of NPCs
- **Bus Stop Search**: O(S) where S = number of bus stops (typically 15-30)
- **Boarding/Alighting**: O(W) where W = waiting NPCs at stop (typically < 10)
- **Passenger Position Update**: O(P) where P = passengers on bus (max 20)

### Optimizations

1. **Distance Gating**: Only NPCs traveling > 200px consider buses
2. **Activity Filtering**: Only commuting NPCs checked for bus usage
3. **One-Time Decision**: NPCs decide once at commute start, not every frame
4. **Waiting List Caching**: BusStop maintains set of waiting NPC IDs

### Expected Performance

With 100 NPCs and 3 bus routes:
- ~40 NPCs may use buses (40% usage rate)
- ~5-10 NPCs waiting at any given time
- ~3-6 buses active (2 per route)
- Negligible CPU overhead (< 1% of frame time)

---

## 12. Future Enhancements

### Potential Additions

1. **Route Preferences**: NPCs remember which routes they've used
2. **Wait Timeout**: NPCs cancel journey if bus doesn't arrive within 60 seconds
3. **Rush Hour**: Increase bus frequency during peak commute times (8-9am, 5-6pm)
4. **Bus Announcements**: UI notifications when buses arrive at stops
5. **Transfer System**: NPCs transfer between routes for longer journeys
6. **Fare System**: Deduct money from NPCs when boarding
7. **Bus Breakdowns**: Random events where buses malfunction
8. **Night Routes**: Reduced service 10pm-6am instead of complete shutdown

---

## 13. Known Limitations

1. **No Route Matching**: NPCs board any bus at a stop, not just buses going to their destination
2. **No Wait Timeout**: NPCs wait indefinitely for buses (could add 60s timeout)
3. **No Transfers**: NPCs can't transfer between routes
4. **Fixed Schedules**: Bus frequency doesn't adapt to demand
5. **No Fare System**: Boarding is free
6. **Simple Pathfinding**: NPCs use nearest stops, not optimal routes

---

## 14. Code Examples

### Example: NPC Starting Bus Journey

```python
# In NPCManager._assign_bus_journey()
nearest_start_stop = bus_manager.get_nearest_bus_stop(current_grid_x, current_grid_y)
nearest_dest_stop = bus_manager.get_nearest_bus_stop(dest_grid_x, dest_grid_y)

npc.start_bus_journey(
    bus_stop_pos=(nearest_start_stop.grid_x, nearest_start_stop.grid_y),
    destination_stop=(nearest_dest_stop.grid_x, nearest_dest_stop.grid_y),
    final_dest=(npc.target_x, npc.target_y)
)
```

### Example: Bus Handling Boarding

```python
# In Bus._handle_passenger_boarding_alighting()
for npc_id in waiting_npc_ids:
    if self.is_full():
        break

    npc = self._find_npc_by_id(npcs, npc_id)
    if npc and npc.current_activity == Activity.WAITING_FOR_BUS:
        success = self.add_passenger(npc_id)
        if success:
            npc.board_bus(self.id)
            bus_stop.remove_waiting_npc(npc_id)
```

### Example: Express Route Generation

```python
# In BusManager._generate_single_route()
is_express = random.random() < self.express_route_chance
route = BusRoute(route_id, is_express=is_express)

# ... add stops ...

if is_express:
    route.calculate_express_stops(skip_factor=2)
```

---

## 15. Summary

The Phase 7.13 enhancements transform the bus system from a visual prop into a fully functional public transportation network with:

✅ **Intelligent NPC Passengers**: NPCs autonomously decide to use buses, walk to stops, wait, board, ride, and alight
✅ **Express Routes**: 30% of routes are express, stopping at every other stop with faster service
✅ **Crowding Visualization**: Color-coded passenger counts (gray/green/yellow/red) show bus capacity at a glance
✅ **Realistic Behavior**: NPCs only use buses for long commutes, prefer buses based on individual preference
✅ **Seamless Integration**: Works with existing NPC schedules, traffic system, and game loop

**Result**: A living, breathing public transportation system that adds depth and realism to the city simulation.

---

**End of Document**
