"""
Unit tests for ConfigManager class.

Tests persistent preferences, consent workflows, and file I/O.
"""

import pytest
import json
import tempfile
from pathlib import Path
from config_manager import ConfigManager


class TestConfigManagerBasics:
    """Test basic ConfigManager functionality"""
    
    @pytest.fixture
    def temp_config(self, tmp_path):
        """Create a ConfigManager with temporary config directory"""
        config_dir = tmp_path / "test_configs"
        return ConfigManager(config_dir=str(config_dir), config_file="test_prefs.json")
    
    def test_init_creates_empty_prefs(self, temp_config):
        """ConfigManager starts with empty preferences when no file exists"""
        assert temp_config.preferences == {}
    
    def test_save_and_load_prefs(self, temp_config):
        """Preferences persist across ConfigManager instances"""
        # Save some preferences
        temp_config.save_prefs({"test_key": True, "another_key": "value"})
        
        # Create new instance pointing to same file
        new_config = ConfigManager(
            config_dir=str(temp_config.config_dir),
            config_file="test_prefs.json"
        )
        
        # Should load saved preferences
        assert new_config.preferences == {"test_key": True, "another_key": "value"}
    
    def test_save_prefs_creates_directory(self, tmp_path):
        """save_prefs creates config directory if it doesn't exist"""
        nonexistent_dir = tmp_path / "new_dir" / "nested"
        config = ConfigManager(config_dir=str(nonexistent_dir))
        
        config.save_prefs({"key": "value"})
        
        assert nonexistent_dir.exists()
        assert (nonexistent_dir / "user_prefs.json").exists()


class TestGetConsentDefaults:
    """Test get_consent() with default parameter"""
    
    @pytest.fixture
    def temp_config(self, tmp_path):
        config_dir = tmp_path / "test_configs"
        return ConfigManager(config_dir=str(config_dir), config_file="test_prefs.json")
    
    def test_first_time_empty_input_defaults_yes(self, temp_config, monkeypatch):
        """Empty input on first run defaults to YES when default=True"""
        monkeypatch.setattr('builtins.input', lambda _: "")
        
        result = temp_config.get_consent(
            key="test_consent",
            prompt_text="Test prompt?",
            default=True
        )
        
        assert result is True
        assert temp_config.preferences["test_consent"] is True
    
    def test_first_time_empty_input_defaults_no(self, temp_config, monkeypatch):
        """Empty input on first run defaults to NO when default=False"""
        monkeypatch.setattr('builtins.input', lambda _: "")
        
        result = temp_config.get_consent(
            key="test_consent",
            prompt_text="Test prompt?",
            default=False
        )
        
        assert result is False
        assert temp_config.preferences["test_consent"] is False
    
    def test_first_time_explicit_yes(self, temp_config, monkeypatch):
        """Explicit 'y' grants consent regardless of default"""
        monkeypatch.setattr('builtins.input', lambda _: "y")
        
        result = temp_config.get_consent(
            key="test_consent",
            prompt_text="Test prompt?",
            default=False  # Default is NO, but user says YES
        )
        
        assert result is True
        assert temp_config.preferences["test_consent"] is True
    
    def test_first_time_explicit_no(self, temp_config, monkeypatch):
        """Explicit 'n' denies consent regardless of default"""
        monkeypatch.setattr('builtins.input', lambda _: "n")
        
        result = temp_config.get_consent(
            key="test_consent",
            prompt_text="Test prompt?",
            default=True  # Default is YES, but user says NO
        )
        
        assert result is False
        assert temp_config.preferences["test_consent"] is False
    
    def test_previous_consent_empty_defaults_yes(self, temp_config, monkeypatch):
        """Empty input with previous consent defaults to YES when default=True"""
        temp_config.save_prefs({"test_consent": True})
        monkeypatch.setattr('builtins.input', lambda _: "")
        
        result = temp_config.get_consent(
            key="test_consent",
            prompt_text="Test?",
            default=True
        )
        
        assert result is True
    
    def test_previous_consent_empty_defaults_no_revokes(self, temp_config, monkeypatch):
        """Empty input with previous consent defaults to NO when default=False (REVOKES!)"""
        temp_config.save_prefs({"test_consent": True})
        monkeypatch.setattr('builtins.input', lambda _: "")
        
        result = temp_config.get_consent(
            key="test_consent",
            prompt_text="Test?",
            default=False  # Default is NO - should revoke!
        )
        
        assert result is False
        assert temp_config.preferences["test_consent"] is False  # Saved as revoked
    
    def test_previous_denial_empty_defaults_yes_grants(self, temp_config, monkeypatch):
        """Empty input with previous denial defaults to YES when default=True (GRANTS!)"""
        temp_config.save_prefs({"test_consent": False})
        monkeypatch.setattr('builtins.input', lambda _: "")
        
        result = temp_config.get_consent(
            key="test_consent",
            prompt_text="Test?",
            default=True  # Default is YES - should grant!
        )
        
        assert result is True
        assert temp_config.preferences["test_consent"] is True  # Saved as granted
    
    def test_previous_denial_empty_defaults_no(self, temp_config, monkeypatch):
        """Empty input with previous denial defaults to NO when default=False"""
        temp_config.save_prefs({"test_consent": False})
        monkeypatch.setattr('builtins.input', lambda _: "")
        
        result = temp_config.get_consent(
            key="test_consent",
            prompt_text="Test?",
            default=False
        )
        
        assert result is False
    
    def test_invalid_input_retry(self, temp_config, monkeypatch):
        """Invalid input prompts user again until valid input"""
        inputs = iter(["invalid", "maybe", "y"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        result = temp_config.get_consent(
            key="test_consent",
            prompt_text="Test?",
            default=True
        )
        
        assert result is True