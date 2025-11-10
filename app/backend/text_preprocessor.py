from typing import List,Tuple
import regex as re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk import word_tokenize, pos_tag
from anytree import Node
from main import get_bin_data_by_IdList
from typing import BinaryIO

stop_words: set[str] = None

def stopwords_init():
    global stop_words
    stop_words = set(stopwords.words('english'))
    return

def get_data(node_array:List[Node])->List[BinaryIO|None]:
    # Get all the file data needed from main
    text_data_list: List[str] = []
    bin_Idx_list: List[int] = []
    for node in node_array:
        bin_Id = node.file_data['binary_index']
        bin_Idx_list.append(bin_Id)
    text_data_list = [str(x) for x in get_bin_data_by_IdList(bin_Idx_list)]
    return text_data_list

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
    #declare output list
    preProcessed_doclist: List[List[str]] = []
    
    text_data_list = get_data(node_array)
    #print(node_array)
    #print(text_data_list)
    for i in range(len(node_array)):
        tokenarray: List[str]
        node = node_array[i]
        text = text_data_list[i]
        if text is not None: #If downstream error then will be none!
            tokenarray = get_tokens(text)
            tokenarray = stopword_filtered_tokens(tokenarray)
            tokenarray = lemmatize_tokens(tokenarray)
            preProcessed_doclist.append(tokenarray)
        else:
            print("Failed to process text file:" + str(node))
            continue
    return preProcessed_doclist

#reads file and gets token, currently from local dir
#TODO: rework to use binary array instead
def get_tokens(text:str) -> List[str]:
    
    clean_txt:str
    # cleaning whitespace and line breaks
    clean_txt = re.sub(r"\n", " ",text)
    clean_txt = re.sub(r"\s+", " ", clean_txt).strip()

    # removing non-alphabetic tokens
    # this can result in the loss of tokens that contain actual words, like in "2.Python"
    # here we replace all non-alphabetic characters with a single space, then remove all surrounding spaces
    reg_text: str
    reg_txt = re.sub(r"[^\p{L}\s]", " ", clean_txt)
    reg_txt = re.sub(r"\s+", " ", reg_txt).strip()
    reg_tokens: list[str] = word_tokenize(reg_txt)

    return reg_tokens

def stopword_filtered_tokens(tokens: List[str]) -> List[str]:
    try:
        # import tokens from text_tokenizer
        global stop_words
        
        #only init stopwords if it has not be initalized
        if stop_words is None:
            stopwords_init()
        
        # remove English stopwords
        filtered_tokens: list[str] = [word.lower() for word in tokens if word.lower() not in stop_words]
        #print(f"Stopword filtered tokens: {filtered_tokens}")
    except Exception as e:
        print(f"An error occurred in stopword_filtered_tokens: {e}")
        return []

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
       
def lemmatize_tokens(words:List[str]) -> List[str]:
    # assign label to each word (adjective, verb, etc)
    pos_tags: List[Tuple[str, str]] = pos_tag(words)

def lemmatize_tokens(node:Node) -> List[str]:
    try:
        words: List[str] = stopword_filtered_tokens(node)

        # assign label to each word (adjective, verb, etc)
        pos_tags: List[Tuple[str, str]] = pos_tag(words)

        # create instance of NTLK's lemmatizer, which converts words to their base lemma form, using dictionary knowledge
        lemmatizer: WordNetLemmatizer = WordNetLemmatizer()

        # lemmatize each word
        lemmatized_words: list[str] = [lemmatizer.lemmatize(word, get_wordnet_pos(tag)) for word, tag in pos_tags]

        return lemmatized_words
    except Exception as e: 
        print(f"An error occurred in lemmatize_tokens: {e}")
        return []


# If youre looking for the local test as there is comprehensive test in main testsuite under backend/tests_backend