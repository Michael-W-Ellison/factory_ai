"""
Tests for the SaveManager class.

Tests save/load operations, validation, sanitization, and auto-save functionality.
Uses mocked file operations to avoid actual disk I/O.
"""

import sys
from unittest.mock import MagicMock

# Mock pygame before importing any src modules
sys.modules['pygame'] = MagicMock()

import json
import os
import pytest
from unittest.mock import patch, mock_open

from src.systems.save_manager import SaveManager, SaveValidationError


class TestSaveNameSanitization:
    """Tests for save name sanitization."""

    def test_valid_alphanumeric_name(self):
        """Test that valid alphanumeric names pass sanitization."""
        manager = SaveManager()
        result = manager._sanitize_save_name("mysave123")
        assert result == "mysave123"

    def test_valid_name_with_underscore(self):
        """Test that underscores are allowed in save names."""
        manager = SaveManager()
        result = manager._sanitize_save_name("my_save_file")
        assert result == "my_save_file"

    def test_valid_name_with_hyphen(self):
        """Test that hyphens are allowed in save names."""
        manager = SaveManager()
        result = manager._sanitize_save_name("my-save-file")
        assert result == "my-save-file"

    def test_valid_name_with_space(self):
        """Test that spaces are allowed in save names."""
        manager = SaveManager()
        result = manager._sanitize_save_name("My Save File")
        assert result == "My Save File"

    def test_empty_name_raises_error(self):
        """Test that empty save names raise ValueError."""
        manager = SaveManager()
        with pytest.raises(ValueError, match="cannot be empty"):
            manager._sanitize_save_name("")

    def test_whitespace_only_name_raises_error(self):
        """Test that whitespace-only names raise ValueError."""
        manager = SaveManager()
        with pytest.raises(ValueError, match="cannot be empty"):
            manager._sanitize_save_name("   ")

    def test_path_traversal_rejected(self):
        """Test that path traversal attempts are rejected."""
        manager = SaveManager()
        with pytest.raises(ValueError, match="cannot contain"):
            manager._sanitize_save_name("../../../etc/passwd")

    def test_absolute_path_rejected(self):
        """Test that absolute paths are rejected."""
        manager = SaveManager()
        with pytest.raises(ValueError, match="cannot be an absolute path"):
            manager._sanitize_save_name("/etc/passwd")

    def test_forward_slash_rejected(self):
        """Test that forward slashes are rejected."""
        manager = SaveManager()
        with pytest.raises(ValueError, match="cannot contain path separators"):
            manager._sanitize_save_name("subdir/savefile")

    def test_backslash_rejected(self):
        """Test that backslashes are rejected."""
        manager = SaveManager()
        with pytest.raises(ValueError, match="cannot contain path separators"):
            manager._sanitize_save_name("subdir\\savefile")

    def test_dangerous_characters_rejected(self):
        """Test that dangerous characters are rejected."""
        manager = SaveManager()
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in dangerous_chars:
            with pytest.raises(ValueError):
                manager._sanitize_save_name(f"save{char}file")

    def test_name_length_limit(self):
        """Test that names exceeding max length are rejected."""
        manager = SaveManager()
        long_name = "a" * 51
        with pytest.raises(ValueError, match="cannot exceed"):
            manager._sanitize_save_name(long_name)


class TestPathSecurityValidation:
    """Tests for path security validation."""

    def test_valid_path_within_save_directory(self):
        """Test that paths within save directory are valid."""
        manager = SaveManager()
        # Use a path that would be in the save directory
        file_path = os.path.join(manager.SAVE_DIRECTORY, "test.json")
        result = manager._validate_path_security(file_path)
        assert result is True

    def test_path_escaping_save_directory_rejected(self):
        """Test that paths escaping save directory are rejected."""
        manager = SaveManager()
        with pytest.raises(ValueError, match="escapes save directory"):
            manager._validate_path_security("/etc/passwd")


class TestSaveSchemaValidation:
    """Tests for save file schema validation."""

    def test_valid_save_data_passes_validation(self):
        """Test that valid save data passes validation."""
        manager = SaveManager()
        save_data = {
            'version': '1.0',
            'timestamp': '2024-01-01T00:00:00',
            'game_state': {
                'time': {'day': 1, 'hour': 6},
                'resources': {'money': 10000},
                'buildings': [],
                'robots': [],
                'research': {}
            }
        }
        is_valid, warnings = manager._validate_save_schema(save_data)
        assert is_valid is True

    def test_missing_version_generates_warning(self):
        """Test that missing version generates warning."""
        manager = SaveManager()
        save_data = {
            'timestamp': '2024-01-01T00:00:00',
            'game_state': {}
        }
        is_valid, warnings = manager._validate_save_schema(save_data)
        assert any('version' in w for w in warnings)

    def test_missing_game_state_fails_validation(self):
        """Test that missing game_state fails validation."""
        manager = SaveManager()
        save_data = {
            'version': '1.0',
            'timestamp': '2024-01-01T00:00:00'
        }
        is_valid, warnings = manager._validate_save_schema(save_data)
        assert is_valid is False

    def test_invalid_time_data_type_generates_warning(self):
        """Test that invalid time data type generates warning."""
        manager = SaveManager()
        save_data = {
            'version': '1.0',
            'timestamp': '2024-01-01T00:00:00',
            'game_state': {
                'time': {'day': 'not_a_number', 'hour': 6}
            }
        }
        is_valid, warnings = manager._validate_save_schema(save_data)
        assert any('day' in w and 'numeric' in w for w in warnings)


