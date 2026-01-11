from gensim.corpora import Dictionary
from gensim.models import LdaModel
import math

def generate_topic_vectors(documents: list[list[str]], num_topics: int | None = None):
    if documents is None:
        raise TypeError("Documents must be a list.")

    if not isinstance(documents, list):
        raise TypeError("Documents must be a list of lists.")

    if any(not isinstance(doc, list) for doc in documents):
        raise TypeError("Each document must be a list of tokens.")

    # filter empty token lists
    documents = [doc for doc in documents if doc]
    if not documents:
        # if user passed num_topics, respect it for shape
        if num_topics is not None:
            if num_topics <= 0:
                raise ValueError("num_topics must be greater than 0")
            return None, None, [], [[] for _ in range(num_topics)]
        return None, None, [], []

    num_docs = len(documents)

    # Choose num_topics
    if num_topics is not None:
        if not isinstance(num_topics, int) or num_topics <= 0:
            raise ValueError("num_topics must be a positive integer")
    else:
        num_topics = max(1, int(math.sqrt(num_docs)))
        num_topics = min(num_topics, num_docs)


    # build dictionary and corpus
    dictionary = Dictionary(documents)
    corpus = [dictionary.doc2bow(doc) for doc in documents]

    try:
        lda_model = LdaModel(
            corpus=corpus,
            id2word=dictionary,
            num_topics=num_topics,
            random_state=42,
            passes=10,
            alpha=0.1,
            eta=0.01
        )

    actual_topics = lda_model.num_topics


    except Exception as e:
        raise RuntimeError(f"LDA training failed: {e}")

    # dense topic vectors: topics per document (force fixed size)
    doc_topic_vectors = []
    for doc_bow in corpus:
        topic_probs = [0.0] * num_topics
        for topic_id, prob in lda_model.get_document_topics(doc_bow, minimum_probability=0):
            if topic_id < num_topics:
                topic_probs[topic_id] = float(prob)
        # normalize (sometimes gensim collapses mass into 1 topic)
        s = sum(topic_probs)
        if s > 0:
            topic_probs = [p / s for p in topic_probs]
        doc_topic_vectors.append(topic_probs)


    # dense topic-term vectors
    topic_term_vectors = []
    vocab_size = len(dictionary)

    for topic_id in range(num_topics):
        term_probs = [0.0] * vocab_size
        if topic_id < actual_topics:
            for term_id, prob in lda_model.get_topic_terms(topic_id, topn=vocab_size):
                term_probs[term_id] = float(prob)
        topic_term_vectors.append(term_probs)


    return lda_model, dictionary, doc_topic_vectors, topic_term_vectors
