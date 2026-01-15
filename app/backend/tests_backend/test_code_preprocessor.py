import pytest
from anytree import Node
import code_preprocessor
import pygments
import pygments.token as tk
from pygments.token import _TokenType


@pytest.fixture
def code_nodes():
    """Create test code file nodes"""
    return [
        Node("code.py", file_data={'binary_index': 0, 'filename': 'code.py', 'filepath': '/test/code.py'}),
        Node("script.js", file_data={'binary_index': 1, 'filename': 'script.js', 'filepath': '/test/script.js'}),
        Node("empty.cpp", file_data={'binary_index': 2, 'filename': 'empty.cpp', 'filepath': '/test/empty.cpp'}),
        Node("codeProcessor_testfile.cpp", file_data={'binary_index': 3, 'filename': 'codeProcessor_testfile.cpp', 'filepath': '/test/codeProcessor_testfile.cpp'})
    ]

@pytest.fixture
def code_data():
    """Test code file contents"""
    
    with open("tests_backend/test_main_dir/mock_files/codeProcessor_testfile.cpp",'r') as file:
        large_code:str = file.read()
    
    return [
        "def calculate_sum(first_value, second_value):\n    return first_value + second_value",
        "function getUserName() { return user_name; }",
        "",
        large_code
    ]
    
def test_get_filters():
    #get result from function
    result = code_preprocessor.get_code_filters()
    #Assert declared return type is followed
    assert isinstance(result,list)
    assert len(result) == 2

    #Check that all elements are a valid pygments.token type
    assert isinstance(result[0],list)
    assert isinstance(result[1],list)
    assert all(isinstance(x,_TokenType)for x in result[0])
    assert all(isinstance(x,_TokenType)for x in result[1]) 

def test_set_filters():
    
    #Bad input to check if except statement works
    with pytest.raises(Exception):
        code_preprocessor.set_code_filters(1,Node()) #Bad input to check if except statement works
    
    assert code_preprocessor.set_code_filters([tk.Comment,tk.Name],[tk.Punctuation,tk.Keyword]) #assert that return value is true indicating success
    
    resulting_filters = code_preprocessor.get_code_filters()
    
    #Check if filters were actually set
    assert resulting_filters[0] == [tk.Comment,tk.Name] 
    assert resulting_filters[1] == [tk.Punctuation,tk.Keyword]

def test_append_filters():
    
    #Bad input to check if except statement works
    with pytest.raises(Exception):
        code_preprocessor.append_code_filters(1,Node()) #Bad input to check if except statement works
    
    assert code_preprocessor.append_code_filters([tk.Text],[tk.Operator]) #assert that return value is true indicating success
    
    resulting_filters = code_preprocessor.get_code_filters()
    
    #Check if filters were actually set
    assert resulting_filters[0] == [tk.Comment,tk.Name,tk.Text] 
    assert resulting_filters[1] == [tk.Punctuation,tk.Keyword,tk.Operator]