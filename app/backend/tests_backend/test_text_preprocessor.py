from pytest_mock import mocker
from text_preprocessor import *
from anytree import Node
from typing import OrderedDict

#generated mock nodes based on mock files.
nodelist:OrderedDict[str,Node] = {}
#generated mock data list for use by text preprocessor
datalist:List|None = []

#Adds a mock entry to both nodelist and datalist based on file name and content
#Only adds attributes used by text_preprocessor to Nodes (for minimal coupling)
def add_mock_entry(name:str,content:str):
    
    #static variable implemented as func attribute to track functioncals
    if not hasattr(add_mock_entry,"idxCounter"):
        add_mock_entry.idxCounter=0
    else:
        add_mock_entry.idxCounter += 1
    
    #scoping global variiables
    global nodelist,datalist
    
    #construct test node
    testNode:Node = Node(name,file_data={'binary_index':add_mock_entry.idxCounter})
    
    #add entries to global Lists
    nodelist[name] = testNode
    if content is not None:
        datalist.append(content)
    else:
        datalist.append('')
    return

#Adds mockdata to global lists
def test_setUp():
    add_mock_entry("simple_text","This is the simple text used")
    add_mock_entry("stopwords_text","the and if but or")
    add_mock_entry("punctuations_text","...!!!???")
    add_mock_entry("empty_text",None)
    
    largetext_1= open("tests_backend/test_main_dir/mock_files/textProcessor_testfile1.txt",'rb').read()
    largetext_2= open("tests_backend/test_main_dir/mock_files/textProcessor_testfile2.txt",'rb').read()
    add_mock_entry("lg_text_test1",str(largetext_1))
    add_mock_entry("lg_text_test2",str(largetext_2))

#gets file data from liist based on passed node
def get_test_str(node:Node):
    testStr :str = datalist[node.file_data['binary_index']]     #access bin_idx from node
    return testStr
  
#--------------
# Test operations chain
#--------------
  
def test_get_tokens():
    tokens = get_tokens(get_test_str(nodelist['simple_text']))
    # ensure it returns a list of strings
    assert all(isinstance(token, str) for token in tokens)
    # ensure common words are tokenized
    expectedResult = ['This','is','the','simple','text','used']
    assert all(expected==result for expected, result in zip(expectedResult,tokens))

def test_stopword_filtering():
    tokens = get_tokens(get_test_str(nodelist['simple_text']))
    filtered = stopword_filtered_tokens(tokens)
    assert  all(word.isalpha() for word in filtered)
    assert "the" not in filtered #"the" is a stopword and should be removed
    expectedResult = ['simple','text','used']
    assert all(expected==filtered for expected, filtered in zip(expectedResult,filtered))

def test_lemmatization():
    tokens = stopword_filtered_tokens(get_tokens(get_test_str(nodelist['simple_text'])))
    lemmatized = lemmatize_tokens(tokens)
    assert all(isinstance(lemma,str)for lemma in lemmatized) 
    # ensure known lemmas appear
    assert "use" in lemmatized
    assert "used" not in lemmatized

#-------------
# Edgecase testing
#-------------
def test_stopword_only():
    tokens = get_tokens(get_test_str(nodelist['stopwords_text']))
    filtered = stopword_filtered_tokens(tokens)
    assert len(filtered) == 0
    

def test_punctuation_only():
    tokens = get_tokens(get_test_str(nodelist['punctuations_text'])) # long string of punctuation marks should all be removed
    assert len(tokens) == 0

#-------------
# Large file and comprehensive test
#-------------
   
def test_large_simple():
    tokens = stopword_filtered_tokens(get_tokens(get_test_str(nodelist['lg_text_test2'])))
    lemmatized = lemmatize_tokens(tokens)
    assert all(isinstance(lemma,str)for lemma in lemmatized)     

def test_large_complex():
    tokens = stopword_filtered_tokens(get_tokens(get_test_str(nodelist['lg_text_test1'])))
    lemmatized = lemmatize_tokens(tokens)
    assert all(isinstance(lemma,str)for lemma in lemmatized) 

def test_comprehensive(mocker):
    mocker.patch('text_preprocessor.get_data',return_value = datalist)
    temp_nodelist: List[Node] = list(nodelist.values())
    print(temp_nodelist)
    result: List[List[str]] = text_preprocess(temp_nodelist)
    for x in result:
        print(x)
    assert isinstance(result,List)
    assert len(result) == 6
    assert all(isinstance(sublist,List)for sublist in result)
    for sublist in result:
        assert all(isinstance(token,str)for token in sublist)
    