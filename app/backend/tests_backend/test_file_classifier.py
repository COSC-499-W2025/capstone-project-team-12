import pytest
from anytree import Node
from file_classifier import FileClassifier

@pytest.fixture
def classifier():
    return FileClassifier()

@pytest.fixture
def code_tree():
    """
    Create code tree
    """
    root = Node(
        "project", 
        type="directory", 
        path="/project",
        classification=None,
        is_repo_head=False,
        binary_data_index=0
    )
    img = Node("image.png",
        type="file",
        path="/project/image.png",
        classification=None,
        is_repo_head=False,
        parent=root,
        extension='.png',
        binary_data_index=1
    )
    git = Node(".git", 
        type="directory", 
        path="/project/.git",
        classification=None,
        is_repo_head=False,
        parent=root,
        binary_data_index=2
    )
    src = Node("src", 
        type="directory", 
        path="/project/src",
        classification=None,
        is_repo_head=False,
        parent=root,
        binary_data_index=3
    )
    app_js = Node("app.js", 
        type="file", 
        path="/project/src/app.js",
        classification=None,
        is_repo_head=False,
        parent=src,
        extension='.js',
        binary_data_index=4
    )
    main_py = Node("main.py", 
        type="file", 
        path="/project/main.py",
        classification=None,
        is_repo_head=False,
        parent=root,
        extension ='.py',
        binary_data_index=5
    )
    config = Node("config.json",
        type="file",
        path="/project/src/config.json",
        classification=None,
        is_repo_head=False,
        parent=src,
        extension='.json',
        binary_data_index=6
    )

    return root

@pytest.fixture
def mixed_tree():
    """
    Create mixed tree
    """

    root = Node("project", 
        type="directory", 
        path="/project",
        classification=None,
        is_repo_head=False,
        binary_data_index=0
    )
    img = Node("image.png",
        type="file",
        path="/project/image.png",
        classification=None,
        is_repo_head=False,
        parent=root,
        extension='.png',
        binary_data_index=1
    )
    git = Node(".git", 
        type="directory", 
        path="/project/.git",
        classification=None,
        is_repo_head=False,
        parent=root,
        binary_data_index=2
    )
    src = Node("src", 
        type="directory", 
        path="/project/src",
        classification=None,
        is_repo_head=False,
        parent=root,
        binary_data_index=3
    )
    app_js = Node("app.js", 
        type="file", 
        path="/project/src/app.js",
        classification=None,
        is_repo_head=False,
        parent=src,
        extension='.js',
        binary_data_index=4
    )
    readme = Node("README.md", 
        type="file", 
        path="/project/README.md",
        classification=None,
        is_repo_head=False,
        parent=root,
        extension ='.md',
        binary_data_index=5
    )
    config = Node("config.json",
        type="file",
        path="/project/src/config.json",
        classification=None,
        is_repo_head=False,
        parent=src,
        extension='.json',
        binary_data_index=6
    )

    return root

@pytest.fixture
def binary_data_array():
    """
    Create test binary data array
    """
    return [b'data1', b'data2', b'data3', b'data4', b'data5', b'data6']



def test_classify_files(classifier, mixed_tree, binary_data_array):
    """Test classify_files with mixed tree"""
    text_files, code_files, binary_data = classifier.classify_files(mixed_tree, binary_data=binary_data_array)

    # verifty classifications
    assert len(text_files) == 1
    assert (getattr(node, "classification", None) == "text" for node in text_files)
    text_names = {node.name for node in text_files}
    assert "README.md" in text_names

    assert len(code_files) == 2
    assert all(getattr(node, "classification", None) == "code" for node in code_files)
    code_names = {node.name for node in code_files}
    assert "app.js" in code_names
    assert "config.json" in code_names
    
    # verify invalid files are removed
    assert ".git" not in [node.name for node in text_files + code_files]
    assert "image.png" not in [node.name for node in text_files + code_files]
    assert binary_data[1] is None # image.png data removed
    assert binary_data[2] == b"data3"

    assert all(node.parent is None for node in text_files + code_files)

