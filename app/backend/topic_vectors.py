from gensim.corpora import Dictionary
from gensim.models import LdaModel

def generate_topic_vectors(documents: list[list[str]], num_topics: int = 5):
    if not documents:
        return None, [], [[] for _ in range(num_topics)]

    #build dictionary and corpus
    dictionary = Dictionary(documents)
    #what pii remover returns is a token list, so we have to convert it to a BOW (where each. vectors corresponds to the frequencey of the word in the doc)
    corpus = [dictionary.doc2bow(doc) for doc in documents]

    #train LDA model 
    lda_model = LdaModel(
        corpus = corpus,
        id2word = dictionary,
        num_topics = num_topics,
        random_state = 42 #seed value 
    )

    #dense topic vectors: basically topics per document
    doc_topic_vectors = [
        [prob for _, prob in lda_model.get_document_topics(doc_bow, minimum_probability=0)]
        for doc_bow in corpus
    ]

    #dense topic-term vectors: basically how many words per topic
    topic_term_vectors = []
    vocab_size = len(dictionary)

    #note: gensim returns a sparse list of (term_id, prob) pairs, which means not all the words from our dictionary will be in it since it removes the terms for which the probability is 0. So we initialize an array of vocab_size 0s for the probabilities, and then fill in the ones that gensim returns. This esnures that we still have vocab_size probabilities, even if some of them are 0.
    for topic_id in range(num_topics):

        #initially 0, will represent the probability that a word belongs to a certain topic
        term_probs = [0.0] * vocab_size

        #get the term_id - prob pairs from gensim
        for term_id, prob in lda_model.get_topic_terms(topic_id, topn=vocab_size):
            term_probs[term_id] = prob
        
        #add to output list 
        topic_term_vectors.append(term_probs)

    return lda_model, doc_topic_vectors, topic_term_vectors
    
  