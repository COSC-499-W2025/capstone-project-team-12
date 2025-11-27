from typing import List,Tuple
import regex as re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk import word_tokenize, pos_tag
from anytree import Node
from typing import BinaryIO
from main import get_bin_data_by_Id

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
def text_preprocess(text_nodes: List[Node]) ->List[List[str]]:
    #declare output list
    preProcessed_doclist: List[List[str]] = []
    if text_nodes is None:
        raise ValueError("Text Proprocess error: No nodes given!")
        return
    
    for i in range(len(text_nodes)):
        
        #Temp array for storing text file currently being processed.
        token_array: List[str]
        
        cur_text_node: Node = text_nodes[i]
        cur_text_binId: int = cur_text_node.file_data['binary_index']
        cur_text_data: BinaryIO= str(get_bin_data_by_Id(cur_text_binId))
        try:
            if cur_text_data: #If downstream error then will be none!
                token_array = get_tokens(cur_text_data)
                token_array = stopword_filtered_tokens(token_array)
                token_array = lemmatize_tokens(token_array)
                preProcessed_doclist.append(token_array)
            else:
                raise RuntimeWarning("Failed to process text file, NO DATA! Skipping file:" + cur_text_node.file_data['filename'])
                continue
        except Exception as e:
            print("Unexpected runtime error in: Text_Preprocessor:{e}")
            continue
    return preProcessed_doclist


def get_tokens(filestring:str) -> List[str]:
    """ 
    Converts passed text file data string into List of preprocessed tokens

    Params: filestring = String of text file loaded as a string    
    Return: List[str]  = Contains preprocessed and filtered tokens generated from filestring
    """ 
    
    clean_txt:str
    #Replace Line breaks with one whitespace
    clean_txt = re.sub(r"\n", " ",filestring)
    #Replace multiple whitespaces or multiple line breaks with one whitespace
    clean_txt = re.sub(r"\s+", " ", clean_txt).strip()

    # removing tokens containing non-alphabetic characters and replacing with one whitespace
    # this can result in the loss of tokens that contain actual words, like in "2.Python"
    reg_txt: str
    reg_txt = re.sub(r"[^\p{L}\s]", " ", clean_txt)
    reg_txt = re.sub(r"\s+", " ", reg_txt).strip()
    
    #convert normalized filestring to token list using nltk
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
    try:
        # assign label to each word (adjective, verb, etc)
        pos_tags: List[Tuple[str, str]] = pos_tag(words)

        # create instance of NTLK's lemmatizer, which converts words to their base lemma form, using dictionary knowledge
        lemmatizer: WordNetLemmatizer = WordNetLemmatizer()

        # lemmatize each word
        lemmatized_words: list[str] = [lemmatizer.lemmatize(word, get_wordnet_pos(tag)) for word, tag in pos_tags]

        return lemmatized_words
    except Exception as e:
        raise RuntimeError(f"An error occurred in lemmatize_tokens: {e}")