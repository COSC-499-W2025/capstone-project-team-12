from gensim.corpora import Dictionary
from gensim.models import LdaModel

def generate_topic_vectors(documents: list[list[str]], num_topics: int = 5):
    if documents is None:
        raise TypeError("Documents must be a list.")

    if not documents:
        return None, None, [], [[] for _ in range(num_topics)]

    #ensure all docs are lists
    if any(not isinstance(doc, list) for doc in documents):
        raise TypeError("Each document must be a list of tokens.")

    #filter empty token lists
    documents = [doc for doc in documents if doc]
    if not documents:
        return None, None, [], [[] for _ in range(num_topics)]

    if num_topics <= 0:
        raise ValueError("num_topics must be greater than 0")

    #build dictionary and corpus
    dictionary = Dictionary(documents)
    corpus = [dictionary.doc2bow(doc) for doc in documents]

    try: 
        lda_model = LdaModel(
            corpus=corpus,
            id2word=dictionary,
            num_topics=num_topics,
            random_state=42  #seed value 
        )
    except Exception as e:
        raise RuntimeError(f"LDA training failed: {e}")

    #dense topic vectors: topics per document (probabilities)
    doc_topic_vectors = [
        [float(prob) for _, prob in lda_model.get_document_topics(doc_bow, minimum_probability=0)]
        for doc_bow in corpus
    ]

    #dense topic-term vectors: term probabilities per topic
    topic_term_vectors = []
    vocab_size = len(dictionary)
    for topic_id in range(num_topics):
        term_probs = [0.0] * vocab_size
        for term_id, prob in lda_model.get_topic_terms(topic_id, topn=vocab_size):
            term_probs[term_id] = float(prob)
        topic_term_vectors.append(term_probs)

    # Return dictionary too so callers can map term IDs back to words
    return lda_model, dictionary, doc_topic_vectors, topic_term_vectors

