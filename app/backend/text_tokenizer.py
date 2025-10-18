import re
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk import word_tokenize, pos_tag

nlp = spacy.load("en_core_web_sm")

# --------------------------
# TOKENIZATION
# --------------------------
def get_tokens(filepath):
    
    # read and clean local text (with sithara's implementation can read file from file system)
    file_path = filepath
    with open(file_path, "r", encoding="utf-8") as f:
        working_txt = f.read()

    # cleaning whitespace and line breaks
    clean_txt = re.sub(r"\n", " ", working_txt)
    clean_txt = re.sub(r"\s+", " ", clean_txt).strip()

    print("Cleaned text preview:\n", clean_txt[:200], "\n")

    tokens = word_tokenize(clean_txt)
    print("First 5 tokens:\n", tokens[:5], "\n")

    # remove non-alphabetic tokens. this includes numbers, and punctuation such as ":" and "@"
    filtered_tokens_alpha = [word for word in tokens if word.isalpha()]
    print("Alphabetic tokens:\n", filtered_tokens_alpha, "\n")

    # filtered_tokens_alpha removes all tokens that contain non-alphabetic characters. This can result in loss of tokens that
    # contain actual words, such as "2.Python"
    # here we replace all non-alphabetic characters with a single space, then remove all surrounding spaces
    reg_txt = re.sub(r"[^a-zA-Z\s]", " ", clean_txt)
    reg_txt = re.sub(r"\s+", " ", reg_txt).strip()
    reg_tokens = word_tokenize(reg_txt)

    print("Regularized tokens:\n", reg_tokens, "\n")

    return reg_tokens

# --------------------------
# STOPWORD REMOVAL
# --------------------------
def sw_filtered_tokens(filepath):
    # import tokens from text_tokenizer
    tokens = get_tokens(filepath)

    # load stopwords
    stop_words = set(stopwords.words('english'))

    # remove English stopwords
    filtered_tokens = [word.lower() for word in tokens if word.lower() not in stop_words]
    print(f"Stopword filtered tokens: {filtered_tokens}")

    return filtered_tokens


# --------------------------
# LEMMATIZATION
# --------------------------

# we need to tell the lemmatizer what part of speech the word in question is: adjective, verb, etc
def get_wordnet_pos(tag):
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
       
def lemmatize_tokens(filepath):
    words = sw_filtered_tokens(filepath)

    # assign label to each word (adjective, verb, etc)
    pos_tags = pos_tag(words)

    # create instance of NTLK's lemmatizer, which converts words to their base lemma form, using dictionary knowledge
    lemmatizer = WordNetLemmatizer()

    # lemmatize each word
    lemmatized_words = [lemmatizer.lemmatize(word, get_wordnet_pos(tag)) for word, tag in pos_tags]

    # join into a single string
    lemmatized_sentence = ' '.join(lemmatized_words)
    print(f"\nLemmatized words: {lemmatized_sentence}")
    return lemmatized_sentence


# --------------------------
# RUN FILE
# --------------------------
if __name__ == "__main__":
    lemmatize_tokens("app/mock_data/example1.txt")
