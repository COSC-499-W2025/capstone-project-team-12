from combined_preprocess import combined_preprocess
from anytree import Node
from typing import List
import pytest

# Test fixtures - shared test data
@pytest.fixture
def text_nodes():
    """Create test text file nodes"""
    return [
        Node("simple.txt", file_data={'binary_index': 0, 'filename': 'simple.txt'}),
        Node("readme.md", file_data={'binary_index': 1, 'filename': 'readme.md'}),
        Node("empty.txt", file_data={'binary_index': 2, 'filename': 'empty.txt'})
    ]

@pytest.fixture
def text_data():
    """Test text file contents"""
    return [
        "This is a simple text document",
        "Project documentation with important details",
        ""
    ]

@pytest.fixture
def code_nodes():
    """Create test code file nodes"""
    return [
        Node("code.py", file_data={'binary_index': 0, 'filename': 'code.py', 'filepath': '/test/code.py'}),
        Node("script.js", file_data={'binary_index': 1, 'filename': 'script.js', 'filepath': '/test/script.js'}),
        Node("empty.cpp", file_data={'binary_index': 2, 'filename': 'empty.cpp', 'filepath': '/test/empty.cpp'})
    ]

@pytest.fixture
def code_data():
    """Test code file contents"""
    return [
        "def calculate_sum(first_value, second_value):\n    return first_value + second_value",
        "function getUserName() { return user_name; }",
        ""
    ]

# Basic functionality tests
def test_text_only(text_nodes, text_data):
    # Ensures process text files correctly
    result = combined_preprocess(text_nodes[:2], text_data[:2], [], [])
    
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(token, str) for doc in result for token in doc)

def test_code_only(code_nodes, code_data):
    # Ensures process code files correctly
    result = combined_preprocess([], [], code_nodes[:2], code_data[:2])
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(token, str) for doc in result for token in doc)

def test_mixed_text_and_code(text_nodes, text_data, code_nodes, code_data):
    # Ensure combine text and code files done correctly
    result = combined_preprocess(text_nodes[:1], text_data[:1], code_nodes[:1], code_data[:1])
    
    assert isinstance(result, list)
    assert len(result) >= 2
    assert all(isinstance(doc, list) for doc in result)

def test_empty_inputs():
    # Should handle empty input gracefully
    result = combined_preprocess([], [], [], [])
    
    assert result == []

def test_normalize_parameter(code_nodes, code_data):
    # Should respect normalize parameter
    result_normalized = combined_preprocess([], [], code_nodes[:1], code_data[:1], normalize=True)
    result_unnormalized = combined_preprocess([], [], code_nodes[:1], code_data[:1], normalize=False)
    
    assert isinstance(result_normalized, list)
    assert isinstance(result_unnormalized, list)

# Edge case tests
def test_empty_files(text_nodes, text_data, code_nodes, code_data):
    # Should handle empty files correctly
    result = combined_preprocess(text_nodes[2:], text_data[2:], code_nodes[2:], code_data[2:])
    
    assert isinstance(result, list)

def test_comprehensive(text_nodes, text_data, code_nodes, code_data):
    # Should process all file types together
    result = combined_preprocess(text_nodes, text_data, code_nodes, code_data, normalize=True)
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(doc, list) for doc in result)
    # Verify all tokens are strings and non-empty
    for doc in result:
        if doc:  # Skip empty documents
            assert all(isinstance(token, str) and len(token) > 0 for token in doc)