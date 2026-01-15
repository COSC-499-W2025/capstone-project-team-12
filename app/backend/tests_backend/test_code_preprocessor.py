import pytest
from anytree import Node
import code_preprocessor
import pygments.token as tk
from pygments.token import _TokenType
from pygments.util import ClassNotFound
from pygments.lexer import Lexer
import pygments

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
    
#generates token data based on above test data to be used in tests for token based functions
@pytest.fixture
def token_data(code_nodes,code_data):
    """Returns token data for functions that expect tokens as input"""
    token_filelist:list[list[pygments.token]] = []
    lexers: list[pygments.lexer] = []
    for i in range(len(code_nodes)):
        lexer = code_preprocessor.identify_lexer(code_nodes[i],code_data[i])
        lexers.append(lexer)
        tokenlist = code_preprocessor.get_tokens(code_data[i],lexers[i])
        token_filelist.append(tokenlist)
    return token_filelist

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
    
# Not a test just resets filters to default values so the rest of testing is representative of general use-case
def reset_filters():
    code_preprocessor.set_code_filters([tk.Comment, tk.Name,tk.Name.Function,tk.Text],
                                       [tk.Whitespace,tk.Punctuation,tk.Operator,tk.__builtins__,tk.Keyword,tk.Generic])
    assert True
#tests lexer    
def test_identify_lexer(code_nodes,code_data):
    
    #For all test nodes try identifying the lexer
    for i in range(len(code_nodes)):
        node_result = code_preprocessor.identify_lexer(code_nodes[i],code_data[i])
        assert isinstance(node_result,Lexer)
        assert node_result.name in ["JavaScript","Python","C++"]
    
    #Test if error is raised for a badly formed code file that cannot be identified both based on filename AND code data
    with pytest.raises(ClassNotFound):
        test_node: Node = Node("hullaballu.capys", file_data={'binary_index': 0, 'filename': 'hullaballu.capys', 'filepath': '/test/hullaballu.capys'})
        test_data:str = "CAPYSMASH BE LIKE: ijsdwafbiojns()[ doi::gjinaois ebfi+usdjk gnffdn jgklas kxjnig"
        result = code_preprocessor.identify_lexer(test_node,test_data)
        print(result.name)

def test_get_tokens(code_nodes,code_data):
    
    #Test Setup
    lexers:list[pygments.lexer] = []
    for i in range(len(code_nodes)):
        lexer = code_preprocessor.identify_lexer(code_nodes[i],code_data[i])
        lexers.append(lexer)
    
    #Gathering results for all test data    
    results: list[list[pygments.token]] = []
    for i in range(len(code_data)):
            result = code_preprocessor.get_tokens(code_data[i],lexers[i])    
            results.append(result)
    
    #Checking that tokens were fetched and they are all of the correct type
    for result in results:
        assert all(isinstance(token[0],_TokenType)for token in result)

def test_pygToken_toStr_conversion(token_data):
    for tokenlist in token_data:
        result_token_list = code_preprocessor.pygmentTokenList_to_stringTokenList(tokenlist)
        assert all(isinstance(token,str)for token in result_token_list)
