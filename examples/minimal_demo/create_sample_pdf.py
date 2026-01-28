#!/usr/bin/env python3
"""Generate sample PDF for minimal_demo testing.

This script creates a simple PDF file that can be used for testing
the Aletheia document parsing pipeline.

Usage:
    python create_sample_pdf.py
"""

from pathlib import Path

# Try to use reportlab if available, otherwise create minimal PDF manually
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch

    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


def create_pdf_with_reportlab(output_path: Path) -> None:
    """Create sample PDF using reportlab library."""
    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, height - 72, "Sample Document")

    # Body text
    c.setFont("Helvetica", 12)
    y_position = height - 120

    lines = [
        "This is a sample document for testing Aletheia's document parsing",
        "capabilities. It contains simple text content that should be",
        "extracted accurately.",
        "",
        "Key Features:",
        "- Text extraction from PDF files",
        "- Layout analysis and block detection",
        "- OCR support for scanned documents",
        "",
        "Invoice Details:",
        "Invoice #: INV-2024-001",
        "Date: 2024-01-15",
        "Amount: $1,234.56",
    ]

    for line in lines:
        c.drawString(72, y_position, line)
        y_position -= 18

    c.save()
    print(f"Created PDF with reportlab: {output_path}")


def create_minimal_pdf(output_path: Path) -> None:
    """Create a minimal valid PDF without external dependencies.

    This creates a basic PDF that is valid but has limited formatting.
    """
    # Minimal PDF structure
    content = """%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 283 >>
stream
BT
/F1 18 Tf
72 720 Td
(Sample Document) Tj
0 -30 Td
/F1 12 Tf
(This is a sample document for testing Aletheia's) Tj
0 -18 Td
(document parsing capabilities.) Tj
0 -30 Td
(Invoice #: INV-2024-001) Tj
0 -18 Td
(Date: 2024-01-15) Tj
0 -18 Td
(Amount: $1,234.56) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000264 00000 n
0000000598 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
677
%%EOF"""

    output_path.write_text(content)
    print(f"Created minimal PDF: {output_path}")


def main():
    """Generate sample PDF in the minimal_demo folder."""
    # Determine output path
    script_dir = Path(__file__).parent
    output_path = script_dir / "sample.pdf"

    # Create the PDF
    if HAS_REPORTLAB:
        create_pdf_with_reportlab(output_path)
    else:
        print("reportlab not installed, creating minimal PDF...")
        create_minimal_pdf(output_path)

    # Verify the file was created
    if output_path.exists():
        size = output_path.stat().st_size
        print(f"PDF created successfully: {size} bytes")
    else:
        print("ERROR: Failed to create PDF")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
