"""Database connection and configuration utilities."""

import psycopg
from rich.console import Console
from rich.table import Table

from config.settings.schemas import config_registry as config
from config.settings.schemas.database import BaseDatabaseConfig

console = Console()
db_configs = config.database


def get_db_config(alias: str = "default") -> BaseDatabaseConfig:
    """Get database configuration for a specific alias.

    Args:
        alias: Database alias (default: "default")

    Returns:
        Database configuration for the specified alias

    Raises:
        KeyError: If alias is not found in configurations
    """
    if alias not in db_configs:
        available = ", ".join(db_configs.keys())
        raise KeyError(
            f"Database alias '{alias}' not found. Available aliases: {available}"
        )
    return db_configs[alias]


def get_all_db_aliases() -> list[str]:
    """Get list of all configured database aliases."""
    return list(db_configs.keys())


def show_db_info(alias: str = "default") -> None:
    """Display database configuration in a formatted table.

    Args:
        alias: Database alias to display (default: "default")
    """
    db_config = get_db_config(alias)
    table = Table(title=f"Database Configuration [{alias}]", show_header=False)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="yellow")

    table.add_row("Alias", alias)
    table.add_row("Engine", str(db_config.engine))
    table.add_row("Name", db_config.name)
    table.add_row("User", db_config.user)
    table.add_row("Host", db_config.host)
    table.add_row("Port", str(db_config.port))

    console.print(table)


def show_all_db_info() -> None:
    """Display all database configurations."""
    aliases = get_all_db_aliases()
    console.print(f"[cyan]Found {len(aliases)} database(s) configured[/cyan]\n")

    for i, alias in enumerate(aliases):
        show_db_info(alias)
        if i < len(aliases) - 1:
            console.print()


def connect_to_postgres(
    dbname: str | None = None,
    alias: str = "default",
) -> psycopg.Connection:
    """Create connection to PostgreSQL database.

    Args:
        dbname: Database name to connect to. If None, uses configured database.
        alias: Database alias to use for connection parameters.

    Returns:
        Active PostgreSQL connection with autocommit enabled.
    """
    db_config = get_db_config(alias)
    return psycopg.connect(
        host=db_config.host,
        port=db_config.port,
        user=db_config.user,
        password=db_config.password.get_secret_value(),
        dbname=dbname or db_config.name,
        autocommit=True,
    )


def connect_with_admin_credentials(
    admin_user: str,
    admin_password: str,
    dbname: str = "postgres",
    alias: str = "default",
) -> psycopg.Connection:
    """Create connection using admin credentials.

    Args:
        admin_user: PostgreSQL admin username.
        admin_password: PostgreSQL admin password.
        dbname: Database to connect to (default: postgres).
        alias: Database alias to use for connection parameters.

    Returns:
        Active PostgreSQL connection with autocommit enabled.
    """
    db_config = get_db_config(alias)
    return psycopg.connect(
        host=db_config.host,
        port=db_config.port,
        user=admin_user,
        password=admin_password,
        dbname=dbname,
        autocommit=True,
    )


def prompt_admin_credentials() -> tuple[str, str]:
    """Prompt user for PostgreSQL admin credentials.

    Returns:
        Tuple of (admin_username, admin_password).

    Raises:
        typer.Exit: If password is not provided.
    """
    import typer
    from rich.prompt import Prompt

    console.print("[yellow]PostgreSQL admin credentials required:[/yellow]")
    admin_user = Prompt.ask("Admin username", default="postgres")
    admin_password = Prompt.ask("Admin password", password=True)

    if not admin_password:
        console.print("[red]✗ Admin password is required[/red]")
        raise typer.Exit(code=1)

    return admin_user, admin_password
