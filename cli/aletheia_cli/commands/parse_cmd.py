"""Parse command for document processing."""

import click
from pathlib import Path

from aletheia_cli.client.sidecar_client import SidecarClient
from aletheia_cli.utils.formatter import format_output


@click.command("parse")
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--output", "-o",
    type=click.Choice(["json", "markdown", "text"]),
    default="json",
    help="Output format",
)
@click.option("--pages", "-p", help="Page range (e.g., '1-5', '1,3,5')")
@click.option(
    "--ocr-engine",
    type=click.Choice(["tesseract", "trocr", "easyocr"]),
    default="tesseract",
    help="OCR engine to use",
)
@click.option("--layout/--no-layout", default=True, help="Enable layout detection")
@click.option("--tables/--no-tables", default=True, help="Extract tables")
@click.option("--cache/--no-cache", default=True, help="Use cached results")
@click.pass_context
def parse(ctx, file, output, pages, ocr_engine, layout, tables, cache):
    """Parse a document and output structured data."""
    file_path = Path(file)

    if ctx.obj.get("verbose"):
        click.echo(f"Parsing: {file_path}")
        click.echo(f"  OCR engine: {ocr_engine}")
        click.echo(f"  Layout detection: {layout}")
        click.echo(f"  Table extraction: {tables}")

    # Connect to sidecar
    client = SidecarClient()

    try:
        result = client.parse(
            file_path=file_path,
            pages=pages,
            ocr_engine=ocr_engine,
            extract_layout=layout,
            extract_tables=tables,
            use_cache=cache,
        )

        # Format and output
        formatted = format_output(result, output)
        click.echo(formatted)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
