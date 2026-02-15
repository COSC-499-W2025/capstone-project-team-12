import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from main_utils import compare_path

# We define the root path string
TEST_ROOT = Path("/app/repos/test_scenarios/path_comparison")

class TestPathComparison:

    def test_detect_different_parent_directory(self):
        """Test detecting when a project is moved from loc_1 to loc_2."""
        #define paths
        old_path = str(TEST_ROOT / "loc_1" / "MyProject")
        new_path = str(TEST_ROOT / "loc_2" / "MyProject")
        
        # Mock CLI to auto-reject ('n') the warning so compare_path returns False
        with patch("main_utils.CLI") as MockCLI:
            MockCLI.return_value.get_input.return_value = 'n'
            
            result = compare_path(old_path, new_path)
            
            assert result is False
            #Verify the warning triggered a prompt
            MockCLI.return_value.get_input.assert_called_once()

    def test_detect_different_folder_name(self):
        """Test detecting when MyProject is renamed to MyProject_v2 in the same folder."""
        old_path = str(TEST_ROOT / "loc_1" / "MyProject")
        new_path = str(TEST_ROOT / "loc_1" / "MyProject_v2") #Name change
        
        with patch("main_utils.CLI") as MockCLI:
            MockCLI.return_value.get_input.return_value = 'n'
            
            result = compare_path(old_path, new_path)
            
            assert result is False

    def test_detect_different_drive_anchor(self):
        """
        Simulates C: vs D: drives. 
        Since we are in Linux (/app/repos), we MUST mock the Path object logic 
        because we cannot physically create a D: drive.
        """
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