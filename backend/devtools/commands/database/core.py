"""Core database commands Typer application.

Exposes all database management commands with environment-based safety guards.
"""

import typer

from devtools.commands.database.operations import (
    create_database,
    drop_database,
    reset_database,
)
from devtools.commands.database.setup import setup as setup_database
from devtools.commands.database.users import create_user as create_db_user
from devtools.commands.database.users import drop_user as drop_db_user
from devtools.commands.database.verify import verify_database

# Initialize Typer app
db_app = typer.Typer(
    name="db",
    help="Database management commands",
    no_args_is_help=True,
)


@db_app.command(name="create")
def create() -> None:
    """Create PostgreSQL database using configuration settings."""
    create_database()


@db_app.command(name="drop")
def drop(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force drop without confirmation",
    ),
    allow_in_production: bool = typer.Option(
        False,
        "--allow-in-production",
        help="Allow this operation in production environment",
    ),
) -> None:
    """Drop PostgreSQL database using configuration settings.

    ⚠️  DESTRUCTIVE OPERATION - This will permanently delete ALL data!

    This command is blocked in production by default. Use --allow-in-production
    to explicitly allow this operation in production environments.
    """
    drop_database(force=force, allow_in_production=allow_in_production)


@db_app.command(name="reset")
def reset(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force reset without confirmation",
    ),
    no_migrate: bool = typer.Option(
        False,
        "--no-migrate",
        help="Skip running migrations",
    ),
    allow_in_production: bool = typer.Option(
        False,
        "--allow-in-production",
        help="Allow this operation in production environment",
    ),
) -> None:
    """Reset database: drop, create, and optionally run migrations.

    ⚠️  DESTRUCTIVE OPERATION - This will permanently delete ALL data!

    This command is blocked in production by default. Use --allow-in-production
    to explicitly allow this operation in production environments.
    """
    reset_database(
        force=force,
        no_migrate=no_migrate,
        allow_in_production=allow_in_production,
    )


@db_app.command(name="create-user")
def create_user(
    superuser: bool = typer.Option(
        False,
        "--superuser",
        help="Create user with SUPERUSER privileges",
    ),
    drop: bool = typer.Option(
        False,
        "--drop",
        help="Drop user if exists",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force without confirmation",
    ),
    allow_in_production: bool = typer.Option(
        False,
        "--allow-in-production",
        help="Allow superuser creation in production environment",
    ),
) -> None:
    """Create PostgreSQL user using configuration settings.

    By default, creates a user with CREATEDB privilege.
    Use --superuser to create with SUPERUSER privileges.

    ⚠️  Creating SUPERUSER is blocked in production by default.
    Use --allow-in-production to explicitly allow this in production.
    """
    create_db_user(
        superuser=superuser,
        drop=drop,
        force=force,
        allow_in_production=allow_in_production,
    )


@db_app.command(name="drop-user")
def drop_user(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force without confirmation",
    ),
    allow_in_production: bool = typer.Option(
        False,
        "--allow-in-production",
        help="Allow this operation in production environment",
    ),
) -> None:
    """Drop PostgreSQL user using configuration settings.

    ⚠️  DESTRUCTIVE OPERATION - This will revoke all access for this user!

    This command is blocked in production by default. Use --allow-in-production
    to explicitly allow this operation in production environments.
    """
    drop_db_user(force=force, allow_in_production=allow_in_production)


@db_app.command(name="setup")
def setup(
    superuser: bool = typer.Option(
        False,
        "--superuser",
        help="Create user with SUPERUSER privileges",
    ),
    reset: bool = typer.Option(
        False,
        "--reset",
        help="Drop existing user and database before recreating",
    ),
    no_migrate: bool = typer.Option(
        False,
        "--no-migrate",
        help="Skip running migrations",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force without confirmation",
    ),
    allow_in_production: bool = typer.Option(
        False,
        "--allow-in-production",
        help="Allow superuser/reset in production environment",
    ),
) -> None:
    """Complete database setup: create user, database, and run migrations.

    This is a convenience command that combines:
    1. Create PostgreSQL user (if needed)
    2. Create database (if needed)
    3. Grant privileges
    4. Run Django migrations (unless --no-migrate)

    ⚠️  Using --superuser or --reset is blocked in production by default.
    Use --allow-in-production to explicitly allow these in production.
    """
    setup_database(
        superuser=superuser,
        reset=reset,
        no_migrate=no_migrate,
        force=force,
        allow_in_production=allow_in_production,
    )


@db_app.command(name="verify")
def verify() -> None:
    """Verify database connection, tables, and migration status.

    Checks:
    - PostgreSQL connectivity
    - Database existence
    - Table structure
    - Migration status

    This is a safe, read-only operation.
    """
    verify_database()
