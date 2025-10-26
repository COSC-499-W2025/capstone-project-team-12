from typing import List
import pygments.util
import pygments.lexers
import pygments.token as tk
import pygments
from anytree import Node


# Lists composed of pygments.token type. 
# All tokens of type not in Include will be dropped
# All tokens of a type in Include but also of a type in exclude will be dropped
# Eg. for python code, to include all Identifiers add: "pygments.token.Name" to Include
# But you can exclude built in functions from the above by adding: "pygments.token.Name.Builtin" to exclude
#i.e exclude will remove certain subtypes of token types allowed by Include.
#set values by using 'set_filters(...)' function define below.
Include = [tk.Comment, tk.Name] #Default values for inclusion filter
Exclude = [tk.Whitespace,tk.Punctuation,tk.Operator,tk.__builtins__,tk.Keyword] #Default value for exclusion filter

# Primary function to be used by main.py, Receives node array and returns Array of Arrays consisting of user defined tokens.
# Each sub array refers to Identifiers extracted from individual files
# eg. [
#      ["ExampleVariable","Account Balance","Suspicion Flag"]
#      ["IntegralDivisions,TestVarInt"]
#     ]


def code_preprocess(node_array: List[Node]):
    for node in node_array:
       code_tokens = []
       code_tokens.append(get_identifiers(node))


# Returns an array of Pygment token objects when provided with a filepath
# Uses filepath to identify language, returns None if language not supported.
def get_tokens(filepath:str):
    with open(filepath, "r", encoding="utf-8") as file:
        code_string =  file.read()
        #Try tp get appropriate lexer using the filepath and extension
        try:
            lexer = pygments.lexers.get_lexer_for_filename(filepath)
            return pygments.lex(code_string,lexer)
        #If Language not supported or, extension is invalid. Print error to console and Return None
        except pygments.util.ClassNotFound:
            print("Failed to identify Lexer! Language Not supported or Invalid file extension.\n")
            return None

def get_identifiers(node: Node):
    return None


def extract_identifiers(filepath : str):
    tokens = get_tokens(filepath)
    tokens = filter(filter_by_category(),tokens)

def filter_by_category(token: pygments.token):
    if(token[1] is TypeIn for TypeIn in Include):
        if(token[1] is not TypeEx for TypeEx in Exclude):
            return True
    else:
        return False


def set_filters(include: List[pygments.token], exclude: List[pygments.token]):
    Include = include
    Exclude = exclude
    return

def localtest(filepath):
    return None

localtest("testfile.cpp")