class TestSaveGame:
    """Tests for save game functionality."""

    @patch('os.makedirs')
    @patch('tempfile.mkstemp')
    @patch('os.fdopen')
    @patch('os.fsync')
    @patch('shutil.move')
    def test_save_game_creates_file(self, mock_move, mock_fsync, mock_fdopen, mock_mkstemp, mock_makedirs):
        """Test that save_game creates a save file."""
        manager = SaveManager()
        mock_mkstemp.return_value = (5, '/tmp/test.json.tmp')
        mock_file = MagicMock()
        mock_file.fileno.return_value = 5
        mock_fdopen.return_value.__enter__ = MagicMock(return_value=mock_file)
        mock_fdopen.return_value.__exit__ = MagicMock(return_value=False)

        game_state = {'time': {'day': 1}}
        result = manager.save_game(game_state, "test_save")

        assert result is True

    def test_save_game_rejects_invalid_name(self):
        """Test that save_game rejects invalid save names."""
        manager = SaveManager()
        game_state = {'time': {'day': 1}}

        result = manager.save_game(game_state, "../invalid")
        assert result is False

    @patch('os.makedirs')
    @patch('tempfile.mkstemp')
    @patch('os.fdopen')
    @patch('os.fsync')
    @patch('shutil.move')
    def test_save_game_updates_current_save_name(self, mock_move, mock_fsync, mock_fdopen, mock_mkstemp, mock_makedirs):
        """Test that save_game updates current_save_name."""
        manager = SaveManager()
        mock_mkstemp.return_value = (5, '/tmp/test.json.tmp')
        mock_file = MagicMock()
        mock_file.fileno.return_value = 5
        mock_fdopen.return_value.__enter__ = MagicMock(return_value=mock_file)
        mock_fdopen.return_value.__exit__ = MagicMock(return_value=False)

        game_state = {'time': {'day': 1}}
        manager.save_game(game_state, "my_save")

        assert manager.current_save_name == "my_save"


class TestLoadGame:
    """Tests for load game functionality."""

    def test_load_game_rejects_invalid_name(self):
        """Test that load_game rejects invalid save names."""
        manager = SaveManager()
        result = manager.load_game("../invalid")
        assert result is None

    @patch('os.path.exists')
    def test_load_game_returns_none_for_missing_file(self, mock_exists):
        """Test that load_game returns None for non-existent file."""
        mock_exists.return_value = False
        manager = SaveManager()

        result = manager.load_game("nonexistent")
        assert result is None

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_game_parses_valid_json(self, mock_file, mock_exists):
        """Test that load_game parses valid JSON."""
        mock_exists.return_value = True
        save_data = {
            'version': '1.0',
            'timestamp': '2024-01-01T00:00:00',
            'game_state': {'time': {'day': 5, 'hour': 12}}
        }
        mock_file.return_value.read.return_value = json.dumps(save_data)

        manager = SaveManager()

        with patch('json.load', return_value=save_data):
            result = manager.load_game("valid_save")

        assert result is not None
        assert result['time']['day'] == 5

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_game_returns_none_for_invalid_json(self, mock_file, mock_exists):
        """Test that load_game returns None for invalid JSON."""
        mock_exists.return_value = True

        manager = SaveManager()

        with patch('json.load', side_effect=json.JSONDecodeError('', '', 0)):
            result = manager.load_game("invalid_json")

        assert result is None


class TestQuickSaveLoad:
    """Tests for quick save and load functionality."""

    @patch.object(SaveManager, 'save_game')
    def test_quick_save_uses_quicksave_name(self, mock_save):
        """Test that quick_save uses QUICK_SAVE_NAME."""
        mock_save.return_value = True
        manager = SaveManager()
        game_state = {'time': {'day': 1}}

        manager.quick_save(game_state)

        mock_save.assert_called_once_with(game_state, SaveManager.QUICK_SAVE_NAME)

    @patch.object(SaveManager, 'load_game')
    def test_quick_load_uses_quicksave_name(self, mock_load):
        """Test that quick_load uses QUICK_SAVE_NAME."""
        mock_load.return_value = {'time': {'day': 1}}
        manager = SaveManager()

        manager.quick_load()

        mock_load.assert_called_once_with(SaveManager.QUICK_SAVE_NAME)


