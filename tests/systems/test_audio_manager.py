"""
Unit tests for AudioManager.

Tests audio playback, volume control, and settings integration.
Mocks pygame.mixer for testing without actual audio hardware.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
import os


@pytest.fixture
def mock_pygame():
    """Create comprehensive pygame mock."""
    mock_pg = MagicMock()

    # Mock pygame.get_init to return True
    mock_pg.get_init.return_value = True

    # Mock mixer module
    mock_mixer = MagicMock()
    mock_pg.mixer = mock_mixer

    # Mock Sound class
    mock_sound = MagicMock()
    mock_mixer.Sound.return_value = mock_sound

    # Mock mixer.music module
    mock_music = MagicMock()
    mock_mixer.music = mock_music
    mock_music.get_busy.return_value = False

    return mock_pg


@pytest.fixture
def mock_settings_manager():
    """Create mock settings manager."""
    settings = MagicMock()
    settings.get.side_effect = lambda section, key, default=None: {
        ('audio', 'master_volume'): 1.0,
        ('audio', 'music_volume'): 0.7,
        ('audio', 'sfx_volume'): 0.8,
        ('audio', 'mute'): False,
    }.get((section, key), default)
    return settings


@pytest.fixture
def audio_manager(mock_pygame):
    """Create AudioManager with mocked pygame."""
    with patch.dict('sys.modules', {'pygame': mock_pygame}):
        with patch('os.path.exists', return_value=False):
            from src.systems.audio_manager import AudioManager
            return AudioManager(settings_manager=None, sound_dir='data/sounds')


@pytest.fixture
def audio_manager_with_sounds(mock_pygame):
    """Create AudioManager with some mock sounds loaded."""
    with patch.dict('sys.modules', {'pygame': mock_pygame}):
        with patch('os.path.exists', return_value=False):
            from src.systems.audio_manager import AudioManager
            am = AudioManager(settings_manager=None, sound_dir='data/sounds')
            am.initialized = True
            # Manually add some mock sounds
            am.sounds['ui_click'] = MagicMock()
            am.sounds['ui_hover'] = MagicMock()
            return am


class TestAudioManagerInit:
    """Tests for AudioManager initialization."""

    def test_init_default_volumes(self, audio_manager):
        """Test default volume values."""
        assert audio_manager.master_volume == 1.0
        assert audio_manager.music_volume == 0.7
        assert audio_manager.sfx_volume == 0.8

    def test_init_not_muted(self, audio_manager):
        """Test default mute state."""
        assert audio_manager.muted is False

    def test_init_empty_sounds(self, audio_manager):
        """Test sounds start empty (no sound directory)."""
        assert audio_manager.sounds == {}

    def test_init_no_current_music(self, audio_manager):
        """Test no music playing initially."""
        assert audio_manager.current_music is None

    def test_init_with_settings_manager(self, mock_pygame, mock_settings_manager):
        """Test initialization with settings manager."""
        with patch.dict('sys.modules', {'pygame': mock_pygame}):
            with patch('os.path.exists', return_value=False):
                from src.systems.audio_manager import AudioManager
                am = AudioManager(
                    settings_manager=mock_settings_manager,
                    sound_dir='data/sounds'
                )

                assert am.settings_manager == mock_settings_manager


class TestVolumeControl:
    """Tests for volume control."""

    def test_set_master_volume(self, audio_manager):
        """Test setting master volume."""
        audio_manager.set_master_volume(0.5)
        assert audio_manager.master_volume == 0.5

    def test_set_master_volume_clamps_high(self, audio_manager):
        """Test master volume clamped to max 1.0."""
        audio_manager.set_master_volume(1.5)
        assert audio_manager.master_volume == 1.0

    def test_set_master_volume_clamps_low(self, audio_manager):
        """Test master volume clamped to min 0.0."""
        audio_manager.set_master_volume(-0.5)
        assert audio_manager.master_volume == 0.0

    def test_set_music_volume(self, audio_manager):
        """Test setting music volume."""
        audio_manager.set_music_volume(0.3)
        assert audio_manager.music_volume == 0.3

    def test_set_sfx_volume(self, audio_manager):
        """Test setting SFX volume."""
        audio_manager.set_sfx_volume(0.6)
        assert audio_manager.sfx_volume == 0.6


class TestMuteControl:
    """Tests for mute functionality."""

    def test_set_muted_true(self, audio_manager):
        """Test setting mute on."""
        audio_manager.set_muted(True)
        assert audio_manager.muted is True

    def test_set_muted_false(self, audio_manager):
        """Test setting mute off."""
        audio_manager.muted = True
        audio_manager.set_muted(False)
        assert audio_manager.muted is False

    def test_toggle_mute_on(self, audio_manager):
        """Test toggling mute on."""
        audio_manager.muted = False

        result = audio_manager.toggle_mute()

        assert result is True
        assert audio_manager.muted is True

    def test_toggle_mute_off(self, audio_manager):
        """Test toggling mute off."""
        audio_manager.muted = True

        result = audio_manager.toggle_mute()

        assert result is False
        assert audio_manager.muted is False


class TestSoundEffects:
    """Tests for sound effect playback."""

    def test_play_sfx_not_initialized(self, audio_manager):
        """Test play_sfx when not initialized."""
        audio_manager.initialized = False

        result = audio_manager.play_sfx('ui_click')

        assert result is False

    def test_play_sfx_muted(self, audio_manager_with_sounds):
        """Test play_sfx when muted."""
        audio_manager_with_sounds.muted = True

        result = audio_manager_with_sounds.play_sfx('ui_click')

        assert result is False

    def test_play_sfx_not_loaded(self, audio_manager_with_sounds):
        """Test play_sfx with sound not loaded."""
        result = audio_manager_with_sounds.play_sfx('nonexistent_sound')
        assert result is False

    def test_play_sfx_success(self, audio_manager_with_sounds):
        """Test successful sound playback."""
        result = audio_manager_with_sounds.play_sfx('ui_click')

        assert result is True
        audio_manager_with_sounds.sounds['ui_click'].play.assert_called_once()

    def test_play_sfx_with_volume_multiplier(self, audio_manager_with_sounds):
        """Test sound playback with volume multiplier."""
        audio_manager_with_sounds.play_sfx('ui_click', volume_multiplier=0.5)

        audio_manager_with_sounds.sounds['ui_click'].set_volume.assert_called()


class TestConvenienceMethods:
    """Tests for convenience sound methods."""

    def test_play_ui_click(self, audio_manager_with_sounds):
        """Test UI click sound method."""
        result = audio_manager_with_sounds.play_ui_click()
        assert result is True

    def test_play_ui_hover(self, audio_manager_with_sounds):
        """Test UI hover sound method."""
        result = audio_manager_with_sounds.play_ui_hover()
        assert result is True


class TestMusicPlayback:
    """Tests for music playback."""

    def test_play_music_not_initialized(self, audio_manager):
        """Test play_music when not initialized."""
        audio_manager.initialized = False

        result = audio_manager.play_music('gameplay')

        assert result is False

    def test_play_music_unknown_track(self, audio_manager):
        """Test play_music with unknown track name."""
        audio_manager.initialized = True

        result = audio_manager.play_music('nonexistent_track')

        assert result is False

    def test_stop_music(self, mock_pygame, audio_manager):
        """Test stopping music."""
        audio_manager.initialized = True
        audio_manager.current_music = 'gameplay'

        audio_manager.stop_music()

        assert audio_manager.current_music is None

    def test_pause_music(self, audio_manager):
        """Test pausing music."""
        audio_manager.initialized = True

        audio_manager.pause_music()

        assert audio_manager.music_paused is True

    def test_resume_music(self, audio_manager):
        """Test resuming music."""
        audio_manager.initialized = True
        audio_manager.music_paused = True

        audio_manager.resume_music()

        assert audio_manager.music_paused is False

    def test_is_music_playing_false(self, mock_pygame, audio_manager):
        """Test is_music_playing when not playing."""
        audio_manager.initialized = True
        mock_pygame.mixer.music.get_busy.return_value = False

        result = audio_manager.is_music_playing()

        assert result is False


class TestEffectiveVolume:
    """Tests for effective volume calculations."""

    def test_effective_sfx_volume_not_muted(self, audio_manager):
        """Test effective SFX volume when not muted."""
        audio_manager.master_volume = 0.8
        audio_manager.sfx_volume = 0.5

        effective = audio_manager._get_effective_sfx_volume()

        assert effective == pytest.approx(0.4)

    def test_effective_sfx_volume_muted(self, audio_manager):
        """Test effective SFX volume when muted."""
        audio_manager.muted = True

        effective = audio_manager._get_effective_sfx_volume()

        assert effective == 0.0


class TestApplySettings:
    """Tests for applying settings from SettingsManager."""

    def test_apply_settings(self, audio_manager, mock_settings_manager):
        """Test applying settings from manager."""
        audio_manager.apply_settings(mock_settings_manager)

        assert audio_manager.master_volume == 1.0
        assert audio_manager.music_volume == 0.7
        assert audio_manager.sfx_volume == 0.8
        assert audio_manager.muted is False


class TestUtilityMethods:
    """Tests for utility methods."""

    def test_get_available_sounds(self, audio_manager_with_sounds):
        """Test getting list of available sounds."""
        sounds = audio_manager_with_sounds.get_available_sounds()

        assert 'ui_click' in sounds
        assert 'ui_hover' in sounds

    def test_stop_all(self, mock_pygame, audio_manager):
        """Test stopping all audio."""
        audio_manager.initialized = True
        audio_manager.current_music = 'gameplay'

        audio_manager.stop_all()

        assert audio_manager.current_music is None
        assert audio_manager.music_paused is False


class TestStatistics:
    """Tests for audio statistics."""

    def test_get_stats(self, audio_manager_with_sounds):
        """Test getting audio statistics."""
        stats = audio_manager_with_sounds.get_stats()

        assert 'initialized' in stats
        assert 'sounds_loaded' in stats
        assert 'current_music' in stats
        assert 'music_playing' in stats
        assert 'master_volume' in stats
        assert 'muted' in stats

    def test_get_stats_values(self, audio_manager_with_sounds):
        """Test audio statistics values."""
        stats = audio_manager_with_sounds.get_stats()

        assert stats['sounds_loaded'] == 2
        assert stats['master_volume'] == 1.0


class TestCleanup:
    """Tests for audio cleanup."""

    def test_cleanup(self, mock_pygame, audio_manager):
        """Test audio cleanup."""
        audio_manager.initialized = True
        audio_manager.sounds['test'] = MagicMock()

        audio_manager.cleanup()

        assert audio_manager.initialized is False
        assert audio_manager.sounds == {}

    def test_cleanup_not_initialized(self, audio_manager):
        """Test cleanup when not initialized."""
        audio_manager.initialized = False

        # Should not raise any errors
        audio_manager.cleanup()

        assert audio_manager.initialized is False


class TestSupportedFormats:
    """Tests for supported audio formats."""

    def test_supported_formats_defined(self, audio_manager):
        """Test that supported formats are defined."""
        from src.systems.audio_manager import AudioManager

        assert '.wav' in AudioManager.SUPPORTED_FORMATS
        assert '.ogg' in AudioManager.SUPPORTED_FORMATS
        assert '.mp3' in AudioManager.SUPPORTED_FORMATS


class TestSFXDefinitions:
    """Tests for SFX definitions."""

    def test_sfx_definitions_exist(self, audio_manager):
        """Test that SFX definitions are defined."""
        from src.systems.audio_manager import AudioManager

        assert 'ui_click' in AudioManager.SFX_DEFINITIONS
        assert 'robot_select' in AudioManager.SFX_DEFINITIONS
        assert 'alert_warning' in AudioManager.SFX_DEFINITIONS


class TestMusicTracks:
    """Tests for music track definitions."""

    def test_music_tracks_defined(self, audio_manager):
        """Test that music tracks are defined."""
        from src.systems.audio_manager import AudioManager

        assert 'menu' in AudioManager.MUSIC_TRACKS
        assert 'gameplay' in AudioManager.MUSIC_TRACKS
