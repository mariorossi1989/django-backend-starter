"""Core database operations: create, drop, and reset database."""

import sys

import psycopg
from psycopg import errors
import typer
from rich.panel import Panel
from rich.prompt import Confirm

from devtools.commands.database.connection import (
    connect_to_postgres,
    console,
    get_all_db_aliases,
    get_db_config,
    show_all_db_info,
    show_db_info,
)
from devtools.commands.database.guards import (
    require_explicit_confirmation,
    require_non_production,
    warn_destructive_operation,
)


def create_database(alias: str = "default", all_dbs: bool = False) -> None:
    """Create PostgreSQL database using configuration settings.

    Args:
        alias: Database alias to operate on (default: "default")
        all_dbs: If True, operate on all configured databases
    """
    if all_dbs:
        aliases = get_all_db_aliases()
        console.print(f"[cyan]Creating {len(aliases)} database(s)...[/cyan]\n")
        for db_alias in aliases:
            try:
                _create_single_database(db_alias)
                console.print()
            except typer.Exit:
                continue
        return

    _create_single_database(alias)


def _create_single_database(alias: str) -> None:
    """Create a single PostgreSQL database.

    Args:
        alias: Database alias to create
    """
    try:
        db_config = get_db_config(alias)
        db_name = db_config.name
        db_user = db_config.user

        show_db_info(alias)
        console.print()

        with (
            console.status("[bold green]Connecting to PostgreSQL..."),
            connect_to_postgres(dbname="postgres", alias=alias) as conn,
            conn.cursor() as cursor,
        ):
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            db_exists = cursor.fetchone() is not None

            if db_exists:
                console.print(
                    f"[red]✗[/red] Database '{db_name}' already exists.",
                    style="bold red",
                )
                console.print(
                    "\nUse [cyan]devtools db drop[/cyan] first to drop it, "
                    "or [cyan]devtools db reset[/cyan] to drop and recreate."
                )
                raise typer.Exit(code=1)

            # Create database
            console.print(f"[yellow]Creating database '{db_name}'...[/yellow]")
            cursor.execute(f'CREATE DATABASE "{db_name}" OWNER "{db_user}"')  # type: ignore

            # Verify creation
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if not cursor.fetchone():
                console.print(
                    "[red]✗[/red] Failed to verify database creation",
                    style="bold red",
                )
                raise typer.Exit(code=1)

            console.print()
            console.print(
                Panel(
                    f"[green]✓[/green] Database '{db_name}' created successfully!",
                    title="Success",
                    border_style="green",
                )
            )
            console.print("\n[bold]Next steps:[/bold]")
            console.print("  1. Run migrations: [cyan]python manage.py migrate[/cyan]")
            console.print(
                "  2. Create superuser: [cyan]python manage.py createsuperuser[/cyan]"
            )

    except KeyboardInterrupt:
        console.print("\n[red]✗ Operation cancelled by user.[/red]")
    except psycopg.OperationalError as e:
        console.print(f"[red]✗ Connection failed:[/red] {e}", style="bold red")
        console.print("\n[yellow]Please verify:[/yellow]")
        console.print("  - PostgreSQL server is running")
        console.print(f"  - Host '{db_config.host}' is accessible")
        console.print(f"  - Port {db_config.port} is correct")
        console.print(f"  - User '{db_config.user}' credentials are correct")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]✗ Unexpected error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1) from None


def drop_database(
    force: bool = False,
    allow_in_production: bool = False,
    alias: str = "default",
    all_dbs: bool = False,
) -> None:
    """Drop PostgreSQL database using configuration settings.

    Args:
        alias: Database alias to operate on (default: "default")
        all_dbs: If True, operate on all configured databases
    Args:
        force: Skip confirmation prompts.
        allow_in_production: Allow operation in production environment.
    """
    require_non_production("drop database", allow_in_production)

    if all_dbs:
        aliases = get_all_db_aliases()
        console.print(f"[cyan]Dropping {len(aliases)} database(s)...[/cyan]\n")
        for db_alias in aliases:
            try:
                _drop_single_database(db_alias, force, allow_in_production)
                console.print()
            except typer.Exit:
                continue
        return

    _drop_single_database(alias, force, allow_in_production)


