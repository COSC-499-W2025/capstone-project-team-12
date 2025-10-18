import unittest
from app.backend.text_tokenizer import get_tokens, sw_filtered_tokens, lemmatize_tokens

class TestTextProcessor(unittest.TestCase):

    def setUp(self):
        self.filepath = "app/mock_data/example1.txt"

    def test_get_tokens(self):
        tokens = get_tokens(self.filepath)
        # ensure it returns a list of strings
        self.assertIsInstance(tokens, list)
        self.assertTrue(all(isinstance(tok, str) for tok in tokens))
        # ensure common words are tokenized
        self.assertIn("Python", tokens)

    def test_stopword_filtering(self):
        filtered = sw_filtered_tokens(self.filepath)
        self.assertTrue(all(word.isalpha() for word in filtered))
        self.assertNotIn("the", filtered)  # "the" is a stopword and should be removed

    def test_lemmatization(self):
        lemma_sentence = lemmatize_tokens(self.filepath)
        self.assertIsInstance(lemma_sentence, str)
        # ensure known lemmas appear
        self.assertIn("use", lemma_sentence) 
        self.assertNotIn("used", lemma_sentence)

if __name__ == "__main__":
    unittest.main()
