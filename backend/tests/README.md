# Backend Tests

Comprehensive test suite for the backend application organized by test type.

## 🚀 Quick Start

### Setup

```bash
cd backend
uv sync
```

### Run Tests

You have **two options**:

#### Option 1: Using `uv run` (simple, one-off commands)

```bash
# All tests
uv run pytest

# Specific category
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v

# With coverage
uv run pytest --cov=config --cov-report=html
```

#### Option 2: Activate venv (faster for long sessions)

```bash
source .venv/bin/activate

# All tests
pytest

# Specific category
pytest tests/unit/ -v
pytest tests/integration/ -v

# With coverage
pytest --cov=config --cov-report=html

# When done
deactivate
```

Both approaches do the same thing; choose based on your preference.

## 📁 Structure

```
tests/
├── README.md                   # This file
├── TESTING.md                  # Main testing guide
├── __init__.py                 # Tests package
│
├── db_commands/               # Database command tests (interactive)
│   ├── test_db_commands.sh    # Interactive test script
│   ├── quickstart.py          # Quick start guide
│   ├── demo_commands.py       # Command demonstrations
│   ├── EXAMPLES.md            # Practical examples
│   └── README.md              # Complete documentation
│
├── unit/                      # Unit tests (pytest)
│   ├── __init__.py
│   ├── test_settings/         # Settings tests
│   ├── test_commands/         # Management commands
│   └── test_utils/            # Utility functions
│
├── integration/               # Integration tests (pytest)
│   ├── __init__.py
│   ├── test_database/         # Database integration
│   ├── test_api/              # API integration
│   └── test_workflows/        # End-to-end workflows
│
└── fixtures/                  # Test fixtures and data
    ├── __init__.py
    ├── data/                  # Sample data
    ├── factories/             # Model factories
    └── conftest.py            # Shared fixtures
```

## 🚀 Test Execution

### Database Command Tests (Interactive)

For testing database management commands with guided workflows, see:

**`db_commands/README.md`** — Complete guide to running database command tests

Quick reference:
```bash
# View available tests
uv run python tests/db_commands/quickstart.py

# Read practical examples
cat tests/db_commands/EXAMPLES.md
```

### Unit Tests (pytest)

```bash
# Run all unit tests
pytest tests/unit/

# Run with coverage
pytest tests/unit/ --cov=config --cov-report=html
```

### Integration Tests (pytest)

```bash
# Run all integration tests
pytest tests/integration/

# Run specific category
pytest tests/integration/test_database/
```

### All Tests

```bash
# Run everything
pytest

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

## 📚 Documentation

| File | Description |
|------|-------------|
| `TESTING.md` | Main testing guide and overview |
| `db_commands/README.md` | Database commands testing guide |
| `db_commands/EXAMPLES.md` | Practical command examples |

## 🎯 Test Categories

### 1. Database Commands (`db_commands/`)

**Type**: Interactive bash scripts  
**Purpose**: Test database operations, user management, safety guards  
**Run**: `./tests/db_commands/test_db_commands.sh`

Features:
- ✅ Interactive menu with 6 test flows
- ✅ Production safety verification
- ✅ Step-by-step guidance
- ✅ Environment simulation

### 2. Unit Tests (`unit/`)

**Type**: pytest  
**Purpose**: Test individual components in isolation  
**Run**: `pytest tests/unit/`

Test:
- Settings and configuration
- Utility functions
- Model methods
- Business logic

### 3. Integration Tests (`integration/`)

**Type**: pytest  
**Purpose**: Test component interactions  
**Run**: `pytest tests/integration/`

Test:
- Database operations
- API endpoints
- End-to-end workflows
- External services

### 4. Fixtures (`fixtures/`)

**Type**: pytest fixtures and data  
**Purpose**: Provide reusable test data  
**Usage**: Imported via conftest.py

Contains:
- Sample data files
- Model factories
- Shared fixtures

## ⚙️ Configuration

### pytest.ini (create if needed)

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.django.development
python_files = test_*.py
python_classes = Test*
python_functions = test_*
testpaths = tests
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### Install Test Dependencies

```bash
# Using uv
uv add pytest pytest-cov pytest-django
```

## 💡 Common Commands

```bash
# Specific test file
pytest tests/unit/test_settings/test_environment.py

# Specific test function
pytest tests/unit/test_settings/test_environment.py::test_production_mode

# With coverage report
pytest --cov=. --cov-report=html
open htmlcov/index.html

# Parallel execution
pytest -n auto

# Show print statements
pytest -s

# Failed tests only
pytest --lf
```

## 🎓 Learning Path

### Beginner

1. Run `uv run python tests/db_commands/quickstart.py`
2. Try `./tests/db_commands/test_db_commands.sh`
3. Run `pytest tests/unit/ -v`

### Intermediate

1. Explore `tests/db_commands/EXAMPLES.md`
2. Write your first unit test
3. Run integration tests

### Advanced

1. Add pytest fixtures
2. Configure coverage reporting
3. Integrate with CI/CD

## 🔍 Troubleshooting

### "Module not found"
```bash
uv sync
```

### "No tests collected"
```bash
# Check test file naming (must start with test_)
# Check pytest configuration
pytest --collect-only
```

### "Database connection failed"
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify test database config
cat .env | grep DATABASE
```

## 📖 More Information

- **Main Guide**: `tests/TESTING.md` - Comprehensive testing documentation
- **DB Commands**: `tests/db_commands/README.md` - Database testing guide
- **Examples**: `tests/db_commands/EXAMPLES.md` - Practical scenarios

## 🤝 Contributing

When adding tests:

1. **Place in correct directory**
   - Unit tests → `unit/`
   - Integration tests → `integration/`
   - DB command tests → `db_commands/`

2. **Follow conventions**
   - File names: `test_*.py`
   - Test functions: `test_*`
   - Test classes: `Test*`

3. **Add documentation**
   - Docstrings for test classes/functions
   - Update relevant README files
   - Add examples if applicable

4. **Verify tests pass**
   ```bash
   pytest
   ```

## 🎯 Next Steps

```bash
# 1. Explore database command tests (interactive)
./tests/db_commands/test_db_commands.sh

# 2. Run unit tests (quick)
pytest tests/unit/ -v

# 3. Read the main guide
cat tests/TESTING.md

# 4. Browse examples
cat tests/db_commands/EXAMPLES.md
```

---

**Quick Links**:
- [Main Testing Guide](TESTING.md)
- [Database Commands Tests](db_commands/README.md)
- [Practical Examples](db_commands/EXAMPLES.md)
