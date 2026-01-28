#!/usr/bin/env python3
"""Download and cache ML models for Aletheia."""

import argparse
from pathlib import Path

# Model registry
MODELS = {
    "tesseract": {
        "type": "system",
        "description": "Tesseract OCR (install via apt/brew)",
    },
    "layoutparser": {
        "type": "detectron2",
        "url": "lp://PubLayNet/faster_rcnn/R_50_FPN_3x",
        "description": "Layout detection model",
    },
    "trocr-printed": {
        "type": "huggingface",
        "model_id": "microsoft/trocr-base-printed",
        "description": "TrOCR for printed text",
    },
    "layoutlmv3": {
        "type": "huggingface",
        "model_id": "microsoft/layoutlmv3-base",
        "description": "LayoutLMv3 for document understanding",
    },
}


def download_model(name: str, cache_dir: Path) -> bool:
    """Download a specific model."""
    if name not in MODELS:
        print(f"Unknown model: {name}")
        return False

    model_info = MODELS[name]
    print(f"Downloading {name}: {model_info['description']}")

    model_type = model_info['type']
    model_dir = cache_dir / name
    model_dir.mkdir(parents=True, exist_ok=True)

    if model_type == "system":
        # System-level dependency - provide instructions
        print(f"  -> System dependency - install manually:")
        if name == "tesseract":
            print("     Windows: choco install tesseract")
            print("     macOS:   brew install tesseract")
            print("     Ubuntu:  sudo apt install tesseract-ocr")
        return True

    elif model_type == "huggingface":
        # Download from HuggingFace Hub
        model_id = model_info.get("model_id", "")
        print(f"  -> Downloading from HuggingFace: {model_id}")
        try:
            from huggingface_hub import snapshot_download
            snapshot_download(
                repo_id=model_id,
                local_dir=model_dir,
                local_dir_use_symlinks=False,
            )
            print(f"  ✓ Downloaded to: {model_dir}")
            return True
        except ImportError:
            print("  -> huggingface_hub not installed. Run: pip install huggingface_hub")
            return False
        except Exception as e:
            print(f"  ✗ Download failed: {e}")
            return False

    elif model_type == "detectron2":
        # LayoutParser models via detectron2
        url = model_info.get("url", "")
        print(f"  -> LayoutParser model: {url}")
        print("  -> Note: Will be downloaded on first use")
        # Create a marker file
        marker = model_dir / "model_url.txt"
        marker.write_text(url)
        return True

    else:
        print(f"  -> Unknown model type: {model_type}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Download Aletheia ML models")
    parser.add_argument(
        "models",
        nargs="*",
        default=["all"],
        help="Models to download (default: all)",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path.home() / ".local" / "share" / "aletheia" / "models",
        help="Model cache directory",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available models",
    )

    args = parser.parse_args()

    if args.list:
        print("Available models:")
        for name, info in MODELS.items():
            print(f"  {name}: {info['description']}")
        return

    # Create cache directory
    args.cache_dir.mkdir(parents=True, exist_ok=True)

    # Download models
    models_to_download = list(MODELS.keys()) if "all" in args.models else args.models

    for model in models_to_download:
        download_model(model, args.cache_dir)


if __name__ == "__main__":
    main()
