import pytest
import tempfile
import os
from pathlib import Path
from main import validate_path


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

