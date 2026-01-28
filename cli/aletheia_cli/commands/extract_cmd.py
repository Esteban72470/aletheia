"""Extract command for specific element extraction."""

import click
from pathlib import Path

from aletheia_cli.client.sidecar_client import SidecarClient
from aletheia_cli.utils.formatter import format_output


@click.command("extract")
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--type", "-t",
    type=click.Choice(["tables", "figures", "text", "all"]),
    default="all",
    help="Element type to extract",
)
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.option(
    "--format", "-f",
    type=click.Choice(["json", "csv", "markdown"]),
    default="json",
    help="Output format",
)
@click.pass_context
def extract(ctx, file, type, output, format):
    """Extract specific elements from documents."""
    file_path = Path(file)

    if ctx.obj.get("verbose"):
        click.echo(f"Extracting from: {file_path}")
        click.echo(f"  Type: {type}")

    # Connect to sidecar
    client = SidecarClient()

    try:
        # Parse document
        result = client.parse(file_path=file_path)

        # Extract requested elements
        elements = []
        if type in ("tables", "all"):
            for page in result.get("pages", []):
                elements.extend(page.get("tables", []))

        if type in ("figures", "all"):
            for page in result.get("pages", []):
                elements.extend(page.get("figures", []))

        if type in ("text", "all"):
            for page in result.get("pages", []):
                elements.extend(page.get("blocks", []))

        # Output
        if output:
            output_dir = Path(output)
            output_dir.mkdir(parents=True, exist_ok=True)

            for i, element in enumerate(elements):
                element_file = output_dir / f"{type}_{i}.{format}"
                element_file.write_text(format_output(element, format))

            click.echo(f"Extracted {len(elements)} elements to: {output_dir}")
        else:
            formatted = format_output({"elements": elements}, format)
            click.echo(formatted)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