def _drop_single_database(
    alias: str,
    force: bool,
    allow_in_production: bool,
) -> None:
    """Drop a single PostgreSQL database.

    Args:
        alias: Database alias to drop
        force: Skip confirmation prompts
        allow_in_production: Allow operation in production environment
    """
    try:
        db_config = get_db_config(alias)
        db_name = db_config.name

        show_db_info(alias)
        console.print()

        warn_destructive_operation("DROP DATABASE", db_name)

        # Confirm drop unless --force
        if not force:
            require_explicit_confirmation("database", db_name, force)

            if not Confirm.ask("Are you absolutely sure?", default=False):
                console.print("[yellow]Operation cancelled.[/yellow]")
                raise typer.Exit(code=0)

        with (
            console.status("[bold yellow]Connecting to PostgreSQL..."),
            connect_to_postgres(dbname="postgres", alias=alias) as conn,
            conn.cursor() as cursor,
        ):
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            db_exists = cursor.fetchone() is not None

            if not db_exists:
                console.print(
                    f"[yellow]Database '{db_name}' does not exist. "
                    f"Nothing to drop.[/yellow]"
                )
                raise typer.Exit(code=0)

            # Drop database with FORCE option (PostgreSQL 13+)
            # This automatically terminates all connections including superuser
            console.print(f"[yellow]Dropping database '{db_name}'...[/yellow]")
            try:
                cursor.execute(f'DROP DATABASE "{db_name}" WITH (FORCE)')  # type: ignore
            except errors.SyntaxError:
                # Fallback for PostgreSQL < 13: try manual termination
                console.print(
                    "[yellow]Note: Using fallback connection termination "
                    "(PostgreSQL < 13)[/yellow]"
                )
                cursor.execute(
                    """
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = %s
                      AND pid <> pg_backend_pid()
                    """,
                    (db_name,),
                )
                cursor.execute(f'DROP DATABASE "{db_name}"')  # type: ignore

            # Verify deletion
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if cursor.fetchone():
                console.print(
                    "[red]✗ Failed to verify database deletion[/red]",
                    style="bold red",
                )
                raise typer.Exit(code=1)

            console.print()
            console.print(
                Panel(
                    f"[green]✓[/green] Database '{db_name}' dropped successfully!",
                    title="Success",
                    border_style="green",
                )
            )

    except KeyboardInterrupt:
        console.print("\n[red]✗ Operation cancelled by user.[/red]")
        raise typer.Exit(code=1) from None
    except psycopg.OperationalError as e:
        console.print(f"[red]✗ Connection failed:[/red] {e}", style="bold red")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]✗ Unexpected error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1) from None


def reset_database(
    force: bool = False,
    no_migrate: bool = False,
    allow_in_production: bool = False,
    alias: str = "default",
    all_dbs: bool = False,
) -> None:
    """Reset database: drop, create, and optionally run migrations.

    Args:
        force: Skip confirmation prompts.
        no_migrate: Skip running Django migrations after reset.
        allow_in_production: Allow operation in production environment.
        alias: Database alias to operate on (default: "default")
        all_dbs: If True, operate on all configured databases
    """
    require_non_production("reset database", allow_in_production)

    if all_dbs:
        aliases = get_all_db_aliases()
        console.print(f"[cyan]Resetting {len(aliases)} database(s)...[/cyan]\n")
        for db_alias in aliases:
            try:
                _reset_single_database(db_alias, force, no_migrate, allow_in_production)
                console.print()
            except typer.Exit:
                continue
        return

    _reset_single_database(alias, force, no_migrate, allow_in_production)


