# Logging

Centralized logging configuration using **Loguru** with Django integration.

## Overview

The logging system provides:

- **Centralized configuration** via Pydantic schemas
- **Environment-specific settings** (development vs production)
- **Loguru for all logging** - Django and application logs use Loguru exclusively
- **Django logging coordination** through Python's logging module interceptor
- **File rotation and retention** with configurable policies
- **Unified log format** across entire application

## How It Works

1. **Loguru is initialized** in `manage.py` and `wsgi.py` via `setup_logging()`
2. **Python logging is intercepted** - All Django logs are routed to Loguru via `InterceptHandler`
3. **Configuration is managed** - All settings come from `config/settings/schemas/logging.py` (Pydantic pattern)
4. **Environment-aware** - Development uses console-only, production uses file-based logging

```
Django logging (logging module)
        ↓
   InterceptHandler
        ↓
    Loguru
        ↓
    ├─ Console (always)
    └─ File (production only)
```

## Configuration

### Schema (`config/settings/schemas/logging.py`)

```python
class LoggingConfig(BaseSettings):
    level: LogLevelEnum = LogLevelEnum.INFO
    log_dir: str = "logs"
    format: str = "..."  # Loguru format string
    rotation: str = "500 MB"
    retention: str = "7 days"
    compression: str = "zip"
    write_to_file: bool = False  # Dev: False, Prod: True
```

### Access via Registry

```python
from config.settings.schemas import config_registry

# Get logging config
log_config = config_registry.logging
print(log_config.level)           # "DEBUG" (dev) or "INFO" (prod)
print(log_config.write_to_file)   # False (dev) or True (prod)
print(log_config.log_file_path)   # Path to main log file
print(log_config.django_log_file_path)  # Path to Django log file
```

## Usage

### In your application code

```python
from loguru import logger

# Use logger directly
logger.info("Application started")
logger.debug("Debug information")
logger.error("An error occurred", exc_info=True)

# With context binding
logger.bind(user_id=123).info("User action")
logger.bind(request_id="abc123").debug("Processing request")
```

### Django logging

Django logging is automatically captured by `InterceptHandler`:

```python
import logging

# This log message goes through Loguru
logger = logging.getLogger('django')
logger.info("Django message")
logger.warning("Django warning")
```

Both application and Django logs use the same Loguru instance and configuration.

## Environment Variables

In `.env`:

```bash
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=DEBUG

# Directory for log files (relative to project root)
LOG_DIR=logs
```

## Log Files

### Development

```
Console output only (colorized, real-time)
├─ No files created
├─ DEBUG level (verbose)
└─ Example: 2024-01-15 14:32:50 | DEBUG | myapp.service:process:42 - Processing started
```

### Production

```
logs/
├── app.log           # Main application log (all modules)
└── django.log        # Django-specific log (Django requests, queries, etc.)

Configuration:
├─ INFO level (less verbose)
├─ Retention: 30 days
├─ Rotation: 500 MB per file
└─ Compression: automatic zip of rotated logs
```

## Django Settings Integration

In `config/settings/django/base.py`:

```python
# Minimal LOGGING dict - Loguru handles everything
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
}
```

The actual logging setup happens in `setup_logging()` which is called early in the application startup.

## Initialization

Loguru is initialized automatically at application startup:

### In `manage.py` (CLI commands)

```python
from config.logger import setup_logging
from config.settings.schemas import config_registry as config

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", config.django_settings_module)
    setup_logging()  # ← Initialize Loguru here
    execute_from_command_line(sys.argv)
```

### In `config/wsgi.py` (Production server)

```python
from config.logger import setup_logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", config.django_settings_module)
setup_logging()  # ← Initialize Loguru here

application = get_wsgi_application()
```

The `setup_logging()` function:
1. Removes default Loguru handler
2. Adds console output with color formatting
3. Adds file handlers (only if `write_to_file=True` in production)
4. Sets up rotation and retention policies
5. Redirects Python logging → Loguru via `InterceptHandler`

## Pattern Explanation

This implementation follows the Pydantic configuration pattern used throughout the project:

1. **Schema Definition** - `LoggingConfig` with environment-specific subclasses
2. **Factory Pattern** - `logging_config_factory` returns appropriate config
3. **Registry Integration** - Accessible via `config_registry.logging`
4. **Environment-based Selection** - Development vs production automatically chosen

Just like `DatabaseConfig` and `DjangoConfig`, logging configuration:
- Loads from `.env` via Pydantic
- Validates types and ranges
- Provides cached properties for file paths
- Is accessible globally through `config_registry`

## Log Formats

### Console Output (Development)

Colorized, easy to read:

```
2024-01-15 14:32:50 | DEBUG    | myapp.service:process:42 - Processing started
2024-01-15 14:32:51 | INFO     | django.request:log_response:123 - GET /api/users/ 200
2024-01-15 14:32:52 | ERROR    | myapp.utils:compute:89 - Calculation failed
```

### File Output (Production)

Same Loguru format, persisted to disk:

```
2024-01-15 14:32:50 | INFO     | myapp.service:process:42 - Service initialized
2024-01-15 14:32:51 | WARNING  | django.db.backends:log_sql:156 - Slow query (2.5s)
2024-01-15 14:32:52 | ERROR    | myapp.utils:compute:89 - Failed to compute value
```

Format configuration in `config/settings/schemas/logging.py`:

```python
format: str = Field(
    default=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
)
```

## Production Considerations

### Log Levels

- **Development**: DEBUG (verbose, all messages)
- **Production**: INFO (relevant messages only)

### File Management

- **Automatic Rotation**: Files rotate at 500 MB
- **Automatic Retention**: Old logs deleted after 30 days
- **Automatic Compression**: Rotated logs compressed as `.zip`
- **Directory Creation**: `logs/` directory created automatically on first run

### Django Query Logging

In production, Django database query logging is reduced to WARNING level to avoid excessive I/O and disk usage.

## Related Files

- **`config/logger.py`** - Loguru setup, `InterceptHandler` for Django integration
- **`config/settings/schemas/logging.py`** - `LoggingConfig` Pydantic models with environment variants
- **`config/settings/schemas/registry.py`** - Registry provides `config_registry.logging`
- **`config/settings/django/base.py`** - Minimal `LOGGING` dict (Loguru handles everything)
- **`manage.py`** - Calls `setup_logging()` before Django initialization
- **`config/wsgi.py`** - Calls `setup_logging()` for production server
- **`.env.template`** - `LOG_LEVEL` and `LOG_DIR` environment variables
