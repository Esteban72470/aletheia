"""Output formatting utilities."""

import json
from typing import Any


def format_output(data: Any, format: str = "json") -> str:
    """
    Format data for output.

    Args:
        data: Data to format
        format: Output format (json, markdown, text)

    Returns:
        Formatted string
    """
    if format == "json":
        return json.dumps(data, indent=2, default=str)

    elif format == "markdown":
        return _to_markdown(data)

    elif format == "text":
        return _to_text(data)

    elif format == "csv":
        return _to_csv(data)

    else:
        return str(data)


def _to_markdown(data: Any) -> str:
    """Convert data to Markdown format."""
    if isinstance(data, dict):
        lines = []

        if "pages" in data:
            lines.append(f"# Document: {data.get('document_id', 'Unknown')}\n")

            for page in data.get("pages", []):
                lines.append(f"## Page {page.get('page_number', '?')}\n")

                for block in page.get("blocks", []):
                    text = block.get("text", "")
                    block_type = block.get("type", "text")

                    if block_type == "heading":
                        lines.append(f"### {text}\n")
                    else:
                        lines.append(f"{text}\n")

        return "\n".join(lines)

    return str(data)


def _to_text(data: Any) -> str:
    """Convert data to plain text."""
    if isinstance(data, dict):
        if "pages" in data:
            text_parts = []
            for page in data.get("pages", []):
                for block in page.get("blocks", []):
                    text_parts.append(block.get("text", ""))
            return "\n\n".join(text_parts)

        return "\n".join(f"{k}: {v}" for k, v in data.items())

    return str(data)


def _to_csv(data: Any) -> str:
    """Convert data to CSV format."""
    if isinstance(data, dict) and "cells" in data:
        lines = []
        for row in data.get("cells", []):
            lines.append(",".join(f'"{cell}"' for cell in row))
        return "\n".join(lines)

    return str(data)
