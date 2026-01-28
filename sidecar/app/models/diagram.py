"""Diagram data model."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .document import BoundingBox


class Node(BaseModel):
    """Node in a diagram graph."""

    id: str = Field(..., description="Unique node identifier")
    label: str = Field(..., description="Node label/text")
    shape: Optional[str] = Field(
        default=None,
        description="Node shape: rectangle, circle, diamond, oval, etc.",
    )
    bbox: Optional[BoundingBox] = Field(
        default=None, description="Bounding box in source image"
    )
    node_type: Optional[str] = Field(
        default=None,
        description="Semantic type: entity, process, decision, data, etc.",
    )
    properties: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional node properties"
    )


class Edge(BaseModel):
    """Edge connecting nodes in a diagram graph."""

    id: str = Field(..., description="Unique edge identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    label: Optional[str] = Field(default=None, description="Edge label")
    edge_type: Optional[str] = Field(
        default=None,
        description="Edge type: directed, bidirectional, association, etc.",
    )
    properties: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional edge properties"
    )


class DiagramGraph(BaseModel):
    """Diagram graph model for extracted diagrams."""

    diagram_id: str = Field(..., description="Unique diagram identifier")
    diagram_type: str = Field(
        ...,
        description="Diagram type: flowchart, sequence, architecture, er, class, network, etc.",
    )
    title: Optional[str] = Field(default=None, description="Diagram title")
    nodes: List[Node] = Field(
        default_factory=list, description="Nodes in the diagram"
    )
    edges: List[Edge] = Field(
        default_factory=list, description="Edges connecting nodes"
    )
    source_image: Optional[str] = Field(
        default=None, description="URI to source image"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in diagram extraction",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional diagram metadata"
    )
