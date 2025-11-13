"""
ResearchManager - Manages the research system and tech tree.

Handles:
- Loading research tree from JSON
- Tracking completed and in-progress research
- Checking prerequisites
- Applying research effects to game systems
- Research progress over time
"""

import json
import os
from typing import Dict, List, Optional, Set


class ResearchManager:
    """
    Manages the research/technology system.

    Research provides upgrades to robots, buildings, and unlocks new features.
    Research has costs, time requirements, and prerequisites.
    """

    def __init__(self):
        """Initialize the research manager."""
        # Research tree data (loaded from JSON)
        self.research_tree: Dict = {}

        # Completed research (tech IDs)
        self.completed_research: Set[str] = set()

        # Current research in progress
        self.current_research: Optional[str] = None
        self.research_progress: float = 0.0  # Seconds of progress
        self.research_time_required: float = 0.0  # Total seconds needed

        # Research effects cache (for quick lookups)
        self.active_effects: Dict[str, float] = {}

        # Load research tree
        self._load_research_tree()

    def _load_research_tree(self):
        """Load research tree from JSON file."""
        config_path = os.path.join('data', 'config', 'research.json')

        if not os.path.exists(config_path):
            print(f"Warning: Research file not found at {config_path}")
            return

        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                self.research_tree = data.get('research_tree', {})

            # Flatten the tree for easier access
            self._flatten_tree()

            print(f"Loaded research tree with {len(self.research_tree)} technologies")

        except Exception as e:
            print(f"Error loading research tree: {e}")
            self.research_tree = {}

    def _flatten_tree(self):
        """Flatten nested category structure into flat dict of tech ID -> tech data."""
        flattened = {}

        for category_name, category_data in self.research_tree.items():
            if isinstance(category_data, dict):
                for tech_id, tech_data in category_data.items():
                    if isinstance(tech_data, dict):
                        # Add tech ID to the data
                        tech_data['id'] = tech_id
                        tech_data['category'] = tech_data.get('category', category_name)
                        flattened[tech_id] = tech_data

        self.research_tree = flattened

    def get_research(self, tech_id: str) -> Optional[Dict]:
        """
        Get research data by tech ID.

        Args:
            tech_id (str): Technology ID

        Returns:
            dict: Research data or None if not found
        """
        return self.research_tree.get(tech_id)

    def is_completed(self, tech_id: str) -> bool:
        """
        Check if research is completed.

        Args:
            tech_id (str): Technology ID

        Returns:
            bool: True if completed
        """
        return tech_id in self.completed_research

    def is_available(self, tech_id: str) -> bool:
        """
        Check if research is available to start (prerequisites met).

        Args:
            tech_id (str): Technology ID

        Returns:
            bool: True if all prerequisites are met
        """
        research = self.get_research(tech_id)
        if not research:
            return False

        # Already completed
        if self.is_completed(tech_id):
            return False

        # Check prerequisites
        prereqs = research.get('prerequisites', [])
        for prereq in prereqs:
            if not self.is_completed(prereq):
                return False

        return True

    def can_afford(self, tech_id: str, money: float) -> bool:
        """
        Check if player can afford the research.

        Args:
            tech_id (str): Technology ID
            money (float): Available money

        Returns:
            bool: True if can afford
        """
        research = self.get_research(tech_id)
        if not research:
            return False

        cost = research.get('cost', 0)
        return money >= cost

    def start_research(self, tech_id: str, money: float) -> bool:
        """
        Start researching a technology.

        Args:
            tech_id (str): Technology ID
            money (float): Available money

        Returns:
            bool: True if research started successfully
        """
        # Check if already researching something
        if self.current_research is not None:
            return False

        # Check if available
        if not self.is_available(tech_id):
            return False

        # Check if can afford
        if not self.can_afford(tech_id, money):
            return False

        # Start research
        research = self.get_research(tech_id)
        self.current_research = tech_id
        self.research_progress = 0.0
        self.research_time_required = research.get('time', 60.0)  # Default 60 seconds

        return True

    def cancel_research(self) -> Optional[str]:
        """
        Cancel current research.

        Returns:
            str: ID of cancelled research, or None if nothing was being researched
        """
        if self.current_research is None:
            return None

        cancelled = self.current_research
        self.current_research = None
        self.research_progress = 0.0
        self.research_time_required = 0.0

        return cancelled

    def update(self, dt: float):
        """
        Update research progress.

        Args:
            dt (float): Delta time in seconds
        """
        if self.current_research is None:
            return

        # Add progress
        self.research_progress += dt

        # Check if complete
        if self.research_progress >= self.research_time_required:
            self._complete_research(self.current_research)

    def _complete_research(self, tech_id: str):
        """
        Complete a research and apply its effects.

        Args:
            tech_id (str): Technology ID
        """
        # Add to completed
        self.completed_research.add(tech_id)

        # Apply effects
        research = self.get_research(tech_id)
        if research:
            effects = research.get('effects', {})
            for effect_name, effect_value in effects.items():
                # Store effects (will be applied by game systems)
                self.active_effects[effect_name] = effect_value

        # Clear current research only if this is the research being completed
        if self.current_research == tech_id:
            self.current_research = None
            self.research_progress = 0.0
            self.research_time_required = 0.0

        print(f"Research completed: {research.get('name', tech_id)}")

    def get_research_progress(self) -> float:
        """
        Get current research progress as a percentage (0.0-1.0).

        Returns:
            float: Progress percentage
        """
        if self.current_research is None:
            return 0.0

        if self.research_time_required == 0:
            return 1.0

        return min(1.0, self.research_progress / self.research_time_required)

    def get_effect_multiplier(self, effect_name: str) -> float:
        """
        Get the cumulative multiplier for an effect.

        Args:
            effect_name (str): Effect name (e.g., 'robot_speed')

        Returns:
            float: Multiplier value (1.0 = no effect, 1.5 = +50%, etc.)
        """
        return self.active_effects.get(effect_name, 1.0)

    def get_available_research(self) -> List[Dict]:
        """
        Get list of all available (but not completed) research.

        Returns:
            list: List of research data dicts
        """
        available = []

        for tech_id, tech_data in self.research_tree.items():
            if self.is_available(tech_id) and not self.is_completed(tech_id):
                available.append(tech_data)

        return available

    def get_research_by_category(self, category: str) -> List[Dict]:
        """
        Get all research in a category.

        Args:
            category (str): Category name

        Returns:
            list: List of research data dicts
        """
        research_list = []

        for tech_id, tech_data in self.research_tree.items():
            if tech_data.get('category') == category:
                research_list.append(tech_data)

        return research_list

    def get_stats(self) -> Dict:
        """
        Get research statistics.

        Returns:
            dict: Statistics
        """
        total_research = len(self.research_tree)
        completed = len(self.completed_research)
        available = len(self.get_available_research())

        return {
            'total_research': total_research,
            'completed': completed,
            'available': available,
            'in_progress': self.current_research is not None,
            'completion_percentage': (completed / total_research * 100) if total_research > 0 else 0
        }

    def to_dict(self) -> Dict:
        """
        Serialize research state for saving.

        Returns:
            dict: Serialized state
        """
        return {
            'completed_research': list(self.completed_research),
            'current_research': self.current_research,
            'research_progress': self.research_progress,
            'research_time_required': self.research_time_required,
            'active_effects': self.active_effects
        }

    def from_dict(self, data: Dict):
        """
        Load research state from saved data.

        Args:
            data (dict): Saved state
        """
        self.completed_research = set(data.get('completed_research', []))
        self.current_research = data.get('current_research')
        self.research_progress = data.get('research_progress', 0.0)
        self.research_time_required = data.get('research_time_required', 0.0)
        self.active_effects = data.get('active_effects', {})

    def __repr__(self):
        """String representation for debugging."""
        stats = self.get_stats()
        return (f"ResearchManager(total={stats['total_research']}, "
                f"completed={stats['completed']}, "
                f"available={stats['available']}, "
                f"in_progress={stats['in_progress']})")
