"""Caching utilities for parsed documents."""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from app.config import settings


class Cache:
    """File-based cache for parsed documents."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize cache.

        Args:
            cache_dir: Cache directory path
        """
        self.cache_dir = cache_dir or settings.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=settings.cache_ttl_hours)

    def _get_cache_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{key}.json"

    def _hash_content(self, content: bytes) -> str:
        """Generate a cache key from content."""
        return hashlib.sha256(content).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if not settings.cache_enabled:
            return None

        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None

        try:
            with open(cache_path, "r") as f:
                data = json.load(f)

            # Check expiration
            cached_at = datetime.fromisoformat(data["cached_at"])
            if datetime.utcnow() - cached_at > self.ttl:
                cache_path.unlink()
                return None

            return data["value"]
        except (json.JSONDecodeError, KeyError):
            return None

    def set(self, key: str, value: Any) -> None:
        """
        Store a value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        if not settings.cache_enabled:
            return

        cache_path = self._get_cache_path(key)
        data = {
            "value": value,
            "cached_at": datetime.utcnow().isoformat(),
        }

        with open(cache_path, "w") as f:
            json.dump(data, f)

    def delete(self, key: str) -> bool:
        """
        Delete a cache entry.

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
            return True
        return False

    def clear(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries cleared
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        return count

    def get_or_compute(
        self,
        content: bytes,
        compute_fn,
    ) -> Any:
        """
        Get from cache or compute and store.

        Args:
            content: Content bytes for key generation
            compute_fn: Function to compute value if not cached

        Returns:
            Cached or computed value
        """
        key = self._hash_content(content)
        cached = self.get(key)

        if cached is not None:
            return cached

        value = compute_fn()
        self.set(key, value)
        return value
