import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from main_utils import compare_path

# Root path for string comparison (does not need to exist physically)
TEST_ROOT = Path("/app/repos/test_scenarios/path_comparison")

class TestPathComparison:

    def test_detect_different_parent_directory(self):
        """Test detecting when a project is moved from loc_1 to loc_2."""
        old_path = str(TEST_ROOT / "loc_1" / "MyProject")
        new_path = str(TEST_ROOT / "loc_2" / "MyProject")
        
        with patch("main_utils.CLI") as MockCLI:
            MockCLI.return_value.get_input.return_value = 'n'
            
            result = compare_path(old_path, new_path)
            
            assert result is False
            MockCLI.return_value.get_input.assert_called_once()

    def test_detect_different_drive_anchor(self):
        """Simulates C: vs D: drives (Windows behavior mocked on Linux)."""
        old_path_str = "C:/app/repos/MyProject"
        new_path_str = "D:/app/repos/MyProject"

        with patch("main_utils.Path") as MockPath:
            mock_old = MagicMock()
            mock_new = MagicMock()

            # Mock behavior to simulate Windows paths
            mock_old.resolve.return_value = mock_old
            mock_old.anchor = "C:\\"
            mock_old.parent = "C:\\app\\repos"
            mock_old.name = "MyProject"

            mock_new.resolve.return_value = mock_new
            mock_new.anchor = "D:\\"
            mock_new.parent = "D:\\app\\repos"
            mock_new.name = "MyProject"

            MockPath.side_effect = [mock_old, mock_new]

            with patch("main_utils.CLI") as MockCLI:
                MockCLI.return_value.get_input.return_value = 'n'
                
                result = compare_path(old_path_str, new_path_str)
                
                assert result is False

    def test_similar_paths_pass(self):
        """Happy path: The path is exactly the same."""
        path = str(TEST_ROOT / "loc_1" / "MyProject")
        
        with patch("main_utils.CLI") as MockCLI:
            result = compare_path(path, path)
            
            assert result is True
            MockCLI.return_value.get_input.assert_not_called()

    def test_detect_version_update_passes(self):
        """
        Test that 'MyProject' -> 'MyProject_v2' is considered similar enough (High Similarity)
        and DOES NOT trigger a warning prompt.
        """
        old_path = "/app/repos/MyProject"
        new_path = "/app/repos/MyProject_v2" # High similarity

        with patch("main_utils.CLI") as MockCLI:
            result = compare_path(old_path, new_path)
            
            assert result is True
            MockCLI.return_value.get_input.assert_not_called()

    def test_detect_substring_rename_passes(self):
        """
        Test that 'MyProject' -> 'MyProject_Backup_Archive' passes.
        This tests the specific 'is_substring' logic in main_utils.py.
        Even if similarity ratio is low due to length difference, it should pass if one is a substring of the other.
        """
        old_path = str(TEST_ROOT / "loc_1" / "MyProject")
        new_path = str(TEST_ROOT / "loc_1" / "MyProject_Backup_Archive_2025")
        
        with patch("main_utils.CLI") as MockCLI:
            result = compare_path(old_path, new_path)
            
            assert result is True
            MockCLI.return_value.get_input.assert_not_called()

    def test_detect_completely_different_name_fails(self):
        """
        Test that 'MyProject' -> 'Photos' is considered different
        and DOES trigger a warning prompt.
        """
        old_path = "/app/repos/MyProject"
        new_path = "/app/repos/Photos" # Low similarity, not a substring

        with patch("main_utils.CLI") as MockCLI:
            MockCLI.return_value.get_input.return_value = 'n'
            
            result = compare_path(old_path, new_path)
            
            assert result is False
            MockCLI.return_value.get_input.assert_called_once()