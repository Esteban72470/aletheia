"""Aletheia CLI entry point."""

import click

from aletheia_cli.commands.parse_cmd import parse
from aletheia_cli.commands.preview_cmd import preview
from aletheia_cli.commands.extract_cmd import extract
from aletheia_cli.commands.serve_cmd import serve


@click.group()
@click.version_option(version="0.1.0", prog_name="aletheia")
@click.option("--config", "-c", type=click.Path(), help="Config file path")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def cli(ctx, config, verbose):
    """Aletheia - Document and image parser for AI agents."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["verbose"] = verbose


# Register commands
cli.add_command(parse)
cli.add_command(preview)
cli.add_command(extract)
cli.add_command(serve)


if __name__ == "__main__":
    cli()
