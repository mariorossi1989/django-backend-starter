"""Main CLI application for DevTools."""

import typer
from rich.console import Console
from rich.traceback import install

from devtools.commands.database import db_app

# Install rich traceback for better error display
install(show_locals=True)

# Initialize console
console = Console()

# Create main Typer app
app = typer.Typer(
    name="devtools",
    help="🛠️  Development and operations tools for the project",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Add database commands
app.add_typer(db_app, name="db", help="🗄️ Database management commands")


@app.callback()
def callback():
    """
    DevTools CLI - Manage database, cache, deployments and more.
    """
    pass


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        from devtools import __version__

        console.print(f"DevTools version: [bold cyan]{__version__}[/bold cyan]")
        raise typer.Exit()


@app.command()
def version(
    show: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """Show DevTools version."""
    pass


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
