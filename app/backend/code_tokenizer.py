import nltk
import re
import spacy
from nltk.tokenize import word_tokenize, regexp_tokenize, sent_tokenize
nlp = spacy.load("en_core_web_sm")

# read and clean local text (with sithara's implementation can read file from file system)
file_path = "app/mock_data/example1.txt"
with open(file_path, "r", encoding="utf-8") as f:
    working_txt = f.read()

# cleaning whitespace and line breaks
clean_txt = re.sub(r"\n", " ", working_txt)
clean_txt = re.sub(r"\s+", " ", clean_txt).strip()

print("Cleaned text preview:\n", clean_txt[:200], "\n")

tokens = word_tokenize(clean_txt)
print("First 5 tokens: \n",tokens[:5],"\n")