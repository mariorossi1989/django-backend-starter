# Database Commands - Testing Examples

Quick reference for testing database management commands.

## Prerequisites

1. Go to backend directory:
```bash
cd backend
```

2. Configure `.env` file:
```bash
cp .env.template .env
# Edit .env with your settings
```

3. Ensure PostgreSQL is running:
```bash
sudo systemctl status postgresql
```

## Quick Start

You have **two options** to run commands. Both work identically:

### Option 1: Using `uv run` (simple, no activation needed)

```bash
uv run devtools db --help
uv run devtools db setup
uv run devtools db create-user
```

### Option 2: Activate venv (faster for multiple commands)

```bash
source .venv/bin/activate
devtools db --help
devtools db setup
devtools db create-user
```

Choose Option 1 for single commands; use Option 2 if you'll run multiple commands in a session.

## Test Scenarios

### Scenario 1: First Time Setup (Single Database)

**Goal**: Set up database from scratch

```bash
# 1. Create user and database
uv run devtools db setup

# 2. Verify
psql -h localhost -U your_user -d your_db -c "\\dt"

# 3. Create Django superuser
uv run python manage.py createsuperuser
```

### Scenario 1b: First Time Setup (Multiple Databases)

**Goal**: Set up multiple databases from scratch

```bash
# 1. View all configured databases
uv run devtools db info

# 2. Setup all databases at once
uv run devtools db setup --all

# 3. Or setup individually
uv run devtools db setup                 # default
uv run devtools db setup --alias db2     # db2

# 4. Verify all databases
psql -h localhost -U postgres -c "\\l"

# 5. Run migrations for each database
uv run python manage.py migrate
uv run python manage.py migrate --database db2
```

### Scenario 2: Reset Development Database

**Goal**: Clean slate for development

```bash
# Quick reset with migrations (default database)
uv run devtools db reset --force

# Reset specific database
uv run devtools db reset --alias db2 --force

# Reset all databases
uv run devtools db reset --all --force

# Reset without migrations
uv run devtools db reset --no-migrate --force
```

### Scenario 3: Manual Database Lifecycle

**Goal**: Step-by-step database management

```bash
# 1. Create user first (default database)
uv run devtools db create-user

# 2. Create user for specific database
uv run devtools db create-user --alias db2

# 3. Create databases
uv run devtools db create                # default
uv run devtools db create --alias db2    # specific

# 4. Run migrations
uv run python manage.py migrate
uv run python manage.py migrate --database db2

# 5. When done, clean up
uv run devtools db drop --force                # default
uv run devtools db drop --alias db2 --force    # specific
uv run devtools db drop-user --force
uv run devtools db drop-user --alias db2 --force
```

### Scenario 4: Test Production Guards

**Goal**: Verify safety mechanisms

```bash
# 1. Temporarily set production mode
# Edit .env: ENV_STATE=production

# 2. Try dangerous operation (should be blocked)
uv run devtools db drop
# Expected: ⚠️  OPERATION BLOCKED

# 3. Try with override flag
uv run devtools db drop --allow-in-production
# Should work but ask for confirmation

# 4. Restore development mode
# Edit .env: ENV_STATE=development
```

### Scenario 5: Create Superuser (Development Only)

**Goal**: Create PostgreSQL superuser

```bash
# This is BLOCKED in production
uv run devtools db create-user --superuser

# With existing user replacement
uv run devtools db create-user --superuser --drop --force
```

## Common Workflows

### Daily Development

```bash
# Morning: Start fresh
uv run devtools db reset --force

# Work on features...

# End of day: Optional cleanup
uv run devtools db drop --force
```

### CI/CD Pipeline

```bash
# Setup for tests (single database)
uv run devtools db setup --no-migrate --force

# Setup for tests (multiple databases)
uv run devtools db setup --all --no-migrate --force

# Run migrations
uv run python manage.py migrate
uv run python manage.py migrate --database db2

# Run tests
uv run python manage.py test

# Cleanup
uv run devtools db drop --all --force
```

### Switching Branches

```bash
# Before switching
uv run devtools db drop --force

# Switch branch
git checkout feature-branch

# Recreate
uv run devtools db setup --force
```

