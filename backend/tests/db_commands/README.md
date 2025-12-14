# Database Command Tests

Quick guide for running and testing database management commands.

## 🚀 Quick Start

### Option 1: Using `uv run`

```bash
# View available tests
uv run python tests/db_commands/quickstart.py

# Read practical examples
cat tests/db_commands/EXAMPLES.md
```

### Option 2: Activate venv

```bash
source .venv/bin/activate

# View available tests
python tests/db_commands/quickstart.py

# Read examples
cat tests/db_commands/EXAMPLES.md

# When done
deactivate
```

## Test Files

### test_db_commands.sh
Interactive bash script with 6 test flows:
1. Basic Commands       - Help and documentation
2. Database Lifecycle   - Create, verify, drop (supports --alias and --all)
3. User Management      - Create, drop users (supports --alias and --all)
4. Complete Setup       - Full workflow with multiple databases
5. Production Guards    - Safety mechanism tests
6. Reset Database       - Reset workflows (supports --alias and --all)

**Multi-Database Support**: All commands support `--alias <name>` to operate on specific databases or `--all` to operate on all configured databases.

### quickstart.py
Quick start guide displaying:
- Available test scripts
- Command examples
- Safety information
- Documentation links

### demo_commands.py
Demonstration script showing command structure and available operations.

### EXAMPLES.md
Practical examples and scenarios:
- First time setup
- Development workflows
- CI/CD pipelines
- Troubleshooting

### README.md
Complete documentation including:
- Test flow descriptions
- Prerequisites
- Environment setup
- Safety notes

## Test Flows

For detailed information about each test flow, see README.md in this directory.

## Environment Setup

Before running tests (works with both `uv run` and venv activation):

1. Configure .env file:
   ```bash
   cp .env.template .env
   # Edit .env with your settings
   ```

2. Ensure PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   ```

3. Set environment to development:
   ```bash
   export ENV_STATE=development
   ```

## 📖 More Information

- **Devtools CLI**: `../devtools/README.md` — Full devtools documentation
- **Test Execution**: `../README.md` — How to run tests
- **Examples**: `EXAMPLES.md` — Practical command examples
