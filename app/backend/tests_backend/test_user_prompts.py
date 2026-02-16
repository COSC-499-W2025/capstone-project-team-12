"""
Unit tests for ConfigManager and user prompt default behaviors.
Tests persistent preferences, consent workflows, and prompt defaults.
"""

import pytest
from config_manager import ConfigManager


class TestConfigManagerBasics:
    """Test basic ConfigManager functionality"""
    
    @pytest.fixture
    def temp_config(self, tmp_path):
        return ConfigManager(config_dir=str(tmp_path / "test_configs"), config_file="test_prefs.json")
    
    def test_persistence_and_corrupted_json(self, temp_config, tmp_path):
        """Preferences persist across instances and handle corrupted JSON"""
        # Test persistence
        temp_config.save_prefs({"test_key": True})
        new_config = ConfigManager(config_dir=str(temp_config.config_dir), config_file="test_prefs.json")
        assert new_config.preferences == {"test_key": True}
        
        # Test corrupted JSON handling
        config_dir = tmp_path / "corrupted"
        config_dir.mkdir()
        with open(config_dir / "user_prefs.json", 'w') as f:
            f.write("{invalid")
        assert ConfigManager(config_dir=str(config_dir)).preferences == {}


class TestGetConsentFirstTime:
    """Test get_consent() on first use (no previous preference)"""
    
    @pytest.fixture
    def temp_config(self, tmp_path):
        return ConfigManager(config_dir=str(tmp_path / "test_configs"), config_file="test_prefs.json")
    
    @pytest.mark.parametrize("user_input,default,expected", [
        ("", True, True),      # Empty → default YES
        ("", False, False),    # Empty → default NO
        ("y", False, True),    # Explicit y overrides default NO
        ("n", True, False),    # Explicit n overrides default YES
    ])
    def test_first_time_inputs(self, temp_config, monkeypatch, user_input, default, expected):
        """Test empty and explicit inputs with different defaults"""
        monkeypatch.setattr('builtins.input', lambda _: user_input)
        result = temp_config.get_consent(key="test", prompt_text="Test?", default=default)
        assert result is expected
    
    def test_invalid_retry(self, temp_config, monkeypatch):
        """Invalid input prompts retry until valid"""
        inputs = iter(["invalid", "y"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        assert temp_config.get_consent(key="test", prompt_text="Test?", default=True) is True


class TestGetConsentWithHistory:
    """Test get_consent() when user has previous preference"""
    
    @pytest.fixture
    def temp_config(self, tmp_path):
        return ConfigManager(config_dir=str(tmp_path / "test_configs"), config_file="test_prefs.json")
    
    @pytest.mark.parametrize("previous,user_input,default,expected,saved", [
        # Previously granted
        (True, "", True, True, None),      # Empty + default=True → keeps
        (True, "", False, False, False),   # CRITICAL: Empty + default=False → revokes
        (True, "n", True, False, False),   # Explicit n → revokes
        (True, "invalid", True, True, None), # Invalid → keeps previous
        
        # Previously denied
        (False, "", True, True, True),     # CRITICAL: Empty + default=True → grants
        (False, "", False, False, None),   # Empty + default=False → keeps denial
        (False, "y", False, True, True),   # Explicit y → grants
    ])
    def test_consent_with_history(self, temp_config, monkeypatch, previous, user_input, default, expected, saved):
        """Test all scenarios with previous consent history"""
        temp_config.save_prefs({"test": previous})
        monkeypatch.setattr('builtins.input', lambda _: user_input)
        result = temp_config.get_consent(key="test", prompt_text="Test?", component="test", default=default)
        assert result is expected
        if saved is not None:
            assert temp_config.preferences["test"] is saved


class TestEdgeCases:
    """Test edge cases and input variations"""
    
    @pytest.fixture
    def temp_config(self, tmp_path):
        return ConfigManager(config_dir=str(tmp_path / "test_configs"), config_file="test_prefs.json")
    
    @pytest.mark.parametrize("user_input,expected", [
        ("YES", True),    # Case insensitive
        ("  y  ", True),  # Whitespace trimmed
        ("no", False),    # Full word accepted
    ])
    def test_input_variations(self, temp_config, monkeypatch, user_input, expected):
        """Input is case-insensitive and whitespace-trimmed"""
        monkeypatch.setattr('builtins.input', lambda _: user_input)
        result = temp_config.get_consent(key="test", prompt_text="Test?", default=False)
        assert result is expected
    
    def test_multiple_keys_independent(self, temp_config, monkeypatch):
        """Different keys maintain independent states"""
        monkeypatch.setattr('builtins.input', lambda _: "y")
        temp_config.get_consent(key="f1", prompt_text="F1?", default=False)
        monkeypatch.setattr('builtins.input', lambda _: "n")
        temp_config.get_consent(key="f2", prompt_text="F2?", default=True)
        assert temp_config.preferences == {"f1": True, "f2": False}


class TestMainPromptLogic:
    """Test prompt logic patterns used in main.py and analysis_pipeline.py"""
    
    @pytest.mark.parametrize("response,expected_proceed", [
        ("", True),    # Empty → proceed (default YES)
        ("n", False),  # Explicit n → skip
        ("no", False), # Explicit no → skip
    ])
    def test_not_in_no_pattern(self, response, expected_proceed):
        """Test 'not in (n, no)' pattern for thumbnail/edit/delete prompts"""
        assert (response.lower() not in ('n', 'no')) is expected_proceed
    
    @pytest.mark.parametrize("username,expected_skip", [
        ("", True),          # Empty → skip
        ("   ", True),       # Whitespace → skip
        ("user", False),     # Valid → proceed
    ])
    def test_github_username_pattern(self, username, expected_skip):
        """Test GitHub username empty check pattern"""
        assert (not username.strip()) is expected_skip