#!/usr/bin/env python3
"""Quick database commands demonstration script.

This script demonstrates common database command workflows without requiring
user interaction. Useful for CI/CD or automated testing.
"""

import os
import subprocess  # noqa: S404
import sys
from pathlib import Path

# Colors
CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
NC = "\033[0m"


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{CYAN}{'=' * 60}{NC}")
    print(f"{CYAN}{text:^60}{NC}")
    print(f"{CYAN}{'=' * 60}{NC}\n")


def print_section(text: str) -> None:
    """Print a section header."""
    print(f"\n{YELLOW}▸ {text}{NC}")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"{GREEN}✓ {text}{NC}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"{RED}✗ {text}{NC}")


def run_command(description: str, command: list[str], show_output: bool = True) -> bool:
    """Run a command and return success status."""
    print_section(description)
    print(f"{YELLOW}Running: {' '.join(command)}{NC}\n")

    try:
        result = subprocess.run(  # noqa: S603
            command,
            capture_output=not show_output,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            print_success(f"{description} - SUCCESS")
            return True
        else:
            print_error(f"{description} - FAILED (exit code: {result.returncode})")
            if not show_output and result.stderr:
                print(result.stderr)
            return False
    except Exception as e:
        print_error(f"{description} - ERROR: {e}")
        return False


def demo_help_commands() -> None:
    """Demonstrate help commands."""
    print_header("DEMO 1: Help Commands")

    commands = [
        ("Main database help", ["python3", "-m", "devtools", "db", "--help"]),
        (
            "Create command help",
            ["python3", "-m", "devtools", "db", "create", "--help"],
        ),
        ("Drop command help", ["python3", "-m", "devtools", "db", "drop", "--help"]),
        ("Setup command help", ["python3", "-m", "devtools", "db", "setup", "--help"]),
    ]

    for desc, cmd in commands:
        run_command(desc, cmd, show_output=True)
        print()


def demo_environment_check() -> None:
    """Show current environment configuration."""
    print_header("DEMO 2: Environment Check")

    # Read .env file
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with Path(env_file).open() as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    if "PASSWORD" not in line:  # Don't show passwords
                        print(f"  {line.strip()}")
                    else:
                        key = line.split("=")[0]
                        print(f"  {key}=***")
    else:
        print_error(".env file not found")

    print()


def demo_dry_run_commands() -> None:
    """Demonstrate commands that don't modify database (safe)."""
    print_header("DEMO 3: Safe Commands (Dry Run)")

    print_section("These commands are safe and won't modify the database:")
    print("  • devtools db --help")
    print("  • devtools db create --help")
    print("  • devtools db drop --help")
    print("  • Environment variable checks")
    print()

    print_section("To test actual database operations, use:")
    print("  • ./tests/test_db_commands.sh (interactive)")
    print("  • python tests/demo_commands.py --run-all (requires confirmation)")
    print()


def demo_production_guards() -> None:
    """Demonstrate production safety guards."""
    print_header("DEMO 4: Production Safety Guards")

    print_section("Safety Features:")
    print("  ✓ DROP operations blocked in production")
    print("  ✓ RESET operations blocked in production")
    print("  ✓ SUPERUSER creation blocked in production")
    print("  ✓ Explicit --allow-in-production flag required")
    print()

    print_section("Example of blocked operation in production:")
    print("  ENV_STATE=production")
    print("  $ devtools db drop")
    print("  → ⚠️  OPERATION BLOCKED - Safety guard active")
    print()

    print_section("Override with explicit flag (use with caution):")
    print("  $ devtools db drop --allow-in-production")
    print("  → Proceeds with confirmation")
    print()


def demo_command_structure() -> None:
    """Show command structure and available options."""
    print_header("DEMO 5: Command Structure")

    commands_info = [
        ("db create", "Create database", "Safe in dev/prod"),
        ("db drop", "Drop database", "⚠️  Blocked in prod"),
        ("db reset", "Reset database", "⚠️  Blocked in prod"),
        ("db create-user", "Create PostgreSQL user", "Safe in dev/prod"),
        ("db create-user --superuser", "Create superuser", "⚠️  Blocked in prod"),
        ("db drop-user", "Drop user", "⚠️  Blocked in prod"),
        ("db setup", "Complete setup", "Safe in dev/prod"),
        ("db setup --reset", "Setup with reset", "⚠️  Blocked in prod"),
    ]

    print(f"{'Command':<30} {'Description':<25} {'Safety':<20}")
    print("-" * 75)
    for cmd, desc, safety in commands_info:
        print(f"{cmd:<30} {desc:<25} {safety:<20}")

    print()


def main() -> None:
    """Main execution."""
    # Change to backend directory
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)

    print_header("Database Commands Demonstration")
    print("This script demonstrates database commands without executing")
    print("destructive operations.")
    print()

    try:
        demo_help_commands()
        demo_environment_check()
        demo_command_structure()
        demo_production_guards()
        demo_dry_run_commands()

        print_header("Demonstration Complete")
        print_success("All demonstrations completed successfully")
        print()
        print("Next steps:")
        print("  1. Review test flows: cat tests/README.md")
        print("  2. Run interactive tests: ./tests/test_db_commands.sh")
        print("  3. Configure your .env file for actual testing")
        print()

    except KeyboardInterrupt:
        print_error("\nDemonstration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error during demonstration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
