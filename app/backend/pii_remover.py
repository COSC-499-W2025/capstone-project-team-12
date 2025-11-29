from presidio_anonymizer import AnonymizerEngine
from nltk.tokenize import word_tokenize
from typing import List
import re
import spacy
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import SpacyNlpEngine


def remove_pii (processed_docs: list[list[str]]) -> list[list[str]]:
    """ Takes a list of tokens lists (processed text and code documents) and removes PII using Presidio.
        Returns a list of tokens lists. Updated this to handle large documents by chunking them into manageable pieces. 
        This prevents errors when processing documents that exceed the default token limit.
    """
    MAX_CHARS = 200_000

    # load spaCy model
    nlp = spacy.load("en_core_web_sm")
    nlp.max_length = 2_500_000

    # wrap it for presidio
    nlp_engine = SpacyNlpEngine(models={"en": nlp})
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
    anonymizer = AnonymizerEngine()

    bag_of_words: list[list[str]] = []
    
    for tokens in processed_docs:
        text = " ".join(tokens) # join tokens as a single string since Presidio expects text input

        chunks = []
        for i in range(0, len(text), MAX_CHARS):
            chunks.append(text[i:i + MAX_CHARS])
        
        anonymized_tokens_total = []

        # Process each chunk independently
        for chunk in chunks:
            results = analyzer.analyze(text=chunk, language='en')

            anonymized = anonymizer.anonymize(
                text=chunk,
                analyzer_results=results
            )
        
            # remove any leftover tags from redaction (ie <EMAIL>, <PERSON>)
            clean_text = re.sub(r"<[^>]+>", "", anonymized.text)

            # convert anonymized text back to list of lists of tokens (this will be our BoW input for the ML model)
            anonymized_tokens = word_tokenize(clean_text.lower())

        bag_of_words.append(anonymized_tokens_total)

    return bag_of_words