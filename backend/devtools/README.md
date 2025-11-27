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

```bash
# Create database
uv run devtools db create

# Drop database
uv run devtools db drop

# Reset database (drop + create + migrate)
uv run devtools db reset

# Setup complete database (create + migrate)
uv run devtools db setup

# Verify database connection
uv run devtools db verify
```

### User Commands

```bash
# Create a database user
uv run devtools create-user [username]

# Drop a database user
uv run devtools drop-user [username]
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

### Development Session

```bash
# Setup once
source .venv/bin/activate
devtools db setup

# Then just use Django commands
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Reset Database

```bash
# Option 1: Full reset (drop + create + migrate)
uv run devtools db reset

# Option 2: Just drop and recreate
uv run devtools db drop
uv run devtools db create
```

### Create Additional Database Users

```bash
# Interactive
 uv run devtools db create-user
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

### Example 1: Setup for Development

```bash
# First time setup
uv run devtools db setup

# Create development users
uv run devtools create-user dev_user_1
uv run devtools create-user dev_user_2

# Verify it works
uv run python manage.py shell

# In Django shell
>>> from django.contrib.auth.models import User
>>> User.objects.all().count()
3  # default superuser + 2 development users
```

### Example 2: Fresh Database

```bash
# Reset the database (start from scratch)
uv run devtools db reset

# Verify it's empty
uv run python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.all().count()
0

# Create a new superuser
uv run python manage.py createsuperuser
```

### Example 3: CI/CD Pipeline

```bash
# uv is ideal for automation - no activation needed
uv sync
uv run devtools db create
uv run python manage.py migrate
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

Make sure you're in the backend directory and have run `uv sync`:

```bash
cd backend
uv sync
uv run devtools --help
```

### "Database connection failed"

Check your `.env` file:

```bash
cat .env | grep DATABASE_URL
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
