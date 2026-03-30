import os
from pathlib import Path
from file_manager import FileManager
import time

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
    #UPDATE: with deduplication logic we now only have 6 unique files
    assert len(fm.binary_data_array) == 6


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

def test_file_manager_deduplication(tmp_path):
    fm = FileManager()
    
    # Create two different files with identical content
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    content = b"identical content"
    file1.write_bytes(content)
    file2.write_bytes(content)
    
    #load from the directory containing both
    result = fm.load_from_filepath(str(tmp_path))
    
    assert result['status'] == 'success'
    
    #check that we have exactly one unique entry in the binary data array
    assert len(fm.get_binary_array()) == 1
    assert fm.get_binary_array()[0] == content
    
    #verify that both files point to the same binary index
    file_nodes = [node for node in fm.file_tree.descendants if node.type == "file"]
    assert len(file_nodes) == 2
    
    idx1 = file_nodes[0].file_data['binary_index']
    idx2 = file_nodes[1].file_data['binary_index']
    
    assert idx1 == 0
    assert idx2 == 0

def test_deduplication_zero_byte_files(tmp_path):
    """
    Test that the FileManager correctly deduplicates multiple 
    zero-byte (empty) files into a single binary entry.
    """
    fm = FileManager()
    
    #create multiple empty files
    file1 = tmp_path / "empty1.txt"
    file2 = tmp_path / "empty2.log"
    file1.touch()
    file2.touch()
    
    result = fm.load_from_filepath(str(tmp_path))
    
    assert result['status'] == 'success'
    
    #verify that the system combined the empty content to a single binary entry
    # (The hash of an empty string is consistent)
    assert len(fm.get_binary_array()) == 1
    assert fm.get_binary_array()[0] == b""
    
    #verify both files are represented in the tree
    nodes = [n for n in fm.file_tree.descendants if n.type == "file"]
    assert len(nodes) == 2
    
    #both should point to the same binary index
    assert nodes[0].file_data['binary_index'] == nodes[1].file_data['binary_index']


def test_deduplication_different_metadata(tmp_path):
    """
    Files with same content but different metadata should
    be relfected in file tree accordingly
    """
    fm = FileManager()
    
    #create two files with same content
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    content = b"content"
    file1.write_bytes(content)
    file2.write_bytes(content)
    
    #change metadata (timestamps)
    os.utime(file2, (time.time() - 1000, time.time() - 1000))
    
    fm.load_from_filepath(str(tmp_path))
    
    #content should be deduplicated
    assert len(fm.get_binary_array()) == 1
    
    #both nodes should still exist with different last_modified timestamps
    nodes = [n for n in fm.file_tree.descendants if n.type == "file"]
    assert nodes[0].file_data['last_modified'] != nodes[1].file_data['last_modified']

def test_file_hash_in_metadata(tmp_path):
    """
    Test that a generated hash string is successfully assigned to 
    the file's metadata dictionary inside the tree.
    """
    fm = FileManager()
    file1 = tmp_path / "file1.txt"
    file1.write_bytes(b"hash test content")
    
    result = fm.load_from_filepath(str(tmp_path))
    assert result['status'] == 'success'
    
    file_nodes = [n for n in fm.file_tree.descendants if n.type == "file"]
    assert 'file_hash' in file_nodes[0].file_data
    assert isinstance(file_nodes[0].file_data['file_hash'], str)


def test_cross_session_deduplication(tmp_path):
    """
    Test that a newly initialized FileManager correctly deduplicates
    content when provided with state from a previous session.
    """
    # 1. Simulate the first session processing files
    fm1 = FileManager()
    file1 = tmp_path / "file1.txt"
    content = b"persistent content"
    file1.write_bytes(content)
    
    fm1.load_from_filepath(str(tmp_path))
    prev_binary = fm1.get_binary_array()
    prev_hashes = fm1.seen_hashes
    original_hash = fm1.file_objects[0]['file_hash']
    
    # 2. Simulate the second (editing) session
    fm2 = FileManager()
    # Pre-load the state 
    fm2.set_previous_state(prev_binary, prev_hashes)
    
    # Load the same file again, ensuring we pass reset_state=False
    # so we don't wipe out the state we just set
    fm2.load_from_filepath(str(tmp_path), reset_state=False)
    
    # 3. Verify that it correctly recognized the old file data 
    # instead of creating a duplicate binary entry
    assert len(fm2.get_binary_array()) == 1
    assert fm2.file_objects[0]['binary_index'] == 0
    assert fm2.file_objects[0]['file_hash'] == original_hash