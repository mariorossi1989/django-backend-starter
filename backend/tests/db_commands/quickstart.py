#!/usr/bin/env python3
"""Quick Start Guide - Database Commands Testing

This script provides a simple, safe way to explore database commands.
"""

from pathlib import Path


def print_colored(text: str, color: str = "") -> None:
    """Print colored text."""
    colors = {
        "cyan": "\033[0;36m",
        "green": "\033[0;32m",
        "yellow": "\033[1;33m",
        "red": "\033[0;31m",
        "blue": "\033[0;34m",
    }
    nc = "\033[0m"
    print(f"{colors.get(color, '')}{text}{nc}")


def main() -> None:
    """Display quick start guide."""
    print_colored("\n" + "=" * 70, "cyan")
    print_colored("  DATABASE COMMANDS - QUICK START GUIDE", "cyan")
    print_colored("=" * 70 + "\n", "cyan")

    print_colored("📚 AVAILABLE TEST SCRIPTS\n", "yellow")

    print("1️⃣  Interactive Test Menu (Recommended)")
    print("   Run: ./tests/test_db_commands.sh")
    print("   Features:")
    print("     • Menu-driven interface")
    print("     • Multiple test flows")
    print("     • Safety checks and confirmations")
    print("     • Environment simulation\n")

    print("2️⃣  Quick Command Examples")
    print("   View help and documentation without executing commands\n")

    print_colored("🎯 QUICK START STEPS\n", "yellow")

    print("Step 1: Configure Environment")
    print("   • Edit backend/.env with your database credentials")
    print("   • Set ENV_STATE=development for testing")
    print("   • Ensure PostgreSQL is running\n")

    print("Step 2: Run Interactive Tests")
    print("   $ cd backend")
    print("   $ ./tests/test_db_commands.sh\n")

    print("Step 3: Choose a Test Flow")
    print("   Option 1: Basic Commands       - Safe, no DB changes")
    print("   Option 2: Database Lifecycle   - Create/drop test DB")
    print("   Option 3: User Management      - Create/drop test user")
    print("   Option 4: Complete Setup       - Full workflow")
    print("   Option 5: Production Guards    - Test safety features")
    print("   Option 6: Reset Database       - Reset workflow\n")

    print_colored("💡 COMMAND EXAMPLES\n", "yellow")

    commands = [
        ("View all database commands", "python3 -m devtools db --help"),
        ("Show create command help", "python3 -m devtools db create --help"),
        ("Create database", "python3 -m devtools db create"),
        ("Drop database (safe mode)", "python3 -m devtools db drop"),
        ("Drop database (force)", "python3 -m devtools db drop --force"),
        ("Create user", "python3 -m devtools db create-user"),
        ("Create superuser", "python3 -m devtools db create-user --superuser"),
        ("Complete setup", "python3 -m devtools db setup"),
        ("Reset database", "python3 -m devtools db reset"),
    ]

    for desc, cmd in commands:
        print(f"  {desc}")
        print(f"  $ {cmd}\n")

    print_colored("⚠️  PRODUCTION SAFETY\n", "yellow")

    print("Dangerous operations are BLOCKED in production:")
    print("  ✗ drop      - Cannot drop database")
    print("  ✗ reset     - Cannot reset database")
    print("  ✗ drop-user - Cannot drop users")
    print("  ✗ --superuser - Cannot create superusers\n")

    print("To override (use with extreme caution):")
    print("  $ devtools db drop --allow-in-production\n")

    print_colored("📖 DOCUMENTATION\n", "yellow")

    print("  • Full testing guide: cat tests/README.md")
    print("  • Interactive menu: ./tests/test_db_commands.sh")
    print("  • Module docs: python3 -m devtools db --help\n")

    print_colored("🚀 READY TO START?\n", "green")
    print("Run the interactive test menu:")
    print_colored("  $ ./tests/test_db_commands.sh\n", "cyan")


if __name__ == "__main__":
    # Change to backend directory
    backend_dir = Path(__file__).parent.parent
    if backend_dir.exists():
        import os

        os.chdir(backend_dir)

    main()
