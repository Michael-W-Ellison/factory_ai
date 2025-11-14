"""
GameAI - Autonomous AI agent that can play the recycling factory game.

The AI can:
- Collect materials efficiently
- Build and upgrade buildings strategically
- Manage power systems
- Process materials for profit
- Compete for high scores
"""

import random
from src.entities.buildings import (
    Factory,
    LandfillGasExtraction,
    SolarArray,
    MethaneGenerator,
    BatteryBank,
    PaperRecycler,
    PlasticRecycler,
    MetalRefinery,
    Glassworks,
    RubberRecycler,
    Warehouse,
    Silo
)


class GameAI:
    """
    AI agent that can play the recycling factory game autonomously.

    The AI makes strategic decisions about:
    - Which buildings to construct
    - Where to place buildings
    - How to allocate resources
    - When to upgrade vs expand
    """

    def __init__(self, game, difficulty="medium"):
        """
        Initialize the AI player.

        Args:
            game: Game instance to play
            difficulty (str): AI difficulty level (easy/medium/hard)
        """
        self.game = game
        self.difficulty = difficulty

        # AI state tracking
        self.game_time = 0.0
        self.last_building_attempt = 0.0
        self.building_cooldown = 5.0  # Seconds between building attempts

        # Strategy parameters based on difficulty
        self._set_difficulty_parameters()

        # Building priorities (will be updated based on game state)
        self.building_priorities = []

        # Performance tracking
        self.stats = {
            'buildings_placed': 0,
            'buildings_failed': 0,
            'total_collected': 0.0,
            'total_processed': 0.0,
            'peak_power_surplus': 0.0,
        }

    def _set_difficulty_parameters(self):
        """Set AI parameters based on difficulty level."""
        if self.difficulty == "easy":
            self.building_cooldown = 8.0
            self.efficiency_target = 0.6  # 60% efficiency
            self.expansion_threshold = 3000  # Money needed before expanding
        elif self.difficulty == "medium":
            self.building_cooldown = 4.0
            self.efficiency_target = 0.75
            self.expansion_threshold = 2000
        else:  # hard
            self.building_cooldown = 2.0
            self.efficiency_target = 0.90
            self.expansion_threshold = 1500

    def update(self, dt):
        """
        Update AI decision-making.

        Args:
            dt (float): Delta time in seconds
        """
        self.game_time += dt

        # Evaluate game state
        state = self._evaluate_game_state()

        # Make strategic decisions
        self._update_building_priorities(state)

        # Execute actions
        if self.game_time - self.last_building_attempt >= self.building_cooldown:
            self._try_build_next_building(state)
            self.last_building_attempt = self.game_time

    def _evaluate_game_state(self):
        """
        Evaluate current game state and return analysis.

        Returns:
            dict: Game state analysis
        """
        state = {
            'money': self.game.resources.money,
            'stored_materials': self.game.resources.get_total_stored_weight(),
            'stored_value': self.game.resources.get_total_stored_value(),
            'power_generation': self.game.power.total_generation,
            'power_consumption': self.game.power.total_consumption,
            'power_surplus': self.game.power.total_generation - self.game.power.total_consumption,
            'power_storage': self.game.power.current_power,
            'max_power_storage': self.game.power.max_storage,
            'building_count': len(self.game.buildings.buildings),
            'robot_count': len([e for e in self.game.entities.entities if hasattr(e, 'autonomous')]),
        }

        # Calculate needs
        state['needs_power'] = state['power_surplus'] < 2.0
        state['needs_storage'] = state['stored_materials'] > 0  # Has materials to store
        state['needs_processing'] = state['stored_materials'] > 100.0
        state['has_funds'] = state['money'] >= self.expansion_threshold

        return state

    def _update_building_priorities(self, state):
        """
        Update building priorities based on game state.

        Args:
            state (dict): Game state analysis
        """
        priorities = []

        # Early game: Focus on power
        if state['building_count'] < 3:
            if state['power_generation'] < 20.0:
                priorities.append(('power', 10))
            priorities.append(('storage', 8))

        # Mid game: Processing and expansion
        elif state['building_count'] < 10:
            if state['needs_power']:
                priorities.append(('power', 9))
            if state['needs_storage']:
                priorities.append(('storage', 7))
            if state['needs_processing']:
                priorities.append(('processing', 8))

        # Late game: Optimization
        else:
            if state['needs_power']:
                priorities.append(('power', 10))
            if state['power_surplus'] > 5.0:
                priorities.append(('processing', 9))
            priorities.append(('storage', 6))

        self.building_priorities = sorted(priorities, key=lambda x: x[1], reverse=True)

    def _try_build_next_building(self, state):
        """
        Attempt to build the next priority building.

        Args:
            state (dict): Game state analysis
        """
        if not state['has_funds']:
            return

        # Try to build multiple buildings if we have funds (aggressive expansion)
        buildings_this_round = 0
        max_buildings_per_round = 3 if self.difficulty == "hard" else 2 if self.difficulty == "medium" else 1

        while buildings_this_round < max_buildings_per_round and state['money'] >= self.expansion_threshold:
            built_something = False

            # Try each priority in order
            for building_type, priority in self.building_priorities:
                building = None

                if building_type == 'power':
                    building = self._select_power_building(state)
                elif building_type == 'storage':
                    building = self._select_storage_building(state)
                elif building_type == 'processing':
                    building = self._select_processing_building(state)

                if building and state['money'] >= building.base_cost:
                    # Try to find valid placement
                    position = self._find_building_position(building)
                    if position:
                        grid_x, grid_y = position
                        building.grid_x = grid_x
                        building.grid_y = grid_y

                        # Try to place
                        if self.game.buildings.place_building(building):
                            self.stats['buildings_placed'] += 1
                            print(f"[AI] Placed {building.name} at ({grid_x}, {grid_y})")

                            # Deduct cost
                            self.game.resources.money -= building.base_cost
                            state['money'] = self.game.resources.money
                            buildings_this_round += 1
                            built_something = True
                            break  # Try next priority
                        else:
                            self.stats['buildings_failed'] += 1

            # If we couldn't build anything, stop trying
            if not built_something:
                break

    def _select_power_building(self, state):
        """Select best power building based on state."""
        # Prefer solar if we can afford it (cheap and clean)
        if state['money'] >= 2000:
            return SolarArray(0, 0)

        # Otherwise landfill gas (if early game)
        if state['building_count'] < 5:
            return LandfillGasExtraction(0, 0)

        return None

    def _select_storage_building(self, state):
        """Select best storage building based on state."""
        # Prefer warehouse for flexibility
        if state['money'] >= 3000:
            return Warehouse(0, 0)

        return None

    def _select_processing_building(self, state):
        """Select best processing building based on materials."""
        # Start with paper recycler (cheapest, most common material)
        if state['money'] >= 5000:
            return PaperRecycler(0, 0)

        return None

    def _find_building_position(self, building):
        """
        Find a valid position to place a building.

        Args:
            building: Building to place

        Returns:
            tuple: (grid_x, grid_y) or None if no position found
        """
        grid_width = self.game.grid.width_tiles
        grid_height = self.game.grid.height_tiles

        # Try to place near factory first
        factory_buildings = self.game.buildings.get_buildings_by_type('factory')
        if factory_buildings:
            factory = factory_buildings[0]
            search_x = factory.grid_x
            search_y = factory.grid_y
        else:
            # Search from center
            search_x = grid_width // 2
            search_y = grid_height // 2

        # Spiral search pattern
        max_radius = 20
        for radius in range(1, max_radius):
            # Try positions in a square around the search point
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    # Only check perimeter of square
                    if abs(dx) != radius and abs(dy) != radius:
                        continue

                    grid_x = search_x + dx
                    grid_y = search_y + dy

                    # Check bounds
                    if (grid_x < 0 or grid_y < 0 or
                        grid_x + building.width_tiles > grid_width or
                        grid_y + building.height_tiles > grid_height):
                        continue

                    # Check if valid
                    building.grid_x = grid_x
                    building.grid_y = grid_y
                    if self.game.buildings._is_valid_placement(building):
                        return (grid_x, grid_y)

        return None

    def get_stats(self):
        """
        Get AI performance statistics.

        Returns:
            dict: Performance stats
        """
        return {
            **self.stats,
            'game_time': self.game_time,
            'difficulty': self.difficulty,
            'current_money': self.game.resources.money,
            'building_count': len(self.game.buildings.buildings),
        }

    def __repr__(self):
        """String representation for debugging."""
        return (f"GameAI(difficulty={self.difficulty}, "
                f"buildings={self.stats['buildings_placed']}, "
                f"time={self.game_time:.1f}s)")