def _reset_single_database(
    alias: str,
    force: bool,
    no_migrate: bool,
    allow_in_production: bool,
) -> None:
    """Reset a single PostgreSQL database.

    Args:
        alias: Database alias to reset
        force: Skip confirmation prompts
        no_migrate: Skip running Django migrations after reset
        allow_in_production: Allow operation in production environment
    """
    try:
        db_config = get_db_config(alias)
        db_name = db_config.name
        db_user = db_config.user

        console.print(
            Panel(
                f"[bold cyan]DATABASE RESET [{alias}][/bold cyan]",
                border_style="cyan",
                expand=False,
            )
        )
        console.print()

        show_db_info(alias)
        console.print()

        warn_destructive_operation("RESET DATABASE", db_name)

        # Confirm reset unless --force
        if not force:
            require_explicit_confirmation("database", db_name, force)

            if not Confirm.ask("Are you absolutely sure?", default=False):
                console.print("[yellow]Operation cancelled.[/yellow]")
                raise typer.Exit(code=0)

        console.print()
        console.rule("[cyan]Starting Reset Process[/cyan]")
        console.print()

        with (
            connect_to_postgres(dbname="postgres", alias=alias) as conn,
            conn.cursor() as cursor,
        ):
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            db_exists = cursor.fetchone() is not None

            # Step 1: Drop if exists
            if db_exists:
                console.print("[yellow]Step 1/3:[/yellow] Dropping database...")
                try:
                    # Use FORCE option (PostgreSQL 13+) to terminate all connections
                    cursor.execute(f'DROP DATABASE "{db_name}" WITH (FORCE)')  # type: ignore
                except errors.SyntaxError:
                    # Fallback for PostgreSQL < 13
                    cursor.execute(
                        """
                        SELECT pg_terminate_backend(pg_stat_activity.pid)
                        FROM pg_stat_activity
                        WHERE pg_stat_activity.datname = %s
                          AND pid <> pg_backend_pid()
                        """,
                        (db_name,),
                    )
                    cursor.execute(f'DROP DATABASE "{db_name}"')  # type: ignore
                console.print(f"  [green]✓[/green] Database '{db_name}' dropped")
            else:
                console.print(
                    f"[yellow]Step 1/3:[/yellow] Database '{db_name}' "
                    f"does not exist, skipping drop"
                )

            console.print()

            # Step 2: Create database
            console.print("[yellow]Step 2/3:[/yellow] Creating database...")
            cursor.execute(f'CREATE DATABASE "{db_name}" OWNER "{db_user}"')  # type: ignore
            console.print(f"  [green]✓[/green] Database '{db_name}' created")
            console.print()

        # Step 3: Run migrations
        if not no_migrate:
            console.print("[yellow]Step 3/3:[/yellow] Running migrations...")
            import subprocess  # noqa: S404
            from pathlib import Path

            manage_py = Path(__file__).parents[3] / "manage.py"
            result = subprocess.run(  # noqa: S603
                [sys.executable, str(manage_py), "migrate", "--no-input"],
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
            if result.returncode == 0:
                console.print("  [green]✓[/green] Migrations completed")
            else:
                console.print(
                    f"  [red]✗[/red] Migrations failed:\n{result.stderr}",
                    style="bold red",
                )
                raise typer.Exit(code=1)
        else:
            console.print(
                "[yellow]Step 3/3:[/yellow] Skipping migrations (--no-migrate)"
            )

        console.print()
        console.print(
            Panel(
                "[green]✓[/green] Database reset completed successfully!",
                title="Success",
                border_style="green",
            )
        )
        console.print("\n[bold]Next steps:[/bold]")
        if no_migrate:
            console.print("  1. Run migrations: [cyan]python manage.py migrate[/cyan]")
            console.print(
                "  2. Create superuser: [cyan]python manage.py createsuperuser[/cyan]"
            )
        else:
            console.print(
                "  1. Create superuser: [cyan]python manage.py createsuperuser[/cyan]"
            )

    except KeyboardInterrupt:
        console.print("\n[red]✗ Operation cancelled by user.[/red]")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]✗ Unexpected error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1) from None
