"""
DeconstructionManager - manages building and prop deconstruction system.

Handles:
- Deconstructing buildings for material recovery
- Deconstructing props for material recovery
- Deconstruction time and worker assignment
- Material recovery rates
- Illegal material tagging from deconstruction
"""

import math
from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class DeconstructionState(Enum):
    """Deconstruction operation states."""
    IDLE = 0  # No deconstruction in progress
    IN_PROGRESS = 1  # Deconstruction happening
    COMPLETED = 2  # Deconstruction finished
    CANCELLED = 3  # Deconstruction cancelled


@dataclass
class DeconstructionJob:
    """
    Deconstruction job tracking.

    Attributes:
        id: Unique job identifier
        target_type: 'building' or 'prop'
        target_id: ID of target to deconstruct
        target_position: Position of target
        progress: Deconstruction progress (0-100%)
        workers_assigned: Number of workers assigned
        time_remaining: Time remaining (seconds)
        materials_to_recover: Materials that will be recovered
        state: Current job state
    """
    id: int
    target_type: str  # 'building' or 'prop'
    target_id: int
    target_position: Tuple[float, float]
    progress: float = 0.0
    workers_assigned: int = 0
    time_remaining: float = 0.0
    total_time: float = 0.0
    materials_to_recover: Dict[str, float] = None
    state: DeconstructionState = DeconstructionState.IDLE
    is_illegal_source: bool = False  # If true, materials will be marked illegal

    def __post_init__(self):
        if self.materials_to_recover is None:
            self.materials_to_recover = {}


