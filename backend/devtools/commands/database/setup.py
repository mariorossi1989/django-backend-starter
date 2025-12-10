"""Complete database setup workflow."""

import sys

import typer
from psycopg import errors
from rich.panel import Panel
from rich.prompt import Confirm

from devtools.commands.database.connection import (
    connect_with_admin_credentials,
    console,
    get_all_db_aliases,
    get_db_config,
    prompt_admin_credentials,
    show_db_info,
)
from devtools.commands.database.guards import (
    require_non_production,
    warn_destructive_operation,
)


def setup(
    superuser: bool = False,
    reset: bool = False,
    no_migrate: bool = False,
    force: bool = False,
    allow_in_production: bool = False,
    alias: str = "default",
    all_dbs: bool = False,
) -> None:
    """Complete database setup: create user, database, and run migrations.

    Args:
        superuser: Create user with SUPERUSER privileges.
        reset: Drop existing user and database before recreating.
        no_migrate: Skip running Django migrations.
        force: Skip confirmation prompts.
        allow_in_production: Allow operation in production environment.
        alias: Database alias to operate on (default: "default")
        all_dbs: If True, operate on all configured databases
    """
    # Block superuser and reset in production
    if superuser and not allow_in_production:
        require_non_production("create superuser", allow_in_production)

    if reset and not allow_in_production:
        require_non_production("reset setup", allow_in_production)

    if all_dbs:
        aliases = get_all_db_aliases()
        console.print(f"[cyan]Setting up {len(aliases)} database(s)...[/cyan]\n")
        for db_alias in aliases:
            try:
                _setup_single_database(
                    db_alias, superuser, reset, no_migrate, force, allow_in_production
                )
                console.print()
            except typer.Exit:
                continue
        return

    _setup_single_database(
        alias, superuser, reset, no_migrate, force, allow_in_production
    )


