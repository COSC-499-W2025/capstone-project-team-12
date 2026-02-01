import os
from pathlib import Path
from file_manager import FileManager

# Defining directory paths
BASE_DIR = Path(__file__).parent
TEST_FILES_DIR = BASE_DIR / "test_main_dir"


def test_load_single_file():
    # Test that a single valid file can be loaded successfully
    file_path = TEST_FILES_DIR / "pii_text.txt"
    fm = FileManager()
    result = fm.load_from_filepath(str(file_path))
    
    # Expect success and a valid file tree
    assert result["status"] == "success"
    assert "tree" in result
    assert result["tree"].name == file_path.name


def test_load_directory():
    # Test that an entire directory can be loaded properly
    fm = FileManager()
    result = fm.load_from_filepath(str(TEST_FILES_DIR))
    
    # Expect success and the directory name to match
    assert result["status"] == "success"
    tree = result["tree"]
    assert tree.name == TEST_FILES_DIR.name

    # Verify that a known file exists inside the directory
    assert any("pii_text.txt" in child.name for child in tree.children)


def test_invalid_path():
    # Ensure invalid or non-existent paths return an error
    fm = FileManager()
    result = fm.load_from_filepath("/path/does/not/exist.txt")

    # Expect an error result
    assert result["status"] == "error"


def test_large_file_is_rejected(mocker):
    # Test that a file larger than max_size_bytes is rejected
    fm = FileManager()
    fake_path = Path("/fake/large.txt")

    # Mock large file and all other calls
    mocker.patch.object(Path, "exists", return_value=True)
    mocker.patch.object(Path, "is_file", return_value=True)
    mocker.patch.object(Path, "stat", return_value=mocker.Mock(st_size=fm.max_size_bytes + 1))
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"fake data"))

    # Load the fake file and check the result
    result = fm.load_from_filepath(fake_path)
    assert result["status"] == "error"
    assert "No valid files" in result["message"]


def test_git_repo_recognition():
    # Test that .git directories or files inside a repo are correctly recognized
    repo_path = Path("/app/repos")
    fm = FileManager()
    result = fm.load_from_filepath(repo_path)

    # Ensure the repo loads successfully
    assert result["status"] == "success", f"Load failed: {result.get('message')}"

    # Find any nodes that contain '.git' in their name
    git_nodes = [n for n in fm.file_tree.descendants if ".git" in n.name]

    # Expect at least one .git folder or file to be detected
    assert len(git_nodes) >= 1, "Expected at least one .git node in the repo tree"


def test_rar_files():
    # Test that unsupported archive types like .rar return an error
    file_path = TEST_FILES_DIR / "group12_project_proposal.rar"
    fm = FileManager()
    result = fm.load_from_filepath(file_path)

    # Expect an error result
    assert result["status"] == "error"


def test_folder_with_empty_file():
    # Ensure that empty files are still included correctly in the results
    folder_path = TEST_FILES_DIR / "mock_files"
    fm = FileManager()
    result = fm.load_from_filepath(folder_path)

    print("DEBUG:", result)  

    # Folder should load successfully
    assert result["status"] == "success"

    # Verify total number of loaded files and binary entries
    assert len(fm.file_objects) == 4
    assert len(fm.binary_data_array) == 4

    # Find the empty file in file_objects
    empty_file_obj = next((f for f in fm.file_objects if f["filename"] == "empty_file.txt"), None)
    assert empty_file_obj is not None

    # Check that its size is 0 and binary data is an empty byte string
    assert empty_file_obj["size_bytes"] == 0
    assert fm.binary_data_array[empty_file_obj["binary_index"]] == b""

    # Confirm that the tree structure includes all 4 files
    file_nodes = [n for n in fm.file_tree.descendants if n.type == "file"]
    assert len(file_nodes) == 4


def test_nested_zip():
    # Test extraction of nested zip archives (zip files inside another zip)
    zip_path = TEST_FILES_DIR / "test_with_nested.zip"
    fm = FileManager()
    result = fm.load_from_filepath(zip_path)

    # Expect success and the correct total number of extracted files
    assert result["status"] == "success"
    assert len(fm.file_objects) == 9
    assert len(fm.binary_data_array) == 9


def test_get_binary_array():
    # Test that get_binary_array() correctly returns the binary data array
    fm = FileManager()
    folder_path = TEST_FILES_DIR / "mock_files"
    result = fm.load_from_filepath(folder_path)

    # Should successfully load the folder
    assert result["status"] == "success"

    # Retrieve the binary array directly via the getter
    binary_array = fm.get_binary_array()

    # It should match the internal array reference
    assert binary_array == fm.binary_data_array
    assert len(binary_array) == len(fm.file_objects)

    # For each file, verify that its binary index maps to valid bytes
    for fobj in fm.file_objects:
        idx = fobj["binary_index"]
        # Make sure the entry exists and is byte data
        assert binary_array[idx] is not None
        assert isinstance(binary_array[idx], (bytes, bytearray))

def test_tree_metadata_timestamps():
    #test that tree nodes have created_at and last_modified timestamps
    file_path = TEST_FILES_DIR / "pii_text.txt"
    fm = FileManager()
    result = fm.load_from_filepath(str(file_path))

    assert result["status"] == "success"
    tree = result["tree"]

    # Check root node created_at
    assert hasattr(tree, "created_at")
    assert isinstance(tree.created_at, str)

    #Check file node last_modified
    file_node = tree.children[0]
    assert hasattr(file_node, "last_modified")
    assert isinstance(file_node.last_modified, str)
