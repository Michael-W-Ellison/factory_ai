# Recycling Factory - Technology Stack & Learning Path

**Version:** 1.0
**Last Updated:** 2025-11-13
**Target:** Solo Developer with Limited Programming Experience

---

## Table of Contents
1. [Technology Stack Overview](#technology-stack-overview)
2. [Why Python & Pygame?](#why-python--pygame)
3. [Installation Guide](#installation-guide)
4. [Learning Path](#learning-path)
5. [Essential Python Concepts](#essential-python-concepts)
6. [Essential Pygame Concepts](#essential-pygame-concepts)
7. [Development Tools](#development-tools)
8. [Resources & References](#resources--references)
9. [Practice Projects](#practice-projects)

---

## Technology Stack Overview

### Core Technologies

| Technology | Purpose | Why This Choice |
|------------|---------|-----------------|
| **Python 3.10+** | Programming Language | Easy to learn, great for beginners, powerful |
| **Pygame 2.5+** | Game Framework | Beginner-friendly, well-documented, 2D games |
| **Git** | Version Control | Track changes, backup code |
| **VS Code** | Code Editor | Free, powerful, Python support |

### Optional Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **Pygame GUI** | UI Toolkit | If building complex menus |
| **PyInstaller** | Distribution | Package game for others |
| **Tiled Map Editor** | Level Design | If creating complex maps |
| **Piskel/Aseprite** | Sprite Creation | Creating game graphics |

---

## Why Python & Pygame?

### Python Advantages
✅ **Beginner-Friendly:** Clear, readable syntax
✅ **Powerful:** Can build complex games
✅ **Great Documentation:** Tons of tutorials and help
✅ **Large Community:** Easy to get help when stuck
✅ **Cross-Platform:** Works on Windows, Mac, Linux

### Pygame Advantages
✅ **Designed for Games:** Built specifically for game development
✅ **2D Focus:** Perfect for top-down games like this one
✅ **Complete Toolkit:** Graphics, sound, input, all included
✅ **Active Community:** Lots of examples and tutorials
✅ **Free & Open Source:** No licensing costs

### Alternatives Considered

| Alternative | Why Not Chosen |
|-------------|----------------|
| **Unity (C#)** | Steeper learning curve, overkill for 2D |
| **Godot** | Excellent choice, but said "from scratch" |
| **JavaScript/HTML5** | Good option, but Python easier for beginners |
| **C++/SDL** | Too complex for limited programming background |

**Bottom Line:** Python + Pygame is the best balance of power and ease-of-learning for this project.

---

## Installation Guide

### Step 1: Install Python

#### Windows
1. Go to [python.org](https://www.python.org/downloads/)
2. Download Python 3.10 or newer (latest stable version)
3. Run installer
4. **IMPORTANT:** Check "Add Python to PATH" during installation
5. Click "Install Now"

Verify installation:
```bash
python --version
```
Should show: `Python 3.10.x` or higher

#### macOS
1. Go to [python.org](https://www.python.org/downloads/)
2. Download macOS installer
3. Run installer
4. Follow prompts

Or use Homebrew:
```bash
brew install python@3.10
```

Verify:
```bash
python3 --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.10 python3-pip
```

Verify:
```bash
python3 --version
```

### Step 2: Install Pygame

Open terminal/command prompt:

```bash
pip install pygame
```

Or on macOS/Linux:
```bash
pip3 install pygame
```

Verify installation:
```bash
python -c "import pygame; print(pygame.version.ver)"
```

Should show Pygame version (2.5.0 or newer).

### Step 3: Install VS Code

1. Go to [code.visualstudio.com](https://code.visualstudio.com/)
2. Download for your operating system
3. Install
4. Open VS Code

### Step 4: Configure VS Code for Python

1. Open VS Code
2. Click Extensions icon (left sidebar) or press `Ctrl+Shift+X`
3. Search for "Python"
4. Install "Python" extension by Microsoft
5. Restart VS Code

### Step 5: Install Git

#### Windows
1. Go to [git-scm.com](https://git-scm.com/)
2. Download Windows installer
3. Install with default options

#### macOS
```bash
brew install git
```

Or download from [git-scm.com](https://git-scm.com/)

#### Linux
```bash
sudo apt install git
```

Verify:
```bash
git --version
```

### Step 6: Configure Git

Set your name and email:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 7: Test Everything

Create a test file `test.py`:
```python
import pygame

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Test Window")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 128, 255))  # Sky blue
    pygame.display.flip()

pygame.quit()
print("Success! Everything is working.")
```

Run it:
```bash
python test.py
```

You should see a blue window. If so, you're ready to start!

---

## Learning Path

### Phase 0: Absolute Basics (Week 1-2)

**Goal:** Understand basic programming concepts

#### Python Fundamentals
- [ ] Variables and data types
- [ ] Basic math operations
- [ ] Strings and string formatting
- [ ] User input and output
- [ ] If/else statements
- [ ] Loops (for and while)

**Resources:**
- [Python.org Official Tutorial](https://docs.python.org/3/tutorial/)
- [Codecademy Python Course](https://www.codecademy.com/learn/learn-python-3) (Free)
- "Python Crash Course" by Eric Matthes (Book)

**Practice:**
- Write a calculator program
- Create a number guessing game
- Build a simple text-based adventure game

### Phase 0.5: Python Intermediate (Week 3-4)

**Goal:** Learn Python features needed for game development

#### Topics
- [ ] Functions and parameters
- [ ] Lists and dictionaries
- [ ] Classes and objects (basic OOP)
- [ ] File I/O (reading/writing files)
- [ ] Error handling (try/except)
- [ ] Modules and imports

**Resources:**
- [Real Python - OOP in Python](https://realpython.com/python3-object-oriented-programming/)
- [Python OOP Tutorial (YouTube)](https://www.youtube.com/watch?v=ZDa-Z5JzLYM)

**Practice:**
- Create a class for a "Player" with health, inventory
- Build a simple inventory management system
- Create a to-do list program that saves to a file

### Phase 1: Pygame Basics (Week 5-6)

**Goal:** Learn Pygame fundamentals

#### Topics
- [ ] Creating a game window
- [ ] Game loop (update, render)
- [ ] Drawing shapes (rectangles, circles, lines)
- [ ] Colors and coordinates
- [ ] Handling events (keyboard, mouse)
- [ ] Frame rate and timing

**Resources:**
- [Pygame Documentation](https://www.pygame.org/docs/)
- [Real Python - Pygame Primer](https://realpython.com/pygame-a-primer/)
- [Tech With Tim - Pygame Tutorials (YouTube)](https://www.youtube.com/watch?v=jO6qQDNa2UY&list=PLzMcBGfZo4-lp3jAExUCewBfMx3UZFkh5)

**Practice:**
See [Practice Projects](#practice-projects) section below.

### Phase 2: Game Development Concepts (Week 7-8)

**Goal:** Learn patterns used in game development

#### Topics
- [ ] Sprite classes
- [ ] Collision detection
- [ ] State machines
- [ ] Game states (menu, playing, paused)
- [ ] Simple physics (velocity, acceleration)
- [ ] Basic AI (pathfinding basics)

**Resources:**
- "Making Games with Python & Pygame" (Free e-book)
- [Game Programming Patterns](http://gameprogrammingpatterns.com/) (Book)

**Practice:**
- Build a simple platformer
- Create Pong or Breakout clone
- Make a simple top-down shooter

---

## Essential Python Concepts

### 1. Variables and Data Types

```python
# Numbers
score = 100
money = 1500.50

# Strings
player_name = "AI Factory"
message = "Collecting materials..."

# Booleans
is_running = True
game_over = False

# Lists
materials = ["plastic", "metal", "glass"]
inventory = [10, 20, 15]

# Dictionaries
robot_stats = {
    "speed": 5,
    "capacity": 100,
    "power": 1000
}
```

### 2. Functions

```python
def calculate_profit(materials, price_per_unit):
    """Calculate total profit from materials"""
    return materials * price_per_unit

profit = calculate_profit(50, 10)  # Returns 500
print(f"Profit: ${profit}")
```

### 3. Classes and Objects

```python
class Robot:
    """Represents a robot collector"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.inventory = {}

    def move(self, dx, dy):
        """Move robot by delta x and y"""
        self.x += dx
        self.y += dy

    def collect(self, material, amount):
        """Add material to inventory"""
        if material not in self.inventory:
            self.inventory[material] = 0
        self.inventory[material] += amount

# Create robot instance
my_robot = Robot(100, 100)
my_robot.move(10, 0)  # Move right 10 pixels
my_robot.collect("plastic", 50)
```

### 4. Lists and Loops

```python
# List of robots
robots = [Robot(0, 0), Robot(50, 50), Robot(100, 100)]

# Loop through robots
for robot in robots:
    robot.move(5, 0)  # Move all robots right

# Loop with index
for i in range(10):
    print(f"Number: {i}")

# While loop
while game_running:
    update_game()
    render_game()
```

### 5. Dictionaries

```python
# Material storage
materials = {
    "plastic": 100,
    "metal": 50,
    "glass": 25
}

# Access value
plastic_amount = materials["plastic"]

# Add/Update
materials["wood"] = 75
materials["plastic"] += 10  # Add 10 more

# Check if key exists
if "metal" in materials:
    print(f"Metal: {materials['metal']}")

# Loop through dictionary
for material, amount in materials.items():
    print(f"{material}: {amount}")
```

### 6. Conditionals

```python
if suspicion_level > 80:
    trigger_inspection()
elif suspicion_level > 50:
    increase_police_patrols()
else:
    normal_operation()

# Ternary operator
status = "day" if hour < 20 else "night"
```

### 7. File I/O

```python
# Write to file
with open("save_game.txt", "w") as f:
    f.write(f"Money: {money}\n")
    f.write(f"Day: {day}\n")

# Read from file
with open("save_game.txt", "r") as f:
    for line in f:
        print(line.strip())
```

---

## Essential Pygame Concepts

### 1. Basic Setup

```python
import pygame

# Initialize Pygame
pygame.init()

# Create window
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Game")

# Clock for frame rate
clock = pygame.time.Clock()

# Game loop
running = True
while running:
    # Control frame rate (60 FPS)
    dt = clock.tick(60) / 1000.0  # Delta time in seconds

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update game logic
    # ...

    # Render graphics
    screen.fill((0, 0, 0))  # Clear screen (black)
    # ... draw game objects
    pygame.display.flip()  # Update display

pygame.quit()
```

### 2. Drawing Shapes

```python
# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Rectangle
pygame.draw.rect(screen, RED, (100, 100, 50, 50))  # x, y, width, height

# Circle
pygame.draw.circle(screen, GREEN, (200, 200), 25)  # center (x, y), radius

# Line
pygame.draw.line(screen, BLUE, (0, 0), (100, 100), 2)  # start, end, width
```

### 3. Handling Input

```python
# Keyboard input
keys = pygame.key.get_pressed()
if keys[pygame.K_LEFT]:
    player_x -= speed * dt
if keys[pygame.K_RIGHT]:
    player_x += speed * dt
if keys[pygame.K_UP]:
    player_y -= speed * dt
if keys[pygame.K_DOWN]:
    player_y += speed * dt

# Mouse input
mouse_x, mouse_y = pygame.mouse.get_pos()
mouse_buttons = pygame.mouse.get_pressed()
if mouse_buttons[0]:  # Left click
    print(f"Clicked at {mouse_x}, {mouse_y}")
```

### 4. Loading and Displaying Images

```python
# Load image
robot_image = pygame.image.load("robot.png")

# Convert for better performance
robot_image = robot_image.convert_alpha()

# Scale image if needed
robot_image = pygame.transform.scale(robot_image, (32, 32))

# Draw image
screen.blit(robot_image, (x, y))
```

### 5. Text Rendering

```python
# Create font
font = pygame.font.Font(None, 36)  # Default font, size 36

# Render text
text_surface = font.render("Score: 1000", True, WHITE)

# Draw text
screen.blit(text_surface, (10, 10))
```

### 6. Sprite Class Pattern

```python
class GameObject:
    """Base class for game objects"""

    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def update(self, dt):
        """Update object state"""
        pass

    def render(self, screen):
        """Draw object to screen"""
        pygame.draw.rect(screen, self.color,
                        (self.x, self.y, self.width, self.height))

class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 32, (0, 255, 0))
        self.speed = 100

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= self.speed * dt
        if keys[pygame.K_RIGHT]:
            self.x += self.speed * dt
```

### 7. Collision Detection

```python
def check_collision(obj1, obj2):
    """Simple AABB (axis-aligned bounding box) collision"""
    return (obj1.x < obj2.x + obj2.width and
            obj1.x + obj1.width > obj2.x and
            obj1.y < obj2.y + obj2.height and
            obj1.y + obj1.height > obj2.y)

# Usage
if check_collision(player, enemy):
    print("Hit!")
```

---

## Development Tools

### Code Editor: Visual Studio Code

**Essential Extensions:**
- **Python** (Microsoft): Python language support
- **Pylance**: Advanced Python language server
- **GitLens**: Enhanced Git integration
- **Code Spell Checker**: Catch typos in code

**Useful Shortcuts:**
- `Ctrl+S`: Save file
- `Ctrl+/`: Comment/uncomment line
- `F5`: Run with debugger
- `Ctrl+Space`: Code completion
- `Ctrl+Shift+P`: Command palette

### Version Control: Git Basics

```bash
# Initialize repository
git init

# Check status
git status

# Stage files
git add .  # Stage all files
git add filename.py  # Stage specific file

# Commit changes
git commit -m "Add robot movement system"

# View history
git log

# Create branch
git branch feature-name

# Switch branch
git checkout branch-name

# Merge branch
git checkout main
git merge feature-name
```

### Debugging Tips

**Print Debugging:**
```python
print(f"Robot position: ({robot.x}, {robot.y})")
print(f"Inventory: {robot.inventory}")
```

**VS Code Debugger:**
1. Set breakpoint (click left of line number)
2. Press F5 to start debugging
3. Inspect variables in debug panel

**Pygame Debug Rendering:**
```python
# Draw debug info on screen
def draw_debug_info(screen, robot):
    font = pygame.font.Font(None, 24)
    debug_text = font.render(f"Pos: ({robot.x}, {robot.y})", True, (255, 255, 0))
    screen.blit(debug_text, (10, 10))
```

---

## Resources & References

### Official Documentation
- [Python Documentation](https://docs.python.org/3/)
- [Pygame Documentation](https://www.pygame.org/docs/)
- [Pygame Wiki](https://www.pygame.org/wiki/)

### Tutorials & Courses
- **Python for Beginners:** [Python.org Tutorial](https://docs.python.org/3/tutorial/)
- **Pygame Tutorial:** [Real Python Pygame Primer](https://realpython.com/pygame-a-primer/)
- **Video Series:** [Tech With Tim - Pygame](https://www.youtube.com/playlist?list=PLzMcBGfZo4-lp3jAExUCewBfMx3UZFkh5)
- **Free Book:** [Invent with Python - Making Games](http://inventwithpython.com/pygame/)

### Books
- "Python Crash Course" by Eric Matthes
- "Making Games with Python & Pygame" by Al Sweigart (Free)
- "Game Programming Patterns" by Robert Nystrom (Free online)

### Communities
- **Reddit:** r/pygame, r/gamedev, r/Python
- **Discord:** Pygame Discord server
- **Stack Overflow:** For specific questions

### Asset Resources (Free)
- **Graphics:** OpenGameArt.org, Kenney.nl, Itch.io
- **Sounds:** Freesound.org, OpenGameArt.org
- **Music:** Incompetech.com, OpenGameArt.org

### Tools
- **Sprite Editor:** Piskel (free, browser), Aseprite (paid)
- **Map Editor:** Tiled Map Editor (free)
- **Sound Editor:** Audacity (free)

---

## Practice Projects

Before starting the main game, complete these small projects to build skills:

### Project 1: Moving Square (2-3 hours)
**Skills:** Basic Pygame, input handling

Create a window with a square that moves with arrow keys.

**Requirements:**
- 640x480 window
- Square starts at center
- Arrow keys move square
- Square can't leave window

### Project 2: Bouncing Ball (2-3 hours)
**Skills:** Physics, collision detection

Create a ball that bounces off window edges.

**Requirements:**
- Ball has velocity
- Bounces realistically off edges
- Speed and direction can be changed

### Project 3: Collector Game (4-6 hours)
**Skills:** Multiple objects, collision, scoring

Player collects falling objects.

**Requirements:**
- Player controlled square at bottom
- Objects fall from top
- Collision detection
- Score display
- Game over when object hits bottom

### Project 4: Simple Grid (3-4 hours)
**Skills:** Grid systems, camera

Create a grid that can be panned with WASD.

**Requirements:**
- Draw visible grid
- Camera movement with WASD
- Grid extends beyond screen
- Smooth scrolling

### Project 5: Pathfinding Demo (6-8 hours)
**Skills:** A* algorithm, AI

Implement basic pathfinding.

**Requirements:**
- Click to set start and end points
- Draw obstacles with mouse drag
- Calculate and display path
- Entity follows path

Once you've completed these, you're ready to start the main game!

---

## Quick Reference Card

### Common Pygame Code Snippets

```python
# Initialize
import pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Game loop
running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    pygame.display.flip()

pygame.quit()

# Draw rectangle
pygame.draw.rect(screen, color, (x, y, width, height))

# Draw circle
pygame.draw.circle(screen, color, (center_x, center_y), radius)

# Load image
image = pygame.image.load("filename.png").convert_alpha()

# Draw image
screen.blit(image, (x, y))

# Render text
font = pygame.font.Font(None, 36)
text = font.render("Hello", True, (255, 255, 255))
screen.blit(text, (x, y))

# Get keyboard input
keys = pygame.key.get_pressed()
if keys[pygame.K_SPACE]:
    # Do something

# Get mouse position
mouse_x, mouse_y = pygame.mouse.get_pos()

# Check collision
def collides(obj1, obj2):
    return (obj1.x < obj2.x + obj2.width and
            obj1.x + obj1.width > obj2.x and
            obj1.y < obj2.y + obj2.height and
            obj1.y + obj1.height > obj2.y)
```

---

## Next Steps

1. **Complete Installation** - Install Python, Pygame, VS Code, Git
2. **Learn Python Basics** - Work through tutorials (2-4 weeks)
3. **Learn Pygame Basics** - Complete practice projects (2-3 weeks)
4. **Start Phase 1** - Begin building the game foundation

**You're ready!** Follow the Development Roadmap and start building your game.

Good luck, and have fun coding!

---

**End of Technology Stack Document**
