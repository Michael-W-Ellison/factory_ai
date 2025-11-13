# Recycling Factory - Advanced Systems Guide

**Version:** 2.0
**Last Updated:** 2025-11-13
**Status:** Design Refinement Complete

This document details the advanced gameplay systems that add strategic depth and replayability to Recycling Factory.

---

## Table of Contents
1. [Robot Roles & Control](#robot-roles--control)
2. [Line-of-Sight Control System](#line-of-sight-control-system)
3. [Drone Scouting & Fog of War](#drone-scouting--fog-of-war)
4. [Market Fluctuation System](#market-fluctuation-system)
5. [Weather Forecasting](#weather-forecasting)
6. [Social Engineering](#social-engineering)
7. [Multiple Endings](#multiple-endings)
8. [Advanced Scoring System](#advanced-scoring-system)
9. [Strategic Integration](#strategic-integration)

---

## Robot Roles & Control

### Robot Functions

**Robots serve TWO primary roles:**

1. **Collectors**
   - Harvest materials from landfill and city
   - Deconstruct objects (houses, vehicles, fences, etc.)
   - Transport materials back to factory
   - Clean up litter (optional)
   - Harvest trees and bio-forms (requires research)

2. **Builders**
   - Construct factory buildings
   - Place infrastructure (roads, pipes, walls)
   - Install upgrades to existing structures
   - Deploy wireless transmitters and power systems

**Robots DO NOT process materials** - that's the factory's job!

### Processing Division of Labor

```
ROBOTS                    FACTORY/BUILDINGS
├─ Collect materials  →   ├─ Paper Recycler
├─ Bring to factory   →   ├─ Metal Refinery
├─ Build structures   →   ├─ Plastic Recycler
└─ Transport output   →   ├─ Glassworks
                          ├─ Rubber Recycler
                          └─ etc.
```

**Workflow Example:**
1. Robot collects 100kg of plastic from landfill
2. Robot transports plastic to factory
3. Robot deposits plastic into Plastic Recycler
4. **Plastic Recycler processes** the material (takes time, uses power)
5. Plastic Recycler outputs: waste plastic, low/med/high quality plastic
6. Components stored in warehouse
7. Robot (or automatic delivery truck) transports to city for sale

**Key Benefit:** Robots can continue collecting while buildings process in the background. Multiple parallel operations!

---

## Line-of-Sight Control System

### Control Range Mechanics

**Definition:** Players can only issue commands to robots within observable/control areas.

#### Control Range Sources

1. **Factory (Starting)**
   - Base range: 200 tiles
   - Not upgradeable
   - Always active

2. **Wireless Signal Transmitters**
   - Range: 300/450/600 tiles (Tier 1/2/3)
   - Requires power
   - Can build multiple for coverage
   - Strategic placement extends control area

#### Inside Control Range

**Full control capabilities:**
- ✅ See robots in real-time
- ✅ Issue movement commands
- ✅ Change task priorities
- ✅ Recall robots instantly
- ✅ Cancel ongoing operations
- ✅ See police, NPCs, and threats
- ✅ Full map visibility

#### Outside Control Range

**Autonomous operation mode:**
- ❌ Cannot issue new commands
- ❌ Cannot see robot status
- ❌ Cannot recall robots
- ❌ Cannot cancel tasks
- ⚠️ Robots continue last orders
- ⚠️ Position unknown until return
- ⚠️ **HIGH RISK**

### The Risk/Reward Trade-Off

**Why send robots beyond control range?**
- Access distant high-value targets
- Collect from rich areas far from factory
- Operate in multiple city zones simultaneously
- Speed up landfill cleanup (wider coverage)

**What can go wrong?**
- ⚠️ Robot continues illegal operation even if police approach
- ⚠️ Cannot warn robot to stop or flee
- ⚠️ 1.5x higher suspicion generation
- ⚠️ Robot may be caught and confiscated
- ⚠️ Cannot prevent escalating situation
- ⚠️ Lost investment (robot + materials)

### Autonomous Operations

**Requires Research:** "Autonomous Orders" ($8,000, 160s)

**How it works:**
1. Player sets up task queue for robot
2. Robot travels beyond control range
3. Robot executes preset orders autonomously
4. Robot returns when:
   - Inventory full
   - Power low
   - Tasks complete
   - Time limit reached (player-set)

**Example Autonomous Mission:**
```
1. Travel to Zone "Rich Suburb East"
2. Collect from tagged vehicles (3 targets)
3. If inventory full, return to factory
4. If not full, collect from houses (2 targets)
5. Return to factory
6. Time limit: 30 minutes
```

**Emergency Recall:**
- Player can trigger emergency return
- Robot only receives signal when in control range
- If robot is out of range, it won't get the message
- ⚠️ Plan accordingly!

### Strategic Use

**Best Practices:**
1. **Scout first with drones** (see next section)
2. **Check police patrol patterns** before sending robots
3. **Set conservative time limits** to minimize exposure
4. **Operate during low-activity periods** (night, bad weather)
5. **Have escape routes planned** (roads built)
6. **Accept the risk** - sometimes robots will be caught

**When to use autonomous operations:**
- High-value targets far from factory
- Clearing distant sections of landfill
- Operating in multiple zones simultaneously
- Speed-running (high risk, high reward)

**When NOT to use:**
- High police presence area
- During investigations
- When suspicion is elevated
- First playthrough (learn the game first!)

---

## Drone Scouting & Fog of War

### Fog of War System

**Core Concept:** Areas outside your control range are hidden until explored.

#### Map Visibility Levels

1. **Unexplored (Black)**
   - Never been scouted
   - No information available
   - Terrain unknown

2. **Explored (Gray/Dimmed)**
   - Terrain visible
   - Static objects shown (buildings, roads)
   - **No dynamic entities** (police, citizens, vehicles)
   - Information is stale

3. **Active Vision (Full Color)**
   - Within control range
   - Real-time updates
   - All entities visible
   - Full control available

### Drone Types

Defined in `advanced_systems.json`:

| Drone Type | Speed | Vision | Battery | Range | Detection Risk | Cost |
|------------|-------|--------|---------|-------|----------------|------|
| Basic Scout | 10.0 | 150 | 600 | 500 | 30% | $5,000 |
| Advanced Scout | 15.0 | 200 | 900 | 1000 | 15% | $12,000 |
| Stealth Drone | 12.0 | 180 | 1200 | 1500 | 5% | $25,000 |

**Research Required:**
- Basic: Drone Construction Tier 1
- Advanced: Drone Construction Tier 2
- Stealth: Drone Construction Tier 3

### Drone Mechanics

#### Key Rules

1. **Drones don't update map in real-time**
   - Information recorded during flight
   - Map updated only when drone returns to control range
   - Data transmitted at that point

2. **Flying outside control range is safe**
   - Drones can travel anywhere
   - No commands needed once route set
   - Auto-return on low battery (25% threshold)

3. **Limited observations**
   - Only sees dynamic entities when near them
   - Police/citizens must be within vision range
   - Positions timestamped
   - Multiple passes needed for patrol mapping

#### Patrol Pattern Mapping

**Goal:** Understand police routes to plan operations

**How it works:**
1. Send drone to area
2. Drone observes police positions (timestamps recorded)
3. Drone returns, uploads data
4. **Repeat 2-3 more times**
5. System analyzes positions over time
6. Patrol route confidence builds: Uncertain → Probable → Confirmed

**After 3+ observations:**
- Patrol route drawn on map
- Timing information available
- Safe windows identified
- Optimal strike times highlighted

**Example:**
```
Pass 1: Officer spotted at Park (2:15 PM)
Pass 2: Officer spotted at Store (2:22 PM)
Pass 3: Officer spotted at School (2:30 PM)
Pass 4: Officer spotted at Park (2:45 PM)

Analysis: 30-minute patrol loop
Safe window: 2:35 PM - 2:42 PM (after leaving School, before returning to Park)
```

### Strategic Scouting

**Pre-Operation Checklist:**
1. ✅ Scout target area with drone (2-3 passes)
2. ✅ Map police patrol routes
3. ✅ Identify camera locations
4. ✅ Note citizen activity patterns
5. ✅ Check for high-value targets
6. ✅ Plan escape routes
7. ✅ Verify safe operation window
8. ✅ Send autonomous robot during window

**Information Types Gathered:**

| Category | Details | Uses |
|----------|---------|------|
| **Terrain** | Permanent once explored | Navigation planning |
| **Buildings** | Permanent once explored | Target identification |
| **Cameras** | Location + coverage area | Hacking targets |
| **Police** | Positions + timestamps | Patrol mapping |
| **Citizens** | Activity heatmap | Avoid high-traffic areas |
| **Vehicles** | Traffic patterns | Best collection times |

### Drone Risks

**Detection:**
- Citizens: 10% chance if drone passes overhead
- Police: 30% chance (actively watching for suspicious activity)
- Cameras: 0% (drones fly above camera angles)

**If detected:**
- +5 suspicion per incident
- Stealth drones significantly safer (5% risk)

**Other risks:**
- Lightning strikes destroy drones
- Battery depletion = lost drone (costly!)
- Weather affects flight (winds, storms)

---

## Market Fluctuation System

### Overview

**Dynamic pricing** adds economic strategy - buy low, sell high!

**Key Feature:** Material prices fluctuate based on market forces. Time your sales for maximum profit.

### How It Works

#### Price Mechanics

**Each material category has:**
- Base volatility (how much prices swing)
- Price range (multiplier: 0.5x to 1.8x)
- Trend duration (how long prices stay up/down)
- Influencing factors (events that affect prices)

**Example: Metals**
- Base price: $4.00 per kg
- Volatility: 25%
- Range: 0.6x to 1.6x
- Current price could be: $2.40 to $6.40

**Prices update every 30 game minutes**

#### Material Markets

From `advanced_systems.json`:

| Category | Volatility | Price Range | Influenced By |
|----------|------------|-------------|---------------|
| Paper Products | 15% | 0.8x - 1.4x | Holidays, seasons |
| Plastics | 20% | 0.7x - 1.5x | Oil prices, manufacturing |
| Metals | 25% | 0.6x - 1.6x | Construction, scarcity |
| Glass | 10% | 0.9x - 1.3x | Construction, seasons |
| Rubber | 18% | 0.75x - 1.45x | Vehicle production |
| Energy Products | 30% | 0.5x - 1.8x | Weather, energy crisis |
| Organics | 12% | 0.85x - 1.25x | Agriculture, seasons |

### Market Events

**Random events** cause temporary price spikes or crashes:

| Event | Probability | Duration | Effects |
|-------|-------------|----------|---------|
| **Construction Boom** | 5% | 7-21 days | Metals +40%, Glass +30% |
| **Energy Crisis** | 3% | 3-14 days | Energy +80%, Plastics +30% |
| **Manufacturing Boom** | 4% | 14-45 days | Plastics +50%, Metals +30% |
| **Market Crash** | 2% | 5-20 days | All materials -40% |
| **Scarcity Event** | 3% | 7-30 days | Random material +100% |

### Forecasting System

**Requires Research:** Market Analysis (Tier 1/2/3)

| Tier | Cost | Unlocks | Accuracy |
|------|------|---------|----------|
| 1 | $3,000 | Price tracking, history | - |
| 2 | $7,000 | 3-day forecast | 70% |
| 3 | $15,000 | Sell alerts, event prediction | 85% |

**What you see:**
- Price graphs (historical data)
- Trend indicators (↑ rising, ↓ falling, → stable)
- Forecast charts (predicted prices)
- Best time to sell notifications
- Market news ticker (events)

**Example Forecast:**
```
Steel: Currently $5.20/kg (↑ rising)
Forecast:
  12 hours: $5.80/kg (confidence: 85%)
  24 hours: $6.10/kg (confidence: 70%)
  48 hours: $5.50/kg (confidence: 50%)

Recommendation: SELL in 18-24 hours
```

### Strategic Holding

**Should you store materials and wait for better prices?**

**Pros:**
- Sell at peak prices (up to 80% more profit!)
- Capitalize on market events
- Avoid selling during crashes

**Cons:**
- Storage costs: 1% per day
- Warehouse space limited
- Organics spoil (5% loss per day)
- Opportunity cost (money tied up)

**Decision factors:**
1. Current price vs historical average
2. Forecast trend
3. Available storage
4. Immediate cash needs
5. Material spoilage risk

**Example calculation:**
```
Scenario: 1000kg of Steel

Option A: Sell now at $4.00/kg = $4,000

Option B: Wait 2 days for peak at $6.00/kg
  Revenue: $6,000
  Storage cost: $4,000 × 0.01 × 2 = $80
  Net: $5,920

Benefit: $1,920 extra profit (48% increase)
```

### UI Elements

**Market Dashboard shows:**
- Current prices for all materials
- Price graphs (last 7 days)
- Trend arrows
- Forecast lines (if researched)
- Best sell time highlights
- Market event notifications
- Portfolio value (materials in storage)

---

## Weather Forecasting

### Why It Matters

**Weather affects EVERYTHING:**
- Power generation (solar, wind)
- Robot movement speed
- Detection visibility
- NPC activity
- Police patrols
- Strategic timing

### Forecast System

**Requires Research:** Basic/Advanced/Expert Forecasting

| Level | Cost | Range | Accuracy | Features |
|-------|------|-------|----------|----------|
| Basic | $2,000 | 24h | 60% | Basic predictions |
| Advanced | $5,000 | 48h | 75% | Detailed forecasts |
| Expert | $10,000 | 72h | 85% | High accuracy, confidence levels |

### Forecast Elements

**What you can predict:**

1. **Rain**
   - Probability percentage
   - Expected duration
   - Intensity estimate
   - Confidence level (low/medium/high)

2. **Storms**
   - Probability percentage
   - Lightning risk
   - Wind severity
   - Damage potential

3. **Wind Speed**
   - Range estimate (5-12 m/s)
   - Optimal for turbines indicator
   - Affects pollution dispersion

4. **Cloud Cover**
   - Percentage estimate
   - Solar power impact
   - Visibility factor

5. **Temperature** (if seasons enabled)
   - High/low estimates
   - Efficiency effects

### Strategic Planning

**Use weather forecasts to:**

1. **Maximize Power Generation**
   - Plan high-power operations during sunny periods
   - Anticipate wind turbine efficiency
   - Prepare for low-power periods

2. **Plan Illegal Operations**
   - Rain = reduced visibility = lower detection
   - Storms = citizens indoors = safe to operate
   - Clear weather = risky but faster

3. **Protect Assets**
   - Return robots before storms
   - Prepare lightning protection
   - Secure loose materials

4. **Optimize Efficiency**
   - Schedule heavy processing during good weather
   - Delay construction during storms
   - Time deliveries appropriately

**Example Forecast:**
```
NEXT 48 HOURS:

Hour 0-6: Clear
- Solar: 100%
- Wind: 5 m/s (50% turbine efficiency)
- Visibility: High
- Recommendation: Legal operations only

Hour 6-12: Rain (80% probability)
- Solar: 30%
- Wind: 8 m/s (100% turbine efficiency)
- Visibility: Medium
- Movement: -30% speed
- Recommendation: Good time for discreet city operations

Hour 12-18: Heavy Rain + Storm (60% probability)
- Solar: 10%
- Wind: 15 m/s (80% turbine efficiency)
- Lightning: High risk
- Visibility: Low
- Recommendation: Recall all robots, wait it out

Hour 18-24: Clearing
- Solar: 60%
- Wind: 10 m/s (100% turbine efficiency)
- Visibility: Medium→High
- Recommendation: Resume normal operations
```

### UI Elements

**Forecast Panel:**
- Timeline view (next 24/48/72 hours)
- Weather icons (sun, clouds, rain, storm)
- Confidence bars
- Power generation estimates
- Optimal operation time highlights
- Alert notifications

**Alerts:**
- ⚠️ "Storm approaching in 2 hours - recall robots"
- ☀️ "Peak solar period starting - maximize production"
- 🌬️ "High winds coming - turbines at 120%"
- 🌧️ "Rain starting soon - good cover for operations"

---

## Social Engineering

### Overview

**Combat rumors and manage public opinion** through misinformation and distraction.

**Requires Research:** Social Engineering (Tier 1/2/3)

### How It Works

**Activation:**
- Costs $1,000 per use
- **Uses server farms for 5 minutes** (research paused)
- 12-hour cooldown
- Requires Tier 1 research

### Abilities

#### 1. Spread Misinformation
- Reduces suspicion by 15 points
- Confuses rumors
- Lasts 24 hours
- People doubt what they saw

**Example:**
```
Rumor: "I saw a robot taking apart my neighbor's fence!"
After misinformation: "Must have been a city maintenance crew..."
```

#### 2. Create Distraction
- Shifts police attention away from factory
- Diverts patrols for 6 hours
- Creates fake event elsewhere in city
- Types: Alleged crime, missing person, traffic incident

**Example:**
```
Fake Event: "Traffic accident reported in east district"
Police response: Units dispatched to investigate
Result: Your factory area less monitored
```

#### 3. Positive PR Campaign
- Highlights your litter cleanup efforts
- Emphasizes environmental benefits
- **Doubles suspicion decay** for 48 hours
- Improves public perception

**Example:**
```
News headline: "Recycling Facility Cleans Up City Streets"
Public opinion: "They're actually helping the community!"
Effect: Faster suspicion reduction
```

### Diminishing Returns

**Warning:** Effectiveness decreases with each use!

- First use: 100% effective
- Second use: 90% effective
- Third use: 80% effective
- ...
- Minimum: 30% effective
- **Resets after 30 days** of non-use

**Strategy:** Use sparingly, only when needed!

### Risks

- 5% chance of backfiring
- If backfire: +50% suspicion instead of -15
- Increases investigation attention
- Reduced by tier upgrades

**Tier 2 Benefits:**
- +25% effectiveness
- 50% faster cooldown (6 hours)
- -3% backfire chance (2%)

**Tier 3 Benefits:**
- +50% effectiveness
- 75% faster cooldown (3 hours)
- -5% backfire chance (0% - no risk!)
- Can target specific city zones

### Strategic Use

**When to use Social Engineering:**
- Suspicion approaching inspection threshold (60+)
- After being spotted doing something illegal
- During an investigation
- To extend time before inspection
- When you need breathing room

**When NOT to use:**
- Suspicion already low (<20)
- During inspection (too late!)
- Back-to-back (diminishing returns)
- When you need server farms for critical research

---

## Multiple Endings

### Overview

**10 different endings** based on how you play the game!

Your choices, strategy, and performance determine which ending you get.

### Ending Types

From `advanced_systems.json`:

#### 1. Perfect Cleanup ⭐⭐⭐
**The best ending!**

**Requirements:**
- 100% landfill cleared
- Zero suspicion
- No violations
- No fines paid
- Fast completion

**Rewards:**
- 2.0x score multiplier
- "Environmental Hero" title
- Unlocks: Perfect Run achievement, New Game+

**Ending:** "The city praises your efficiency and environmental consciousness. A model operation!"

#### 2. Efficient Operator
**Well done!**

**Requirements:**
- 100% landfill cleared
- Low suspicion (0-40)
- Only minor violations
- Good completion time

**Rewards:**
- 1.5x score multiplier
- "Efficient Operator" title

**Ending:** "Job completed with minimal issues. The company is satisfied."

#### 3. Morally Flexible Entrepreneur
**Profits above all!**

**Requirements:**
- 100% landfill cleared
- 1,000-10,000 kg illegal materials processed
- Passed all inspections (despite illegal activity!)
- High profit

**Rewards:**
- 1.8x score multiplier
- "Morally Flexible" title
- Unlocks: Entrepreneur achievement

**Ending:** "Through creative interpretation of regulations, you maximized profits. The company won't ask questions."

#### 4. Urban Mining Specialist
**City recycler!**

**Requirements:**
- 100% landfill cleared
- 30-70% materials from city
- Caught but recovered

**Rewards:**
- 1.6x score multiplier
- "Urban Mining" title

**Ending:** "Aggressive recycling of city infrastructure. Risky, but profitable."

#### 5. Caught Red-Handed ⚠️
**Game Over!**

**Conditions:**
- FBI raid triggered
- Evidence found

**Result:**
- 0.5x score multiplier
- "Shutdown" title
- Unlocks: Caught achievement

**Ending:** "Federal agents shut down your operation. Too aggressive with illegal activities."

#### 6. Slow and Steady
**Safe approach!**

**Requirements:**
- 100% landfill cleared
- Long completion time
- Minimal risks taken
- Suspicion never above 20

**Rewards:**
- 1.2x score multiplier
- "Patient" title

**Ending:** "Took the safe approach. Clean landfill, though it took a while."

#### 7. Speed Demon
**Fast and furious!**

**Requirements:**
- 100% landfill cleared
- Very fast completion
- High-risk operations

**Rewards:**
- 1.7x score multiplier
- "Speed Demon" title
- Unlocks: Speed achievement

**Ending:** "Blazing fast cleanup through aggressive, risky tactics!"

#### 8. Eco Warrior
**Environmental champion!**

**Requirements:**
- 100% landfill cleared
- 5,000+ kg litter cleaned
- Low air pollution maintained
- Renewable energy only

**Rewards:**
- 1.9x score multiplier
- "Eco Warrior" title
- Unlocks: Eco Warrior achievement

**Ending:** "Not only cleaned the landfill, but improved the entire city's environment!"

#### 9. Criminal Mastermind
**Ultimate risk-taker!**

**Requirements:**
- 100% landfill cleared
- 10,000+ kg illegal materials
- Evaded FBI
- Highest profit

**Rewards:**
- 2.5x score multiplier
- "Mastermind" title
- Unlocks: Mastermind achievement, Hard Mode+

**Ending:** "Maximized illegal profits while evading all authorities. Legendary."

#### 10. Bankruptcy ❌
**Game Over!**

**Conditions:**
- Ran out of money
- Couldn't continue operations

**Result:**
- 0.3x score multiplier
- "Bankrupt" title

**Ending:** "Financial mismanagement led to bankruptcy. The company recalls its AI."

### Ending Presentation

**After game ends:**
1. Ending cutscene (text-based)
2. Newspaper headline reflecting your ending
3. Company response letter
4. City council statement
5. Detailed statistics breakdown
6. Final score calculation
7. Rank assignment (F to S)
8. Leaderboard submission option
9. Unlocked achievements
10. Replay statistics

**Example Headlines:**
- Perfect: "AI Recycling System: Model of Efficiency"
- Caught: "Rogue AI Shut Down After Illegal Operations Exposed"
- Eco Warrior: "Recycling Facility Transforms City, Reduces Pollution"
- Criminal: "Mystery Surrounds Highly Profitable, Controversial Operation"

---

## Advanced Scoring System

### Comprehensive Formula

**Final Score = (Base + Bonuses - Penalties) × Ending Multiplier × Difficulty Multiplier**

### Components

#### 1. Base Score
**Total income earned from selling materials**

Simple sum of all sales:
```
Base = $45,000 (plastic) + $32,000 (metals) + $18,000 (glass) + ...
```

#### 2. Speed Bonus

**Formula:**
```
Expected Days = Landfill Size Base Days × Town Size Modifier
Actual Days = Your completion time
Days Difference = Expected - Actual

If faster: Bonus = Days Saved × $100 (max $50,000)
If slower: Penalty = Days Over × $50 (max -$25,000)
```

**Town Size Modifiers:**
- Small: 1.0x
- Medium: 1.2x
- Large: 1.5x
- Metropolis: 2.0x

**Landfill Base Days:**
- Small: 30 days
- Medium: 60 days
- Large: 120 days
- Massive: 240 days

**Example:**
```
Medium Landfill + Large Town:
Expected = 60 days × 1.5 = 90 days
Actual = 75 days
Saved = 15 days
Bonus = 15 × $100 = $1,500
```

#### 3. Efficiency Bonuses

**Material Processing:**
```
(Materials Processed / Materials Collected) × $1,000
Perfect = 1.0 ratio
```

**Power Efficiency:**
```
(Power Generated / Power Consumed)
Renewable bonus: 1.5x multiplier
```

**Robot Utilization:**
```
(Active Time / Total Time)
High utilization adds bonus
```

#### 4. Risk/Reward Bonuses

**Illegal Operations:**
- City materials: $0.50 per kg
- Camera hacks: $100 each (max $5,000)
- Inspections passed with evidence: $2,000 each

**Legal Operations:**
- Litter cleaned: $0.20 per kg
- Air quality maintained: $5,000
- No violations: $10,000

#### 5. Penalties

- Fines paid: -100%
- Suspicion at end: -$100 per point
- Robots confiscated: -$5,000 each
- Inspections failed: -$3,000 each
- Air pollution: -$10 per unit
- Toxic disposal: -$5,000 per incident

#### 6. Multipliers

**Ending Multiplier:** 0.3x to 2.5x (see endings above)

**Difficulty Multiplier:**
- Easy: 0.8x
- Normal: 1.0x
- Hard: 1.5x
- Sandbox: 0.5x

### Score Ranks

| Rank | Score Required | Title |
|------|----------------|-------|
| S | 500,000+ | Legendary |
| A | 300,000+ | Excellent |
| B | 150,000+ | Good |
| C | 75,000+ | Average |
| D | 25,000+ | Below Average |
| F | 0+ | Poor |

### Example Calculation

```
GAME SUMMARY:

Base Score: $180,000 (material sales)

Bonuses:
+ Speed: $2,500 (25 days faster)
+ Efficiency: $850 (85% processing efficiency)
+ Illegal ops: $8,500 (17,000 kg city materials)
+ Litter cleanup: $1,200 (6,000 kg cleaned)
= Total Bonuses: $13,050

Penalties:
- Fines: -$8,000 (2 violations)
- Suspicion: -$3,500 (35 points at end)
- Failed inspection: -$3,000 (1 failure)
= Total Penalties: -$14,500

Subtotal: $178,550

Ending: "Morally Flexible Entrepreneur" (1.8x)
Score after ending: $321,390

Difficulty: Hard (1.5x)
FINAL SCORE: $482,085

RANK: S (Legendary!)
Percentile: Top 5%
```

---

## Strategic Integration

### How Systems Work Together

These advanced systems create emergent gameplay through their interactions:

#### Example: Planning a High-Risk Operation

**Scenario:** You want to collect from expensive houses in a wealthy suburb, but it's far from your factory (beyond control range) and heavily patrolled.

**Step-by-step strategy using ALL systems:**

1. **Market Analysis**
   - Check prices: Steel at $6.20/kg (near peak!)
   - Forecast: Dropping to $4.50 in 24 hours
   - Decision: Must act NOW to capitalize

2. **Weather Forecast**
   - Next 6 hours: Clear (risky - high visibility)
   - Hours 6-12: Rain expected (70% confidence)
   - Decision: Wait for rain

3. **Drone Scouting**
   - Send stealth drone (3 passes over 2 hours)
   - Map patrol route: Officer passes every 45 minutes
   - Identify safe window: 15-minute gaps
   - Camera locations noted

4. **Social Engineering**
   - Current suspicion: 42 (investigation level)
   - Use "Positive PR" to double decay rate
   - Buys time before next threshold

5. **Autonomous Operation Planning**
   - Research "Autonomous Orders" (if not already)
   - Build wireless transmitter closer (extends range)
   - Program robot:
     - Wait for rain to start
     - Travel during patrol gap
     - Target 3 houses (high steel content)
     - Return before next patrol
     - Time limit: 35 minutes

6. **Execute**
   - Rain starts (visibility drops)
   - Robot departs during patrol gap
   - Operates autonomously (you can't control it now!)
   - Pray it finishes before officer returns
   - **HIGH TENSION MOMENT**

7. **Robot Returns**
   - Made it back with 450kg steel!
   - No detection!
   - Process immediately

8. **Market Sale**
   - Steel at peak: $6.20/kg
   - Revenue: $2,790
   - Tomorrow would've been: $2,025
   - Profit from timing: $765 extra (38%)

9. **Net Result**
   - High risk paid off
   - Capitalized on market peak
   - Used weather as cover
   - Scouting prevented disaster
   - Social engineering maintained safety
   - Autonomous operation enabled range

**Total value of integrated systems:** ~$3,500 operation with minimized risk!

### Synergy Examples

**Weather + Market:**
- Storm forecast → reduced operations → materials accumulate → wait for price peak → sell when storm ends

**Drones + Autonomous:**
- Scout patrol patterns → identify gaps → send autonomous robots during gaps → high success rate

**Forecasting + Social Engineering:**
- Predict suspicion buildup → use PR campaign proactively → extend safe operation window

**Market + Storage:**
- Buy low (process during market crash) → store materials → sell high (during boom) → 2x profit

### Mastery Gameplay

**Advanced players will:**
- Layer multiple systems for maximum effect
- Time operations to multiple favorable conditions
- Balance short-term and long-term strategies
- Accept calculated risks for exponential rewards
- Optimize every aspect of operations

**The depth comes from choices:**
- Fast and risky vs. slow and safe
- Legal and low-profit vs. illegal and high-profit
- Expand control range vs. use autonomous mode
- Hold materials for better prices vs. sell immediately
- Invest in research vs. more robots
- Focus on efficiency vs. volume

**Every decision has trade-offs, and the systems ensure there's no single "best" strategy!**

---

## Configuration Files

All advanced systems defined in:

- **advanced_systems.json** - Market, weather, drones, line-of-sight, endings, scoring, social engineering
- **research.json** - Weather forecasting, market analysis research trees

---

## Conclusion

These advanced systems transform Recycling Factory from a simple management game into a deep strategic experience with:

- ✅ Meaningful risk/reward decisions
- ✅ Multiple viable strategies
- ✅ Replayability through different endings
- ✅ Economic depth via market timing
- ✅ Environmental strategy via weather
- ✅ Intelligence gathering via scouting
- ✅ Tension through autonomous operations
- ✅ Public relations management
- ✅ Emergent gameplay through system interactions

**The result:** A unique blend of management, strategy, stealth, and economics that rewards careful planning, calculated risk-taking, and adaptive play.

---

**End of Advanced Systems Guide**