def _setup_single_database(
    alias: str,
    superuser: bool,
    reset: bool,
    no_migrate: bool,
    force: bool,
    allow_in_production: bool,
) -> None:
    """Set up a single PostgreSQL database.

    Args:
        alias: Database alias
        superuser: Create user with SUPERUSER privileges
        reset: Drop existing user and database before recreating
        no_migrate: Skip running Django migrations
        force: Skip confirmation prompts
        allow_in_production: Allow operation in production environment
    """
    try:
        db_config = get_db_config(alias)
        db_name = db_config.name
        db_user = db_config.user
        db_password = db_config.password.get_secret_value()

        console.print(
            Panel(
                f"[bold cyan]DATABASE SETUP [{alias}][/bold cyan]",
                border_style="cyan",
                expand=False,
            )
        )
        console.print()

        show_db_info(alias)
        console.print()

        if not force:
            console.print(
                "This will create PostgreSQL user and database using config settings."
            )
            if reset:
                warn_destructive_operation("RESET SETUP", f"{db_user} and {db_name}")
            if superuser:
                console.print(
                    "[yellow]⚠️  User will be created with SUPERUSER privileges[/yellow]"
                )
            console.print()

            if not Confirm.ask("Continue?", default=True):
                console.print("[yellow]Operation cancelled.[/yellow]")
                raise typer.Exit(code=0)

        admin_user, admin_password = prompt_admin_credentials()

        console.print()
        console.rule("[cyan]Setup Process[/cyan]")
        console.print()

        with (
            connect_with_admin_credentials(
                admin_user, admin_password, alias=alias
            ) as conn,
            conn.cursor() as cursor,
        ):
            # Check existing
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (db_user,))
            user_exists = cursor.fetchone() is not None

            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            db_exists = cursor.fetchone() is not None

            step = 1
            total = 4 if not no_migrate else 3

            # Step 1: Drop database first (if reset and exists)
            if db_exists and reset:
                console.print(
                    f"[yellow]Step {step}/{total}:[/yellow] Dropping database..."
                )
                try:
                    # Use FORCE option (PostgreSQL 13+) to terminate all connections
                    cursor.execute(f'DROP DATABASE "{db_name}" WITH (FORCE)')  # type: ignore
                except errors.SyntaxError:
                    # Fallback for PostgreSQL < 13
                    cursor.execute(
                        """
                        SELECT pg_terminate_backend(pg_stat_activity.pid)
                        FROM pg_stat_activity
                        WHERE pg_stat_activity.datname = %s AND pid <> pg_backend_pid()
                        """,
                        (db_name,),
                    )
                    cursor.execute(f'DROP DATABASE "{db_name}"')  # type: ignore
                console.print("  [green]✓[/green] Database dropped")
                db_exists = False

            # Step 2: Drop user (if reset and exists, now that DB is gone)
            if user_exists and reset:
                console.print(f"[yellow]Step {step}/{total}:[/yellow] Dropping user...")
                cursor.execute(
                    """
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.usename = %s AND pid <> pg_backend_pid()
                    """,
                    (db_user,),
                )
                cursor.execute(f'DROP USER "{db_user}"')  # type: ignore
                console.print("  [green]✓[/green] User dropped")
                user_exists = False

            # Step 3: Create user
            if not user_exists:
                console.print(f"[yellow]Step {step}/{total}:[/yellow] Creating user...")
                if superuser:
                    stmt = (
                        f"CREATE USER \"{db_user}\" WITH PASSWORD '{db_password}' "
                        f"SUPERUSER CREATEDB CREATEROLE LOGIN"
                    )
                else:
                    stmt = (
                        f"CREATE USER \"{db_user}\" WITH PASSWORD '{db_password}' "
                        f"CREATEDB LOGIN"
                    )
                cursor.execute(stmt)  # type: ignore
                console.print("  [green]✓[/green] User created")
            else:
                console.print(
                    f"[yellow]Step {step}/{total}:[/yellow] User exists, skipping"
                )

            step += 1
            console.print()

            # Step 4: Create database
            if not db_exists:
                console.print(
                    f"[yellow]Step {step}/{total}:[/yellow] Creating database..."
                )
                cursor.execute(f'CREATE DATABASE "{db_name}" OWNER "{db_user}"')  # type: ignore
                console.print("  [green]✓[/green] Database created")
            elif not reset:
                console.print(
                    "[red]✗ Database exists. Use --reset to drop and recreate.[/red]"
                )
                raise typer.Exit(code=1)

            step += 1
            console.print()

            # Step 5: Privileges
            console.print(
                f"[yellow]Step {step}/{total}:[/yellow] Granting privileges..."
            )
            cursor.execute(
                f'GRANT ALL PRIVILEGES ON DATABASE "{db_name}" TO "{db_user}"'  # type: ignore
            )
            console.print("  [green]✓[/green] Privileges granted")

            step += 1
            console.print()

        # Step 6: Migrations
        if not no_migrate:
            console.print(
                f"[yellow]Step {step}/{total}:[/yellow] Running migrations..."
            )
            import subprocess  # noqa: S404
            from pathlib import Path

            manage_py = Path(__file__).parents[3] / "manage.py"
            result = subprocess.run(  # noqa: S603
                [
                    sys.executable,
                    str(manage_py),
                    "migrate",
                    "--database",
                    alias,
                    "--no-input",
                ],
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )

            if result.returncode == 0:
                console.print("  [green]✓[/green] Migrations completed")
            else:
                console.print("  [red]✗[/red] Migrations failed")
                if result.stderr:
                    console.print(f"[red]{result.stderr}[/red]")
                raise typer.Exit(code=1)
        else:
            console.print(f"[yellow]Step {step}/{total}:[/yellow] Skipping migrations")

        console.print()
        console.print(
            Panel(
                "[green]✓[/green] Database setup completed successfully!",
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
        console.print(f"[red]✗ Error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1) from None
