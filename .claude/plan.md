# Production Readiness Fixes Implementation Plan

## Overview
This plan addresses all discovered production readiness issues, organized by priority. Each phase includes specific files, line numbers, and implementation details.

---

## Phase 1: CRITICAL - Fix Save/Load System (Estimated: 2-3 hours)

### Issue
`save_manager.py` lines 729, 739, 775, 801 have empty restoration loops in `load_game()`. Buildings, robots, cameras, and weather state are NOT actually restored when loading a save.

### Files to Modify
- `src/systems/save_manager.py`

### Implementation Details

#### 1.1 Building Restoration (line ~729)
```python
# Current: Empty loop that does nothing
for building_data in state.get('buildings', []):
    pass

# Fix: Actually restore buildings
for building_data in state.get('buildings', []):
    building_type = building_data.get('type')
    grid_x = building_data.get('grid_x')
    grid_y = building_data.get('grid_y')
    # Create building instance based on type
    # Restore building state (level, processing, queues)
    # Place building in building_manager
```

#### 1.2 Robot Restoration (line ~739)
```python
# Fix: Restore robots with their state
for robot_data in state.get('robots', []):
    x = robot_data.get('x')
    y = robot_data.get('y')
    autonomous = robot_data.get('autonomous', True)
    robot = game.entities.create_robot(x, y, autonomous)
    robot.carrying = robot_data.get('carrying', {})
    robot.health = robot_data.get('health', 100)
    # Restore other robot state
```

#### 1.3 Camera State Restoration (line ~775)
```python
# Fix: Restore security camera states
for i, camera_state in enumerate(state.get('camera_states', [])):
    if i < len(game.camera_manager.cameras):
        camera = game.camera_manager.cameras[i]
        camera.disabled = camera_state.get('disabled', False)
        camera.disabled_timer = camera_state.get('disabled_timer', 0)
```

#### 1.4 Weather Restoration (line ~801)
```python
# Fix: Restore weather manager state
weather_state = state.get('weather', {})
if weather_state and hasattr(game, 'weather_manager'):
    game.weather_manager.current_weather = weather_state.get('current')
    game.weather_manager.transition_progress = weather_state.get('transition', 0)
```

### Verification
- Create a save, modify game state, load save, verify state matches

---

## Phase 2: HIGH Priority - Implement Missing Functionality (Estimated: 3-4 hours)

### 2.1 config.py - Disable Debug Mode
**File:** `config.py` line 23
```python
# Change from:
DEBUG_MODE = True

# To:
DEBUG_MODE = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
```

### 2.2 resource_manager.py - Implement update()
**File:** `src/systems/resource_manager.py` line 206

Implement the placeholder with actual functionality:
- Market price fluctuations (small random variations)
- Storage decay for organic materials
- Passive income calculation

```python
def update(self, dt: float) -> None:
    """Update resource manager state."""
    # Market price fluctuations (subtle, every game hour)
    self._market_timer += dt
    if self._market_timer >= 60.0:  # Every game minute
        self._market_timer = 0.0
        self._apply_price_fluctuations()
    
    # Organic material decay
    self._apply_storage_decay(dt)
```

### 2.3 city_building.py - Implement Illegal Deconstruction Suspicion
**File:** `src/entities/city_building.py` line 271

```python
# In start_deconstruction():
if self.is_illegal_to_deconstruct:
    # Add suspicion for illegal activity
    if hasattr(self, 'suspicion_manager') and self.suspicion_manager:
        self.suspicion_manager.add_suspicion(
            15.0, 
            'illegal_deconstruction',
            f'Illegal deconstruction of {self.name}'
        )
```

### 2.4 battery_fab.py - Complete Material Consumption
**File:** `src/entities/buildings/battery_fab.py` line 121

Review and complete the material consumption logic from input queue.

### 2.5 hud.py - Implement Notification Duration
**File:** `src/ui/hud.py` line 395

Implement the duration parameter for notifications:
```python
def add_notification(self, message: str, duration: float = 5.0):
    """Add notification with auto-dismiss after duration."""
    notification = {
        'message': message,
        'time_remaining': duration,
        'alpha': 255
    }
    self.notifications.append(notification)
```

---

## Phase 3: MEDIUM Priority - Error Handling Improvements (Estimated: 1-2 hours)

### 3.1 audio_manager.py - Add Logging to Silent Except Blocks
**File:** `src/systems/audio_manager.py` lines 360, 371, 382, 403, 430

Replace all `except pygame.error: pass` with:
```python
except pygame.error as e:
    logger.debug(f"Audio operation failed (non-critical): {e}")
```

### 3.2 Add Logging to Silent Returns
**Files:**
- `src/systems/bus_route.py` line 137
- `src/systems/save_manager.py` lines 628, 638
- `src/ui/settings_ui.py` line 472
- `src/ui/research_ui.py` line 64

Add `logger.debug()` calls before silent returns/fallbacks.

---

## Phase 4: MEDIUM Priority - Implement Empty Stubs (Estimated: 2-3 hours)

### 4.1 city_generator.py - Implement _place_park_features()
**File:** `src/world/city_generator.py` line 366

