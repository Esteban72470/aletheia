"""Preview command for visual output."""

import click
from pathlib import Path

from aletheia_cli.client.sidecar_client import SidecarClient


@click.command("preview")
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output file path",
)
@click.option(
    "--format", "-f",
    type=click.Choice(["html", "svg", "png"]),
    default="html",
    help="Preview format",
)
@click.option("--overlay/--no-overlay", default=True, help="Show bounding boxes")
@click.option("--open", "open_browser", is_flag=True, help="Open in browser")
@click.pass_context
def preview(ctx, file, output, format, overlay, open_browser):
    """Generate a visual preview of parsed output."""
    file_path = Path(file)

    if ctx.obj.get("verbose"):
        click.echo(f"Generating preview for: {file_path}")

    # Connect to sidecar
    client = SidecarClient()

    try:
        # Parse document first
        result = client.parse(file_path=file_path)

        # Generate preview
        preview_content = client.preview(
            document_id=result.get("document_id"),
            format=format,
            show_overlay=overlay,
        )

        # Output
        if output:
            output_path = Path(output)
            output_path.write_text(preview_content)
            click.echo(f"Preview saved to: {output_path}")

            if open_browser and format == "html":
                import webbrowser
                webbrowser.open(f"file://{output_path.absolute()}")
        else:
            click.echo(preview_content)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
