"""PostgreSQL user management commands."""

import typer
from rich.panel import Panel
from rich.table import Table

from devtools.commands.database.connection import (
    connect_with_admin_credentials,
    console,
    get_all_db_aliases,
    get_db_config,
    prompt_admin_credentials,
)
from devtools.commands.database.guards import (
    is_production,
    require_explicit_confirmation,
    require_non_production,
    warn_destructive_operation,
)


def create_user(
    superuser: bool = False,
    drop: bool = False,
    force: bool = False,
    allow_in_production: bool = False,
    alias: str = "default",
    all_dbs: bool = False,
) -> None:
    """Create PostgreSQL user using configuration settings.

    Args:
        superuser: Create user with SUPERUSER privileges.
        drop: Drop user if it already exists before creating.
        force: Skip confirmation prompts.
        allow_in_production: Allow superuser creation in production.
        alias: Database alias to operate on (default: "default")
        all_dbs: If True, operate on all configured databases
    """
    # Block superuser creation in production
    if superuser and not allow_in_production:
        require_non_production("create superuser", allow_in_production)

    if all_dbs:
        aliases = get_all_db_aliases()
        console.print(
            f"[cyan]Creating user(s) for {len(aliases)} database(s)...[/cyan]\n"
        )
        for db_alias in aliases:
            try:
                _create_single_user(
                    db_alias, superuser, drop, force, allow_in_production
                )
                console.print()
            except typer.Exit:
                continue
        return

    _create_single_user(alias, superuser, drop, force, allow_in_production)


def _create_single_user(
    alias: str,
    superuser: bool,
    drop: bool,
    force: bool,
    allow_in_production: bool,
) -> None:
    """Create a PostgreSQL user for a single database.

    Args:
        alias: Database alias
        superuser: Create user with SUPERUSER privileges
        drop: Drop user if it already exists before creating
        force: Skip confirmation prompts
        allow_in_production: Allow superuser creation in production
    """
    try:
        db_config = get_db_config(alias)
        db_user = db_config.user
        db_password = db_config.password.get_secret_value()
        db_host = db_config.host
        db_port = db_config.port

        table = Table(title=f"User Configuration [{alias}]", show_header=False)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="yellow")
        table.add_row("Alias", alias)
        table.add_row("User", db_user)
        table.add_row("Host", db_host)
        table.add_row("Port", str(db_port))

        # Show warning if creating superuser
        if superuser:
            privileges_text = "[bold red]SUPERUSER[/bold red]"
            if is_production():
                console.print()
                console.print(
                    Panel(
                        "[bold yellow]⚠️  Creating SUPERUSER in PRODUCTION"
                        "[/bold yellow]\n\n"
                        "This user will have unrestricted access to ALL databases.",
                        title="Security Warning",
                        border_style="yellow",
                    )
                )
                console.print()
        else:
            privileges_text = "CREATEDB"

        table.add_row("Privileges", privileges_text)
        console.print(table)
        console.print()

        admin_user, admin_password = prompt_admin_credentials()

        if not force:
            from rich.prompt import Confirm

            if not Confirm.ask(f"Create PostgreSQL user '{db_user}'?", default=True):
                console.print("[yellow]Operation cancelled.[/yellow]")
                raise typer.Exit(code=0)

        with (
            console.status("[bold green]Connecting to PostgreSQL..."),
            connect_with_admin_credentials(
                admin_user, admin_password, alias=alias
            ) as conn,
            conn.cursor() as cursor,
        ):
            # Check if user exists
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (db_user,))
            user_exists = cursor.fetchone() is not None

            if user_exists and drop:
                # Require explicit confirmation for drop
                require_non_production("drop user", allow_in_production)
                warn_destructive_operation("DROP USER", db_user)
                require_explicit_confirmation("user", db_user, force)

                console.print(
                    f"[yellow]Terminating connections from '{db_user}'...[/yellow]"
                )
                cursor.execute(
                    """
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.usename = %s
                      AND pid <> pg_backend_pid()
                    """,
                    (db_user,),
                )
                console.print(f"[yellow]Dropping user '{db_user}'...[/yellow]")
                cursor.execute(f'DROP USER "{db_user}"')  # type: ignore
                console.print(f"  [green]✓[/green] User '{db_user}' dropped")
            elif user_exists:
                console.print(
                    f"[red]✗ User '{db_user}' already exists. "
                    f"Use --drop to recreate.[/red]"
                )
                raise typer.Exit(code=1)

            # Create user
            console.print(f"[yellow]Creating user '{db_user}'...[/yellow]")

            if superuser:
                create_stmt = (
                    f'CREATE USER "{db_user}" WITH '
                    f"PASSWORD '{db_password}' "
                    f"SUPERUSER CREATEDB CREATEROLE LOGIN"
                )
            else:
                create_stmt = (
                    f'CREATE USER "{db_user}" WITH '
                    f"PASSWORD '{db_password}' "
                    f"CREATEDB LOGIN"
                )

            cursor.execute(create_stmt)  # type: ignore

            # Verify creation
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (db_user,))
            if not cursor.fetchone():
                console.print("[red]✗ Failed to verify user creation[/red]")
                raise typer.Exit(code=1)

            console.print()
            console.print(
                Panel(
                    f"[green]✓[/green] User '{db_user}' created successfully!",
                    title="Success",
                    border_style="green",
                )
            )

            privileges = (
                "SUPERUSER, CREATEDB, CREATEROLE, LOGIN"
                if superuser
                else "CREATEDB, LOGIN"
            )
            console.print(f"[dim]Privileges: {privileges}[/dim]")
            console.print("\n[bold]Next steps:[/bold]")
            console.print("  1. Create database: [cyan]devtools db create[/cyan]")

    except KeyboardInterrupt:
        console.print("\n[red]✗ Operation cancelled by user.[/red]")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1) from None


