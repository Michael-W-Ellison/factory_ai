"""
Audio Events - Centralized audio event handling for game systems.

Provides a clean interface for triggering audio events from any game system
without requiring direct access to the AudioManager.
"""

from typing import Optional, TYPE_CHECKING
from enum import Enum
from src.core.logger import get_logger

if TYPE_CHECKING:
    from src.systems.audio_manager import AudioManager

logger = get_logger(__name__)


class MusicState(Enum):
    """Music states for dynamic music switching."""
    MENU = "menu"
    GAMEPLAY_CALM = "gameplay"
    GAMEPLAY_TENSE = "tense"
    VICTORY = "victory"
    DEFEAT = "defeat"


class AudioEventHandler:
    """
    Handles audio events from game systems.

    This class provides a centralized way to trigger audio events,
    making it easy to add audio to any game system without tight coupling.
    """

    _instance: Optional['AudioEventHandler'] = None

    def __init__(self, audio_manager: 'AudioManager'):
        """
        Initialize audio event handler.

        Args:
            audio_manager: AudioManager instance
        """
        self.audio = audio_manager
        self.current_music_state = MusicState.MENU
        self.suspicion_threshold_tense = 60
        self.last_suspicion_level = 0
        AudioEventHandler._instance = self

    @classmethod
    def get_instance(cls) -> Optional['AudioEventHandler']:
        """Get the global AudioEventHandler instance."""
        return cls._instance

    # === Building Events ===

    def on_building_placed(self):
        """Called when a building is placed."""
        self.audio.play_build_place()

    def on_building_complete(self):
        """Called when construction completes."""
        self.audio.play_sfx('build_complete')

    def on_building_demolished(self):
        """Called when a building is demolished."""
        self.audio.play_sfx('build_demolish')

    # === Research Events ===

    def on_research_started(self):
        """Called when research begins."""
        self.audio.play_sfx('research_start')

    def on_research_complete(self):
        """Called when research completes."""
        self.audio.play_research_complete()

    # === Robot Events ===

    def on_robot_selected(self):
        """Called when a robot is selected."""
        self.audio.play_robot_select()

    def on_robot_move(self):
        """Called when robot starts moving."""
        self.audio.play_sfx('robot_move', 0.5)

    def on_robot_collect(self):
        """Called when robot collects materials."""
        self.audio.play_sfx('robot_collect')

    def on_robot_deposit(self):
        """Called when robot deposits materials."""
        self.audio.play_sfx('robot_deposit')

    def on_robot_low_battery(self):
        """Called when robot battery is low."""
        self.audio.play_sfx('robot_low_battery')

    # === Money Events ===

    def on_money_gained(self, amount: float = 0):
        """Called when money is gained."""
        if amount >= 1000:
            self.audio.play_money_gain()

    def on_money_lost(self, amount: float = 0):
        """Called when money is lost."""
        if amount >= 500:
            self.audio.play_money_loss()

    # === Alert Events ===

    def on_warning(self):
        """Called for general warnings."""
        self.audio.play_alert('warning')

    def on_danger(self):
        """Called for danger alerts."""
        self.audio.play_alert('danger')

    def on_inspection_warning(self):
        """Called when inspection is imminent."""
        self.audio.play_alert('inspection')

    def on_police_alert(self):
        """Called when police are alerted."""
        self.audio.play_alert('police')

    # === UI Events ===

    def on_ui_click(self):
        """Called on UI button click."""
        self.audio.play_ui_click()

    def on_ui_hover(self):
        """Called on UI element hover."""
        self.audio.play_ui_hover()

    def on_menu_open(self):
        """Called when menu opens."""
        self.audio.play_sfx('ui_open')

    def on_menu_close(self):
        """Called when menu closes."""
        self.audio.play_sfx('ui_close')

    def on_ui_error(self):
        """Called on UI error."""
        self.audio.play_sfx('ui_error')

    def on_ui_success(self):
        """Called on UI success."""
        self.audio.play_sfx('ui_success')

    # === Game State Events ===

    def on_game_start(self):
        """Called when game starts."""
        self.set_music_state(MusicState.GAMEPLAY_CALM)

    def on_game_victory(self):
        """Called on victory."""
        self.set_music_state(MusicState.VICTORY)

    def on_game_defeat(self):
        """Called on defeat."""
        self.set_music_state(MusicState.DEFEAT)

    def on_return_to_menu(self):
        """Called when returning to menu."""
        self.set_music_state(MusicState.MENU)

    # === Dynamic Music ===

    def update_music_for_suspicion(self, suspicion_level: float):
        """
        Update music based on current suspicion level.

        Args:
            suspicion_level: Current suspicion level (0-100)
        """
        if self.current_music_state in (MusicState.VICTORY, MusicState.DEFEAT):
            return

        # Hysteresis to prevent rapid switching
        if suspicion_level >= self.suspicion_threshold_tense + 5:
            if self.current_music_state != MusicState.GAMEPLAY_TENSE:
                self.set_music_state(MusicState.GAMEPLAY_TENSE)
        elif suspicion_level < self.suspicion_threshold_tense - 5:
            if self.current_music_state != MusicState.GAMEPLAY_CALM:
                self.set_music_state(MusicState.GAMEPLAY_CALM)

        self.last_suspicion_level = suspicion_level

    def set_music_state(self, state: MusicState):
        """
        Set the current music state and play appropriate track.

        Args:
            state: Music state to switch to
        """
        if state == self.current_music_state:
            return

        self.current_music_state = state

        track_map = {
            MusicState.MENU: 'menu',
            MusicState.GAMEPLAY_CALM: 'gameplay',
            MusicState.GAMEPLAY_TENSE: 'tense',
            MusicState.VICTORY: 'victory',
            MusicState.DEFEAT: 'defeat',
        }

        track = track_map.get(state, 'gameplay')
        loops = -1 if state not in (MusicState.VICTORY, MusicState.DEFEAT) else 0

        self.audio.play_music(track, loops=loops, fade_ms=2000)
        logger.debug(f"Music state changed to: {state.value}")


def get_audio_events() -> Optional[AudioEventHandler]:
    """Get the global AudioEventHandler instance."""
    return AudioEventHandler.get_instance()
