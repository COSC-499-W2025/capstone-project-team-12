from presidio_anonymizer import AnonymizerEngine
from nltk.tokenize import word_tokenize
from typing import List
import re
from presidio_analyzer import AnalyzerEngine


def remove_pii(processed_docs: List[List[str]]) -> List[List[str]]:
    """ Takes a list of tokens lists (processed text and code documents) and removes PII using Presidio.
        Returns a list of tokens lists. Updated this to handle large documents by chunking them into manageable pieces. 
        This prevents errors when processing documents that exceed the default token limit.
    """
    MAX_CHARS = 200_000

    # Simple initialization like the working version - let Presidio handle the model loading
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()

    bag_of_words: List[List[str]] = []
    
    for tokens in processed_docs:
        text = " ".join(tokens)

        # Chunk the text to handle large documents
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

            # convert anonymized text back to list of tokens
            anonymized_tokens = word_tokenize(clean_text.lower())
            
            # Collect tokens from this chunk
            anonymized_tokens_total.extend(anonymized_tokens)

        # Append complete token list for this document
        bag_of_words.append(anonymized_tokens_total)

    return bag_of_words