```python
def _place_park_features(self, block):
    """Place decorative features in park blocks."""
    # Place trees at regular intervals
    # Place benches along paths
    # Place fountains at center of large parks
    # Place lamp posts for lighting
```

### 4.2 controls_help.py - Implement update() Animation
**File:** `src/ui/controls_help.py` line 300

```python
def update(self, dt: float):
    """Update help overlay animations."""
    if self.visible:
        # Fade in animation
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + dt * 500)
        # Scroll animation for long content
        self._update_scroll(dt)
```

---

## Phase 5: MEDIUM Priority - Extract Magic Numbers to Config (Estimated: 2-3 hours)

### 5.1 Create GameConfig Class
**New file:** `src/core/game_config.py`

```python
"""Centralized game configuration values."""
from dataclasses import dataclass

@dataclass
class TimeConfig:
    SECONDS_PER_MINUTE: int = 60
    SECONDS_PER_HOUR: int = 3600
    SECONDS_PER_DAY: int = 86400
    SECONDS_PER_WEEK: int = 604800

@dataclass  
class InspectionConfig:
    WARNING_TIME_MIN: float = 86400.0  # 24 hours
    WARNING_TIME_MAX: float = 172800.0  # 48 hours
    DURATION: float = 3600.0  # 1 hour
    IMMUNITY_PERIOD: float = 604800.0  # 7 days
    SUSPICION_THRESHOLD: int = 60
    FINE_MINOR: int = 5000
    FINE_MAJOR: int = 20000

@dataclass
class EntityConfig:
    TARGET_CAMERA_COUNT: int = 25
    MAX_DRONES: int = 5
    BUS_MAX_CAPACITY: int = 20
    PARKED_VEHICLE_COUNT: int = 30
    TARGET_PROP_COUNT: int = 100

@dataclass
class SuspicionConfig:
    TIER_THRESHOLDS: tuple = (0, 21, 41, 61, 81)
    BASE_DECAY_RATE: float = 0.1
    DECAY_STOP_LEVEL: float = 60.0
```

### 5.2 Update Files to Use Config
Replace hardcoded values in:
- `src/systems/inspection_manager.py`
- `src/systems/suspicion_manager.py`
- `src/systems/weather_manager.py`
- `src/core/game.py`
- Other files with repeated magic numbers

---

## Phase 6: LOW Priority - Minor Fixes (Estimated: 1 hour)

### 6.1 Add Logging to Cleanup Handlers
**Files:**
- `src/systems/save_manager.py` line 269
- `src/ui/settings_manager.py` line 288

```python
except Exception as e:
    logger.error(f"Operation failed, cleaning up: {e}")
    # cleanup code
    raise
```

### 6.2 Fix Test File Temporary File Creation
**File:** `test_phase11_ui_ux.py` line 297

```python
# Change from:
temp_file = tempfile.mktemp(suffix='.json')

# To:
fd, temp_file = tempfile.mkstemp(suffix='.json')
os.close(fd)
```

---

## Phase 7: LOW Priority - TODO UI Indicators (Estimated: 4-6 hours)

### Files with TODO Comments for UI Indicators:
1. `src/entities/buildings/battery_bank.py` - Charge level, charging animation, rate display
2. `src/entities/buildings/solar_array.py` - Power output, sun tracking, efficiency display
3. `src/entities/buildings/methane_generator.py` - Fuel level, smoke particles, power indicator
4. `src/entities/buildings/silo.py` - Fill level bar, material icon, transfer rate
5. `src/entities/buildings/warehouse.py` - Fill level bar, material type icons

Each building needs:
- Visual indicator rendering in `render()` method
- State tracking variables
- Update logic in `update()` method

---

## Implementation Order (Recommended)

1. **Phase 1** (Critical) - Save/Load must work correctly
2. **Phase 2.1** (Quick win) - Disable DEBUG_MODE
3. **Phase 3** (Quick win) - Add logging to error handlers
4. **Phase 6** (Quick win) - Minor fixes
5. **Phase 2** (Rest) - Implement missing functionality
6. **Phase 4** - Implement empty stubs
7. **Phase 5** - Extract magic numbers (can be incremental)
8. **Phase 7** - UI indicators (visual polish, lowest priority)

---

## Verification Checklist

- [ ] All Python files pass `py_compile`
- [ ] All existing tests pass
- [ ] Save/load cycle works correctly
- [ ] No new `pass` or `...` stubs introduced
- [ ] All new code has docstrings
- [ ] No hardcoded DEBUG = True
- [ ] Logger used instead of print
- [ ] No bare except clauses

---

## Estimated Total Time: 15-22 hours

| Phase | Time | Priority |
|-------|------|----------|
| Phase 1 | 2-3h | CRITICAL |
| Phase 2 | 3-4h | HIGH |
| Phase 3 | 1-2h | MEDIUM |
| Phase 4 | 2-3h | MEDIUM |
| Phase 5 | 2-3h | MEDIUM |
| Phase 6 | 1h | LOW |
| Phase 7 | 4-6h | LOW |
