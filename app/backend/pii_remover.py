from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from nltk.tokenize import word_tokenize
from typing import List
from anytree import Node
from text_preprocessor import text_preprocess
import re

def remove_pii (processed_docs: list[list[str]]) -> list[list[str]]:
    """ Takes a list of tokens lists (processed text and code documents) and removes PII using Presidio.
        Returns a list of tokens lists.
    """
    # initialize the analyzer & anonymizer
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()
    bag_of_words: list[list[str]] = []
    
    for tokens in processed_docs:
        text = " ".join(tokens) # join tokens as a single string since Presidio expects text input

        # analyze text for PII
        results = analyzer.analyze(text=text, language='en')

        # redact all detected entities
        operators = {"DEFAULT": {"operator_name": "redact"}}

        # anonymize the text
        anonymized_response = anonymizer.anonymize(text=text,
                                                analyzer_results=results)
        
        # remove any leftover tags from redaction (ie <EMAIL>, <PERSON>)
        clean_text = re.sub(r"<[^>]+>", "", anonymized_response.text)

        # convert anonymized text back to list of lists of tokens (this will be our BoW input for the ML model)
        anonymized_tokens = word_tokenize(clean_text.lower())
        bag_of_words.append(anonymized_tokens)

    return bag_of_words


if __name__ == "__main__": # testing locally to show it works. unit tests to come. 
    nodes = []
    for i, path in enumerate([
        "tests_backend/test_main_dir/textProcessor_testfile1.txt",
        "tests_backend/test_main_dir/textProcessor_testfile2.txt",
        "tests_backend/test_main_dir/pii_text.txt"
    ]):
        node = Node(f"doc{i}") # creating dummy list of nodes with filepaths
        node.filepath = path
        nodes.append(node)

    # running text_preprocess() for stopword removal and lemmatization
    processed_docs = text_preprocess(nodes)

    print("\n--- Preprocessed Token Lists ---")
    for doc in processed_docs:
        print(doc)

    # remove PII
    anonymized_docs = remove_pii(processed_docs)

    print("\n--- After PII Removal ---")
    for doc in anonymized_docs:
        print(doc)