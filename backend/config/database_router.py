"""Database router for managing multi-database operations in Django.

This router ensures that:
1. Django's built-in apps (auth, admin, sessions, etc.) only use the 'default' database
2. Custom apps can be routed to specific databases via configuration
3. Relations are only allowed between models in the same database
"""

from typing import ClassVar


class AppDatabaseRouter:
    """Route database operations based on app labels.

    Configure app-to-database mappings in your settings:
        DATABASE_ROUTERS = ['config.database_router.AppDatabaseRouter']

    To route a custom app to a specific database, add it to route_app_labels:
        route_app_labels = {
            'myapp': 'db2',
            'analytics': 'db3',
        }
    """

    # Map app labels to database aliases
    # Example: {'myapp': 'db2', 'analytics': 'db3'}
    route_app_labels: ClassVar[dict[str, str]] = {}

    # Django's built-in apps that should only exist on 'default'
    django_system_apps: ClassVar[set[str]] = {
        "admin",
        "auth",
        "contenttypes",
        "sessions",
        "messages",
        "staticfiles",
    }

    def db_for_read(self, model, **hints):
        """Determine which database to use for read operations.

        Args:
            model: The model being queried
            **hints: Additional routing hints

        Returns:
            Database alias or None to use default routing
        """
        app_label = model._meta.app_label

        # Route to specific database if configured
        if app_label in self.route_app_labels:
            return self.route_app_labels[app_label]

        # Django system apps always use default
        if app_label in self.django_system_apps:
            return "default"

        # Use default for everything else
        return "default"

    def db_for_write(self, model, **hints):
        """Determine which database to use for write operations.

        Args:
            model: The model being written
            **hints: Additional routing hints

        Returns:
            Database alias or None to use default routing
        """
        app_label = model._meta.app_label

        # Route to specific database if configured
        if app_label in self.route_app_labels:
            return self.route_app_labels[app_label]

        # Django system apps always use default
        if app_label in self.django_system_apps:
            return "default"

        # Use default for everything else
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """Determine if a relation between two objects is allowed.

        Relations are only allowed between models in the same database.

        Args:
            obj1: First model instance
            obj2: Second model instance
            **hints: Additional routing hints

        Returns:
            True if relation is allowed, False if not, None if no opinion
        """
        db1 = self.route_app_labels.get(obj1._meta.app_label, "default")
        db2 = self.route_app_labels.get(obj2._meta.app_label, "default")

        # Allow relations only if both models are in the same database
        return db1 == db2

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Determine if a migration should run on a given database.

        This ensures:
        - Django system apps only migrate on 'default'
        - Custom apps only migrate on their designated database
        - Other apps only migrate on 'default'

        Args:
            db: Database alias where migration would run
            app_label: Label of the app being migrated
            model_name: Name of the model being migrated (optional)
            **hints: Additional routing hints

        Returns:
            True if migration is allowed, False if not, None if no opinion
        """
        # Django system apps only migrate on default
        if app_label in self.django_system_apps:
            return db == "default"

        # Custom routed apps only migrate on their designated database
        if app_label in self.route_app_labels:
            return db == self.route_app_labels[app_label]

        # Everything else (including custom apps not explicitly routed) goes to default
        return db == "default"
