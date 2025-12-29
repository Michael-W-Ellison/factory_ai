# Recycling Factory - Project Overview

Welcome to the **Recycling Factory** game project! This document provides a quick overview of the project structure and how to get started.

---

## What is This Game?

An AI-controlled automated recycling factory management game where you balance profit-making with avoiding detection while recycling materials from a landfill and potentially the nearby city.

**Genre:** Top-down RTS/Management Simulation with Stealth elements

---

## Quick Start

### Prerequisites
1. **Python 3.10+** - [Download here](https://www.python.org/downloads/)
2. **Pygame 2.5+** - Install with: `pip install pygame`
3. **Git** - [Download here](https://git-scm.com/)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd factory_ai

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

### Current Status
This project is in **late beta** with ~75% of features complete. All core gameplay systems are implemented and functional. The game includes 128 Python source files, 40 game systems, and 56 test files.

---

## Project Structure

```
factory_ai/
├── main.py                 # Entry point - run this to start the game
├── config.py              # Game settings and configuration
├── requirements.txt       # Python dependencies
│
├── docs/                  # Documentation
│   ├── GAME_DESIGN_DOCUMENT.md       # Complete game design
│   ├── TECHNICAL_DESIGN_DOCUMENT.md  # Technical architecture
│   ├── DEVELOPMENT_ROADMAP.md        # Step-by-step development guide
│   └── TECHNOLOGY_STACK.md           # Learning resources and setup
│
├── src/                   # Source code
│   ├── core/              # Core game engine
│   │   ├── game.py        # Main game class and loop
│   │   └── constants.py   # Game constants and enums
│   │
│   ├── entities/          # Game entities (robots, NPCs, buildings)
│   ├── systems/           # Game systems (resources, detection, etc.)
│   ├── world/             # World management (grid, city, factory)
│   ├── ai/                # AI behaviors (pathfinding, robot/NPC AI)
│   ├── ui/                # User interface components
│   ├── rendering/         # Rendering system
│   └── utils/             # Utility functions
│
├── data/                  # Game data
│   ├── config/            # Configuration files (JSON)
│   ├── saves/             # Save game files
│   └── assets/            # Graphics, sounds, etc.
│
└── tests/                 # Unit tests (to be added)
```

---

## Key Documents

**Start here if you're new:**

1. **[TECHNOLOGY_STACK.md](docs/TECHNOLOGY_STACK.md)**
   - Installation guide
   - Learning resources for Python and Pygame
   - Practice projects to build skills

2. **[DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md)**
   - Step-by-step development phases
   - Estimated timelines
   - Completion checklists

3. **[GAME_DESIGN_DOCUMENT.md](docs/GAME_DESIGN_DOCUMENT.md)**
   - Complete game design specification
   - All systems explained in detail
   - Gameplay mechanics

4. **[TECHNICAL_DESIGN_DOCUMENT.md](docs/TECHNICAL_DESIGN_DOCUMENT.md)**
   - Software architecture
   - Data structures and algorithms
   - Code examples

---

## Development Phases

The game is built in phases. The project is currently at **Phase 14 (Balance & Polish)**.

### Completed Phases:
- ✅ Phase 0: Learning & Setup
- ✅ Phase 1-3: Core Foundation & Robot Systems
- ✅ Phase 4: Building System (32 building types)
- ✅ Phase 5: Material Processing & Components
- ✅ Phase 6: Research System (130+ technologies)
- ✅ Phase 7: City & Detection System
- ✅ Phase 8: Camera & Inspection System
- ✅ Phase 9: Authority & FBI System
- ✅ Phase 10: Advanced Features (drones, weather, market)
- ✅ Phase 11: UI/UX (functional)
- ✅ Phase 13: Save/Load System

### Current Focus:
- 🔄 Phase 12: Audio (not yet implemented)
- 🔄 Phase 14: Balance & Polish
- 🔄 Phase 15: Launch Preparation

See [DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md) for complete details.

---

## Current Features

**Core Systems (Complete):**
- ✅ Game engine with 60 FPS game loop
- ✅ Grid-based world (100x75 tiles)
- ✅ Camera controls (WASD, zoom)
- ✅ Entity management system
- ✅ A* pathfinding

**Gameplay Systems (Complete):**
- ✅ 43 entity types (robots, NPCs, vehicles, buildings)
- ✅ 32 building types with power/processing
- ✅ Material collection and processing
- ✅ Component manufacturing
- ✅ Research tree (130+ technologies)

**City & Detection (Complete):**
- ✅ Procedural city generation
- ✅ NPCs with daily schedules
- ✅ Police patrols and chases
- ✅ Suspicion and detection system
- ✅ Security cameras with hacking
- ✅ Inspection mechanics
- ✅ FBI investigation system

**Advanced Features (Complete):**
- ✅ Weather system
- ✅ Market price fluctuations
- ✅ Drone surveillance
- ✅ Traffic simulation
- ✅ Bus transportation
- ✅ Animal ecosystem (8 species)
- ✅ AI opponents
- ✅ Complete save/load
- ✅ Day/night cycle

**Remaining Work:**
- 🔄 Audio/music integration
- 🔄 Final balance tuning
- 🔄 Distribution packaging

---

## How to Use This Project

### If You're New to Programming:
1. Read [TECHNOLOGY_STACK.md](docs/TECHNOLOGY_STACK.md) first
2. Complete the learning resources (Python, then Pygame)
3. Do the practice projects
4. Start Phase 1 of the roadmap

### If You Know Python/Pygame:
1. Skim [GAME_DESIGN_DOCUMENT.md](docs/GAME_DESIGN_DOCUMENT.md) to understand the game
2. Read [TECHNICAL_DESIGN_DOCUMENT.md](docs/TECHNICAL_DESIGN_DOCUMENT.md) for architecture
3. Follow [DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md) starting at Phase 1
4. Build the game incrementally!

---

## Customization

You can customize the game by modifying `config.py`:

```python
# Display settings
SCREEN_WIDTH = 1280      # Window width
SCREEN_HEIGHT = 720      # Window height
FPS = 60                 # Frames per second

# Game settings
STARTING_MONEY = 10000   # Starting budget
STARTING_ROBOTS = 2      # Number of robots at start

# Debug settings
DEBUG_MODE = True        # Enable debug features
SHOW_FPS = True          # Display frame rate
```

---

## Getting Help

### Resources
- **Documentation:** See `docs/` folder
- **Python Help:** [python.org](https://www.python.org/doc/)
- **Pygame Help:** [pygame.org](https://www.pygame.org/docs/)

### Communities
- r/pygame on Reddit
- r/gamedev on Reddit
- Pygame Discord server
- Stack Overflow

### Tips
- Read error messages carefully
- Use `print()` statements to debug
- Test frequently as you build
- Commit your code often with Git
- Take breaks when stuck

---

## License

[Add your license here]

---

## Credits

Game design and development: [Your name]

Built with Python and Pygame.

---

**Ready to contribute?** See [DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md) for the remaining tasks in Phases 12, 14, and 15!

The game is feature-complete and ready for playtesting and polish.