def drop_user(
    force: bool = False,
    allow_in_production: bool = False,
    alias: str = "default",
    all_dbs: bool = False,
) -> None:
    """Drop PostgreSQL user using configuration settings.

    Args:
        force: Skip confirmation prompts.
        allow_in_production: Allow operation in production environment.
        alias: Database alias to operate on (default: "default")
        all_dbs: If True, operate on all configured databases
    """
    require_non_production("drop user", allow_in_production)

    if all_dbs:
        aliases = get_all_db_aliases()
        console.print(
            f"[cyan]Dropping user(s) for {len(aliases)} database(s)...[/cyan]\n"
        )
        for db_alias in aliases:
            try:
                _drop_single_user(db_alias, force, allow_in_production)
                console.print()
            except typer.Exit:
                continue
        return

    _drop_single_user(alias, force, allow_in_production)


def _drop_single_user(
    alias: str,
    force: bool,
    allow_in_production: bool,
) -> None:
    """Drop a PostgreSQL user for a single database.

    Args:
        alias: Database alias
        force: Skip confirmation prompts
        allow_in_production: Allow operation in production environment
    """
    try:
        db_config = get_db_config(alias)
        db_user = db_config.user

        console.print(f"[cyan]User to drop [{alias}]:[/cyan]", db_user)
        console.print()

        warn_destructive_operation("DROP USER", db_user)

        if not force:
            require_explicit_confirmation("user", db_user, force)

        admin_user, admin_password = prompt_admin_credentials()

        with (
            console.status("[bold yellow]Connecting to PostgreSQL..."),
            connect_with_admin_credentials(
                admin_user, admin_password, alias=alias
            ) as conn,
            conn.cursor() as cursor,
        ):
            # Check if user exists
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (db_user,))
            if not cursor.fetchone():
                console.print(
                    f"[yellow]User '{db_user}' does not exist. "
                    f"Nothing to drop.[/yellow]"
                )
                raise typer.Exit(code=0)

            # Terminate connections
            console.print(
                f"[yellow]Terminating connections from '{db_user}'...[/yellow]"
            )
            cursor.execute(
                """
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.usename = %s
                  AND pid <> pg_backend_pid()
                """,
                (db_user,),
            )

            # Drop user
            console.print(f"[yellow]Dropping user '{db_user}'...[/yellow]")
            cursor.execute(f'DROP USER "{db_user}"')  # type: ignore

            console.print()
            console.print(
                Panel(
                    f"[green]✓[/green] User '{db_user}' dropped successfully!",
                    title="Success",
                    border_style="green",
                )
            )

    except KeyboardInterrupt:
        console.print("\n[red]✗ Operation cancelled by user.[/red]")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1) from None
