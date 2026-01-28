"""CLI configuration utilities."""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml


_config: Optional[Dict[str, Any]] = None

DEFAULT_CONFIG = {
    "sidecar": {
        "host": "127.0.0.1",
        "port": 8420,
        "timeout": 30,
    },
    "cache": {
        "enabled": True,
        "directory": "~/.cache/aletheia",
        "max_size_gb": 10,
    },
    "defaults": {
        "ocr_engine": "tesseract",
        "output_format": "json",
    },
}


def get_config_path() -> Path:
    """Get the configuration file path."""
    return Path.home() / ".config" / "aletheia" / "config.yaml"


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from file.

    Args:
        config_path: Optional custom config path

    Returns:
        Configuration dictionary
    """
    global _config

    path = config_path or get_config_path()

    if path.exists():
        with open(path) as f:
            _config = yaml.safe_load(f) or {}
    else:
        _config = {}

    # Merge with defaults
    return {**DEFAULT_CONFIG, **_config}


def get_config() -> Dict[str, Any]:
    """Get the current configuration."""
    global _config
    if _config is None:
        return load_config()
    return {**DEFAULT_CONFIG, **_config}


def save_config(config: Dict[str, Any], config_path: Optional[Path] = None) -> None:
    """
    Save configuration to file.

    Args:
        config: Configuration dictionary
        config_path: Optional custom config path
    """
    path = config_path or get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
