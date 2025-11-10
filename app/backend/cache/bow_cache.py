from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
import hashlib, json, pickle, tempfile, os
from typing import List, Optional, Any

# default cache directory is "backend/cache/bow"
DEFAULT_CACHE_DIR = Path(os.environ.get("BOW_CACHE_DIR", "backend/cache/bow"))
DEFAULT_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _stable_json(obj: Any) -> str:
    """
     Produces a stable JSON representation of obj for hashing purposes
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def compute_cache_key(
    repo_id: Optional[str],
    head_commit: Optional[str],
    preprocess_signature: Optional[dict[str, Any]],
) -> str:
    """
    Computes a hash string the identifies a BoW cache entry. Missing values are allowed and are replaces with placeholder values to ensure consistent key format
    """
    repo_id = repo_id or "no_repo"
    head_commit = head_commit or "no_commit"
    preprocess_json = _stable_json(preprocess_signature or {})
    material = f"{repo_id}|{head_commit}|{preprocess_json}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BoWCacheKey:
    """
    Container for the cache identifiers:
    - repo_id: repository or file identifier
    - head_commit: git commit hash (if repo) or None (if single file)
    - preprocess_signature: dict describing preprocessing configuration (stopwords, filters, etc.)
    """
    repo_id: Optional[str]
    head_commit: Optional[str]
    preprocess_signature: Optional[dict[str, Any]]

    def to_hex(self) -> str:
        """Convert the three fields into a stable hex key."""
        return compute_cache_key(self.repo_id, self.head_commit, self.preprocess_signature)


class BoWCache:
    """
    Filesystem based cache for storing and retrieving BoW token lists. Each cache entry is a pickled file containing List[List[str]]:
    - Uses atomic writes
    - Organizes files into subdirectories based on first two hex chars of hash
    - Safe for concurrent reads
    """

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, key_hex: str) -> Path:
        """
        Compute the file path for a given cache key
        """
        return self.cache_dir / key_hex[:2] / f"{key_hex}.pkl"

    def has(self, key: BoWCacheKey) -> bool:
        """Return True if a cache entry exists for this key """
        return self._path_for(key.to_hex()).exists()

    def get(self, key: BoWCacheKey) -> Optional[List[List[str]]]:
        """
        Try to load cached token lists for the given key. Returns None on cache miss or if file is corrupted
        """
        path = self._path_for(key.to_hex())
        if not path.exists():
            return None
        try:
            with path.open("rb") as f:
                return pickle.load(f)
        except Exception:
            # On any error delete the cache entry and return None
            try:
                path.unlink()
            except Exception:
                pass
            return None

    def set(self, key: BoWCacheKey, bow: List[List[str]]) -> None:
        """
        Cache storage. Atomic write pattern:
          1. Write to temp file in same directory
          2. Rename temp file to final path 
        """
        path = self._path_for(key.to_hex())
        path.parent.mkdir(parents=True, exist_ok=True)

        fd, tmpname = tempfile.mkstemp(dir=str(path.parent), prefix="._bow_", suffix=".tmp")
        try:
            with os.fdopen(fd, "wb") as tmpf:
                pickle.dump(bow, tmpf, protocol=pickle.HIGHEST_PROTOCOL)
            os.replace(tmpname, path)  
        finally:
            # cleanup leftover temp file if something failed
            if os.path.exists(tmpname):
                try:
                    os.remove(tmpname)
                except Exception:
                    pass

    def invalidate(self, key: BoWCacheKey) -> None:
        """Remove the cached file for this key, if it exists"""
        path = self._path_for(key.to_hex())
        if path.exists():
            path.unlink()

