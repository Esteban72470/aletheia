"""CLI cache utilities."""

import hashlib
import json
from pathlib import Path
from typing import Any, Optional

from aletheia_cli.utils.config import get_config


class CLICache:
    """Local cache for CLI operations."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize CLI cache.

        Args:
            cache_dir: Cache directory path
        """
        config = get_config()
        cache_path = cache_dir or config.get("cache", {}).get("directory", "~/.cache/aletheia")
        self.cache_dir = Path(cache_path).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_key(self, file_path: Path) -> str:
        """Generate cache key from file path and content."""
        content = file_path.read_bytes()
        return hashlib.sha256(content).hexdigest()[:16]

    def get(self, file_path: Path) -> Optional[Any]:
        """
        Get cached result for a file.

        Args:
            file_path: Source file path

        Returns:
            Cached data or None
        """
        key = self._get_key(file_path)
        cache_file = self.cache_dir / f"{key}.json"

        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)

        return None

    def set(self, file_path: Path, data: Any) -> None:
        """
        Cache result for a file.

        Args:
            file_path: Source file path
            data: Data to cache
        """
        key = self._get_key(file_path)
        cache_file = self.cache_dir / f"{key}.json"

        with open(cache_file, "w") as f:
            json.dump(data, f)

    def clear(self) -> int:
        """
        Clear all cached data.

        Returns:
            Number of entries cleared
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        return count
