# Devtools CLI

Standalone command-line interface for database and DevOps operations.

## Overview

`devtools` is a Typer-based CLI tool for managing database operations, user management, and project operations. It's designed to simplify common DevOps tasks with a clean, intuitive interface.

## Installation

The devtools package is included in the project dependencies. No separate installation needed.

## 🚀 Quick Start

### Option 1: Using `uv run`

```bash
# From backend directory
uv run devtools --help
```

### Option 2: Activate venv

```bash
source .venv/bin/activate
devtools --help
```

### Shell Completion (Optional)

For faster command typing, install shell completions:

```bash
# Bash
uv run devtools --install-completion bash

# Zsh
uv run devtools --install-completion zsh

# Fish
uv run devtools --install-completion fish
```

After installation, restart your shell or run `source ~/.bashrc` (or equivalent) to enable tab completion.

## 📋 Available Commands

### Database Commands

All database commands support `--alias` (or `-a`) to specify which database to operate on, and `--all` to operate on all configured databases.

```bash
# Create database
uv run devtools db create                    # Default database
uv run devtools db create --alias db2        # Specific database
uv run devtools db create --all              # All databases

# Drop database
uv run devtools db drop                      # Default database
uv run devtools db drop --alias db2 --force  # Specific database
uv run devtools db drop --all --force        # All databases

# Reset database (drop + create + migrate)
uv run devtools db reset                     # Default database
uv run devtools db reset --alias db2         # Specific database
uv run devtools db reset --all               # All databases

# Setup complete database (create user + database + migrate)
uv run devtools db setup                     # Default database
uv run devtools db setup --alias db2         # Specific database
uv run devtools db setup --all               # All databases

# Show all database configurations
uv run devtools db info

# Verify database connection
uv run devtools db verify
```

### User Commands

User commands also support `--alias` and `--all` flags:

```bash
# Create a database user
uv run devtools db create-user                    # Default database user
uv run devtools db create-user --alias db2        # Specific database user
uv run devtools db create-user --all              # All database users

# Create superuser
uv run devtools db create-user --superuser        # Default (development only)
uv run devtools db create-user --superuser -a db2 # Specific database

# Drop a database user
uv run devtools db drop-user                      # Default database user
uv run devtools db drop-user --alias db2 --force  # Specific database user
uv run devtools db drop-user --all --force        # All database users
```

### Help and Info

```bash
# Show all commands
uv run devtools --help

# Show command help
uv run devtools db --help
uv run devtools create-user --help
```

## 🔧 Common Workflows

### First Time Setup

```bash
# Option 1: Using uv run
uv run devtools db setup
uv run python manage.py createsuperuser
uv run python manage.py runserver

# Option 2: With venv activated
source .venv/bin/activate
devtools db setup
python manage.py createsuperuser
python manage.py runserver
```

### Multiple Databases Setup

```bash
# Setup all configured databases at once
uv run devtools db setup --all

# Or setup specific databases individually
uv run devtools db setup                # default database
uv run devtools db setup --alias db2    # db2 database
uv run devtools db setup --alias analytics  # analytics database

# View all configured databases
uv run devtools db info
```

### Development Session

```bash
# Setup once
source .venv/bin/activate
devtools db setup

# For multiple databases
devtools db setup --all

# Then just use Django commands
python manage.py migrate
python manage.py migrate --database db2  # Migrate specific database
python manage.py createsuperuser
python manage.py runserver
```

### Reset Database

```bash
# Option 1: Full reset (drop + create + migrate)
uv run devtools db reset                 # Default database
uv run devtools db reset --alias db2     # Specific database
uv run devtools db reset --all           # All databases

# Option 2: Just drop and recreate
uv run devtools db drop --alias db2
uv run devtools db create --alias db2
```

### Create Additional Database Users

```bash
# Interactive
uv run devtools db create-user                  # Default database
uv run devtools db create-user --alias db2      # Specific database
uv run devtools db create-user --all            # All databases
```

