# Testing Database Commands

This guide shows you how to test the database management commands with various workflows.

## 🚀 Quick Start

From the project root:

```bash
# Option 1: Using uv run (simple, one-off commands)
cd backend
uv run devtools db --help
uv run devtools db setup

# Option 2: Activate venv (faster for multiple commands)
cd backend
source .venv/bin/activate
devtools db --help
devtools db setup
```

Both approaches work identically; choose based on your preference.

## 📁 Test Files

| File | Purpose | When to Use |
|------|---------|-------------|
| `tests/quickstart.py` | Display quick start guide | First time, need overview |
| `tests/db_commands/test_db_commands.sh` | Interactive test menu (multi-DB support) | Main testing tool |
| `tests/README.md` | Complete testing documentation | Detailed reference |
| `tests/EXAMPLES.md` | Command examples and scenarios | Quick command lookup |

**Note**: All database commands now support `--alias <name>` for specific databases and `--all` for all configured databases.

## 🎯 Test Flows

The interactive test script provides 6 different flows:

### 1. Basic Commands
- **What it does**: Shows help for all commands
- **Safe**: ✅ Yes, no database changes
- **Use when**: First time, learning commands

### 2. Database Lifecycle
- **What it does**: Create → Verify → Drop database (supports `--alias` and `--all`)
- **Safe**: ⚠️  Creates and drops test database
- **Use when**: Testing basic CRUD operations
- **Multi-DB**: Supports operations on specific or all databases

### 3. User Management
- **What it does**: Create user, test superuser, drop user (supports `--alias` and `--all`)
- **Safe**: ⚠️  Creates and drops PostgreSQL user
- **Use when**: Testing user operations and guards
- **Multi-DB**: Can create/drop users for specific databases

### 4. Complete Setup
- **What it does**: Full setup workflow with migrations (supports `--all`)
- **Safe**: ⚠️  Creates database and runs migrations
- **Use when**: Testing end-to-end setup, multiple database configurations
- **Multi-DB**: Can setup all databases at once

### 5. Production Guards
- **What it does**: Simulates production, tests safety blocks
- **Safe**: ✅ Yes, temporarily changes ENV_STATE
- **Use when**: Verifying safety mechanisms

### 6. Reset Database
- **What it does**: Tests database reset with/without migrations
- **Safe**: ⚠️  Drops and recreates database
- **Use when**: Testing reset functionality

## 💡 Usage Examples

### Interactive Menu (Easiest)

```bash
cd backend
./tests/db_commands/test_db_commands.sh

# Follow the prompts:
# 1. Choose a test flow (1-7)
# 2. Confirm operations when asked
# 3. Review results
# 4. Press Enter to continue
```

### Run Specific Flow

```bash
cd backend

# Run just the basic commands flow
./tests/db_commands/test_db_commands.sh basic

# Run production guards test
./tests/db_commands/test_db_commands.sh guards

# Run all flows
./tests/db_commands/test_db_commands.sh all
```

### Manual Commands

```bash
# Option 1: Using uv run (simple)
uv run devtools db --help
uv run devtools db info                      # Show all configured databases
uv run devtools db create                    # Default database
uv run devtools db create --alias db2        # Specific database
uv run devtools db create --all              # All databases
uv run devtools db drop --force
uv run devtools db drop --alias db2 --force  # Specific database
uv run devtools db setup
uv run devtools db setup --all               # All databases
uv run devtools db setup --reset --force

# Option 2: With venv activated (faster)
source .venv/bin/activate
devtools db --help
devtools db info                             # Show all configured databases
devtools db create                           # Default database
devtools db create --alias db2               # Specific database
devtools db create --all                     # All databases
devtools db drop --force
devtools db drop --alias db2 --force         # Specific database
devtools db setup
devtools db setup --all                      # All databases
devtools db setup --reset --force
```

## 🛡️ Safety Features

### Automatic Protection

In **production environment** (`ENV_STATE=production`), these operations are **automatically blocked**:

- ❌ `db drop` - Cannot drop databases
- ❌ `db reset` - Cannot reset databases  
- ❌ `db drop-user` - Cannot drop users
- ❌ `db create-user --superuser` - Cannot create superusers
- ❌ `db setup --reset` - Cannot reset during setup

### Override Protection

To override (use with extreme caution):

```bash
# Add --allow-in-production flag
python3 -m devtools db drop --force --allow-in-production
```

### Test Protection

Run **Flow 5** (Production Guards) to verify safety mechanisms work correctly:

```bash
./tests/db_commands/test_db_commands.sh guards
```

## ⚙️ Prerequisites

Before testing, ensure:

1. **PostgreSQL is running**
   ```bash
   sudo systemctl status postgresql
   ```

2. **`.env` file is configured**
   ```bash
   cd backend
   cp .env.template .env
   # Edit .env with your settings
   ```

3. **Environment variables set**
   ```bash
   # For testing, use development
   ENV_STATE=development
   
   # Single database configuration
   DB_ALIASES=default
   DB_ENGINE=postgresql
   DB_NAME=test_db
   DB_USER=test_user
   DB_PASSWORD=secure_password
   DB_HOST=localhost
   DB_PORT=5432
   
   # Multiple databases (optional)
   DB_ALIASES=default,db2
   
   # Default database (DB_ prefix)
   DB_ENGINE=postgresql
   DB_NAME=test_db
   DB_USER=test_user
   DB_PASSWORD=secure_password
   DB_HOST=localhost
   DB_PORT=5432
   
   # Second database (DB_DB2_ prefix)
   DB_DB2_ENGINE=postgresql
   DB_DB2_NAME=test_db2
   DB_DB2_USER=test_user2
   DB_DB2_PASSWORD=secure_password2
   DB_DB2_HOST=localhost
   DB_DB2_PORT=5432
   ```
   
   **Prefix Pattern**: For database alias `{ALIAS}`, use `DB_{ALIAS}_` prefix (uppercase).  
   Example: `db2` → `DB_DB2_NAME`, `analytics` → `DB_ANALYTICS_NAME`

## 📚 Documentation

- **Quick Start**: `python3 tests/quickstart.py`
- **Full Guide**: `cat tests/README.md`
- **Examples**: `cat tests/EXAMPLES.md`
- **Command Help**: `uv run devtools db --help`

## 🔍 Troubleshooting

### "Command not found: python"
```bash
# Use uv run instead
uv run devtools db --help

# Or activate venv
source .venv/bin/activate
devtools db --help
```

### "Permission denied"
```bash
# Make scripts executable
chmod +x tests/*.sh tests/*.py
```

### "PostgreSQL connection failed"
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify credentials in .env
cat .env | grep DATABASE
```

### "Module not found: typer"
```bash
# From project root, sync dependencies
cd backend
source .venv/bin/activate
uv sync
```

## 🎓 Learning Path

### Beginner
1. Run `python3 tests/quickstart.py` - Overview
2. Run Flow 1 (Basic) - Learn commands
3. Read `tests/EXAMPLES.md` - See examples

### Intermediate
1. Run Flow 2 (Lifecycle) - Test operations
2. Run Flow 5 (Guards) - Understand safety
3. Try manual commands from examples

### Advanced
1. Run Flow 4 (Setup) - Complete workflow
2. Test in both dev and prod environments
3. Create custom test scenarios

## 📝 Summary

```bash
# Simplest way to start testing
uv run devtools db --help

# Or activate venv for faster iteration
source .venv/bin/activate
devtools db --help
devtools db setup
```

**Remember**: Always test with a **test database**, never with production data!
