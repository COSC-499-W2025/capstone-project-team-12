from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer.operators import OperatorsFactory

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
    anonymizer_config = {"DEFAULT": {"operator_name": "redact"}}

    # anonymize the text
    anonymized_response = anonymizer.anonymize(text=text,
                                            analyzer_results=results,
                                            anonymizer_config=anonymizer_config)

    # convert anonymized text back to list of lists of tokens (this will be our BoW input for the ML model)
    anonymized_tokens = word_tokenize(anonymized.text.lower())
    bag_of_words.append(anonymized_tokens)

    return bag_of_words