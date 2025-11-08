import hashlib
from cache.bow_cache import BoWCache, BoWCacheKey
from text_preprocessor import text_preprocess
from pii_remover import remove_pii


def get_or_build_bow(node_array: list) -> list[list[str]]:
    """
    Runs the full text preprocessing + PII removal pipeline, using the BoW cache to skip redundant work.
    Returns a list of lists of anonymized tokens ready for text analysis.
    """
    # with the current setup, we assume all text files use the same preprocessing steps
    preprocess_signature = {
        "lemmatizer": True,
        "stopwords": "nltk_english_default",
        "pii_removal": True,
        "filters": ["text"]
    }

    # build repo_id by hashing joined file paths
    file_paths = [getattr(node, "filepath", str(node.name)) for node in node_array]
    joined_paths = "|".join(file_paths)
    repo_id = hashlib.md5(joined_paths.encode()).hexdigest()

    # no git commit info for text files
    head_commit = None

    # initialize cache and key
    key = BoWCacheKey(repo_id, head_commit, preprocess_signature)
    cache = BoWCache()

    # check cache for existing BoW
    if cache.has(key):
        print(f"Cache hit for BoW (repo_id={repo_id})")
        cached = cache.get(key)
        if cached is not None:
            return cached
        print("Cache corrupted or unreadable - regenerating...")

    # if we reach here, we have a cache miss
    print("Cache miss - running text preprocessing + PII removal...")
    processed_docs = text_preprocess(node_array)
    anonymized_docs = remove_pii(processed_docs)

    # save to cache
    cache.set(key, anonymized_docs)
    print("Saved final BoW to cache")

    return anonymized_docs
