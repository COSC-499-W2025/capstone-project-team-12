import pytest
import pickle
import hashlib
from pathlib import Path
from anytree import Node
from cache.bow_cache import BoWCache, BoWCacheKey, compute_cache_key


def test_compute_cache_key_stable():
    sig = {"lemmatizer": True, "stopwords": "nltk_english_default"}
    key1 = compute_cache_key("repo1", "abc123", sig)
    key2 = compute_cache_key("repo1", "abc123", dict(sig))  # identical copy
    assert key1 == key2

def test_cache_set_and_get(tmp_path):
    cache = BoWCache(cache_dir=tmp_path)
    key = BoWCacheKey("repo1", "commit1", {"version": "v1"})
    tokens = [["this", "is", "a", "test"]]

    # store
    cache.set(key, tokens)
    assert cache.has(key)

    # retrieve
    loaded = cache.get(key)
    assert loaded == tokens
    assert isinstance(loaded[0], list)

def test_cache_invalidate(tmp_path):
    cache = BoWCache(cache_dir=tmp_path)
    key = BoWCacheKey("repo2", "commit2", {"version": "v1"})
    tokens = [["invalidate", "me"]]

    cache.set(key, tokens)
    assert cache.has(key)
    cache.invalidate(key)
    assert not cache.has(key)

def test_cache_handles_corrupted_file(tmp_path):
    cache = BoWCache(cache_dir=tmp_path)
    key = BoWCacheKey("repo3", None, {"test": True})
    path = cache._path_for(key.to_hex())

    # manually create a corrupted pickle file
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"not a pickle")

    result = cache.get(key)
    assert result is None
    assert not path.exists()


def test_bow_cache_key_allows_missing_fields(tmp_path):
    """Ensure that BoWCacheKey works even if some parameters are None """
    key = BoWCacheKey(None, None, None)
    result = key.to_hex()
    assert isinstance(result, str)
    assert len(result) == 64  # MD5 hex length