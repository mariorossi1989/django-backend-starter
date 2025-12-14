#!/usr/bin/env bash
# Test Database Commands - Interactive Testing Script
#
# This script provides guided testing flows for database management commands
# with built-in safety checks and environment simulation.
#
# Usage:
#     ./tests/db_commands/test_db_commands.sh [flow]
#
# Flows:
#     1) basic     - Test basic commands (create, info)
#     2) lifecycle - Test complete database lifecycle
#     3) users     - Test user management
#     4) setup     - Test complete setup workflow
#     5) guards    - Test production safety guards
#     6) all       - Run all test flows

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Helper functions
print_header() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_section() {
    echo -e "\n${BLUE}▸ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

run_command() {
    local description="$1"
    shift
    echo -e "\n${YELLOW}→ Running:${NC} $@"
    if "$@"; then
        print_success "$description"
        return 0
    else
        print_error "$description failed"
        return 1
    fi
}

confirm() {
    local prompt="$1"
    read -p "$(echo -e "${YELLOW}${prompt} (y/N):${NC} ")" -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

wait_for_user() {
    echo -e "\n${CYAN}Press Enter to continue...${NC}"
    read
}

check_prerequisites() {
    print_section "Checking prerequisites"
    
    # Check if in backend directory
    if [[ ! -f "$BACKEND_DIR/manage.py" ]]; then
        print_error "Not in backend directory"
        exit 1
    fi
    
    # Check if .env exists
    if [[ ! -f "$BACKEND_DIR/.env" ]]; then
        print_warning ".env file not found"
        if confirm "Create .env from template?"; then
            cp "$BACKEND_DIR/.env.template" "$BACKEND_DIR/.env"
            print_info "Please edit .env file with your configuration"
            exit 0
        else
            exit 1
        fi
    fi
    
    # Check Python environment
    if [[ ! -d "$BACKEND_DIR/.venv" ]]; then
        print_warning "Virtual environment not found"
        print_info "Creating virtual environment..."
        python3 -m venv "$BACKEND_DIR/.venv"
    fi
    
    print_success "Prerequisites OK"
}

get_current_env() {
    cd "$BACKEND_DIR"
    source .env
    echo "${ENV_STATE:-development}"
}

show_env_info() {
    local current_env=$(get_current_env)
    echo -e "${CYAN}Current Environment:${NC} ${YELLOW}${current_env}${NC}"
    
    if [[ "$current_env" == "production" ]]; then
        print_warning "Running in PRODUCTION mode - destructive operations will be blocked"
    else
        print_info "Running in DEVELOPMENT mode - all operations allowed"
    fi
}

# Test Flow 1: Basic Commands
test_basic_flow() {
    print_header "TEST FLOW 1: Basic Commands"
    show_env_info
    
    print_section "Testing help commands"
    run_command "Show main db help" python3 -m devtools db --help
    wait_for_user
    
    print_section "Testing create command help"
    run_command "Show create help" python3 -m devtools db create --help
    wait_for_user
    
    print_section "Testing drop command help"
    run_command "Show drop help" python3 -m devtools db drop --help
    wait_for_user
    
    print_success "Basic flow completed"
}

# Test Flow 2: Database Lifecycle
test_lifecycle_flow() {
    print_header "TEST FLOW 2: Database Lifecycle"
    show_env_info
    
    print_warning "This flow will create and drop a test database"
    if ! confirm "Continue?"; then
        return
    fi
    
    print_section "Step 1: Show all database configurations"
    run_command "Show database info" python3 -m devtools db info || true
    wait_for_user
    
    print_section "Step 2: Create database (default)"
    run_command "Create database" python3 -m devtools db create || true
    wait_for_user
    
    print_section "Step 3: Verify database exists"
    print_info "Check your PostgreSQL instance to verify database was created"
    wait_for_user
    
    print_section "Step 4: Drop database (default)"
    run_command "Drop database" python3 -m devtools db drop --force || true
    wait_for_user
    
    print_success "Lifecycle flow completed"
}

# Test Flow 3: User Management
test_users_flow() {
    print_header "TEST FLOW 3: User Management"
    show_env_info
    
    print_warning "This flow will create and drop a PostgreSQL user"
    if ! confirm "Continue?"; then
        return
    fi
    
    print_section "Step 1: Create regular user"
    run_command "Create user" python3 -m devtools db create-user || true
    wait_for_user
    
    print_section "Step 2: Try to create superuser"
    print_info "This should be blocked in production"
    run_command "Create superuser" python3 -m devtools db create-user --superuser --drop || true
    wait_for_user
    
    print_section "Step 3: Drop user"
    run_command "Drop user" python3 -m devtools db drop-user --force || true
    wait_for_user
    
    print_success "User management flow completed"
}

# Test Flow 4: Complete Setup
test_setup_flow() {
    print_header "TEST FLOW 4: Complete Setup Workflow"
    show_env_info
    
    print_warning "This flow will run complete database setup"
    if ! confirm "Continue?"; then
        return
    fi
    
    print_section "Testing setup with migrations"
    run_command "Complete setup" python3 -m devtools db setup || true
    wait_for_user
    
    print_section "Testing reset setup"
    print_info "This should be blocked in production"
    run_command "Reset setup" python3 -m devtools db setup --reset || true
    wait_for_user
    
    print_success "Setup flow completed"
}

# Test Flow 5: Production Guards
test_guards_flow() {
    print_header "TEST FLOW 5: Production Safety Guards"
    
    print_section "Simulating PRODUCTION environment"
    print_info "Temporarily setting ENV_STATE=production"
    
    # Backup current .env
    cp "$BACKEND_DIR/.env" "$BACKEND_DIR/.env.backup"
    
    # Set production mode
    sed -i 's/ENV_STATE=.*/ENV_STATE=production/' "$BACKEND_DIR/.env"
    
    show_env_info
    wait_for_user
    
    print_section "Test 1: Try to drop database (should be blocked)"
    python3 -m devtools db drop --force || print_success "Correctly blocked"
    wait_for_user
    
    print_section "Test 2: Try to create superuser (should be blocked)"
    python3 -m devtools db create-user --superuser || print_success "Correctly blocked"
    wait_for_user
    
    print_section "Test 3: Try with --allow-in-production flag"
    print_warning "This would work but we'll skip actual execution"
    print_info "Command: python3 -m devtools db drop --force --allow-in-production"
    wait_for_user
    
    # Restore .env
    mv "$BACKEND_DIR/.env.backup" "$BACKEND_DIR/.env"
    print_success "Restored development environment"
    
    print_success "Production guards flow completed"
}

# Test Flow 6: Reset and Lifecycle
test_reset_flow() {
    print_header "TEST FLOW 6: Reset Database"
    show_env_info
    
    print_warning "This flow will reset the database (drop + create + migrate)"
    if ! confirm "Continue?"; then
        return
    fi
    
    print_section "Testing reset without migrations (default)"
    run_command "Reset (no migrate)" python3 -m devtools db reset --no-migrate || true
    wait_for_user
    
    print_section "Testing reset with migrations (default)"
    run_command "Reset with migrations" python3 -m devtools db reset --force || true
    wait_for_user
    
    print_success "Reset flow completed"
}

# Test Flow 7: Multi-Database Operations
test_multidb_flow() {
    print_header "TEST FLOW 7: Multi-Database Operations"
    show_env_info
    
    print_info "This flow demonstrates multi-database support"
    print_warning "Ensure you have multiple databases configured in .env (DB_ALIASES)"
    if ! confirm "Continue?"; then
        return
    fi
    
    print_section "Step 1: Show all database configurations"
    run_command "Show all databases" python3 -m devtools db info || true
    wait_for_user
    
    print_section "Step 2: Setup all databases"
    print_info "This will setup all databases defined in DB_ALIASES"
    if confirm "Setup all databases?"; then
        run_command "Setup all databases" python3 -m devtools db setup --all --force || true
        wait_for_user
    fi
    
    print_section "Step 3: Test specific database operations"
    print_info "These commands show how to target specific databases"
    echo -e "\n${YELLOW}Example commands (not executed):${NC}"
    echo "  python3 -m devtools db create --alias db2"
    echo "  python3 -m devtools db drop --alias db2 --force"
    echo "  python3 -m devtools db setup --alias analytics"
    echo "  python3 -m devtools db reset --alias db2 --force"
    wait_for_user
    
    print_section "Step 4: Cleanup (optional)"
    if confirm "Drop all databases?"; then
        run_command "Drop all databases" python3 -m devtools db drop --all --force || true
        wait_for_user
    fi
    
    print_success "Multi-database flow completed"
}

# Main menu
show_menu() {
    print_header "Database Commands Test Flows"
    echo "Select a test flow to run:"
    echo
    echo "  1) basic     - Test basic commands and help"
    echo "  2) lifecycle - Test database create/drop lifecycle"
    echo "  3) users     - Test user management"
    echo "  4) setup     - Test complete setup workflow"
    echo "  5) guards    - Test production safety guards"
    echo "  6) reset     - Test database reset"
    echo "  7) multidb   - Test multi-database operations (--alias, --all)"
    echo "  8) all       - Run all flows sequentially"
    echo "  q) quit      - Exit"
    echo
}

run_all_flows() {
    test_basic_flow
    test_lifecycle_flow
    test_users_flow
    test_setup_flow
    test_guards_flow
    test_reset_flow
    test_multidb_flow
}

# Main execution
main() {
    cd "$BACKEND_DIR"
    
    check_prerequisites
    
    if [[ $# -eq 1 ]]; then
        case "$1" in
            basic|1)
                test_basic_flow
                ;;
            lifecycle|2)
                test_lifecycle_flow
                ;;
            users|3)
                test_users_flow
                ;;
            setup|4)
                test_setup_flow
                ;;
            guards|5)
                test_guards_flow
                ;;
            reset|6)
                test_reset_flow
                ;;
            multidb|7)
                test_multidb_flow
                ;;
            all|8)
                run_all_flows
                ;;
            *)
                echo "Unknown flow: $1"
                show_menu
                exit 1
                ;;
        esac
    else
        # Interactive mode
        while true; do
            show_menu
            read -p "Enter choice: " choice
            case $choice in
                1) test_basic_flow ;;
                2) test_lifecycle_flow ;;
                3) test_users_flow ;;
                4) test_setup_flow ;;
                5) test_guards_flow ;;
                6) test_reset_flow ;;
                7) test_multidb_flow ;;
                8) run_all_flows ;;
                q|Q) 
                    print_info "Goodbye!"
                    exit 0
                    ;;
                *)
                    print_error "Invalid choice"
                    ;;
            esac
        done
    fi
}

main "$@"
