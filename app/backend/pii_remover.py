from presidio_anonymizer import AnonymizerEngine
from nltk.tokenize import word_tokenize
from typing import List
import re
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngine, SpacyNlpEngine, NerModelConfiguration

def init_anonymizer():
     # Define which model to use
    model_config = [{"lang_code": "en", "model_name": "en_core_web_sm"}]

    # Define which entities the model returns and how they map to Presidio's
    entity_mapping = dict(
        PER="PERSON",
        LOC= "LOCATION",
        GPE="LOCATION",
        ORG="ORGANIZATION"
    )

    ner_model_configuration = NerModelConfiguration(default_score = 0.6, model_to_presidio_entity_mapping=entity_mapping)

    # Create the NLP Engine based on this configuration
    spacy_nlp_engine = SpacyNlpEngine(models= model_config, ner_model_configuration=ner_model_configuration)
    return spacy_nlp_engine

def remove_pii(processed_docs: List[List[str]]) -> List[List[str]]:
    """ Takes a list of tokens lists (processed text and code documents) and removes PII using Presidio.
        Returns a list of tokens lists. Updated this to handle large documents by chunking them into manageable pieces. 
        This prevents errors when processing documents that exceed the default token limit.
    """
    MAX_CHARS = 200_000

    spacy_nlp_engine = init_anonymizer()
    
    analyzer = AnalyzerEngine(nlp_engine=spacy_nlp_engine)
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