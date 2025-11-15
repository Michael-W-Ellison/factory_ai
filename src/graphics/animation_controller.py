"""
Animation Controller - Manages sprite animations for game entities.

Handles frame timing, animation loops, and state transitions.
"""

import pygame
from typing import Dict, List, Optional, Callable
from enum import Enum


class AnimationType(Enum):
    """Types of animations."""
    IDLE = "idle"
    WALK = "walk"
    RUN = "run"
    WORK = "work"
    SLEEP = "sleep"
    VEHICLE_IDLE = "vehicle_idle"
    VEHICLE_MOVE = "vehicle_move"
    ROBOT_IDLE = "robot_idle"
    ROBOT_MOVE = "robot_move"
    DRONE_HOVER = "drone_hover"
    DRONE_MOVE = "drone_move"


class Animation:
    """
    Represents a single animation sequence.

    Attributes:
        frames: List of frame indices
        frame_duration: Duration of each frame in seconds
        loop: Whether the animation loops
    """

    def __init__(self, frames: List[int], frame_duration: float = 0.1, loop: bool = True):
        """
        Initialize an animation.

        Args:
            frames: List of frame indices to play
            frame_duration: Duration of each frame in seconds
            loop: Whether to loop the animation
        """
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.current_frame_index = 0
        self.time_in_frame = 0.0
        self.is_playing = True
        self.is_finished = False

    def update(self, dt: float) -> int:
        """
        Update the animation state.

        Args:
            dt: Delta time in seconds

        Returns:
            int: Current frame index
        """
        if not self.is_playing or self.is_finished:
            return self.frames[self.current_frame_index]

        self.time_in_frame += dt

        if self.time_in_frame >= self.frame_duration:
            self.time_in_frame -= self.frame_duration
            self.current_frame_index += 1

            if self.current_frame_index >= len(self.frames):
                if self.loop:
                    self.current_frame_index = 0
                else:
                    self.current_frame_index = len(self.frames) - 1
                    self.is_finished = True
                    self.is_playing = False

        return self.frames[self.current_frame_index]

    def reset(self):
        """Reset the animation to the first frame."""
        self.current_frame_index = 0
        self.time_in_frame = 0.0
        self.is_finished = False
        self.is_playing = True

    def get_current_frame(self) -> int:
        """Get the current frame index."""
        return self.frames[self.current_frame_index]


class AnimationController:
    """
    Controls animations for a game entity.

    Manages multiple animation states and handles transitions.
    """

    def __init__(self):
        """Initialize the animation controller."""
        self.animations: Dict[AnimationType, Animation] = {}
        self.current_animation: Optional[AnimationType] = None
        self.default_animation = AnimationType.IDLE

        # Set up default animations
        self._setup_default_animations()

    def _setup_default_animations(self):
        """Set up default animation configurations."""
        # NPC animations
        self.animations[AnimationType.IDLE] = Animation([0], 1.0, loop=True)
        self.animations[AnimationType.WALK] = Animation([0, 1, 0, 2], 0.15, loop=True)
        self.animations[AnimationType.RUN] = Animation([0, 1, 0, 2], 0.1, loop=True)
        self.animations[AnimationType.WORK] = Animation([0, 1], 0.5, loop=True)
        self.animations[AnimationType.SLEEP] = Animation([0], 1.0, loop=True)

        # Vehicle animations
        self.animations[AnimationType.VEHICLE_IDLE] = Animation([0], 1.0, loop=True)
        self.animations[AnimationType.VEHICLE_MOVE] = Animation([0], 1.0, loop=True)

        # Robot animations
        self.animations[AnimationType.ROBOT_IDLE] = Animation([0, 1], 0.5, loop=True)
        self.animations[AnimationType.ROBOT_MOVE] = Animation([0, 1], 0.2, loop=True)

        # Drone animations
        self.animations[AnimationType.DRONE_HOVER] = Animation([0, 1, 2, 3], 0.1, loop=True)
        self.animations[AnimationType.DRONE_MOVE] = Animation([0, 1, 2, 3, 4, 5], 0.08, loop=True)

    def add_animation(self, animation_type: AnimationType, frames: List[int],
                     frame_duration: float = 0.1, loop: bool = True):
        """
        Add or replace an animation.

        Args:
            animation_type: Type of animation
            frames: List of frame indices
            frame_duration: Duration of each frame
            loop: Whether to loop the animation
        """
        self.animations[animation_type] = Animation(frames, frame_duration, loop)

    def play_animation(self, animation_type: AnimationType, restart: bool = False):
        """
        Play an animation.

        Args:
            animation_type: Type of animation to play
            restart: Whether to restart if already playing
        """
        if animation_type not in self.animations:
            return

        if self.current_animation != animation_type or restart:
            self.current_animation = animation_type
            self.animations[animation_type].reset()

    def update(self, dt: float) -> int:
        """
        Update the current animation.

        Args:
            dt: Delta time in seconds

        Returns:
            int: Current frame index
        """
        if self.current_animation is None:
            self.current_animation = self.default_animation

        if self.current_animation in self.animations:
            return self.animations[self.current_animation].update(dt)

        return 0

    def get_current_frame(self) -> int:
        """Get the current frame index."""
        if self.current_animation is None:
            return 0

        if self.current_animation in self.animations:
            return self.animations[self.current_animation].get_current_frame()

        return 0

    def is_playing(self) -> bool:
        """Check if an animation is currently playing."""
        if self.current_animation is None:
            return False

        if self.current_animation in self.animations:
            return self.animations[self.current_animation].is_playing

        return False

    def is_finished(self) -> bool:
        """Check if the current animation has finished."""
        if self.current_animation is None:
            return True

        if self.current_animation in self.animations:
            return self.animations[self.current_animation].is_finished

        return True

    def set_default_animation(self, animation_type: AnimationType):
        """Set the default animation to play when nothing else is playing."""
        self.default_animation = animation_type


