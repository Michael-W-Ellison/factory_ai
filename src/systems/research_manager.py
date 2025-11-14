"""
ResearchManager - Manages research technology tree and effects.

Handles research progress, prerequisites, costs, and applies effects
to robots, buildings, and game systems.
"""

import json
import os
from typing import Dict, List, Optional, Set


class ResearchManager:
    """
    Manages the research technology tree.

    Tracks completed and in-progress research, checks prerequisites,
    handles costs and time, and applies research effects to game systems.
    """

    def __init__(self):
        """Initialize the research manager."""
        # Load research definitions
        self.research_definitions = self._load_research_definitions()

        # Completed research: {tech_id: completion_time}
        self.completed_research = {}

        # In-progress research: {tech_id: progress_info}
        self.current_research = None
        self.research_progress = 0.0  # Hours completed
        self.research_total_time = 0.0  # Total hours needed

        # Effects changed flag (for updating game systems)
        self.effects_changed = False

        # Statistics
        self.stats = {
            'total_researched': 0,
            'money_spent': 0,
            'time_spent': 0.0
        }

    def _load_research_definitions(self) -> Dict:
        """
        Load research definitions from JSON file.

        Returns:
            dict: Research technology definitions
        """
        json_path = os.path.join('data', 'research.json')
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                data = json.load(f)
                return data.get('technologies', {})
        else:
            print(f"Warning: {json_path} not found, using empty research tree")
            return {}

    def get_research_definition(self, tech_id: str) -> Optional[Dict]:
        """
        Get the definition for a research technology.

        Args:
            tech_id (str): Technology identifier

        Returns:
            dict: Technology definition or None
        """
        return self.research_definitions.get(tech_id)

    def is_completed(self, tech_id: str) -> bool:
        """
        Check if a technology has been researched.

        Args:
            tech_id (str): Technology identifier

        Returns:
            bool: True if research completed
        """
        return tech_id in self.completed_research

    def is_available(self, tech_id: str) -> bool:
        """
        Check if a technology is available to research.

        Args:
            tech_id (str): Technology identifier

        Returns:
            bool: True if all prerequisites are met and not already researched
        """
        if self.is_completed(tech_id):
            return False

        tech = self.get_research_definition(tech_id)
        if not tech:
            return False

        # Check prerequisites
        prerequisites = tech.get('prerequisites', [])
        for prereq_id in prerequisites:
            if not self.is_completed(prereq_id):
                return False

        return True

    def can_start_research(self, tech_id: str, money: float):
        """
        Check if player can start researching a technology.

        Args:
            tech_id (str): Technology identifier
            money (float): Available money

        Returns:
            tuple: (can_research: bool, reason: str)
        """
        # Check if technology exists
        tech = self.get_research_definition(tech_id)
        if not tech:
            return False, f"Unknown technology: {tech_id}"

        # Check if already completed
        if self.is_completed(tech_id):
            return False, "Already researched"

        # Check if already researching something
        if self.current_research is not None:
            return False, f"Already researching {self.current_research}"

        # Check if available (prerequisites met)
        if not self.is_available(tech_id):
            missing = self._get_missing_prerequisites(tech_id)
            return False, f"Missing prerequisites: {', '.join(missing)}"

        # Check if can afford
        cost = tech.get('cost', 0)
        if money < cost:
            return False, f"Insufficient funds (need ${cost}, have ${money:.0f})"

        return True, "Can research"

    def _get_missing_prerequisites(self, tech_id: str) -> List[str]:
        """
        Get list of missing prerequisites for a technology.

        Args:
            tech_id (str): Technology identifier

        Returns:
            list: List of missing prerequisite tech IDs
        """
        tech = self.get_research_definition(tech_id)
        if not tech:
            return []

        prerequisites = tech.get('prerequisites', [])
        missing = []

        for prereq_id in prerequisites:
            if not self.is_completed(prereq_id):
                prereq_tech = self.get_research_definition(prereq_id)
                prereq_name = prereq_tech.get('name', prereq_id) if prereq_tech else prereq_id
                missing.append(prereq_name)

        return missing

    def start_research(self, tech_id: str, money: float):
        """
        Start researching a technology.

        Args:
            tech_id (str): Technology identifier
            money (float): Available money

        Returns:
            tuple: (success: bool, money_remaining: float)
        """
        can_research, reason = self.can_start_research(tech_id, money)

        if not can_research:
            print(f"Cannot start research: {reason}")
            return False, money

        tech = self.get_research_definition(tech_id)
        cost = tech.get('cost', 0)
        time = tech.get('time', 1.0)

        # Deduct cost
        money_remaining = money - cost

        # Start research
        self.current_research = tech_id
        self.research_progress = 0.0
        self.research_total_time = time

        # Update statistics
        self.stats['money_spent'] += cost

        print(f"Started research: {tech.get('name', tech_id)} (${cost}, {time} hours)")

        return True, money_remaining

    def update(self, dt: float) -> Optional[str]:
        """
        Update research progress.

        Args:
            dt (float): Delta time in hours (game time)

        Returns:
            str: Completed tech_id if research finished, None otherwise
        """
        if self.current_research is None:
            return None

        # Update progress
        self.research_progress += dt

        # Check if completed
        if self.research_progress >= self.research_total_time:
            completed_tech = self.current_research
            self._complete_research(completed_tech)
            return completed_tech

        return None

    def _complete_research(self, tech_id: str):
        """
        Complete a research technology.

        Args:
            tech_id (str): Technology identifier
        """
        tech = self.get_research_definition(tech_id)
        if not tech:
            return

        # Mark as completed
        self.completed_research[tech_id] = self.research_progress

        # Update statistics
        self.stats['total_researched'] += 1
        self.stats['time_spent'] += self.research_progress

        # Set effects changed flag
        self.effects_changed = True

        # Clear current research
        self.current_research = None
        self.research_progress = 0.0
        self.research_total_time = 0.0

        print(f"✓ Research complete: {tech.get('name', tech_id)}")

    def cancel_research(self) -> bool:
        """
        Cancel current research (no refund).

        Returns:
            bool: True if research was cancelled
        """
        if self.current_research is None:
            return False

        tech_id = self.current_research
        tech = self.get_research_definition(tech_id)

        print(f"Cancelled research: {tech.get('name', tech_id) if tech else tech_id}")

        self.current_research = None
        self.research_progress = 0.0
        self.research_total_time = 0.0

        return True

    def get_effect(self, effect_name: str, default=1.0):
        """
        Get the cumulative effect value from all completed research.

        Args:
            effect_name (str): Effect identifier
            default: Default value if no research affects this

        Returns:
            Effect value (typically a multiplier or boolean)
        """
        result = default

        for tech_id in self.completed_research:
            tech = self.get_research_definition(tech_id)
            if not tech:
                continue

            effects = tech.get('effects', {})
            if effect_name in effects:
                effect_value = effects[effect_name]

                # Handle different effect types
                if isinstance(effect_value, bool):
                    result = effect_value
                elif isinstance(effect_value, (int, float)):
                    # For multipliers, take the highest value (not additive)
                    if effect_value > result:
                        result = effect_value

        return result

    def get_effect_multiplier(self, effect_name: str) -> float:
        """
        Get effect as a multiplier (default 1.0).

        Args:
            effect_name (str): Effect identifier

        Returns:
            float: Effect multiplier
        """
        return float(self.get_effect(effect_name, 1.0))

    def has_unlock(self, unlock_name: str) -> bool:
        """
        Check if an unlock has been researched.

        Args:
            unlock_name (str): Unlock identifier (e.g., 'unlock_drones')

        Returns:
            bool: True if unlocked
        """
        return bool(self.get_effect(unlock_name, False))

    def get_available_technologies(self, category: str = None) -> List[Dict]:
        """
        Get list of available technologies.

        Args:
            category (str, optional): Filter by category

        Returns:
            list: List of available technology definitions
        """
        available = []

        for tech_id, tech in self.research_definitions.items():
            # Skip if already completed
            if self.is_completed(tech_id):
                continue

            # Filter by category
            if category and tech.get('category') != category:
                continue

            # Check if available
            if self.is_available(tech_id):
                available.append({
                    'id': tech_id,
                    **tech
                })

        # Sort by cost
        available.sort(key=lambda t: t.get('cost', 0))

        return available

    def get_completed_technologies(self, category: str = None) -> List[Dict]:
        """
        Get list of completed technologies.

        Args:
            category (str, optional): Filter by category

        Returns:
            list: List of completed technology definitions
        """
        completed = []

        for tech_id in self.completed_research:
            tech = self.get_research_definition(tech_id)
            if not tech:
                continue

            # Filter by category
            if category and tech.get('category') != category:
                continue

            completed.append({
                'id': tech_id,
                **tech
            })

        # Sort by completion time
        completed.sort(key=lambda t: self.completed_research.get(t['id'], 0))

        return completed

    def get_progress_info(self) -> Optional[Dict]:
        """
        Get information about current research progress.

        Returns:
            dict: Progress info or None if not researching
        """
        if self.current_research is None:
            return None

        tech = self.get_research_definition(self.current_research)
        if not tech:
            return None

        return {
            'tech_id': self.current_research,
            'name': tech.get('name', self.current_research),
            'progress': self.research_progress,
            'total_time': self.research_total_time,
            'percent': (self.research_progress / self.research_total_time * 100) if self.research_total_time > 0 else 0,
            'remaining': self.research_total_time - self.research_progress
        }

    def get_statistics(self) -> Dict:
        """
        Get research statistics.

        Returns:
            dict: Statistics
        """
        return {
            **self.stats,
            'researching': self.current_research is not None,
            'available_count': len(self.get_available_technologies())
        }

    def save_state(self) -> Dict:
        """
        Save research manager state.

        Returns:
            dict: Serialized state
        """
        return {
            'completed_research': self.completed_research,
            'current_research': self.current_research,
            'research_progress': self.research_progress,
            'research_total_time': self.research_total_time,
            'stats': self.stats
        }

    def load_state(self, state: Dict):
        """
        Load research manager state.

        Args:
            state (dict): Serialized state
        """
        self.completed_research = state.get('completed_research', {})
        self.current_research = state.get('current_research')
        self.research_progress = state.get('research_progress', 0.0)
        self.research_total_time = state.get('research_total_time', 0.0)
        self.stats = state.get('stats', {
            'total_researched': 0,
            'money_spent': 0,
            'time_spent': 0.0
        })

        # Set effects changed flag to apply research effects
        self.effects_changed = True

    def __repr__(self):
        """String representation for debugging."""
        completed = len(self.completed_research)
        total = len(self.research_definitions)
        researching = f", researching {self.current_research}" if self.current_research else ""
        return f"ResearchManager({completed}/{total} completed{researching})"
