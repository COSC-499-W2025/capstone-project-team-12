import numpy as np
from topic_vectors import generate_topic_vectors


def test_basic_topic_vector_shapes():
    docs = [
        ["apple", "banana", "apple"],
        ["banana", "carrot", "banana"],
        ["apple", "carrot", "durian"]
    ]

    lda, dictionary, doc_vectors, topic_vectors = generate_topic_vectors(docs, num_topics=2)

    assert len(doc_vectors) == len(docs)

    for vec in doc_vectors:
        assert len(vec) == 2
        assert all(0 <= p <= 1 for p in vec)
        assert abs(sum(vec) - 1.0) < 1e-6

    assert len(topic_vectors) == 2

    unique_tokens = set(token for doc in docs for token in doc)
    vocab_size = len(unique_tokens)

    for vec in topic_vectors:
        assert len(vec) == vocab_size
        assert all(0 <= p <= 1 for p in vec)


def test_consistent_output_across_runs():
    docs = [
        ["dog", "cat", "mouse"],
        ["dog", "dog", "cat"],
    ]

    lda1, dict1, doc_vecs1, topic_vecs1 = generate_topic_vectors(docs, num_topics=2)
    lda2, dict2, doc_vecs2, topic_vecs2 = generate_topic_vectors(docs, num_topics=2)

    for v1, v2 in zip(doc_vecs1, doc_vecs2):
        assert np.allclose(v1, v2)

    for t1, t2 in zip(topic_vecs1, topic_vecs2):
        assert np.allclose(t1, t2)


def test_empty_documents_list():
    lda, dictionary, doc_vecs, topic_vecs = generate_topic_vectors([], num_topics=2)

    assert lda is None
    assert dictionary is None
    assert doc_vecs == []
    assert topic_vecs == [[], []]  # two topics → two empty term vectors


def test_single_word_documents():
    docs = [["hello"], ["hello"], ["hello"]]

    lda, dictionary, doc_vecs, topic_vecs = generate_topic_vectors(docs, num_topics=2)

    # Document-topic vectors valid
    for vec in doc_vecs:
        assert len(vec) == 2
        assert abs(sum(vec) - 1.0) < 1e-6

    # vocab size = 1
    for tvec in topic_vecs:
        assert len(tvec) == 1
        assert all(0 <= p <= 1 for p in tvec)


def test_topic_term_vectors_match_vocab_size():
    docs = [
        ["red", "blue"],
        ["blue", "green"],
        ["red", "green", "green"],
    ]

    lda, dictionary, doc_vecs, topic_vecs = generate_topic_vectors(docs, num_topics=3)

    unique_tokens = set(token for doc in docs for token in doc)
    vocab_size = len(unique_tokens)

    for vec in topic_vecs:
        assert len(vec) == vocab_size


def test_invalid_document_structure():
    bad_inputs = [
        "not a list",
        [123, 456],
        [["valid"], "oops"],
        None,
    ]

    for bad in bad_inputs:
        try:
            generate_topic_vectors(bad, num_topics=2)
        except Exception as e:
            assert isinstance(e, (TypeError, ValueError))
        else:
            assert False, f"Expected an exception for input: {bad}"


def test_documents_with_empty_token_lists():
    docs = [[], ["hello"], []]

    lda_model, dictionary, doc_vecs, topic_vecs = generate_topic_vectors(docs, num_topics=2)

    assert len(doc_vecs) == 1
    assert len(doc_vecs[0]) == 2
    assert abs(sum(doc_vecs[0]) - 1.0) < 1e-6

    # only "hello" in vocab → vocab size 1
    for vec in topic_vecs:
        assert len(vec) == 1


def test_all_documents_empty():
    docs = [[], [], []]

    lda, dictionary, doc_vecs, topic_vecs = generate_topic_vectors(docs, num_topics=3)

    assert lda is None
    assert dictionary is None
    assert doc_vecs == []
    assert len(topic_vecs) == 3
    assert all(vec == [] for vec in topic_vecs)


def test_invalid_num_topics():
    docs = [["apple", "banana"]]

    for bad_topics in [0, -1, -5]:
        try:
            generate_topic_vectors(docs, num_topics=bad_topics)
        except Exception as e:
            assert isinstance(e, ValueError)
        else:
            assert False, f"Expected ValueError for num_topics={bad_topics}"
