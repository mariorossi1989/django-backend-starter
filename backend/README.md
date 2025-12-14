# Backend

Backend application with Django, Pydantic settings, and a standalone CLI for database management.

## 📋 Requirements & Technology Stack

### System Requirements

- **OS**: Ubuntu 22.04 or later (or any Linux distribution with equivalent tools)
- **Python**: 3.11 or higher
- **PostgreSQL**: 16 or higher (for database)

### 🛠️ Core Technologies

| Component | Tool | Purpose |
|-----------|------|---------|
| **Framework** | Django 5.2 | Application framework |
| **Database** | PostgreSQL + psycopg 3 | Database and driver |
| **Settings** | Pydantic + pydantic-settings | Configuration management and validation |
| **Package Manager** | uv | Fast, modern Python dependency management |
| **Code Quality** | Ruff | Python formatting and linting |
| **Logging** | Loguru | Advanced, flexible logging with rotation/retention |
| **CLI Tools** | Typer + Rich | Command-line interface for devtools |
| **Testing** | pytest + pytest-django | Testing framework |
| **Build System** | Hatchling | Python package building |

### Key Design Decisions

- **Ruff for Code Quality**: All Python code is formatted and linted with Ruff for consistency and best practices
- **uv for Package Management**: Replaces pip/poetry for faster, simpler dependency management
- **Pydantic for Configuration**: Type-safe configuration with validation using Pydantic schemas
- **Loguru for Logging**: Centralized, structured logging with environment-specific behavior (console in dev, file-based in production)
- **Devtools CLI**: Standalone command-line tool (Typer) for database operations and DevOps tasks


## 🚀 Quick Start

### 1. Install uv (Package Manager)

uv is a fast, modern Python package manager. Install it first:

```bash
# On Ubuntu/Debian
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip (if you have Python already)
pip install uv

# Verify installation
uv --version
```

### 2. Clone & Navigate to Backend

```bash
# Clone the repository
git clone <repository-url>
cd django-backend-starter
```

### 3. Configure Environment Variables

From the project root:

```bash
cd backend
```
Create a `.env` file from the template:

```bash
cp .env.template .env
```

Edit `.env` with your local development settings:

```bash
# Environment state
ENV_STATE="development"

# Django security key (use a strong key in production)
DJANGO_SECRET_KEY="your-secure-dev-key-here"

# Database aliases (comma-separated list)
DB_ALIASES="default"

# Default database configuration
DB_ENGINE="postgresql"
DB_NAME="backend_db"
DB_USER="dev_user"
DB_PASSWORD="dev_password"
DB_HOST="localhost"
DB_PORT="5432"
```

#### Multiple Databases (Optional)

The project supports multiple database configurations. Add additional databases by:

1. **Add aliases to the list**:
```bash
DB_ALIASES=["default", "db2", "analytics"]
```

2. **Configure each database with its own prefix**:
```bash
# Default database (uses DB_ prefix)
DB_ENGINE="postgresql"
DB_NAME="backend_db"
DB_USER="dev_user"
DB_PASSWORD="dev_password"
DB_HOST="localhost"
DB_PORT="5432"

# Second database (uses DB_DB2_ prefix)
DB_DB2_ENGINE="postgresql"
DB_DB2_NAME="database2"
DB_DB2_USER="db2_user"
DB_DB2_PASSWORD="db2_password"
DB_DB2_HOST="localhost"
DB_DB2_PORT="5432"

# Analytics database (uses DB_ANALYTICS_ prefix)
DB_ANALYTICS_ENGINE="postgresql"
DB_ANALYTICS_NAME="analytics_db"
DB_ANALYTICS_USER="analytics_user"
DB_ANALYTICS_PASSWORD="analytics_password"
DB_ANALYTICS_HOST="localhost"
DB_ANALYTICS_PORT="5432"
```

**Prefix Pattern**: For database alias `{ALIAS}`, use `DB_{ALIAS}_` prefix (uppercase).  
Example: `db2` → `DB_DB2_NAME`, `analytics` → `DB_ANALYTICS_NAME`

**Important**: 
- Never commit `.env` to version control (it's in `.gitignore`)
- In development, you can use simple values
- In production, use strong, randomly generated values

### 4. Create Virtual Environment & Install Dependencies

```bash
# From project root
cd backend

# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install all dependencies
uv sync
```

These commands:
1. Create a `.venv` virtual environment with Python 3.11+
2. Install all dependencies from `pyproject.toml`
3. Set up development tools (pytest, ruff, etc.)

**Verify installation**:
```bash
source .venv/bin/activate
python --version  # Should be 3.11+
uv pip list       # Should show all installed packages
```

### 5. Database Setup

```bash
# Option A: Using uv run
uv run devtools db setup

# Option B: With venv activated
source .venv/bin/activate
devtools db setup
```

### 6. Create Superuser

```bash
# Option A: Using uv run
uv run python manage.py createsuperuser

# Option B: With venv activated
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## 🧹 Code Quality with Ruff

We use **Ruff** for code formatting and linting to ensure consistent, high-quality Python code.

### Format Code

Format all Python files in the project:

```bash
# Using uv
uv run ruff format .

# With venv activated
ruff format .
```

### Check Code Quality

Check for linting issues without making changes:

```bash
# Using uv
uv run ruff check .

# With venv activated
ruff check .
```

### Fix Common Issues

Automatically fix fixable linting issues:

```bash
# Using uv
uv run ruff check . --fix

# With venv activated
ruff check . --fix
```

**Best Practice**: Run these commands before committing:
```bash
uv run ruff format .
uv run ruff check .
```

### Pre-commit Hooks (Recommended)

To automatically run Ruff on every commit, install pre-commit hooks:

```bash
# Install pre-commit using uv (installs globally, no venv needed)
uv tool install pre-commit

# Navigate to project root and install the git hooks
cd ..  # Go to project root (django-backend-starter/)
pre-commit install
```

> **Note**: `uv tool install` installs pre-commit as a global tool, so you don't need to activate the venv. The `pre-commit install` command configures git hooks for this specific repository.

**What it does**:
- Automatically runs `ruff format` and `ruff check --fix` before each commit
- Prevents commits with code quality issues
- Ensures consistent code style across the team

**Test pre-commit**:
```bash
# Run on all files manually
pre-commit run --all-files
```

The configuration is in `.pre-commit-config.yaml` at the project root.

## 📝 Logging with Loguru

We use **Loguru** for centralized, structured logging that follows environment-specific behavior:

- **Development**: Console output only (colorized, clean format)
- **Production**: Console + rotating file logs with retention policies

For detailed logging configuration, usage patterns, and examples, see **[`config/LOGGING.md`](config/LOGGING.md)**

## 📁 Project Structure

```
django-backend-starter/
├── backend/                   # Django application
│   ├── config/                # Django configuration
│   ├── devtools/              # CLI for DevOps operations
│   ├── tests/                 # Test suite
│   ├── manage.py
│   ├── pyproject.toml
│   └── README.md              # This file
│
├── .pre-commit-config.yaml
├── README.md                  # Main project README
└── .gitignore

## 📚 Related Documentation

- **Logging Configuration**: `config/LOGGING.md` — Loguru setup, configuration, and usage examples
- **Devtools CLI**: `devtools/README.md` — Database and DevOps operations
- **Testing Guide**: `tests/README.md` — Complete testing documentation
- **Database Command Tests**: `tests/db_commands/README.md` — Running database tests
- **Examples**: `tests/db_commands/EXAMPLES.md` — Practical scenarios
- **Project Root README**: `../README.md` — Full project overview
