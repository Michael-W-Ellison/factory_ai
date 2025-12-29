# Recycling Factory

An AI-controlled automated recycling factory management game built with Python and Pygame.

![Status](https://img.shields.io/badge/status-beta-green)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Pygame](https://img.shields.io/badge/pygame-2.5+-green)
![Completion](https://img.shields.io/badge/completion-75%25-brightgreen)

---

## About

**Recycling Factory** is a top-down RTS/management simulation game where you play as an AI in control of an automated robotic recycling factory. Your goal is to make a profit by recycling materials from a landfill while avoiding detection from authorities when engaging in... less-than-legal activities.

### Key Features (Implemented)
- Autonomous robot management with A* pathfinding
- Complex material processing system with 15+ material types
- Factory building and expansion (32 building types)
- Research and technology upgrades (130+ technologies)
- Dynamic procedurally-generated city with NPCs
- Police patrols and detection mechanics
- Authority escalation system with FBI investigations
- Security camera system with hacking capabilities
- Inspection system with pass/fail consequences
- Power generation and management
- Economic simulation with market fluctuations
- Weather system affecting gameplay
- Traffic simulation with vehicles and buses
- Animal ecosystem with 8 species
- AI opponent system for competitive play
- Complete save/load functionality
- Day/night cycle with time progression

---

## Quick Start

### Prerequisites
- Python 3.10 or higher
- Pygame 2.5 or higher

### Installation

```bash
# Clone the repository
git clone https://github.com/Michael-W-Ellison/factory_ai.git
cd factory_ai

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

---

## Current Status

**Phase:** Late Beta - Feature Complete

This project has implemented the majority of planned features across all development phases. The game includes:

**Core Systems (Complete):**
- Game engine with 60 FPS game loop
- Grid-based world (100x75 tiles)
- Camera controls and rendering
- Entity management system

**Gameplay Systems (Complete):**
- 40+ game systems implemented
- 43 entity types
- 32 building types
- Full research tree
- Material processing pipeline
- Power and resource management

**City & Detection (Complete):**
- Procedural city generation
- NPC schedules and behaviors
- Police patrols and chases
- Suspicion tiers and escalation
- Security cameras with hacking
- Inspection mechanics
- FBI investigation system

**Advanced Features (Complete):**
- Weather effects
- Market price fluctuations
- Drone surveillance
- Traffic simulation
- Bus transportation
- Animal ecosystem
- AI opponents
- Scoring system

**Remaining Work:**
- Audio/music integration
- Final balance tuning
- Distribution packaging

See [DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md) for detailed progress.

---

## Documentation

Comprehensive documentation is available in the `docs/` folder:

- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Quick project overview and getting started
- **[GAME_DESIGN_DOCUMENT.md](docs/GAME_DESIGN_DOCUMENT.md)** - Complete game design specification
- **[TECHNICAL_DESIGN_DOCUMENT.md](docs/TECHNICAL_DESIGN_DOCUMENT.md)** - Technical architecture and implementation
- **[DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md)** - Step-by-step development guide
- **[TECHNOLOGY_STACK.md](docs/TECHNOLOGY_STACK.md)** - Technology choices and learning resources
- **[COMPREHENSIVE_TODO.md](COMPREHENSIVE_TODO.md)** - Detailed task tracking

---

## Project Structure

```
factory_ai/
├── main.py                    # Game entry point
├── config.py                  # Configuration settings
├── src/                       # Source code (128 Python files)
│   ├── core/                  # Core game engine
│   ├── entities/              # Game entities (43 files)
│   │   └── buildings/         # Building types (23 files)
│   ├── systems/               # Game systems (40 files)
│   ├── world/                 # World management
│   ├── ai/                    # AI behaviors
│   ├── ui/                    # User interface (14 files)
│   ├── graphics/              # Graphics and sprites
│   └── rendering/             # Rendering system
├── data/                      # Game data and assets
│   ├── config/                # JSON configuration files
│   └── saves/                 # Save game directory
├── docs/                      # Technical documentation
└── test_*.py                  # Test files (56 files)
```

---

## Controls

| Key | Action |
|-----|--------|
| WASD | Move camera |
| Arrow Keys | Alternative camera movement |
| Mouse Wheel | Zoom in/out |
| B | Building menu |
| R | Research menu |
| M | Map view |
| ESC | Pause menu |
| F5 | Quick save |
| F9 | Quick load |
| F1 | Help/Controls |

---

## Configuration

Edit `config.py` to customize game settings:

```python
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
STARTING_MONEY = 10000
STARTING_ROBOTS = 2
DEBUG_MODE = True
```

---

## Building Standalone Executables

### Quick Build

```bash
# Install build dependencies
pip install -r requirements-dev.txt

# Build standalone executable
python build.py
```

The executable will be created at `dist/RecyclingFactory` (Linux/Mac) or `dist/RecyclingFactory.exe` (Windows).

### Build Options

| Command | Description |
|---------|-------------|
| `python build.py` | Single-file executable (~18 MB) |
| `python build.py --onedir` | Directory build (faster, ~42 MB) |
| `python build.py --debug` | With console window for debugging |
| `python build.py --clean` | Remove build artifacts |

### Creating Installers

```bash
# Build executable + platform installer
python build_installer.py

# Build installer only (if executable exists)
python build_installer.py --installer-only
```

**Windows:** Creates `dist/installer/RecyclingFactory_Setup_1.0.0.exe` (requires [Inno Setup](https://jrsoftware.org/isdl.php))

**Linux:** Creates `dist/RecyclingFactory_Linux.tar.gz` with desktop integration:
```bash
tar -xzf RecyclingFactory_Linux.tar.gz
cd RecyclingFactory_Linux
./install.sh
```

---

## Development

### Running Tests

```bash
# Run all tests
python -m pytest test_*.py

# Run specific test
python -m pytest test_building_system.py
```

### Contributing

This is currently a solo development project. If you'd like to contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## Codebase Statistics

| Metric | Count |
|--------|-------|
| Total Files | 232 |
| Python Source Files | 128 |
| Test Files | 56 |
| Systems Implemented | 40 |
| Entity Types | 43 |
| Building Types | 32 |
| Lines of Code | ~50,000+ |

---

## License

[Add license information here]

---

## Credits

**Developer:** Michael W. Ellison

**Built With:**
- [Python](https://www.python.org/)
- [Pygame](https://www.pygame.org/)

---

## Contact

- GitHub: [@Michael-W-Ellison](https://github.com/Michael-W-Ellison)
- Issues: [GitHub Issues](https://github.com/Michael-W-Ellison/factory_ai/issues)

---

**Status:** Beta - Feature Complete, Polishing in Progress
