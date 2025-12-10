"""Database management commands package.

Provides modular database operations including database lifecycle management,
user management, and complete setup workflows with environment-based security guards.

Structure:
    - core.py: Main Typer application and command definitions
    - operations.py: Database lifecycle operations (create, drop, reset)
    - users.py: User management operations
    - setup.py: Complete setup workflow
    - connection.py: Database connection utilities
    - guards.py: Environment-based security guards

Security:
    Dangerous operations (drop, reset, superuser creation) are blocked in
    production by default. Use --allow-in-production to override.
"""

from devtools.commands.database.core import db_app

__all__ = ["db_app"]
