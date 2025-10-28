from typing import List,Tuple
import regex as re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk import word_tokenize, pos_tag
from anytree import Node
from gensim.utils import simple_preprocess

stop_words: set[str] = None 

def stopwords_init():
    global stop_words
    stop_words = set(stopwords.words('english'))
    return

# Primary function for external use of module. 
# Each sub array refers to tokens extracted from individual text files
# eg. [
#      ["capy","bring","happy","toy"]           --> Corresponds to one txt file
#      ["Smith" "common" "lastname" "bear"]     --> Corresponds to another txt file
#     ]
# Note should only be called on array of text files, i.e Should not be called on array of codefile nodes
# Instead call `codepreprocess_entrypoint(...)` and add the results pf both functions together
# Before forwarding PII removal and eventually to analysis step
def text_preprocess(node_array:List[Node]) ->List[List[str]]:
    preProcessed_doclist: List[List[str]] = []
    for node in node_array:
        tokenarray: List[str] = lemmatize_tokens(node)
        if tokenarray is not None: #If downstream error then will be none!
            preProcessed_doclist.append(tokenarray)
        else:
            print("Failed to process text file:" + str(node))
            continue
    return preProcessed_doclist

#reads file and gets token, currently from local dir
#TODO: rework to use binary array instead
def get_tokens(node:Node) -> list[str]:
    
    # read and clean local text (with sithara's implementation can read file from file system)
    file_path: str = node.filepath
    with open(file_path, "r", encoding="utf-8") as f:
        working_txt: str = f.read()

    # cleaning whitespace and line breaks
    clean_txt: str = re.sub(r"\n", " ", working_txt)
    clean_txt: str = re.sub(r"\s+", " ", clean_txt).strip()

    #print("\nCleaned text preview:\n", clean_txt[:200], "\n")

    # removing non-alphabetic tokens
    # this can result in the loss of tokens that contain actual words, like in "2.Python"
    # here we replace all non-alphabetic characters with a single space, then remove all surrounding spaces

    reg_txt: str = re.sub(r"[^\p{L}\s]", " ", clean_txt)
    reg_txt: str = re.sub(r"\s+", " ", reg_txt).strip()
    reg_tokens: list[str] = word_tokenize(reg_txt)

    #print("Regularized tokens:\n", reg_tokens, "\n")

    return reg_tokens

def stopword_filtered_tokens(node: Node) -> list[str]:
    # import tokens from text_tokenizer
    tokens: list[str] = get_tokens(node)
    global stop_words
    
    #only init stopwords if it has not be initalized
    if stop_words is None:
        stopwords_init()
    
    # remove English stopwords
    filtered_tokens: list[str] = [word.lower() for word in tokens if word.lower() not in stop_words]
    #print(f"Stopword filtered tokens: {filtered_tokens}")

    return filtered_tokens


# --------------------------
# LEMMATIZATION
# --------------------------

# we need to tell the lemmatizer what part of speech the word in question is: adjective, verb, etc
def get_wordnet_pos(tag: str) -> str:
    if tag.startswith('J'):
        return wordnet.ADJ  # adjective
    elif tag.startswith('V'):
        return wordnet.VERB # verb
    elif tag.startswith('N'):
        return wordnet.NOUN # noun
    elif tag.startswith('R'):
        return wordnet.ADV  # adverb
    else:         
        return wordnet.NOUN # default to noun
       
def lemmatize_tokens(node:Node) -> List[str]:
    
    words: List[str] = stopword_filtered_tokens(node)

    # assign label to each word (adjective, verb, etc)
    pos_tags: List[Tuple[str, str]] = pos_tag(words)

    # create instance of NTLK's lemmatizer, which converts words to their base lemma form, using dictionary knowledge
    lemmatizer: WordNetLemmatizer = WordNetLemmatizer()

    # lemmatize each word
    lemmatized_words: list[str] = [lemmatizer.lemmatize(word, get_wordnet_pos(tag)) for word, tag in pos_tags]

    return lemmatized_words


# --------------------------
# RUN FILE
# --------------------------
def print_output(output):
    for result in output:
        print(str(result)+'\n')
    return

def localtest(filepaths:List[str]):
    nodelist: List[Node] = []
    i = 0
    #Test Identifier Extraction:
    for filepath in filepaths:
        testNode: Node = Node("testingNode {} ".format(i))
        testNode.filepath = str(filepath)
        nodelist.append(testNode)
        
    #Test output 
    output = list(text_preprocess(nodelist))    
    print("\n----RESULT----\n")
    print_output(output)

if __name__ == "__main__":
    pathlist: List[str] = []
    pathlist.append("tests_backend/test_main_dir/textProcessor_testfile1.txt")
    pathlist.append("tests_backend/test_main_dir/textProcessor_testfile2.txt")
    localtest(pathlist)
