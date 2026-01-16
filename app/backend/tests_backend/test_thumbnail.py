import pytest
from input_validation import validate_thumbnail_path

#Note: Test for the general path existience validation is checked by test_validate_path.py
#Note: Test for analysis path is also handled by test_validate_path.py module.

def test_validate_format():
    """Check if wrong format raises error"""
    with pytest.raises(TypeError):
        validate_thumbnail_path("tests_backend/test_main_dir/test_images/img.dng")

def test_validate_path_type():
    """Check if invalid path type raises error (dir or not a file)"""
    with pytest.raises(IsADirectoryError):
        validate_thumbnail_path("tests_backend/test_main_dir")

def test_validate_size():
    with pytest.raises(ValueError):
        validate_thumbnail_path("tests_backend/test_main_dir/test_images/large_image.jpg")

def comprehensive_test():
   assert validate_thumbnail_path("/tests_backend/test_main_dir/test_images/flower.jpeg")