class TestAutoSave:
    """Tests for auto-save functionality."""

    @patch.object(SaveManager, 'save_game')
    def test_auto_save_triggers_after_interval(self, mock_save):
        """Test that auto_save triggers after interval days."""
        mock_save.return_value = True
        manager = SaveManager()
        manager.last_auto_save_day = 0
        manager.auto_save_interval_days = 5

        game_state = {'time': {'day': 5}}
        result = manager.auto_save(game_state, current_day=5)

        assert result is True
        mock_save.assert_called_once()

    @patch.object(SaveManager, 'save_game')
    def test_auto_save_does_not_trigger_before_interval(self, mock_save):
        """Test that auto_save does not trigger before interval."""
        manager = SaveManager()
        manager.last_auto_save_day = 0
        manager.auto_save_interval_days = 5

        game_state = {'time': {'day': 3}}
        result = manager.auto_save(game_state, current_day=3)

        assert result is False
        mock_save.assert_not_called()

    def test_auto_save_disabled_returns_false(self):
        """Test that auto_save returns False when disabled."""
        manager = SaveManager()
        manager.auto_save_enabled = False

        game_state = {'time': {'day': 10}}
        result = manager.auto_save(game_state, current_day=10)

        assert result is False

    @patch.object(SaveManager, 'save_game')
    def test_auto_save_updates_last_save_day(self, mock_save):
        """Test that auto_save updates last_auto_save_day on success."""
        mock_save.return_value = True
        manager = SaveManager()
        manager.last_auto_save_day = 0
        manager.auto_save_interval_days = 5

        manager.auto_save({'time': {}}, current_day=10)

        assert manager.last_auto_save_day == 10


class TestDeleteSave:
    """Tests for delete save functionality."""

    def test_delete_save_rejects_invalid_name(self):
        """Test that delete_save rejects invalid save names."""
        manager = SaveManager()
        result = manager.delete_save("../invalid")
        assert result is False

    @patch('os.path.exists')
    @patch('os.remove')
    def test_delete_save_removes_existing_file(self, mock_remove, mock_exists):
        """Test that delete_save removes existing file."""
        mock_exists.return_value = True
        manager = SaveManager()

        result = manager.delete_save("valid_save")

        assert result is True
        mock_remove.assert_called_once()

    @patch('os.path.exists')
    def test_delete_save_returns_false_for_missing_file(self, mock_exists):
        """Test that delete_save returns False for missing file."""
        mock_exists.return_value = False
        manager = SaveManager()

        result = manager.delete_save("nonexistent")

        assert result is False


class TestGetSaveList:
    """Tests for get_save_list functionality."""

    @patch('os.path.exists')
    def test_get_save_list_returns_empty_for_missing_directory(self, mock_exists):
        """Test that get_save_list returns empty list when directory missing."""
        mock_exists.return_value = False
        manager = SaveManager()

        result = manager.get_save_list()

        assert result == []

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_save_list_returns_save_info(self, mock_file, mock_listdir, mock_exists):
        """Test that get_save_list returns save file information."""
        mock_exists.return_value = True
        mock_listdir.return_value = ['save1.json', 'save2.json']

        save_data = {
            'version': '1.0',
            'timestamp': '2024-01-01T00:00:00',
            'game_state': {'time': {'day': 1}, 'resources': {'money': 5000}}
        }

        manager = SaveManager()

        with patch('json.load', return_value=save_data):
            result = manager.get_save_list()

        assert len(result) == 2


class TestSafeTypeConversions:
    """Tests for safe type conversion helper methods."""

    def test_safe_int_with_valid_int(self):
        """Test _safe_int with valid integer."""
        assert SaveManager._safe_int(42, 0) == 42

    def test_safe_int_with_valid_float(self):
        """Test _safe_int with valid float."""
        assert SaveManager._safe_int(42.7, 0) == 42

    def test_safe_int_with_none(self):
        """Test _safe_int with None returns default."""
        assert SaveManager._safe_int(None, 99) == 99

    def test_safe_int_with_invalid_string(self):
        """Test _safe_int with invalid string returns default."""
        assert SaveManager._safe_int("not_a_number", 99) == 99

    def test_safe_float_with_valid_float(self):
        """Test _safe_float with valid float."""
        assert SaveManager._safe_float(3.14, 0.0) == 3.14

    def test_safe_float_with_none(self):
        """Test _safe_float with None returns default."""
        assert SaveManager._safe_float(None, 1.5) == 1.5

    def test_safe_bool_with_true(self):
        """Test _safe_bool with True."""
        assert SaveManager._safe_bool(True, False) is True

    def test_safe_bool_with_string_true(self):
        """Test _safe_bool with string 'true'."""
        assert SaveManager._safe_bool("true", False) is True

    def test_safe_bool_with_none(self):
        """Test _safe_bool with None returns default."""
        assert SaveManager._safe_bool(None, True) is True

    def test_safe_dict_with_valid_dict(self):
        """Test _safe_dict with valid dictionary."""
        d = {'a': 1, 'b': 2}
        result = SaveManager._safe_dict(d)
        assert result == d

    def test_safe_dict_with_none(self):
        """Test _safe_dict with None returns empty dict."""
        result = SaveManager._safe_dict(None)
        assert result == {}

    def test_safe_list_with_valid_list(self):
        """Test _safe_list with valid list."""
        lst = [1, 2, 3]
        result = SaveManager._safe_list(lst)
        assert result == lst

    def test_safe_list_with_none(self):
        """Test _safe_list with None returns empty list."""
        result = SaveManager._safe_list(None)
        assert result == []
