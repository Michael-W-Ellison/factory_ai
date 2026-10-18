"""
Tests for DeconstructionManager.

Tests deconstruction workflows including:
- Starting deconstruction jobs
- Canceling jobs
- Progress tracking
- Material recovery
- Worker assignment
- Illegal structure handling
- Statistics tracking
"""

import sys
from unittest.mock import MagicMock, patch

# Mock pygame before any imports that might need it
sys.modules['pygame'] = MagicMock()
sys.modules['pygame.font'] = MagicMock()
sys.modules['pygame.transform'] = MagicMock()
sys.modules['pygame.Surface'] = MagicMock()

import pytest

from src.systems.deconstruction_manager import (
    DeconstructionManager,
    DeconstructionJob,
    DeconstructionState
)


class MockResourceManager:
    """Mock resource manager for testing."""

    def __init__(self, initial_money: float = 100000.0):
        self.money = initial_money
        self.materials = {}


class MockMaterialInventory:
    """Mock material inventory for testing."""

    def __init__(self):
        self.materials = {}
        self.sources = {}

    def add_material(self, material_type: str, quantity: float, source):
        if material_type not in self.materials:
            self.materials[material_type] = 0.0
            self.sources[material_type] = []
        self.materials[material_type] += quantity
        self.sources[material_type].append(source)


@pytest.fixture
def mock_resource_manager():
    """Provide a mock resource manager."""
    return MockResourceManager()


@pytest.fixture
def mock_material_inventory():
    """Provide a mock material inventory."""
    return MockMaterialInventory()


@pytest.fixture
def deconstruction_manager(mock_resource_manager):
    """Provide a deconstruction manager with mocked dependencies."""
    return DeconstructionManager(mock_resource_manager)


@pytest.fixture
def deconstruction_manager_with_inventory(mock_resource_manager, mock_material_inventory):
    """Provide a deconstruction manager with material inventory."""
    return DeconstructionManager(mock_resource_manager, mock_material_inventory)


class TestDeconstructionJob:
    """Tests for DeconstructionJob dataclass."""

    def test_job_initialization(self):
        """Test that DeconstructionJob initializes with correct values."""
        job = DeconstructionJob(
            id=1,
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            progress=0.0,
            workers_assigned=2,
            time_remaining=60.0,
            total_time=60.0,
            materials_to_recover={"steel": 50.0},
            state=DeconstructionState.IN_PROGRESS,
            is_illegal_source=False
        )

        assert job.id == 1
        assert job.target_type == "building"
        assert job.target_id == 100
        assert job.target_position == (500.0, 300.0)
        assert job.progress == 0.0
        assert job.workers_assigned == 2
        assert job.time_remaining == 60.0
        assert job.materials_to_recover == {"steel": 50.0}
        assert job.state == DeconstructionState.IN_PROGRESS
        assert job.is_illegal_source is False

    def test_job_default_materials(self):
        """Test that DeconstructionJob defaults to empty materials dict."""
        job = DeconstructionJob(
            id=1,
            target_type="prop",
            target_id=50,
            target_position=(100.0, 100.0)
        )

        assert job.materials_to_recover == {}

    def test_job_default_state(self):
        """Test that DeconstructionJob defaults to IDLE state."""
        job = DeconstructionJob(
            id=1,
            target_type="prop",
            target_id=50,
            target_position=(100.0, 100.0)
        )

        assert job.state == DeconstructionState.IDLE


class TestDeconstructionState:
    """Tests for DeconstructionState enum."""

    def test_state_values(self):
        """Test that all expected states exist."""
        assert DeconstructionState.IDLE.value == 0
        assert DeconstructionState.IN_PROGRESS.value == 1
        assert DeconstructionState.COMPLETED.value == 2
        assert DeconstructionState.CANCELLED.value == 3


class TestDeconstructionManagerInit:
    """Tests for DeconstructionManager initialization."""

    def test_manager_initialization(self, deconstruction_manager):
        """Test that DeconstructionManager initializes correctly."""
        assert deconstruction_manager.jobs == {}
        assert deconstruction_manager.next_job_id == 1
        assert deconstruction_manager.total_jobs_completed == 0
        assert deconstruction_manager.total_materials_recovered == 0
        assert deconstruction_manager.total_illegal_deconstructions == 0

    def test_manager_parameters(self, deconstruction_manager):
        """Test that DeconstructionManager has expected parameters."""
        assert deconstruction_manager.base_deconstruction_time == 60.0
        assert deconstruction_manager.time_per_size_unit == 10.0
        assert deconstruction_manager.worker_speed_multiplier == 0.5
        assert deconstruction_manager.recovery_rate == 0.7
        assert deconstruction_manager.illegal_structure_penalty == 0.5


