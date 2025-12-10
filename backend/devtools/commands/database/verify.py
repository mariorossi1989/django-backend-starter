"""Verify database connection and migrations status."""

import subprocess  # noqa: S404
import sys

import typer
from rich.panel import Panel
from rich.table import Table

from devtools.commands.database.connection import (
    connect_to_postgres,
    console,
    show_db_info,
)

__all__ = ["verify_database"]


def verify_database() -> None:
    """Verify database connection and show status.

    Checks:
    - PostgreSQL connectivity
    - Database existence
    - Table structure
    - Migration status
    """
    console.print(Panel("[bold cyan]Database Verification[/bold cyan]", expand=False))

    # 1. Show configuration
    console.print("\n[bold]Configuration:[/bold]")
    show_db_info()

    # 2. Test connection
    console.print("\n[bold]Testing connection...[/bold]")
    try:
        conn = connect_to_postgres()
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            result = cur.fetchone()
        conn.close()

        if result:
            version = result[0]
            console.print("[green]✓ Database connection successful[/green]")
            console.print(f"  PostgreSQL: {version.split(',')[0]}")
        else:
            console.print("[red]✗ Could not retrieve version[/red]")
            raise typer.Exit(code=1) from None
    except Exception as err:
        console.print(f"[red]✗ Connection failed: {err}[/red]")
        raise typer.Exit(code=1) from err

    # 3. Check tables
    console.print("\n[bold]Checking tables...[/bold]")
    try:
        conn = connect_to_postgres()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            )
            result = cur.fetchone()
        conn.close()

        if result:
            table_count = result[0]
            if table_count > 0:
                console.print(f"[green]✓ Found {table_count} tables[/green]")
            else:
                msg = (
                    "[yellow]⚠ No tables found "
                    "(database might not be migrated)[/yellow]"
                )
                console.print(msg)
        else:
            console.print("[yellow]⚠ Could not check tables[/yellow]")
    except Exception as err:
        console.print(f"[red]✗ Failed to check tables: {err}[/red]")
        raise typer.Exit(code=1) from err

    # 4. Check migrations
    console.print("\n[bold]Checking migrations...[/bold]")
    try:
        result = subprocess.run(  # noqa: S603
            [sys.executable, "manage.py", "showmigrations", "--plan"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            # Count applied and pending migrations
            output_lines = result.stdout.strip().split("\n")
            applied = sum(1 for line in output_lines if "[X]" in line)
            pending = sum(1 for line in output_lines if "[ ]" in line)

            migration_table = Table(show_header=True, header_style="bold")
            migration_table.add_column("Status", style="cyan")
            migration_table.add_column("Count", style="yellow")
            migration_table.add_row("[green]✓ Applied[/green]", str(applied))
            migration_table.add_row("[yellow]⊘ Pending[/yellow]", str(pending))

            console.print(migration_table)

            if pending > 0:
                msg = (
                    "[yellow]⚠ Run 'python manage.py migrate' to apply "
                    "pending migrations[/yellow]"
                )
                console.print(msg)
        else:
            console.print("[yellow]⚠ Could not check migrations[/yellow]")
    except subprocess.TimeoutExpired:
        console.print("[yellow]⚠ Migration check timed out[/yellow]")
    except Exception as err:
        console.print(f"[yellow]⚠ Could not check migrations: {err}[/yellow]")

    console.print("\n[bold green]✓ Database verification complete[/bold green]")
