"""Hashing utilities."""

import hashlib
from typing import Union


def compute_hash(content: Union[bytes, str], algorithm: str = "sha256") -> str:
    """
    Compute hash of content.

    Args:
        content: Content to hash
        algorithm: Hash algorithm (sha256, md5, etc.)

    Returns:
        Hex digest string
    """
    if isinstance(content, str):
        content = content.encode("utf-8")

    hasher = hashlib.new(algorithm)
    hasher.update(content)
    return hasher.hexdigest()


def compute_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    """
    Compute hash of a file.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm

    Returns:
        Hex digest string
    """
    hasher = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def short_hash(content: Union[bytes, str], length: int = 8) -> str:
    """
    Compute a short hash for identification.

    Args:
        content: Content to hash
        length: Length of short hash

    Returns:
        Short hash string
    """
    full_hash = compute_hash(content)
    return full_hash[:length]
