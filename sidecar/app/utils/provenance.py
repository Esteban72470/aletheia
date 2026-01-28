"""Provenance tracking utilities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class ExtractionRecord:
    """Record of a single extraction."""

    extraction_id: str
    type: str
    value: Any
    confidence: float
    page: Optional[int] = None
    bbox: Optional[List[float]] = None
    model: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StageRecord:
    """Record of a pipeline stage execution."""

    name: str
    model: Optional[str] = None
    version: Optional[str] = None
    duration_ms: int = 0
    inputs: int = 0
    outputs: int = 0


class ProvenanceTracker:
    """Track extraction provenance for traceability."""

    def __init__(self, document_id: str, source_hash: str):
        """
        Initialize provenance tracker.

        Args:
            document_id: Document identifier
            source_hash: Hash of source document
        """
        self.provenance_id = str(uuid4())
        self.document_id = document_id
        self.source_hash = source_hash
        self.extractions: List[ExtractionRecord] = []
        self.stages: List[StageRecord] = []
        self.started_at = datetime.utcnow()

    def add_extraction(
        self,
        type: str,
        value: Any,
        confidence: float,
        page: Optional[int] = None,
        bbox: Optional[List[float]] = None,
        model: Optional[str] = None,
    ) -> str:
        """
        Record an extraction.

        Args:
            type: Extraction type (text, table, figure, etc.)
            value: Extracted value
            confidence: Confidence score
            page: Page number
            bbox: Bounding box
            model: Model used

        Returns:
            Extraction ID
        """
        extraction_id = str(uuid4())[:8]
        record = ExtractionRecord(
            extraction_id=extraction_id,
            type=type,
            value=value,
            confidence=confidence,
            page=page,
            bbox=bbox,
            model=model,
        )
        self.extractions.append(record)
        return extraction_id

    def add_stage(
        self,
        name: str,
        duration_ms: int,
        model: Optional[str] = None,
        version: Optional[str] = None,
        inputs: int = 0,
        outputs: int = 0,
    ):
        """
        Record a pipeline stage.

        Args:
            name: Stage name
            duration_ms: Duration in milliseconds
            model: Model used
            version: Model version
            inputs: Number of inputs
            outputs: Number of outputs
        """
        record = StageRecord(
            name=name,
            model=model,
            version=version,
            duration_ms=duration_ms,
            inputs=inputs,
            outputs=outputs,
        )
        self.stages.append(record)

    def to_dict(self) -> Dict[str, Any]:
        """
        Export provenance as dictionary.

        Returns:
            Provenance data
        """
        total_duration = sum(s.duration_ms for s in self.stages)

        return {
            "provenance_id": self.provenance_id,
            "source": {
                "document_id": self.document_id,
                "hash": self.source_hash,
                "accessed_at": self.started_at.isoformat(),
            },
            "extractions": [
                {
                    "extraction_id": e.extraction_id,
                    "type": e.type,
                    "confidence": e.confidence,
                    "location": {"page": e.page, "bbox": e.bbox},
                    "model": e.model,
                    "timestamp": e.timestamp.isoformat(),
                }
                for e in self.extractions
            ],
            "pipeline": {
                "stages": [
                    {
                        "name": s.name,
                        "model": s.model,
                        "version": s.version,
                        "duration_ms": s.duration_ms,
                    }
                    for s in self.stages
                ],
                "total_duration_ms": total_duration,
            },
        }