# Predefined animation controllers for common entity types
class NPCAnimationController(AnimationController):
    """Animation controller specifically for NPCs."""

    def update_for_activity(self, activity: str, dt: float) -> int:
        """
        Update animation based on NPC activity.

        Args:
            activity: Current NPC activity
            dt: Delta time

        Returns:
            int: Current frame index
        """
        # Map activities to animations
        activity_map = {
            'sleeping': AnimationType.SLEEP,
            'working': AnimationType.WORK,
            'walking': AnimationType.WALK,
            'commuting': AnimationType.WALK,
            'running': AnimationType.RUN,
        }

        # Default to idle if activity not mapped
        animation = activity_map.get(activity.lower(), AnimationType.IDLE)
        self.play_animation(animation)

        return self.update(dt)


class VehicleAnimationController(AnimationController):
    """Animation controller specifically for vehicles."""

    def update_for_state(self, is_moving: bool, dt: float) -> int:
        """
        Update animation based on vehicle state.

        Args:
            is_moving: Whether the vehicle is moving
            dt: Delta time

        Returns:
            int: Current frame index
        """
        if is_moving:
            self.play_animation(AnimationType.VEHICLE_MOVE)
        else:
            self.play_animation(AnimationType.VEHICLE_IDLE)

        return self.update(dt)


class RobotAnimationController(AnimationController):
    """Animation controller specifically for robots."""

    def update_for_state(self, is_moving: bool, dt: float) -> int:
        """
        Update animation based on robot state.

        Args:
            is_moving: Whether the robot is moving
            dt: Delta time

        Returns:
            int: Current frame index
        """
        if is_moving:
            self.play_animation(AnimationType.ROBOT_MOVE)
        else:
            self.play_animation(AnimationType.ROBOT_IDLE)

        return self.update(dt)


class DroneAnimationController(AnimationController):
    """Animation controller specifically for drones."""

    def update_for_state(self, is_moving: bool, battery_level: float, dt: float) -> int:
        """
        Update animation based on drone state.

        Args:
            is_moving: Whether the drone is moving
            battery_level: Current battery level (0-100)
            dt: Delta time

        Returns:
            int: Current frame index
        """
        # Slower animation if battery is low
        if battery_level < 20:
            # Modify frame duration for current animation
            if self.current_animation in self.animations:
                self.animations[self.current_animation].frame_duration = 0.2

        if is_moving:
            self.play_animation(AnimationType.DRONE_MOVE)
        else:
            self.play_animation(AnimationType.DRONE_HOVER)

        return self.update(dt)


class AnimalAnimationController(AnimationController):
    """Base animation controller for animals."""

    def __init__(self):
        """Initialize animal animation controller."""
        super().__init__()
        # Override default animations for animals
        self.animations[AnimationType.IDLE] = Animation([0], 0.5, loop=True)
        self.animations[AnimationType.WALK] = Animation([0, 1, 0, 2], 0.2, loop=True)
        self.animations[AnimationType.RUN] = Animation([0, 1, 0, 2], 0.1, loop=True)

    def update_for_behavior(self, behavior: str, dt: float) -> int:
        """
        Update animation based on animal behavior.

        Args:
            behavior: Current behavior (idle, walking, running, fleeing, chasing, eating)
            dt: Delta time

        Returns:
            int: Current frame index
        """
        behavior_map = {
            'idle': AnimationType.IDLE,
            'walking': AnimationType.WALK,
            'wander': AnimationType.WALK,
            'running': AnimationType.RUN,
            'fleeing': AnimationType.RUN,
            'chasing': AnimationType.RUN,
            'eating': AnimationType.IDLE,
        }

        animation = behavior_map.get(behavior.lower(), AnimationType.IDLE)
        self.play_animation(animation)

        return self.update(dt)


class BirdAnimationController(AnimalAnimationController):
    """Animation controller for birds."""

    def __init__(self):
        """Initialize bird animation controller."""
        super().__init__()
        # Birds have wing flapping animation
        self.animations[AnimationType.IDLE] = Animation([0, 1, 2], 0.15, loop=True)  # Gentle flapping
        self.animations[AnimationType.WALK] = Animation([0, 1, 2], 0.1, loop=True)   # Flying


class FishAnimationController(AnimalAnimationController):
    """Animation controller for fish."""

    def __init__(self):
        """Initialize fish animation controller."""
        super().__init__()
        # Fish have swimming animation with tail wag
        self.animations[AnimationType.IDLE] = Animation([0, 1, 2], 0.2, loop=True)  # Slow swim
        self.animations[AnimationType.WALK] = Animation([0, 1, 2], 0.1, loop=True)  # Fast swim
