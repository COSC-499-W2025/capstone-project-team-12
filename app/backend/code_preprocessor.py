from typing import List
import pygments
import pygments.lexers
import pygments.util
import pygments.token as tk
import pygments.lexer
from anytree import Node
import regex as re
from pathlib import Path


#minimum token length for consideration
MIN_TOKEN_LEN = 5

def set_min_len(min_len:int) -> bool:
    """
    Sets the minimum length of token to be considered in code preprocess pipeline
    Returns True on Success, False on Failure
    """
    global MIN_TOKEN_LEN 
    try:
        MIN_TOKEN_LEN = min_len
        return True
    except:
        return False

def get_min_len()-> int:
    """Returns current setting for minimum length of token to be considered in code preprocess pipeline"""
    global MIN_TOKEN_LEN
    return MIN_TOKEN_LEN


# Lists composed of pygments.token type
# All tokens of type not in Include will be dropped
# All tokens of a type in Include but also of a type in exclude will be dropped
# Eg. for python code, to include all Identifiers add: "pygments.token.Name" to Include
# But you can exclude built in functions from the above by adding: "pygments.token.Name.Builtin" to exclude
# i.e exclude will remove certain subtypes of token types allowed by Include.
# EXCLUDE HAS HIGHER PRIORITY
#set values by using 'set_filters(...)' function defined below.
Include: List[pygments.token] = [tk.Comment, tk.Name,tk.Name.Function,tk.Text] #Default values for inclusion filter
Exclude: List[pygments.token] = [tk.Whitespace,tk.Punctuation,tk.Operator,tk.__builtins__,tk.Keyword,tk.Generic] #Default value for exclusion filter


def get_code_filters()->List[List[pygments.token]]|None:
    """OOP method to get current state of filters. Returns none if Filters are not Intialized"""
    global Include 
    global Exclude
    if Include is not None and Exclude is not None:
        #print("Inclusion Filters:" +str(Include) + '\n')
        #print("Exclusion Filters:" +str(Exclude) + '\n')
        return [Include,Exclude]
    else:
        return None
        


def set_code_filters(include: List[pygments.token], exclude: List[pygments.token]) -> bool:
    """Sets values of code token type filters. Returns true on success, false on fail."""
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
    """Appends parameter Lists's elements of code token type to filter lists. Returns true on success, false on fail."""
    try:
        global Include, Exclude
        Include = Include + include
        Exclude = Exclude + exclude
        return True #Sucessfully added token filters
    except:
        print("Failed to add token type filters")    
        return False #Failed to add token filters




def code_preprocess(code_nodes: List[Node],code_data:List[str], normalize:bool = True) -> List[List[str]]:
    """
    Primary function to be used by main.py, Receives node array and returns Array of Arrays consisting of user defined tokens.

    Args:
        code_nodes (List[Node]): List of code nodes
        code_data (List[str]): List of code_data corresponding to code_nodes, must be string not bytes or BinaryIO
        normalize (bool, optional): Defaults to True. See note for description

    Returns:
        List[List[str]]: See note for descripton
        
    Note:   
        # Each sub array refers to Identifiers extracted from individual files
        # eg. [
        #      ["Example","Variable","Account","Balance","Suspicion Flag"]
        #      ["Integral","Divisions","Test","Var","Int"]
        #     ]
        # By default the tokens are normalized, i.e snake_case and camelCase is removed and each sub word is seperated into multiple strings 
        # set normalize to false to preserve camelCase or snake_case    
    """
    
    #Output list that will be returned
    codefile_tokenlist:List[List[pygments.token]] = [] #typed list of list with pypi tokens.
    
    #Preprocess each node in code_files_array
    for i in range(len(code_nodes)): #Process each node
        
        #Declare loop variables
        lexer:pygments.lexer = None
        tokenarray:List[pygments.token|str] = []
        
        
        #Load Lexer, if failed to Load Lexer skip file
        try:
            lexer = identify_lexer(code_nodes[i],code_data[i])
        except Exception as e:
            codefile_tokenlist.append([''])
            tmp_filename:str = code_nodes[i].file_data['filename']
            print(f"Failed to get lexer for file {tmp_filename}:\n\t Reason: {e}\n\tSkipping File...")
            continue
        
        #tokenize code, on fail skipfile
        try:
            tokenarray = get_tokens(code_data[i],lexer)
        except Exception as e:
            codefile_tokenlist.append([''])
            tmp_filename:str = code_nodes[i].file_data['filename']
            print(f"Failed to get tokens for file {tmp_filename}: \n\t Reason: {e}\n\tSkipping File...")
            continue      

        #Extract identifiers from code
        try:
            tokenarray = extract_identifiers(tokenarray)
        except Exception as e:
            codefile_tokenlist.append([''])
            tmp_filename:str = code_nodes[i].file_data['filename']
            print(f"Failed to extract identifiers for file {tmp_filename}:\n\t Reason: {e}\n\tSkipping File...")
            continue
    tokenarray = pygmentTokenList_to_stringTokenList(tokenarray)
    if normalize:
        tokenarray = normalize_identifiers(tokenarray)
    
    codefile_tokenlist.append(tokenarray)
    return codefile_tokenlist


