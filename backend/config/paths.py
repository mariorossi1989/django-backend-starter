"""Path definitions for the project.

Defines base paths used throughout the application for configuration,
environment files, and other resources.
"""

from pathlib import Path

# Root directory of the entire project
_ROOT_DIR = Path(__file__).resolve().parents[2]

# Backend application directory
PROJECT_DIR = _ROOT_DIR / "backend"

# Environment configuration file path
PROJECT_ENV_FILE = PROJECT_DIR / ".env"
