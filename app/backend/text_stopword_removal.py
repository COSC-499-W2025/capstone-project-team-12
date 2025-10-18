from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from text_tokenizer import get_tokens

# import tokens from text_tokenizer
tokens = get_tokens("app/mock_data/example1.txt")

# load stopwords
stop_words = set(stopwords.words('english'))

# remove English stopwords
sw_filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
print(f"Stopword filtered tokens: {sw_filtered_tokens}")