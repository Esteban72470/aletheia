"""Serve command to start the sidecar service."""

import click


@click.command("serve")
@click.option("--port", "-p", default=8420, help="Port number")
@click.option("--host", "-h", default="127.0.0.1", help="Host address")
@click.option("--workers", "-w", default=1, help="Number of workers")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
@click.pass_context
def serve(ctx, port, host, workers, reload):
    """Start the local sidecar service."""
    click.echo(f"Starting Aletheia sidecar on {host}:{port}")

    try:
        import uvicorn

        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            workers=workers if not reload else 1,
            reload=reload,
        )
    except ImportError:
        click.echo("Error: uvicorn not installed. Install with: pip install uvicorn", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error starting server: {e}", err=True)
        raise SystemExit(1)