## Troubleshooting Examples

### "Database already exists"

```bash
# Option 1: Drop and recreate
uv run devtools db drop --force
uv run devtools db create

# Option 2: Use reset
uv run devtools db reset --force
```

### "User already exists"

```bash
# Recreate user
uv run devtools db create-user --drop --force
```

### "Connection refused"

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check credentials in .env
cat .env | grep DATABASE

# Test connection manually
psql -h localhost -U your_user -d postgres
```

### "Operation blocked in production"

```bash
# Verify environment
cat .env | grep ENV_STATE

# Change to development
# Edit .env: ENV_STATE=development

# Or use override flag (dangerous!)
uv run devtools db drop --allow-in-production
```

## Command Cheat Sheet

| Command | Description | Blocked in Prod? | Multi-DB? |
|---------|-------------|------------------|--------|
| `db create` | Create database | No | Yes (`--alias`, `--all`) |
| `db drop` | Drop database | ⚠️  Yes | Yes (`--alias`, `--all`) |
| `db reset` | Reset database | ⚠️  Yes | Yes (`--alias`, `--all`) |
| `db create-user` | Create user | No | Yes (`--alias`, `--all`) |
| `db create-user --superuser` | Create superuser | ⚠️  Yes | Yes (`--alias`, `--all`) |
| `db drop-user` | Drop user | ⚠️  Yes | Yes (`--alias`, `--all`) |
| `db setup` | Complete setup | No | Yes (`--alias`, `--all`) |
| `db setup --reset` | Setup with reset | ⚠️  Yes | Yes (`--alias`, `--all`) |
| `db info` | Show all databases | No | N/A |

## Environment Variables

### Environment State

```bash
# Development (permissive)
ENV_STATE=development

# Production (restrictive)
ENV_STATE=production
```

### Database Configuration

```bash
# Single database
DB_ALIASES="default"
DB_ENGINE="postgresql"
DB_NAME="backend_db"
DB_USER="dev_user"
DB_PASSWORD="dev_password"
DB_HOST="localhost"
DB_PORT="5432"

# Multiple databases
DB_ALIASES="default,db2,analytics"

# Default database (DB_ prefix)
DB_ENGINE="postgresql"
DB_NAME="backend_db"
DB_USER="dev_user"
DB_PASSWORD="dev_password"
DB_HOST="localhost"
DB_PORT="5432"

# Second database (DB_DB2_ prefix)
DB_DB2_ENGINE="postgresql"
DB_DB2_NAME="database2"
DB_DB2_USER="db2_user"
DB_DB2_PASSWORD="db2_password"
DB_DB2_HOST="localhost"
DB_DB2_PORT="5432"

# Analytics database (DB_ANALYTICS_ prefix)
DB_ANALYTICS_ENGINE="postgresql"
DB_ANALYTICS_NAME="analytics_db"
DB_ANALYTICS_USER="analytics_user"
DB_ANALYTICS_PASSWORD="analytics_password"
DB_ANALYTICS_HOST="localhost"
DB_ANALYTICS_PORT="5432"
```

**Prefix Pattern**: For alias `{ALIAS}`, use `DB_{ALIAS}_` prefix (uppercase).

## Safety Tips

✅ **DO**:
- Use `--force` flag for automated scripts
- Test in development environment first
- Verify operations with `--help` before running
- Keep backups of production data

❌ **DON'T**:
- Use `--allow-in-production` without careful consideration
- Run destructive commands without understanding them
- Skip reading confirmation prompts
- Test on production databases

## Getting Help

```bash
# Main help
uv run devtools --help

# Database commands help
uv run devtools db --help

# Specific command help
uv run devtools db create --help
uv run devtools db drop --help
uv run devtools db setup --help

# Show all configured databases
uv run devtools db info

# Or with venv activated
source .venv/bin/activate
devtools --help
devtools db --help
devtools db info
```

## Next Steps

1. Run interactive tests: `./tests/test_db_commands.sh`
2. Read full guide: `cat tests/README.md`
3. Try quick start: `python3 tests/quickstart.py`
