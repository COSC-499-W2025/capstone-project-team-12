import unittest
import os
from text_tokenizer import get_tokens, sw_filtered_tokens, lemmatize_tokens

class TestTextProcessor(unittest.TestCase):

    def setUp(self):
        self.filepath = os.path.join(
        os.path.dirname(__file__),
        "test_main_dir",
        "mock_texts",
        "text_prep_text.txt"
    )
        # create temporary mock files for edge cases
        self.empty_file = os.path.join(
            os.path.dirname(__file__),
            "test_main_dir",
            "mock_texts",
            "empty.txt"
        )
        open(self.empty_file, "w").close()

        self.stopword_file = os.path.join(
            os.path.dirname(__file__),
            "test_main_dir",
            "mock_texts",
            "only_stopwords.txt"
        )
        with open(self.stopword_file, "w") as f:
            f.write("the and if but or")

        self.punct_file = os.path.join(
            os.path.dirname(__file__),
            "test_main_dir",
            "mock_texts",
            "punct.txt"
        )
        with open(self.punct_file, "w") as f:
            f.write("...!!!???")

    def tearDown(self):
        # clean up temporary files
        for f in [self.empty_file, self.stopword_file, self.punct_file]:
            if os.path.exists(f):
                os.remove(f)

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

    def test_empty_file(self):
        lemma = lemmatize_tokens(self.empty_file) # empty file has no tokens/lemmatized words
        self.assertEqual(lemma, "")

    def test_only_stopwords(self):
        filtered = sw_filtered_tokens(self.stopword_file)
        self.assertEqual(filtered, []) # all stopwords should be filtered out so should be empty

    def test_punctuation_only(self):
        tokens = get_tokens(self.punct_file) # long string of punctuation marks should all be removed
        self.assertEqual(tokens, [])

    def test_keep_letter_accents(self): # keep accents on letters
        lemma = lemmatize_tokens(self.filepath)
        self.assertIn("résumé", lemma)


if __name__ == "__main__":
    unittest.main()