def test_classify_files_with_none_tree(classifier):
    """Test classify_files raises ValueError with None tree"""
    with pytest.raises(ValueError, match="Unprocessed tree cannot be None"):
        classifier.classify_files(None, [])


def test_classify_files_with_invalid_type(classifier):
    """Test classify_files raises TypeError with invalid tree type"""
    with pytest.raises(TypeError, match="Expected Node object, got"):
        classifier.classify_files("not a node", [])

def test_classify_files_empty_tree(classifier):
    """Test classify_files with empty tree"""
    root = Node("empty", type="directory", path="/empty", classification=None)
    text_files, code_files, binary_data = classifier.classify_files(root, [])
    
    assert len(text_files) == 0
    assert len(code_files) == 0
    assert binary_data == []

def test_filter_tree_text_mode(classifier, mixed_tree, binary_data_array):
    """Test _filter_tree in text mode"""
    text_files, remaining_tree = classifier._filter_tree(mixed_tree, "text", binary_data_array)

    assert len(text_files) == 1
    text_names = {node.name for node in text_files}
    assert "README.md" in text_names
    assert "app.js" not in text_names 

    # verify classifications and detachment
    for node in text_files:
        assert node.classification == "text"
        assert node.parent is None

    # verify invalid files are removed and code files remain
    remaining_files = {node.name for node in remaining_tree.descendants if hasattr(node, "type") and node.type == "file"}
    assert "app.js" in remaining_files
    assert "config.json" in remaining_files
    assert "image.png" not in remaining_files
    assert ".git" not in remaining_files

def test_filter_tree_code_mode(classifier, code_tree, binary_data_array):
    """Test _filter_tree in code mode"""
    code_files, remaining_tree = classifier._filter_tree(code_tree, "code", binary_data_array)

    assert len(code_files) == 3
    code_names = {node.name for node in code_files}
    assert "app.js" in code_names
    assert "main.py" in code_names

    # verify classifications and detachment
    for node in code_files:
        assert node.classification == "code"
        assert node.parent is None

    # reamaining tree should only have files that are neither code nor text
    assert len(remaining_tree.descendants) == 2  # image.png and .git remain


def test_is_text(classifier):
    """Test _is_text"""
    txt_node = Node("test.txt", type="file", extension='.txt')
    md_node = Node("readme.md", type="file", extension='.md')
    pdf_node = Node("doc.pdf", type="file", extension='.pdf')
    py_node = Node("script.py", type="file", extension='.py')
    invalid = Node("file", type="file", extension=None)
    
    assert classifier._is_text(txt_node) == True
    assert classifier._is_text(md_node) == True
    assert classifier._is_text(pdf_node) == True
    assert classifier._is_text(py_node) == False
    assert classifier._is_text(invalid) == False


def test_is_code(classifier):
    """Test _is_code"""
    js_node = Node("app.js", type="file", extension='.js')
    py_node = Node("main.py", type="file", extension='.py')
    txt_node = Node("readme.docx", type="file", extension='.docx')
    unknown_ext = Node("file.xyz", type="file", extension='.xyz')
    
    assert classifier._is_code(js_node) == True
    assert classifier._is_code(py_node) == True
    assert classifier._is_code(txt_node) == False
    assert classifier._is_code(unknown_ext) == False


def test_get_extension(classifier):
    """Test _getExtension """
    # node with extension attribute
    node_with_ext = Node("test.txt", type="file", extension='.txt')
    assert classifier._getExtension(node_with_ext) == '.txt'
    
    # Node without extension attribute
    node_no_ext = Node("test", type="file")
    assert classifier._getExtension(node_no_ext) == ''
    
    # Node with empty extension
    node_empty = Node("test.", type="file", extension='')
    assert classifier._getExtension(node_empty) == ''
    

def test_detach_node(classifier):
    """Test _detach_node"""
    parent = Node("parent", type="directory", binary_data_index=0)
    child = Node("child.txt", type="file", parent=parent, binary_data_index=1)
    binary_data = [b'data1', b'data2']

    classifier._detach_node(child, binary_data)

    assert child.parent is None
    assert binary_data[1] is None

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])