class DeconstructionManager:
    """
    Manages deconstruction of buildings and props.

    Allows players to recover materials from structures.
    """

    def __init__(self, resource_manager, material_inventory=None):
        """
        Initialize deconstruction manager.

        Args:
            resource_manager: ResourceManager instance
            material_inventory: MaterialInventory instance (optional)
        """
        self.resources = resource_manager
        self.material_inventory = material_inventory

        # Active jobs
        self.jobs: Dict[int, DeconstructionJob] = {}
        self.next_job_id = 1

        # Deconstruction parameters
        self.base_deconstruction_time = 60.0  # 60 seconds for small items
        self.time_per_size_unit = 10.0  # Additional time per size unit
        self.worker_speed_multiplier = 0.5  # Each worker reduces time by 50%

        # Material recovery rates
        self.recovery_rate = 0.7  # Recover 70% of materials
        self.illegal_structure_penalty = 0.5  # Only 50% recovery from illegal structures

        # Statistics
        self.total_jobs_completed = 0
        self.total_materials_recovered = 0
        self.total_illegal_deconstructions = 0

    def start_deconstruction(self, target_type: str, target_id: int,
                            target_position: Tuple[float, float],
                            materials: Dict[str, float],
                            size: float = 1.0,
                            is_illegal: bool = False,
                            workers: int = 1) -> Optional[int]:
        """
        Start deconstructing a building or prop.

        Args:
            target_type: 'building' or 'prop'
            target_id: ID of target to deconstruct
            target_position: Position of target
            materials: Materials used to build (for recovery calculation)
            size: Size multiplier for time calculation
            is_illegal: Whether this is an illegal structure
            workers: Number of workers to assign

        Returns:
            int: Job ID if successful, None otherwise
        """
        # Calculate deconstruction time
        base_time = self.base_deconstruction_time + (self.time_per_size_unit * size)

        # Apply worker multiplier
        worker_multiplier = 1.0 / (1.0 + (workers - 1) * self.worker_speed_multiplier)
        total_time = base_time * worker_multiplier

        # Calculate materials to recover
        recovery_rate = self.recovery_rate
        if is_illegal:
            recovery_rate = self.illegal_structure_penalty

        materials_to_recover = {
            material: quantity * recovery_rate
            for material, quantity in materials.items()
        }

        # Create job
        job = DeconstructionJob(
            id=self.next_job_id,
            target_type=target_type,
            target_id=target_id,
            target_position=target_position,
            progress=0.0,
            workers_assigned=workers,
            time_remaining=total_time,
            total_time=total_time,
            materials_to_recover=materials_to_recover,
            state=DeconstructionState.IN_PROGRESS,
            is_illegal_source=is_illegal
        )

        self.jobs[self.next_job_id] = job
        self.next_job_id += 1

        print(f"\n🔨 DECONSTRUCTION STARTED")
        print(f"  Target: {target_type.title()} #{target_id}")
        print(f"  Position: ({target_position[0]:.0f}, {target_position[1]:.0f})")
        print(f"  Workers: {workers}")
        print(f"  Estimated time: {total_time:.0f} seconds")
        print(f"  Materials to recover:")
        for material, quantity in materials_to_recover.items():
            print(f"    {material}: {quantity:.1f}")

        if is_illegal:
            self.total_illegal_deconstructions += 1

        return job.id

    def cancel_deconstruction(self, job_id: int) -> bool:
        """
        Cancel a deconstruction job.

        Args:
            job_id: ID of job to cancel

        Returns:
            bool: True if successful, False otherwise
        """
        if job_id not in self.jobs:
            return False

        job = self.jobs[job_id]

        if job.state != DeconstructionState.IN_PROGRESS:
            return False

        # Cancel job
        job.state = DeconstructionState.CANCELLED

        print(f"\n🔨 DECONSTRUCTION CANCELLED")
        print(f"  Job #{job_id}")
        print(f"  Progress: {job.progress:.1f}%")

        # Remove job
        del self.jobs[job_id]

        return True

    def update(self, dt: float, game_time: float):
        """
        Update all deconstruction jobs.

        Args:
            dt: Delta time in seconds
            game_time: Current game time
        """
        # Update each job
        for job_id in list(self.jobs.keys()):
            job = self.jobs[job_id]

            if job.state == DeconstructionState.IN_PROGRESS:
                self._update_job(job, dt)

                # Check if completed
                if job.progress >= 100.0:
                    self._complete_job(job)

    def _update_job(self, job: DeconstructionJob, dt: float):
        """Update a single deconstruction job."""
        # Update progress
        if job.total_time > 0:
            progress_per_second = 100.0 / job.total_time
            job.progress += progress_per_second * dt
            job.progress = min(100.0, job.progress)

        # Update time remaining
        job.time_remaining -= dt
        job.time_remaining = max(0.0, job.time_remaining)

    def _complete_job(self, job: DeconstructionJob):
        """Complete a deconstruction job and recover materials."""
        job.state = DeconstructionState.COMPLETED
        job.progress = 100.0
        job.time_remaining = 0.0

        print(f"\n🔨 DECONSTRUCTION COMPLETED")
        print(f"  Job #{job.id}")
        print(f"  Recovered materials:")

        # Recover materials
        total_recovered = 0
        for material, quantity in job.materials_to_recover.items():
            print(f"    {material}: {quantity:.1f}")
            total_recovered += quantity

            # Add to inventory if available
            if self.material_inventory is not None:
                # Determine source type based on whether it's illegal
                from systems.material_inventory import MaterialSource

                if job.is_illegal_source:
                    # Illegal source - materials are tagged as illegal
                    source = MaterialSource.UNKNOWN  # Or appropriate illegal source
                else:
                    # Legal deconstruction - processed/legal source
                    source = MaterialSource.PROCESSED

                self.material_inventory.add_material(material, quantity, source)

        # Update statistics
        self.total_jobs_completed += 1
        self.total_materials_recovered += total_recovered

        # Remove job
        del self.jobs[job.id]

    def assign_workers(self, job_id: int, workers: int) -> bool:
        """
        Assign workers to a deconstruction job.

        Args:
            job_id: ID of job
            workers: Number of workers to assign

        Returns:
            bool: True if successful, False otherwise
        """
        if job_id not in self.jobs:
            return False

        job = self.jobs[job_id]

        if job.state != DeconstructionState.IN_PROGRESS:
            return False

        # Recalculate time with new worker count
        old_workers = job.workers_assigned
        job.workers_assigned = workers

        # Recalculate time remaining
        worker_multiplier_old = 1.0 / (1.0 + (old_workers - 1) * self.worker_speed_multiplier)
        worker_multiplier_new = 1.0 / (1.0 + (workers - 1) * self.worker_speed_multiplier)

        # Adjust time remaining
        job.time_remaining *= worker_multiplier_new / worker_multiplier_old

        print(f"\n🔨 WORKERS ASSIGNED: {workers}")
        print(f"  Job #{job_id}")
        print(f"  New estimated time: {job.time_remaining:.0f} seconds")

        return True

    def get_job_status(self, job_id: int) -> Optional[Dict]:
        """
        Get status of a deconstruction job.

        Args:
            job_id: ID of job

        Returns:
            dict: Job status information, or None if not found
        """
        if job_id not in self.jobs:
            return None

        job = self.jobs[job_id]

        return {
            'id': job.id,
            'target_type': job.target_type,
            'target_id': job.target_id,
            'position': job.target_position,
            'progress': job.progress,
            'workers': job.workers_assigned,
            'time_remaining': job.time_remaining,
            'state': job.state.name,
            'materials': job.materials_to_recover
        }

    def get_active_jobs(self) -> List[int]:
        """Get list of active job IDs."""
        return [
            job_id for job_id, job in self.jobs.items()
            if job.state == DeconstructionState.IN_PROGRESS
        ]

    def get_job_count(self) -> int:
        """Get number of active jobs."""
        return len(self.get_active_jobs())

    def get_summary(self) -> Dict:
        """
        Get deconstruction system summary.

        Returns:
            dict: Summary information
        """
        return {
            'active_jobs': len(self.get_active_jobs()),
            'total_completed': self.total_jobs_completed,
            'materials_recovered': self.total_materials_recovered,
            'illegal_deconstructions': self.total_illegal_deconstructions,
            'recovery_rate': self.recovery_rate * 100,
            'jobs': [self.get_job_status(job_id) for job_id in self.get_active_jobs()]
        }

    def __repr__(self):
        """String representation for debugging."""
        return (f"DeconstructionManager(active_jobs={len(self.get_active_jobs())}, "
                f"completed={self.total_jobs_completed})")
