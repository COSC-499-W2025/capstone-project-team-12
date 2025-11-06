import pytest
import tempfile
import os
from pathlib import Path
from main import validate_path
from unittest.mock import patch, MagicMock, mock_open


# test if basic text file is validated
def test_valid_file(tmp_path):
    file = tmp_path / "testfile.txt"
    file.write_text("hello world")
    result = validate_path(str(file))
    assert result == file.resolve()


# file not found is raised if file non existent
def test_invalid_path_raises_filenotfound():
    with pytest.raises(FileNotFoundError):
        validate_path("non_existent_file.txt")


# RAR file rejected
def test_rar_file_raises_valueerror(tmp_path):
    rar_file = tmp_path / "archive.rar"
    rar_file.write_text("dummy data")
    with pytest.raises(ValueError, match="RAR files are not supported"):
        validate_path(str(rar_file))



def test_file_too_large(tmp_path):
    large_file = tmp_path / "bigfile.bin"
    large_file.touch()

    # Path.stat() (from validate_path) normally returns an os.stat_result object so we Create a fake stat object that mimics os.stat_result with a large st_size
    class FakeStat:
        st_size = 5 * 1024 * 1024 * 1024  # 5gb, too large for our file validation
        st_mode = 0o100644  # other object attributes
        st_mtime = st_ctime = st_atime = 0

    # replace Path.stat() return value just for this test
    real_stat = Path.stat
    try:
        Path.stat = lambda self, **kwargs: FakeStat()
        with pytest.raises(ValueError, match="File too large"):
            validate_path(str(large_file))
    finally:
        Path.stat = real_stat  # restore original Path.stat() return value afterwards



def test_directory_too_large(tmp_path):
    # the fake directory has these files, and each file is 5gb
    dir_path = tmp_path / "bigdir"
    dir_path.mkdir()
    big_file = dir_path / "file1.bin"
    big_file.touch()

    # Create a fake os.stat_result object again
    class FakeStat:
        st_size = 5 * 1024 * 1024 * 1024 
        st_mode = 0o100644
        st_mtime = st_ctime = st_atime = 0

    # Save original setting
    real_stat = Path.stat
    real_rglob = Path.rglob

    try:
        # change Path.stat to always return the fake large file size (for now)
        Path.stat = lambda self, **kwargs: FakeStat()

        # change Path.rglob to just return a list with our one fake file (for now)
        Path.rglob = lambda self, pattern: [big_file]

        with pytest.raises(ValueError, match="File too large"):
            validate_path(str(dir_path))
    finally:
        # Restore original setting
        Path.stat = real_stat
        Path.rglob = real_rglob


# test that any quotations used when entering the file path are stripped
def test_strip_quotes(tmp_path):
    file = tmp_path / "quoted.txt"
    file.write_text("sample")
    quoted_path = f"'{file}'"
    double_quoted_path = f'"{file}"'
    
    assert validate_path(quoted_path) == file.resolve()
    assert validate_path(double_quoted_path) == file.resolve()

def test_empty_path():
    """test that empty filepaths raises valueErrors"""
    with pytest.raises(ValueError, match= "Filepath cannot be empty"):
        validate_path("")

    with pytest.raises(ValueError, match= "Filepath cannot be empty"):
        validate_path("                 ")

    with pytest.raises(ValueError, match= "Filepath cannot be empty"):
        validate_path("\t\n")

def test_invalid_path_resolution():
    """Test that path resolution errors are caught and converted to ValueError"""
    with patch('pathlib.Path.expanduser') as mock_expand:
        # create mock path object
        mock_path = MagicMock()
        mock_path.resolve.side_effect = OSError("Invalid path")
        mock_expand.return_value = mock_path

        with pytest.raises(ValueError, match = "Invalid file path"):
            validate_path("/some/path")

def test_file_persmission_error(tmp_path):
    """Test that permission errors are caught and converted"""
    # create a temporary directory 
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    
    # simulate PermissionError
    def mock_rglob(*args):
        raise PermissionError("Cannot access directory")
    
    # patch Path.rglob so that any call to rglob inside validate_path will raise the PermissionError.
    with patch.object(Path, 'rglob', side_effect=mock_rglob):
        with pytest.raises(ValueError, match="Cannot access directory"):
            validate_path(str(test_dir))