class TestStartDeconstruction:
    """Tests for starting deconstruction jobs."""

    def test_start_deconstruction_success(self, deconstruction_manager):
        """Test successfully starting a deconstruction job."""
        job_id = deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            materials={"steel": 100.0, "concrete": 200.0},
            size=2.0,
            workers=2
        )

        assert job_id == 1
        assert job_id in deconstruction_manager.jobs
        assert deconstruction_manager.jobs[job_id].state == DeconstructionState.IN_PROGRESS

    def test_start_deconstruction_increments_job_id(self, deconstruction_manager):
        """Test that job IDs increment properly."""
        job_id_1 = deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            materials={"steel": 100.0}
        )

        job_id_2 = deconstruction_manager.start_deconstruction(
            target_type="prop",
            target_id=200,
            target_position=(600.0, 400.0),
            materials={"wood": 50.0}
        )

        assert job_id_1 == 1
        assert job_id_2 == 2

    def test_start_deconstruction_calculates_time(self, deconstruction_manager):
        """Test that deconstruction time is calculated correctly."""
        job_id = deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            materials={"steel": 100.0},
            size=1.0,
            workers=1
        )

        job = deconstruction_manager.jobs[job_id]
        expected_time = 60.0 + 10.0  # base + size
        assert job.total_time == expected_time

    def test_start_deconstruction_worker_speed_bonus(self, deconstruction_manager):
        """Test that more workers reduce deconstruction time."""
        job_id_1_worker = deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            materials={"steel": 100.0},
            size=1.0,
            workers=1
        )

        job_id_2_workers = deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=101,
            target_position=(600.0, 400.0),
            materials={"steel": 100.0},
            size=1.0,
            workers=2
        )

        time_1_worker = deconstruction_manager.jobs[job_id_1_worker].total_time
        time_2_workers = deconstruction_manager.jobs[job_id_2_workers].total_time

        assert time_2_workers < time_1_worker

    def test_start_deconstruction_material_recovery_rate(self, deconstruction_manager):
        """Test that material recovery uses correct recovery rate."""
        job_id = deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            materials={"steel": 100.0},
            is_illegal=False
        )

        job = deconstruction_manager.jobs[job_id]
        assert job.materials_to_recover["steel"] == 70.0  # 100 * 0.7

    def test_start_deconstruction_illegal_penalty(self, deconstruction_manager):
        """Test that illegal structures have reduced recovery rate."""
        job_id = deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            materials={"steel": 100.0},
            is_illegal=True
        )

        job = deconstruction_manager.jobs[job_id]
        assert job.materials_to_recover["steel"] == 50.0  # 100 * 0.5
        assert job.is_illegal_source is True

    def test_start_deconstruction_tracks_illegal_count(self, deconstruction_manager):
        """Test that illegal deconstructions are tracked."""
        initial_count = deconstruction_manager.total_illegal_deconstructions

        deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            materials={"steel": 100.0},
            is_illegal=True
        )

        assert deconstruction_manager.total_illegal_deconstructions == initial_count + 1


class TestCancelDeconstruction:
    """Tests for canceling deconstruction jobs."""

    def test_cancel_deconstruction_success(self, deconstruction_manager):
        """Test successfully canceling a deconstruction job."""
        job_id = deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            materials={"steel": 100.0}
        )

        result = deconstruction_manager.cancel_deconstruction(job_id)

        assert result is True
        assert job_id not in deconstruction_manager.jobs

    def test_cancel_nonexistent_job(self, deconstruction_manager):
        """Test canceling a non-existent job returns False."""
        result = deconstruction_manager.cancel_deconstruction(99999)

        assert result is False

    def test_cancel_already_completed_job(self, deconstruction_manager):
        """Test canceling an already completed job returns False."""
        job_id = deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            materials={"steel": 100.0}
        )

        # Manually set state to completed
        deconstruction_manager.jobs[job_id].state = DeconstructionState.COMPLETED

        result = deconstruction_manager.cancel_deconstruction(job_id)

        assert result is False


