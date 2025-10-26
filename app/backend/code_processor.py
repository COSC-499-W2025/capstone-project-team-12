from typing import List
import pygments

import pygments.lexers
import pygments.util
import pygments.token as tk
from anytree import Node

#minimum token length for consideration
MIN_TOKEN_LEN = 5

# Lists composed of pygments.token type. 
# All tokens of type not in Include will be dropped
# All tokens of a type in Include but also of a type in exclude will be dropped
# Eg. for python code, to include all Identifiers add: "pygments.token.Name" to Include
# But you can exclude built in functions from the above by adding: "pygments.token.Name.Builtin" to exclude
# i.e exclude will remove certain subtypes of token types allowed by Include.
# EXCLUDE HAS HIGHER PRIORITY
#set values by using 'set_filters(...)' function defined below.
Include = [tk.Comment, tk.Name,tk.Name.Function] #Default values for inclusion filter
Exclude = [tk.Whitespace,tk.Punctuation,tk.Operator,tk.__builtins__,tk.Keyword] #Default value for exclusion filter

#OOP method to get current state of filters. Returns none if Filters are not Intialized
def get_code_filters()->List[List[pygments.token]]:
    global Include 
    global Exclude
    if Include is not None and Exclude is not None:
        #print("Inclusion Filters:" +str(Include) + '\n')
        #print("Exclusion Filters:" +str(Exclude) + '\n')
        return [Include,Exclude]
    else:
        return None
        

# Sets values of code token type filters. Returns true on success, false on fail.
def set_code_filters(include: List[pygments.token], exclude: List[pygments.token]) -> bool:
    try:
        global Include 
        global Exclude  
        Include = include
        Exclude = exclude
        return True         #Sucessfully set token filters
    except:
        print("Failed to set token type filters")    
        return False        #Failed to set token filters
    
def append_code_filters(include: List[pygments.token], exclude: List[pygments.token]):
    try:
        global Include, Exclude
        Include = Include + include
        Exclude = Exclude + exclude
        return True #Sucessfully added token filters
    except:
        print("Failed to add token type filters")    
        return False #Failed to add token filters



# Primary function to be used by main.py, Receives node array and returns Array of Arrays consisting of user defined tokens.
# Each sub array refers to Identifiers extracted from individual files
# eg. [
#      ["ExampleVariable","Account Balance","Suspicion Flag"]
#      ["IntegralDivisions,TestVarInt"]
#     ]
#By default the above string version is followed, set asString to False and receive pygments tokens directly
def code_preprocess(node_array: List[Node],asString:bool = True) -> List[List[pygments.token]] | List[List[str]]:
    codefile_tokenlist:List[List[pygments.token]] = [] #typed list of list with pypi tokens.
    for node in node_array: #Process each node
       #with get_identifiers(node) as tokenarray:
        tokenarray: List[pygments.token] = get_identifiers(node)
        if tokenarray is not None: #If downstream error then will be none!
            codefile_tokenlist.append(tokenarray)
        else:
            print("Failed to process code file:" + node)
            continue
    if asString: #use helper function to convert pypi tokens to strings (for text_process)
        temp:List[List[str]] = []
        for sublist in codefile_tokenlist:
            temp.append(pypiToken_to_string(sublist))
        codefile_tokenlist = temp
    return codefile_tokenlist

#Helper function to convert array of pypi tokens to array of Strings
def pypiToken_to_string(tokenarray: List[pygments.token]) -> List[str]:
    token_strList: List[str] = []
    for pypiToken in tokenarray:
        token_strList.append(pypiToken[1])
    return token_strList

# Returns an array of Pygment token objects when provided with a filepath
# Uses filepath to identify language, returns None if language not supported.
def get_tokens(filepath:str) -> List[pygments.token]:
    with open(filepath, "r", encoding="utf-8") as file:
        code_string =  file.read()
        #Try tp get appropriate lexer using the filepath and extension
        try:
            lexer = pygments.lexers.get_lexer_for_filename(filepath)
            return list(pygments.lex(code_string,lexer))
        #If Language not supported or, extension is invalid. Print error to console and Return None
        except pygments.util.ClassNotFound:
            print("Failed to identify Lexer! Language Not supported or Invalid file extension.\n")
            return None

# Given a anytree filenode with filename attribute, returns list of all valid tokens. 
# For definition of valid token see filters.
def get_identifiers(node: Node) -> List[pygments.token]:
    tokens = get_tokens(node.filepath)
    if tokens is None:
        print("Failed to get tokens from file")
        return None
    else:
        temp = list(filter(filter_by_category,tokens)) #Use filter function that returns true or false to generate iterable of tokens
        return list(temp)


# Uses the global Include Exclude filters to return True or False
# True if it passes all filters, false in every other case.
def filter_by_category(token: pygments.token) -> bool:
    if len(token[1]) < MIN_TOKEN_LEN: #filter out short variables and functions like 'flag' 'endl' 'cout' etc
        return False
    if token[0] in Exclude: #Exclude Filter
        return False
    if token[0] not in Include: #Include Filter
        return False
    else:
        return True #Return true if all filters pass!


def localtest(filepath:str):
    
    #Test Getting and Setting Filters:
    get_code_filters()
    append_code_filters([],[])
    get_code_filters()
    
    #Test Identifier Extraction:
    testNode: Node = Node("testingNode")
    testNode.filepath = str(filepath)
    nodelist: List[Node] = [testNode,testNode]
    output = list(code_preprocess(nodelist))
    for result in output:
        print("RESULT" + str(result))
    return


localtest("tests_backend/test_main_dir/code_proc_testfile.cpp")