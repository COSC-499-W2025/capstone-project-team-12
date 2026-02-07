import pytest
from anytree import Node
from tree_manager import TreeManager

#Helpers 

def create_file_node(name, parent, binary_index, last_modified, classification=None):
    """Helper to create a file node with standard attributes."""
    n = Node(name, parent=parent, type="file", binary_index=binary_index, last_modified=last_modified)
    if classification:
        n.classification = classification
    n.file_data = {'binary_index': binary_index}
    return n

def create_mock_test_files(scenario_type):
    """Generates mock old/new trees and binary data based on the specified scenario."""
    old_root = Node("root", type="directory")
    new_root = Node("root", type="directory")
    old_binary = []
    new_binary = []

    if scenario_type == "identical":
        #Identical trees: Same name, same timestamp
        create_file_node("file1.txt", old_root, 0, "2023-01-01T12:00:00", classification="confidential")
        old_binary = [b"content1"]
        
        create_file_node("file1.txt", new_root, 0, "2023-01-01T12:00:00")
        new_binary = [b"content1"]

    elif scenario_type == "modified":
        #Modified file: Same name, different timestamp
        create_file_node("file1.txt", old_root, 0, "2023-01-01T12:00:00", classification="old_class")
        old_binary = [b"old_content"]
        
        create_file_node("file1.txt", new_root, 0, "2023-01-02T12:00:00") 
        new_binary = [b"new_content"]

    elif scenario_type == "new":
        #New file: Only exists in new tree
        create_file_node("new_file.txt", new_root, 0, "2023-01-01T12:00:00")
        new_binary = [b"new_data"]

    elif scenario_type == "deleted":
        # Deleted file: Only exists in old tree
        create_file_node("deleted.txt", old_root, 0, "2023-01-01T12:00:00")
        old_binary = [b"gone"]

    elif scenario_type == "mixed":
        # Mixed: A(unchanged), B(modified), C(new)
        # Old Tree
        create_file_node("A.txt", old_root, 0, "T1", classification="keep_me")
        create_file_node("B.txt", old_root, 1, "T1", classification="lose_me")
        old_binary = [b"dataA", b"dataB_old"]
        
        # New Tree
        create_file_node("A.txt", new_root, 0, "T1") 
        create_file_node("B.txt", new_root, 1, "T2") 
        create_file_node("C.txt", new_root, 2, "T1") 
        new_binary = [b"dataA", b"dataB_new", b"dataC"]

    elif scenario_type == "nested":
        # Nested structure
        old_sub = Node("sub", parent=old_root, type="directory")
        create_file_node("file.txt", old_sub, 0, "T1", classification="meta")
        old_binary = [b"data"]
        
        new_sub = Node("sub", parent=new_root, type="directory")
        create_file_node("file.txt", new_sub, 0, "T1")
        new_binary = [b"data"]
        
    else:
        raise ValueError(f"Unknown scenario type: {scenario_type}")

    return old_root, old_binary, new_root, new_binary

@pytest.fixture
def tm():
    return TreeManager()

#  Tests 

def test_initialization(tm):
    assert tm is not None

def test_merge_identical_trees(tm):
    old_root, old_binary, new_root, new_binary = create_mock_test_files("identical")
    
    merged_tree, merged_binary = tm.merge_trees(old_root, old_binary, new_root, new_binary)
    
    #assert data preserved from old binary , metadata preserved
    assert len(merged_binary) == 1
    assert merged_binary[0] == b"content1"
    
    node = new_root.children[0]
    assert node.name == "file1.txt"
    assert node.binary_index == 0
    assert getattr(node, 'classification', None) == "confidential"

def test_merge_modified_file(tm):
    old_root, old_binary, new_root, new_binary = create_mock_test_files("modified")
    
    merged_tree, merged_binary = tm.merge_trees(old_root, old_binary, new_root, new_binary)
    
    #assert new content used, metadata reset
    assert len(merged_binary) == 1
    assert merged_binary[0] == b"new_content"
    
    node = new_root.children[0]
    assert node.binary_index == 0
    assert getattr(node, 'classification', None) is None

def test_merge_new_file(tm):
    old_root, old_binary, new_root, new_binary = create_mock_test_files("new")
    
    merged_tree, merged_binary = tm.merge_trees(old_root, old_binary, new_root, new_binary)
    
    assert len(merged_binary) == 1
    assert merged_binary[0] == b"new_data"
    assert new_root.children[0].name == "new_file.txt"

def test_merge_deleted_file(tm):
    old_root, old_binary, new_root, new_binary = create_mock_test_files("deleted")
    
    merged_tree, merged_binary = tm.merge_trees(old_root, old_binary, new_root, new_binary)
    
    #assert file removed from result
    assert len(merged_binary) == 0
    assert len(merged_tree.children) == 0

def test_mixed_merge_scenario(tm):
    old_root, old_binary, new_root, new_binary = create_mock_test_files("mixed")
    
    merged_tree, merged_binary = tm.merge_trees(old_root, old_binary, new_root, new_binary)
    
    #assert binary order in merged list: 
    # 1. A (from old)
    # 2. B (from new/updated)
    # 3. C (from new/added)
    
    assert len(merged_binary) == 3
    assert merged_binary[0] == b"dataA"
    assert merged_binary[1] == b"dataB_new"
    assert merged_binary[2] == b"dataC"
    
    #Verify nodes
    children = {c.name: c for c in new_root.children}
    
    # A.txt: Unchanged
    assert children["A.txt"].classification == "keep_me"
    assert children["A.txt"].binary_index == 0
    
    # B.txt: Modified
    assert getattr(children["B.txt"], 'classification', None) is None
    assert children["B.txt"].binary_index == 1
    
    # C.txt: New
    assert children["C.txt"].binary_index == 2

def test_nested_structure_merge(tm):
    old_root, old_binary, new_root, new_binary = create_mock_test_files("nested")
    
    merged_tree, merged_binary = tm.merge_trees(old_root, old_binary, new_root, new_binary)
    
    assert len(merged_binary) == 1
    
    #assert that we found the file deep in the tree and preserved meta
    new_sub_node = new_root.children[0]
    new_file_node = new_sub_node.children[0]
    
    assert new_file_node.name == "file.txt"
    assert new_file_node.classification == "meta"
    assert new_file_node.binary_index == 0