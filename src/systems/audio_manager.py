"""
Audio Manager - Handles all game audio (music and sound effects).

Provides:
- Background music playback with looping
- Sound effects with volume control
- Integration with SettingsManager for volume settings
- Graceful degradation when audio files are missing
"""

import os
import pygame
from typing import Dict, Optional, List
from src.core.logger import get_logger

logger = get_logger(__name__)


class AudioManager:
    """
    Manages all game audio including music and sound effects.

    Integrates with SettingsManager to respect user volume preferences.
    Handles missing audio files gracefully without crashing.
    """

    # Supported audio formats
    SUPPORTED_FORMATS = ('.wav', '.ogg', '.mp3')

    # Sound effect categories and their files
    SFX_DEFINITIONS = {
        # UI sounds
        'ui_click': 'ui/click.wav',
        'ui_hover': 'ui/hover.wav',
        'ui_open': 'ui/open.wav',
        'ui_close': 'ui/close.wav',
        'ui_error': 'ui/error.wav',
        'ui_success': 'ui/success.wav',

        # Game events
        'build_place': 'game/build_place.wav',
        'build_complete': 'game/build_complete.wav',
        'build_demolish': 'game/demolish.wav',
        'research_complete': 'game/research_complete.wav',
        'research_start': 'game/research_start.wav',

        # Robot sounds
        'robot_select': 'robot/select.wav',
        'robot_move': 'robot/move.wav',
        'robot_collect': 'robot/collect.wav',
        'robot_deposit': 'robot/deposit.wav',
        'robot_low_battery': 'robot/low_battery.wav',

        # Alerts
        'alert_warning': 'alerts/warning.wav',
        'alert_danger': 'alerts/danger.wav',
        'alert_inspection': 'alerts/inspection.wav',
        'alert_police': 'alerts/police.wav',

        # Ambient
        'ambient_factory': 'ambient/factory_hum.wav',
        'ambient_city': 'ambient/city.wav',

        # Money
        'money_gain': 'game/money_gain.wav',
        'money_loss': 'game/money_loss.wav',
    }

    # Music tracks
    MUSIC_TRACKS = {
        'menu': 'music/menu_theme.ogg',
        'gameplay': 'music/gameplay.ogg',
        'tense': 'music/tense.ogg',
        'victory': 'music/victory.ogg',
        'defeat': 'music/defeat.ogg',
    }

    def __init__(self, settings_manager=None, sound_dir: str = 'data/sounds'):
        """
        Initialize the audio manager.

        Args:
            settings_manager: SettingsManager instance for volume settings
            sound_dir: Directory containing sound files
        """
        self.settings_manager = settings_manager
        self.sound_dir = sound_dir

        # Volume levels (0.0 to 1.0)
        self.master_volume = 1.0
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.muted = False

        # Audio state
        self.initialized = False
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.current_music: Optional[str] = None
        self.music_paused = False

        # Initialize pygame mixer
        self._init_mixer()

        # Load initial settings
        if settings_manager:
            self.apply_settings(settings_manager)

        # Load available sounds
        self._load_sounds()

    def _init_mixer(self) -> bool:
        """Initialize pygame mixer for audio playback."""
        try:
            # Check if pygame is initialized
            if not pygame.get_init():
                logger.warning("Pygame not initialized, skipping audio initialization")
                return False

            # Initialize mixer with good defaults
            pygame.mixer.init(
                frequency=44100,  # CD quality
                size=-16,         # 16-bit signed
                channels=2,       # Stereo
                buffer=512        # Low latency
            )

            # Set up multiple channels for simultaneous sounds
            pygame.mixer.set_num_channels(16)

            self.initialized = True
            logger.info("Audio system initialized successfully")
            return True

        except pygame.error as e:
            logger.warning(f"Could not initialize audio system: {e}")
            self.initialized = False
            return False

    def _load_sounds(self) -> None:
        """Load all available sound effects."""
        if not self.initialized:
            logger.debug("Audio not initialized, skipping sound loading")
            return

        if not os.path.exists(self.sound_dir):
            logger.info(f"Sound directory '{self.sound_dir}' not found - audio disabled")
            return

        loaded_count = 0
        for name, relative_path in self.SFX_DEFINITIONS.items():
            full_path = os.path.join(self.sound_dir, relative_path)

            if os.path.exists(full_path):
                try:
                    sound = pygame.mixer.Sound(full_path)
                    self.sounds[name] = sound
                    loaded_count += 1
                    logger.debug(f"Loaded sound: {name}")
                except pygame.error as e:
                    logger.warning(f"Could not load sound '{name}': {e}")
            else:
                logger.debug(f"Sound file not found: {relative_path}")

        if loaded_count > 0:
            logger.info(f"Loaded {loaded_count} sound effects")
        else:
            logger.info("No sound files found - game will run without audio")

    def apply_settings(self, settings_manager) -> None:
        """
        Apply volume settings from SettingsManager.

        Args:
            settings_manager: SettingsManager instance
        """
        self.settings_manager = settings_manager

        self.master_volume = settings_manager.get('audio', 'master_volume', 1.0)
        self.music_volume = settings_manager.get('audio', 'music_volume', 0.7)
        self.sfx_volume = settings_manager.get('audio', 'sfx_volume', 0.8)
        self.muted = settings_manager.get('audio', 'mute', False)

        # Apply music volume immediately
        self._update_music_volume()

        logger.debug(f"Applied audio settings: master={self.master_volume}, "
                    f"music={self.music_volume}, sfx={self.sfx_volume}, muted={self.muted}")

    def set_master_volume(self, volume: float) -> None:
        """Set master volume (0.0 to 1.0)."""
        self.master_volume = max(0.0, min(1.0, volume))
        self._update_music_volume()

        if self.settings_manager:
            self.settings_manager.set('audio', 'master_volume', self.master_volume)

    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        self._update_music_volume()

        if self.settings_manager:
            self.settings_manager.set('audio', 'music_volume', self.music_volume)

    def set_sfx_volume(self, volume: float) -> None:
        """Set sound effects volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))

        if self.settings_manager:
            self.settings_manager.set('audio', 'sfx_volume', self.sfx_volume)

    def set_muted(self, muted: bool) -> None:
        """Set mute state."""
        self.muted = muted
        self._update_music_volume()

        if self.settings_manager:
            self.settings_manager.set('audio', 'mute', self.muted)

    def toggle_mute(self) -> bool:
        """Toggle mute state. Returns new mute state."""
        self.set_muted(not self.muted)
        return self.muted

    def _update_music_volume(self) -> None:
        """Update the currently playing music volume."""
        if not self.initialized:
            return

        if self.muted:
            pygame.mixer.music.set_volume(0)
        else:
            effective_volume = self.master_volume * self.music_volume
            pygame.mixer.music.set_volume(effective_volume)

    def _get_effective_sfx_volume(self) -> float:
        """Get the effective SFX volume considering master and mute."""
        if self.muted:
            return 0.0
        return self.master_volume * self.sfx_volume

    # === Sound Effects ===

    def play_sfx(self, name: str, volume_multiplier: float = 1.0) -> bool:
        """
        Play a sound effect.

        Args:
            name: Sound effect name (from SFX_DEFINITIONS)
            volume_multiplier: Additional volume multiplier (0.0 to 1.0)

        Returns:
            True if sound was played, False otherwise
        """
        if not self.initialized or self.muted:
            return False

        if name not in self.sounds:
            logger.debug(f"Sound not loaded: {name}")
            return False

        try:
            sound = self.sounds[name]
            effective_volume = self._get_effective_sfx_volume() * volume_multiplier
            sound.set_volume(effective_volume)
            sound.play()
            return True
        except pygame.error as e:
            logger.warning(f"Could not play sound '{name}': {e}")
            return False

    def play_ui_click(self) -> bool:
        """Play UI click sound."""
        return self.play_sfx('ui_click')

    def play_ui_hover(self) -> bool:
        """Play UI hover sound."""
        return self.play_sfx('ui_hover', 0.5)  # Quieter

    def play_build_place(self) -> bool:
        """Play building placement sound."""
        return self.play_sfx('build_place')

    def play_research_complete(self) -> bool:
        """Play research completion sound."""
        return self.play_sfx('research_complete')

    def play_alert(self, alert_type: str = 'warning') -> bool:
        """Play alert sound."""
        return self.play_sfx(f'alert_{alert_type}')

    def play_robot_select(self) -> bool:
        """Play robot selection sound."""
        return self.play_sfx('robot_select')

    def play_money_gain(self) -> bool:
        """Play money gain sound."""
        return self.play_sfx('money_gain')

    def play_money_loss(self) -> bool:
        """Play money loss sound."""
        return self.play_sfx('money_loss')

    # === Music ===

    def play_music(self, track_name: str, loops: int = -1, fade_ms: int = 1000) -> bool:
        """
        Play background music.

        Args:
            track_name: Music track name (from MUSIC_TRACKS)
            loops: Number of times to loop (-1 for infinite)
            fade_ms: Fade in duration in milliseconds

        Returns:
            True if music started, False otherwise
        """
        if not self.initialized:
            return False

        if track_name not in self.MUSIC_TRACKS:
            logger.warning(f"Unknown music track: {track_name}")
            return False

        relative_path = self.MUSIC_TRACKS[track_name]
        full_path = os.path.join(self.sound_dir, relative_path)

        if not os.path.exists(full_path):
            logger.debug(f"Music file not found: {relative_path}")
            return False

        try:
            # Stop current music with fade
            if self.current_music:
                pygame.mixer.music.fadeout(fade_ms // 2)

            # Load and play new track
            pygame.mixer.music.load(full_path)
            self._update_music_volume()
            pygame.mixer.music.play(loops, fade_ms=fade_ms)

            self.current_music = track_name
            self.music_paused = False
            logger.info(f"Playing music: {track_name}")
            return True

        except pygame.error as e:
            logger.warning(f"Could not play music '{track_name}': {e}")
            return False

    def stop_music(self, fade_ms: int = 1000) -> None:
        """Stop background music with fade out."""
        if not self.initialized:
            return

        try:
            pygame.mixer.music.fadeout(fade_ms)
            self.current_music = None
            self.music_paused = False
        except pygame.error as e:
            logger.debug(f"Audio operation failed (non-critical): {e}")

    def pause_music(self) -> None:
        """Pause background music."""
        if not self.initialized:
            return

        try:
            pygame.mixer.music.pause()
            self.music_paused = True
        except pygame.error as e:
            logger.debug(f"Audio operation failed (non-critical): {e}")

    def resume_music(self) -> None:
        """Resume paused background music."""
        if not self.initialized:
            return

        try:
            pygame.mixer.music.unpause()
            self.music_paused = False
        except pygame.error as e:
            logger.debug(f"Audio operation failed (non-critical): {e}")

    def is_music_playing(self) -> bool:
        """Check if music is currently playing."""
        if not self.initialized:
            return False
        return pygame.mixer.music.get_busy() and not self.music_paused

    # === Utility ===

    def stop_all(self) -> None:
        """Stop all audio (music and sound effects)."""
        if not self.initialized:
            return

        try:
            pygame.mixer.stop()  # Stop all sound effects
            pygame.mixer.music.stop()  # Stop music
            self.current_music = None
            self.music_paused = False
        except pygame.error as e:
            logger.debug(f"Audio operation failed (non-critical): {e}")

    def get_available_sounds(self) -> List[str]:
        """Get list of loaded sound effect names."""
        return list(self.sounds.keys())

    def get_stats(self) -> Dict:
        """Get audio system statistics."""
        return {
            'initialized': self.initialized,
            'sounds_loaded': len(self.sounds),
            'current_music': self.current_music,
            'music_playing': self.is_music_playing(),
            'master_volume': self.master_volume,
            'music_volume': self.music_volume,
            'sfx_volume': self.sfx_volume,
            'muted': self.muted,
        }

    def cleanup(self) -> None:
        """Clean up audio resources."""
        if self.initialized:
            try:
                self.stop_all()
                pygame.mixer.quit()
                logger.info("Audio system cleaned up")
            except pygame.error as e:
                logger.debug(f"Audio cleanup failed (non-critical): {e}")
        self.initialized = False
        self.sounds.clear()