## 🛡️ Production Safety

All destructive operations (`drop`, `reset`) are blocked in production by default.

### Override Safety (with caution)

```bash
uv run devtools db drop --allow-in-production
uv run devtools db reset --allow-in-production
```

**Use with extreme caution!**

## 📝 Examples

### Example 1: Setup for Development (Single Database)

```bash
# First time setup
uv run devtools db setup

# Create Django superuser
uv run python manage.py createsuperuser

# Verify it works
uv run python manage.py shell

# In Django shell
>>> from django.contrib.auth.models import User
>>> User.objects.all().count()
1  # Your superuser
```

### Example 2: Setup for Multiple Databases

```bash
# Setup all databases at once
uv run devtools db setup --all

# Or setup individually
uv run devtools db setup                 # default
uv run devtools db setup --alias db2     # db2
uv run devtools db setup --alias analytics  # analytics

# View all configurations
uv run devtools db info

# Migrate specific database
uv run python manage.py migrate --database db2
```

### Example 3: Fresh Database Reset

```bash
# Reset specific database (start from scratch)
uv run devtools db reset --alias db2

# Reset all databases
uv run devtools db reset --all --force

# Verify it's empty
uv run python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.all().count()
0

# Create a new superuser
uv run python manage.py createsuperuser
```

### Example 4: CI/CD Pipeline

```bash
# uv is ideal for automation
uv venv # if not created yet!
source .venv/bin/activate
uv sync
uv run devtools db create --all
uv run python manage.py migrate
uv run python manage.py migrate --database db2
uv run pytest
```

## 🔗 Related Documentation

- **Backend Setup**: `../README.md` — Main backend README
- **Testing**: `../tests/README.md` — How to run tests
- **Project Root**: `../../README.md` — Full project overview

## 🛠️ Implementation Details

### Entry Point

The `devtools` CLI is configured as a package entry point in `pyproject.toml`:

```toml
[project.scripts]
devtools = "devtools.cli:main"
```

### Structure

```
devtools/
├── __init__.py
├── __main__.py          # Allow `python -m devtools`
├── cli.py               # Main CLI definition
├── commands/
│   └── database/        # Database operation commands
│       ├── create.py
│       ├── drop.py
│       ├── reset.py
│       ├── setup.py
│       └── verify.py
└── README.md            # This file
```

### Creating New Commands

To add a new command:

1. Create a new file in `commands/` directory
2. Define command function with Typer decorator
3. Import and add to CLI in `cli.py`
4. Update this README with the new command

Example:

```python
# commands/example.py
import typer

def example_command(name: str = "World"):
    """Example command description."""
    typer.echo(f"Hello {name}!")
```

Then in `cli.py`:

```python
from devtools.commands.example import example_command

app.command()(example_command)
```

## 💡 Tips and Tricks

### Check what the CLI will do (dry run)

```bash
# Most commands support --help to show what they'll do
uv run devtools db setup --help
```

### Run Python code after setup

```bash
# Setup, then enter Django shell
uv run devtools db setup && uv run python manage.py shell
```

### Check database status

```bash
# Verify connection and migrations
uv run devtools db verify
```

## 🐛 Troubleshooting

### "Command not found: devtools"

Make sure you're in the _backend_ directory and have created the virtual environment:

```bash
cd backend
source .venv/bin/activate
uv sync
uv run devtools --help
```

### "Database connection failed"

Check your `.env` file:

```bash
cat .env | grep DB_
```

View configured databases:

```bash
uv run devtools db info
```

Ensure PostgreSQL is running:

```bash
sudo systemctl status postgresql
```

### "Permission denied"

Some commands require proper database permissions. Check your PostgreSQL user:

```bash
psql -U postgres -l
```

## 📖 More Information

For database command examples and workflows, see `../tests/db_commands/README.md`.
