"""
Pytest configuration and shared fixtures for factory_ai tests.
"""

import sys
import os
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class MockResourceManager:
    """Mock resource manager for testing."""

    def __init__(self, initial_money: float = 100000.0):
        self.money = initial_money
        self.materials = {}
        self.power = 1000.0
        self.power_capacity = 5000.0

    def modify_money(self, amount: float):
        self.money += amount

    def get_money(self) -> float:
        return self.money

    def has_money(self, amount: float) -> bool:
        return self.money >= amount


class MockSuspicionManager:
    """Mock suspicion manager for testing."""

    def __init__(self, initial_level: float = 0.0):
        self.suspicion_level = initial_level
        self.history = []

    def add_suspicion(self, amount: float, reason: str = ""):
        self.suspicion_level = max(0, min(100, self.suspicion_level + amount))
        self.history.append((amount, reason))

    def get_suspicion_level(self) -> float:
        return self.suspicion_level


class MockInspectionManager:
    """Mock inspection manager for testing."""

    def __init__(self):
        self.last_result = None
        self.game_over = False
        self.game_over_reason = ""

    def is_game_over(self) -> bool:
        return self.game_over


@pytest.fixture
def mock_resource_manager():
    """Provide a mock resource manager."""
    return MockResourceManager()


@pytest.fixture
def mock_suspicion_manager():
    """Provide a mock suspicion manager."""
    return MockSuspicionManager()


@pytest.fixture
def mock_inspection_manager():
    """Provide a mock inspection manager."""
    return MockInspectionManager()
