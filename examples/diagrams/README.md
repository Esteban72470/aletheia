# Diagram Examples

This directory contains sample diagrams for testing Aletheia's diagram parsing capabilities.

## Files

- `flowchart.png` - Process flowchart
- `architecture.png` - System architecture diagram
- `sequence.png` - Sequence diagram
- `er_diagram.png` - Entity-relationship diagram
- `class_diagram.png` - UML class diagram

## Expected Extraction

Aletheia should extract:
- Nodes (boxes, circles, entities)
- Edges (arrows, connections)
- Labels and text
- Relationships between elements
- Diagram type classification

## Diagram Graph Output

```json
{
  "type": "flowchart",
  "nodes": [
    {"id": "1", "label": "Start", "shape": "oval"},
    {"id": "2", "label": "Process", "shape": "rectangle"},
    {"id": "3", "label": "Decision", "shape": "diamond"}
  ],
  "edges": [
    {"from": "1", "to": "2", "label": ""},
    {"from": "2", "to": "3", "label": "check"}
  ]
}
```

## Testing

```bash
aletheia parse diagrams/flowchart.png --output flowchart_result.json
aletheia parse diagrams/architecture.png --query "describe the system components"
```