class TestUpdateDeconstruction:
    """Tests for updating deconstruction progress."""

    def test_update_increases_progress(self, deconstruction_manager):
        """Test that update increases job progress."""
        job_id = deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            materials={"steel": 100.0}
        )

        initial_progress = deconstruction_manager.jobs[job_id].progress

        deconstruction_manager.update(dt=10.0, game_time=100.0)

        assert deconstruction_manager.jobs[job_id].progress > initial_progress

    def test_update_decreases_time_remaining(self, deconstruction_manager):
        """Test that update decreases time remaining."""
        job_id = deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            materials={"steel": 100.0}
        )

        initial_time = deconstruction_manager.jobs[job_id].time_remaining

        deconstruction_manager.update(dt=10.0, game_time=100.0)

        assert deconstruction_manager.jobs[job_id].time_remaining < initial_time

    def test_update_completes_job(self, deconstruction_manager):
        """Test that update completes job when progress reaches 100%."""
        job_id = deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            materials={"steel": 100.0},
            size=0.0,  # Minimal time
            workers=5  # Fast workers
        )

        # Run update with enough time to complete
        deconstruction_manager.update(dt=1000.0, game_time=1000.0)

        # Job should be completed and removed
        assert job_id not in deconstruction_manager.jobs
        assert deconstruction_manager.total_jobs_completed == 1


class TestAssignWorkers:
    """Tests for worker assignment."""

    def test_assign_workers_success(self, deconstruction_manager):
        """Test successfully assigning workers to a job."""
        job_id = deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            materials={"steel": 100.0},
            workers=1
        )

        result = deconstruction_manager.assign_workers(job_id, 3)

        assert result is True
        assert deconstruction_manager.jobs[job_id].workers_assigned == 3

    def test_assign_workers_nonexistent_job(self, deconstruction_manager):
        """Test assigning workers to non-existent job returns False."""
        result = deconstruction_manager.assign_workers(99999, 3)

        assert result is False

    def test_assign_workers_adjusts_time(self, deconstruction_manager):
        """Test that assigning more workers adjusts time remaining."""
        job_id = deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            materials={"steel": 100.0},
            workers=1
        )

        initial_time = deconstruction_manager.jobs[job_id].time_remaining

        deconstruction_manager.assign_workers(job_id, 3)

        new_time = deconstruction_manager.jobs[job_id].time_remaining
        assert new_time < initial_time


class TestJobStatus:
    """Tests for job status retrieval."""

    def test_get_job_status_existing(self, deconstruction_manager):
        """Test getting status of an existing job."""
        job_id = deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            materials={"steel": 100.0, "concrete": 50.0},
            workers=2
        )

        status = deconstruction_manager.get_job_status(job_id)

        assert status is not None
        assert status['id'] == job_id
        assert status['target_type'] == "building"
        assert status['target_id'] == 100
        assert status['position'] == (500.0, 300.0)
        assert status['workers'] == 2
        assert status['state'] == "IN_PROGRESS"
        assert "steel" in status['materials']

    def test_get_job_status_nonexistent(self, deconstruction_manager):
        """Test getting status of non-existent job returns None."""
        status = deconstruction_manager.get_job_status(99999)

        assert status is None


class TestActiveJobs:
    """Tests for active job tracking."""

    def test_get_active_jobs(self, deconstruction_manager):
        """Test getting list of active job IDs."""
        job_id_1 = deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            materials={"steel": 100.0}
        )

        job_id_2 = deconstruction_manager.start_deconstruction(
            target_type="prop",
            target_id=200,
            target_position=(600.0, 400.0),
            materials={"wood": 50.0}
        )

        active_jobs = deconstruction_manager.get_active_jobs()

        assert job_id_1 in active_jobs
        assert job_id_2 in active_jobs
        assert len(active_jobs) == 2

    def test_get_job_count(self, deconstruction_manager):
        """Test getting active job count."""
        deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            materials={"steel": 100.0}
        )

        deconstruction_manager.start_deconstruction(
            target_type="prop",
            target_id=200,
            target_position=(600.0, 400.0),
            materials={"wood": 50.0}
        )

        assert deconstruction_manager.get_job_count() == 2


class TestSummary:
    """Tests for summary statistics."""

    def test_get_summary(self, deconstruction_manager):
        """Test getting deconstruction system summary."""
        deconstruction_manager.start_deconstruction(
            target_type="building",
            target_id=100,
            target_position=(500.0, 300.0),
            materials={"steel": 100.0}
        )

        summary = deconstruction_manager.get_summary()

        assert 'active_jobs' in summary
        assert 'total_completed' in summary
        assert 'materials_recovered' in summary
        assert 'illegal_deconstructions' in summary
        assert 'recovery_rate' in summary
        assert 'jobs' in summary
        assert summary['active_jobs'] == 1
        assert summary['recovery_rate'] == 70.0

    def test_repr(self, deconstruction_manager):
        """Test string representation."""
        repr_str = repr(deconstruction_manager)

        assert "DeconstructionManager" in repr_str
        assert "active_jobs=" in repr_str
        assert "completed=" in repr_str
