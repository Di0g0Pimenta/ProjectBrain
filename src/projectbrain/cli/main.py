import typer

from projectbrain.core.constants import APP_NAME, APP_VERSION
from projectbrain.services.project_initializer import ProjectInitializer

app = typer.Typer(
    help="ProjectBrain - Persistent memory for software projects.",
)


@app.command()
def version() -> None:
    """Show the application version."""
    typer.echo(f"{APP_NAME} {APP_VERSION}")


@app.command()
def init() -> None:
    """Initialize ProjectBrain in the current project."""

    initializer = ProjectInitializer()

    root = initializer.initialize()

    typer.secho(
        f"Project initialized at: {root}",
        fg=typer.colors.GREEN,
    )