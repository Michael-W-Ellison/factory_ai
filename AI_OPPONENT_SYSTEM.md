# AI Opponent System Documentation

## Overview

The AI Opponent System enables competitive offline gameplay where players compete against intelligent AI-controlled factories. The system features strategic AI decision-making, dynamic market competition, and multiple win conditions.

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [AI Personalities](#ai-personalities)
4. [Game Modes](#game-modes)
5. [Win Conditions](#win-conditions)
6. [Market Dynamics](#market-dynamics)
7. [API Reference](#api-reference)
8. [Integration Guide](#integration-guide)
9. [Examples](#examples)

---

## Features

### Core Features

- **Offline Competition**: Play against AI without internet connection
- **5 AI Personalities**: Aggressive, Balanced, Cautious, Opportunist, Innovator
- **Strategic Decision-Making**: AI makes realistic factory management decisions
- **Dynamic Market**: Competitive market with supply/demand economics
- **Multiple Win Conditions**: Net worth, market share, profit, survival, time limit
- **Difficulty Scaling**: Adjustable AI difficulty (0.0-1.0)
- **Real-time Rankings**: Live leaderboard with player and AI positions

### AI Capabilities

- **Resource Management**: Manages money, workers, and production
- **Strategic Planning**: Pursues long-term goals (expansion, efficiency, market dominance)
- **Risk Assessment**: Evaluates police activity and market conditions
- **Tactical Decisions**: Builds workstations, hires workers, adjusts production
- **Market Timing**: Buys and sells based on market conditions
- **Stealth**: Hides operations when heat is too high

---

## Architecture

### Component Structure

```
src/
├── entities/
│   └── ai_factory.py          # AI factory entity with decision-making
├── systems/
│   └── ai_opponent_manager.py # Manages competition and market
└── ui/
    └── competitor_ui.py       # UI panels for competition view
```

### Class Hierarchy

```
AIFactory
├── Resource Management (money, workers, workstations)
├── Production System (rates, inventory, quality)
├── Decision Engine (strategic AI)
└── Statistics Tracking

AIOpponentManager
├── Market Simulation (demand, prices)
├── Competition Tracking (rankings, scores)
├── Win Condition Checking
└── Multiple AI Opponents
```

---

## AI Personalities

### 1. Aggressive

**Strategy**: High risk, fast expansion

**Characteristics**:
- Risk tolerance: 0.8
- Favors rapid expansion
- Builds workstations and hires workers frequently
- Increases production aggressively
- May overextend and go bankrupt

**Decision Priorities**:
1. Build workstations (70% chance when viable)
2. Increase production
3. Expand before stabilizing
4. Takes on more heat/risk

**Best Against**: Cautious opponents
**Weak Against**: Market crashes, investigations

---

### 2. Balanced

**Strategy**: Moderate risk, steady growth

**Characteristics**:
- Risk tolerance: 0.5
- Balanced approach to all aspects
- Makes decisions based on situation
- Adapts to conditions
- Most well-rounded

**Decision Priorities**:
1. Expand when profitable (50% chance)
2. Hire workers when needed (60% chance)
3. Sell when inventory high
4. Save during uncertainty

**Best Against**: Most opponents
**Weak Against**: Extreme strategies

---

### 3. Cautious

**Strategy**: Low risk, slow but safe

**Characteristics**:
- Risk tolerance: 0.2
- Prioritizes safety and stability
- Avoids police attention
- Saves money conservatively
- Rarely goes bankrupt

**Decision Priorities**:
1. Hide when police activity high
2. Save money when low
3. Hire workers before expanding
4. Slow, steady production

**Best Against**: Aggressive opponents, investigations
**Weak Against**: Opportunists, fast markets

---

### 4. Opportunist

**Strategy**: Adapts to market conditions

**Characteristics**:
- Risk tolerance: 0.6
- Watches market closely
- Sells when prices high
- Buys when conditions favorable
- Flexible strategy

**Decision Priorities**:
1. Sell when price multiplier > 1.2
2. Increase production when demand high
3. Expand when market viable
4. Save during poor conditions

**Best Against**: Fixed-strategy opponents
**Weak Against**: Stable markets

---

### 5. Innovator

**Strategy**: Focuses on technology and upgrades

**Characteristics**:
- Risk tolerance: 0.4
- Invests heavily in technology
- Upgrades production capacity
- Higher quality products
- Long-term advantage

**Decision Priorities**:
1. Upgrade machines (60% chance when affordable)
2. Build high-tech workstations
3. Increase production efficiency
4. Quality over quantity

**Best Against**: Volume-based opponents
**Weak Against**: Early game rushes

---

## Game Modes

### Solo Mode

**Description**: Player vs environment only
- No AI opponents
- Focus on police/FBI challenges
- Achievement-based progression

**Use Case**: Learning, relaxed gameplay

---

### Competitive Mode

**Description**: Player vs AI opponents
- 1-5 AI opponents
- Shared market
- Rankings updated live
- Win condition based

**Use Case**: Standard competitive play

**Configuration**:
```python
from systems.ai_opponent_manager import get_ai_opponent_manager, GameMode

ai_manager = get_ai_opponent_manager(
    num_opponents=3,
    game_mode=GameMode.COMPETITIVE
)
```

---

### Tournament Mode

**Description**: Timed competition with rankings
- Fixed time limit (default 1 hour)
- Best position at end wins
- Leaderboard preserved
- Statistics tracked

**Use Case**: Quick competitive sessions

**Configuration**:
```python
ai_manager = get_ai_opponent_manager(
    num_opponents=4,
    game_mode=GameMode.TOURNAMENT
)
```

---

## Win Conditions

### Net Worth

**Condition**: Highest total net worth wins

**Calculation**:
```
Net Worth = Money + Asset Value
Asset Value = (Workstations × 25k) + (Workers × 3k) +
              (Tech Level × 30k) + (Inventory × 800)
```

**Threshold**: $1,000,000
**Best For**: Long-term strategic play

---

### Market Share

**Condition**: Largest percentage of market wins

**Calculation**:
```
Market Share = Your Sales / Total Market Sales
```

**Threshold**: 50%
**Best For**: Sales-focused gameplay

---

### Profit

**Condition**: Highest profit wins

**Calculation**:
```
Profit = Total Revenue - Total Expenses
```

**Threshold**: $500,000
**Best For**: Efficiency-focused play

---

### Survival

**Condition**: Last factory standing wins

**Mechanics**:
- Factories go bankrupt at -$50k
- Survivor declared winner
- Net worth used for ties

**Best For**: High-risk competitive play

---

### Time Limit

**Condition**: Best position when time expires

**Duration**: Configurable (default 3600s / 1 hour)

**Scoring**: Uses win condition scoring method
**Best For**: Quick competitive sessions

---

## Market Dynamics

### Supply and Demand

**Demand Calculation**:
```python
demand_level = 1.0 + sin(time * 0.1) * 0.3 + random(-0.1, 0.1)
# Range: 0.5 - 2.0
```

**Effects**:
- High demand (>1.5): Easier to sell, higher volumes
- Low demand (<0.8): Harder to sell, lower volumes

---

### Price Multiplier

**Price Calculation**:
```python
supply_pressure = total_inventory / market_size
price_multiplier = 1.0 + (1.0 - supply_pressure) * 0.5
# Range: 0.5 - 2.0
```

**Effects**:
- High prices (>1.2): Good time to sell
- Low prices (<0.9): Poor time to sell

**Player Strategy**: AI opponents track this and sell strategically

---

### Competition Level

**Factors**:
- Number of active factories
- Total production capacity
- Market saturation

**Effects**:
- More competition = lower prices
- Less competition = higher prices
- Market share harder to gain with more opponents

---

### Police Activity

**Dynamics**:
- Base level: 0.3 (30%)
- Fluctuates: ±0.05 per tick
- Investigations boost to 0.7+

**AI Response**:
- Cautious AI: Hides at 50% activity
- Balanced AI: Hides at 70% activity
- Aggressive AI: Hides at 85% activity

---

## API Reference

### AIFactory Class

```python
class AIFactory:
    def __init__(self, name: str, personality: AIPersonality,
                 difficulty: float, starting_money: int)
```

**Methods**:

```python
def update(self, dt: float, market_conditions: Dict, police_activity: float)
"""Update AI state and make decisions."""

def get_net_worth(self) -> int
"""Calculate total net worth."""

def get_profit(self) -> int
"""Get total profit."""

def get_statistics(self) -> Dict
"""Get comprehensive statistics."""
```

**Attributes**:
- `money`: Current cash
- `workers`: Number of workers
- `workstations`: Number of workstations
- `technology_level`: Tech upgrade level
- `production_rate`: Units per hour
- `inventory`: Finished products
- `market_share`: Percentage of market
- `heat_level`: Police suspicion (0-100)
- `current_goal`: Strategic goal
- `hiding`: Whether hiding from police

---

### AIOpponentManager Class

```python
class AIOpponentManager:
    def __init__(self, num_opponents: int, game_mode: GameMode,
                 win_condition: WinCondition)
```

**Methods**:

```python
def update(self, dt: float, player_factory: Optional[Dict])
"""Update all opponents and market."""

def get_market_conditions(self) -> Dict
"""Get current market state."""

def get_leaderboard(self) -> List[Dict]
"""Get formatted leaderboard."""

def get_opponent_by_rank(self, rank: int) -> Optional[AIFactory]
"""Get opponent by ranking position."""

def get_statistics(self) -> Dict
"""Get comprehensive statistics."""
```

**Attributes**:
- `opponents`: List of AIFactory instances
- `demand_level`: Market demand (0.5-2.0)
- `price_multiplier`: Price multiplier (0.5-2.0)
- `police_activity`: Police activity level (0-1)
- `rankings`: Current rankings
- `winner`: Winner name (if any)

---

### UI Components

#### CompetitorPanel

```python
class CompetitorPanel:
    def __init__(self, x: int, y: int, width: int = 300, height: int = 500)
    def render(self, surface: pygame.Surface, leaderboard: List[Dict])
```

**Displays**:
- Ranked list of competitors
- Company names
- Current scores
- Player highlighted in green

#### MarketPanel

```python
class MarketPanel:
    def __init__(self, x: int, y: int, width: int = 250, height: int = 200)
    def render(self, surface: pygame.Surface, market_data: Dict)
```

**Displays**:
- Market demand level
- Price multiplier
- Police activity
- Investigation status

#### OpponentDetailPanel

```python
class OpponentDetailPanel:
    def __init__(self, x: int, y: int, width: int = 350, height: int = 300)
    def render(self, surface: pygame.Surface, opponent_stats: Dict)
    def toggle(self)
```

**Displays**:
- Opponent name and personality
- Detailed statistics
- Current strategic goal
- Resource levels

---

## Integration Guide

### Basic Setup

```python
from systems.ai_opponent_manager import (
    get_ai_opponent_manager, GameMode, WinCondition
)

# Initialize AI opponent system
ai_manager = get_ai_opponent_manager(
    num_opponents=3,
    game_mode=GameMode.COMPETITIVE,
    win_condition=WinCondition.NET_WORTH
)

# Create UI
from ui.competitor_ui import CompetitorPanel, MarketPanel

leaderboard_panel = CompetitorPanel(x=20, y=20)
market_panel = MarketPanel(x=20, y=540)
```

---

### Game Loop Integration

```python
# In your game loop
def update(dt):
    # Prepare player factory stats
    player_stats = {
        'name': 'Player',
        'money': player.money,
        'net_worth': player.calculate_net_worth(),
        'profit': player.total_revenue - player.total_expenses,
        'workers': player.workers,
        'workstations': player.workstations,
        'technology_level': player.tech_level,
        'market_share': 0.0,  # Will be calculated
        'sales': player.sales_this_period,
        'age': player.time_in_business,
    }

    # Update AI opponents
    ai_manager.update(dt, player_stats)

    # Get data for UI
    leaderboard = ai_manager.get_leaderboard()
    market_data = ai_manager.get_statistics()

    # Render UI
    leaderboard_panel.render(screen, leaderboard)
    market_panel.render(screen, market_data)

    # Check for winner
    if ai_manager.winner:
        display_victory_screen(ai_manager.winner)
```

---

### Custom Configuration

```python
# Aggressive tournament
ai_manager = get_ai_opponent_manager(
    num_opponents=5,
    game_mode=GameMode.TOURNAMENT,
    win_condition=WinCondition.PROFIT
)
ai_manager.time_limit = 1800  # 30 minute tournament

# Survival mode
ai_manager = get_ai_opponent_manager(
    num_opponents=4,
    game_mode=GameMode.COMPETITIVE,
    win_condition=WinCondition.SURVIVAL
)

# Market share competition
ai_manager = get_ai_opponent_manager(
    num_opponents=3,
    game_mode=GameMode.COMPETITIVE,
    win_condition=WinCondition.MARKET_SHARE
)
```

---

## Examples

### Example 1: Standard Competitive Match

```python
# Setup
ai_manager = get_ai_opponent_manager(
    num_opponents=3,
    game_mode=GameMode.COMPETITIVE,
    win_condition=WinCondition.NET_WORTH
)

# Game loop
while running:
    dt = clock.tick(60) / 1000.0

    # Update player
    player.update(dt)

    # Update AI
    ai_manager.update(dt, player.get_stats())

    # Check victory
    if ai_manager.winner:
        if ai_manager.winner == "Player":
            print("You won!")
        else:
            print(f"{ai_manager.winner} won!")
        break
```

**Expected Outcome**:
- Race to $1M net worth
- AI opponents expand and compete
- Player must outpace AI growth
- Typical duration: 15-30 minutes

---

### Example 2: Accessing AI Decisions

```python
# Get top opponent
top_opponent = ai_manager.get_opponent_by_rank(0)

if top_opponent:
    stats = top_opponent.get_statistics()
    print(f"Leader: {stats['name']}")
    print(f"Net Worth: ${stats['net_worth']:,}")
    print(f"Strategy: {stats['personality']}")
    print(f"Goal: {stats['current_goal']}")
```

---

### Example 3: Market Analysis

```python
# Get market conditions
market = ai_manager.get_market_conditions()

# Strategic decisions based on market
if market['price_multiplier'] > 1.2:
    print("High prices! Good time to sell.")
    player.sell_inventory()

if market['demand'] > 1.5:
    print("High demand! Increase production.")
    player.increase_production()

if market['investigation_active']:
    print("Investigation! Reduce heat.")
    player.hide_operations()
```

---

### Example 4: Custom AI Difficulty

```python
# Create custom difficulty opponents
from entities.ai_factory import AIFactory, AIPersonality

# Easy opponent
easy_ai = AIFactory(
    name="Beginner Bot",
    personality=AIPersonality.CAUTIOUS,
    difficulty=0.2,
    starting_money=30000
)

# Hard opponent
hard_ai = AIFactory(
    name="Expert AI",
    personality=AIPersonality.AGGRESSIVE,
    difficulty=0.9,
    starting_money=70000
)

ai_manager.opponents.extend([easy_ai, hard_ai])
```

---

## Performance Considerations

### Optimization Tips

1. **Update Frequency**: AI makes decisions every 5-15 seconds (based on difficulty)
2. **Decision Caching**: Market conditions cached and shared
3. **Opponent Limit**: Maximum 5 opponents recommended
4. **Statistics Updates**: Rankings updated every frame, but heavy calculations done on decision ticks

### Scalability

**1-2 Opponents**: Minimal performance impact
**3-4 Opponents**: Recommended for most systems
**5 Opponents**: Maximum supported, may impact lower-end systems

---

## Strategy Guide

### Playing Against AI

#### Beating Aggressive AI
- Let them overextend
- Wait for market crashes
- Focus on efficiency over expansion
- Capitalize when they go bankrupt

#### Beating Cautious AI
- Expand faster early game
- Take calculated risks
- Build market share quickly
- Don't let them stabilize

#### Beating Opportunist AI
- Monitor market closely
- Beat them to good deals
- Build consistent production
- Don't rely on market timing

#### Beating Innovator AI
- Fast expansion early
- Volume over quality initially
- Tech race if long game
- Profit taking before they scale

---

## Troubleshooting

### AI Not Making Decisions

**Problem**: AI opponents idle, no actions
**Solution**: Ensure `update()` called with valid `dt` and `market_conditions`

```python
# Correct
ai_manager.update(dt=0.016, player_factory=player_stats)

# Incorrect
ai_manager.update(dt=0)  # No time passing
```

---

### Market Prices Stuck

**Problem**: Prices don't change
**Solution**: Market updates in AI manager `update()` method

```python
# Market updates automatically with AI manager
ai_manager.update(dt, player_stats)
```

---

### No Winner Declared

**Problem**: Game continues indefinitely
**Solution**: Check win condition thresholds

```python
# View current standings
leaderboard = ai_manager.get_leaderboard()
for entry in leaderboard:
    print(f"{entry['name']}: {entry['score']}")

# Check if threshold met
if WinCondition.NET_WORTH:
    # Need $1,000,000 net worth
```

---

## Future Enhancements

Potential additions:

1. **Personality Customization**: Player-created AI personalities
2. **Alliance System**: AI opponents can form temporary alliances
3. **Sabotage**: AI can sabotage competitors
4. **AI Learning**: AI adapts strategies based on player behavior
5. **Multiplayer**: Real players + AI opponents mixed
6. **Difficulty Profiles**: Named difficulty presets (Beginner, Veteran, Master)
7. **Historical Stats**: Track AI performance across multiple games
8. **AI Traits**: Additional personality modifiers (cautious + greedy, etc.)

---

## License

This AI opponent system is part of the Factory AI simulation project.

---

## Credits

**Strategic AI**: Finite state machine with goal-based planning
**Market Simulation**: Supply/demand economics model
**Decision Engine**: Personality-driven weighted random choices

---

**Last Updated**: 2025-11-15
**Version**: 1.0.0
**Author**: Factory AI Development Team
