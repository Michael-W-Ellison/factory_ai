"""
EntityManager - manages all entities in the game.
"""

from src.entities.robot import Robot
from src.entities.collectible import CollectibleObject


class EntityManager:
    """
    Manages all entities in the game world.

    Handles creation, updating, rendering, and removal of entities.
    """

    def __init__(self, grid=None, resource_manager=None, research_manager=None, material_inventory=None):
        """Initialize the entity manager.

        Args:
            grid: Grid object (for pathfinding)
            resource_manager: ResourceManager (for depositing materials)
            research_manager: ResearchManager (for applying bonuses to new entities)
            material_inventory: MaterialInventory (for tracking material sources)
        """
        # All entities by ID
        self.entities = {}

        # Entities grouped by type for efficient iteration
        self.robots = []
        self.collectibles = []
        self.buildings = []  # For future use

        # Selected robot (for player control)
        self.selected_robot = None

        # Systems
        self.grid = grid
        self.resource_manager = resource_manager
        self.research_manager = research_manager
        self.material_inventory = material_inventory

        # Factory position (for robots to return to)
        self.factory_pos = None

    def create_robot(self, x, y, autonomous=True):
        """
        Create a new robot.

        Args:
            x (float): World X position
            y (float): World Y position
            autonomous (bool): If True, robot operates autonomously

        Returns:
            Robot: The created robot
        """
        robot = Robot(x, y, autonomous=autonomous)
        self.entities[robot.id] = robot
        self.robots.append(robot)

        # Set factory position if available
        if self.factory_pos:
            robot.factory_pos = self.factory_pos

        # Apply research effects to new robot
        if self.research_manager:
            robot.apply_research_effects(self.research_manager)

        # Auto-select first robot if not autonomous
        if not autonomous and self.selected_robot is None:
            self.select_robot(robot)

        print(f"Created {robot}")
        return robot

    def create_collectible(self, x, y, material_type, quantity, source=None):
        """
        Create a new collectible object.

        Args:
            x (float): World X position
            y (float): World Y position
            material_type (str): Type of material
            quantity (float): Amount in kg
            source (MaterialSource): Source of material (default: LANDFILL)

        Returns:
            CollectibleObject: The created collectible
        """
        from src.systems.material_inventory import MaterialSource
        if source is None:
            source = MaterialSource.LANDFILL

        collectible = CollectibleObject(x, y, material_type, quantity, source)
        self.entities[collectible.id] = collectible
        self.collectibles.append(collectible)
        return collectible

    def select_robot(self, robot):
        """
        Select a robot for player control.

        Args:
            robot (Robot): Robot to select
        """
        # Deselect previous robot
        if self.selected_robot:
            self.selected_robot.selected = False

        # Select new robot
        self.selected_robot = robot
        if robot:
            robot.selected = True

    def select_robot_at(self, x, y):
        """
        Select a robot at the given world position.

        Args:
            x (float): World X position
            y (float): World Y position

        Returns:
            Robot or None: The selected robot, if any
        """
        # Check robots in reverse order (top to bottom)
        for robot in reversed(self.robots):
            if (robot.x <= x <= robot.x + robot.width and
                robot.y <= y <= robot.y + robot.height):
                self.select_robot(robot)
                return robot
        return None

    def get_collectibles_near(self, x, y, radius):
        """
        Get collectibles within radius of a position.

        Args:
            x (float): World X position
            y (float): World Y position
            radius (float): Search radius in pixels

        Returns:
            list: List of nearby collectibles
        """
        nearby = []
        for collectible in self.collectibles:
            dx = collectible.x - x
            dy = collectible.y - y
            distance = (dx * dx + dy * dy) ** 0.5
            if distance <= radius:
                nearby.append(collectible)
        return nearby

    def update(self, dt):
        """
        Update all entities.

        Args:
            dt (float): Delta time in seconds
        """
        # Update robots with grid and entity_manager context
        for robot in self.robots:
            robot.update(dt, grid=self.grid, entity_manager=self)

        # Update other entities (collectibles don't need special context)
        for collectible in self.collectibles:
            collectible.update(dt)

        # Handle collection for all robots
        self._handle_collection()

        # Remove inactive entities
        self._remove_inactive_entities()

    def set_factory_position(self, x, y):
        """
        Set the factory position for all robots.

        Args:
            x (float): World X position of factory
            y (float): World Y position of factory
        """
        self.factory_pos = (x, y)
        # Update existing robots
        for robot in self.robots:
            robot.factory_pos = self.factory_pos

    def apply_research_effects_to_robots(self, research_manager):
        """
        Apply research effects to all robots.

        Args:
            research_manager: ResearchManager instance
        """
        for robot in self.robots:
            robot.apply_research_effects(research_manager)

    def _handle_collection(self):
        """
        Handle automatic collection of materials by robots.

        Robots will automatically collect materials they collide with.
        """
        # Collection radius (slightly larger than robot size for easier collection)
        collection_radius = 40  # pixels

        for robot in self.robots:
            # Skip if robot is full
            if robot.is_full():
                continue

            # Get robot center position
            robot_center_x, robot_center_y = robot.get_center()

            # Find nearby collectibles
            nearby_collectibles = self.get_collectibles_near(
                robot_center_x, robot_center_y, collection_radius
            )

            # Try to collect from nearby collectibles
            for collectible in nearby_collectibles:
                # Check if robot actually collides with this collectible
                if robot.collides_with(collectible):
                    # Calculate how much space robot has
                    available_space = robot.max_capacity - robot.current_load
                    if available_space <= 0:
                        break  # Robot is full

                    # Collect as much as possible
                    amount_collected = collectible.collect(available_space)

                    # Add to robot's inventory with source tracking
                    robot.add_material(collectible.material_type, amount_collected, collectible.source)

                    # Print feedback
                    if amount_collected > 0:
                        print(f"{robot} collected {amount_collected:.1f}kg of {collectible.material_type}")

                    # If robot is now full, stop collecting
                    if robot.is_full():
                        print(f"{robot} inventory is full!")
                        break

    def _remove_inactive_entities(self):
        """Remove entities marked as inactive."""
        inactive_ids = [eid for eid, entity in self.entities.items() if not entity.active]

        for eid in inactive_ids:
            entity = self.entities[eid]

            # Remove from specific lists
            if isinstance(entity, Robot):
                self.robots.remove(entity)
                if self.selected_robot == entity:
                    self.selected_robot = None
            elif isinstance(entity, CollectibleObject):
                self.collectibles.remove(entity)

            # Remove from main dict
            del self.entities[eid]

    def render(self, screen, camera):
        """
        Render all entities.

        Args:
            screen: Pygame surface
            camera: Camera object
        """
        # Render collectibles first (so they appear under robots)
        for collectible in self.collectibles:
            collectible.render(screen, camera)

        # Render robots on top
        for robot in self.robots:
            robot.render(screen, camera)

    def get_stats(self):
        """
        Get statistics about entities.

        Returns:
            dict: Entity statistics
        """
        return {
            'total_entities': len(self.entities),
            'robots': len(self.robots),
            'collectibles': len(self.collectibles),
            'buildings': len(self.buildings),
        }

    def __repr__(self):
        """String representation for debugging."""
        return (f"EntityManager(robots={len(self.robots)}, "
                f"collectibles={len(self.collectibles)})")
