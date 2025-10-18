import re
import spacy
from nltk.tokenize import word_tokenize, regexp_tokenize, sent_tokenize
nlp = spacy.load("en_core_web_sm")

def get_tokens(filepath):
# read and clean local text (with sithara's implementation can read file from file system)
    # file_path = "app/mock_data/example1.txt"
    file_path = filepath
    with open(file_path, "r", encoding="utf-8") as f:
        working_txt = f.read()

    # cleaning whitespace and line breaks
    clean_txt = re.sub(r"\n", " ", working_txt)
    clean_txt = re.sub(r"\s+", " ", clean_txt).strip()

    print("Cleaned text preview:\n", clean_txt[:200], "\n")

    tokens = word_tokenize(clean_txt)
    print("First 5 tokens: \n",tokens[:5],"\n")

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

if __name__ == "__main__":
    tokens = get_tokens("app/mock_data/example1.txt")
    print(tokens[:20])