def pygmentTokenList_to_stringTokenList(tokenarray: List[pygments.token]) -> List[str]:
    """Helper for `code_preprocess(...)` to convert an array of pygment tokens to array of strings"""
    token_strList: List[str] = []
    for token in tokenarray:
        token_strList.append(token[1]) #gensim does not automatically lowercase tokens like Spacy
    return token_strList

def normalize_identifiers(idents:List[str])-> List[str]:
    """Helper function to normalize all identifiers in a list"""
    normalized_idents:List[str] = [] 
    for ident in idents:
        normalized_idents.extend(normalize_identifier(ident))
    return normalized_idents

def normalize_identifier(ident:str)->List[str]:
    """Normalizes identifiers by eliminating camelCase/snake_case and splitting each word in identifier"""
    #replace camelCase with consideration to Acronyms
    ident = re.sub(r"""((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))""", r' \1',ident)

    #Explanation for above regex
    #if BOTH the following 2 cases are true:
    #(?<=[a-z])[A-Z] (Any number of lowercase letters)[Followed by single uppercase letter]
    #(?<!\A)[A-Z](?=[a-z]) (A non starting uppercase letter)[But is an uppercase letter](And is followed by a lowercase letter)
    #Then add a leading blank and the matching substring!

    ident = ident.replace("_"," ")   #replace underscore with spaces
    ident = ident.lower()            #lowercase the extracted tokens
    
    #By this stage an identifiier like 'capybaraCount_SpecifierCAPYS' should be 'capybara count specifier capys'
    #With this normalized form, split the token name by using space as seperator
    tokenList: List[str] = ident.split(sep=' ')
    tokenList = [token.lower() for token in tokenList] #Gensim does not lowercase tokens automatically must be done manually.
    return tokenList


def get_tokens(code_data:str,lexer:pygments.lexer) -> List[pygments.token]:
    """
        Returns an array of Pygment token objects when provided with a code data
        Must provide lexer that corresponds to code data
        On fail to load tokens, Raises Exception
    """
    tokens:List[pygments.token] = list(pygments.lex(code_data,lexer))
    return tokens
    if tokens is None:
        raise Exception("Failed to get tokens from file")
    return

def identify_lexer(code_node:Node,code_data:str):
    """
        Attempts to find and return appropriate lexer for code file.
        First by using filepath/name
        Second by guessing from content of file
        
        On Fail returns pygments.util.ClassNotFound error 
    """
    lexer: pygments.lexer = None
    try:
        lexer = pygments.lexers.get_lexer_for_filename(code_node.file_data['filename'])
        return lexer
    #Codeblock below runs if language cannot be identified by filename
    except pygments.util.ClassNotFound as e1:
        #Try to find the appropriate lexer by analyzing the data directly
        try:
            lexer = pygments.lexers.guess_lexer(code_data)
            return lexer
        except pygments.util.ClassNotFound as e2:
            raise pygments.util.ClassNotFound("Failed to identify Lexer! Language Not supported or Invalid file extension.")


def extract_identifiers(token_list:List[pygments.token]) -> List[pygments.token]:
    """
        Given a List of pygment tokens, 
        returns list of all filtered tokens
    """
    
    tokens: List[pygments.token] = []
    if token_list is None or len(token_list) == 0:
        print("Failed to get tokens from file")
        raise Exception
    else:
        tokens = list(filter(filter_by_category,token_list)) #Use filter function that returns true or false to generate iterable of tokens
        return tokens



def filter_by_category(token: pygments.token) -> bool:
    """
        Uses the global Include Exclude filters to return True or False
        True if it passes all filters, false in every other case.
    """
    
    if len(token[1]) < MIN_TOKEN_LEN: #filter out short variables and functions like 'flag' 'endl' 'cout' etc
        return False
    if token[0] in Exclude: #Exclude Filter
        return False
    if token[0] not in Include: #Include Filter
        return False
    else:
        return True #Return true if all filters pass!

if __name__ == "__main__":
    
    def localtest(filepath:str):
        tmpString:str = ''
        
        def print_output(output):
            for result in output:
                print(str(result)+'\n')
            return

        with open(filepath,'r') as f:
            tmpString = f.read()
            
        #Test Getting and Setting Filters:
        #print(get_code_filters())
        #append_code_filters([],[])
        #print(get_code_filters())
        
        #Test Identifier Extraction:
        testNode: Node = Node("testingNode",file_data={})
        testNode.file_data['filepath'] = str(filepath)
        testNode.file_data['filename'] = str(Path(filepath).name)
    
        nodelist: List[Node] = [testNode,testNode]
        datalist: List[str] = [tmpString,tmpString]
        #Test Primary output type
        output = list(code_preprocess(nodelist,datalist))    
        print("\n----PRIMARY RESULT----\n")
        print_output(output)

        #Test Secondary output type
        output = list(code_preprocess(nodelist,datalist,normalize = False)) 
        print("\n----SECONDARY RESULT----\n")
        print_output(output)

    localtest("app/backend/tests_backend/test_main_dir/mock_files/codeProcessor_testfile.cpp")