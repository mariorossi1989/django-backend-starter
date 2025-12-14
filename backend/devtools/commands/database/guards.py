"""Security guards for database operations based on environment.

Prevents dangerous operations in production environments unless explicitly
allowed with safety flags.
"""

import typer
from rich.console import Console
from rich.panel import Panel

from config.settings.schemas import config_registry as config
from config.settings.schemas.environment import EnvStateEnum

console = Console()


class ProductionGuardError(Exception):
    """Raised when a dangerous operation is attempted in production."""

    pass


def is_production() -> bool:
    """Check if running in production environment.

    Returns:
        True if current environment is production, False otherwise.
    """
    return config.env_state == EnvStateEnum.PRODUCTION


def require_non_production(
    operation_name: str,
    allow_in_production: bool = False,
) -> None:
    """Guard against dangerous operations in production.

    Args:
        operation_name: Name of the operation being attempted.
        allow_in_production: If True, allows operation despite production env.

    Raises:
        typer.Exit: If operation is not allowed in production.
    """
    if is_production() and not allow_in_production:
        console.print()
        console.print(
            Panel(
                f"[bold red]⚠️  OPERATION BLOCKED[/bold red]\n\n"
                f"Operation '[cyan]{operation_name}[/cyan]' is not allowed in "
                f"[bold red]PRODUCTION[/bold red] environment.\n\n"
                f"This is a safety measure to prevent accidental data loss.\n\n"
                f"[yellow]To override this protection:[/yellow]\n"
                f"  • Use the [cyan]--allow-in-production[/cyan] flag\n"
                f"  • Switch to development: [cyan]ENV_STATE=development[/cyan]",
                title="🛡️  Production Safety Guard",
                border_style="red",
            )
        )
        console.print()
        raise typer.Exit(code=1)


def warn_destructive_operation(
    operation_name: str,
    target: str,
) -> None:
    """Display warning for destructive operations.

    Args:
        operation_name: Name of the destructive operation.
        target: What is being affected (database name, user, etc.).
    """
    env_badge = (
        "[bold red]PRODUCTION[/bold red]"
        if is_production()
        else "[bold yellow]DEVELOPMENT[/bold yellow]"
    )

    console.print()
    console.print(
        Panel(
            f"[bold red]⚠️  DESTRUCTIVE OPERATION WARNING[/bold red]\n\n"
            f"Environment: {env_badge}\n"
            f"Operation: [cyan]{operation_name}[/cyan]\n"
            f"Target: [yellow]{target}[/yellow]\n\n"
            f"[bold]This action cannot be undone![/bold]",
            title="⚠️  Warning",
            border_style="red" if is_production() else "yellow",
        )
    )
    console.print()


def require_explicit_confirmation(
    item_name: str,
    item_value: str,
    force: bool = False,
) -> None:
    """Require user to type exact value to confirm dangerous operation.

    Args:
        item_name: Name of the item (e.g., "database", "user").
        item_value: The exact value user must type.
        force: If True, skips confirmation.

    Raises:
        typer.Exit: If confirmation fails or user cancels.
    """
    if force:
        return

    from rich.prompt import Prompt

    typed_value = Prompt.ask(
        f"Type the {item_name} name '[yellow]{item_value}[/yellow]' to confirm"
    )

    if typed_value != item_value:
        console.print(f"[red]✗ {item_name.capitalize()} name mismatch. Aborted.[/red]")
        raise typer.Exit(code=0)
