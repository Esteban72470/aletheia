"""HTTP client for communicating with the Aletheia sidecar."""

from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from aletheia_cli.utils.config import get_config


class SidecarClient:
    """Client for the Aletheia sidecar service."""

    def __init__(self, host: str = None, port: int = None, timeout: float = 30.0):
        """
        Initialize the sidecar client.

        Args:
            host: Sidecar host (default from config)
            port: Sidecar port (default from config)
            timeout: Request timeout in seconds
        """
        config = get_config()
        self.host = host or config.get("sidecar", {}).get("host", "127.0.0.1")
        self.port = port or config.get("sidecar", {}).get("port", 8420)
        self.base_url = f"http://{self.host}:{self.port}"
        self.timeout = timeout

    def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the sidecar."""
        url = f"{self.base_url}{path}"

        with httpx.Client(timeout=self.timeout) as client:
            response = client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()

    def health(self) -> Dict[str, Any]:
        """Check sidecar health."""
        return self._request("GET", "/health")

    def parse(
        self,
        file_path: Path,
        pages: Optional[str] = None,
        ocr_engine: str = "tesseract",
        extract_layout: bool = True,
        extract_tables: bool = True,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Parse a document.

        Args:
            file_path: Path to document
            pages: Page range
            ocr_engine: OCR engine to use
            extract_layout: Enable layout detection
            extract_tables: Extract tables
            use_cache: Use cached results

        Returns:
            Parsed document data
        """
        options = {
            "pages": pages,
            "ocr_engine": ocr_engine,
            "extract_layout": extract_layout,
            "extract_tables": extract_tables,
        }

        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            data = {"options": str(options)}

            return self._request("POST", "/api/v1/parse", files=files, data=data)

    def query(
        self,
        document_id: str,
        query: str,
        page_range: Optional[tuple] = None,
    ) -> Dict[str, Any]:
        """
        Query a parsed document.

        Args:
            document_id: Document ID
            query: Query string
            page_range: Optional page range tuple

        Returns:
            Query results
        """
        payload = {
            "document_id": document_id,
            "query": query,
            "page_range": list(page_range) if page_range else None,
        }

        return self._request("POST", "/api/v1/query", json=payload)

    def preview(
        self,
        document_id: str,
        format: str = "html",
        show_overlay: bool = True,
    ) -> str:
        """
        Generate a preview of parsed document.

        Args:
            document_id: Document ID
            format: Output format ('html', 'json', 'text')
            show_overlay: Show bounding boxes in HTML preview

        Returns:
            Preview content
        """
        params = {
            "format": format,
            "overlay": str(show_overlay).lower(),
        }

        try:
            result = self._request(
                "GET",
                f"/api/v1/documents/{document_id}/preview",
                params=params
            )
            return result.get("content", "")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"<!-- Document {document_id} not found -->"
            raise
